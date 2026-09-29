# CROSS-SPECIES-SAMPLE-SUPPORT-DIAGNOSTIC-013D

After EXP013C was revealed, the same four locked maize tasks were used for a controlled sample-support diagnostic. Marker panels and target indices were held fixed. Training subsets were nested at n=30, 60 and 120; a fixed disjoint 100-person group formed the independent operator reference.

Raw ordering improves strongly with sample support: power-debias Spearman rises 0.517→0.673→0.903 and whole-training bootstrap rises 0.584→0.700→0.882. The mean independent direction reproducibility also rises from 0.318 to 0.414 to 0.460 because the training-defined predictive directions themselves become better supported.

The diagnostic also shows that calibration is not a fixed universal constant. Post-hoc affine slopes required by maize change with n (power 0.505→0.558→0.697; bootstrap 0.775→0.968→1.211). Therefore EXP013C's absolute-scale mismatch is best described as a combination of small-n estimator resolution and domain/sample-regime calibration shift.

Practical interface: report raw ordering quality separately from calibrated reliability magnitude, condition calibration on sample-support regime, and retain an estimator-resolution flag whenever support-count and direction-ranking instruments disagree.
