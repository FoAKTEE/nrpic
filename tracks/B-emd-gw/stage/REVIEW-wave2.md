# Lead's review of the wave-2 helper packages (B-emd-gw)

Lead session of 2026-11-15 (after the four helpers finished). Method: each package was
checked from its registered outputs with code written for this review
(`stage/review_wave2/scripts/`), sharing as little as possible with the helper's code;
predictions R1-R10 were committed before the review runs (`stage/review_wave2/JOURNAL.md`,
commits e09a0d2 and 2f8806a), outcomes are appended there. The helpers' conclusions had been
read first (their reports), so this is a recheck of artefacts, not a blind one; the blind
check of the wave-1 material is the verifier's (`stage/G0/VERIFIER.md`).

Review runs (all registered, processors only, scouting, gate G1):

| Run | What | Result |
|---|---|---|
| B-20261115-190007-e09a0d2 | first_source: c_+ at (k, +-k, 0) from the bin dumps of all 10 scan runs with an own reader (`athbin.py`, layout from `athenak/src/outputs/binary.cpp` 125-232), own reference g(tau), own TT projector for the null | R1-R6 |
| B-20261115-190019-b5f5eb6 | late TT rise: own TT projector and band sums on dumps 7 and 13 of both wave-1 cosmology runs | R6b |
| B-20261115-190015-4dd3416 | newton_tests: H1 from an own linear-growth integration; t_x, quadrupole energy and self-similar constants from the history files | R7-R9 |
| B-20261115-190323-2f8806a | rerun of the verifier's v2, v3, v6 and leaf comparison | R10 |
| B-20261115-190433-2d1d185 | figures `stage/review_wave2/figs/rv_review_first_source.png`, `rv_review_newton.png` (looked at) | |

## first_source

Confirmed (numbers: lead / helper):
- Second-order amplitude before shell crossing (P2): max |c_+/(s g) - 1| for 2 <= a <= 10 =
  0.224 / 0.22, 0.222 / 0.22, 0.435 / 0.44 percent (eps = 0.1, 0.3, 1, 64^3); K2 with the
  opposite sign; 32^3: 0.195, 0.190, 0.379 percent. Lead and helper c_+(K1) agree to 9e-14 of
  |s| at every dump, so the helper's pipeline reads the dumps correctly. [VERIFIED]
- Linearity (P3): 0.050 / 0.05 percent. Null: largest TT amplitude 1.9e-16 (64^3) and
  3.7e-16 (32^3) at every tenth dump, z-dependence <= 2e-14. [VERIFIED]
- Second gauge (P6c): raw zero-shift minus Gamma-driver difference 0.131, 0.360, 1.454,
  4.82, 11.52 percent of |s| at a = 5, 10, 20, 40, 60 (helper 0.12, 0.36, 1.5, 4.9, 11.5);
  after the helper's G_tot 0.005, 0.008, 0.031, 0.29, 1.21 percent; median corrected/raw
  0.0840 / 0.084 (64^3), 0.0928 / 0.093 (32^3). The reduction by a factor 12 in a second
  gauge is the strongest evidence that G_tot is right; G_tot itself was not rewritten here.
- Resolution (P8): |c_+(32^3)/c_+(64^3) - 1| <= 0.091 percent for 5 <= a <= 40, 0.4-0.5
  percent at a = 80 (zero shift), 3.2 percent at a = 100 (eps = 1). [VERIFIED]
- Quasi-static TT field: (dc/dtau)^2/(|K|^2 c^2) of the K1 mode 0.036 at a = 4 and <= 0.013
  for a >= 12 (helper, all modes: 0.04, <= 0.01). [VERIFIED for K1]
- Late rise of the wave-1 dumps (P7): total rms 2.4882e-9 / 2.488e-9 and 4.3116e-9 /
  4.312e-9 at a = 1001; share of the rise at |k|L/2pi >= 20 0.926 / 0.93 and 0.972 / 0.97;
  rms below 10 +7.7 / +8 and +9.7 / +10 percent; deposit ratio at >= 20 1.94 / 1.9.
  [VERIFIED]

