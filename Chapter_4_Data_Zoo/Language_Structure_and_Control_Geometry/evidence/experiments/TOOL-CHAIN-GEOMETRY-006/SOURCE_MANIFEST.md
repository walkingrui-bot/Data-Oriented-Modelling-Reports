# Source manifest — TOOL-CHAIN-GEOMETRY-006

## BFCL V4 primary data

Repository: https://github.com/HuanzhiMao/BFCL-Result
Snapshot folder: `2025-12-16/score/`

Primary aggregate files:
- https://raw.githubusercontent.com/HuanzhiMao/BFCL-Result/main/2025-12-16/score/data_overall.csv
- https://raw.githubusercontent.com/HuanzhiMao/BFCL-Result/main/2025-12-16/score/data_multi_turn.csv
- https://raw.githubusercontent.com/HuanzhiMao/BFCL-Result/main/2025-12-16/score/data_agentic.csv
- https://raw.githubusercontent.com/HuanzhiMao/BFCL-Result/main/2025-12-16/score/data_non_live.csv

Raw evaluator files parsed in the failure-anatomy assay:
- `2025-12-16/score/claude-opus-4-5-20251101-FC/multi_turn/BFCL_v4_multi_turn_base_score.json`
- `2025-12-16/score/Salesforce_Llama-xLAM-2-70b-fc-r/multi_turn/BFCL_v4_multi_turn_base_score.json`
- `2025-12-16/score/glm-4.6-FC/multi_turn/BFCL_v4_multi_turn_base_score.json`

BFCL leaderboard/evaluation documentation: https://gorilla.cs.berkeley.edu/leaderboard

## Current real-environment comparison

Tau3 Banking leaderboard: https://taubench.com/tau3/leaderboard/banking

## Tool-protocol documentation used in the discussion

OpenAI:
- https://developers.openai.com/api/docs/guides/function-calling

Google Gemini:
- https://ai.google.dev/gemini-api/docs/function-calling
- https://ai.google.dev/gemini-api/docs/thought-signatures

Anthropic Claude:
- https://docs.anthropic.com/en/docs/agents-and-tools/tool-use/implement-tool-use
- https://docs.anthropic.com/en/docs/agents-and-tools/tool-use/overview

## Specialized trajectory-training context

Salesforce xLAM-2-70B-FC-R model card:
- https://huggingface.co/Salesforce/Llama-xLAM-2-70b-fc-r

APIGen-MT / xLAM multi-turn work:
- https://arxiv.org/abs/2504.03601

## Evidence boundary

The benchmark files directly support observed accuracy, perturbation, pairing, correlation and evaluator-error results. Provider documentation supports statements about public tool-call contracts. Neither source establishes proprietary hidden model internals; architecture-level causes therefore remain hypotheses for controlled follow-up.
