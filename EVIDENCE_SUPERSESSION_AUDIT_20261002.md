# Evidence Supersession Audit — 2026-10-02

Scope: Chapters 1–5 of **Data-Oriented-Modelling-Reports**, checked against the research record completed through 2 October 2026.

This audit preserves executed numerical results and distinguishes four update types:

- **SUPERSEDED INTERPRETATION** — later experiments support a different interpretation of the same earlier observations.
- **SCOPE UPDATE** — the earlier result remains valid, while its generalization is now narrower.
- **EVIDENCE ADVANCED** — a hypothesis or proposed interface has received later experimental support.
- **CURRENT** — no substantive contradiction was identified.

The purpose is to keep historical experiments intact while preventing earlier interpretations from being read as the current project position.

---

## Chapter 1 — Language Models Fit the Function That Generates the Answer

Primary text: `Chapter_1_Language_Models_Fit_the_Function_That_Generates_the_Answer/report_text/LLM_Activity_Report_EN.md`

### 1.1 §6, “The model writes something. Then it meets what it wrote.”

**Status: SCOPE UPDATE**

The report correctly identifies self-written text as a memory/control surface and correctly anticipates long-chain drift. The sentence

> “More running time lets a rule form, and then lets it keep changing.”

now requires a state-conditional interpretation.

Later controlled reasoning experiments show that answer readiness can be present at depth 0, can be lost after an additional step, and can reappear after further actions. In the 027 series, readiness sets are frequently disconnected. Active recovery outperforms passive continuation, and repeated append-only rescue is strongly non-monotonic.

**Current interpretation:** extra computation is an action on predictive state, not a monotonic resource. Its value depends on the current state, the selected operation and whether the trajectory is already inside an answer-ready region.

### 1.2 Opening thesis and §7, “Freeze the weights. Watch the rule move.”

**Status: SCOPE UPDATE**

The central “effective generative function” framing remains a working hypothesis and is compatible with later evidence. Later direct-answer, stopping and recovery experiments sharpen one point: useful rule/state organization can already be present before an explicit reasoning chain is generated.

**Current interpretation:** explicit reasoning is one observable and reinjectable control trajectory through a predictive state space. It is neither the unique route by which an answer-generating state forms nor a quantity whose benefit is determined by length alone.

### 1.3 §16, “Get hold of the generator.”

**Status: EVIDENCE ADVANCED**

The later 027A–027E and ASTIG studies turn the proposed observation/control programme into a more explicit hierarchy: stop when ready; bypass a risky edge when a safe local alternative exists; traverse toward a nearby answer-ready region; reconstruct state when local traversal is insufficient; use append-only rescue only under immediate verification.

On 125 canonical correct-to-wrong exits, the assembled hierarchy routes 15 to preventive bypass, 108 to local recovery and 2 to reconstruction, with successful immediate readiness recovery for all 125. The corresponding held-out foundation subset contains 60 events and recovers all 60.

---

## Chapter 2 — Language Models: Motor Control and Deep-Space Drift

Primary text: `Chapter_2_Language_Models_Motor_Control_and_Deep_Space_Drift/report_text/Dynamic_Generative_Rule_Fitting_Phase2_EN.md`

### 2.1 §§8–12, mirror stabilization and adaptive control

**Status: SCOPE UPDATE**

The mirror and center-estimation experiments remain valid demonstrations in their constructed systems. Later pretrained-model experiments establish a distinct natural-model result: a late residual-stream TEXT/ACT control interface exists in the tested Qwen2.5-1.5B-Instruct model, but the induced correction is locally fragile.

MODE-CONTROL changes 9/59 over-action cases at dose −1 and 18/59 at dose −2 at block 23. An equal-norm opposite intervention at blocks 24–26 reverses all nine dose −1 corrections.

**Current interpretation:** causal control directions can be locally real while commitment remains weak downstream. The constructed long-run stabilizers in Chapter 2 should be read as demonstrations of control mechanisms, not as evidence that the same stability property already holds in a natural pretrained LLM.

### 2.2 §14, “Take the instruments to a natural LLM.”

**Status: EVIDENCE ADVANCED**

The proposed programme has now been partially executed. Layerwise mode readability and direct residual-stream intervention have been measured in a fixed pretrained model. The later result supports a selective first-action control interface while also quantifying its susceptibility to downstream counter-intervention.

---

## Chapter 3 — Machine Learning Epidemiology / reasoning-state studies

Primary texts:
- `Chapter_3_Machine_Learning_Epidemiology/Research_Report/REPORT_EN.md`
- `Chapter_3_Machine_Learning_Epidemiology/How_Language_Models_Reach_an_Answer/REPORT_EN.md`

### 3.1 §§44–45, stopping geometry

