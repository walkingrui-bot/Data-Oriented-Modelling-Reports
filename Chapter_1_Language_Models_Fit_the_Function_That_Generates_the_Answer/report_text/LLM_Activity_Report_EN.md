# Language Models Fit the Function That Generates the Answer

*Phase 1 · Chasing the rule behind the words*

Independent research report · Revised 26 September 2026

A language model is fitting the function that will generate its answer. That is the central claim of this research. The problem, the context and the computation so far assemble a particular way of generating: which relations matter, which history gets recruited, which continuations become available. The answer comes out of that organization. Thinking is the work of bringing it into being.

Once that function becomes the object of study, the whole scene changes. A pause, a detour, a return to an earlier sentence, a sudden answer: each becomes a visible event in the formation of a generator. It may come together in one forward pass. It may develop through internal state, repeated reading or a long external chain of thought. Training supplies the repertoire. Inference gets a particular generative function working on a particular problem.

By fitting, we mean the formation and adjustment of that effective function during inference. The weights can stay frozen as context changes runtime state, recruits different parts of history and reshapes the distribution of successors. In our explicit constructions, an executed transition goes further: it rewrites the conditions that generate later transitions. We follow this object through functional transfer, historical interventions and rules built to be taken apart.

This report follows 27 experiments, E01–E27, from language fingerprints to neural interventions and a world of self-rewriting rules. The wager is simple and large: to understand an answer, get hold of the process that makes it generatable.

## The claims, up front

Here is where each claim stands, with the experiments that put it there. The central thesis gives the expedition its direction; the rows below keep track of what each test actually settled.

| ID | Claim | Status | Evidence |
| --- | --- | --- | --- |
| H20 | Language models fit generative functions capable of producing final answers | Unifying working hypothesis | E01–E27 |
| H11 | Runtime state transfers rule-specific function to a new input | Demonstrated in model | E18 |
| H12 | Rule formation can occur within one forward pass | Demonstrated | E26 |
| H14 | RTG produces temporal and lineage dynamics | Constructively demonstrated | E20–E22 |
| H01 | Identity order and local recurrence carry structural information | Observational support | E01–E07 |
| H02 | Relational geometry partly survives language and form changes | Observational support | E03–E06 E13 |
| H03 | Surface identity or visit strength suffices for gaze targeting | Unsupported in pilot | E10 E11 |
| H04 | Regression launch has lower local duration load | Exploratory support | E10 |
| H05 | Real motion history improves prediction from low-dimensional projections | Supported in tested settings | E16 E22 E25 |
| H06 | D C describes movement regimes in some systems | Observed support | E16 E25 |
| H07 | Concentrated states necessarily have lower transition entropy | Robust version retired | E16 |
| H08 | Raw attention weight equals intervention effect | Refuted under tested definition | E26 |
| H09 | Selective historical influence is realized across architectures | Demonstrated in task | E26 |
| H10 | A local donor activation suffices to reproduce historical effects | Local sufficiency refuted | E26 |
| H13 | Additional THINK progressively sharpens rules and improves performance | Pending | E19 |
| H15 | RTG outperforms ordinary recurrence on static permutations | Advantage prediction failed | E23 |
| H16 | Final-answer supervision trains nonzero RTG writes | Demonstrated in task | E23 |
| H17 | Combined constraints maintain long-run graph stability | Constructively demonstrated | E24 |
| H18 | Real large models use the specific RTG mechanism | Pending | E20–E25 |
| H19 | Deep-layer displacement partly reproduces a prompt effect | Recorded support | E27 |
| H21 | AIA internal projections implement costly self-observation | Architecture and testable prediction | §3 |
| H22 | DeepSeek continuation matches the human reference fingerprint of 0.263 | Exact match recorded | E14 |

## 1 Strip away the wording. What is still there?

We began by pushing expression around: five languages, classical and modern Chinese, several retellings of a story, and round trips from programs to natural-language explanations and back. Words changed. Syntax changed. Speakers changed. Parts of the relational organization kept showing up. A useful unit emerged: a relational packet, several elements holding one another in place through roles and directions, then reaching into another packet.

The measurements gave that intuition teeth. In Natural L3, local offsets gave AUC 0.558; adding same-identity recurrence raised it to 0.751. Typed, directed bridge propagation reached 0.883 over successive rounds, against 0.486 after position shuffling. Classical/modern pairs gave aggregate bridge AUC 0.842. Program–explanation round trips passed 229014 execution comparisons. We could now change the expression, preserve selected content and measure the structure that came through.

Block shuffling located much of that signal at local and intermediate scales: preserve larger contiguous pieces and the original becomes harder to distinguish from the shuffle. Deep backtracking from a single anchor faded quickly; related groups held up better. The picture taking shape was a traffic of relational packets, continuing, recombining and reactivating through a visible stream of words.

## 2 Thought has somewhere to go back to

Reading already gives us movement: a jump, a pause, a return, a line whose arrangement changes what happens next. Even the feeling that an argument has gone wrong can arrive before a clean verbal objection. Some relation is still pulling. Our interpretation puts abstract thought inside perception and action: an unresolved relation recruits an earlier activity pattern, and their coordination gives the present a new direction.

The gaze work split the return into two questions: when does a return open up, and what deserves to be revisited? In data from two participants, regression launches favored lower local duration load. Choosing the destination called for richer relational information. The proposed mechanism leaves an eligibility trace for unfinished relations, opens a revisit gate as load falls, and spreads affinity across historical packets. Competition, support and decay settle that field into a useful reinstatement. E10–E12 contain the pilot and its controls.

That makes the learning target an entire coordination episode. Which present state called up which old packet? How did they interact? What became possible afterward? A large, sparsely active Packet Field has something concrete to learn here. Old material earns its place in the present by helping the process continue. Episode-level credit assignment becomes central: learn the coordination that made the return useful.

## 3 Beneath language, above life

Intelligence lives “beneath language and above life.” Life keeps activity going. Intelligence organizes activity through relations, history and consequences. Language gives some of that organization a form that can travel, survive and be read again. The research object is this ongoing relational organization. Language, gaze and action are ways of catching it in motion.

