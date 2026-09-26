#!/usr/bin/env python3
"""Deterministic release checks of supplied evidence; no training or downloads."""
import argparse
import csv
import importlib.util
import json
import math
import sys
from pathlib import Path

import numpy as np

sys.dont_write_bytecode = True


def rows(path):
    with path.open(encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def module(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    obj = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(obj)
    return obj


def verify(root):
    cloud = root / "evidence/cloud/01_Experiments"
    out = {"operation": "deterministic recalculation and source-code counterexamples",
           "neural_training_runs": 0, "new_pretrained_inference_runs": 0}
    ws1 = rows(cloud / "01_WORD_SENSITIVITY_001/WORD_SENSITIVITY_001_intervention_validation.csv")
    stats = {}
    for metric in ("FutureGain", "Drive", "Steer"):
        pairs = []
        for row in ws1:
            try:
                p, o = float(row[metric + "_pred"]), float(row[metric + "_obs"])
                if np.isfinite(p) and np.isfinite(o):
                    pairs.append((p, o))
            except (ValueError, TypeError):
                pass
        p, o = np.asarray(pairs).T
        stats[metric] = {"n": len(p), "pearson_r": float(np.corrcoef(p, o)[0, 1]),
                         "median_relative_error_with_1e_12_floor_pct": float(np.median(abs(p-o)/(abs(p)+1e-12))*100),
                         "max_absolute_error": float(np.max(abs(p-o))),
                         "zero_observed_count": int(np.sum(o == 0))}
    assert stats["Drive"]["n"] == 44 and stats["Steer"]["n"] == 43
    assert all(value["pearson_r"] > .99999 for value in stats.values())
    out["scanner"] = stats

    ws2 = rows(cloud / "02_WORD_SENSITIVITY_002/WORD_SENSITIVITY_002_state_transplant_full.csv")
    tokens, states = sorted({r["token"] for r in ws2}), sorted({int(r["state_id"]) for r in ws2})
    lookup = {(r["token"], int(r["state_id"])): r for r in ws2}
    variance = {}
    for metric in ("ImmediateDrive", "InputGain", "CarryGain", "ProbeSteer", "Alignment", "StateDisplacement"):
        x = np.array([[float(lookup[t, s][metric]) for s in states] for t in tokens])
        if metric != "Alignment":
            x = np.log10(x)
        grand = x.mean()
        a = x.mean(axis=1, keepdims=True) - grand
        b = x.mean(axis=0, keepdims=True) - grand
        interaction = x - grand - a - b
        ss = np.sum((x-grand)**2)
        vals = [float(x.shape[1]*np.sum(a*a)/ss*100),
                float(x.shape[0]*np.sum(b*b)/ss*100), float(np.sum(interaction**2)/ss*100)]
        assert abs(sum(vals)-100) < 1e-8
        variance[metric] = dict(zip(("token_pct", "state_pct", "interaction_pct"), vals))
    assert len(ws2) == 3520 and abs(variance["ImmediateDrive"]["interaction_pct"]-74.33) < .01
    out["state_transplant"] = {"rows": len(ws2), "tokens": len(tokens), "states": len(states), "variance": variance}

    atlas_dir = cloud / "03_TOKEN_OPERATOR_ATLAS_001"
    atlas = module(atlas_dir / "TOKEN_OPERATOR_ATLAS_001_os.py", "release_atlas")
    transitions = rows(atlas_dir / "TOKEN_OPERATOR_ATLAS_001_operator_state_table.csv")
    error = 0.0
    for row in transitions:
        h = np.array([float(row[f"h_in_{k}"]) for k in range(1,11)])
        expected = np.array([float(row[f"h_out_{k}"]) for k in range(1,11)])
        error = max(error, float(np.max(abs(atlas.apply(row["token"], h)-expected))))
    assert len(transitions) == 6336 and error < 1e-12
    out["recovered_runtime_consistency"] = {"transitions": len(transitions), "max_coordinate_error": error,
        "comparison": "recovered runtime versus its saved transition table"}

    tc4 = cloud / "09_TOOL_CALL_004"
    incidents = rows(tc4 / "TOOL_CALL_004_heldout_wrong_case_dissection.csv")
    recovered = sum(r["channel_removal_flips_correct"].lower() == "true" for r in incidents)
    similarity = rows(tc4 / "TOOL_CALL_004_cross_model_geometry_similarity.csv")
    geometry = {}
    for same in (True, False):
        chosen = [r for r in similarity if (r["same_architecture"].lower() == "true") == same]
        geometry["within_architecture" if same else "cross_architecture"] = {
            "pairs": len(chosen),
            "fingerprint_correlation_mean": float(np.mean([float(r["fingerprint_corr"]) for r in chosen])),
            "gradient_gram_correlation_mean": float(np.mean([float(r["gradient_gram_corr"]) for r in chosen]))}
    assert recovered == 25 and len(incidents) == 41
    out["cloud_semantic_selection"] = {"architecture_case_errors": len(incidents),
        "distinct_tasks": len({r["case_id"] for r in incidents}),
        "retrospective_pairwise_recoveries": recovered, "recovery_percent": recovered/len(incidents)*100,
        "geometry": geometry}

    stability = module(cloud / "06_TOOL_CALL_001/TOOL_CALL_001_stability_guard.py", "release_stability")
    original = stability.sample_metrics({"action_names": ["winner", "runner", "third"],
        "logits": np.array([[2.,1.,0.]]), "logit_grads": np.array([[[0.],[.1],[100.]]])})[0]
    nearest = min((2-1)/.1, (2-0)/100)
    finite_winner = int(np.argmax(np.array([2.,1.,0.])+np.array([0.,.1,100.])*.02001))
    assert math.isclose(original["tool_stability_radius"], 10) and nearest == .02 and finite_winner == 2

    validator = module(cloud / "07_TOOL_CALL_002/TOOL_CALL_002_partial_operator_guard.py", "release_guard")
    nan_ok = validator.typ_ok(float("nan"), "number")
    unknown_integer_ok = validator.typ_ok("not an integer", "integer")
    readiness = module(cloud / "08_TOOL_CALL_003/TOOL_CALL_003_action_readiness_os.py", "release_readiness")
    diagnostic = readiness.evaluate({"hard_call_domain": False, "actions": [
        {"name": "CALL:example", "kind": "CALL", "score": 2., "gradient": [1.], "admissible": True},
        {"name": "CONTINUE", "kind": "CONTINUE", "score": 1., "gradient": [0.], "admissible": True}]})
    assert nan_ok and unknown_integer_ok and diagnostic["operation"] == "EXECUTE"
    semantic = module(tc4 / "TOOL_CALL_004_semantic_selection_os.py", "release_semantic")
    counterexample = {"correct_id": "correct", "candidates": [
        {"id": "wrong", "full": 3., "name_neutral": 1., "description_neutral": 3., "schema_neutral": 3.},
        {"id": "correct", "full": 2., "name_neutral": 2., "description_neutral": 2., "schema_neutral": 2.},
        {"id": "third", "full": 1., "name_neutral": 4., "description_neutral": 1., "schema_neutral": 1.}]}
    source_diagnosis = semantic.diagnose(counterexample)
    out["source_counterexamples"] = {"runner_up_radius": original["tool_stability_radius"],
        "all_competitor_minimum": nearest, "finite_winning_candidate_index": finite_winner,
        "historical_type_check_accepts_nan": bool(nan_ok),
        "historical_unknown_integer_type_falls_through": bool(unknown_integer_ok),
        "historical_readiness_operation_with_false_hard_domain": diagnostic["operation"],
        "pairwise_vs_all_candidate_construction": {"correct_minus_original_wrong_after": 1.,
            "winner_after": "third", "source_diagnosis": source_diagnosis}}
    n, k, z = 100, 99, 1.959963984540054
    phat = k/n
    center = (phat+z*z/(2*n))/(1+z*z/n)
    half = z*math.sqrt(phat*(1-phat)/n+z*z/(4*n*n))/(1+z*z/n)
    out["reported_local_arithmetic_only"] = {
        "four_view_accepted_accuracy": 11/28,
        "wilson_99_of_100": [center-half, center+half],
        "paired_exact_p_for_59_vs_0": 2*2**(-59),
        "test_policy_coverage": 38/100,
        "paraphrase_original_policy_coverage": 12/40,
        "paraphrase_policy_coverage": 2/40,
        "source": "aggregate values transcribed from supplied local reports"}
    out["status"] = "PASS"
    return out


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[2])
    parser.add_argument("--out", type=Path)
    args = parser.parse_args()
    result = verify(args.root.resolve())
    payload = json.dumps(result, ensure_ascii=False, indent=2, allow_nan=False)
    if args.out:
        args.out.write_text(payload+"\n", encoding="utf-8")
    print(payload)
