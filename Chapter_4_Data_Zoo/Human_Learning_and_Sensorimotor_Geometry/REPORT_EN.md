# Human Learning and Sensorimotor Geometry

Biosphere 3 · Chapter 4 Data Zoo · Subreport 2

Living research report · English edition v1.0 · 27 September 2026

## Executive summary

This report brings together four studies of the relationship between dimensionality, human learning and coordinated action. The starting question is practical: which aspects of a complex representation make it demanding to learn or control? Study 001 measures the geometry of seven public datasets. Its most informative example is handwritten digits: people can recognize these objects even though the measured image representation has a participation rank of 20.23 and needs 40 principal components to retain 95% of standardized variance. The distinction between the recorded input and the task performed on that input organizes the report.

Study 002 examines measured learning behavior in 55,080 retained trials from 102 participants. Increasing the number of reward-relevant dimensions from one to three reduces expected reward in both information conditions. When participants know the relevant dimension count, active selection expands and response time rises. Study 003 then compares real body movement with character-level predictive dynamics in a technical-English corpus. Both representations contain a compact dominant spectrum together with a longer tail of variation; their numerical summaries depend on the representation and scaling used.

Study 004 separates physical recruitment from temporal coordination within 900 reaches by ten participants. Broader endpoint movement accompanies an increase of 0.522 effective kinematic channels and a decrease of 0.244 in kinematic stable rank. These are medians of within-participant contrasts. More coordinates can therefore participate in a movement organized by a concentrated covariance spectrum. Across the four studies, available variables, active selection, recruitment breadth and spectral concentration emerge as distinct measurable quantities. Sensorimotor reuse is presented as the mechanistic hypothesis connecting these observations.

## Research map

| Study | Evidence | Main reading question |
| --- | --- | --- |
| 001 · Section 1 | Seven public datasets | How much of the observed geometry fits into four dimensions? |
| 002 · Section 2 | 102 human learners | How do task complexity, selection and learning change together? |
| 003 · Section 3 | 20 motion clips and a text corpus | How concentrated is movement in each representation? |
| 004 · Section 4 | 900 reaches with kinematics and sEMG | How does broader recruitment relate to temporal rank? |

Reader’s note. This summary, the glossary and paragraphs labelled “Reader’s note”, “Table note” or “Figure note” provide additional interpretation and measurement context. Study identifiers 001–004 connect the report to its evidence files. Tables and figures are numbered consecutively throughout this edition.

## Terms and abbreviations

| Term | Meaning in this report |
| --- | --- |
| Raw dimension / p | Number of recorded variables or retained measurement channels. |
| Relevant dimension | A feature dimension that affects the reward rule in Study 002. |
| Selected dimension | A dimension on which a learner actively chooses a feature. |
| Recruitment breadth / B | Effective number of channels sharing displacement or activity energy: B = (Σe)² / Σe². |
| Covariance / C; eigenvalue / λ | C describes joint variation; its eigenvalues quantify variation along principal modes. |
| Stable rank | Report convention: Σλ / λ₁. A dimensionless measure of concentration in the strongest mode. |
| Participation rank / PR | (Σλ)² / Σλ². Effective number of energetic covariance modes. |
| PCA / PC | Principal component analysis / principal component. |
| d80, d90, d95 | Number of ordered modes needed to retain 80%, 90% or 95% of total spectral energy. |
| Top-k energy | Fraction of the total spectral energy carried by the first k modes. |
| ID / MLE / TwoNN | Intrinsic dimension / maximum-likelihood estimate / two-nearest-neighbor estimate. |
| 10-NN recall | Fraction of the original ten nearest neighbors retained after projection. |
| RT / ms | Reaction time / milliseconds. |
| sEMG / RMS / MAV | Surface electromyography / root mean square / mean absolute value. |
| CMU / UCI HAR | Carnegie Mellon University / University of California, Irvine Human Activity Recognition dataset. |
| L3 / UNK | Three-character context / symbol collecting characters outside the 63-character vocabulary. |
| CI / ρ / SHA | Interval reported with an estimate / Spearman rank correlation / source-content identifier. |

Reader’s note. For a centered data matrix, the stable-rank convention used here equals its squared Frobenius norm divided by its squared spectral norm. The report applies Σλ / λ₁ to covariance eigenvalues, or the equivalent singular-value energies of the language field. Recruitment breadth applies a participation formula to channel energies; participation rank applies it to covariance eigenvalues. Each quantity therefore names both a calculation and the object being measured.

Reader’s note. A “three-to-four” observation should be read together with its metric, signal representation and analysis level. The CONFIRMED, SUPPORTED and PROVISIONAL labels in Sections 3 and 4 describe the source reports’ evidence assessment within the specified datasets. The mechanistic discussion connects the measurements through an explicit hypothesis about control organization.

## 1. Real-Data Screening of Effective Dimensionality and Human Interpretability

From low-dimensional morphology to high-dimensional images

**Table 1. Study 001 overview**

| Question | Do datasets that are easy for humans to reason about directly occupy a low-dimensional variation regime, and what breaks when raw input is high-dimensional? |
| --- | --- |
| Primary measurements | Global covariance ranks, PCA d95, k=10 local intrinsic dimension, TwoNN, four-dimensional variance retention, and four-dimensional neighborhood preservation. |
| Data basis | Numerical results are calculated from the real public datasets described below. |
| Evidence package | HUMAN\_COMFORT\_GEOMETRY\_001\_Evidence.zip |

Table note. Public observational datasets; descriptive geometry. The question about human interpretability motivates the screening. Human ratings or recognition accuracy were not collected in this study.

### 1.1 Experimental motivation

Human reasoning often feels comfortable when only a few quantities vary independently at once. The working hypothesis tested here was that directly understandable data may occupy an effective variation space of roughly three to four dimensions, whereas domains that require statistical or computational assistance may have substantially higher local freedom.

The experiment deliberately included a visual counterexample candidate. Handwritten digits are easy for humans to recognize, but their raw input consists of dozens of pixel variables. This separates two hypotheses: a strict claim that easy human understanding requires low raw intrinsic dimension, and a weaker claim that human cognition operates on a low-dimensional task representation extracted from potentially higher-dimensional input.

### 1.2 Data

**Table 2. Datasets and analyzed variables**

| Dataset | N | Analyzed variables | Role in screening |
| --- | --- | --- | --- |
| Iris | 150 | 4 | Four continuous flower measurements; directly nameable morphology. |
| Palmer Penguins morphology | 342 | 4 | Bill length/depth, flipper length, body mass. |
| Diabetes | 442 | 10 | Ten clinical baseline variables. |
| Wine | 178 | 13 | Thirteen chemical measurements. |
| Breast cancer | 569 | 30 | Thirty continuous nuclear morphology measurements. |
| UCI HAR summary | 180 | 66 | Subject × activity means/standard deviations from wearable-sensor features. |
| Digits | 1797 | 61 | 8×8 grayscale handwritten digits; three constant pixel columns removed. |

Table note. N counts analyzed observations; p counts retained variables. HAR observations are subject–activity summaries. Digits has 61 nonconstant pixels after removing three constant columns.

Five datasets were loaded directly from scikit-learn 1.8.0. Palmer Penguins and the UCI HAR summary were read from their public GitHub data files. The evidence package records the source identities and the exact Palmer Penguins blob SHA.

### 1.3 Geometry measurements

**Table 3. Geometry measurements**

| Measurement | Operational meaning |
| --- | --- |
| Stable rank | trace(C) / λmax(C). Measures how concentrated covariance energy is in the strongest global direction. |
| Participation rank | trace(C)^2 / trace(C^2). Effective number of globally energetic covariance modes. |
| PCA d95 | Number of principal components required for 95% of total standardized variance. |
| Local ID (k=10 MLE) | Nearest-neighbor maximum-likelihood intrinsic-dimension estimate at each observation; the report uses the median. |
| TwoNN | Independent nearest-neighbor ratio estimate of intrinsic dimension. |
| Four-dimensional variance | Fraction of total standardized variance retained by the first four PCs. |
| Four-dimensional 10-NN recall | Fraction of original ten nearest neighbors retained after projection to the first four PCs. |
| Four-dimensional distance correlation | Correlation of pairwise distances before and after four-PC projection. |

