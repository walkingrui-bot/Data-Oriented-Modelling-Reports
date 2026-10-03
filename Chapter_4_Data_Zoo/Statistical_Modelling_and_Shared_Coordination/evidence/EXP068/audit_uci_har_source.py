"""EXP068 source-only audit. Reads UCI240's official archive entirely in memory."""

from __future__ import annotations

import io
import json
import math
import urllib.request
import zipfile
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path


URL = "https://archive.ics.uci.edu/static/public/240/human%2Bactivity%2Brecognition%2Busing%2Bsmartphones.zip"
HERE = Path(__file__).resolve().parent
MAX_DOWNLOAD = 70 * 1024 * 1024
CHANNELS = (
    "total_acc_x", "total_acc_y", "total_acc_z",
    "body_gyro_x", "body_gyro_y", "body_gyro_z",
)


def official_archive() -> tuple[zipfile.ZipFile, int, int]:
    request = urllib.request.Request(URL, headers={"User-Agent": "StatPsyMoE-EXP068-source-audit/1.0"})
    with urllib.request.urlopen(request, timeout=120) as response:
        declared = response.headers.get("Content-Length")
        if declared is not None and int(declared) > MAX_DOWNLOAD:
            raise ValueError(f"official archive exceeds frozen {MAX_DOWNLOAD} byte download cap")
        data = response.read(MAX_DOWNLOAD + 1)
    if len(data) > MAX_DOWNLOAD:
        raise ValueError(f"official archive exceeds frozen {MAX_DOWNLOAD} byte download cap")
    outer = zipfile.ZipFile(io.BytesIO(data))
    names = outer.namelist()
    if any(name.endswith("train/subject_train.txt") for name in names):
        return outer, len(data), 0
    inner = [name for name in names if name.lower().endswith(".zip")]
    if len(inner) != 1:
        raise ValueError(f"expected one inner ZIP or direct HAR files; inner ZIP count={len(inner)}")
    info = outer.getinfo(inner[0])
    if info.file_size > 100 * 1024 * 1024:
        raise ValueError("inner ZIP exceeds 100 MiB bound")
    inner_data = outer.read(inner[0])
    return zipfile.ZipFile(io.BytesIO(inner_data)), len(data), len(inner_data)


def member(zf: zipfile.ZipFile, suffix: str) -> tuple[str, bytes]:
    found = [name for name in zf.namelist() if name.endswith(suffix) and not name.startswith("__MACOSX/")]
    if len(found) != 1:
        raise ValueError(f"expected exactly one member ending {suffix!r}, got {found[:5]}")
    info = zf.getinfo(found[0])
    if info.file_size > 25 * 1024 * 1024:
        raise ValueError(f"member exceeds 25 MiB bound: {found[0]}")
    return found[0], zf.read(found[0])


def one_domain(zf: zipfile.ZipFile, domain: str) -> tuple[dict, set[tuple[bytes, ...]]]:
    subject_name, subject_raw = member(zf, f"{domain}/subject_{domain}.txt")
    label_name, label_raw = member(zf, f"{domain}/y_{domain}.txt")
    subjects = [int(line) for line in subject_raw.splitlines() if line.strip()]
    labels = [int(line) for line in label_raw.splitlines() if line.strip()]
    channels: dict[str, list[bytes]] = {}
    channel_meta: dict[str, dict] = {}
    valid_all = True
    for channel in CHANNELS:
        name, raw = member(zf, f"{domain}/Inertial Signals/{channel}_{domain}.txt")
        rows = [b" ".join(line.split()) for line in raw.splitlines() if line.strip()]
        bad_width = 0
        bad_finite = 0
        for row in rows:
            values = row.split()
            if len(values) != 128:
                bad_width += 1
                continue
            try:
                if any(not math.isfinite(float(value)) for value in values):
                    bad_finite += 1
            except ValueError:
                bad_finite += 1
        channel_meta[channel] = {
            "member": name,
            "rows": len(rows),
            "invalid_width": bad_width,
            "invalid_or_nonfinite": bad_finite,
        }
        valid_all &= bad_width == 0 and bad_finite == 0
        channels[channel] = rows
    n = len(labels)
    equal_lengths = len(subjects) == n and all(len(rows) == n for rows in channels.values())
    valid_all &= equal_lengths and set(labels) <= set(range(1, 7))
    by_class: dict[str, dict] = {}
    for label in range(1, 7):
        indices = [i for i, y in enumerate(labels) if y == label]
        by_class[str(label)] = {
            "windows": len(indices),
            "subjects": len({subjects[i] for i in indices}) if len(subjects) == n else None,
        }
    full_keys: set[tuple[bytes, ...]] = set()
    if equal_lengths:
        full_keys = set(zip(*(channels[channel] for channel in CHANNELS)))
    result = {
        "label_member": label_name,
        "subject_member": subject_name,
        "windows": n,
        "subjects": sorted(set(subjects)),
        "unique_subjects": len(set(subjects)),
        "labels_outside_1_to_6": sum(y not in range(1, 7) for y in labels),
        "lengths_aligned": equal_lengths,
        "all_six_channels_128_finite": bool(valid_all),
        "by_class": by_class,
        "channels": channel_meta,
        "unique_six_channel_windows": len(full_keys) if equal_lengths else None,
    }
    return result, full_keys


