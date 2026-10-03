#!/usr/bin/env python3
"""EXP057: controlled retrospective capacity comparison on real train/validation pairs."""

from __future__ import annotations

import csv
import io
import json
import math
import sys
import time
import traceback
from pathlib import Path

import numpy as np
import pandas as pd
import torch
from torch import nn


HERE = Path(__file__).resolve().parent
P17 = HERE.parent / "STAT-PSYMOE-EXP017-20261002-001"
P19 = HERE.parent / "STAT-PSYMOE-EXP019-20261002-001"
OLD = P17 / "results/native_six/EXP017-NATIVE-TRAIN-001"
sys.path.insert(0, str(P17))
from train_native_six import native_geometry  # noqa: E402
from train_source_level_six import (  # noqa: E402
    Ganglion, SEEDS, SIX, ShrunkRate, ganglion_predict, new_logistic,
    probability, split_name,
)


RUN_ID = "EXP057-CAPACITY-001"
MAX_EPOCHS = 2000
PATIENCE = 200
LR = 0.002
MAX_SECONDS = 90 * 60
ARMS = {"B16": (16, 16), "C32": (16, 32), "F32": (32, 32),
        "C64": (16, 64), "F64": (64, 64)}


class CapacityGanglion(nn.Module):
    def __init__(self, interface_width: int, core_width: int):
        super().__init__()
        self.interfaces = nn.ModuleList([
            nn.Sequential(nn.Linear(4, interface_width), nn.Tanh()) for _ in SIX
        ])
        self.core = nn.Sequential(nn.Linear(interface_width, core_width), nn.Tanh())
        self.outcome = nn.Linear(core_width, 1)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        parts = torch.stack([module(x[:, j, :]) for j, module in enumerate(self.interfaces)], dim=1)
        available = x[:, :, 3:4]
        combined = (parts * available).sum(dim=1) / available.sum(dim=1).clamp_min(1.0)
        return self.outcome(self.core(combined)).squeeze(-1)