Table note. Ranks and intrinsic-dimension estimates are dimensionless. PCA retention is a fraction of standardized variance; neighborhood recall is a fraction of original neighbors. C is the covariance matrix and λmax its largest eigenvalue.

Continuous variables were standardized feature-wise before covariance or distance calculations. Constant columns were removed. The local estimate therefore measures variation relative to the observed standardized cloud rather than the nominal number of recorded fields.

Reader’s note. The human-comfort interpretation is a hypothesis motivating this dataset screen. The observed quantities here are geometric summaries; direct learning behavior enters in Section 2.

### 1.4 Experimental procedure

1. Load each real dataset and retain continuous numeric variables specified in the evidence manifest.

2. Remove zero-variance columns and z-score every retained feature.

3. Compute covariance eigenvalues and derive stable, participation and entropy ranks plus PCA d95.

4. Fit nearest-neighbor geometry and estimate local intrinsic dimension using k=10 MLE and TwoNN.

5. Project the same standardized data to four principal components and measure variance retention, 10-NN recall and pairwise-distance correlation.

6. For the five scikit-learn datasets, repeat the analysis on twenty deterministic 80% subsamples to check local-dimension stability.

### 1.5 Results

**Table 4. Geometry across seven public datasets**

| Dataset | p | Participation rank | Local ID (MLE) | TwoNN | d95 | First 4 variance | 4D 10-NN recall |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Iris | 4 | 1.71 | 2.94 | 1.53 | 2 | 100.0% | 99.8% |
| Wine | 13 | 5.10 | 6.99 | 7.88 | 10 | 73.6% | 59.7% |
| Diabetes | 10 | 4.53 | 6.06 | 7.15 | 8 | 76.8% | 51.6% |
| Breast cancer | 30 | 3.98 | 8.37 | 9.46 | 10 | 79.2% | 52.1% |
| Digits | 61 | 20.23 | 8.13 | 8.85 | 40 | 36.5% | 33.6% |
| Palmer Penguins morphology | 4 | 1.92 | 3.90 | 4.02 | 3 | 100.0% | 100.0% |
| UCI HAR subject-activity summary | 66 | 2.01 | 7.96 | 9.75 | 12 | 83.9% | 58.3% |

Table note. Source: combined\_geometry\_results.csv. Descriptive estimates after feature-wise standardization; no covariate adjustment. Percentages are retained variance or neighbor recall. Larger local ID and d95 indicate richer geometry.

![Figure 1](<figures/figure_01_study_001_local_intrinsic_dimension.png>)

**Figure 1. Local intrinsic dimension from the k=10 nearest-neighbor MLE. Morphology occupies the lowest measured local-dimensional regime; the remaining datasets require approximately six to eight local dimensions, with HAR higher under TwoNN.**

Figure note. Study 001; seven standardized public datasets. Bars show median local k=10 MLE estimates from combined\_geometry\_results.csv; no interval bars are plotted.

![Figure 2](<figures/figure_02_study_001_four_dim_variance.png>)

**Figure 2. Fraction of standardized variance captured by four principal components. Handwritten digits are the principal counterexample to a strict raw-four-dimensional account of easy recognition.**

Figure note. Study 001; the same seven datasets. Bars show percentage of standardized variance retained by four PCs, from combined\_geometry\_results.csv; no interval bars are plotted.

![Figure 3](<figures/figure_03_study_001_global_vs_local_dimension.png>)

**Figure 3. Global participation rank versus local intrinsic dimension. Strong global anisotropy can coexist with substantially higher local degrees of freedom.**

Figure note. Study 001; each point is one dataset. Axes compare covariance participation rank and median local k=10 MLE from combined\_geometry\_results.csv; no interval bars are plotted.

### 1.6 Evidence-supported interpretation

Iris and Palmer Penguins morphology fall directly in the proposed low-dimensional zone. Their local MLE intrinsic dimensions are approximately 2.94 and 3.90, and four dimensions preserve essentially all of the measured geometry. These datasets support the idea that direct multivariable reasoning is naturally comfortable when the observed variables themselves occupy only a few independent directions.

Wine, Diabetes and Breast Cancer shift into a higher local regime: approximately 6.99, 6.06 and 8.37 local dimensions. A four-PC representation preserves only about half of the ten-neighbor structure in these datasets. This supplies a concrete geometric distinction between direct low-dimensional morphology and multivariable domains normally handled with statistical models.

UCI HAR supplies an important separation between global and local geometry. Its participation rank is approximately 2.01 and its first four PCs carry about 83.9% of standardized variance, yet its local MLE dimension is about 7.96 and TwoNN is about 9.75. Strong correlations among sensor variables create a small number of global axes without reducing all local combinations to two dimensions.

Handwritten digits reject the strict version of the hypothesis. The dataset is easy for humans to recognize as objects, but its participation rank is about 20.23, d95 is 40, local MLE dimension is about 8.13, and four PCs retain only 36.5% of variance and about one third of local neighbors. Human object recognition therefore does not require the raw sensory manifold itself to live in three or four dimensions.

### 1.7 Updated hypothesis: a low-dimensional control workspace

The combined pattern supports a more specific hypothesis than a raw-data threshold: human explicit reasoning may be comfortable when the task requires only a few simultaneously independent control variables, even when the sensory input from which those variables are extracted is much higher-dimensional. In this formulation, difficulty depends on task/control dimension, compression burden and nuisance interference rather than raw feature count alone.

A testable mechanistic extension is that this control bandwidth may be related to the geometry of sensorimotor coordination. If abstract reasoning reuses neural machinery developed for movement planning, prediction and action simulation, then a small set of simultaneously active control synergies could provide a natural three-to-four-dimensional working regime. This report treats that statement as a mechanism hypothesis for direct motor-data testing; the present experiment establishes the data-geometry side of the question.

### 1.8 Resampling check

**Table 5. Local-dimension stability under subsampling**

| Dataset | 10th percentile | Median | 90th percentile |
| --- | --- | --- | --- |
| Breast cancer | 8.14 | 8.28 | 8.43 |
| Diabetes | 5.92 | 6.06 | 6.27 |
| Digits | 7.89 | 7.97 | 8.07 |
| Iris | 2.73 | 2.85 | 2.97 |
| Wine | 6.43 | 6.58 | 6.75 |

Table note. Source: resampling\_stability.csv. Percentiles summarize 20 deterministic 80% subsamples per dataset. These are empirical subsampling quantiles, distinct from a participant confidence interval.

The local-dimension ordering is stable under repeated 80% subsampling. The screening result is therefore carried by dataset geometry rather than a single sample draw.

### 1.9 Evidence synthesis

Established by this experiment: directly interpretable four-variable morphology lies near a three-to-four-dimensional local regime; several multivariable biomedical/chemical datasets occupy a six-to-eight-dimensional local regime; global low rank and local intrinsic dimension are distinct; and easy visual recognition can operate on raw manifolds well above four dimensions.

### 1.10 References and source identities

- scikit-learn 1.8.0 built-in datasets: Iris, Wine, Diabetes, Breast Cancer Wisconsin, Digits.

- Palmer Penguins: allisonhorst/palmerpenguins, inst/extdata/penguins.csv, blob 25b46d384bf81f8399188500ea54917bb49d8890.

- UCI HAR tidy summary: ahmedtadde/UCI-HAR-Dataset, MyTidyDF.txt.

- Vong WK, Hendrickson AT, Navarro DJ, Perfors A. Do Additional Features Help or Hurt Category Learning? Cognitive Science. 2019;43:e12724. doi:10.1111/cogs.12724.

## 2. Human Learning Under One to Three Relevant Dimensions

Trial-level behavioral reanalysis of task complexity, response time and active feature selection

**Table 6. Study 002 overview**

| Question | How does measured human learning change as the true number of reward-relevant dimensions increases from one to three? |
| --- | --- |
| Primary source | 57,240 public trial records from Song et al. (2022), fixed by Git blob SHA e834ccbbe1e183b7e2c094702b50f2e9ce558441. |
| Analyzed sample | 102 participants after reproducing the source paper threshold that excludes four participants below 0.468 overall expected reward. |
| Evidence package | HUMAN\_LEARNING\_DIMENSION\_002\_Evidence.zip |

