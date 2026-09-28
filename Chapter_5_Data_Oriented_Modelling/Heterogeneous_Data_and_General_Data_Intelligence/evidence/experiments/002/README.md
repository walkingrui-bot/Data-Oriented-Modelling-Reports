# 002 — Generated rules and routed physical dynamics

Synthetic experiment.

A physical simulator supplies position, contact, deformation, visibility and object descriptors. Direct prediction, generated local rules and a mixture of rule experts are compared through one-step prediction and autoregressive rollout. Separate homogeneous-law and hidden heterogeneous-law conditions are retained. Uniform and shuffled routing interventions measure the contribution of the learned router.

Read [report section 3.7](../../../REPORT_EN.md#37-world-moe-002-routing-under-homogeneous-and-heterogeneous-transition-laws) for the full methods, comparisons and interpretation.

## Evidence

Result tables, summary metadata and figures.

Report tables: [15](../../../evidence/report_tables/table_15.csv), [16](../../../evidence/report_tables/table_16.csv), [17](../../../evidence/report_tables/table_17.csv).

Report figures: [5](../../../figures/figure_05.png), [6](../../../figures/figure_06.png).

| File | Contents |
| --- | --- |
| [heterogeneous_matched_budget.png](heterogeneous_matched_budget.png) | Scientific figure |
| [homogeneous_rollout.png](homogeneous_rollout.png) | Scientific figure |
| [homogeneous_world_rollout.csv](homogeneous_world_rollout.csv) | Derived result or metadata |
| [matched_budget_models.csv](matched_budget_models.csv) | Derived result or metadata |
| [router_ablation.csv](router_ablation.csv) | Derived result or metadata |
| [summary.json](summary.json) | Derived result or metadata |

Execution details and input contracts are in the [reproduction guide](../../../REPRODUCTION_GUIDE.md).
