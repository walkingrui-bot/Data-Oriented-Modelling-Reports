## 2 Token Control Scanner

Experiment WORD-SENSITIVITY-001 · Cloud experiment · 26 September 2026

The scanner measures several ways in which a token can influence subsequent computation. Its first calibration system is a frozen 897-parameter Adam-trained GRU with six-dimensional learned embeddings. Eight matched XOR-style probes provide 44 token positions each: 11 prompt tokens, 31 chain-of-thought tokens, and two answer tokens. The detailed case is Q=0110.

The final readout is the logit difference between answers 1 and 0. The future readout concatenates subsequent hidden states with the final answer propensity. Global percentiles use all eight probes; phase-specific percentiles retain the distinction between prompt, reasoning, and answer positions.

### 2.1 Six complementary measurements

| Measurement | Mathematical object | Operational interpretation |
| --- | --- | --- |
| Drive | $D_t=\|\partial z/\partial e_t\|$ | First-order effect on the final target readout |
| Future Gain | $G_t=\sigma_1(\partial R_{\mathrm{future}}/\partial e_t)$ | Largest local effect on the selected future response vector |
| Alignment | $A_t=|\cos(e_t-e_{\mathrm{ref}},v_{1,t})|$ | Alignment of the centered token embedding with the leading future-control direction |
| Rotation | $R_t=\angle(v_{1,t},v_{1,t+1})$ | Change in the leading local input-control direction between adjacent positions |
| Steer | $S_t=\sigma_1(\partial^2z/\partial e_t\partial e_{t+1})$ | Effect of the current token on the next token’s answer-control vector |
| Persistence | $P_t=\sum_{u\geq t}\|\partial h_u/\partial e_t\|_F$ | Accumulated sensitivity along the measured future trajectory |

Alignment uses the reference embedding and coordinates of the particular model. Persistence accumulates over the selected horizon. Steer measures the adjacent-token mixed derivative. These definitions make each readout reproducible and attach its interpretation to a specified target and measurement window.

### 2.2 Finite intervention closure

The experiment applies symmetric finite embedding perturbations along the leading future-response direction, answer gradient, and leading mixed-derivative direction. The perturbation magnitude is 0.02 times the median centered embedding norm, approximately 0.05281. It compares the resulting secants with the differential predictions.

| Metric | Pearson r | Median relative error | Max absolute error | N |
| --- | --- | --- | --- | --- |
| FutureGain | 0.99999979 | 0.0297% | 1.145e-03 | 44 |
| Drive | 0.99999998 | 2.1150% | 3.348e-05 | 44 |
| Steer | 0.99999999 | 0.0162% | 1.281e-05 | 43 |

Source transcription: [Table 007](../evidence/source_tables/t007_ORIGINAL.csv).

The relative-error convention is $|p-o|/(|p|+10^{-12})$, where $p$ and $o$ are the predicted and observed values. The local audit reproduces the Drive median of 2.115% and Steer median of 0.0162% using this convention. In 28 of the 44 Drive observations, very small predictions correspond to a numerically zero finite response. The maximum absolute Drive error is approximately $3.35\times10^{-5}$. Reporting absolute error, the denominator floor, and the correlation together captures the numerical resolution of the assay.

![Future Gain differential and finite-intervention comparison](../figures/WORD_SENSITIVITY_001_futuregain_validation.png)

Figure 2.1. Future Gain predictions and finite trajectory-response secants in the archived calibration experiment.

![Drive differential and finite-intervention comparison](../figures/WORD_SENSITIVITY_001_drive_validation.png)

Figure 2.2. Final-answer Drive predictions and finite response. The relative-error floor is specified in the text.

![Steer differential and finite-intervention comparison](../figures/WORD_SENSITIVITY_001_steer_validation.png)

Figure 2.3. Mixed-derivative Steer predicts the finite change in the next token’s control vector.

### 2.3 The Q0110 diagnostic record

The following source table is split into matching column groups for readability. Token position is the common row key. Historical `nan` entries mark quantities outside the applicable adjacent-step measurement at the final token.

Source table 008 column group 1 of 3. Repeated leading fields identify the same rows.

