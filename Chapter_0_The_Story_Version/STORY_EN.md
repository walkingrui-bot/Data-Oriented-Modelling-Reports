# Chapter 0 — The Story Version

**Don't feel like reading the reports? Getting lost in them? Start here.**

[Chapter 0](README.md) · [All chapters](../README.md) · [Download Word](Data_Oriented_Modelling_Living_Narrative_EN_v0.8_20260930.docx)

## Data-Oriented Modelling

*A Living Explanatory Narrative*

*From the shape of data to the world a model learns*

English version 0.8 · 30 September 2026

This is the story behind Data-Oriented Modelling. It keeps the intuitions, examples and arguments that help explain why we run these experiments, and grows alongside the research.

## How to read this story

Let us start with a story that almost anyone can follow, then see how far it takes us. Along the way, an ordinary moving body will lead us into statistics, machine learning, generative models, general data intelligence and chain-of-thought. A research paper might introduce some of these ideas with an equation. Here, we begin by asking what a model is doing when it observes, compares and tries to work out where it is.

The story begins with familiar statistics and follows the thread through training history, possible future responses and the changing course of a generated answer. The comparisons are there to make the structure visible. We can then connect each idea to an experiment, a mathematical definition or a question worth testing.

First make the world understandable. Then use the equations to pin down the structure we have understood.

### A few words we will use

- Time is the forward-running clock in this story. Causal relationships concern how changes affect what follows; we describe those relationships within the changing world.

- Degrees of freedom describe relatively independent ways a system can vary. We will distinguish them from the number of recorded variables, the dimension of a particular representation and the extent of the places the system can reach.

- A generating mechanism is our name for a pattern of constraints and changes supported by repeated, compatible evidence. Physical and biological processes act in the world; our descriptions of those processes develop as we investigate them.

- Motor control is the analogy we use for a language model repeatedly locating its current position in context and choosing how to continue. The language experiments give this analogy its specific meaning here.

- The language-model pattern we borrow is generation conditioned on a preceding context. Natural language is its most familiar example. General data intelligence can use related predictive ideas while keeping the native structures of other kinds of data.

- A Data Passport describes the data presented to a model. Data Geometry is one of its main eye tests: it measures shape, neighbourhoods, compression and mixing under a specified way of observing the data.

- Chain-of-thought is a visible generated path. Our experiments also examine how the distribution of possible future responses changes along that path.

- A state is the statistical or functional situation at a particular point, described at a chosen observation scale. Scale sets the window through which we look. In the predictive-state experiments, future-response probes tell us which situations behave differently, including situations with the same visible text or location.

- Architecture makes some structures easier to represent and learn. The training data, their order and grouping, the sampling scheme and the learning objective jointly shape what the trained model comes to treat as its world.

## 1 Why data form a cloud

Our first move was very simple: take the data out of the spreadsheet. A table is a convenient way for us to look at something much richer. Imagine a changing body, or a piece of moving matter. As time passes, its state changes. We choose an observation method, measure some parts of that state and arrange the readings into rows and columns. That is how we end up with the familiar table.

t → Z(t)

Time has a special role in this picture. You can sit perfectly still and the clock will keep going. We use it as the axis along which the state develops. The freedoms we want to count belong to the state itself: as the clock advances, how many relatively independent ways can it change?

### 1.1 A fingertip makes dimension easier to understand

Imagine watching just one fingertip. Its position lies in three-dimensional space, so we can give it three coordinates: x, y and z. Now fix the shoulder, elbow and wrist, and allow only one finger joint to rotate. The fingertip still lives in three-dimensional space, but it travels along an arc. One angle describes its movement.

Ambient dimension = 3; local movement dimension ≈ 1

Release a second independent joint and the tip may begin to sweep out a surface. Release the wrist, then the elbow and shoulder, and its reachable region can grow. Let the waist turn, the legs walk and the whole person jump, and the hand can reach much farther. Add stairs, a lift or a train and the person can travel farther still. The body's joints have stayed the same; the available actions and environment have changed where they can take it.

Degrees of freedom tell us how many independent choices of movement are available. Reachability tells us where those choices can take us.

An arm can have many internal joint freedoms while the task of placing its fingertip at a location has only three positional coordinates. A complicated internal system can therefore produce a simple-looking observation. Watching the fingertip alone may leave several explanations open: the shoulder moved, the elbow moved, the wrist moved, or the person took a step.

Internal configuration q → endpoint p = f(q)

That is our first, very ordinary example of the same observed output arising from different internal configurations.

### 1.2 Many simple parts can produce a complicated whole

Now replace the body with data. Suppose we have many simple components, each with only one or two ways of changing. Together they can supply many partially independent patterns of variation. Their connections coordinate some movements and constrain others. The useful question is how many joint patterns we need to describe the variation we actually observe.

This is a helpful way to think about the high effective dimensions in our genomic work. Picture a body with many joints, some moving together and some retaining considerable freedom. The report measures that variation in several ways and at several scales. A covariance-based dimension, a local geometric dimension and the number of directions useful for a prediction task each describe a different part of the picture. [1]

Many simple components can supply many directions of variation. Coupling shapes their joint movement and can tie some directions together. Nonlinear relationships can also spread the observed variation across several coordinate directions.

### 1.3 Stack the observations and a cloud appears

Record the state at successive times and we obtain a trajectory. Put the observations on the same plot and temporarily set aside their order, and we obtain a cloud. We can also make a cloud by observing many different people or systems. The Passport records which of these sampling stories produced the points.

Z(t₁), Z(t₂), …, Z(tₙ) → a cloud of observed states

Several intimidating geometric words now become quite approachable. Shape describes the region occupied by the observations. Boundaries describe the edges we can see. Density reflects where the system spends time, which people or states we sample, and how often we measure them. Anisotropy means that the cloud spreads farther in some directions than others. Curvature describes how its local orientation bends as we move through it. The body's possible movement helps us imagine these properties; measurements and sampling help determine the cloud we actually get.

