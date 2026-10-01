# Source availability

The published evidence consists of research-derived measurements, tables, analysis code and figures. External raw datasets, request strings, prompts, trajectory text, downloaded benchmark repositories, model weights and raw execution logs are not redistributed.

## External sources

- [SWE-bench experiments](https://github.com/SWE-bench/experiments): public agent trajectories used in the early observational analysis.
- [SWE-Xplorer-Experiments](https://github.com/mahirlabibdihan/SWE-Xplorer-Experiments): public matched agent traces. Per-file URLs appear in the recovered source manifests.
- [When2Call](https://huggingface.co/datasets/nvidia/When2Call): the external request source named in the experimental record. The original paired derivative is identified by its SHA-256 in SOURCE_MANIFEST.json and is not included.
- [Qwen2.5-1.5B-Instruct](https://huggingface.co/Qwen/Qwen2.5-1.5B-Instruct): the fixed model used for internal intervention, revision 989aa7980e4cf806f80c7fef2b1adb7bc71aa306. No weights are included.
- Iris, Wine, Breast Cancer Wisconsin and Digits: numerical datasets accessed through scikit-learn in the original proxy studies; no dataset copies are included.

## Files not recovered for this edition

The earlier ASTIG row-level records and analysis scripts are represented by the manuscript's aggregate tables and figures. MODE-CONTROL FINAL's all-layer logits, mode axes, intervention indices, orthogonal/shuffled-control rows, dose-response rows, generated continuations, output-arbitration rows and reversal matrix were referenced in the experimental record but were not available among the retrieved files. The released final summary preserves the available measurements. The package therefore supports inspection and selected recalculation of those summaries, rather than full independent recomputation of every final intervention.

The [evidence index](EVIDENCE_INDEX.md) gives experiment-level coverage. File transformations are limited to English report preparation, removal of workflow/local-path metadata, documented column projection and portable script paths. Numerical source outputs copied without changes are identified as such in the manifest.
