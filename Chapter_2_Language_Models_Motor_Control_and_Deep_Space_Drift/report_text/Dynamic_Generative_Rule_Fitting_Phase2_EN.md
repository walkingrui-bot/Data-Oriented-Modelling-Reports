# Language Models: Motor Control and Deep-Space Drift

*Phase 2 · Instruments and controls for the generative function*

Independent research report · Revised 26 September 2026

Here, motor control means measuring and steering the evolution of generative states and output distributions. The deep-space image follows the chapter’s self-feeding experiments: a drifting trajectory can also shift the reference used to judge its direction.

A language model fits the function that generates its answer. The problem and computational history shape that function; each output adds conditions for what comes next. Thinking brings the generator into operation and changes it through its own results. Phase 2 gives us instruments and controls.

In the constructed tasks, we locate the source of a future fork before outputs separate, map where the future is readable and steerable, and push generation toward a defined reference. Content and state mirrors offset expressed preference and stabilize self-feeding. Here, the future means distributions of upcoming outputs, with measurable horizons, sources and intervention effects.

The ambition is to get our hands on the generator as it forms. Establish north. Find what is pulling the future and where a push still works. Give the correction a dose. Watch the influence left outside the source map. A long reasoning chain becomes something to instrument and steer.

## The claims, up front

Here is what the experiments established and where we go next. H20 carries the central thesis; H34–H35 extend it toward complementary model evolution.

| ID | Final claim | Status | Evidence |
| --- | --- | --- | --- |
| H20 | Models fit functions that generate answers | Unifying hypothesis | E01–E39 |
| H23 | Future influence locates delayed sources | Constructed support | E28–E29 |
| H24 | Integration along an actual counterfactual recovers sources | Constructed support | E29 |
| H25 | Readability and controllability require separate measurements | Constructed support | E30 |
| H26 | Self-history takeover and opposition are distinct | Constructed support | E37 |
| H27 | Balance Band monitors specified source relations | Mechanism-specific support | E37–E38 |
| H28 | A residual influence channel extends source monitoring | Noise-world support | E39 |
| H29 | Complementary content offsets recursive distribution drift | Constructed support | E31 |
| H30 | A learned mirror stabilizes self-fed generation | Constructed support | E32–E33 |
| H31 | Reference identification and stabilization are separate tasks | Constructed support | E34 |
| H32 | Mirrors and direct center estimators are parallel implementations | Comparative support | E35 |
| H33 | Cumulative dose is the main variable in the tested control regime | Dose-matched support | E33 E36 |
| H34 | Transferable generative control variables exist in natural LLMs | Pending direct tests | Proposed protocol |
| H35 | Paired symmetry can support stabilization and co-evolution without center labels | Theoretical direction | Future work |

## 1. The ship moves. So does its idea of north.

Frozen weights leave plenty of room for a moving function. Context, internal state and computational history change the effective continuation rule under the same parameters. That runtime organization is what we call fitting. Phase 1 followed it through one-pass formation and multi-step external reasoning. Both can bring a particular way of generating into operation.

In a self-fed chain, Cₜ → Fₜ → yₜ → Cₜ₊₁ → Fₜ₊₁. The output becomes part of the context that forms the next function. This preserves progress and gives a deviation somewhere to live. The ship drifts; then its compass uses the already-drifted course to redefine north. The next paragraph can sound perfectly at home in the world the previous paragraph just invented.

That gives a useful reasoning interval a dynamical interpretation. Early computation brings external constraints together and forms a region capable of generating the answer. Continued self-history can then acquire more control. Coherence with the accumulated text can rise as fidelity to the original problem falls. Phase 2 puts this hypothesis to work: measure source, direction, horizon and control gain, then see which interventions change the course.

Experiments and claims: H20;E24 E26 E28–E39

## 2. We wanted a better question than “where is the attention?”

The question we wanted was: who has the power to change what comes next? We built the Generative Control Map, GCM, around the future in formation. What continuation is taking shape? Which source shapes it? When will its influence appear? Where can it still be changed? What influence escapes the current source model? Those are five instruments with five operational jobs.

FCI gives the source question an intervention: hold the specified conditions fixed, change a source and measure the resulting change in the future distribution. Attention shows historical routing and helps screen candidates cheaply. Future influence makes a source demonstrate its consequences. For the future we wanted to explain, that was the quantity worth chasing.

