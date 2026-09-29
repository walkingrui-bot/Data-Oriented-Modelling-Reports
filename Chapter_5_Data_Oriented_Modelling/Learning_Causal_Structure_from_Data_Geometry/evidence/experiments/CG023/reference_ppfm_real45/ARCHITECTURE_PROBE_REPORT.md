# PPFM ARCHITECTURE PROBE — REAL45

Date: 2026-09-27
Status: completed small real-data architecture probe

## Scope
This is a local architecture probe using the archived early PPFM real corpus, not the current 220-task PPFM-020 corpus. It uses 45 of the 48 archived real tasks from Breast Cancer Wisconsin, sklearn Diabetes, and RAND HIE. Three tasks were excluded because the conditioning variable had only four distinct values, insufficient for the fixed 4-context -> fifth-context design; no artificial strata were created.

For every task, independently bootstrapped real observations form five empirical conditioning contexts. Four 24D context tokens are supplied and the model predicts the fifth context's nine-point response field. Train/test episode banks are generated with separate fixed seeds. All architectures receive identical episodes and 900 updates; two seeds are run per architecture.

## Main result

| Architecture | Parameters | Mean test MSE | vs GRU | Task wins vs GRU |
|---|---:|---:|---:|---:|
| Context Attention | 253,449 | 0.041722 | -17.43% | 37/45 |
| Dual Path (GRU + direct evidence) | 626,985 | 0.047795 | -5.41% | 30/45 |
| GRU baseline | 400,457 | 0.050529 | reference | — |

The lightweight attention model improves all three real-data families relative to GRU: Breast Cancer ~18.68%, Diabetes ~18.36%, RAND HIE ~13.79%. It also uses ~36.71% fewer parameters than the GRU baseline.

## Structural stress test
The same trained models were re-evaluated after changing only the order of the four context tokens. Each token retains its own measured context coordinate, so permutation changes presentation order but not the evidence set.

| Architecture | Base MSE | Random permutation | Relative change | Reversed order | Relative change |
|---|---:|---:|---:|---:|---:|
| Context Attention | 0.041722 | 0.041722 | 0.0% | 0.041722 | 0.0% |
| Dual Path | 0.047795 | 0.108041 | +126.10% | 0.161928 | +238.72% |
| GRU | 0.050529 | 0.166503 | +229.27% | 0.340244 | +572.02% |

## Interpretation
The measured gain is consistent with an architecture/data-structure match: these context observations behave as coordinate-bearing evidence elements whose arbitrary presentation order should not define meaning. The position-free attention model preserves that symmetry exactly in this probe and simultaneously lowers test error. The dual path partly improves prediction but retains the recurrent order sensitivity.

This supports testing context-attention in the current PPFM line. It does not establish that attention will dominate on the current 220-task corpus, survival/history interfaces, or future native temporal structures; those require direct current-corpus training.

## Files
- `architecture_summary.csv`: seed-aggregated main results
- `per_task_seedmean.csv`: seed-averaged results for all 45 tasks
- `permutation_stress.csv`: order perturbation results
- `probe_spec.json`: fixed probe definition and excluded tasks
- `ppfm_arch_probe_single.py`: executable probe source
- `*.pt`: trained probe checkpoints
