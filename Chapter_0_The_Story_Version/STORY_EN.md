# Chapter 0 — The Story Version

**Don't feel like reading the reports? Getting lost in them? Start here.**

[Chapter 0](README.md) · [All chapters](../README.md) · [Download Word](Data_Oriented_Modelling_Living_Narrative_EN_v0.8_20260930.docx)

## Data Oriented Modelling

*A Living Explanatory Narrative*

*From why data takes this shape to what a model treats as its world*

English version 0.8 · 30 September 2026

This is the explanatory companion to Data-Oriented Modelling. It keeps the intuitions, stories, metaphors, distinctions and sequence of explanations behind the research together. It is a living account for readers of the reports, talks and teaching materials.

## How to read this story

This is not a conversation dressed up as a paper. It deliberately keeps the part of our conversations that was most useful: start with a story anyone can understand, then gradually discover that the story contains the underlying structure of statistics, machine learning, generative models, general data intelligence and chains of thought. A paper might introduce many of these ideas with equations. Here we first ask: if we imagine data as a person, and a model as something that keeps observing, comparing and finding its bearings again, what is it actually doing?

The story starts with the most ordinary statistics and travels all the way to training history, future-response fields and the unfolding of a chain of thought one point at a time. None of the metaphors is a final mathematical definition. They are ways of making the structure visible. Once we can see it, we can decide which parts need formal definitions and which need experimental tests.

The most important principle is simple: explain the world first, then introduce the equations. Equations should pin down a structure we already understand, rather than hide it.

### A few conventions for this story

- The “time axis” is the directed axis along which the state of the world moves forward. We do not invent a separate “causal axis”.

- “Degrees of freedom” means the number of relatively independent ways a system can currently change. It is neither the number of variables nor the volume of the reachable space.

- In this story, a “generating mechanism” is not a label handed to us in advance. It is a concept we arrive at after observing many stable, repeated and mutually compatible constraints and changes.

- “Motor control” has a specific meaning in this project: the continuous process, familiar from language models, of locating the current state from the preceding context and then deciding what comes next. The term does not automatically include robot policies or other systems here.

- A “language model” is first of all a computational pattern here: generate what follows from what came before. Natural language is its most familiar example; general data intelligence can use a similar structure.

- The Data Passport is broader than Data Geometry. Data Geometry is one of its most important eyesight tests: has the model's view of the world been stretched, flattened, bent or blurred together by its lenses?

- Chain-of-thought text is not a word-for-word transcript of a model's internal “thoughts”. What we want to study is how the probabilities of possible future responses change at each point in generation.

- “State” does not introduce a mysterious extra entity here. It means the statistical state that the same data or language presents at a particular observation scale. Change the scale, and the state you can see changes too.

- Architecture is not the sole protagonist of the second half. Architecture makes some structures easier to implement and learn. How training data is laid out, ordered, grouped, sampled and mixed, and the history of those experiences, shapes which structures the model eventually treats as its world.

## 1 Understanding the data cloud before discussing models

At the beginning, we did just one thing: take “data” out of the table. A table is what we get when we lay out a more complicated, higher-dimensional state along a few chosen axes so that humans can read it. The data itself is more like a moving mass of material. As the world moves forward in time, that material keeps changing state. Humans choose a way to observe it, cut those states into rows and columns, and end up with the familiar data table.

t → Z(t)

Time is special here. You can sit completely still, and time still moves on. You cannot stop it or make the world run backwards in the same sense. We do not count time as “one more degree of freedom for the body”. We treat it as the advancing axis to which all state changes are tied. What is worth counting is how many relatively independent ways the state Z can change as time moves forward.

### 1.1 One finger can explain dimensions and degrees of freedom

Suppose we look only at a fingertip. Its position lives in three-dimensional space, so we can write it as (x, y, z). But if we fix the shoulder, elbow and wrist and allow just one finger joint to turn, the fingertip can only move along an arc. It still lives in three-dimensional space. That does not give it three degrees of freedom.

Ambient dimension = 3; effective movement dimension ≈ 1.

Now release a second joint. The fingertip may begin to sweep out a surface instead of following a single line. Release the wrist, and its reachable region expands again. Release the elbow and shoulder, bring the whole arm into the movement, and the fingertip can reach more places. Let the waist join in, let the legs walk, let the whole person jump, and the reachable space grows further. Finally, add stairs, lifts or vehicles. The body has not suddenly acquired dozens of new joint degrees of freedom, but the person can now reach a much larger space.

Degrees of freedom asks, “How many independent ways can you move?” Reachable space asks, “Where can those movements ultimately take you?” We must not confuse the two.

There is another important detail. The arm can have many internal joint degrees of freedom, while the endpoint task, “put the fingertip at a position in three-dimensional space”, has at most three position directions. A system with many internal degrees of freedom can therefore produce a low-dimensional observation. Conversely, looking only at the fingertip may tell us nothing about whether the shoulder moved, the elbow bent, the wrist turned or the whole person took an extra step.

Internal state q → endpoint p = f(q)

This is the simplest version of a distinction we will keep meeting: the same output can come from different internal states.

### 1.2 High dimension can come from things moving together

Now replace the body with data. Imagine many simple little objects, each with only one or two ways to change. If their movements are partly independent and partly coupled, the whole system can have many joint directions of variation. The key question is not whether every variable is independent. It is how many relatively independent joint patterns of movement we need to describe what the whole system actually does.

So a high effective dimension in genomic data should not be imagined as “192 completely independent switches, making the number of combinations explode”. Think instead of a body with many joints. The joints are neither completely independent nor welded into a single rigid stick. They form many partly coupled patterns of movement. We need many directions to describe the variation, but those directions are not all unrelated.

Many simple objects, partly independent and partly moving together, can produce many degrees of freedom. Coordinated changes across objects can be part of what gives the combined system its directions of variation.

### 1.3 Remove the order in time and a trajectory becomes a data cloud

Lay out the states frame by frame in time, and we get a trajectory: Z(t₁), Z(t₂), Z(t₃), and so on. Temporarily forget which came first and pile those states together, and we get a data cloud. The cloud is not the world itself. It is the visible trail the world has left behind.

{Z(t₁), Z(t₂), …, Z(tₙ)} → observed data cloud