Data Geometry measures those properties systematically. It gives us part of the description of the world presented to the model. The wider Data Passport also records how that presentation came about.

### 1.4 Statistical transformations change the map

We can look at the same observations through different coordinates. A relationship may look awkward along x, so a statistician tries log(x), adds x², or uses a spline basis. It is rather like bending the ruler and laying the observations out again.

Observed data x → coordinate map φ(x) → a new visible geometry

A polynomial term or basis expansion may appear to be just another column in the spreadsheet. It also changes the coordinates available to the model. Nearby observations can move farther apart, and a curved relationship can become easier to represent. The choice of map matters: keeping x alongside x² preserves the sign information, whereas replacing x entirely by x² folds positive and negative values together. A new map can reveal a relationship, stretch it or merge distinctions.

A statistical transformation gives the same observations a different arrangement. We choose the arrangement for the distinctions the task needs.

That is one reason traditional statistics often feels so well motivated. There is usually a reason for bending the ruler: a logarithm for a particular distributional relationship, a spline for local nonlinearity, a periodic term for seasonality, an interaction for a suspected change in an effect. Someone can explain why that new view might help.

In this sense, much of statistical modelling is representation design guided by human knowledge. We inspect the data, choose a view, examine the residuals and decide whether another view is needed. There can be several layers of this process, with a statistician making decisions between them.

Think of a person taking a photograph, interpreting it and deciding where to point the camera next. In a deep model, some of the decisions about the next view are themselves learned.

### 1.5 From a path to a surface to a cloud

Start with an idealized world in which the state has one freely varying coordinate, u. Under a smooth map, its observations trace a one-dimensional path, even if that path sits in a much larger space. The path can bend. What matters is that one free parameter moves us along it.

Z = g(u) → a one-dimensional path

Allow a second independent coordinate that produces a distinct observed change, and the path can open into a surface. A third can open it into a volume. Further independent changes make the possible states richer. Put samples from those states together and the cloud becomes thicker and more varied.

This is why counting columns is only a beginning. We want to know which changes those columns permit us to see, how the changes depend on one another, and what our observation has compressed or left out.

## 2 Correlations, modes and unusual observations

### 2.1 Two measurements moving together

Watch a person squat. Their knees usually bend more as their body moves down. Plot repeated observations and those measurements will vary together. A correlation can arise because two coordinates share part of the same movement.

Shared variation can leave a statistical correlation.

There are plenty of other ways for a person to become lower, though. They can sit, kneel, bend at the waist or fall. The ground can move too. Bent knees and reduced height can be strongly associated in one familiar movement while other routes lead to a similar endpoint.

A strong correlation tells us about shared variation. To explain the route that produced it, we need the rest of the evidence.

### 2.2 A system can have several favourite postures

People spend a lot of time standing, sitting, crouching or lying down. They spend very little time in many other physically possible postures. Stack enough observations and the cloud may contain several dense regions, rather than one evenly filled mist.

That gives us one intuitive source of multimodality: several commonly occupied regions. A fall has a different role in this picture. It may be a brief transition from standing to lying down. Where a system tends to stay and how it travels between those places answer different questions.

A mode is a commonly occupied region. A transition path connects regions through a sequence of states.

### 2.3 An unusual point may have a story of its own

Suppose most low body positions in our sample come with bent knees. Then we see someone very low down with their knees almost straight. A statistical rule might flag the observation as an outlier. The interesting question is what happened: did the instrument misread, or did the person arrive there by another route, perhaps a fall?

The first question in data-oriented modelling is therefore quite concrete: how did this point come to be here? Its answer helps us decide how to use the observation.

## 3 Causal inference and the question of identity

Imagine someone travelling from city A to city B. Time passes, and there has to be a physically possible route between the two locations. We may observe parts of the journey, or use other evidence to reconstruct how the journey could have happened. That gives us a starting point for thinking about causal investigation.

State A → a possible sequence of changes over time → state B

We also want to know whether the person arriving at B is the person who left A. A detective would compare several traces. An identity card is useful, but the face, height, movements and other evidence should fit together. Equally, a change of clothes or haircut during the journey is perfectly compatible with the same person arriving.

A mechanism becomes more convincing when its different traces fit together across the changes we observe.

This is why epidemiology can feel like detective work. We examine possible substitutions: an instrument change masquerading as a disease effect, a difference in age structure appearing as an exposure effect, or a shared cause producing both observations. Repeated evidence helps us build and name a candidate account of what happened.

To attribute the change to a particular factor, we also need a credible comparison: what happens when that factor changes, and what happens under the relevant alternative? Randomized interventions, suitable natural experiments and observational designs with explicit assumptions provide different ways to make that comparison. Timing, identity, measurement, selection and common causes all enter the case. The travel story helps organize the clues; the study design gives those clues their causal force. This is the distinction developed in our causal-geometry report. [2]

## 4 Traditional statistics and the tidy fan

### 4.1 Hold the body still and turn one joint

Imagine an ideal mechanical person standing perfectly still. Only one shoulder angle can change, and the arm has a fixed length. The arm sweeps out a tidy fan-shaped sector, while its tip follows the outer arc. We can begin with a mathematical description of that main movement.

Y = f(θ) + ε

A real person adds texture to the picture. There is a little shaking, a shifting joint centre, soft-tissue movement and small contributions from the wrist, elbow and trunk. The instrument adds measurement error. Our clean outline becomes fuzzy.

A useful statistical approach is to fit the main structure and inspect what remains. Small fluctuations may be handled by a noise model. Repeated, directional residual patterns invite another question: did we fix a joint that was actually moving, or miss some other systematic part of the process?

Start with an intelligible movement, examine its residuals, then add the part of the structure that the evidence calls for.

### 4.2 Three reasons a cloud can spread out

Random disturbance or measurement error can thicken a path into a fuzzy tube. Another independently varying input can open a curve into a surface. Several operating conditions can produce separate branches or clusters. All three can look like greater scatter, so the explanation depends on how the observations were generated and measured.

