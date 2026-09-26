"""Learned rule reader, explicit RTG state, and a parameter-matched Elman control.

The module receives only shuffled (source, destination) rule rows and a start.
There are no labels, teacher transitions, oracle trajectories, or hidden modes here.
"""
from __future__ import annotations

import math
import torch
from torch import nn
from torch.nn import functional as F


def unit(x):
    return F.normalize(x, dim=-1, eps=1e-8)


def discrete_state(probability):
    hard = F.one_hot(probability.argmax(-1), probability.shape[-1]).to(probability.dtype)
    # Exactly one realized forward event, with a biased soft surrogate backward.
    return hard + (probability - probability.detach())


class RuleReader(nn.Module):
    def __init__(self, n=10, width=32):
        super().__init__()
        self.n, self.width = n, width
        self.query = nn.Parameter(torch.randn(n, width) * 0.2)
        self.key = nn.Parameter(torch.randn(n, width) * 0.2)
        self.value = nn.Parameter(torch.randn(n, width) * 0.2)
        self.answer = nn.Linear(width, n)

    def all_rows(self, source, destination):
        keys, values = self.key[source], self.value[destination]
        attention = torch.softmax(torch.einsum('ad,bjd->baj', self.query, keys) / math.sqrt(self.width), -1)
        context = attention @ values
        return self.answer(context), context

    def forward(self, source, destination, start):
        logits, _ = self.all_rows(source, destination)
        return logits[torch.arange(len(start)), start]


class DynamicLearner(nn.Module):
    """Both arms deliberately own exactly these active trainable tensors."""
    def __init__(self, reader: RuleReader, relation_dim=16, geometry_scale=1., write_budget=1.):
        super().__init__()
        self.reader = reader
        self.reader.requires_grad_(False)
        self.n, self.d = reader.n, relation_dim
        self.scale, self.budget = geometry_scale, write_budget
        self.relation = nn.Linear(reader.width * 4, relation_dim)
        self.w_phi = nn.Linear(relation_dim, relation_dim, bias=False)
        self.w_m = nn.Linear(relation_dim, relation_dim, bias=False)
        self.w_inherit = nn.Linear(relation_dim, relation_dim, bias=False)
        self.raw_gamma = nn.Parameter(torch.tensor(math.log(math.expm1(1.))))
        self.raw_eta = nn.Parameter(torch.tensor(math.log(math.expm1(2.))))
        self.raw_rho = nn.Parameter(torch.tensor(0.))
        self.raw_retention = nn.Parameter(torch.tensor(math.log(9.)))

    def coefficients(self):
        return F.softplus(self.raw_gamma), F.softplus(self.raw_eta), torch.sigmoid(self.raw_rho), torch.sigmoid(self.raw_retention)

    def coefficient_dict(self):
        return dict(zip(('gamma', 'eta', 'rho', 'retention'), [float(x.detach()) for x in self.coefficients()]))

    def prepare(self, source, destination):
        raw, context = self.reader.all_rows(source, destination)
        centered = raw - raw.mean(-1, keepdim=True)
        geometry = self.scale * centered / centered.square().mean(-1, keepdim=True).sqrt().clamp_min(1e-5)
        b, n = source.shape
        q = self.reader.query[None, :, None, :].expand(b, n, n, -1)
        k = self.reader.key[None, None, :, :].expand(b, n, n, -1)
        c = context[:, :, None, :].expand(b, n, n, -1)
        v = self.reader.value[None, None, :, :].expand(b, n, n, -1)
        phi = unit(torch.tanh(self.relation(torch.cat((q, k, c, v), -1))))
        return geometry, phi


