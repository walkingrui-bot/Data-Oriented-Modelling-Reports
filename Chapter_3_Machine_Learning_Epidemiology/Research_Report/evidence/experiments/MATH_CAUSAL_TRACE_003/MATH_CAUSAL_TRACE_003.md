# MATH_CAUSAL_TRACE_003 | Mathematical causal tracing of training history

## Object

Same 10-parameter recurrent network and local order intervention used in MICRO-001/CAUSAL-002. Derivative audit is evaluated in float64 from the same seeded initial parameter values to suppress numerical noise.

## 1. Local training-order effect is an SGD commutator

For U_s(theta)=theta-eta g_s(theta), the adjacent-order difference obeys

theta_AB - theta_BA = eta^2 [H_b g_a - H_a g_b] + O(eta^3).

Epoch 1: exact norm=0.001263925; predicted norm=0.001268313; cosine=0.999928; relative error=1.252%.

Across all 20 baseline epoch-start states: mean cosine=0.999421; minimum cosine=0.998740; mean relative error=3.548%.

## 2. Training token -> parameter update -> CoT slice

Treating the fixed scalar token encoding x_t as the intervention coordinate, one SGD step gives the exact local derivative

d theta+ / d x_t = -eta * d^2 L / (d theta d x_t).

For CoT slice k, J_k = d z_k / d theta, therefore

d z_k / d x_t = J_k (d theta+ / d x_t).

Direct autograd and the matrix product J_k P agree to max absolute error 6.505e-19.

Strongest local token-to-parameter derivatives at initialization:

| record   | token_name   |   token_value |   dtheta_dx_L2 | top_parameter   |   top_dtheta_dx |
|:---------|:-------------|--------------:|---------------:|:----------------|----------------:|
| (0, 0)   | Q_B          |            -1 |     0.00933174 | u1              |      0.00761556 |
| (0, 0)   | FINAL        |            -1 |     0.0091145  | u1              |      0.00733442 |
| (1, 0)   | FINAL        |            -1 |     0.00911408 | u1              |      0.00733402 |
| (0, 1)   | FINAL        |            -1 |     0.00911254 | u1              |      0.00733251 |
| (1, 0)   | Q_B          |            -1 |     0.00908779 | u1              |      0.0073031  |
| (0, 1)   | Q_B          |             1 |     0.00756577 | u1              |      0.00502294 |
| (1, 1)   | Q_B          |             1 |     0.00565487 | u2              |     -0.00371821 |
| (1, 1)   | FINAL        |             1 |     0.00563826 | u2              |     -0.00371219 |
| (0, 0)   | Q_A          |            -1 |     0.00239804 | u1              |      0.00156454 |
| (0, 1)   | Q_A          |            -1 |     0.00202163 | u2              |      0.00127446 |

## 3. Exact finite-difference decomposition over CoT

For the two final history-conditioned models, with bar denoting midpoint and Delta denoting baseline minus swapped:

Delta h_t = S_t [ Wbar Delta h_(t-1) + Delta W hbar_(t-1) + Delta u x_t + Delta b ],

Delta z_t = vbar^T Delta h_t + Delta v^T hbar_t.

S_t is the elementwise secant slope of tanh between the two trajectories. The additive source terms were recursively split into all 10 parameter channels.

Maximum reconstruction residual for Delta z across the probe sequence: 4.094e-16.

|   coldstart_k | token   |   delta_z_base_minus_swap |   contrib_W11 |   contrib_W12 |   contrib_W21 |   contrib_W22 |   contrib_u1 |   contrib_u2 |   contrib_b1 |   contrib_b2 |   contrib_v1 |   contrib_v2 |
|--------------:|:--------|--------------------------:|--------------:|--------------:|--------------:|--------------:|-------------:|-------------:|-------------:|-------------:|-------------:|-------------:|
|             0 | Q_B=0   |                -0.0161713 |   0.00406402  |    0.00238883 |   0.0045335   |   3.77499e-05 | -0.00418099  |  0.000258427 |  -0.0119467  | -0.00263913  |  -0.0116902  |  0.00300321  |
|             1 | AND     |                -0.0321195 |  -0.0022577   |   -0.00430288 |  -0.00185988  |  -5.64586e-05 |  5.49571e-05 | -0.00029397  |  -0.0161436  | -0.00287595  |  -0.00732902 |  0.00294499  |
|             2 | A=1     |                -0.0360056 |  -0.00455481  |   -0.00895737 |  -0.00661976  |  -0.000188774 |  0.00913947  | -0.00353162  |  -0.023026   | -0.00516665  |   0.00622941 |  0.000670509 |
|             3 | B=0     |                -0.0339938 |   0.000136338 |   -0.00329335 |  -0.000765074 |  -6.17542e-05 | -0.00284359  | -0.000150966 |  -0.0125765  | -0.00218886  |  -0.0159059  |  0.00365584  |
|             4 | GIVES   |                -0.0358891 |  -0.00374692  |   -0.00514749 |  -0.00246882  |  -5.24054e-05 | -0.00215896  |  0.000129472 |  -0.00956419 | -0.00114713  |  -0.0155081  |  0.00377548  |
|             5 | r=0     |                -0.0282135 |  -0.00196595  |   -0.00242391 |  -0.000893146 |  -1.62035e-05 | -0.00265773  |  0.000215231 |  -0.00365967 | -0.000283014 |  -0.0206255  |  0.00409642  |
|             6 | ANSWER  |                -0.0403669 |  -0.00949258  |   -0.00960129 |  -0.00947248  |  -0.000133834 |  0.0056015   | -0.00141898  |  -0.0128594  | -0.00194048  |  -0.00367999 |  0.00263064  |
|             7 | 0       |                -0.0315111 |  -0.00205521  |   -0.00347845 |  -0.00176316  |  -3.56272e-05 | -0.00269824  |  0.000168142 |  -0.00603082 | -0.000631852 |  -0.0189616  |  0.00397569  |

## 4. Training event -> future training -> final CoT

For a local swap event in epoch e, later SGD updates have tangent map A_s = I - eta H_s. Let Phi be their ordered product. Then

Delta z_(k,T)^(e) ~= J_(k,T) Phi_(T<-e) Delta theta_e,

and substituting the local commutator gives a closed history-to-CoT approximation.

Using exact local swap Delta theta plus tangent propagation over 20 epochs x 8 CoT slices: correlation=0.999994, relative L2 error=0.338%.

Using only the Hessian/gradient commutator plus tangent propagation: correlation=0.998317, relative L2 error=2.544%.

## 5. CoT itself has a history-conditioned tangent geometry

For D_t=diag(1-h_t^2), A_t=D_t W, the local influence of an earlier input token x_j on later logit z_t is

d z_t / d x_j = v^T A_t A_(t-1) ... A_(j+1) D_j u,  j<=t.

Analytic recurrence and autograd agree to max absolute error 2.220e-16. The Frobenius norm of the difference between the baseline and swapped CoT tangent maps is 0.051691.

## Evidence statement

In this controlled 10-parameter system, the local temporal order of training examples produces a parameter displacement captured by the noncommuting SGD update fields. That displacement is propagated by the tangent dynamics of later training and is read out differently across CoT prefixes. Training-token, parameter, hidden-state, and CoT-output effects can therefore be connected by explicit derivative and finite-difference identities in this system.
