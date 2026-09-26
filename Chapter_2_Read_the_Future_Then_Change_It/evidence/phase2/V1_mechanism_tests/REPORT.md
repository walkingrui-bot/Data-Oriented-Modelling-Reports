# Reviewer Follow-up Experiments — Round 1
Date: 2026-09-25

This package directly tests four reviewer concerns.

## 1. Wrong-center MGC

A pair-mirror was trained around a deliberately biased latent center rather than the true stable center.

Long-run:
- correct mirror → true-center late TV: 0.0797
- strong wrong-center mirror → true-center late TV: 0.1833
- strong wrong-center mirror → its taught wrong-center late TV: 0.0958

The wrong-center controller is much closer to the wrong center than the true center.

**Conclusion:** mirror stabilization does not discover the reference by itself. The hard problem is center / symmetry identification.

## 2. Mirror vs direct center denoiser

A same-width MLP was trained directly as h→h_center.

Harder-than-training static test:
- mirror midpoint output TV: 0.0431
- direct center denoiser output TV: 0.0364

Closed loop:
- correct mirror late TV: 0.0797
- direct denoiser late TV: 0.0679

The denoiser also remained slightly better across all tested OOD drift-radius bands through 2.5–3.0.

**Conclusion:** this toy does not establish a unique mirror advantage. Mirror is currently a structured parameterization of center/counter-state estimation. Any unique benefit must be shown in settings where direct center labels are unavailable but pairwise symmetry is obtainable.

## 3. TMC dose-matched cadence

Earlier TMC cadence experiments kept lambda fixed per correction, so every-k-token control also reduced cumulative dose by 1/k.

New matched-dose conditions:
- 1 token: lambda=.025
- 2 tokens: lambda=.050
- 4 tokens: lambda=.100
- 8 tokens: lambda=.200
- 16 tokens: lambda=.400

All have nominal lambda/token=.025.

Late TV:
- every_1: 0.3931
- every_2: 0.3965
- every_4: 0.3946
- every_8: 0.3975
- every_16: 0.3935
- free: 0.4162

The five matched-dose means span only 0.0044.

Every-1 minus every-16:
- mean difference: -0.00047
- paired trajectory-bootstrap 95% CI: [-0.00996, 0.00893]

**Conclusion:** the prior dramatic frequency curve was predominantly a total-dose effect. This toy does not currently support the stronger claim that control cadence itself must match token read-back cadence.

## 4. Balance Band negative-control worlds

### Self-history takeover
- near-optimal: (13, 33)
- Balance Band: (12, 31)
- Jaccard: 0.864

### Prompt dilution, no self-opposition
- near-optimal: (21, 39)
- Balance Band: (11, 33)
- Jaccard: 0.448
- max self-opposition: 0

The band becomes conservative because External Anchor Control falls, but Self-Opposition correctly stays silent.

### Pure accumulated noise, no self-opposition
- near-optimal: (20, 54)
- original Balance Band: (13, 111)
- Jaccard: 0.354
- late output error: 0.092
- 73.5% of clearly bad timepoints are still labelled balance.

This is an honest failure. The original Balance Band detects a specific source-control mechanism; it is not a universal overthinking detector.

## 5. New engineering channel: Residual / Unattributed Future Influence

The pure-noise failure shows that Prompt + Question + Self-history may not exhaust all future-changing causes.

Adding a fixed residual gate:
residual-FCI / external-anchor-FCI < 5%

changes the pure-noise predicted band from
(13, 111)
to
(13, 45)

and improves Jaccard from 0.354 to 0.619, while the bad-timepoint false-safe fraction falls to 0%.

This suggests a fifth GCM instrument:
**Residual / Unattributed Future Influence**.

## 6. Manuscript corrections prompted by review

### Self-Opposition
Do not frame 91.4% vs 88.3% as a large standalone predictive win. The stronger result is mechanistic decomposition:
- Self-Takeover = how much future control has moved to self-history.
- Self-Opposition = whether that acquired control is turning against external anchors.
- surface deviation remains a complementary monitor.

### Exact FCI 90.6% vs 100%
These came from different protocols:
- Round 1: earlier task/model protocol; 90.6% on its correct-example subset and 81.8% across all examples.
- GCM Engineering Round 2: redesigned delayed-divergence task, three independent models, held-out history-pattern split, and 100% four-step rollout accuracy; exact FCI then recovered the true source in all 192 held-out cases.
The later 100% is not an improvement on the same benchmark.

## 7. Updated theory status

Survives:
- center/counter-state control can stabilize self-conditioned generation when its reference relation is good;
- future-causal monitoring can attribute which modeled sources control continuation;
- Balance Band is useful for the mechanism it explicitly models.

Corrected:
- MGC does not infer the right center by itself;
- mirror is not yet superior to direct center estimation;
- token-level TMC cadence is not independently established after dose matching;
- Balance Band is not universal across overthinking mechanisms;
- unmodeled future-changing causes require an explicit residual channel.
