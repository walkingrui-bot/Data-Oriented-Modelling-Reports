# Source availability

This issue uses the supplied language research report v1.8 and fifteen recovered independent experiment archives. `EVIDENCE_MANIFEST.json` records each recovered archive identity and SHA-256 hash. The publication directories contain inspected, extracted authored artifacts. Generated Python cache files and partial-run copies are omitted.

## External inputs

External datasets are referenced, not bundled. Source manifests inside each study folder retain available repository names, commits, file paths and Git blob identities. They are the authoritative source pins for that study.

| Source family | Use | Retrieval route |
| --- | --- | --- |
| MCTS | Human Chinese simplification and compression | [blcuicall/mcts](https://github.com/blcuicall/mcts); LSP-001 and RELATION-COMPRESSION-006 source manifests |
| CSS | Independent Chinese simplification validation | The LSP-001 corpus manifest and the Yang, Sun and Wan 2023 reference in the report |
| Universal Dependencies | Multilingual transition, arity, dependency and router measurements | [Universal Dependencies](https://universaldependencies.org/); exact treebank blobs in the recovered structural-study manifests |
| FLORES-200 | Aligned meanings and writing-system controls | [FLORES-200](https://github.com/facebookresearch/flores); NATLANG-COMPAT-004B source_manifest.csv |
| ParaphraseBench | Fixed SQL targets under request paraphrases | [DataManagementLab](https://github.com/DataManagementLab); RESPONSE-REGIME-004B1 SOURCE_MANIFEST.json |
| BFCL and tau3 | Dated public tool-use benchmark comparisons | [BFCL results](https://github.com/HuanzhiMao/BFCL-Result), [BFCL leaderboard](https://gorilla.cs.berkeley.edu/leaderboard), [tau-bench](https://taubench.com/leaderboard/); TOOL-CHAIN-GEOMETRY-006 source records |

The natural-language benchmark text, treebank `.conllu` files, original benchmark response logs, original leaderboard datasets and externally supplied model weights are absent from this package. Authored controlled stimuli, synthetic register-world episode records, the study-trained small policy checkpoints, and derived aggregate results are included where recovered.

## Availability limits

LSP-002, LSP-003, TOOL-CHAIN-GEOMETRY-006B and NATLANG-COMPAT-004A have report-level evidence only in this edition. In particular, the separate 004A archive mentioned in the source bibliography was not recovered, so its claimed source-blob manifest cannot be supplied here. The four studies' table transcriptions and embedded figures are explicitly labeled as report extracts.

Some recovered studies contain complete-looking analysis or training scripts, some provide partial reproduction skeletons, and others provide results without code. `EVIDENCE_INDEX.md` specifies these differences. No claim of a fully self-contained, independently rerun nineteen-study suite is made by this edition.

The recovered study manifests document their original execution environments and may refer to historical local paths. Those records are retained as provenance. The publication-level `CHECKSUMS.sha256` is authoritative for the contents of this release.
