# Figure catalogue

All 56 manuscript figures are present in the English report. Figures 1–10, 15, 35, 47 and 54 use English reconstructions from the reported measurements; the source graphics are retained under evidence/original_figures. The remaining figures preserve the supplied image files. Captions state the sample, quantity and uncertainty convention.

**[Figure 1](figures/figure_01.png)** Positional clustering in the research-conversation code sequence relative to 400 frequency-preserving permutations. Bars show observed/reference ratios for the window Fano statistic, repeated bigram types and repeated trigram types. The vertical axis is logarithmic because the trigram ratio is approximately 191.3. No uncertainty bars are shown.

**[Figure 2](figures/figure_02.png)** Surface-density equalization on the research-conversation code sample. Blue bars show the raw distribution and orange bars the corrected effective mass. Normalized entropy rises from 0.912 to 0.983; Gini falls from 0.485 to 0.220. The last two pairs show the mass held by the highest-frequency 5% and 10% of codes. Values are descriptive statistics without error bars.

**[Figure 3](figures/figure_03.png)** Differences between resolved and unresolved Claude 4 Sonnet trajectories after length matching. Action and transition entropy differences are +0.095 and +0.019, while repeated bigram and trigram fractions differ by approximately −0.031 and −0.051. The mean residual length difference is −0.026 steps. Bars are descriptive matched differences; no inferential interval is shown.

**[Figure 4](figures/figure_04.png)** Mean length of recorded reasoning chunks in early, middle and late trajectory phases: 77, 102 and 129 words. The sample comprises 135 chunks from 20 GPT-5-mini trajectories. Points are phase means without uncertainty bars.

**[Figure 5](figures/figure_05.png)** Language statistics across the same trajectory phases. First-person density decreases from 6.00% to 5.20% and social/filler density from 0.337% to 0.222%; repeated bigram and trigram fractions increase overall. Each line is the corresponding descriptive phase statistic; no uncertainty band is shown.

**[Figure 6](figures/figure_06.png)** Leave-one-trajectory-out NLL for the 117 reasoning-to-tool pairs. Sublinear count weighting reduces NLL relative to linear exposure; the table also reports presence-only weighting. Lower NLL is better. Bars show aggregate evaluation values without uncertainty intervals.

**[Figure 7](figures/figure_07.png)** Next-action accuracy for the same 117 pairs. Role-aware weighting reaches 47.86%, compared with 46.15% for raw or square-root weighting and 47.01% for quarter-power weighting. The unchanged folds support a within-experiment comparison.

**[Figure 8](figures/figure_08.png)** Attention mass outside the original 15-nearest-neighbour reference on four numerical datasets. Geometry correction reduces the measured nonlocal mass; a Topology lens masks all edges outside the candidate graph and therefore gives zero by construction. Bars are measured fractions under the specified relation operators, without error bars.

**[Figure 9](figures/figure_09.png)** Mean accuracy of a label-propagation proxy using 10% labelled data on the four numerical datasets. Raw global attention reaches 65.80%; Geometry, Topology and their combination reach 92.20%, 93.65% and 93.92%. These are within-protocol comparisons with the same attention kernel. No uncertainty interval is shown.

**[Figure 10](figures/figure_10.png)** The initial corrective-optics design. Surface language or numerical inputs pass through role identification, sublinear exposure weighting and topology/geometry correction before the standard attention calculation. The conceptual diagram separates corrections to measurement from the core attention operation; it contains no quantitative estimates.

**[Figure 11](figures/figure_11.png)** Sequential lens ablation on four numerical datasets with 10% labels. The blue line shows mean task accuracy and the orange line far-field attention mass. Exposure reduces concentration, Topology masks disallowed far-field edges, and Geometry calibrates the permitted local edges. Points show protocol means without uncertainty bands.

**[Figure 12](figures/figure_12.png)** Accuracy in the cumulative-context probe over 135 steps. Global role protection reduces the gain from exposure correction. Restricting the working neighbourhood before adding Role and Geometry gives 50.37%, compared with 36.30% raw. Bars are aggregate held-out accuracies.

