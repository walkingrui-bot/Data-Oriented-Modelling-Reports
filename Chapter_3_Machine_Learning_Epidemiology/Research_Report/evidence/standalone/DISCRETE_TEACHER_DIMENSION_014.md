# DISCRETE-TEACHER-DIMENSION-014

## Experimental question

TEACHER-DIMENSION-TRANSFER-013 showed in a continuous system that a teacher's intrinsic control dimension can be transmitted to a sufficiently expressive student. This experiment asks the stricter language-like question: does the same dimensionality remain identifiable when the teacher exposes only a discrete autoregressive token trace?

The visible world is held fixed across all conditions: six trinary prompt tokens, six binary CoT tokens, one binary answer, the same vocabulary, sequence length, student architecture, finite prompt universe, optimizer schedule and training budget. Only the teacher's hidden causal rank d changes from 1 to 6.

## Discrete autoregressive teacher

All 3^6 = 729 prompts x in {-1,0,+1}^6 are enumerated. The teacher forms z = B_d^T x, where B_d has d orthonormal columns. Seven pre-threshold logits (six CoT positions plus answer) are generated from z; each CoT bit is thresholded to 0/1 and then fed back into the next teacher step. Within a fixed discrete branch, the complete teacher prompt-to-future-logit Jacobian has exact rank d.

Thus surface dimensionality remains six while the teacher's true causal control dimension is known exactly.

## Student and control-field readout

A 24-state tanh autoregressive RNN is trained on the complete finite prompt universe. At each realized teacher branch, the 7x6 Jacobian from the six prompt numeric-token coordinates to the six CoT logits plus final answer logit is computed analytically.

A single prompt state may expose fewer dimensions because nonlinear saturation temporarily suppresses some directions. To measure the whole state-conditioned control field, local Jacobians from 183 distributed prompt states are stacked before SVD. The resulting global r95 is the smallest number of singular modes carrying 95% of control-field energy.

Two common initializations are used for every d.

## Regime A: hard tokens only

The student receives only the thresholded 0/1 CoT and answer tokens.

Mean bit accuracy over all d and both initializations is 0.9910. The finite discrete mapping is therefore learned well.

However, the learned continuous geometry is not a one-to-one copy of the teacher. Median global r95 for d=1...6 is:

{1: 1.0, 2: 3.5, 3: 4.5, 4: 4.0, 5: 5.0, 6: 5.0}

The strongest mismatch is in intermediate dimensions: d=2 and d=3 teachers are implemented with extra continuous control directions despite almost identical discrete behavior.

Across all conditions, 0.9258 of control-field energy lies in the teacher's true causal subspace on average, and the mean principal-angle error is 6.069 degrees.

This establishes an identifiability result: the hard token trace constrains the discrete decision map but does not uniquely specify how the student must interpolate between token states.

## Regime B: identical visible tokens + continuous token margins

The visible CoT/answer sequence is unchanged. Training additionally matches the teacher's pre-threshold continuous token logit/margin at every CoT/answer position.

The learned median global r95 becomes exactly:

{1: 1.0, 2: 2.0, 3: 3.0, 4: 4.0, 5: 5.0, 6: 6.0}

for teacher d=1...6.

Across both initializations, 0.9962 of control-field energy lies in the known teacher causal subspace, and the mean principal-angle error falls to 0.444 degrees.

Thus the graded numeric trace restores the dimensional structure that hard symbolic identity alone leaves underdetermined.

## Local axes versus global field

The experiment also separates instantaneous and global dimensionality. Individual prompt states often expose only 1-3 strong directions even when d is larger. Across prompt states these local axes rotate, and the stacked control field recovers the larger teacher dimension.

This is the discrete autoregressive analogue of the previously observed rotating control field: high global dimension does not require every local state to simultaneously display every mode.

## Geometry controls

### Dense versus sparse surface realization

For d=2, the causal subspace is implemented once as a dense orientation distributed across all six visible prompt coordinates and once as a sparse orientation using only two coordinates. The causal rank is the same in both worlds. Results are stored in `geometry_controls.csv`.

### Orientation control

Three independent d=4 causal subspace orientations are trained under numeric-margin supervision. Control-rank recovery and subspace alignment remain high across orientations, showing that recovery concerns intrinsic dimension rather than privileged coordinate axes.

## Interpretation

TEACHER-DIMENSION-TRANSFER-013 and this experiment answer different questions.

The continuous experiment showed that teacher dimension can be transmitted.

The present discrete experiment shows that **hard token identity is not sufficient to make that transmission unique**. A student can reproduce nearly the same discrete CoT/answer behavior while embedding the behavior in a higher-dimensional or rotated continuous control geometry.

The teacher's numeric pre-threshold margins strongly restore both rank and orientation. Therefore, in this controlled system:

1. intrinsic control dimension is a transmissible property;
2. tokenization can discard information required to identify that dimension;
3. the same visible language trace admits multiple continuous control realizations;
4. richer graded traces constrain the recovered control field much more strongly.

This sharpens the human-language hypothesis. Observing a low-dimensional control field in a language model does not by itself prove that human cognition has the same dimensionality, because discrete linguistic traces may both erase teacher geometry and permit student-specific extra geometry. Recovering teacher dimensionality requires studying what aspects of the trace survive tokenization and what additional constraints repeatedly force the same control subspace.
