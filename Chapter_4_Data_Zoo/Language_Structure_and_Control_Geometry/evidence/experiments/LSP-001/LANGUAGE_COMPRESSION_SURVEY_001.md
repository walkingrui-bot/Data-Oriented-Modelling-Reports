# LANGUAGE-COMPRESSION-SURVEY-001
## Human Chinese sentence simplification as hierarchical peeling of linguistic structure

Date: 2026-09-27

### Research question
Does repeated sentence shortening preferentially remove particular classes of linguistic material, leaving a small relational/event skeleton? This survey is a first empirical bridge between the previously observed low-dimensional/repeated-operator hypothesis and natural Chinese language.

### Data actually computed
1. MCTS (LREC-COLING 2024): 723 original Chinese news sentences, each with five independent human simplifications, giving 3,615 source→human-simplification pairs.
2. CSS (ACL 2023): 383 original sentences with two human simplifications each, giving 766 pairs.

Total human simplification pairs computed: **4,381**.

Two further public resources were located for the next structural pass:
- CSSWiki (LREC-COLING 2024): ~1.6k operation-annotated Chinese simplification pairs.
- Universal Dependencies Chinese GSDSimp: 4,997 dependency-annotated Simplified Chinese sentences.

### Operationalization
Chinese text was segmented with a Unicode-aware word segmenter. For each source→target pair:

`compression ratio = target token count / source token count`

For MCTS, the 2,078 pairs with ratio < 1 were divided empirically into three equal-sized compression strata:
- L1 mild: 0.9130 < ratio < 1.0; n=686; mean ratio=0.9505.
- L2 medium: 0.7826 < ratio <= 0.9130; n=693; mean ratio=0.8552.
- L3 strong: ratio <= 0.7826; n=699; mean ratio=0.6391.

“Deletion” in the quantitative tables means **exact surface-token disappearance**: a source token no longer appears in the target after multiset matching. It therefore measures visible lexical survival, while paraphrase/substitution can also make a source token disappear. This definition is intentionally reproducible.

A small fixed lexicon was used to group common grammatical/scaffolding tokens (preposition/coverb, structural particle, aspect/modal, conjunction, demonstrative, pronoun, common adverbial/time/degree items). All remaining lexical material forms a coarse CONTENT_OTHER baseline. These categories are a first-pass functional grouping rather than a full POS/dependency parse.

### Core quantitative result: progressive peeling
Exact surface-token disappearance increases monotonically with compression:
- L1 mild: 21.64%
- L2 medium: 30.53%
- L3 strong: 48.05%

The ordering is not uniform across token classes. At mild compression, quantitative detail and contextual/relational scaffolding are disproportionately removed before the broad content-word baseline:

| Category | L1 mild | L2 medium | L3 strong |
|---|---:|---:|---:|
| Numbers / quantitative detail | 51.56% | 60.75% | 76.38% |
| Common degree/time/adverbial material | 37.52% | 50.94% | 65.99% |
| Preposition / coverb scaffolding | 30.43% | 49.48% | 61.07% |
| Determiner / demonstrative material | 28.16% | 43.40% | 64.23% |
| Conjunctions | 25.59% | 31.43% | 51.03% |
| Broad content baseline | 22.44% | 31.02% | 47.69% |
| Aspect / modal items | 19.90% | 25.17% | 52.19% |
| Structural particles | 16.04% | 28.59% | 55.89% |
| Pronouns | 9.16% | 20.93% | 44.25% |

Interpretation supported by this pass:
1. **Mild compression preferentially strips coordinates and implementation detail**: quantities, temporal/degree material, coverb/prepositional scaffolding and determiners disappear faster than the broad content baseline.
2. **Medium compression intensifies the same process**: adverbial and prepositional scaffolding approach 50% surface disappearance while broad content remains around 31%.
3. **Strong compression reaches the grammatical and lexical core**: structural particles, connectives, aspect/modal material and broad content all begin to disappear at high rates.
4. Thus natural human simplification behaves more like progressive peeling than uniform token loss.

### Five-human-reference consensus
MCTS is especially informative because five humans simplify every source independently. For frequent source tokens (>=60 occurrences), exact-form survival across the five references shows a large contrast.

Frequently reformulated/dropped surface items:
- 已 20.62%
- 以 34.92%
- 为 50.85%
- 将 58.72%
- 对 65.56%
- 是 70.34%
- 与 70.98%
- 在 78.69%
- 的 79.20%

Frequently preserved domain/core-content items:
- 国家 93.80%
- 企业 93.73%
- 经济 92.17%
- 中国 88.67%
- 说 87.76%
- 国际 87.08%
- 发展 86.22%

The exact lexical identities of the high-survival content words are news-domain dependent. The useful signal is the repeated contrast between relation-realization/scaffolding forms and central topical/event content.

### Independent CSS validation
CSS carries human operation labels. In the 766 pairs:
- 212 were tagged “删除信息” (information deletion).
- These pairs had mean target/source token ratio **0.817**.
- **92.45%** of them were shorter than the source.
- Pairs without that tag had mean ratio **1.003**, and 30.14% were shorter.

Thus length-based compression strata track the human-annotated deletion operation strongly enough to serve as a first quantitative proxy for hierarchical shortening.

CSS also confirms that Chinese simplification is a mixture of transformations rather than pure deletion: in the pair-level data examined here, lexical replacement, sentence rewriting, information deletion and sentence splitting co-occur.

### Relation to school “缩句”
Chinese school pedagogy describes 缩句 as repeatedly removing “枝叶” such as 定语、状语、补语 while retaining a sentence “主干”, commonly expressed as 主语—谓语—宾语 or related two/three-part frames. That pedagogical operation is more syntactically aggressive and controlled than natural text simplification.

The empirical simplification data show a compatible but more graded pattern: contextual/detail material and relation-realization scaffolding are shed early; the lexical/event core is preferentially retained; deeper compression progressively enters the core itself.

### Evidence boundary and current hypothesis
The present evidence supports a **hierarchical peeling structure** in natural human Chinese simplification and supports treating many surface words as realizations/modifiers around a smaller relational/event core.

The direct “2–3 degrees of freedom” test is naturally formulated at the next representation level: for every compression layer, count surviving semantic arguments and dependency-core relations (e.g., subject, predicate/root, object/complement), then ask whether sentence width stabilizes around 2–3 local participant/relation slots while complexity grows mainly by recursive composition.

This gives a testable distinction:
- **width hypothesis**: local relational units remain low-arity;
- **depth hypothesis**: linguistic complexity is produced mainly by recursive composition/repeated operators rather than ever-increasing local arity.

### References
- Chong et al. (2024), *MCTS: A Multi-Reference Chinese Text Simplification Dataset*, LREC-COLING 2024.
- Yang, Sun & Wan (2023), *A New Dataset and Empirical Study for Sentence Simplification in Chinese*, ACL 2023.
- Liu & Lee (2024), *CSSWiki: A Chinese Sentence Simplification Dataset with Linguistic and Content Operations*, LREC-COLING 2024.
- Universal Dependencies, Chinese GSDSimp treebank, CC BY-SA 4.0.
