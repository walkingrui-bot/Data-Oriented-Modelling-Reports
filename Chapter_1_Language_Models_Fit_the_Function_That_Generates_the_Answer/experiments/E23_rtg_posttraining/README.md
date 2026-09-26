# E23 RTG post-training with final-answer supervision

[Experiment index](../README.md)

There were 4000 base updates and 8970 adapter updates, totaling 12970. Across 563200 formal outputs, post-trained RTG, the recurrent control, iterated reader and no-write/reset-M conditions all reached 100% over lengths 1–20. RTG step0 achieved 85.78% at length 20, rising to 100% after training; mean write norm on prespecified diagnostic trajectories was approximately 0.9998. RTG and the recurrent control had equal final accuracy.

## Method

Phase A used ten-state random permutations, a 32-dimensional one-step reader, 16-dimensional relations and write budget 1. Seeds were 101/202/303/404/505. After reader training, the base was frozen. RTG and parameter-matched Elman adapters each had 2836 trainable parameters and used final-answer CE at lengths 1–4. Each seed tested 512 rules with two starts, 11 lengths and ten conditions.

## Interpretation

Final-answer supervision trains nonzero RTG writes into task-compatible updates. Several mechanisms solve the static-rule task exactly, making their internal dynamics and response to interventions the next useful comparison.

## Artifacts and reproduction

**Code data checkpoints and per-episode outputs**

This is the most complete training archive: fixed configuration, synthetic inputs, checkpoints, 563200 formal outputs and traces. Restore the compressed JSONL, then stage the original package name before using its replay entry point. See docs/REPRODUCTION.md.

Paths below are relative to the repository root. The complete file inventory is in [artifacts.csv](artifacts.csv).

| File | Role | Locator |
| --- | --- | --- |
| [evidence/R5_posttraining/configs/phaseA_v1.json](../../evidence/R5_posttraining/configs/phaseA_v1.json) | configuration |  |
| [evidence/R5_posttraining/results/seeds_summary.csv](../../evidence/R5_posttraining/results/seeds_summary.csv) | result_or_record |  |
| [evidence/R5_posttraining/results/accuracy_by_length.csv](../../evidence/R5_posttraining/results/accuracy_by_length.csv) | result_or_record |  |
| [evidence/R5_posttraining/results/per_episode_predictions.jsonl.gz](../../evidence/R5_posttraining/results/per_episode_predictions.jsonl.gz) | result_or_record |  |
| [evidence/R5_posttraining/src/models.py](../../evidence/R5_posttraining/src/models.py) | code |  |
| [evidence/R5_posttraining/REPORT.md](../../evidence/R5_posttraining/REPORT.md) | method_or_report |  |

## Related hypotheses

H15, H16, H18, H20

- C13: Sufficiency refers to specified properties and tasks; RTG is an implemented mechanism instance.
