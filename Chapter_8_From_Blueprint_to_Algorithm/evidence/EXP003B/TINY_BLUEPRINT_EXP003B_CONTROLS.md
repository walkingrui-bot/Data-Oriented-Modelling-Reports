# EXP003B Negative Controls

- Normal latent state + own payload: **100.00%** exact answer accuracy.
- Zero latent state + own payload: **2.70%**.
- Randomly permuted latent states, scored against each recipient's original answer: **12.58%**.
- The same permuted states, scored against the donor-plan counterfactual answer: **100.00%**.

Interpretation: disrupting which latent state is paired with a payload disrupts the original answer, while the transplanted latent state still specifies the donor plan for the new payload.
