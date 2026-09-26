# Round 2 protocol
Task: query-dependent latest-event memory.
History length: 12 events + one query.
Channels: 3; values: binary.
Target: value of the latest event from the queried channel.

Architectures: GRU, simplified SSM, one-layer causal Transformer, orderless bag baseline.
Seeds: 11, 22, 33.

Interventions:
1. flip latest relevant event;
2. flip older same-channel event;
3. flip other-channel event;
4. swap the last two queried-channel events while preserving the exact multiset.

Transformer-specific:
compare raw final-query attention weights against per-position causal effects measured by value-flip intervention.

Causal effect metric: total-variation distance between output distributions.
