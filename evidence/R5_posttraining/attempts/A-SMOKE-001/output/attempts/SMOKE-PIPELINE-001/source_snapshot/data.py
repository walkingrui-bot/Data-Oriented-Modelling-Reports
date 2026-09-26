"""Permutation episodes. The oracle lives here and is never passed to a learner."""
from __future__ import annotations

import math
from dataclasses import dataclass
import numpy as np
import torch


def permutation_rank(permutations: np.ndarray) -> np.ndarray:
    p = np.asarray(permutations, dtype=np.int64)
    rank = np.zeros(len(p), dtype=np.int64)
    for i in range(p.shape[1] - 1):
        rank += (p[:, i + 1:] < p[:, i, None]).sum(1) * math.factorial(p.shape[1] - i - 1)
    return rank


def belongs(rank: np.ndarray, split: str) -> np.ndarray:
    if split == 'train':
        return rank % 10 < 8
    if split == 'validation':
        return rank % 10 == 8
    if split == 'test':
        return rank % 10 == 9
    raise ValueError(split)


def sample_rules(rng: np.random.Generator, count: int, n: int, split: str,
                 unique: bool = False) -> np.ndarray:
    found, seen = [], set()
    while len(found) < count:
        p = rng.random((max(64, (count - len(found)) * 12), n)).argsort(1)
        ids = permutation_rank(p)
        for row, rid in zip(p[belongs(ids, split)], ids[belongs(ids, split)]):
            if unique and int(rid) in seen:
                continue
            found.append(row)
            seen.add(int(rid))
            if len(found) == count:
                break
    return np.asarray(found, dtype=np.int64)


def final_answer(rules: np.ndarray, start: np.ndarray, length: int) -> np.ndarray:
    state = np.array(start, dtype=np.int64, copy=True)
    for _ in range(length):
        state = rules[np.arange(len(rules)), state]
    return state


@dataclass
class Episodes:
    rules: np.ndarray
    starts: np.ndarray
    row_order: np.ndarray

    def __len__(self):
        return len(self.starts)

    @property
    def rule_ids(self):
        return permutation_rank(self.rules)

    def take(self, selection) -> 'Episodes':
        return Episodes(self.rules[selection], self.starts[selection], self.row_order[selection])

    def inputs(self) -> tuple[torch.Tensor, torch.Tensor, torch.Tensor]:
        source = torch.from_numpy(self.row_order.astype(np.int64))
        destination = torch.from_numpy(np.take_along_axis(self.rules, self.row_order, axis=1).astype(np.int64))
        return source, destination, torch.from_numpy(self.starts.astype(np.int64))

    def target(self, length: int) -> torch.Tensor:
        return torch.from_numpy(final_answer(self.rules, self.starts, length).astype(np.int64))

    def save(self, path):
        np.savez_compressed(path, rules=self.rules.astype(np.uint8), starts=self.starts.astype(np.uint8),
                            row_order=self.row_order.astype(np.uint8), rule_ids=self.rule_ids)


def random_episodes(rng, batch: int, n: int, split: str) -> Episodes:
    rules = sample_rules(rng, batch, n, split)
    return Episodes(rules, rng.integers(n, size=batch), rng.random((batch, n)).argsort(1))


def evaluation_episodes(rng, count: int, n: int, split: str) -> Episodes:
    rules = sample_rules(rng, count, n, split, unique=True)
    starts = rng.random((count, n)).argsort(1)[:, :2]
    repeated = np.repeat(rules, 2, axis=0)
    return Episodes(repeated, starts.reshape(-1), rng.random((2 * count, n)).argsort(1))


def renamed_episodes(rng, episodes: Episodes) -> tuple[Episodes, np.ndarray]:
    renamed, starts, names = [], [], []
    for i in range(0, len(episodes), 2):
        f = episodes.rules[i]
        while True:
            rename = rng.permutation(len(f))
            changed = np.empty_like(f)
            changed[rename] = rename[f]
            if belongs(permutation_rank(changed[None]), 'test')[0]:
                break
        for j in range(i, i + 2):
            renamed.append(changed)
            starts.append(rename[episodes.starts[j]])
            names.append(rename)
    p = np.asarray(renamed)
    return Episodes(p, np.asarray(starts), rng.random(p.shape).argsort(1)), np.asarray(names)
