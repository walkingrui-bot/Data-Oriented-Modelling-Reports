# Tiny Blueprint EXP003B — Answer-Only Latent Blueprint

**Seed:** 20261009  
**Parameters:** 20,454  
**Latent bottleneck:** 8 dimensions  
**Training signal:** final answer tokens only

The planner receives context rules, query, order bit, and style bit. The executor receives only the latent `z` plus the numeric payload `(x,y)`. Blueprint labels are not used to train the network.

## Fresh-test answer performance

- token 1: **100.00%**
- token 2: **100.00%**
- exact answer: **100.00%**
- attention mass on the relevant rule fact: **0.033602**

## What is readable from `z` after training?

Linear probes are trained only after the network is frozen.

- operation: **100.00%**
- argument order: **100.00%**
- style: **100.00%**
- complete 12-state blueprint: **100.00%**

## Causal transplant

For 3,000 random pairs, the donor supplies `z`, while a different recipient supplies new numbers `(x,y)`. The expected counterfactual answer is the donor blueprint executed on the recipient numbers.

- exact donor-plan transplant agreement: **100.00%**

## Evidence supported

Under answer-only training, the 8-D bottleneck acquires a compact state from which all three blueprint factors can be read. The same state can be transplanted to new payloads and makes the executor apply the donor plan to the recipient numbers. In this controlled system, the hidden state therefore functions as a reusable internal blueprint even though no blueprint label was supplied during model training.
