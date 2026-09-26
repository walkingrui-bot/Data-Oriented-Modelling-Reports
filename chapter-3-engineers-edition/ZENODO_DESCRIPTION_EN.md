# Model Control Diagnostics

## Chapter 3 — The Engineer’s Edition

Living Engineering Record v0.6

This engineering report studies how formed models respond to tokens, internal states, tool descriptions, and finite interventions. It develops a practical measurement workflow connecting state-conditioned token effects, executable operator queries, tool-selection scores, and host-side execution contracts.

The integrated edition brings together nine cloud experiments and subsequent local model studies. In a frozen 897-parameter GRU, differential measurements of direct answer influence, future-response gain, and adjacent-token steering are validated through finite perturbations. A 3,520-cell token–state study measures context-dependent response structure, and an included recovered runtime executes a 6,336-transition operator atlas. Constructed action systems and cross-architecture selector experiments supply further tests of decision boundaries, evidence-channel sensitivity, and action readiness.

The local update reports a finite internal-state intervention that restores the correct tool to first place in a selected SmolLM2-135M-Instruct case. A separate frozen comparison evaluates a 22.7M relevance ranker, alternative 135M readouts, and TF-IDF matching on 100 BFCL tasks. Both relevance ranking and lexical matching obtain 99/100. A separately registered forty-task paraphrase study yields 38/40 and 34/40 respectively, and measures a change in frozen-policy acceptance coverage from 30% to 5%.

The report translates these findings into explicit engineering interfaces for diagnostics, candidate ranking, argument binding, and execution-domain checks. It distinguishes local geometric sensitivity, task correctness, intervention effects, and accepted coverage through their measurement definitions and evaluation denominators.

The release contains the integrated English report, browsable chapters, original cloud evidence and stage archives, the supplied local reports, numerical verification, and file-level provenance. A source-availability map identifies the supporting local files referenced by the completed reports. This preserves engineering version 0.6 as an archival snapshot of the living record, paired with research version 1.9. The description of the merged record is in [Chapter 3](../chapter-3/ZENODO_DESCRIPTION_EN.md).

Keywords: model control diagnostics; token operators; state-conditioned sensitivity; tool selection; activation patching; semantic ranking; abstention; engineering reproducibility.
