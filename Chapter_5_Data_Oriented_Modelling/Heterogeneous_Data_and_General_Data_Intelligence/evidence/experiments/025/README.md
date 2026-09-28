# 025 — Temporal coarse-graining

Derived reanalysis of 024.

The five 7-, 14-, 30-, 60- and 90-day summaries from 024 are joined to calculate coverage, partner concentration, continuity and spectral ratios. Log-log slopes describe these five measured scales. The included analysis script reads the two released 024 summary tables, enabling this calculation directly from the package.

Read [report section 8.5](../../../REPORT_EN.md#85-real-graph-temporal-renormalization-025-what-time-coarse-graining-does-to-a-real-relation-field) for the full methods, comparisons and interpretation.

## Evidence

Derived tables, summary metadata, figures and analysis code.

Report tables: [86](../../../evidence/report_tables/table_86.csv).

Report figures: [64](../../../figures/figure_64.png), [65](../../../figures/figure_65.png), [66](../../../figures/figure_66.png), [67](../../../figures/figure_67.png), [68](../../../figures/figure_68.png).

| File | Contents |
| --- | --- |
| [analyze_025.py](analyze_025.py) | Analysis code |
| [fig025A_coverage_scaling.png](fig025A_coverage_scaling.png) | Scientific figure |
| [fig025B_partner_scaling.png](fig025B_partner_scaling.png) | Scientific figure |
| [fig025C_continuity_scaling.png](fig025C_continuity_scaling.png) | Scientific figure |
| [fig025D_turnover_scaling.png](fig025D_turnover_scaling.png) | Scientific figure |
| [fig025E_spectral_ratio.png](fig025E_spectral_ratio.png) | Scientific figure |
| [rg025_descriptive_logfits.csv](rg025_descriptive_logfits.csv) | Derived result or metadata |
| [rg025_multiscale_renormalization.csv](rg025_multiscale_renormalization.csv) | Derived result or metadata |
| [rg025_summary.json](rg025_summary.json) | Derived result or metadata |
| [source_024_hashes.csv](source_024_hashes.csv) | Derived result or metadata |

Execution details and input contracts are in the [reproduction guide](../../../REPRODUCTION_GUIDE.md).
