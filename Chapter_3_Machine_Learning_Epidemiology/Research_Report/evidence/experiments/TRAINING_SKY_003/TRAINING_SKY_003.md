# TRAINING-SKY-003 — Question × Training-Sky × CoT/Answer

## Core correction
A first answer-readout used a correct-vs-wrong sign convention and was not interpreted. The corrected fixed axis is always `logit(1)-logit(0)`. A separate true question-only free-generation readout feeds no CoT tokens at all.

## True question-only result

| finding            |   n_questions |   pairwise_cosine_min |   pairwise_cosine_max |   pairwise_cosine_mean | interpretation                                                                                             |
|:-------------------|--------------:|----------------------:|----------------------:|-----------------------:|:-----------------------------------------------------------------------------------------------------------|
| free_question_only |             8 |                     1 |                     1 |                      1 | All tested questions share the same question-only training-sky answer fingerprint in this tiny-model case. |

## Strongest structural differentiation positions

| readout           |   k |   same_structure_cos |   different_structure_cos |   structure_separation |   same_answer_cos |   different_answer_cos |   answer_separation |
|:------------------|----:|---------------------:|--------------------------:|-----------------------:|------------------:|-----------------------:|--------------------:|
| Answer-fixed-axis |   0 |             0.999757 |                  0.977462 |              0.0222953 |          0.996825 |               0.968513 |           0.0283119 |
| CoT               |  29 |             0.999552 |                  0.925321 |              0.0742305 |          0.998662 |               0.888874 |           0.109788  |

## Strongest answer-class differentiation positions

| readout           |   k |   same_structure_cos |   different_structure_cos |   structure_separation |   same_answer_cos |   different_answer_cos |   answer_separation |
|:------------------|----:|---------------------:|--------------------------:|-----------------------:|------------------:|-----------------------:|--------------------:|
| Answer-fixed-axis |   0 |             0.999757 |                  0.977462 |              0.0222953 |          0.996825 |               0.968513 |           0.0283119 |
| CoT               |  29 |             0.999552 |                  0.925321 |              0.0742305 |          0.998662 |               0.888874 |           0.109788  |

## Question-entry reconstruction of downstream tensors

| readout   |   energy_explained_by_k0_question_signature |   relative_L2_residual |
|:----------|--------------------------------------------:|-----------------------:|
| CoT       |                                    0.559747 |               0.663516 |
| Answer    |                                    0.42429  |               0.758756 |

## Global multi-question SVD

| readout   |   mode |   singular_value |   explained_fraction |   cumulative |
|:----------|-------:|-----------------:|---------------------:|-------------:|
| CoT       |      1 |      0.000428313 |          0.72492     |     0.72492  |
| CoT       |      2 |      0.000240378 |          0.228326    |     0.953247 |
| CoT       |      3 |      6.69063e-05 |          0.0176889   |     0.970935 |
| CoT       |      4 |      4.93075e-05 |          0.00960712  |     0.980543 |
| CoT       |      5 |      3.6025e-05  |          0.00512831  |     0.985671 |
| CoT       |      6 |      2.94852e-05 |          0.00343539  |     0.989106 |
| Answer    |      1 |      0.000913232 |          0.617697    |     0.617697 |
| Answer    |      2 |      0.000712645 |          0.376148    |     0.993845 |
| Answer    |      3 |      7.54953e-05 |          0.00422136  |     0.998066 |
| Answer    |      4 |      4.21589e-05 |          0.00131641  |     0.999383 |
| Answer    |      5 |      2.59858e-05 |          0.000500132 |     0.999883 |
| Answer    |      6 |      9.85807e-06 |          7.19775e-05 |     0.999955 |
