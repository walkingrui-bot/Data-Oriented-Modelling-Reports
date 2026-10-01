# Data-Oriented Modelling — Reports

## What Data-Oriented Modelling means

We study how data can tell us what kind of model to build. The starting point is the process that produced the observations. We then investigate which relationships stay stable, which change with the situation, and how those changes unfold. These findings guide the model's structure, what it learns and how it is evaluated. This is the central idea of **Data-Oriented Modelling: model design itself becomes an outcome of data analysis.**

Every observation has a source, a time and a way of being measured. We begin by establishing what was recorded and how the recording process shaped it. This gives us a basis for separating changes in the underlying system from changes in how it was observed. It also lets us bring different sources together while preserving what each observation means.

Next we study how the data is organised. By *data geometry*, we mean how observations are arranged and related: their distances, neighbourhoods, patterns of variation and paths through time. Statistics and mathematical modelling help us find which differences carry useful information, which relationships repeat, and how several influences work together. This analysis gives model design its first set of requirements.

A central question is where that structure carries information about cause and effect. We develop hypotheses about what generates the observations, work out what those hypotheses predict, and compare those predictions with measured responses. A hypothesis gains support where its expected relationships and responses hold under the conditions tested. The process continues as new observations help us refine the account of how the system works.

We also follow what happens when something changes. The size, direction and timing of the response tell us where information matters and how its effects travel through the system. This connects the description of a state with an explanation of what happens next. It gives us a concrete basis for deciding which information a model should retain.

That question follows the information through learning. As a model transforms and combines its inputs, we examine what happens to the relationships we have measured. We want the distinctions that support prediction, explanation or action to remain useful throughout the computation. Designing a representation and a training objective therefore includes deciding which relationships they should preserve, and measuring how well they do so.

Some relationships remain stable across the conditions studied. Others depend on the current situation or on what happened earlier. We investigate both the relationships and the rules governing their change. Stable structure can support a direct mathematical mapping. Useful information from the past gives a model a reason to keep memory. Measurable changes in the governing relationships give it a reason to update its account of the mechanism. The evidence determines which of these roles the model needs.

**Complexity is something the data has to ask for.** We look for repeatable patterns that the current model leaves unexplained, then test whether additional computation captures them. Each addition earns its place through a measurable contribution. This makes both the amount of computation and where it is used part of the research.

When several sources describe a shared system, we first establish the meaning and structure of each source. Their models can then be coordinated by asking whether they support a common account that explains their observations. Information about the same moment is brought together according to what it describes; changes through real time retain their chronology. The aim is to learn what is shared while preserving the contributions of the different observations.

For systems that act, this extends into a continuing cycle: evidence informs the model's account of the current state, that state supports a decision, and the observed result informs the next decision. We study both the individual operation and its contribution to the complete sequence of behaviour. Perception, decision and execution each become parts of the same measurable process.

Precision comes from fitting the computation to the particular data and the question being asked. Generality comes from identifying which principles and learned relationships can carry across tasks, sources and settings. We test these possibilities through repeated measurements, appropriate comparisons and targeted interventions.

Our aim is to reach model design with an experimental reason for each part of the computation. **Study how the world produces data → identify stable and changing mechanisms → build the model those findings call for.** In this way, *when to build which model* becomes a research question in its own right.

## Research lines and evidence

This map connects the design philosophy to the studies that support it. Status reflects the records reviewed on **1 October 2026**. **Published** entries link to public reports and their evidence indexes. **Recorded experiments — publication pending** identifies existing research records; **documented design — publication pending** identifies a prepared method or architecture specification.

