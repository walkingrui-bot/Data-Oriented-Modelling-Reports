# TOOL-CALL-002 — Classic Case Dissection / Partial Operator Manual

## Core rule

A tool is a partial operator, not a free-form language action.

State:
`z_t = (x_t, e_t, R_t, B_t, g_t)`

- `x_t`: model state
- `e_t`: external environment state
- `R_t`: runtime tool registry
- `B_t`: currently bound argument information
- `g_t`: user goal

Admissible executable set:

`U_t = {ASK, ABSTAIN, WAIT} ∪ {(k,a): k∈R_t, a∈Schema_k, Required_k(a)=complete, Pre_k(e_t,a)=true}`

For parallel calls, the action can be a set `S ⊆ U_t`.

## Failure classes from classic BFCL cases

- Simple: argument-domain failure.
- Multiple: tool identity boundary among competing partial operators.
- Irrelevance: empty useful action set; nearest-tool projection is wrong.
- Parallel: output is a set; cardinality/coverage becomes part of correctness.
- Missing parameter: operator exists but required binding is missing; CALL is undefined until ASK resolves it.
- Missing function: desired operator is absent from the current registry; nearest available tool must not substitute for it.

## Deterministic guard

```bash
python TOOL_CALL_002_partial_operator_guard.py cases

python TOOL_CALL_002_partial_operator_guard.py validate   --case BFCL_simple_python_0   --proposal '{"mode":"CALL","calls":[{"name":"calculate_triangle_area","arguments":{"base":10,"height":5}}]}'
```

This guard checks only the hard executable domain:
MODE, registry membership, call-set cardinality, required bindings, schema fields and basic types.

Important: a call can be schema-valid but semantically wrong (for example choosing the base/height triangle function for a three-side problem). Semantic tool selection still requires model-level telemetry / behavior scoring.

## Engineering order

1. Decide MODE: CALL / CALL_SET / ASK / WAIT / ABSTAIN.
2. Compute admissible registry `R_t`.
3. Do not select a tool outside `R_t`.
4. Verify all required bindings before CALL.
5. Validate schema/types.
6. Verify environment preconditions after prior side effects.
7. For parallel tasks, verify set cardinality and goal coverage.
8. Execute.
9. Treat execution result as a state transition; recompute the admissible set before the next call.
