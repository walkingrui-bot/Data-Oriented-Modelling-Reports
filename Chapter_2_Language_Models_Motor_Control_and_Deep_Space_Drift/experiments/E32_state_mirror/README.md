# E32 State mirrors and 30,000-step control


Mirror MSE was 0.0152 and involution MSE 0.00822. Under harder perturbations, main-state center MSE was 0.3806 versus 0.0553 for the midpoint; output TV was 0.2139 versus 0.0818. Long-run late TV was 0.0884 for free generation, 0.0880 for a clone, 0.1279 for a random mirror and 0.0214 for the learned mirror. Learned-mirror late KL was 0.00158 and TV over the first 500 post-shock steps was 0.0235.

## Method

A nonlinear 24-dimensional self-fed generator combines slow task state, feedback drift and a nonlinear decoder. Train a two-hidden-layer MLP on same-task, opposite-drift state pairs, with an involution constraint. Its runtime input is the current hidden state. Run eight independent trajectories per condition for 30,000 steps, with shocks at steps 7,500/15,000/22,500. The closed loop fuses main-state and mirror-state logits.

## Final interpretation

Learned local symmetry supplies the stabilizing structure. Midpoint diagnostics and logit fusion are recorded separately because they differ under a nonlinear decoder. Runtime uses the current state; training pairs and evaluation use the experiment’s defined reference relation.

## Evidence files

| File | Contents |
| --- | --- |
| [01_long_run_summary.csv](../../evidence/phase2/M1_state_mirror/01_long_run_summary.csv) | result_table |
| [02_mirror_quality.csv](../../evidence/phase2/M1_state_mirror/02_mirror_quality.csv) | result_table |
| [REPORT.md](../../evidence/phase2/M1_state_mirror/REPORT.md) | protocol_or_report |

[artifacts.csv](artifacts.csv) · [experiment.json](experiment.json)

Protocols, derived results and figures support inspection of methods and numbers. Archived reports retain original wording; this page and the Phase 2 findings provide the final interpretation. Training code and checkpoints can be added in a subsequent archive. Recompute summaries from the repository root with `python audit/recalculate_phase2.py`.

## Related claims

H20, H30
