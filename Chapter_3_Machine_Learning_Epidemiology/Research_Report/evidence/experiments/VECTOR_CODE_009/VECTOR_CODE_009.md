# VECTOR-CODE-009 — Vector token codes and hidden control directions

## Question

Does a token’s internal vector code have causal effects beyond its visible label and beyond the token-0→token-1 contrast direction?

## Model and training

- 12 trainable parameters: W(2x2)=4, U(2x2)=4, b(2)=2, v(2)=2.
- Fixed two-dimensional bit codes: e0=(-1, cy), e1=(+1, cy); therefore e1-e0=(2,0) for every codebook.
- Structural marker codes fixed at R=(0,2.5), C=(-2.2,-1.4), A=(2.3,-1.6).
- Four questions 00,01,10,11; endpoint target vector 0011. Each question has two paired intermediate chain targets, with History A/B reversing their within-question order.
- SGD, 60 epochs, lr=0.035; intermediate losses weighted 0.6 and endpoint loss 2.5. Within a seed/history comparison only cy changes.

## 1. Strict observable lock with an unchanged semantic contrast vector

The strongest group is seed14 / History B. Four different orthogonal codebook offsets retain the identical generated four-question CoT signature `00|00|11|11` and identical correct endpoint `0011`, while the bit contrast vector is exactly (2,0) in every model.

|    cy |   probe_z |   grad_parallel |   grad_orthogonal |   grad_norm |   orth_frac |
|------:|----------:|----------------:|------------------:|------------:|------------:|
| -1    |  -1.72636 |    -0.0152875   |      -0.00408908  | 0.015825    |    0.258394 |
| -0.25 |  -1.58805 |    -2.17424e-05 |      -2.69757e-06 | 2.19091e-05 |    0.123125 |
|  0.25 |  -2.12582 |    -0.0095657   |      -0.0112215   | 0.0147454   |    0.761022 |
|  1.5  |  -1.60823 |    -0.00287019  |      -0.000897488 | 0.00300724  |    0.298443 |

Max/min route-code gain ratio = **722.300x**.

## 2. A purely orthogonal code intervention changes the answer

Selected case: seed14 / History B / cy=0.25 / question 11. The visible route token remains `1`. Its normal code is e1=(1,0.25). The intervention changes only embedding dimension 2: e1→(1,0.25+δ), leaving the semantic-axis coordinate and visible label unchanged.

- Natural answer logit: 2.114650285.
- Local answer gradient wrt route embedding: (-0.023832968, -0.029375077).
- Orthogonal component = 77.656% of gradient norm and 60.304% of squared gradient energy; angle from semantic axis = 50.946 degrees.
- Answer zero crossings with downstream code regenerated: [np.float64(1.380351241933309), np.float64(1.4279948019443043), np.float64(1.7403830691101987)].
- Answer zero crossings with downstream code held fixed: [np.float64(1.380351241933309)].
- Downstream code switches: [np.float64(1.4287500000000002)].

The first answer boundary occurs before the downstream discrete code switches, so a purely orthogonal numeric perturbation can alter the final answer even while the visible route token and downstream code bit are unchanged.

## 3. Coordinate gauge control

All bit codes and marker codes were transformed by the same 37-degree rotation plus translation c=(0.31,-0.47), with exact first-layer compensation U'=U R^T and b'=b-U'c. Across all four questions and all four forced two-bit chains:

- maximum answer-logit error = 4.441e-16
- maximum final-hidden-state distance = 3.511e-16

Therefore no absolute vector coordinate or direction has universal semantic privilege. The causal object is the code relative to the learned input map, current state, structural codes, and nonlinear transition geometry.

## Working conclusion

In this controlled vector-code system, visible token identity and the token-0→token-1 contrast do not exhaust computational function. An embedding direction orthogonal to the contrast axis can carry substantial downstream control, and models with identical visible CoT strings and endpoints can differ by hundreds-fold in local vector-code gain. Specific vector codes acquire extra effect by occupying high-gain regions of the learned dynamics; exact coordinate reparameterizations with weight compensation leave function unchanged.
