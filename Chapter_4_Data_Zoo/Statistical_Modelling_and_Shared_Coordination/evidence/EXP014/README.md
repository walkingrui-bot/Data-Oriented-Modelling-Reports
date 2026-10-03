# INTERNAL_COORDINATION_014 - Statistical Observer Committee and Conditional Routing

Experiment 014 asks whether multiple traditional statistical models should enter the shared ganglion as a committee of derived observers.

The three observers are: an additive masked logistic model, an interaction polynomial model, and a beta-binomial empirical-Bayes evidence-state model. All training-time observer outputs are strict target-group cross-fitted predictions.

Main result: the observers have different evidence-regime profiles, but a larger committee does not improve the current drug-evidence prototype. The single interaction observer from Experiment 013 remains stronger on the median. A learned router consistently gives most weight to the interaction observer and substantial secondary weight to empirical Bayes, while additive receives the smallest weight. As biological pipelines disappear, additive weight rises slightly. This routing structure is reproducible, but the extra routing flexibility currently costs more optimisation error than it returns in predictive gain.

This is retained as a useful negative engineering result: observer diversity exists, but the present system should not pay for a multi-observer committee until the native evidence pipelines become richer.