class RTG(DynamicLearner):
    def event(self, geometry, external, memory, phi, state, *, mode='full'):
        logits = torch.einsum('ba,bak->bk', state, geometry)
        p = torch.softmax(logits, -1)
        child = discrete_state(p)
        relation = torch.einsum('ba,bakd,bk->bd', state, phi, child)
        source_memory = torch.einsum('ba,bad->bd', state, memory)
        gamma, eta, rho, retention = self.coefficients()
        if mode == 'gamma_zero':
            gamma = gamma * 0
        g = unit(self.w_phi(relation) + gamma * self.w_m(source_memory))
        descendant = torch.einsum('ba,bakd->bkd', child, phi)
        score = torch.einsum('bd,bkd->bk', g, descendant)
        score = score - score.mean(-1, keepdim=True)
        delta = child[:, :, None] * (eta * score)[:, None, :]
        if mode == 'no_write':
            delta = delta * 0
        proposed_norm = delta.flatten(1).norm(dim=1)
        alpha = (self.budget / (proposed_norm + 1e-8)).clamp(max=1.)
        if mode == 'unbounded':
            alpha = torch.ones_like(alpha)
        next_geometry = external + retention * (geometry - external) + alpha[:, None, None] * delta
        old_at_child = torch.einsum('ba,bad->bd', child, memory)
        new_at_child = unit((1 - rho) * old_at_child + rho * self.w_inherit(g))
        next_memory = memory + child[:, :, None] * (new_at_child - old_at_child)[:, None, :]
        if mode == 'no_inheritance':
            next_memory = memory
        elif mode == 'reset_m':
            next_memory = next_memory * 0
        info = {'logits': logits, 'probabilities': p, 'g': g, 'alpha': alpha,
                'delta_gene': delta, 'proposed_norm': proposed_norm,
                'actual_norm': (alpha[:, None, None] * delta).flatten(1).norm(dim=1)}
        return next_geometry, next_memory, child, info

    def forward(self, source, destination, start, length, *, mode='full', trace=False):
        geometry, phi = self.prepare(source, destination)
        external = geometry
        memory = geometry.new_zeros(len(start), self.n, self.d)
        state = F.one_hot(start, self.n).float()
        records = []
        if trace:
            writers = [[None] * self.n for _ in start]
            geometry_writers = [[[] for _ in range(self.n)] for _ in start]
        for step in range(length):
            next_geometry, next_memory, child, info = self.event(geometry, external, memory, phi, state, mode=mode)
            if trace:
                p = info['probabilities'].detach()
                entropy = -(p * p.clamp_min(1e-12).log()).sum(-1)
                a_ids, b_ids = state.argmax(-1).tolist(), child.argmax(-1).tolist()
                for i, (a, b) in enumerate(zip(a_ids, b_ids)):
                    event_id = f'e{step}'
                    records.append({
                        'episode_index': i, 'step': step, 'event_id': event_id, 'a': a, 'b': b,
                        'inherited_source_writer': writers[i][a],
                        'recombined_destination_writer': writers[i][b],
                        'decision_row_writers': list(geometry_writers[i][a]),
                        'ancestry_semantics': 'computation_dependencies_not_necessity_proof',
                        'L_before': geometry[i].detach().tolist(), 'L_after': next_geometry[i].detach().tolist(),
                        'M_before': memory[i].detach().tolist(), 'M_after': next_memory[i].detach().tolist(),
                        'M_norms': next_memory[i].detach().norm(dim=-1).tolist(),
                        'g': info['g'][i].detach().tolist(), 'alpha': float(info['alpha'][i].detach()),
                        'delta_gene_norm': float(info['proposed_norm'][i].detach()),
                        'delta_projection_norm': 0., 'actual_write_norm': float(info['actual_norm'][i].detach()),
                        'continuation_entropy': float(entropy[i]), 'effective_candidates': float(entropy[i].exp()),
                        'top_share': float(p[i].max()),
                    })
                    if mode not in ('no_inheritance', 'reset_m'):
                        writers[i][b] = event_id
                    elif mode == 'reset_m':
                        writers[i] = [None] * self.n
                    if mode != 'no_write':
                        geometry_writers[i][b].append(event_id)
            geometry, memory, state = next_geometry, next_memory, child
        return (info['logits'], records) if trace else info['logits']


class RecurrentAdapter(DynamicLearner):
    """Ordinary global Elman state, not an RTG implementation."""
    def forward(self, source, destination, start, length):
        geometry, phi = self.prepare(source, destination)
        state = F.one_hot(start, self.n).float()
        hidden = geometry.new_zeros(len(start), self.d)
        gamma, eta, rho, retention = self.coefficients()
        for _ in range(length):
            local_features = torch.einsum('ba,bakd->bkd', state, phi)
            correction = eta * torch.einsum('bd,bkd->bk', torch.tanh(self.w_inherit(hidden)), local_features)
            correction = correction - correction.mean(-1, keepdim=True)
            correction = correction * (self.budget / (correction.norm(dim=-1, keepdim=True) + 1e-8)).clamp(max=1.)
            logits = torch.einsum('ba,bak->bk', state, geometry) + correction
            child = discrete_state(torch.softmax(logits, -1))
            edge = torch.einsum('bkd,bk->bd', local_features, child)
            proposal = torch.tanh(self.w_phi(edge) + gamma * self.w_m(hidden))
            hidden = retention * (1 - rho) * hidden + rho * proposal
            state = child
        return logits


def iterated_base(reader, source, destination, start, length):
    geometry, _ = reader.all_rows(source, destination)
    state = start
    for _ in range(length):
        logits = geometry[torch.arange(len(start)), state]
        state = logits.argmax(-1)
    return logits


def trainable_count(model):
    return sum(p.numel() for p in model.parameters() if p.requires_grad)