At this point, many impressive-sounding terms in data geometry become ordinary descriptions of a moving body. Shape is the shape the generating system can sweep out. A boundary marks how far it can go. Density shows where it tends to spend its time. Anisotropy means it moves easily in some directions and reluctantly in others. Curvature describes how quickly the allowed directions of movement change as its position changes.

In a formal treatment, Data Geometry systematically measures these shapes as the model sees them. But Data Geometry is only one part of the Data Passport.

### 1.4 Statistical transformations change the viewing axes

There are many ways for humans to lay out this mass of data. A simple statistical transformation does not create another world. It puts a different ruler or coordinate system in front of the same one. Perhaps a relationship looks very curved along x. A statistician uses prior knowledge to look at log(x), x² or a spline basis instead. It is as if we have bent the viewing axis, then laid out the same states again.

Same underlying states → new coordinate map φ(x) → different visible geometry

Polynomial terms, log transformations and basis expansions can look like “adding a few more columns”. More fundamentally, they redefine the coordinates the model sees. Two states that were close can be pulled farther apart in the new coordinates. A curved relationship can look straighter. We have not secretly replaced the points or changed the world. We have changed the map.

At its simplest, a statistical transformation takes the same data and lays it out in a way a human thinks will be more meaningful.

This helps explain why traditional statistics often feels so reasoned. Statisticians do not usually bend an axis for no reason: a log for skewness, a spline for local nonlinearity, periodic terms for seasonality, an interaction for suspected effect modification. Each new view comes with a reason someone can put into words.

Traditional statistics can therefore be understood as representation design guided by human prior knowledge. A person looks at the data, decides which angle to try next, inspects the residuals and decides whether another ruler is needed. There can even be many layers. There is simply a statistician sitting between each pair.

Traditional statistics is like “look at a photograph → understand it → decide how to take the next one”. Many deep models also learn how the next photograph should be taken.

### 1.5 From a line to a cloud as more directions become free

Begin with an ideal world whose state has only one freely varying coordinate, u. However high-dimensional the surrounding space is, all the data must lie along a one-dimensional path. It can be a straight line or an arc. What matters is the single free parameter, not whether the path is straight.

Z = g(u) → one-dimensional reachable path

Release a second genuinely independent coordinate, u₂, and that path may spread into a surface. Release a third, and it can form a volume. Release more joint directions of variation, and the reachable state space expands further. Finally, remove the time order, and the cloud we see becomes thicker and richer.

That is why dimension is best understood as something more than the number of columns in a table. What matters is how many relatively independent directions of change those columns allow, and how those directions are constrained, coupled, compressed or opened up.

## 2 Correlation multiple modes and outliers are not mysterious either

### 2.1 Correlation when the same movement carries two measurements along

Stay with the human body. When someone squats normally, their knees bend more and their body usually gets lower. Plot many such movements, and the two measurements often change together. At its simplest, correlation means that as the system follows its allowed paths, two observation coordinates share part of the movement.

Shared movement → statistical correlation

But squatting is not the only way to get lower. You can sit, kneel, bend over, fall, or even stand on ground that moves. Bent knees and a low body can be strongly correlated within one common mechanism without being the only route to that outcome.

A strong correlation tells us that two observed directions often move together. It does not guarantee that only one generating path can produce the result.

### 2.2 Multiple modes when a system has several favourite postures

People do not use every theoretically reachable posture equally often. Standing, sitting, squatting and lying down are common. Many extreme joint positions are physically possible, but people rarely stay in them. Pile many states into a data cloud, and we often get several dense regions rather than a uniform mist.

This is one simple source of multiple modes: the same system has several places where it commonly settles. Falling is different. It may be a brief path from standing to lying down, rather than a mode where the system stays. A mode and a transition path must therefore be kept separate.

A mode is where the system often stays. A transition path is where it passes on its way between common states.

### 2.3 Outliers as bad measurements or rare but real paths

Suppose most people bend their knees when they get lower. Then we find someone whose body is low but whose knees have hardly bent. The simplest statistical description calls this an outlier. From the perspective of generating mechanisms, a better question is whether the measurement is wrong or whether the person followed another legitimate path, such as falling. That is the distinction between an error and another generating regime.

The first response in data-oriented modelling should not be “delete that point”. First ask why it could appear there. Is it a measurement error, or does it belong to another reachable mechanism?

## 3 Causal inference becomes a detective story about whether it is still you

In our conversations, we almost gave causality an extra “causal axis”, before bringing the explanation back to time. There is only the time axis here. What matters is that if a state moves from A to B, an allowed path must exist in this world. You cannot simply jump from city A to city B. If you really arrive in B three days later, either we have observed some intermediate states or an existing account at least tells us that the journey is possible.

A → admissible path over time → B

Reachability alone is not enough. We also need to establish that the person who arrived in B is still you. Think of a police investigation. Someone may be holding your identity card, but if the height, face, movements and other traces do not match, perhaps someone was substituted along the way. Conversely, a person can travel for three days, change clothes, get a haircut and look different in a photograph without becoming a different person. What we need is compatibility across several kinds of evidence.

We do not recognise a causal mechanism from one photograph. We recognise it from a trail of clues that continue to fit together.

This is why epidemiology can feel so much like detective work. Researchers have to rule out substitutions. Has a laboratory effect quietly taken the place of a disease effect? Has the measurement system changed? Is the age distribution impersonating the exposure? Has a common cause produced both A and B? We see the traces. “Mechanism” is the name we give them after enough of those traces fit together.

For this story, we can begin with three questions about establishing causality. First, is the path from A to B possible in time and in theory? Second, does the evidence along the way show that it is still the same system, with no substitution halfway through? Third, when the factor we claim matters changes, do the later traces change in the corresponding way?

*Reading note: These clues organise a causal investigation; they are not an identification rule by themselves. A causal claim still needs a defensible comparison or intervention and assumptions about confounding and measurement. See research record [2].*

## 4 Traditional statistics draws an ideal fan and looks at how reality departs from it

### 4.1 The lovely ideal of a person who can move only one joint

