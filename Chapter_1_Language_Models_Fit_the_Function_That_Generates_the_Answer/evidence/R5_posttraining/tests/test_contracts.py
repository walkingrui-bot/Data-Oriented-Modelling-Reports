import copy
import itertools
import unittest
import numpy as np
import torch
from torch.nn import functional as F

from ..src.data import permutation_rank, belongs, random_episodes, final_answer
from ..src.models import RuleReader, RTG, RecurrentAdapter, iterated_base, trainable_count


class Contracts(unittest.TestCase):
    def setUp(self):
        torch.set_num_threads(1)
        torch.manual_seed(731)
        self.reader = RuleReader()
        self.rtg = RTG(self.reader)
        self.ep = random_episodes(np.random.default_rng(731), 12, 10, 'train')

    def test_exact_rule_partition(self):
        p = np.array(list(itertools.permutations(range(5))))
        r = permutation_rank(p)
        self.assertEqual(len(set(r)), 120)
        self.assertTrue(np.array_equal(r, np.arange(120)))
        count = sum(belongs(r, x).astype(int) for x in ('train', 'validation', 'test'))
        self.assertTrue(np.array_equal(count, np.ones(120)))

    def test_label_convention(self):
        rules = np.array([[1, 2, 0], [0, 2, 1]])
        self.assertEqual(final_answer(rules, np.array([0, 1]), 3).tolist(), [0, 2])

    def test_destination_write_and_budget(self):
        src, dst, start = self.ep.inputs()
        ext, phi = self.rtg.prepare(src, dst)
        state = F.one_hot(start, 10).float()
        mem = torch.zeros(12, 10, 16)
        with torch.no_grad():
            self.rtg.raw_eta.fill_(30.)
        nxt, newmem, child, info = self.rtg.event(ext, ext, mem, phi, state)
        b = child.argmax(-1)
        delta = nxt - ext
        mask = ~F.one_hot(b, 10).bool()
        self.assertLess(float(delta[mask].abs().max().detach()), 1e-6)
        self.assertLessEqual(float(info['actual_norm'].max().detach()), 1.000001)
        self.assertLess(float(info['alpha'].min().detach()), 1.)
        self.assertTrue(torch.equal(child.detach(), F.one_hot(b, 10).float()))
        self.assertTrue(torch.allclose(newmem.norm(dim=-1).max(1).values, torch.ones(12), atol=1e-6))

    def test_no_write_equals_iterated_reader(self):
        args = self.ep.inputs()
        for length in (1, 2, 4):
            self.assertTrue(torch.equal(self.rtg(*args, length, mode='no_write').argmax(-1),
                                        iterated_base(self.reader, *args, length).argmax(-1)))

    def test_first_answer_precedes_trainable_write(self):
        args = self.ep.inputs()
        first = self.rtg(*args, 1)
        self.assertFalse(first.requires_grad)
        self.assertTrue(self.rtg(*args, 2).requires_grad)
        self.assertTrue(torch.equal(first.argmax(-1), self.reader(*args).argmax(-1)))

    def test_row_order_invariance(self):
        source, dest, start = self.ep.inputs()
        p = torch.arange(9, -1, -1)
        a = self.rtg(source, dest, start, 4)
        b = self.rtg(source[:, p], dest[:, p], start, 4)
        self.assertTrue(torch.allclose(a, b, atol=2e-5))

    def test_inherited_state_causally_enters_phenotype(self):
        src, dst, start = self.ep.inputs()
        ext, phi = self.rtg.prepare(src, dst)
        state = F.one_hot(start, 10).float()
        empty = torch.zeros(12, 10, 16)
        random_memory = torch.randn_like(empty)
        _, _, _, a = self.rtg.event(ext, ext, empty, phi, state)
        _, _, _, b = self.rtg.event(ext, ext, random_memory, phi, state)
        _, _, _, c = self.rtg.event(ext, ext, empty, phi, state, mode='gamma_zero')
        _, _, _, d = self.rtg.event(ext, ext, random_memory, phi, state, mode='gamma_zero')
        self.assertFalse(torch.allclose(a['g'], b['g']))
        self.assertTrue(torch.equal(c['g'], d['g']))

    def test_matched_active_parameters_and_frozen_base(self):
        recurrent = RecurrentAdapter(copy.deepcopy(self.reader))
        recurrent.load_state_dict(self.rtg.state_dict())
        self.assertEqual(trainable_count(self.rtg), trainable_count(recurrent))
        initial = {k: v.clone() for k, v in self.reader.state_dict().items()}
        for model in (self.rtg, recurrent):
            opt = torch.optim.Adam([p for p in model.parameters() if p.requires_grad], lr=.001)
            loss = F.cross_entropy(model(*self.ep.inputs(), 4), self.ep.target(4))
            loss.backward()
            for name, p in model.named_parameters():
                if p.requires_grad:
                    self.assertIsNotNone(p.grad, name)
                    self.assertTrue(torch.isfinite(p.grad).all(), name)
                else:
                    self.assertIsNone(p.grad, name)
            opt.step()
            for k, v in model.reader.state_dict().items():
                self.assertTrue(torch.equal(v, initial[k]), k)

    def test_trace_contract(self):
        _, trace = self.rtg(*self.ep.take(slice(0, 2)).inputs(), 4, trace=True)
        self.assertEqual(len(trace), 8)
        for row in trace:
            for key in ('L_before', 'L_after', 'M_norms', 'g', 'alpha', 'delta_gene_norm',
                        'delta_projection_norm', 'continuation_entropy', 'effective_candidates',
                        'top_share', 'decision_row_writers', 'event_id'):
                self.assertIn(key, row)


if __name__ == '__main__':
    unittest.main(verbosity=2)