| Instrument | Question |
| --- | --- |
| Future-State Readout | Which future is being formed? |
| Attributed Future Influence / FCI | Which known source changes that future? |
| Influence Horizon Profile | At which step does influence appear? |
| Future Control Gain | Which layer and position retain control? |
| Residual Future Influence | What future influence lies outside attributed sources? |

Experiments and claims: E28–E30 E39

## 3. Same opening. Different futures. Find the cause.

We deliberately hid the difference downstream. A query selected one of four historical cues. A/B modes produced the same first two outputs, then split at steps 3–4. A generative constraint could therefore be in place before the visible sequence gave it away. The test was to find its source before the fork appeared.

The first round trained three independent models, with four-step held-out accuracy of about 98.8%, 98.0% and 94.1%. Among correct predictions, averaging equally across seeds, exact FCI located the source with 90.6% Top-1 accuracy. Mean attention gave 42.5%; immediate next-step causal effect gave 32.9%; chance was 25%. Including model errors gave 81.8% for FCI and 41.1% for mean attention. Looking farther ahead recovered influence that the next step barely expressed.

The second round raised the bar with held-out history patterns: 64 examples per model across three models, 192 in total. Attention’s layer and read-position were chosen on training data and fixed for testing. Three-point IDFG followed the actual counterfactual direction and recovered 192 out of 192 sources. Batched future margin and exact FCI did the same. Calibrated attention reached 58.3%. In this task, the source of the future fork was there to be found before the output announced it.

The horizon profile tells the story almost by itself. Relevant-source mean TV was about 0.00005 across the first two steps and about 0.999 at steps 3–4. Every example first crossed TV=0.1 at step 3. The present output could look unchanged as a later divergence was already being prepared.

| Round 2 instrument | Source Top-1 | ROC-AUC |
| --- | --- | --- |
| Calibrated raw attention | 58.3% | 0.772 |
| Attention × future-gradient | 58.3% | 0.708 |
| Future gradient norm | 69.3% | 0.817 |
| Directional Future Gradient | 79.2% | 0.870 |
| Three-point integrated DFG | 100% | 1.000 |
| Batched future margin | 100% | 1.000 |
| Exact FCI | 100% | 1.000 |

Experiments and claims: E28 E29

## 4. The best viewing window can be a terrible steering wheel

Readable and steerable turned out to have different maps. In the second-round network, final-layer mode readout reached 0.896, yet mean control gain at the tested historical positions was zero. Layer 1 gave a weaker readout, 0.672, and a much larger gain, 0.497. A clear view of a future and a handle that can change it belong at different places in this network.

Then we tried the handles. Across 36 independent trajectories, a norm-0.75 intervention along the gradient gave Spearman=0.99515 and Pearson=0.98376 between predicted gain and observed effect. In the first round, bidirectional interventions moved P(A) from 0.117 to 0.465 and, in reverse, from 0.834 to 0.444. Directional control had become an experimental variable.

The engineering move follows directly: read where the future is legible; intervene where measured gain still gives control over the chosen target. A good instrument panel and a good actuator can sit in different layers.

Experiments and claims: E28 E30

## 5. Keep track of who is steering

We built a world in which the sources could be pulled apart. In 4,000 independent trajectories of 120 tokens, eight-step counterfactuals tested Prompt, Question and Self-history separately. External Anchor measured the original problem’s influence. Self-Takeover measured the share acquired by the chain’s own history. Self-Opposition measured how that history pushed against the external anchor. Acquiring control and steering against the problem became separate things to observe.

Define External as FCI_prompt+FCI_question and Takeover as FCI_self/(External+FCI_self). For each full trajectory, Balance Band asks for External to reach at least 95% of its trajectory peak and for Opposition/External<5%. It selected 12–31, close to the near-optimal interval 13–33. Across a 3×3 parameter neighborhood, mean Jaccard was 0.751. The useful interval had a measurable relation among sources.

A separate trajectory split tested advance warning. Calibrate on safe points at least 24 tokens from failure; then predict failure within 12 tokens. At about 5% safe false alarms, Opposition detected 91.4% of imminent failures with a median lead of six tokens. Current output deviation detected 88.3%, with a lead of five. Source direction gave a view of the developing failure, with output deviation providing another useful monitor.

This puts a sharper question underneath “how long should the model think?” Let external constraints do their organizing work; watch the chain’s own history as it starts pulling the future against them. The full-trajectory experiment locates that relation retrospectively. For a live controller, the design in section 14 draws its reference from training data or the prefix already observed.

Experiments and claims: E37

## 6. Give the unaccounted influence its own dial

