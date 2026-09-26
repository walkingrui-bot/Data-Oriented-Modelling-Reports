# Engineering interfaces for Chapter 3

This guide integrates the two supplied local READMEs with the executable cloud atlas. The current English report explains the measured behavior and component corrections. `LOCAL_SOURCE_MAP.csv` records whether each cited local file is present in this collection.

## Included token operator runtime

The recovered NumPy runtime and its state bank are included. From the release root:

```sh
cd evidence/cloud/01_Experiments/03_TOKEN_OPERATOR_ATLAS_001
python3 TOKEN_OPERATOR_ATLAS_001_os.py list
python3 TOKEN_OPERATOR_ATLAS_001_os.py card B
python3 TOKEN_OPERATOR_ATLAS_001_os.py apply B --state-id 54
python3 TOKEN_OPERATOR_ATLAS_001_os.py compare B result --state-id 54
python3 TOKEN_OPERATOR_ATLAS_001_os.py compose "A,0,xor,B" --state-id 54
python3 TOKEN_OPERATOR_ATLAS_001_os.py order B result --state-id 54
```

Python 3 and NumPy are sufficient for this entry point. The saved states have IDs 0–351. Custom input uses `--h` with ten comma-separated numbers. The recovered-model calibration and exact runtime-to-table check are separate results in the report.

## Reported local diagnostics

Study MCD-ENGINEERING-20260926-001 supplies the following interface specification for `mcd.py`. The supplied report records 15 targeted contract tests.

```sh
python3 mcd.py diagnose incident.json
python3 mcd.py radius telemetry.json
python3 mcd.py guard domain.json
```

Input errors return `INVALID_INPUT` with exit code 2. Normal diagnostic completion returns exit code 0. The output is a diagnostic or submitted-contract result; the host has the execution interface.

### Diagnose

Required input fields are `score_unit` and `candidates`. Each candidate has a unique `id` and finite scores for `full`, `name_neutral`, `description_neutral`, and `schema_neutral`. All scores share a model and scoring convention. The reported pretrained example uses equal-length candidate-label next-token log probabilities.

An optional `correct_id` is used for retrospective assessment. Outputs retain tied winners, changes for every competitor, and actual first place across the candidate set. Missing views, nonfinite values, and duplicate IDs receive an input rejection. Input-intervention sensitivity describes the observed comparison.

### Radius

The input identifies `model_revision`, `checkpoint`, `score_unit`, and `coordinate_system`. Each action has `id`, `score`, `gradient`, and `admissible`. Gradients have a common dimension and the host supplies admissibility.

The calculation considers every admissible competitor. Optional calibration carries the same four provenance fields, `n`, and `warning_floor`. A provenance mismatch is rejected. An uncalibrated measurement returns `UNCALIBRATED`; a zero gradient difference is marked first-order unidentifiable. The output records `certified: false` for the local approximation.

### Guard

Input comprises `registry`, `context`, and `proposal`. A registry tool has `schema` and `permissions`. Trusted context supplies `snapshot_id`, permission receipts, and precondition receipts. Parallel calls require `parallel_independent: true`. The proposal contains the same snapshot, a mode, and calls with `name` and `arguments`.

The supported subset has explicit types: closed objects, arrays and their items, strings, booleans, null, finite numbers, strict integers, enums, minimum/maximum, and minItems/maxItems. Unsupported keywords and types are rejected. Description is annotation. The host explicitly converts any external schema conventions such as BFCL `dict` or `float` labels.

Checks cover registry membership, bindings, schema values, receipts, snapshot identity, empty CALL, calls accompanying a no-operation mode, duplicate calls, and parallel conditions. The host supplies actual environment verification, intent and scope, authentication, audit, and revalidation at atomic execution. `hard_domain_admissible: true` reports satisfaction of the submitted local contract.

### Inspect the reported pretrained case

In the original project environment, the reported command is:

```sh
.venv-neural/bin/python research/records/MCD-ENGINEERING-20260926-001/inspect_case.py --case multiple_23 --posthoc
```

