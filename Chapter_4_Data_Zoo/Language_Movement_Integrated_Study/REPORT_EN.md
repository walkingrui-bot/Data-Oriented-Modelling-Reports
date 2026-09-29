# Language–Movement Integrated Study

Cross-domain geometry of language, sensorimotor control, intoxicated speech and alcohol-related gait perturbation

Data-Oriented Modelling · Chapter 4 Data Zoo · Subreport 03

English publication edition v1.0 · 29 September 2026

## Executive summary

A complex output can have a compact geometry of change. This study examines that distinction through a normal language–movement reference, published speech-disfluency calibration, a time-resolved acoustic analysis, and a reanalysis of controlled-drinking gait summaries.

In the acoustic specimen, 103 segments from two recordings show broader and more tortuous temporal movement in the intoxicated condition. Timing controls locate much of the observed organization in frame adjacency and coordination across acoustic bands. In the gait analysis, four subgroup displacement vectors derived from a 100-participant study concentrate 77.73% of their squared energy in one leading mode. Feature and subgroup sensitivity analyses characterize how that concentration depends on the representation.

The integrated working hypothesis separates the geometry of a perturbation from the geometry of its realization: a compact state shift may unfold into richer output-specific dynamics. Speech and gait provide complementary measurements of that possibility, with their source populations and units of analysis kept explicit.

The report presents all five studies, thirteen figures and their evidence tables. A terminology guide, primary-source annotation for three ALC table cells, a rounded-matrix reproduction note and a practical measurement checklist support independent reading and reuse.

## Reading guide

Read the results overview for the full numerical argument, Sections 1–2 for measurement vocabulary and motivation, Sections 3–5 for the reference and speech studies, Sections 6–7 for gait geometry and robustness, and Section 8 for the integrated interpretation. Section 9 maps the evidence; Section 10 gives a practical checklist.

Table A. Terminology and abbreviations

| Term | Meaning in this report |
| --- | --- |
| State / movement | A state is a represented observation. Movement is the difference between consecutive states within one sequence. |
| Perturbation / realization | A perturbation is a condition-related displacement. Realization is how change appears in a particular output system and context. |
| Stable rank / PR | Stable rank summarizes energy relative to the leading mode. Participation rank (PR) summarizes how broadly energy is distributed. |
| d95 / Top-4 | d95 counts modes needed for 95% energy. Top-4 is the energy fraction in the leading four modes. |
| SVD / PC1 | Singular value decomposition; PC1 names the leading singular direction here. Gait SVD is uncentered about the zero-displacement origin. |
| SD / RMS | Standard deviation; root mean square. Each refers to the scaling operation specified in the methods. |
| ALC / KAISD | Alcohol Language Corpus; Korean language Alcohol Intoxicated Speech Detector source project. |
| BrAC / BAC | Breath alcohol concentration / blood alcohol concentration. Gait exposure is labelled BrAC as in the source article. |
| Jackknife / permutation | Removing one feature or subgroup; randomizing feature identities or timing under a defined reference construction. |
| Recruitment breadth / tortuosity | Effective number of channels carrying movement energy; trajectory path length relative to endpoint displacement. |

Definitions are specific to the measurement objects used here. A spectral rank is an effective concentration measure; its value depends on representation and scaling.

### Study scope

This report consolidates the language–movement experiments underlying a cross-domain intoxication hypothesis: reference geometry, task-conditioned speech calibration, acoustic matrix geometry, and controlled-drinking gait reanalysis. Source identity, calculation object and evidence level accompany each study.

## Results overview

The study begins from a separation already established in the language and sensorimotor records: a system may occupy a broad state space while its moment-to-moment movement is carried by only a few dominant directions. In the existing reference comparison, median raw human angular-velocity movement has stable rank 4.04 and natural-language L3 predictive-state movement has stable rank 4.08; both require 20 modes for 95% energy in their specified representations. These values distinguish dominant local movement from the higher-dimensional tail needed for faithful representation; each rank refers to its specified representation.

The speech experiment reanalyzes the public KAISD held-out object as 103 approximately eight-second mel-spectrogram segments: 52 sober and 51 intoxicated, each represented by 345 time frames × 128 mel bands. With one shared band-wise scaler, intoxicated temporal movement broadens from stable rank 3.538 to 4.054 and participation rank 10.176 to 13.809. d95 rises from 81 to 87 modes, while Top-4 movement energy falls from 45.26% to 35.51%. At segment level, the intoxicated trajectories take slightly larger steps, retain less directional continuity and become more tortuous, while movement-band recruitment breadth narrows modestly.

Two destructive controls locate the geometry more precisely. Randomizing frame order collapses much of the sober–intoxicated rank gap, showing that a large fraction of the separation belongs to temporal organization. Independently circularly shifting the 128 mel bands destroys their shared timing and drives stable rank into the 80s in both conditions. Real speech in both states is therefore strongly cross-band coordinated; intoxication broadens movement inside a still highly coordinated system with the independently shifted bands providing a much broader reference.

The movement-side reanalysis uses a controlled drinking study with 100 participants (50 women, 50 men) measured at 0.00% and 0.11% BrAC during forward and backward gait. Six selected gait coordinates were converted into four subgroup intoxication-displacement vectors using sober SD units. These four surface responses have an uncentered stable rank of 1.286: the first common direction carries 77.73% of displacement energy and the first two carry 90.74%. A dedicated robustness analysis evaluates that concentration. Removing any one feature leaves first-mode energy between 60.65% and 82.44%; removing any one subgroup leaves 73.28% to 88.46%. In a 200,000-replicate feature-identity permutation control, the observed 77.73% first-mode concentration exceeds the null 95th percentile of 75.82% (empirical one-sided p=0.0275).

Together the measured results motivate a working synthesis nicknamed The Magical Hypothesis: alcohol may apply a comparatively narrow state perturbation, while each output system realizes that perturbation through its own local control dynamics. The gait factorization makes that statement concrete at the aggregate movement level: 61.37% of the standardized displacement energy is shared across sex and walking direction, 21.86% belongs to a sex-dependent realization branch, 8.50% to walking direction and 8.27% to their interaction. In the measured speech specimen the local temporal trajectory broadens while cross-band coordination remains strong; in the gait summary the family of alcohol-induced state shifts is narrow but branches systematically by context. Across these measured objects, surface complexity and perturbation complexity motivate a working architecture: compact perturbation → output-system-specific dynamics → diverse observable symptoms.

Table 1. Experiment map

