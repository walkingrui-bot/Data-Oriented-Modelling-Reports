#!/usr/bin/env python3
"""Redraw the supplied TOOL-CALL-002 schematic with nonoverlapping labels.

This is a presentation change, with no new experimental data. The original
PNG remains byte-for-byte preserved under evidence/cloud and figures.
"""
from pathlib import Path
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch

root = Path(__file__).resolve().parents[2]
fig, ax = plt.subplots(figsize=(12, 3.2))
ax.set(xlim=(0, 12), ylim=(0, 3.2))
ax.axis("off")
ax.text(6, 2.95, "Tool call as a guarded partial operator", ha="center",
        va="center", fontsize=15, weight="bold")

def box(x, y, width, height, label, face):
    ax.add_patch(FancyBboxPatch((x, y), width, height,
                 boxstyle="round,pad=0.025,rounding_size=0.06",
                 facecolor=face, edgecolor="#56646d", linewidth=1))
    ax.text(x+width/2, y+height/2, label, ha="center", va="center", fontsize=10)

labels = ["Language\nstate x", "Mode\nCALL / ASK / ABSTAIN",
          "Registry\nTool k available?", "Bindings\nRequired args complete?",
          "Partial\noperator", "World\nstate update"]
for i, label in enumerate(labels):
    x = .1 + 2*i
    box(x, 1.62, 1.72, .72, label, "#e5edf3")
    if i < 5:
        ax.add_patch(FancyArrowPatch((x+1.75, 1.98), (x+1.98, 1.98),
                     arrowstyle="-|>", mutation_scale=12, color="#56646d"))
for x, label in [(.5, "Irrelevant registry\nABSTAIN"),
                 (4.25, "Missing function\nWAIT / REQUEST"),
                 (8, "Missing parameter\nASK / CLARIFY")]:
    box(x, .35, 3.4, .75, label, "#f5f7f8")

fig.subplots_adjust(left=.01, right=.99, bottom=.02, top=.99)
fig.savefig(root/"figures/partial_operator_redrawn.png", dpi=220, facecolor="white")
plt.close(fig)
print("Created the attributed partial-operator schematic.")
