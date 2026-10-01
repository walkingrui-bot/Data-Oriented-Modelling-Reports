# Data-Oriented Modelling — Reports

## What Data-Oriented Modelling means

# Data-Oriented Modelling

The core of data-oriented modelling is to determine the modelling approach from the structure of the data itself.

For problems in which the mechanisms, relationships between variables, and constraints are already relatively well understood, mathematical modelling can directly incorporate these known structures and often achieve high interpretability and computational precision. Neural networks, by contrast, are well suited to learning complex mappings from large numbers of samples and extracting general statistical patterns through shared parameters. These two approaches have different strengths and correspond to different data conditions.

The first step in modelling is therefore to study the data. This involves identifying the statistical structure of the data, its temporal relationships, dependencies between variables, patterns of change across different states, and the stability of these structures across samples and conditions. As these properties become clearer, it also becomes clearer what the model needs to learn, which relationships can be calculated directly, and which components need to be learned from data.

Different types of data correspond to substantially different learning tasks. Some problems are dominated by stable mappings; in others, the mapping changes with the state of the system. Some data exhibit deeper generative regularities, while other datasets contain multiple observations of the same underlying object from different perspectives. Different statistical structures require different forms of representation and different computational structures.

How the data are presented to the model is equally important. Static variables, temporal trajectories, state transitions, and multi-source observations define different learning problems. The representation of the data determines which structures the model can directly use and is therefore itself part of model design.

Within this framework, mathematical methods, statistical models, and neural networks are combined according to the structure of the data. Relationships that are already well characterised can be incorporated directly into mathematical models. Complex regularities that need to be estimated from samples can be handled by learning models. Relationships that vary with state can be represented using computational structures capable of expressing such variation. Model complexity, architecture, and training strategy are therefore determined by the characteristics of the specific data.

This approach applies both to general modelling across different data types and to high-precision modelling for a specific dataset. The former focuses on modelling principles that can be reused across different data structures, while the latter focuses on making full use of structures already identified within a particular dataset.

Data-oriented modelling ultimately addresses a practical question:

For the data at hand, what combination of representation, mathematical structure, and learning method produces the most appropriate model?

Mathematics, statistics, and machine learning already provide a large collection of mature tools. The essential task is to identify the structure of the data accurately and apply the appropriate methods in the appropriate places.

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
