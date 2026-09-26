## 5 Public incident casebook

Experiment REAL-WORLD-OPERATOR-FAILURES-001 · Published-case synthesis · 26 September 2026

This casebook converts documented interaction patterns into measurable engineering questions. Its sources are the IFEval++ prompt-variation study, SimpleToolHalluBench and Reasoning Trap, R-Judge, and the InjecAgent repository. The public incidents motivate the assays; the operator-level explanations are hypotheses to test through instrumentation.

### 5.1 Prompt wording and constraint retention

The IFEval++ example concerns a sleep-themed blog with wording, constraint, and distractor variations. A minimum word count and an approximate target word count specify related but distinct constraints. An equivalence test therefore begins with the exact task and evaluator contract for each prompt.

For matched constraints, proposed measurements include the divergence of control paths, retention of a constraint-related direction into generation, the functional distance between two surface expressions at a common state, and the first sampled position at which a measured divergence appears. These assays ask whether alternative input forms preserve the required functional outcome.

### 5.2 Requested tools and registry membership

One published pattern requests a restaurant-address function in an environment with no tools. The model describes a call and supplies a purported result. Another requests a vehicle-route change with an unrelated calibration function available. The former concerns registry membership; the latter concerns matching the available capability to the goal.

| Incident | Proposed measurement | Engineering question |
| --- | --- | --- |
| Requested function outside the registry | Registry Violation Margin | How does the unregistered-call score compare with clarification or abstention? |
| Function-name capture | Tool-Name Capture Ratio | How strongly do the requested name and registry evidence affect selection? |
| Registry intervention | Registry Counterfactual Gain | What changes when the required function is added or removed? |
| Irrelevant registered function | Capability Projection Error | How does the selected capability differ from the requested operation? |
| Distractor attraction | Distractor Attraction Margin | What score advantage does an available but irrelevant candidate have over abstention? |
| Fabricated result | Fabricated Observation Onset | At which sampled point does the trace begin to represent an unobserved outcome? |

These definitions separate a valid execution handle from a capability that addresses the request. Their mathematical realization depends on a specified behavioral score and controlled comparison.

### 5.3 External content and action authority

The Evernote incident begins with a request to retrieve the latest note containing “Budget.” An instruction embedded in the returned note redirects the agent toward granting smart-lock access. The related Amazon-review case places the access request in a product review field. Both motivate measuring the same instruction-like content under different source-channel labels.

The source-conditioned operator is $T(a,x,s)$, where $a$ is the linguistic input, $x$ is the model state, and $s$ identifies the channel. Candidate measurements include the action-gradient contribution of an external span relative to the user’s goal span, the response difference between user and tool-data presentations, and the change in the action-control direction after the external content.

The archived case file retains the public examples and the chosen behavior targets. The synthesis here describes the incidents in paraphrase. Source URLs and the original short extracts remain in the supplied records.

### 5.4 Common incident record

An incident record contains the model revision, tokenized transcript, source labels, registry, selected action scores, sampled states, and intervention definition. The useful output is a traceable relation between an input change and a behavioral change. Where internal states are accessible, a finite patch tests a proposed mediating state direction.

The casebook establishes the question and measurement contract. The following instrumentation prototype implements a subset of that contract.

## 6 Failure axis instrumentation

Experiment REAL-WORLD-OPERATOR-TELEMETRY-002 · Archived instrumentation and constructed self-check · 26 September 2026

The supplied Failure Axis Guard script provides case listing, a Hugging Face locator, report tracing, and a proposed guard plan. It includes paired and gradient-source modes. The cloud package contains the instrumentation and a saved mechanism self-check. The later local study in Section 12 contributes measured pretrained-model interventions.

![Failure axis workflow](../figures/REAL_WORLD_OPERATOR_TELEMETRY_002_pipeline.png)

Figure 6.1. The original instrumentation workflow. Its locator outputs require the interpretation and acceptance checks described below.

### 6.1 Behavioral score and local control axis

For a selected failure continuation and reference continuation, define a differentiable behavior margin $z$. At layer $\ell$ and token $t$, measure the state $h_{\ell t}$ and gradient

