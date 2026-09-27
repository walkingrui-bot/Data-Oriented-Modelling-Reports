# NATLANG-COMPAT-004B calculation record

Date: 2026-09-27

## Data
- FLORES-200 dev, 997 aligned meaning IDs per variant.
- Eight same-language / different-script pairs: Acehnese, Modern Standard Arabic, Banjar, Kashmiri, Central Kanuri, Minangkabau, Tamasheq, Chinese.
- Controls: all available different-language / same-script pairs within the selected Arab/Latin/Devanagari/Tifinagh/Hant pools, plus an equal-sized deterministic sample of different-language / different-script pairs.
- Raw external corpus text is not duplicated in this evidence package. `source_manifest.csv` records exact Git blob SHAs and URLs.

## Surface feature construction
- Unicode NFKC + lowercasing.
- 24-dimensional signed-hash character 3-5-gram surface vector.
- 8 sentence-structure coordinates: log character count, log whitespace-token count, digit ratio, punctuation ratio, whitespace ratio, combining-mark ratio, log mean token length, log token-length SD.
- Per-variant z-scoring on the 800-row training split.
- Ridge linear transfer operator fitted on 800 aligned rows; 197 aligned rows held out for retrieval.
- Random split seed: 20260927.
- Blocked robustness split: rows 1-800 train, rows 801-997 test.
- Permuted-alignment control: training target rows shifted by 137 positions.

## Script-neutral construction
- The same pipeline after replacing glyph identities with coarse Unicode/category symbols (letter, number, mark, whitespace, punctuation classes, symbol/other), retaining coarse sequence structure and sentence-level coordinates.
- This assay measures structural continuity after glyph identity removal; it is not treated as a standalone semantic representation.

## Data-geometry diagnostics
- Stable rank, participation rank, PCA-95 dimension, TwoNN estimate, distance coefficient of variation.
- 20 x 80% resampling stability for stable rank.
- Original-space 10-NN preservation after PCA to 4D and 8D on 220-row diagnostic subsets.

## Primary results
- Surface same-language / different-script: direct 5.36%, mapped 9.61%, gain +4.25 pp.
- Different-language / same-script: direct 7.53%, mapped 6.25%, gain -1.28 pp.
- Different-language / different-script: direct 2.67%, mapped 4.13%, gain +1.46 pp.
- Same-language permuted-alignment control: 0.51%, essentially nominal 1/197 chance.
- Same-language blocked mapped: 7.65%.
- Script-neutral same-language / different-script: direct 28.78%, mapped 33.53%.
- Mean surface script-displacement stable rank: 14.96; script-neutral residual displacement: 4.39.
- Mean 10-NN retention: PCA-4D 20.80%, PCA-8D 31.35%.
