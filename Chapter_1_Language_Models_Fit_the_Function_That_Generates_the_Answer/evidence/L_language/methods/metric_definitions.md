# Metric definitions

## Token/identity representation
Early experiments deliberately remove semantic labels. A token is represented only by its identity, occurrence position, local offsets, and recurrence relations. In multilingual pilots, the first pass used Unicode-normalized character bigrams to avoid dependence on a particular language tokenizer; later sanity checks used word-level tokens for English/Spanish/French.

## Local geometry
Equality/recurrence at short relative offsets (typically ±1…±16 or lag bins). It captures local order without semantic labels.

## Recurrence
A repeated identity links the current occurrence to previous occurrences. Important controls preserve token frequency but shuffle positions, so recurrence count alone cannot solve the task.

## Structural bridge
A recurrence is informative when a small neighborhood of relations around the old occurrence is reinstated around the new occurrence. Implementations used ordered/equality patterns around repeated positions and iterative propagation of typed offsets. Ordinary untyped graph diffusion was a negative control.

## Block-shuffle structural horizon
Text is split into contiguous blocks of size k; blocks are shuffled while within-block order is preserved. If discrimination falls toward 0.5 as k grows, the destroyed information is increasingly global; if it remains high only at small k, the strongest signal is local/mesoscale.

## Eye-movement regression
In the pilot, a backward interest-area transition of at least 5 word positions is treated as a clear long regression. This is intentionally stricter than counting every small corrective saccade, but is not identical to published canonical regression definitions.

## Gate percentile
For a regression source fixation, fixation duration is ranked against nearby forward-reading source fixations matched by trial and approximate location. 0.5 is the local median; values below 0.5 mean the regression tends to launch from relatively shorter/lower-load fixations.

## Target availability / history
For a true regression target, compare whether it had been fixated before to distance-matched old positions. Among previously seen candidates, rank prior visit count, dwell time, maximum fixation, and recency. Values near 0.5 indicate no target-selection value.

## Effective candidate number (expected semantic field)
For non-negative relation weights w_i over candidate old targets, normalize p_i=w_i/sum(w) and compute exp(-sum p_i log p_i). This is the entropy-effective number of simultaneously supported candidates. Larger E[PPMI] effective counts indicate a more distributed attraction field than direct PPMI.

## Genre/author geometry
All public-domain style/author experiments use the same English tokenizer and equal-sized content-word windows. Features include recurrence density; short/mid/long recurrence proportions; gap CV; local bridge; repeated bigram/trigram density; and burst CV over eight temporal bins.