| t | Token | Phase | Hotness% | Dominant metric | Flags |
| --- | --- | --- | --- | --- | --- |
| 22 | compute | COT | 99.7159 | Alignment | axis-aligned |
| 43 | 0 | ANSWER | 98.8636 | Drive | drive-hot |
| 42 | answer | ANSWER | 98.2558 | Steer | drive-hot, steer-hot |
| 7 | D | PROMPT | 98.0114 | FutureGain | future-gain-hot, frame-turn, persistent |
| 36 | 1 | COT | 97.7273 | Alignment | axis-aligned |
| 26 | D | COT | 96.5909 | PersistenceArea | future-gain-hot, frame-turn, persistent |
| 41 | ; | COT | 95.9302 | Steer | drive-hot, steer-hot |
| 3 | B | PROMPT | 94.3182 | PersistenceArea | future-gain-hot, persistent |
| 40 | 0 | COT | 94.1860 | Steer | drive-hot, steer-hot |
| 5 | C | PROMPT | 93.7500 | FutureGain | future-gain-hot, persistent |
| 19 | result | COT | 92.3295 | Alignment | axis-aligned |
| 30 | result | COT | 91.7614 | Alignment | axis-aligned |
| 39 | result | COT | 91.2791 | Steer | drive-hot, steer-hot |
| 34 | 1 | COT | 90.1163 | Rotation | frame-turn |
| 38 | final | COT | 90.1163 | Steer | steer-hot |

Source table 008 column group 2 of 3. Repeated leading fields identify the same rows.

| t | Drive | FutureGain | Steer | Alignment | Rotation° |
| --- | --- | --- | --- | --- | --- |
| 22 | 1.101e-10 | 0.6139 | 1.646e-10 | 0.8264 | 70.3549 |
| 43 | 0.1586 | 0.5061 | nan | 0.3264 | nan |
| 42 | 0.0592 | 0.7117 | 0.0675 | 0.0680 | 67.1773 |
| 7 | 2.339e-16 | 1.8303 | 9.129e-17 | 0.0510 | 86.2650 |
| 36 | 1.624e-04 | 0.7061 | 1.804e-04 | 0.7684 | 46.7366 |
| 26 | 1.784e-08 | 1.7646 | 7.510e-09 | 0.1311 | 77.6115 |
| 41 | 0.0451 | 0.6143 | 0.0140 | 0.2069 | 15.0930 |
| 3 | 3.832e-18 | 1.5824 | 4.592e-18 | 0.0715 | 70.9023 |
| 40 | 0.0044 | 0.6177 | 0.0096 | 0.6647 | 32.2078 |
| 5 | 1.977e-17 | 1.6152 | 5.325e-17 | 0.1922 | 53.8683 |
| 19 | 8.563e-12 | 0.5624 | 4.896e-12 | 0.7121 | 74.9151 |
| 30 | 9.390e-08 | 0.5171 | 9.795e-08 | 0.7114 | 72.3496 |
| 39 | 0.0017 | 0.5152 | 0.0018 | 0.6712 | 51.8434 |
| 34 | 2.207e-05 | 0.7006 | 2.551e-05 | 0.6162 | 77.0346 |
| 38 | 4.365e-04 | 0.6876 | 7.547e-04 | 0.1517 | 57.0258 |

Source table 008 column group 3 of 3. Repeated leading fields identify the same rows.

| t | Persistence |
| --- | --- |
| 22 | 1.5443 |
| 43 | 0.6511 |
| 42 | 1.1244 |
| 7 | 3.6689 |
| 36 | 1.1355 |
| 26 | 3.3936 |
| 41 | 1.2653 |
| 3 | 3.2569 |
| 40 | 0.9844 |
| 5 | 3.1081 |
| 19 | 1.1577 |
| 30 | 1.0499 |
| 39 | 0.9869 |
| 34 | 1.4130 |
| 38 | 1.4581 |

Source transcription: [Table 008](../evidence/source_tables/t008_ORIGINAL.csv).

![Token Control Scanner heatmap](../figures/WORD_SENSITIVITY_001_scanner_heatmap.png)

