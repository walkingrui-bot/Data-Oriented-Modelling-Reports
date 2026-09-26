## 49 Controlled validation across neural statistical and mathematical systems

Research ID: ML-EPIDEMIOLOGY-VALIDATION-20260926-002. The completed second campaign constructs matched validation conditions for the main claims, including three miniature architectures, four textual sources, finite-state constructions and measured stopping costs. The source is evidence/replications/validation/REPORT_ORIGINAL.md; CLAIM_COVERAGE_ORIGINAL.md maps the historical chapters to V00–V14. The completed supplementary report takes chronological precedence over the earlier review snapshot.

### 49.1 Learning history changes continuous response fields

V04 branches from nine parent micro-models using identical data, learning rate and update count, with AB versus BA training order. It covers 27 pairs and 54 branches. Fifty branches completed; four produced nonfinite loss from the same previously unqualified Transformer parent at larger learning rates. Twenty-three pairs preserve correct complete endpoints in all three task modes. At the prespecified learning rate 3, parameter and output changes exceed the chosen tolerance in 3/3 GRUs, 2/3 Transformers and 3/3 Mambas. A follow-up audit of 128 common successor programs gives identical native discrete predictions in all 23 qualified pairs.

[REPRODUCED] Learning order changes continuous response fields and confidence under matched starting state, examples and budget. The follow-up separates this measurable effect from discrete prediction changes on the chosen program set.

V12 holds weights fixed and edits the actual Adam first or second moments before one common training update. All pre-intervention weights and outputs coincide. Zeroing first moments changes the subsequent answer margin in 9/9 models; 8/9 retain full-task correctness, with the remaining parent already unqualified. Nine restoration controls recover parameters and outputs exactly. Zeroing second moments produces large updates and widespread damage, identifying the role of adaptive preconditioning. The demonstrated state dependence concerns the next learning step.

### 49.2 Control energy concentration and finite interventions

V08 measures nine 64 × 48 input-control Jacobians in the same 64 successor-observation coordinates. All have concentrated spectra: 3–6 modes account for 95% of energy, and the first three carry approximately 83–97%. The first linear input map has full column rank in all nine models. Weak local directions still affect output under finite interventions, with particularly visible nonlinear departures in Mamba.

An explicit rank-three linear-bottleneck control keeps output change within approximately 3 × 10^−15 at intervention amplitude 10. This calibration distinguishes exact linear silence in the constructed bottleneck from low local sensitivity in the neural measurements.

V06 aligns seeds through answer-response fields for common questions and successor programs. Principal-direction angles are approximately 6.5–8.8° for Transformer, 41–65° for GRU and 19–37° for Mamba, with corresponding energy spectra recorded. An invertible orthogonal change of hidden basis alone produces raw angles of 61–85°; inverse transformation restores the slice to machine precision. Functional alignment supplies the appropriate common coordinates for cross-seed interpretation.

[REPRODUCED] A few modes carry much of the measured control energy across three architectures. Exact rank, 95%-energy dimension, stable rank and finite-amplitude sensitivity are distinct readouts.

### 49.3 Feedback resolution transfers teacher geometry across architectures

V09 trains 81 students: three known teacher ranks, three world seeds, three student architectures and three feedback channels. Each run uses 800 updates, matched training counts and paired initialization. A common binary cross-entropy objective and matched initial full-training-set gradient norms at zero logits reduce initial loss-scale differences.

| Architecture | Feedback | Mean test bit accuracy | Jacobian energy in teacher subspace | Models reaching 95% accuracy |
| --- | --- | --- | --- | --- |
| GRU | Hard labels | 90.95% | 83.55% | 1/9 |
| GRU | Two confidence bins | 95.18% | 95.00% | 6/9 |
| GRU | Continuous probability | 98.74% | 99.70% | 9/9 |
| Transformer | Hard labels | 92.63% | 87.54% | 0/9 |
| Transformer | Two confidence bins | 93.32% | 89.69% | 1/9 |
| Transformer | Continuous probability | 98.68% | 99.12% | 9/9 |
| Mamba | Hard labels | 88.87% | 82.62% | 0/9 |
| Mamba | Two confidence bins | 90.98% | 74.92% | 0/9 |
| Mamba | Continuous probability | 98.93% | 99.64% | 9/9 |

[REPRODUCED] Continuous probability feedback improves accuracy in 27/27 paired comparisons and recovers the teacher's rank as Jacobian r95 in 27/27 models, for the tested ranks 2, 4 and 6. Two-bin feedback increases teacher-subspace energy in 17/27 comparisons, showing an architecture-dependent response.

For each of nine worlds, a full-rank-eight perturbation teacher reproduces the same hard labels and two-bin confidence values on all 512 training examples. Continuous logits allow linear recovery of the original teacher. This constructive witness establishes that those finite discrete traces admit multiple exact teacher ranks. Effective-dimension estimates retain their separate statistical interpretation.

