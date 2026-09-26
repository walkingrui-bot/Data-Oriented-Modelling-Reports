# E33 Dynamic mirror dose response and shock control


Per-step λ=0/0.05/0.10/0.20/0.35/0.50 gave late TV=0.4167/0.3922/0.3460/0.2672/0.1562/0.0766. Under strong shocks, free/every-8/adaptive/every-token late TV was 0.4244/0.3828/0.0508/0.0525. The fixed-per-intervention-λ cadence sweep ranged from 0.0675 for every-token control to 0.4155 for free generation and also varied cumulative dose.

## Method

Train a separate mirror operator for this 24-dimensional world and fuse logits as (1−λ)l(h)+λl(M(h)). Cadence sweep: 12 paired trajectories×3,200 tokens, summarized over the last 800. Dose sweep: ten trajectories×3,000 tokens, summarized over the last 700. Shock test: six trajectories×8,000 tokens, with shocks at steps 2,000/4,000/6,000. Complete trajectories are the statistical units.

## Final interpretation

Dynamic mirrors provide continuously adjustable control. Interpret the cadence sweep as joint variation of cadence and cumulative dose; E36 separates dose from timing.

## Evidence files

| File | Contents |
| --- | --- |
| [01_shock_longrun_summary.csv](../../evidence/phase2/M2_dynamic_mirror/01_shock_longrun_summary.csv) | result_table |
| [02_correction_frequency_stats.csv](../../evidence/phase2/M2_dynamic_mirror/02_correction_frequency_stats.csv) | result_table |
| [03_per_token_dose_stats.csv](../../evidence/phase2/M2_dynamic_mirror/03_per_token_dose_stats.csv) | result_table |
| [04_mirror_operator_quality.csv](../../evidence/phase2/M2_dynamic_mirror/04_mirror_operator_quality.csv) | result_table |
| [05_frequency_seed_level.csv](../../evidence/phase2/M2_dynamic_mirror/05_frequency_seed_level.csv) | result_table |
| [PROTOCOL.md](../../evidence/phase2/M2_dynamic_mirror/PROTOCOL.md) | protocol_or_report |
| [REPORT.md](../../evidence/phase2/M2_dynamic_mirror/REPORT.md) | protocol_or_report |

[artifacts.csv](artifacts.csv) · [experiment.json](experiment.json)

Protocols, derived results and figures support inspection of methods and numbers. Archived reports retain original wording; this page and the Phase 2 findings provide the final interpretation. Training code and checkpoints can be added in a subsequent archive. Recompute summaries from the repository root with `python audit/recalculate_phase2.py`.

## Related claims

H20, H30, H33