A source map deserves a test of what it covers. We ran the same Balance Band rule in worlds driven by self-history takeover, prompt dilution and pure latent noise. The third world gave us a further object to measure: Residual / Unattributed Future Influence, the future-changing effect outside the three named sources.

With latent noise available for intervention, adding Residual-FCI/External-Anchor-FCI<5% contracted the pure-noise band from 13–111 to 13–45. Jaccard against the true near-optimal interval 20–54 rose from 0.354 to 0.619. Clearly bad time points classified as balanced fell from 73.5% to zero. The other two worlds retained their intervals. One extra dial materially changed what the instrument could see.

The map now asks both who is steering among known sources and what else is moving the future. Here the latent-noise channel makes that residual directly manipulable. Richer systems invite richer source interventions and tests of their interactions. Coverage itself becomes part of the measurement design.

| Constructed world | Near-optimal | Final monitored band | Jaccard |
| --- | --- | --- | --- |
| Self-history takeover | 13–33 | 12–31 | 0.864 |
| Prompt dilution | 21–39 | 11–33 | 0.448 |
| Pure latent noise | 20–54 | 13–45 | 0.619 |

Experiments and claims: E38 E39

## 7. Give the ship landmarks and room to move

Phase 1 had already run the reference idea for a million steps. E24 separated fast local rewriting from frozen or slow reference geometry: zero out-of-bounds transitions, 100% late coverage, late entropy 1.577 and maximum single-state occupancy 3.74%. The process kept generating a rich range of admissible movement.

The controls make the result vivid. Support-only control stayed inside the allowed region but fell to late entropy 0.000015 and coverage 12.5%. Free self-conditioning produced 46.06% out-of-bounds transitions across the full run. After strong shocks, constrained entropy moved from 1.5771 to 1.5666 and recovered to 1.5777 in the 4,000–5,000-step window. The target was a region in which useful movement could keep happening.

Phase 2 brought that reference into local control. Construct the counterpart of the present deviation around a defined center. Let the original and its counterpart shape the next generative function together. The reference tells us where north is; the mirror supplies an opposing structure we can use here and now.

Experiments and claims: E24;E31–E36

## 8. Let the preference show itself. Write its counterpart.

The first mirror was almost cheeky. Let the model generate a short block, exposing its current preference; then write an equally sized complementary block back into context. The binary Transformer had four layers, hidden size 32, four heads and a 31-token context, with known center p*=0.5. If its eight generated tokens contained k ones, the shuffled eight-token mirror contained 8−k ones.

All three conditions added 16 tokens per round, over 64 independent trajectories and 80 rounds. The hard mirror finished at mean deviation 0.0195: about 92.3% below self-feeding and 80.9% below random neutral blocks. Inside a round, deviation fell from 0.06595 after the self block to 0.01854 after the mirror. We could watch the preference appear and then watch the complementary write offset it.

That makes preference a control problem with an observable relation. The second block’s antisymmetry to the bias just expressed determines how much deviation survives read-back. The content writes against a particular deviation and changes the next generation. Then we took the same idea inside the generator.

| Read-back condition | Final mean deviation | Extreme fraction |
| --- | --- | --- |
| 16 self-generated tokens | 0.2540 | 48.44% |
| 8 self + 8 random neutral | 0.1022 | 0% |
| 8 self + 8 exact mirror | 0.0195 | 0% |

Experiments and claims: E31

## 9. Put the mirror inside the state

The Mirror Generation Controller, MGC, learns opposite-drift state pairs under the same task condition: M(h₊)≈h₋ and M(M(h))≈h. Their midpoint, [h+M(h)]/2, estimates a local center; [h−M(h)]/2 extracts antisymmetric deviation. In local symmetric coordinates, the ideal relation is M(G)=2G*−G, with both states in the generator’s valid domain. The mirror gives us a center and a counter-state in one construction.

In a nonlinear 24-dimensional self-fed world, a two-hidden-layer MLP reached mirror MSE 0.0152 and involution error 0.00822. Under harder perturbations, its midpoint cut state MSE to the reference center from 0.3806 to 0.0553 and output TV from 0.2139 to 0.0818. The current state carried enough structure for the learned mirror to recover a useful local center.

We then ran eight independent trajectories per condition for 30,000 steps, with shocks at steps 7,500, 15,000 and 22,500. Learned-mirror late TV was 0.0214. Free generation gave 0.0884, a clone 0.0880 and a random mirror 0.1279. The learned symmetry supplied the useful control. Reference relations entered training pairs and evaluation; runtime control took the current hidden state as input.

