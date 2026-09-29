# CG-023 Protocol

## Question
Can one explicit, executable world state integrate multiple meaningful generative coordinates and continue producing future consequences outside the local training/scoring window?

## Data-generating system
- 600 independent 4D affine dynamical worlds: `x[t+1]=M x[t]+b`.
- Spectral radius scaled approximately to 0.72-0.90; row absolute sum capped at 0.95.
- Whole-world split: 400 train / 100 dev / 100 frozen test.
- 16 equilibrium and 16 one-step temporal observations per world.

## Evidence coordinates
1. Equilibrium: external forcing `u` and exact equilibrium response `x*`.
2. Temporal: ordered transition `(x_t, x_{t+1})`.
3. Mixed: four equilibrium + four temporal evidence tokens.

Evidence-array position has no positional encoding and is semantically arbitrary. The order inside a temporal token is a generative coordinate and is preserved.

## Models
- World Program: 8 explicit `(M,b,logit)` candidates; 48D token width; three untied attention blocks; four heads; FF width 96; 59,974 parameters. Persistent iterative state is only the explicit world object.
- Direct Attention: same depth evidence attention plus query encoder and decoder; 89,636 parameters; no executable relation state.

## Training
- Seeds: 11, 22.
- Adam, learning rate 0.0015, batch 96.
- Registered budget: 700 updates.
- Temporal query horizons during training: 1-4 only.
- Evidence context length: randomly 4-8.
- World-state update depth: randomly 3-6.
- Development score every 50 updates; best dev checkpoint retained while the registered run continues to 700.

Selected checkpoints in both seeds: World update 250, Direct update 500.

## Frozen tests
- Equilibrium interpolation and larger-forcing extrapolation.
- Temporal rollout 1/2/4/8/16/32; extended stress horizons 64/128.
- Pure temporal vs mixed coordinate evidence.
- Container reversal (meaningless order control).
- Temporal pair reversal `(x_t,x_{t+1}) -> (x_{t+1},x_t)` (semantic-direction control).
- State serialization/replay after explicit update 2.
- Continued world-state updates to update 20.
- Sequential-shock stress test outside the training operation set.

## Independent real-data reference
The package includes summaries of the prior REAL45 PPFM probes: one-, three-, six-layer and tied-six attention on the same 45 real tasks. They provide independent evidence that evidence-token container order can be permutation invariant while deeper attention improves the local probe. Those runs are not counted as CG-023 training.
