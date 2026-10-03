#!/usr/bin/env python3
"""Exploratory six-datasource source-level training on the fixed 26.06 cache.

This is not a native raw-evidence or point-in-time benchmark.
"""

from __future__ import annotations

import argparse
import copy
import csv
import json
import math
import platform
from importlib.metadata import version
from pathlib import Path

import duckdb
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import torch
from scipy.special import expit, logit
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import average_precision_score, brier_score_loss, log_loss, roc_auc_score
from sklearn.model_selection import StratifiedGroupKFold
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler
from torch import nn


HERE = Path(__file__).resolve().parent
SIX = (
    "gwas_credible_sets",
    "gene_burden",
    "eva",
    "expression_atlas",
    "impc",
    "europepmc",
)
SEEDS = (101, 202, 303)
BOOTSTRAPS = 300


def fnv1a32(value: str) -> int:
    h = 2166136261
    for character in str(value):
        h = ((h ^ ord(character)) * 16777619) & 0xFFFFFFFF
    return h


def split_name(target: str) -> str:
    bucket = fnv1a32(target) % 100
    return "train" if bucket < 70 else ("validation" if bucket < 85 else "test")


def load_matrix() -> tuple[pd.DataFrame, np.ndarray, dict]:
    manifest = json.loads((HERE / "cache_manifest.json").read_text())
    if manifest["release"] != "26.06" or manifest["association"]["cohort_restricted_rows"] != 15153:
        raise RuntimeError("Cache identity or expected row count changed")
    con = duckdb.connect()
    cohort = con.execute("SELECT * FROM read_parquet(?) ORDER BY targetId,diseaseId", [str(HERE / "cohort_mapped.parquet")]).df()
    assoc = con.execute("SELECT * FROM read_parquet(?)", [str(HERE / "association_cohort_18.parquet")]).df()
    if len(cohort) != 26235 or cohort.duplicated(["targetId", "diseaseId"]).any():
        raise RuntimeError("Cohort pair unit is not unique")
    if assoc.duplicated(["targetId", "diseaseId", "aggregationValue"]).any():
        raise RuntimeError("Datasource pair unit is not unique")
    if set(assoc.columns).intersection({"clinical", "overall_score", "label", "phase"}):
        raise RuntimeError("Outcome-adjacent field in source cache")
    if set(cohort.label.unique()) != {0, 1}:
        raise RuntimeError("Invalid binary terminal label")

    x = np.zeros((len(cohort), len(SIX), 4), dtype=np.float32)
    key = cohort[["targetId", "diseaseId"]]
    for j, datasource in enumerate(SIX):
        part = assoc.loc[assoc.aggregationValue == datasource, [
            "targetId", "diseaseId", "associationScore", "evidenceCount", "currentNovelty"
        ]].copy()
        part["present"] = 1.0
        merged = key.merge(part, on=["targetId", "diseaseId"], how="left", validate="one_to_one", sort=False)
        present = merged.present.fillna(0).to_numpy(np.float32)
        score = merged.associationScore.fillna(0).to_numpy(np.float32)
        count = merged.evidenceCount.fillna(0).to_numpy(np.float32)
        novelty = merged.currentNovelty.fillna(0).to_numpy(np.float32)
        if not np.isfinite(score).all() or not np.isfinite(count).all() or not np.isfinite(novelty).all():
            raise RuntimeError(f"Nonfinite source feature: {datasource}")
        if (score < 0).any() or (score > 1).any() or (count < 0).any():
            raise RuntimeError(f"Out-of-range source feature: {datasource}")
        x[:, j, 0] = score
        x[:, j, 1] = np.log1p(count)
        x[:, j, 2] = novelty
        x[:, j, 3] = present
    cohort["split"] = cohort.targetId.map(split_name)
    overlaps = [
        len(set(cohort.loc[cohort.split == a, "targetId"]).intersection(cohort.loc[cohort.split == b, "targetId"]))
        for a, b in (("train", "validation"), ("train", "test"), ("validation", "test"))
    ]
    if any(overlaps):
        raise RuntimeError(f"Target-level split leakage: {overlaps}")
    return cohort, x, manifest


