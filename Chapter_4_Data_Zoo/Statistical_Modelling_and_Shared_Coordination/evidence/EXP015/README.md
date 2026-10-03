# INTERNAL_COORDINATION_015 — Statistical Routing Below the Shared Ganglion

Experiment 015 formalises the hypothesis that MoE routing should be a statistical operation when the experts themselves are statistical evidence models.

Three target-group cross-fitted experts are used:
- Additive
- Interaction
- Empirical-Bayes

The router is not a neural network. Expert weights minimise out-of-fold weighted Bernoulli log loss on the probability simplex.

## Main result
The availability+density Stat-MoE scores:
- full evidence: 0.197408
- one unavailable pipeline: 0.197904
- two unavailable pipelines: 0.198547
- three unavailable pipelines: 0.199334

This is better than the neural-routed committee from Experiment 014 in all four availability regimes.

The learned statistical routing is interpretable. With all six pipelines available, OOF-optimal weights are Additive 0.18 / Interaction 0.38 / Empirical-Bayes 0.44. With only three pipelines available the optimum becomes 0 / 1 / 0. Conditioning additionally on evidence density reveals a sharper pattern: very low-density states are routed mainly to Empirical-Bayes; moderate/high-density states are routed mainly to Interaction.

Using Stat-MoE as an additional ganglion observer remains useful (removing it after training worsens all regimes), but the ganglion does not improve the coarse six-summary task beyond the standalone statistical mixture. This locates routing below shared cross-channel coordination.