Return to ordinary statistics. Suppose a person really does stand like an ideal robot, perfectly upright, with every other body part fixed. Only one shoulder joint can rotate, and the arm has a fixed length. The region swept by the arm can be beautifully regular, like a fan. A statistician can start by proposing that this is the main generating mechanism.

Y = f(θ) + ε

Reality is never quite so tidy. The person trembles a little. The centre of joint rotation is not as perfectly fixed as a mathematical hinge. Soft tissue moves. The wrist, elbow and torso cannot remain absolutely still. The instrument adds measurement error. Our ideal thin fan acquires a fuzzy edge.

One lovely feature of traditional statistics is that it does not immediately declare every bit of fuzz a new law of nature. It first says: perhaps the main skeleton is still this fan, and the rest can go into the residuals. If the residuals are small jitters with no pattern, we can provisionally treat them as noise. If they show stable structure, the statistician asks whether we mistakenly held one of the joints fixed.

A typical statistical refinement goes like this: propose an ideal mechanism → inspect the residuals → find a patterned departure → release another joint we can explain.

### 4.2 Noise extra freedom and another mechanism spread data in different ways

An ideal path can become a fuzzy tube because of random disturbances or measurement error. A curve can spread into a surface because another independent degree of freedom has genuinely been released. A cloud can split into quite different regions because several generating regimes have been mixed together. All three can look like “the data spread out” on a plot, but they mean very different things.

Noise thickens; a new degree of freedom expands; a new mechanism branches.

This also helps explain the interpretability of traditional statistics. Ideally, whenever it adds another degree of freedom, it wants to tell you which joint it has just released.

## 5 Simple machine learning also learns how this particular person shakes

Now things get interesting. A flexible model concerned only with prediction error does not need to know what a shoulder joint is. It sees that the real trajectory has little jagged edges instead of being a smooth arc. If those edges are predictable, it has a reason to learn them too.

Person A shakes a lot when raising an arm. A model trained only on A may learn both the smooth overall structure and A's personal jagged pattern beautifully. Test it on A again, and its predictions are almost perfect. Move to person B, whose arm rises steadily, and the model still insists on predicting A's jagged movements. It fails because it has learned A too specifically.

Learning more detail does not necessarily mean learning more structure that transfers.

Traditional statistics often tries to separate the shared skeleton from individual departures: everyone shares an overall structure, and each person has their own variation around it. Simple machine learning in a single training environment may instead weld the patterns of this individual, this laboratory or this instrument into the main function.

That is why “Laboratory A and Laboratory B did the same experiment” does not guarantee that the model saw the same world. The variable names, procedures and tasks can all match. But if the laboratories have different jitters, instrument textures or recruited populations, a model can faithfully learn those details. It learns the actual training data, which need not be the shared structure that transfers.

## 6 Generative learning builds a denser web of conditional probabilities

### 6.1 More dimensions can mean more relationships to look at

Adding a dimension of observation does not always mean photographing another object. We can look from above, below, left and right. We can also look at the relationship between above and below, between left and right, or among above, below and left together. Relationships themselves can become observation coordinates.

Bring back the body. We can look at the shoulder, elbow, wrist and fingers separately. We can also look at shoulder–elbow combinations, elbow–wrist combinations, or the shoulder, elbow and wrist together. As we add comparisons of pairs, triples and higher-order combinations, the model's space of relationships becomes richer. These are additional representation coordinates or relational features. They do not mean that the world has acquired the same number of independent degrees of freedom.

### 6.2 Why calculating probabilities can begin to look like a mechanism

Suppose a model has seen many human postures. It need not contain an explicit statement that the shoulder is a ball-and-socket joint and the elbow a hinge. It can gradually acquire statistical facts such as these: in one shoulder state, certain elbow states are more common; given a shoulder–elbow combination, certain wrist states are more common; include the fingers, and the set of compatible combinations narrows further.

P(wrist | shoulder, elbow), P(finger | shoulder, elbow, wrist), …

When generating a posture, it can favour states that fit the current context at each step and end up with something that looks like a real human body overall. It does not first have to explicitly discover a “human-body generating mechanism”. It can learn a sufficiently dense network of local and higher-order compatibility relationships.

Local compatibility, followed by more local compatibility, can accumulate into global consistency. Rich enough probabilistic constraints can begin to behave like mechanism constraints.

This makes the criticism “it is only calculating probabilities” rather interesting. If visible behaviour in the real world is itself shaped by layers of physical constraints, biological constraints, individual habits, tasks and environments, perhaps a mechanism does not have to be one central engine. It may be a landscape of reachable possibilities shaped by many constraints.

## 7 A surprising reversal when mechanism is the name we arrive at afterwards

How do we know that an arm has a generating mechanism? Nobody handed the mechanism to us to look at. We first observed many things: certain joint changes often occurred together; certain postures almost never occurred; certain disturbances reliably changed later states. These relationships kept recurring across times, people and viewing angles. Only then did we compress that stable structure into a sentence: there is a mechanism here.

Observations → recurring constraints → stable regularities → “mechanism”

In this story, then, a generating mechanism is a concept reached after the evidence, in the sense of how we come to know something. The world certainly contains physical and biological processes. But “this is the same mechanism” and “this is a particular pathway” are researchers' ways of condensing and naming repeated evidence.

We never directly see the word “mechanism”. We see changes that recur, fit together and constrain what can happen next. Afterwards, we call them a mechanism.

### 7.1 People and models can share a pattern of learning without being the same kind of thing

People and language models are obviously different things. Human bodies, nervous systems, consciousness and social experience are not parameters, attention or other engineering components. Yet the way observations lead us to expect how the world will continue may share a striking pattern: observe → find recurring relationships → compress the constraints → form expectations about the future → revise them with new observations.

Scientists give stable structures names such as “inflammatory mechanism”, “feedback pathway” or “joint dynamics”. A model need not name them. At its current observation scale, it needs statistical constraints that make some futures more probable and others less probable. If it preserves which states are compatible, which are unreachable, which histories change the future and which disturbances change the next step, it has captured some of the observable structure that makes us describe reality as having mechanisms.

“It is only calculating probabilities” need not be a demotion. The deeper question is how science itself arrives at the concept of mechanism from stable probabilistic traces.

## 8 Why epidemiology suddenly fits this story so well