Noise can thicken a path. Another independent variation can open it out. A change of operating regime can create another branch.

The attractive ideal of an interpretable statistical model is that, when we add a new component, we can explain which part of the movement it represents.

## 5 A model can learn one person very thoroughly

Now give the observations to a flexible predictor. It sees a slightly jagged trajectory and can learn the jaggedness when it is predictable. It can do that without ever naming the shoulder joint.

Imagine that person A's arm movement has a characteristic tremble. A model trained only on A may learn both the broad movement and A's particular zigzags. It predicts another movement by A very well. Then person B raises an unusually steady arm, while the model keeps predicting A's zigzags. The model has learned one person's movement in considerable detail. The question is how much of that detail transfers to another person.

Some learned detail is shared structure. Some belongs to the particular person or setting in which it was observed.

A hierarchical statistical model might represent a common movement with person-specific departures around it. A predictor trained in a single setting can instead incorporate the person's, laboratory's or instrument's particularities into its main function. Flexible models can also be designed to separate those components; training data and objectives determine what evidence they have for doing so.

This explains why two laboratories running the same named experiment can still present different worlds to a model. Their variable names and protocols may match while instrument texture, recruitment or local conditions differ. A model can faithfully learn those differences. We then need to establish which parts belong to the structure we want to carry between laboratories.

## 6 How learned probabilities can produce mechanism-like behaviour

### 6.1 Looking at relationships creates more ways to observe

Another observation coordinate need not mean another physical object. We can look at the top, bottom, left and right of something. We can also examine how the top relates to the bottom, or how three parts fit together. A relationship can itself become a feature we measure.

Return to the body. We can record the shoulder, elbow, wrist and fingers separately, and also describe their combinations. Pairwise and higher-order comparisons enrich the representation. They give us more ways to describe the same body, while its underlying movement freedoms are determined by the body and its constraints.

### 6.2 Learning probabilities can capture the effect of constraints

Suppose a model has seen many human postures. It might learn that certain elbow positions commonly accompany a particular shoulder position, that some wrist positions fit a particular shoulder-and-elbow combination, and that adding the fingers narrows the compatible possibilities further. It can learn these relationships through the observations.

P(wrist | shoulder, elbow), P(finger | shoulder, elbow, wrist), …

When those conditional relationships fit together as a coherent joint model, generation can assemble a plausible whole posture. Each new choice respects the context already in place and the relevant constraints. Rich, coordinated probability relationships can therefore reproduce important aspects of a mechanism's observable behaviour.

The pieces have to fit together. Compatible local and higher-order relationships can then support a coherent whole.

This makes the phrase “it is only calculating probabilities” rather interesting. Physical constraints, biology, habits, tasks and environments all shape what can happen together. A learned distribution can capture some of that shape. A mechanism may involve many interacting constraints, and probability models give us one way to describe their combined observable effects.

## 7 How we come to call something a mechanism

How do we arrive at a mechanism for arm movement? We observe many things: joints changing together, postures that rarely occur, and disturbances that reliably alter what follows. We compare observations across people, times and viewpoints. Eventually we compress a substantial body of compatible evidence into a useful explanation.

Observations → recurring constraints → stable relationships → a mechanism description

That is the sense in which “mechanism” is a concept we form after observing. Physical and biological processes are already happening. Our statements that “this is the same mechanism” or “this is a particular pathway” are descriptions developed through investigation.

We see changes that recur, fit together and help predict or explain what follows. We give their organized account a name.

### 7.1 A resemblance in how knowledge is built

Human bodies, nervous systems and social experience give people a very different starting point from an engineered model. Yet there is an interesting resemblance in one pattern of learning: observe relationships, retain recurring structure, form expectations, and revise those expectations when new observations arrive.

A scientist may name the structure an inflammatory mechanism, a feedback pathway or joint dynamics. A model may encode useful parts of it in its response to context. We can examine what it has learned by asking which combinations it preserves, which histories it distinguishes and how its predictions change after specified perturbations. Those are concrete pieces of the structure that make a mechanism description useful.

The interesting question is what those learned probabilities preserve about the world, and how we can test it.

## 8 Why epidemiology feels at home here

Some of the small departures that complicate prediction are exactly what epidemiology wants to investigate. An exposure, a disease or an environmental condition may slightly shift a state distribution, change how a group of measurements varies together, or alter the probability of a particular transition.

Imagine building a stack of burgers. Someone checking whether the stack will fall might be happy to ignore a tiny sideways lean. An epidemiologist asks, “Why does the exposed group lean a little farther left at every layer?”

A small shift becomes interesting when it recurs in a population under a meaningful comparison.

A generative model gives us a way to study the joint pattern: means, variances, relationships, modes and trajectories can be learned together. A well-designed shared learning system can compare traces across laboratories and populations, accumulating evidence for common structure while representing environment-specific differences separately.

The detective work continues. A recurring trace might belong to the exposure of interest, a common age distribution, a shared instrument or a recruitment practice. Generative modelling can help locate the trace. Epidemiological design and causal analysis help determine whose trace it is. [2]

## 9 A Data Passport for the world presented to a model

The Passport now has a natural place in the story. Before learning begins, we describe how the model's data came into being. The physical world passes through an experiment or observation process, a sampling scheme and an encoding. The result is the data available to the model.

World → observation → sampling → encoding → data → model

The Passport therefore records more than geometric shape. Where did the data come from? How many distinct people or systems contributed? Which environments were observed? How were the measurements made? What are the time structure, missingness, noise, labels and batch differences? How much history may matter for the task? These properties help define the statistical world the model is being shown.

### 9.1 Geometry as an eye test

Geometry asks what our view has done to the relationships between states. Are meaningful neighbours still neighbours? Has a direction been compressed, stretched or bent? Have distinct situations been merged? We answer these questions relative to a specified representation, comparison or task. A second view or a controlled intervention can supply a useful reference.

