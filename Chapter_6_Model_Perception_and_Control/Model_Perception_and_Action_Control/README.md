# Model Perception and Action Control

**Corrective Optics for Language Models**

Chapter 6, Report 01 · English edition 1.0 · 1 October 2026

[Chapter 6](../README.md) · [All chapters](../../README.md)

A decision-making agent needs a calibrated view of its task, a rule for choosing an eligible action and an observation of what changed after execution. This report follows those requirements from language statistics through recorded coding-agent loops to targeted intervention inside a pretrained language model.

| Read or inspect | Open |
| --- | --- |
| Integrated English report | [Markdown](REPORT_EN.md) · [Word](Model_Perception_and_Action_Control_EN_v1.0.docx) |
| Experiment evidence | [Evidence index](EVIDENCE_INDEX.md) · [Source availability](SOURCE_AVAILABILITY.md) |
| 56 figures | [Figure catalogue](FIGURES.md) |
| 57 reported tables | [CSV transcriptions](evidence/report_tables/README.md) |
| File provenance | [Source manifest](SOURCE_MANIFEST.json) · [Checksums](SHA256SUMS) |
| Report and evidence package | [Download ZIP](../releases/Chapter_6_Report_01_Publication_v1.0_20261001.zip) · [SHA-256](../releases/Chapter_6_Report_01_Publication_v1.0_20261001.zip.sha256) |

## The evidence chain

The ASTIG studies measure exposure, role, topology and geometry corrections. Matched coding-agent traces then separate useful local representations from recurring actions, and test cooldown, candidate expansion, phase eligibility, controlled recovery replay and real command verification. MODE-COLLISION-001 measures layerwise mode readability in a controlled eight-layer model. MODE-CONTROL identifies selective first-action control axes in blocks 21–23 of a fixed Qwen2.5-1.5B-Instruct model and measures their response to a later opposing intervention.

The final study uses 70 paired requests. At block 23, a negative dose of two changes 18 of 59 baseline over-action cases to a textual first action. At dose one, nine cases change; a second equal-norm opposite intervention at blocks 24–26 restores ACT in all nine. The measured endpoint is the first action under the stated contract.

## Using this release

Start with the executive summary and reading guide, then follow an experiment identifier to the evidence index. Recovered numerical outputs are distinct from manuscript-table transcriptions. The early ASTIG row records and the final MODE-CONTROL intervention row files were not recovered for this edition; the included summary and figures retain their reported measurements. External raw datasets and trajectory text are not included.

Run `python verify_results.py` from this directory to check the included counts, selected arithmetic, three-seed aggregations and file hashes. This checks the published derived evidence; it does not repeat training or model intervention.

Related reports: [How Language Models Reach an Answer](../../Chapter_3_Machine_Learning_Epidemiology/How_Language_Models_Reach_an_Answer/README.md) and [Modelling Hypothesized Mechanisms Underlying Data](../../Chapter_5_Data_Oriented_Modelling/Modelling_Hypothesized_Mechanisms_Underlying_Data/README.md).

Some hypotheses developed in this research have received substantive validation through engineering implementations. Data models are forthcoming.