AIA gives that idea three functional fields. CEG is the ecology of continuing updates, bounded activity, competition and decay. The second field is that activity organized by events, historical relations and consequences. The third opens finite interfaces for observation and action, including language. The second field lives in how the first continues: old relations gain influence, new relations take shape, and the next action acquires its conditions.

Self-observation grew from a fixed readout Z into changes, multistage snapshots and then Public, Focus and Flow. Public exposes an already formed common surface. Focus spends reading resources locally. Flow samples provenance, current paths and possible continuations. Together they give the system temporal slices, local detail and paths to inspect. Using an interface also changes what the system encounters next.

Reading becomes a way of writing. Speaking, focusing and tracing a path all add conditions to the next state. This yields a concrete architectural prediction: an action tendency can form in the persistent field before the reporting field puts it into words. Change the reporting interface and the action organization separately, and their effects can come apart. A persistent internal field, an external reasoning chain, or both can carry this loop.

## 4 DeepSeek hits 0.263. The chase changes.

The first turning point came with three decimal places: 0.263. The human reference: 0.263. The DeepSeek-V3-Base continuation: 0.263. An exact match at the reported precision. A base model continuing a passage had regenerated the measured recurrence fingerprint. That was the jolt. We had been measuring the shape of language; now the generator of that shape had stepped into view.

| Comparison | Recurrence density | Role in the study |
| --- | --- | --- |
| Human reference | 0.263 | Relational fingerprint |
| DeepSeek-V3-Base continuation | 0.263 | The same fingerprint in a continuation |

The comparison used a base-model continuation in the same authorial context. The author’s public example contains the unfinished blog passage submitted to DeepSeek-V3-Base and the selected completion [8]. The research record measures recurrence density in the human reference and that continuation. The exact 0.263 match belongs to this measurement. This was the result that changed the direction of the investigation.

The claim became bolder: learning language includes learning ways to generate its relational organization. Training acquires a family of generative possibilities; context brings one mode into operation. Recurrence density is a fingerprint left behind. We wanted the thing leaving the fingerprint. What kind of process could keep generating this organization as the text moved forward?

## 5 The path knows something the snapshot leaves out

Long reasoning traces gave us motion to inspect. Let z describe relational statistics in successive windows, v describe their change, and a describe the change in that change. Then ask a sharp question: after seeing the present slice, how much does the path into it still tell us?

In the QwQ record, five-fold one-step MSE fell from 0.889 with z alone to 0.835 with z/v/a. Break the temporal alignment and it rose to 0.909. Endpoint MSE moved from 1.008 to 0.956, versus 1.011 under mismatch. Several window sizes retained the direction. The path was carrying predictive information beyond the current relational projection. How the process got here mattered to what it did next.

Then came a result with a wonderfully awkward implication for a straight-line picture of thought: about 50.76% of steps moved closer to the endpoint. Roughly half. Reasoning turns, returns and temporarily heads away. Concentrated movement can also be faster, so speed and progress deserve separate dials. Diffuse and concentrated regimes, D/C, describe recurring patterns within that larger history-dependent movement.

## 6 The model writes something. Then it meets what it wrote.

Think of a ticker timer: movement leaves a sequence of marks, and the marks retain changes of direction, speed, retreat and renewed motion. Visible reasoning gives us such a trace. Language also does something especially consequential: it stays in the context. The process gets to encounter its own marks again.

CoT is therefore an observation surface, a memory surface and a control surface at once. Present organization produces a sentence. The sentence enters history. That history participates in the next organization. Speaking becomes active probing: the model encounters itself through its own projection, much as a gaze movement brings new input. The loop is effective rule → textual projection → rereading → a new effective rule.

This is also where a long chain can acquire its own gravity. Each output edits the conditions of the next computation. A small displacement can become the reference for another displacement, and later text can grow beautifully coherent with the world the model has just written for itself. That gives long-chain drift a mechanism hypothesis: self-writing gradually moves the generator’s reference. More running time lets a rule form, and then lets it keep changing.

## 7 Freeze the weights. Watch the rule move.

Frozen networks gave us handles: context, historical reads, rereading after writes and contextual routing geometry. In random-permutation tasks, Pilot 01 had the model emit intermediate states and read them back. External text preserved state for serial computation and extended a learned operation. The network could keep doing computational work by returning to what it had written.

At the same token and position, different histories produced different K/V states across layers. Replacing deep K states could push the continuation in a chosen direction. E18 sharpened the challenge: give a recipient the donor’s runtime state, then ask it to apply the donor’s rule to the recipient’s starting point. Transporting an executable relation is a demanding target. The experiment separated it from transporting a ready-made answer and traced the effect to distributed runtime organization after contextual processing.

We could now ask what a state makes downstream computation do. Runtime organization carried rule-specific function through reading, reorganization and routing. Formation could also be fast: later direct-answer models reached 100% on the corresponding held-out test within a single forward pass. External reasoning offers a longer workspace; a forward pass can already bring a useful rule into operation.

## 8 Make the past earn its influence

“History matters” becomes much more interesting when a piece of history can be changed. E26 used twelve events across three channels and queried the latest relevant record. Old records and other channels stayed in view. Change the relevant event, an obsolete event or another channel’s event, then measure the output distribution. Now the past has to show what it can actually make happen.

Three architectures answered with strong selectivity. Relevant-record TV was 0.9969 for GRU, 0.9824 for SSM and 0.9990 for Transformer, with much smaller effects for obsolete and other-channel records. Reverse two differing relevant events and the sequence models flipped with the correct answer; the bag model scored 50% across paired cases. Current relevance gave particular historical relations and their order real force.

Attention gave us routing. Intervention gave us consequences. The largest raw-attention position found the relevant record in 90.61% of cases; the largest intervention effect found it in 100%. High attention coincided with low effect at 16.17% of positions. For this question, the more revealing quantity was already in our hands: the power of a historical item to change the continuation.

State transplantation made the distribution of that power visible. Query-position copying gave donor-rule accuracy 22.75%; evidence-position copying gave 37.58%; full-layer copying gave 99.33%. A complete history had organized a distributed computation. Reading a rule label and making the network execute the rule called for different evidence. The whole organization could do what a local transplant left unfinished.

