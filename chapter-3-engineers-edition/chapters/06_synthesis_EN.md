## 15 Engineer operating guide

### 15.1 Inspect a formed model

Begin with a defined behavior score and a saved model/state identity. Use the token scanner to distinguish immediate answer effects, future-state effects, adjacent-token steering, and trajectory persistence. Where a recovered operator runtime is available, APPLY and ORDER provide executable queries at the saved states.

Use standard input interventions to measure the role of tool names, descriptions, and schemas in a selected decision. Retain all candidate scores, canonical mappings, and any tied winners. When the expected answer is known retrospectively, record both the pairwise margin and first place among every candidate.

For an internal patch, retain the input pair, state alignment, layer and token location, intervention magnitude, behavioral score before and after, self control, and comparison directions. These fields make the observation traceable to a specific operation on a specific model.

### 15.2 Establish the selection interface

Measure natural selection accuracy, candidate-order response, use of the query, and behavior when candidates match poorly. The local comparison demonstrates that a relevance-trained 22.7M model can be a more effective selector than the tested 135M label readout. It also demonstrates the value of a lexical baseline on the same tasks.

If a rejection policy is used, freeze it on a named calibration set and report accepted-set accuracy, coverage, and the definition of the rejection test population. Repeat those measurements under relevant wording or document changes. The paraphrase study provides an example in which coverage changes substantially even though all accepted outcomes remain correct.

### 15.3 Included executable entry point

The recovered token atlas is directly included and its 6,336-row transition table is checked by the release verifier. The cloud incident and controller utilities retain their historical implementations and manuals in their respective experiment directories. The current interpretation of their outputs is given in Sections 6–11.

```sh
python3 evidence/editorial/verify_supplied_evidence.py --root .
```

This command recalculates selected statistics from packaged files and checks the documented source-code counterexamples. It uses NumPy and the Python standard library. Its saved result is supplied in `evidence/editorial/verification_results.json`.

### 15.4 Reported local component entry points

The local reports describe the following commands in their original host project:

```sh
python3 mcd.py diagnose incident.json
python3 mcd.py radius telemetry.json
python3 mcd.py guard domain.json
python3 selector.py /absolute/path/request.json
python3 selector.py /absolute/path/request.json --method lexical
python3 selector.py /absolute/path/request.json --policy policy.json
```

These are the reported local interfaces. Their implementation files, model cache revisions, original BFCL inputs, and policy are identified in `LOCAL_SOURCE_MAP.csv`. The English interface manual describes their inputs and outputs, and the four supplied local source documents remain alongside it for provenance.

The selector input is an object with a nonempty string `query` and a `tools` array. Every tool has a unique nonempty `name`, nonempty `description`, and object-valued `parameters`. The evaluated distribution is English requests and capability descriptions. Output includes `diagnostic`, candidate scores, and telemetry. Empty candidates return `NO_CANDIDATES`; a tied top score returns `TIED` with no selected tool; a unique top score returns `RANKED`.

The scores retain their units: relevance logits or lexical cosine similarities. With a policy, the caller reads the `recommendation` field even if the diagnostic `selected` field retains the highest-scoring name after abstention. The local component separates ranking from action execution.

The documented truncation strategy preserves the query and truncates the tool-document tail to the 512-token budget, recording truncation in telemetry. A query exceeding the feasible budget follows the tokenizer’s error path. Archived experiment output paths use exclusive creation; a new run receives a new ID and output location.

### 15.5 Host execution responsibilities

The host maps a selected canonical candidate to the actual registry entry, obtains missing arguments, validates the supported schema, checks current authorization and environment conditions, and invokes the tool. It then records the observed result and updates the next decision snapshot.

The reported guard component checks submitted receipts and schema values. The host supplies the connection between those receipts and the actual environment. This interface allows selection quality, binding correctness, execution validity, and the external result to be evaluated independently.

## 16 Integrated findings and evidence status

