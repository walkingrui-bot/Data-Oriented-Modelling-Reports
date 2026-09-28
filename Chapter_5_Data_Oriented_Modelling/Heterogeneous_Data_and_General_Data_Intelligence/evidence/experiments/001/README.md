# 001 — Structured chemical signals

Synthetic experiment.

Three latent communication coordinates, three synthetic species and two environmental coordinates generate five-signal episodes from a structured 60-molecule library. Ten combinations are held out; training uses 12,000 episodes and the other 50 molecules. Structure-aware recurrent and transformer predictors are compared with last-signal and shuffled-chemistry controls. The recorded outcomes include held-out ranking, receiver-response error, latent-state probes and response geometry.

Read [report section 3.3](../../../REPORT_EN.md#33-semiotic-chem-001-predictive-states-in-structured-chemical-signals) for the full methods, comparisons and interpretation.

## Evidence

Result tables, simulation specification and model checkpoint.

Report tables: [8](../../../evidence/report_tables/table_08.csv), [9](../../../evidence/report_tables/table_09.csv).

Report figures: [3](../../../figures/figure_03.png).

| File | Contents |
| --- | --- |
| [GRU_state_control_geometry.csv](GRU_state_control_geometry.csv) | Derived result or metadata |
| [experiment_spec.json](experiment_spec.json) | Derived result or metadata |
| [latent_communication_state_probe.csv](latent_communication_state_probe.csv) | Derived result or metadata |
| [models_and_config.pt](models_and_config.pt) | Synthetic model checkpoint |
| [molecule_library.csv](molecule_library.csv) | Authored synthetic design |
| [receiver_response_prediction.csv](receiver_response_prediction.csv) | Derived result or metadata |
| [seen_signal_prediction.csv](seen_signal_prediction.csv) | Derived result or metadata |
| [zero_shot_heldout_molecules_by_prefix.csv](zero_shot_heldout_molecules_by_prefix.csv) | Derived result or metadata |
| [zero_shot_postprefix_summary.csv](zero_shot_postprefix_summary.csv) | Derived result or metadata |

Execution details and input contracts are in the [reproduction guide](../../../REPRODUCTION_GUIDE.md).
