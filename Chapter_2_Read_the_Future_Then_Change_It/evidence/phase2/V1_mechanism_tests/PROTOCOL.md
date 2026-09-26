# Protocol summary

Wrong-center MGC
- nonlinear 24-d generation-state world used in prior MGC/TMC
- pair-mirror MLP trained around true or biased center
- strong biased-center magnitude: 1.5 along a normalized latent direction
- closed-loop: 64 trajectories × 6000 tokens

Direct center estimator baseline
- same-width MLP
- same training-state distribution
- target: h(c,d=0)
- OOD drift-radius scan through 2.5–3.0
- same closed-loop world

Dose-matched TMC
- paired common random numbers
- 48 trajectories × 4000 tokens
- equal nominal lambda/token=.025
- interval/lambda: 1/.025, 2/.05, 4/.10, 8/.20, 16/.40
- last 1000-token mean TV per trajectory
- paired trajectory bootstrap for every1 vs every16

Balance Band controls
- self-history takeover
- prompt dilution with self-opposition=0
- pure accumulated latent noise with self-opposition=0
- original fixed Balance Band retained
- extra residual-FCI gate tested as a repair