In ordinary prediction, we often worry about a model mistaking one person's small shake for a rule about everyone. Epidemiology often deliberately pursues just such small but recurring shifts. An exposure, disease or environmental factor may not turn someone into an entirely different person. It may slightly tilt the existing state cloud, change how a few variables move together, or produce a small but stable shift in a transition probability.

An engineer might say, “The burger stack hasn't fallen over. Don't worry about two millimetres to the left or right.” An epidemiologist might say, “Hang on. Why is every layer in the exposed group shifted a little to the left on average?”

Epidemiology often searches for deviations that are small, recurring and visible at the population level.

This is where generative models can help. They can retain the joint structure of a data cloud instead of squeezing everything into one label. They can try to learn how means, variances, covariances, multiple modes, trajectories and local relationships change together. A tiny trace that recurs across laboratories, populations and batches can accumulate. A trace that appears only in Laboratory A, and not in B or C, has a harder time becoming part of the shared mechanism in a well-designed shared-learning system. It is more likely to be assigned to an environment-specific or noise component.

Of course, “it occurs across laboratories” is evidence of stability, not automatic proof of the target mechanism. Epidemiology still has detective work to do. Who left the trace? Could a shared age distribution, the same instrument or similar recruitment have produced it? The generative model helps find stable small traces. Epidemiology still has to check identities, exclude stand-ins and work out attribution.

## 9 The Data Passport asks what world the model actually sees

The role of the Data Passport should now be clear. It is more than a table with a few extra descriptive statistics. Before learning starts, it gives the currently visible world an identity card. The real world passes through experiments, measurement, sampling and variable encoding before becoming the data D available to the model. The model does not meet the world directly. It meets D.

World → observation → sampling → encoding → D → model

The Data Passport therefore records more than geometry. Where did the data come from? How many generating individuals and environments are involved? How was it measured? What is its time structure? What is missing? What noise is present? Where did the labels come from? Are batches consistent? How far back might memory matter? All of this belongs to the world the model can see.

### 9.1 Data Geometry is the eyesight test inside the Passport

Data Geometry is an especially important part because it asks whether the lenses have distorted the model's world. Variable names cannot answer this. Are states that were close still close in the observation space? Has a continuous direction been bent? Have different states been squeezed together? Have some directions been exaggerated while others were flattened?

The Data Passport asks, “What world did you show the model?” Data Geometry asks, “Did a funhouse mirror or an astigmatic lens distort its view?”

This is also the foundation of the later work on corrective optics. A small geometric distortion can change neighbourhoods, comparisons, routing and states, eventually changing future responses. Tilt the lens, and judgments about similarity, distance and which local function to call can all tilt with it.

### 9.2 The Passport describes the statistical world the model can actually see

One more distinction matters. The Data Passport is not just an instruction card that we stand beside the model and hand to it. The model has no direct route around the statistical properties of its observations to some unmediated real world. What it faces is the statistical world produced by observation, sampling and encoding. Giving that data an identity card means measuring that visible world again and writing its properties down for humans to inspect.

“State” need not become a mysterious extra entity here either. For data, the Passport describes the state of the currently visible statistical world. For language, a state is the statistical picture presented by the same language at a particular observation scale. A model generates language sequentially, but it can use statistical structure formed at different scales, rather than only the linear sentence a human sees.

In other words: real world → observable data → statistical world. The Passport translates what the model actually sees into an identity card humans can examine. Engineering funhouse mirrors may distort that visible world further, but that is another layer of the story.

## 10 A real language assistant cannot simply be the most common human

If a generative model's ideal were simply to reproduce empirical probabilities faithfully, a language assistant would face a strange demand from the start. We do not want it to have the average competence of all humanity. If seven out of ten people solve an equation incorrectly, should the model get it wrong with probability 0.7? Obviously not. We want it to depart selectively from the empirical distribution: reliably choose a rare but correct answer, while suppressing frequent answers that are wrong or unhelpful.

This bias does not suddenly appear at deployment. Data selection, cleaning, task construction and preference training have already shaped the world the model sees. From the beginning, it faces an empirical world that has been selected, reweighted and bent towards engineering goals.

It learns as much as it can of the probabilistic world humans have left behind, then is asked to betray parts of that world when a task demands it.

## 11 Why this project calls language modelling motor control

By the definition used here, a language model generates what follows from what came before. Its particular difficulty is that each user brings a local world, and that local world never matches the training world exactly. From the context, the model must keep locating itself again: what are we discussing, which definitions apply here, which defaults should be suppressed, and where does the user want to go?

A conversation is therefore more than “given these conditions, generate one sample”. It is a continuing attempt to line things up. The model estimates where you are and takes a step. You say more, and the local target changes. The model finds its bearings again. It is chasing a target that the preceding conversation keeps specifying and revising.

Context → current statistical view → next response → new context → find your bearings again → …

Here, “state” refers to the statistical view of language at an observation scale, rather than an extra internal object we simply assume exists. A token, five to ten words, a larger chunk, a sentence and a whole stretch of context are progressively wider windows onto the same language. A “relation” can be thought of as a bigger word formed at a wider scale. Part of the model's complexity comes from the different statistical directions the same language presents through these windows.

*Reading note: The window is the observation scale; the statistical view through it is the state. Similar visible summaries can conceal different retained histories and different futures. The controlled examples in research record [3] make this distinction measurable.*

A particular code or cue can pull a sentence strongly at a local scale, while a wider scale gives it another interpretation. We see a linear text. The model can use the clouds of relationships formed by that same text at several scales. Language is generated in sequence, but its observable statistical structure need not have the shape of a sequence.

That is why this project describes language modelling as motor control. Whether robots also exercise control is not the point of this particular definition. Here it means repeatedly finding the current position from the context already formed, then generating the next step.

## 12 General data intelligence should not let the training majority overrule the data in front of it

Once we think of a language model as something that finds its bearings from what came before and then generates what comes next, general data intelligence fits naturally into the story. Suppose 90% of similar symptom patterns in the training set came from obesity. An ordinary predictor following frequent patterns could easily say, “This new data is probably obesity again.” But an ideal data intelligence cannot simply do that. Training history tells it what kinds of worlds are common. The data in front of it must help determine which local world it is in now.

