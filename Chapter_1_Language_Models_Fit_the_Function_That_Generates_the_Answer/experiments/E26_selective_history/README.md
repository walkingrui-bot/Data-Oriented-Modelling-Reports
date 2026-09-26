# E26 Selective history attention and distributed state

[Experiment index](../README.md)

Relevant/obsolete/other TV was 0.9969/0.0011/0.0010 for GRU, 0.9824/0.0047/0.0061 for SSM and 0.9990/0.0003/0.0001 for Transformer. All sequence models correctly flipped after order swaps; the bag model achieved approximately 71.1% ordinarily and 50% averaged over pairs. Top attention located the relevant record in 90.61%, versus 100% for top intervention effect; high-attention/low-effect rate was 16.17%. Round 3 query-only/evidence-only/full-layer donor-rule accuracy was 22.75/37.58/99.33%, with TV 0.7654/0.6120/7.43×10⁻⁹.

## Method

Round 2 used 12 binary events across three channels, querying the latest value of one channel. Three architectures each used three seeds. Interventions flipped relevant, obsolete same-channel or other-channel values, or swapped the last two differing relevant events, with a bag baseline. Round 3 separately trained three two-layer, 16-dimensional, two-head Transformers on three modular-arithmetic evidence pairs, transplanted local or full-layer state, and trained direct-answer MLP/set controls.

## Interpretation

Historical influence measures the output change caused by a value flip. Attention and intervention produce different rankings of that influence. Full-layer copying supplies sufficient state for deterministic downstream computation; the local transfers show how its effect is distributed. Separately trained one-shot MLPs achieved 100% on unseen evidence-x patterns across three seeds. An eight-evidence, 30%-corruption set model averaged 97.17% versus a 97.64% reference, supporting single-forward-pass rule processing.

## Artifacts and reproduction

**Protocols tables and figures**

Two evidence families jointly cover history interventions, attention comparisons, state transplantation and one-shot formation. The protocols and per-seed tables are retained.

Paths below are relative to the repository root. The complete file inventory is in [artifacts.csv](artifacts.csv).

| File | Role | Locator |
| --- | --- | --- |
| [evidence/X2_selective_history/PROTOCOL.md](../../evidence/X2_selective_history/PROTOCOL.md) | method_or_report |  |
| [evidence/X2_selective_history/01_history_voice_interventions.csv](../../evidence/X2_selective_history/01_history_voice_interventions.csv) | result_or_record |  |
| [evidence/X2_selective_history/02_same_material_different_order.csv](../../evidence/X2_selective_history/02_same_material_different_order.csv) | result_or_record |  |
| [evidence/X2_selective_history/03_attention_vs_causal_voice.csv](../../evidence/X2_selective_history/03_attention_vs_causal_voice.csv) | result_or_record |  |
| [evidence/X3_state_transplant/PROTOCOL.md](../../evidence/X3_state_transplant/PROTOCOL.md) | method_or_report |  |
| [evidence/X3_state_transplant/01_forged_history_injection.csv](../../evidence/X3_state_transplant/01_forged_history_injection.csv) | result_or_record |  |
| [evidence/X3_state_transplant/02_one_shot_rule_formation.csv](../../evidence/X3_state_transplant/02_one_shot_rule_formation.csv) | result_or_record |  |

## Related hypotheses

H08, H09, H10, H12, H20

