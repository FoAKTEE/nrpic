# What G2 of B-emd-gw still lacks (batch 28, 2026-11-26 13:40 PST)

Met: criterion (a) (FLRW particle run sub-percent and converging in mesh 16-128 and particle
number 1-27 per cell), a first full-GR kinetic run, the population box to a = 143 in two gauges
and at two meshes in the gauge the track reads (q0060: GM1 holds), the particle leg to a = 141,
the shifted 0.028 box to a = 141 and its amplitude scaling against the 0.014 box (S1, S2, S3
hold), halo masses against the Newtonian mode with equal GR particle masses (N2e, GN1e hold),
constraint norms against time, a slice mosaic with zoom boxes, the verification-ladder schematic,
failed runs on record, the reproducibility list (C6), the G2 schematics (C16), the package
documents (C14), the multi-code row (C9).

Lacking, item by item of CHECKLIST.md:

| Item | State | What it waits for |
|---|---|---|
| C1 code paths pass their tests | FAIL as written, for the shearing-dust case L2 only (no mesh-converged number; each refinement moves away from CosmoGRaPH) | a ruling of the orchestrator (outbox 2026-11-26), or an amplitude without stream crossing at N_y = 64, 128, 256, designed and predicted first (processors and at most one card-hour) |
| C2 three-way convergence | OPEN | GM2, GM3: analysis B-20261126-212212-c54d979 (registered, running at the end of batch 28), then `compare_legs.py --base $S/B-20261125-115558-2ab4161/analysis_gr_gd.json --halo-base $S/B-20261126-022407-87e8803/analysis_gr_gd.json --leg m256gd:<its analysis_gr_m256gd.json>` |
| C3 constraints behave | FAIL as written for the mesh at one particle per cell (M4 and GM4 refuted: Hr_mean falls 1.1-1.4 times when the spacing halves, in both gauges); the constraints fall with particle number (Q1) | a ruling under decision 0039 item 2(c) (requested), or a mesh pair at a fixed number of particles per cell above one |
| C5 verification report | OPEN | C2, C17 |
| C11 convergence figures | OPEN: particle number and gauge exist; mesh in the shifted gauge missing | the GM comparison above (its pop_legs.png) |
| C15 one script per figure | OPEN | splitting analyze_b.py, analyze_f.py, analyze.py, analyze_gr.py into one script per figure over cached intermediates (no card) |
| C17 working note | OPEN | section VI with GM1-GM4, M2, M3, Q1, S2, S3 and ledger rows; abstract and summary for G2; check_manuscript.py --compile with /paper-writing |
| C18 verifier | OPEN | a fresh-context verifier after C17 (requested) |

Failures on record that need no further run: X3 (setup error), the time part of GD1 and of N1p,
the particle leg's chain cut at a = 94.8; batch 21: N4 as written (cause found: estimator), GN2
after a = 36, NB1, VC1 second part, VC2 side statements, the defective first band run; batch 23:
M1 (B-20261125-093500-242d3a3 closed failed), M4 in its reachable part, GN1 of batch 21 withdrawn,
the slip a' = 4a in S2/S3; batch 28: GM4 first part, M2 largest masses at a = 64-72, M3 first
part at a = 100 (1.214 against 1.2), Q1 high-k part.

G2 is not complete: C2 and C11 wait for a running processor analysis, C15 and C17 for writing,
C18 for a verifier; C1 and C3 are failures as written that need a ruling. No card run is needed.