Omitting `--posthoc` gives the unknown-answer diagnostic form. `analyze_probe.py` recomputes summaries from the existing score record. The study’s `pretrained_probe.py --phase main` and patch script use exclusive result creation. Further experiments require a new run identity and output paths.

The local test entry point is:

```sh
.venv-neural/bin/python -m unittest discover -s research/records/MCD-ENGINEERING-20260926-001 -p test_mcd.py -v
```

## Reported local selector

Study MCD-SELECTION-20260926-002 describes `selector.py`. The report records ten local contract tests. The interface independently scores the query against each tool’s capability document and returns the canonical name.

```sh
.venv-neural/bin/python research/records/MCD-SELECTION-20260926-002/selector.py --case multiple_60
.venv-neural/bin/python research/records/MCD-SELECTION-20260926-002/selector.py --case multiple_60 --method lexical
.venv-neural/bin/python research/records/MCD-SELECTION-20260926-002/selector.py --case multiple_153 --policy research/records/MCD-SELECTION-20260926-002/policy.json
.venv-neural/bin/python research/records/MCD-SELECTION-20260926-002/selector.py /absolute/path/request.json
```

`--method rerank_description` is the development-stage description-only variant. The default relevance method uses the full tool document. The original host environment uses an existing `.venv-neural`, float32 MPS with CPU fallback, and four CPU threads.

### Request and response

The request has a nonempty `query` string and `tools` array. Each tool has a unique nonempty `name`, nonempty `description`, and object-valued `parameters`. The evaluated requests and descriptions are English.

Outputs include `diagnostic`, `candidate_scores`, and `telemetry`. Empty candidates produce `NO_CANDIDATES`. A top-score tie produces `TIED` with an empty selection. Otherwise the output is `RANKED` with the canonical name. Relevance logits and lexical cosines retain their respective units.

The default recommendation is `RANKING_ONLY_UNCALIBRATED`. An explicit policy matched to the model revision and method produces `CANDIDATE_FOR_BINDING` or `ABSTAIN_UNCERTAIN`, with `executes_tools: false`. The diagnostic `selected` field may retain a top candidate during abstention; the caller uses `recommendation` to choose the next step.

The experimental policy was calibrated on 30 original tasks plus 30 gold-removal conditions. It has 38% coverage on the frozen 100-task set and 5% on the forty paraphrases. Those are measured properties of this particular policy and task material. Missing arguments lead to clarification after a relevant candidate has been identified.

The documented 512-token truncation strategy retains the query and cuts the candidate-document tail, recording the event in telemetry. Overlong queries follow the tokenizer’s error path. Empty queries, duplicate names, and invalid scores are rejected.

### Model and data identities

| Role | Official model | Pinned revision |
| --- | --- | --- |
| Original instruction model | HuggingFaceTB/SmolLM2-135M-Instruct | `12fd25f77366fa6b3b4b768ec3050bf629380bac` |
| Relevance ranker | cross-encoder/ms-marco-MiniLM-L6-v2 | `233902d25c440f23af6f7d6e94d2946bac0bee0a` |

The author’s model cache holds one copy of each referenced checkpoint. The relevance loader uses local files and disables remote code. BFCL task and answer files are referenced from the parent local study. The lexical IDF uses development-task candidate descriptions and therefore also depends on that original input file.

`FROZEN_PROTOCOL.md`, `test_scores.jsonl`, `test_summary.json`, `control_scores.jsonl`, `policy.json`, and `dev_segments.json` identify the main comparison records. `compare.py`, `study_analysis.py`, and `controls.py` identify the scoring and analysis implementation. The child MCD-SEMANTIC-STRESS-20260926-003 study has its own report reference.

The local selector test command is:

```sh
.venv-neural/bin/python research/records/MCD-SELECTION-20260926-002/test_selector.py
```

The source logs retain the original base-Python smoke-test error and the corrected environment entry point. Timing is recorded in a separate warmed sequential study. The two READMEs and two terminal reports are the local source documents supplied with this release.
