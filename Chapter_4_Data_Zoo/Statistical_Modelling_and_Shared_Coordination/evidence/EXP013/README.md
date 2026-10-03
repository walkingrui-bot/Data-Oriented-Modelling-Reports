# INTERNAL_COORDINATION_013 — Statistical Observer as a Coordinated Evidence Channel

Experiment 013 tests a specific extension of the Stat-PsyMoE idea: the result of a conventional statistical model is itself treated as an observer and allowed to enter the shared ganglion alongside the six biological evidence channels.

## Leakage control
The statistical observer is generated with five-fold **target-group cross-fitting** inside the outer training partition. A training target never receives a statistical-channel value from a model fitted on that target group. Validation and test use the final statistical observer fitted only on outer-training targets.

## Main median log loss
| Model | Full | -1 pipeline | -2 pipelines | -3 pipelines |
|---|---:|---:|---:|---:|
| Statistical observer only | 0.197776 | 0.198202 | 0.198687 | 0.199351 |
| Six-channel Stat-PsyMoE | 0.197562 | 0.198029 | 0.198656 | 0.199417 |
| + statistics as 7th channel | 0.197543 | 0.198054 | 0.198583 | 0.199371 |
| + output precision | 0.197447 | 0.197969 | 0.198563 | 0.199292 |

The direct incremental gain from adding the seventh channel is small because its information is derived from the same six evidence sources. The stronger result is mechanistic: once trained with the statistical observer, removing that channel or pairing it with the wrong evidence state reliably damages the model.

Median full-evidence log loss after removing the trained statistical channel is 0.198016; with a mispaired statistical result it is 0.199612.

## Interpretation
Traditional statistics can function as an additional **model observer** inside the shared coordination system. It does not become a seventh biological evidence source. Instead, it supplies a compressed second-order view of the same evidence field. The ganglion learns to use that view jointly with the native evidence channels.

The precision head remains useful in two of three seeds, so making statistics a channel does not remove the separate role of task-specific statistical precision.