## 9 Catch the transition in the act

Every route kept sending us back to movement. Language statistics showed relational shape. v and a showed direction and turning. K/V and residual states showed organization after computation. Interventions showed what that organization could do next. Put them together and the object is active: read → reorganize → route → generate → write → read again.

A snapshot is wonderfully good at being a snapshot. Explaining the next state asks for the transition that produces it. This is where “operator” acquired its working meaning: the process by which present organization becomes its successor, together with the local constraints expressed in that process. We began looking for how a rule exists in movement.

A checkpoint preserves state; execution gets the transition going. Relational shape, motion, revisits, endpoints, internal routing, language and self-observation gave us complementary views of the same pursuit. They also accumulated demands on a possible mechanism. Eventually those demands became a construction brief.

## 10 Build the rule. Put it under the microscope.

Here came the second turning point: from an unobserved rule to a constructed rule that can be observed. We took relational fingerprints, temporal structure, path effects and self-writing into an executable world. Give a candidate rule explicit state. Give it update laws. Let it run. Then interrupt it, exchange its history and see what breaks or changes. Construction made the rule available for experiment.

The research loop now ran phenomena → empirical constraints → construction → new consequences → independent tests. Alter inheritance. Delete one projection event. Exchange histories. Perturb geometry. Observe the same mechanism’s next move. The question “how does a rule change later rules?” had acquired controls we could operate.

RTG reached this point by an architecture-independent route: start from text statistics and reasoning dynamics, collect their generative demands, and construct relational-transition dynamics that meet them. Neural interventions approached the same problem through layers, attention and runtime state. Both routes asked how history organizes current generation and how current generation changes the future.

RTG is an executable member of that mechanism family. It keeps history, rewrites continuations and generates measurable dynamics. We had put one member of the family on the bench. Now it could be made to show its work.

## 11 The move rewrites the map

Start with what the immediate future makes accessible. A next-step map says how readily each successor can occur; total continuation capacity says how strongly or quickly continuation proceeds. Write K = ΛP: unnormalized capacity K combines total capacity Λ with directional distribution P. Stronger activity can concentrate on fewer possibilities. That gives us a direct way for concentrated movement to become faster.

Then comes a tiny implementation choice with large consequences. After a→b, strengthening a→b records the traveled edge. Changing what happens immediately afterward requires a write into the conditions for leaving b. The completed transition now has descendants. Its occurrence changes which transition gets to occur next.

E20 put numbers on the distinction. Immediate TV change in the next continuation law was zero with static and same-edge updates, 0.0202 with genealogy, and 0.0173 with genealogy plus projection. Neighboring relation-feature similarity also changed with the write mechanism. Projection writes accumulated and altered the future encountered on returning to a position. A bounded write budget kept the process sustainable. The map had become part of the action.

## 12 A transition leaves descendants

The bold idea here is reproduction. A relational transition reproduces conditions for generating its descendants. What gets inherited is a rewrite phenotype: a way of changing the world that comes next. Descendants carry that way of writing into new relations and new circumstances.

RTG gives this idea a local memory M. Present relation features, inherited M at the source, interactions and mutation produce a write phenotype g. It changes successor geometry at the destination and joins the memory available when that destination participates again. History lives in how the system continues to change. Meeting lineages can recombine, compete, reinforce or cancel. Their encounter can generate a continuation new to both.

E21 let us exchange provenance under fixed present conditions. We swapped inherited memory with the current node, geometry and transition conditions held fixed, and compared real, shuffled and absent lineages. The experiment gave inheritance its own intervention. Where the system had come from remained an active ingredient in what it could generate now.

## 13 The construction starts answering back

Once running, RTG produced measurable consequences. In E22, MSE was 0.8792 for state, 0.8655 with v and 0.8553 with v/a; temporal mismatch gave 0.8848. D/C patterns emerged, the concentrated/diffuse speed ratio reached 1.1048, and the endpoint-approach fraction was 0.5233. The constructed world generated directional correspondences with the motion signatures that had helped motivate it.

Delete a single projection write and 141 of 400 pairs diverged within 60 steps under synchronized random streams. Nineteen of 27 neighboring parameter settings passed the joint criteria. One act of self-projection could change a later path, and the joint behavior occupied an explorable parameter region. Observation, history and movement were now coupled inside an executable object.

Final-answer supervision then trained this writing process into task-compatible computation. On static permutations, RTG learned nonzero writes and reached 100% through test horizon 20. Recurrent and other controls reached 100% too. That tie was useful: the answer had run out of resolving power before the mechanisms had run out of differences. We needed to inspect how each system kept generating.

## 14 One million steps. Still moving.

A self-rewriting world deserves a long run. We gave it a million steps: generate, feed the result straight back, let history change the next-step map, repeat. Legal support preserved admissible moves. Bounded writes limited each modification. Frozen or slower reference geometry gave the moving system landmarks.

In the representative million-step run, combined constraints retained late entropy 1.577 and 100% state coverage. Support-mask-only control finished at entropy 0.000015 and coverage 12.5%. After a major perturbation, constrained entropy moved from 1.5771 to 1.5666 and recovered to 1.5777 in the following window. E24 also retains ten-seed runs at a shorter horizon. A stable reference could support a whole region of continuing movement.

That is the kind of stability worth pursuing: room to turn, explore and recover. A teacher trace is one route actually taken. A student can learn constraints that admit several valid routes and then make a new one. The target becomes a generative region rich enough to keep doing useful work.

## 15 The answer is a very small peephole

Many internal organizations can arrive at the same correct answer. A final label gives us a low-dimensional outlet from a high-dimensional process. Content, relational organization, rhythm, tone, style and dependence on context expose far more of its behavior. Add interventions and long feedback loops, and the generative fingerprint becomes much harder to hide behind one score.

Long execution magnifies the difference. Two processes can pass the same early evaluator as small deviations enter their histories. Their next computations inherit those deviations. Reproducing one historical trajectory demands its particular provenance; solving a problem allows external constraints to bring the process into an admissible region along a new valid route. This is why a living generative process deserves to be judged across its movement.

