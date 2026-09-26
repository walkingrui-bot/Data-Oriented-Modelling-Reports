# TOKEN OPERATOR OS — Engineer Manual

## Install
Unzip the artifact bundle. Requires Python 3 + NumPy only.

## 1. See available tokens
```bash
python TOKEN_OPERATOR_ATLAS_001_os.py list
```

## 2. Inspect a saved real state
```bash
python TOKEN_OPERATOR_ATLAS_001_os.py state --state-id 54
```

## 3. APPLY — execute one token operator
```bash
python TOKEN_OPERATOR_ATLAS_001_os.py apply B --state-id 54
```
Read:
- `h_out`: state after the token
- `delta`: exact runtime state movement
- `delta_norm`: movement magnitude

## 4. CARD — look up the token's global operator manual
```bash
python TOKEN_OPERATOR_ATLAS_001_os.py card B
```
Read:
- `shared_operator_coordinates`: six compact coordinates for the token's conditional operator signature
- `nearest_operators`: globally closest token functions over the 352-state bank
- `highest_order_effect_partners`: tokens whose order with this token changes state most
- `movement_stable_rank/top1/top3`: how many state-response directions the token uses
- `direction_consistency`: whether it tends to move states in one common direction
- `delta_norm_q05/median/q95`: normal operating range

## 5. COMPARE — compare two token functions at the same state
```bash
python TOKEN_OPERATOR_ATLAS_001_os.py compare B result --state-id 54
```
Read `output_distance`. Larger = more different state transformation at this state.

## 6. COMPOSE — execute an ordered token sequence
```bash
python TOKEN_OPERATOR_ATLAS_001_os.py compose "A,0,xor,B" --state-id 54
```
Read:
- `total_state_change`
- per-token `delta_norm`
- final `h_out`

## 7. ORDER — test whether order matters
```bash
python TOKEN_OPERATOR_ATLAS_001_os.py order B result --state-id 54
```
Read `state_distance`.
- near 0: the two orders are locally close
- large: order materially changes the resulting state

## 8. Use your own 10D state
Replace `--state-id` with:
```bash
--h "h1,h2,h3,h4,h5,h6,h7,h8,h9,h10"
```

## Files to use directly
- `TOKEN_OPERATOR_ATLAS_001_runtime.npz` — runtime
- `TOKEN_OPERATOR_ATLAS_001_token_operator_cards.csv` — spreadsheet/manual table
- `TOKEN_OPERATOR_ATLAS_001_operator_state_table.csv` — all token × saved-state transitions
- `TOKEN_OPERATOR_ATLAS_001_global_operator_distance_matrix.csv` — global function distances
- `TOKEN_OPERATOR_ATLAS_001_order_effect_matrix.csv` — pairwise order effects
- `TOKEN_OPERATOR_ATLAS_001_token_generator_coefficients.csv` — affine-summary operator coordinates
- `TOKEN_OPERATOR_ATLAS_001_conditional_operator_signature_coefficients.csv` — direct conditional signature coordinates

## Runtime calibration
This OS is reconstructed from the previously saved hidden-state/Jacobian telemetry because the original checkpoint was not present in the current artifact set.
- natural-transition MSE: 7.027e-07
- 95% absolute coordinate error: 0.001537
- median A-Jacobian cosine: 0.999844
- median B-Jacobian cosine: 0.999941
Use this bundle as the engineering diagnostic reconstruction of this model instance.
