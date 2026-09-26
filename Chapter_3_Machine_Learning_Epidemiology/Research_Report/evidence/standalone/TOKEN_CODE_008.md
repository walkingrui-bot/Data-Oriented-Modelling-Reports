# TOKEN-CODE-008 — Numerical token code as a causal variable

## Question

Surface token identity, internal numeric code, and downstream computational action are separated. The experiment asks whether particular numeric token codes have effects beyond the visible symbol, and which aspects of code are coordinate artifacts versus causal geometry.

## 1. Gauge control

All scalar inputs were transformed as `x' = a x + c` with a=1.7 and c=-0.43. The model input weight and bias were exactly compensated as `u'=u/a`, `b'=b-(u/a)c`. All bit codes and structural-marker codes were transformed together.

Max hidden-state difference across all questions/chains: **4.720e-16**. Max answer-logit difference: **5.829e-16**. Thus raw coordinate values are not intrinsically meaningful under an exactly compensated reparameterization.

## 2. Frozen-model numeric-code intervention

The visible route token label is held fixed while the numeric value actually fed back is swept continuously from -3 to +3; downstream code is regenerated and the final answer is measured.

|   seed | history   | answer_zero_crossings         |   downstream_code_switches |   max_abs_local_gain |   code_at_max_gain |   gain_sign |
|-------:|:----------|:------------------------------|---------------------------:|---------------------:|-------------------:|------------:|
|     14 | history_A | 0.358184;0.627103;0.935238    |                     0.6275 |              199.098 |              0.625 |           1 |
|     14 | history_B |                               |                            |                1.281 |             -3     |          -1 |
|     25 | history_A | -2.675469;-2.502681;-2.296054 |                    -2.5025 |              239.178 |             -2.5   |           1 |
|     25 | history_B | 0.405996;0.672483;0.919771    |                     0.6725 |              140.95  |              0.67  |           1 |

## 3. Retraining under different codebooks

The surface corpus, targets, training order, optimizer, initialization seed, and update count are fixed while only the numeric codes assigned to visible bit tokens 0/1 are changed over a grid. Structural marker codes remain fixed.

Total trained codebook models: **144**; strict natural-endpoint matched (`0011`, 4/4 correct): **58**.

Top endpoint-matched models by absolute local route-code gain:

|   seed | history   |   code0 |   code1 |   center |   span |   min_marker_distance |   natural_endpoint_vector |   local_route_code_gain |   finite_route_bit_flip_effect |   control_J_fro |   probe_answer_logit |   route0 |   code0_generated |
|-------:|:----------|--------:|--------:|---------:|-------:|----------------------:|--------------------------:|------------------------:|-------------------------------:|----------------:|---------------------:|---------:|------------------:|
|     14 | history_B |    -2   |     1   |    -0.5  |    3   |                   0.3 |                      0011 |               -3.50586  |                      -0.766773 |        3.66229  |            -0.379365 |        0 |                 0 |
|     14 | history_A |    -1   |     1   |     0    |    2   |                   0.3 |                      0011 |               -3.35005  |                       1.88731  |        2.94018  |            -0.237086 |        1 |                 0 |
|     25 | history_B |    -1   |     1   |     0    |    2   |                   0.3 |                      0011 |               -3.02058  |                       1.3943   |        3.16894  |            -0.264824 |        1 |                 0 |
|     25 | history_B |    -1.5 |     1   |    -0.25 |    2.5 |                   0.3 |                      0011 |               -1.70145  |                       1.81173  |        1.74026  |            -0.465362 |        1 |                 0 |
|     14 | history_A |    -2   |     1.5 |    -0.25 |    3.5 |                   0.8 |                      0011 |               -1.69579  |                      -0.444555 |        1.68841  |            -0.745657 |        0 |                 1 |
|     25 | history_B |    -0.5 |     1   |     0.25 |    1.5 |                   0.3 |                      0011 |               -1.32541  |                      -0.457043 |        0.982988 |            -1.09761  |        0 |                 0 |
|     25 | history_B |     0.5 |     1   |     0.75 |    0.5 |                   0.2 |                      0011 |               -1.02058  |                       1.32776  |        1.02896  |            -0.638394 |        1 |                 0 |
|     25 | history_A |     0.5 |     2   |     1.25 |    1.5 |                   0.2 |                      0011 |               -0.743398 |                       2.49862  |        0.577376 |            -1.13012  |        1 |                 1 |
|     25 | history_A |    -0.5 |     2   |     0.75 |    2.5 |                   0.3 |                      0011 |               -0.663468 |                      -0.535566 |        0.47831  |            -0.932861 |        0 |                 0 |
|     25 | history_A |    -1   |     1.5 |     0.25 |    2.5 |                   0.8 |                      0011 |               -0.380581 |                      -0.09715  |        0.430585 |            -1.35225  |        0 |                 0 |

### Fixed token distance, moving absolute placement

