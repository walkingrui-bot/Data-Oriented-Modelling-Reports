#!/usr/bin/env python3
"""CGC source-specific OOF experts, statistical routing, and six-source increment probe."""

from __future__ import annotations

import json
import sys
import traceback
from pathlib import Path

import numpy as np
import pandas as pd
import torch
from sklearn.model_selection import StratifiedGroupKFold


HERE = Path(__file__).resolve().parent
PARENT = HERE.parent / "STAT-PSYMOE-EXP017-20261002-001"
sys.path.insert(0, str(PARENT))
from train_native_six import load_native  # noqa: E402
from train_source_level_six import (  # noqa: E402
    Ganglion, SEEDS, SIX, ShrunkRate, ganglion_predict, metrics, new_logistic,
    probability, simplex_fit,
)
from paired_analysis import paired_difference  # noqa: E402


RUN_ID = "EXP019-CGC-STAT-001"
OUT = HERE / "results" / RUN_ID
OLD_RUN = PARENT / "results/native_six/EXP017-NATIVE-TRAIN-001"
STATE_FIELDS = (
    "local_prediction", "predictive_entropy", "scaled_log_evidence_rows", "availability",
    "native_score", "mutation_fraction", "scaled_log_mutated", "scaled_log_publications",
    "study_support", "direction_support", "expert_disagreement",
)
EXPERTS = ("curated_score", "mutation_context", "study_support")


def subsets_and_folds(cohort: pd.DataFrame):
    y = cohort.label.to_numpy(np.int64)
    target = cohort.targetId.to_numpy()
    idx = {name: np.where(cohort.split.to_numpy() == name)[0]
           for name in ("train", "validation", "test")}
    tr = idx["train"]
    folds = list(StratifiedGroupKFold(n_splits=5, shuffle=True, random_state=20261002)
                 .split(np.zeros((len(tr), 1)), y[tr], target[tr]))
    if any(set(target[tr][fit]) & set(target[tr][held]) for fit, held in folds):
        raise RuntimeError("Target leakage in inherited OOF folds")
    return y, target, idx, folds


def rebuild_old_states(cohort, raw, geometry, idx, folds, y):
    """Recompute EXP017 states in memory and compare to original saved predictions."""
    tr = idx["train"]
    route = json.loads((OLD_RUN / "routing_weights.json").read_text())
    states = {name: np.zeros((len(where), len(SIX), 4), np.float32)
              for name, where in idx.items()}
    for j, ds in enumerate(SIX):
        score_features = np.column_stack((raw[:, j, 0], raw[:, j, 2], raw[:, j, 3]))
        geom = geometry[ds]
        category = np.where(raw[:, j, 3] == 0, 0,
                            np.where(raw[:, j, 0] == 0, 1, 2)).astype(int)
        oof = np.zeros((len(tr), 3), float)
        for fit, held in folds:
            score = new_logistic().fit(score_features[tr][fit], y[tr][fit])
            native = new_logistic(c=0.5).fit(geom[tr][fit], y[tr][fit])
            shrink = ShrunkRate(40.0).fit(category[tr][fit], y[tr][fit])
            oof[held, 0] = probability(score, score_features[tr][held])
            oof[held, 1] = probability(native, geom[tr][held])
            oof[held, 2] = shrink.predict(category[tr][held])
        weights = np.asarray(route["local"][ds]["weights"], dtype=float)
        score = new_logistic().fit(score_features[tr], y[tr])
        native = new_logistic(c=0.5).fit(geom[tr], y[tr])
        shrink = ShrunkRate(40.0).fit(category[tr], y[tr])
        scale = float(route["local"][ds]["coverage_scale_train_q95"])
        for name, where in idx.items():
            expert = oof if name == "train" else np.column_stack((
                probability(score, score_features[where]),
                probability(native, geom[where]),
                shrink.predict(category[where]),
            ))
            pred = np.clip(expert @ weights, 1e-7, 1 - 1e-7)
            states[name][:, j, 0] = pred
            states[name][:, j, 1] = -(pred * np.log(pred) + (1 - pred) * np.log1p(-pred))
            states[name][:, j, 2] = np.clip(raw[where, j, 1] / scale, 0, 2)
            states[name][:, j, 3] = raw[where, j, 3]
    old_oof = pd.read_parquet(OLD_RUN / "train_channel_oof.parquet")
    if not old_oof[["targetId", "diseaseId", "label"]].reset_index(drop=True).equals(
        cohort.iloc[tr][["targetId", "diseaseId", "label"]].reset_index(drop=True)
    ):
        raise RuntimeError("Old OOF pair order changed")
    oof_max = {}
    for j, ds in enumerate(SIX):
        oof_max[ds] = float(np.max(np.abs(old_oof[ds + "__prediction"].to_numpy() -
                                           states["train"][:, j, 0])))
    if max(oof_max.values()) > 2e-6:
        raise RuntimeError(f"Old six OOF reconstruction failed: {oof_max}")
    old_test = pd.read_parquet(OLD_RUN / "test_predictions.parquet")
    if not old_test[["targetId", "diseaseId", "label"]].reset_index(drop=True).equals(
        cohort.iloc[idx["test"]][["targetId", "diseaseId", "label"]].reset_index(drop=True)
    ):
        raise RuntimeError("Old test pair order changed")
    ckpt_max = {}
    for seed in SEEDS:
        obj = torch.load(OLD_RUN / f"ganglion_seed_{seed}.pt", map_location="cpu", weights_only=True)
        model = Ganglion()
        model.load_state_dict(obj["state_dict"])
        reconstructed = ganglion_predict(model, states["test"], "cpu")
        ckpt_max[str(seed)] = float(np.max(np.abs(
            reconstructed - old_test[f"ganglion_seed_{seed}"].to_numpy())))
    if max(ckpt_max.values()) > 2e-6:
        raise RuntimeError(f"Old checkpoint prediction reconstruction failed: {ckpt_max}")
    return states, {"old_train_oof_max_abs_difference": oof_max,
                    "old_test_checkpoint_max_abs_difference": ckpt_max,
                    "old_checkpoint_paths": [str(OLD_RUN / f"ganglion_seed_{s}.pt") for s in SEEDS]}


