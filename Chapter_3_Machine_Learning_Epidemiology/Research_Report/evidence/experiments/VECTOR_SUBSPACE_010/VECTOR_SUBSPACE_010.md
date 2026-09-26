# VECTOR-SUBSPACE-010 — Lexical, control, and silent subspaces of token embeddings

## Goal

Decompose a four-dimensional numeric token code into (i) the visible token-contrast axis, (ii) directions that actually control future chain/answer dynamics, and (iii) exact silent directions.

## Architecture

The recurrent hidden state remains two-dimensional. Token/marker inputs are four-dimensional. The trainable input matrix is U∈R^{2×4}; total trainable parameters are 16: W(2×2), U(2×4), b(2), v(2). Bit codebooks always satisfy e1−e0=(2,0,0,0), so the lexical contrast axis is fixed while the common 3D orthogonal offset changes.

By linear algebra, only Row(U) can affect the hidden preactivation; Null(U) is an exact silent embedding subspace. With rank(U)=2, R^4=Row(U)⊕Null(U), with two readable and two silent dimensions.

## Selected endpoint-correct case

|   seed | history   |   off2 |   off3 |   off4 | chain       |   ans |   G_frob |   orthogonal_energy_fraction |   top_control_angle_from_semantic_deg |   semantic_axis_projection_to_U_rowspace |
|-------:|:----------|-------:|-------:|-------:|:------------|------:|---------:|-----------------------------:|--------------------------------------:|-----------------------------------------:|
|     14 | A         |    0.6 |      0 |      0 | 00|00|11|11 |  0011 |  2.32745 |                     0.786062 |                               62.4501 |                                 0.700112 |

### Control-matrix SVD

|   G_mode |   singular_value |   energy_fraction |        d1 |         d2 |          d3 |        d4 |   abs_cos_semantic |   angle_semantic_deg |   rowspace_fraction |   nullspace_fraction |
|---------:|-----------------:|------------------:|----------:|-----------:|------------:|----------:|-------------------:|---------------------:|--------------------:|---------------------:|
|        1 |      2.32722     |       0.9998      |  0.46252  | -0.0408807 |  0.770374   | -0.436953 |           0.46252  |              62.4501 |         1           |          2.33038e-32 |
|        2 |      0.0329338   |       0.000200227 | -0.525577 | -0.684709  | -0.00714518 | -0.504867 |           0.525577 |              58.2929 |         1           |          3.15546e-30 |
|        3 |      2.03924e-17 |       7.67673e-35 | -0.670677 |  0.260102  |  0.60752    |  0.336837 |           0.670677 |              47.8807 |         1.82732e-30 |          1           |
|        4 |      2.32862e-18 |       1.00101e-36 |  0.245022 | -0.679595  |  0.193374   |  0.663869 |           0.245022 |              75.8169 |         9.39854e-32 |          1           |

Gradient projection residual outside Row(U): **3.720e-16**. This numerically confirms that every local token→answer gradient lies in the readable input subspace.

### Exact silent-direction intervention

Perturbing the visible route token embedding by amplitudes up to ±5 along either null-space direction produced maximum answer-logit change **0.000e+00** and maximum final-hidden distance **0.000e+00**.

Thus different 4D numeric token codes can be exactly functionally equivalent whenever they differ only by a vector in Null(U). The computational embedding object is naturally a quotient class e + Null(U), or equivalently the effective code Ue.

## Strict observable-lock groups

Across the codebook search, models were grouped only when seed/history, all four self-generated CoT strings, all four answers, and the lexical contrast vector were identical. The strongest groups still showed large differences in total local token-control gain:

|   seed | history   | chain       |   answer |   n_codebooks |   min_control |   max_control |   control_ratio |   max_orth_energy |   max_top_angle |   min_sem_projection |
|-------:|:----------|:------------|---------:|--------------:|--------------:|--------------:|----------------:|------------------:|----------------:|---------------------:|
|      2 | A         | 00|00|11|11 |     0011 |             5 |    0.00784272 |       0.78412 |         99.9806 |          0.797691 |          63.281 |             0.714136 |

## Working interpretation

The visible token contrast is one direction in embedding space, not the whole computational token. The learned input map selects a low-dimensional readable/control subspace; directions in its null space are exactly silent. Within the readable subspace, the dominant downstream-control modes can be substantially misaligned with the lexical contrast axis. Hence token function is better represented by the equivalence class under the silent subspace and by its state-dependent control gain, rather than by surface label or raw embedding coordinates alone.


## 4D coordinate gauge control

All bit and marker embeddings were transformed by one deterministic random 4D orthogonal matrix plus translation `(0.31,-0.47,0.22,-0.19)`, with exact compensation `U'=UQ^T`, `b'=b-U'c`. Across all questions and all forced two-bit chains, the maximum answer-logit error was **3.331e-16** and maximum hidden-state distance was **3.342e-16**. Thus the named raw coordinates are a gauge choice; the readable/silent decomposition transforms covariantly with the model.

## Lexical axis itself contains a silent component

For the selected case, the raw lexical contrast axis `(1,0,0,0)` has readable projection norm **0.700112** (energy fraction **49.016%**) and silent projection norm **0.714033** (energy fraction **50.984%**). The dominant control mode is **48.651°** away even from the *readable projection* of the lexical axis. Thus the distinction “token 0 vs token 1” itself mixes a part the network can read with a part this trained input map exactly ignores.