Table note. The source contains 106 participants; the reported analysis retains 102. The experimental factors are relevant dimension count and knowledge of that count.

### 2.1 Experimental motivation

HUMAN-COMFORT-GEOMETRY-001 suggested that raw dimensionality is not the appropriate cognitive quantity. This experiment moves to direct human behavior and uses a task in which the number of relevant dimensions is explicitly manipulated. The principal candidate variable is therefore task-relevant dimensionality: how many independent feature dimensions must be learned and controlled to maximize reward.

### 2.2 Source experiment and raw data

Song et al. used a three-dimensional “build your own icon” task. Every stimulus had color, shape and texture. Depending on the game, one, two or all three dimensions contained a rewarding feature. Half of the games informed participants of the number of relevant dimensions; the other half did not. Each participant played three games of each of the six resulting conditions, with 30 trials per game.

The public CSV contains 57,240 trial rows from 106 participants. The raw data include participant/game/trial identifiers, true task dimensionality, the hint condition, reaction time, selections on each feature dimension, the realized stimulus and the reward outcome.

### 2.3 Reanalysis and exclusion reproduction

The source paper defines chance expected reward as 0.40 and maximum expected reward as 0.80. For each trial, expected reward probability was reconstructed directly from the realized features and the game rule:

Expected reward = 0.20 + 0.60 × (rewarding relevant features present / relevant dimensions)

Applying the paper’s exclusion threshold of overall expected reward &lt; 0.468 identifies four participants in the raw file: 50, 51, 89 and 86. Their reconstructed overall expected rewards are 0.418, 0.436, 0.455 and 0.466. The analysis therefore retains 102 participants, 1,836 games and 55,080 trials.

Reader’s note. Recalculation from the fixed source identifies 463 retained records with missing RT, selected-feature count and built-feature values. The archived scoring transformation assigns these records zero relevant matches and an expected reward of 0.20. RT and selected-feature summaries use available responses. The 55,080 records therefore include 54,617 records with observed RT and selection counts.

### 2.4 Measurements

**Table 7. Behavioral measurements**

| Measurement | Role |
| --- | --- |
| Expected reward probability | Noise-free task performance implied by the configured stimulus and true reward rule. |
| Reaction time | Raw trial rt; medians summarize skewed response-time distributions. |
| Selected dimensions | Number of dimensions on which the participant actively selected a feature. |
| Relevant-feature match | Fraction of relevant dimensions whose realized feature equals the rewarding feature. |
| All-relevant match | Whether all relevant dimensions simultaneously contain their rewarding feature. |
| Learning gain | Last-five-trial expected reward minus first-five-trial expected reward within games. |

Table note. Expected reward, feature-match fractions and learning gains are on a 0–1 scale. RT is in milliseconds. Selected dimensions is a count from zero to three.

The 3D-minus-1D contrasts were calculated within participant. Uncertainty intervals are 5,000 deterministic paired bootstrap resamples over the 102 participant differences.

### 2.5 Condition-level results

**Table 8. Condition-level learning results**

| Relevant D | Hint | Expected reward | Median RT (ms) | Selected D | Relevant match | All match | First 5 | Last 5 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | Known | 0.633 | 1900 | 1.80 | 0.722 | 0.722 | 0.479 | 0.723 |
| 1 | Unknown | 0.652 | 2325 | 2.33 | 0.753 | 0.753 | 0.470 | 0.738 |
| 2 | Known | 0.533 | 2346 | 2.36 | 0.556 | 0.317 | 0.436 | 0.588 |
| 2 | Unknown | 0.533 | 2346 | 2.35 | 0.555 | 0.322 | 0.445 | 0.599 |
| 3 | Known | 0.510 | 2521 | 2.65 | 0.516 | 0.169 | 0.434 | 0.556 |
| 3 | Unknown | 0.482 | 2346 | 2.33 | 0.470 | 0.102 | 0.414 | 0.527 |

Table note. Source: condition\_summary.csv; each condition contains 306 games and 9,180 retained trial records. Expected reward and match rates average trial records; selected dimensions averages game means. RT is the pooled median of available trial RTs. First 5 and Last 5 refer to expected reward.

![Figure 4](<figures/figure_04_study_002_expected_reward_by_dimension.png>)

**Figure 4. Reconstructed expected reward decreases as the number of truly relevant dimensions increases. Chance is 0.40 and the maximum is 0.80 in every game type.**

Figure note. Study 002; 102 retained participants, 55,080 trial records. Points are condition means of reconstructed expected reward from condition\_summary.csv. Lines connect conditions; no uncertainty bars are plotted.

![Figure 5](<figures/figure_05_study_002_rt_by_dimension.png>)

**Figure 5. When task dimensionality is known, response time increases with relevant dimensionality. In the unknown condition, response time remains near the same operating level across 1D–3D games.**

Figure note. Study 002; points are pooled medians of available trial RTs in milliseconds, from condition\_summary.csv. Knowledge of the dimension count defines the two series; no uncertainty bars are plotted.

![Figure 6](<figures/figure_06_study_002_selected_dimensions.png>)

**Figure 6. Knowing the dimensionality changes the breadth of active selection: approximately 1.80, 2.36 and 2.65 dimensions are selected in known 1D, 2D and 3D games. Unknown games remain near 2.33 dimensions.**

Figure note. Study 002; points average game-level mean selected-feature counts, from condition\_summary.csv. True task dimension is the horizontal axis; no uncertainty bars are plotted.

### 2.6 Paired 1D-to-3D effects

**Table 9. Paired 3D-minus-1D effects**

| condition | metric | Effect (3D−1D) | 95% bootstrap interval |
| --- | --- | --- | --- |
| Known | Expected reward | -0.123 | \[-0.144, -0.102\] |
| Known | Reaction time | 539.3 ms | \[451.7, 630.0\] ms |
| Known | Selected dimensions | 0.850 | \[0.714, 0.986\] |
| Known | Relevant-feature match | -0.206 | \[-0.239, -0.172\] |
| Known | All-relevant match | -0.553 | \[-0.593, -0.510\] |
| Unknown | Expected reward | -0.170 | \[-0.187, -0.152\] |
| Unknown | Reaction time | 51.5 ms | \[-9.1, 113.4\] ms |
| Unknown | Selected dimensions | 0.002 | \[-0.071, 0.073\] |
| Unknown | Relevant-feature match | -0.283 | \[-0.312, -0.253\] |
| Unknown | All-relevant match | -0.652 | \[-0.685, -0.617\] |

Table note. Source: paired\_effects.csv. Effects average participant-level 3D-minus-1D differences, with 5,000 paired participant bootstrap resamples. RT first uses a median within each game, then averages games within participant and condition. The RT contrast therefore differs from subtraction of the pooled RT medians in Table 8.

### 2.7 What the human data support

When participants know the task dimensionality, increasing the relevant dimension count from one to three produces a clear behavioral cost. Expected reward falls by 0.123, relevant-feature match falls by 0.206, and median game reaction time increases by about 539 ms. At the same time, active selection breadth expands by about 0.85 dimensions. The measured cost therefore accompanies a wider task-control demand.

The unknown condition has a different geometry. Participants select approximately 2.33 dimensions across all true task complexities and show little 1D-to-3D change in reaction time. Their performance nonetheless declines more strongly as true complexity rises. This pattern supports a distinction between environmental task dimension and the width of the control policy currently deployed by the learner.

Learning occurs in every condition: expected reward rises from the first five to the last five trials. The gain is largest in 1D games and smaller in 3D games, consistent with slower acquisition when more independent rewarding features must be identified.

### 2.8 External validation beyond three dimensions

A separate human category-learning study by Vong et al. manipulated 4, 10 and 16 binary stimulus features. Its published Experiment 1 provides an important boundary condition for the current hypothesis: additional dimensions harmed performance when most extra features were irrelevant or only weakly predictive, but produced no reliable 4-versus-16 penalty when all features supported the same family-resemblance category structure.

![Figure 7](<figures/figure_07_study_002_vong_external_validation.png>)

**Figure 7. Published 4-feature minus 16-feature accuracy effects from Vong et al. (2019), Experiment 1. Positive values mean the four-feature condition was easier. Error bars are the published 95% intervals.**