The midpoint served as the center diagnostic; the running controller fused logits from the state and its mirror. A nonlinear decoder makes these different operations, and the experiment records them separately. Together they turn internal correspondence into something that can keep a generator near a reference through repeated self-feeding.

Experiments and claims: E32

## 10. A very good compass will take you to the north you teach it

We deliberately taught one mirror a shifted center. Across 64 trajectories of 6,000 tokens, late TV was 0.0958 to that taught center and 0.1833 to the true center. A correct-center mirror gave 0.0797 to the true center; free generation gave 0.4197. The stabilizer did its job around the reference it had learned. Choosing north and holding course are experimentally separable jobs.

Direct center labels gave us another route. A same-width estimator trained on the same distribution achieved output TV 0.0364 under harder static perturbations, compared with 0.0431 for the mirror midpoint. Closed-loop values were 0.0679 and 0.0797 respectively. Direct estimation stayed slightly ahead through unseen drift-radius bands of 2.5–3.0. If the center is available as a label, estimate it directly: the experiment makes that option attractive.

Mirrors offer a second object as well as a center: the counterpart of the present deviation. That points to a particularly interesting next test. Learn from paired opposite deviations around the same task and see what their relation teaches about north. Direct labels and paired symmetry give us two ways to organize the supervision.

Experiments and claims: E34 E35

## 11. Turn the dose dial

Dynamic mirror control, TMC, writes the intervention as lᶜᵗʳˡ=(1−λ)l(h)+λl(M(h)). Now the amount of mirror contribution is a dial. In ten independent trajectories of 3,000 tokens, raising per-step λ from zero to 0.50 lowered late TV from 0.4167 to 0.0766, with decreasing intermediate values. The generative function responded continuously to the control input.

We then held dose steady and changed cadence. Forty-eight paired trajectories shared common random numbers over 4,000 tokens. Intervals of 1/2/4/8/16 tokens used λ=0.025/0.05/0.10/0.20/0.40: the same nominal 0.025/token. The five late-TV means spanned 0.0044. Every-1 minus every-16 was −0.00047, with paired-bootstrap 95% CI [−0.00996,0.00893]. In this world, cumulative dose explained the main stability benefit.

The archived fixed-λ cadence sweep had given 0.0675 late TV for every-token control and 0.4155 for free generation. Increasing intervention frequency there also increased total dose. The matched-dose result settles the interpretation of that gain: cumulative control input is the main dial in this construction. Timing gets its own sharper test in worlds with irreversible writes, saturation or brief control windows.

The controls also survived repeated shocks. Six trajectories of 8,000 steps received shocks at steps 2,000/4,000/6,000. Adaptive and every-step mirrors gave late TV=0.0508 and 0.0525, against 0.4244 for free generation. Across the first 250 post-shock steps, mean TV was 0.0658 and 0.0661. The loop kept returning generation toward its reference as read-back and external disturbances continued.

| Interval (tokens) | λ per intervention | Late TV |
| --- | --- | --- |
| 1 | 0.025 | 0.3931 |
| 2 | 0.050 | 0.3965 |
| 4 | 0.100 | 0.3946 |
| 8 | 0.200 | 0.3975 |
| 16 | 0.400 | 0.3935 |
| Free generation | 0 | 0.4162 |

Experiments and claims: E33 E36

## 12. An instrument panel, a reference and a set of controls

The parts now have jobs. Reference relations define where useful generation can move. GCM reads the future state, attributes sources and maps horizon and gain. The residual channel watches additional influence. A mirror or direct estimator supplies a corrective direction. Dynamic control sets its dose and timing. A content mirror reaches the same loop through external context.

Put those parts together and the next joint experiment writes itself. Let external constraints integrate. Re-anchor or intervene when sources push against them. Expand source checks when residual influence rises. Move the intervention to another site, or return to a stable anchor, when control gain falls. This is a proposed adaptive loop built from tested components, with a measurement and an action attached to each decision.

The target is a generative function that keeps serving the original problem and retains room to move. The same final constraints can support several textual routes, internal states and local searches. Control can preserve that freedom by acting on the organization that keeps appropriate answers generatable. Keep the generator on course and give it room to find a route.

Experiments and claims: E24 E28–E39

## 13. What if the next generation had a counterpart?

The loop also appears across model generations: Mₜ produces Dₜ, and Dₜ trains Mₜ₊₁. Preferences, omitted regions and habitual ways of generating can travel through it. Independent data, verifiable consequences and complementary bias structure provide different places to anchor the process.