**[Figure 13](figures/figure_13.png)** Held-out next-action accuracy by trajectory quartile. Raw, Exposure-only and the final stack are compared on the same states within each quartile. The final stack’s largest gain over raw occurs in Q3. Lines join descriptive accuracies; no uncertainty intervals are shown.

**[Figure 14](figures/figure_14.png)** Adaptive prescription results in three trajectory batches. Bars compare the fixed default Geometry+Role prescription, ungated adaptation and evidence-gated adaptation. The adjacent tables distinguish the fixed default from the best fixed prescription, particularly in Batch B. All values are held-out accuracies under the stated protocol.

**[Figure 15](figures/figure_15.png)** Estimated switching gain and the one-SE threshold within outer training folds. Batches A and B remain below the threshold and retain the default. Batch C permits routing in five of six folds, covering 73.81% of its states. Bars summarize the gate’s inputs, rather than confidence intervals on the final performance difference.

**[Figure 16](figures/figure_16.png)** Sequential calibrated correction in 128 states from 18 trajectories. Accuracy rises from 50.00% raw to 52.34% with Exposure, 58.59% with Topology, 59.38% with Geometry and 61.72% with Role. Evaluation holds out complete trajectories. Points are aggregate accuracies without uncertainty intervals.

**[Figure 17](figures/figure_17.png)** Accuracy under repeated irrelevant history in 92 eligible states. The raw cumulative representation falls from 50.00% to 31.52% at 16× repetition; the calibrated prescription falls from 61.96% to 55.43%. The x-axis gives the repetition multiplier. Lines join descriptive stress-test values.

**[Figure 18](figures/figure_18.png)** Decision changes relative to the unperturbed prediction in the same 92 states. At 16× irrelevant-history repetition, the raw flip rate is 61.96% and the corrected rate 9.78%. A flip records a changed prediction, irrespective of whether it becomes correct or incorrect.

**[Figure 19](figures/figure_19.png)** Corrected decision-flip rates when ordinary content or a functional-role token is repeated in the current reasoning state. At 16×, the rates are 1.56% and 12.50%. The next-action label is held fixed, so this is a sensitivity comparison; a flip is not automatically a semantically appropriate change.

**[Figure 20](figures/figure_20.png)** Action-state decoding for three models on ten matched tasks. The plotted structural correction is Topology+Geometry; the table separately reports the transferred GPT exposure/role calibration. Blue, orange and green show Raw, Topology+Geometry and the best corrected setting plotted in the source figure. For Qwen, Raw at 27.13% remains better than its best corrected bar at approximately 23.2%.

**[Figure 21](figures/figure_21.png)** Repeated action-bigram and trigram mass in the matched ten-task comparison. The Qwen traces show greater local repetition than the other two model groups. These are descriptive action-sequence statistics; repeated action classes can also occur during legitimate work.

**[Figure 22](figures/figure_22.png)** Qwen action-state accuracy stratified by Submitted and LimitsExceeded status. Structural correction improves the 35-state Submitted subset and reduces accuracy in the 400-state limit-exceeded subset under this decoder. The independent decoder in ASTIG-012B tests and revises the resulting treatment hypothesis.

**[Figure 23](figures/figure_23.png)** First warning and first strong-loop alert in eight Qwen LimitsExceeded trajectories. The horizontal reference is the 50-step limit. All strong alerts occur at steps 9–14. Task identifiers are shown on the x-axis; lines connect the observed task-level timings.

**[Figure 24](figures/figure_24.png)** Task-level strong-loop alerts with W = 8 and threshold 0.50. All eight Qwen LimitsExceeded traces alert; the two Qwen, ten GPT and ten DeepSeek Submitted controls have no strong alerts. Bars show observed proportions in these four groups.

**[Figure 25](figures/figure_25.png)** Strong-loop detection and Submitted-control alert rates across the nine window/threshold settings. Loop detection remains 100%; control alerts occur only in three settings. These are observed task-level rates, with no uncertainty intervals.

**[Figure 26](figures/figure_26.png)** Leave-one-task-out accuracy under the independent 512-dimensional decoder. GPT, DeepSeek and Qwen contribute 153, 267 and 410 states respectively. Bars compare Raw, Local-Corrected and the naive gate-to-Raw treatment. The latter is identical to Local-Corrected where no strong gate fires.

