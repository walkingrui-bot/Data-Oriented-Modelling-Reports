#!/usr/bin/env python3
import argparse, copy, html, math, random, re, time
from collections import Counter
from pathlib import Path

import numpy as np
import pandas as pd
import torch
import torch.nn as nn
import torch.nn.functional as F

torch.set_num_threads(4)

VOCAB = 64
EMB = 8
HIDDEN = 48
SEQLEN = 48
BATCH = 48
STEPS = 900
SEEDS = [11, 22, 33]

class TokenGRU(nn.Module):
    def __init__(self, vocab=VOCAB, emb=EMB, hidden=HIDDEN):
        super().__init__()
        self.emb = nn.Embedding(vocab, emb)
        self.gru = nn.GRU(emb, hidden, batch_first=True)
        self.head = nn.Linear(hidden, vocab)

    def forward(self, x, h0=None):
        e = self.emb(x)
        h, hn = self.gru(e, h0)
        return self.head(h), h

def encode_language(text):
    cnt = Counter(text)
    chars = [c for c, _ in cnt.most_common(VOCAB - 1)]
    char2id = {c: i for i, c in enumerate(chars)}
    unk = VOCAB - 1
    ids = np.array([char2id.get(c, unk) for c in text], dtype=np.int64)
    return ids, chars

def entropy_counts(arr, vocab=VOCAB):
    c = np.bincount(arr, minlength=vocab).astype(float)
    p = c / c.sum()
    p = p[p > 0]
    return float(-(p * np.log(p)).sum())

def gen_symbolic(length=450_000, d=6, seed=0):
    rng = np.random.default_rng(seed)
    bits = rng.integers(0, 2, size=6, dtype=np.int8)
    arr = np.empty(length, dtype=np.int64)
    flip_ps = np.linspace(0.045, 0.27, 6)
    for t in range(length):
        arr[t] = sum(int(bits[j]) << j for j in range(6))
        for j in range(6):
            if j < d:
                if rng.random() < flip_ps[j]:
                    bits[j] ^= 1
            else:
                bits[j] = rng.integers(0, 2)
    return arr

def gen_symbolic_matched(length=450_000, seed=2468):
    rng = np.random.default_rng(seed)
    ps = np.array([0.50, 0.40, 0.30, 0.20, 0.15, 0.10])
    lam = np.array([0.85, 0.78, 0.71, 0.64, 0.57, 0.50])
    a = ps * (1 - lam)
    b = (1 - ps) * (1 - lam)
    bits = (rng.random(6) < ps).astype(np.int8)
    arr = np.empty(length, dtype=np.int64)
    for t in range(length):
        arr[t] = sum(int(bits[j]) << j for j in range(6))
        for j in range(6):
            if bits[j] == 0:
                if rng.random() < a[j]:
                    bits[j] = 1
            else:
                if rng.random() < b[j]:
                    bits[j] = 0
    return arr

def train_token(data, seed=0, model=None, steps=STEPS, lr=3e-3):
    if model is None:
        torch.manual_seed(seed)
        np.random.seed(seed)
        random.seed(seed)
        model = TokenGRU()
    else:
        model = copy.deepcopy(model)
        torch.manual_seed(seed)
        np.random.seed(seed)
        random.seed(seed)

    opt = torch.optim.AdamW(model.parameters(), lr=lr, weight_decay=1e-4)
    data_t = torch.from_numpy(data)
    N = len(data) - SEQLEN - 1
    last_loss = None

    for _ in range(steps):
        starts = torch.randint(0, N, (BATCH,))
        idx = starts[:, None] + torch.arange(SEQLEN + 1)[None, :]
        b = data_t[idx]
        x, y = b[:, :-1], b[:, 1:]
        logits, _ = model(x)
        loss = F.cross_entropy(logits.reshape(-1, VOCAB), y.reshape(-1))
        opt.zero_grad()
        loss.backward()
        torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0)
        opt.step()
        last_loss = float(loss.detach())
    return model, last_loss

def local_future_jacobian(model, seq, t, horizon=8):
    model.eval()
    seq_t = torch.as_tensor(seq, dtype=torch.long)
    with torch.no_grad():
        if t > 0:
            ep = model.emb(seq_t[:t]).unsqueeze(0)
            _, hprev = model.gru(ep)
        else:
            hprev = torch.zeros(1, 1, model.gru.hidden_size)
        efut = model.emb(seq_t[t + 1:t + horizon]).detach()
        e0 = model.emb(seq_t[t]).detach()

    def func(e):
        inp = torch.cat([e.unsqueeze(0), efut], dim=0).unsqueeze(0)
        out, _ = model.gru(inp, hprev)
        return out.reshape(-1)

    try:
        J = torch.autograd.functional.jacobian(
            func, e0, vectorize=True, strategy="forward-mode"
        )
    except Exception:
        eps = 1e-3
        cols = []
        for j in range(e0.numel()):
            d = torch.zeros_like(e0)
            d[j] = eps
            cols.append(((func(e0 + d) - func(e0 - d)) / (2 * eps)).detach())
        J = torch.stack(cols, dim=1)
    return J.detach()