Mirror co-evolution takes the local idea across generations: build a counterpart that offsets present bias, and let successive models fit through complementary relations. Content and state mirrors already give us local mechanisms to experiment with. The next hypothesis asks whether paired deviations around a shared task can teach a symmetry that helps successive models keep their bearings.

For natural language, north can draw on the original problem, verifiable consequences, stable relational geometry and multiple views of the result. The next construction needs high-dimensional generative variables that preserve semantic and task invariants, with a center or paired symmetry defined around them. The present experiments give that pursuit measurable interfaces: sources, horizons, states, gain and controlled continuations.

Experiments and claims: H34 H35

## 14. Take the instruments to a natural LLM

The next direct test starts with an open-weight reasoning model. Delete, replace or compress the system prompt, user question, early reasoning and recent reasoning separately. Measure short-horizon FCI and influence horizons. Read future state. Map control gain by layer and position. Then connect source changes before harmful overthinking to independent task outcomes. The experiment should make the original problem’s changing influence visible.

Compare question re-anchoring, verified-relation compression, direct center estimation, paired state mirrors and content mirrors at matched dose. Give reference identification its own experimental conditions. Track semantic preservation, answer quality, long-run distribution drift and cost under center labels, paired labels and unseen tasks. Calibrate online Balance Band thresholds from prefix-available quantities and design the residual channel alongside the source interventions.

Existing studies provide useful points of contact in natural language: reasoning-path deviation and harmful overthinking [1–2], followed by reasoning faithfulness, CoT and activation monitoring, counterfactual explanations and reasoning structure [3–6]. Our route into this territory is the generator itself. Read what is forming. Find what can still change it. Then try the controls.

Experiments and claims: Proposed protocol

## Open the experiment folders

Phase 2 adds twelve experiments, E28–E39, to the first phase’s E01–E27. Each folder gives the English methods, results and interpretation, plus experiment.json and artifacts.csv. Shared tables, figures and protocols live under evidence/phase2/.

| Experiments | Subject | Evidence directory |
| --- | --- | --- |
| E28 | Future causal influence | G1_generative_control |
| E29–E30 | Future instruments and control sites | G2_future_instruments |
| E31 | Content mirror | M0_content_mirror |
| E32 | State mirror | M1_state_mirror |
| E33 | Dynamic mirror | M2_dynamic_mirror |
| E37 | Source control and balance | B1_causal_balance |
| E34–E36; E38–E39 | Center, dose, sources and residuals | V1_mechanism_tests |

EXPERIMENT_INDEX.csv takes each result back to its evidence files. FINAL_INTERPRETATIONS.csv collects the current findings. The evidence folders hold the original protocols, tables and figures; audit/recalculate_phase2.py recomputes their summaries.

Notation: TV is total variation, usually half the sum of absolute probability differences; MSE is mean squared error; KL is relative entropy; AUC is area under the ROC curve. Each world’s distribution support and summary window follow its protocol. Means, trajectory quantiles and confidence intervals are kept distinct.

## References

[1] Guan, W. et al. (2026). Mitigating Overthinking in Large Reasoning Language Models via Reasoning Path Deviation Monitoring. https://arxiv.org/abs/2603.14251

[2] Caldarella, S., Talon, D., Aljundi, R., Ricci, E., & Mancini, M. (2026). Thinking Past the Answer: Evaluating Harmful Overthinking in Large Reasoning Models. https://arxiv.org/abs/2606.02835

[3] Chen, Y. et al. (Anthropic). Reasoning Models Don’t Always Say What They Think. https://assets.anthropic.com/m/71876fabef0f0ed4/original/reasoning_models_paper.pdf

[4] Pachocki, J. / OpenAI (2026). An Alien Mind. https://openai.com/index/an-alien-mind/

[5] Karvonen, A., Ong, E., Kantamneni, S., & Marks, S. (2026). Would This Change Your Answer? Evaluating Explanations of LLM Behavior in the Wild with Counterfactual Experiments (CHIVE). https://alignment.anthropic.com/2026/chive/

[6] Google DeepMind (2026). Towards Structural Understanding of LLM Overthinking. https://deepmind.google/research/publications/203490/

[Experiment dossiers](../../Chapter_1_Language_Models_Fit_the_Function_That_Generates_the_Answer/experiments/README.md) · [Evidence index](../../Chapter_1_Language_Models_Fit_the_Function_That_Generates_the_Answer/EXPERIMENT_INDEX.csv)
