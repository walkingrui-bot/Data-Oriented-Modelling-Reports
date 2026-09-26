# COT-BUDGET-GEOMETRY-021

## Question

For a particular trained model and a particular question:

1. Does the answer need any CoT at all?
2. If so, how many genuine reasoning steps are required?
3. Is there an upper "reasonable" CoT length?
4. Is reasonable CoT length actually a scalar interval, or is the correct object a state/action-dependent admissible set?

## Problem-specific mathematical expansion

Let the prompt consist of tokens q_1,...,q_m. The prompt forms the initial state

h_0(q) = F_{q_m} o ... o F_{q_1}(h_init).

For a chosen thought policy pi=(a_1,a_2,...),

h_(k+1) = F_theta(h_k,e(a_(k+1))).

For binary answer y, define the correct-signed answer-readiness margin after immediately applying the common answer gate:

M_y(h) = s_y [z_1(F_theta(h,e_answer)) - z_0(F_theta(h,e_answer))],

where s_y=+1 for y=1 and -1 for y=0.

For one problem q and thought policy pi:

m_q(k;pi) = M_y(h_k).

A first-order local distance to the answer decision surface is

rho_q(k;pi) = m_q(k;pi) / ||grad_h M_y(h_k)||.

For a required robustness epsilon, the minimal reasoning depth is therefore model- and policy-conditioned:

k_min(q,theta,pi,epsilon)
= min {k : rho_q(k;pi) >= epsilon}.

This is not an intrinsic scalar property of an abstract answer. It is a property of the trained model, the exact prompt state, the answer readout and the permitted thought actions.

## Exact finite value of one thought step

Let Delta h_k = h_(k+1)-h_k. The exact finite contribution of a thought step to answer readiness is

G_q,k = M_y(h_(k+1)) - M_y(h_k)
      = integral_(gamma_k) grad_h M_y(h)^T dh.

The experiment evaluates this path integral numerically. Across all 16 problems and three genuine relation steps, 32-point Gauss-Legendre integration closes the observed finite margin change with maximum error approximately 3.6e-5.

A single local dot product grad M . Delta h is not enough in this model; its correlation with the exact finite gain is only about 0.24 because the state transitions are strongly nonlinear.

The exact stopping relation is therefore

m_q(k) = m_q(0) + sum_(j<k) G_q,j.

The question "how much CoT is required?" becomes "how many state transitions are needed for cumulative finite control work to move the current problem state into the robust answer region?"

## Round 1: the same 4-bit task gives different required depths for individual questions

All 16 problems have the same formal three-relation XOR depth and all are solved perfectly when their full trained route is used.

Under the CoT-mode prompt state and with no inserted blank steps:

- 8/16 problems can already be answered correctly at k=0.
- 3/16 first become correct at k=2.
- 5/16 first become correct at k=3.
- none first become correct at k=1.

In this particular model all eight y=1 cases are prompt-ready, whereas y=0 cases require two or three relation steps. This is a learned decision-geometry asymmetry, not a universal property of XOR.

Representative trajectories:

Question 0001, y=1:
m0=+4.99. No CoT is required under the hard-boundary criterion.

Question 0000, y=0:
m0=-6.38
G1=+3.16
G2=+3.80
so m2=+0.59. Two relation steps are sufficient.

Question 0101, y=0:
m0=-15.09
G1=-1.17
G2=+12.84
leaving m2=-3.42;
G3=+13.99 then moves the state to m3=+10.57.
Three relation steps are required.

Thus the needed depth is determined by initial answer deficit plus the finite state-space work performed by subsequent thought actions, not by formal problem depth alone.

## Round 2: "length" is not enough

After each genuine CoT stage, 0-8 blank-compute actions are inserted before the answer gate.

At total budget 3, four different action compositions give:

- 0 genuine relation + 3 blank: 75% accuracy
- 1 relation + 2 blank: 50%
- 2 relations + 1 blank: 50%
- 3 genuine relations + 0 blank: 100%

The same scalar computation length therefore corresponds to radically different answer-readiness.

