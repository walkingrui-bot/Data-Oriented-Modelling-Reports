# LANGUAGE-CONTROL-DIMENSION-COLLAPSE-014

## Question

Does language training itself compress the effective control freedom of a recurrent language model, relative to training on a non-linguistic world with genuinely higher intrinsic control dimension?

This experiment was designed as a complement to `TEACHER-DIMENSION-TRANSFER-013`. The aim here was not merely to vary the teacher's intrinsic dimension, but to ask whether a model trained on natural language occupies a systematically flatter local future-control geometry than the same architecture trained on high-dimensional non-linguistic sequential data.

## Core design

All token conditions used the same architecture and optimization budget:

- vocabulary size: 64
- embedding dimension: 8
- GRU hidden dimension: 48
- output head: 64-way next-token prediction
- sequence length: 48
- batch size: 48
- optimizer: AdamW
- training steps: 900
- random seeds: 11, 22, 33

### Language condition

A 431,826-character English technical-language corpus was built from locally installed Go documentation after HTML stripping. The 63 most frequent characters plus an UNK symbol formed the 64-token vocabulary.

Observed unigram entropy:

- **3.198 nats**

Final next-token loss across the three trained models was approximately 1.82–1.90 nats.

### Synthetic control worlds

Each synthetic token represented a six-bit state (64 possible tokens).

For low-dimensional calibration worlds, only the first `d` bits carried temporally predictive Markov structure; the remaining bits were independently resampled nuisance dimensions.

Conditions used here:

- synthetic 2D world
- synthetic 3D world
- synthetic 6D world

A stronger six-dimensional control was also created to match the language condition in both marginal token entropy and prediction difficulty.

For the matched six-dimensional world:

- six independently predictive state dimensions
- stationary bit probabilities: `[0.50, 0.40, 0.30, 0.20, 0.15, 0.10]`
- persistence parameters: `[0.85, 0.78, 0.71, 0.64, 0.57, 0.50]`
- observed unigram entropy: **3.231 nats**
- theoretical conditional entropy: **1.836 nats**
- trained next-token loss: **1.84–1.86 nats**

Thus this control closely matched the language corpus in both symbol entropy and prediction difficulty while retaining six independent predictive control dimensions.

## Control-field readout

For each trained model, 30 random trajectory windows were sampled.

At each window:

- context length: 32 tokens
- future horizon: 8 recurrent steps
- future response: concatenated hidden trajectory over the next 8 steps, dimension `8 × 48 = 384`
- local control input: current 8D token embedding

The local future-response Jacobian was

\[
J_t = \frac{\partial (h_t, h_{t+1}, \ldots, h_{t+7})}{\partial e_t}.
\]

Singular values of `J_t` were used to measure effective local control dimensionality.

Primary readouts:

- stable rank
- participation rank
- entropy effective rank
- 95% energy dimension
- energy captured by the first 2 and first 3 singular modes

Reported values below are the mean of each seed's median trajectory statistic, with SD across the three seeds.

## Main results

| Condition | Stable rank | Participation rank | Entropy effective rank | 95% energy dimension | Energy in top 3 modes |
|---|---:|---:|---:|---:|---:|
| Random initialization | 4.368 ± 0.608 | 6.607 ± 0.306 | 7.220 ± 0.156 | 8.000 ± 0.000 | 56.2% ± 2.7% |
| Language | **2.238 ± 0.026** | **3.559 ± 0.044** | **4.786 ± 0.045** | **6.000 ± 0.000** | **79.9% ± 0.9%** |
| Synthetic 2D | 2.029 ± 0.215 | 3.048 ± 0.343 | 4.021 ± 0.349 | 5.167 ± 0.289 | 87.5% ± 2.0% |
| Synthetic 3D | 2.559 ± 0.180 | 3.898 ± 0.253 | 4.885 ± 0.263 | 5.667 ± 0.577 | 79.7% ± 2.5% |
| Synthetic 6D, uniform | 3.358 ± 0.062 | 5.223 ± 0.024 | 6.151 ± 0.015 | 7.000 ± 0.000 | 68.4% ± 1.2% |
| Synthetic 6D, entropy + difficulty matched | **3.101 ± 0.122** | **4.929 ± 0.149** | **5.891 ± 0.100** | **6.667 ± 0.577** | **70.4% ± 1.5%** |

The entropy-and-difficulty-matched six-dimensional world retained a stable rank **38.6% higher** than language and a participation rank **38.5% higher** than language, despite closely matched marginal entropy and next-token prediction loss.

The language model's control spectrum was therefore much closer to the synthetic 2D/3D calibration worlds than to either six-dimensional world.

Random initialization was substantially less concentrated than the language-trained state. Stable rank fell from 4.368 at initialization to 2.238 after language training, while the top-three-mode energy rose from 56.2% to 79.9%.

## Training-order intervention

Two directional transfer tests were added.

### Six-dimensional world → language

A model first trained on the six-dimensional synthetic world was subsequently trained on the language corpus.

Across three seeds, after language training:

- stable rank: **2.196 ± 0.156**
- participation rank: **3.472 ± 0.271**
- entropy effective rank: **4.600 ± 0.313**
- top-three-mode energy: **80.8% ± 2.3%**

The model moved back into the same low-dimensional control regime as language-only training.

### Language → six-dimensional world

A language-trained model was subsequently trained on the six-dimensional synthetic world.

Across three seeds:

- stable rank: **2.848 ± 0.105**
- participation rank: **4.489 ± 0.242**
- top-three-mode energy: **72.3% ± 2.3%**

The effective control geometry re-expanded toward the six-dimensional regime.

## Interpretation supported by this experiment

Within this controlled recurrent model, effective control dimension is not fixed by architecture.

The same 8D-input / 48D-hidden GRU can occupy markedly different future-control geometries depending on the structure of its training world.

Natural-language training consistently drives the local control spectrum toward a low-dimensional regime close to the 2D–3D synthetic calibration worlds.

A genuinely six-dimensional predictive world expands the spectrum, including when marginal symbol entropy and prediction difficulty are matched to language.

Training order further shows that this geometry is plastic:

- six-dimensional training can be compressed by subsequent language training;
- language-compressed geometry can be re-expanded by subsequent high-dimensional training.

The evidence therefore supports a concrete version of the hypothesis:

> **Language data can act as a dimensionality-selective teacher, concentrating the model's effective future-control geometry into a small number of dominant modes.**

In this micro-model, the observed language regime is consistent with an effective control structure on the order of roughly two to three dominant dimensions.

## Next empirical scale

The direct next target is to repeat the same measurement hierarchy in:

1. subword/BPE language models;
2. Transformer blocks rather than GRUs;
3. pretrained language models before and after non-linguistic high-dimensional adaptation;
4. matched high-dimensional synthetic sequence worlds with controlled intrinsic rank;
5. full Prompt → CoT → Answer future-response measurements.

The central quantity to preserve across scales is the local future-control spectrum rather than surface token semantics.