Not confirmed here (not rechecked, stays the helper's): the gauge-piece code `fslib/gauge.py`
beyond the two-gauge consistency above; the magnetic-Weyl agreement (P6d); the absolute
rho_GW/rho_bar values (3.5e-6, 8.8e-9); the slicing checks P9, P10 (P10's coefficients are
the helper's estimate, as it says); the two checks done by hand and not registered (shift
integral, transformed metric at tau = 1.9).

Wrong or imprecise (small, corrected in the documents of this review, not in the helper's
files, which stay as the record):
1. "eps = 1 peaks at a ~ 95, c_+/s = 2.5": c_+/s has two maxima, 2.5 near a = 95 and the
   largest, 2.55, at a = 123 (lead run, R6).
2. "c_+ at 32^3 and 64^3 agree to <= 0.06 percent at a = 5-40": 0.091 percent for eps = 0.1;
   for eps = 1 the largest difference for 40 < a <= 80 is 1.02 percent (R5; my own bound of
   1 percent failed there).
3. Framing of the gauge result (README item 3 and request 2: "the code's zero-shift strain
   matches the second-order Poisson-gauge value to < 1.1 percent (G_tot)"). What is measured
   is the size of the spatial-gauge piece, |G_tot/c_+| < 1.1 percent for a <= 20. The
   G_tot-corrected strain departs from the second-order reference more than the raw one
   (eps = 1: 0.69 against 0.44 percent at a = 10, 3.5 against 2.3 percent at a = 20; the
   helper's own `results/scan_summary_64.json`, keys `rel_dev_at_a` and
   `corrected_rel_dev_at_a`). So the departure from s g after a ~ 10 is neither junk nor
   spatial gauge: it is beyond second order (it grows with eps), and G_tot does not bring the
   code closer to the second-order value. This agrees with the verifier's derivation (C5:
   with zero shift and Newtonian first-order slicing, gauge differences of the TT strain enter
   only beyond second order) and with its weakest point 1 (the window is a <= 10 at
   delta = 0.01). [JUDGEMENT]
Process defects, all recorded by the helper and acceptable: the killed and the failed
initial-data runs (outputs used and complete), outputs moved after a literal
`$NRPIC_RUN_DIR` directory, one superseded plot run.

Large items left open (in `stage/G1/OPEN.md`): convergence in particle number and at 128^3;
the jittered-lattice null; the York TT part; adoption of `gauge_piece_total` into gw_diag
(the helper's request 1; accepted, scheduled, not done in this session).

## newton_tests

Confirmed:
- H1 (seven-point Laplacian, force too strong by [(kh/2)/sin(kh/2)]^2 - 1): my own
  linear-growth integration reproduces the helper's predictions to the printed digits;
  measured/predicted at a = 2 and 5 is 0.984, 0.982 (n = 16), 0.989, 1.019 (32), 1.000, 1.013
  (64), within the claimed 2 percent; later (a = 10, 15) 1.08-1.28, the nonlinear stage that
  H1 does not cover. [VERIFIED; the measured sheet errors are the helper's (pancake.json),
  not reread]
- N1 from the history files: t_x = 24.065902, 23.895492, 23.860390 (identical), E/M =
  3.2222e-4, 4.0085e-4, 4.4370e-4 (helper 3.22e-4, 4.01e-4, 4.44e-4), Richardson t_x =
  23.85128 (order 2.28) against the ODE's 23.8524, step check 2e-7. [VERIFIED]
- N3: E/(M (2 alpha)^(7/2)) = 0.0620684 (N = 32), 0.0772146 (N = 64), the same for all four
  alpha to 8e-15 and 3e-14. [VERIFIED]

Comments:
- The energy to the first crossing is far from its asymptotic range (35, 19, 10 percent
  from the extrapolated value, order 0.88), so the +0.7 percent agreement of the Richardson
  value with the ODE is not evidence of convergence to 1 percent [JUDGEMENT]; the crossing
  time (second order, Richardson within 5e-5 of the ODE) is.
- N3 tests that the discrete problem has no hidden scale (exact rescaling), which is what it
  claims; the physics of the 7/2 law is in N1's convergence to the ODE.
- Figure `figs/ell_convergence.png`, right panel: the legend says "raw Q-double-dot"; the
  energy uses the third derivative. Label only.
Decision on the helper's request 4 (G1 criterion 2): met for the single-patch N-body
baseline in the code (lead's judgement; reasons in `stage/G1/CHECKLIST.md`); N2 waits for
core's species history.

## note

Confirmed: the two corrections of the lead's wave-1 documents I spot-checked are right
(Hamiltonian constraint at t = 3000 Mpc/h 3.11e-8, 2.48e-9, 2.98e-9 in
`cosmo/analysis/daverio_a.json`, `a_n8/16/32` keys `Hr`; the Newtonian mode is on main since
core-v0.3). Pages 1-4 of `note/main.pdf` read; `nrpic-stage verify` reran its six scripts
and regenerated its twelve figure files equal to the committed ones (helper's verify run).
Fixed: the note said that the resolved part of the late TT rise "stays frozen"; the
first-source band sums (and R6b) show it grows (+8-10 percent below |k|L/2pi = 10,
twentyfold in 10-20). Sentence corrected, `main.pdf` recompiled (10 pages, no undefined
references; commit 2f8806a). The four corrections the note asked for are made in
`stage/G1/STATUS.md` (rewritten) and in the errata section of `stage/G0/STAGE_REPORT.md`.
Open: the note does not yet carry the first-source scan and the Newtonian-mode results
(Sec. IV, V); step 4 of the new-paper procedure (reviewer agents) was not run.

## verifier (stage/G0/VERIFIER.md)

Confirmed: v2_crossed, v3_junk, v6_za_scaling reproduce their registered JSON exactly
(R10); (5/12)|phi_x phi_y| = 1.5399e-5 from my own s; my g(tau) gives the junk envelope
1.9 percent over the period around a = 60, consistent with its exact 1.807 percent.
What the track does with each WRONG or NOT CONFIRMED item:

| Item | Verdict | Action of the track |
|---|---|---|
| C2 side: TT-fraction crossover 0.18 | WRONG (0.289) | corrected in `scope/SCOPE.md` risk 1 with the thresholds 0.032 and 0.19 (commit 87682d9); the measure is marked as counting only the scope's terms |
| C6: oblique-wave generator not TT | WRONG (generator) | confirms the track's outbox; core flipped the signs on `core/requests-b` and ran k = (1, 1, 1) with gw_diag (core message 20261115T1850Z); the track reruns its own oblique test when that branch is on main, and flips `xy`, `yz` in `periodic_z4c/analysis/refsol.py` tt_polarization then (core's note) |
| C8: Omega_GW today proportional to sigma^(7/2) | NOT CONFIRMED | read at the source: eq. (result_OmZ) takes 1 + z_e at each configuration's collapse (2403.15126:1061), which supports sigma^(5/2); the paper states 7/2 (1074). SCOPE.md now cites 1007 and 1031 for the emitted spectrum and marks the Omega-today scaling TO VERIFY; G1 criterion 2 is judged on the emitted energy only |
| C1 caveat: K overlap with the global mode a total derivative only for x-independent lapse | caveat | wording in SCOPE.md section 2 is kept; the conclusion (no TT at nonzero k) is unaffected |
| Weakest point 1: comparison window | accepted | SCOPE.md section 6 now states the reference (s g with junk) and the window a <= 10 at delta = 0.01; a delta = 0.0025 run is in the next scan (`stage/G1/OPEN.md`) |
| Weakest point 2: noise floor not measured | accepted | the jitter option exists on core/requests-b (`make_waves.py --jitter`); the jittered null is next action 2 |
| Weakest point 3: relativistic regime | accepted | stop rule of SCOPE.md section 6 stands (delta <= 0.02 until a slicing passes collapse; joint work with Track A) |
| C5: OPEN item 7 closable at second order | accepted | closed at second order: the verifier's derivation plus the measured size of the spatial-gauge piece (< 1.1 percent of c_+ for a <= 20, first_source P5); slicing piece bounded only (P10) |
| File name VERIFIER.md, harness expects VERIFIER_REPORT.md | naming | kept as written by the verifier; request to orch to accept the name (outbox) |