E27 gave us a directional handle on one such factor. A real deep-layer displacement reduced conditional A/B TV from 0.721 to 0.218, against 0.634 for norm-matched random directions. Positive and negative doses moved P(A) continuously. A complete history organizes distributed function, and a particular generative factor can still offer a useful control direction. Both belong in the account.

## 16 Get hold of the generator

The sequence is now concrete: provenance → historical influence → effective rule → next-step map → output → self-writing. Provenance gives the route into the present. Historical influence says which parts of that route can still change the continuation. Their organization forms an effective rule. The next-step map makes successors available. Output realizes one of them and writes conditions for what follows.

Training fits ways of generating language. Inference fits a way of generating this continuation. Learned weights supply capabilities; present history organizes them into an effective function. That organization may form rapidly in one pass or develop through revisiting and rereading. Hesitation, revision and the eventual answer are outward events in the life of the generator.

This is the reason to study language-model activity. Text projects an ongoing process and then returns to it as a new condition. Attention gives one implementation of historical participation. Interventions reveal its consequences. RTG makes inheritance and continued rewriting executable. Each approach gives us another grip on how the present recruits the past to make a future.

Our claim is deliberately large: during reasoning, the model fits the function that generates the answer. The DeepSeek fingerprint sent us after it. Constructing rules gave us a world in which to handle it. The experiments gave us things to measure, transfer, erase, exchange and steer. The next question practically asks itself: once we can observe the generator, how much of its future can we change?

## The lab notebook: E01–E27

Here are the methods, results and interpretations behind the story. Each experiment ID leads to its evidence files in the accompanying repository.

Notation: D/C denotes diffuse and concentrated movement regimes; K/V denotes attention keys and values. Total variation (TV) is half the sum of absolute probability differences, with support defined by each experiment. AUC, ARI, MSE and entropy retain their original experimental scales.

### E01 Role information in anonymous identity and position

**Methods** — Three complexity levels of natural-language and code materials were represented through symbol identity, position and recurrence. Role-discrimination AUC and clustering ARI measured structural readability. Position shuffles preserved the token multiset to separate frequency from order. The retained records are task-level summaries.

**Results** — Natural L1/L2/L3 AUCs were 1.000/0.873/0.642, with ARIs of 1.000/0.757/0.166. Code AUCs were 0.983/0.804/0.922. Related frequency-preserving shuffle controls were approximately 0.48–0.51.

**Interpretation** — Identity and order carry role information in these materials, giving relational structure a measurable footprint.

### E02 Recurrence and typed relational propagation

**Methods** — Natural L3 compared local offsets, multiscale offsets, global same-identity recurrence and iterative typed bridge propagation. Untyped graph diffusion and position shuffles served as controls; coarse and fine roles were evaluated separately.

**Results** — AUC was 0.558 for local offsets, 0.570 for multiscale offsets and 0.751 with global recurrence. Bridge rounds 0–5 yielded 0.707/0.782/0.833/0.858/0.881/0.883; the shuffle result was 0.486. Coarse-role probe accuracy rose from 82.7% to 93.8%, and fine-role accuracy from 86.8% to 92.5%. Untyped diffusion was approximately 0.44–0.50.

**Interpretation** — The results support representations that retain the type and direction of relations surrounding recurrence. They provide structural evidence for reconnecting local relational neighborhoods.

### E03 Structural comparison across five languages

**Methods** — Leave-one-language-out tests covered Chinese, English, French, Japanese and Spanish. The initial representation used Unicode-normalized character bigrams. Shared code terms were removed from program explanations. Formal prose and program explanations were separate groups.

**Results** — For code-term-stripped program explanations, mean local/recurrence/bridge AUCs were 0.871/0.950/0.989. Bridge values in the five languages were 0.958/0.993/0.999/0.999/0.995. Formal-prose means were 0.851/0.909/0.979.

**Interpretation** — Structural-discrimination AUCs show that relational information survives changes in surface language under the archived protocols.

### E04 Structural scale and word-level checks

**Methods** — Contiguous blocks were shuffled as units, preserving within-block order, with block size increasing from 1 to 32. English, Spanish and French were also reanalyzed using word-level units.

**Results** — For stripped program explanations, bridge AUC at block sizes 1/2/4/8/16/24/32 was 1.000/0.995/0.909/0.754/0.643/0.571/0.551. In the three-language word-level check, mean local AUC was approximately 0.865 and bridge AUC 0.858.

**Interpretation** — Preserving larger local blocks made original and shuffled materials more similar, locating much of the discriminative signal at local to intermediate scales. Word-level results retain structural signal, with representation-dependent bridge gains.

### E05 Diachronic rewriting and multilingual relay

**Methods** — Four classical/modern Chinese pairs were tested in both directions: Shi Shuo, Lanting Ji Xu, Zuiweng Ting Ji and Tao Hua Yuan Ji. A nine-version relay of Tao Hua Yuan Ji held the event sequence fixed and used leave-one-version-out evaluation, with additional external English and Japanese versions.

**Results** — Across the four texts, local/recurrence/bridge summary AUCs were 0.592/0.586/0.842. The nine-version bridge result was 0.806±0.012. Effects varied by text and direction; Tao Hua Yuan Ji yielded 0.809 and 0.615 in the two directions. At block sizes 1/2/4/8/16, diachronic bridge AUCs were 0.842/0.692/0.604/0.553/0.486; relay values were 0.807/0.684/0.536/0.482/0.497.

**Interpretation** — Preserving the event sequence preserves part of the relational geometry across rewriting and translation. The variation by text and direction shows how this continuity interacts with expression.

### E06 Program and natural-language round trips

**Methods** — Four small program families and three refactored versions were passed through program/explanation round trips. Exhaustive or dense input-domain execution checks assessed program equivalence, and multilingual explanations were analyzed for relational geometry.

**Results** — All 229014 execution comparisons agreed. Explanation-text local/recurrence/bridge AUCs were 0.697/0.712/0.803. Corresponding bridge AUCs at block sizes 1/2/4/8/12 were 0.806/0.737/0.655/0.581/0.540.

