"""Plot EXP019 frozen train/validation eligibility without test selection data."""

import json
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np


HERE = Path(__file__).resolve().parent
data = json.loads((HERE / "eligibility_train_validation.json").read_text())["candidates"]
rows = sorted(data, key=lambda x: (-x.get("train", {}).get("pairs", -1), x["datasource"]))
names = [row["datasource"].replace("_", " ") for row in rows]
y = np.arange(len(rows))
fig, axes = plt.subplots(1, 4, figsize=(13.8, 5.0), sharey=True)
for ax, split, key, threshold, title in (
    (axes[0], "train", "pairs", 200, "Train pairs"),
    (axes[1], "validation", "pairs", 50, "Validation pairs"),
    (axes[2], "train", "events", 10, "Train events"),
    (axes[3], "validation", "events", 3, "Validation events"),
):
    values = [row.get(split, {}).get(key, 0) for row in rows]
    colors = ["#2f7f80" if row["eligibility"] == "PASS" else "#aeb6ba" for row in rows]
    ax.barh(y, values, color=colors, height=.67)
    ax.axvline(threshold, color="#9a5c37", linestyle="--", linewidth=1)
    ax.set_title(title)
    ax.set_xlim(0, max(max(values) * 1.1, threshold * 1.15))
    ax.grid(axis="x", alpha=.18)
    ax.set_axisbelow(True)
    for i, value in enumerate(values):
        ax.text(value + max(max(values), threshold) * .012, i, str(value), va="center", fontsize=7)
axes[0].set_yticks(y, names, fontsize=8)
axes[0].invert_yaxis()
fig.suptitle("EXP019 native source eligibility  |  Open Targets 26.06  |  train and validation only")
fig.text(.5, .02, "Dashed lines are the preregistered gates. State variability is checked separately.",
         ha="center", fontsize=8, color="#4d5559")
fig.subplots_adjust(left=.19, right=.99, top=.87, bottom=.10, wspace=.12)
fig.savefig(HERE / "source_support.png", dpi=180)
plt.close(fig)
