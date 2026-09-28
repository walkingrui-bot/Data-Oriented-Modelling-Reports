# 024 — Active relation fields and observation gaps

Empirical derived analysis.

Email-Eu-core-temporal contains 332,334 directed events among 986 users. The timestamp audit identifies a 271.816-day gap; the primary analysis uses complete windows inside the preceding continuous segment. Neighbour coverage, node and dyad state spectra, degree strata and partition persistence are measured. The supplied script implements gap selection, state matrices, spectra and continuity calculations.

Read [report section 8.4](../../../REPORT_EN.md#84-real-graph-active-field-geometry-024-static-neighbourhoods-active-relations-and-time-scale-separation) for the full methods, comparisons and interpretation.

## Evidence

Derived summaries, source identities, figures and executable core definitions.

Report tables: [82](../../../evidence/report_tables/table_82.csv), [83](../../../evidence/report_tables/table_83.csv), [84](../../../evidence/report_tables/table_84.csv), [85](../../../evidence/report_tables/table_85.csv).

Report figures: [58](../../../figures/figure_58.png), [59](../../../figures/figure_59.png), [60](../../../figures/figure_60.png), [61](../../../figures/figure_61.png), [62](../../../figures/figure_62.png), [63](../../../figures/figure_63.png).

| File | Contents |
| --- | --- |
| [active_neighbour_scale.csv](active_neighbour_scale.csv) | Derived result or metadata |
| [analysis_method.py](analysis_method.py) | Analysis code |
| [community_activity_30d.csv](community_activity_30d.csv) | Derived result or metadata |
| [degree_strata_30d.csv](degree_strata_30d.csv) | Derived result or metadata |
| [fig024A_time_axis_gap.png](fig024A_time_axis_gap.png) | Scientific figure |
| [fig024B_active_neighbour_coverage.png](fig024B_active_neighbour_coverage.png) | Scientific figure |
| [fig024C_temporal_continuity.png](fig024C_temporal_continuity.png) | Scientific figure |
| [fig024D_effective_rank.png](fig024D_effective_rank.png) | Scientific figure |
| [fig024E_degree_strata.png](fig024E_degree_strata.png) | Scientific figure |
| [fig024F_partition_retention.png](fig024F_partition_retention.png) | Scientific figure |
| [gap_diagnostics.csv](gap_diagnostics.csv) | Derived result or metadata |
| [legacy_vs_gapaware_30d.csv](legacy_vs_gapaware_30d.csv) | Derived result or metadata |
| [paired_continuity_30d.csv](paired_continuity_30d.csv) | Derived result or metadata |
| [paired_partition_persistence_30d.csv](paired_partition_persistence_30d.csv) | Derived result or metadata |
| [source_identity_validation.json](source_identity_validation.json) | Derived result or metadata |
| [source_provenance.json](source_provenance.json) | Derived result or metadata |
| [temporal_state_geometry.csv](temporal_state_geometry.csv) | Derived result or metadata |
| [window_activity_30d_all.csv](window_activity_30d_all.csv) | Derived result or metadata |

The executable core covers gap detection, windowed matrices, spectra and continuity. Other released tables supply the recorded coverage, community and bootstrap results. External timestamped events are obtained separately from the source in `source_provenance.json`.

Execution details and input contracts are in the [reproduction guide](../../../REPRODUCTION_GUIDE.md).