def make_development_states():
    cohort = pd.read_parquet(P17 / "cohort_mapped.parquet").sort_values(
        ["targetId", "diseaseId"]
    ).reset_index(drop=True)
    if len(cohort) != 26235:
        raise RuntimeError("Original cohort row count changed")
    cohort["split"] = cohort.targetId.map(split_name)
    dev = cohort.loc[cohort.split.isin(("train", "validation"))].reset_index(drop=True)
    index = {name: np.flatnonzero(dev.split.to_numpy() == name)
             for name in ("train", "validation")}
    tr, va = index["train"], index["validation"]
    if len(tr) != 17702 or len(va) != 4132:
        raise RuntimeError("Train/validation pair support changed")
    if set(dev.targetId.iloc[tr]) & set(dev.targetId.iloc[va]):
        raise RuntimeError("Target crosses train/validation")
    y = dev.label.to_numpy(dtype=np.float32)
    raw = np.zeros((len(dev), len(SIX), 4), dtype=np.float32)
    geometry = {}
    key = dev[["targetId", "diseaseId"]]
    for j, datasource in enumerate(SIX):
        source = pd.read_parquet(P17 / f"native_{datasource}_pair_features.parquet")
        if datasource == "eva":
            categories = pd.read_parquet(P17 / "native_eva_category_features.parquet")
            source = source.merge(categories, on=["targetId", "diseaseId"], how="left", validate="one_to_one")
        merged = key.merge(source, on=["targetId", "diseaseId"], how="left", validate="one_to_one", sort=False)
        available = merged.native_evidence_rows.notna().to_numpy(np.float32)
        raw[:, j, 0] = merged.max_native_score.fillna(0).to_numpy(np.float32)
        raw[:, j, 1] = np.log1p(merged.native_evidence_rows.fillna(0).to_numpy(np.float32))
        raw[:, j, 2] = merged.mean_native_score.fillna(0).to_numpy(np.float32)
        raw[:, j, 3] = available
        geometry[datasource], _ = native_geometry(datasource, merged, available)
    if not np.isfinite(raw).all() or (raw[:, :, 0] < 0).any() or (raw[:, :, 0] > 1).any():
        raise RuntimeError("Invalid source state")

    route = json.loads((OLD / "routing_weights.json").read_text())
    original_oof = pd.read_parquet(OLD / "train_channel_oof.parquet")
    expected_key = dev.iloc[tr][["targetId", "diseaseId", "label"]].reset_index(drop=True)
    if not original_oof[["targetId", "diseaseId", "label"]].reset_index(drop=True).equals(expected_key):
        raise RuntimeError("Old train OOF pair order changed")
    states = {"train": np.zeros((len(tr), len(SIX), 4), np.float32),
              "validation": np.zeros((len(va), len(SIX), 4), np.float32)}
    train_prediction_max = 0.0
    for j, datasource in enumerate(SIX):
        local = route["local"][datasource]
        scale = float(local["coverage_scale_train_q95"])
        train_prediction = original_oof[datasource + "__prediction"].to_numpy(np.float32)
        train_available = original_oof[datasource + "__availability"].to_numpy(np.float32)
        train_prediction_max = max(train_prediction_max, float(np.max(np.abs(
            train_available - raw[tr, j, 3]
        ))))
        states["train"][:, j, 0] = train_prediction
        states["train"][:, j, 1] = -(
            train_prediction * np.log(train_prediction) +
            (1 - train_prediction) * np.log1p(-train_prediction)
        )
        states["train"][:, j, 2] = np.clip(raw[tr, j, 1] / scale, 0, 2)
        states["train"][:, j, 3] = train_available

        score_features = np.column_stack((raw[:, j, 0], raw[:, j, 2], raw[:, j, 3]))
        category = np.where(raw[:, j, 3] == 0, 0,
                            np.where(raw[:, j, 0] == 0, 1, 2)).astype(int)
        score = new_logistic().fit(score_features[tr], y[tr])
        native = new_logistic(c=0.5).fit(geometry[datasource][tr], y[tr])
        shrink = ShrunkRate(40.0).fit(category[tr], y[tr])
        expert = np.column_stack((
            probability(score, score_features[va]),
            probability(native, geometry[datasource][va]),
            shrink.predict(category[va]),
        ))
        pred = np.clip(expert @ np.asarray(local["weights"], dtype=float), 1e-7, 1 - 1e-7)
        states["validation"][:, j, 0] = pred
        states["validation"][:, j, 1] = -(pred * np.log(pred) + (1 - pred) * np.log1p(-pred))
        states["validation"][:, j, 2] = np.clip(raw[va, j, 1] / scale, 0, 2)
        states["validation"][:, j, 3] = raw[va, j, 3]
    if train_prediction_max > 0:
        raise RuntimeError(f"Train availability differs: {train_prediction_max}")

    old_val = pd.read_parquet(P19 / "results/EXP019-ONBOARD-001/validation_predictions.parquet")
    if not old_val[["targetId", "diseaseId", "label"]].reset_index(drop=True).equals(
        dev.iloc[va][["targetId", "diseaseId", "label"]].reset_index(drop=True)
    ):
        raise RuntimeError("Old validation pair order changed")
    old_max = {}
    for seed in SEEDS:
        original = torch.load(OLD / f"ganglion_seed_{seed}.pt", map_location="cpu", weights_only=True)
        model = Ganglion()
        model.load_state_dict(original["state_dict"])
        rebuilt = ganglion_predict(model, states["validation"], "cpu")
        old_max[str(seed)] = float(np.max(np.abs(
            rebuilt - old_val[f"old_seed_{seed}"].to_numpy(dtype=float)
        )))
    if max(old_max.values()) > 2e-6:
        raise RuntimeError(f"Validation state reconstruction mismatch: {old_max}")
    summary = {"run_id": RUN_ID, "train_pairs": len(tr), "validation_pairs": len(va),
               "train_targets": dev.targetId.iloc[tr].nunique(),
               "validation_targets": dev.targetId.iloc[va].nunique(),
               "train_events": int(y[tr].sum()), "validation_events": int(y[va].sum()),
               "old_validation_prediction_max_abs_difference": old_max,
               "train_availability_max_abs_difference": train_prediction_max,
               "test_split_accessed_for_evaluation": False,
               "old_training_state_reused_by_path": str(OLD / "train_channel_oof.parquet"),
               "old_checkpoint_paths": [str(OLD / f"ganglion_seed_{s}.pt") for s in SEEDS]}
    (HERE / "STATE_RECONSTRUCTION.json").write_text(json.dumps(summary, indent=2) + "\n")
    return dev, y, index, states