**Status: EVIDENCE ADVANCED**

No retraction is required. The state-dependent stopping result is strengthened by the later recovery hierarchy.

The earlier report separates answer readiness from scalar confidence and shows disconnected readiness sets. The later 027A–027E sequence extends the action space from **answer / continue / stop** to **stop / bypass / bounded traversal / state reconstruction / verified rescue**.

Repeated generic rescue is explicitly non-monotonic, reinforcing the earlier conclusion that continued reasoning is a state transition decision rather than a fixed-depth policy.

### 3.2 §50.2, “The framework transfers to natural reasoning in pretrained language models”

**Status: SCOPE UPDATE / EVIDENCE ADVANCED**

The claim should remain narrower than a full transfer claim. Later Qwen experiments provide direct pretrained-model evidence for first-action mode geometry and causal intervention, while full multi-step reasoning control remains a separate evidence level.

A suitable current wording is: **pretrained-model transfer is established for a local first-action control interface in the tested cohort; broader reasoning-controller transfer remains a separate target.**

---

## Chapter 4 — Data Zoo

### 4.1 Subreport 01 — Language Structure and Control Geometry

Primary text: `Chapter_4_Data_Zoo/Language_Structure_and_Control_Geometry/REPORT_EN.md`

**Status: SCOPE UPDATE**

The report’s distinction between broad sentence state space and narrow local movement remains compatible with later work. The later multiscale generation series adds an important qualification: low-dimensional local movement does not by itself identify a unique privileged set of observation scales or determine the generator architecture.

Later loss-design experiments show that future consequence and useful training intervention are state- and horizon-dependent. EXP019 gives a positive late-training intervention: held-out high-gain improvements across future bands 1 / 2 / 3–4 / 5–6 / 7–10 are +0.03575 / +0.02990 / +0.03551 / +0.01452 / +0.00422, with the first four confidence intervals excluding zero. EXP021 supplies a preregistered null: all three intervention windows are vetoed and the run exactly matches baseline (NLL 4.6071796417; maximum targeted held-out loss delta 0).

EXP022 then measures cross-band interactions at step 350 and α = 0.03125. Across three panels, 15/50, 15/50 and 17/50 interaction cells are significant. The full response remains almost additive (additive-control correlation 0.9973–0.9991; 95.8–98.1% response energy retained), while the interaction residual is concentrated: its top two SVD axes explain 92.93% and its participation ratio is 1.79. Eight of fifteen stable interactions spill outside their source pair.

**Current interpretation:** language contains multiple future-relevant scales whose useful interventions and cross-scale interactions depend on prediction horizon and training state. Descriptive low-rank transition geometry is a measurement target, not a fixed architecture prescription.

The multiscale line is complete through **EXP022**; EXP023 is in progress as of this audit.

### 4.2 Subreport 02 — Human Learning and Sensorimotor Geometry

**Status: CURRENT**

No substantive contradiction was identified. The report already separates raw dimensionality, active selection width, recruitment breadth and dominant temporal rank, and explicitly keeps the sensorimotor-reuse explanation at hypothesis level.

### 4.3 Subreport 03 — Language–Movement Integrated Study

**Status: CURRENT**

The report already includes INTOX-GAIT-ROBUST-005 and correctly separates measured speech/gait objects from the cross-domain working hypothesis. No later result currently requires retraction of the numerical gait or acoustic findings.

### 4.4 Subreport 04 — Genomic Predictive Geometry and Model Capacity

**Status: CURRENT**

The report already records the whole-genome/transcriptome GEUVADIS × 1000 Genomes study as a protocol-only extension and separates predictive geometry, sample-supported predictive geometry and estimator calibration. The later research record does not yet justify changing that protocol-only status.

---

## Chapter 5 — Data-Oriented Modelling

### 5.1 Report 01 — Heterogeneous Data and General Data Intelligence

Primary text: `Chapter_5_Data_Oriented_Modelling/Heterogeneous_Data_and_General_Data_Intelligence/REPORT_EN.md`

**Status: SCOPE UPDATE / EVIDENCE ADVANCED**

The report already argues for preserving native source structure and comparing representations through future consequences. Later INTERNAL-COORDINATION-001–008 makes the shared-state idea more precise.

The later experiments support a layered organization:

**local/native mechanisms → shared consequence constraints → coordinated reality state**

rather than a requirement for raw-modality fusion or direct latent alignment.

Thirty directed cross-view retrieval tests reach 100% under intact world correspondence; shuffling world correspondence removes executable equivalence. Same-time permutation of six channels changes output only at numerical precision (~2.4×10⁻⁸), while reversing real chronology increases pinball loss from 0.0557 to 0.0733 and moves the learned state.

