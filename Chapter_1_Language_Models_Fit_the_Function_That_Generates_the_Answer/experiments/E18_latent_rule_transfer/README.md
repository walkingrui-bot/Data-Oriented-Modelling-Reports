# E18 Transplanting executable state for a latent rule

[Experiment index](../README.md)

Accuracy at horizons 1–5 was 97%–100%. Transplanting all first-layer contextual evidence outputs changed predictions in 83.0% of cases; 51.2% applied the donor rule to the recipient start, and 10.8% emitted the donor’s own answer. Single-position transfer rates were 3.8%–19.3%, versus 51.0% for all evidence in the positional analysis. Restoring recipient K/V downstream reduced main operator transfer to 20.4%/26.0%. A separate upstream explicit-rule control used 1000 rows, 59 prefixes and 295 pairs: first-layer attention-readout transfer reached 84.1% donor targets, versus 0 for MLP transfer and 50.2% for one head. This is a separate sample from the latent-rule experiment.

## Method

Pilot 02 retained the three-layer, 64-dimensional, four-head model. The hidden rule was y=(x+b) mod 5, with two examples supplied. States were collected for 1500 episodes; 1484 baseline-correct episodes formed the pairing pool. The main operator test used 500 pairs differing in b and start, transplanting evidence states with the recipient query fixed. Positional decomposition and same-rule controls used separately defined 400-pair sets.

## Interpretation

Runtime state transfers rule-specific function. Same-rule replacement retained 70.5% correctness; different-rule replacement yielded 18.0% recipient correctness and 52.0% operator answers. Four dimensions are the algebraic maximum for five centered rule centroids. At scale 1.5, the rule direction increased operator probability by 0.150 versus 0.034 for a wrong direction. Transplanted evidence supplies a causal route through which downstream computation applies the donor rule.

## Artifacts and reproduction

**Code checkpoint and intervention outputs**

Read cotlatent.py and the paired transplant analyses with their saved JSONs. Use a working copy for original path adaptation. cotfreedom_upstream.py belongs to the P1 model lineage and imports cotstep; keep that dependency distinct from cotlatent.

Paths below are relative to the repository root. The complete file inventory is in [artifacts.csv](artifacts.csv).

| File | Role | Locator |
| --- | --- | --- |
| [evidence/P2_latent_rule/cotlatent_mechanism.py](../../evidence/P2_latent_rule/cotlatent_mechanism.py) | code |  |
| [evidence/P2_latent_rule/cotlatent_mechanism.json](../../evidence/P2_latent_rule/cotlatent_mechanism.json) | result_or_record |  |
| [evidence/P2_latent_rule/cotlatent_position.json](../../evidence/P2_latent_rule/cotlatent_position.json) | result_or_record |  |
| [evidence/P2_latent_rule/cotlatent_same_rule_control.json](../../evidence/P2_latent_rule/cotlatent_same_rule_control.json) | result_or_record |  |
| [evidence/P2_latent_rule/cotlatent_rule_direction.json](../../evidence/P2_latent_rule/cotlatent_rule_direction.json) | result_or_record |  |
| [evidence/P2_latent_rule/cotlatent.pt](../../evidence/P2_latent_rule/cotlatent.pt) | checkpoint |  |
| [evidence/P2_latent_rule/cotfreedom_upstream.json](../../evidence/P2_latent_rule/cotfreedom_upstream.json) | result_or_record |  |

## Related hypotheses

H11, H20

- C06: Pilot 02 uses a baseline-correct pool; distinguish 500-pair and 400-pair analyses.
- C07: Five centered centroids have algebraic rank at most four.
