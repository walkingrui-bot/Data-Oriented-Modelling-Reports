# CHAIN-SEMANTICS-007

## Aim

Separate the surface identity of a CoT string from its model-specific downstream function. The experiment asks whether different strings can be functionally equivalent and whether the same string can be functionally different after different training histories.

## Functional definition

For fixed model theta, question Q and chain C, define the semantic signature as

S_theta(C;Q) = (h_after_chain, R_theta(C;xi)),

where h_after_chain is the 2D recurrent state immediately after the chain feedback actions, and R_theta(C;xi) is a standardized future-response curve obtained by feeding a probe xi and then the answer marker. Surface distance is Hamming distance between the two visible chain bits; functional distance is the RMS distance between future-response curves, with hidden-state and answer-gradient distances reported separately.

## Seed 14: same symbolic chain square, two different semantic geometries

For the maximally different surface pair 00 vs 11 (Hamming distance 2), History A has future-response RMS distance 2.898590, whereas History B has 0.007250; the ratio is 399.8x. Hidden-state distances are 2.345494 and 0.106825, respectively.

For pair 01 vs 11, History B is an even tighter functional near-synonym: future-response RMS=0.001136, answer-logit difference=0.006328, and answer-state-gradient distance=0.014072. The same two strings in History A have future-response RMS=2.816272, a 2479.6x larger separation.

## Same string, different function

|   seed |   chain |   surface_hamming |   hidden_distance |   answer_logit_absdiff |   answer_state_gradient_distance |   future_response_RMS |   future_response_max_absdiff |
|-------:|--------:|------------------:|------------------:|-----------------------:|---------------------------------:|----------------------:|------------------------------:|
|     14 |      00 |                 0 |          2.35056  |               3.12978  |                        0.302613  |             2.80131   |                      2.81731  |
|     14 |      01 |                 0 |          2.07434  |               3.07751  |                        0.0717276 |             2.72523   |                      2.79817  |
|     14 |      10 |                 0 |          0.574754 |               1.26048  |                        1.86747   |             0.329416  |                      0.910058 |
|     14 |      11 |                 0 |          0.145953 |               0.339355 |                        0.766796  |             0.0952832 |                      0.118162 |

For visible chain 00, the two training histories produce a cross-history post-chain hidden-state distance of 2.350555 and future-response RMS distance of 2.801314, despite the surface string being identical.

## Exact action-space origin of semantic displacement

Let H_theta(x_R,x_C) be the post-chain hidden state. For two action encodings x0 and x1, the finite state displacement obeys the exact line integral

H_theta(x1)-H_theta(x0) = integral_0^1 J_H(x0+s Delta x) Delta x ds.

The same identity holds for the answer logit. The route and code columns of J_H therefore decompose a finite chain change into route-mediated and code-mediated state displacement.

|   seed | history   |   chain0 |   chain1 |   surface_hamming |    delta_h1 |    delta_h2 |   route_integrated_h1 |   route_integrated_h2 |   code_integrated_h1 |   code_integrated_h2 |   hidden_closure_error |   delta_answer_logit |   route_integrated_answer |   code_integrated_answer |   answer_closure_error |
|-------:|:----------|---------:|---------:|------------------:|------------:|------------:|----------------------:|----------------------:|---------------------:|---------------------:|-----------------------:|---------------------:|--------------------------:|-------------------------:|-----------------------:|
|     14 | history_A |       00 |       11 |                 2 |  1.34645    | 1.92052     |             1.08551   |           1.38949     |            0.260937  |            0.531037  |            5.60773e-15 |          -2.83353    |               -2.17988    |               -0.653654  |            8.10463e-15 |
|     14 | history_A |       01 |       11 |                 1 |  1.13764    | 1.63029     |             1.13764   |           1.63029     |            0         |            0         |            5.06826e-15 |          -2.74448    |               -2.74448    |                0         |            7.54952e-15 |
|     14 | history_B |       00 |       11 |                 2 |  0.0724321  | 0.0785184   |             0.0340521 |           0.0196349   |            0.03838   |            0.0588835 |            2.79371e-16 |          -0.0431036  |               -0.01274    |               -0.0303636 |            2.63678e-16 |
|     14 | history_B |       01 |       11 |                 1 |  0.0314443  | 0.00768436  |             0.0314443 |           0.00768436  |            0         |            0         |            4.51028e-17 |          -0.00632792 |               -0.00632792 |                0         |            4.33681e-18 |
|     25 | history_A |       00 |       11 |                 2 | -0.00226676 | 0.0639049   |             0.0117641 |           0.00431984  |           -0.0140309 |            0.059585  |            2.37404e-16 |          -0.0403091  |               -0.00437927 |               -0.0359298 |            2.01228e-16 |
|     25 | history_A |       01 |       11 |                 1 |  0.0120129  | 0.000273525 |             0.0120129 |           0.000273525 |            0         |            0         |            1.71429e-16 |          -0.0016589  |               -0.0016589  |                0         |            6.09322e-17 |
|     25 | history_B |       00 |       11 |                 2 |  0.395836   | 1.90329     |             0.62934   |           1.39046     |           -0.233504  |            0.512831  |            5.67362e-15 |          -2.09519    |               -1.66166    |               -0.433527  |            5.77316e-15 |
|     25 | history_B |       01 |       11 |                 1 |  0.592706   | 1.6169      |             0.592706  |           1.6169      |            0         |            0         |            4.46304e-15 |          -2.02332    |               -2.02332    |                0         |            5.77316e-15 |

