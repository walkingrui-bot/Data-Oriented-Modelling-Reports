# TOOL-CALL-003 — Action Readiness Geometry
## Engineer Manual

### What this solves

Do not ask only **which tool is top-1**.

At every tool-decision checkpoint decide among:

`CALL(tool)` / `CALL_SET(tools)` / `ASK` / `WAIT` / `ABSTAIN` / `CONTINUE`

A tool may be semantically attractive but not executable. A tool may be executable but not yet robustly ready. A model may already be CALL-ready and become worse after another reasoning step.

---

## 1. Required telemetry

At the chosen layer/time checkpoint save:

1. hidden state `h_t`
2. runtime registry `R_t`
3. currently bound arguments `B_t`
4. environment preconditions `e_t`
5. explicit user goal / subgoals
6. one score `Q_a` for every candidate action
7. one hidden-state gradient `g_a = dQ_a/dh_t` for every action
8. hard admissibility flag for every action

Use the same score convention for all candidates at one checkpoint.

Recommended score sources:
- constrained continuation log-probability;
- native tool/action head logit;
- separately trained action-value/critic.

Do not compare unrelated scores from different heads without calibration.

---

## 2. Compile the hard executable domain first

A CALL candidate exists only if:

`tool ∈ runtime_registry`
AND required arguments are bound
AND schema/type validation passes
AND permission/scope is allowed
AND environment preconditions hold.

This is the **partial-operator domain** from TOOL-CALL-002.

If a required parameter is missing, remove CALL and expose ASK.
If the required function is absent, remove CALL and expose WAIT.
If no useful executable operator exists, ABSTAIN must remain available.
For multiple independent subgoals, expose CALL_SET.

---

## 3. Compute action readiness

Let `a*` be the best admissible action and `b*` the best alternative, including CONTINUE.

`M = Q(a*) - Q(b*)`

`g = dM/dh = g_a* - g_b*`

`rho = M / ||g||`

`rho` is the local action-stability radius.

Interpretation:
- positive large: robustly inside the action region;
- positive small: near a mode/tool boundary;
- negative: another action is better.

---

## 4. Decision rule

Use action-specific thresholds calibrated on clean traces.

If `rho < tau(kind)`:
`HOLD_UNSTABLE`
- do not execute a consequential tool;
- request clarification, rerun, or require approval.

Otherwise:

- winner CALL -> `EXECUTE`
- winner CALL_SET -> `EXECUTE_SET`
- winner ASK -> ask for the missing binding
- winner WAIT -> report/request missing capability
- winner ABSTAIN -> no tool
- winner CONTINUE -> permit another reasoning step

---

## 5. One-click CLI

```bash
python TOOL_CALL_003_action_readiness_os.py decide state.json --thresholds thresholds.json
```

Output:
- winner action
- runner-up
- readiness margin
- stability radius
- robustness threshold
- operation to perform
- nearest boundary gradient

### Calibrate from clean telemetry

```bash
python TOOL_CALL_003_action_readiness_os.py calibrate clean.jsonl --out thresholds.json
```

Starting rule: clean p01 radius. Recalibrate per model + task family + tool registry.

### Audit a reasoning/tool trace

```bash
python TOOL_CALL_003_action_readiness_os.py trace trace.jsonl --thresholds thresholds.json
```

The tracer reports:
- `TOOL_OVERTHINKING_EXIT`
- `CALL_REENTRY`

---

## 6. Tool-overthinking

Definition:

A state is already in a robust CALL region.
The system executes CONTINUE/thought instead of executing.
The next state leaves the robust CALL region even though the tool is still hard-executable.

This is not “the answer got longer”.
It is a negative continuation transition in action-readiness geometry.

Operational response:
1. log the first robust CALL checkpoint;
2. if the policy continues, keep tracing;
3. if CALL readiness is lost with the hard domain unchanged, flag overthinking;
4. compare execution at first-ready vs later state;
5. use the earlier state for counterfactual execution/replay;
6. if reproducible, train/route the controller to stop at the first robust region.

---

## 7. Argument-level readiness

A correct tool identity is not enough.

Before execution either:
- use schema-constrained decoding; and
- measure each content-bearing argument value separately.

For argument slot `j`:

`rho_j = M_j / ||dM_j/dh||`

If any consequential required slot is below threshold:
do not execute the whole call.

---

## 8. Post-tool result

After a tool result arrives:
- treat it as a new observation;
- update environment, bindings and registry;
- recompute the entire admissible set and readiness;
- never reuse the previous CALL decision automatically.

---

## 9. Production safety order

1. hard registry/schema/permission gate
2. action readiness geometry
3. argument-level readiness
4. external execution guard
5. human approval for consequential side effects
6. recompute after every tool result

Readiness geometry is an observability/controller layer. It is not a replacement for deterministic execution guards.

---

## 10. Debugging a robust wrong action

If the wrong tool is **robustly** selected (large rho), this is not ordinary boundary fragility.

Pass the case to the existing Failure Axis Guard OS:
- LOCATE layer/token/FCA
- TRACE source/control contributions
- PATCH counterfactually
- VERIFY rescue

That distinguishes:
- near-boundary instability;
- from a deeply embedded semantic mis-selection.
