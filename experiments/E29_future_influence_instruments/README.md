# E29 Future sources and influence horizons


Source Top-1: calibrated attention 58.3%, attention×future-gradient 58.3%, gradient norm 69.3%, DFG 79.2%, and 100% for three-point IDFG, batched future margin and exact FCI. Relevant-source TV was about 0.000054/0.000056 at H1/H2 and 0.998948/0.998897 at H3/H4. All 192 examples first exceeded TV=0.1 at H3.

## Method

Use three independent models and 64 held-out history patterns per model, totaling 192 examples with successful four-step rollouts. Select the attention layer and query read-position on training data, then freeze them for testing. Compare exact FCI, gradient norm, DFG along the actual cue-flip direction, three-point integrated DFG and batched future margin. Record counterfactual TV at each horizon.

## Final interpretation

Measuring along an actual counterfactual connects local sensitivity to an operation that changes the future. Horizon profiles reveal constraints whose effects are still latent in the text. The 100% score describes source identification in this constructed task.

## Evidence files

| File | Contents |
| --- | --- |
| [01_metric_benchmark.csv](../../evidence/phase2/G2_future_instruments/01_metric_benchmark.csv) | result_table |
| [02_metric_top1_by_seed.csv](../../evidence/phase2/G2_future_instruments/02_metric_top1_by_seed.csv) | result_table |
| [03_influence_horizon_profile.csv](../../evidence/phase2/G2_future_instruments/03_influence_horizon_profile.csv) | result_table |
| [PROTOCOL.md](../../evidence/phase2/G2_future_instruments/PROTOCOL.md) | protocol_or_report |
| [REPORT.md](../../evidence/phase2/G2_future_instruments/REPORT.md) | protocol_or_report |

[artifacts.csv](artifacts.csv) · [experiment.json](experiment.json)

Protocols, derived results and figures support inspection of methods and numbers. Archived reports retain original wording; this page and the Phase 2 findings provide the final interpretation. Training code and checkpoints can be added in a subsequent archive. Recompute summaries from the repository root with `python audit/recalculate_phase2.py`.

## Related claims

H20, H23, H24
