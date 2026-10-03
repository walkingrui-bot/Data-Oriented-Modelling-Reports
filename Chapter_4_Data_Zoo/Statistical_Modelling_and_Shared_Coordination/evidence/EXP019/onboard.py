#!/usr/bin/env python3
"""EXP019 CGC frozen interface, full fine-tune, shuffle, and no-Europe-PMC control."""

from __future__ import annotations

import csv
import json
import math
import sys
import time
import traceback
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import torch
from torch import nn


HERE = Path(__file__).resolve().parent
PARENT = HERE.parent / "STAT-PSYMOE-EXP017-20261002-001"
sys.path.insert(0, str(PARENT))
from train_native_six import load_native  # noqa: E402
from train_source_level_six import Ganglion, SEEDS, SIX, ganglion_predict, metrics  # noqa: E402
from paired_analysis import paired_difference  # noqa: E402
from cgc_stat_models import STATE_FIELDS, rebuild_old_states, subsets_and_folds  # noqa: E402


RUN_ID = "EXP019-ONBOARD-001"
OUT = HERE / "results" / RUN_ID
OLD_RUN = PARENT / "results/native_six/EXP017-NATIVE-TRAIN-001"
MAX_EPOCHS = 1000
PATIENCE = 100
LEARNING_RATE = .002
ARMS = ("frozen", "full_retrain", "no_ep_frozen")
EP_INDEX = SIX.index("europepmc")


class ExtendedGanglion(nn.Module):
    def __init__(self, new_width: int):
        super().__init__()
        self.interfaces = nn.ModuleList(
            [nn.Sequential(nn.Linear(4, 16), nn.Tanh()) for _ in SIX] +
            [nn.Sequential(nn.Linear(new_width, 16), nn.Tanh())]
        )
        self.core = nn.Sequential(nn.Linear(16, 16), nn.Tanh())
        self.outcome = nn.Linear(16, 1)

    def forward(self, old: torch.Tensor, new: torch.Tensor) -> torch.Tensor:
        parts = torch.stack([self.interfaces[j](old[:, j, :]) for j in range(len(SIX))], dim=1)
        present = old[:, :, 3:4]
        old_sum = (parts * present).sum(dim=1)
        new_present = new[:, 3:4]
        new_sum = self.interfaces[len(SIX)](new) * new_present
        denominator = (present.sum(dim=1) + new_present).clamp_min(1.0)
        return self.outcome(self.core((old_sum + new_sum) / denominator)).squeeze(-1)


def old_checkpoint(seed: int):
    path = OLD_RUN / f"ganglion_seed_{seed}.pt"
    obj = torch.load(path, map_location="cpu", weights_only=True)
    return path, obj["state_dict"]


def extend(seed: int, width: int, arm: str, device: str):
    torch.manual_seed(seed + 1900)
    model = ExtendedGanglion(width)
    path, legacy = old_checkpoint(seed)
    missing, unexpected = model.load_state_dict(legacy, strict=False)
    expected = {f"interfaces.{len(SIX)}.0.weight", f"interfaces.{len(SIX)}.0.bias"}
    if set(missing) != expected or unexpected:
        raise RuntimeError(f"Old checkpoint structure mismatch: {missing}, {unexpected}")
    if arm != "full_retrain":
        for name, parameter in model.named_parameters():
            parameter.requires_grad = name.startswith(f"interfaces.{len(SIX)}.")
    trainable = sum(p.numel() for p in model.parameters() if p.requires_grad)
    return model.to(device), legacy, path, trainable


def predict(model: ExtendedGanglion, old: np.ndarray, new: np.ndarray, device: str):
    model.eval()
    with torch.no_grad():
        logits = model(torch.as_tensor(old, dtype=torch.float32, device=device),
                       torch.as_tensor(new, dtype=torch.float32, device=device))
        return torch.sigmoid(logits).detach().cpu().numpy()


def legacy_displacement(model: ExtendedGanglion, legacy: dict) -> dict:
    current = model.cpu().state_dict()
    detail = {}
    for prefix in ("interfaces.", "core.", "outcome."):
        if prefix == "interfaces.":
            keys = [k for k in legacy if k.startswith(prefix)]
        else:
            keys = [k for k in legacy if k.startswith(prefix)]
        squared = sum(float(torch.sum((current[k] - legacy[k]) ** 2)) for k in keys)
        detail[prefix.rstrip(".")] = math.sqrt(squared)
    exact = all(torch.equal(current[k], legacy[k]) for k in legacy)
    return {"old_parameters_exactly_equal": exact, "frobenius_by_component": detail}