def new_logistic(c: float = 1.0):
    return make_pipeline(StandardScaler(), LogisticRegression(C=c, max_iter=600, solver="lbfgs"))


def pairwise_features(x: np.ndarray) -> np.ndarray:
    score, count, novelty, available = (x[:, :, i] for i in range(4))
    blocks = [score, count, novelty, available]
    for i in range(len(SIX)):
        for j in range(i + 1, len(SIX)):
            blocks.extend((score[:, i:i + 1] * score[:, j:j + 1],
                           available[:, i:i + 1] * available[:, j:j + 1]))
    return np.concatenate(blocks, axis=1)


def additive_features(x: np.ndarray) -> np.ndarray:
    return np.concatenate([x[:, :, i] for i in range(4)], axis=1)


def count_features(x: np.ndarray) -> np.ndarray:
    return np.column_stack((x[:, :, 1].sum(axis=1), x[:, :, 3].sum(axis=1)))


def calibration_features(x: np.ndarray) -> np.ndarray:
    return x[:, :, 0].sum(axis=1, keepdims=True)


class ShrunkRate:
    def __init__(self, strength: float = 20.0):
        self.strength = strength

    def fit(self, category: np.ndarray, label: np.ndarray):
        self.base = float(np.mean(label))
        self.n = np.bincount(category, minlength=int(category.max()) + 1)
        self.pos = np.bincount(category, weights=label, minlength=len(self.n))
        return self

    def predict(self, category: np.ndarray) -> np.ndarray:
        n = np.zeros(len(category), dtype=float)
        pos = np.zeros(len(category), dtype=float)
        known = category < len(self.n)
        n[known] = self.n[category[known]]
        pos[known] = self.pos[category[known]]
        return (pos + self.strength * self.base) / (n + self.strength)


def presence_mask(x: np.ndarray) -> np.ndarray:
    out = np.zeros(len(x), dtype=np.int64)
    for j in range(len(SIX)):
        out |= (x[:, j, 3] > 0.5).astype(np.int64) << j
    return out


def probability(model, x: np.ndarray) -> np.ndarray:
    return model.predict_proba(x)[:, 1]


def simplex_fit(predictions: np.ndarray, label: np.ndarray) -> tuple[np.ndarray, float]:
    best_w = np.array([0.0, 0.0, 1.0])
    best_loss = math.inf
    for i in range(21):
        for j in range(21 - i):
            weights = np.array([i, j, 20 - i - j], dtype=float) / 20.0
            p = np.clip(predictions @ weights, 1e-7, 1 - 1e-7)
            loss = float(log_loss(label, p, labels=[0, 1]))
            if loss < best_loss:
                best_w, best_loss = weights, loss
    return best_w, best_loss


def metrics(label: np.ndarray, pred: np.ndarray) -> dict:
    pred = np.clip(np.asarray(pred, dtype=float), 1e-7, 1 - 1e-7)
    if len(label) != len(pred) or not np.isfinite(pred).all():
        raise RuntimeError("Invalid metric prediction")
    bins = np.minimum((pred * 10).astype(int), 9)
    ece = sum(
        (bins == b).mean() * abs(float(pred[bins == b].mean()) - float(label[bins == b].mean()))
        for b in range(10) if (bins == b).any()
    )
    result = {
        "n": int(len(label)),
        "positive_prevalence": float(np.mean(label)),
        "logloss": float(log_loss(label, pred, labels=[0, 1])),
        "brier": float(brier_score_loss(label, pred)),
        "auroc": float(roc_auc_score(label, pred)) if len(np.unique(label)) == 2 else None,
        "auprc": float(average_precision_score(label, pred)) if len(np.unique(label)) == 2 else None,
        "ece_10_equal_width": float(ece),
    }
    if np.ptp(pred) > 1e-9:
        calibrator = LogisticRegression(C=1e6, max_iter=600).fit(logit(pred).reshape(-1, 1), label)
        result["calibration_intercept"] = float(calibrator.intercept_[0])
        result["calibration_slope"] = float(calibrator.coef_[0, 0])
    else:
        result["calibration_intercept"] = None
        result["calibration_slope"] = None
    return result


