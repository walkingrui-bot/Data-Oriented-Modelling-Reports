## 48 Cross architecture replication of relational trajectories and stopping

Research ID: ML-EPIDEMIOLOGY-XARCH-20260926-001. This campaign supplies a conceptual replication across GRU, causal Transformer and Mamba models. Its completed report is included in evidence/replications/xarch/REPORT_ORIGINAL.md. The present synthesis uses the full nine-model denominator and preserves the distinction between task learning, requested answer readout and stopping cost.

### 48.1 Common task training and evaluation

The campaign trained three initializations of each architecture, seeds 2601, 2602 and 2603. Each two-layer model had hidden width 48 and received 900 AdamW updates on the same 48 sequences: all 16 four-bit questions in Direct, Blank and relational-CoT modes. Parameter counts were 29,291 for GRU, 40,523 for Transformer and 35,424 for Mamba. Each sequence contributed an equal-weight mean over its generated tokens. These are nine independent training runs; the 144 model–question observations are repeated measurements within those runs.

Direct emits the answer, Blank emits three X tokens before the answer, and CoT emits three relation values followed by the answer. The third relation value already equals the answer. All questions appeared in model training. An eight-fold question-grouped evaluation holds stopping labels out from the ridge stopping rule, using a fixed threshold of 0.8. The original stopping study used six-bit questions and up to five relation steps, so the two protocols provide complementary conceptual tests.

### 48.2 Complete nine model results

All nine models learned the full relational chain and the Direct answer. Eight learned the Blank sequence perfectly. A disconnected readiness set means that at least one question has a correct requested answer, then an incorrect answer, then a correct answer again along the measured relation path. Seven of nine models exhibit this phenomenon, with examples in all three architectures.

| Architecture and seed | Direct correct | Blank correct | Full CoT correct | Disconnected questions of 16 | Stop answer accuracy | Mean relation steps | Savings versus 3 steps |
| --- | --- | --- | --- | --- | --- | --- | --- |
| GRU 2601 | 100% | 100% | 100% | 4 | 100% | 0.7500 | 75.00% |
| GRU 2602 | 100% | 100% | 100% | 0 | 100% | 0.5000 | 83.33% |
| GRU 2603 | 100% | 100% | 100% | 0 | 100% | 1.7500 | 41.67% |
| Transformer 2601 | 100% | 100% | 100% | 3 | 62.50% | 1.5625 | 47.92% |
| Transformer 2602 | 100% | 62.50% | 100% | 3 | 81.25% | 2.0625 | 31.25% |
| Transformer 2603 | 100% | 100% | 100% | 6 | 100% | 1.3125 | 56.25% |
| Mamba 2601 | 100% | 100% | 100% | 8 | 100% | 0.5000 | 83.33% |
| Mamba 2602 | 100% | 100% | 100% | 9 | 81.25% | 1.1875 | 60.42% |
| Mamba 2603 | 100% | 100% | 100% | 5 | 87.50% | 1.6875 | 43.75% |

[REPRODUCED] Path-dependent, nonmonotonic requested-answer readiness occurs across these three architectures. The observation is tied to the recorded question, prefix, answer request and output rule. Direct performance establishes a strong reference: each trained model also implements a correct immediate-answer route on this task.

### 48.3 Fixed depth and native vocabulary readout

The stopping metric compares the two answer tokens after inserting ANSWER following a self-generated relation prefix. The following fixed-depth results use exactly that same scoring rule. The last column uses the saved unrestricted prediction at the chosen stopping point.

| Architecture and seed | k 0 | k 1 | k 2 | k 3 | Native token accuracy at chosen stop |
| --- | --- | --- | --- | --- | --- |
| GRU 2601 | 75% | 50% | 50% | 100% | 100% |
| GRU 2602 | 75% | 75% | 100% | 100% | 100% |
| GRU 2603 | 50% | 50% | 50% | 100% | 93.75% |
| Transformer 2601 | 50% | 62.5% | 81.25% | 100% | 50% |
| Transformer 2602 | 68.75% | 50% | 50% | 100% | 81.25% |
| Transformer 2603 | 75% | 56.25% | 68.75% | 100% | 100% |
| Mamba 2601 | 100% | 75% | 62.5% | 100% | 93.75% |
| Mamba 2602 | 81.25% | 50% | 50% | 100% | 81.25% |
| Mamba 2603 | 50% | 56.25% | 87.5% | 100% | 87.5% |

