"""Correct the gate from the preserved EXP038 person diagnostics, no source read."""

import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
old_path = HERE / "GROUP_SUMMARY.json"
old = json.loads(old_path.read_text())
assert old["run_id"] == "EXP038-COHORT-001"
assert old["group_denominators"] == {"PD": 44, "HC": 45}
assert old["group_qualifications"]["PD"]["PASS"] == 39
assert old["group_qualifications"]["HC"]["PASS"] == 45
assert old["all_reasons"] == {"MEMBER_EXCEEDS_BUDGET": 5}
assert old["gate"] == "SOURCE_ACCESS_INDETERMINATE"
failed = HERE / "derived" / "failed_GATE_001"
failed.mkdir(parents=True, exist_ok=False)
old_path.rename(failed / "GROUP_SUMMARY.json")
new = {**old, "adjudication_run_id": "EXP038-GATE-002", "prior_gate_output": str(failed / "GROUP_SUMMARY.json"), "gate": "COHORT_SOURCE_PASS_LOWER_BOUND", "unread_PD_member_count": 5, "interpretation": "PD39 and HC45 already exceed fixed >=36 each; five PD files remain unread and are not model-ready"}
old_path.write_text(json.dumps(new, ensure_ascii=False, indent=2) + "\n")
print(json.dumps({"gate": new["gate"], "PD_pass": 39, "HC_pass": 45, "unread_PD": 5}))