def grouped_ci(label: np.ndarray, pred: np.ndarray, targets: np.ndarray, seed: int = 1701) -> dict:
    group_ids, reverse = np.unique(targets, return_inverse=True)
    by_group = [np.where(reverse == j)[0] for j in range(len(group_ids))]
    rng = np.random.default_rng(seed)
    values = {metric: [] for metric in ("logloss", "brier", "auroc", "auprc")}
    for _ in range(BOOTSTRAPS):
        chosen = rng.integers(0, len(group_ids), len(group_ids))
        idx = np.concatenate([by_group[j] for j in chosen])
        yb = label[idx]
        pb = np.clip(pred[idx], 1e-7, 1 - 1e-7)
        values["logloss"].append(float(log_loss(yb, pb, labels=[0, 1])))
        values["brier"].append(float(brier_score_loss(yb, pb)))
        if len(np.unique(yb)) == 2:
            values["auroc"].append(float(roc_auc_score(yb, pb)))
            values["auprc"].append(float(average_precision_score(yb, pb)))
    return {
        name: [float(np.quantile(v, 0.025)), float(np.quantile(v, 0.975))] if v else None
        for name, v in values.items()
    }


class Ganglion(nn.Module):
    def __init__(self):
        super().__init__()
        self.interfaces = nn.ModuleList([nn.Sequential(nn.Linear(4, 16), nn.Tanh()) for _ in SIX])
        self.core = nn.Sequential(nn.Linear(16, 16), nn.Tanh())
        self.outcome = nn.Linear(16, 1)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        parts = torch.stack([module(x[:, j, :]) for j, module in enumerate(self.interfaces)], dim=1)
        available = x[:, :, 3:4]
        combined = (parts * available).sum(dim=1) / available.sum(dim=1).clamp_min(1.0)
        return self.outcome(self.core(combined)).squeeze(-1)


def ganglion_predict(model: Ganglion, x: np.ndarray, device: str) -> np.ndarray:
    model.eval()
    with torch.no_grad():
        logits = model(torch.as_tensor(x, dtype=torch.float32, device=device))
        return torch.sigmoid(logits).cpu().numpy()


