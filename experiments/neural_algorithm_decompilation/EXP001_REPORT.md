# EXP001 — Blueprint Slots and Context Fill in a Pretrained Language Model

**Research line:** Neural Algorithm Decompilation  
**Model:** Qwen/Qwen2.5-0.5B-Instruct  
**Status:** Executed controlled-model experiment  
**Date:** 2026-10-06  
**Experimental branch:** `exp/neural-blueprint-slots-qwen05b-20261006`

## Question

Does a pretrained language model construct a blueprint as a fixed set of physically separate slots, or does it implement a variable number of logical slots through a shared physical substrate? How is context information transferred into the currently executable part of that blueprint?

The experiment separates four measurable objects:

1. simultaneous future-item decodability before the first output token;
2. effective dimension and overlap of future-position codes;
3. stage-dependent source-token attention;
4. causal transfer from a source token into the next output state.

A separate context-fill assay changes one source value while permuting requested output order. This distinguishes source-addressed representation from output-slot-addressed representation.

## Model and task

The tested model is Qwen2.5-0.5B-Instruct (reported 0.49B parameters, 24 Transformer blocks, hidden size 896, 14 attention heads and 2 KV heads).

The primary behavioral assay is exact sequence copying for lengths 2–6. Copying was selected because the model gave restricted next-digit accuracy 1.0 at the tested lengths, whereas reversal became unreliable as length increased. The analysis therefore studies a computation the model can execute rather than confounding slot geometry with gross task failure.

## Result 1 — The initial state contains multiple future items, but not as independent physical slots

Before the first output token, the final prompt state was probed for every future output position using independently sampled digit positions.

At layer 24:

| Length | Probe accuracy by future offset | Effective rank | Rank95 | Mean pairwise slot-subspace overlap |
|---|---|---:|---:|---:|
| 2 | 1.000, 0.975 | 4.456 | 6 | 0.671 |
| 3 | 1.000, 0.958, 0.908 | 5.076 | 7 | 0.582 |
| 4 | 1.000, 0.925, 0.650, 0.750 | 5.765 | 8 | 0.625 |
| 5 | 1.000, 0.900, 0.408, 0.483, 0.658 | 5.149 | 8 | 0.641 |
| 6 | 1.000, 0.875, 0.458, 0.400, 0.417, 0.583 | 5.649 | 9 | 0.653 |

Chance for each digit probe is 1/6.

The first future item is perfectly readable at every tested length. Later items remain above chance but become progressively less explicit as the plan length grows. Meanwhile the joint coding dimension does not grow in proportion to the number of future positions: effective rank remains about 4.5–5.8 from length 2 to 6.

Future-position subspaces also overlap strongly. Mean pairwise overlap stays about 0.58–0.67. For the same future offset across adjacent sequence lengths, layer-24 subspace overlap is 0.752 (2→3), 0.686 (3→4), 0.712 (4→5), and 0.664 (5→6).

**Supported interpretation:** additional logical output positions are represented through substantial reuse of a common physical coding substrate. The measurements do not support one new independent hidden-state subspace for every additional output slot.

## Result 2 — A stage-dependent source pointer selects the item currently due

In a five-item copy task, attention from the current output state to the source positions was measured across layers and output stages.

Layer 16 gives the strongest source-pointer signature:

- mean selectivity for the currently due source item: **0.6185**;
- uniform-within-source baseline: **0.20**;
- mean head hit rate: **0.8607**.

By stage at layer 16:

| Output stage | Correct-source selectivity | Head hit rate |
|---|---:|---:|
| 0 | 0.760 | 0.946 |
| 1 | 0.558 | 0.875 |
| 2 | 0.517 | 0.786 |
| 3 | 0.586 | 0.804 |
| 4 | 0.670 | 0.893 |

The selected source location moves with the output stage. This is compatible with a dynamic addressing operation rather than a fixed one-slot-per-source readout.

## Result 3 — Source content is causally handed off before the final layer

A donor run changed the currently due source item. Its contextual state was transplanted into the original run at the corresponding source position.

Mean change in donor-vs-original next-token margin:

| Patch location | Target source | Distractor source |
|---|---:|---:|
| embedding | +16.711 | +0.646 |
| block 7 | +16.518 | +0.627 |
| block 15 | +16.425 | +0.701 |
| block 23 | 0.000 | 0.000 |

The target source state has a large selective causal effect through block 15, while an unrelated source position has a small effect. By block 23, changing the source-position state no longer changes the next-token margin in this assay.

**Supported interpretation:** source information is retrieved and transferred into downstream computation before the final block. The source position acts as a causal input carrier during the earlier/middle stack, after which responsibility has been handed off to later states.

## Result 4 — Context filling changes coordinate system across depth