The natural object is a budget/action surface, not a length axis.

## The admissible set can be non-contiguous

After all three correct relations, all 16 problems are initially answer-correct. One extra blank step drops aggregate accuracy to 50%. Two blank steps restore it to 100%.

For 8/16 individual problems, the set of correct blank budgets over n=0...8 is non-contiguous.

Example 0001:

n=0: signed margin +13.339
n=1: -0.266
n=2: +4.950
n=3: +6.835

Thus its hard-admissible set begins {0,2,3,4,...}, not [0,k].

Repeated blank computation is an iterated nonlinear map

h_(n+1)=W(h_n)=F_theta(h_n,e_X),

and the answer margin is M_y(W^n(h_*)).

For problem 0001, the local blank-transition Jacobian spectral radius is 1.42 at n=0 and 1.57 at n=1, consistent with an expanding local transition that can move the state out of and then back into the correct answer basin.

Therefore the mathematically correct object is generally an admissible thought set, not necessarily an interval.

## Proposed definition of a problem-conditioned reasonable CoT set

For a fixed allowed thought policy pi, define

A_(epsilon,delta)(q,pi)
= { k :
    rho_q(k;pi) >= epsilon
    and S_q(k;pi) >= 1-delta },

where S is the probability of surviving the intended reasoning prefix under the model's own token policy.

If a compute price lambda is required, define a utility

U_q(k;pi)
= P(correct | h_k) - lambda C(k) - beta R_error(k),

and an eta-near-optimal set

K_eta(q,pi)
= {k in A : U_q(k;pi) >= max_j U_q(j;pi)-eta}.

There is no theorem that K_eta must be contiguous.

More generally, when action identity is not fixed, the correct object is

S_epsilon(q)
= {a_1:k : rho_q(h_k) >= epsilon},

a subset of thought-action trajectories. "CoT length" is only the one-dimensional projection |a_1:k| and can erase the causal structure.

## Round 3: CoT can be necessary for a learned compositional generalization, but not automatically

A 6-bit hierarchical parity task is trained on 48/64 combinations and evaluated on 16 held-out combinations while retaining all local pairwise XOR patterns in the training set.

Across three initializations:

Seed 22021:
- Direct held-out answer accuracy 50%
- Blank-think 62.5%
- CoT 93.75%

Seed 22022:
- Direct 43.75%
- Blank 43.75%
- CoT 43.75%

Seed 22023:
- Direct 50%
- Blank 31.25%
- CoT 56.25%

The first seed provides a positive "CoT-needed" case: the same model family can reuse explicit learned relations to solve held-out compositions that its direct route does not solve.

The other two seeds are equally important negative controls. CoT does not rescue a model that has not formed the required reusable operator geometry.

Thus "this problem needs CoT" is not a property of problem complexity alone. It depends on

problem structure x learned reusable operators x current state geometry x thought policy.

## Relation to current literature

External work has already established that reasoning length should be adaptive rather than universally maximized. `When More is Less` reports inverted-U accuracy versus CoT length and shows that optimal length increases with task difficulty and decreases with model capability. Adaptive Computation Time likewise treats computation depth as input-dependent. Budget-forcing work demonstrates that forced extra reasoning can sometimes improve answers, while later analyses show model-dependent plateaus or degradation. Recent structural analyses of overthinking argue that useless exploration and verification are better descriptors than raw length alone.

The current controlled result sharpens these observations: even for one fixed problem/model, the admissible set can be non-contiguous, and equal token budgets can behave differently because thought-action identity and state geometry matter.

## Working conclusion

A useful scalar "optimal CoT length" can exist only after a thought policy, robustness criterion and compute/error cost have been fixed.

The more fundamental per-problem object is a state-conditioned stopping geometry:

prompt state -> finite thought-action work -> robust answer region.

CoT is required when the current state is outside the acceptable answer region and the learned thought actions provide a viable trajectory into it. It is unnecessary when the current state is already answer-ready. Extra CoT becomes harmful when additional actions move the state out of the acceptable region or accumulate enough generation risk/cost to dominate their information gain.
