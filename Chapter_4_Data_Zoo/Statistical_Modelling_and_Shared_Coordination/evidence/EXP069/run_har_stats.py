"""EXP069 frozen person-level ACC/GYR/JOINT statistical comparison."""

from __future__ import annotations

import csv
import io
import json
import sys
import warnings
from pathlib import Path

import numpy as np
from sklearn.exceptions import ConvergenceWarning
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler


HERE = Path(__file__).resolve().parent
SOURCE_DIR = HERE.parent / "STAT-PSYMOE-EXP068-20261002-001"
sys.path.insert(0, str(SOURCE_DIR))
from audit_uci_har_source import CHANNELS, member, official_archive  # noqa: E402

SEED = 20261002
MODES = {"ACC": slice(0, 33), "GYR": slice(33, 66), "JOINT": slice(0, 66)}


def read_int_member(zf, suffix: str) -> np.ndarray:
    _, raw = member(zf, suffix)
    return np.loadtxt(io.BytesIO(raw), dtype=np.int32)


def channel_features(x: np.ndarray) -> np.ndarray:
    mean = x.mean(axis=1)
    std = x.std(axis=1)
    quantiles = np.quantile(x, [0.10, 0.50, 0.90], axis=1).T
    rms = np.sqrt(np.mean(np.square(x), axis=1))
    span = np.ptp(x, axis=1)
    mean_abs_delta = np.mean(np.abs(np.diff(x, axis=1)), axis=1)
    left = x[:, :-1] - x[:, :-1].mean(axis=1, keepdims=True)
    right = x[:, 1:] - x[:, 1:].mean(axis=1, keepdims=True)
    denominator = np.sqrt(np.sum(left * left, axis=1) * np.sum(right * right, axis=1))
    lag_corr = np.divide(np.sum(left * right, axis=1), denominator,
                         out=np.zeros(len(x)), where=denominator > 0)
    freq = np.fft.rfftfreq(128, d=1 / 50)
    spectrum = np.abs(np.fft.rfft(x - mean[:, None], axis=1)) ** 2
    total_energy = spectrum[:, freq > 0].sum(axis=1)
    low = np.divide(spectrum[:, (freq >= 0.4) & (freq < 3)].sum(axis=1), total_energy,
                    out=np.zeros(len(x)), where=total_energy > 0)
    mid = np.divide(spectrum[:, (freq >= 3) & (freq < 10)].sum(axis=1), total_energy,
                    out=np.zeros(len(x)), where=total_energy > 0)
    return np.column_stack((mean, std, quantiles, rms, span, mean_abs_delta, lag_corr, low, mid))


def read_domain(zf, domain: str) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    subjects = read_int_member(zf, f"{domain}/subject_{domain}.txt")
    labels = read_int_member(zf, f"{domain}/y_{domain}.txt")
    blocks = []
    for channel in CHANNELS:
        _, raw = member(zf, f"{domain}/Inertial Signals/{channel}_{domain}.txt")
        matrix = np.loadtxt(io.BytesIO(raw), dtype=np.float64)
        if matrix.shape != (len(labels), 128) or not np.all(np.isfinite(matrix)):
            raise ValueError(f"invalid signal matrix: {domain}/{channel}: {matrix.shape}")
        blocks.append(channel_features(matrix))
    features = np.hstack(blocks)
    if len(subjects) != len(labels) or features.shape != (len(labels), 66):
        raise ValueError(f"alignment failure: {domain}")
    if not np.all(np.isfinite(features)) or set(labels) != set(range(1, 7)):
        raise ValueError(f"nonfinite feature or invalid label: {domain}")
    return features, labels, subjects


def source_summary(y: np.ndarray, subjects: np.ndarray) -> dict:
    return {
        "windows": int(len(y)),
        "subjects": sorted(map(int, np.unique(subjects))),
        "by_class": {str(c): {
            "windows": int(np.sum(y == c)),
            "subjects": int(len(np.unique(subjects[y == c]))),
        } for c in range(1, 7)},
    }


def classifier():
    return make_pipeline(StandardScaler(), LogisticRegression(
        C=1.0, penalty="l2", solver="lbfgs", max_iter=500, random_state=SEED,
    ))