| Record | Data object | Calculation | Evidence role |
| --- | --- | --- | --- |
| LM-BASE-001 | Prior natural-language and human-motion records | Stable/participation rank, d95, Top-k | Normal cross-domain reference |
| INTOX-SPEECH-CAL-002 | ALC, 150-speaker disfluency analysis | Task-conditioned sober→intoxicated changes | External calibration of task dependence |
| INTOX-SPEECH-GEO-003 | KAISD held-out 103 mel segments | State and Δ-frame geometry + controls | Direct raw-matrix intoxicated-speech evidence |
| INTOX-GAIT-GEO-004 | 100-participant 0.00→0.11% BrAC gait summaries | Standardized displacement vectors + uncentered SVD | Controlled-drinking movement perturbation geometry |
| INTOX-GAIT-ROBUST-005 | 004 4×6 gait-displacement matrix | Jackknives + scaling controls + 200k permutations + 2×2 factorization | Robustness of shared perturbation backbone |

Study IDs retain their sequence across report, figures and evidence folders. The studies combine prior calculations, published aggregate calibration, a two-recording acoustic analysis, and aggregate gait reanalysis.

## 1. Evidence convention and measurement vocabulary

The report distinguishes three evidence layers. Direct matrix calculations describe the selected source rows or tensors. Published aggregate reanalysis describes numeric summaries reported by the source study. Cross-domain synthesis connects those measurements as a working hypothesis. The speech and gait results describe different source populations and different mathematical objects; their integration is a comparison of organization across domains.

For nonnegative eigenvalues ordered from largest to smallest, the spectral summaries are:

$$
r_{\mathrm{stable}}=\frac{\sum_i\lambda_i}{\lambda_1}
$$

$$
\mathrm{PR}=\frac{(\sum_i\lambda_i)^2}{\sum_i\lambda_i^2}
$$

$$
d_{95}=\min\{k:\sum_{i=1}^{k}\lambda_i\geq0.95\sum_i\lambda_i\}
$$

$$
\mathrm{Top4}=\frac{\sum_{i=1}^{4}\lambda_i}{\sum_i\lambda_i}
$$

$$
\Delta x_t=x_{t+1}-x_t
$$

Recruitment breadth applies the participation formula to channel energies. For gait displacement, the same rank formulas use squared singular values of the uncentered matrix. Together the summaries distinguish dominant concentration, the high-fidelity tail, local movement and channel recruitment. Movement differences remain within each sequence.

Evidence availability. The companion collection provides source identities, authored derived tables, all thirteen figures, and analysis scripts. Original source recordings, provider tensors and participant observations remain at their source distribution channels.

## 2. Scoping observation — relation trajectory and execution trajectory are different failure surfaces

This line began with a deliberately odd comparison: formal thought disorder and intoxicated speech can both sound “disorganized,” but the observable failure may live in different parts of the trajectory. Published formal-thought-disorder examples can preserve local grammar while their proposition-to-proposition relation path drifts sharply. Alcoholized speech, by contrast, supplies many examples in which a target utterance is retained while local articulation, pausing, repair or timing changes. That contrast defined two separate measurement axes for the present study: relational/semantic trajectory and surface execution trajectory.

The scoping comparison defines two measurement axes for the experiments. It motivated the subsequent decision to treat language as a moving state and to ask exactly where an intoxication perturbation appears: in target identity, in local temporal movement, in recruitment breadth, or in the coordination that binds many output channels into one trajectory.

Evidence note. Source examples used in scoping include Elvevåg et al. (2010), Hinzen & Rosselló (2015), and Xu et al. (2025). The formal quantitative record below begins where matched numeric data are available.

## 3. LM-BASE-001 — Normal language and human movement share compact dominant spectra over broader tails

The baseline asks what geometry characterizes the reference language and movement representations before intoxication is introduced. The prior Data Zoo sensorimotor report measured human movement and natural-language predictive movement with the same spectral logic. The comparison is reused here as the baseline coordinate system.

Table 2. Reference geometry

| Domain | Representation | Stable rank | PR | d95 | Top-4 |
| --- | --- | --- | --- | --- | --- |
| Human motion | Angular-velocity movement, raw | 4.04 | 8.06 | 20 | 62.4% |
| Human motion | Angular-velocity movement, 5-frame smooth | 3.29 | 7.01 | 18 | 64.4% |
| Natural language | Character bigram teacher field | 2.48 | 4.34 | 13 | 77.4% |
| Natural language | L3 predictive-state movement | 4.08 | 9.24 | 20 | 55.1% |

Source: LM-BASE-001 baseline summary. Ranks and d95 are dimensionless; Top-4 is a percentage of the spectrum. Each row retains its own representation and preprocessing. L3 denotes the named predictive-state representation in the prior language record.

![Figure 1: Reference stable rank in the prior human-motion and natural-language representations (LM-BASE-001; Table 2). Each bar summarizes the specified representation; values near four describe dominant spectral concentration within that representation. Values are recorded point summaries.](figures/Figure_01.png)

Figure 1. Reference stable rank in the prior human-motion and natural-language representations (LM-BASE-001; Table 2). Each bar summarizes the specified representation; values near four describe dominant spectral concentration within that representation. Values are recorded point summaries.

The reference result supplies the scale distinction used throughout this report. Human motion and language can place much of ongoing change into a few dominant modes while retaining a substantially longer high-fidelity tail. In the raw human angular-velocity and L3 language movement representations, stable rank is approximately four but d95 is 20. The dominant movement core and the full represented state therefore need separate measurements.

## 4. INTOX-SPEECH-CAL-002 — Alcohol effects on speech are task-conditioned before geometry is measured

This calibration examines how the observed alcohol-related speech change depends on the speaking task. The Alcohol Language Corpus provides sober and intoxicated recordings from the same 162 speakers across read, spontaneous and command-and-control speech, with breath and blood alcohol measurements. A published 150-speaker disfluency analysis supplies a useful external calibration before the raw-matrix geometry experiment.

Table 3. Task-conditioned ALC disfluency summaries

| Measure | Read speech | Spontaneous speech | Command & control |
| --- | --- | --- | --- |
| Filled pauses | 0.28% → 0.42% | 2.23% → 2.50% | 0.50% → 0.60% (n.s.) |
| Unfilled pauses >50 ms | 21.44% → 27.46% | 22.81% → 24.00% | 18.12% → 18.24% (n.s.) |
| False starts | 0.31% → 0.38% | 1.19% → 1.15% (n.s.) | 0.59% → 0.82% |
| Repetitions | 0.31% → 0.33% (n.s.) | 0.72% → 0.46% | 0.028% → 0.029% (n.s.) |
| Word interruptions | 0.33% → 0.55% | 0.065% → 0.064% (n.s.) | 0.09% → 0.15% (n.s.) |
| Phone lengthening | 0.13% → 0.25% | 0.31% → 0.47% | 0.06% → 0.10% (n.s.) |
| Unfilled-pause duration | 172 → 205 ms | 367 → 402 ms | 256 → 265 ms (n.s.) |

