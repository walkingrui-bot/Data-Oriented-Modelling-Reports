# TOOL-CHAIN-GEOMETRY-006E pilot diagnostics

Two end-to-end autoregressive policies were executed before the controlled transfer. They are retained as design diagnostics and are not pooled into the formal 2×2 factorial.

- End-to-end AR v1: 825 held-out oracle-prefix decisions; exact action 22.18%; JSON parse 100%; schema validity 100%. Formal 450-task/1,800-trajectory scan yielded 0.67% final-state accuracy in each cell and mean first divergence ≈1.01 steps. This establishes a syntax/strategy dissociation under the first training objective.
- Semantic-weighted GRU epoch-1 diagnostic: 543 held-out oracle-prefix decisions; exact action 19.15%; JSON parse 53.59%; schema validity 35.36%. Semantic weighting increased competition among output slots and motivated isolating action serialization from planner learning.

The formal 006E construction therefore freezes the validated 006D planner/event reader and changes only the action serialization surface.