| Research line | Evidence and contribution | Record and publication status |
| --- | --- | --- |
| Language Generation and Answer Recovery | Experiments track answer-ready states, training history, local control and recovery along a reasoning trajectory. | **Published:** [Chapter 2](Chapter_2_Language_Models_Motor_Control_and_Deep_Space_Drift/README.md), [Chapter 3](Chapter_3_Machine_Learning_Epidemiology/README.md) and [How Language Models Reach an Answer](Chapter_3_Machine_Learning_Epidemiology/How_Language_Models_Reach_an_Answer/EVIDENCE_INDEX.md), following [Chapter 1](Chapter_1_Language_Models_Fit_the_Function_That_Generates_the_Answer/README.md). |
| Identifying and Modelling Data-Generating Mechanisms | Studies locate identifiable information under stated assumptions, measure how representations transform it, and test candidate operations through transfer, edits and interventions. | **Published:** [Chapter 5, Report 01](Chapter_5_Data_Oriented_Modelling/Heterogeneous_Data_and_General_Data_Intelligence/EVIDENCE_INDEX.md); [Report 02, CG001–CG024](Chapter_5_Data_Oriented_Modelling/Learning_Causal_Structure_from_Data_Geometry/EVIDENCE_INDEX.md); [Report 03](Chapter_5_Data_Oriented_Modelling/Modelling_Hypothesized_Mechanisms_Underlying_Data/EVIDENCE_INDEX.md). |
| Data Structure and Dataset-Specific Modelling | Dataset-specific studies examine language structure, human learning, language–movement relations and genomic predictive geometry in their own statistical forms. | **Published:** [Chapter 4, Subreports 01–04](Chapter_4_Data_Zoo/README.md), each with its own evidence index. |
| Model Perception and Action Control | ASTIG studies connect calibrated observation, candidate availability, task phase and execution feedback. Layerwise mode measurements and targeted interventions test first-action control in a fixed pretrained model. | **Published:** [Chapter 6, Report 01](Chapter_6_Model_Perception_and_Control/Model_Perception_and_Action_Control/README.md) · [evidence index](Chapter_6_Model_Perception_and_Control/Model_Perception_and_Action_Control/EVIDENCE_INDEX.md). Continues Chapters 2, 3 and 5. |
| Multiscale Language Generation | Scale comparisons and room interventions inform a multiscale block generator. EXP015 measures future-block consequences at 1,988 word-replacement points, providing an empirical target for gain and loss design. | **Recorded experiments — publication pending:** EXP001–EXP015; *Multiscale Language Computation Living Record*, v1.4, with experiment evidence packages. |
| Chemical Structure Changes and Odor Responses | Matched molecular-edit trajectories separate transferable response directions, current-state conditioning and transition-dependent direction. CHEM-ODOR-007 tests the previous response as a predictor of the next response across held-out chemical trajectories. | **Recorded experiments — publication pending:** Chemical–Odor 001–007, including *Stable Mappings, Variable Operators, and Latent Transition State*, v0.1. Data Zoo chemical–odor line. |
| Multi-Source Observation and Shared-State Modelling | Controlled multi-channel experiments learn a shared state while separating stable measurement operators and changing channel states. Experiment 008 tests same-time permutation invariance and sensitivity to real chronology. | **Recorded experiments — publication pending:** INTERNAL-COORDINATION-001–008; *Living Report*, v0.9. A reusable coordination layer around specialized data models. |
| Data Structure and Computational Resource Allocation | On three real numeric datasets with semi-synthetic observation distortions, residual-driven module birth and dormancy respond to a compute price. Geometry and neighbourhood retention quantify the resulting trade-offs. | **Recorded experiments — publication pending:** GDI-DATA-CLOUD-003, *Self-Growing Capacity Under a Compute Price*, v0.1, and its evidence package. |
| Longitudinal Prediction and History Aggregation | Whole-entity validation tests compact representations of observation history for a specified next-step prediction. In the studied dataset, all eight history coordinates selected in each of seven folds belong to the same repeated-measurement family: 56/56 selections. | **Recorded experiments — publication pending:** GDI longitudinal study 004, v0.3; companion observation-modelling record, v0.29. Dataset-specific signal discovery and aggregation line. |
| Evidence Combinations and Statistical Relationships | Enumeration of six evidence classes measures conditional associations and higher-order interactions in an observed dataset. | **Recorded analysis — publication pending:** HOW-FAR-001, v0.1. Exhaustive statistical analysis of six evidence classes. |
| Data Provenance, Time and Measurement Structure | Eighteen source-specific passport designs record observation units, native geometry, hierarchy, time, provenance and uncertainty. The design aligns evidence by its availability time and specifies evaluation against later observations. | **Documented design — publication pending:** *Evidence Data Passport: 18 Pipelines*, v0.1. Native-source and versioned-evidence extension of HOW-FAR. |
| Error Recovery and Expert Routing Control | Controlled two-layer MoE experiments distinguish local recomputation from downstream recovery. Route locks, clean-route replay and timing interventions locate routing contributions in eight-seed studies. | **Recorded experiments — publication pending:** INTERROGATIVE-CONTROL-001, SELF-QUESTION-REENTRY-002, ROUTE-LOCK-REENTRY-003 and ROUTE-TIMING-REENTRY-004; *Living Record*, v0.4. Agent-control extension. |

## Reports and reading routes

**[不想看／看不懂报告，就看过来。](Chapter_0_The_Story_Version/README.md)**

