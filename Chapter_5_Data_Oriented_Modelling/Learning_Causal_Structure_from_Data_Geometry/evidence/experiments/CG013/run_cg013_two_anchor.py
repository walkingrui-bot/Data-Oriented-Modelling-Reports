#!/usr/bin/env python3
"""
CG-013 Two-Anchor / Few-Shot Chart Calibration

Small-data protocol:
- Reuse exactly the 10 real cross-source Tuebingen pairs from CG-012.
- Use the zero-shot Sachs child-texture margin from CG-012 as the uncalibrated
  direction score.
- Compute direction-free geometry for each external pair.
- A known-direction anchor tells whether the Sachs texture should be kept (+)
  or flipped (-) in that anchor.
- Select the two nearest anchors using direction-free geometry only.
- Primary selective rule: only bootstrap-stable anchors are eligible, and a
  direction is called only when the two nearest stable anchors agree.
- Controls: one-anchor, point-anchor, distance-weighted, random stable
  two-anchor consensus, and pre-specified geometry-block ablations.

No new large dataset is introduced.
"""
print(__doc__)
