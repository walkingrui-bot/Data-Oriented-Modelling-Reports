# Experimental protocol summary

1. **Frequency-preserving controls:** shuffle positions within each unit/window while preserving the exact token multiset.
2. **Leave-one-domain-out tests:** in cross-language work, train on other languages and test an entirely unseen language.
3. **Surface-anchor removal:** in program explanations, mask shared code identifiers/keywords before cross-language testing.
4. **Block shuffles:** preserve increasingly large local blocks to locate the structural horizon.
5. **Word-level sanity checks:** rerun alphabetic languages using real word tokens to quantify character/morphology contribution.
6. **Semantic invariance checks:** classical→modern Chinese uses fixed event/argument anchors; multilingual story relay locks event sequence; code↔language round-trips use executable tests rather than subjective semantic scoring.
7. **Human eye pilot:** separate three questions: launch/gate, target selection, and post-landing scanpath replay. Do not infer internal state from surface word recurrence alone.
8. **Style/author controls:** equal window lengths; content-word-only reruns; same-author cross-genre cases; same-source multi-translator cases.
9. **Evidence retention rule:** negative results and failed neural/learning proxies are preserved rather than silently discarded.