def cgc_features(cohort: pd.DataFrame, tr: np.ndarray):
    pair = pd.read_parquet(HERE / "native_cancer_gene_census_pair_features.parquet")
    merged = cohort[["targetId", "diseaseId"]].merge(pair, on=["targetId", "diseaseId"],
                                                       how="left", validate="one_to_one", sort=False)
    available = merged.native_evidence_rows.notna().to_numpy(float)

    def values(name):
        return merged[name].fillna(0).to_numpy(float)

    score = values("max_native_score")
    resource = values("max_resource_score")
    rows = values("native_evidence_rows")
    mutated = values("mutated_sample_count")
    tested = values("tested_sample_count")
    typed = values("typed_mutation_sample_count")
    contexts = values("mutation_sample_context_rows")
    literature = values("publication_reference_count")
    studies = values("distinct_studies")
    direction = values("distinct_trait_directions") + values("distinct_target_directions")
    raw_fraction = mutated / np.maximum(tested, 1.0)
    fraction = np.clip(raw_fraction, 0, 1)
    log_mutated = np.log1p(mutated)
    log_publications = np.log1p(literature)
    native = {
        "curated_score": np.column_stack((available, score, resource)),
        "mutation_context": np.column_stack((available, log_mutated,
                                               np.log1p(tested), fraction,
                                               np.log1p(typed), np.log1p(contexts))),
        "study_support": np.column_stack((available, log_publications,
                                            np.log1p(studies), direction)),
    }
    scalars = {"available": available, "score": score, "rows": rows,
               "mutation_fraction": fraction, "log_mutated": log_mutated,
               "log_publications": log_publications, "study_support": np.log1p(studies),
               "direction_support": direction}
    train_positive = available[tr] > 0
    if not train_positive.any():
        raise RuntimeError("CGC has no train availability after frozen gate")
    scales = {
        "density": max(float(np.quantile(np.log1p(rows[tr][train_positive]), .95)), 1.0),
        "mutated": max(float(np.quantile(log_mutated[tr][train_positive], .95)), 1.0),
        "publications": max(float(np.quantile(log_publications[tr][train_positive], .95)), 1.0),
    }
    diagnostics = {"feature_names": {
        "curated_score": ["availability", "max_native_score", "max_resource_score"],
        "mutation_context": ["availability", "log_mutated_samples", "log_tested_samples",
                             "clipped_mutated_fraction", "log_typed_mutations", "log_mutation_contexts"],
        "study_support": ["availability", "log_publication_references",
                          "log_distinct_studies", "trait_plus_target_direction_count"],
    }, "fraction_over_one_train_validation": int(np.sum(
        (raw_fraction > 1) & cohort.split.isin(("train", "validation")).to_numpy())),
        "train_only_scales": scales,
        "date_fields_used_as_features": [],
        "provenance_key_field": "provenance_study_key"}
    return native, scalars, merged, scales, diagnostics