Figure 2.4. Six scanner measurements for Q=0110, expressed as percentiles of the eight-probe calibration distribution.

![Direct and future sensitivity](../figures/WORD_SENSITIVITY_001_drive_vs_futuregain.png)

Figure 2.5. Final-answer sensitivity and future-trajectory sensitivity describe different measured effects.

Prompt token D at position 7 has Drive approximately $2.3\times10^{-16}$, Future Gain 1.8303, Rotation 86.2650 degrees, and Persistence 3.6689. Prompt B at position 3 similarly has Future Gain 1.5824 and Persistence 3.2569. These tokens strongly affect the recorded trajectory even at positions whose direct final-answer gradients are extremely small.

At position 22, `compute` has Alignment 0.8264 with a small direct Drive. The alignment identifies the direction used by the actual embedding displacement; the final answer effect also depends on gain and subsequent propagation. Near the answer, the semicolon at position 41 combines Drive 0.0451 with Steer 0.0140. The `answer` token at position 42 has Steer 0.0675, and the final answer token has Drive 0.1586.

Source table 009 column group 1 of 2. Repeated leading fields identify the same rows.

| t | Token | Phase | Observed role | Drive | FutureGain |
| --- | --- | --- | --- | --- | --- |
| 7 | D | PROMPT | Prompt state-shaper | 2.339e-16 | 1.8303 |
| 3 | B | PROMPT | Prompt persistent shaper | 3.832e-18 | 1.5824 |
| 22 | compute | COT | Aligned but low direct drive | 1.101e-10 | 0.6139 |
| 26 | D | COT | CoT trajectory hotspot | 1.784e-08 | 1.7646 |
| 41 | ; | COT | Late meta-controller | 0.0451 | 0.6143 |
| 42 | answer | ANSWER | Answer-stage driver + steer | 0.0592 | 0.7117 |
| 43 | 0 | ANSWER | Endpoint driver | 0.1586 | 0.5061 |

Source table 009 column group 2 of 2. Repeated leading fields identify the same rows.

| t | Steer | Alignment | Rotation° | Persistence |
| --- | --- | --- | --- | --- |
| 7 | 9.129e-17 | 0.0510 | 86.2650 | 3.6689 |
| 3 | 4.592e-18 | 0.0715 | 70.9023 | 3.2569 |
| 22 | 1.646e-10 | 0.8264 | 70.3549 | 1.5443 |
| 26 | 7.510e-09 | 0.1311 | 77.6115 | 3.3936 |
| 41 | 0.0140 | 0.2069 | 15.0930 | 1.2653 |
| 42 | 0.0675 | 0.0680 | 67.1773 | 1.1244 |
| 43 | nan | 0.3264 | nan | 0.6511 |

Source transcription: [Table 009](../evidence/source_tables/t009_ORIGINAL.csv).

### 2.4 Engineering interpretation and diagnostic card

The measured profiles support several useful descriptions: a direct answer driver, a state or future-trajectory shaper, an adjacent-step steering point, and an action aligned with the leading control direction. A token event can exhibit several of these properties. The diagnostic object is the model, prefix state, token embedding, and target readout together.

A diagnostic card should record the token, position, and phase; raw and calibrated Drive and Future Gain; Alignment; Rotation; Steer; the Persistence horizon; the finite-intervention check; and the calibration distribution. Future Gain and Persistence address changes in the subsequent trajectory. Drive addresses the selected answer readout. The eight-probe calibration establishes this instrument on the specified GRU and teacher-forced trajectories.

The archived CSV, JSON, and figures are indexed under `01_WORD_SENSITIVITY_001`. The next experiment holds token identity fixed and measures the role of the current state.

## 3 The same token across different states

Experiment WORD-SENSITIVITY-002 · Cloud experiment · 26 September 2026

The experiment uses the same frozen GRU and embeddings. A bank of 352 actual prefix states comes from eight probes with 44 positions each. Ten fixed tokens—`0`, `1`, `;`, `result`, `xor`, `A`, `B`, `C`, `D`, and `compute`—are applied to every state, producing a complete 3,520-cell factorial design. The next-token probe for Steer is always `result`.

