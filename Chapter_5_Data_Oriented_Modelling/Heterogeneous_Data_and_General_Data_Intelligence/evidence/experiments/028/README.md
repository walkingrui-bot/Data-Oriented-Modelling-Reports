# 028 — Persistent coordination and state versions

Authored corpus with controlled stress.

Eight persistent workers execute 240 query-derived task plans per coordinator condition. The schedule includes owner loss, recovery, a delayed shard and version conflicts. Adaptive routing, replica budget and commit discipline are recorded separately. Acceptance, retrieval coverage, internal write accounting and final-state agreement against the centralized reference are distinct outcomes.

Read [report section 9.3](../../../REPORT_EN.md#93-distributed-ontology-plan-continuation-028-task-continuity-across-faults-and-version-changes) for the full methods, comparisons and interpretation.

## Evidence

Plan traces, summary tables, figures and coordinator code.

Report tables: [93](../../../evidence/report_tables/table_93.csv), [94](../../../evidence/report_tables/table_94.csv).

Report figures: [79](../../../figures/figure_79.png), [80](../../../figures/figure_80.png), [81](../../../figures/figure_81.png), [82](../../../figures/figure_82.png), [83](../../../figures/figure_83.png), [84](../../../figures/figure_84.png).

| File | Contents |
| --- | --- |
| [do028_phase_summary.csv](do028_phase_summary.csv) | Derived result or metadata |
| [do028_plan_trace.csv](do028_plan_trace.csv) | Derived result or metadata |
| [do028_policy_summary.csv](do028_policy_summary.csv) | Derived result or metadata |
| [do028_summary.json](do028_summary.json) | Derived result or metadata |
| [fig028A_plan_acceptance.png](fig028A_plan_acceptance.png) | Scientific figure |
| [fig028B_phase_recall.png](fig028B_phase_recall.png) | Scientific figure |
| [fig028C_phase_latency.png](fig028C_phase_latency.png) | Scientific figure |
| [fig028D_versioning_control.png](fig028D_versioning_control.png) | Scientific figure |
| [fig028E_reference_state_error.png](fig028E_reference_state_error.png) | Scientific figure |
| [fig028F_pending_log.png](fig028F_pending_log.png) | Scientific figure |
| [run_028.py](run_028.py) | Analysis code |

Read the frozen numeric input from [study 027](../027/README.md). The plan trace records 240 plans for each of four policies (960 rows).

Execution details and input contracts are in the [reproduction guide](../../../REPRODUCTION_GUIDE.md).
