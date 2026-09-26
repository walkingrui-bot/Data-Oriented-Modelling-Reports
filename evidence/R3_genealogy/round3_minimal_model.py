"""
Minimal CE2G-style transition-genealogy sketch.

State:
  S_t : continuation geometry
  M_t : local history-produced rewrite phenotype

Realized transition a->b:
  G_t = norm(phi_ab + gamma * M_t(a))
  G_t reweights descendant transitions b->*
  G_t is inherited into M_(t+1)(b)

Writes are bounded by a CE2G-style budget.

This file records the minimal model form; the archived CSVs contain the
numerical outputs and parameter sweeps used in ROUND3_REPORT.md.
"""