def train_arm(seed: int, arm: str, old, new, y, idx, device: str):
    model, legacy, parent_path, trainable = extend(seed, new.shape[1], arm, device)
    tr, va = idx["train"], idx["validation"]
    old_tr = old["train"].copy()
    old_va = old["validation"].copy()
    if arm == "no_ep_frozen":
        old_tr[:, EP_INDEX, :] = 0
        old_va[:, EP_INDEX, :] = 0
    xt = torch.as_tensor(old_tr, dtype=torch.float32, device=device)
    nt = torch.as_tensor(new[tr], dtype=torch.float32, device=device)
    yt = torch.as_tensor(y[tr], dtype=torch.float32, device=device)
    xv = torch.as_tensor(old_va, dtype=torch.float32, device=device)
    nv = torch.as_tensor(new[va], dtype=torch.float32, device=device)
    yv = torch.as_tensor(y[va], dtype=torch.float32, device=device)
    optimizer = torch.optim.Adam((p for p in model.parameters() if p.requires_grad), lr=LEARNING_RATE)
    best_loss = math.inf
    best_epoch = 0
    best_state = None
    trace_path = OUT / f"trace_{arm}_seed_{seed}.csv"
    start = time.monotonic()
    with trace_path.open("w", newline="") as file:
        writer = csv.writer(file)
        writer.writerow(("epoch", "train_logloss", "validation_logloss"))
        for epoch in range(1, MAX_EPOCHS + 1):
            model.train()
            optimizer.zero_grad()
            loss = nn.functional.binary_cross_entropy_with_logits(model(xt, nt), yt)
            loss.backward()
            optimizer.step()
            model.eval()
            with torch.no_grad():
                val_loss = float(nn.functional.binary_cross_entropy_with_logits(model(xv, nv), yv).cpu())
            writer.writerow((epoch, float(loss.detach().cpu()), val_loss))
            file.flush()
            if val_loss < best_loss - 1e-7:
                best_loss, best_epoch = val_loss, epoch
                best_state = {k: v.detach().cpu().clone() for k, v in model.state_dict().items()}
            if epoch - best_epoch >= PATIENCE:
                break
    if best_state is None:
        raise RuntimeError(f"No saved best state for {arm} seed {seed}")
    model.load_state_dict(best_state)
    displacement = legacy_displacement(model, legacy)
    if arm != "full_retrain" and not displacement["old_parameters_exactly_equal"]:
        raise RuntimeError(f"Old parameters changed in frozen arm {arm} seed {seed}")
    if arm == "full_retrain" and displacement["old_parameters_exactly_equal"]:
        raise RuntimeError(f"Full retrain never changed old parameters, seed {seed}")
    if arm == "full_retrain":
        payload = {"run_id": RUN_ID, "arm": arm, "seed": seed, "best_epoch": best_epoch,
                   "parent_checkpoint_path": str(parent_path), "state_dict": best_state}
    else:
        payload = {"run_id": RUN_ID, "arm": arm, "seed": seed, "best_epoch": best_epoch,
                   "parent_checkpoint_path": str(parent_path),
                   "new_interface_state_dict": model.interfaces[len(SIX)].cpu().state_dict()}
    ckpt_path = OUT / f"{arm}_seed_{seed}.pt"
    torch.save(payload, ckpt_path)
    model.to(device)
    validation_pred = predict(model, old_va, new[va], device)
    diagnostic = {"arm": arm, "seed": seed, "parent_checkpoint_path": str(parent_path),
                  "checkpoint_path": str(ckpt_path), "best_epoch": best_epoch,
                  "epochs_run": epoch, "best_validation_logloss": best_loss,
                  "validation_metrics": metrics(y[va], validation_pred),
                  "trainable_parameters": trainable,
                  "total_parameters": sum(p.numel() for p in model.parameters()),
                  "training_wall_seconds": time.monotonic() - start,
                  "legacy_parameter_displacement": displacement,
                  "optimizer": {"type": "Adam", "learning_rate": LEARNING_RATE,
                                "max_epochs": MAX_EPOCHS, "validation_patience": PATIENCE}}
    return model, validation_pred, diagnostic


