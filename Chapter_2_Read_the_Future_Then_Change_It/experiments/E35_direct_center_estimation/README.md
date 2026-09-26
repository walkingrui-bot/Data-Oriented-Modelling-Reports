# E35 Direct center estimation and mirror parameterization


Output TV under harder static perturbations was 0.0431 for the mirror midpoint and 0.0364 for direct center estimation. Closed-loop late TV was 0.0797 and 0.0679. Direct estimation was also slightly better across the tested OOD radius bands.

## Method

Train a same-width MLP on the same state distribution to estimate h(c,d=0) directly, and compare it with the mirror midpoint. Evaluate harder static perturbations, closed-loop operation in the same world and out-of-distribution drift-radius bands through 2.5–3.0.

## Final interpretation

Direct estimation is an effective implementation when center labels are available. Paired symmetry supplies a structured parameterization of center and counter-state. A next experiment compares them using paired labels as the supervision signal.

## Evidence files

| File | Contents |
| --- | --- |
| [01_wrong_center_static_generalization.csv](../../evidence/phase2/V1_mechanism_tests/01_wrong_center_static_generalization.csv) | result_table |
| [02_wrong_center_closed_loop.csv](../../evidence/phase2/V1_mechanism_tests/02_wrong_center_closed_loop.csv) | result_table |
| [03_mirror_vs_denoiser_OOD.csv](../../evidence/phase2/V1_mechanism_tests/03_mirror_vs_denoiser_OOD.csv) | result_table |
| [PROTOCOL.md](../../evidence/phase2/V1_mechanism_tests/PROTOCOL.md) | protocol_or_report |
| [REPORT.md](../../evidence/phase2/V1_mechanism_tests/REPORT.md) | protocol_or_report |

[artifacts.csv](artifacts.csv) · [experiment.json](experiment.json)

Protocols, derived results and figures support inspection of methods and numbers. Archived reports retain original wording; this page and the Phase 2 findings provide the final interpretation. Training code and checkpoints can be added in a subsequent archive. Recompute summaries from the repository root with `python audit/recalculate_phase2.py`.

## Related claims

H20, H32