### 49.4 Function level structure is reproduced on independent text segments

V03 uses the original technical corpus and three further works: Alice's Adventures in Wonderland, The Adventures of Sherlock Holmes and On the Origin of Species. Continuous segments define train, development and test sets. Counts, state representation, PCA and operators are fitted using training segments. Contexts stay within segment boundaries. A separate analysis holds out an entire work.

[REPRODUCED] State-dependent update functions lower test distribution MSE on all four sources. They also improve observed character log-score within each of the three additional works. This is direct evidence that useful function-level structure can be reconstructed through a statistical representation independently of the original neural implementation.

| Source | Test segments | Log-score gain over reset | Conditional segment bootstrap 95% interval |
| --- | --- | --- | --- |
| Alice | 2 | +0.0381 | [+0.0362, +0.0401] |
| Sherlock Holmes | 8 | +0.0487 | [+0.0416, +0.0539] |
| Darwin | 8 | +0.0174 | [+0.0032, +0.0306] |
| Original technical corpus | 7 | −0.0299 | [−0.0501, −0.0086] |

The intervals condition on the fitted model and correlated segments within a work. The original technical corpus's character log-score decreases despite its MSE improvement. In the leave-one-work-out evaluation, all four log-score gains are negative. The demonstrated predictive advantage is therefore within-source and metric-specific.

Bigram fields have stable ranks approximately 2.27–2.53 and r95 of 8–11. IID residual absolute energy is approximately 0.14–0.36% of the real-corpus energy. Word-order shuffling largely retains bigram energy and operator prediction performance, tying this assay primarily to local statistical transitions.

Directly fitted two-token operators outperform products of separately fitted one-token operators on every source, with matched test denominators:

| Source in report order | Direct two-token MSE | Composed one-token MSE |
| --- | --- | --- |
| Alice | 0.1260 | 0.1411 |
| Sherlock Holmes | 0.1065 | 0.1196 |
| Darwin | 0.1435 | 0.1672 |
| Technical corpus | 0.1630 | 0.1909 |

The ten-dimensional affine operators generate an unrestricted linear algebraic envelope of dimension 111, saturating the available affine envelope. Two-token residuals relative to this envelope are at numerical precision. A comparison with a grammar-, length- or path-constrained composition set is a distinct operator test. The current results establish useful fitted updates and directly measured composition error.

### 49.5 Training material changes the learned predictive function

V14 starts with three architectures and three parent seeds trained on technical corpus A. Each parent continues either on A or for the same number of updates on Alice corpus B, inheriting identical parameters and Adam state. The campaign records 10,800 updates across the parent and successor stages.

In 9/9 paired comparisons, switching to B lowers held-out B-text NLL and raises held-out A-text NLL. Probability fields differ on all nine comparisons over 64 common prompts. B-text NLL after switching is approximately 1.90–1.93 for GRU, 2.07–2.11 for Transformer and 1.80–1.84 for Mamba; continuing A gives approximately 2.68–2.69, 2.68–2.75 and 2.75–2.80.

[REPRODUCED] With equal additional training and a common parent state, changing the material changes the predictive function across all three architectures. These nine model pairs test two specified textual sources.

### 49.6 Exact state counts and constructive mathematics

The original 021 system has 275 legal states and 11 actions. Refining future-response partitions gives the following exact sequence, independently recalculated for this release from the archived transition definitions:

| Maximum future program length | 0 | 1 | 2 | 3 | 4 | 5 | 6 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Distinguishable classes | 5 | 65 | 105 | 173 | 258 | 275 | 275 |

[CONFIRMED] The original 173-class count is exact for the horizon through three steps. The stable full-future partition contains 275 classes, giving a minimum of 275 distinguishable persistent states, or nine bits under fixed-length binary encoding. Relative to the 25 visible goal–main states, the class-count ratio is 11 and log2(11)=3.459. This is a count-based capacity comparison.

A four-step distinguishing witness uses states (1,0,5,3) and (1,0,2,3). All programs of length at most three give equal outputs; R+1 → R+2 → COMPARE → CORRECT gives final outputs 2 and 1. Chapter 34 and its state-count figure now use the corrected horizon labels.

V10 compiles the same finite system into a ReLU transition implementation with one persistent scalar. All 3,025 single-step transitions and 275 readouts have zero error, as do 1,000 programs of length 32. Exhaustive transitions and closure of the legal integer states support induction over any finite program. The compiler uses 273 ReLU nodes and 3,300 fixed coefficients. Information capacity and the number of Euclidean state coordinates are thereby separated explicitly.

V02 constructs a four-state process in which two states share a next-token distribution and diverge after receiving the same token. V02b augments the representation with two-token future signatures, distinguishes all four states, fits the update maps and passes exhaustive tests through six steps. This supplies an executable sufficient-state construction.