Training prior P(M) → current data D → updated location P(M | D)

Suppose the current Data Passport shows degrees of freedom, coupling, time structure, distribution shape and response patterns that do not look like obesity. They look more like a mechanism that was rare in training. The system has to let that evidence outweigh the majority vote and locate itself again.

General data intelligence should first learn the different shapes a world can take, then use the current data to ask, “Which kind of world am I in now?” It should not merely retrieve the most common answer in training.

That is why the Data Passport is more than a peripheral tool. Its measurements provide coordinates for finding the current position. A natural-language model locates itself through the preceding context. Data intelligence locates itself through the identity of the data currently before it.

## 13 Training history can decide which familiar route comes first

Return to training history. Suppose a model first learns that legs can move a person close to a target, then learns that an arm can reach the remaining distance. The later training does not happen on an empty map. The leg route is already well built. When arm data arrives, the model can use the old road to remove most of the error and let the new ability handle what remains.

Reverse the order: arms first, legs afterwards. The model may make the arm's reach its default route, then mainly use the legs to cover what the arm cannot reach. Both models can eventually put a hand at the same target. Their internal probability landscapes can still be different.

What is learned first can shape what later becomes the default explanatory route, and which remaining errors the later ability is mainly used to repair. It changes more than the order in which knowledge arrives.

So a training set should not be understood only as an unordered collection. Identical contents in D₁, D₂ and D₃ do not guarantee that D₁ → D₂ → D₃ and D₃ → D₂ → D₁ will produce the same function. Early training grinds a lens. Later data is seen through that lens.

D₁ → geometry G₁ → D₂ seen through G₁ → geometry G₂ → …

## 14 A chain of thought is the surface path that was actually taken

We need to settle an easy misunderstanding. A chain of thought is not an exposed list of the model's internal function calls. Nor must the model first form a whole sentence in its head and then copy it out. What we are describing is a changing field of probabilities over future responses.

At a particular point in generation, imagine letting the model continue all the way to the end. It has a whole range of possible futures, each with a probability. Ordinary generation does not write all those futures out. It realises one small step. The next step is then conditioned on the original user input plus the prefix already written, giving a new distribution over what can follow.

F₀ → choose one local continuation → F₁ → choose one → F₂ → …

Think of each Fₜ as answering, “If I continued from here to the end, what might I write?” Each step changes the picture of the future.

### 14.1 A burger explains how a smooth change can look like a sudden reversal

Our most intuitive example is Papa's burger shop. The ideal burger stack has a centre line at x = 0. A person stacking it has that target in mind: if it leans left, correct to the right; if it leans right, correct to the left. But the training text is never one perfectly straight burger stack. Human texts already contain trajectories that lean left, correct right, lean left again and correct right again. A model may learn those swings as part of the normal probability structure of generation.

The model can also assign different probabilities to futures that go towards A and futures that go towards B. Imagine A's probability gradually falling from 0.80 to 0.60, 0.51 and 0.49, while B rises from 0.20 to 0.40, 0.49 and 0.51. The underlying change is smooth, but the current output can take only one direction. As B overtakes A, the visible wording might suddenly switch from “carry on” to “do not do it”.

A human sees a sudden change of mind. What happened in the probability picture was that another future gradually won the one output position available at that moment.

### 14.2 Why a whole reasoning sentence may never have existed as one fixed plan

This is the counterintuitive part. We end up reading a complete sentence such as, “Therefore we should continue ... although, on closer consideration, we should actually stop ...” It is natural to imagine that the model first had that entire thought and then wrote it down. Generation need not work that way.

At the first token, continuations may predominantly head towards A. After the second, B may appear in more of the possible futures. After the third, B may dominate. After the fourth, almost everything may head towards B. Grammar smoothly stitches together the local choices realised at these different moments, producing what looks to a human like one complete sentence.

Sentence = first(F₀) + first(F₁) + first(F₂) + …

The sentence certainly exists as language. Yet there need never have been a single moment when a stable plan for that whole sentence was held in place throughout generation. It can be assembled from local choices made under successively changing pictures of the future.

A chain-of-thought sentence can be one sentence linguistically without ever being one fixed functional state.

## 15 Why each reasoning point needs its own continuation

If we see only the tokens actually written in an ordinary chain of thought, we know only what the model realised at each step. We want to know where its possible futures pointed at that moment. So we take each prefix separately and let the model continue from there. This is a rollout: allowing a partial sequence to run forward so that we can examine its possible continuations.

Prefix x₁ … xₜ → unfold the future-response field Fₜ

A perfectly smooth short phrase such as “Next, let us consider this condition further” could sit above a future-response field that has already switched A → B → A → B, reversing three times. Reading the phrase alone gives us almost none of that information. “Next”, “further” and “consider” are not independent complete thoughts. The three reversals in future responses are what may connect to the training history.

The chain-of-thought text tells us which step the model actually took. Rollouts at each point tell us where its possible futures headed when it took that step.

Tokens matter for measurement because they provide the finest step of the generation process. But in interpretation, a token cannot simply be treated as one thought: language does not acquire its meaning one isolated character at a time. We want to compare F₁, F₂, F₃ and so on across successive prefixes, watching how future responses change as the available view of the language changes.

*Reading note: Conditional probabilities already assign probabilities to complete continuations. The story does not mean that the eventual sentence was impossible from the starting prefix; it means that no single fixed plan need remain preferred throughout generation. In experiments, we sample or enumerate a defined set of continuations, rather than observe every possible future. The burger probabilities are illustrative; sampling need not switch exactly at 0.5.*

## 16 Why a chain of thought looks like the shadow of training history

The Chapter 3 research does not simply claim that a chain of thought remembers training text. Training history first shapes the model's current functional landscape. Then a new question arrives. As the prefix grows, the same language presents different views at different scales, and the distribution of future responses keeps changing. On the surface, we see only the chain that was actually generated.

Training history → functional geometry → trajectory of future responses → visible chain of thought

The chain is therefore more like a shadow cast by training history. A shadow is not the original object, and a symptom is not the medical record itself. The task is to use the response trajectory we can measure now to work backwards towards how past experience shaped the machine.

