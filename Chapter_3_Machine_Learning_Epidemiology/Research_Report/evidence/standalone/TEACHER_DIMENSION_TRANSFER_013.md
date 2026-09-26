# TEACHER-DIMENSION-TRANSFER-013

## Question

Does the low effective dimensionality of a learned Prompt/CoT control field primarily reflect a property of the model architecture, or can the intrinsic number of independent control variables in the training world be transferred into the learned control geometry?

## Synthetic teacher worlds

All teachers live in the same ambient 10-dimensional token/state space. For intrinsic teacher dimension d=1,...,6, let B_d contain d orthonormal columns and define

`F_d(x) = B_d tanh(A_d B_d^T x)`.

The exact teacher Jacobian is

`J_d(x)=B_d D(x) A_d B_d^T`,

so its generic rank is exactly d. All ten ambient input coordinates are sampled; the teacher ignores the orthogonal complement of span(B_d). Thus d measures causal/intrinsic control dimension rather than the number of visible coordinates.

The synthetic CoT trajectory is repeated application of the learned transition. For a horizon K=5, future response is

`R_K(x)=(x_1,...,x_5)`

and the future-control Jacobian is the vertical stack of ordered transition-Jacobian products. Learned effective dimension is summarized primarily by r95: the smallest number of singular modes carrying 95% of future-control energy. Stable rank and entropy rank are also saved.

## Student controls

Both branches use the same 10x10 trainable matrix shapes and the same parameter count.

- **full10**: all ten hidden coordinates are readable.
- **bottleneck3**: a fixed rank-3 projector is inserted between the nonlinear hidden state and output, enforcing a strict control-rank ceiling of 3 without changing trainable matrix shapes.

For a given initialization seed, the initial weights and minibatch schedule are reused across all teacher dimensions. Three initialization seeds are run per condition.

## Main result: teacher dimension transfers into the learned control field

### Full student

|   teacher_dim |   median_future_r95 |   mean_stable_rank |   mean_test_mse |   subspace_energy |
|--------------:|--------------------:|-------------------:|----------------:|------------------:|
|             1 |                   1 |            1       |     2.94821e-07 |          0.999998 |
|             2 |                   2 |            1.5902  |     6.622e-07   |          0.999998 |
|             3 |                   3 |            1.98242 |     1.17621e-06 |          0.999999 |
|             4 |                   4 |            2.57523 |     1.33006e-06 |          0.999999 |
|             5 |                   5 |            3.03422 |     3.18791e-06 |          1        |
|             6 |                   6 |            3.63837 |     2.95721e-06 |          1        |

Across d=1,...,6, the correlation between teacher intrinsic dimension and learned median future-control r95 is **1.000000**. A linear fit gives slope **1.0000** and intercept **0.0000**. The median r95 sequence is `1.0,2.0,3.0,4.0,5.0,6.0`.

The full student therefore expands its learned effective control dimension as independent control degrees of freedom are added to the teacher world. The architecture has ten readable dimensions, yet d=1 and d=2 teachers do not induce ten-dimensional control fields.

### Rank-3 architecture control

|   teacher_dim |   median_future_r95 |   mean_stable_rank |   mean_test_mse |   subspace_energy |
|--------------:|--------------------:|-------------------:|----------------:|------------------:|
|             1 |                   1 |            1       |     1.46085e-07 |          1        |
|             2 |                   2 |            1.58751 |     3.60923e-07 |          1        |
|             3 |                   3 |            1.99342 |     7.2737e-13  |          1        |
|             4 |                   3 |            2.26073 |     0.0218235   |          0.999798 |
|             5 |                   3 |            2.35713 |     0.0452573   |          0.999781 |
|             6 |                   3 |            2.51069 |     0.0682385   |          0.9997   |

For d<=3 the rank-3 student tracks the teacher dimension. For d>3, learned future-control r95 saturates at 3 while prediction error rises sharply. Correlation with `min(d,3)` is **1.000000**.

