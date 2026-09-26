# E31 Hard-mirror context


Final mean |p−0.5| was 0.2540 for self-feeding, 0.1022 for neutral blocks and 0.0195 for hard mirrors. Extreme fractions were 48.44%, 0% and 0%. The mirror reduced deviation by about 92.3% relative to self-feeding and 80.9% relative to neutral blocks. Within a round, deviation fell from 0.06595 after the self block to 0.01854 after the mirror block.

## Method

Use a four-layer causal Transformer with hidden size 32, four heads and a 31-token binary context to infer a Bernoulli parameter. The reference is known: p*=0.5. Add 16 tokens per round: 16 self-generated; eight self-generated plus eight neutral random; or eight self-generated with k ones plus a shuffled eight-token mirror containing 8−k ones. Run 64 independent trajectories per condition for 80 rounds.

## Final interpretation

Exactly complementary evidence offsets newly formed bias at the content input. The known center and exactly pairable binary world make the operation directly testable.

## Evidence files

| File | Contents |
| --- | --- |
| [REPORT.md](../../evidence/phase2/M0_content_mirror/REPORT.md) | protocol_or_report |
| [results.csv](../../evidence/phase2/M0_content_mirror/results.csv) | result_table |

[artifacts.csv](artifacts.csv) · [experiment.json](experiment.json)

Protocols, derived results and figures support inspection of methods and numbers. Archived reports retain original wording; this page and the Phase 2 findings provide the final interpretation. Training code and checkpoints can be added in a subsequent archive. Recompute summaries from the repository root with `python audit/recalculate_phase2.py`.

## Related claims

H20, H29