The Passport asks what world we have presented. Geometry helps us examine how that world looks through the chosen lens.

This is the starting point for the Corrective Optics line of research. A geometric change can alter which observations count as neighbours, what gets compared or mixed, and which action or local function is selected. A small change in the lens can therefore matter farther down the chain.

### 9.2 Writing down the statistical world we have measured

The model receives observations through its actual input and encoding. The Passport is our measured description of that observable world: it makes properties of the data available for inspection and, where the system is designed that way, for conditioning the model or selecting an operation. The measurements and the data have connected roles.

For data, this description can include the distribution, dependence and history visible at a particular scale. For language, we can describe the current context through a token, a phrase, a sentence or a wider history. In our functional experiments, we also ask what future responses the trained model produces from that situation. Training history and retained computational information can make two apparently similar situations behave differently. [3]

The Passport translates properties of the model's observable world into a form people can inspect. The encoder and later computation then determine how that information is represented and used. Both stages belong in the investigation. [1, 4]

## 10 The assistant we actually want

Suppose a collection of worked examples contains a common mistake in seven out of ten solutions to a particular problem. Those frequencies describe that collection. When we ask an assistant to solve the problem, our target is a correct solution. We want it to learn enough of the relevant structure to select that solution reliably, even if the correct examples were rarer.

Data selection, cleaning, task construction and preference training already shape this objective. The model encounters a selected and weighted version of human records. Its learned behaviour reflects both the records and the way they were used.

We use the world recorded in data to teach a system, then define the responses we want it to produce for a task.

## 11 Language generation as a moving rendezvous

Each user brings a local situation. The useful definitions, assumptions and destination of this conversation may differ from the most familiar setting in training. A helpful model has to keep using the context to locate the task: what is being discussed, which conditions matter here, and where are we trying to go?

A conversation makes the movement particularly visible. The model responds, the user adds something, and the local target becomes clearer or changes. The model then has to locate the task again. It is rather like a continuing rendezvous with a destination specified and revised through the conversation.

Context → a current view of the task → response → updated context → locate the task again

We can observe this at several scales. One token, a short phrase, a larger passage and the whole context reveal different statistical relationships. A relation among words can itself be treated as a larger unit of comparison. The observation scale tells us which relationships we are examining; the state describes the particular situation and its possible responses within that examination.

A local cue may strongly influence a continuation and then acquire a different role in the wider context. We read a linear sequence of words. The model's computation can use relationships across that sequence and across several levels of representation. The language is generated in order, while its statistical relationships can have a much richer shape.

This is why we use motor control as a guiding analogy. A generated step changes the context for the next step, and the system continually adjusts its response within that changing context. Our language-control experiments examine specific versions of that process. [5]

## 12 General data intelligence has to locate the current case

The same idea gives us a way into general data intelligence. Imagine a training collection in which most examples with a particular broad pattern come from one condition. That history provides a prior expectation. The measurements in the current dataset then provide evidence about which condition best explains this case.

Training prior P(M) → current data D → updated P(M | D)

Suppose the current data's variation, dependence, time structure and measured responses fit a rarer condition much better. Strong enough evidence can move the prediction towards that condition. How far it should move depends on the evidence, its reliability and the prior. That is the relocalization we want a data-intelligence system to perform.

Learn what kinds of worlds are possible, then use the current observations to work out which world best fits the case at hand.

In this design, Passport measurements provide useful coordinates for locating the case. When the output is an occurrence probability, the relevant population frequencies also belong in its calibration. Learning a structural response and estimating how often it occurs are related tasks with different targets. [6]

## 13 Training history leaves familiar routes

Imagine learning first that your legs can carry you close to a target, then learning that your arm can reach the remaining distance. The arm is being learned in a world where the leg route is already familiar. New learning can use that route and concentrate on what remains.

Reverse the order and a different habit may develop. Reaching with the arm becomes the familiar starting point, while the legs learn to make up the shortfall. Both routes can put the fingertip in the same place. Their organization can still differ.

What is learned early can shape the route that later learning finds easiest to use.

Our training-history experiments give this story a concrete counterpart. Reordering the same training records can change the learned parameters and later response trajectories. In those comparisons, the training set is more than a bag of examples: the sequence of updates is part of how the model takes shape. [3]

First training experience → a changed model → later experience processed through that model → further change

## 14 How a sentence takes shape

A useful way to study a generated chain is to ask what the model could produce next from each prefix. Its conditional behaviour defines a distribution over possible continuations. We use future-response measurements to map selected parts of that distribution and how they change along the chain.

At any prefix, we can continue generation and observe a possible future. Repeating that process, or using a defined set of probes, shows how responses are distributed. Ordinary generation realizes one next step. That step becomes part of the context from which the next conditional distribution is defined.

Current possible continuations → one realized step → updated possible continuations → another step

Think of a future-response map as an answer to “If we continued from here, what kinds of outcomes would we get?” We redraw the measured map as the prefix changes.

### 14.1 A burger can lean smoothly before the visible choice flips

Picture a burger-stacking game. The target centre line is straight. Lean too far left and you move the next layer right; lean right and you correct left. Human accounts of reasoning often contain just such movements: a proposal, an objection, a correction and another adjustment. One hypothesis is that repeated exposure to these patterns can make turning back part of a model's learned continuation habits.

Now imagine a readout with two choices, A and B. As the state changes, the probability of A moves through 0.80, 0.60, 0.51 and 0.49, while B moves through 0.20, 0.40, 0.49 and 0.51. The values are an illustration. A decoder that selects the higher-probability choice switches abruptly at the crossing, even though the underlying scores changed gradually. A sampling decoder expresses those changing probabilities through the frequencies of its choices.

A sudden change in the visible choice can be the surface effect of a gradual change in the competing response scores.

### 14.2 One sentence can emerge from a changing series of choices

