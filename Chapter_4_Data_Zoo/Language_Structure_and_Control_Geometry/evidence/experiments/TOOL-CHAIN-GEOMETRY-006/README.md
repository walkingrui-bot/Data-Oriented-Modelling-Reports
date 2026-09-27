# TOOL-CHAIN-GEOMETRY-006 Evidence Package

Date: 2026-09-27

This bundle contains the executed derived statistics and figures used in Chapter 3 - The Language Edition v0.5 for TOOL-CHAIN-GEOMETRY-006.

## Computation rule

Every quantitative statement in this experiment was computed from retrieved benchmark data. No uncomputed relationship is promoted to an empirical result. The report distinguishes direct measurements from interpretation and from public interface documentation.

## Primary data

The primary benchmark snapshot is the BFCL V4 result repository, 2025-12-16 score snapshot:

- `2025-12-16/score/data_overall.csv` — 109 model/config rows used for cross-axis correlations and FC-vs-Prompt pairing.
- `2025-12-16/score/data_multi_turn.csv` — multi-turn category table.
- `2025-12-16/score/data_agentic.csv` — web-search and memory categories.
- `2025-12-16/score/data_non_live.csv` — single-turn AST categories.
- Three raw 200-episode `multi_turn_base_score.json` evaluator files were parsed for Claude Opus 4.5 FC, Salesforce xLAM-2-70B FC, and GLM-4.6 FC-thinking.

Exact source URLs and paths are in `SOURCE_MANIFEST.md`.

## Included derived evidence

- `derived/tool_chain_006_summary.json` — central recomputed statistics.
- `derived/selected_model_profiles.csv` — selected model/config profile table used in Figure 4.6.
- `derived/multiturn_perturbation_drops.csv` — calculated Base-minus-condition drops.
- `derived/paired_fc_vs_prompt_multiturn.csv` — 25 matched FC/Prompt multi-turn deltas.
- `derived/base_error_type_counts.csv` — evaluator error counts from 600 raw episodes.
- `figures/fig_4_6_tool_axis_profiles.png`
- `figures/fig_4_7_multiturn_perturbation_drops.png`
- `figures/fig_4_8_fc_prompt_multiturn_delta.png`
- `figures/fig_4_9_base_error_composition.png`
- `recompute_tool_chain_006.py` — recomputation script expecting the BFCL source files listed above.

## Headline computed results

- Spearman rho, N=109: non-live single-turn AST vs multi-turn = 0.452; non-live AST vs agentic mean = 0.239; multi-turn vs agentic mean = 0.620; web-search vs memory = 0.793.
- Among 57 configurations with multi-turn base >=20%, mean drops were 11.95 pp for missing function, 13.48 pp for missing parameter, and 8.30 pp for long context.
- Among 25 matched FC/Prompt model-family pairs, FC-minus-Prompt multi-turn delta had mean +12.45 pp, median +7.00 pp, 21 positive and 4 negative pairs; range -47.50 to +59.75 pp.
- In 600 raw multi-turn-base episodes from three strong configurations, 124 episodes failed: 79 instance-state mismatch (63.7%), 30 execution-response mismatch (24.2%), and 15 empty-turn response (12.1%).

These values describe the specified benchmark snapshot and evaluation protocol.