Source: Schiel and Heinrich (2015), as transcribed in the supplied study. Values run sober → intoxicated. Filled-pause and phone-lengthening counts use syllable denominators; false starts, repetitions, word interruptions and unfilled pauses use word denominators. Durations are milliseconds. n.s. is the source’s nonsignificance label. The original analysis uses generalized linear models; these values are published summaries. See Table B for the three verified cell mappings.

### Primary-source annotation

Three cells in Table 3 have different row/column assignments in the primary publication. Table B records the verified mapping from Schiel and Heinrich (2015), Table 2, page 28. Both the study transcription and the primary-source values are visible so the calibration can be interpreted with the correct task and disfluency labels.

Table B. Verified ALC cell mapping

| Measure and task | Study transcription | Primary Table 2 |
| --- | --- | --- |
| Repetitions: command & control | 0.028% → 0.029% | 0.09% → 0.15% |
| Word interruptions: spontaneous | 0.065% → 0.064% | 0.028% → 0.029% |
| Word interruptions: command & control | 0.09% → 0.15% | 0.065% → 0.064% |

All three comparisons are labelled n.s. in the primary table. The task-conditioned interpretation remains applicable. Source: Schiel and Heinrich (2015), Table 2; author-hosted PDF listed in Reference 7.

The task interaction is the important result. In read speech, several interruption and timing measures increase together. Spontaneous speech shows a different mixture, including a decrease in repetition rate despite increases in some pauses and phone lengthening. Command-and-control speech changes much less. The data therefore support a state-perturbation interpretation whose observable disfluencies depend on the speaking task.

Evidence note. The ALC section supplies published calibration from a 150-speaker analysis. The KAISD experiment below supplies a separate acoustic matrix analysis. Source verification for the three flagged ALC cells is recorded immediately after Table 3.

## 5. INTOX-SPEECH-GEO-003 — Raw-matrix intoxicated-speech geometry

Research question. When speech is represented as a multichannel time trajectory, how does intoxication change the geometry of actual movement between adjacent acoustic states?

Data. The public KAISD project stores a held-out DataLoader containing two labeled source recordings after preprocessing. The saved object contains 103 mel-spectrogram segments: 52 sober and 51 intoxicated. Every segment is a 128-band × 345-frame matrix. The project preprocessing uses 22.05 kHz audio, 128 mel bands, 2048-point FFT, 512-sample hop and a per-segment image normalization before saving. The present analysis uses the saved held-out matrices directly rather than the project classifier.

Shared scaling and movement construction. All frames from both conditions were pooled only to estimate one mean and SD for each mel band. The same scaler was then applied to both states. State geometry is calculated over standardized frames. Temporal movement is calculated as the first difference within each segment; no artificial transition is inserted between two separate segments.

Interpretation note. Condition labels and recording identities are tied within this held-out pair. The calculations describe a condition-associated contrast in these recordings, together with within-recording timing structure. Segment resampling measures stability within that specimen; it does not create additional independent speakers.

Table 4. Pooled KAISD state and movement geometry

| Condition | Object | Stable rank | PR | d95 | Top-4 |
| --- | --- | --- | --- | --- | --- |
| Sober | State cloud | 1.897 | 3.416 | 42 | 70.18% |
| Intoxicated | State cloud | 2.144 | 4.252 | 49 | 64.07% |
| Sober | Temporal movement | 3.538 | 10.176 | 81 | 45.26% |
| Intoxicated | Temporal movement | 4.054 | 13.809 | 87 | 35.51% |

Source: INTOX-SPEECH-GEO-003 recorded pooled results. State = standardized frames; movement = within-segment first differences. Shared scaling uses frames from both conditions. Stable rank, PR and d95 are dimensionless; Top-4 is percent covariance energy. The specimen comprises two recordings and 103 segments.

![Figure 2: Pooled temporal-movement stable and participation ranks for KAISD (INTOX-SPEECH-GEO-003). The 52 sober and 51 intoxicated segments come from two source recordings. One shared band-wise scaler precedes within-segment differencing. Bars are pooled point estimates; both measures are higher in the intoxicated object.](figures/Figure_02.png)

Figure 2. Pooled temporal-movement stable and participation ranks for KAISD (INTOX-SPEECH-GEO-003). The 52 sober and 51 intoxicated segments come from two source recordings. One shared band-wise scaler precedes within-segment differencing. Bars are pooled point estimates; both measures are higher in the intoxicated object.

![Figure 3: Top-4 energy of pooled KAISD temporal movement (INTOX-SPEECH-GEO-003). Four leading covariance modes retain 45.26% of sober and 35.51% of intoxicated movement energy under the shared scaler. Bars are point estimates from the two-recording specimen.](figures/Figure_03.png)

Figure 3. Top-4 energy of pooled KAISD temporal movement (INTOX-SPEECH-GEO-003). Four leading covariance modes retain 45.26% of sober and 35.51% of intoxicated movement energy under the shared scaler. Bars are point estimates from the two-recording specimen.

### 5.1 Segment-level trajectory anatomy

Table 5. KAISD segment-level trajectory medians

| Median measure | Sober | Intoxicated | Direction |
| --- | --- | --- | --- |
| Movement stable rank | 3.542 | 4.365 | broader |
| Movement participation rank | 10.001 | 14.754 | broader |
| d95 | 67 | 72 | longer tail |
| Top-4 energy | 46.31% | 37.08% | less concentrated |
| Frame-step norm | 3.931 | 4.121 | larger steps |
| Adjacent-direction cosine | 0.301 | 0.281 | less directional persistence |
| Tortuosity | 105.05 | 117.75 | more winding |
| Movement-band breadth /128 | 121.74 | 116.98 | slightly narrower recruitment |

Source: INTOX-SPEECH-GEO-003 recorded segment medians, 52 sober and 51 intoxicated. Stable rank, PR, d95, cosine and tortuosity are dimensionless; step norm is in standardized acoustic coordinates. “Breadth /128” means an effective band count out of 128, not a normalized fraction: the values are 121.74 and 116.98. Top-4 is percent energy.

![Figure 4: Intoxicated-to-sober ratios of segment-level median trajectory measurements in KAISD (INTOX-SPEECH-GEO-003; Table 5). A ratio above one indicates an increase. Steps and tortuosity increase, while directional continuity and effective band recruitment decrease. Ratios compare the two sets of segment medians.](figures/Figure_04.png)