This gives “machine learning epidemiology” one of its most vivid meanings. We receive a model that has already been formed. We do not have to imagine human thoughts inside its head. As in a case dissection, we examine states, disturbances, future responses and rollouts at successive points for lasting structural traces of the training history.

The chain of thought is not the medical record. It is a symptom that training history has left in present function.

### 16.1 High quality reasoning text might teach the model to keep reversing

Here is a rather funny hypothesis that deserves an experiment. When humans write “high-quality reasoning”, they often show the whole correction process: propose A, say “wait, that is wrong”, and switch to B. They may then check, reject and correct again. To a human reader, this looks careful, transparent and like a demonstration of thought.

The training model does not see what the person was really thinking. It sees a trajectory that actually occurs in the training set: A → reject A → B. If this pattern recurs, going some distance and then turning becomes a frequent conditional structure in its own right. Frequent reversals in later reasoning do not necessarily mean the model has acquired more layers of human reflection. Some may reflect a training history that made turning around part of a normal reasoning path.

Training text that looks like excellent human reasoning need not be the best functional training trajectory. One model can sound wonderfully reflective while its future responses swing repeatedly from side to side. Another can produce a chain that sounds abrupt, yet move smoothly out of region A, cross a transition zone and enter B just once. Its functional path may be cleaner.

The useful comparison is therefore broader than “with a chain of thought” versus “without one”. What kinds of reasoning paths do different training histories create? Going directly to the right answer, correcting once, correcting repeatedly and turning smoothly might leave different numbers of reversals, turning positions, swing sizes and speeds of finding the right location again. This remains a hypothesis to test, not an established result.

Humans may see “make a mistake, reflect, then correct it” as excellent reasoning. A model may learn “go some way, then reverse” as a high-probability path. An attractive chain of thought need not have better reasoning geometry.

### 16.2 A chain of thought gives the model more chances to find its bearings

A new question often does not land in the middle of a familiar training route. On first reading the user input, the model must make an initial judgment: is this more like A or B? If it has to answer immediately, that first location can become its final commitment. It looks like A, so off it goes towards A.

A chain of thought stretches the process out. The model follows A for a while, turning a vague candidate into a concrete path. As that path is written out, its mismatch with the user's original conditions can become apparent. This part does not fit. That constraint cannot be satisfied. The probabilities of future responses rearrange, and B or another route becomes more likely.

On this account, the chain helps a fixed model take several more steps through a probability landscape it has already learned. Every step conditions the next one again, giving it more evidence about where it currently is. The valuable part is the opportunity to find its bearings again, rather than how closely the visible text resembles human thought.

This also explains why an easy question may need no long chain at all: the first location was already accurate. Difficult questions, unfamiliar distributions and questions near the junction of several old routes may benefit more from travelling a little way so that a mistaken match can expose itself.

The value is not simply “think a few more sentences”. It is turning one initial placement into repeated checks: walk a little, then ask whether this route still fits the world the user described.

### 16.3 The practical question of length and when to stop

Following this explanation, one very simple thing deserves attention: the length of the chain. Give the model enough steps to find the right location, then stop promptly, rather than merely training it to imitate a style of “high-quality reasoning”.

Too short, and the first resemblance to A becomes the answer. The model has not travelled far enough to expose where the A route conflicts with the user's conditions. The failure is not necessarily a lack of deep thought. There was too little trajectory for a mistaken location to become visible.

Too long, and the opposite problem can appear. The generated text keeps entering the context and developing its own momentum. The user's original conditions remain, but as the self-generated prefix grows, the model may spend more effort explaining what it has just written than approaching the original target. A long chain can turn from a tool for finding the right position into a path that reinforces the wrong one.

The ideal length is therefore not a fixed 100 tokens, 500 tokens or one universal budget. It is more like a stopping moment: when future responses have reached a stable region compatible with the user's goal, and further continuation no longer helps the model find a better position, it should stop. An easy question may reach that point almost immediately. A difficult one may need longer.

One way to formalise this is to treat length as a control budget: minimise the number of generation steps needed to reach the stable target region, while penalising continuation that achieves nothing. The question becomes how long it takes to complete the positioning, rather than how complete the thinking looks on the page.

In this picture, the best chain is just long enough for the model to find the right place, then stops. Length is the budget for doing that.

*Reading note: A correct answer can occur in a narrow, unstable window, and a stable answer can be wrong. Stopping therefore needs a task-specific check of whether the answer is ready and correct. Which actions are taken matters as well as their number. See research records [3] and [7].*

If we keep only one everyday sentence from this part, let it be this: before asking whether a model can answer, ask what world it saw, which lenses it saw that world through, and where in that world it is starting from now.

## 17 How we fed the model became more interesting than choosing its architecture

At this point, we thought the second half would finally turn to architecture. What should we use for language, for population statistics, for genomic data? But the more we worked, the less it looked like choosing from a toolbox. Often a model learned a distorted picture because we arranged the data in one fixed way, showed it that arrangement ten thousand times, and then acted surprised when it treated the arrangement as part of the world.

Imagine a collection of population observations with no meaningful order. For convenient storage, we always put young people first, middle-aged people next and older people last. Or Laboratory A first, then B, then C. A human calls that formatting. The model does not know the word “formatting”. It sees one recurring fact: every time, A is followed by B, and B by C.

Now suppose we choose a model particularly inclined to pass information from one item to the next. What will it learn? That A is followed by B, and B by C, of course. We merely laid the data out along an axis so it could be read. The model took that axis to be the direction in which the world moves.

> “You show it to me this way every time. Of course I think this is how the world goes.”

### 17.1 The GRU may have taken your formatting a little too seriously

That is why, when we looked again at the GRU, or gated recurrent unit, it began to seem a little unfairly blamed. It is easy to say that a GRU is unsuitable for this kind of statistical data and cannot learn its real structure. A simpler possibility is that it readily uses the route from the previous item to the next, and our training really did hand it the same order again and again.

If we could show the same data forwards today, backwards tomorrow, randomly the day after, and then demonstrate every equivalent arrangement, a fixed order would stop being reliable. The model would have to find what remains unchanged across those arrangements. But real high-dimensional data does not make this cheap. We cannot demonstrate every possible way of laying it out equally often.

