# Model Control Diagnostics

## Chapter 3 — The Engineer’s Edition

Living Engineering Record v0.6 · Archival snapshot · 26 September 2026

The engineering part of [Chapter 3](../chapter-3/README.md), paired with the [research record v1.9](../machine-learning-epidemiology/README.md).

This snapshot of a living engineering report studies how formed models respond to tokens, states, tool descriptions, and internal interventions. It combines nine cloud experiments with the subsequent local pretrained-model investigation, frozen selector comparison, and paraphrase stress study.

The current record connects state-conditioned token measurements, an executable recovered runtime, tool-selection geometry, component contracts, and measured request-to-tool ranking. Its evidence includes finite-intervention calibration, an actual pretrained-model state-patch case, and a 100-task comparison in which both neural relevance ranking and lexical matching obtain 99/100.

## Read the report

- [Integrated English report](REPORT_EN.md)
- [Formatted Word report](Chapter_3_Engineers_Edition_v0.6_EN.docx)
- [Cloud experiments](CLOUD_EXPERIMENTS_EN.md)
- [Local engineering audit and pretrained intervention](LOCAL_ENGINEERING_EN.md)
- [Local selection and paraphrase studies](LOCAL_SELECTION_EN.md)
- [Engineering interfaces and commands](ENGINEERING_INTERFACES_EN.md)
- [Evidence index](EVIDENCE_INDEX.md)
- [Source availability](SOURCE_AVAILABILITY.md)
- [Combined archival description](../chapter-3/ZENODO_DESCRIPTION_EN.md)

## Current findings

The scanner’s Drive, Future Gain, and Steer measurements close against finite perturbations in the specified 897-parameter GRU. The 3,520-cell transplant study measures strong token–state interaction. The recovered runtime executes the included 6,336-transition atlas. Later local results report a finite internal intervention that restores the correct tool to first place in one selected 135M model case.

The frozen selector comparison obtains 99/100 with both a 22.7M relevance model and a TF-IDF baseline, compared with 40/100 for the original 135M label readout. Forty paired paraphrases yield 38/40 and 34/40 respectively. The unchanged rejection policy accepts 12/40 original requests and 2/40 paraphrases. The report keeps accuracy, intervention outcomes, and accepted coverage separately identifiable.

## Evidence organization

| Directory or file | Contents |
| --- | --- |
| `chapters/` | Browsable English sections |
| `evidence/cloud/` | All 229 members of the supplied cloud archive, expanded unchanged |
| `evidence/cloud/04_Original_Stage_Bundles/` | Eleven original stage archives |
| `evidence/source_tables/` | All 123 source Word tables transcribed in source order |
| `evidence/editorial/` | Deterministic recalculation, source-code counterexamples, and attributed plotting inputs |
| `figures/` | Source experiment figures, three figures drawn from reported local aggregates, and one attributed schematic redrawn for readability |
| `source/` | Six exact supplied source files, including the original cloud ZIP and four local documents |
| `LOCAL_SOURCE_MAP.csv` | Availability of each supporting file referenced by the local documents |
| `SOURCE_PROVENANCE.csv` | Source identities and hashes |
| `FILE_MANIFEST.csv` and `CHECKSUMS.sha256` | Assembled release file inventory and integrity records |

Original code and data retain their original language and experimental identities. The English report carries the current integrated interpretation. Local supporting attachments referenced by the supplied reports have individually recorded availability.

## Verify the supplied numerical evidence

With Python 3 and NumPy installed, run from the release root:

```sh
python3 evidence/editorial/verify_supplied_evidence.py --root .
```

The saved [verification result](evidence/editorial/verification_results.json) distinguishes calculations on included cloud artifacts from arithmetic checks of reported local aggregates.

## Version policy

The source cloud engineering record is v0.5. This v0.6 English edition integrates the subsequent local reports and audit corrections under the requested Chapter 3 publication label. Experiment IDs and original version history remain traceable. This report and the Machine Learning Epidemiology v1.9 research record form the two companion parts of Chapter 3, published together and consolidated in one archival collection.
