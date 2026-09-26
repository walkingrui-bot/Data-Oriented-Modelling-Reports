# Protocol — Tokenwise Mirror Control Round 1

Statistical unit:
- complete autoregressive trajectory, never individual tokens.

Frequency campaign:
- 12 paired trajectories
- 3,200 tokens each
- correction interval: 1, 2, 4, 8, 16, or never
- primary metric: final 800-token mean TV to stable reference distribution per trajectory
- uncertainty: trajectory bootstrap 95% CI

Dose campaign:
- 10 trajectories
- 3,000 tokens each
- per-token mirror lambda: 0, .05, .10, .20, .35, .50
- primary metric: final 700-token mean TV per trajectory

Shock campaign:
- 6 trajectories per condition
- 8,000 tokens
- strong latent perturbations at steps 2,000 / 4,000 / 6,000
- conditions: free, mirror every 8 tokens, adaptive mirror, mirror every token, oracle reference
- metrics: TV, KL, entropy deviation, high-drift fraction, post-shock windows

Controller runtime input:
- current generation state only
- no correct next token
- no reference distribution