**[Don't feel like reading the reports? Getting lost in them? Start with Chapter 0 — The Story Version.](Chapter_0_The_Story_Version/README.md)** A moving finger, a cloud of data, a stack of burgers and a detective explain why we are doing this research. The story grows with the project.

Chapters 1–6 contain the research reports, supporting experiments and evidence.

| Chapter | Title | Open |
| --- | --- | --- |
| **0** | **The Story Version — 不严肃小故事版** | [Read the story](Chapter_0_The_Story_Version/README.md) |
| **1** | **Language Models Fit the Function That Generates the Answer** | [Read Chapter 1](Chapter_1_Language_Models_Fit_the_Function_That_Generates_the_Answer/README.md) |
| **2** | **Language Models: Motor Control and Deep-Space Drift** | [Read Chapter 2](Chapter_2_Language_Models_Motor_Control_and_Deep_Space_Drift/README.md) |
| **3** | **Machine Learning Epidemiology** | [Read Chapter 3](Chapter_3_Machine_Learning_Epidemiology/README.md) |
| **4** | **Data Zoo** | [Read Chapter 4](Chapter_4_Data_Zoo/README.md) |
| **5** | **Data-Oriented Modelling** | [Read Chapter 5](Chapter_5_Data_Oriented_Modelling/README.md) |
| **6** | **Model Perception and Control — Continuing Chapters 2, 3 and 5** | [Read Chapter 6](Chapter_6_Model_Perception_and_Control/README.md) |

**Chapter 3 contains two reports.** Report 01 brings together the research report and The Engineer’s Edition. Report 02, **[How Language Models Reach an Answer](Chapter_3_Machine_Learning_Epidemiology/How_Language_Models_Reach_an_Answer/README.md)**, connects language dynamics, protected training and answer-recovery control across 18 experiments. It is also listed as Chapter 2, Report 02.

[Chapters 1 and 2, original reports — DOI](https://doi.org/10.5281/zenodo.22974937) · [Chapter 3, Report 01, both editions — DOI](https://doi.org/10.5281/zenodo.22983593)

This is a self-directed personal-interest research project. It is maintained as a living research record. Chapter 4 collects independently versioned subreports: [Language Structure and Control Geometry](Chapter_4_Data_Zoo/Language_Structure_and_Control_Geometry/README.md) is Subreport 1, and [Human Learning and Sensorimotor Geometry](Chapter_4_Data_Zoo/Human_Learning_and_Sensorimotor_Geometry/README.md) is Subreport 2. [Language–Movement Integrated Study](Chapter_4_Data_Zoo/Language_Movement_Integrated_Study/README.md) is Subreport 3. [Genomic Predictive Geometry and Model Capacity](Chapter_4_Data_Zoo/Genomic_Predictive_Geometry_and_Model_Capacity/README.md) is Subreport 4. These reports are available in English edition v1.0.

[About the project](Chapter_1_Language_Models_Fit_the_Function_That_Generates_the_Answer/PROJECT_INFORMATION.md) · [Citation](Chapter_1_Language_Models_Fit_the_Function_That_Generates_the_Answer/CITATION.md) · [Source and reuse terms](Chapter_1_Language_Models_Fit_the_Function_That_Generates_the_Answer/SOURCE_NOTES.md)

Chapter 5, **Data-Oriented Modelling**, is a series of independently versioned reports. Its first report, **Heterogeneous Data and General Data Intelligence**, connects generating mechanisms, observation processes and source-native structures with modelling and distributed coordination.

Chapter 5, Report 02, **[Learning Causal Structure from Data Geometry](Chapter_5_Data_Oriented_Modelling/Learning_Causal_Structure_from_Data_Geometry/README.md)**, examines where causal information occurs in data geometry, how learning preserves or distorts it, and how retained structure is tested through transfer and interventions.

Chapter 5, Report 03, **[Modelling Hypothesized Mechanisms Underlying Data](Chapter_5_Data_Oriented_Modelling/Modelling_Hypothesized_Mechanisms_Underlying_Data/README.md)**, connects data geometry, training coverage and valid state transformations with candidate operations tested through validation.

Chapter 6, **Model Perception and Control — Continuing Chapters 2, 3 and 5**, studies decision-making agents. It directly continues the research developed in Chapters 2, 3 and 5. Report 01, **[Model Perception and Action Control](Chapter_6_Model_Perception_and_Control/Model_Perception_and_Action_Control/README.md)**, connects calibrated observation, action eligibility and execution feedback with layerwise measurements and targeted first-action intervention.

**Recommended reading order:** [Chapter 2](Chapter_2_Language_Models_Motor_Control_and_Deep_Space_Drift/README.md) → [Chapter 3](Chapter_3_Machine_Learning_Epidemiology/README.md) → [Chapter 5](Chapter_5_Data_Oriented_Modelling/README.md) → [Chapter 6](Chapter_6_Model_Perception_and_Control/README.md).

Some hypotheses developed in this research have received substantive validation through engineering implementations. Data models are forthcoming.