Each state comes from a recorded canonical trajectory. The current input token is the manipulated variable. The full transplant grid is an engineering stress test of state–token combinations; the natural-occurrence subset retains combinations that appeared on the recorded trajectories.

### 3.1 Local response fingerprint

| Measurement | Definition | Interpretation |
| --- | --- | --- |
| Immediate Drive | $\|\partial z_{\mathrm{after}}/\partial e\|$ | Immediate answer-propensity sensitivity |
| Input Gain | $\sigma_1(\partial h^+/\partial e)$ | Largest token-to-state injection gain |
| Carry Gain | $\sigma_1(\partial h^+/\partial h)$ | Retention or amplification of an incoming state difference |
| Probe Steer | $\sigma_1(\partial^2z_2/\partial e_{\mathrm{current}}\partial e_{\mathrm{result}})$ | Effect on the fixed next probe’s control vector |
| Alignment | $|\cos(e-e_{\mathrm{ref}},\partial z/\partial e)|$ | Token-action alignment with the immediate answer direction |
| State Displacement | $\|h^+-h\|$ | Finite state movement caused by the token |

### 3.2 Token and state variance decomposition

The balanced decomposition separates token identity, state, and their nonadditive interaction. Positive-valued measurements use log10; Alignment uses its original scale. The three sums of squares add to the total for the fixed grid.

| Metric | Scale | Token identity | State | Token × state |
| --- | --- | --- | --- | --- |
| ImmediateDrive | log10 | 19.03% | 6.64% | 74.33% |
| InputGain | log10 | 19.89% | 29.21% | 50.90% |
| CarryGain | log10 | 13.25% | 46.98% | 39.77% |
| ProbeSteer | log10 | 27.09% | 16.36% | 56.55% |
| Alignment | raw | 27.24% | 7.75% | 65.01% |
| StateDisplacement | log10 | 7.83% | 22.43% | 69.75% |

Source transcription: [Table 015](../evidence/source_tables/t015_ORIGINAL.csv).

![Variance decomposition](../figures/WORD_SENSITIVITY_002_variance_decomposition.png)

Figure 3.1. Token identity, state, and token–state interaction contributions across the six measurements.

The interaction accounts for 74.33% of Immediate Drive variation, 56.55% of Probe Steer, and 65.01% of Alignment. Carry Gain has a substantial state main effect, 46.98%, and a 39.77% interaction contribution. These are descriptive variance allocations across the complete diagnostic grid. The 352 prefixes share models and trajectories.

The interaction changes the relative organization of token effects. A single state-dependent gain applied equally to every token would produce a different factorial pattern. The present measurements justify reporting where a particular token has a strong effect, together with the readout used to define that effect.

### 3.3 Context sensitivity cards

| Token | Context dependency percentile | Fingerprint dispersion | Hot-state rate % | Largest span metric | q95/q05 span |
| --- | --- | --- | --- | --- | --- |
| ; | 100.0000 | 2.6134 | 87.2159 | ImmediateDrive | 5.2717 |
| A | 90.0000 | 2.5173 | 33.8068 | ProbeSteer | 4.8650 |
| result | 80.0000 | 2.4715 | 65.0568 | ProbeSteer | 5.2050 |
| B | 70.0000 | 2.2118 | 33.2386 | ProbeSteer | 5.2486 |
| 0 | 60.0000 | 1.9867 | 32.9545 | ImmediateDrive | 4.2224 |
| 1 | 50.0000 | 1.9808 | 33.5227 | ProbeSteer | 3.9211 |
| xor | 40.0000 | 1.8943 | 13.6364 | CarryGain | 2.4586 |
| C | 30.0000 | 1.8886 | 25.0000 | ProbeSteer | 4.1094 |
| compute | 20.0000 | 1.8427 | 32.1023 | ProbeSteer | 5.8009 |
| D | 10.0000 | 1.5498 | 56.8182 | ProbeSteer | 2.4557 |

Source transcription: [Table 017](../evidence/source_tables/t017_ORIGINAL.csv).