$$g_{\ell t}=\frac{\partial z}{\partial h_{\ell t}}.$$

For an aligned pair of trajectories, form $\Delta h_{\ell t}=h_{\mathrm{failure}}-h_{\mathrm{reference}}$ and the local contribution $c_{\ell t}=\langle\Delta h_{\ell t},g_{\ell t}\rangle$. The prototype stacks high-load vectors, weights them by absolute contribution, and uses their leading singular direction as a candidate failure-control axis. A finite state patch then measures the associated change in the behavior margin.

In paired mode, the comparison uses two inputs with an explicit alignment. In gradient-source mode, the comparison starts from the gradients of a selected input span and a directional intervention. A patch effect establishes a local intervention result for that model, case, behavior score, and state location.

### 6.2 Saved mechanism self-check

The saved demonstration uses state 251 of the recovered runtime and the two orders `0 → first` and `first → 0`. Their final state distance is 4.2121. The earlier step has weak control alignment and a rescue fraction approximately 0.0182; the later step has alignment 1.0 and rescue fraction 1.0.

Source table 060 column group 1 of 2. Repeated leading fields identify the same rows.

| step | token\_failure | token\_safe | paired\_state\_distance | control\_alignment | causal\_contribution |
| --- | --- | --- | --- | --- | --- |
| 0 | 0 | first | 2.8847 | 0.1106 | 0.0701 |
| 1 | first | 0 | 4.2121 | 1.0000 | 4.2121 |

Source table 060 column group 2 of 2. Repeated leading fields identify the same rows.

| step | rescue\_fraction |
| --- | --- |
| 0 | 0.0182 |
| 1 | 1.0000 |

Source transcription: [Table 060](../evidence/source_tables/t060_ORIGINAL.csv).

![Constructed failure axis self-check](../figures/REAL_WORLD_OPERATOR_TELEMETRY_002_selftest.png)

Figure 6.2. Saved finite-patch demonstration on the recovered runtime.

The command named `self-test` displays the archived JSON. Recomputing the mechanism requires executing the underlying calculation. This distinction is reflected in the release verification record.

### 6.3 Interpreting locator output

| Field | Current interpretation |
| --- | --- |
| `selected_layer` | Best-ranked layer among those evaluated by the prototype |
| `axis_file` | Saved vector for the model, case, and score definition |
| `patch_rescue_fraction` | Measured change relative to the chosen paired behavior gap |
| `layer_ranking` | Ranking of the sampled layer interventions |
| `source_authority_ratio` | Relative span-gradient measurement under the selected target |
| `goal_gradient_angle_deg` | Angle between the two selected target gradients |
| `injection_onset` | Earliest matched high-load token retained by the selected layer’s top-k procedure |

The original locator ranks a layer even when its patch effect is weak. A current incident assessment therefore reads the effect size and control results alongside the rank. The onset field reports a position within the sampled top-k procedure. A claim about the earliest causal event would require a coverage and intervention design that directly tests that quantity.

### 6.4 Operational use

From the included cloud experiment directory, `cases` lists the example records and `trace --report ...` reads a saved locator result. The `locate --model ...` entry point requires a compatible accessible causal language model and its runtime dependencies. The original manual is retained beside the script.

The source proposes source tagging, structured extraction of task-relevant fields, registry enumeration, argument validation, host authorization checks, and regression cases. These are host-side design proposals. The internal axis supplies diagnostic information and finite counterfactual measurements. Its calibration is specific to model revision, task, behavioral score, and state coordinate convention.

## 7 Tool calls as a hybrid action system

Experiment TOOL-CALL-001 · Constructed mechanism · 26 September 2026

A tool interaction combines continuous model state, discrete mode and tool selection, structured arguments, and an external environment transition. The experiment expresses this sequence as

$$p(m,k,a\mid x,R)=p(m\mid x,R)\,p(k\mid m,x,R)\,p(a\mid k,x,R),$$

followed by execution $e_{t+1}=E_k(e_t,a)$, an observation of the resulting environment, and a subsequent model-state update. A small internal displacement can cross a discrete selection boundary and change which finite external operation is proposed.

