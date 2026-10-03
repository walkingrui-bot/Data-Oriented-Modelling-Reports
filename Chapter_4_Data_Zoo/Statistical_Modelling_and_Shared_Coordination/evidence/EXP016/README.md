# INTERNAL_COORDINATION_016 — 18-Pipeline Native Data Plane

Experiment 016 converts the previous six coarse Open Targets datatype summaries into a concrete 18-line Evidence Data Passport integration plan pinned to Open Targets 26.06.

## What is completed

- All 18 Passport IDs are mapped to current 26.06 datasource identities.
- Each line has a source-level association route through `association_by_datasource_direct`.
- Each line is mapped to a current source-specific evidence dataset / native route.
- The narrow `CRISPRbrain` label is upgraded to the current general `crispr_screen` pipeline while preserving project/study identity; Project Score maps to the unified `crispr` evidence line.
- Within-pipeline Stat-MoE candidates, time-lock fields and ganglion export semantics are defined for every line.
- The 26.06 EFO→Mondo change is handled through a disease-ID bridge using `disease.obsoleteTerms`, `obsoleteXRefs` and `dbXRefs` before joining the legacy 26,278-pair terminal cohort.
- A reproducible Python harness implements registry validation, source-level association pivoting, native evidence loading, time locking, OOF statistical routing, shared-ganglion construction and frozen-ganglion onboarding.

## Two-level modelling hierarchy

1. **Native pipeline:** preserve each source's observation unit, repeated structure, uncertainty, time and provenance.
2. **Stat-MoE inside pipeline:** fit candidate statistical experts and route by strict OOF risk.
3. **Channel interface:** export one calibrated state containing prediction/support, uncertainty, novelty/time and availability.
4. **Shared ganglion:** coordinate the 18 calibrated channel states. Expert routing is not performed here.
5. **Terminal precision:** evaluate later human clinical outcome after the evidence snapshot has been frozen.

## Pinned release

The engineering registry is pinned to Open Targets `26.06` to preserve compatibility with Experiments 011–015. The public downloads site may subsequently point to a newer quarterly release; reproducibility requires the release stamp to stay explicit.

## Data required for the first full 18-line training run

Mount the Open Targets 26.06 output tree under one directory, minimally including:

- `association_by_datasource_direct/`
- `disease/`
- the 18 `evidence_*` source directories listed in `results/pipeline_registry.csv`

Then run:

```bash
python code/native_pipeline_harness.py --data-root /path/to/opentargets/26.06/output --validate-only
```

The harness also contains the shared 18-interface ganglion and the frozen-ganglion onboarding operation for a held-out/new evidence pipeline.

## Evidence status

Experiment 016 is the source-level construction and compatibility experiment. It reports an executable 18-pipeline data plane and release-specific mapping. Predictive performance remains attached to Experiments 011–015 until the 26.06 source parquet is mounted and the 18 native lines are actually trained.
