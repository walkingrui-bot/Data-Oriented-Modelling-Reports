# 026 — Corpus placement and retrieval coordination

Authored corpus and measured execution.

A frozen 134-page research document supplies 372 state objects, 500 deterministic queries and 30,000 TF-IDF features. Placement and routing comparisons use 2, 4, 8 or 16 logical shards. Process benchmarks run on one host. Reference agreement is measured against centralized TF-IDF retrieval. The frozen document predates the publication report; saved numeric state is supplied in 027.

Read [report section 9.1](../../../REPORT_EN.md#91-distributed-ontology-coordination-026-one-logical-corpus-across-physical-owners) for the full methods, comparisons and interpretation.

## Evidence

Derived summaries, figures and corpus-processing/benchmark code.

Report tables: [87](../../../evidence/report_tables/table_87.csv), [88](../../../evidence/report_tables/table_88.csv), [89](../../../evidence/report_tables/table_89.csv).

Report figures: [69](../../../figures/figure_69.png), [70](../../../figures/figure_70.png), [71](../../../figures/figure_71.png), [72](../../../figures/figure_72.png), [73](../../../figures/figure_73.png).

| File | Contents |
| --- | --- |
| [do026_balanced_sharding.csv](do026_balanced_sharding.csv) | Derived result or metadata |
| [do026_centroid_routing.csv](do026_centroid_routing.csv) | Derived result or metadata |
| [do026_compact_router.csv](do026_compact_router.csv) | Derived result or metadata |
| [do026_envelope_routing.csv](do026_envelope_routing.csv) | Derived result or metadata |
| [do026_process_benchmark.csv](do026_process_benchmark.csv) | Derived result or metadata |
| [do026_routed_process_benchmark.csv](do026_routed_process_benchmark.csv) | Derived result or metadata |
| [do026_sharding.csv](do026_sharding.csv) | Derived result or metadata |
| [do026_summary_final.json](do026_summary_final.json) | Derived result or metadata |
| [do026_workload_summary.csv](do026_workload_summary.csv) | Derived result or metadata |
| [fig026A_partition_pareto.png](fig026A_partition_pareto.png) | Scientific figure |
| [fig026B_compact_routing.png](fig026B_compact_routing.png) | Scientific figure |
| [fig026C_process_throughput.png](fig026C_process_throughput.png) | Scientific figure |
| [fig026D_coordinator_state.png](fig026D_coordinator_state.png) | Scientific figure |
| [fig026E_batching.png](fig026E_batching.png) | Scientific figure |
| [run_026.py](run_026.py) | Analysis code |
| [run_026b.py](run_026b.py) | Analysis code |
| [run_026c.py](run_026c.py) | Analysis code |
| [run_026d.py](run_026d.py) | Analysis code |

The frozen 372-object numeric workload is in [study 027](../027/README.md). Corpus-building scripts accept `B3_CORPUS_DOCX`; the published English report is a separate text snapshot. Benchmark scripts can read the saved numeric workload directly.

Execution details and input contracts are in the [reproduction guide](../../../REPRODUCTION_GUIDE.md).