**Interpretation** — Across four program families, 229014 execution comparisons preserve program semantics over the tested input domains. Their explanations also carry measurable relational structure.

### E07 Single-anchor hops and relational groups

**Methods** — Natural language, Go and Rust were tested with repeated single-anchor backtracking and with related three-word/five-word groups, random groups and position shuffles.

**Results** — Single-anchor AUCs at hop 1 were 0.820/0.785/0.799, at hop 2 were 0.534/0.465/0.509, and at hop 5 were 0.215/0.200/0.196. Related three-word groups yielded 0.672/0.664/0.642 and five-word groups 0.582/0.567/0.541. Random three-word groups after five rounds yielded 0.465/0.437/0.437.

**Interpretation** — Short-range backtracking and related groups preserve useful structure. Deep single-anchor hopping rapidly changes the relation between the representation and the original labels.

### E08 Structural evaluation of learning proxies

**Methods** — Predictive backpropagation with homeostatic constraints, repeated versus diverse materials, and directional STDP were compared. Sequence-distribution discrimination and occurrence-level role retention were treated as separate outcomes.

**Results** — Predictive BP yielded L2/L3 AUCs of 0.806/0.809. Thirty sentences repeated ten times yielded 0.689, versus 0.735 for 300 diverse sentences. STDP distribution AUC rose from 0.603 to 0.994, with partial occurrence-role retention.

**Interpretation** — Distribution statistics and occurrence-level relational roles give two distinct views of what a learning system acquires.

### E09 Qualification of the TRF neural prototype

**Methods** — TRF-v0.1R assessed temporal persistence, cross-event flow and structural-language performance against position shuffles over three seeds, 24 lives and 480 events.

**Results** — The prototype sustained temporal persistence and long-distance cross-event flow. Its FULL-versus-shuffle structural-language advantage varied across runs.

**Interpretation** — Persistent activity and cross-event flow were established engineering results. Order sensitivity supplied a separate test of learned language structure.

### E10 Human gaze launch and target selection

**Methods** — The Scanpath Studio OneStop demo contained two readers, 3209 fixations, 680 backward transitions and 188 regressions spanning at least five word positions. Surface selectors used 173 comparable events with distance-matched, previously fixated candidates. Launch analysis used 175 matched events and ranked source duration against nearby forward-reading fixations within trials.

**Results** — Literal recurrence, local bag overlap and ordered surface bridges produced target ranks around 0.43–0.50. The source table gives launch percentiles of 0.3768 per event and 0.3645 under trial-equal weighting, with a bootstrap interval of 0.3002–0.4285; trial-equal duration difference was −22.26 ms. Across minimum regression distances of 2–30 word positions, launch percentiles ranged approximately 0.345–0.426. Exact word-length matching yielded 0.3561 across 23 events, interval 0.2170–0.5049; length ±1 yielded 0.4355 across 110 events, interval 0.3555–0.5155.

**Interpretation** — Launch opportunity and destination selection have different signatures: lower-duration moments favor a return, and choosing its destination recruits additional relational information. The pilot contains two independent readers; event and trial summaries describe repeated observations within those readers.

### E11 Target availability and post-return trajectories

**Methods** — Within the same gaze pilot, previously visited rates were compared between true targets and distance-matched old locations. Visit count, dwell, maximum fixation and recency ranked already-seen candidates. Four-step post-return scanpaths were compared with distance-matched null paths.

**Results** — Previously visited rates were 0.7447 for true targets and 0.6609 for controls. Trial-equal excess was 0.1206, with a bootstrap interval of 0.0557–0.1861. Candidate ranks for count, dwell, maximum fixation, recency and recency×dwell were 0.5135/0.5043/0.4799/0.5055/0.5076. Four-step set overlap was 0.2818 versus 0.2934; exact sequence overlap was 0.313 versus 0.317.

**Interpretation** — Prior visits make historical locations available for return. Candidate selection calls for richer relational information, and the post-return paths motivate reinstatement of useful relations rather than literal replay of a scanpath.

### E12 Candidate distributions in an expected relation field

**Methods** — Public Wilcox predictors were used to compare direct and expected PPMI over old candidates. Nonnegative weights were normalized and exponentiated entropy measured effective candidate count. Six languages and three positional batches were examined for field width and top-target choice.

**Results** — The 18 language-by-batch rows report 290 source observations. Weighting by these counts gives 83.104% with larger expected effective candidate count. The median of the 18 batch-level median ratios is 1.4139; the archived report gives approximately 59% top-target agreement.

**Interpretation** — Expected relation fields spread weight over more historical candidates, motivating a distributed representation of possible return targets.

### E13 Genre authors and parallel translations

**Methods** — Equal-length English content-word windows compared novels, poetry and drama. Hardy and Wilde supplied same-author cross-genre cases, and human translations of Book I of the Odyssey and Iliad supplied same-source comparisons. Historical six-style pilot tables retain their correction flags.

**Results** — Genre explained approximately 55%–62% of author-mean variation in rec/local/mid/long/bridge. Recalculation gives mean window accuracy 52.6786% and 9/14 correct majority predictions; those 14 rows represent 12 unique authors. Hardy and Wilde were approximately 1.22 units from their new-genre centroids. Odyssey translations had recurrence CV 0.5134 and local/long/bridge CVs 0.0556/0.0663/0.0663. The six-style pilot recorded approximately 28%–30% classification with all tokens (reported p=0.033) and 38% with content words (reported p=0.01), against chance 1/6.

**Interpretation** — Genre and content jointly constrain relational geometry. The author comparison contains 12 unique authors and 14 author-by-genre records, with 9 correct majority predictions.

### E14 The DeepSeek Base match that changed the research question

**Methods** — A human reference and a DeepSeek-V3-Base continuation in the same authorial context were compared through recurrence density. The original synthesis records the measurement; the author’s published example identifies the continuation [8].

**Results** — Both recurrence densities were reported as 0.263, to three decimal places.

**Interpretation** — This was the first turning point: a precise match in relational structure redirected the research toward the function generating that structure. Language prediction had reproduced the measured fingerprint, 0.263. The result made the upstream generative rule the next object of investigation.