| Finding | Current evidence | Operational interpretation |
| --- | --- | --- |
| Three scanner measurements predict finite effects | Archived 897-parameter GRU data; release recalculation | Use the specified derivatives and scales as calibrated local instruments |
| A fixed token has state-dependent effects | Complete 10-by-352 response grid and finite high/low examples | Identify the model–state–token–readout event |
| Token functions can be queried through a recovered runtime | Included NPZ, source, 6,336 transitions, and reconstruction calibration | Execute the recovered model and retain its calibration identity |
| Tool scores have multiple competing boundaries | Constructed affine example and inspected original code | Take the minimum over admissible competitors for the local tangent estimate |
| Tool availability, relevance, and complete binding are separately measurable | Named BFCL case contracts and local component audit | Match capability, clarify arguments, then check execution conditions |
| Readiness can exit and re-enter along a trajectory | Specified seven-dimensional controller | Treat the result as a constructive action-geometry example |
| Evidence-channel sensitivity differs across miniature architectures | Archived intervention tables and response fingerprints | Compare standardized functional responses with per-model coordinates |
| A finite state intervention changes a pretrained tool choice | Reported `multiple_23` study, four sampled blocks | Local intervention evidence for the pinned 135M model and readout |
| Independent relevance ranking improves the tested label interface | Reported frozen 100-task comparison, 99/100 versus 40/100 | Qualify the selection interface on the target behavior |
| A lexical baseline matches the neural method on the original final tasks | Reported equal 99/100 outcomes | Include simple baselines in engineering comparisons |
| Wording changes affect ranking and accepted coverage | Reported forty paired paraphrases | Report accuracy and coverage under the same input intervention |

### 16.1 Corrections carried through the report

The runner-up radius in historical tables is named as a pairwise quantity. Current nearest-boundary equations use all admissible competitors. The exact runtime-to-table check is kept separate from approximate reconstruction against original telemetry. Empirical signature compression is indexed by its state bank.

Channel neutralization is described as an input intervention, and the 25/41 result is labeled retrospective pairwise recovery. Four-view agreement is accompanied by observed accuracy. The pretrained patch is identified by case, block sample, score, and controls. The 40-task paraphrase follow-up retains its own registration and task range.

Earlier proposals about automatically acting on a local radius or view agreement are represented in the original source record. The current integrated guide assigns those measurements a diagnostic role and evaluates selection and execution through their corresponding behavioral and host contracts.

### 16.2 Source availability

The supplied cloud archive contains 229 files, including nine experiment directories, three shared telemetry collections, five historical engineering Word editions, a reference research record, eleven original stage archives, and source indexes. Every member is retained in the expanded cloud tree. The exact uploaded ZIP is retained separately.

The local additions consist of two completed reports and two READMEs. Their referenced code, raw score files, state telemetry, protocols, and logs are listed in `LOCAL_SOURCE_MAP.csv`, with a status for each item. The paraphrase study is represented by the results included in its parent report; its own report is a referenced item.

The new English narrative, source-order table transcriptions, generated figures, verification script, and calculated results each have a declared origin. Original data and code retain their source language and file identity. Hash manifests describe the assembled release bytes.

## 17 Version record

| Version | Date | Content |
| --- | --- | --- |
| v0.1 | 26 September 2026 | Token scanner, state transplant, operator atlas, public casebook, and telemetry prototype |
| v0.2 | 26 September 2026 | Added TOOL-CALL-001 hybrid action geometry |
| v0.3 | 26 September 2026 | Added TOOL-CALL-002 guarded partial operators |
| v0.4 | 26 September 2026 | Added TOOL-CALL-003 constructed action readiness |
| v0.5 | 26 September 2026 | Added TOOL-CALL-004 cross-architecture semantic selection |
| v0.6 | 26 September 2026 | Integrated English Chapter 3 edition with local engineering audit, pretrained intervention, selector comparison, paraphrase follow-up, and evidence crosswalk |

This edition preserves the chronological experimental identities and uses the subsequent measured audit to update the current engineering interpretation. Future additions can extend this record with complete protocols, results, discussion, data references, and version history.