def shuffle_observed(new: np.ndarray, seed: int):
    permuted = new.copy()
    present = np.flatnonzero(new[:, 3] > 0)
    rng = np.random.default_rng(seed + 45000)
    permuted[present] = new[rng.permutation(present)]
    if not np.array_equal(permuted[:, 3], new[:, 3]):
        raise RuntimeError("Correspondence shuffle changed pair availability")
    return permuted


def compare(y, targets, left, right):
    frame = pd.DataFrame({"targetId": targets, "label": y,
                          "left": left, "right": right})
    return paired_difference(frame, "left", "right")


def subgroup(y, old, new, baseline, onboard):
    mask_old = old[:, :, 3].sum(axis=1) > 0
    mask_new = new[:, 3] > 0
    result = {}
    for name, mask in (("old_supported_new_present", mask_old & mask_new),
                       ("old_supported_new_absent", mask_old & ~mask_new),
                       ("new_present_old_absent", ~mask_old & mask_new)):
        if not mask.any():
            result[name] = {"pairs": 0, "events": 0}
            continue
        old_p = np.clip(baseline[mask], 1e-7, 1 - 1e-7)
        new_p = np.clip(onboard[mask], 1e-7, 1 - 1e-7)
        labels = y[mask]
        old_loss = -np.mean(labels * np.log(old_p) + (1 - labels) * np.log1p(-old_p))
        new_loss = -np.mean(labels * np.log(new_p) + (1 - labels) * np.log1p(-new_p))
        result[name] = {"pairs": int(mask.sum()), "events": int(y[mask].sum()),
                        "baseline_logloss": float(old_loss),
                        "onboard_logloss": float(new_loss),
                        "max_absolute_prediction_shift": float(np.max(np.abs(onboard[mask] - baseline[mask]))),
                        "mean_absolute_prediction_shift": float(np.mean(np.abs(onboard[mask] - baseline[mask])))}
    return result


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=False)
    completed = []
    try:
        torch.set_num_threads(4)
        cohort, raw, geometry, _ = load_native()
        y, targets, idx, folds = subsets_and_folds(cohort)
        old, reconstruction = rebuild_old_states(cohort, raw, geometry, idx, folds, y)
        (OUT / "old_reconstruction.json").write_text(json.dumps(reconstruction, indent=2) + "\n")
        frame = pd.read_parquet(HERE / "results/EXP019-CGC-STAT-001/cgc_exported_state.parquet")
        if not frame[["targetId", "diseaseId", "split"]].reset_index(drop=True).equals(
            cohort[["targetId", "diseaseId", "split"]].reset_index(drop=True)
        ):
            raise RuntimeError("CGC state order differs from old cohort")
        new = frame[list(STATE_FIELDS)].to_numpy(np.float32)
        if not np.isfinite(new).all():
            raise RuntimeError("Nonfinite CGC exported state")
        device = "mps" if torch.backends.mps.is_available() else (
            "cuda" if torch.cuda.is_available() else "cpu")
        models, validation, diagnostics = {}, {}, {}
        baseline_validation = {}
        baseline_no_ep_validation = {}
        for seed in SEEDS:
            _, legacy = old_checkpoint(seed)
            base = Ganglion().to(device)
            base.load_state_dict(legacy)
            baseline_validation[seed] = ganglion_predict(base, old["validation"], device)
            without_ep = old["validation"].copy()
            without_ep[:, EP_INDEX, :] = 0
            baseline_no_ep_validation[seed] = ganglion_predict(base, without_ep, device)
            for arm in ARMS:
                model, prediction, diagnostic = train_arm(seed, arm, old, new, y, idx, device)
                models[(arm, seed)] = model
                validation[(arm, seed)] = prediction
                diagnostics[f"{arm}_seed_{seed}"] = diagnostic
                completed.append(f"{arm}_seed_{seed}")
                print(json.dumps({"completed": completed[-1], "epoch": diagnostic["best_epoch"],
                                  "validation_logloss": diagnostic["validation_metrics"]["logloss"]}),
                      flush=True)
        selected = {arm: min(SEEDS, key=lambda seed: diagnostics[f"{arm}_seed_{seed}"]["validation_metrics"]["logloss"])
                    for arm in ARMS}
        selection = {"run_id": RUN_ID, "device": device, "candidate_seeds": SEEDS,
                     "selected_by_validation_only": selected,
                     "validation_baseline": {str(seed): metrics(y[idx["validation"]], baseline_validation[seed])
                                             for seed in SEEDS},
                     "validation_no_ep_baseline": {str(seed): metrics(y[idx["validation"]], baseline_no_ep_validation[seed])
                                                   for seed in SEEDS},
                     "arm_diagnostics": diagnostics,
                     "test_performance_computed_at_selection_time": False}
        (OUT / "validation_selection.json").write_text(
            json.dumps(selection, ensure_ascii=False, indent=2, allow_nan=False) + "\n")
        val_frame = cohort.iloc[idx["validation"]][["targetId", "diseaseId", "label"]].copy()
        for seed in SEEDS:
            val_frame[f"old_seed_{seed}"] = baseline_validation[seed]
            val_frame[f"old_no_ep_seed_{seed}"] = baseline_no_ep_validation[seed]
            for arm in ARMS:
                val_frame[f"{arm}_seed_{seed}"] = validation[(arm, seed)]
        val_frame.to_parquet(OUT / "validation_predictions.parquet", index=False)

        # Only now read/evaluate the previously viewed test labels. These results
        # are retrospective development descriptors and cannot select an arm/seed.
        te = idx["test"]
        test_frame = cohort.iloc[te][["targetId", "diseaseId", "label"]].copy()
        base_test, base_no_ep_test = {}, {}
        test_metrics, controls = {}, {}
        old_no_ep_test = old["test"].copy()
        old_no_ep_test[:, EP_INDEX, :] = 0
        for seed in SEEDS:
            _, legacy = old_checkpoint(seed)
            base = Ganglion().to(device)
            base.load_state_dict(legacy)
            base_test[seed] = ganglion_predict(base, old["test"], device)
            base_no_ep_test[seed] = ganglion_predict(base, old_no_ep_test, device)
            test_frame[f"old_seed_{seed}"] = base_test[seed]
            test_frame[f"old_no_ep_seed_{seed}"] = base_no_ep_test[seed]
            test_metrics[f"old_seed_{seed}"] = metrics(y[te], base_test[seed])
            test_metrics[f"old_no_ep_seed_{seed}"] = metrics(y[te], base_no_ep_test[seed])
            for arm in ARMS:
                model = models[(arm, seed)]
                old_input = old_no_ep_test if arm == "no_ep_frozen" else old["test"]
                p = predict(model, old_input, new[te], device)
                test_frame[f"{arm}_seed_{seed}"] = p
                test_metrics[f"{arm}_seed_{seed}"] = metrics(y[te], p)
                reference = base_no_ep_test[seed] if arm == "no_ep_frozen" else base_test[seed]
                controls[f"{arm}_seed_{seed}"] = {
                    "paired_minus_own_old_baseline": compare(y[te], targets[te], p, reference),
                    "legacy_preservation_subsets": subgroup(y[te], old_input, new[te], reference, p),
                }
                if arm == "frozen":
                    shuf = predict(model, old_input, shuffle_observed(new[te], seed), device)
                    test_frame[f"frozen_shuffle_seed_{seed}"] = shuf
                    controls[f"{arm}_seed_{seed}"]["correspondence_shuffle"] = {
                        "available_pairs": int(np.sum(new[te, 3] > 0)),
                        "test_original_logloss": test_metrics[f"{arm}_seed_{seed}"]["logloss"],
                        "test_shuffled_logloss": metrics(y[te], shuf)["logloss"],
                        "paired_shuffled_minus_original": compare(y[te], targets[te], shuf, p),
                    }
        test_frame.to_parquet(OUT / "test_predictions.parquet", index=False)
        best_frozen = selected["frozen"]
        best_full = selected["full_retrain"]
        best_no_ep = selected["no_ep_frozen"]
        final_comparisons = {
            "frozen_best_minus_old_same_seed": controls[f"frozen_seed_{best_frozen}"]["paired_minus_own_old_baseline"],
            "full_best_minus_old_same_seed": controls[f"full_retrain_seed_{best_full}"]["paired_minus_own_old_baseline"],
            "full_best_minus_frozen_best": compare(y[te], targets[te],
                test_frame[f"full_retrain_seed_{best_full}"].to_numpy(),
                test_frame[f"frozen_seed_{best_frozen}"].to_numpy()),
            "no_ep_frozen_best_minus_no_ep_old_same_seed":
                controls[f"no_ep_frozen_seed_{best_no_ep}"]["paired_minus_own_old_baseline"],
        }
        (OUT / "test_metrics.json").write_text(json.dumps({
            "qualification": "retrospective development; test was previously viewed",
            "selected_by_validation_only": selected, "metrics": test_metrics,
            "best_arm_paired_comparisons": final_comparisons,
        }, ensure_ascii=False, indent=2, allow_nan=False) + "\n")
        (OUT / "controls.json").write_text(json.dumps(controls, ensure_ascii=False, indent=2,
                                                        allow_nan=False) + "\n")
        names = ["Old six", "CGC frozen", "CGC full retrain", "No EP old", "No EP plus CGC"]
        values = [test_metrics[f"old_seed_{best_frozen}"]["logloss"],
                  test_metrics[f"frozen_seed_{best_frozen}"]["logloss"],
                  test_metrics[f"full_retrain_seed_{best_full}"]["logloss"],
                  test_metrics[f"old_no_ep_seed_{best_no_ep}"]["logloss"],
                  test_metrics[f"no_ep_frozen_seed_{best_no_ep}"]["logloss"]]
        fig, ax = plt.subplots(figsize=(7.4, 3.7))
        ax.barh(names, values, color=["#798a90", "#397d87", "#356f92", "#ad8d5a", "#9e6b55"])
        ax.invert_yaxis()
        ax.set_xlabel("Test Bernoulli log-loss (retrospective development)")
        ax.set_title("EXP019 Cancer Gene Census 6 to 7 source extension")
        for i, value in enumerate(values):
            ax.text(value + .0008, i, f"{value:.6f}", va="center", fontsize=8)
        ax.set_xlim(0, max(values) * 1.15)
        fig.tight_layout()
        fig.savefig(OUT / "test_logloss_comparison.png", dpi=180)
        plt.close(fig)
        (OUT / "protocol_and_environment.json").write_text(json.dumps({
            "run_id": RUN_ID, "research_id": "STAT-PSYMOE-EXP019-20261002-001",
            "source": "cancer_gene_census", "release": "26.06",
            "terminal_cohort": str(PARENT / "cohort_mapped.parquet"),
            "old_checkpoint_dir": str(OLD_RUN), "new_state": str(HERE / "results/EXP019-CGC-STAT-001/cgc_exported_state.parquet"),
            "old_state_rebuilt_in_memory": True, "old_state_reconstruction": str(OUT / "old_reconstruction.json"),
            "source_state_fields": STATE_FIELDS,
            "frozen_checkpoint_contents": "new interface only; restore requires named EXP017 old checkpoint",
            "full_retrain_initialization": "saved EXP017 checkpoint plus randomly initialized new interface; all parameters trainable",
            "training": {"seeds": SEEDS, "max_epochs": MAX_EPOCHS, "patience": PATIENCE,
                         "optimizer": "Adam", "lr": LEARNING_RATE, "batch": "all train pairs"},
            "device": device, "test_role": "retrospective development only; no test-driven selection",
        }, ensure_ascii=False, indent=2) + "\n")
        print(json.dumps({"selected_by_validation": selected,
                          "test_logloss": {name: value["logloss"] for name, value in test_metrics.items()},
                          "paired_best": final_comparisons}, ensure_ascii=False), flush=True)
    except Exception as exc:
        (OUT / "failure.json").write_text(json.dumps({
            "run_id": RUN_ID, "error_type": type(exc).__name__, "error": str(exc),
            "traceback": traceback.format_exc(), "completed_arms": completed,
            "existing_outputs": sorted(p.name for p in OUT.iterdir()),
        }, ensure_ascii=False, indent=2) + "\n")
        raise


if __name__ == "__main__":
    main()