This supports the controlled relation

`d_control ≈ min(d_teacher, d_architecture)`

within this synthetic system. The low-dimensional field is therefore neither exclusively a property of the teacher nor exclusively a property of the model: the teacher supplies independent control degrees of freedom, while architecture supplies an upper bound on how many can be represented.

## Ten visible coordinates, only two causal dimensions

The d=2 control is trained in two representations:

1. `dense10_to2`: the two teacher directions are dense mixtures of all ten visible coordinates;
2. `sparse2_of10`: only two ambient coordinate directions are causally used while all ten observed coordinates still vary.

| surface_geometry   |   median_r95 |   stable_rank |    test_mse |   teacher_subspace_energy |
|:-------------------|-------------:|--------------:|------------:|--------------------------:|
| dense10_to2        |            2 |       1.5902  | 6.622e-07   |                  0.999998 |
| sparse2_of10       |            2 |       1.58338 | 4.34598e-06 |                  0.999999 |

Both recover approximately two-dimensional control. Thus the learned control dimension follows intrinsic causal dimension rather than raw visible-variable count or whether the relevant coordinates are densely mixed across the surface representation.

## Orientation control

For d=4 the teacher subspace is independently rotated three times in the same ambient R^10 space.

| orientation   |   median_r95 |   stable_rank |    test_mse |   teacher_subspace_energy |
|:--------------|-------------:|--------------:|------------:|--------------------------:|
| main          |            4 |       2.57523 | 1.33006e-06 |                  0.999999 |
| rotA          |            4 |       2.59468 | 2.23591e-06 |                  0.999999 |
| rotB          |            4 |       2.59486 | 2.48459e-06 |                  0.999999 |

The learned control dimension remains approximately four across orientations. This excludes a fixed privileged coordinate set as the explanation for the dimension transfer.

## Geometry transfer, not only scalar rank

For each learned future-control Jacobian J and teacher subspace projector P_B=B_d B_d^T, the experiment records

`||J P_B||_F^2 / ||J||_F^2`.

In the full10 branch this energy fraction remains close to one, showing that the student not only reproduces the number of active directions but concentrates future sensitivity inside the teacher-defined causal subspace.

## Interpretation

This experiment directly separates three dimensions:

- ambient/token dimension: fixed at 10;
- teacher intrinsic control dimension: deliberately set to 1,...,6;
- model architecture control ceiling: either 10 or 3.

The learned future-control spectrum follows the teacher dimension until the architecture ceiling is reached. A superficially ten-variable world with only two independent causal directions still yields an approximately two-dimensional learned control field.

The result therefore supports a **dimension-transfer mechanism** in this controlled system: the effective dimensionality of learned reasoning/control dynamics can be inherited from the intrinsic variation structure of the training world. The model architecture determines the available ceiling, while the teacher determines how much of that capacity is systematically carved into stable control directions.

This is a direct experimental realization of the proposed distinction:

`high-dimensional substrate -> low-dimensional effective control manifold`,

with the dimensionality of that manifold changing when the teacher's intrinsic dimensionality is changed.

## Evidence boundary

The experiment establishes dimension transfer in a deliberately constructed continuous recurrent teacher/student system where teacher rank is mathematically known. It motivates, but by itself does not identify, the intrinsic control dimension of human cognition or natural-language training data. The next empirical question is whether the same scaling relation survives autoregressive discrete-token language teachers and then larger language models.

## Files

- `model_dimension_transfer_summary.csv`
- `aggregate_dimension_transfer.csv`
- `per_state_control_dimension_metrics.csv`
- `control_singular_spectra.csv`
- `teacher_exact_dimension_metrics.csv`
- `orientation_control_d4.csv`
- `redundant_surface_dimension_control.csv`
- `teacher_to_control_dimension_transfer.png`
- `architecture_bottleneck_error.png`
- `control_spectrum_by_teacher_dimension.png`
- `orientation_invariance_d4.png`
- `redundant_surface_control.png`