Figure note. External published evidence: Vong et al. (2019), Experiment 1, Table 1, DOI 10.1111/cogs.12724. Effects are model-based 4-minus-16-feature accuracy differences, with the published 95% intervals; they are separate from the Song trial reanalysis.

The 4-versus-16 accuracy difference was approximately −2 percentage points in the all-features condition (95% interval −8 to +4), +11 points in the intermediate structure (+5 to +17), and +15 points in the single-feature structure (+7 to +22). Their Experiment 2 again found no dimensionality penalty within family-resemblance categories when feature predictiveness was varied. This independently shows that raw feature count alone does not determine human learning difficulty.

### 2.9 Updated Human Comfort Geometry hypothesis

The two experiments together support a control-space formulation. Human difficulty increases when more independent task-relevant relations must be discovered and simultaneously maintained, and also when many irrelevant dimensions compete for attention. High raw dimensionality can remain manageable when the structure supplies redundancy or a compressible task representation.

Human difficulty ≈ task/control dimension + compression burden + nuisance interference

The present 1D–3D trial data do not by themselves establish a sharp threshold at three or four dimensions. They show a measurable cost as concurrent relevant dimensionality increases within that range, and they reveal adaptive control-width changes when dimensionality is explicitly known. The Vong study shows that sixteen raw dimensions can remain learnable when their information is aligned, placing the likely bottleneck at effective control and attention rather than nominal input dimension.

### 2.10 Sensorimotor-workspace mechanism hypothesis

A mechanistic hypothesis follows naturally from the motor-simulation account proposed in the research discussion. Human movement is commonly organized through coordinated synergies rather than independent control of every muscle or sensory channel. If abstract reasoning reuses predictive and control circuits built for embodied action, a small number of simultaneously active control directions may form a comfortable operating regime for both movement simulation and explicit thought.

This mechanism predicts a measurable correspondence: tasks whose effective control geometry exceeds the dimensionality of ordinary sensorimotor synergies should require stronger decomposition, serial attention, external notation or statistical tools.

### 2.11 Evidence status

Directly reanalyzed evidence: 55,080 retained trials from 102 participants, with task dimensionality, hint condition, response time and feature-selection behavior measured from the public source. The 1D-to-3D effects and bootstrap intervals in this report were calculated from those records. External validation: Vong et al. 2019 values are published aggregate estimates and are kept separate from the raw-data reanalysis.

### 2.12 References and source identities

- Song M, Baah PA, Cai MB, Niv Y. Humans combine value learning and hypothesis testing strategically in multi-dimensional probabilistic reward learning. PLOS Computational Biology. 2022;18:e1010699. doi:10.1371/journal.pcbi.1010699.

- Public raw data: github.com/mingyus/humans-combine-value-learning-and-hypothesis-testing, data/data\_all\_wClickInfo.csv, Git blob e834ccbbe1e183b7e2c094702b50f2e9ce558441.

- Vong WK, Hendrickson AT, Navarro DJ, Perfors A. Do Additional Features Help or Hurt Category Learning? The Curse of Dimensionality in Human Learners. Cognitive Science. 2019;43:e12724. doi:10.1111/cogs.12724.

## 3. Dominant Sensorimotor Geometry and Its Relation to Natural Language

Real human motion trajectories, predictive-language dynamics, and the 3–4 dimensional comfort hypothesis

**Table 10. Study 003 overview**

| Question | Do human movement and natural language share a low-dimensional dominant movement spectrum even when their full representational geometry remains higher-dimensional? |
| --- | --- |
| Real data | 20 CMU motion-capture clips from three subjects + a 431,826-character technical-English corpus. |
| Main motion object | 46 non-root joint-angle channels; angular-velocity movement after angle unwrapping. Finger/thumb channels are excluded because CMU documentation states they were not actually captured. |
| Main language object | 64-symbol character predictive geometry: frequency-weighted bigram teacher field and 3-character predictive-state transitions. |
| Data basis | Measurements use public motion records and the archived technical-English corpus. Mechanistic extensions are identified separately. |

Table note. Motion and language are separate data sources. The text-derived objects describe empirical character prediction in the specified corpus; the motor objects describe measured joint-angle trajectories.

### 3.1 Experimental motivation

HUMAN-COMFORT-GEOMETRY-001 separated raw input dimensionality from human interpretability: high-dimensional images can be easy to recognize, whereas several tabular datasets lose much of their neighborhood structure when forced into four dimensions. HUMAN-LEARNING-DIMENSION-002 then showed that human learners incur measurable costs when more independent task-relevant dimensions must be tracked, while the actively selected control width can remain near a small operating range.

The present experiment tests the proposed sensorimotor bridge. The motivating idea is that explicit thought may reuse predictive-control machinery developed for embodied action. The empirical question is therefore narrower than a claim that the body literally has only three or four degrees of freedom: does the energy-dominant geometry of real movement repeatedly concentrate into a few strong directions, and does natural language exhibit a comparable spectral organization?

### 3.2 Real motion data and preprocessing

Twenty AMC motion-capture sequences were analyzed from CMU subjects 01, 02 and 03. The selected material spans playground climbing/swinging, ordinary walking and running, jump/balance, punching, lifting, swordplay, washing, and walking on uneven terrain. CMU records these motions at 120 Hz. The database documentation notes that hand/toe joints can be noisy and that finger/thumb joints were added for editing rather than captured; finger/thumb channels were therefore excluded in the primary analysis.

**Table 11. Motion-source coverage**

| Source | Clips | Movement range |
| --- | --- | --- |
| Subject 01 | 6 | Playground: jumping, climbing, hanging, swinging, descending |
| Subject 02 | 10 | Walk, run, jump/balance, punch, lift, swordplay, wash |
| Subject 03 | 4 | Walk on uneven terrain |

Table note. N counts clips from three people. Clips are descriptive analysis units and include repeated observations from the same person.

### 3.3 Geometry measured

For each frame, x\_t is the vector of retained joint angles. Angle channels were unwrapped before differencing. Realized movement is v\_t = x\_(t+1) − x\_t. The covariance spectrum of x\_t measures the configuration space actually occupied by a clip; the covariance spectrum of v\_t measures the directions in which the body is actually moving.

Reader’s note. The movement vector is a per-frame angular difference. Converting it to degrees per second at 120 Hz multiplies every channel by the same constant and preserves these normalized spectral summaries.

**Table 12. Spectral measurements**

| Metric | Definition | Interpretation |
| --- | --- | --- |
| Stable rank | Σλ / λ₁ | Energy-weighted number of dominant directions; the main cross-domain comparison. |
| Participation rank | (Σλ)² / Σλ² | Broader effective dimensionality of the spectrum. |
| d80 / d95 | Modes reaching 80% / 95% energy | How many directions are needed for increasingly faithful reconstruction. |
| Top-4 energy | Σ first four λ / Σλ | How much actual movement is carried by four dominant modes. |

Table note. All spectral summaries are dimensionless. λ denotes a nonnegative spectral eigenvalue. Top-4 is reported as a percentage when displayed in results tables.

Two motion geometries were retained. Raw-amplitude geometry centers joint-angle channels but preserves their observed angular amplitudes, so frequently and strongly moving joints dominate the spectrum. Coordinate-balanced geometry z-scores each channel before the spectrum, giving small and large joint variations equal variance. A five-frame moving average supplies a separate sensitivity analysis for high-frequency measurement noise.

### 3.4 Human motion: a low-rank core over a broad tail

**Table 13. Motion geometry by representation**

| Motion representation | Stable rank | Participation rank | d95 | Top-4 |
| --- | --- | --- | --- | --- |
| Pose/configuration, raw amplitude | 1.99 | 3.00 | 8 | 89.0% |
| Angular velocity, raw amplitude | 4.04 | 8.06 | 20 | 62.4% |
| Angular velocity, 5-frame smooth | 3.29 | 7.01 | 18 | 64.4% |
| Angular velocity, coordinate-balanced | 6.50 | 15.11 | 25 | 42.0% |

Table note. Source: motion\_trial\_geometry.csv. Entries are medians over 20 clips. Raw-amplitude spectra preserve differences in channel amplitudes; coordinate-balanced spectra standardize each retained channel. No covariate adjustment.