### E15 Relational geometry of visible chain of thought

**Methods** — ChainScope supplied 16 matched world-model prompt sets for DeepSeek-R1 and DeepSeek-chat, in two batches of eight. The 64-token window analysis used 400 R1 and 321 chat traces. Fixed-lag analysis required at least 96 content words, retaining 398/50 traces, with 14 long QwQ Putnam traces as a model-family check.

**Results** — R1 had lower recurrence, bridge and repeated n-grams in all 16 prompt sets, and higher burst CV in 14/16. After frequency-preserving shuffles, early-to-late local surplus changed by +0.0504 for R1, −0.0120 for chat and +0.1108 for QwQ. With 48-token windows and 24-token lag, early-to-late speeds were 2.943→2.672, 2.817→2.743 and 2.204→2.551.

**Interpretation** — Visible reasoning redistributes relational scales as it develops. Model and window size shape the observed speed and bridge patterns.

### E16 QwQ trajectory prediction and movement regimes

**Methods** — The extended record contains 115 correct QwQ traces; one analysis used 99 sufficiently long traces and 958 nonoverlapping 100-content-word windows. Existing relational statistics defined z, successive differences defined v, and differences of v defined a. Whole-trace holdouts compared predictors, temporal mismatches and endpoints. A separately rewritten analysis used the longest 90 traces, 2590 windows and 2500 z/v states.

**Results** — Five-fold one-step MSEs were 0.889 for z, 0.835 for z/v/a and 0.909 for mismatched motion. Free-rollout second-half MSEs were 1.254/1.194/1.260 and endpoint MSEs 1.008/0.956/1.011; the switching model gave endpoint MSE 0.938. Approximately 50.76% of steps approached the endpoint. The rewritten implementation gave K2 centroid-silhouette 0.346, concentrated/diffuse speeds 0.498/0.454 and transition entropies 0.9994/0.9988 bits. State/+v/+v+a MSEs for windows 80/100/120 were 0.759/0.714/0.708, 0.791/0.743/0.737 and 0.830/0.796/0.775; the window100 all-scale values were 0.674/0.656/0.642.

**Interpretation** — The motion history adds predictive information to the current relational projection. Reanalysis preserves D/C structure and faster concentrated motion; the measured transition entropies place both regimes close to one bit.

### E17 External recurrence and K V intervention with fixed weights

**Methods** — Pilot 01 used a three-layer, 64-dimensional, four-head decoder-only Transformer. Each episode sampled a five-state permutation; prompts gave its table, start and horizon. Training covered lengths 1–5. Frozen evaluation emitted and reread states, with 120 cases per reported horizon. K/V interventions selected baseline-correct donor/recipient episodes with identical three-token prefixes but different successors, aggregating approximately 300 pairs equally across 60 prefixes.

**Results** — At horizons 1/3/5/8, rollout final accuracy was 90.8/88.3/85.8/66.7%. Scoring the first initial-prompt prediction against the final label gave 90.8/35.0/45.0/15.0%. At fixed token/position, K effective rank rose 0→3.431→4.036 and V rank 0→2.553→3.609. Deep K/V/KV patch flip rates were 13.3/1.0/12.0%, with exact donor-target rates 10.7/0/9.7%.

**Interpretation** — This establishes use of external serial computation and deep routing states in the trained network. Its first prediction was trained as the next intermediate state, so the one-shot comparison measures this network’s immediate output. Separately trained direct-answer models are assessed in E26. The multiseed script changes sampling seeds and loads one checkpoint; it supplies intervention-sampling repetitions.

### E18 Transplanting executable state for a latent rule

**Methods** — Pilot 02 retained the three-layer, 64-dimensional, four-head model. The hidden rule was y=(x+b) mod 5, with two examples supplied. States were collected for 1500 episodes; 1484 baseline-correct episodes formed the pairing pool. The main operator test used 500 pairs differing in b and start, transplanting evidence states with the recipient query fixed. Positional decomposition and same-rule controls used separately defined 400-pair sets.

**Results** — Accuracy at horizons 1–5 was 97%–100%. Transplanting all first-layer contextual evidence outputs changed predictions in 83.0% of cases; 51.2% applied the donor rule to the recipient start, and 10.8% emitted the donor’s own answer. Single-position transfer rates were 3.8%–19.3%, versus 51.0% for all evidence in the positional analysis. Restoring recipient K/V downstream reduced main operator transfer to 20.4%/26.0%. A separate upstream explicit-rule control used 1000 rows, 59 prefixes and 295 pairs: first-layer attention-readout transfer reached 84.1% donor targets, versus 0 for MLP transfer and 50.2% for one head. This is a separate sample from the latent-rule experiment.

**Interpretation** — Runtime state transfers rule-specific function. Same-rule replacement retained 70.5% correctness; different-rule replacement yielded 18.0% recipient correctness and 52.0% operator answers. Four dimensions are the algebraic maximum for five centered rule centroids. At scale 1.5, the rule direction increased operator probability by 0.150 versus 0.034 for a wrong direction. Transplanted evidence supplies a causal route through which downstream computation applies the donor rule.

### E19 Progressive THINK with noisy evidence

**Methods** — An independently implemented ten-symbol, 64-dimensional, three-layer, four-head pre-LN Transformer had 155456 parameters. Each episode supplied eight evidence items with 0.3 corruption probability, using final-answer supervision after ANS. Seeds 41/42/43 each received 24000 updates at batch 128, totaling 9216000 online episodes. THINK counts were 0/1/2/3/4/6/8. Each seed used 256 algebraically selected pairs with distinct recipient, donor and operator answers.

**Results** — At 0 THINK, accuracies were 35.01/36.69/49.93%; at 8 THINK they were 35.01/37.26/49.80%, a mean gain of 0.146 percentage points. The 1218 intervention conditions × 256 pairs × three seeds produced 935424 condition outputs. Seed43 had nine exploratory whole-evidence positives, increasing operator probability by approximately 0.100–0.205.

**Interpretation** — Across three independently trained models, additional THINK left mean accuracy nearly unchanged. The intervention sweep exposed local causal control in the evidence region, supplying a route for studying how further computation could develop a rule.

