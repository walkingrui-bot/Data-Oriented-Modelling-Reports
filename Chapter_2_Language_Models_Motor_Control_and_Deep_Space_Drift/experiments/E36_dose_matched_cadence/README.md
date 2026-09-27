# E36 Control cadence at matched dose


Late TV across the five intervals was 0.3931/0.3965/0.3946/0.3975/0.3935, versus 0.4162 for free generation. The range of the five means was 0.0044. Every-1 minus every-16 was −0.00047, with bootstrap 95% CI [−0.00996,0.00893].

## Method

Use 48 paired trajectories with common random numbers, each 4,000 tokens long, and average TV over the last 1,000 tokens of each trajectory. Intervals of 1/2/4/8/16 tokens use λ=0.025/0.05/0.10/0.20/0.40, holding nominal dose at 0.025/token. Bootstrap the paired trajectory difference between every-1 and every-16.

## Final interpretation

Cumulative dose is the main supported explanation in this world; matched-dose outcomes are similar across 1–16-token intervals. Irreversible writes, saturation or missed control windows can be studied with the same separation of dose and timing.

## Evidence files

| File | Contents |
| --- | --- |
| [04_TMC_dose_matched_cadence.csv](../../evidence/phase2/V1_mechanism_tests/04_TMC_dose_matched_cadence.csv) | result_table |
| [05_TMC_dose_matched_paired_test.csv](../../evidence/phase2/V1_mechanism_tests/05_TMC_dose_matched_paired_test.csv) | result_table |
| [PROTOCOL.md](../../evidence/phase2/V1_mechanism_tests/PROTOCOL.md) | protocol_or_report |
| [REPORT.md](../../evidence/phase2/V1_mechanism_tests/REPORT.md) | protocol_or_report |

[artifacts.csv](artifacts.csv) · [experiment.json](experiment.json)

Protocols, derived results and figures support inspection of methods and numbers. Archived reports retain original wording; this page and the Phase 2 findings provide the final interpretation. Training code and checkpoints can be added in a subsequent archive. Recompute summaries from the repository root with `python audit/recalculate_phase2.py`.

## Related claims

H20, H33
