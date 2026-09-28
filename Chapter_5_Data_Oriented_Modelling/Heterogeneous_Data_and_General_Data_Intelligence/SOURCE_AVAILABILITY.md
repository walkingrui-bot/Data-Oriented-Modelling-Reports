# Source availability

The released evidence consists of authored simulations, model outputs, aggregate empirical measurements, scientific figures, calculation code and numeric representations of the authored research corpus. External provider raw datasets are kept outside this publication.

| Study | Data used | Released material | Source identity or access route |
| --- | --- | --- | --- |
| HIER-STAT-001, STAT-SCALE-001, WORLD-RULE-001 | Authored simulators | Report results and table transcriptions | Methods in report sections 3.1, 3.2 and 3.6 |
| REAL-BIRD-001 | Recorded Bengalese finch syllable sequences | Report results and original figure | `NickleDave/pomma`, `bl26lb16_sequences.txt`, as cited in report section 4.7 |
| REAL-WAGGLE-001 | Honeybee waggle directions | Report results | `BioroboticsLab/WDD_paper`, `GroundTruthData/GTAverage.csv`, as cited in report section 4.7 |
| QS-GRAPH-001 | Quorum-sensing family and role records | Report aggregates | `qhmu/QSDB`, `data/QSDB_qsgroups.txt`, as cited in report section 4.7 |
| 001–021 | Authored synthetic worlds | Recorded results, controls, figures and available metadata; 001 includes synthetic descriptors and a model checkpoint | Per-study READMEs and report methods |
| 022 | Dolphins, Email-Eu-core, ca-GrQc, Facebook Combined, Cora | Graph-level measurements and figures | Dataset names and topology conventions in section 8.2 |
| 023 | Facebook ego network 0, Email-Eu-core-temporal, Bitcoin-OTC | Attribute, temporal and signed-edge aggregate measurements | Dataset names and conventions in section 8.3 |
| 024 | Email-Eu-core-temporal | Aggregate window/stratum/partition measurements, figures and core calculations | [Source provenance](evidence/experiments/024/source_provenance.json) and [source identity](evidence/experiments/024/source_identity_validation.json) |
| 025 | Derived 024 measurements | Scale comparisons, fits and analysis code | [024 active-neighbour scale](evidence/experiments/024/active_neighbour_scale.csv) and [024 temporal state geometry](evidence/experiments/024/temporal_state_geometry.csv) |
| 026–028 | Frozen authored research corpus | TF-IDF matrices, shard assignments, derived traces, summaries and code | [027 frozen numeric inputs](evidence/experiments/027/README.md) and the workload metadata |

For Email-Eu-core-temporal, the supplied provenance names the [official SNAP page](https://snap.stanford.edu/data/email-Eu-core-temporal.html), the `SteveHuntsman/PathHomologyDataAndScripts` public mirror path `email-Eu-core-temporal.txt`, and Git blob `6d864f3a7d511359c8fc19c6a83b4e2302741669`. The recorded raw source size is 5,517,753 bytes. This identity is metadata; the raw event file is external to the release.

The early real-data studies and 022–023 are cited at the source level recorded in the supplied report. A source version should be recorded when obtaining those datasets for a new execution. The six foundational studies retain report-level coverage in this release.

`do026_X.npz` and `do026_Q.npz` are numeric sparse matrices of the authored report workload, with shapes 372 × 30,000 and 500 × 30,000. The 372-element integer assignment vector uses eight shards. The package carries this frozen geometry separately from the publication text.