Maximum hidden-state closure error: 5.674e-15; maximum answer-logit closure error: 8.105e-15.

## Local control geometry

For the 2D action coordinates, J_C = d h_after_chain / d(x_R,x_C). Its singular values quantify how strongly local token-action differences are expanded or contracted by the recurrent dynamics.

|   seed | history   |   chain |        J11 |       J12 |        J21 |       J22 |   singular1 |   singular2 |   frobenius |   determinant |
|-------:|:----------|--------:|-----------:|----------:|-----------:|----------:|------------:|------------:|------------:|--------------:|
|     14 | history_A |      00 | 0.0536388  | 0.0824511 | 0.0157171  | 0.0360495 |   0.105762  |  0.00603019 |   0.105933  |   0.000637763 |
|     14 | history_A |      01 | 0.082663   | 0.127066  | 0.150514   | 0.345228  |   0.40531   |  0.0232226  |   0.405975  |   0.00941234  |
|     14 | history_A |      10 | 0.725337   | 0.149418  | 1.26501    | 0.491805  |   1.54231   |  0.108739   |   1.54614   |   0.167709    |
|     14 | history_A |      11 | 0.512484   | 0.105571  | 0.165091   | 0.0641834 |   0.551701  |  0.02803    |   0.552412  |   0.0154642   |
|     14 | history_B |      00 | 0.0406632  | 0.0217289 | 0.0355819  | 0.0633112 |   0.0832584 |  0.0216348  |   0.0860234 |   0.00180128  |
|     14 | history_B |      01 | 0.0360879  | 0.0192841 | 0.00949396 | 0.0168927 |   0.044235  |  0.0096426  |   0.0452738 |   0.00042654  |
|     14 | history_B |      10 | 0.00652738 | 0.0196177 | 0.00500358 | 0.0446474 |   0.0493003 |  0.00392029 |   0.0494559 |   0.000193272 |
|     14 | history_B |      11 | 0.00576063 | 0.0173133 | 0.00130523 | 0.0116467 |   0.0215879 |  0.00206109 |   0.021686  |   4.44945e-05 |

In seed14 History B the control Jacobian Frobenius norm is small across all four discrete chains (0.0217-0.0860), matching the observed collapse of multiple strings into nearly the same downstream response family. History A contains much larger-gain regions, including ||J_C||_F=1.5461 at chain 10.

## Parameter-history origin of a same-string semantic change

For seed14 visible chain 00, the exact finite difference between History A and History B was decomposed along the straight parameter path theta_B+s(theta_A-theta_B) by integrating the parameter Jacobian of the post-chain state and answer logit.

| parameter   |   delta_parameter |   contribution_h1 |   contribution_h2 |   contribution_answer_logit |   contribution_state_norm |
|:------------|------------------:|------------------:|------------------:|----------------------------:|--------------------------:|
| W11         |       0.0144401   |       -0.00247773 |       -0.00411396 |                 0.00740559  |                0.00480248 |
| W12         |       0.0106948   |       -0.0044288  |       -0.00610948 |                 0.0103815   |                0.00754586 |
| W21         |       0.0252515   |       -0.0115803  |       -0.0170852  |                 0.0284613   |                0.0206399  |
| W22         |       0.0362335   |       -0.0352483  |       -0.0526683  |                 0.084749    |                0.063375   |
| u1          |       0.130918    |       -0.0181709  |        0.104399   |                -0.093261    |                0.105969   |
| u2          |       0.295892    |        0.299516   |        0.265596   |                -0.392279    |                0.400314   |
| b1          |       0.255833    |       -0.136593   |       -0.462264   |                 0.741303    |                0.482022   |
| b2          |       0.54479     |       -1.50691    |       -1.70402    |                 2.73827     |                2.27474    |
| v1          |       8.61343e-05 |        0          |        0          |                 1.23999e-05 |                0          |
| v2          |       0.0278437   |        0          |        0          |                 0.00473762  |                0          |

State closure error: 3.140e-15; answer-logit closure error: 2.584e-09.

## Mirror replication

|   seed | history   |   mean_future_response_pair_distance |   max_future_response_pair_distance |   min_future_response_pair_distance |   mean_hidden_pair_distance |   mean_control_jacobian_frobenius |
|-------:|:----------|-------------------------------------:|------------------------------------:|------------------------------------:|----------------------------:|----------------------------------:|
|     14 | history_A |                           1.89623    |                          2.89859    |                         0.0991737   |                   1.41727   |                         0.652616  |
|     14 | history_B |                           0.00411459 |                          0.00724959 |                         0.00113578  |                   0.0617821 |                         0.0506098 |
|     25 | history_A |                           0.00408256 |                          0.00646393 |                         0.000240899 |                   0.0457931 |                         0.0604451 |
|     25 | history_B |                           1.42706    |                          2.19085    |                         0.0456738   |                   1.25411   |                         0.655531  |

Seed14 places the expanded semantic geometry in History A and the collapsed geometry in History B. Seed25 shows the mirror organization: History A is collapsed and History B is expanded. This matches the mirror route-control cases previously identified in CHAIN-CONTROL-006.

## Evidence-supported interpretation

In this controlled system, CoT surface identity is not sufficient to identify computational meaning. Different visible chains can produce nearly identical post-chain states and future-response functions within one trained model, while the same visible chain can produce strongly different states and future-response functions across two training histories. The functional mapping is determined by the trained transition dynamics. A useful operational semantics for CoT in this system is therefore model-conditioned state transition and downstream response, rather than string identity alone.
