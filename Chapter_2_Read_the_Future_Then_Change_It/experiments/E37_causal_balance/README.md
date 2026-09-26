# E37 Source control and the reasoning balance interval


The near-optimal interval was 13–33 and the causal interval 12–31. Across nine worlds, mean/median Jaccard was 0.751/0.818. At about 5% safe false alarms, self-opposition detected 91.4% of imminent failures with median lead six tokens; output deviation detected 88.3% with lead five. Overall self-takeover AUC was 0.706.

## Method

Use 4,000 independent constructed trajectories of 120 tokens, with manipulable prompt/question integration and self-conditioned updates. Measure external anchor, self-takeover and self-opposition using eight-step counterfactual future influence. Balance Band requires external≥95% of its trajectory peak and opposition/external<5%. Test a 3×3 parameter neighborhood. Split warning evaluation by trajectory, calibrate on safe points at least 24 tokens from failure and predict failure within 12 tokens.

## Final interpretation

Control share and effect direction distinguish who takes over from where that control points. The band characterizes the attributed mechanism. Its peak-based definition is used for whole-trajectory analysis; live deployment requires a separately calibrated reference available from the observed prefix.

## Evidence files

| File | Contents |
| --- | --- |
| [01_source_control_over_time.csv](../../evidence/phase2/B1_causal_balance/01_source_control_over_time.csv) | result_table |
| [02_overthinking_warning_auc.csv](../../evidence/phase2/B1_causal_balance/02_overthinking_warning_auc.csv) | result_table |
| [03_fixed_false_alarm_early_warning.csv](../../evidence/phase2/B1_causal_balance/03_fixed_false_alarm_early_warning.csv) | result_table |
| [04_balance_band_neighborhood.csv](../../evidence/phase2/B1_causal_balance/04_balance_band_neighborhood.csv) | result_table |
| [PROTOCOL.md](../../evidence/phase2/B1_causal_balance/PROTOCOL.md) | protocol_or_report |
| [REPORT.md](../../evidence/phase2/B1_causal_balance/REPORT.md) | protocol_or_report |

[artifacts.csv](artifacts.csv) · [experiment.json](experiment.json)

Protocols, derived results and figures support inspection of methods and numbers. Archived reports retain original wording; this page and the Phase 2 findings provide the final interpretation. Training code and checkpoints can be added in a subsequent archive. Recompute summaries from the repository root with `python audit/recalculate_phase2.py`.

## Related claims

H20, H26, H27
