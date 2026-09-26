# Round 3 protocol

## Experiment A — forged upstream history
Task: infer hidden b in y=(x+b) mod 5 from three evidence pairs, answer a new query.
Model: 2-layer Transformer, hidden size 16, 2 heads.
Seeds: 11, 22, 33.
Final test accuracy: 98.5%, 99.2%, 100%.

Interventions after layer 1:
1. mean rule-direction shift at query position;
2. exact natural donor query activation into recipient;
3. donor evidence contextual states only;
4. full donor layer-1 distributed state.

Compare downstream target accuracy, output TV, and layer-2 query-state cosine.

## Experiment B — is temporally evolving rule state necessary?
B1: one-shot MLP, three clean evidence pairs, held-out evidence-x patterns.
B2: one-shot permutation-invariant set model, eight evidence pairs, 30% corrupted relations.
No recurrence, no persistent hidden state, no CoT, no iterative rule update.
Compare against majority/Bayes reference for B2.
