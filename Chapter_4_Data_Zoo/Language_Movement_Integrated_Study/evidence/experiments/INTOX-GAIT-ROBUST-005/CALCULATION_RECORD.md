# Gait calculation record

The analysis object has rows female forward, male forward, female backward and male backward, and columns foot rotation, stride length, step width, stride time, cadence and velocity. Zero denotes no intoxicated-minus-sober displacement, so singular-value calculations remain uncentered.

The recorded calculations include six feature-removal fits, four subgroup-removal fits, row-unit/column-RMS/sign controls, 200,000 within-row feature-identity permutations, orthonormal Hadamard factorization and mean-vector/PC1 alignment. The report also mentions exhaustive feature subsets; the supplied script implements the named output tables listed in the reproduction guide.

The source evidence describes results at working-matrix precision and supplies a three-decimal public matrix. Recorded values and public-matrix rerun values remain separately labelled. `recomputed_from_report_rounded_matrix.csv` contains the nine deterministic rounded-matrix reference quantities checked during publication preparation.
