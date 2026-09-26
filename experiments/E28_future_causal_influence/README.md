# E28 Future causal influence before delayed divergence


Four-step held-out accuracy was approximately 98.8%, 98.0% and 94.1%. On correct examples, source Top-1 was 90.6% for exact FCI, 42.5% for mean attention, 20.8% for last-layer attention, 32.9% for immediate causal effect and 38.7% for a first-order future approximation. All-example FCI and mean attention were 81.8% and 41.1%. Directional intervention moved P(A) from 0.117 to 0.465 for B→A and from 0.834 to 0.444 in reverse.

## Method

Train three independent small causal Transformers. Each example has four binary history cues and a query selecting one. Future modes share their first two outputs and diverge at steps 3–4. Counterfactually flip each cue and measure the future distribution change, reporting all examples and the correctly predicted subset separately, with equal weighting across seeds. Estimate a mode direction on training data and intervene in layer 1 in both directions, with random-direction controls.

## Final interpretation

The future distribution exposes task-relevant influence before the next token does. The 90.6% result belongs to this round’s correct-example protocol and is reported separately from E29’s 100%.

## Evidence files

| File | Contents |
| --- | --- |
| [01_metric_comparison_all_examples.csv](../../evidence/phase2/G1_generative_control/01_metric_comparison_all_examples.csv) | result_table |
| [02_metric_comparison_correct_examples.csv](../../evidence/phase2/G1_generative_control/02_metric_comparison_correct_examples.csv) | result_table |
| [03_future_mode_readout_by_layer.csv](../../evidence/phase2/G1_generative_control/03_future_mode_readout_by_layer.csv) | result_table |
| [04_bidirectional_control_layer1.csv](../../evidence/phase2/G1_generative_control/04_bidirectional_control_layer1.csv) | result_table |
| [05_random_direction_control.csv](../../evidence/phase2/G1_generative_control/05_random_direction_control.csv) | result_table |
| [REPORT.md](../../evidence/phase2/G1_generative_control/REPORT.md) | protocol_or_report |

[artifacts.csv](artifacts.csv) · [experiment.json](experiment.json)

Protocols, derived results and figures support inspection of methods and numbers. Archived reports retain original wording; this page and the Phase 2 findings provide the final interpretation. Training code and checkpoints can be added in a subsequent archive. Recompute summaries from the repository root with `python audit/recalculate_phase2.py`.

## Related claims

H20, H23
