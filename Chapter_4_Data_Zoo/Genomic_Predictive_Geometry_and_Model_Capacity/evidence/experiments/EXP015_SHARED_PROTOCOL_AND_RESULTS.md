# EXP015A / EXP015B — Mechanism-Aligned Omics Geometry

## Scope of the completed studies
EXP014B (multiple real datasets per structure to estimate within-structure vs between-structure Data Passport variance) is **not executed in this version**. It remains a future atlas-validation experiment.

## EXP015A: matched-width layer geometry
Actual data: 59 NCI-60 cell lines after removing the all-NA RNA cell line LC:NCI_H23; 22,283 HG-U133A RNA probes; 162 lysate-array protein probes. The genome comparator is the archived AEHRC/PEPS 1000 Genomes 162-SNP matrix, deterministically downsampled to 59 individuals (seed 15015).

For the fair-width comparison, each layer was represented as 59×162. RNA used the 162 highest raw-variance HG-U133A probes; protein used all 162 probes; genome used all 162 SNPs. Feature-wise mean imputation (where needed) and z-scoring preceded sample-space Gram/spectrum calculations.

Key result: PR dimension / TWO-NN were genome 40.00 / 49.87, RNA 10.53 / 7.55, protein 15.44 / 13.16. Top eigen shares were 0.058, 0.211, 0.168. RNA all-22,283 sensitivity analysis retained low PR (11.84), so the concentrated global geometry is not created by choosing only 162 RNA probes.

A fixed alternate-feature 81→81 predictive probe gave r90 genome/RNA/protein = 25/4/7 and effective rank = 16.76/2.69/3.78. Energy per matrix entry was 0.0188/0.0883/0.0606.

## EXP015B: same-cell, same-gene RNA→protein operator
One highest-variance RNA probe and one highest-variance protein probe were selected per symbol, yielding 92 matched symbols in the same 59 NCI-60 cell lines. Mean same-gene correlation was 0.3959 (median 0.3806); 92.4% were positive. A 5,000-permutation gene-label null had mean 0.00293 and p=0.000200.

The full RNA→protein cross-covariance operator had energy 313.85, energy-effective rank 5.01, r90=11, and top-direction energy share 0.373.

Within-tissue cell-line shuffle retained cancer-lineage composition but reduced mean same-gene correlation to 0.1704 and operator energy to 249.52; global cell shuffle reduced them to approximately 0 and 146.07. Both controls had empirical p≈0.000333 with 3,000 shuffles.

## Evidence interpretation
In these real datasets, inherited genotype variation is a much thicker high-dimensional point cloud, whereas RNA and protein expression occupy more concentrated coordinated state manifolds. Their within-layer predictive operators are stronger but substantially narrower. The protein layer is slightly wider than the RNA top-162 layer rather than being a simple further compression. The matched RNA→protein mapping is strongly mechanism-aligned on average, but gene-wise coupling is heterogeneous; regulation beyond mRNA abundance contributes additional degrees of freedom.

## Assay scope and registered designs

The protein layer is the 162-probe NCI-60 lysate antibody array. A broad quantitative-proteome replication, including the previously suggested NCI-60 SWATH-MS source, remains an unexecuted independent design. The authoritative EXP015C protocol in this edition is the paired GEUVADIS/1000 Genomes genome–transcriptome design in EXP015C_PROTOCOL_LOCKED.json.
