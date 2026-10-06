# Evidence index

[Chapter 8](README.md) · [English report](REPORT_EN.md)

The records below support the experiments reviewed in Chapter 8. They retain their original experimental values. The publication work translated and organized the report and redrew the figures from recorded values; it did not retrain the models or repeat the experiments.

| Study | Question and evaluation | Main record |
| --- | --- | --- |
| EXP001 | Can an explicit plan be calibrated? Synthetic contexts; test plans; presentation shuffles | [Record](evidence/EXP001/TINY_BLUEPRINT_EXP001_REPORT.md) |
| EXP002 | Can current relations construct the plan? Rule permutation (2, 1, 0) held out | [Record](evidence/EXP002/TINY_BLUEPRINT_EXP002_CONTEXT_BUILT_REPORT.md) |
| EXP003 | Does a latent plan transfer to an unseen rule? Preliminary values retained from the final manuscript | [Record](REPORT_EN.md#2-a-blueprint-learned-without-blueprint-labels) |
| EXP003B | Can answers alone teach a transferable procedure? Fresh contexts and payloads; 3,000 donor transfers | [Record](evidence/EXP003B/TINY_BLUEPRINT_EXP003B_LATENT_BLUEPRINT_REPORT.md) |
| EXP004 and B/C | Where does joint readout appear and what carries control? Frozen probes, donor states, coordinate and fact interventions | [Record](evidence/EXP004/TINY_BLUEPRINT_EXP004_FORMATION_LOCALIZATION.md) |
| EXP005 | Can an explicit program reproduce network behavior? 52,272 valid inputs; reported exhaustive equivalence | [Record](evidence/EXP005/TINY_BLUEPRINT_EXP005_NEURAL_NETWORK_DECOMPILATION.md) |
| GRU_SINGLE | How are shuffled facts assembled into an ordered program? 4,992 valid inputs; layer transplants and slot edits | [Record](evidence/GRU_SINGLE/PROGRAM_GRU_SINGLE_OBJECTIVE_DECOMPILATION_REPORT.md) |
| GRU_COMPETING | What survives conflicting objectives? Task-cued control; conflict gradients and paired output branches | [Record](evidence/GRU_COMPETING/TWO_GOAL_BLUEPRINT_COMPETITION_REPORT.md) |
| TRANSFORMER | How do context, positions and emitted state coordinate execution? Activation patching; forward/reverse traces; state edits; compositional holdout | [Record](evidence/TRANSFORMER/TRANSFORMER_BLUEPRINT_COT_DECOMPILATION_REPORT.md) |
| CURRICULUM | Does early training change execution readiness and order? Matched initialization and final training; independent-seed checks | [Record](evidence/CURRICULUM/TRAINING_ORDER_BLUEPRINT_FRONTLOADING_REPORT.md) |
| SERIALIZATION | How does answer placement interact with causal prerequisites? R2A/A2R comparisons; three dependent-task seeds; marker and value interventions | [Record](evidence/SERIALIZATION/SERIALIZATION_POLICY_OPERATOR_PRECEDENCE_REPORT.md) |

## Archived files

### EXP001

- [TINY_BLUEPRINT_EXP001_REPORT.md](evidence/EXP001/TINY_BLUEPRINT_EXP001_REPORT.md)
- [tiny_blueprint_exp001.py](evidence/EXP001/tiny_blueprint_exp001.py)

### EXP002

- [TINY_BLUEPRINT_EXP002_CONTEXT_BUILT_REPORT.md](evidence/EXP002/TINY_BLUEPRINT_EXP002_CONTEXT_BUILT_REPORT.md)
- [tiny_blueprint_exp002_context_built.pt](evidence/EXP002/tiny_blueprint_exp002_context_built.pt)

### EXP003B

- [TINY_BLUEPRINT_EXP003B_LATENT_BLUEPRINT_REPORT.md](evidence/EXP003B/TINY_BLUEPRINT_EXP003B_LATENT_BLUEPRINT_REPORT.md)
- [TINY_BLUEPRINT_EXP003B_CONTROLS.md](evidence/EXP003B/TINY_BLUEPRINT_EXP003B_CONTROLS.md)
- [tiny_blueprint_exp003b_latent_blueprint.pt](evidence/EXP003B/tiny_blueprint_exp003b_latent_blueprint.pt)

### EXP004

- [TINY_BLUEPRINT_EXP004_FORMATION_LOCALIZATION.md](evidence/EXP004/TINY_BLUEPRINT_EXP004_FORMATION_LOCALIZATION.md)
- [TINY_BLUEPRINT_EXP004B_INTERNAL_LOCATION.md](evidence/EXP004/TINY_BLUEPRINT_EXP004B_INTERNAL_LOCATION.md)
- [TINY_BLUEPRINT_EXP004C_BIRTH_OPERATOR.md](evidence/EXP004/TINY_BLUEPRINT_EXP004C_BIRTH_OPERATOR.md)

### EXP005

- [TINY_BLUEPRINT_EXP005_NEURAL_NETWORK_DECOMPILATION.md](evidence/EXP005/TINY_BLUEPRINT_EXP005_NEURAL_NETWORK_DECOMPILATION.md)
- [TINY_BLUEPRINT_EXP005A_PARAMETER_PROGRAM_EXTRACTION.json](evidence/EXP005/TINY_BLUEPRINT_EXP005A_PARAMETER_PROGRAM_EXTRACTION.json)
- [decompiled_tiny_blueprint_algorithm.py](evidence/EXP005/decompiled_tiny_blueprint_algorithm.py)

### GRU_SINGLE

- [PROGRAM_GRU_SINGLE_OBJECTIVE_DECOMPILATION_REPORT.md](evidence/GRU_SINGLE/PROGRAM_GRU_SINGLE_OBJECTIVE_DECOMPILATION_REPORT.md)
- [PROGRAM_GRU_BLUEPRINT_LOCALIZATION.json](evidence/GRU_SINGLE/PROGRAM_GRU_BLUEPRINT_LOCALIZATION.json)
- [decompiled_program_gru_algorithm.py](evidence/GRU_SINGLE/decompiled_program_gru_algorithm.py)
- [program_gru_single_objective.pt](evidence/GRU_SINGLE/program_gru_single_objective.pt)

### GRU_COMPETING

- [TWO_GOAL_BLUEPRINT_COMPETITION_REPORT.md](evidence/GRU_COMPETING/TWO_GOAL_BLUEPRINT_COMPETITION_REPORT.md)
- [TWO_GOAL_SINGLE_HEAD_BLUEPRINT_ANALYSIS.json](evidence/GRU_COMPETING/TWO_GOAL_SINGLE_HEAD_BLUEPRINT_ANALYSIS.json)
- [PARTIAL_CONFLICT_BLUEPRINT_ANALYSIS.json](evidence/GRU_COMPETING/PARTIAL_CONFLICT_BLUEPRINT_ANALYSIS.json)
- [program_gru_two_competing_goals_single_head.pt](evidence/GRU_COMPETING/program_gru_two_competing_goals_single_head.pt)
- [program_gru_partially_conflicting_objectives.pt](evidence/GRU_COMPETING/program_gru_partially_conflicting_objectives.pt)

### TRANSFORMER

- [TRANSFORMER_BLUEPRINT_COT_DECOMPILATION_REPORT.md](evidence/TRANSFORMER/TRANSFORMER_BLUEPRINT_COT_DECOMPILATION_REPORT.md)
- [TRANSFORMER_CAUSAL_BLUEPRINT_PATCHING.json](evidence/TRANSFORMER/TRANSFORMER_CAUSAL_BLUEPRINT_PATCHING.json)
- [TRANSFORMER_ATTENTION_EXECUTION_ROUTING.json](evidence/TRANSFORMER/TRANSFORMER_ATTENTION_EXECUTION_ROUTING.json)
- [TRANSFORMER_COT_STATE_INTERVENTION.json](evidence/TRANSFORMER/TRANSFORMER_COT_STATE_INTERVENTION.json)
- [TRANSFORMER_REVERSE_TRACE_DIAGNOSIS.json](evidence/TRANSFORMER/TRANSFORMER_REVERSE_TRACE_DIAGNOSIS.json)
- [recovered_transformer_execution_schedule.py](evidence/TRANSFORMER/recovered_transformer_execution_schedule.py)

### CURRICULUM

- [TRAINING_ORDER_BLUEPRINT_FRONTLOADING_REPORT.md](evidence/CURRICULUM/TRAINING_ORDER_BLUEPRINT_FRONTLOADING_REPORT.md)

### SERIALIZATION

- [SERIALIZATION_POLICY_OPERATOR_PRECEDENCE_REPORT.md](evidence/SERIALIZATION/SERIALIZATION_POLICY_OPERATOR_PRECEDENCE_REPORT.md)
- [DEPENDENT_R2A_FRONT_STABILITY_METRICS.json](evidence/SERIALIZATION/DEPENDENT_R2A_FRONT_STABILITY_METRICS.json)
- [SERIALIZATION_CAUSAL_ASYMMETRY.json](evidence/SERIALIZATION/SERIALIZATION_CAUSAL_ASYMMETRY.json)
- [SERIALIZATION_RATIONALIZATION_AND_STABILITY.json](evidence/SERIALIZATION/SERIALIZATION_RATIONALIZATION_AND_STABILITY.json)
- [MARKER_VS_STATE_CAUSAL_TEST.json](evidence/SERIALIZATION/MARKER_VS_STATE_CAUSAL_TEST.json)

## Figures and tables

English figure data are in [figure_data](evidence/figure_data/). The source manuscript’s nine original images are in [source_figures](evidence/source_figures/). [Report tables](evidence/report_tables/) include the complete proposition-review matrix as CSV. Figure numbers and captions are recorded in [Figure_Index.csv](Figure_Index.csv).

## Interpretation of availability

EXP003’s preliminary holdout values and the 18,432-parameter count for the flexible-order model are retained from the final manuscript. A separate EXP003 result file and a separate architecture record for that parameter count were not recovered. The supporting EXP003B controls, curriculum report and other listed measurements are included. The recovered Transformer schedule is an explicit description of the measured forward execution loop; it is distinct from the exhaustive network-equivalence results reported for EXP005 and the single-objective GRU.

Checkpoint files are the archived synthetic-task models. They have been preserved byte-for-byte; they were not executed during preparation of this edition.
