# E34 The reference center determines stabilization direction


Late TV to the true center was 0.4197 for free generation and 0.0797 for the correct-center mirror. A strongly biased-center mirror had TV=0.1833 to the true center and 0.0958 to the taught wrong center.

## Method

In the same nonlinear 24-dimensional world, construct mirror-training pairs around either the true center or a shifted center. The strong shift has magnitude 1.5 along a normalized latent direction. Run 64 trajectories×6,000 tokens per condition and measure late TV to both the true and taught centers.

## Final interpretation

The stabilizer faithfully implements its learned reference relation. Identifying the right center is an upstream task; maintaining stability around it is the control task.

## Evidence files

| File | Contents |
| --- | --- |
| [01_wrong_center_static_generalization.csv](../../evidence/phase2/V1_mechanism_tests/01_wrong_center_static_generalization.csv) | result_table |
| [02_wrong_center_closed_loop.csv](../../evidence/phase2/V1_mechanism_tests/02_wrong_center_closed_loop.csv) | result_table |
| [PROTOCOL.md](../../evidence/phase2/V1_mechanism_tests/PROTOCOL.md) | protocol_or_report |
| [REPORT.md](../../evidence/phase2/V1_mechanism_tests/REPORT.md) | protocol_or_report |

[artifacts.csv](artifacts.csv) · [experiment.json](experiment.json)

Protocols, derived results and figures support inspection of methods and numbers. Archived reports retain original wording; this page and the Phase 2 findings provide the final interpretation. Training code and checkpoints can be added in a subsequent archive. Recompute summaries from the repository root with `python audit/recalculate_phase2.py`.

## Related claims

H20, H31