Read a sentence such as “We should continue ... although, after checking that condition, stopping would be better.” It is easy to imagine that the whole sentence was prepared in advance and then copied out. Autoregressive generation also gives us another, very concrete account of how it can take shape.

After the first token, the favoured continuations may mostly lead towards A. After another token, continuations towards B become more likely. A later prefix may strongly favour B. Grammar can join those successive choices into one fluent sentence, although the preferred continuation changes along the way.

Each chosen token joins the prefix that conditions the next choice. Their realized sequence is the sentence we read.

The model's initial conditional probabilities already define probabilities for complete continuations through their successive token probabilities. The sentence that eventually appears is one such possible path. What can change repeatedly is the preferred continuation conditional on the prefix reached so far. The useful story is therefore about a sentence assembled through changing conditional choices, rather than a sentence held throughout as one fixed plan.

A sentence can be a single linguistic unit while taking shape across a succession of different functional states.

## 15 Why we examine every prefix

The final text records the choices that were realized. To understand the alternatives around those choices, we pause at successive prefixes and run the declared response probes or continuation samples. This lets us compare how the measured future changes from one point to the next.

Prefix x₁ … xₜ → specified future probes or rollout samples → a measured response map

Imagine an apparently uneventful phrase such as “Let us consider this condition more carefully.” Across its prefixes, a response probe could favour A, then B, then A again. The ordinary wording may reveal little of that change. We record reversals, their locations and their sizes, then compare them across controlled training histories.

The text records the step taken. Prefix-by-prefix probing measures the alternatives visible from the points along that path.

Tokens give us convenient checkpoints in an autoregressive sequence. Meaning can span several of them, and the computation inside a token step can itself have many layers. We specify the probe set, horizon and observation scale so that the response maps being compared answer the same question. In our finite reasoning worlds, a bounded set of continuations can be enumerated; in larger models, declared probes and sampled continuations provide the measured view. [3, 7]

## 16 Chain-of-thought as a shadow of training history

Training changes a model's function. A new question then sets a trajectory through that function as the prefix grows. The visible chain records one realized path. Our third chapter studies how controlled changes in training history alter the responses along such paths, including cases with matching final answers.

Training history → learned function → future-response trajectory → visible generated chain

This makes the shadow a useful image. The response trajectory carries traces of how the model was shaped. By comparing known histories and applying interventions, we can identify which features of those histories leave which measurable traces. Different histories can also share a trace, so the experimental comparison is part of interpreting it.

That is one reason the name Machine Learning Epidemiology felt so natural. We inspect an already trained system, measure its responses and perturb selected parts of it. The aim is to connect present functional behaviour with the history that produced it.

The generated chain is a present observation through which we investigate the model's training history.

### 16.1 What correction-heavy examples might teach

Here is a hypothesis I find rather funny, and worth testing. People often write “good reasoning” by showing all their corrections: propose A, say “wait, that is wrong,” change to B, check again and perhaps revise once more. To a reader, it can look careful and transparent.

The training record also contains a sequence of actual textual moves. Repeated examples of A, an objection to A and a turn towards B make that pattern part of the learning material. They could influence how often a model changes direction during its own generation.

We can therefore compare the style of an explanation with its functional trajectory. One chain might sound reflective while its measured responses oscillate. Another might sound abrupt while making one useful transition. Which behaviour helps depends on the task and on whether the turns improve the answer.

The testable question is how different kinds of training paths affect later response geometry. Direct solutions, one correction, repeated corrections and gradual transitions give us candidate training conditions. Reversal counts, turning points, oscillation size and time to a verified answer provide possible outcomes. This passage is a hypothesis about training design.

A polished account of correction and a useful course of computation are both worth examining. The experiments tell us how they relate.

### 16.2 Continued reasoning can create opportunities to relocate

A new question may lie between several familiar routes. The first response can favour one of them before all relevant consequences have been worked through. Requiring an immediate answer makes that early position especially important.

Generating intermediate steps can expose consequences of a candidate route. A proposed step may clash with a condition in the question; a calculation may reveal a mismatch. That can reorganize the next response. A tool call or other fresh observation can bring additional information into the process as well.

This is the relocalization interpretation: continued computation gives the model opportunities to change its functional situation using the original conditions, consequences it has derived and observations it has obtained. A generated assertion gains evidential value through its relation to those checks. The usefulness of each step is something we can measure.

For an easy case, a reliable answer may already be available at the start. For another case, useful intermediate operations may lead to one later. The required path depends on the question, what the model has learned and which operations are available. That is why our experiments compare action types and resulting states as well as the number of steps.

Take a step, check where it has brought you, and use that information to choose the next move.

### 16.3 Choosing the steps and knowing when to stop

This brings us to a very practical control problem: what sequence of useful operations reaches an acceptable answer, and when should we stop? Length is one part of the budget. The identity and order of the operations determine where that budget takes us.

Stopping too early can commit to a route before a relevant condition has been worked through. A well-chosen continuation may move the model into a state from which the answer can be read reliably.

Continuing also changes the state. Self-generated context can reinforce a route, and even a meaningful additional operation can move the immediate answer from correct to incorrect. Our controlled experiments measure such exits directly. Their occurrence depends on the state and action, not simply on reaching a universally excessive number of tokens.

The stopping target is task-specific: a verified acceptable answer, or valid completion of the current work. In a question-answering task, a correct answer can be worth returning as soon as the completion rule is satisfied, even if further generation would move away from it. When work must continue, safe continuation and recovery become separate control decisions.

We can express the aim as reaching acceptable completion at an appropriate cost. The cost includes generated steps and, where relevant, probes, verification and tool use. Accuracy and verified task progress determine whether a shorter route is useful.

The practical aim is a useful path to a verified result, with stopping at the right moment. Our experiments treat the answer-ready state and the choice of action as the objects of control. [3, 7]

## 17 How training teaches a model what its world is

At this point, it is tempting to ask which architecture should be assigned to each kind of data. Our experiments lead to a richer question. Several architectures may represent a useful set of relationships when capacity and training are suitable. How, then, are we repeatedly presenting those relationships during learning?