![Context sensitivity map](../figures/WORD_SENSITIVITY_002_context_dependency_map.png)

Figure 3.2. Context-dependency ranking and the proportion of states placing a token in at least one global top-decile hotspot.

![Robust state spans](../figures/WORD_SENSITIVITY_002_robust_state_span_heatmap.png)

Figure 3.3. The 95th-to-5th percentile spans over 352 states for each fixed token.

The semicolon has the highest aggregate context-dependency rank within these ten candidates, followed by A, `result`, and B. Probe Steer spans are approximately 5.25 for B, 5.20 for `result`, and 5.80 for `compute`. The ranking belongs to this candidate set and state bank.

### 3.4 Natural occurrences and the transplant grid

| Token | Natural max/min | Transplant max/min | Transplant q95/q05 |
| --- | --- | --- | --- |
| ; | 1.1464 | 5.8640 | 5.1988 |
| result | 1.0392 | 6.8816 | 5.2050 |
| A | 1.3482 | 11.4869 | 4.8650 |
| B | 1.2175 | 9.6237 | 5.2486 |
| compute | 1.0710 | 6.8008 | 5.8009 |

Source transcription: [Table 018](../evidence/source_tables/t018_ORIGINAL.csv).

![Natural and transplanted Probe Steer ranges](../figures/WORD_SENSITIVITY_002_natural_vs_transplant_steer.png)

Figure 3.4. Natural-occurrence and complete-transplant ranges for Probe Steer.

For `result`, the natural maximum-to-minimum ratio is approximately 1.04, and the complete transplant ratio is 6.88. For B, the corresponding ratios are approximately 1.22 and 9.62. The recorded trajectories therefore sample a relatively restricted part of the measured token–state response range. Transplant measurements extend coverage to combinations relevant to stress testing.

### 3.5 Finite validation of high and low states

Source table 019 column group 1 of 3. Repeated leading fields identify the same rows.

| Metric | Token | Low state | Low prefix tail | Low pred | Low obs |
| --- | --- | --- | --- | --- | --- |
| Drive | ; | Q=1001 t=35 COT | 1 ; second result 1 ; combine 1 | 0.0966 | 0.0966 |
| Steer | B | Q=1100 t=19 COT | compute A 1 xor B 1 ; first | 0.0274 | 0.0274 |
| InputGain | B | Q=1011 t=30 COT | compute C 1 xor D 1 ; second | 0.2803 | 0.2804 |

Source table 019 column group 2 of 3. Repeated leading fields identify the same rows.

| Metric | Token | High state | High prefix tail | High pred | High obs |
| --- | --- | --- | --- | --- | --- |
| Drive | ; | Q=1001 t=20 COT | A 1 xor B 0 ; first result | 0.6405 | 0.6402 |
| Steer | B | Q=1100 t=10 PROMPT | 1 B 1 C 0 D 0 reason | 0.2639 | 0.2637 |
| InputGain | B | Q=1011 t=17 COT | reason : compute A 1 xor B 0 | 1.2854 | 1.2850 |

Source table 019 column group 3 of 3. Repeated leading fields identify the same rows.

| Metric | Token | Pred ratio | Observed ratio | Ratio error % |
| --- | --- | --- | --- | --- |
| Drive | ; | 6.6288 | 6.6258 | 0.0460 |
| Steer | B | 9.6200 | 9.6078 | 0.1268 |
| InputGain | B | 4.5858 | 4.5832 | 0.0577 |

Source transcription: [Table 019](../evidence/source_tables/t019_ORIGINAL.csv).

![Finite validation of state-dependent ratios](../figures/WORD_SENSITIVITY_002_finite_pair_validation.png)

Figure 3.5. Predicted and observed high-to-low response ratios with token embeddings held fixed.

For the semicolon in Q=1001, Immediate Drive changes from approximately 0.0966 to 0.6405 across two prefixes. The predicted ratio is 6.6288 and the finite observed ratio is 6.6258. For B in Q=1100, Probe Steer gives ratios 9.6200 and 9.6078. A second B pair gives Input Gain ratios 4.5858 and 4.5832. All three ratio errors are below 0.13%.