The context-fill assay used a temporary key/value table. One key value was changed while the requested key order was permuted. Therefore the same semantic source edit could be compared either by source-key identity or by requested output slot.

Two edit magnitudes were executed independently: 0→1 and 4→9. They show the same qualitative depth transition.

### Early layers: source-addressed

For 0→1 edits at layer 6:

| Number of requested slots | Same-source cosine | Same-output-slot cosine | Slot minus source |
|---|---:|---:|---:|
| 2 | 0.763 | 0.572 | -0.191 |
| 4 | 0.791 | 0.605 | -0.186 |
| 6 | 0.812 | 0.626 | -0.186 |

The 4→9 replication gives the same ordering.

Thus early edit directions are more stable when aligned by the source key/location than when aligned by the eventual requested output slot.

### Late layers: partial remapping toward output-slot coordinates

At layer 18 for 0→1:

| Slots | Same-source cosine | Same-output-slot cosine | Slot minus source |
|---|---:|---:|---:|
| 2 | 0.376 | 0.551 | +0.175 |
| 4 | 0.328 | 0.376 | +0.049 |
| 6 | 0.391 | 0.381 | -0.009 |

The independent 4→9 edit gives +0.310, +0.053 and -0.008 at the same layer.

For two requested slots, the representation cleanly changes from source-dominant to output-slot-dominant. With four slots the late output-slot advantage is weaker. With six slots it is approximately tied.

Late-layer slot identity remains decodable above chance but its separation weakens with slot count. Representative best slot-decode accuracies are:

- 2 slots: 1.000 (chance 0.500);
- 4 slots: 0.458–0.500 (chance 0.250);
- 6 slots: 0.292–0.339 (chance 0.167).

At the same time, the edit-prototype geometry remains extremely low-dimensional: participation-rank estimates are roughly 1.1–1.7 and rank90 is usually 1–2 even when six logical slots are requested.

Cross-length prototype alignment is high. In the 0→1 assay, shared-slot prototype cosine between four- and six-slot tasks is about 0.91–0.97 across the sampled middle/late layers. The 4→9 replication is similar.

## Mechanistic synthesis

The executed measurements support the following staged organization:

```
context source positions
        ↓
source-addressed local representation
        ↓
stage-dependent pointer / retrieval
        ↓
partial remapping into output-slot coordinates
        ↓
causal handoff to downstream output state
        ↓
token emission
```

The current best description is therefore **variable logical slots over a reused physical substrate**, not a fixed bank of one independent physical slot per future item.

A useful operational form is:

```
blueprint = shared plan code + phase/pointer state + currently bound content
```

The number of logical future positions can increase without a proportional increase in measured coding dimension. The currently due item receives the strongest explicit representation, while later items remain more compressed/overlapping and are progressively retrieved as generation advances.

The weakening of late slot separation from 2 to 4 to 6 requested positions is consistent with competition for a shared representational substrate. This experiment measures that compression/interference pattern; identifying its architectural limit requires a dedicated length/capacity sweep.

## Evidence boundary

These results establish the measured organization for controlled copy and temporary key/value tasks in one fixed pretrained Qwen2.5-0.5B-Instruct checkpoint.

Linear decodability is used as a measurement of available information, not as proof that the model internally uses the linear decoder. Effective rank is a property of the measured coding geometry and should not be read as an exact count of biological-style registers.

The context-fill free generations are less reliable than the copy task, especially for repeated-value prompts. The context-fill result is therefore interpreted primarily from hidden-state geometry, paired edit directions and teacher-forced margins rather than from unrestricted generation.

## Executed evidence

- Fast copy/reverse slot probe: GitHub Actions run **37472995262**.
- Initial independent-position blueprint probe: run **37474028219**.
- Context-fill 0→1 replication: run **37474456880**.
- Context-fill 4→9 replication: run **37475447655**.

Scripts:

- `scratch/neural_blueprint_slots_qwen05b/run_fast.py`
- `experiments/neural_algorithm_decompilation/EXP001B_initial_blueprint_probe.py`
- `experiments/neural_algorithm_decompilation/EXP001_blueprint_slots_qwen05b.py`

## Next experiment

The next direct test should separate **logical plan length** from **physical coding capacity** by increasing the number of independently addressable items while keeping the same operation family, then causally clamping or swapping the phase/pointer state.

The critical predictions are:

1. if logical slots are generated dynamically, plan length can increase while the shared coding dimension saturates;
2. pointer-state intervention should change which source item is transferred without globally changing source content;
3. once physical capacity is exceeded, slot-specific remapping and output margin should deteriorate before source information itself disappears;
4. increasing model width/depth should move that transition if it is a genuine capacity boundary.
