# SVD_HISTORY_MODES_004 | Spectral anatomy of the history-to-CoT causal kernel

## Object

The 20 x 8 matrix K contains the measured effect of swapping the local training order in exactly one epoch (row e) on the final logit at each cold-start CoT prefix k (column k). Thus K[e,k] is a directly intervened history-to-CoT causal response in this controlled 10-parameter system.

## 1. Singular spectrum

K = U Sigma V^T. U defines orthogonal training-history modes; V defines orthogonal CoT-response modes; singular values quantify the strength of each coupled mode.

|mode|singular value|energy|cumulative|
|---:|---:|---:|---:|
|1|0.0213778974|97.377669%|97.377669%|
|2|0.00336277966|2.409496%|99.787165%|
|3|0.000995582562|0.211195%|99.998360%|
|4|8.60076218e-05|0.001576%|99.999936%|
|5|1.66309547e-05|0.000059%|99.999995%|
|6|4.81760487e-06|0.000005%|100.000000%|
|7|3.46574251e-07|0.000000%|100.000000%|
|8|3.67767993e-08|0.000000%|100.000000%|

Stable rank = 1.026929; entropy effective rank = 1.137510; participation-ratio effective rank = 1.053934. Rank-1 relative Frobenius error = 0.161936; rank-2 = 0.046134; rank-3 = 0.004050.

## 2. Where the low rank lives

Let D[e,:] be the final 10-parameter displacement caused by a single-epoch order swap, and J[k,:] = dz_k/dtheta at the baseline final model. First-order readout gives K ~= D J^T.

The observed K and D J^T have correlation 0.999996433 and relative L2 error 0.1502%. D itself has 93.1153% energy in mode 1, 99.5426% in modes 1-2, and 99.9436% in modes 1-3. J has 74.4486% in mode 1, 92.3243% in modes 1-2, and 99.3139% in modes 1-3.

## 3. Dominant modes

The first K mode is positive across all epochs and all CoT prefixes. It therefore acts primarily as a global amplitude mode: local order swaps differ mostly in how strongly they excite one common CoT-response shape. The second and third modes encode smaller shape corrections across training time and CoT position.

## 4. Training time becomes a smooth spectral coordinate

To separate response shape from overall amplitude, each row of K was L2-normalized and the mean profile removed before a second SVD. The first shape mode explains 85.3462% of remaining energy and the first two explain 99.8069%. The first four history-shape modes align with DCT frequencies 1-4 with absolute cosines 0.904570, 0.900950, 0.979258, 0.927457, respectively. In 50,000 random permutations for each fixed frequency, each observed alignment exceeded all sampled permutations (Monte Carlo p <= 2e-05).

This supports a smooth low-frequency organization of epoch position in this case: changing the historical location of the same local order event changes the CoT response through a small set of slowly varying temporal modes rather than arbitrary per-epoch patterns.

## 5. Training-token -> CoT kernel is even more concentrated

The 36 x 8 local training-token-to-CoT derivative matrix from MATH-003 has 98.8563% of its energy in the first singular mode, 99.9749% in the first two, and 99.9996% in the first three. Thus local training-token effects also pass through a very low-dimensional transmission structure in this case.

## 6. Mathematical model reproduces mode geometry

For the exact-local-delta + tangent prediction, the top-3 history subspace differs from the measured top-3 subspace by at most 0.0873 degrees, and the CoT subspace by at most 0.0608 degrees. Replacing the local delta with the Hessian/gradient commutator still gives maxima 2.4442 and 0.7942 degrees. Thus the propagation equation reproduces not only individual cell values but the dominant singular geometry.

## Evidence statement

In this 10-parameter controlled case, the causal influence matrix from local training-order events to later CoT-prefix logits is overwhelmingly low-rank. Most historical variation survives training in a small parameter subspace and is read out through a small CoT-sensitivity subspace. After removing global amplitude, the residual dependence on epoch position is organized by smooth low-frequency temporal modes. These statements are directly supported for this constructed system and its specified intervention family.