The resulting Context Sensitivity Card records identity, context-dependency percentile, hot-state rate, robust spans, natural and transplant ranges, extreme-state examples, and finite validation. Probe Steer retains its fixed `result` probe, and Alignment retains the model’s coordinate and reference convention. The current engineering program uses these present-model measurements to select diagnostic states.

## 4 Executable token operator atlas

Experiment TOKEN-OPERATOR-ATLAS-001 · Cloud experiment · 26 September 2026

The atlas exposes a token as a state-dependent function $T_a(h)$. Engineers can inspect its response signature, apply it at a stored state, compare two tokens, execute a sequence, or measure an order effect. The runtime uses Python and NumPy.

| Command | Operation | Example arguments |
| --- | --- | --- |
| CARD | Retrieve the token’s calibrated operator card | `card B` |
| APPLY | Compute the next state for a token | `apply B --state-id 54` |
| COMPARE | Compare two outputs from a common state | `compare B result --state-id 54` |
| COMPOSE | Execute an ordered token sequence | `compose "A,0,xor,B" --state-id 54` |
| ORDER | Compare the two orders of a token pair | `order B result --state-id 54` |

### 4.1 Runtime reconstruction and calibration

Saved natural transitions, six-dimensional embeddings, and state/input Jacobians supply the reconstruction target. A GRU of the same architecture is fitted to this telemetry. The packaged runtime is this recovered model, with a separately measured agreement to the earlier telemetry.

| Calibration check | Value |
| --- | --- |
| Natural transition MSE | 7.027e-07 |
| 95% abs coordinate error | 0.0015 |
| Max abs coordinate error | 0.0081 |
| Median cosine: A Jacobian | 0.9998 |
| Median rel. error: A Jacobian | 0.0182 |
| Median cosine: B Jacobian | 0.9999 |
| Median rel. error: B Jacobian | 0.0118 |

Source transcription: [Table 030](../evidence/source_tables/t030_ORIGINAL.csv).

All arbitrary token/state queries use the recovered runtime. A second consistency question compares that runtime with the atlas generated from it. The local audit reports a maximum coordinate discrepancy of approximately $5.55\times10^{-16}$ across all 6,336 transitions. The release recalculation gives zero discrepancy with its NumPy execution and the saved values. This runtime-to-table consistency and the reconstruction error above measure different relationships.

### 4.2 Conditional operator signatures

Eighteen tokens are applied to the same 352 ten-dimensional states. Each token’s signature contains the full 352-by-10 array of state movements. Singular-value summaries use these conditional signatures directly.

| Measurement | Value |
| --- | --- |
| Tokens | 18.0000 |
| Real state bank | 352.0000 |
| Token × state transitions | 6.336e+03 |
| Conditional operator signature stable rank | 2.3607 |
| Signature top-3 energy | 0.8730 |
| Signature 95% dimension | 6.0000 |
| All-movement stable rank | 2.0660 |
| All-movement top-3 energy | 0.8265 |
| All-movement 95% dimension | 6.0000 |

Source transcription: [Table 031](../evidence/source_tables/t031_ORIGINAL.csv).

Six shared signature coordinates account for at least 95% of the recorded cross-token variation; the first three account for 87.30%. CARD exposes the coordinates as OP1 through OP6. They provide a compact index on this measured bank.

![Shared operator coordinates](../figures/TOKEN_OPERATOR_ATLAS_001_operator_coordinates.png)

Figure 4.1. Six shared coordinates of the 18 token-operator signatures.

![Operator distance matrix](../figures/TOKEN_OPERATOR_ATLAS_001_operator_distance_matrix.png)

Figure 4.2. Distances between token operators over the common state bank.

![Operator and movement spectra](../figures/TOKEN_OPERATOR_ATLAS_001_spectrum.png)

Figure 4.3. Empirical compression of conditional signatures and state movements.

The source quick-reference table records movement quantiles, response rank, directional consistency, nearest operators, and strong order partners. Matching column groups retain every source row.

Source table 028 column group 1 of 2. Repeated leading fields identify the same rows.

