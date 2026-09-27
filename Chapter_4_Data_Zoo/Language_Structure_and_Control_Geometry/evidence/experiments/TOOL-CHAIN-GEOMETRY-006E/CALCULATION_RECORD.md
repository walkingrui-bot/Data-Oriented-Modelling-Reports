# TOOL-CHAIN-GEOMETRY-006E calculation record

Formal design: frozen final-006D event reader and planner; unconstrained neural token-autoregressive JSON emitter; exact same 3 × 200 held-out task panels and four provenance × normalization cells as 006D.

Emitter assay: 153 valid action tuples, JSON parse=1.000, schema-valid=1.000, semantic exact=1.000.

Formal trajectories: 600 tasks × 4 cells = 2,400. Final-state accuracies: P1_N1=0.8350; P1_N0=0.6900; P0_N1=0.7433; P0_N0=0.6767.

Paired factorial effects: provenance=5.25 pp; normalization=10.58 pp; interaction=7.83 pp. Bootstrap 95% intervals are stored in results.json.

Single-read: n=337, interaction=0.00 pp. Multi-read: n=263, interaction=17.87 pp.

Paired outcome agreement with 006D=0.998333; mean accuracy delta=0.167 pp. Four of 2,400 task-cell outcomes changed, all from 006D failure to 006E success, all SWAP cases in raw/non-normalized cells.

006D schema-error trajectory rates and 006E planner→emitter projection rates are identical by cell: P1_N1=5.67%, P1_N0=15.17%, P0_N1=11.50%, P0_N0=14.83%. The legal-action emitter assay is 153/153 exact, so these projection events arise when the frozen planner proposes an out-of-schema tuple.