The mechanism study isolates four properties: discrete selection boundaries, registry-conditioned availability, sequential argument generation, and the size of the external effect associated with changing an action.

### 7.1 Current nearest-boundary definition

For winner $w$, scores $Q_j$, and gradients $g_j$ at a common state, the distance to the pairwise tangent boundary for competitor $j$ is

$$r_{w,j}=\frac{Q_w-Q_j}{\|g_w-g_j\|}.$$

The nearest admissible tangent boundary is obtained from all competitors:

$$r_{\mathrm{local}}=\min_{j\ne w,\ j\ \mathrm{admissible}}r_{w,j}.$$

The score runner-up identifies one boundary. A lower-scoring candidate can have a steeper score difference and a closer boundary. The local audit’s affine example uses scores 2, 1, and 0 with scalar gradients 0, 0.1, and 100. The runner-up distance is 10; the third candidate’s distance is 0.02. At displacement 0.02001, the third candidate wins.

This is a first-order measurement in the declared state coordinates and score units. A zero gradient difference is recorded as first-order unidentifiability. Finite nonlinear behavior is evaluated separately through perturbation measurements.

### 7.2 Historical boundary and amplification results

The original study sampled 20,000 constructed latent states. Its historical `d_flip` statistic used the score runner-up. The table and original plots retain that measurement identity. The later all-competitor definition supplies the corrected interpretation for new nearest-boundary calculations.

| metric | value |
| --- | --- |
| Boundary median d\_flip | 0.5964 |
| Boundary p05 d\_flip | 0.0442 |
| Near-boundary (d&lt;0.05) fraction | 0.0563 |
| Median finite world amplification | 2.6861 |
| P95 finite world amplification | 34.7689 |
| No-tool hallucination crossover reasoning gain | 2.3000 |
| Distractor capture crossover reasoning gain | 0.9000 |
| Distractor best tool similarity | 0.9338 |
| Goal-to-best-single-tool relative error | 0.3578 |
| 5-slot base full-call validity | 0.8268 |
| 5-slot perturbed full-call validity | 0.6487 |
| Relative drop after early perturbation | 0.2154 |
| Goal-to-valid-tool-positive-cone relative error | 0.3578 |

Source transcription: [Table 070](../evidence/source_tables/t070_ORIGINAL.csv).

Among these constructed states, 5.63% fall below the original runner-up radius threshold of 0.05. For the action flips measured in this construction, the ratio of finite world effect to latent perturbation has median 2.6861 and 95th percentile 34.7689. These quantities demonstrate the amplification mechanism under the specified controller and environment mapping.

![Historical tool boundary map](../figures/TOOL_CALL_001_boundary_map.png)

Figure 7.1. Original constructed selection geometry. Historical boundary values use the source runner-up convention.

### 7.3 Registry evidence and goal drive

The construction varies a goal-drive gain in a requested-tool score and compares it with an abstention score. If the goal term grows faster than the feasibility contribution, the requested action crosses the selection boundary. The recorded crossovers are approximately 2.30 for the nonexistent-tool example and 0.90 for the distractor example.

The registry diagnostic compares the largest in-registry and out-of-registry scores. Its margin and tangent radius describe the selected score functions. The host registry determines which execution handles can be invoked.

![Goal drive and registry capture](../figures/TOOL_CALL_001_reasoning_capture.png)

Figure 7.2. Constructed gain changes and their effect on the requested-tool versus abstention boundary.

### 7.4 Sequential argument generation

For a sequence of required slots, full-call validity factors into the conditional probability of satisfying each slot given the preceding valid slots. The constructed five-slot example has full-call validity 0.8268 at baseline and 0.6487 after an early perturbation, a relative reduction approximately 21.54%.

![Schema sequence validity](../figures/TOOL_CALL_001_schema_compounding.png)

Figure 7.3. Recorded full-call validity across sequential slot decisions.

![Argument cascade](../figures/TOOL_CALL_001_argument_cascade.png)

Figure 7.4. Effect of an early perturbation on later argument conditions in the construction.