The central result is a separation between dominant movement geometry and full joint-wise complexity. Across all 20 clips, the median raw angular-velocity stable rank is 4.04; after the five-frame smoothing sensitivity analysis it is 3.29. Yet the median d95 remains 20 raw modes and 18 smoothed modes. The body therefore uses a few strong directions without collapsing its complete variation into only three or four coordinates.

![Figure 8](<figures/figure_08_study_003_motion_velocity_stable_rank.png>)

**Figure 8. Stable rank of raw angular-velocity spectra across 20 real CMU motion clips. The dashed line marks rank 4 as a visual reference, not a fitted threshold.**

Figure note. Study 003; one raw-amplitude velocity stable-rank estimate per CMU clip, from motion\_trial\_geometry.csv. Twenty clips come from three subjects. The rank-four line is a reference; no uncertainty intervals are plotted.

**Table 14. Motion geometry by movement family**

| Movement family | N | Raw v stable | Smooth v stable | Raw v d95 | Smooth top-4 |
| --- | --- | --- | --- | --- | --- |
| complex playground | 6 | 3.71 | 4.33 | 21 | 50.0% |
| locomotion | 7 | 4.48 | 2.92 | 17 | 77.4% |
| single/skill actions | 7 | 4.67 | 3.07 | 18 | 66.5% |

Table note. Source: motion\_group\_summary.csv. N counts clips; entries are medians within each movement family. These are descriptive summaries of the selected clips.

Locomotion gives the cleanest concentration: its median smoothed stable rank is 2.92 and its first four modes carry about 77.4% of movement energy. Single/skill actions have a median of 3.07. The playground clips are broader, with a median smoothed stable rank of 4.33, showing that richer body–environment interaction can recruit a wider set of dominant directions.

![Figure 9](<figures/figure_09_study_003_raw_vs_balanced_motion_rank.png>)

**Figure 9. Coordinate balancing broadens the measured movement spectrum. Raw-amplitude rank describes dominant realized movement energy; balanced rank describes how many joint channels can vary when each channel is given equal variance.**

Figure note. Study 003; the same selected clips under raw-amplitude and standardized-channel preprocessing, from motion\_trial\_geometry.csv. The comparison isolates the effect of coordinate scaling; no uncertainty intervals are plotted.

### 3.5 Natural language recalculated with the same spectral logic

The language comparison was recomputed from the same 431,826-character technical-English corpus used in the Chapter 3 language-mathematics experiments. The vocabulary is the 63 most frequent characters plus UNK. The first representation is the frequency-weighted bigram teacher field P(next\|current) minus the unigram baseline. The second forms empirical next-character distributions for three-character contexts observed at least ten times; successive contexts define predictive-state movement.

**Table 15. Language geometry by representation**

| Representation | Stable rank | Participation rank | d95 | Top-4 |
| --- | --- | --- | --- | --- |
| Character bigram teacher field | 2.48 | 4.34 | 13 | 77.4% |
| L3 predictive-state cloud | 4.29 | 10.15 | 22 | 52.0% |
| L3 predictive-state movement | 4.08 | 9.24 | 20 | 55.1% |

Table note. Source: language\_geometry.csv. Each row is one representation of the same 431,826-character corpus. L3 context distributions require at least ten observed occurrences.

The local bigram teacher field has stable rank 2.48. The richer three-character predictive-state cloud has stable rank 4.29, while the actual predictive-state movement has stable rank 4.08. The language state is not exhausted by four dimensions: predictive-state movement requires 20 modes for 95% energy, and the state cloud requires 22.

### 3.6 Direct motion–language comparison

**Table 16. Motion–language comparison**

| Domain | Object | Stable rank | Participation rank | d95 | Top-4 |
| --- | --- | --- | --- | --- | --- |
| Human motion | Angular-velocity movement (raw amplitude) | 4.04 | 8.06 | 20 | 62.4% |
| Human motion | Angular-velocity movement (5-frame smooth) | 3.29 | 7.01 | 18 | 64.4% |
| Natural language | Character bigram teacher field | 2.48 | 4.34 | 13 | 77.4% |
| Natural language | L3 predictive-state movement | 4.08 | 9.24 | 20 | 55.1% |

Table note. Source: motion\_language\_comparison.csv. Motion values summarize 20 clips; language values summarize one corpus. Similar dimensionless statistics compare spectral shape across the specified representations.

![Figure 10](<figures/figure_10_study_003_motion_language_stable_rank.png>)

**Figure 10. Stable rank of dominant movement geometry. The median raw human angular-velocity spectrum (4.04) and the natural-language L3 predictive-state movement spectrum (4.08) are nearly identical under this metric.**

Figure note. Study 003; motion summaries are clip medians and language summaries are corpus-level estimates, from motion\_language\_comparison.csv. The plotted stable ranks describe those representations; no uncertainty intervals are plotted.

![Figure 11](<figures/figure_11_study_003_motion_language_top4.png>)

**Figure 11. Four-mode energy retention. A few dominant modes carry much of both domains, while weaker directions continue beyond four modes.**

Figure note. Study 003; Top-4 reports the fraction of spectral energy in the first four modes, using motion\_language\_comparison.csv. Motion and language use the representations identified on the axes; no uncertainty intervals are plotted.

The numerical coincidence is unusually sharp: median raw human angular-velocity stable rank is 4.042, and natural-language L3 predictive-state movement stable rank is 4.076. Both also have d95 = 20 in the measured representations. These are independently constructed objects with different physical units, so the result is best read as a shared spectral form rather than an equality of coordinates.

Reader’s note. The comparison concerns descriptive spectra from the selected clips and one technical-English corpus. Similar rank values motivate the sensorimotor hypothesis. They provide a comparison of representation geometry; the corpus statistics are not direct measurements of a reader’s neural activity.

### 3.7 Discussion: the number four was never the whole story

At first glance, this experiment seems to hand us a wonderfully simple result: human movement is 'about four-dimensional', natural-language movement is 'about four-dimensional', and the two stable ranks nearly sit on top of one another. The data are more interesting than that. The moment every joint is forced to count equally, the movement spectrum broadens sharply: median angular-velocity stable rank rises from 4.04 to 6.50, participation rank rises to 15.11, and 25 modes are needed to recover 95% of balanced movement energy. The body is therefore not a four-dimensional machine, and language is not a four-dimensional code. What keeps reappearing near three to four dimensions is something more specific: the dominant movement spectrum, the small set of directions carrying the largest share of ongoing change.

This is where the three experiments snap together. HUMAN-COMFORT-GEOMETRY-001 removed the simplest version of the idea by showing that an easy object can arrive through a much richer raw manifold: handwritten digits are perfectly recognizable while their measured image geometry is far above four dimensions. HUMAN-LEARNING-DIMENSION-002 then moved the question from the environment to the learner. When people know how many task-relevant dimensions matter, they widen their active selection; when they do not know, they hover near an approximately two-to-three-dimensional operating width even as the environment becomes harder and performance falls. HUMAN-SENSORIMOTOR-GEOMETRY-003 now adds the missing physical bridge: real multi-joint movement and predictive-language movement both show a compact set of strong directions riding on top of a much broader tail. The hypothesis has therefore changed shape. 'Three to four dimensions' is no longer being treated as the size of the world, the sensory input, or the full internal representation. It is becoming a candidate bandwidth for dominant control.

### 3.8 Sensorimotor reuse: from a nice metaphor to a mechanism we can attack

The sensorimotor-reuse idea can now be stated in a form that is experimentally vulnerable. Suppose abstract reasoning and language reuse part of the predictive-control machinery that originally evolved to coordinate perception, action and feedback. In that case, reasoning does not need to inherit the body's literal joints or coordinates. It only needs to inherit the same style of organization: a high-dimensional state space in which, at any moment, a much smaller set of directions carries most of the active change. That is exactly the spectral pattern measured here.

The numerical match makes the clue hard to ignore: median raw human angular-velocity stable rank is 4.042, whereas natural-language L3 predictive-state movement is 4.076, and both measured representations reach d95 at 20 modes. These numbers do not mean that a hip angle and a character transition are secretly the same coordinate. They mean that two independently constructed dynamical objects exhibit almost the same separation between a low-rank moving core and a higher-dimensional tail. The motor-synergy literature gives this interpretation a biological precedent: complex behavior can be assembled from a small number of strongly expressed coordination patterns while many additional degrees of freedom remain available. Our kinematic result shows the same architecture from a different direction.