Figure 4. Intoxicated-to-sober ratios of segment-level median trajectory measurements in KAISD (INTOX-SPEECH-GEO-003; Table 5). A ratio above one indicates an increase. Steps and tortuosity increase, while directional continuity and effective band recruitment decrease. Ratios compare the two sets of segment medians.

The widening of temporal covariance occurs alongside a slight decrease in movement-band participation breadth. The two measurements locate different aspects of the change: slightly narrower band-energy recruitment accompanies less concentrated joint temporal motion across those bands.

### 5.2 Stability under segment resampling

Two hundred fifty deterministic 80% without-replacement segment subsamples were drawn independently within each condition. The 10th–90th percentile stable-rank interval is 3.491–3.601 for sober speech and 3.946–4.174 for intoxicated speech. Participation-rank intervals are 9.949–10.439 and 13.209–14.471. The two resampling bands remain separated under this segment-removal scheme. These intervals describe stability within the two source recordings.

### 5.3 Destructive controls

Frame-order control. Each segment retained its acoustic frames but their order was randomized before differencing. Across 30 deterministic replicates, median movement stable rank becomes 2.004 for sober and 2.190 for intoxicated speech. The stable-rank gap contracts from 0.516 in the real sequence to 0.186 after frame shuffling, a reduction of about 64%. The participation-rank gap contracts by about 80%. A large fraction of the observed condition separation therefore belongs to the real adjacency structure.

Cross-band coordination control. Each mel band retained its own within-band time series but was independently circularly shifted, breaking cross-band synchrony. Median stable rank rises to 85.37 for sober and 83.25 for intoxicated speech. The real 3–4-rank movement field therefore depends on strong coordination among many acoustic bands in both states. Intoxication broadens movement within a strongly coordinated acoustic signal.

![Figure 5: Stable rank of KAISD temporal movement under timing controls (INTOX-SPEECH-GEO-003; logarithmic vertical axis). Real-sequence values are pooled estimates; frame-order values are medians over 30 permutations. Independent band shifts give the recorded control medians, with replicate count unspecified in the evidence. These are point summaries. Timing controls broaden the interpretation from condition differences to within-signal coordination.](figures/Figure_05.png)

Figure 5. Stable rank of KAISD temporal movement under timing controls (INTOX-SPEECH-GEO-003; logarithmic vertical axis). Real-sequence values are pooled estimates; frame-order values are medians over 30 permutations. Independent band shifts give the recorded control medians, with replicate count unspecified in the evidence. These are point summaries. Timing controls broaden the interpretation from condition differences to within-signal coordination.

Evidence note. The 103 segments derive from two held-out source recordings. The supported statistical object is segment/time-series geometry within this held-out pair. Participant-level generalization constitutes a separate measurement layer.

## 6. INTOX-GAIT-GEO-004 — Controlled-drinking gait displacement and contextual branches

This reanalysis asks how strongly the alcohol-related gait displacements align across the four sex × walking-direction groups, and how much contextual variation remains around the shared direction.

Data. Gimunová et al. measured 100 healthy young adults, 50 women and 50 men, twice: sober at 0.00% BrAC and after controlled vodka administration at mean 0.11 ± 0.01% BrAC. Every participant completed forward and backward gait on a 100 Hz Zebris pressure platform. The source article reports mean and SD for twelve gait variables in all four sex × direction subgroups.

To reduce algebraic redundancy among gait-cycle percentages, the geometry retains six surface coordinates: foot rotation, stride length, step width, stride time, cadence and velocity. For each subgroup and coordinate, the intoxication displacement is standardized by the sober standard deviation, as defined below. The resulting 4 × 6 matrix is analyzed with an uncentered SVD because the origin represents zero displacement from the sober condition. The selected coordinates can still have biomechanical dependencies; the scaling and feature-removal analyses examine sensitivity to their representation.

$$
\Delta z=\frac{\mathrm{mean}_{0.11}-\mathrm{mean}_{0.00}}{\mathrm{SD}_{0.00}}
$$

Table 6. Standardized gait-displacement matrix

| Subgroup | Foot rot. | Stride len. | Step width | Stride time | Cadence | Velocity |
| --- | --- | --- | --- | --- | --- | --- |
| Female forward | +0.126 | +0.529 | +0.144 | +0.100 | −0.085 | +0.246 |
| Male forward | −0.012 | +0.253 | −0.046 | +0.111 | −0.086 | +0.167 |
| Female backward | −0.129 | +0.512 | +0.423 | 0.000 | +0.014 | +0.262 |
| Male backward | +0.189 | +0.019 | +0.210 | +0.182 | −0.196 | −0.075 |

Source: INTOX-GAIT-GEO-004 derived matrix. Values are signed intoxicated-minus-sober mean differences divided by the corresponding sober SD; positive values indicate an increase. The public matrix is rounded to three decimals. Each row is a subgroup mean contrast, with four rows in total; the source cohort has 100 participants. Selected coordinates retain biomechanical dependencies.

### 6.1 The perturbation family is strongly concentrated

The four subgroup displacement vectors have uncentered stable rank 1.286 and participation rank 1.592. The first common mode carries 77.73% of displacement energy; the first two modes carry 90.74%. The surface gait changes therefore contain a strong shared component alongside context-dependent subgroup responses.

![Figure 6: Uncentered singular-value energy spectrum of four standardized gait-displacement vectors (INTOX-GAIT-GEO-004; Table 6), derived from the published 100-participant study. The first mode contains 77.73% of the aggregate displacement energy. Bars show deterministic matrix-energy fractions.](figures/Figure_06.png)

Figure 6. Uncentered singular-value energy spectrum of four standardized gait-displacement vectors (INTOX-GAIT-GEO-004; Table 6), derived from the published 100-participant study. The first mode contains 77.73% of the aggregate displacement energy. Bars show deterministic matrix-energy fractions.

The first common axis is dominated by stride length (+0.802), step width (+0.421) and velocity (+0.395), followed by stride time (+0.120) and a small negative cadence loading (−0.095). Foot rotation contributes almost no common loading (+0.006), which is consistent with its more context-specific direction across subgroups.

![Figure 7: First right-singular-vector loadings for the gait displacement matrix (INTOX-GAIT-GEO-004). Loadings are dimensionless coordinates of a unit vector in the sober-SD-standardized feature basis. Its sign is oriented toward positive stride length. Bars describe a multivariable direction, with strongest weights on stride length, step width and velocity.](figures/Figure_07.png)

Figure 7. First right-singular-vector loadings for the gait displacement matrix (INTOX-GAIT-GEO-004). Loadings are dimensionless coordinates of a unit vector in the sober-SD-standardized feature basis. Its sign is oriented toward positive stride length. Bars describe a multivariable direction, with strongest weights on stride length, step width and velocity.