| Token | Move med | Q05 | Q95 | Resp rank | Top3 energy |
| --- | --- | --- | --- | --- | --- |
| &lt;Q&gt; | 2.5065 | 1.5476 | 3.4993 | 1.5369 | 0.9191 |
| A | 2.7874 | 0.8056 | 3.3128 | 1.7545 | 0.8945 |
| 0 | 2.6220 | 1.0867 | 3.4154 | 1.7953 | 0.8998 |
| B | 2.7230 | 0.8782 | 3.2671 | 1.7102 | 0.8970 |
| C | 2.4310 | 1.0373 | 2.8860 | 1.9181 | 0.8706 |
| D | 2.0469 | 0.9441 | 3.1369 | 1.5554 | 0.9012 |
| reason | 2.5874 | 0.8711 | 3.6712 | 1.5955 | 0.9151 |
| : | 3.4453 | 1.4290 | 4.0871 | 1.7088 | 0.8978 |
| compute | 2.5263 | 1.3357 | 3.6020 | 1.4192 | 0.9169 |
| xor | 2.3543 | 0.8452 | 2.8273 | 1.7134 | 0.8815 |
| ; | 3.1285 | 1.6634 | 4.5438 | 1.5248 | 0.9152 |
| first | 2.6027 | 1.0007 | 4.2527 | 1.5691 | 0.9193 |
| result | 2.5576 | 0.9851 | 3.3628 | 1.6083 | 0.8985 |
| second | 2.6324 | 0.7373 | 3.3842 | 1.6625 | 0.9049 |
| combine | 2.4746 | 0.9474 | 3.6116 | 1.5631 | 0.9153 |
| final | 2.3637 | 1.7788 | 3.0217 | 1.6965 | 0.9174 |
| answer | 2.4772 | 1.7161 | 3.0155 | 1.8291 | 0.9051 |
| 1 | 2.5002 | 1.1113 | 3.2873 | 1.8675 | 0.9054 |

Source table 028 column group 2 of 2. Repeated leading fields identify the same rows.

| Token | Direction consistency | Nearest op | Nearest RMSE | Strong order partner | Order effect |
| --- | --- | --- | --- | --- | --- |
| &lt;Q&gt; | 0.5321 | 1 | 0.4025 | first | 3.6686 |
| A | 0.6988 | second | 0.1228 | : | 3.2892 |
| 0 | 0.6924 | 1 | 0.1565 | first | 3.7242 |
| B | 0.6154 | second | 0.1388 | : | 3.2058 |
| C | 0.6149 | B | 0.2462 | : | 3.1505 |
| D | 0.4773 | combine | 0.2586 | compute | 2.7964 |
| reason | 0.7565 | result | 0.2370 | &lt;Q&gt; | 3.4886 |
| : | 0.8184 | ; | 0.3591 | A | 3.2892 |
| compute | 0.6475 | 0 | 0.4380 | first | 3.6605 |
| xor | 0.6669 | C | 0.4003 | : | 2.5414 |
| ; | 0.7515 | : | 0.3591 | compute | 3.2573 |
| first | 0.6150 | combine | 0.2896 | 0 | 3.7242 |
| result | 0.6550 | reason | 0.2370 | 0 | 3.2494 |
| second | 0.6766 | A | 0.1228 | 0 | 3.1830 |
| combine | 0.5164 | D | 0.2586 | 0 | 3.2535 |
| final | 0.4420 | answer | 0.3464 | &lt;Q&gt; | 2.9411 |
| answer | 0.4159 | B | 0.3038 | : | 3.1343 |
| 1 | 0.6199 | 0 | 0.1565 | first | 3.5075 |

Source transcription: [Table 028](../evidence/source_tables/t028_ORIGINAL.csv).

### 4.3 Affine summaries and direct composition

The atlas also fits $T_a(h)\approx A_a h+b_a$ as a browsing summary. Held-out coordinate RMSE ranges approximately from 0.043 to 0.067. APPLY, COMPARE, COMPOSE, and ORDER execute the recovered nonlinear GRU.