### 3.9 What the evidence now supports

**Table 17. Evidence synthesis for motion and language**

| Status | Evidence-supported statement |
| --- | --- |
| CONFIRMED | Twenty selected CMU clips contain a median raw pose stable rank of 1.99 and raw angular-velocity stable rank of 4.04; the median smoothed velocity stable rank is 3.29. |
| CONFIRMED | Coordinate balancing raises median velocity stable rank to 6.50 and participation rank to 15.11, demonstrating that many joint-wise directions remain available beneath the dominant energy spectrum. |
| CONFIRMED | The technical-English bigram teacher field has stable rank 2.48; L3 predictive-state movement has stable rank 4.08 and d95=20. |
| SUPPORTED | Human movement and natural language share a low-rank dominant movement geometry over a higher-dimensional tail in the tested representations. |
| PROVISIONAL | A common sensorimotor-style control bandwidth contributes to the 3–4-dimensional comfort regime observed in human reasoning and learning. |

Table note. Scope: the 20 selected clips and the recorded technical-English corpus. Status terms retain the source report’s distinction between measured results, interpretation and the proposed mechanism.

### 3.10 References and source identities

- CMU Graphics Lab Motion Capture Database. <https://mocap.cs.cmu.edu/> . Motion capture at 120 Hz; CMU documentation notes hand/toe noise and states that finger/thumb joints were not actually captured.

- Public AMC source mirror used for reproducible file identity: <https://github.com/cyun9601/CMU-MOCAP-Data> . Exact Git blob SHAs are listed in source\_manifest.csv.

- Natural-language corpus: walkingrui-bot/biosphere-3-public-reports, Chapter 3 evidence bundle, Git blob 51ccc565cb49f1da25c5791e62a8590ff2f72992.

- d'Avella A, Saltiel P, Bizzi E. Combinations of muscle synergies in the construction of a natural motor behavior. Nature Neuroscience. 2003;6:300–308. doi:10.1038/nn1010.

## 4. Expand the Effectors, Compress the Control Spectrum

Real sEMG-feature and upper-body reaching geometry in 900 human reaches

**Table 18. Study 004 overview**

| Field | Analysis |
| --- | --- |
| Question | When a reach recruits a broader set of body coordinates, does the independent temporal dimensionality of kinematics and muscle activation expand with it? |
| Real data | 10 participants · 900 forward reaches · 21,096 processed windows · 6 kinematic velocity channels · 7 upper-arm sEMG feature streams |
| Main result | Recruitment breadth expands; independent temporal rank stays compact. High-breadth reaches recruit broader kinematics (+0.522 effective channels, 95% CI +0.373 to +0.741) yet show lower kinematic stable rank (−0.244, −0.343 to −0.137). |
| Dominant spectrum | At the single-reach level, 3 modes carry median 95.8% of kinematic and 95.6% of EMG-RMS covariance energy. Pooled participant×target cells still retain ~94% in four modes. |
| Data basis | Quantitative results use the fixed public source. Mechanistic interpretation is distinguished from direct measurement. |

Table note. The primary contrasts compare top and bottom endpoint-breadth tertiles within each participant. Across-participant estimates are medians; 95% intervals resample the ten participants.

### 4.1 Experimental motivation

The previous experiment left us with an uncomfortable but useful clue. Real human movement and natural-language predictive movement both carried a small set of strong directions over a much richer tail. That made “three to four dimensions” look less like the dimensionality of the world and more like the width of a dominant control process. But HUMAN-SENSORIMOTOR-GEOMETRY-003 was still looking at the visible output of the body. The relationship between movement and muscle activity raises a further question: if a reach becomes broader, do the muscles and joint dynamics simply open more independent control channels?

This dataset lets that question be asked inside the same person and the same reach. The important twist is that it also forces us to stop using the word “dimension” as if it meant only one thing. A movement can recruit many joints or muscles and still drive them with a small number of shared temporal commands. The experiment therefore measures both recruitment breadth and independent temporal rank, rather than allowing one to stand in for the other.

### 4.2 Real reaching and muscle-activation data

The primary source is the University of Melbourne Upper Limb Forward-reaching dataset associated with Yu et al. (2023). Ten non-disabled, right-handed participants performed reaching movements to nine spatial targets, with ten repetitions per target. The public processed table contains 21,096 time windows and exactly 900 reaches. Upper-body kinematics are paired with surface-EMG features from seven muscles: biceps short and long heads, triceps lateral and long heads, and anterior, middle and posterior deltoid.

Six kinematic velocity channels were retained: shoulder flexion/extension, shoulder adduction/abduction, scapular protraction/retraction, scapular depression/elevation, trunk flexion/extension and trunk bending. The primary muscle representation uses the seven RMS feature streams; MAV is retained as an independent sensitivity analysis. The public processing pipeline uses 200-ms windows with 100-ms overlap, yielding a 10-Hz feature stream.

**Table 19. Reaching-source identity and sample**

| Source object | Dataset value |
| --- | --- |
| Git blob | 44fa933e7d164aa7279c545047d42d6ee6aae5c4 |
| Rows × columns | 21,096 × 51 |
| Participants | 10 |
| Reaches | 900 (90 per participant) |
| Targets | 9; 10 repetitions per participant×target |
| Kinematic channels used | 6 pose + 6 matched velocity channels |
| Muscle channels used | 7 RMS streams; 7 MAV streams for sensitivity |

Table note. The table describes the fixed processed dataset. A window is a 200-ms feature interval with 100-ms overlap. The 900 reaches comprise 90 reaches per participant.

### 4.3 Two different meanings of “dimension”

The first quantity is recruitment breadth. For a set of non-negative channel energies e\_j, the participation breadth is B = (Σe\_j)² / Σe\_j². A value near 1 means one channel carries nearly everything; a value near 6 or 7 means activity is spread broadly across the available coordinates or muscles. Endpoint breadth is computed from standardized start-to-end displacement across six pose coordinates. Kinematic and EMG energy breadth use mean squared activity after subject-wide RMS scaling.

The second quantity is independent temporal geometry. Within each reach, channels are standardized by the participant-wide mean and SD, their covariance spectrum is decomposed, and stable rank, d90, d95 and top-k energy are measured. Recruitment asks “how many effectors are participating?” Covariance rank asks “how many independent temporal patterns are needed to coordinate what they are doing?” Those questions turn out to have different answers.

All high-versus-low comparisons are made within participant by sorting the 90 reaches on endpoint breadth and contrasting top and bottom tertiles. Across-participant uncertainty is a deterministic 20,000-resample bootstrap of the ten participant-level statistics (seed 20260927). Sign counts are retained alongside the intervals.

Reader’s note. High-minus-low means the difference between the median measure in the upper and lower endpoint-breadth tertiles within each person. The across-person median and bootstrap preserve the participant as the inference unit. Overlapping feature windows and repeated reaches are grouped within participants.

### 4.4 The first clean result: broader reaches really do recruit broader kinematics

The continuous result is strong. Within participant, endpoint movement breadth and kinematic energy breadth have a median Spearman correlation of 0.391, with a 95% bootstrap interval of 0.270 to 0.519. Every one of the ten participants is positive. When the top third of reaches is compared with the bottom third, kinematic energy breadth rises by a median 0.522 effective channels (0.373 to 0.741), again positive in all ten participants.

The spatial target rows tell the same story without using the continuous score. Median endpoint breadth increases from 2.63 to 3.10 to 3.77 across rows 0→1→2, and kinematic energy breadth increases from 4.39 to 4.84 to 5.05. In other words, the broader movement is not a naming convention. More of the measured upper-body coordinate set is actually carrying movement energy.

![Figure 12](<figures/figure_12_study_004_fig1_recruitment_breadth_by_target_row.png>)

**Figure 12. Realized movement and effector recruitment broaden across the three spatial target rows. These are descriptive medians over 300 reaches per row.**

Figure note. Study 004; target\_row\_summary.csv. Each target row pools 300 reaches from ten participants. Breadth is an effective channel count based on displacement or activity energy; points are descriptive medians without uncertainty intervals.

### 4.5 Then the geometry turns around