def fit_one(arm: str, seed: int, xtr, ytr, xva, yva, device: str, started: float):
    if time.monotonic() - started > MAX_SECONDS:
        raise TimeoutError("EXP057 total 90-minute budget reached before next model")
    interface_width, core_width = ARMS[arm]
    torch.manual_seed(seed)
    model = CapacityGanglion(interface_width, core_width).to(device)
    parameter_count = sum(p.numel() for p in model.parameters())
    xt = torch.as_tensor(xtr, dtype=torch.float32, device=device)
    yt = torch.as_tensor(ytr, dtype=torch.float32, device=device)
    xv = torch.as_tensor(xva, dtype=torch.float32, device=device)
    yv = torch.as_tensor(yva, dtype=torch.float32, device=device)
    optimizer = torch.optim.Adam(model.parameters(), lr=LR)
    best = math.inf
    best_epoch = 0
    best_state = None
    trace_path = HERE / "TRACES" / f"{arm}_seed_{seed}.csv"
    fit_start = time.monotonic()
    with trace_path.open("x", newline="") as file:
        writer = csv.writer(file)
        writer.writerow(("epoch", "train_logloss", "validation_logloss"))
        for epoch in range(1, MAX_EPOCHS + 1):
            model.train()
            optimizer.zero_grad()
            loss = nn.functional.binary_cross_entropy_with_logits(model(xt), yt)
            loss.backward()
            optimizer.step()
            model.eval()
            with torch.no_grad():
                val_loss = float(nn.functional.binary_cross_entropy_with_logits(model(xv), yv).cpu())
            writer.writerow((epoch, float(loss.detach().cpu()), val_loss))
            if val_loss < best - 1e-7:
                best, best_epoch = val_loss, epoch
                best_state = {k: v.detach().cpu().clone() for k, v in model.state_dict().items()}
            if epoch % 250 == 0 or epoch - best_epoch >= PATIENCE:
                file.flush()
                print(f"{arm} seed={seed} epoch={epoch} best={best:.8f} at {best_epoch}", flush=True)
            if epoch - best_epoch >= PATIENCE:
                break
            if time.monotonic() - started > MAX_SECONDS:
                raise TimeoutError("EXP057 total 90-minute budget reached during model")
    if best_state is None:
        raise RuntimeError("No best model state")
    model.load_state_dict(best_state)
    state_path = HERE / "MODEL_STATES" / f"{arm}_seed_{seed}.pt"
    with state_path.open("xb") as file:
        torch.save({"run_id": RUN_ID, "arm": arm, "seed": seed,
                    "best_epoch": best_epoch, "state_dict": best_state}, file)
    with torch.no_grad():
        pred = torch.sigmoid(model(xv)).detach().cpu().numpy()
    per_pair = -(yva * np.log(np.clip(pred, 1e-7, 1 - 1e-7)) +
                 (1 - yva) * np.log(np.clip(1 - pred, 1e-7, 1 - 1e-7)))
    result = {"arm": arm, "seed": seed, "interface_width": interface_width,
              "core_width": core_width, "total_parameters": parameter_count,
              "core_weight_shape": [core_width, interface_width],
              "best_epoch": best_epoch, "epochs_run": epoch,
              "validation_logloss": float(np.mean(per_pair)),
              "best_validation_logits_loss": best,
              "last_validation_logloss": val_loss,
              "fit_seconds": time.monotonic() - fit_start,
              "device": device, "trace_path": str(trace_path),
              "checkpoint_path": str(state_path)}
    (HERE / "DIAGNOSTICS" / f"{arm}_seed_{seed}.json").write_text(
        json.dumps(result, indent=2) + "\n"
    )
    print("COMPLETE", arm, seed, result["validation_logloss"], result["fit_seconds"], flush=True)
    return result, pred


