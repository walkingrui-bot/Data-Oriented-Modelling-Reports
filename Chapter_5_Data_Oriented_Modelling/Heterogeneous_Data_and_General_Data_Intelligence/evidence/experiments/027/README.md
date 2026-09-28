# 027 — Replication, delayed workers and concurrent updates

Authored corpus with controlled stress.

The frozen 372-object, 500-query workload and eight balanced shards are subjected to single-shard loss, an injected 350 ms delay and concurrent state updates. Selective and full one-backup replication are compared. The light straggler test precomputes retrieval and measures orchestration wait; the concurrent-write test compares update disciplines.

Read [report section 9.2](../../../REPORT_EN.md#92-distributed-ontology-resilience-027-replication-latency-and-concurrent-updates) for the full methods, comparisons and interpretation.

## Evidence

Frozen numeric workload, derived results, figures and calculation code.

Report tables: [90](../../../evidence/report_tables/table_90.csv), [91](../../../evidence/report_tables/table_91.csv), [92](../../../evidence/report_tables/table_92.csv).

Report figures: [74](../../../figures/figure_74.png), [75](../../../figures/figure_75.png), [76](../../../figures/figure_76.png), [77](../../../figures/figure_77.png), [78](../../../figures/figure_78.png).

| File | Contents |
| --- | --- |
| [do026_Q.npz](do026_Q.npz) | Authored frozen numeric workload |
| [do026_X.npz](do026_X.npz) | Authored frozen numeric workload |
| [do026_balanced_assign8.npy](do026_balanced_assign8.npy) | Authored frozen numeric workload |
| [do027_concurrent_updates.csv](do027_concurrent_updates.csv) | Derived result or metadata |
| [do027_failure_policy_summary.csv](do027_failure_policy_summary.csv) | Derived result or metadata |
| [do027_replication_storage.csv](do027_replication_storage.csv) | Derived result or metadata |
| [do027_single_shard_failure.csv](do027_single_shard_failure.csv) | Derived result or metadata |
| [do027_straggler_timeout.csv](do027_straggler_timeout.csv) | Derived result or metadata |
| [do027_summary.json](do027_summary.json) | Derived result or metadata |
| [do027_update_summary.csv](do027_update_summary.csv) | Derived result or metadata |
| [fig027A_redundancy_recovery.png](fig027A_redundancy_recovery.png) | Scientific figure |
| [fig027B_shard_failure_profile.png](fig027B_shard_failure_profile.png) | Scientific figure |
| [fig027C_straggler_tradeoff.png](fig027C_straggler_tradeoff.png) | Scientific figure |
| [fig027D_update_throughput.png](fig027D_update_throughput.png) | Scientific figure |
| [fig027E_update_loss.png](fig027E_update_loss.png) | Scientific figure |
| [summarize_027.py](summarize_027.py) | Analysis code |
| [run_027.py](run_027.py) | Analysis code |
| [run_027b_straggler_light.py](run_027b_straggler_light.py) | Analysis code |

`do026_X.npz` has shape 372 × 30,000; `do026_Q.npz` has shape 500 × 30,000; `do026_balanced_assign8.npy` holds 372 assignments to shards 0–7. These are numeric representations of the authored research corpus. `run_027b_straggler_light.py` produces the orchestration-wait comparison reported in Table 91.

Execution details and input contracts are in the [reproduction guide](../../../REPRODUCTION_GUIDE.md).