**[Figure 27](figures/figure_27.png)** Next-action class accuracy in the 300 gate-positive Qwen states. Local-Corrected reaches 53.67%, versus 21.67% for Raw and for the naive gate-to-Raw strategy. This measures representation utility within recorded loops.

**[Figure 28](figures/figure_28.png)** Qwen accuracy across the twelve local-history and kNN settings. Local-Corrected exceeds Raw throughout the tested neighbourhood. The naive gated strategy loses much of that retained local information. The x-axis identifies each k/K combination.

**[Figure 29](figures/figure_29.png)** Recorded-edge interception as cooldown horizon increases. Qwen loop coverage rises from 47.0% at h = 1 to 97.0% at h = 4. Always-on cooldown also blocks a small number of Submitted-control edges; gated cooldown blocks none of their 430 states. Bars represent observed proportions.

**[Figure 30](figures/figure_30.png)** Four-command cooldown coverage in all eight Qwen loop tasks. Five tasks have 100% interception, as shown by the task table; pooled coverage is 291/300. The figure gives observed task-level percentages.

**[Figure 31](figures/figure_31.png)** First strong-loop alert and first four-command cooldown interception in the eight Qwen loop tasks. Their separation is one or two steps. The two series show directly observed event times in the recorded trajectories.

**[Figure 32](figures/figure_32.png)** Candidate availability after four-command cooldown in 300 Qwen loop states. Own-history searches cover 43.67%, 47.33% and 59.33% at k = 2, 4 and 8. Same-task external traces supply unseen commands and unseen progression-role candidates in all 300 states. Bars measure availability, not live task success.

**[Figure 33](figures/figure_33.png)** Task-level median similarity ranks of unseen progression exits among unseen external candidates. The eight task medians range from 2 to 15; their state-weighted mean rank is about 8.77. Lower rank means greater cosine similarity.

**[Figure 34](figures/figure_34.png)** Roles of the 300 highest-similarity unseen progression candidates: 139 Edit, 64 Test and 97 Submit. These counts describe stage-blind selection from the recorded external pool.

**[Figure 35](figures/figure_35.png)** Pre-submission observations in 20 GPT/DeepSeek Submitted traces. All have Edit and post-edit verification; 12 have a formal post-edit Test and 11 have a latest Test with return code zero. Bars show trajectory counts.

**[Figure 36](figures/figure_36.png)** Observable phase among 300 Qwen strong-loop decisions: 112 pre-edit, 113 edited but unverified and 75 edited with recorded validation. The percentages are 37.3%, 37.7% and 25.0%.

**[Figure 37](figures/figure_37.png)** Task-level lower bounds on premature stage-blind Submit selections. Within each task, max(0, Submit selections − submit-ready states) gives a guaranteed count. The bounds total at least 76 of the 97 Submit choices. The figure compares role-only Submit counts with these lower bounds.

**[Figure 38](figures/figure_38.png)** Aggregate role allocation with and without phase conditioning. Stage-blind selection gives 139/64/97 Edit/Test/Submit choices; phase-first allocation gives 112/113/75. The latter follows the observed phase rule and availability results.

**[Figure 39](figures/figure_39.png)** First-priority role agreement after replacing hashed geometry with exact sparse cosine. Stage-blind selection agrees in 74/300 states (24.67%), while phase-first routing agrees in 300/300. These values measure compliance with the defined phase rule.

**[Figure 40](figures/figure_40.png)** After one novel command and resumption of the recorded Qwen future, the next gate clears in 8/300 states (2.67%). Mean strong-loop occupancy over the following five decisions is 98.13%. The two bars describe different diagnostic horizons.

**[Figure 41](figures/figure_41.png)** Cumulative replay release coverage at takeover horizons of one through five steps. Release means recorded Submit or diagnostic gate clearance. Coverage is 80, 102, 150, 189 and 300 of 300 states. At five steps, 174 are Submitted and 126 nonterminal states have cleared gates.

**[Figure 42](figures/figure_42.png)** Minimum takeover duration needed for the replay release condition. Counts at one through five steps are 80, 22, 48, 39 and 111. The largest group requires five steps under this W = 8 diagnostic.