def rank_metrics(s):
    s = np.asarray(s, float)
    e = s * s
    if e.sum() == 0:
        return dict(stable=0, pr=0, erank=0, d95=0, top2=0, top3=0)
    p = e / e.sum()
    stable = e.sum() / e.max()
    pr = e.sum() ** 2 / np.sum(e ** 2)
    erank = np.exp(-np.sum(p * np.log(p + 1e-12)))
    d95 = int(np.searchsorted(np.cumsum(p), 0.95) + 1)
    return dict(
        stable=float(stable),
        pr=float(pr),
        erank=float(erank),
        d95=d95,
        top2=float(p[:2].sum()),
        top3=float(p[:3].sum()),
    )

def evaluate(model, data, n=30, context=32, horizon=8, seed=0):
    rng = np.random.default_rng(seed)
    maxstart = len(data) - context - horizon - 2
    rows = []
    for start in rng.integers(0, maxstart, size=n):
        w = data[start:start + context + horizon + 1]
        J = local_future_jacobian(model, w, context, horizon)
        s = torch.linalg.svdvals(J).cpu().numpy()
        rows.append(rank_metrics(s))
    return pd.DataFrame(rows).median(numeric_only=True).to_dict()

def summarize(seed_rows):
    df = pd.DataFrame(seed_rows)
    out = {"condition": df["condition"].iloc[0]}
    for c in ["stable", "pr", "erank", "d95", "top2", "top3"]:
        out[c + "_mean"] = df[c].mean()
        out[c + "_sd"] = df[c].std()
    return out

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--corpus", default="LANGUAGE-CONTROL-DIMENSION-COLLAPSE-014_language_corpus.txt")
    ap.add_argument("--out", default="LANGUAGE-CONTROL-DIMENSION-COLLAPSE-014_reproduced.csv")
    args = ap.parse_args()

    text = Path(args.corpus).read_text(encoding="utf-8")
    lang, _ = encode_language(text)
    syn2 = gen_symbolic(d=2, seed=123)
    syn3 = gen_symbolic(d=3, seed=321)
    syn6 = gen_symbolic(d=6, seed=456)
    syn6m = gen_symbolic_matched()

    data = {
        "Language": lang,
        "Synthetic 2D": syn2,
        "Synthetic 3D": syn3,
        "Synthetic 6D uniform": syn6,
        "Synthetic 6D entropy+loss matched": syn6m,
    }

    print("Unigram entropy:")
    for k, v in data.items():
        print(k, entropy_counts(v))

    trained = {}
    rows = []

    for seed in SEEDS:
        torch.manual_seed(seed)
        r = TokenGRU()
        met = evaluate(r, lang, seed=4000 + seed)
        rows.append({"condition": "Random init", "seed": seed, **met})

        for i, (name, arr) in enumerate(data.items()):
            model, loss = train_token(arr, seed=seed)
            trained[(seed, name)] = model
            met = evaluate(model, arr, seed=5000 + 10 * i + seed)
            rows.append({"condition": name, "seed": seed, "loss": loss, **met})
            print(seed, name, "loss", round(loss, 4), "stable", round(met["stable"], 4))

    # Training-order interventions
    for seed in SEEDS:
        s6_to_lang, loss = train_token(
            lang, seed=100 + seed,
            model=trained[(seed, "Synthetic 6D uniform")],
            steps=900,
        )
        met = evaluate(s6_to_lang, lang, seed=8000 + seed)
        rows.append({"condition": "SYN6→LANG", "seed": seed, "loss": loss, **met})

        lang_to_s6, loss = train_token(
            syn6, seed=200 + seed,
            model=trained[(seed, "Language")],
            steps=900,
        )
        met = evaluate(lang_to_s6, syn6, seed=9000 + seed)
        rows.append({"condition": "LANG→SYN6", "seed": seed, "loss": loss, **met})

    raw = pd.DataFrame(rows)
    raw.to_csv(args.out, index=False)

    summaries = []
    for cond in raw["condition"].unique():
        sub = raw[raw["condition"] == cond]
        summaries.append(summarize(sub.to_dict("records")))
    summary = pd.DataFrame(summaries)
    summary_path = str(Path(args.out).with_name(Path(args.out).stem + "_summary.csv"))
    summary.to_csv(summary_path, index=False)
    print("\nSummary:")
    print(summary.to_string(index=False))
    print("\nWrote", args.out, "and", summary_path)

if __name__ == "__main__":
    main()