Consider the same dataset under different orders, groups, sampling rates and task mixtures. Some relationships will appear again and again; others may be rare or disappear between batches. A convenient presentation habit can become one of the most reliable patterns the model encounters. Learning it may reduce the training loss very effectively.

Architecture helps determine which structures are easy to learn. The data, objective and course of training shape which of them the model actually learns.

### 17.1 Representation, learning bias and training experience

Three questions help organize the discussion. What functions can the architecture represent? Which relationships does it make easy to express and optimize? And what pattern of examples and updates does training actually provide? These questions concern representational capacity, learning bias and training history respectively. Keeping them separate makes an observed success or failure easier to explain.

The history matters because a model experiences updates in a sequence. Earlier changes affect the model through which later observations are processed. Two procedures can use the same observations and still differ in their order, repetition, grouping and optimization path. Training is a process of shaping a function.

### 17.2 When presentation order becomes a learned relationship

A gated recurrent unit, or GRU, provides a clear example. It updates a carried state as inputs arrive. That is useful when order contains information. If records are always displayed in an arbitrary A–B–C order, however, the model also receives repeated evidence that this order is reliable. A training procedure has to establish which order relationships belong to the task.

Repeated presentation can make “after A comes B, then C” an easy route to lower loss. A storage convention may then become part of the learned transition pattern. We were arranging the material for convenience; the model was learning the arrangement it repeatedly saw.

One way to investigate this is to vary presentations that are genuinely equivalent for the task while preserving the relationships we want to learn. Recurrence is then evaluated on whether it retains the meaningful structure across those views. Appropriate encodings, explicit labels and symmetry-aware designs provide other ways to express the intended invariance. The cost and coverage required by each approach are experimental questions.

That gives us a practical criterion for selecting an architecture and training scheme together: how much data and computation are needed to learn the useful relationships while remaining stable under irrelevant presentation changes? The answer is specific to the task and the available observations.

### 17.3 Experts make conditional allocation explicit

A mixture-of-experts system, or MoE, routes work among modules. It provides an explicit way to allocate different computations to different situations. A sufficiently capable dense model can also learn different responses in different input regions. The useful comparison concerns the resulting functions, the routing information and the resources each design uses.

Training matters in either case. A router supplied with indistinguishable inputs and experts trained on nearly identical distributions may develop very similar functions. A dense model with informative conditions may develop useful specialization within its shared network. Our routing interventions establish that learned expert allocation can affect prediction, while the useful partition can differ substantially from the labels assigned by the simulator. [4]

The architecture provides ways to share or allocate computation. Training determines how those possibilities are used.

### 17.4 Keep meaningful structure stable and vary incidental presentation

Suppose a relationship is part of the structure we want to preserve. We would like it to remain available across batches, task slices and equivalent presentations. Suppose another feature is merely an accident of storage or display. Varying it can help expose which useful relationships persist.

The word “equivalent” matters. A person's recorded temporal order, a graph's connectivity and the identity of a repeated measurement can carry precisely the information the task needs. We can change the order in which independent people are presented while keeping each person's longitudinal history intact. The Passport helps us specify which changes preserve the object of interest.

Increasing a training collection is valuable when it improves coverage of relevant states, environments, transitions and conditions. Additional examples near a difficult boundary can teach something that repeated endpoints do not. For a genuine continuous transition, intermediate observations help describe the route. For a discrete switch, examples should make the switching condition and the valid responses clear. Coverage follows the structure of the task.

### 17.5 Architecture remains part of the explanation

An architecture can make the desired invariance or relationship easier to represent. That can change the amount of data and computation needed to learn it. A design that already respects an irrelevant ordering symmetry may need less training to achieve the corresponding stability.

We therefore examine more than accuracy under one fixed presentation. What happens when an irrelevant order, batch composition, study mixture or task adjacency changes? Does the model retain the relationships and future responses that matter? These comparisons help reveal which parts of the learned behaviour depend on the presentation chosen by the researcher.

### 17.6 Designing the learning setting from the data

The practical sequence is now fairly clear. Describe the observable data with a Passport. Specify the target structure and the presentation choices. Design the ordering, sampling, grouping, task mixture and sharing used in training. Then choose and revise the architecture in light of what it must preserve and compute efficiently.

Passport → target structure and presentation choices → training design → architectural support → robustness checks

Our starting question is what learning experience will help the model retain the structure we care about.

### 17.7 When conditional rules compete for shared parameters

Capacity gives us one possible explanation for conflict between tasks. Conditional structure gives us another. Under condition A, a particular response may be useful; under condition B, another response may be required. The model needs enough representational and computational capacity, informative condition cues and training that makes their relevance learnable.

Sometimes the conditions vary continuously. Observations between them can describe a useful transition. Sometimes the task changes through a discrete switch. Both situations can be represented by a conditional model. A valid response at A and a valid response at B can coexist in the same model when the inputs distinguish which response is called for.

Population context, disease state, experimental setting or a change in a generating rule may alter a local response function. We should preserve the condition under which that function applies. A discrete output requirement can call for a definite choice even when the model's representations vary smoothly. The requirement on the output and the organization of the internal representation are separate things to measure.

Shared training can still create interference. An update that improves one region can worsen predictions in another. Limited capacity, the way features are shared, the loss, the sampling balance and the optimization path can all contribute. Our experiments measure this directly by making an update in one region and evaluating its effect in others. That turns the image of two rules “pulling against each other” into an observable training comparison. [4]

A larger dense model can sometimes allocate useful distinctions more effectively. Informative conditions tell it which local response is needed. If the observable input leaves two conditions indistinguishable, prediction has to represent the remaining uncertainty or obtain another informative observation. Making the condition measurable changes that problem more directly than simply adding parameters.