def main() -> None:
    archive, download_bytes, inner_bytes = official_archive()
    train, train_keys = one_domain(archive, "train")
    test, test_keys = one_domain(archive, "test")
    overlap = sorted(set(train["subjects"]) & set(test["subjects"]))
    duplicate_keys = len(train_keys & test_keys)
    total = train["windows"] + test["windows"]
    gates = {
        "total_valid_windows_at_least_9000": total >= 9000 and train["all_six_channels_128_finite"] and test["all_six_channels_128_finite"],
        "train_at_least_20_subjects": train["unique_subjects"] >= 20,
        "test_at_least_8_subjects": test["unique_subjects"] >= 8,
        "total_at_least_28_subjects": len(set(train["subjects"]) | set(test["subjects"])) >= 28,
        "subject_sets_disjoint": len(overlap) == 0,
        "each_class_train_at_least_15_subjects": all(train["by_class"][str(y)]["subjects"] >= 15 for y in range(1, 7)),
        "each_class_test_at_least_6_subjects": all(test["by_class"][str(y)]["subjects"] >= 6 for y in range(1, 7)),
        "six_channels_aligned_width_128_finite": train["all_six_channels_128_finite"] and test["all_six_channels_128_finite"],
        "labels_only_1_to_6": train["labels_outside_1_to_6"] == 0 and test["labels_outside_1_to_6"] == 0,
        "no_exact_cross_domain_six_channel_duplicate": duplicate_keys == 0,
    }
    result = {
        "research_id": "STAT-PSYMOE-EXP068-20261002-001",
        "attempt_id": "EXP068-SOURCE-001",
        "retrieved_at_utc": datetime.now(timezone.utc).isoformat(),
        "official_url": URL,
        "official_dataset_page": "https://archive.ics.uci.edu/dataset/240/human%2Bactivity%2Brecognition%2B",
        "citation": "Reyes-Ortiz, J.; Anguita, D.; Ghio, A.; Oneto, L.; Parra, X. (2013). Human Activity Recognition Using Smartphones. UCI. doi:10.24432/C54S4K; CC BY 4.0.",
        "download_bytes": download_bytes,
        "inner_zip_bytes": inner_bytes,
        "reported_preprocessing": "Official UCI windows: filtered, 128 samples, 50 percent overlap; not continuous raw signals",
        "independent_unit": "subject",
        "total_windows": total,
        "total_subjects": len(set(train["subjects"]) | set(test["subjects"])),
        "subject_overlap": overlap,
        "cross_domain_exact_six_channel_duplicate_windows": duplicate_keys,
        "train": train,
        "test": test,
        "gates": gates,
        "gate_result": "REAL_HAR_PERSON_SPLIT_SOURCE_READY_FOR_STAT_DESIGN" if all(gates.values()) else "STOP_REAL_HAR_SOURCE_SUPPORT",
        "model_fits": 0,
        "test_performance_scores": 0,
    }
    (HERE / "SOURCE_MATRIX.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({
        "download_bytes": download_bytes,
        "train_windows": train["windows"], "test_windows": test["windows"],
        "train_subjects": train["unique_subjects"], "test_subjects": test["unique_subjects"],
        "train_class_subjects": {k: v["subjects"] for k, v in train["by_class"].items()},
        "test_class_subjects": {k: v["subjects"] for k, v in test["by_class"].items()},
        "subject_overlap": overlap,
        "cross_domain_duplicates": duplicate_keys,
        "gate_result": result["gate_result"],
    }, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
