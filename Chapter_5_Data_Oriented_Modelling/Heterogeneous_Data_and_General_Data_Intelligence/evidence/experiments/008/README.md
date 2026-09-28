# 008 — Mechanism drift and routing freshness

Synthetic experiment.

The observation manifold stays fixed across six eras while the transition operator changes by 0.32 radians per era. One comparison retrains experts using current or stale maps. A separate intervention holds the expert functions fixed and replaces only the router. These comparisons answer different questions and have separate summary files.

Read [report section 5.6](../../../REPORT_EN.md#56-generative-manifold-drift-008-routing-under-changing-transition-functions) for the full methods, comparisons and interpretation.

## Evidence

Result tables for both interventions and figures.

Report tables: [38](../../../evidence/report_tables/table_38.csv), [39](../../../evidence/report_tables/table_39.csv).

Report figures: [22](../../../figures/figure_22.png), [23](../../../figures/figure_23.png).

| File | Contents |
| --- | --- |
| [all_runs.csv](all_runs.csv) | Derived result or metadata |
| [drift_performance.png](drift_performance.png) | Scientific figure |
| [drift_summary.csv](drift_summary.csv) | Derived result or metadata |
| [map_migration.png](map_migration.png) | Scientific figure |
| [strict_routing_intervention_runs.csv](strict_routing_intervention_runs.csv) | Derived result or metadata |
| [strict_routing_intervention_summary.csv](strict_routing_intervention_summary.csv) | Derived result or metadata |
| [strict_stale_routing_penalty.png](strict_stale_routing_penalty.png) | Scientific figure |

Execution details and input contracts are in the [reproduction guide](../../../REPRODUCTION_GUIDE.md).