**Current interpretation:** presentation order within one simultaneous observation set should be quotiented out, while world chronology remains part of the generating structure. A shared state is justified by cross-view consequences, not by forcing all modalities into one common raw representation.

The line “Predictive states can be shared across modalities” in §4.4 should therefore be updated from a proposed cross-modal test to a consequence-defined coordination result with the above scope.

### 5.2 Report 02 — Learning Causal Structure from Data Geometry

Primary text: `Chapter_5_Data_Oriented_Modelling/Learning_Causal_Structure_from_Data_Geometry/REPORT_EN.md`

#### §10.1, “Recommended analytical sequence”

**Status: SUPERSEDED INTERPRETATION**

The sequence currently says:

> “Second apply a reversibility/identifiability gate.”

This remains a valid historical triage procedure for the CG-006 programme, but it is no longer the project-level role assigned to causal modelling.

The current framing is:

**observed data → multiple possible causal worlds → simulated / imagined / measured consequences → revised worlds → repeated comparison**

Causal geometry contributes constraints, local charts, candidate relations and response measurements to this generator. Identifiability remains one measurable property of a proposed world, rather than the global gate that decides whether modelling proceeds.

Importantly, the report itself already anticipates the newer direction in §21:

**Data ↔ representations ↔ hypotheses ↔ models/operators ↔ simulated or observed consequences ↔ revised representations.**

The correction is therefore primarily one of hierarchy: §10.1 should be labelled as the historical triage interface, while §21 supplies the current higher-level interpretation.

#### CG-001–CG-024 numerical findings

**Status: CURRENT**

No numerical retraction is implied by the framing update. The identifiability-boundary, chart, transfer, intervention-response and generated-mechanism experiments retain their stated evidence levels.

### 5.3 Report 03 — Modelling Hypothesized Mechanisms Underlying Data

Primary text: `Chapter_5_Data_Oriented_Modelling/Modelling_Hypothesized_Mechanisms_Underlying_Data/REPORT_EN.md`

#### Executive summary, §1, §19 and conclusion

**Status: SUPERSEDED AS A GENERAL DOM PROCEDURE; CURRENT AS A SPECIAL-CASE PROCEDURE**

The report presents a procedure in which explicit assumptions about geometry, sampling, task structure and valid states define a small candidate set, followed by a validation probe.

The executed experiments support that procedure when structural constraints are already known or when a scientific hypothesis deliberately defines an admissible model family.

The current Data-Oriented Modelling programme adds a broader regime for problems whose mechanism is not known in advance: measured data structure, history and consequences are used to learn the mechanism state and its changes, rather than supplying a prespecified mechanism label as the organising truth.

**Current interpretation:** known constraints can restrict inadmissible operations; unknown generating mechanisms are learned and compared through their consequences. The Report 03 procedure is therefore one branch of DOM, not the universal entry procedure.

The numerical findings on attention geometry, local scales, coverage, graph-state legality and validation probes remain unchanged.

---

## Repository-level status lines that are already stale

The root `README.md` currently under-reports two active research lines:

1. **Multiscale Language Generation** is listed as EXP001–EXP015. The living record has now completed through **EXP022**; EXP023 is in progress.
2. **Chemical Structure Changes and Odor Responses** is listed as 001–007. The line has now completed through **EXP015**.

The later chemical–odor campaign materially narrows the early “shared operator / transport” interpretation. In EXP012, one observed early-frame re-anchor raises future pooled cosine from 0.08134 to 0.27230, while persistent tangent continuation is negative in the final campaign (−0.05075). In EXP013, a no-shift frame reaches 0.38383, a global tangent 0.23227, chemical-nearest-neighbour transfer −0.15889, chemical ridge 0.06246, and the best chemistry-inferred later frame only 0.02060 versus 0.27230 for the observed re-anchor.

**Current chemical–odor interpretation:** stable operators exist for some transformation families, while changing families require an observed family frame and observation-triggered re-anchoring; chemistry-derived cross-family frame transport was not supported in the tested campaign.

---

## Recommended annotation policy

Do not rewrite historical numerical results. Add a dated **Later evidence update — 2026-10-02** block near the top of affected reports and point to this audit.

Use the following labels inline:

- **Superseded interpretation** — for Chapter 5 Report 02 §10.1 as the project-level causal framing, and Chapter 5 Report 03 when presented as the universal DOM entry procedure.
- **Scope updated by later evidence** — for Chapter 1 reasoning-time language, Chapter 2 stabilization/control generalization, Chapter 4 language-scale interpretation and Chapter 5 Report 01 shared-state interpretation.
- **Evidence advanced** — for Chapter 2 natural-LLM intervention, Chapter 3 stopping/recovery and Chapter 5 cross-view coordination.

This preserves the research chronology while making the current evidence hierarchy explicit.
