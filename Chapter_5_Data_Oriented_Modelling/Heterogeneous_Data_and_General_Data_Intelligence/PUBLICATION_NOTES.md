# Publication notes

This edition presents the research as Chapter 5, Report 01. The English Word report, its 84 figures and all 94 numerical and explanatory tables are retained. The web edition adds direct evidence links and the annotations below. The study identifiers connect the narrative to the supplied experiment records.

## Recorded-result reconciliation

The review matched 1,301 numeric cells across 73 result tables to specified archive rows and metrics. It checked stated seed means, percentage conversions, time units and display rounding. 1,299 cells agree within direct-rounding tolerance; two final-digit differences occur in Table 42.

| Table 42 condition and model | Retained report value | Archived rollout MSE | Direct three-decimal rounding |
| --- | --- | --- | --- |
| K0_O1 / Snapshot | 0.660 | 0.6594661474227905 | 0.659 |
| K1_O1 / SourceTracker | 0.844 | 0.8434720039367676 | 0.843 |

The source is [010/model_summary.csv](evidence/experiments/010/model_summary.csv), column `rollout_last_MSE`. The retained values and source precision are shown together so readers can use the appropriate precision. The cell-level record is [numeric_reconciliation.csv](verification/numeric_reconciliation.csv).

## Selecting the matching comparison

The gain-normalized 019 comparison uses `NormHealthy`, `NormLesion` and `NormFatigue` in [gain_normalization_comparison.csv](evidence/experiments/019/gain_normalization_comparison.csv). Its earlier gating comparison remains a separate recorded control. Report Figures 45–46 display the normalized comparison.

The graph row of Table 76 and Figure 50 uses [graph_long_training_audit.csv](evidence/experiments/021/graph_long_training_audit.csv). The file named `final_cross_source_scorecard.csv` records the preceding graph-adapter comparison. Table 73 records the initial comparison, Table 74 the node-identity adapter, and Table 75 the longer-training comparison. These stages are indexed separately.

The temporal email summaries in 023 use the full recorded span. Study 024 isolates the primary continuous segment before the 271.816-day gap and calculates complete-window statistics. Study 025 builds on the 024 definitions. Both observation-axis treatments are preserved with their source files.

## Figure and method coverage

Seventy-five report images are byte-identical to images in the supplied archives. Figures 3, 15, 16, 45, 46 and 50 retain their report-rendered form and have corresponding numeric tables in the supplied experiments. Figure 1 is a conceptual figure. Figures 2 and 4 belong to the report-only foundational studies. [FIGURE_MAP.csv](FIGURE_MAP.csv) records every case.

The six foundational studies listed in the [evidence index](EVIDENCE_INDEX.md) are supported here by their report methods, results, table transcriptions and available images. The independent experiment archives supplied for this edition cover 001–028, with the integrated prediction experiment identified as 018B. Availability of training code varies by study.

## Execution and data scope

The 026–028 workload is a frozen numeric representation of an authored 134-page research document: 372 objects and 500 query vectors. The publication Word file is a separate text snapshot. Saved matrices support the recorded downstream workload; corpus-extraction scripts specify a separately supplied source document. Retrieval agreement uses the centralized TF-IDF reference. Timing records describe the specified single-host processes and completion rules.

Empirical graph files in this publication are derived summaries and analysis outputs. The package includes synthetic experiment records, the synthetic model checkpoint and three authored-corpus numeric arrays. External provider edge lists, individual source records, source corpora and original timestamp streams are obtained separately using [Source availability](SOURCE_AVAILABILITY.md).

The code map identifies portability changes to input and output paths. Calculation code, figures and results are retained; document-assembly utilities and draft-writing sections are omitted from the public evidence directories. The executable core supplied for 024 covers gap detection, state matrices, spectral measures and continuity; the other 024 measurements are available as recorded outputs.
