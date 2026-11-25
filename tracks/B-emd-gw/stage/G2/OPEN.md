# What G2 of B-emd-gw still lacks (batch 21, 2026-11-25 09:20 PST)

Met: criterion (a) (FLRW particle run sub-percent and converging in mesh 16-128 and particle
number 1-27 per cell), a first full-GR kinetic run, the population box to a = 143 in two gauges,
constraint norms against time, a slice mosaic with zoom boxes, the verification-ladder schematic,
failed runs on record; batch 21: the reproducibility list (C6, `REPRODUCE.md`), the G2 schematics
on release core-v0.7 (C16), the same-particle Newtonian comparison in both gauges (part of C9).

Lacking, item by item of CHECKLIST.md, with the queue entry or processor work that serves it:

| Item | What is missing | Served by |
|---|---|---|
| C1 code paths pass their tests | (i) the 0.028 box past a = 36 in the shifted gauge; (ii) shearing-dust L2 converged in the mesh | (i) q0044 `pop_s028_gd2` (S1-S3); (ii) none yet: an amplitude without stream crossing at N_y = 64, 128, 256, designed first |
| C2 three-way convergence | mesh leg 256^3; particle leg past a = 95; the gauge at a second mesh | q0007 `pop_s014_gr256` (M1-M4); q0042 `pop_s014_gr_p8_cont` (P8C1-2, Q1); gauge at a second mesh: no entry (needs a decision: 256^3 shifted) |
| C3 constraints behave | late growth of Hr_mean, Mr_mean not shown to fall with mesh or particle number | q0007 (M4), q0042 (Q1), q0044 (S1) |
| C5 verification report | waits for C1-C3, C9 | writing, after the runs |
| C9 multi-code row | amplitude scaling in full GR past a = 30; the GR-particle quasi-static estimator rerun without the rest-mass weight (analyze_gr.py, about an hour of processors, prediction first); the gauge dependence of FoF masses (a mass by proper distance) | q0044 (S2, S3); processor work (next session) |
| C11 convergence figures | particle-number and mesh figures of the population box; the gauge figure at one mesh exists | q0042, q0007 |
| C14 package documents | REVIEW of batch 21 exists; the report regenerated after the runs | writing |
| C15 one script per figure | analyze_b.py, analyze_f.py, analyze_gr.py, analyze.py draw several figures each (the note's figures are one script each) | rewriting (no card) |
| C17 working note | G2 section exists (settled items and the queue entry per open item, checker passed with --compile); the C1-C3 results of the queued runs, abstract and summary for G2 | writing after the runs |
| C18 verifier | a fresh-context verifier recomputing ledger Table VIII and the G2 numbers | after C17 |

Failures on record that need no further run: X3 (setup error), the time part of GD1 and of N1p,
the particle leg's chain cut at a = 94.8; batch 21: N4 as written (cause found: estimator), GN1,
GN2 after a = 36, NB1, VC1 second part, VC2 side statements, the defective first band run.

G2 is not complete. No ruling of the orchestrator is needed to close an item as a failure on record.
