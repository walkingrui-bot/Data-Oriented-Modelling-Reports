#!/usr/bin/env python3
"""Exploratory native-summary Stat-MoE and shared ganglion for six 26.06 sources."""

from __future__ import annotations

import json
import math
import platform
from importlib.metadata import version
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import torch
from sklearn.model_selection import StratifiedGroupKFold

from paired_analysis import paired_difference
from train_source_level_six import (
    HERE, SEEDS, SIX, ShrunkRate, additive_features, calibration_features,
    count_features, ganglion_fit, ganglion_predict, grouped_ci, lesion_controls,
    metrics, new_logistic, pairwise_features, presence_mask, probability,
    simplex_fit, split_name,
)


RUN_ID = "EXP017-NATIVE-TRAIN-001"
OUT = HERE / "results/native_six" / RUN_ID
SOURCE_TEST = HERE / "results/source_level_six/EXP017-SOURCE-TRAIN-001/test_predictions.parquet"


def log_count(series: pd.Series) -> np.ndarray:
    value = series.fillna(0).to_numpy(float)
    if (value < 0).any():
        raise RuntimeError(f"Negative native count: {series.name}")
    return np.log1p(value)


def asinh_value(series: pd.Series) -> np.ndarray:
    return np.arcsinh(series.fillna(0).to_numpy(float))


def native_geometry(datasource: str, frame: pd.DataFrame, available: np.ndarray) -> tuple[np.ndarray, list[str]]:
    blocks: list[np.ndarray] = [available]
    names = ["availability"]

    def add(name: str, value: np.ndarray) -> None:
        if not np.isfinite(value).all():
            raise RuntimeError(f"Nonfinite geometry field {datasource}.{name}")
        blocks.append(value)
        names.append(name)

    if datasource == "gwas_credible_sets":
        for name in ("distinct_study_loci", "distinct_publications"):
            add(name, log_count(frame[name]))
        for name in ("max_resource_score", "mean_resource_score"):
            add(name, frame[name].fillna(0).to_numpy(float))
    elif datasource == "gene_burden":
        add("strongest_neglog10_p", log_count(frame.strongest_neglog10_p))
        for name in ("max_abs_beta", "mean_beta"):
            add(name, asinh_value(frame[name]))
            add(name + "__missing_given_present", (frame[name].isna().to_numpy() & (available > 0)).astype(float))
        for name in ("distinct_cohorts", "distinct_projects", "max_study_sample_size"):
            add(name, log_count(frame[name]))
    elif datasource == "eva":
        for name in ("distinct_variants", "distinct_studies", "distinct_significance_sets", "distinct_confidence_levels"):
            add(name, log_count(frame[name]))
        for name in (
            "pathogenic_rows", "likely_pathogenic_rows", "benign_rows", "likely_benign_rows",
            "uncertain_rows", "conflict_rows", "evidence_only_rows", "expert_panel_rows",
        ):
            add(name, log_count(frame[name]))
        denom = frame.category_evidence_rows.fillna(0).to_numpy(float).clip(min=1)
        add("pathogenic_fraction", (frame.pathogenic_rows.fillna(0).to_numpy(float) +
                                    frame.likely_pathogenic_rows.fillna(0).to_numpy(float)) / denom)
        add("uncertain_fraction", frame.uncertain_rows.fillna(0).to_numpy(float) / denom)
    elif datasource == "expression_atlas":
        for name in ("distinct_studies", "distinct_contrasts"):
            add(name, log_count(frame[name]))
        for name in ("mean_signed_log2fc", "mean_abs_log2fc", "max_abs_log2fc"):
            add(name, asinh_value(frame[name]))
        direction = frame.positive_direction_rows.fillna(0).to_numpy(float) - frame.negative_direction_rows.fillna(0).to_numpy(float)
        denom = frame.positive_direction_rows.fillna(0).to_numpy(float) + frame.negative_direction_rows.fillna(0).to_numpy(float)
        add("direction_balance", direction / np.maximum(denom, 1.0))
    elif datasource == "impc":
        add("distinct_models", log_count(frame.distinct_models))
        for name in ("max_resource_score", "mean_resource_score"):
            add(name, frame[name].fillna(0).to_numpy(float) / 100.0)
        for name in ("max_mouse_phenotype_count", "max_human_phenotype_count"):
            add(name, log_count(frame[name]))
            add(name + "__missing_given_present", (frame[name].isna().to_numpy() & (available > 0)).astype(float))
    elif datasource == "europepmc":
        add("distinct_publications", log_count(frame.distinct_publications))
        for name in ("max_resource_score", "mean_resource_score"):
            add(name, log_count(frame[name]))
    else:
        raise RuntimeError(f"Unexpected native datasource: {datasource}")
    return np.column_stack(blocks), names