def fit_predict(x_fit: np.ndarray, y_fit: np.ndarray, x_score: np.ndarray) -> np.ndarray:
    model = classifier()
    with warnings.catch_warnings():
        warnings.simplefilter("error", ConvergenceWarning)
        model.fit(x_fit, y_fit)
    if list(model[-1].classes_) != list(range(1, 7)):
        raise ValueError("fit missing one or more classes")
    return model.predict_proba(x_score)


def person_scores(y: np.ndarray, subjects: np.ndarray, probabilities: np.ndarray) -> dict[int, dict]:
    if probabilities.shape != (len(y), 6):
        raise ValueError("probability shape mismatch")
    result = {}
    for subject in sorted(map(int, np.unique(subjects))):
        mask = subjects == subject
        true = y[mask]
        prob = probabilities[mask]
        if set(map(int, true)) != set(range(1, 7)):
            raise ValueError(f"subject {subject} missing activity class")
        choice = np.argmax(prob, axis=1) + 1
        recalls = [np.mean(choice[true == c] == c) for c in range(1, 7)]
        result[subject] = {
            "windows": int(mask.sum()),
            "logloss": float(-np.mean(np.log(np.maximum(prob[np.arange(len(true)), true - 1], 1e-15)))),
            "balanced_accuracy": float(np.mean(recalls)),
        }
    return result


def comparison(rows: dict[str, dict[int, dict]]) -> dict:
    subjects = sorted(rows["ACC"])
    means = {model: {
        metric: float(np.mean([rows[model][s][metric] for s in subjects]))
        for metric in ("logloss", "balanced_accuracy")
    } for model in rows}
    delta_ll = np.array([rows["JOINT"][s]["logloss"] - rows["ACC"][s]["logloss"] for s in subjects])
    delta_bacc = np.array([rows["JOINT"][s]["balanced_accuracy"] - rows["ACC"][s]["balanced_accuracy"] for s in subjects])
    rng = np.random.default_rng(SEED)
    picks = rng.integers(0, len(subjects), size=(2000, len(subjects)))
    ci = np.quantile(delta_ll[picks].mean(axis=1), [0.025, 0.975])
    return {
        "subjects": len(subjects),
        "person_equal_weight_means": means,
        "joint_minus_acc_logloss": float(np.mean(delta_ll)),
        "joint_minus_acc_balanced_accuracy": float(np.mean(delta_bacc)),
        "paired_person_bootstrap_logloss_95pct_ci": list(map(float, ci)),
        "subjects_joint_lower_logloss": int(np.sum(delta_ll < 0)),
    }


def save_person_rows(path: Path, rows: dict[str, dict[int, dict]]) -> None:
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle)
        writer.writerow(["subject", "windows", "prior_logloss", "prior_bacc",
                         "acc_logloss", "acc_bacc", "gyr_logloss", "gyr_bacc",
                         "joint_logloss", "joint_bacc"])
        for s in sorted(rows["ACC"]):
            writer.writerow([s, rows["ACC"][s]["windows"],
                             rows["PRIOR"][s]["logloss"], rows["PRIOR"][s]["balanced_accuracy"],
                             rows["ACC"][s]["logloss"], rows["ACC"][s]["balanced_accuracy"],
                             rows["GYR"][s]["logloss"], rows["GYR"][s]["balanced_accuracy"],
                             rows["JOINT"][s]["logloss"], rows["JOINT"][s]["balanced_accuracy"]])


def gate(metrics: dict, threshold_people: int) -> dict[str, bool]:
    return {
        "logloss_gain_at_least_0_03": metrics["joint_minus_acc_logloss"] <= -0.03,
        "balanced_accuracy_gain_at_least_0_02": metrics["joint_minus_acc_balanced_accuracy"] >= 0.02,
        "bootstrap_upper_below_zero": metrics["paired_person_bootstrap_logloss_95pct_ci"][1] < 0,
        "enough_people_improved": metrics["subjects_joint_lower_logloss"] >= threshold_people,
    }