### 6.2 Shared displacement and contextual realization

Table 7. Pairwise gait-displacement cosines

| Pair of intoxication vectors | Cosine |
| --- | --- |
| Female forward vs. Female backward | 0.832 |
| Female forward vs. Male forward | 0.874 |
| Male forward vs. Male backward | 0.129 |
| Female forward vs. Male backward | 0.321 |
| Female backward vs. Male backward | 0.179 |

Source: INTOX-GAIT-GEO-004 recorded geometry. Cosines are dimensionless directional similarities between aggregate displacement vectors. A value near one indicates alignment. These are descriptive matrix comparisons.

The clearest branch is male backward gait. After projection onto the common first axis, the residual norm is 27.9% for female forward, 30.9% for female backward, 59.7% for male forward and 95.7% for male backward. If male backward is temporarily removed, the leading mode captures 88.46% of the remaining three displacement vectors and the three-row stable rank contracts to 1.130.

![Figure 8: Subgroup residual norm after projection onto the first gait singular direction (INTOX-GAIT-GEO-004). Each value is residual vector norm divided by that subgroup’s original norm, expressed as a percentage. The denominator differs by subgroup; these are norm ratios, rather than fractions of pooled squared energy. Male backward gait has the largest relative residual.](figures/Figure_08.png)

Figure 8. Subgroup residual norm after projection onto the first gait singular direction (INTOX-GAIT-GEO-004). Each value is residual vector norm divided by that subgroup’s original norm, expressed as a percentage. The denominator differs by subgroup; these are norm ratios, rather than fractions of pooled squared energy. Male backward gait has the largest relative residual.

The gait geometry combines a shared perturbation direction with context-dependent realization. Its unit of analysis is the subgroup-mean change: most energy across the four displacement vectors lies in a compact common family, with the largest residual concentrated in male backward gait. The participant-level variation underlying each group mean is a separate object of analysis.

Evidence note. The gait geometry is calculated from published subgroup means and sober SDs. It describes the geometry of four group-average alcohol displacements. Participant-level gait manifolds and BAC dose-response trajectories constitute a separate measurement layer.

## 7. INTOX-GAIT-ROBUST-005 — Robustness of the shared gait displacement

The robustness analysis examines how the concentration changes when a gait variable or subgroup is removed, when coordinate magnitudes are rescaled, and when correspondence between feature identities is broken.

This experiment reuses the 4 × 6 sober-SD displacement construction from 004. Its measurements concern the same four aggregate vectors. Six leave-one-feature-out SVDs, four leave-one-subgroup-out SVDs, row-unit and column-RMS scaling controls, a sign-only sensitivity analysis, exhaustive feature subsets, a 200,000-replicate feature-identity permutation null, and an exact orthogonal 2 × 2 sex × walking-direction decomposition were evaluated on that construction. Zero continues to represent no alcohol-induced displacement, so the SVD remains uncentered.

Precision and reproduction. The report-recorded results use the working-matrix precision described in the source evidence. The distributed 4 × 6 matrix has three decimal places. An independent rerun of the supplied script with 200,000 permutations and seed 20260927 yields Table C; the two result sets retain their distinct precision.

Table C. Original results and public-matrix reproduction

| Quantity | Report-recorded | Public-matrix rerun |
| --- | --- | --- |
| PC1 energy (%) | 77.73 | 77.7308 |
| Top-2 energy (%) | 90.74 | 90.7619 |
| Stable rank | 1.286 | 1.286492 |
| Shared energy (%) | 61.37 | 61.4039 |
| PC1 permutation p | 0.0275 | 0.027695 |
| Shared-factor permutation p | 0.0409 | 0.040895 |

Rerun: supplied gait script, three-decimal matrix, 200,000 permutations, seed 20260927. Empirical p = (upper-tail count + 1)/(200,000 + 1). Precision and randomization details apply to this rerun; rounded output is not a reconstruction of the full-precision working matrix.

### 7.1 Feature and subgroup sensitivity

A concentrated first mode remains after each single-coordinate removal. Across the six leave-one-feature-out fits, first-mode energy ranges from 60.65% to 82.44% and stable rank from 1.213 to 1.649. Stride length is the strongest individual contributor: deleting it produces the least concentrated five-feature matrix, yet the first mode still carries 60.65% of displacement energy. Removing foot rotation or step width instead increases first-mode energy above 82%.

Table 8. Leave-one-feature-out gait geometry

| Omitted feature | PC1 energy | Top-2 energy | Stable rank |
| --- | --- | --- | --- |
| Foot rotation | 82.44% | 92.61% | 1.213 |
| Stride length | 60.65% | 86.18% | 1.649 |
| Step width | 82.43% | 98.44% | 1.213 |
| Stride time | 80.41% | 91.32% | 1.244 |
| Cadence | 80.67% | 91.00% | 1.240 |
| Velocity | 76.37% | 90.27% | 1.309 |

Source: INTOX-GAIT-ROBUST-005 recorded results. Each fit retains four subgroup rows and five feature columns. Energy percentages use that reduced matrix’s squared singular values; stable rank is dimensionless. Fits are uncentered and descriptive.

![Figure 9: Leave-one-feature-out gait sensitivity (INTOX-GAIT-ROBUST-005; Table 8). Each bar is the first-mode share of squared displacement energy after omitting the named column and recomputing the uncentered SVD. The lowest recorded share is 60.65% after stride-length removal; all six fits retain a concentrated leading mode. The solid and dashed horizontal lines are full-six-feature benchmarks: observed PC1 energy (77.73%) and its permutation-null 95th percentile (75.82%). The reduced fits have different reference objects.](figures/Figure_09.png)

Figure 9. Leave-one-feature-out gait sensitivity (INTOX-GAIT-ROBUST-005; Table 8). Each bar is the first-mode share of squared displacement energy after omitting the named column and recomputing the uncentered SVD. The lowest recorded share is 60.65% after stride-length removal; all six fits retain a concentrated leading mode. The solid and dashed horizontal lines are full-six-feature benchmarks: observed PC1 energy (77.73%) and its permutation-null 95th percentile (75.82%). The reduced fits have different reference objects.

The same result survives a subgroup jackknife. Omitting female-forward, male-forward, female-backward or male-backward gait leaves first-mode energy between 73.28% and 88.46% and stable rank between 1.130 and 1.365. The concentration becomes strongest when male-backward gait is omitted, confirming the earlier observation that this condition is the largest contextual branch rather than the source of the common mode.

Table 9. Leave-one-subgroup-out gait geometry