Codebooks with span=2 keep the distance between 0 and 1 fixed while shifting both along the scalar code axis. Their gains still change, isolating absolute placement relative to the learned nonlinearity/marker geometry from simple code separation.

|   seed | history   |   n |   gain_min |    gain_max |   gain_abs_ratio |
|-------:|:----------|----:|-----------:|------------:|-----------------:|
|     14 | history_A |   3 | -3.35005   | -0.0565146  |         59.2776  |
|     14 | history_B |   3 | -0.087933  | -0.0118343  |          7.43033 |
|     25 | history_A |   2 | -0.0978695 | -0.0146743  |          6.66945 |
|     25 | history_B |   3 | -3.02058   | -0.00398898 |        757.231   |

## 4. Interpretation supported by this toy system

The visible symbol is not the causal object by itself. The raw scalar coordinate is also not intrinsically meaningful, because a global affine code change with exact first-layer compensation is a gauge transformation. What matters is the **uncompensated code geometry relative to the current network and other structural codes**, which sets local state-transition gain, saturation, branch thresholds, and downstream feedback. Particular numeric code regions can therefore have strong extra effects in a fixed/trained coordinate system without implying that a universal number such as `+1` has semantic privilege.


## 5. Smooth high-gain code bands inside a fixed model

To separate true local gain from discrete downstream branch switching, the downstream code token is held fixed while the route numeric code is varied continuously. The exact local derivative is

`dz/dx = v^T D4 W D3 W D2 W D1 u`, where each `Dt = diag(1-h_t^2)` is the tanh local-gain matrix along the chain.

|   seed | history   |   peak_code |   peak_gain |   distance_code1_to_peak |   distance_code0_to_peak |
|-------:|:----------|------------:|------------:|-------------------------:|-------------------------:|
|     14 | history_A |      0.846  |    -4.33792 |                   0.154  |                   1.846  |
|     14 | history_B |     -3      |    -1.28996 |                   4      |                   2      |
|     25 | history_A |     -2.311  |   -10.6039  |                   3.311  |                   1.311  |
|     25 | history_B |      0.8945 |    -3.53934 |                   0.1055 |                   1.8945 |

In the two previously identified strong-control models (seed14 History A and seed25 History B), the learned high-gain band is centered near x≈0.85–0.89, placing the ordinary token-1 code `+1` close to a high-gain region. At token-0 code `-1`, the same models have tiny local gain. Thus a specific numeric code can acquire extra functional effect in a fixed learned coordinate system because it lands near a nonlinear high-gain band. The gauge control shows this does not make `+1` universally privileged: an exactly compensated global reparameterization leaves all behavior invariant.


## 6. Strict observable lock: same CoT strings and same answers, different numeric-code function

The codebook grid was regrouped by seed, training history, all four natural endpoint answers, and the **entire four-question generated chain-bit signature**. Thus models in each group have the same visible answers and the same visible generated CoT bits; only the internal scalar codebook differs.

|   seed | history   | chain_signature   |   n_codebooks | max_gain_codebook   |   max_gain | min_gain_codebook   |    min_gain |   abs_gain_ratio |   endpoint |
|-------:|:----------|:------------------|--------------:|:--------------------|-----------:|:--------------------|------------:|-----------------:|-----------:|
|     25 | history_B | 00|00|11|11       |            13 | (-0.5,1)            |  -1.32541  | (-2,1.5)            | -0.00259433 |        510.887   |         11 |
|     14 | history_B | 00|00|11|11       |            12 | (-2,1)              |  -3.50586  | (-1.5,1.5)          | -0.0116612  |        300.644   |         11 |
|     25 | history_A | 00|00|11|11       |            13 | (-0.5,2)            |  -0.663468 | (-1.5,1.5)          | -0.00335904 |        197.517   |         11 |
|     14 | history_A | 00|00|11|11       |            12 | (-1,1.5)            |  -0.260815 | (-2,0.5)            | -0.00170581 |        152.898   |         11 |
|     25 | history_B | 10|00|11|11       |             3 | (-1,1)              |  -3.02058  | (0.5,1)             | -1.02058    |          2.95967 |         11 |

The strongest group is seed25 History B: 13 different codebooks all produce the same four-question visible chain signature `00|00|11|11` and the same answer vector `0011`. Yet the probe route-code local gain ranges from about 0.00259 to 1.32541, a ~510.9-fold difference. Similar strict-observable groups show ~300.6x, ~197.5x, and ~152.9x gain ratios. Therefore complete observation of this toy CoT string plus the endpoint still does not identify the computational role of its token code.

## Working conclusion

Within this controlled model, particular numeric token codes can have large extra causal effects because training places them in different regions of the learned nonlinear transition geometry. This effect is **coordinate-system dependent rather than universally attached to a number**: a globally affine-transformed code system with exact first-layer compensation is functionally identical. The causal object is therefore the relation between token code, current state, learned weights, nonlinear gain, and the other codes used by the system.
