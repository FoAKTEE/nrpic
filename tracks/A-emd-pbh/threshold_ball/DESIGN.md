# DESIGN of threshold_ball (A-emd-pbh, batch 5 of wave 3, 2026-11-21)

Aim: the first scan across a threshold of black-hole formation in the set-up that works (the
expanding ball with the nested static mesh of conv_ball), run unattended on the cards
(decision 0025 items 4, 5). Toward G2 (horizon formation against the exact solution at several
amplitudes, mesh convergence at the threshold) and the threshold machinery of G3.

## 1. What threshold, and why only this one [JUDGEMENT]

Family: data set 3 of conv_ball (compensated top hat, H R_b = 0.7, R1 = 0.65 R_b, R2 = 0.95 R_b,
M = 1, matter edge 4.25 M) with the core contrast delta_c as amplitude. The core is closed FLRW
for every delta_c > 0; all its shells crunch together, so the first trapped sphere is always the
core edge (R_i = 2.653 M) and a horizon always forms before the crunch (design run
A-20261121-202520-3164672: tau_AH < tau_c for every delta_c in 0.2-2). In pressureless spherical
collapse without dispersion there is therefore no "halted" branch: the only threshold is the
finite-duration one of scope/SCOPE.md section 3 (A_c(t_end): BH if the horizon forms by t_end,
NO-BH "late" if the core is still contracting at t_end). Re-expansion needs non-sphericity or
dispersion (the triaxial scan, after this one). The time measure is the invariant one of the exact
solution: tau_AH, the proper time of the core-edge shell when it is first trapped; the code's
counterpart is ddet of conv_ball (proper time of the tracked particles at the finder's radius at
first detection). The coordinate time of first detection is slicing-dependent (1.2-1.4 M after
tau_AH at delta_c = 1.5 in conv_ball) and is reported, not used for the outcome.

End time t_end = 45 M (11.6 initial ages t_i = 3.887 M). Exact events (data run
A-20261121-202812-cae4436, prep_summary.json):

| delta_c | core turnaround | tau_AH | crunch | m_AH | outcome at t_end = 45 |
|---|---|---|---|---|---|
| 1.0 | 6.157 | 15.386 | 16.201 | 0.54925 | BH |
| 0.7 | 10.094 | 23.405 | 24.075 | 0.46686 | BH |
| 0.5 | 15.925 | 35.160 | 35.738 | 0.41194 | BH |
| 0.45 | 18.361 | 40.054 | 40.610 | 0.39821 | BH |
| 0.42 | 20.156 | 43.656 | 44.199 | 0.38997 | BH |
| 0.40 | 21.531 | 46.415 | 46.950 | 0.38448 | NO-BH (late) |
| 0.35 | 25.803 | 54.980 | 55.492 | 0.37074 | NO-BH (late) |
| 0.20 | 55.568 | 114.574 | 115.023 | 0.32955 | NO-BH (late) |

Exact bracket A_c(45) in (0.40, 0.42] (ratio 1.05, below the 1.1 of SCOPE section 3); linear
interpolation of tau_AH gives A_c(45) = 0.410.

## 2. Members, meshes, executables

Decks: `decks/nest{16,32,64}_L32.athinput` = conv_ball's decks (commit 8a13936c) with
`<fastflow> diagnostics` declared; outer boundary 32 M because the envelope's matter edge
reaches about 26 M (areal) by t = 54 and 32 M near t = 76. Physics and gauge as conv_ball
(relaxed 1+log, lapse_leak 8; PCS clouds; excision below alpha 0.1). Command-line options of
every member: hmean_tol_0 = 1e30, diagnostics, find_every 8, finder from half of min(tau_AH, tlim),
field dumps at turnaround, tau_AH - 2, tau_AH, tau_AH + 4. Executable: release core-v0.6 card
build (`.work/build_gpu_v06/src/athena`) for the scan; conv_ball's C-R1.25 keeps core_gauge,
its series' executable. Processor smoke test of both decks with every option:
A-20261121-203211-6d3ce73 (exit 0; the first attempt A-20261121-203156-d094c56 failed because
the conv_ball decks do not declare `diagnostics`).

| order | member | mesh (finest) | tlim | card-h requested | model card-h |
|---|---|---|---|---|---|
| 1 | B-d0.42 | B (M/32), nestB 621464 | 51 | 2 | 0.6 |
| 2 | B-d0.40 | B | 54 | 2 | 0.6 |
| 3 | A-d0.42, A-d0.40 (one batch) | A (M/16), nestA 77704 | 51, 54 | 0.67 | 0.1 |
| 4 | B-d0.45 | B | 47 | 2 | 0.55 |
| 5 | B-d0.50 | B | 42 | 2 | 0.5 |
| 6 | B-d1.00 | B | 23 | 1 | 0.25 |
| 7 | B-d0.70 | B | 31 | 1 | 0.35 |
| 8 | B-d0.35 | B | 62 | 2 | 0.7 |
| 9 | B-d0.20 | B | 70 | 2 | 0.8 |
| 10 | C-R1.25 (conv_ball leg) | C (M/64), 5653672, outer 16 M, core_gauge | 16 | 4 | 2.3 |
| 11 | C-d0.42 | C (M/64), nestC 4969736 | 51 | 14 | 8.2 |

Model: B 0.31 s per cycle (conv_ball B 0.262 s with outer 16 M, plus 20 per cent for the
outer level), 128 cycles per M; C 2.25 s per cycle, 256 cycles per M. Sum of the model 15
card-hours, requested 32.7 (G2 allotment left 53.6 before this batch). Order: the bracket first,
the cheap third mesh, the rest of the scan, then the long C chains.

## 3. Sequencer

`scripts/sequencer.sh` (started with setsid nohup; state in
`scratch/A-emd-pbh/sequencer_threshold/`) submits the lines of `queue.txt` through nrpic-run
whenever fewer than two Slurm jobs named `A-*` of this user are queued or running. Stop: create
`scratch/A-emd-pbh/sequencer_threshold/STOP`, or kill the PID in `sequencer.pid`. A queue line
whose submission is refused five times is marked skipped in `done.txt`.