def fit_experts(native, y, idx, folds, available):
    tr = idx["train"]
    oof = np.zeros((len(tr), len(EXPERTS)), float)
    for fit, held in folds:
        for j, name in enumerate(EXPERTS):
            model = new_logistic(c=0.5).fit(native[name][tr][fit], y[tr][fit])
            oof[held, j] = probability(model, native[name][tr][held])
    weights = {}
    oof_loss = {}
    for regime, mask in (("absent", available[tr] == 0), ("present", available[tr] > 0)):
        if np.sum(mask) < 10:
            raise RuntimeError(f"Insufficient OOF support for {regime} route")
        w, loss = simplex_fit(oof[mask], y[tr][mask])
        weights[regime] = w
        oof_loss[regime] = float(loss)
    models = {name: new_logistic(c=0.5).fit(native[name][tr], y[tr]) for name in EXPERTS}
    experts = {}
    route = {}
    for split, where in idx.items():
        expert = oof if split == "train" else np.column_stack([
            probability(models[name], native[name][where]) for name in EXPERTS])
        weight = np.where(available[where, None] > 0,
                          weights["present"][None, :], weights["absent"][None, :])
        experts[split] = expert
        route[split] = np.clip(np.sum(expert * weight, axis=1), 1e-7, 1 - 1e-7)
    report = {"experts": EXPERTS, "weights": {key: val.tolist() for key, val in weights.items()},
              "oof_route_logloss_by_regime": oof_loss,
              "train_oof": {name: metrics(y[tr], oof[:, j]) for j, name in enumerate(EXPERTS)} | {
                  "stat_moe": metrics(y[tr], route["train"])},
              "validation": {name: metrics(y[idx["validation"]], experts["validation"][:, j])
                             for j, name in enumerate(EXPERTS)} | {
                  "stat_moe": metrics(y[idx["validation"]], route["validation"])}}
    return experts, route, report


def export_states(cohort, idx, experts, route, scalars, scales, merged):
    p = route["train"]
    full = np.empty((len(cohort), len(STATE_FIELDS)), np.float32)
    for split, where in idx.items():
        p = route[split]
        available = scalars["available"][where]
        full[where] = np.column_stack((
            p,
            -(p * np.log(p) + (1 - p) * np.log1p(-p)),
            np.clip(np.log1p(scalars["rows"][where]) / scales["density"], 0, 2),
            available,
            scalars["score"][where],
            scalars["mutation_fraction"][where],
            np.clip(scalars["log_mutated"][where] / scales["mutated"], 0, 2),
            np.clip(scalars["log_publications"][where] / scales["publications"], 0, 2),
            scalars["study_support"][where],
            scalars["direction_support"][where],
            np.std(experts[split], axis=1),
        ))
    if not np.isfinite(full).all() or not np.array_equal(full[:, 3], scalars["available"]):
        raise RuntimeError("Invalid CGC exported state")
    frame = cohort[["targetId", "diseaseId", "split"]].copy()
    for j, name in enumerate(STATE_FIELDS):
        frame[name] = full[:, j]
    frame["provenance_study_key"] = merged.provenance_study_key
    frame["earliest_evidence_date"] = merged.earliest_evidence_date
    frame.to_parquet(OUT / "cgc_exported_state.parquet", index=False)
    return full