[CONDITIONAL] Five stopping rules preserve perfect binary answer accuracy. Four also use fewer relation steps than every perfect fixed-depth policy for that model. Mamba 2601 is already perfect at fixed zero steps. Transformer 2601 reaches the same 62.5% with one fixed step, compared with 1.5625 selected steps; Mamba 2602 reaches the same 81.25% at zero steps. GRU 2602's reduction is 75% relative to its strongest perfect fixed baseline of two steps. Three of the five binary-perfect stoppers also remain perfect under unrestricted token output. These paired comparisons define the practical interpretation of the savings column.

### 48.4 Content interventions affect successor answers

For each of the 16 questions, the experiment flips one relation bit in an otherwise fixed three-relation prefix. The no-op control has maximum logit difference zero. Counts below measure resulting answer flips.

| Architecture and seed | Flip r1 | Flip r2 | Flip r3 |
| --- | --- | --- | --- |
| GRU 2601 | 7/16 | 12/16 | 4/16 |
| GRU 2602 | 8/16 | 8/16 | 8/16 |
| GRU 2603 | 4/16 | 4/16 | 12/16 |
| Transformer 2601 | 0/16 | 0/16 | 16/16 |
| Transformer 2602 | 0/16 | 0/16 | 16/16 |
| Transformer 2603 | 0/16 | 0/16 | 15/16 |
| Mamba 2601 | 1/16 | 0/16 | 14/16 |
| Mamba 2602 | 0/16 | 0/16 | 12/16 |
| Mamba 2603 | 5/16 | 5/16 | 12/16 |

[REPRODUCED] Relation-token content has a causal effect on subsequent output under these interventions. Transformer responses concentrate on r3, the answer-bearing token. Holding later relations fixed isolates the selected input intervention and constrains mediation through subsequent tokens. Coherent counterfactual trajectories, matched controls and selective restoration provide the next level of algorithm-specific evidence.

### 48.5 Pretrained model measurements and task screening

The campaign also loaded official Pythia-70M and Mamba-130M weights, with actual parameter counts 70,426,624 and 129,135,360. On 12 fixed English texts, both completed forward passes, greedy eight-token continuation, input-embedding gradients and central-difference checks. Input-ID versus original-embedding no-op errors were zero; all gradients were finite. Maximum relative differences between automatic gradients and central differences at epsilon 0.01 were 1.141% and 0.526%.

A subsequent exploratory task screen froze four demonstrations and its criteria before inspecting task outputs, then scored the other 12 questions.

| Model | Direct native answer | Blank native answer | Self-generated complete relation chain and answer | Native answer after correct relations |
| --- | --- | --- | --- | --- |
| Pythia-70M | 5/12 | 6/12 | 0/12 | 9/12 |
| Mamba-130M | 5/12 | 5/12 | 1/12 | 7/12 |

The demonstrated result is measurement compatibility on the installed pretrained models. These task scores define their screening status under the frozen prompt. The supplied report preserves every raw continuation reference and the distinction between a correct final symbol and a correct relation chain.

### 48.6 Execution record and evidence identity

All 8,100 scheduled updates completed in a batch of approximately 383 seconds. Each final checkpoint includes weights, optimizer state, random states, step count and reference logits. The original JSON export encountered a NumPy int64 serialization error after checkpoint saving. Recovery loaded the same nine terminal states and reran the unchanged evaluation function with scalar conversion at the JSON boundary. All nine independent restore checks gave maximum logit error zero. The original error records and the recovered results retain separate identities in the campaign report.

The attached report is the source for this replication's numerical tables. Its linked evaluation JSON, protocol, logs and checkpoints are listed individually in REPLICATION_SOURCE_MAP.csv with their current availability. The report documents completed training and evaluation; file-level provenance is recorded separately from the scientific result.