def ganglion_fit(xtr, ytr, xva, yva, seed: int, out: Path, max_epochs: int = 250, patience: int = 30):
    torch.manual_seed(seed)
    device = "mps" if torch.backends.mps.is_available() else ("cuda" if torch.cuda.is_available() else "cpu")
    model = Ganglion().to(device)
    initial_core = model.core[0].weight.detach().cpu().clone()
    xt = torch.as_tensor(xtr, dtype=torch.float32, device=device)
    yt = torch.as_tensor(ytr, dtype=torch.float32, device=device)
    xv = torch.as_tensor(xva, dtype=torch.float32, device=device)
    yv = torch.as_tensor(yva, dtype=torch.float32, device=device)
    optimizer = torch.optim.Adam(model.parameters(), lr=0.002)
    best = math.inf
    best_epoch = 0
    best_state = None
    grad_rms = {}
    with (out / f"training_trace_seed_{seed}.csv").open("w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(("epoch", "train_logloss", "validation_logloss"))
        for epoch in range(1, max_epochs + 1):
            model.train()
            optimizer.zero_grad()
            train_loss = nn.functional.binary_cross_entropy_with_logits(model(xt), yt)
            train_loss.backward()
            current_grad = {
                name: float(torch.sqrt(torch.mean(parameter.grad.detach() ** 2)).cpu())
                for name, parameter in model.named_parameters() if parameter.grad is not None
            }
            optimizer.step()
            model.eval()
            with torch.no_grad():
                val_loss = float(nn.functional.binary_cross_entropy_with_logits(model(xv), yv).cpu())
            writer.writerow((epoch, float(train_loss.detach().cpu()), val_loss))
            f.flush()
            if val_loss < best - 1e-7:
                best, best_epoch = val_loss, epoch
                best_state = {key: value.detach().cpu().clone() for key, value in model.state_dict().items()}
                grad_rms = current_grad
            if epoch - best_epoch >= patience:
                break
    assert best_state is not None
    model.load_state_dict(best_state)
    torch.save({"seed": seed, "best_epoch": best_epoch, "state_dict": best_state}, out / f"ganglion_seed_{seed}.pt")
    final_core = model.core[0].weight.detach().cpu()
    delta = final_core - initial_core
    singular = torch.linalg.svdvals(delta).numpy()
    proportions = singular / max(float(singular.sum()), 1e-12)
    effective_rank = float(np.exp(-np.sum(proportions * np.log(np.clip(proportions, 1e-12, 1)))))
    diagnostic = {
        "seed": seed,
        "device": device,
        "best_epoch": best_epoch,
        "validation_logloss": best,
        "core_weight_displacement_frobenius": float(torch.linalg.vector_norm(delta)),
        "core_delta_singular_values": singular.tolist(),
        "core_delta_effective_rank": effective_rank,
        "gradient_rms_at_best_epoch": grad_rms,
    }
    return model, device, diagnostic, delta


def lesion_controls(model: Ganglion, device: str, delta: torch.Tensor, xte: np.ndarray, yte: np.ndarray, seed: int):
    u, singular, vt = torch.linalg.svd(delta)
    top = singular[0] * torch.outer(u[:, 0], vt[0, :])
    learned = copy.deepcopy(model)
    random_control = copy.deepcopy(model)
    generator = torch.Generator(device="cpu").manual_seed(seed + 1000)
    noise = torch.randn(delta.shape, generator=generator)
    noise *= torch.linalg.vector_norm(top) / torch.linalg.vector_norm(noise)
    with torch.no_grad():
        learned.core[0].weight.sub_(top.to(device))
        random_control.core[0].weight.sub_(noise.to(device))
    return {
        "top_direction_removed_logloss": metrics(yte, ganglion_predict(learned, xte, device))["logloss"],
        "random_matched_norm_logloss": metrics(yte, ganglion_predict(random_control, xte, device))["logloss"],
        "removed_frobenius_norm": float(torch.linalg.vector_norm(top)),
    }


def main(run_id: str) -> None:
    out = HERE / "results" / "source_level_six" / run_id
    out.mkdir(parents=True, exist_ok=False)
    try:
        torch.set_num_threads(4)
        cohort, x, manifest = load_matrix()
        label = cohort.label.to_numpy(np.int64)
        targets = cohort.targetId.to_numpy()
        subsets = {name: np.where(cohort.split.to_numpy() == name)[0] for name in ("train", "validation", "test")}
        tr, va, te = (subsets[name] for name in ("train", "validation", "test"))
        split_summary = {
            name: {"pairs": int(len(idx)), "targets": int(len(set(targets[idx]))),
                   "positives": int(label[idx].sum()), "prevalence": float(label[idx].mean()),
                   "six_source_rows": {ds: int(x[idx, j, 3].sum()) for j, ds in enumerate(SIX)}}
            for name, idx in subsets.items()
        }
        (out / "split_summary.json").write_text(json.dumps(split_summary, indent=2) + "\n")
        if min(split_summary[s]["positives"] for s in split_summary) == 0:
            raise RuntimeError("A split lacks positive terminal outcomes")
        folds = list(StratifiedGroupKFold(n_splits=5, shuffle=True, random_state=20261002).split(x[tr], label[tr], targets[tr]))
        if any(set(targets[tr][train]).intersection(targets[tr][held]) for train, held in folds):
            raise RuntimeError("OOF target leakage")

        predictions: dict[str, dict[str, np.ndarray]] = {name: {} for name in subsets}
        base_rate = float(label[tr].mean())
        for name, idx in subsets.items():
            predictions[name]["prevalence"] = np.full(len(idx), base_rate)

        global_features = {
            "count_logistic": count_features(x),
            "calibration_only": calibration_features(x),
            "additive_logistic": additive_features(x),
            "pairwise_logistic": pairwise_features(x),
        }
        for name, features in global_features.items():
            model = new_logistic(c=0.5 if name == "pairwise_logistic" else 1.0).fit(features[tr], label[tr])
            for split, idx in subsets.items():
                predictions[split][name] = probability(model, features[idx])

        masks = presence_mask(x)
        eb = ShrunkRate().fit(masks[tr], label[tr])
        for split, idx in subsets.items():
            predictions[split]["empirical_bayes"] = eb.predict(masks[idx])

        global_experts = ("additive_logistic", "pairwise_logistic", "empirical_bayes")
        global_oof = np.zeros((len(tr), 3), dtype=float)
        for fit, held in folds:
            for j, name in enumerate(global_experts[:2]):
                model = new_logistic(c=0.5 if j == 1 else 1.0).fit(global_features[name][tr][fit], label[tr][fit])
                global_oof[held, j] = probability(model, global_features[name][tr][held])
            eb_fold = ShrunkRate().fit(masks[tr][fit], label[tr][fit])
            global_oof[held, 2] = eb_fold.predict(masks[tr][held])
        global_weights, global_oof_loss = simplex_fit(global_oof, label[tr])
        predictions["train"]["stat_moe"] = global_oof @ global_weights
        for split in ("validation", "test"):
            predictions[split]["stat_moe"] = np.column_stack([
                predictions[split][name] for name in global_experts
            ]) @ global_weights

        states = {name: np.zeros((len(idx), len(SIX), 4), dtype=np.float32) for name, idx in subsets.items()}
        routing = {"global_experts": list(global_experts), "global_weights": global_weights.tolist(),
                   "global_oof_logloss": global_oof_loss, "local": {}}
        for j, ds in enumerate(SIX):
            score_features = x[:, j, [0, 3]]
            count_local_features = x[:, j, [1, 3]]
            categories = x[:, j, 3].astype(int)
            local_oof = np.zeros((len(tr), 3), dtype=float)
            for fit, held in folds:
                score_model = new_logistic().fit(score_features[tr][fit], label[tr][fit])
                count_model = new_logistic().fit(count_local_features[tr][fit], label[tr][fit])
                rate_model = ShrunkRate(40.0).fit(categories[tr][fit], label[tr][fit])
                local_oof[held, 0] = probability(score_model, score_features[tr][held])
                local_oof[held, 1] = probability(count_model, count_local_features[tr][held])
                local_oof[held, 2] = rate_model.predict(categories[tr][held])
            weights, oof_loss = simplex_fit(local_oof, label[tr])
            routing["local"][ds] = {"experts": ["score_logistic", "count_logistic", "availability_shrinkage"],
                                    "weights": weights.tolist(), "oof_logloss": oof_loss,
                                    "train_available_pairs": int(categories[tr].sum())}
            score_final = new_logistic().fit(score_features[tr], label[tr])
            count_final = new_logistic().fit(count_local_features[tr], label[tr])
            rate_final = ShrunkRate(40.0).fit(categories[tr], label[tr])
            for split, idx in subsets.items():
                p = local_oof @ weights if split == "train" else np.column_stack((
                    probability(score_final, score_features[idx]),
                    probability(count_final, count_local_features[idx]),
                    rate_final.predict(categories[idx]),
                )) @ weights
                p = np.clip(p, 1e-7, 1 - 1e-7)
                states[split][:, j, 0] = p
                states[split][:, j, 1] = -(p * np.log(p) + (1 - p) * np.log(1 - p))
                states[split][:, j, 2] = x[idx, j, 2]
                states[split][:, j, 3] = x[idx, j, 3]
        (out / "routing_weights.json").write_text(json.dumps(routing, indent=2) + "\n")
        oof_frame = cohort.iloc[tr][["targetId", "diseaseId", "label"]].copy()
        for j, ds in enumerate(SIX):
            oof_frame[ds + "__prediction"] = states["train"][:, j, 0]
            oof_frame[ds + "__availability"] = states["train"][:, j, 3]
        oof_frame.to_parquet(out / "train_channel_oof.parquet", index=False)

        controls = {}
        ganglion_diagnostics = {}
        for seed in SEEDS:
            model, device, diagnostic, delta = ganglion_fit(states["train"], label[tr], states["validation"], label[va], seed, out)
            name = f"ganglion_seed_{seed}"
            for split in ("validation", "test"):
                predictions[split][name] = ganglion_predict(model, states[split], device)
            xte = states["test"]
            ablations = {}
            for j, ds in enumerate(SIX):
                damaged = xte.copy()
                damaged[:, j, :] = 0
                ablations[ds] = metrics(label[te], ganglion_predict(model, damaged, device))["logloss"]
            rng = np.random.default_rng(seed + 2000)
            shuffled = xte.copy()
            for j in range(len(SIX)):
                shuffled[:, j, :] = xte[rng.permutation(len(xte)), j, :]
            controls[name] = {
                "test_logloss_original": metrics(label[te], predictions["test"][name])["logloss"],
                "test_logloss_channel_shuffle": metrics(label[te], ganglion_predict(model, shuffled, device))["logloss"],
                "single_pipeline_ablation_logloss": ablations,
                "learned_direction_lesion": lesion_controls(model, device, delta, xte, label[te], seed),
            }
            ganglion_diagnostics[name] = diagnostic

        metric_results = {}
        for name in predictions["test"]:
            metric_results[name] = {
                "validation": metrics(label[va], predictions["validation"][name]),
                "test": metrics(label[te], predictions["test"][name]),
                "test_grouped_bootstrap_95ci": grouped_ci(label[te], predictions["test"][name], targets[te], seed=1701),
            }
        (out / "metrics.json").write_text(json.dumps(metric_results, indent=2) + "\n")
        (out / "controls.json").write_text(json.dumps(controls, indent=2) + "\n")
        (out / "ganglion_diagnostics.json").write_text(json.dumps(ganglion_diagnostics, indent=2) + "\n")
        test_frame = cohort.iloc[te][["targetId", "diseaseId", "label"]].copy()
        for name, pred in predictions["test"].items():
            test_frame[name] = pred
        test_frame.to_parquet(out / "test_predictions.parquet", index=False)

        plt.figure(figsize=(6.5, 4.2))
        labels = ["prevalence", "count_logistic", "additive_logistic", "pairwise_logistic", "empirical_bayes", "stat_moe"]
        values = [metric_results[name]["test"]["logloss"] for name in labels]
        plt.barh(labels, values, color="#397d87")
        plt.xlabel("Test Bernoulli log loss")
        plt.title("EXP017 six-source retrospective baselines")
        plt.tight_layout()
        plt.savefig(out / "baseline_logloss.png", dpi=160)
        plt.close()

        (out / "protocol_and_environment.json").write_text(json.dumps({
            "run_id": run_id,
            "research_id": "STAT-PSYMOE-EXP017-20261002-001",
            "qualification": "Exploratory 26.06 datasource-level retrospective cohort; native raw and point-in-time not tested",
            "input_manifest": str(HERE / "cache_manifest.json"),
            "six_datasources": SIX,
            "split": "FNV1a32 target hash modulo 100: 70/15/15",
            "local_oof": "5-fold StratifiedGroupKFold by target; simplex weights on OOF log loss",
            "ganglion_seeds": SEEDS,
            "ganglion_max_epochs": 250,
            "ganglion_early_stop_patience": 30,
            "bootstrap": f"{BOOTSTRAPS} target-group resamples",
            "versions": {name: version(name) for name in ("numpy", "pandas", "scikit-learn", "scipy", "torch", "duckdb", "pyarrow")},
            "python": platform.python_version(),
            "output_dir": str(out),
        }, indent=2) + "\n")
        print(json.dumps({
            "run_id": run_id,
            "split_summary": split_summary,
            "test_logloss": {name: round(result["test"]["logloss"], 6) for name, result in metric_results.items()},
            "output_dir": str(out),
        }, indent=2))
    except Exception as exc:
        (out / "failure.json").write_text(json.dumps({
            "run_id": run_id, "error_type": type(exc).__name__, "error": str(exc),
            "existing_outputs": sorted(p.name for p in out.iterdir()),
        }, indent=2) + "\n")
        raise


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--run-id", default="EXP017-SOURCE-TRAIN-001")
    main(parser.parse_args().run_id)
