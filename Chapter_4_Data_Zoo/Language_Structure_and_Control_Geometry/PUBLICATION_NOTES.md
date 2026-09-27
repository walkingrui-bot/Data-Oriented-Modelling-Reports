# Publication notes

The English report preserves the scientific results, numerical tables, discussions, interpretations and all source images. Reader guidance and the annotations below are additions to help interpret the supplied record.

## Dependency descriptor dimensionality

DEPENDENCY-ORDER-007 describes a seven-coordinate sentence-organization descriptor but reports an eight-dimensional PCA neighborhood result. The same entry appears in the recovered `geometry_summary.csv`, `statistical_summary.json` and calculation record. An eight-component PCA projection is incompatible with a strictly seven-coordinate input as described. The recovered artifacts do not provide the feature matrix needed to establish which description is wrong. The original values are preserved; the 8D neighborhood claim is flagged as unresolved.

## Shuffled edge message counts

RELATIONAL-ROUTER-008 states that the shuffled-edge control preserves relation-message count. The recovered script instead creates one shuffled pair for every predicate after the first, and creates hierarchical pairs only for predicates with a measured predicate ancestor. These rules can yield different pair counts. The 49-coordinate output interface is matched; equality of message counts is not established by those rules alone. This distinction is annotated beside the retained source interpretation.

## Engineering validation scope

The router is supplied with dependency annotations. Its targets are organization statistics derived from the same trees, and the adaptive gate uses observed predicate count and nesting. It tests structural encoding and reconstruction, with a small consistent reported advantage for the hierarchical interface. It does not constitute an end-to-end language-generation benchmark. The adaptive variant retains both fitted heads, so sparse activation is not by itself a demonstrated reduction in total model storage or deployment cost.

## Evidence availability

Fifteen of nineteen topical studies have recovered independent archives. Four have their original report results, table transcriptions and images only. Code coverage varies among recovered studies. The evidence index records the distinction rather than filling the gaps with reconstructed or newly invented artifacts.
