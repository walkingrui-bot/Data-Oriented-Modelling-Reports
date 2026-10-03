# INTERNAL_COORDINATION_003 — Multilingual and Code Common Core

Experiment 003 tests whether six surface systems can converge on one scene-specific internal state without direct latent alignment. The six views are English, Chinese, Japanese, Spanish, Python and JavaScript descriptions of the same executable piecewise-affine function.

For each held-out semantic scene, the model produces six 16-dimensional internal states. Stacking them gives the experiment's central object, a **16 × 6 state matrix**. Reality Binding requires a state obtained from any source view to generate target views of the same semantic scene. No loss directly minimizes distances between the six internal columns.

## Main reported result

Across three independent initializations, Reality Binding achieved median cross-view semantic-token accuracy 98.24%, 100% cross-view scene retrieval in all 30 directed view pairs in every run, and median executable semantic equivalence 75.0% under free generation. The shuffled-correspondence control had median executable equivalence 0.0% and median scene retrieval 43.38%.

A naive syntax-dominated pilot produced a collapsed representation. The reported protocol therefore weights program-defining tokens more strongly while retaining full sequence generation. The identity-retrieval and executable audits are retained specifically to reject this kind of false common core.

## Structure

- `protocol.json` — fixed architecture, data split, optimization settings and exact run seeds.
- `code/model_and_data.py` — semantic simulator, six renderers, shared encoder/core/decoder, training and geometry metrics.
- `code/reproduce.py` — exact self → binding → shuffled protocol for runs 1–3; `--smoke` performs a short wiring check.
- `code/execution_audit.py` — parses free generations and tests functional equivalence on an independent x-grid.
- `results/` — per-run metrics, aggregate summaries, geometry matrices, gradient-pressure and phase-change records.
- `states/` — trained checkpoints for all three conditions and three initializations.
- `figures/` — figures used in the report.
- `report/` — standalone Experiment 003 report and updated Living Report v0.3.

## Reproduction

From the evidence-package root:

```bash
python code/reproduce.py --run 1 --out reproduced/run1
python code/reproduce.py --run 2 --out reproduced/run2
python code/reproduce.py --run 3 --out reproduced/run3
```

Requirements: Python 3, PyTorch, NumPy. Matplotlib is used only for report figures. The complete reported protocol is CPU-compatible.

## Audit boundary

The canonical simulator parameters define the controlled semantic world and are used for data construction and post-training audit. They are not supplied to the learned 16D state and no direct latent-state alignment target is used.
