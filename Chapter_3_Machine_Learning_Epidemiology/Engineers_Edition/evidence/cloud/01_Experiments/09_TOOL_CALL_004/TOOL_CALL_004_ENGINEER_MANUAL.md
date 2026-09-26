# TOOL-CALL-004 — Semantic Tool Selection Geometry
## Engineering manual

This module is for the case where **two or more tools are all hard-executable** but the model chooses the wrong one.

### Do not collapse the tool definition into one string

Treat each candidate as at least three evidence channels:

1. `HANDLE/NAME` — canonical function/tool name.
2. `DESCRIPTION` — what operation the tool performs.
3. `SCHEMA/BINDING` — argument names/types/required fields.

The experiment shows these channels are not weighted the same way across architectures.

### Required online/incident telemetry

For every candidate tool record a comparable score under:

- `full`
- `name_neutral`: replace names with opaque IDs, keep descriptions + schema
- `description_neutral`: keep name + schema, replace description with a neutral placeholder
- `schema_neutral`: keep name + description, remove parameter-name evidence

Optional stronger audit:

- `name_only`
- `description_only`
- `schema_only`

### One-click diagnosis

```bash
python TOOL_CALL_004_semantic_selection_os.py diagnose incident.json
```

Read:

- `EVIDENCE_VIEW_DISAGREEMENT`
- `NAME_CAPTURE_RISK`
- `DESCRIPTION_CAPTURE_RISK`
- `SCHEMA_CAPTURE_RISK`
- `channel_effect_on_selected_margin`
- if an oracle/correct tool is known after an incident: `incident_root_channel`

### Engineering rule

Do **not** use one universal hidden axis or one universal channel weighting across architectures.

The cross-architecture experiment found:
- recurrent models leaned strongly on schema/description evidence;
- the tiny Transformer leaned much more on name/description evidence;
- perturbation fingerprints transferred much better within architecture than across architecture.

The portable layer is therefore **multi-view functional diagnosis**, not raw neuron coordinates.

### Prevention

1. **Separate semantic selection from canonical execution names.**
   Present opaque candidate IDs during semantic ranking; map the selected opaque ID back to the executable tool name afterward.
2. **Do a binding-compatibility gate before ranking**, but do not let parameter-name overlap alone choose the tool.
3. **Use discriminative tool descriptions.**
   Candidate descriptions should state what distinguishes near-neighbor functions.
4. **Run a counterfactual alias audit.**
   Renaming tool handles should not change a semantics-preserving selection beyond a calibrated tolerance.
5. **Run multi-view consistency.**
   If full/name-neutral/schema-neutral rankings disagree for a consequential call, HOLD instead of executing.
6. **Always log top-2 candidates and their pairwise margin.**
   Semantic selection is a competition, not a single-tool confidence score.
7. **Calibrate per architecture/model.**
   GRU/LSTM/Transformer evidence reliance differed substantially in the controlled replication.
8. **For robustly wrong selections, run Failure Axis Guard.**
   A large selection radius plus wrong semantics means a deeply encoded mis-selection, not mere boundary noise.
9. **Regression suite.**
   Include BFCL multiple cases plus handle-alias, schema-alias and description-ambiguity variants.

### Cross-architecture interpretation

The shared mathematical form is:

`tool margin = F(model state, goal evidence, tool-name evidence, description evidence, binding/schema evidence)`

not

`tool margin = universal_name_axis + universal_schema_axis`.

Architecture changes the internal factorization and interactions.

### Open-source checkpoint interface

The same four views can be run on any accessible HuggingFace/tool-calling checkpoint.
For each view:
- keep the same user prompt;
- change only the chosen evidence channel;
- score the candidate tool-call continuations;
- capture residual states and gradients if the model is locally instrumentable.

The current run attempted SmolLM2-135M-Instruct, but this runtime could not retrieve its Xet-hosted weight object, so no open-source hidden-state result is claimed here.