def write_json(name: str, obj: dict) -> None:
    (HERE / name).write_text(json.dumps(obj, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def main() -> None:
    zf, download_bytes, _ = official_archive()
    x_train, y_train, subject_train = read_domain(zf, "train")
    x_test, y_test, subject_test = read_domain(zf, "test")
    expected = json.loads((SOURCE_DIR / "SOURCE_MATRIX.json").read_text(encoding="utf-8"))
    actual_train = source_summary(y_train, subject_train)
    actual_test = source_summary(y_test, subject_test)
    checks = {
        domain: (actual["windows"] == expected[domain]["windows"]
                 and actual["subjects"] == expected[domain]["subjects"]
                 and actual["by_class"] == expected[domain]["by_class"])
        for domain, actual in (("train", actual_train), ("test", actual_test))
    }
    checks["subject_disjoint"] = not bool(set(actual_train["subjects"]) & set(actual_test["subjects"]))
    checks["six_channels_66_features"] = x_train.shape[1] == x_test.shape[1] == 66
    recheck = {"download_bytes": download_bytes, "checks": checks,
               "train": actual_train, "test": actual_test,
               "gate": "SOURCE_STRUCTURE_MATCH" if all(checks.values()) else "STOP_SOURCE_VERSION_DRIFT"}
    write_json("SOURCE_RECHECK.json", recheck)
    if not all(checks.values()):
        print(json.dumps(recheck, ensure_ascii=False))
        return

    oof = {mode: np.zeros((len(y_train), 6), dtype=np.float64) for mode in (*MODES, "PRIOR")}
    people = sorted(map(int, np.unique(subject_train)))
    folds = {subject: i % 5 for i, subject in enumerate(people)}
    for fold in range(5):
        score_mask = np.array([folds[int(s)] == fold for s in subject_train])
        fit_mask = ~score_mask
        for mode, columns in MODES.items():
            oof[mode][score_mask] = fit_predict(x_train[fit_mask, columns], y_train[fit_mask],
                                                x_train[score_mask, columns])
        freq = np.bincount(y_train[fit_mask], minlength=7)[1:].astype(np.float64)
        freq /= freq.sum()
        oof["PRIOR"][score_mask] = freq
    oof_rows = {mode: person_scores(y_train, subject_train, prob) for mode, prob in oof.items()}
    save_person_rows(HERE / "OOF_PERSON_ROWS.csv", oof_rows)
    oof_metrics = comparison(oof_rows)
    oof_metrics.update({"fold_subject_assignment": folds, "bootstrap_resamples": 2000,
                        "bootstrap_seed": SEED, "models": "fixed L2 logistic C=1, scaler fit only on fold training people",
                        "source_recheck": recheck["gate"], "test_performance_scored": False})
    oof_metrics["gates"] = gate(oof_metrics, threshold_people=14)
    oof_metrics["decision"] = "PASS_JOINT_DEV_GATE" if all(oof_metrics["gates"].values()) else "STOP_JOINT_DEV_GATE"
    write_json("OOF_METRICS.json", oof_metrics)
    print(json.dumps({"oof": {k: oof_metrics[k] for k in (
        "person_equal_weight_means", "joint_minus_acc_logloss", "joint_minus_acc_balanced_accuracy",
        "paired_person_bootstrap_logloss_95pct_ci", "subjects_joint_lower_logloss", "gates", "decision")}}, indent=2))
    if oof_metrics["decision"] != "PASS_JOINT_DEV_GATE":
        return

    test_prob = {mode: fit_predict(x_train[:, cols], y_train, x_test[:, cols]) for mode, cols in MODES.items()}
    freq = np.bincount(y_train, minlength=7)[1:].astype(np.float64)
    freq /= freq.sum()
    test_prob["PRIOR"] = np.broadcast_to(freq, (len(y_test), 6)).copy()
    test_rows = {mode: person_scores(y_test, subject_test, prob) for mode, prob in test_prob.items()}
    save_person_rows(HERE / "TEST_PERSON_ROWS.csv", test_rows)
    test_metrics = comparison(test_rows)
    test_metrics.update({"bootstrap_resamples": 2000, "bootstrap_seed": SEED,
                         "development_gate": oof_metrics["decision"], "test_performance_scored": True})
    test_metrics["gates"] = gate(test_metrics, threshold_people=6)
    test_metrics["decision"] = ("REAL_HAR_GYRO_INCREMENT_SUPPORTED_WITHIN_PROTOCOL"
                                if all(test_metrics["gates"].values()) else "NO_INDEPENDENT_PERSON_HOLDOUT_INCREMENT")
    write_json("TEST_METRICS.json", test_metrics)
    print(json.dumps({"test": {k: test_metrics[k] for k in (
        "person_equal_weight_means", "joint_minus_acc_logloss", "joint_minus_acc_balanced_accuracy",
        "paired_person_bootstrap_logloss_95pct_ci", "subjects_joint_lower_logloss", "gates", "decision")}}, indent=2))


if __name__ == "__main__":
    main()