### E20 Decomposing writes to continuation geometry

**Methods** — A CE²G-inspired synthetic relational world compared static, same-edge, signed-local, genealogy, delay, projection and combined variants. A phenotype scan used 16 parameter points with three seeds each. Fixed-condition comparisons used 20/30 seeds for successor-row distributions, revisits and adjacent-edge similarity, followed by write-budget and single-projection deletion controls.

**Results** — Median immediate successor-law TV across 20 seeds was 0 for static and same-edge, 0.0202 for genealogy and 0.0173 for genealogy+projection. At projection strength 0.08, unbudgeted entropy/replay was 0.513/0.455, versus 0.816/0.220 at budget 0.15. Across 80 synchronized pairs, 60-step divergence after deletion was 46.25% in the unbudgeted condition, 38.75% at 0.15 and 48.75% at 0.25.

**Interpretation** — Strengthening an executed edge and rewriting successors of its destination produce different dynamics. Several update rules generate dynamic phenotypes, and bounded writes retain the causal effect of projection.

### E21 Lineage inheritance of rewrite behavior

**Methods** — Each node carries local rewrite state M. The executed transition’s relation feature combines with source M to form a rewrite code, modifying destination successors and M. Fixed, inherited, shuffled-ancestry and no-inheritance conditions were compared. A transplant held geometry, node and current action fixed and exchanged history-produced M.

**Results** — Across 30 seeds, inherited-code lag1–4 similarities were 0.4247/0.2439/0.2051/0.2021, versus 0.0292/0.0175/0.0120/0.0141 for fixed updates. Across 40 seeds, real-minus-shuffled differences were +0.2754/+0.0826/+0.0447/+0.0386. In 750 M transplants, gamma=1 gave median successor TV 0.0099 and 13.9% divergence over 25 steps; gamma=0 gave zero effect.

**Interpretation** — This establishes an inherited state controlling how an action rewrites its successors, with a causal effect in the constructed system. Systems sharing geometry can diverge because M differs; the complete state includes both geometry and M.

### E22 Constructive sufficiency of RTG dynamics

**Methods** — The complete RTG world combines continuation geometry, inherited local rewriting, recombination, mutation, projection events and write budgets. Seven low-bandwidth statistic families define z. Sixty independent trajectories support five-fold trace-level prediction; 400 pairs test projection deletion. A neighborhood scan spans gamma=1.2/1.4/1.6, rho=0.26/0.32/0.38 and genealogy write=0.5/0.6/0.7, totaling 27 points.

**Results** — State/+v/+v+a/mismatched MSEs were 0.8792/0.8655/0.8553/0.8848. K2 silhouette was 0.2632, concentrated/diffuse speed ratio 1.1048, progress difference 0.0589 and endpoint-approach fraction 0.5233. Deleting one projection produced divergence in 141/400 pairs within 60 steps. Nineteen of 27 neighboring parameter points passed the joint criteria.

**Interpretation** — RTG generates temporal predictive structure, recurring movement regimes and causal projection effects in one mechanism. Nineteen successful neighboring parameter settings place these properties in a region of the parameter space. The resulting movement has directional correspondences with the observed CoT trajectories.

### E23 RTG post-training with final-answer supervision

**Methods** — Phase A used ten-state random permutations, a 32-dimensional one-step reader, 16-dimensional relations and write budget 1. Seeds were 101/202/303/404/505. After reader training, the base was frozen. RTG and parameter-matched Elman adapters each had 2836 trainable parameters and used final-answer CE at lengths 1–4. Each seed tested 512 rules with two starts, 11 lengths and ten conditions.

**Results** — There were 4000 base updates and 8970 adapter updates, totaling 12970. Across 563200 formal outputs, post-trained RTG, the recurrent control, iterated reader and no-write/reset-M conditions all reached 100% over lengths 1–20. RTG step0 achieved 85.78% at length 20, rising to 100% after training; mean write norm on prespecified diagnostic trajectories was approximately 0.9998. RTG and the recurrent control had equal final accuracy.

**Interpretation** — Final-answer supervision trains nonzero RTG writes into task-compatible updates. Several mechanisms solve the static-rule task exactly, making their internal dynamics and response to interventions the next useful comparison.

### E24 Long-run stability of a single-step feedback loop

**Methods** — A C++ world had 32 states, five allowed successors per state and 12-dimensional transition features. Free self-writing, support-mask-only and support-plus-budget-plus-reference-relaxation conditions were compared. Each used ten seeds for 100000 steps and seed101 for 1000000 steps, with geometry perturbations at one-quarter, one-half and three-quarters of the run. The constrained version used budget 0.12 and retention 0.98, versus 0.9995 in controls.

**Results** — Across ten seeds, free/mask-only/constrained violation rates were 31.39/0/0%, late entropies 0.065/0.158/1.582 nats and late coverage 43.1/49.7/100%. In the million-step representative run, mask-only late entropy/coverage was 0.000015/12.5%, versus 1.577/100% when constrained. Constrained entropy before perturbation, during the first 1000 subsequent steps and during steps 4000–5000 was 1.5771/1.5666/1.5777.

**Interpretation** — The combined configuration stabilizes a finite symbolic graph: the support mask enforces valid moves, and the full mechanism sustains path diversity and recovery after shocks.

### E25 History-conditioned continuation in three architectures

**Methods** — Episodes sampled A/B permutations and a trigger that switched mode when encountered. GRU, simplified SSM and one-layer causal Transformer used 24 dimensions; Transformer had four heads. Each architecture used seeds 11/22/33 and training length six. Each model supplied 320 sixteen-step trajectories; standardized hidden states were projected onto eight PCA components for five-fold trace-level Ridge prediction.

**Results** — GRU/SSM/Transformer state MSEs were 0.959/1.812/1.593, falling to 0.729/1.367/1.197 with v/a and rising to 0.964/1.819/1.603 after mismatch. On the first 300 of 449 pairs sharing visible state and rule tables but differing in history, TV was 0.365/0.324/0.361 and mean accuracy 0.652/0.633/0.654. D/C clustering varied by architecture. Initial trigger/neutral intervention TV ratios were 1.022/1.040/1.058.

