# RISKS of F-hills

Updated 2026-11-15 by the lead. Evidence and run ids: `stage/G0/SCOPING.md`, `JOURNAL.md`.

| Risk | Likelihood | Effect | Watch | Response |
|---|---|---|---|---|
| R1 compute: G2 (about 120 card-hours) and G3 (about 500) exceed the 40 of decision 0006; G1 fits with no margin | certain | scan lines and convergence not done | allotment answer from orch/user | request filed; q = 4 for convergence and the first scan line; object (b) passages are 3-10 times cheaper |
| R2 q = 10 convergence does not fit one card (m/16: 2654-4544 MeshBlocks; about 3000 slots; no MPI) | certain on the present build | G2 at q = 10 impossible | core's answer (two cards or 32^3 blocks) | convergence at q = 4; request to core |
| R3 core capability not released (`core/multi-puncture` not on main, not in CLAUDE.md) | medium | G1 runs cannot start | core and orch replies | runs fully specified (stage/G1/STATUS.md) so they start the day it lands |
| R4 a member plunges into the heavy hole (geodesic reference: 94 percent of phases at r_p = 8 M) | high | a 20:1 merger at m/8 inside the passage; finder and refinement must follow it | P1 trackers and horizons near t = 80-120 | heavy finder follows the merged horizon; request a pairwise common-horizon trigger; restart files every 5 M |
| R5 the two references disagree in kind at q = 10 (HRNA holds the hole fixed; Newton has no plunge) | certain | neither is a truth for the NR comparison | V6/V7 | report NR against both; restart both from the NR state at t = 60; use q -> large limits only as checks |
| R6 member gauge (shift_eta = 2 gives eta m = 0.1) and tracker lag (0.48-0.61 of P/M_ADM over 10-40 M for eta m = 2, core) | medium | coordinate trajectories and binding energies biased for tens of M | R4 run | calibrate f(t); gauge-free observables (asymptotic speeds, horizon masses, energy balance) |
| R7 approximate (superposed Bowen-York) data change the outcome; junk does not converge (1004.1353 Punc_N.tex:185-194, 1238-1261) | medium | outcome near boundaries data-dependent | R0, R2; horizon masses vs closed form | decision rule of three_punctures PLAN section 5; constraint solve on the mesh (decision 0010 item 4) before G3 |
| R8 chaos near outcome boundaries (2505.03934) | high near edges | single runs not representative | phase windows in both references | choose phases inside robust windows; distributions over phase at G3 |
| R9 newton3 energies at finite q not conserved (V5b) | certain until fixed | wrong Newtonian energies at q <= 100 (classes unaffected away from E = 0) | - | barycentric definition; rerun finiteq, P3, three_punctures scans (next wave) |
| R10 m/8 is a scouting resolution (core: horizon masses scatter by 1 percent in the first 2.5 M) | high | outcome near boundaries resolution-dependent | G2 triple at q = 4 | report boundaries as intervals |
| R11 object (b) clumps must be mildly relativistic (m/R > 0.044 at a_b = 30 r_gb; Roche factor unverified) and must not relax during about 200 M | medium | (b) needs larger a_b or more particles | Track C models; G2 relaxation test | request to C-sidm; a_b = 60 r_gb fallback (0.022) |
| R12 competition: RIT plans up to 128:1:1 (2406.11985 TBH3.tex:707-711); BAM scatters N black holes (2505.03934) | medium | novelty window short for (a) | citation queries before each gate | (b) is the wider novelty; move it forward (proposal to orch) |
| R13 novelty verdict and baselines not checked by a second agent | - | gate review may reject | orch | request filed |
