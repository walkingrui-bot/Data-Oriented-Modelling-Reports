#!/usr/bin/env python3
"""Plot the observed EXP018 cohort support without inventing model results."""

import json
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

HERE = Path(__file__).resolve().parent
data = json.loads((HERE / "cohort_support.json").read_text())["three_source_union"]
splits = ("train", "validation", "test")
negative = [data[s]["negative_pairs"] for s in splits]
positive = [data[s]["positive_pairs"] for s in splits]
x = np.arange(len(splits))
fig, ax = plt.subplots(figsize=(6.4, 3.4))
ax.bar(x, negative, color="#427d89", label="Negative terminal pairs")
ax.bar(x, positive, bottom=negative, color="#b97450", label="Positive terminal pairs")
ax.set_xticks(x, splits)
ax.set_ylabel("Pairs with any of the three new sources")
ax.set_ylim(0, max(negative) + 3)
ax.set_title("EXP018 fixed-cohort support: ClinGen + G2P + Orphanet")
ax.legend(frameon=False, loc="upper right")
for i, (neg, pos) in enumerate(zip(negative, positive)):
    ax.text(i, neg + pos + .2, f"{neg + pos} pairs; {pos} positive", ha="center", fontsize=9)
fig.tight_layout()
fig.savefig(HERE / "cohort_support.png", dpi=180)
