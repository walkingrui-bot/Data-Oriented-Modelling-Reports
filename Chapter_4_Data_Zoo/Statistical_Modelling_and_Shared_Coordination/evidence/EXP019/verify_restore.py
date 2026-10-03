#!/usr/bin/env python3
"""Restore EXP019 new states from saved files and their original EXP017 parents."""

from __future__ import annotations

import json
import traceback

import numpy as np
import pandas as pd
import torch

from cgc_stat_models import STATE_FIELDS, rebuild_old_states, subsets_and_folds
from onboard import ARMS, EP_INDEX, OUT, SEEDS, extend, predict
from train_native_six import load_native


OUTPUT = OUT / "restore_verification.json"
FAILURE = OUT / "restore_failure.json"


def main() -> None:
    if OUTPUT.exists() or FAILURE.exists():
        raise RuntimeError("Existing restore record must be preserved")
    torch.set_num_threads(4)
    cohort, raw, geometry, _ = load_native()
    y, _, idx, folds = subsets_and_folds(cohort)
    old, _ = rebuild_old_states(cohort, raw, geometry, idx, folds, y)
    state = pd.read_parquet(OUT.parent / "EXP019-CGC-STAT-001/cgc_exported_state.parquet")
    new = state[list(STATE_FIELDS)].to_numpy(np.float32)
    saved = pd.read_parquet(OUT / "validation_predictions.parquet")
    detail = {}
    for arm in ARMS:
        for seed in SEEDS:
            model, legacy, old_path, _ = extend(seed, new.shape[1], arm, "cpu")
            path = OUT / f"{arm}_seed_{seed}.pt"
            obj = torch.load(path, map_location="cpu", weights_only=True)
            if obj["parent_checkpoint_path"] != str(old_path):
                raise RuntimeError(f"Parent locator mismatch: {arm} seed {seed}")
            if arm == "full_retrain":
                model.load_state_dict(obj["state_dict"])
            else:
                model.interfaces[6].load_state_dict(obj["new_interface_state_dict"])
                if not all(torch.equal(model.state_dict()[key], value) for key, value in legacy.items()):
                    raise RuntimeError(f"Frozen legacy parameter changed on restore: {arm} seed {seed}")
            old_val = old["validation"].copy()
            if arm == "no_ep_frozen":
                old_val[:, EP_INDEX, :] = 0
            actual = predict(model, old_val, new[idx["validation"]], "cpu")
            expected = saved[f"{arm}_seed_{seed}"].to_numpy(float)
            diff = float(np.max(np.abs(actual - expected)))
            if diff > 3e-6:
                raise RuntimeError(f"Validation prediction mismatch: {arm} seed {seed}, {diff}")
            detail[f"{arm}_seed_{seed}"] = {"checkpoint": str(path),
                                            "parent_checkpoint": str(old_path),
                                            "validation_max_abs_difference": diff,
                                            "best_epoch": int(obj["best_epoch"])}
    OUTPUT.write_text(json.dumps({"run_id": "EXP019-RESTORE-001", "status": "PASS",
                                  "new_checkpoints": len(detail), "detail": detail},
                                 ensure_ascii=False, indent=2) + "\n")
    print(json.dumps({"status": "PASS", "new_checkpoints": len(detail),
                      "max_difference": max(x["validation_max_abs_difference"] for x in detail.values())}))


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        if not FAILURE.exists():
            FAILURE.write_text(json.dumps({"run_id": "EXP019-RESTORE-001",
                                           "error_type": type(exc).__name__, "error": str(exc),
                                           "traceback": traceback.format_exc()}, ensure_ascii=False, indent=2) + "\n")
        raise
