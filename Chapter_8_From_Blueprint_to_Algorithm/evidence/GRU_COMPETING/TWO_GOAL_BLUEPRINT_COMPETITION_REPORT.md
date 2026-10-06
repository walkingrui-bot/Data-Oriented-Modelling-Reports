# Two-Goal Blueprint Competition — Report

## Baseline

The single-objective 187,069-parameter GRU learned one ordered program `E0 -> E1 -> E2` with 100% full-domain accuracy. Its context-final first-layer state carried a strongly additive three-slot blueprint (R² 0.9315).

## Control: goals made distinguishable

When goals A and B were given separate task cues but shared one output head, both tasks reached 100%. Their training gradients remained positively aligned. This control shows that when the network can condition on the goal, it can keep both plans without destructive competition.

## True partial conflict

The final competition experiment removed the task cue and applied two losses to the same input and same output head:

- Goal A: `E0 -> E1 -> E2`
- Goal B: `E0 -> E2 -> E1`

The goals share the first step and the same three operations. They produce the same answer on 25% of the finite domain and different answers on 75%.

The theoretical optimum average loss for the conflicting cases is the equal two-target mixture. Training reached loss **0.5291** vs theoretical **0.5199**.

On genuinely conflicting cases:
- both A and B were present in the model's top-2 outputs: **100.00%**
- mean probability on A: **0.4989**
- mean probability on B: **0.4987**

## What happened to the blueprint

The blueprint did not disappear. Before the payload arrives, the network still reconstructs the three logical operation slots:

- Layer 1 after all three facts: E0/E1/E2 readout = **100/100/100%**
- Layer 2 after all three facts: E0 **100%**, E1 **98.46%**, E2 **99.07%**

The raw 64-way program remains highly readable:
- Layer 1: **97.60%**
- Layer 2: **97.00%**

The first-layer slot-additive geometry remains strong but is weaker than the single-goal baseline:
- single goal Layer 1 R²: **0.9315**
- conflicting goals Layer 1 R²: **0.9212**

Layer 2 changes more:
- single goal Layer 2 R²: **0.8627**
- conflicting goals Layer 2 R²: **0.8176**

Thus competition preserves a shared operation-table precursor while weakening the later execution-facing representation.

## Direct gradient competition

On examples where A and B disagree:

- output-logit gradient cosine: **-1.0000**
- whole-parameter gradient cosine: **-0.5964**
- embedding: **-0.8574**
- GRU Layer 1: **-0.8291**
- GRU Layer 2: **-0.5567**
- output head: **-0.5173**

The two targets therefore pull the shared network in genuinely opposing directions, especially at the input/first recurrent layer.

## Causal branch state

Transplanting a donor context state onto a new payload preserves both donor candidate programs:

- donor A and donor B both appear in top-2: **100.00%**
- donor-A probability: **0.4974**
- donor-B probability: **0.5002**

Editing one shared operation-slot direction makes both candidate branches update consistently:
- both edited branches recovered in top-2: **98.75%**

Layer localization under conflict:
- both donor layers: **100.00%**
- donor L1 + recipient L2: **27.76%**
- recipient L1 + donor L2: **16.14%**
- donor L1 + zero L2: **77.65%**
- zero L1 + donor L2: **37.77%**

## Interpretation supported by this experiment

With one goal, the network forms one ordered execution blueprint. With two indistinguishable but partially conflicting goals, it preserves a shared three-slot operation state and carries two competing execution branches forward instead of committing to one order. The strongest degradation appears in the later execution-facing representation, while the earlier operation-table state remains comparatively stable.