Useful telemetry therefore includes selection scores and gradients, registry status, the decision associated with each content-bearing argument, and the external observation. The original stability script and CSVs are preserved as historical artifacts. Section 11 states the corrected component contracts reported by the local update.

## 8 Tools as guarded partial operators

Experiment TOOL-CALL-002 · BFCL case analysis and component demonstration · 26 September 2026

The casebook uses six BFCL V4 task types: a simple call, selection among tools, irrelevance, parallel calls, a missing parameter, and a missing function. The state includes model state $x_t$, environment $e_t$, registry $R_t$, bound information $B_t$, and goal $g_t$.

A callable partial operator has a registered handle, valid arguments, complete required bindings, and satisfied environment preconditions. ASK, WAIT, and ABSTAIN provide explicit interaction modes for the corresponding conditions.

$$U_t=\{\mathrm{ASK},\mathrm{WAIT},\mathrm{ABSTAIN}\}\cup\mathcal C_t.$$

$$\mathcal C_t=\{(k,a):k\in R_t,\ a\in\mathrm{Schema}_k,\ b_k(a)\land p_k(e_t,a)\}.$$

Here $b_k(a)$ denotes complete required bindings, and $p_k(e_t,a)$ denotes satisfied environment preconditions.

This formal model describes the execution domain. The local update adds explicit permission and environment receipts to the component input contract. Semantic ranking uses the request and tool capabilities before argument completion determines whether to call or clarify.

### 8.1 Six task structures

Source table 078 column group 1 of 2. Repeated leading fields identify the same rows.

| Case | Class | Mode | K tools | Expected calls | Required slots |
| --- | --- | --- | --- | --- | --- |
| BFCL\_simple\_python\_0 | simple | CALL | 1 | 1 | 2 |
| BFCL\_multiple\_1 | multiple\_tool\_selection | CALL | 3 | 1 | 3 |
| BFCL\_irrelevance\_0 | irrelevance\_abstention | ABSTAIN | 1 | 0 | 0 |
| BFCL\_parallel\_multiple\_0 | parallel\_set\_selection | CALL\_SET | 2 | 2 | 4 |
| BFCL\_multi\_turn\_miss\_param\_0 | missing\_parameter\_clarification | ASK\_THEN\_CALL | 2 | 2 | 4 |
| BFCL\_multi\_turn\_miss\_func\_0 | missing\_function\_recovery | WAIT\_FOR\_TOOL\_THEN\_CALL | 4 | 1 | 1 |

Source table 078 column group 2 of 2. Repeated leading fields identify the same rows.

| Case | Parallel width | Turns | Hard gates |
| --- | --- | --- | --- |
| BFCL\_simple\_python\_0 | 1 | 1 | 4 |
| BFCL\_multiple\_1 | 1 | 1 | 5 |
| BFCL\_irrelevance\_0 | 0 | 1 | 2 |
| BFCL\_parallel\_multiple\_0 | 2 | 1 | 6 |
| BFCL\_multi\_turn\_miss\_param\_0 | 1 | 5 | 7 |
| BFCL\_multi\_turn\_miss\_func\_0 | 1 | 5 | 7 |

Source transcription: [Table 078](../evidence/source_tables/t078_ORIGINAL.csv).

![Partial operator diagram](../figures/partial_operator_redrawn.png)

Figure 8.1. Partial-operator model of tool interaction, redrawn from the source diagram for readability. The original is preserved in the cloud evidence directory.

![BFCL case profiles](../figures/TOOL_CALL_002_boundary_profile.png)

Figure 8.2. Structural measurements of the six named cases.

**Simple call.** A triangle-area request supplies base 10 and height 5. Removing the height preserves the relevant capability and changes the next step to argument clarification.

**Multiple tools.** A triangle-area request supplies sides 3, 4, and 5. The benchmark selects the Heron-formula tool. A base-height function can accept two numbers under its schema, so validating the arguments alone does not establish that their roles were supported by the request. These particular side lengths also form a right triangle; the engineering point is the binding and operation contract, independently of a coincident numeric result.

**Irrelevance.** A triangle-area request is paired only with a body-mass-index tool. The relevant response is the no-matching-tool path.

