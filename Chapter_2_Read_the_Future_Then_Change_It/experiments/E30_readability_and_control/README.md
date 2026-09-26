# E30 Readability and control gain


Readout accuracy across layers 1–4 was 0.672/0.661/0.823/0.896; mean control gain was 0.497/0.252/0.129/0.000. Finite-intervention validation gave Spearman=0.99515 and Pearson=0.98376.

## Method

In the constructed network used for E29, fit future-mode probes by layer and compute the gradient norm of the future branch score with respect to historical-position residuals. On 36 independent trajectories, apply a finite perturbation of norm 0.75 along the gradient and compare predicted gain with the observed effect.

## Final interpretation

Sensors and actuators can occupy different sites. Zero last-layer gain refers to the tested historical prompt positions in this task; other positions and networks have their own control maps.

## Evidence files

| File | Contents |
| --- | --- |
| [04_readability_vs_control_gain.csv](../../evidence/phase2/G2_future_instruments/04_readability_vs_control_gain.csv) | result_table |
| [05_control_gain_heatmap.csv](../../evidence/phase2/G2_future_instruments/05_control_gain_heatmap.csv) | result_table |
| [06_control_gain_validation.csv](../../evidence/phase2/G2_future_instruments/06_control_gain_validation.csv) | result_table |
| [PROTOCOL.md](../../evidence/phase2/G2_future_instruments/PROTOCOL.md) | protocol_or_report |
| [REPORT.md](../../evidence/phase2/G2_future_instruments/REPORT.md) | protocol_or_report |

[artifacts.csv](artifacts.csv) · [experiment.json](experiment.json)

Protocols, derived results and figures support inspection of methods and numbers. Archived reports retain original wording; this page and the Phase 2 findings provide the final interpretation. Training code and checkpoints can be added in a subsequent archive. Recompute summaries from the repository root with `python audit/recalculate_phase2.py`.

## Related claims

H20, H25
