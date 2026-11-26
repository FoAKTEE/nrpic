# What G2 of B-emd-gw still lacks (batch 23, 2026-11-25 19:00 PST)

Met: criterion (a) (FLRW particle run sub-percent and converging in mesh 16-128 and particle
number 1-27 per cell), a first full-GR kinetic run, the population box to a = 143 in two gauges,
constraint norms against time, a slice mosaic with zoom boxes, the verification-ladder schematic,
failed runs on record, the reproducibility list (C6), the G2 schematics (C16); batch 23: the
particle leg to a = 141 (Q1 constraint part holds, P8C1-2 hold), the shifted 0.028 box to a = 141
(S1 holds), halo masses against the Newtonian mode with equal GR particle masses (N2e, GN1e hold;
population/JOURNAL 2026-11-25 18:51).

Lacking, item by item of CHECKLIST.md, with the queue entry or processor work that serves it:

| Item | What is missing | Served by |
|---|---|---|
| C1 code paths pass their tests | (i) shearing-dust L2 converged in the mesh; (ii) the zero-shift slice fails at 256^3 (M1 refuted, a = 102): the track's measure must pass in the shifted gauge at the second mesh | (i) none yet: an amplitude without stream crossing at N_y = 64, 128, 256, designed first; (ii) q0060 `pop_s014_gr256_gd` (GM1) |
| C2 three-way convergence | mesh leg in the gauge the track reads (Gamma driver, 256^3); M2, M3 of the zero-shift 256^3 run to a = 100 (analysis running) | q0060 (GM1-GM4); analysis B-20261126-022356-52c2460 (running, M2-M3) |
| C3 constraints behave | Hr_mean falls only 1.1-1.4 times from 128^3 to 256^3 with zero shift (M4 fails where reachable); Mr_mean is set by particles per cell (Q1: 2.9 times smaller with 8 per cell); the shifted gauge at a second mesh not yet run | q0060 (GM4) |
| C5 verification report | waits for C1-C3 | writing, after q0060 |
| C9 multi-code row | S2, S3 (amplitude scaling in full GR, shifted gauge; analysis B-20261126-022403-82f6e69 running); the strain comparison with the particles' estimate with equal masses (A1-A3, GD3 particle parts); a mass by proper distance (R23) | running analysis; processor work |
| C11 convergence figures | the mesh figure in the shifted gauge; the particle-number figure at late times (Q1 high-k part: analysis B-20261126-022838-27fab1b running) | q0060; running analysis, then `compare_legs.py` |
| C14 package documents | report regenerated after the runs | writing |
| C15 one script per figure | analyze_b.py, analyze_f.py, analyze_gr.py, analyze.py draw several figures each (batch 23 added fig_leg_histories.py and judge_s028gd.py, one figure each) | rewriting (no card) |
| C17 working note | G2 section updated in batch 23 (equal-mass masses, the legs); checker not rerun this session; abstract and summary for G2 after q0060 | writing |
| C18 verifier | a fresh-context verifier recomputing ledger Table VIII and the G2 numbers | after C17 |

Failures on record that need no further run: X3 (setup error), the time part of GD1 and of N1p,
the particle leg's chain cut at a = 94.8; batch 21: N4 as written (cause found: estimator), GN2
after a = 36, NB1, VC1 second part, VC2 side statements, the defective first band run; batch 23:
M1 (the 256^3 zero-shift run stops at a = 102, run B-20261125-093500-242d3a3 closed as failed),
M4 in its reachable part, GN1 of batch 21 withdrawn (judged with the rest-mass weight; GN1e holds
with equal masses), the slip a' = 4a in S2/S3 of batch 17 (judged at the same stage, a' = 2a).

G2 is not complete. No ruling of the orchestrator is needed; the open items wait for q0060 and
for the three running analyses.
