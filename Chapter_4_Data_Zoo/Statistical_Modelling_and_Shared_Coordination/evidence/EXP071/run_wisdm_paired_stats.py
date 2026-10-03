"""EXP071: frozen real WISDM paired-window and person-holdout statistical test."""

from __future__ import annotations

import csv
import json
import math
import sys
import warnings
from pathlib import Path

import numpy as np
from sklearn.exceptions import ConvergenceWarning
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler


HERE = Path(__file__).resolve().parent
SOURCE_DIR = HERE.parent / "STAT-PSYMOE-EXP070-20261002-001"
sys.path.insert(0, str(SOURCE_DIR))
from audit_wisdm_source import get_archive, find_member, parse_activity_key  # noqa: E402

CODES = ("A", "D", "E")
CODE_TO_Y = {"A": 1, "D": 2, "E": 3}
WINDOW_TICKS = 10_000_000_000
GRID_STEP_TICKS = 50_000_000
MAX_GAP_TICKS = 1_000_000_000
SEED = 20261002
MODES = {"ACC": slice(0, 33), "GYR": slice(33, 66), "JOINT": slice(0, 66)}


def write_json(name: str, value: dict) -> None:
    (HERE / name).write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def parse_phone(zf, subject: int, sensor: str) -> tuple[dict[str, np.ndarray], dict[str, int], str]:
    suffix = f"raw/phone/{sensor}/data_{subject}_{sensor}_phone.txt"
    name = find_member(zf, suffix)
    if name is None:
        raise ValueError(f"missing official file: {suffix}")
    raw = {code: [] for code in CODES}
    with zf.open(name) as stream:
        for line in stream:
            parts = line.strip().rstrip(b";").split(b",")
            if len(parts) < 2:
                continue
            code = parts[1].decode("ascii", errors="replace").strip()
            if code not in raw:
                continue
            if len(parts) != 6:
                raise ValueError(f"malformed target row in {name}")
            try:
                row_subject = int(parts[0])
                timestamp = int(parts[2])
                values = [float(item) for item in parts[3:]]
            except ValueError as exc:
                raise ValueError(f"bad target value in {name}") from exc
            if row_subject != subject or not all(math.isfinite(v) for v in values):
                raise ValueError(f"wrong subject or nonfinite target row in {name}")
            raw[code].append((timestamp, *values))
    arrays = {code: np.asarray(rows, dtype=np.float64) for code, rows in raw.items()}
    counts = {code: len(rows) for code, rows in raw.items()}
    return arrays, counts, name


def sorted_unique(rows: np.ndarray) -> tuple[np.ndarray, np.ndarray, dict]:
    if rows.ndim != 2 or rows.shape[1] != 4 or len(rows) == 0:
        raise ValueError("empty or malformed activity rows")
    original_ts = rows[:, 0].astype(np.int64)
    inversions = int(np.sum(np.diff(original_ts) < 0))
    order = np.argsort(original_ts, kind="stable")
    ts = original_ts[order]
    xyz = rows[order, 1:]
    unique, inverse, repeats = np.unique(ts, return_inverse=True, return_counts=True)
    if len(unique) < len(ts):
        xyz = np.column_stack([
            np.bincount(inverse, weights=xyz[:, axis], minlength=len(unique)) / repeats
            for axis in range(3)
        ])
    return unique, xyz, {"original_inversions": inversions,
                         "duplicate_timestamps_collapsed": int(len(ts) - len(unique))}


def one_axis_features(x: np.ndarray) -> np.ndarray:
    mean = float(x.mean())
    std = float(x.std())
    p10, p50, p90 = map(float, np.quantile(x, [0.1, 0.5, 0.9]))
    rms = float(np.sqrt(np.mean(x * x)))
    span = float(np.ptp(x))
    mad = float(np.mean(np.abs(np.diff(x))))
    left, right = x[:-1] - x[:-1].mean(), x[1:] - x[1:].mean()
    denom = float(np.sqrt(np.sum(left * left) * np.sum(right * right)))
    corr = float(np.sum(left * right) / denom) if denom > 0 else 0.0
    freq = np.fft.rfftfreq(200, d=0.05)
    power = np.abs(np.fft.rfft(x - mean)) ** 2
    total = float(power[freq > 0].sum())
    low = float(power[(freq >= 0.4) & (freq < 3)].sum() / total) if total > 0 else 0.0
    mid = float(power[(freq >= 3) & (freq < 8)].sum() / total) if total > 0 else 0.0
    return np.array([mean, std, p10, p50, p90, rms, span, mad, corr, low, mid])


