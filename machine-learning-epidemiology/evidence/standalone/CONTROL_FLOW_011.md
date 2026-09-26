# CONTROL-FLOW-011 — State-gated rotation of token-control directions across a CoT

## Goal

Test whether the embedding directions that can control future computation remain fixed as a model advances through its own chain of thought, or whether the CoT state itself reorients future controllability.

This experiment reuses the strict observable-lock pair from VECTOR-SUBSPACE-010: seed 14, the same 4D bit codebook offset `(0.6,0,0)`, and two models that differ only in the historical order of paired chain-training records.

Both histories generate the identical four-question visible chain signature:

`00|00|11|11`

and the identical correct endpoint:

`0011`.

Thus the comparison holds surface CoT, final hard answers, token codebook, initialization family, task and architecture fixed.

## Exact local geometry

For the recurrent update

`h_t = tanh(W h_(t-1) + U e_t + b)`

the immediate token-embedding-to-hidden Jacobian is

`J_t = D_t U`, where `D_t = diag(1-h_t^2)`.

The readable subspace `Row(U)` is fixed within one trained model. What changes with the CoT state is its anisotropy: `D_t` reweights the two hidden input channels and can rotate the dominant right-singular direction inside the same readable plane.

The exact final-answer gradient for a token at step `j` is

`g_j = U^T D_j W^T D_(j+1) ... W^T D_T v`.

Across every history/question/path audited here, this analytic product matches autograd with maximum absolute error **1.943e-16**.

## Same visible CoT, different control flow

History A route→code immediate control-axis rotation across the four questions:

**49.816°–59.314°**

History B:

**89.473°–89.698°**

History B is therefore close to a right-angle frame switch at every question, despite producing the same visible two-token chains and answers as History A.

For Q=00 specifically:

- History A immediate control-axis rotation: **53.988°**
- History B immediate control-axis rotation: **89.698°**
- History A route-token→answer vs code-token→answer direction rotation: **20.587°**
- History B corresponding rotation: **47.737°**

## Root cause in History B: state-gated channel switching

The two rows of History B's learned input matrix `U` are almost orthogonal:

**89.754°**.

For Q=00, the route-token state has tanh derivative gates:

`D_route = (0.555563, 0.649525)`

which give weighted input-row magnitudes:

`(0.250764, 0.839101)`.

The dominant route-stage axis is only **0.0241°** from `U` row 2.

At the code token, the gates become:

`D_code = (0.374992, 0.044581)`

with weighted row magnitudes:

`(0.169260, 0.057593)`.

The second hidden channel is now strongly saturated and its derivative is suppressed. The dominant code-stage axis becomes only **0.0322°** from `U` row 1.

Across all four questions in History B, the dominant axis switches between the two almost-orthogonal `U` rows when the CoT advances from route token to code token.

This is a concrete **state-gated control-frame switch**:

`training history -> learned U geometry + state trajectory -> tanh derivative gates D_t -> dominant embedding-control direction`.

## Control of future controllability

The first CoT token was then continuously perturbed along its own dominant downstream-control direction while its visible token identity was held fixed. The next discrete code token was also held fixed when measuring downstream local control geometry.

### History A, Q=00

- Final answer crosses zero at alpha ≈ **0.315247**
- Next code logit crosses zero at alpha ≈ **0.603530**
- Maximum rotation of the second-token answer-control direction before the next code-bit switch: **22.894°**
- Downstream control-gain ratio over that same branch: **5.207x**

### History B, Q=00

- Final answer crosses zero at alpha ≈ **1.031778**
- Next code logit crosses zero at alpha ≈ **1.764571**
- Maximum downstream control-direction rotation before the next code-bit switch: **48.977°**
- Downstream control-gain ratio: **7.993x**

In both histories the final answer can cross its decision boundary before the next visible CoT bit changes. In History B, the first token can rotate the next token's answer-control direction by almost 49 degrees while the downstream discrete branch remains unchanged.

## Working interpretation

The full readable embedding subspace is fixed by `Row(U)` in this small RNN, so it is more precise to say that the **dominant control frame rotates inside the readable subspace**, rather than that the entire subspace itself rotates.

The mechanism is explicit: CoT tokens alter the hidden state; the hidden state changes the nonlinear derivative gates `D_t`; those gates reweight the learned input channels; and this reorients which embedding direction has the highest downstream control gain.

Thus a CoT token can do more than change the current answer tendency. It can change the **control geometry available to later CoT tokens**. In this controlled case, the chain is therefore a sequence of state-dependent reconfigurations of future controllability.