| Omitted subgroup | PC1 energy | Top-2 energy | Stable rank |
| --- | --- | --- | --- |
| Female forward | 73.28% | 92.12% | 1.365 |
| Male forward | 79.49% | 93.88% | 1.258 |
| Female backward | 75.83% | 97.21% | 1.319 |
| Male backward | 88.46% | 98.47% | 1.130 |

Source: INTOX-GAIT-ROBUST-005 recorded results. Each fit retains three subgroup rows and six columns. Energy percentages use the reduced matrix’s squared singular values; stable rank is dimensionless. Fits are uncentered and descriptive.

![Figure 10: Leave-one-subgroup-out gait sensitivity (INTOX-GAIT-ROBUST-005; Table 9). Bars show deterministic first-mode energy for each remaining three-row matrix. The recorded range is 73.28–88.46%; concentration is greatest after male backward gait is removed. The horizontal line marks PC1 energy for the full four-subgroup matrix (77.73%).](figures/Figure_10.png)

Figure 10. Leave-one-subgroup-out gait sensitivity (INTOX-GAIT-ROBUST-005; Table 9). Bars show deterministic first-mode energy for each remaining three-row matrix. The recorded range is 73.28–88.46%; concentration is greatest after male backward gait is removed. The horizontal line marks PC1 energy for the full four-subgroup matrix (77.73%).

### 7.2 Magnitude, coordinate identity and the permutation null

Normalizing subgroup magnitude reduces the first-mode concentration while retaining a common direction. After every displacement vector is normalized to unit length, the first mode still carries 66.10% of directional energy and the first two carry 89.49% (stable rank 1.513). Equalizing the RMS magnitude of every feature reduces the first-mode share to 55.84% while leaving 90.25% in the first two modes (stable rank 1.791). A sign-only matrix is broader again, with 45.66% in the first mode and stable rank 2.190. The observed backbone therefore uses graded effect magnitude and common coordinate identity; the sign-only construction provides a broader reference.

Table 10. Gait scaling controls

| Construction | PC1 energy | Top-2 energy | Stable rank |
| --- | --- | --- | --- |
| Base sober-SD displacement | 77.73% | 90.74% | 1.286 |
| Row-unit normalized | 66.10% | 89.49% | 1.513 |
| Column-RMS equalized | 55.84% | 90.25% | 1.791 |
| Sign only | 45.66% | 76.02% | 2.190 |

Source: INTOX-GAIT-ROBUST-005 recorded controls. Row normalization gives each subgroup unit Euclidean length; column equalization divides by each feature’s root-mean-square magnitude across rows; sign-only retains signs and zeros. Energy is percent squared singular-value energy; stable rank is dimensionless.

The coordinate-identity control asks a sharper question. In each of 200,000 seeded permutation replicates, the six measured alcohol changes inside each subgroup are kept exactly as observed but their gait-feature labels are independently permuted. This destroys the possibility that stride length in one subgroup lines up with stride length in another while preserving each subgroup’s magnitude distribution. The null first-mode energy averages 60.51%; its 95th percentile is 75.82%. The observed 77.73% lies beyond that threshold, with empirical one-sided p=0.0275. The equivalent stable-rank test gives the same empirical tail probability: observed 1.286 versus a null mean of 1.690 and 5th percentile of 1.319.

Reference-distribution note. Feature permutations assess alignment of named coordinates within the observed matrix. The tail probability is conditional on that construction; participant sampling variability and a causal alcohol-effect test require a different reference distribution.

![Figure 11: Within-row feature-identity permutation distribution for gait PC1 energy (INTOX-GAIT-ROBUST-005). The histogram contains 200,000 recorded permutations. The solid line marks observed energy (77.73%); the dashed line marks the null 95th percentile (75.82%). The empirical upper-tail probability is 0.0275. The reference distribution conditions on the observed four-row matrix.](figures/Figure_11.png)

Figure 11. Within-row feature-identity permutation distribution for gait PC1 energy (INTOX-GAIT-ROBUST-005). The histogram contains 200,000 recorded permutations. The solid line marks observed energy (77.73%); the dashed line marks the null 95th percentile (75.82%). The empirical upper-tail probability is 0.0275. The reference distribution conditions on the observed four-row matrix.

### 7.3 Exact factorization: one shared push plus structured realization

The four rows form a complete 2 × 2 design: female/male × forward/backward. An orthonormal Hadamard basis therefore partitions the exact squared displacement energy into four components without fitting a statistical model: a shared alcohol displacement, a sex realization contrast, a walking-direction contrast and their interaction. The shared component carries 61.37% of total displacement energy. Sex-dependent realization carries 21.86%, walking direction 8.50%, and the sex × direction interaction 8.27%.

Table 11. Orthogonal gait-energy decomposition

| Orthogonal component | Displacement energy |
| --- | --- |
| Shared alcohol displacement | 61.37% |
| Sex realization | 21.86% |
| Walking-direction realization | 8.50% |
| Sex × direction interaction | 8.27% |

Source: INTOX-GAIT-ROBUST-005 recorded Hadamard decomposition. Fractions sum to 100% of the aggregate matrix’s squared Frobenius norm. Equal weighting is across the four subgroup rows. “Sex realization” denotes the female/male contrast in this design; all components are descriptive rather than participant-level variance estimates.

![Figure 12: Orthonormal 2 × 2 decomposition of the gait displacement matrix (INTOX-GAIT-ROBUST-005; Table 11). Shared, sex, walking-direction and interaction components partition total squared displacement energy: 61.37%, 21.86%, 8.50% and 8.27%. These are deterministic aggregate contrasts.](figures/Figure_12.png)

Figure 12. Orthonormal 2 × 2 decomposition of the gait displacement matrix (INTOX-GAIT-ROBUST-005; Table 11). Shared, sex, walking-direction and interaction components partition total squared displacement energy: 61.37%, 21.86%, 8.50% and 8.27%. These are deterministic aggregate contrasts.

The shared factor also persists across the six feature-removal analyses. Under the six feature jackknives, its energy fraction remains between 51.33% and 64.43%. In a second 200,000-replicate coordinate-identity null, the observed shared fraction of 61.37% exceeds the null 95th percentile of 60.35% (empirical one-sided p=0.0409). The explicit mean alcohol-displacement vector and the first SVD loading align at cosine 0.982, showing that the dominant singular direction is almost the same object as the direct common displacement across the four conditions.

In sober-SD units, the direct common displacement is +0.328 for stride length, +0.182 for step width, +0.150 for velocity, +0.098 for stride time, −0.088 for cadence and +0.043 for foot rotation. Stride length contributes 58.9% of the squared common-vector energy, but removing it still leaves a majority shared factor and a 60.65% first singular mode. This distinction is useful when reading the source paper: a variable such as foot rotation can be a strong subgroup-specific marker while contributing little to the displacement shared across every condition.

