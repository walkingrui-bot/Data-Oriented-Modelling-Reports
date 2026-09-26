# ORDER-COT-CAUSAL-001

## Design
Eight autoregressive GRU models (12,846 parameters) shared exactly the same initialization, 128 training sequences, optimizer, learning rate, number of epochs, and update count.
The baseline training-group order was 0-1-2-3-4-5-6-7.
Seven matched intervention models each swapped exactly one adjacent pair, and changed nothing else.

All eight models had identical naked endpoint performance: 8/16. Their greedy predictions on all 16 naked probes were all zeros.

Probe: A=0, B=1, C=1, D=0; correct answer 0.
A fixed valid 24-token CoT trajectory was replayed token by token. At every k the model was cold-started from the original prompt plus exactly the first k CoT tokens, then generated a complete continuation.
The language trajectory itself was never edited between models. The causal intervention was training order.

## Main result
Local training-order swaps produced localized but nonzero changes in the conditional complete-answer response surface despite identical endpoint behavior.

### Adjacent-order intervention summary
| order_intervention   |   mean_answer_JS_bits |   max_answer_JS_bits |   answer_disagreement_points |   mean_completion_edit |   max_completion_edit |   peak_k |
|:---------------------|----------------------:|---------------------:|-----------------------------:|-----------------------:|----------------------:|---------:|
| swap23               |            0.12515    |            0.5       |                           20 |              0.367818  |              0.5      |       12 |
| swap56               |            0.0441177  |            0.100824  |                           20 |              0.268287  |              0.5      |       18 |
| swap45               |            0.0374029  |            0.115231  |                            0 |              0.178469  |              0.3      |        4 |
| swap01               |            0.0327176  |            0.5       |                            0 |              0.123404  |              0.222222 |        6 |
| swap12               |            0.0311027  |            0.5       |                            0 |              0.113799  |              0.3      |       14 |
| swap67               |            0.00260347 |            0.0104958 |                            0 |              0.0262657 |              0.173913 |        0 |
| swap34               |            0.0285121  |            0.5       |                            0 |              0.0235645 |              0.166667 |       18 |

Interpretation: each row is a controlled order intervention. `completion_edit` measures the change in the complete greedy continuation relative to the baseline at identical CoT prefixes. `answer_JS_bits` measures sampled final-answer distribution change. Agreement of a final answer at any k is treated only as output agreement, never as trajectory merging.

## Files
- ORDER_COT_CAUSAL_endpoint.csv
- ORDER_COT_CAUSAL_trace.csv
- ORDER_COT_CAUSAL_effects.csv
- ORDER_COT_CAUSAL_summary.csv
