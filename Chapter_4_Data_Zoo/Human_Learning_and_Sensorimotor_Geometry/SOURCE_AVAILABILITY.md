# Data availability and reproduction

This public edition contains the merged English report, 17 report images, authored analysis outputs, analysis code, source identities and integrity records. It contains no redistributed external datasets, extracted external aggregate-data CSV, original source Word attachments or original source ZIP archives.

The report's Appendix B and final source index describe the research collection used to prepare the report. Their archive and attachment names identify research provenance. The files distributed with this public edition are listed in [EVIDENCE_MANIFEST.csv](EVIDENCE_MANIFEST.csv) and [CHECKSUMS.sha256](CHECKSUMS.sha256).

| Study | Included analysis evidence | External inputs obtained from the provider | Analysis route |
| --- | --- | --- | --- |
| 001 | Dataset-level geometry and subsampling results; three figures | Five datasets supplied by scikit-learn 1.8.0; Palmer Penguins; UCI HAR subject-activity summary | [Analysis](evidence/experiments/001/Evidence/analyze_geometry.py) computes the five built-in datasets and their subsampling summaries. Its two external-source rows record the author's prior geometry calculations. |
| 002 | Condition summaries, paired effects, exclusion calculations and four figures | Behavioral CSV, Git blob `e834ccbbe1e183b7e2c094702b50f2e9ce558441`; Vong et al. (2019), DOI `10.1111/cogs.12724` | [Transformation specification](evidence/experiments/002/Evidence/reanalysis.py); use the aggregation notes below with the published tables. The cited comparison appears in report Section 2.8 and Figure 7. |
| 003 | Clip-level, group-level, language and comparison results; five figures | Twenty AMC motion files and the technical-English corpus | [Recomputation script](evidence/experiments/003/Evidence/human_sensorimotor_geometry_003/recompute_geometry.py) accepts explicit motion and corpus paths. |
| 004 | Participant summaries, target-row results, contrasts, sensitivity and spectra; five figures | Reaching CSV, Git blob `44fa933e7d164aa7279c545047d42d6ee6aae5c4` | [Reproduction script](evidence/experiments/004/Evidence/reproduce_004.py) accepts the provider CSV through `--csv`. |

The [source-lock manifest](evidence/experiments/00_EXTERNAL_RAW_SOURCE_LOCKS.csv) records the repository, path, Git blob SHA and suggested local destination for 25 external inputs. These are source references, with no dataset contents attached. Study 001's five built-in inputs are identified by loader and scikit-learn version in its [source manifest](evidence/experiments/001/Evidence/source_manifest.csv). The UCI HAR blob was resolved when the research collection was assembled on 27 September 2026; the study evidence recorded its repository, file and access date.

## Retrieve and verify provider inputs locally

Readers who wish to reproduce an analysis can retrieve its inputs from the original providers in a separate local working copy. From this component directory, run:

```bash
python evidence/experiments/download_external_raw_sources.py --experiment 004
```

Select `001`, `002`, `003` or `004`; omitting the selection retrieves all 25 pinned inputs. The utility checks existing files against their Git blob SHA and retrieves missing files through the Git Blobs API. It uses Git's NUL-delimited blob header for verification. The resulting local input folders are excluded from publication by the component's `.gitignore`.

## Replay examples

The scientific scripts use Python 3 with NumPy, pandas and SciPy; Study 001 also uses scikit-learn 1.8.0 and Matplotlib. Preserve the publication evidence and write recalculated outputs to a separate directory.

After retrieving the fixed Study 004 source locally:

```bash
python evidence/experiments/004/Evidence/reproduce_004.py \
  --csv evidence/experiments/004/raw_data/DataSet.csv \
  --out replay/004
```

The original script's automatic-download URL uses a blob identifier as a raw-file revision. The explicit local-CSV route above uses the verified input directly.

After retrieving Study 003 inputs locally:

```bash
python evidence/experiments/003/Evidence/human_sensorimotor_geometry_003/recompute_geometry.py \
  --mocap-root evidence/experiments/003/raw_data/mocap \
  --corpus evidence/experiments/003/raw_data/language/LANGUAGE-CONTROL-DIMENSION-COLLAPSE-014_language_corpus.txt \
  --out replay/003
```

Study 002's original script reads the provider CSV beside itself. Copy the script and locally retrieved CSV into a separate replay directory before running it. Its printed summary is a compact transformation check. The report's mean selected dimensions averages game-level means; its paired RT effects first average game-level RT medians within each participant and condition. Expected-reward calculations retain 55,080 trial records; 54,617 records have observed RT and selection values. The 463 records with missing behavioral fields remain in the expected-reward denominator under the archived transformation.

Study 001's script writes alongside itself. Run a copy in a separate directory with scikit-learn 1.8.0 to regenerate the built-in dataset calculations. Scikit-learn supplies those inputs at runtime. The two external-source rows in that script preserve the author's prior calculations and can be independently recalculated from their locked sources.

## Checks completed for this edition

All 69 entries in the original research collection's SHA-256 list matched during preparation. The five Study 001 built-in datasets reproduced the archived full-data geometry summaries to numerical precision. Study 002 exclusions, retained counts, condition point estimates and paired point estimates were checked against its pinned provider file using the report's aggregation levels. Study 003 motion medians were checked from its 20-clip result table. Study 004 participant-level results, the main participant-bootstrap contrasts, and single-reach and pooled spectral summaries were recalculated from its pinned provider CSV.

The Study 002 bootstrap intervals, Study 001 external-source calculations and resampling series, and the full Study 003 raw-motion and corpus analysis retain their supplied results. Vong et al.'s published comparison is identified by its citation in Section 2; its extracted source-data CSV is outside this public package.

## Attribution and reuse

The report and source manifests identify the dataset providers and publications. Readers obtain provider data separately under the source's applicable terms. This package distributes the report, the author's derived analysis, figures and code, and the references needed to locate the inputs.