def load_native() -> tuple[pd.DataFrame, np.ndarray, dict[str, np.ndarray], dict]:
    cache = json.loads((HERE / "native_cache_manifest.json").read_text())
    if cache["release"] != "26.06" or set(cache["sources"]) != set(SIX):
        raise RuntimeError("Six-native source identity is incomplete")
    cohort = pd.read_parquet(HERE / "cohort_mapped.parquet").sort_values(["targetId", "diseaseId"]).reset_index(drop=True)
    if len(cohort) != 26235 or cohort.duplicated(["targetId", "diseaseId"]).any():
        raise RuntimeError("Terminal pair unit changed")
    cohort["split"] = cohort.targetId.map(split_name)
    x = np.zeros((len(cohort), len(SIX), 4), dtype=np.float32)
    geometries: dict[str, np.ndarray] = {}
    feature_names = {}
    key = cohort[["targetId", "diseaseId"]]
    for j, datasource in enumerate(SIX):
        source = pd.read_parquet(HERE / f"native_{datasource}_pair_features.parquet")
        if datasource == "eva":
            categories = pd.read_parquet(HERE / "native_eva_category_features.parquet")
            source = source.merge(categories, on=["targetId", "diseaseId"], how="left", validate="one_to_one")
            if source.category_evidence_rows.isna().any():
                raise RuntimeError("EVA category state does not cover native rows")
        merged = key.merge(source, on=["targetId", "diseaseId"], how="left", validate="one_to_one", sort=False)
        available = merged.native_evidence_rows.notna().to_numpy(np.float32)
        score = merged.max_native_score.fillna(0).to_numpy(np.float32)
        mean_score = merged.mean_native_score.fillna(0).to_numpy(np.float32)
        rows = merged.native_evidence_rows.fillna(0).to_numpy(np.float32)
        if not np.isfinite(score).all() or not np.isfinite(mean_score).all() or not np.isfinite(rows).all():
            raise RuntimeError(f"Invalid native core feature: {datasource}")
        if (score < 0).any() or (score > 1).any() or (rows < 0).any():
            raise RuntimeError(f"Out-of-range native core feature: {datasource}")
        x[:, j, 0] = score
        x[:, j, 1] = np.log1p(rows)
        x[:, j, 2] = mean_score
        x[:, j, 3] = available
        geometry, names = native_geometry(datasource, merged, available)
        geometries[datasource] = geometry
        feature_names[datasource] = names
    target_sets = {name: set(cohort.loc[cohort.split == name, "targetId"]) for name in ("train", "validation", "test")}
    if any(target_sets[a] & target_sets[b] for a, b in (("train", "validation"), ("train", "test"), ("validation", "test"))):
        raise RuntimeError("Target leakage in native split")
    return cohort, x, geometries, feature_names


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=False)
    try:
        torch.set_num_threads(4)
        cohort, x, geometry, feature_names = load_native()
        y = cohort.label.to_numpy(np.int64)
        targets = cohort.targetId.to_numpy()
        subsets = {name: np.where(cohort.split.to_numpy() == name)[0] for name in ("train", "validation", "test")}
        tr, va, te = (subsets[name] for name in ("train", "validation", "test"))
        source_test = pd.read_parquet(SOURCE_TEST)
        if not source_test[["targetId", "diseaseId", "label"]].reset_index(drop=True).equals(
            cohort.iloc[te][["targetId", "diseaseId", "label"]].reset_index(drop=True)
        ):
            raise RuntimeError("Native and source-level test pair order differ")
        split_summary = {
            name: {"pairs": int(len(idx)), "targets": len(set(targets[idx])),
                   "positives": int(y[idx].sum()),
                   "native_pair_coverage": {ds: int(x[idx, j, 3].sum()) for j, ds in enumerate(SIX)}}
            for name, idx in subsets.items()
        }
        (OUT / "split_summary.json").write_text(json.dumps(split_summary, indent=2) + "\n")
        folds = list(StratifiedGroupKFold(n_splits=5, shuffle=True, random_state=20261002).split(x[tr], y[tr], targets[tr]))
        if any(set(targets[tr][fit]) & set(targets[tr][held]) for fit, held in folds):
            raise RuntimeError("Native OOF target leakage")
        predictions = {name: {} for name in subsets}
        for name, idx in subsets.items():
            predictions[name]["prevalence"] = np.full(len(idx), float(y[tr].mean()))
        global_features = {
            "count_logistic": count_features(x),
            "calibration_only": calibration_features(x),
            "additive_logistic": additive_features(x),
            "pairwise_logistic": pairwise_features(x),
        }
        for name, features in global_features.items():
            model = new_logistic(c=0.5 if name == "pairwise_logistic" else 1.0).fit(features[tr], y[tr])
            for split, idx in subsets.items():
                predictions[split][name] = probability(model, features[idx])
        masks = presence_mask(x)
        eb = ShrunkRate().fit(masks[tr], y[tr])
        for split, idx in subsets.items():
            predictions[split]["empirical_bayes"] = eb.predict(masks[idx])
        experts = ("additive_logistic", "pairwise_logistic", "empirical_bayes")
        oof_global = np.zeros((len(tr), 3), dtype=float)
        for fit, held in folds:
            for j, name in enumerate(experts[:2]):
                model = new_logistic(c=0.5 if j == 1 else 1.0).fit(global_features[name][tr][fit], y[tr][fit])
                oof_global[held, j] = probability(model, global_features[name][tr][held])
            prior = ShrunkRate().fit(masks[tr][fit], y[tr][fit])
            oof_global[held, 2] = prior.predict(masks[tr][held])
        global_weights, global_loss = simplex_fit(oof_global, y[tr])
        predictions["train"]["stat_moe"] = oof_global @ global_weights
        for split in ("validation", "test"):
            predictions[split]["stat_moe"] = np.column_stack([predictions[split][name] for name in experts]) @ global_weights

        states = {name: np.zeros((len(idx), len(SIX), 4), np.float32) for name, idx in subsets.items()}
        routing = {"global_experts": experts, "global_weights": global_weights.tolist(),
                   "global_oof_logloss": global_loss, "local": {}}
        for j, ds in enumerate(SIX):
            score_features = np.column_stack((x[:, j, 0], x[:, j, 2], x[:, j, 3]))
            geometry_features = geometry[ds]
            category = np.where(x[:, j, 3] == 0, 0, np.where(x[:, j, 0] == 0, 1, 2)).astype(int)
            local_oof = np.zeros((len(tr), 3), dtype=float)
            for fit, held in folds:
                score_model = new_logistic().fit(score_features[tr][fit], y[tr][fit])
                geometry_model = new_logistic(c=0.5).fit(geometry_features[tr][fit], y[tr][fit])
                rate_model = ShrunkRate(40.0).fit(category[tr][fit], y[tr][fit])
                local_oof[held, 0] = probability(score_model, score_features[tr][held])
                local_oof[held, 1] = probability(geometry_model, geometry_features[tr][held])
                local_oof[held, 2] = rate_model.predict(category[tr][held])
            weights, oof_loss = simplex_fit(local_oof, y[tr])
            routing["local"][ds] = {
                "experts": ["native_score_logistic", "native_geometry_logistic", "three_state_shrinkage"],
                "geometry_fields": feature_names[ds], "weights": weights.tolist(),
                "oof_logloss": oof_loss, "train_available_pairs": int(x[tr, j, 3].sum()),
            }
            score_final = new_logistic().fit(score_features[tr], y[tr])
            geometry_final = new_logistic(c=0.5).fit(geometry_features[tr], y[tr])
            rate_final = ShrunkRate(40.0).fit(category[tr], y[tr])
            positive_log_count = x[tr, j, 1][x[tr, j, 3] > 0]
            scale = max(float(np.quantile(positive_log_count, 0.95)), 1.0)
            routing["local"][ds]["coverage_scale_train_q95"] = scale
            for split, idx in subsets.items():
                pred = local_oof @ weights if split == "train" else np.column_stack((
                    probability(score_final, score_features[idx]),
                    probability(geometry_final, geometry_features[idx]),
                    rate_final.predict(category[idx]),
                )) @ weights
                pred = np.clip(pred, 1e-7, 1 - 1e-7)
                states[split][:, j, 0] = pred
                states[split][:, j, 1] = -(pred * np.log(pred) + (1 - pred) * np.log1p(-pred))
                states[split][:, j, 2] = np.clip(x[idx, j, 1] / scale, 0, 2)
                states[split][:, j, 3] = x[idx, j, 3]
        (OUT / "routing_weights.json").write_text(json.dumps(routing, indent=2) + "\n")
        train_oof = cohort.iloc[tr][["targetId", "diseaseId", "label"]].copy()
        for j, ds in enumerate(SIX):
            train_oof[ds + "__prediction"] = states["train"][:, j, 0]
            train_oof[ds + "__availability"] = states["train"][:, j, 3]
        train_oof.to_parquet(OUT / "train_channel_oof.parquet", index=False)

        controls, diagnostics = {}, {}
        for seed in SEEDS:
            model, device, diagnostic, delta = ganglion_fit(
                states["train"], y[tr], states["validation"], y[va],
                seed, OUT, max_epochs=1000, patience=100,
            )
            name = f"ganglion_seed_{seed}"
            for split in ("validation", "test"):
                predictions[split][name] = ganglion_predict(model, states[split], device)
            xte = states["test"]
            ablations = {}
            for j, ds in enumerate(SIX):
                missing = xte.copy()
                missing[:, j, :] = 0
                ablations[ds] = metrics(y[te], ganglion_predict(model, missing, device))["logloss"]
            shuffled = xte.copy()
            rng = np.random.default_rng(seed + 2000)
            for j in range(len(SIX)):
                shuffled[:, j, :] = xte[rng.permutation(len(xte)), j, :]
            controls[name] = {
                "test_logloss_original": metrics(y[te], predictions["test"][name])["logloss"],
                "test_logloss_pipeline_shuffle": metrics(y[te], ganglion_predict(model, shuffled, device))["logloss"],
                "single_pipeline_missing_logloss": ablations,
                "learned_direction_lesion": lesion_controls(model, device, delta, xte, y[te], seed),
            }
            diagnostics[name] = diagnostic
        results = {
            name: {
                "validation": metrics(y[va], predictions["validation"][name]),
                "test": metrics(y[te], predictions["test"][name]),
                "test_grouped_bootstrap_95ci": grouped_ci(y[te], predictions["test"][name], targets[te]),
            }
            for name in predictions["test"]
        }
        (OUT / "metrics.json").write_text(json.dumps(results, indent=2) + "\n")
        (OUT / "controls.json").write_text(json.dumps(controls, indent=2) + "\n")
        (OUT / "ganglion_diagnostics.json").write_text(json.dumps(diagnostics, indent=2) + "\n")
        test_frame = cohort.iloc[te][["targetId", "diseaseId", "label"]].copy()
        for name, pred in predictions["test"].items():
            test_frame[name] = pred
        test_frame.to_parquet(OUT / "test_predictions.parquet", index=False)
        comparisons = test_frame[["targetId", "label", "stat_moe"]].copy()
        comparisons["source_stat_moe"] = source_test.stat_moe.to_numpy()
        comparisons["source_ganglion_202"] = pd.read_parquet(
            HERE / "results/source_level_six/EXP017-GANGLION-LONG-001/test_predictions.parquet"
        ).ganglion_seed_202.to_numpy()
        best_seed = min(SEEDS, key=lambda s: results[f"ganglion_seed_{s}"]["validation"]["logloss"])
        comparisons["native_best_validation_ganglion"] = test_frame[f"ganglion_seed_{best_seed}"].to_numpy()
        relative = {
            "native_stat_moe_minus_source_stat_moe": paired_difference(comparisons, "stat_moe", "source_stat_moe"),
            "native_best_ganglion_minus_source_ganglion_202": paired_difference(
                comparisons, "native_best_validation_ganglion", "source_ganglion_202"
            ),
            "native_best_ganglion_minus_native_stat_moe": paired_difference(
                comparisons, "native_best_validation_ganglion", "stat_moe"
            ),
        }
        (OUT / "paired_comparisons.json").write_text(json.dumps(relative, indent=2) + "\n")
        plt.figure(figsize=(6.6, 4.4))
        names = ["prevalence", "count_logistic", "additive_logistic", "pairwise_logistic",
                 "empirical_bayes", "stat_moe", *(f"ganglion_seed_{seed}" for seed in SEEDS)]
        plt.barh(names, [results[name]["test"]["logloss"] for name in names], color="#397d87")
        plt.xlabel("Test Bernoulli log loss")
        plt.title("EXP017 native six-source retrospective run")
        plt.tight_layout()
        plt.savefig(OUT / "native_test_logloss.png", dpi=160)
        plt.close()
        (OUT / "protocol_and_environment.json").write_text(json.dumps({
            "run_id": RUN_ID,
            "research_id": "STAT-PSYMOE-EXP017-20261002-001",
            "qualification": "Exploratory 26.06 native evidence summaries; no decision-date time lock",
            "source_manifest": str(HERE / "native_cache_manifest.json"),
            "eva_category_definition": str(HERE / "native_eva_category_definition.json"),
            "split": "same FNV1a32 Ensembl target hash 70/15/15 as source-level run",
            "five_fold_oof": "StratifiedGroupKFold by target; local and global weights train-only",
            "state_fields": ["local_prediction", "predictive_entropy_proxy", "scaled_log_native_evidence_rows", "availability"],
            "datetime_fields_used_as_features": [],
            "ganglion": {"seeds": SEEDS, "max_epochs": 1000, "validation_patience": 100,
                         "best_validation_seed": best_seed},
            "test_seen_in_prior_source_level_run": True,
            "versions": {name: version(name) for name in ("numpy", "pandas", "scikit-learn", "scipy", "torch", "duckdb", "pyarrow")},
            "python": platform.python_version(),
        }, indent=2) + "\n")
        print(json.dumps({
            "run_id": RUN_ID,
            "best_validation_seed": best_seed,
            "native_coverage": split_summary,
            "test_logloss": {name: round(value["test"]["logloss"], 6) for name, value in results.items()},
            "paired_differences": {name: value["left_minus_right_logloss"] for name, value in relative.items()},
            "output_dir": str(OUT),
        }, indent=2))
    except Exception as exc:
        (OUT / "failure.json").write_text(json.dumps({
            "run_id": RUN_ID, "error_type": type(exc).__name__, "error": str(exc),
            "existing_outputs": sorted(p.name for p in OUT.iterdir()),
        }, indent=2) + "\n")
        raise


if __name__ == "__main__":
    main()
