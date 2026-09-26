# Model Control Diagnostics

**Chapter 3 — The Engineer’s Edition**

Living Engineering Record v0.6 · Integrated English release · 26 September 2026

This chapter turns measurements of a formed model into an engineering workflow: inspect how a token acts at a particular state, identify which input evidence changes a decision, test a finite internal intervention, and evaluate the interface that selects an executable candidate. It combines the nine cloud experiments in the v0.5 engineering record with the subsequent local pretrained-model study, selector comparison, and paraphrase stress test.

The combined evidence supports a practical division of work. State-conditioned telemetry characterizes a model’s response and guides interventions. Request-to-tool scoring establishes which capability matches a request. Argument binding and host-side contracts establish the conditions for execution. Each component has its own measurable output and evaluation denominator.

The cloud scanner closes three differential measurements against finite interventions in an 897-parameter GRU. A recovered runtime executes 6,336 token–state transitions. Later local work reports a tool-choice reversal through an internal intervention in SmolLM2-135M-Instruct. A separate frozen comparison obtains 99/100 correct selections with both a 22.7M relevance ranker and a lexical baseline. A 40-task paraphrase study then measures their response to reduced lexical overlap and the accompanying change in abstention coverage.

This edition integrates the later audits directly into the earlier explanations. Nearest-boundary calculations consider every admissible competitor. Pairwise margin recovery and recovery of first place among all candidates are reported separately. Input-view agreement is treated as a measured consistency property. Accuracy, accepted-set accuracy, and coverage retain separate denominators.

## 1 Scope and reading guide

The subject is the present response of an already formed model. The diagnostic unit is the combination of model checkpoint, current state, token or evidence intervention, and target readout. The engineering record uses saved telemetry, constructed controllers, miniature learned selectors, and local pretrained models at their respective evidence levels.

| Section | Material | Reader outcome |
| --- | --- | --- |
| 2–4 | Token scanner, state transplant, executable operator atlas | Query token effects at specified states and reproduce the archived runtime |
| 5–6 | Public incident casebook and failure-axis instrumentation | Specify behavioral targets and interpret intervention telemetry |
| 7–9 | Tool geometry, partial operators, action readiness | Separate score geometry, argument binding, and execution contracts |
| 10 | Cross-architecture semantic selection | Compare standardized evidence interventions across model families |
| 11–12 | Local audit and pretrained internal intervention | Apply the corrected measurement definitions and inspect the reported 135M case |
| 13–14 | Selector comparison and paraphrase stress study | Assess task fit, ranking accuracy, abstention, and wording sensitivity |
| 15–17 | Integrated workflow, evidence ledger, version record | Use the current interpretation and locate its supporting files |

### 1.1 Evidence labels

**Archive verified** identifies a calculation or file relationship checked directly against supplied bytes during preparation of this edition. **Archived experiment** identifies a completed experiment with its source artifacts included. **Reported local experiment** identifies a result in the supplied local terminal reports. The source-availability index records the status of each separately cited local attachment. **Constructed mechanism** identifies a system whose equations or controller were specified by the experimenter. **Engineering proposal** identifies a suggested use beyond the measured condition.

These labels describe different questions: what was measured, how the result was checked, and which files are in this release. Repeated tokens, layers, views, and task variants are observations within a study; their counts retain the relevant model and task grouping.

### 1.2 Current engineering interface

The operator interface offers SCAN, CARD, APPLY, COMPARE, COMPOSE, and ORDER. The incident interface records input-channel changes, decision margins, internal states, and finite patches. The selection interface ranks request–tool pairs and returns a canonical candidate or an abstention. Binding, permissions, environment receipts, and result validation belong to the host execution interface.

The current workflow is:

1. Establish the behavior of the model and readout on the intended selection task.
2. Score request–capability matches and retain all candidate scores.
3. Return a candidate, a tie, or an explicit no-match/uncertain result.
4. Bind arguments and request any missing information.
5. Check the current registry, schema, permissions, and environment state.
6. Execute through the host and validate the resulting observation.
7. Use input and internal interventions to investigate specific measured incidents.

This ordering preserves semantically relevant candidates during clarification. Missing arguments change the next interaction step; they do not by themselves establish that a tool is irrelevant.

### 1.3 Release identity

The engineering version advances from v0.5 to v0.6 for this English integration. “Chapter 3 — The Engineer’s Edition” is the publication label requested for the chapter. The machine-learning epidemiology report v1.9 remains a separately identified research record. Original source documents, filenames, experiment IDs, and historical code are preserved in the evidence collection.

The local reports document completed inference and component tests on the author’s machine. This edition adds deterministic checks of supplied cloud data and reported arithmetic. The availability map identifies the local scripts, raw scores, model-state telemetry, protocols, and logs referenced by those reports.
