# Protocol

Main campaign:
- 4,000 independent autoregressive trajectories
- 120 generated reasoning steps each
- three source components: prompt, user question, self-generated read-back history
- future causal influence horizon: 8 steps
- visible failure: output-distribution deviation > .15 for 3 consecutive steps
- early warning target: visible failure within the next 12 steps

Causal source intervention:
- prompt FCI: neutralize prompt component and its future injection
- question FCI: neutralize user-question component and its future injection
- self-history FCI: remove accumulated self-history component
- opposing-self FCI: self-history influence projected against prompt+question causal direction

Balance-band rule (fixed):
- external-anchor FCI >= 95% of its maximum
- opposing-self FCI / external-anchor FCI < 5%

Neighborhood:
- 3 external-integration rates x 3 self-feedback growth rates = 9 settings
- thresholds held fixed

Statistics:
- trajectory is the unit for train/test split and warning calibration
- warning thresholds calibrated on even-index trajectories and tested on odd-index trajectories
- no individual token is treated as an independent statistical replicate