**Interpretation** — Motion adds order-related predictive information to eight-dimensional state projections. Different histories also produce different outputs at the same visible input. E26 follows this result into selective historical participation.

### E26 Selective history attention and distributed state

**Methods** — Round 2 used 12 binary events across three channels, querying the latest value of one channel. Three architectures each used three seeds. Interventions flipped relevant, obsolete same-channel or other-channel values, or swapped the last two differing relevant events, with a bag baseline. Round 3 separately trained three two-layer, 16-dimensional, two-head Transformers on three modular-arithmetic evidence pairs, transplanted local or full-layer state, and trained direct-answer MLP/set controls.

**Results** — Relevant/obsolete/other TV was 0.9969/0.0011/0.0010 for GRU, 0.9824/0.0047/0.0061 for SSM and 0.9990/0.0003/0.0001 for Transformer. All sequence models correctly flipped after order swaps; the bag model achieved approximately 71.1% ordinarily and 50% averaged over pairs. Top attention located the relevant record in 90.61%, versus 100% for top intervention effect; high-attention/low-effect rate was 16.17%. Round 3 query-only/evidence-only/full-layer donor-rule accuracy was 22.75/37.58/99.33%, with TV 0.7654/0.6120/7.43×10⁻⁹.

**Interpretation** — Historical influence measures the output change caused by a value flip. Attention and intervention produce different rankings of that influence. Full-layer copying supplies sufficient state for deterministic downstream computation; the local transfers show how its effect is distributed. Separately trained one-shot MLPs achieved 100% on unseen evidence-x patterns across three seeds. An eight-evidence, 30%-corruption set model averaged 97.17% versus a 97.64% reference, supporting single-forward-pass rule processing.

### E27 Prompt conditioning and within-network displacement

**Methods** — A four-layer, 24-dimensional, three-head Transformer used 16 content classes, a 52-token vocabulary and four prefix positions. STYLE/NEUTRAL set target A-variant probabilities to 0.9/0.1. Model training included all 16 contents. Displacement estimation used contents 0–7; intervention testing used contents 8–15. Mean final-position STYLE−NEUTRAL displacement was injected and compared with ten norm-matched random directions.

**Results** — Reported three-seed baseline TV was 0.721. Real-displacement TV after layers 1/2/3/4 was 0.711/0.674/0.472/0.218, versus 0.716/0.709/0.662/0.634 for random directions. At layer four in seed0, forward doses 0/0.5/1/1.5/2 gave P(A)=0.174/0.400/0.691/0.829/0.880; reverse intervention gave 0.868/0.664/0.363/0.204/0.137.

**Interpretation** — TV measures the conditional A/B distribution, computed from the correct content’s A/B logits. Layer-four injection occurs after the final block and before the output head. The 45-step campaign supplies the reported layer and dose measurements; the retained 220-step script provides a separate implementation of the layer comparison. Deep displacement exposes a continuously controllable generative factor.

## References and resources

[1] Wilcox EG, Pimentel T, Meister C, Cotterell R. An information-theoretic analysis of targeted regressions during reading. Cognition. 2024;249:105765. https://doi.org/10.1016/j.cognition.2024.105765

[2] Rego ATL, Melo AN, Snell J, Meeter M. What drives regressions in reading? Insights from surprisal and saliency from language models. Cognition. 2026;273:106535. https://doi.org/10.1016/j.cognition.2026.106535

[3] Berzak Y, Malmaud J, Shubi O, Meiri Y, Lion E, Levy R. OneStop: A 360-Participant English Eye Tracking Dataset with Different Reading Regimes. Scientific Data. 2025;12:1995. https://doi.org/10.1038/s41597-025-06272-2

[4] Arcuschin I, Janiak J, Krzyzanowski R, Rajamanoharan S, Nanda N, Conmy A. Chain-of-Thought Reasoning In The Wild Is Not Always Faithful. 2025. https://arxiv.org/abs/2503.08679 ; source repository https://github.com/jettjaniak/chainscope

[5] Wilcox regression predictors and analysis repository. https://github.com/wilcoxeg/regressions

[6] Scanpath Studio demonstration data. https://github.com/lacclab/scanpath-studio

[7] Full historical corpus and literature registry: evidence/L_language/sources/source_index.csv

[8] nostalgebraist. The void. Sections 2–3. 2025. https://github.com/nostalgebraist/the-void/blob/main/the-void.md . The continuation appears in sections 2–3; the recurrence measurement appears in Original Synthesis section 12.5.

[Experiment dossiers](../experiments/README.md) · [Evidence index](../EXPERIMENT_INDEX.csv)

## Later evidence update — 2 October 2026

**Evidence status: scope updated by later experiments.**

The original measurements in this report remain part of the experimental record. Subsequent stopping and recovery experiments refine the interpretation of reasoning time and self-written history.

Experiments STOPPING-GEOMETRY-029 and REASONING-HIERARCHICAL-CONTROLLER-027A–027E show that additional computation is a state transition whose value depends on the current predictive state and the selected operation. Answer readiness can already be present at the prompt state, can be lost after a further step, and can reappear later. Readiness sets are frequently disconnected. Passive continuation and repeated generic rescue therefore do not define a monotonic improvement process.

The current interpretation is that explicit chain-of-thought is one observable and reinjectable control trajectory through predictive state. Additional reasoning is useful when the chosen transition moves the system toward an answer-ready region; once readiness is reached, further transitions can have negative value under the same task criterion.

The later recovery hierarchy makes this operational. Across 125 canonical correct-to-wrong exits, the assembled controller assigns 15 events to preventive bypass, 108 to bounded local recovery and 2 to state reconstruction, with immediate readiness recovery in all 125. The corresponding held-out foundation subset contains 60 events and recovers all 60. Append-only rescue remains a verified fallback because repeated rescue is strongly non-monotonic.

This update refines the interpretation of Sections 6–7 and 16 while preserving their executed results. See [Evidence Supersession Audit — 2026-10-02](../EVIDENCE_SUPERSESSION_AUDIT_20261002.md).

