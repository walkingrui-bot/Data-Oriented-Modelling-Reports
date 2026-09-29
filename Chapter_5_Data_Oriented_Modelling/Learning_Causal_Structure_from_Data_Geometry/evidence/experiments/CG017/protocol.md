# CG-017 — Generated Intermediate Objects in Data and Causal Models

Protocol frozen before training, 2026-09-27. A small CPU feasibility experiment.

Research question: can self-generated intermediate objects help data/causal models,
and how do edits to these objects change subsequent computation? General Data
Intelligence remains an open generative research direction. These implementations
are experimental examples, not definitions of reasoning or admission criteria.

Four routes: Direct; Blank recurrence; Continuous latent feedback; Structured
numeric predictive feedback. Hidden size 48, feedback width 16, four recurrent
updates; same final-task loss, optimizer, batches, seeds, and development selection.
Direct uses zero recurrent updates and is a lower-compute reference. Blank is the
primary repeated-computation comparator. All routes instantiate the same modules;
active parameter counts differ and are reported. No intermediate supervision.

Synthetic panel: three observationally equivalent Gaussian SCM orientations on a
three-node chain, random signed coefficients, random variable permutation. Each
coefficient/permutation group shares its observed sample covariance across all
orientations. 400/100/100 independent parameter groups for train/dev/test; query
intervention and support intervention target differ. Every group contains three
worlds, each with and without a support intervention. Exact structural equations
provide the query intervention means; support means have N=128 sampling noise.
Models output a three-component isotropic Gaussian mixture (sigma=0.15), trained
with final mixture NLL. Generated mixture candidates/weights are the structured
feedback. Test NLL, predictive-mean MSE, oracle candidate MSE, and observationally
compatible world coverage are reported. This tests a constructed family of possible
worlds, including intrinsically ambiguous cases.

Real panel: Sachs/CORNETO log-transformed data, 200 cells per condition; baseline
plus six explicitly measured-target perturbations, five target-held-out folds.
PKC's two perturbations are held out together. Predict five hidden protein values
from six observed values; eight fixed masks shared by all routes. No intervention
label or graph is input. Training/dev split is by cell (80/20) within remaining
conditions; standardization uses training cells only. Test hidden-value standardized
MSE, equally weighted across held-out targets, is the principal score. This is
cross-environment conditional prediction, distinct from estimating unseen do-effects.

Training: seeds 11,22,33; Adam lr .002; synthetic 1200 updates batch96, real800
updates batch64; fixed development checks every100 steps, minimum-dev checkpoint
selected. Training batches are identical across routes at a given seed. No hyperparameter
search or result-dependent extension. All selected checkpoints retained.

Mechanism experiments on both feedback models: cut all feedback; transplant step-2
feedback from a cyclic donor with the same query/mask; rewrite one numeric feedback
coordinate by +1 at step2 and freely regenerate subsequent objects; no-op patch.
Measure task loss, final predictive displacement, and next-token displacement.
Inspect how donor feedback changes finite-difference input sensitivity on eight
prespecified test cases, holding the transplanted token fixed during differentiation.
Also report token covariance effective dimension. These are causal interventions
on these implemented computations, not a universal test of thought.

Report all three seeds and five real targets, including heterogeneous results.
Synthetic ambiguities and selected individual trajectories are illustrative;
population means are computed over the full frozen test sets. External raw data
is excluded from the deliverable ZIP; source URL, hashes, selection indices,
manifest metadata, and a downloader are included for reproduction.
