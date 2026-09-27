# Protocol — GCM Engineering Round 2

Model:
- 4-layer causal Transformer
- hidden size 32
- 4 heads
- 3 independent seeds: 11, 22, 33

Delayed-divergence task:
- four binary history cues
- a query selects which history cue is relevant
- a content variable determines surface output family
- future outputs 1 and 2 are identical under modes A and B
- future outputs 3 and 4 diverge by mode
- held-out history-pattern split: 64 examples per seed
- all three models achieved 100% four-step rollout accuracy on the held-out split

Primary target:
- identify which history element actually changes the delayed future continuation
- do not use final-answer accuracy as the mechanism metric

Exact FCI:
- flip one history element counterfactually
- autoregressively recompute future output distributions
- measure total-variation change over future horizons

Cheap estimators:
1. train-selected raw attention site
2. attention × future-gradient
3. future gradient norm
4. directional future gradient:
   abs(grad_future_score(e_i) dot delta_i)
5. 3-point integrated directional future gradient
6. batched future-margin counterfactual

Control Gain:
- differentiate a delayed future-mode score with respect to residual-state interventions
  at every prompt position and layer
- validate against finite interventions of equal norm
- validation set: 36 trajectories
