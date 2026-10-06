# Single-Objective GRU Blueprint / Algorithm Decompilation

## Training system

A **187,069-parameter**, two-layer GRU was trained with one objective only: predict the final scalar answer after reading three shuffled edge-operation facts and one payload value.

No blueprint, operation-slot, intermediate-state, or auxiliary supervision was supplied.

- valid finite domain: **4,992** cases
- final network accuracy: **100.00%**

## Blueprint assembly

Each fact identifies one logical operation slot (`E0`, `E1`, or `E2`) but the three facts are presented in random order.

After one fact, the operation belonging to the fact already read is 100% linearly readable from the recurrent state, while unread slots remain near chance. After two facts, both seen slots are 100% readable. After all three facts, both recurrent layers expose all three operation slots at 100%, and the complete 64-way operation sequence is 100% linearly readable.

Thus the learned blueprint is assembled incrementally as an **ordered three-slot operation state**, not as the presentation order of input facts.

## Where the blueprint is stored

At the end of the context, before the payload value arrives:

- Layer 1: complete 64-way blueprint linear readout **100%**
- Layer 2: complete 64-way blueprint linear readout **100%**
- Layer-1 hidden geometry explained by independent slot effects: **93.15%**
- Layer-2 hidden geometry explained by independent slot effects: **86.27%**

Causal hidden-state transplantation:

- donor Layer 1 + donor Layer 2 -> donor program on recipient payload: **100.00%**
- donor Layer 1 + recipient Layer 2 -> donor program: **42.63%**
- recipient Layer 1 + donor Layer 2 -> donor program: **13.93%**
- donor Layer 1 + zero Layer 2 -> donor program: **80.50%**
- zero Layer 1 + donor Layer 2 -> donor program: **27.33%**

The evidence identifies Layer 1's context-final recurrent state as the primary blueprint store. Layer 2 also contains a complete readable copy, but behaves more like a coordinated execution-facing representation; perfect transfer requires the matched two-layer state.

## Blueprint geometry

The final context state is strongly decomposable into three ordered slot contributions.

- Layer 1 additive 3-slot R²: **0.9315**
- Layer 2 additive 3-slot R²: **0.8627**

Top Layer-1 dimensions by slot:
- operation slot 1: `[30, 13, 6, 20, 85, 38, 104, 3, 44, 120, 54, 9]`
- operation slot 2: `[69, 97, 8, 32, 117, 94, 36, 92, 99, 96, 80, 76]`
- operation slot 3: `[111, 0, 71, 39, 114, 7, 41, 51, 19, 63, 83, 4]`

The dimensions overlap, so the code is distributed rather than one-neuron-per-operation-slot.

## Counterfactual vector editing

Using only the additive slot directions extracted from hidden-state geometry, one operation slot was changed while the payload was held fixed.

- edit corresponding slot vectors in both layers -> counterfactual program answer: **98.77%**
- edit Layer 1 slot vector only -> counterfactual answer: **68.50%**
- edit Layer 2 slot vector only -> counterfactual answer: **35.27%**

## Decompiled algorithm

The recovered behavioral program is:

1. read each fact;
2. place its operation into the logical slot named by `E0/E1/E2`;
3. after all three facts, hold the ordered program `[op1, op2, op3]`;
4. when the payload arrives, execute those three operations in slot order;
5. emit the final value.

The explicit non-neural program agrees with the trained network on **4,992/4,992 = 100.00%** of the complete valid domain.

## Evidence supported

Under a single final-answer training objective, this larger recurrent network forms a stable ordered operation blueprint before seeing the payload. The primary storage site is the first recurrent layer's context-final hidden state, with a transformed copy in the second layer. The blueprint is assembled slot-by-slot from shuffled facts and is then consumed as an execution program when the payload arrives.