This is where explicit conditional modules can help. The decisive question is which regions benefit from shared learning and which interfere. In our continuous-world experiments, soft sharing can work well across a broad transition, while sharper changes can favour a harder partition under the tested capacity settings. Local transfer measurements help explain that difference. Both continuous and discrete settings can therefore give useful reasons to evaluate modularity. [4]

For population modelling, a candidate design is to infer the relevant context, retain uncertainty about that context, and condition the response on it. Features that transfer usefully across conditions can be shared. More local components can represent condition-specific responses. The partition and the balance of sharing are then selected through appropriate held-out and intervention comparisons.

We decide what to share by examining the predictive task and the effects of shared training. Differences in file format, visible gaps and familiar labels are clues to investigate; training compatibility tells us more directly what a proposed partition achieves.

## 18 How the later research questions grow from the story

Two connected directions now emerge. Training-history experiments show that changing the course of learning can alter later response trajectories. That gives us a way to investigate how training presents different data structures. Population modelling supplies another design question: how should we represent background context, responses conditional on that context and the particular exposure or disease relationship of interest? Together these questions motivate testable hypotheses about how to organize learning.

### 18.1 Following the traces of training through a generated answer

Prefix-by-prefix examination gives us measurements to compare across known training histories. Two models can produce the same final answer, and equally fluent chains, while their intermediate response probabilities follow different routes. In the controlled studies, training interventions and state interventions connect those differences to particular computational changes.

This suggests an experimental strategy for other data structures as well. Vary how relevant examples are ordered, grouped or covered, then measure how the trained response changes. The language experiments establish specific instances of this relationship; the wider programme applies the same style of comparison to new modelling problems.

### 18.2 Training design is part of modelling the data

The Passport describes the statistical world presented to the model. The next question is how learning repeatedly exposes the model to that world: which relationships remain available, which cases dominate, and which conditions distinguish one response from another?

Consider a dataset whose order across independent records is arbitrary. Repeatedly presenting it in one arrangement can make that arrangement predictive during training. Comparing equivalent arrangements can help test whether the model has retained the intended structure. Within a time series or another order-sensitive object, the meaningful order remains part of what we preserve.

Training specifies which patterns recur, which observations become neighbours in computation, and which regions receive enough examples to support learning. It therefore participates in the modelling assumptions. We can inspect and test those assumptions just as we inspect the choice of variables or loss.

### 18.3 A candidate hierarchy for population modelling

Population statistics makes the question especially tangible. A target response may depend on background population characteristics, a physiological or behavioural state, and an exposure or disease process. A common group can dominate a pooled objective simply through its frequency. We want a design that represents the relevant conditions and still measures the target effect or response accurately.

One candidate is to organize learning around background context, then conditional response, then the target departure of interest. This changes the statistical factorization, the information available at each step and the way errors propagate. Uncertainty in an earlier layer should travel forward. Joint models and other factorizations provide meaningful comparisons. The benefit of this proposed hierarchy is something to assess through calibration, transfer and the target outcome.

### 18.4 Modelling hypothesized mechanisms underlying data

This is the motivation for Modelling Hypothesized Mechanisms Underlying Data. We use observations and scientific knowledge to propose an account of how data, relations and valid responses are organized. That account then suggests a concrete modelling operation which can be tested.

The published report already tests this principle through local-scale relations, coverage-aware learning and operators that respect valid graph states. The population hierarchy just described is a further design proposal along the same line. Its value would be assessed by the stability and accuracy it achieves across the relevant samples, studies and observation changes. [6]

A hypothesized mechanism earns its place as a modelling coordinate through those comparisons. It gives us a reason to choose an operation and an observable consequence by which to judge the choice.

### 18.5 The questions meet in one research programme

We begin by describing the observable statistical world. Controlled training-history studies show how learning can leave measurable traces in current responses. We then investigate how presentation, sampling, grouping and coverage shape those responses in other data settings. Hypothesized mechanisms provide further candidate ways to organize and test that learning. Each connection supplies the next experimental question.

The common thread is simple enough to ask out loud: what has the model learned to treat as its world? Data Passports, training history, chain-of-thought measurements and mechanism-guided modelling all give us different ways to pursue the answer.

## 19 Bringing the story together

We have reached the main explanatory thread of Data-Oriented Modelling by starting with a moving person. From that simple picture, the research questions follow one another.

1. The clock advances while a system changes through its available degrees of freedom.

2. Constraints and interactions shape the possible changes. Observation and sampling turn some of them into a cloud of recorded states.

3. The cloud's shape, density, modes and correlations carry traces of both the changing system and the way it was observed.

4. An interpretable statistical model offers an explicit account of the main structure, then uses residual patterns to guide refinement.

5. A flexible learner can capture fine detail. Comparisons across people and settings help identify which details transfer.

6. A coherent generative model combines conditional relationships into a joint account of possible observations and responses.

7. Repeated, compatible and attributable evidence allows us to develop useful descriptions of mechanisms.

8. The Data Passport records the data's relevant properties and provenance. Geometry measures the relationships visible through a specified representation.

9. General data intelligence should use the current observations to locate the case, combining learned experience with evidence and appropriate calibration.

10. Training history can alter the function we end up with and the response paths it makes available.

11. Architecture, objective and training design work together. Ordering, grouping, sampling, sharing and coverage all deserve examination.

12. The generated chain records a realized path. Defined future-response probes measure how the alternatives change along it.

13. Useful inference control chooses operations, checks the result and stops when the task's completion criterion is satisfied at an appropriate cost.

What world did we show the model? Through which lens did it see that world? Where is it now, and what would help it reach the result we want?

## 20 The funhouse mirrors inside the engineering

The story now reaches another layer. Once observations enter a model, tokenization, attention weights, residual updates, routing and optimization help determine what happens to their relationships. These are the lenses we have been calling funhouse mirrors or corrective optics.

The experiments already give us several things to point at. Measured corrections to repetition, local geometry and relation eligibility improve particular predictive comparisons. Recorded agent studies separate the availability of a candidate action from its suitability at the current task phase. The Corrective Optics record also brings process status, output content, repository changes and tests together when examining executed commands. Perception and action each have their own measurable parts. [6–8]