def incremental_probe(old, new, y, target, cohort, idx, folds):
    tr, va = idx["train"], idx["validation"]
    old_flat = {name: old[name].reshape(len(where), -1) for name, where in idx.items()}
    new_split = {name: new[where] for name, where in idx.items()}
    oof = {}
    val = {}
    for name, train_x, val_x in (
        ("M0_six", old_flat["train"], old_flat["validation"]),
        ("M1_six_plus_CGC", np.column_stack((old_flat["train"], new_split["train"])),
         np.column_stack((old_flat["validation"], new_split["validation"]))),
    ):
        pred = np.zeros(len(tr), float)
        for fit, held in folds:
            model = new_logistic(c=0.25).fit(train_x[fit], y[tr][fit])
            pred[held] = probability(model, train_x[held])
        oof[name] = pred
        final = new_logistic(c=0.25).fit(train_x, y[tr])
        val[name] = probability(final, val_x)
    detail = {"train_target_group_oof": {name: metrics(y[tr], p) for name, p in oof.items()},
              "validation": {name: metrics(y[va], p) for name, p in val.items()},
              "validation_paired_M1_minus_M0": paired_difference(pd.DataFrame({
                  "targetId": target[va], "label": y[va], **val}),
                  "M1_six_plus_CGC", "M0_six"),
              "qualification": "Stacker is target-group OOF conditional on inherited EXP017 local OOF states. "
                               "Those inherited train states and CGC routing weights were not recomputed in an outer nested fold; "
                               "validation is the clean incremental selection surface."}
    pred = pd.DataFrame({"targetId": np.concatenate((target[tr], target[va])),
                         "diseaseId": pd.concat((cohort.iloc[tr].diseaseId,
                                                 cohort.iloc[va].diseaseId), ignore_index=True),
                         "label": np.concatenate((y[tr], y[va])),
                         "split": ["train_oof"] * len(tr) + ["validation"] * len(va),
                         "M0_six": np.concatenate((oof["M0_six"], val["M0_six"])),
                         "M1_six_plus_CGC": np.concatenate((oof["M1_six_plus_CGC"],
                                                              val["M1_six_plus_CGC"]))})
    pred.to_parquet(OUT / "incremental_predictions.parquet", index=False)
    return detail


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=False)
    try:
        torch.set_num_threads(4)
        cohort, raw, geometry, _ = load_native()
        y, target, idx, folds = subsets_and_folds(cohort)
        old, reconstruction = rebuild_old_states(cohort, raw, geometry, idx, folds, y)
        (OUT / "old_reconstruction.json").write_text(json.dumps(reconstruction, indent=2) + "\n")
        native, scalars, merged, scales, diagnostics = cgc_features(cohort, idx["train"])
        experts, route, stat_report = fit_experts(native, y, idx, folds, scalars["available"])
        new = export_states(cohort, idx, experts, route, scalars, scales, merged)
        train_oof = cohort.iloc[idx["train"]][["targetId", "diseaseId", "label"]].copy()
        for j, name in enumerate(EXPERTS):
            train_oof[name + "__prediction"] = experts["train"][:, j]
        train_oof["stat_moe_prediction"] = route["train"]
        train_oof.to_parquet(OUT / "cgc_expert_train_oof.parquet", index=False)
        (OUT / "native_stat_routing.json").write_text(json.dumps({
            "run_id": RUN_ID, "source": "cancer_gene_census", "feature_diagnostics": diagnostics,
            "state_fields": STATE_FIELDS, "statistical_routing": stat_report,
            "train_target_group_folds": 5,
            "old_source_reconstruction": str(OUT / "old_reconstruction.json"),
            "test_performance_computed": False,
        }, ensure_ascii=False, indent=2, allow_nan=False) + "\n")
        increment = incremental_probe(old, new, y, target, cohort, idx, folds)
        (OUT / "incremental_train_validation.json").write_text(
            json.dumps(increment, ensure_ascii=False, indent=2, allow_nan=False) + "\n")
        print(json.dumps({"source": "cancer_gene_census",
                          "local_validation_logloss": {name: value["logloss"]
                                                       for name, value in stat_report["validation"].items()},
                          "incremental_validation_logloss": {name: value["logloss"]
                                                             for name, value in increment["validation"].items()},
                          "reconstruction_max": max(reconstruction["old_test_checkpoint_max_abs_difference"].values())},
                         ensure_ascii=False), flush=True)
    except Exception as exc:
        (OUT / "failure.json").write_text(json.dumps({
            "run_id": RUN_ID, "error_type": type(exc).__name__, "error": str(exc),
            "traceback": traceback.format_exc(),
            "existing_outputs": sorted(p.name for p in OUT.iterdir()),
        }, ensure_ascii=False, indent=2) + "\n")
        raise


if __name__ == "__main__":
    main()