def sensor_window_features(times: np.ndarray, xyz: np.ndarray, lo: int, hi: int) -> tuple[np.ndarray | None, str]:
    left = int(np.searchsorted(times, lo, side="left"))
    right = int(np.searchsorted(times, hi, side="left"))
    selected_t = times[left:right]
    if len(selected_t) < 100:
        return None, "fewer_than_100_samples"
    gaps = np.diff(np.concatenate(([lo], selected_t, [hi])))
    if int(np.max(gaps)) > MAX_GAP_TICKS:
        return None, "gap_over_1_second"
    grid = lo + np.arange(200, dtype=np.int64) * GRID_STEP_TICKS
    selected_xyz = xyz[left:right]
    interpolated = [np.interp(grid, selected_t, selected_xyz[:, axis]) for axis in range(3)]
    features = np.concatenate([one_axis_features(axis) for axis in interpolated])
    if features.shape != (33,) or not np.all(np.isfinite(features)):
        raise ValueError("invalid derived sensor feature vector")
    return features, "accepted"


def make_windows(a: tuple[np.ndarray, np.ndarray], g: tuple[np.ndarray, np.ndarray]) -> tuple[list[np.ndarray], dict]:
    at, ax = a
    gt, gx = g
    start = max(int(at[0]), int(gt[0]))
    end = min(int(at[-1]), int(gt[-1]))
    complete = max(0, (end - start) // WINDOW_TICKS)
    features = []
    rejected = {"fewer_than_100_samples": 0, "gap_over_1_second": 0}
    for j in range(int(complete)):
        lo = start + j * WINDOW_TICKS
        hi = lo + WINDOW_TICKS
        af, ar = sensor_window_features(at, ax, lo, hi)
        gf, gr = sensor_window_features(gt, gx, lo, hi)
        if af is None or gf is None:
            rejected[ar if af is None else gr] += 1
            continue
        features.append(np.concatenate([af, gf]))
    return features, {"complete_overlap_windows": int(complete), "accepted": len(features),
                      "rejected": rejected, "leftover_overlap_ticks": int(max(0, end - start) % WINDOW_TICKS)}


def model_probabilities(x_fit, y_fit, x_score) -> np.ndarray:
    model = make_pipeline(StandardScaler(), LogisticRegression(
        C=1.0, penalty="l2", solver="lbfgs", max_iter=500, random_state=SEED,
    ))
    with warnings.catch_warnings():
        warnings.simplefilter("error", ConvergenceWarning)
        warnings.simplefilter("ignore", FutureWarning)
        model.fit(x_fit, y_fit)
    if list(model[-1].classes_) != [1, 2, 3]:
        raise ValueError("fit did not include three classes")
    return model.predict_proba(x_score)


def person_scores(y, subjects, probabilities) -> dict[int, dict]:
    result = {}
    for subject in sorted(map(int, np.unique(subjects))):
        mask = subjects == subject
        true = y[mask]
        prob = probabilities[mask]
        if set(map(int, true)) != {1, 2, 3}:
            raise ValueError(f"subject {subject} lacks all three classes")
        choices = np.argmax(prob, axis=1) + 1
        recalls = [np.mean(choices[true == c] == c) for c in (1, 2, 3)]
        result[subject] = {"windows": int(mask.sum()),
                           "logloss": float(-np.mean(np.log(np.maximum(prob[np.arange(len(true)), true - 1], 1e-15)))),
                           "balanced_accuracy": float(np.mean(recalls))}
    return result


def aggregate(rows: dict[str, dict[int, dict]]) -> dict:
    people = sorted(rows["ACC"])
    means = {name: {metric: float(np.mean([rows[name][s][metric] for s in people]))
                    for metric in ("logloss", "balanced_accuracy")} for name in rows}
    ll = np.array([rows["JOINT"][s]["logloss"] - rows["ACC"][s]["logloss"] for s in people])
    bacc = np.array([rows["JOINT"][s]["balanced_accuracy"] - rows["ACC"][s]["balanced_accuracy"] for s in people])
    rng = np.random.default_rng(SEED)
    picks = rng.integers(0, len(people), size=(2000, len(people)))
    ci = np.quantile(ll[picks].mean(axis=1), [0.025, 0.975])
    return {"people": len(people), "person_equal_weight_means": means,
            "joint_minus_acc_logloss": float(ll.mean()),
            "joint_minus_acc_balanced_accuracy": float(bacc.mean()),
            "paired_person_bootstrap_logloss_95pct_ci": list(map(float, ci)),
            "people_joint_lower_logloss": int(np.sum(ll < 0))}


def model_gate(metrics: dict) -> dict[str, bool]:
    return {"logloss_gain_at_least_0_03": metrics["joint_minus_acc_logloss"] <= -0.03,
            "balanced_accuracy_gain_at_least_0_02": metrics["joint_minus_acc_balanced_accuracy"] >= 0.02,
            "bootstrap_upper_below_zero": metrics["paired_person_bootstrap_logloss_95pct_ci"][1] < 0,
            "two_thirds_people_improved": metrics["people_joint_lower_logloss"] >= math.ceil(2 * metrics["people"] / 3)}


def save_rows(name: str, rows: dict[str, dict[int, dict]]) -> None:
    with (HERE / name).open("w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle)
        writer.writerow(["subject", "windows", "prior_logloss", "prior_bacc", "acc_logloss", "acc_bacc",
                         "gyr_logloss", "gyr_bacc", "joint_logloss", "joint_bacc"])
        for s in sorted(rows["ACC"]):
            writer.writerow([s, rows["ACC"][s]["windows"], rows["PRIOR"][s]["logloss"],
                             rows["PRIOR"][s]["balanced_accuracy"], rows["ACC"][s]["logloss"],
                             rows["ACC"][s]["balanced_accuracy"], rows["GYR"][s]["logloss"],
                             rows["GYR"][s]["balanced_accuracy"], rows["JOINT"][s]["logloss"],
                             rows["JOINT"][s]["balanced_accuracy"]])


def main() -> None:
    expected = json.loads((SOURCE_DIR / "SOURCE_MATRIX.json").read_text(encoding="utf-8"))
    zf, download_bytes, inner_bytes = get_archive()
    key_name, mapping = parse_activity_key(zf)
    if any(mapping.get(c, "").lower() != n.lower() for c, n in (("A", "Walking"), ("D", "Sitting"), ("E", "Standing"))):
        raise ValueError("activity key changed")
    feature_rows, labels, subjects = [], [], []
    observed_counts, window_counts = {}, {}
    source_matches = True
    for subject in range(1600, 1651):
        acc_rows, acc_counts, acc_name = parse_phone(zf, subject, "accel")
        gyr_rows, gyr_counts, gyr_name = parse_phone(zf, subject, "gyro")
        observed_counts[str(subject)] = {"accel": acc_counts, "gyro": gyr_counts}
        info = {"split": "test" if (subject - 1600) % 5 == 0 else "development",
                "accel_member": acc_name, "gyro_member": gyr_name, "activities": {}}
        for code in CODES:
            prior = expected["subjects"][str(subject)]["activities"][code]
            source_matches &= (acc_counts[code] == prior["accel"]["valid_rows"]
                               and gyr_counts[code] == prior["gyro"]["valid_rows"])
            at, ax, adiag = sorted_unique(acc_rows[code])
            gt, gx, gdiag = sorted_unique(gyr_rows[code])
            windows, diag = make_windows((at, ax), (gt, gx))
            info["activities"][code] = {"accel_source_rows": acc_counts[code],
                                        "gyro_source_rows": gyr_counts[code],
                                        "accel_order": adiag, "gyro_order": gdiag, **diag}
            for row in windows:
                feature_rows.append(row)
                labels.append(CODE_TO_Y[code])
                subjects.append(subject)
        info["qualified"] = all(info["activities"][c]["accepted"] >= 10 for c in CODES)
        window_counts[str(subject)] = info
    recheck = {"official_download_bytes": download_bytes, "inner_zip_bytes": inner_bytes,
               "activity_key_member": key_name, "activity_mapping": {c: mapping[c] for c in CODES},
               "all_51_by_class_sensor_raw_row_counts_match_EXP070": bool(source_matches),
               "gate": "SOURCE_STRUCTURE_MATCH" if source_matches else "STOP_SOURCE_VERSION_DRIFT"}
    write_json("SOURCE_RECHECK.json", recheck)
    if not source_matches:
        print(json.dumps(recheck, indent=2))
        return

    dev_people = [s for s in range(1600, 1651) if (s - 1600) % 5 != 0 and window_counts[str(s)]["qualified"]]
    test_people = [s for s in range(1600, 1651) if (s - 1600) % 5 == 0 and window_counts[str(s)]["qualified"]]
    total_accepted = sum(window_counts[str(s)]["activities"][c]["accepted"] for s in range(1600, 1651) for c in CODES)
    support_gates = {"at_least_32_development_people": len(dev_people) >= 32,
                     "at_least_8_test_people": len(test_people) >= 8,
                     "at_least_1800_accepted_windows": total_accepted >= 1800}
    window_result = {"window_ticks": WINDOW_TICKS, "grid_step_ticks": GRID_STEP_TICKS,
                     "max_gap_ticks": MAX_GAP_TICKS, "min_samples_per_sensor_window": 100,
                     "development_people": dev_people, "test_people": test_people,
                     "total_accepted_windows_before_person_qualification": total_accepted,
                     "support_gates": support_gates, "subjects": window_counts,
                     "decision": "PAIRED_WINDOW_SUPPORT_READY" if all(support_gates.values()) else "STOP_PAIRED_WINDOW_SUPPORT"}
    write_json("WINDOW_COUNTS.json", window_result)
    print(json.dumps({"source_gate": recheck["gate"], "window_gate": window_result["decision"],
                      "development_people": len(dev_people), "test_people": len(test_people),
                      "accepted_windows": total_accepted, "support_gates": support_gates}, indent=2))
    if not all(support_gates.values()):
        return

    x = np.asarray(feature_rows, dtype=np.float64)
    y = np.asarray(labels, dtype=np.int32)
    person = np.asarray(subjects, dtype=np.int32)
    valid_people = np.array(dev_people + test_people, dtype=np.int32)
    keep = np.isin(person, valid_people)
    x, y, person = x[keep], y[keep], person[keep]
    dev = np.isin(person, dev_people)
    test = np.isin(person, test_people)
    if x.shape[1] != 66 or not np.all(np.isfinite(x)) or np.any(dev & test):
        raise ValueError("invalid feature or split matrix")
    fold_for = {s: i % 5 for i, s in enumerate(dev_people)}
    dev_indices = np.flatnonzero(dev)
    dev_prob = {mode: np.zeros((len(dev_indices), 3)) for mode in (*MODES, "PRIOR")}
    dev_x, dev_y, dev_subject = x[dev], y[dev], person[dev]
    for fold in range(5):
        score = np.array([fold_for[int(s)] == fold for s in dev_subject])
        train = ~score
        for mode, columns in MODES.items():
            dev_prob[mode][score] = model_probabilities(dev_x[train, columns], dev_y[train],
                                                       dev_x[score, columns])
        freq = np.bincount(dev_y[train], minlength=4)[1:].astype(float)
        freq /= freq.sum()
        dev_prob["PRIOR"][score] = freq
    dev_rows = {mode: person_scores(dev_y, dev_subject, prob) for mode, prob in dev_prob.items()}
    save_rows("OOF_PERSON_ROWS.csv", dev_rows)
    dev_metrics = aggregate(dev_rows)
    dev_metrics.update({"fold_subject_assignment": fold_for, "bootstrap_resamples": 2000,
                        "bootstrap_seed": SEED, "source_gate": recheck["gate"],
                        "window_gate": window_result["decision"], "test_performance_scored": False})
    dev_metrics["gates"] = model_gate(dev_metrics)
    dev_metrics["decision"] = "PASS_JOINT_DEV_GATE" if all(dev_metrics["gates"].values()) else "STOP_JOINT_DEV_GATE"
    write_json("OOF_METRICS.json", dev_metrics)
    print(json.dumps({"oof": {k: dev_metrics[k] for k in (
        "person_equal_weight_means", "joint_minus_acc_logloss", "joint_minus_acc_balanced_accuracy",
        "paired_person_bootstrap_logloss_95pct_ci", "people_joint_lower_logloss", "gates", "decision")}}, indent=2))
    if dev_metrics["decision"] != "PASS_JOINT_DEV_GATE":
        return

    test_x, test_y, test_subject = x[test], y[test], person[test]
    test_prob = {mode: model_probabilities(dev_x[:, columns], dev_y, test_x[:, columns])
                 for mode, columns in MODES.items()}
    freq = np.bincount(dev_y, minlength=4)[1:].astype(float)
    freq /= freq.sum()
    test_prob["PRIOR"] = np.broadcast_to(freq, (len(test_y), 3)).copy()
    test_rows = {mode: person_scores(test_y, test_subject, prob) for mode, prob in test_prob.items()}
    save_rows("TEST_PERSON_ROWS.csv", test_rows)
    test_metrics = aggregate(test_rows)
    test_metrics.update({"bootstrap_resamples": 2000, "bootstrap_seed": SEED,
                         "development_gate": dev_metrics["decision"], "test_performance_scored": True})
    test_metrics["gates"] = model_gate(test_metrics)
    test_metrics["decision"] = ("WISDM_GYRO_INCREMENT_SUPPORTED_WITHIN_PROTOCOL"
                                if all(test_metrics["gates"].values()) else "NO_INDEPENDENT_PERSON_HOLDOUT_INCREMENT")
    write_json("TEST_METRICS.json", test_metrics)
    print(json.dumps({"test": {k: test_metrics[k] for k in (
        "person_equal_weight_means", "joint_minus_acc_logloss", "joint_minus_acc_balanced_accuracy",
        "paired_person_bootstrap_logloss_95pct_ci", "people_joint_lower_logloss", "gates", "decision")}}, indent=2))


if __name__ == "__main__":
    main()
