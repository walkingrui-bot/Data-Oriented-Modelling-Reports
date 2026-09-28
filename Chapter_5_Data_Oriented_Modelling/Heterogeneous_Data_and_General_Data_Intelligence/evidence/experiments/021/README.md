# 021 — Source-native representations

Synthetic experiment.

The recurrent modular design is reused with source-specific adapters and decoders for continuous trajectories, categorical events, unordered point sets and relational graphs. Each source has its own trained model and native scoring rule. Graph controls retain node identity and extend training duration. The report’s final graph row uses graph_long_training_audit.csv.

Read [report section 8.1](../../../REPORT_EN.md#81-multi-source-data-battery-021-one-core-across-data-structures) for the full methods, comparisons and interpretation.

## Evidence

Initial, graph-adapter and longer-training result tables and figures.

Report tables: [72](../../../evidence/report_tables/table_72.csv), [73](../../../evidence/report_tables/table_73.csv), [74](../../../evidence/report_tables/table_74.csv), [75](../../../evidence/report_tables/table_75.csv), [76](../../../evidence/report_tables/table_76.csv).

Report figures: [50](../../../figures/figure_50.png).

| File | Contents |
| --- | --- |
| [all_runs.csv](all_runs.csv) | Derived result or metadata |
| [cross_source_gain.png](cross_source_gain.png) | Scientific figure |
| [cross_source_lesion.png](cross_source_lesion.png) | Scientific figure |
| [cross_source_scorecard.csv](cross_source_scorecard.csv) | Derived result or metadata |
| [final_cross_source_scorecard.csv](final_cross_source_scorecard.csv) | Derived result or metadata |
| [graph_adapter_repair_runs.csv](graph_adapter_repair_runs.csv) | Derived result or metadata |
| [graph_adapter_repair_scorecard.csv](graph_adapter_repair_scorecard.csv) | Derived result or metadata |
| [graph_adapter_repair_summary.csv](graph_adapter_repair_summary.csv) | Derived result or metadata |
| [graph_long_training_audit.csv](graph_long_training_audit.csv) | Derived result or metadata |
| [graph_long_training_runs.csv](graph_long_training_runs.csv) | Derived result or metadata |
| [graph_long_training_summary.csv](graph_long_training_summary.csv) | Derived result or metadata |
| [regression_gates.csv](regression_gates.csv) | Derived result or metadata |
| [summary.csv](summary.csv) | Derived result or metadata |

Table 73 uses `cross_source_scorecard.csv`; Table 74 uses `graph_adapter_repair_summary.csv`; Tables 75–76 and report Figure 50 use the longer-training graph results. The filenames distinguish the three stages.

Execution details and input contracts are in the [reproduction guide](../../../REPRODUCTION_GUIDE.md).
