# What G2 of B-emd-gw still lacks (batch 17, 2026-11-25 04:00 PST)

Met: criterion (a) (FLRW particle run sub-percent and converging in mesh 16-128 and particle
number 1-27 per cell; start-step floor tested at 128 cells, J4), a first full-GR kinetic run (and
the population box to a = 143, now in two gauges), constraint norms against time, a slice mosaic
with zoom boxes, the verification-ladder schematic, failed runs on record.

Lacking, item by item of CHECKLIST.md, with the queue entry or processor run that serves it:

| Item | What is missing | Served by |
|---|---|---|
| C1 code paths pass their tests | (i) the 0.028 box past a = 30.7: the zero-shift stop is the gauge (X0, X1 repeat it, X2 with a Gamma-driver shift passes to a = 36; population/JOURNAL 2026-11-25 04:00), the shifted run to a = 143 is not run; (ii) shearing-dust L2 converged in the mesh: no entry (needs an amplitude without stream crossing at three meshes, designed first; HANDOFF) | (i) q0044 `pop_s028_gd2` (S1-S3); (ii) none yet |
| C2 three-way convergence | mesh leg of the population box (256^3); particle leg past a = 95 (cut by the chain cap); gauge leg: one shift at one mesh (q0004, judged GD1-GD3), no second mesh in that gauge | q0007 `pop_s014_gr256` (in Slurm, job 5283, M1-M4); q0042 `pop_s014_gr_p8_cont` (P8C1-P8C2, then Q1); gauge at a second mesh: no entry (would need 256^3 in the shifted gauge, about 5 card-h: decision for the next lead) |
| C3 constraints behave | growth of Hr_mean and Mr_mean after halo formation, not shown to fall with the mesh or the particle number; larger in the shifted gauge (X2: Hr_mean 2.1e-2 at a = 36) | q0007 (M4), q0042 (Q1), q0044 (S1) |
| C5 verification report | waits for C1-C3, C9 | writing, after the runs |
| C6 reproducibility package | package-level list of commands, decks, executables and run ids | writing (no card) |
| C9 multi-code row | the same-particle Newtonian reference at 128^3 has run (B-20261124-172958-fc4a2cf, -73b0662, exit 0); its analysis and the halo-by-halo comparison (N2-N4) are not done; the amplitude scaling in full GR past a = 30 | processor analysis `analyze.py` + `compare_newton.py` (next session); q0044 (S2, S3) |
| C11 convergence figures | particle-number and mesh figures of the population box; the gauge figure exists for one mesh (`population/figs/pop_legs.png`) | q0042, q0007 |
| C14 package documents | REVIEW of this batch exists; the report regenerated after the runs | writing |
| C15 one script per figure | analyze_b.py, analyze_f.py and analyze_gr.py draw several figures each | rewriting (no card) |
| C16 schematics | track architecture (exists / to be ported / new) and the gate timeline for G2 | writing (no card) |
| C17 working note | G2 sections with the manuscript checker --compile | writing (no card) |
| C18 verifier | a fresh-context verifier recomputing the Supplemental numbers | after C17 |

Failures on record that need no further run: X3 (setup error, restart refused `dt_lightspeed`),
the time part of GD1 (0.185 card-h against 0.2-0.5), of N1p (13 h per Newtonian run), the
particle leg's chain cut by the cap at a = 94.8.

No entry of this owner serves no gate item. No ruling of the orchestrator is needed to close an
item as a failure on record; G2 is not complete.