This leads to a practical engineering conclusion. It is not a claim that a GRU is theoretically unable to learn. If a model readily mistakes our presentation habits for reality, and we cannot afford to wash every presentation bias out of its experience, perhaps we should spare ourselves the struggle and choose a computation that is less easily fooled by this particular trick.

That is also why, when we choose some attention-based models, their appeal need not be magical language ability. Often it is simply that they do not force us to make “previous item to next item” the only route. We want observations to compare with one another without first inventing a false itinerary for their world.

### 17.2 What keeps being taught as real matters more than an architecture contest

The training set can no longer be imagined as a bag of samples. It is more like a history of growing up. The first data builds a road. Later data arrives beside a road that is already there. Whichever direction was reinforced first is more likely to become a shortcut later.

Expanding a training set therefore means more than increasing N. What really helps may be filling regions the model has never seen, filling the gaps between them, adding different environments and showing the same world through different legitimate views. What we want the model to learn should remain present through those changes. Presentation habits we do not want it to learn should vary.

The simplest training principle in this half of the story is this: let the real structure recur reliably. Do not keep tying an artificial presentation habit to the answer.

## 18 Mixtures of experts appear when two villages have no village in between

Then we meet another kind of troublesome data. Suppose people in Village A usually turn left when something happens, while people in Village B turn right in the same situation. The difficulty is not merely that the villages look different. Their local rules for this question really differ.

If the model is small and both villages must use the same patch of parameters, we can get a rather comic result. Today there are more samples from A, so the model is pulled towards “left”. Tomorrow there are more from B, and it is pulled towards “right”. It can be wonderfully right across A and systematically wrong across B. Change the sample ratio slightly, and the whole model tips the other way.

If there really are many natural states between A and B, half like one and half like the other, a larger model has a chance to lay a route through them. Language offers familiar examples. Real text contains many intermediate contexts that add a condition, gradually change direction or partly resemble two different situations. With enough capacity, a model can lay those connections out in fine detail.

Some statistical data does not have that kind of middle ground. Under condition A, the rule is A's. Under B, it is B's. There may be no real “halfway mechanism”. Force shared parameters to blend them into a smooth route, and the model may invent a compromise that does not exist in reality.

> “If there is no road, do not force the model to build an imaginary highway between two worlds.”

A mixture of experts, or MoE, now looks much less mysterious. The plainest solution is to work out whether we are in Village A or Village B, then let the people in the appropriate room do the job. Keep sharing what genuinely benefits from sharing. Where rules conflict and there is no legitimate intermediate state, do not make them fight over the same steering wheel.

We are not interested in MoE merely because the word “expert” sounds clever. Some data worlds demand conditioning: change the condition, and the local rule changes. Giving them separate rooms is one way to implement that fact.

*Reading note: The villages illustrate a modelling hypothesis, not a rule that separated data always requires MoE. A shared model with suitable conditioning and capacity can also keep local rules separate. Research record [4] tests sharing and partitioning under specified conditions, including continuously varying mechanisms.*

## 19 First find out whom you sampled then how they respond then what the disease changes

Population data pushes the problem another level deeper. Each population sample is not the same fixed brick. Today's sample may be slightly younger, tomorrow's slightly heavier, and the day after may include more people in the tail of an exposure distribution. The underlying population might not have changed at all. Sampling still makes the population base in front of us wobble a little.

The first layer is relatively easy to picture: what kinds of people tend to look like what? People of different ages, sexes, body types and lifestyles recur over long periods, allowing a model to build a population map. This base resembles the recurring statistical structures of language. See a region often enough, and you learn what it usually looks like.

The second layer is trickier. The same event can produce different responses on different population bases. Younger people respond one way and older people another. An exposure has a weak effect in one region and a stronger effect in another. The model therefore has to ask where it is standing in the population before it can explain what happened overall.

Only at the third layer do we reach the disease, exposure or target mechanism we really care about. Given how this group would respond anyway, how much further has the target factor tilted its world?

The ideal order is easy to describe: recognise the population base, examine the usual response on that base, then look for the extra shift left by disease.

> “First recognise the person. Then watch how they normally move. Only then ask how the illness has pushed them off course.”

### 19.1 Why the three levels should not all vote at once

If we throw all three into one big pool and let them compete for weight, the densely populated middle tends to win. But being common does not mean being the best place to expose the disease mechanism. The important change might lie in a tail, a subgroup or a very narrow response region.

This is another reason we keep returning to the Data Passport. We need to know how the sampled population is distributed, where it is dense or sparse, where variation is merely sampling fluctuation and where the response rule really changes. Otherwise, the model can mistake “there are more people here” for “this is the place to trust most”.

### 19.2 Why separating layers of mechanism can make training easier

Seen this way, experiments in which separating components of a mechanism improves training need not seem mysterious. Perhaps the model did not gain some magical new knowledge. Perhaps we finally turned three problems fighting over the steering wheel into questions it could address one after another.

First answer A: what kind of population base is this? Once A is established, answer B: how does this kind of population normally respond? Once B is established, answer C: what has the target disease changed on that background?

A → B → C.

The model no longer has to guess which ground it is standing on, how people normally move on that ground and where the disease pushes them, all at once. Arranging the computation in an appropriate order can remove a lot of the fighting.

*Reading note: Population → response → disease is a proposed way to organise this problem. Related controlled experiments motivate the explanation; they do not establish that this exact three-stage population system has already been validated. See research records [4] and [6].*

## 20 The later research questions grew out of the story by themselves

At first, we just wanted to know why two models could answer the same question correctly while producing completely different chains of thought. So we began taking those chains apart. As we did, we found that the sentence was not a transcript of the model's thoughts. The useful information was in where the possible futures leaned when we let the model continue from each point.

Following that trail led us to training history. Whichever road had been built first helped shape where later abilities grew. The question then arose naturally: if training order can shape language reasoning, it can also shape how a model later sees ordinary data.

The second half of Data-Oriented Modelling grew out of that question. We stopped rushing to invent a special architecture for every kind of data and began by examining how data is laid out, grouped and sampled; which examples appear first; which regions receive coverage; and which artificial orders are mistaken for reality.

Population statistics then reminded us that some data already has layers. First recognise the base, then the response, then the target mechanism. Mix those layers together, and the model has to infer the right order of conditioning from a muddle. Of course that can be harder.

