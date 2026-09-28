# 013 — Event timing and physical forecast horizons

Synthetic experiment.

Asynchronous environmental and biomarker observations are represented as fixed 0.5-unit buckets or raw event sequences, with or without timing. Every example uses a common history and a forecast horizon of +1.0 time unit. Density scans and a separate timing-identification control distinguish sampling support from information carried by elapsed time.

Read [report section 6.4](../../../REPORT_EN.md#64-continuous-time-event-carrier-graph-013-observation-events-and-physical-time) for the full methods, comparisons and interpretation.

## Evidence

Result tables, sampling-density and timing controls and figures.

Report tables: [48](../../../evidence/report_tables/table_48.csv), [49](../../../evidence/report_tables/table_49.csv), [50](../../../evidence/report_tables/table_50.csv).

Report figures: [33](../../../figures/figure_33.png), [34](../../../figures/figure_34.png).

| File | Contents |
| --- | --- |
| [all_runs.csv](all_runs.csv) | Derived result or metadata |
| [architecture_comparison.csv](architecture_comparison.csv) | Derived result or metadata |
| [event_vs_bucket.png](event_vs_bucket.png) | Scientific figure |
| [latent_probe.png](latent_probe.png) | Scientific figure |
| [model_summary.csv](model_summary.csv) | Derived result or metadata |
| [sampling_density_scan.csv](sampling_density_scan.csv) | Derived result or metadata |
| [sampling_density_scan_summary.csv](sampling_density_scan_summary.csv) | Derived result or metadata |
| [sampling_density_threshold.png](sampling_density_threshold.png) | Scientific figure |
| [timing_identifiability_runs.csv](timing_identifiability_runs.csv) | Derived result or metadata |
| [timing_identifiability_summary.csv](timing_identifiability_summary.csv) | Derived result or metadata |

Execution details and input contracts are in the [reproduction guide](../../../REPRODUCTION_GUIDE.md).