def gate(rows, wide: str, baseline: str):
    diff = {str(seed): rows[wide][seed]["validation_logloss"] -
            rows[baseline][seed]["validation_logloss"] for seed in SEEDS}
    median = float(np.median(list(diff.values())))
    count = sum(value <= -0.0005 for value in diff.values())
    return {"comparison": f"{wide}_minus_{baseline}", "same_seed_differences": diff,
            "median_difference": median, "seeds_improving_by_at_least_0_0005": count,
            "gate_pass": median <= -0.0010 and count >= 2}


def main():
    for name in ("STATE_RECONSTRUCTION.json", "METRICS.json", "FAILURE.json"):
        if (HERE / name).exists():
            raise FileExistsError(f"Preserve existing attempt output: {name}")
    for name in ("MODEL_STATES", "TRACES", "DIAGNOSTICS"):
        (HERE / name).mkdir(exist_ok=False)
    started = time.monotonic()
    torch.set_num_threads(4)
    device = "mps" if torch.backends.mps.is_available() else ("cuda" if torch.cuda.is_available() else "cpu")
    dev, y, index, states = make_development_states()
    tr, va = index["train"], index["validation"]
    print("STATES_RECONSTRUCTED", len(tr), len(va), device, flush=True)
    rows = {}
    preds = dev.iloc[va][["targetId", "diseaseId", "label"]].copy().reset_index(drop=True)
    for arm in ("B16", "C32", "F32"):
        rows[arm] = {}
        for seed in SEEDS:
            rows[arm][seed], pred = fit_one(arm, seed, states["train"], y[tr],
                                             states["validation"], y[va], device, started)
            preds[f"{arm}_seed_{seed}"] = pred
    gates = {arm: gate(rows, arm, "B16") for arm in ("C32", "F32")}
    for parent, wider in (("C32", "C64"), ("F32", "F64")):
        if gates[parent]["gate_pass"]:
            rows[wider] = {}
            for seed in SEEDS:
                rows[wider][seed], pred = fit_one(wider, seed, states["train"], y[tr],
                                                  states["validation"], y[va], device, started)
                preds[f"{wider}_seed_{seed}"] = pred
            gates[wider] = gate(rows, wider, parent)
    metrics = {"run_id": RUN_ID, "qualification": "retrospective development only; previously seen test not accessed",
               "device": device, "optimizer": "Adam", "learning_rate": LR,
               "max_epochs": MAX_EPOCHS, "patience": PATIENCE, "seeds": list(SEEDS),
               "real_train_pairs": len(tr), "real_validation_pairs": len(va),
               "real_train_targets": dev.targetId.iloc[tr].nunique(),
               "real_validation_targets": dev.targetId.iloc[va].nunique(),
               "arms": {arm: {str(seed): detail for seed, detail in by_seed.items()}
                        for arm, by_seed in rows.items()},
               "gates": gates, "total_seconds": time.monotonic() - started,
               "stat_moe_original_validation_logloss_report_only": 0.20008862,
               "any_best_epoch_at_cap": any(detail["best_epoch"] == MAX_EPOCHS
                                            for by_seed in rows.values() for detail in by_seed.values())}
    preds.to_parquet(HERE / "VALIDATION_PREDICTIONS.parquet", index=False)
    (HERE / "METRICS.json").write_text(json.dumps(metrics, indent=2) + "\n")
    print("GATES", json.dumps(gates), flush=True)
    print("TOTAL_SECONDS", metrics["total_seconds"], flush=True)


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        if not (HERE / "FAILURE.json").exists():
            (HERE / "FAILURE.json").write_text(json.dumps({
                "run_id": RUN_ID, "error_type": type(exc).__name__, "error": str(exc),
                "traceback": traceback.format_exc(),
                "existing_direct_outputs": sorted(p.name for p in HERE.iterdir()),
            }, indent=2) + "\n")
        raise
