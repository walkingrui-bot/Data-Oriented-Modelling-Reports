# Failure Axis Guard OS — Engineer Manual

## What you run

### 0. List the bundled real-world cases
```bash
python REAL_WORLD_OPERATOR_TELEMETRY_002_axis_guard.py cases
```

### 1. One-click localization
```bash
python REAL_WORLD_OPERATOR_TELEMETRY_002_axis_guard.py locate \
  --model /path/to/hf-model \
  --case IPI_EVERNOTE_BUDGET_LOCK \
  --out evernote_report.json
```

The report returns:
- `selected_layer`: layer where the validated failure axis is strongest
- `axis_file`: `.npy` vector for the Failure Control Axis (FCA)
- `injection_onset`: earliest high-contribution token after the clean/failure trajectories diverge
- `source_authority_ratio`: untrusted-source behavioral gradient / trusted-user gradient
- `goal_gradient_angle_deg`: angle between failure target and safe target control directions
- `patch_rescue_fraction`: how much of the clean↔failure behavior gap is rescued by removing the FCA component
- `layer_ranking`: next-best layers for debugging

### 2. Read the trace
```bash
python REAL_WORLD_OPERATOR_TELEMETRY_002_axis_guard.py trace --report evernote_report.json
```

### 3. Generate a prevention / intervention plan
```bash
python REAL_WORLD_OPERATOR_TELEMETRY_002_axis_guard.py guard-plan \
  --case IPI_EVERNOTE_BUDGET_LOCK \
  --report evernote_report.json
```

### 4. Built-in math self-test
```bash
python REAL_WORLD_OPERATOR_TELEMETRY_002_axis_guard.py self-test
```

## What “which axis?” means

For a behavior score z (e.g. malicious tool-call log-probability minus safe response log-probability):

1. Capture residual state `h[layer, token]`.
2. Compute behavior gradient `g = ∂z/∂h`.
3. For clean/failure pairs compute `Δh = h_failure - h_clean`.
4. Per token causal loading is `c = <Δh, g>`.
5. Stack the highest-loading control vectors and run SVD.
6. The top right-singular direction is the FCA for that layer.
7. Remove only that component and rerun.
8. The axis is accepted only if the behavior gap is actually rescued.

No human naming of hidden dimensions is required.

## Prevention order — use this in production

### Prompt injection
1. `SOURCE_TAG`: mark browser/RAG/tool text as `UNTRUSTED_DATA`.
2. `STRUCTURE`: extract required fields into schema; avoid feeding free-form external instructions into privileged planning.
3. `INTENT_GATE`: external data cannot authorize a new side-effect action.
4. `REGISTRY + LEAST PRIVILEGE`: only task-scoped tools and arguments are allowed.
5. `AXIS_MONITOR`: compare failure-axis load / source-authority ratio to a clean calibrated threshold.
6. `APPROVAL`: pause consequential writes / physical / financial actions.
7. `AXIS_PATCH`: diagnostic only; use it to confirm mechanism, not as the sole safety barrier.

### Nonexistent-tool hallucination
1. `REGISTRY_ENUM`: unknown tool name = deterministic block.
2. `NO_TOOL_PATH`: if no valid tool exists, return abstain/no-tool.
3. `SCHEMA_CONSTRAINT`: tool calls come only from registered schemas.
4. `TOOL_GUARD`: validate tool name + args + permission at the execution boundary.
5. `AXIS_MONITOR`: use the localized hallucinated-tool axis as an early-warning telemetry signal.
6. `REGRESSION`: replay the NTA/DT case suite after any model/prompt/tool-registry update.

## Thresholds
Do not hard-code one global number.
For every deployed model:
- collect clean traces
- compute axis-load / source-authority distributions
- start from a clean p99 threshold
- validate against attack/failure cases
- tighten for high-risk tool families

## Dependencies for real model localization
- Python 3
- NumPy
- PyTorch
- Transformers
- an accessible HuggingFace causal-LM checkpoint

The current environment does not contain a public 7B/8B checkpoint, so this package does not claim a real-model layer number here. The localization code is executable and the axis mathematics is self-tested on the existing instrumented recurrent runtime.