Here is the part we did not get by simply extending the previous story. If broader movement meant “open more independent control axes”, covariance rank should rise with recruitment. It does not. High-endpoint-breadth reaches show a median kinematic stable-rank change of −0.244 relative to low-breadth reaches, with a 95% interval from −0.343 to −0.137. Nine of ten participants are negative in the full analysis; after excluding the unusually long reaches (&gt;45 processed windows), all ten are negative and the median remains −0.250.

The target rows make the reversal visible at a glance. Kinematic energy breadth climbs 4.39→4.84→5.05, yet kinematic stable rank falls 1.76→1.65→1.44. The body is using more measured coordinates, but their temporal changes are becoming more—not less—coordinated. This is the key distinction of 004: a broader physical realization can be generated by a narrower shared temporal program.

![Figure 13](<figures/figure_13_study_004_fig2_temporal_rank_by_target_row.png>)

**Figure 13. Covariance stable rank does not mirror recruitment breadth. Kinematic temporal rank becomes more concentrated as the target-row movement becomes broader.**

Figure note. Study 004; target\_row\_summary.csv. Points summarize within-reach covariance stable rank across 300 reaches per target row. Higher rank indicates less concentration in the leading mode; no uncertainty intervals are plotted.

![Figure 14](<figures/figure_14_study_004_fig3_subject_contrasts_recruitment_vs_rank.png>)

**Figure 14. Participant-level high-minus-low endpoint-breadth contrasts. Kinematic recruitment broadens in all participants, while covariance stable rank predominantly contracts.**

Figure note. Study 004; subject\_level\_results.csv. Each participant contributes a within-person top-minus-bottom endpoint-breadth-tertile contrast. The zero line indicates no contrast; no bootstrap intervals are plotted.

### 4.6 The muscle side: many muscles are already in the room

The EMG feature streams start from a different baseline. Median EMG energy breadth is 6.36 out of a possible seven muscles: even ordinary reaches already distribute activity across most of the recorded muscle set. That leaves less room for recruitment breadth to expand. The continuous endpoint-breadth ↔ EMG-RMS breadth association is modest (median within-participant ρ=0.208; 95% interval −0.029 to 0.282; seven of ten positive).

The high-versus-low contrast is +0.164 effective muscles for RMS, with an interval that crosses zero (−0.034 to +0.236). Recomputing the same quantity from MAV gives +0.157, and its interval is just above zero (+0.009 to +0.233; eight of ten positive). The two feature families therefore point in the same direction: broader reaches tend to spread muscle activity a little more broadly, but most muscles were already participating.

What does not appear is a matching expansion of independent EMG temporal rank. The high-versus-low stable-rank change is only +0.051 (−0.031 to +0.105), with six positive and four negative participants. More muscle participation is therefore not accompanied by evidence for a correspondingly larger set of independent temporal commands in this representation.

Reader’s note. RMS and MAV are alternative summaries of the same muscle signals. Their agreement is a feature-definition sensitivity check. Covariance modes describe coordinated signal variation; references to commands or control programs are mechanistic interpretations of those measurements.

![Figure 15](<figures/figure_15_study_004_fig5_emg_recruitment_sensitivity.png>)

**Figure 15. EMG recruitment change under high versus low endpoint breadth. RMS and MAV give a similar modest pattern rather than a large dimensional expansion.**

Figure note. Study 004; subject\_level\_results.csv. RMS and MAV contrasts use features from the same seven muscles and the same participants. Points show participant-level high-minus-low recruitment breadth; no bootstrap intervals are plotted.

### 4.7 The 3–4 band survives — but it has moved to the right place

At the single-reach level, the covariance spectrum is extremely concentrated: the first three modes carry a median 95.8% of standardized kinematic variation and 95.6% of EMG-RMS variation. Median d95 is 3 in both domains, and the first four modes carry 98.7% and 98.0%, respectively. Because a typical reach contains only about 20 processed time windows, we did not stop there.

All ten repetitions were then pooled within each participant×target, giving a median of 206 real windows per cell. The spectrum broadens as expected: d90 becomes 4 and d95 becomes 5 for both kinematics and EMG. Yet four modes still carry 94.8% of kinematic covariance energy and 94.0% of EMG covariance energy. Pooling even more broadly at participant×target-row level leaves four modes carrying about 93.2% and 91.9%.

![Figure 16](<figures/figure_16_study_004_fig4_dominant_mode_retention.png>)

**Figure 16. Dominant-mode retention under both short single-reach and longer pooled estimates. The high-fidelity tail extends beyond four modes, but the first three to four carry most of the temporal covariance energy.**

Figure note. Study 004; spectrum\_summary.csv. Retention is summarized across 900 single reaches and 90 participant–target pools. The figure compares retained covariance energy by mode count and analysis level; no uncertainty intervals are plotted.

**Table 20. Spectral geometry at three analysis levels**

| Analysis level | Domain | Stable rank | d90 | d95 | Top-4 |
| --- | --- | --- | --- | --- | --- |
| Single reach | Kinematics | 1.61 | 3 | 3 | 98.7% |
| Single reach | EMG RMS | 1.42 | 3 | 3 | 98.0% |
| Participant × target (≈206 windows) | Kinematics | 1.94 | 4 | 5 | 94.8% |
| Participant × target (≈206 windows) | EMG RMS | 1.74 | 4 | 5 | 94.0% |
| Participant × target-row (≈612 windows) | Kinematics | 2.35 | 4 | 5 | 93.2% |
| Participant × target-row (≈612 windows) | EMG RMS | 1.96 | 4 | 5 | 91.9% |

Table note. Source: spectrum\_summary.csv. Entries are medians across 900 reaches, 90 participant–target cells or 30 participant–target-row cells. Sample counts refer to processed windows; d90/d95 count modes and Top-4 is retained covariance energy.

### 4.8 Discussion: expand the effectors, compress the control spectrum

#### 4.8.1 Recruitment breadth and control rank are different objects

The central result of 004 is not simply that human reaching is low-dimensional. It is that two quantities that sound similar behave in opposite directions. As endpoint movement becomes broader, kinematic energy spreads across more measured coordinates: the high-minus-low contrast is +0.522 effective channels, with all ten participants positive. At the same time, kinematic covariance stable rank falls by 0.244, with the participant-bootstrap interval entirely below zero. The body becomes broader in where it moves and more coordinated in how those coordinates change through time.

That reversal changes the picture of control. A wider action does not require every newly recruited coordinate to become an independently steered axis. The measured movement is consistent with a broad effector mask driven by a smaller set of shared temporal patterns. Put more concretely: the system can light up more of the body without opening the same number of independent control knobs. This is the first experiment in the series that separates those two operations directly inside the same reaches.

#### 4.8.2 The “3–4” observation survives, but the quantity has to be named correctly

The earlier sensorimotor experiment made a 3–4-dimensional dominant band look striking. 004 sharpens that observation by showing that “3–4” is not one universal dimensionality statistic. In this dataset, single-reach stable rank is lower—about 1.61 for kinematics and 1.42 for EMG-RMS—because the short covariance trajectories are strongly concentrated. Yet the first three modes already carry 95.8% and 95.6% of covariance energy, and the first four carry 98.7% and 98.0%. When ten repetitions are pooled within participant×target, the high-fidelity tail expands to d95=5 while the first four modes still carry 94.8% of kinematic and 94.0% of EMG covariance energy.

So the robust cross-experiment object is better described as a dominant control spectrum than as “the dimensionality of movement.” Stable rank, d95 and Top-k energy answer different questions. The full faithful description extends beyond four modes; the strongest three to four modes nevertheless carry most of the temporal organization. This distinction lets the 003 and 004 findings coexist without forcing numerically different estimators into the same box.

#### 4.8.3 The muscle result makes the separation even clearer

The seven EMG streams begin from a nearly saturated recruitment state: median energy breadth is 6.36 out of 7. Most recorded muscles are already materially participating in an ordinary reach. The MAV sensitivity analysis still detects a modest increase in breadth for high-breadth reaches (+0.157 effective muscles, 95% interval +0.009 to +0.233), yet the EMG stable-rank change is only +0.051 and its interval spans zero. The useful message is therefore not “few muscles are used.” It is almost the opposite: many muscles can already be in the room while their temporal activity is organized by a compact shared spectrum.

#### 4.8.4 002, 003 and 004 now form one cleaner architecture

