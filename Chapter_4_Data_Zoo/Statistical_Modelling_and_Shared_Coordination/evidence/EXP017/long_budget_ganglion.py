#!/usr/bin/env python3
"""Exploratory longer ganglion budget using original EXP017 OOF states."""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd
import torch

from paired_analysis import paired_difference
from train_source_level_six import (
    HERE, SEEDS, SIX, Ganglion, ShrunkRate, ganglion_fit,
    ganglion_predict, grouped_ci, lesion_controls, load_matrix, metrics,
    new_logistic, probability,
)


PARENT = HERE / "results/source_level_six/EXP017-SOURCE-TRAIN-001"
OUT = HERE / "results/source_level_six/EXP017-GANGLION-LONG-001"


def entropy(prob: np.ndarray) -> np.ndarray:
    p = np.clip(prob, 1e-7, 1 - 1e-7)
    return -(p * np.log(p) + (1 - p) * np.log1p(-p))


def recreate_states(cohort: pd.DataFrame, x: np.ndarray) -> tuple[dict, dict]:
    subsets = {name: np.where(cohort.split.to_numpy() == name)[0] for name in ("train", "validation", "test")}
    states = {name: np.zeros((len(idx), len(SIX), 4), np.float32) for name, idx in subsets.items()}
    original_oof = pd.read_parquet(PARENT / "train_channel_oof.parquet")
    original_train = cohort.iloc[subsets["train"]]
    if not original_oof[["targetId", "diseaseId", "label"]].reset_index(drop=True).equals(
        original_train[["targetId", "diseaseId", "label"]].reset_index(drop=True)
    ):
        raise RuntimeError("Original OOF pair order does not match fixed cohort")
    routing = json.loads((PARENT / "routing_weights.json").read_text())
    for j, datasource in enumerate(SIX):
        train_pred = original_oof[datasource + "__prediction"].to_numpy(float)
        train_available = original_oof[datasource + "__availability"].to_numpy(np.float32)
        if not np.array_equal(train_available, x[subsets["train"], j, 3]):
            raise RuntimeError(f"OOF availability changed: {datasource}")
        states["train"][:, j, 0] = train_pred
        states["train"][:, j, 1] = entropy(train_pred)
        states["train"][:, j, 2] = x[subsets["train"], j, 2]
        states["train"][:, j, 3] = train_available
        weights = np.asarray(routing["local"][datasource]["weights"], dtype=float)
        score_features = x[:, j, [0, 3]]
        count_features = x[:, j, [1, 3]]
        categories = x[:, j, 3].astype(int)
        score_model = new_logistic().fit(score_features[subsets["train"]], cohort.label.to_numpy()[subsets["train"]])
        count_model = new_logistic().fit(count_features[subsets["train"]], cohort.label.to_numpy()[subsets["train"]])
        rate_model = ShrunkRate(40.0).fit(categories[subsets["train"]], cohort.label.to_numpy()[subsets["train"]])
        for split in ("validation", "test"):
            idx = subsets[split]
            pred = np.column_stack((
                probability(score_model, score_features[idx]),
                probability(count_model, count_features[idx]),
                rate_model.predict(categories[idx]),
            )) @ weights
            pred = np.clip(pred, 1e-7, 1 - 1e-7)
            states[split][:, j, 0] = pred
            states[split][:, j, 1] = entropy(pred)
            states[split][:, j, 2] = x[idx, j, 2]
            states[split][:, j, 3] = x[idx, j, 3]
    return states, subsets


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=False)
    try:
        torch.set_num_threads(4)
        cohort, x, _ = load_matrix()
        states, subsets = recreate_states(cohort, x)
        label = cohort.label.to_numpy(np.int64)
        tr, va, te = (subsets[name] for name in ("train", "validation", "test"))
        original_test = pd.read_parquet(PARENT / "test_predictions.parquet")
        if not original_test[["targetId", "diseaseId", "label"]].reset_index(drop=True).equals(
            cohort.iloc[te][["targetId", "diseaseId", "label"]].reset_index(drop=True)
        ):
            raise RuntimeError("Original test pair order changed")
        device = "mps" if torch.backends.mps.is_available() else ("cuda" if torch.cuda.is_available() else "cpu")
        reconstruction = {}
        for seed in SEEDS:
            checkpoint = torch.load(PARENT / f"ganglion_seed_{seed}.pt", map_location="cpu", weights_only=True)
            old = Ganglion().to(device)
            old.load_state_dict(checkpoint["state_dict"])
            remade = ganglion_predict(old, states["test"], device)
            saved = original_test[f"ganglion_seed_{seed}"].to_numpy()
            maximum_error = float(np.max(np.abs(remade - saved)))
            reconstruction[str(seed)] = maximum_error
            if maximum_error > 1e-6:
                raise RuntimeError(f"Original state reconstruction failed: seed={seed}, error={maximum_error}")
        (OUT / "reconstruction_check.json").write_text(json.dumps(reconstruction, indent=2) + "\n")

        results = {}
        controls = {}
        diagnostics = {}
        prediction_frame = original_test[["targetId", "diseaseId", "label", "stat_moe"]].copy()
        for seed in SEEDS:
            model, device, diagnostic, delta = ganglion_fit(
                states["train"], label[tr], states["validation"], label[va],
                seed, OUT, max_epochs=1000, patience=100,
            )
            name = f"ganglion_seed_{seed}"
            val_pred = ganglion_predict(model, states["validation"], device)
            test_pred = ganglion_predict(model, states["test"], device)
            prediction_frame[name] = test_pred
            results[name] = {
                "validation": metrics(label[va], val_pred),
                "test": metrics(label[te], test_pred),
                "test_grouped_bootstrap_95ci": grouped_ci(label[te], test_pred, cohort.targetId.to_numpy()[te]),
            }
            ablations = {}
            for j, datasource in enumerate(SIX):
                damaged = states["test"].copy()
                damaged[:, j, :] = 0
                ablations[datasource] = metrics(label[te], ganglion_predict(model, damaged, device))["logloss"]
            shuffled = states["test"].copy()
            rng = np.random.default_rng(seed + 2000)
            for j in range(len(SIX)):
                shuffled[:, j, :] = states["test"][rng.permutation(len(te)), j, :]
            controls[name] = {
                "original_test_logloss": results[name]["test"]["logloss"],
                "shuffled_test_logloss": metrics(label[te], ganglion_predict(model, shuffled, device))["logloss"],
                "single_pipeline_ablation_logloss": ablations,
                "learned_direction_lesion": lesion_controls(model, device, delta, states["test"], label[te], seed),
            }
            diagnostics[name] = diagnostic

        prediction_frame.to_parquet(OUT / "test_predictions.parquet", index=False)
        paired = {
            f"ganglion_seed_{seed}_minus_stat_moe": paired_difference(
                prediction_frame, f"ganglion_seed_{seed}", "stat_moe"
            )
            for seed in SEEDS
        }
        (OUT / "metrics.json").write_text(json.dumps(results, indent=2) + "\n")
        (OUT / "controls.json").write_text(json.dumps(controls, indent=2) + "\n")
        (OUT / "ganglion_diagnostics.json").write_text(json.dumps(diagnostics, indent=2) + "\n")
        (OUT / "paired_vs_stat_moe.json").write_text(json.dumps(paired, indent=2) + "\n")
        best_seed = min(SEEDS, key=lambda s: results[f"ganglion_seed_{s}"]["validation"]["logloss"])
        (OUT / "protocol.json").write_text(json.dumps({
            "run_id": "EXP017-GANGLION-LONG-001",
            "parent_run": "EXP017-SOURCE-TRAIN-001",
            "amendment": "EXP017-AMEND-002",
            "input_oof": str(PARENT / "train_channel_oof.parquet"),
            "input_routing": str(PARENT / "routing_weights.json"),
            "seeds": SEEDS,
            "max_epochs": 1000,
            "validation_patience": 100,
            "selection": "best epoch and best seed by validation log loss only",
            "best_validation_seed": best_seed,
            "test_seen_before_amendment": True,
            "scope": "Post-result exploratory source-level budget extension; no independent confirmation",
        }, indent=2) + "\n")
        print(json.dumps({
            "reconstruction_max_error": reconstruction,
            "best_validation_seed": best_seed,
            "seed_results": {
                str(seed): {
                    "epoch": diagnostics[f"ganglion_seed_{seed}"]["best_epoch"],
                    "validation_logloss": results[f"ganglion_seed_{seed}"]["validation"]["logloss"],
                    "test_logloss": results[f"ganglion_seed_{seed}"]["test"]["logloss"],
                    "difference_from_stat_moe": paired[f"ganglion_seed_{seed}_minus_stat_moe"]["left_minus_right_logloss"],
                }
                for seed in SEEDS
            },
            "output_dir": str(OUT),
        }, indent=2))
    except Exception as exc:
        (OUT / "failure.json").write_text(json.dumps({
            "run_id": "EXP017-GANGLION-LONG-001",
            "error_type": type(exc).__name__,
            "error": str(exc),
            "existing_outputs": sorted(p.name for p in OUT.iterdir()),
        }, indent=2) + "\n")
        raise


if __name__ == "__main__":
    main()
