# Source availability

The public package contains authored analyses and source identities. Provider observations are acquired separately from their original sources. The identities below are those recorded in the supplied experiment archive.

| Source | Recorded use | Version identity |
| --- | --- | --- |
| [aehrc/PEPS](https://github.com/aehrc/PEPS/blob/master/SampleData/input-small.csv) | GENOME-GEOMETRY-001 · `SampleData/input-small.csv` | `280f74857402f303846f552366e742a7c9b838b1` |
| [igvteam/igv-data](https://github.com/igvteam/igv-data/blob/main/data/tutorials/vcf/integrated_call_samples_v3.20130502.ALL.panel) | GENOME-GEOMETRY-001 · `data/tutorials/vcf/integrated_call_samples_v3.20130502.ALL.panel` | `bc447774e6bacc2f4ca3619d14bf96a1846aa4e4` |
| [mccoy-lab/hgv_modules](https://github.com/mccoy-lab/hgv_modules/blob/main/05-pop_structure/common_variants.txt.gz) | GENOME-CAPACITY-002 through PREDICTIVE-DIRECTION-STABILITY-011 · `05-pop_structure/common_variants.txt.gz` | `d9302933c2da909dff257263b92e243f11191f5a` |
| [mccoy-lab/hgv_modules](https://github.com/mccoy-lab/hgv_modules/blob/main/05-pop_structure/integrated_call_samples.txt) | GENOME-CAPACITY-002 through PREDICTIVE-DIRECTION-STABILITY-011 · `05-pop_structure/integrated_call_samples.txt` | `411e4fff4d0db8d022dea15c6afb4f0cc89b91e2` |
| [guillermocomesanacimadevila/Population-to-Genotype-dimensionality-reduction](https://github.com/guillermocomesanacimadevila/Population-to-Genotype-dimensionality-reduction/blob/main/Updated%20Matrices/matrix.csv) | EXTERNAL-TRANSFER-007 + PREDICTIVE-DIRECTION-STABILITY-011 · `Updated Matrices/matrix.csv` | `47ac2529c50e84f216845be69f385e2f1280af7c` |
| [guillermocomesanacimadevila/Population-to-Genotype-dimensionality-reduction](https://github.com/guillermocomesanacimadevila/Population-to-Genotype-dimensionality-reduction/blob/main/Data%20sets/phase1_integrated_calls.20101123.ALL.panel) | EXTERNAL-TRANSFER-007 + PREDICTIVE-DIRECTION-STABILITY-011 · `Data sets/phase1_integrated_calls.20101123.ALL.panel` | `2b70a71fba42f2b4870889eff790ee67ad5e905a` |
| [bionumpy/bionumpy](https://github.com/bionumpy/bionumpy/blob/main/example_data/thousand_genomes.vcf) | SMALL-EXTERNAL-STABILITY-BLIND-012 · `example_data/thousand_genomes.vcf` | `5faa223e61eb3b301ebc397eab1df22e4f105f8d` |
| [bionumpy/bionumpy](https://github.com/bionumpy/bionumpy/blob/main/example_data/thousand_genomes.vcf) | SMALL-N-RELIABILITY-CALIBRATION-013B · `example_data/thousand_genomes.vcf` | `5faa223e61eb3b301ebc397eab1df22e4f105f8d` |
| [shanwai1234/MVP](https://github.com/shanwai1234/MVP/blob/master/demo.data/hapmap/hapmap.txt) | CROSS-SPECIES-ESTIMATOR-BLIND-013C + SAMPLE-SUPPORT-DIAGNOSTIC-013D · `demo.data/hapmap/hapmap.txt` | `b8120641d506cd1ee55e46d8c345f313501c21ae` |
| [scikit-learn 1.8.0](https://scikit-learn.org/stable/modules/generated/sklearn.datasets.load_breast_cancer.html) | CROSS-STRUCTURE-DATA-PASSPORT-PILOT-014A · `sklearn.datasets.load_breast_cancer (provider snapshot excluded)` | `snapshot-sha256:0c3e6f1194211ec4aab4f39399da6aadff5e133d329ef951a5ff9d92e6e7f3c6` |
| [statsmodels 0.14.6](https://www.statsmodels.org/stable/datasets/generated/sunspots.html) | CROSS-STRUCTURE-DATA-PASSPORT-PILOT-014A · `statsmodels.datasets.sunspots (provider snapshot excluded)` | `snapshot-sha256:5e811128e2af9b68a886a6bee381141b54c0717a591ecd25cea561af04344e1c` |
| [NetworkX 3.6.1](https://networkx.org/documentation/stable/reference/generated/networkx.generators.social.karate_club_graph.html) | CROSS-STRUCTURE-DATA-PASSPORT-PILOT-014A · `networkx.karate_club_graph (provider snapshot excluded)` | `snapshot-sha256:7137b29ed4f55d6d14080547a23459c059bb4ee9cbd55060aabfe76b2227eedc` |
| [aalfons/nci60](https://github.com/aalfons/nci60/blob/main/nci60_RNA__Affy_HG_U133(A_B)_GCRMA.txt/nci60_RNA__Affy_HG_U133(A_B)_GCRMA.txt) | MECHANISM-ALIGNED-OMICS-GEOMETRY-015A/015B · `nci60_RNA__Affy_HG_U133(A_B)_GCRMA.txt/nci60_RNA__Affy_HG_U133(A_B)_GCRMA.txt` | `3cbbe27f2d78372e1c885b1a5ede16ebf76c30c7` |
| [aalfons/nci60](https://github.com/aalfons/nci60/blob/main/nci60_Protein__Lysate_Array_log2.txt/nci60_Protein__Lysate_Array_log2.txt) | MECHANISM-ALIGNED-OMICS-GEOMETRY-015A/015B · `nci60_Protein__Lysate_Array_log2.txt/nci60_Protein__Lysate_Array_log2.txt` | `ed0aa9ac1421e47fd1ba80c193e8e663f16548cd` |
| [aehrc/PEPS](https://github.com/aehrc/PEPS/blob/master/SampleData/input-small.csv) | MECHANISM-ALIGNED-OMICS-GEOMETRY-015A · `SampleData/input-small.csv` | `280f74857402f303846f552366e742a7c9b838b1` |

## Paired genome–transcriptome protocol

The locked EXP015C record identifies Zenodo record 15596289 / GEUVADIS (Lappalainen et al., 2013), with `geuvadis.pgen`, `geuvadis.pvar.zst`, `geuvadis.psam`, and `GD462.GeneQuantRPKM.50FN.samplename.resk10.txt.gz`. These are source pointers for an unexecuted protocol in this release, not published experiment results or bundled data. The protocol defines distant same-chromosome variants as at least 5 Mb away and cis-local variants within ±1 Mb.

## Distribution boundary

Five provider observation matrices were excluded: the fixed EXP013B genotype panel and the EXP014A genotype, WDBC, sunspot-window, and karate-adjacency snapshots. Literal genotype dosage strings embedded in the EXP013B code were replaced with an explicit local-input interface. The nested original evidence ZIP and original Word attachment are also outside the publication package.

Selected-marker identifiers, locked split metadata, source hashes, aggregate statistics, direction-level analysis outputs, and figures remain available as the authored research record. External provider data retain their own terms; this release does not grant additional rights over them.

## Reproduction scope

See [Reproduction guide](REPRODUCTION_GUIDE.md) for exact script coverage and commands. No new provider data were downloaded for publication preparation. Result-table verification and the EXP013A replay use the supplied derived results.