The three experiments now line up as a sequence rather than three isolated dimensionality observations. HUMAN-LEARNING-DIMENSION-002 showed that environmental complexity and deployed selection width can separate: under unknown task dimensionality, people kept an active selection width near 2–3 even as performance deteriorated in harder environments. HUMAN-SENSORIMOTOR-GEOMETRY-003 showed that natural movement and language predictive-state movement both contain a rich tail together with a much smaller dominant movement core. HUMAN-EMG-REACHING-GEOMETRY-004 then supplied the missing mechanical separation: broader physical recruitment can occur while the independent temporal spectrum stays compact or even becomes more concentrated.

The resulting working architecture is therefore: high-dimensional substrate → task-dependent recruitment mask → compact dominant temporal control → high-dimensional realized behavior. Each arrow is now tied to an observable quantity rather than to a metaphor. The substrate is represented by the available channels and the high-fidelity spectral tail; recruitment breadth measures how widely activity is distributed; covariance spectra measure how many strong temporal directions organize that activity; the resulting reach is the physical output.

#### 4.8.5 What this changes about the human-comfort hypothesis

The original question was phrased as though humans might simply be comfortable with data that have only three or four dimensions. The experiments have progressively moved the candidate bottleneck away from the raw world. 001 showed that perceptually manageable data can have substantially richer intrinsic structure. 002 located a small active width in deployed task control. 003 found a low-rank dominant movement core over a richer movement and language state. 004 now shows why such a control core could be useful: it can coordinate a much larger set of simultaneously active effectors without requiring one independent controller per effector.

The stronger hypothesis is therefore about independent control demand. A representation may be large, many coordinates may be active, and the faithful state may need a long spectral tail; cognitive or sensorimotor difficulty should be expected to track how many independent relations must be maintained and changed at once more closely than it tracks the raw number of active variables. 004 supplies an embodied mechanism-shaped example of exactly that separation.

#### 4.8.6 Practical guidance: how to measure this without collapsing everything into one “dimension”

A complete analysis reports at least three layers side by side: available or raw coordinate count, recruitment breadth, and temporal spectral geometry. Recruitment breadth should be computed from physically meaningful channel energy or displacement; temporal geometry should report more than one spectral summary—stable rank together with d90/d95 and Top-k energy—because concentration and high-fidelity tail length are not interchangeable.

Short trials and long pooled trajectories should also be reported separately. In 004, single reaches make the spectrum look extremely concentrated, whereas participant×target pooling reveals a longer faithful tail while preserving the dominance of the first few modes. Within-participant contrasts are especially useful because they ask whether the same nervous system changes recruitment and rank together as task realization changes. Feature-family sensitivity checks such as RMS versus MAV help determine whether an apparent recruitment effect belongs to the underlying muscle pattern or to one summary statistic.

The operational question is simple: when a task becomes broader, does the system recruit more coordinates, open more independent temporal modes, or recruit more coordinates through the same shared modes? 004 demonstrates that these outcomes can be separated empirically. That distinction is the practical contribution of this experiment.

### 4.9 What the evidence now supports

**Table 21. Evidence synthesis for reaching and muscle activity**

| Status | Evidence-supported statement |
| --- | --- |
| CONFIRMED | The fixed public source contains 21,096 processed windows from 900 reaches by 10 participants, with synchronized upper-body kinematics and seven sEMG feature streams. |
| CONFIRMED | Realized endpoint breadth covaries with broader kinematic energy recruitment within participant (median ρ=0.391; 95% CI 0.270–0.519; 10/10 positive). |
| CONFIRMED | High-breadth reaches recruit broader kinematics (+0.522 effective channels; 0.373–0.741) while kinematic covariance stable rank becomes lower (−0.244; −0.343 to −0.137). |
| CONFIRMED | Kinematic and EMG temporal covariance are dominated by a few modes: single-reach top-3 ≈95.8%/95.6%; pooled participant×target top-4 ≈94.8%/94.0%. |
| SUPPORTED | EMG recruitment breadth expands modestly with movement breadth; RMS evidence is heterogeneous, while the MAV high−low sensitivity contrast is positive at the subject-bootstrap level. |
| SUPPORTED | Broader effector recruitment and low-dimensional temporal coordination can coexist in real human reaching. |
| PROVISIONAL | A reusable low-dimensional sensorimotor control bandwidth contributes to the small active-control regime observed in explicit human learning and language/reasoning dynamics. |

Table note. Source: key\_results.csv, spectrum\_summary.csv and long\_trial\_sensitivity.csv. Effect intervals use 20,000 participant bootstrap resamples (seed 20260927). Contrasts are within participant, without additional covariate adjustment. Mechanistic status retains the original report’s distinction.

### 4.10 References and source identities

- Yu T, Mohammadi A, Tan Y, Choong P, Oetomo D. Sensor Selection With Composite Features in Identifying User-Intended Poses for Human-Prosthetic Interfaces. IEEE Transactions on Neural Systems and Rehabilitation Engineering. 2023;31:1732–1742. DOI: 10.1109/TNSRE.2023.3258225.

- Upper Limb Forward-reaching Data from Non-disabled Human Subjects. University of Melbourne / Figshare. <https://figshare.unimelb.edu.au/articles/dataset/Upper_Limb_Forward-reaching_Data_from_Non-disabled_Human_Subjects/23294693>

- Reproducible source mirror: <https://github.com/tianshi-yu/UpperLimbReachingData_HRL_Unimelb> ; DataSet.csv Git blob 44fa933e7d164aa7279c545047d42d6ee6aae5c4.

## Appendix A. Supplementary figure

The evidence archive also contains a pose-versus-velocity comparison for Study 003. It complements the motion summaries in Section 3.

![Figure 17](<figures/figure_17_study_003_pose_vs_velocity_rank.png>)

**Figure 17. Pose and angular-velocity stable rank in the selected CMU motion clips.**

Figure note. Additional figure from the Study 003 evidence archive: pose\_vs\_velocity\_rank.png. Values use the raw-amplitude pose and velocity representations in motion\_trial\_geometry.csv. Each clip contributes both measurements; the comparison describes the selected clips.

## Appendix B. Data and source notes

The four studies are linked by their research question and retain separate datasets and analysis units. Study 002 supplies direct experimental learning behavior. Studies 001, 003 and 004 provide descriptive geometry and within-dataset comparisons. The sensorimotor mechanism discussed across these sections is the shared explanatory hypothesis.

| Study | Report source | Principal evidence tables |
| --- | --- | --- |
| 001 | HUMAN-COMFORT-GEOMETRY-001<br>v0.1 · 27 September 2026 | combined\_geometry\_results.csv<br>resampling\_stability.csv |
| 002 | HUMAN-LEARNING-DIMENSION-002<br>v0.1 · 27 September 2026 | condition\_summary.csv<br>paired\_effects.csv<br>exclusions.csv<br>vong2019\_published\_aggregate.csv |
| 003 | HUMAN-SENSORIMOTOR-GEOMETRY-003<br>v0.2 · 27 September 2026 | motion\_trial\_geometry.csv<br>motion\_group\_summary.csv<br>language\_geometry.csv<br>motion\_language\_comparison.csv |
| 004 | HUMAN-EMG-REACHING-GEOMETRY-004<br>v0.2 · 27 September 2026 | subject\_level\_results.csv<br>key\_results.csv<br>spectrum\_summary.csv<br>long\_trial\_sensitivity.csv |

### Source identity and availability

The supplied collection, HUMAN\_GEOMETRY\_001-004\_COMPLETE\_EXPERIMENT\_DATA\_20260927.zip, contains the four source reports, analysis tables, figures and scripts. It also includes the five scikit-learn 1.8.0 dataset exports used in Study 001. The remaining public inputs are identified in 00\_EXTERNAL\_RAW\_SOURCE\_LOCKS.csv. Its companion download\_external\_raw\_sources.py retrieves their fixed Git blobs and verifies the resulting source identity.

The source identities given in the study references distinguish reproducible inputs from a repository’s changing default branch. For Study 004, local reproduction uses reproduce\_004.py with the --csv argument pointing to the DataSet.csv retrieved through the source-lock downloader. The standalone script’s fallback URL places a Git blob identifier in a raw-file revision path; the source-lock downloader instead uses the Git Blobs API appropriate to that identifier.