![Figure 13: Feature scores for the orthonormal gait contrasts (INTOX-GAIT-ROBUST-005). Rows are ordered female forward, male forward, female backward, male backward; the Hadamard transform uses coefficients ±1/2. Scores have sober-SD units. The shared coefficient is twice the four-row mean displacement. Bars show signed point values; stride length dominates the shared component and foot rotation is expressed mainly in contextual contrasts.](figures/Figure_13.png)

Figure 13. Feature scores for the orthonormal gait contrasts (INTOX-GAIT-ROBUST-005). Rows are ordered female forward, male forward, female backward, male backward; the Hadamard transform uses coefficients ±1/2. Scores have sober-SD units. The shared coefficient is twice the four-row mean displacement. Bars show signed point values; stride length dominates the shared component and foot rotation is expressed mainly in contextual contrasts.

Evidence note. INTOX-GAIT-ROBUST-005 establishes robustness and factorization of the published four subgroup-mean displacement vectors. The analyzed object is the aggregate 4 × 6 matrix: feature and subgroup sensitivity analyses, coordinate permutations and orthogonal contrasts all operate on those measured summary values. The result supports a shared group-level alcohol-displacement component with structured sex and task realization. Participant-level raw gait dynamics remain a distinct measurement layer beyond this aggregate construction.

## 8. Discussion — Perturbation geometry and realized trajectories

The working synthesis carries the nickname “The Magical Hypothesis.” It began from a striking resemblance: intoxicated speech sounds wobbly, intoxicated walking looks wobbly, and both involve nervous systems coordinating many degrees of freedom. The calculations turn that resemblance into a measurable question: how concentrated is the observed perturbation, and how broad is the trajectory generated within a particular output system?

The normal reference provides the first separation. Human movement and natural-language predictive movement both place a large share of moment-to-moment change into a compact dominant spectrum while retaining a substantially longer high-fidelity tail. In the specified representations, raw human angular-velocity movement and L3 language movement both sit near stable rank four while requiring 20 modes for 95% energy. The useful object is therefore an organized movement core embedded in a richer state space. That distinction becomes especially informative once alcohol is introduced as a perturbation.

The speech experiment shows what happens inside the local execution trajectory. Intoxicated temporal movement has higher stable rank and participation rank, a longer d95 tail, lower Top-4 concentration, slightly larger frame steps, weaker adjacent-direction persistence and greater tortuosity. At the same time, movement-band participation narrows modestly. The measured change is therefore a redistribution of joint temporal motion across a strongly coordinated acoustic system: similar channels continue to move together, but their local trajectory is less concentrated and more winding.

The destructive controls locate that result in the organization of the trajectory itself. Randomizing frame order removes most of the sober-intoxicated spectral separation, while independently shifting mel bands drives stable rank from the 3–4 range into the 80s in both conditions. Real adjacency and cross-band synchrony are therefore major pieces of the measured geometry. Intoxication broadens motion within the coordinated acoustic representation, while strong cross-band coordination remains the dominant organizing structure.

The gait experiments expose a complementary scale. Across female/male and forward/backward walking, four standardized alcohol-displacement vectors share a strong common direction: the first singular mode carries 77.73% of displacement energy. The result survives removal of every individual feature and every individual subgroup, survives normalization of subgroup magnitude, and remains stronger than the feature-identity permutation null. The common direction is also almost identical to the direct mean displacement vector, with cosine 0.982. The dominant axis is therefore a property already present in the measured family of alcohol-induced shifts.

The exact 2 × 2 factorization gives that family its cleanest anatomy. Shared alcohol displacement accounts for 61.37% of total standardized displacement energy, sex realization for 21.86%, walking direction for 8.50%, and sex × direction interaction for 8.27%. The largest nonshared structure is systematic sex-dependent realization. What first looked like one strange male-backward branch becomes part of a broader decomposition: one common push is followed by structured context-dependent realization.

### 8.1 Current integrated claim

The study supports five linked measurements. First, normal language and human movement combine a compact dominant movement spectrum with a longer faithful tail in their specified representations. Second, intoxicated speech in the KAISD raw-matrix specimen has a broader temporal movement spectrum, lower Top-4 concentration, lower adjacent-direction continuity and greater tortuosity. Third, destructive temporal and cross-band controls show that this speech geometry is built from real temporal order and strong multichannel coordination. Fourth, the 100-person controlled-drinking gait summaries form a narrow group-level displacement family with one dominant common direction. Fifth, the dedicated robustness campaign shows that this gait backbone survives coordinate and subgroup sensitivity analyses and partitions into a 61.37% shared component plus structured sex, direction and interaction realization. Together these measurements motivate The Magical Hypothesis as a cross-domain working architecture: a compact state shift can be followed by richer output-specific dynamics.

### 8.2 The hand that pushes the system may be simpler than the path that follows

The strongest synthesis from the measured objects is a separation between perturbation geometry and realization geometry. In the gait summaries, most standardized alcohol-displacement energy belongs to a shared component, while the remaining energy is organized into sex, direction and interaction branches. In speech, intoxication broadens the local temporal movement field while the acoustic channels remain strongly coordinated. These are two different output systems, but they point to the same organizational possibility: a relatively compact state perturbation can enter a coordinated system and then be unfolded by that system’s own local dynamics.

This separation changes how visible complexity should be read. A broad symptom vocabulary can be generated from a smaller control object when the downstream system contains multiple context-dependent realization paths. Gait provides the clearest aggregate example: one common push accounts for most measured displacement energy, yet the observable surface differs across sex and walking direction. Speech provides the complementary dynamic example: the measured trajectory becomes broader and more tortuous while cross-band coordination remains strong. In these measurements, surface complexity and perturbation complexity are distinct empirical objects.

### 8.3 A common language for different output systems

The comparison across language, speech and gait operates at the level of organization. The shared vocabulary is the geometry of change: dominant movement spectrum, high-fidelity tail, perturbation concentration, trajectory continuity, tortuosity, recruitment breadth, multichannel coordination and the energy assigned to contextual branches. These quantities allow different systems to be compared without forcing their physical coordinates into one space. Speech contributes time-resolved local execution geometry; gait contributes an explicit decomposition of a measured alcohol-displacement family. Their relationship lies in how a perturbation is organized and realized.

This perspective also clarifies the role of the normal reference. The compact dominant movement spectrum observed in both language and human motion is a control-structure measurement embedded in a richer represented state. Alcohol then reveals two ways that structure can be reorganized: local movement can spread across more temporal directions, as in the speech specimen, while the state shift across contexts can remain concentrated around a shared backbone, as in the gait summaries. Together these measurements motivate the hypothesis that a perturbation can be compact at one level and dynamically expansive at another.