The larger engineering picture is still developing, which is part of the fun. My view of the mirror gets clearer one experiment at a time. Which directions are amplified? Which neighbourhoods change? Which connections deserve to influence the next response, and which actions have become appropriate after the world changes? Those questions keep this chapter growing.

## 21 Keeping the narrative alive

This is a living explanatory record. As an experiment changes our understanding, the relevant part of the story changes with it. The examples, results and explanations remain together so that a reader can follow how the account develops.

The continuing themes are the Passport's measurements, the native structure of different data, the design of training experience, conditional sharing, and the measurement and control of future responses. The engineering lenses connect those themes to the operations performed by an actual model.

Throughout the narrative, experiments provide measured examples, design proposals describe operations to evaluate, and analogies make the questions easier to see. The research records below give the definitions and evidence behind the corresponding passages.

## Version history

Version 0.8 · 30 September 2026. English edition, with the story aligned to the current reports on predictive states, training compatibility, causal attribution, conditional modelling and inference control. The body retains the original narrative sequence and central examples.

Versions 0.6 and 0.7 · 29 September 2026. Extended the explanatory record across the whole research programme, introduced the engineering-optics chapter, and developed the discussion of conditional responses, capacity and parameter sharing.

Version 0.5 · 29 September 2026. Connected the training-history investigations with training design for different data structures and with the motivation for modelling hypothesized mechanisms.

Versions 0.1 to 0.4 · 29 September 2026. Established the body, burger, lens and detective examples; developed the discussion of chain-of-thought, relocalization and stopping; expanded the Passport and observation-scale explanation; and connected presentation, training history and architecture.

## Research records behind the story

[1] Genomic Predictive Geometry and Model Capacity. Chapter 4, Report 04, English edition 1.0. The effective-dimension comparisons, task-conditioned predictive dimensions and Data Passport experiments inform Sections 1 and 9. [Open research record](https://github.com/walkingrui-bot/Data-Oriented-Modelling-Reports/blob/e49d085ff9112a8c02ef3ac1a6ff3914bf74dc32/Chapter_4_Data_Zoo/Genomic_Predictive_Geometry_and_Model_Capacity/REPORT_EN.md)

[2] Learning Causal Structure from Data Geometry. Chapter 5, Report 02, English edition 1.0. Experiments CG-001–006 and the later transfer and intervention studies inform Sections 3 and 8. [Open research record](https://github.com/walkingrui-bot/Data-Oriented-Modelling-Reports/blob/e49d085ff9112a8c02ef3ac1a6ff3914bf74dc32/Chapter_5_Data_Oriented_Modelling/Learning_Causal_Structure_from_Data_Geometry/REPORT_EN.md)

[3] Machine Learning Epidemiology and Case Dissection. Chapter 3, Report 01, version 1.9. The training-order interventions, CHAIN-SEMANTICS-007, REASONING-STATE-020, the CoT budget studies and STOPPING-GEOMETRY-029 inform Sections 9 and 13–18. [Open research record](https://github.com/walkingrui-bot/Data-Oriented-Modelling-Reports/blob/e49d085ff9112a8c02ef3ac1a6ff3914bf74dc32/Chapter_3_Machine_Learning_Epidemiology/Research_Report/REPORT_EN.md)

[4] Heterogeneous Data and General Data Intelligence. Chapter 5, Report 01, English edition 1.0. WORLD-MOE-002, WORLD-DATA-MICROSTRUCTURE-004 and DATA-FUSION-PARTITION-006 provide the main comparisons behind Sections 9 and 17. [Open research record](https://github.com/walkingrui-bot/Data-Oriented-Modelling-Reports/blob/e49d085ff9112a8c02ef3ac1a6ff3914bf74dc32/Chapter_5_Data_Oriented_Modelling/Heterogeneous_Data_and_General_Data_Intelligence/REPORT_EN.md)

[5] Language Models Motor Control and Deep-Space Drift. Chapter 2, Report 01. The state, response and control comparisons supply the connection used in Section 11. [Open research record](https://github.com/walkingrui-bot/Data-Oriented-Modelling-Reports/blob/e49d085ff9112a8c02ef3ac1a6ff3914bf74dc32/Chapter_2_Language_Models_Motor_Control_and_Deep_Space_Drift/report_text/Dynamic_Generative_Rule_Fitting_Phase2_EN.md)

[6] Modelling Hypothesized Mechanisms Underlying Data. Chapter 5, Report 03, English edition 1.0. Coverage, prevalence calibration, local-scale relations and valid state operators inform Sections 12, 18 and 20. [Open research record](https://github.com/walkingrui-bot/Data-Oriented-Modelling-Reports/blob/e49d085ff9112a8c02ef3ac1a6ff3914bf74dc32/Chapter_5_Data_Oriented_Modelling/Modelling_Hypothesized_Mechanisms_Underlying_Data/REPORT_EN.md)

[7] How Language Models Reach an Answer. Chapter 3, Report 02, English edition 1.0. Experiments 026–027 measure readiness protection and recovery; 028A studies recorded-agent routing and candidate coverage. These inform Sections 15, 16 and 20. [Open research record](https://github.com/walkingrui-bot/Data-Oriented-Modelling-Reports/blob/e49d085ff9112a8c02ef3ac1a6ff3914bf74dc32/Chapter_3_Machine_Learning_Epidemiology/How_Language_Models_Reach_an_Answer/REPORT_EN.md)

[8] Data-Oriented Modeling Corrective Optics for Language Models. Living Engineering Report, version 1.4, 29 September 2026. The research overview and current evidence summary, including ASTIG-013D and ASTIG-013E, inform Section 20.

Public research records were checked on 30 September 2026. This narrative follows the evolving experimental record.

[Back to Chapter 0](README.md) · [All chapters](../README.md)
