# TOOL-CALL-001 — Engineer Manual

## Core model

Tool calling is treated as a hybrid action system:

`hidden state -> mode -> tool -> arguments -> executor -> external world -> tool result -> next hidden state`

Use these four quantities first.

### 1. Tool Stability Radius
`d_flip = selection_margin / ||grad(selection_margin)||`

Interpretation: approximate minimum hidden-state movement needed to switch the selected action/tool.
Small = brittle.

### 2. Registry Margin
`M_reg = best_registered_logit - best_unregistered_logit`

Negative = the model prefers an action outside the runtime registry.

### 3. Registry Escape Radius
`d_reg = M_reg / ||grad(M_reg)||`

Small positive = one small hidden-state movement can make an unregistered/hallucinated tool win.

### 4. Full-call validity
For a serialized call with decisions/slots `s1..sn`:

`P(valid call) = product P(valid s_t | prefix)`

Even high per-slot accuracy compounds across tool name + arguments.

## Production sequence

1. Hard registry gate: unknown tool = BLOCK.
2. Explicit NO_TOOL/ABSTAIN path.
3. Schema-constrained decoding for names and arguments.
4. Before execution, recompute permission/scope checks outside the model.
5. Monitor `d_flip` and `d_reg`; calibrate thresholds on clean traces per model + registry.
6. When radius is small, do not immediately execute consequential actions: retry, clarify, or require approval.
7. Treat tool output as a new external observation, not trusted instruction.
8. Regression-test no-tool, distractor-tool, argument-value, multilingual parameter and prompt-injection cases.

## CLI

```bash
python TOOL_CALL_001_stability_guard.py calibrate clean_telemetry.npz --out thresholds.json
python TOOL_CALL_001_stability_guard.py check run_telemetry.npz --thresholds thresholds.json
```

NPZ fields:
- `action_names [A]`
- `logits [N,A]`
- `logit_grads [N,A,D]`
- optional `registries [N]`