### 8.4 Closing statement

Across this study, alcohol-related comparisons provide a probe of how complex biological output systems organize change. The experiments establish three layers of evidence: a compact dominant movement spectrum over richer tails in the normal reference; intoxication-related broadening and increased tortuosity in local speech movement while coordination remains strong; and a robust common alcohol-gait displacement component followed by structured sex- and task-dependent realization. These layers motivate the cross-domain working architecture: compact perturbation → output-system-specific dynamics → diverse observable symptoms.

The central hypothesis can be stated simply: the hand that pushes the system may be simpler than the path that follows. In the measured gait object, that hand appears as a 61.37% shared displacement component; in the measured speech object, the realized acoustic path appears as a broader and more tortuous local temporal trajectory. The Language–Movement Integrated Study therefore closes with a concrete distinction between the geometry of a perturbation and the geometry of its realization, and with a measurement vocabulary that can carry that distinction across very different data domains.

## 9. Evidence ledger

Table 12. Evidence ledger

| ID | Evidence object | Supported statement |
| --- | --- | --- |
| LM-BASE-001 | Prior language record + Data Zoo 02 calculations | Normal language and human movement show compact dominant movement spectra over broader representational tails. |
| INTOX-SPEECH-CAL-002 | ALC 150-speaker published disfluency statistics | Alcohol-related speech changes depend strongly on speech task and do not reduce to one universal disfluency direction. |
| INTOX-SPEECH-GEO-003 | 103 KAISD held-out mel segments, direct matrix calculation | Intoxicated acoustic movement is broader and more tortuous under the shared scaler; real adjacency contributes strongly to the condition gap; real low rank depends on cross-band coordination. |
| INTOX-GAIT-GEO-004 | 100-person 0.00→0.11% BrAC published gait summaries, derived 4×6 displacement matrix | Four subgroup alcohol-displacement vectors are dominated by one common mode, with a large male-backward residual branch. |
| INTOX-GAIT-ROBUST-005 | 004 4×6 gait-displacement matrix; deterministic robustness and factorization campaign | The common gait perturbation survives feature/subgroup jackknives and a feature-identity null. Exact 2×2 factorization assigns 61.37% of displacement energy to the shared alcohol component, 21.86% to sex realization, 8.50% to direction, and 8.27% to interaction. |
| The Magical Hypothesis | Cross-domain synthesis after the above calculations | A comparatively narrow intoxication perturbation may be realized through output-specific local dynamics; the current gait evidence supports a robust shared push plus structured contextual branches, while speech shows broadening of local temporal movement in the measured specimen. |

Experiment IDs link to the companion evidence index. Recorded speech results concern a two-recording specimen; gait results concern four group-mean vectors. The final row is a cross-domain working hypothesis.

## 10. Practical measurement checklist

1. Define the object and independent unit. Record whether rows are participants, recordings, segments, time frames or subgroup summaries. The present speech geometry is a two-recording specimen; the gait geometry has four aggregate rows.

2. Fix the representation and scaling. Record feature definitions, units, segment length, filtering, normalization and the reference population used by each scaler. The speech scaler is a descriptive pooled transform; predictive evaluation requires training-fold scaling.

3. Preserve sequence boundaries and coordinate identities. Compute first differences within a recording or segment, and retain matching feature definitions across conditions. State what each randomization preserves and breaks.

4. Report complementary summaries. Present stable rank, participation rank, a cumulative-energy threshold, leading-mode energy and the relevant trajectory or recruitment measures. Relate each number to its own mathematical object.

5. Examine representation sensitivity. Use feature and subgroup removal, row and column scaling, and explicit reference permutations. Keep matrix-energy robustness separate from sampling uncertainty across people or recordings.

6. Make the calculation inspectable. Publish authored derived matrices, result tables, figure captions, source identities, random seeds and software requirements. Label original reported precision and rerun precision, and identify the independent units required for the intended generalization.

These steps operationalize the measurements in this study. A participant-level validation study requires its own sampling design and independent participants; this report supplies a measurement method and its present evidence objects.

## 11. References and source identities

1. Data-Oriented Modelling. The Language Edition, language research record v1.6, 27 September 2026. Related publication: Language Structure and Control Geometry, Chapter 4 Data Zoo, Subreport 01, English edition v1.0. https://github.com/walkingrui-bot/Data-Oriented-Modelling-Reports/tree/main/Chapter_4_Data_Zoo/Language_Structure_and_Control_Geometry

2. Data-Oriented Modelling. Human Learning and Sensorimotor Geometry. Chapter 4 Data Zoo, Subreport 02, English edition v1.0, 27 September 2026. https://github.com/walkingrui-bot/Data-Oriented-Modelling-Reports/tree/main/Chapter_4_Data_Zoo/Human_Learning_and_Sensorimotor_Geometry

3. Elvevåg B, Foltz PW, Rosenstein M, DeLisi LE. An automated method to analyze language use in patients with schizophrenia and their first-degree relatives. J Neurolinguistics. 2010;23(3):270–284. doi:10.1016/j.jneuroling.2009.05.002.

4. Hinzen W, Rosselló J. The linguistics of schizophrenia: thought disturbance as language pathology across positive symptoms. Front Psychol. 2015;6:971. doi:10.3389/fpsyg.2015.00971.

5. Xu W, Pakhomov S, Heagerty P, et al. Perplexity and proximity: Large language model perplexity complements semantic distance metrics for the detection of incoherent speech. J Biomed Inform. 2025;170:104899. doi:10.1016/j.jbi.2025.104899.

6. Schiel F, Heinrich C, Barfüßer S, Gilg T. ALC – Alcohol Language Corpus. Proc LREC. 2008. https://aclanthology.org/L08-1502/

7. Schiel F, Heinrich C. Disfluencies in the speech of intoxicated speakers. Int J Speech Lang Law. 2015. Primary Table 2: https://www.bas.uni-muenchen.de/forschung/publikationen/IJSLL_SchielHeinrich_2015.pdf

8. KAISD (Korean language Alcohol Intoxicated Speech Detector). vilotgit/kaisd, 2020. Public GitHub repository and linked Google Drive held-out object. https://github.com/vilotgit/kaisd

9. Gimunová M, Bozděch M, Novák J, Vojtíšek T. Gender differences in the effect of a 0.11% breath alcohol concentration on forward and backward gait. Sci Rep. 2022;12:18773. doi:10.1038/s41598-022-23621-y.

### Research notice

Some hypotheses developed in this research have received substantive validation through engineering implementations. Data models are forthcoming.
