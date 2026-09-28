# 010 — Persistent carrier tracking and sparse anchors

Synthetic experiment.

Three persistent carriers generate source, environmental, biomarker and pathogen-like burdens through fixed measurement signatures across training and evaluation. Kinetics and signature overlap are varied. The archive includes latent probes, event-gated assimilation, multi-horizon objectives and sparse source-resolved anchor losses. Table 42 has two documented final-digit rounding differences.

Read [report section 6.1](../../../REPORT_EN.md#61-tracking-mechanism-data-010-persistent-carriers-kinetics-and-identity) for the full methods, comparisons and interpretation.

## Evidence

Result tables for the fixed-measurement and anchor comparisons and figures.

Report tables: [42](../../../evidence/report_tables/table_42.csv), [43](../../../evidence/report_tables/table_43.csv).

Report figures: [26](../../../figures/figure_26.png), [27](../../../figures/figure_27.png).

| File | Contents |
| --- | --- |
| [all_runs.csv](all_runs.csv) | Derived result or metadata |
| [anchor_multihorizon_effects.csv](anchor_multihorizon_effects.csv) | Derived result or metadata |
| [anchor_multihorizon_runs.csv](anchor_multihorizon_runs.csv) | Derived result or metadata |
| [anchor_multihorizon_summary.csv](anchor_multihorizon_summary.csv) | Derived result or metadata |
| [event_gated_runs.csv](event_gated_runs.csv) | Derived result or metadata |
| [event_gated_summary.csv](event_gated_summary.csv) | Derived result or metadata |
| [latent_tracking_corrected.png](latent_tracking_corrected.png) | Scientific figure |
| [model_summary.csv](model_summary.csv) | Derived result or metadata |
| [slot_specialization.csv](slot_specialization.csv) | Derived result or metadata |
| [sparse_anchor_supervision.png](sparse_anchor_supervision.png) | Scientific figure |
| [sparse_anchor_supervision_runs.csv](sparse_anchor_supervision_runs.csv) | Derived result or metadata |
| [sparse_anchor_supervision_summary.csv](sparse_anchor_supervision_summary.csv) | Derived result or metadata |
| [tracking_state_recovery.png](tracking_state_recovery.png) | Scientific figure |

Two rounding annotations for Table 42 are documented in [Publication notes](../../../PUBLICATION_NOTES.md).

Execution details and input contracts are in the [reproduction guide](../../../REPRODUCTION_GUIDE.md).
