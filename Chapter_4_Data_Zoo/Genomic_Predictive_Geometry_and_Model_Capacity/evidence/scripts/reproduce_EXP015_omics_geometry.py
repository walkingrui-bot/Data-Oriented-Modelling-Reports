"""Protocol and seed record for EXP015A/B; this is not a complete executable analysis.
Public sources are pinned in SOURCE_MANIFEST.csv.
Raw public source files are intentionally not repacked.
Protocol: keep NCI-60 U133A rows, remove the all-NA cell line from RNA and protein, feature-wise mean-impute then z-score; compute sample-space Gram spectrum, PR, r90, TWO-NN, distance CV. For RNA-protein, match gene symbols and select the highest-variance probe in each layer, compute correlations and cross-covariance spectrum, then run gene-label and cell-pair shuffles with the archived seeds.
"""
SEEDS = {"genome_downsample":15015,"gene_label_permutation":15151,"within_tissue_cell_shuffle":15152,"global_cell_shuffle":15153}
print(SEEDS)