V11 checks 20 numerical worlds. The exact quadratic-loss SGD order identity has error at most 5.36 × 10^−16; smooth nonlinear second-order approximations have a remainder declining approximately cubically with step size; readout path-integral identities have error at most 2.71 × 10^−16. These calculations validate the specified differential and integral relations.

### 49.7 Calibration separates readable information from causal use

V02 creates, in 20 orthogonal coordinate systems, worlds where a comparison bit is readable and used and worlds where the same bit is readable and stored. Probes decode the bit in both. Targeted intervention changes the designated readout only in the used-bit world; the independent readout control is preserved. Known closure worlds and worlds with a specified external generator also pass residual, removal and restoration checks.

These are 40 comparison worlds and 40 closure worlds with known structure. Their role is instrument calibration for causal interpretation. V07 completed the instrument precheck; the completed report records its official-model scientific surgery at the qualification stage.

### 49.8 Task adaptation and complete qualification denominators

V01 adapts the full official Pythia-70M and Mamba-130M backbones with trainable low-rank parameters and a shared eleven-symbol task interface. Three initializations per backbone complete 3,000 updates each, totalling 18,000 updates. Six restored final adapters match reference logits exactly. The split contains 176 training, 80 development and 336 sealed test questions. Relation traces exclude the final answer and support normal ANSWER requests at different budgets.

The prespecified development gate requires at least 95% complete-chain correctness and 99% syntax correctness. Complete-chain development scores of the six adapters range from 0% to 3.75%; all six retain their recorded qualification status and the test set stays sealed for them.

V13 trains three miniature architectures from scratch with three seeds each on the same task and split. Nine initial 4,000-update runs are followed by an already-started 6,000-update extension for each model using the original training set. Two of nine final models pass the frozen development gate: GRU 2731 reaches 96.25% complete-chain correctness and 100% syntax, and GRU 2732 reaches 100% on both. The other seven model outcomes remain in the campaign denominator. These qualifications determine entry to the independent test below.

### 49.9 Independent questions and measured stopping costs

The 336 sealed test questions comprise 80 unseen six/eight-bit combinations and 256 unseen ten/twelve-bit lengths. Only the two development-qualified models enter this evaluation; thresholds and model selection remain fixed afterward.

| Test result | GRU 2731 | GRU 2732 |
| --- | --- | --- |
| Six/eight-bit complete CoT accuracy | 96.25% | 100% |
| Six/eight-bit stopped requested-answer accuracy | 98.75% | 100% |
| Six/eight-bit full relation steps → selected steps | 2.80 → 2.4625 | 2.80 → 0 |
| All 336 stopped requested-answer accuracy | 41.96% | 97.02% |
| All 336 development-calibrated fixed-depth accuracy | 69.94% | 97.02% |
| All 336 Direct complete-output accuracy | 100% | 100% |

[REPRODUCED] In GRU 2731, six of the 64 unseen eight-bit questions have disconnected immediate-readiness sets with the answer-bearing final relation removed from the task. This extends the phenomenon to unseen combinations under a task without final-relation answer leakage. Both models' autonomous full CoT syntax fails on the ten/twelve-bit lengths, and their Direct mode scores 100% across all test lengths. These measurements specify the successful routes and the observed extrapolation behavior.

Service timing includes prefix processing, state classification, the answer request and end-token prediction. Thirty-two predetermined test questions are timed in three rotating strategy rounds. The implementation uses CPU full-prefix recomputation. Answers and chosen depths agree with the independent readout table; all timed end-token predictions are correct.

| Model | Full budget | Calibrated fixed depth | State stopping | Measured comparison |
| --- | --- | --- | --- | --- |
| GRU 2731 | 1.248 ms | 1.071 ms | 1.296 ms | State stopping is 3.9% slower than full budget and 21.0% slower than fixed depth |
| GRU 2732 | 1.304 ms | 0.512 ms | 0.542 ms | State stopping is 58.4% faster than full budget and 5.8% slower than fixed zero depth |

[CONDITIONAL] Step reduction, answer accuracy and actual elapsed cost are now measured separately. GRU 2731 improves within-length requested-answer accuracy with fewer relation steps; the timed implementation favors its calibrated fixed policy. GRU 2732 obtains the same answers with its state rule and fixed zero-depth rule, with the fixed rule taking less time. These measurements define the deployment-relevant comparison for this campaign.

### 49.10 Record integrity and source availability

The completed report preserves the full training and qualification counts, the four V04 interrupted branches, the sampler-recovery description and the distinction between independent training and new measurements on existing models. Dedicated sampler state is recorded for the newer V13/V14 states. Its protocols, JSON outputs, logs and checkpoints are catalogued in REPLICATION_SOURCE_MAP.csv. The attached terminal reports and review are included verbatim; their separately referenced raw files retain a report-linked availability status.

