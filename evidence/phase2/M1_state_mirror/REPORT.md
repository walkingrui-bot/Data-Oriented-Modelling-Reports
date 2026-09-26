# Mirror Generation Controller (MGC) — Round 1

## Engineering question

Can long-run self-conditioned generation be stabilized by a second model that mirrors the model's **generation state**, rather than by generating corrective text?

The intended controller must not need a ground-truth next sentence at runtime.

## Core construction

Let the main model's current generation state be h.

Train a small mirror model M so that, under paired symmetric perturbations around the same task/semantic condition,

M(h_plus) ≈ h_minus
M(h_minus) ≈ h_plus

and encourage the involution property:

M(M(h)) ≈ h.

Then define:

stable-center estimate:
    h_center ≈ (h + M(h)) / 2

drift estimate:
    d_hat ≈ (h - M(h)) / 2

The main model can then be stabilized either by:

1. state correction:
   h_controlled = h - gamma * d_hat

2. logit fusion:
   l_controlled = (l(h) + l(M(h))) / 2

The mirror model is not a second author. It is a local symmetry controller.

## Toy world

A nonlinear synthetic autoregressive generator was constructed with:

- a slowly varying task/semantic state;
- a self-conditioned drift state;
- nonlinear mixing of task and drift into a 24-dimensional hidden state;
- a nonlinear output decoder;
- generated tokens fed back into the next drift update.

The free system therefore develops persistent distribution drift under its own outputs.

A two-hidden-layer MLP mirror model was trained only on paired states generated with the same task condition and opposite drift perturbations.

Runtime input to the mirror model was the current hidden state only. It did not receive the reference output distribution or a correct next token.

## Mirror-model quality

On held-out paired states:

- mirror-state MSE: 0.0152
- involution error M(M(h)) vs h: 0.00822
- output TV between learned mirror and true mirrored counterpart: 0.0404

On a harder perturbation range than used for much of training:

- main-state MSE to latent stable center: 0.3806
- mirror-midpoint MSE to stable center: 0.0553
- main output TV to reference distribution: 0.2139
- mirror-midpoint output TV: 0.0818

Thus the midpoint of the main and learned mirrored states was substantially closer to the latent stable generation center than the main state alone.

## Long-run closed-loop experiment

Eight independent stochastic trajectories were run for 30,000 autoregressive steps per condition, with strong state shocks at steps 7,500, 15,000, and 22,500.

Conditions:

- free: main model alone
- clone: average with an identical copy
- random mirror: average with an unrelated fixed hidden transform
- learned mirror: average main logits with logits decoded from M(h)

### Results

| Condition | Mean TV | Late TV | Late KL | First 500 steps after shock TV | 3k–4k after shock TV |
|---|---:|---:|---:|---:|---:|
| free | 0.0888 | 0.0884 | 0.0253 | 0.0920 | 0.0887 |
| clone | 0.0888 | 0.0880 | 0.0250 | 0.0935 | 0.0891 |
| random mirror | 0.1284 | 0.1279 | 0.0537 | 0.1332 | 0.1288 |
| learned mirror | **0.0218** | **0.0214** | **0.00158** | **0.0235** | **0.0216** |

Relative to free generation, the learned mirror reduced late TV drift by about 76% and late KL by about 94%.

An identical clone did essentially nothing. A random hidden-space "mirror" made the system worse.

Therefore the benefit came from the learned symmetry, not from ensembling or averaging by itself.

## Interpretation

The experiment establishes a proof-of-mechanism for an engineering object:

**Mirror Generation Controller (MGC)**

The model does not generate corrective language. Instead it estimates the counter-state corresponding to the opposite side of the local generation manifold.

The pair:

    h
    M(h)

provides two useful quantities:

    center = (h + M(h))/2
    drift  = (h - M(h))/2

This gives a direct engineering interpretation:

- GCM / generation-state readout tells us what future mode is forming.
- Future Causal Influence tells us which history is shaping it.
- Control Gain tells us where intervention still has leverage.
- MGC supplies a learned counter-state and a local drift estimate.

## Relation to content-level mirror stabilization

Content mirroring and state mirroring can now be treated as two implementations of the same higher-level operation.

Content mirror:
    generate a complementary external trajectory that re-enters context and pulls the generation function back.

State mirror:
    construct a complementary internal generation state and cancel the asymmetric drift before it becomes text.

The state-mirror route is earlier and potentially cheaper because it operates before the deviation must be externalized into language.

## Proposed real-LLM engineering route

1. Use GCM to identify a layer/position with high control gain.
2. Collect paired states under controlled opposite prompt/style/reasoning perturbations.
3. Train a small mirror operator M_l at that site.
4. Add involution loss M_l(M_l(h)) ≈ h.
5. Preserve task semantics using same-task paired samples.
6. At runtime estimate:
       center = (h + M_l(h))/2
       drift = (h - M_l(h))/2
7. Apply partial correction h - gamma*drift, or fuse main/mirror logits.
8. Evaluate with long-horizon distribution drift, constraint fingerprint, entropy, trajectory coverage, and perturbation recovery — not final-answer accuracy alone.

## Current boundary

This is a synthetic proof-of-mechanism, not yet a large-language-model result.

The important engineering result is narrower:

A learned mirror-state operator can stabilize a self-conditioned generative system without being given the correct next output at runtime, and its midpoint can estimate a stable generation center substantially better than the drifting main state alone.