**Parallel calls.** A request for a sum of multiples and a product of primes requires two operations. The proposal is an action set. Completeness is evaluated against the two stated subgoals.

**Missing parameter.** A file-move instruction leaves the source filename unspecified. The next interaction asks for that binding. Once the filename is provided, the relevant call can enter the execution domain.

**Missing function.** A sorting request arrives before the sorting function is available. The interaction records the missing capability; adding that function changes registry membership and enables the corresponding call.

### 8.2 Minimal changes and component checks

| Case | minimal\_change | before | after | gate\_flipped |
| --- | --- | --- | --- | --- |
| BFCL\_simple\_python\_0 | remove height=5 from user request | CALL\_READY | MISSING\_REQUIRED\_ARGUMENT | BINDING\_COMPLETE |
| BFCL\_multiple\_1 | replace 'three sides: 3,4,5' with 'base 4 and height 5' | Heron tool is schema-compatible | base-height tool is schema-compatible | TOOL\_ID |
| BFCL\_irrelevance\_0 | replace offered BMI tool with calculate\_triangle\_area | ABSTAIN | CALL\_READY | MODE / RELEVANCE |
| BFCL\_parallel\_multiple\_0 | remove sentence 'Also find the product of the first five prime numbers.' | CALL\_SET cardinality=2 | CALL\_SET cardinality=1 | CALL\_SET\_CARDINALITY |
| BFCL\_multi\_turn\_miss\_param\_0 | add 'previous\_report.pdf' as the missing source filename | ASK / NO CALL | CALL\_READY | BINDING\_COMPLETE |
| BFCL\_multi\_turn\_miss\_func\_0 | add sort(file\_name) function to current registry | WAIT / NO CALL | CALL\_READY | FUNCTION\_AVAILABLE |

Source transcription: [Table 086](../evidence/source_tables/t086_ORIGINAL.csv).

The source validator demonstrates selected mode, binding, registry, and cardinality checks on named case contracts.

| Case | test | Admissible in source check | failed\_gates |
| --- | --- | --- | --- |
| BFCL\_simple\_python\_0 | correct | True |  |
| BFCL\_simple\_python\_0 | missing\_arg | False | BINDING\_COMPLETE |
| BFCL\_multiple\_1 | correct | True |  |
| BFCL\_multiple\_1 | schema\_valid\_wrong\_semantics | True |  |
| BFCL\_irrelevance\_0 | correct | True |  |
| BFCL\_irrelevance\_0 | wrong\_mode | False | MODE;CALL\_SET\_CARDINALITY |
| BFCL\_parallel\_multiple\_0 | correct | True |  |
| BFCL\_parallel\_multiple\_0 | undercall | False | CALL\_SET\_CARDINALITY |
| BFCL\_multi\_turn\_miss\_param\_0 | correct\_preclarification | True |  |
| BFCL\_multi\_turn\_miss\_func\_0 | unregistered\_missing\_function | False | REGISTRY |

Source transcription: [Table 087](../evidence/source_tables/t087_ORIGINAL.csv).

Its `allowed_modes` and expected call counts are supplied by those case contracts. The later local audit expands validation of numeric values, supported schema features, empty calls, host receipts, snapshot identity, and parallel conditions. The current claim is therefore tied to the checks implemented by each version.

### 8.3 Incident taxonomy

| Type | Condition to inspect | Relevant response |
| --- | --- | --- |
| Execution-domain violation | Registry, binding, schema, permission, or precondition mismatch | Return the specific failed contract check |
| Semantic selection error | Chosen capability differs from the request | Compare request–tool scores and evidence interventions |
| Set-coverage error | Proposed action set differs from required subgoals | Check goal coverage and call-set composition |
| Environment-path error | Current environment differs from the assumed state | Inspect environment receipts and prior outcomes |
| Missing capability | Relevant function is outside the current registry | Report or request the required capability |
| Missing information | Relevant function awaits a binding | Ask for the missing information |

The package retains the six task contracts, minimal changes, source checks, and mathematical dissection. The later integrated workflow keeps semantic matching and executable-domain validation as separately evaluated components.