**[Figure 43](figures/figure_43.png)** Eight real shell commands stratified by assigned phase: three PRE_EDIT, three POST_EDIT_UNVERIFIED and two POST_EDIT_VALIDATED. The adjacent table records whether each phase group changes source files.

**[Figure 44](figures/figure_44.png)** Distinct observer signals represented in the eight-command study: process status, output semantics, repository delta and smoke/test state. Bar heights summarize the recorded signal categories in the source analysis; they are not detection rates from an independent validation cohort.

**[Figure 45](figures/figure_45.png)** Observed outcomes of the eight real command executions: three compatible passes, one environmental block, one fallback verification, one bad edit detected by the verifier and two shell-only submission cases. These categories distinguish execution, environment, artifact and code state.

**[Figure 46](figures/figure_46.png)** Surface-code distribution differences between the 70 TEXT and 70 ACT strings. Total variation, Jensen–Shannon divergence in bits and one minus mass overlap increase with n-gram order. Total variation and one minus overlap coincide by their definitions here. Points are descriptive corpus statistics.

**[Figure 47](figures/figure_47.png)** Decision-state geometry across the eight-layer model, including embedding Layer 0. Fisher ratio uses the left axis and five-neighbour cross-mode mixing the right. The table reports three-seed means. The mode-related displacement strengthens while neighbourhood mixing remains substantial.

**[Figure 48](figures/figure_48.png)** Held-out linear-probe accuracy by layer for the final-token decision state and whole-sequence mean. Curves are means across three seeds; shaded bands show mean ± one sample standard deviation across those seeds. The dashed line marks 50%. Whole-sequence readability peaks at Layer 6.

**[Figure 49](figures/figure_49.png)** Layerwise stable and effective ranks from the seed-7 analysis. The plotted series are decision stable rank, decision effective rank and token-cloud stable rank; the table additionally reports token-cloud effective rank. These are descriptive spectral dimensions without uncertainty bands.

**[Figure 50](figures/figure_50.png)** First-action outcomes in the two-pair preliminary run. Both ACT and both TEXT variants initiate tool calls. The chart reports counts of two ACT tool actions, two TEXT tool actions and zero correct pair-level hard switches. These are engineering-check observations.

**[Figure 51](figures/figure_51.png)** RUN-1 first actions for 70 TEXT and 70 ACT prompts. TEXT produces 11 textual first actions and 59 tool first actions; ACT produces 70 tool first actions. OTHER is zero in both groups.

**[Figure 52](figures/figure_52.png)** Paired reference margins before and after restoring missing information. The x-axis is the TEXT-prompt margin and the y-axis the corresponding ACT-prompt margin. Points above y = x shift toward ACT. Markers distinguish the 11 correctly switching pairs from the remaining 59; no regression fit or uncertainty interval is shown.

**[Figure 53](figures/figure_53.png)** Final-token Fisher separation at levels 1, 24 and 28 in the pretrained model. Blue bars compare inherited TEXT/ACT labels; orange bars compare the observed ASK/OVER_ACT subgroups among TEXT prompts. Level 24 is the output of zero-indexed block 23. Bars reproduce summary measurements without uncertainty intervals.

**[Figure 54](figures/figure_54.png)** Bidirectional mode-axis effects and the 95th percentiles of two matched-control distributions for blocks 21–23. Mode effects exceed both orthogonal and effective label-swap controls. The control bars are distribution quantiles, not confidence intervals on the mode effect.

**[Figure 55](figures/figure_55.png)** First-action rescues among all 59 baseline over-action TEXT cases. Bars show the counts at negative doses −0.5, −1 and −2 for the three preselected blocks. A rescue is a tool-first to text-first change in the observed continuation; it is not a count of completed clarification dialogues.

**[Figure 56](figures/figure_56.png)** ACT restoration among the nine block-23 rescues after a second equal-norm opposite intervention. The restoration counts are 9/9 at blocks 24, 25 and 26 and 5/9 at block 27. The x-axis denotes the site of the second intervention. The curve is a perturbation-response measurement.

## Regenerating publication charts

`python rebuild_figures.py` recreates Figures 1–10, 15, 35, 47 and 54 from their reported values. It requires numpy, matplotlib and Pillow and does not fetch external data. This publication script reconstructs charts; it does not rerun the underlying experiments.
