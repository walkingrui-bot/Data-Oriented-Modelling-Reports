# TOOL-CHAIN-GEOMETRY-006G calculation record

## Construction
- Generative semantic planner architecture retained from 006F.
- Input reader expanded from 545 to 665 coordinates to reserve six raw result-style families.
- Raw styles 0-2 were activated during training; raw styles 3-5 were held out completely and their reserved coordinates stayed inactive during training.
- Training: 6,000 executable tasks, 109,684 oracle action contexts, 3 epochs. NLL: 1.046915 -> 0.479326 -> 0.160948.
- Entry gate on seen schemas: oracle-prefix exact action 91.958%; final-state accuracy P1/N1 72.917%; P1/raw-seen 73.333%. Gate passed.
- Formal campaign: 600 held-out worlds (3 x 200), crossed with two schema regimes (seen/unseen) and four provenance x normalization cells = 4,800 executed trajectories.

## Data-geometry precheck
The geometry audit used 2,110 matched result-bearing decision prefixes per representation. Every row was generated from the same task/step/value; only the result representation changed.

Raw seen vs raw unseen:
- Exact matched feature identity: 0.0%.
- Matched z-space mean L2: 21.444; mean cosine: 0.5483.
- 10-NN same-domain fraction: 0.8691.
- Logistic 5-fold seen/unseen classification accuracy: 1.000.
- Combined stable rank: 36.435; participation rank: 233.625; PCA-95 dimension: 368; top-4 energy: 7.243%.
- 4D PCA 10-NN retention: 0.0606; pairwise-distance CV: 0.1330.
- 20 x 80% resampling: stable-rank mean 36.434, SD 0.151; participation-rank mean 231.062, SD 0.228.

Canonical seen vs canonical unseen:
- Exact matched feature identity: 100.0%.
- Matched z-space L2: 0; cosine: 1.0.
- Canonicalization therefore removes the schema-regime displacement exactly in this reader construction.
- The combined canonical profile has stable rank 22.365, participation rank 106.219, PCA-95 dimension 181 and top-4 energy 11.980%.
- TwoNN on the duplicated seen/unseen canonical union is not interpreted because paired rows are exact duplicates and nearest-neighbor ratios degenerate.

## Formal final-state results
Seen-schema regime:
- P+ / N+: 73.667%
- P+ / raw: 73.833%
- P- / N+: 68.167%
- P- / raw: 70.333%
- Provenance main effect: +4.50 pp, bootstrap 95% CI [+2.08, +7.08].
- Normalization main effect: -1.17 pp, bootstrap 95% CI [-3.00, +0.75].
- Interaction: +2.00 pp, bootstrap 95% CI [-0.67, +4.67].

Unseen-schema regime:
- P+ / N+: 73.667%
- P+ / raw: 2.333%
- P- / N+: 68.167%
- P- / raw: 2.667%
- Provenance main effect: +2.58 pp, bootstrap 95% CI [+1.08, +4.08].
- Normalization main effect: +68.42 pp, bootstrap 95% CI [+64.92, +72.00].
- Interaction: +5.83 pp, bootstrap 95% CI [+2.83, +9.00].

Schema-shift contrast:
- Raw-path mean accuracy: 72.083% seen -> 2.500% unseen, change -69.583 pp, bootstrap 95% CI [-73.083, -66.167].
- Canonical-path mean accuracy: 70.917% seen -> 70.917% unseen, change 0.000 pp, CI [0, 0].
- Normalization main effect: -1.167 pp seen -> +68.417 pp unseen.
- Paired increase in normalization effect: +69.583 pp, bootstrap 95% CI [+66.167, +73.083].
- Exact task-outcome agreement between seen and unseen canonical regimes: 100% in both provenance cells.
- Unseen normalized vs raw paired sign tests: P+ 431 better / 3 worse / 166 ties, two-sided p=6.14e-124; P- 398 better / 5 worse / 197 ties, p=8.47e-111.

## Step-level localization
On 10,840 oracle-prefix decisions per schema regime:
- Seen P+/raw overall exact: 92.214%; post-result exact: 90.000%; WRITE-value exact: 88.278%; multi-read WRITE-value exact: 75.336%.
- Unseen P+/raw overall exact: 56.531%; post-result exact: 44.171%; WRITE-value exact: 14.354%; multi-read WRITE-value exact: 12.081%.
- Canonical P+/N+ is unchanged between seen and unseen: overall 92.841%; WRITE-value 88.915%; multi-read WRITE-value 77.013%.
- Unseen raw failures first diverge at approximately step 2.13 with provenance and 2.08 without provenance (median 2), immediately after the first result-bearing action in most tasks.

## Held-out style controls
Each held-out raw dialect was evaluated separately across all 600 tasks on the semantic planner:
- style 3: P+/raw 1.833%, P-/raw 2.000%.
- style 4: P+/raw 3.000%, P-/raw 3.333%.
- style 5: P+/raw 4.000%, P-/raw 3.500%.
The unseen-schema collapse is therefore not driven by one single held-out format.