| Token | Affine holdout RMSE | Median state error | Q95 state error |
| --- | --- | --- | --- |
| &lt;Q&gt; | 0.0614 | 0.1479 | 0.3532 |
| A | 0.0453 | 0.1192 | 0.2832 |
| 0 | 0.0672 | 0.1676 | 0.3820 |
| B | 0.0476 | 0.1216 | 0.2866 |
| C | 0.0475 | 0.1224 | 0.3079 |
| D | 0.0558 | 0.1296 | 0.3610 |
| reason | 0.0502 | 0.1157 | 0.3328 |
| : | 0.0555 | 0.1342 | 0.3144 |
| compute | 0.0575 | 0.1461 | 0.3302 |
| xor | 0.0468 | 0.1161 | 0.2501 |
| ; | 0.0540 | 0.1339 | 0.2895 |
| first | 0.0563 | 0.1373 | 0.3104 |
| result | 0.0434 | 0.1131 | 0.2331 |
| second | 0.0442 | 0.1157 | 0.2652 |
| combine | 0.0526 | 0.1184 | 0.3363 |
| final | 0.0444 | 0.1024 | 0.2573 |
| answer | 0.0450 | 0.1183 | 0.2465 |
| 1 | 0.0623 | 0.1589 | 0.3417 |

Source transcription: [Table 032](../evidence/source_tables/t032_ORIGINAL.csv).

ORDER evaluates $\|T_b(T_a(h))-T_a(T_b(h))\|$ on the bank. Its output is a finite state difference with an explicit initial state and token order.

| Token A | Token B | Mean order effect | Median | Q95 | Max |
| --- | --- | --- | --- | --- | --- |
| 0 | first | 3.7242 | 3.4795 | 4.2053 | 4.2121 |
| &lt;Q&gt; | first | 3.6686 | 3.5800 | 3.9591 | 3.9654 |
| compute | first | 3.6605 | 3.6823 | 4.1901 | 4.2058 |
| first | 1 | 3.5075 | 3.3188 | 3.9501 | 3.9555 |
| &lt;Q&gt; | reason | 3.4886 | 3.5590 | 3.6460 | 3.6576 |
| 0 | reason | 3.4672 | 3.5098 | 3.6628 | 3.6691 |
| reason | 1 | 3.2928 | 3.3627 | 3.4440 | 3.4608 |
| A | : | 3.2892 | 3.3068 | 3.4050 | 3.4276 |
| reason | compute | 3.2846 | 3.3949 | 3.4468 | 3.4508 |
| compute | ; | 3.2573 | 3.0206 | 3.9090 | 3.9241 |
| 0 | combine | 3.2535 | 3.1238 | 3.6279 | 3.6314 |
| 0 | result | 3.2494 | 3.2914 | 3.3737 | 3.3888 |

Source transcription: [Table 033](../evidence/source_tables/t033_ORIGINAL.csv).

![Order effect matrix](../figures/TOKEN_OPERATOR_ATLAS_001_order_effect_matrix.png)

Figure 4.4. Mean effect of exchanging each pair of token operators.

Large mean order effects include `0`/`first` at 3.7242, `<Q>`/`first` at 3.6686, and `compute`/`first` at 3.6605. The smaller A/`second` effect is approximately 0.235. COMPOSE therefore retains the actual ordered sequence.

### 4.4 Running the included atlas

From the release root:

```sh
cd evidence/cloud/01_Experiments/03_TOKEN_OPERATOR_ATLAS_001
python3 TOKEN_OPERATOR_ATLAS_001_os.py list
python3 TOKEN_OPERATOR_ATLAS_001_os.py card B
python3 TOKEN_OPERATOR_ATLAS_001_os.py apply B --state-id 54
python3 TOKEN_OPERATOR_ATLAS_001_os.py order B result --state-id 54
```

The runtime file contains the recovered GRU, embeddings, state bank, and bases. The manifest supplies operator cards and calibration metadata. State IDs 0–351 address the saved prefixes; `--h` accepts ten comma-separated coordinates. The reported calibration characterizes the saved bank and its local responses. Shared operator coordinates are rebuilt for each model and calibration bank.