That is how Modelling Hypothesized Mechanisms Underlying Data appeared as well. We needed a testable suggestion that perhaps the data should be conditioned in a particular order. Then we could ask experimentally whether training that way made the model more stable and less easily led astray by sampling or presentation. The point was to test a proposed organisation of the data, rather than simply tell an attractive mechanism story.

> “We started by taking a chain of thought apart. Along the way, training history, the geometry of training data and hypothesised mechanism modelling all grew out of it.”

## 21 Bringing the story together

Looking back, Data-Oriented Modelling can begin with a person raising an arm and continue all the way to training a general data model. We do not first need to memorise a list of neural-network names.

How a person can move determines the shapes their data can sweep out. Joints moving together give us degrees of freedom and correlations. Familiar resting postures become multiple modes. Change a viewing axis, and the shape changes again. Traditional statistics draws an ideal fan, then looks at where reality departs from it. Machine learning readily learns what keeps recurring in front of it. Generative models incorporate more and more joint probabilities into their statistical world, until they can generate things that look as though they came from a mechanism.

Then we find that “mechanism” is itself a name humans give after observing many stable phenomena. The Data Passport measures the statistical world actually available to the model and tells us what terrain lies before it.

Language models bring training history into the picture. Only one output step is realised at a time, while the possible futures change with the prefix. The visible chain of thought is the surface written by those successive changes. Let the model continue from each position, and we can begin to see the shadow of its training history.

The final turn is that this reasoning does not belong only to language. How a trainer arranges, orders, groups and repeats data is itself teaching the model what to treat as real. Data-oriented modelling begins by understanding the data world and designing a training experience that misleads as little as possible.

Architecture still matters. Some structures are easier to implement with particular computations, and some models are especially vulnerable to particular presentation biases. We choose an architecture because we understand where this data is most likely to be seen wrongly, rather than because the name sounds advanced.

## 22 The engineering funhouse mirrors we have not fully understood

The story now reaches the funhouse mirrors. So far, we have mainly asked what statistical world humans give the model and how training teaches that world to it. But after the model receives the picture, its own engineering structure continues to change it.

We have already seen some suspicious effects. Some directions are amplified and others flattened. Different things may be squeezed together. A small local word can suddenly pull the future off course. Routing and attention can give certain regions extra weight. We call these effects funhouse mirrors or astigmatic lenses.

But I cannot pretend to understand this whole part yet. I have not fully figured out the funhouse mirror myself, hahaha. We have caught hold of some of the lenses and even begun correction experiments. How they combine into a complete account of engineering distortion still needs to be taken apart experimentally, piece by piece.

So let us leave a little suspense here. Why does the same Data Passport become a different-looking world in different implementations? Which shapes belong to the data, and which were added by the model's lenses? The story can continue as those experiments make the picture clearer.

## 23 A story that grows with the research

This remains a living explanatory account. As new experiments clarify a part of the story, that part can grow with the evidence. The explanation stays together, rather than being scattered across separate technical supplements.

The formal papers distinguish measured findings, hypotheses still to be tested and metaphors that help us understand. This story has one task: explain how we arrived at these questions, step by step, so that someone who knows nothing about models can still follow along.

## Research records behind the story

[1] **Genomic Predictive Geometry and Model Capacity.** Chapter 4, Report 04. Effective dimensions and the Data Passport provide background for Sections 1 and 9. [Open research record](https://github.com/walkingrui-bot/Data-Oriented-Modelling-Reports/blob/main/Chapter_4_Data_Zoo/Genomic_Predictive_Geometry_and_Model_Capacity/REPORT_EN.md)

[2] **Learning Causal Structure from Data Geometry.** Chapter 5, Report 02. Causal structure, transfer and intervention studies provide background for Sections 3 and 8. [Open research record](https://github.com/walkingrui-bot/Data-Oriented-Modelling-Reports/blob/main/Chapter_5_Data_Oriented_Modelling/Learning_Causal_Structure_from_Data_Geometry/REPORT_EN.md)

[3] **Machine Learning Epidemiology and Case Dissection.** Chapter 3, Report 01. Training order, future-response states, chain-of-thought measurements and stopping provide background for Sections 11 and 13–16. [Open research record](https://github.com/walkingrui-bot/Data-Oriented-Modelling-Reports/blob/main/Chapter_3_Machine_Learning_Epidemiology/Research_Report/REPORT_EN.md)

[4] **Heterogeneous Data and General Data Intelligence.** Chapter 5, Report 01. Native data structures, capacity, routing and parameter sharing provide background for Sections 9 and 17–19. [Open research record](https://github.com/walkingrui-bot/Data-Oriented-Modelling-Reports/blob/main/Chapter_5_Data_Oriented_Modelling/Heterogeneous_Data_and_General_Data_Intelligence/REPORT_EN.md)

[5] **Language Models Motor Control and Deep Space Drift.** Chapter 2, Report 01. State, response and control comparisons provide background for Section 11. [Open research record](https://github.com/walkingrui-bot/Data-Oriented-Modelling-Reports/blob/main/Chapter_2_Language_Models_Motor_Control_and_Deep_Space_Drift/report_text/Dynamic_Generative_Rule_Fitting_Phase2_EN.md)

[6] **Modelling Hypothesized Mechanisms Underlying Data.** Chapter 5, Report 03. Tested hypotheses about geometry, coverage, calibration and valid operations provide background for Sections 12 and 19–22. [Open research record](https://github.com/walkingrui-bot/Data-Oriented-Modelling-Reports/blob/main/Chapter_5_Data_Oriented_Modelling/Modelling_Hypothesized_Mechanisms_Underlying_Data/REPORT_EN.md)

[7] **How Language Models Reach an Answer.** Chapter 3, Report 02, also listed under Chapter 2. Answer readiness, protection, recovery and action routing provide background for Sections 15–16 and 22. [Open research record](https://github.com/walkingrui-bot/Data-Oriented-Modelling-Reports/blob/main/Chapter_3_Machine_Learning_Epidemiology/How_Language_Models_Reach_an_Answer/REPORT_EN.md)

[Back to Chapter 0](README.md) · [All chapters](../README.md)
