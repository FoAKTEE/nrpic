# Journal of verify/verifier_g2 (fresh verifier of core's gate G2)

Helper of owner core, batch 6 (2026-11-21), no card time. Fresh context: before my own
verdicts were committed I did not read core's STATUS.md, HANDOFF.md, REVIEW files or the
conclusions of any journal. Claims taken from `tracks/core/stage/G2/EVIDENCE.md`,
`CHECKLIST.md`, `OPEN.md` (first section), `verify/LADDER.md` and the interface documents
(`tracks/core/interfaces/*.md`), which state the claims with run ids.

## Entry 0, 2026-11-21T21:17Z: claims chosen and predictions (written before any check)

Sample: every ladder row that core marks met (rows 1, 2; the met sub-claim of row 4,
"fates of the five models as the paper"; C3 constraints; C4), and at least one claim of
each release core-v0.3 to core-v0.6. For each: what core states, what I expect, what
would refute it. Tolerance for "the stated number": agreement to the digits printed
(relative 1 per cent for two- and three-digit numbers) unless said.

| id | claim (source) | raw output | prediction | refuted if |
|---|---|---|---|---|
| V1 | Row 1: Kerr a = 0.9, e = 0.99 passage, dt = 0.01 to 230 M, largest relative errors of (E, L_z, Q): midpoint analytic 2.781e-8, 0, 1.254e-7; Boris symmetric analytic 9.046e-8, 1.136e-8, 7.825e-7; midpoint Hermite lattice 2.162e-6, 5.304e-6, 5.060e-5; Boris Cholesky lattice 2.046e-6, 3.788e-6, 5.289e-5; paper digits main.tex 825-833; second order in dt; pericentre 1.898325 M (LADDER.md row 1; EVIDENCE regression G core-20261115-065452-3629622) | `scratch/core/core-20261115-065452-3629622/*/geo.traj.bin` | my own E, L_z, Carter Q from the stored (x^i, u_i) with my own Kerr-Schild metrics reproduce every number to 3 digits; the paper's two digits follow by rounding; order of the final position error against my own adaptive reference integration within [1.9, 2.1]; pericentre within 1e-5 M of the turning point of my own radial potential | any number off by more than 1 per cent, a paper digit that does not round to it, order outside [1.9, 2.1] |
| V2 | Row 2: Oppenheimer-Snyder (card, merged exe, core-20261115-065901-3629622): first horizon 16.3894 M, M_AH 1.000353; largest abs(M_AH/M - 1) to 25 M 6.3e-4; deposition identity 1.0e-15. Earlier full run (`runs/os/nocap_sc`): largest 1.34e-3 over 16-60 M, 0.998670 at 60 M, all 9328 particles removed by 19.74 M. Paper: <~ 1e-3 (main.tex 945) | `os.horizon_summary_0.txt`, `os.nrpic.hst`; `runs/os/nocap_sc` | confirmed to the printed digits | any of these off by more than one unit of the last printed digit |
| V3 | Row 4, met part: fates of five models (runs/st/*): 0.900 and 0.819 stay (central lapse 0.886-0.892, 0.787-0.819 over 300 M), 0.605 and 0.500 collapse (first horizon 191.0 M, 104.3 M; M_AH/M 1.0000, 1.0001), 0.283 expands (central lapse 0.976 at 270 M, all particles kept); paper 109 M, 73 M (main.tex 1138). Wave-2 sample: y_c = 0.72, mean central lapse 200-300 M 0.7079 (core-20261115-152843-5728b1d) | hst and horizon files | fates confirmed; numbers to the printed digits | a fate differs, or a number off by more than one unit of the last digit |
| V4 | C3: homogeneous universe (card, core-20261115-065903-3629622): H-norm2 3.7e-10, abs(Theta) 1.1e-11 | `flrw.z4c.user.hst`, `flrw.cstat.hst`, `flrw.nrpic.hst` | confirmed; in addition the scale factor from the proper volume follows Einstein-de Sitter to the size the judge allowed | number off by more than 10 per cent (they are round-off-level), or the expansion off EdS by more than 1e-3 |
| V5 | Deposition identities: (a) OS 1.0e-15 (V2 run); (b) MPI periodic cosmology T6, identity 1e-14 on 1, 2, 4 ranks, positions 1.6e-14 (core-v0.5, `interfaces/mpi.md` row 6, core-20261119-163641-ddb47b0); (c) the card check of core-v0.6 (job 4800, cases dep, depp) | hst columns int_E against sum_mW | identity at 1e-15 to 1e-13 relative; rank counts agree to the stated digits | identity above 1e-12 relative, or ranks differing by more than stated |
| V6 | Exact restart ("restarts are exact", CLAUDE.md; LADDER.md: positions to 9e-16 asymptotically flat, periodic identical; mpi.md row 4 caveat: with Z4c and outflow faces a restart on one rank is not exact, 1e-9 at the faces) | fresh processor runs on release core-v0.6 (`.work/build_cpu_v06`) | periodic set-up: data files of straight and restarted runs byte-identical; Z4c with outflow faces: differences at the 1e-9 level as the caveat says, i.e. "exact" holds only for periodic or particle-only set-ups | periodic restart not byte-identical; or the outflow case byte-identical (then the caveat is wrong) |
| V7 | Newtonian mode. (a) core-v0.3: point mass, rms relative force error of tracers with r >= 0.5: 1.609e-2 (N = 32), 4.94e-3 (64), order 1.70 (core-20261115-150209-3629622). (b) core-v0.6: Fourier solver, T2 pancake against Zel'dovich, spectral n = 32: 9.55e-5 at a = 2, 5.56e-4 at a = 5 (newtonian_mode.md 7.3, cases core-20261119-150559-c1ff7ca) | particle files | (a) confirmed to 3 digits with my own -M r/r^3 reference; (b) confirmed to 2 digits with my own Zel'dovich solution | off by more than 2 per cent |
| V8 | Collision operator (core-v0.3), box relaxation (core-20261115-134036-5684674): end states Maxwell-Juttner at the temperature of the conserved energy (KS p 0.26-0.90), <u^2/W>/3 = theta_eq within 0.06 sigma, energy sums equal to the last bit (collisions.md, section 8 table) | snapshots of shell and two-temperature runs | my own theta_eq from the energy and my own KS test give p in that range; total energy and momentum conserved to rounding | p < 0.01 in any case, or energy drift above 1e-13 relative |
| V9 | Scalar field (core-v0.3), test 1a: Klein-Gordon plane wave, spatial orders 1.991, 3.957, 5.918 for ng = 2, 3, 4 (core-20261115-150004-3629622) | `kg.sf.*.dump` | my own frequency fit from the dumps gives the same orders to 0.01 and the frequency equals the stencil frequency omega_h to 1e-7 relative | order differing by more than 0.02 |
| V10 | Initial-data solver. (a) core-v0.4, T1 Gaussian: central error of psi - 1 (code, ng = 4) -1.92e-2, -5.22e-3, -1.33e-3 at dx = 1, 0.5, 0.25 (second order); (b) core-v0.6: monitor after the solve at round-off (Bowen-York puncture max abs(H) 6.4e-12 on card and processor, job 4800, core-20261121-154700-2de4974; test C 2.4e-12 to 2.0e-11) | mesh outputs and hst | (a) my own continuum reference (radial ODE) gives the same errors to 2 digits and order 1.9-2.0; (b) confirmed from the hst | (a) errors off by more than 5 per cent or order outside [1.8, 2.2]; (b) monitor above 1e-10 |
| V11 | Boundary (core-v0.6, z4c_faces): fall-off ghosts lower the boundary-cell constraint next to a face at t = 0 / after one step about 12 times at every order (tests a0, a0b, c0); stock boundary cell 1.9e-3 = 0.79 of the stencil estimate (run core-20261119-143938-eded041) | mesh outputs | ratio 8-16, stock value within 10 per cent | ratio below 4 or stock value off by more than 20 per cent |

Order of work: V1, V2, V4, V5a (cheap readers), V3, V9, V7a, V8, V6 (fresh runs), V7b,
V10, V11, V5b-c. What cannot be reached in a few hours is listed as not checked.

## Entry 1, 2026-11-21T21:28Z: outcomes V1-V4, V7a, V8, V9 (registered analyses)

- V1, run core-20261121-212008-6986d13 (own CKS and spherical KS metrics; self-test: the
  spherical inverse equals inv(J^T g_CKS J) to 4.4e-16). Largest relative errors (E, L_z,
  Q) at dt = 0.01: midpoint analytic 2.781e-8, 0, 1.254e-7; Boris symmetric analytic
  9.046e-8, 1.136e-8, 7.825e-7; midpoint lattice 2.162e-6, 5.304e-6, 5.060e-5; Boris
  Cholesky lattice 2.046e-6, 3.788e-6, 5.289e-5: every claimed number to its four digits;
  each rounds to the paper's two digits (main.tex 825-833). Initial E, L_z, Q = 0.99738,
  2.4328, 1.974 as main.tex 811. Order of the final position error against my own DOP853
  reference: 2.0003/2.0001 (midpoint), 1.9991/1.9998 (Boris symmetric), 1.9989/1.9997
  (Cholesky), as claimed. Pericentre: root of my radial potential 1.898327 M, my reference
  integration 1.898327 M at 98.948 M, as claimed. Prediction held. CONFIRMED.
- V2, run core-20261121-212106-131e909: regression O first horizon 16.3894 M, M_AH
  1.000352575670864; largest abs(M_AH/M - 1) to 25 M 6.345e-4; deposition identity
  (|int_E - sum_mW| / sum_mW) at most 9.6e-16. nocap_sc: largest 1.338e-3 (at 54.4 M),
  1.000093 at 20 M, 0.998762 at 40 M, 0.9986707 at 60 M (claim prints 0.998670, a
  truncation, not a rounding), all 9328 particles gone at 19.739 M. Prediction held.
  CONFIRMED. Seen in the figure: after 31 M the 60 M run is outside +-1e-3 and stays at
  -1.3e-3; "of the order of the paper's <~ 1e-3" is a judgement that I share, but the
  number is not below 1e-3 after 31 M, and the evidence to 60 M is a pre-program run
  (`runs/os/nocap_sc`, untracked, not registered).
- V3, run core-20261121-212244-3f782d9: central lapse (probe at the origin) 0.900:
  0.8862-0.8919; 0.819: 0.7875-0.8190; both keep 10000 particles to 300 M. 0.605: first
  horizon 191.0 M, last M_AH 0.99999; 0.500: 104.31 M, last M_AH 1.00005 (run ends at
  120 M); 0.283: central lapse 0.4054 -> 0.97598 at 270 M (run ends at 270 M), 10000 kept.
  Wave-2 y_c = 0.72: mean central lapse 200-300 M 0.70789. Every number as claimed.
  CONFIRMED (fates). Ratios to the paper 191.0/109 = 1.75, 104.3/73 = 1.43 as LADDER says.
- V4, run core-20261121-212248-a7972d1 (own EdS in the conformal-time lapse: a = (1 +
  t/2)^2): lapse against a 1.9e-7, mean K 3.8e-7, proper volume 1.1e-6 relative to t = 2
  (a = 4); identity 2.2e-16; H-norm2 3.696e-10 and the column read as "|Theta|" 1.106e-11
  as claimed. But the hst column is `Theta-norm2` = sum of vol * Theta^2
  (`athenak/src/outputs/history.cpp` lines 186 and 229; the file header truncates the name
  to `Theta-norm`), not |Theta|: the pointwise max |Theta| (cstat) is 2.27e-7 and max |H|
  1.69e-6. Numbers CONFIRMED; the label "|Theta| 1.1e-11" in CHECKLIST C3 is WRONG.
- V7a, run core-20261121-212516-0f0a65b: far rms relative force error 1.6092e-2 (N = 32),
  4.9399e-3 (64), order 1.704: as claimed (EVIDENCE: 1.609e-2, 4.94e-3, 1.70). The number
  of tracers with r >= 0.5 is 706, not 846 as `interfaces/newtonian_mode.md` 5.2 says (same
  particle file as the original run, cmp identical; no simple cut gives 846). CONFIRMED;
  the count in the interface text NOT CONFIRMED.
- V8, run core-20261121-212611-5973536: theta_eq from the conserved energy equals the
  summary's to 1e-15; KS p of the end state 0.897, 0.744, 0.447, 0.261 (claimed 0.26 to
  0.90); pressure estimator within 0.056 standard errors (claimed 0.06); energy sums
  (fsum) equal first to last in three cases, one unit in the last place in shell_2
  (-2.0e-16), as claimed; momentum change below 4e-19 of the energy. Per species in the
  two-temperature runs: z = +-0.56 and +-0.2, KS p 0.13-0.99. CONFIRMED. Note: the run
  used the branch executable of core-coll (wave 1), not a release build.
- V9, run core-20261121-212422-b616c6e (own dump reader; at t = 0 the field equals cos(k.x)
  to 1.6e-15; own stencil symbols): least-squares orders over n = 8..24: 1.9913, 3.9566,
  5.9181 (claimed 1.991, 3.957, 5.918). My symbols reproduce the code's omega_h to 1e-12.
  A plain phase fit is biased by the counter-propagating wave (B/A up to 1e-2, the initial
  momentum is that of the exact omega); with a two-wave fit omega_meas / omega_h - 1 =
  -1.21e-9 to -1.31e-9 in all twelve runs, which is the RK4 phase error (omega dt)^4/120
  = 1.31e-9 at dt = 1/512. `interfaces/scalar_field.md` test 1 says -1.2e-8 ... -1.34e-8:
  ten times too large (the run's own summary.json gives -1.21e-9). Orders CONFIRMED; the
  frequency-agreement number of the interface text WRONG by a factor 10 (typo-like).

## Entry 2, 2026-11-21T21:50Z: outcomes V5b, V7b, V10a, V10b; V6 attempts

- V5b, run core-20261121-213807-4cc035d (MPI, core-v0.5, case t6_cosmo_east of
  core-20261119-163641-ddb47b0): deposition identity max |int_E / sum_mW - 1| 9.8e-15,
  7.4e-15, 3.1e-15 on 1, 2, 4 ranks (claim 1e-14); positions against one rank at most
  5.3e-15 (2 ranks) and 4.0e-15 (4 ranks) over 13 snapshots (claim 1.6e-14, an upper bound
  here); E and S_i at the particles 1.21e-14 and 1.26e-14 of the column maxima (claim
  1.3e-14); metric at the particles 2e-13 absolute, 8e-15 of the column maxima (the
  driver's "metric DIFFERENT" is a byte statement). Prediction held. CONFIRMED.
- V7b, run core-20261121-213946-cee79fa (Fourier Poisson solver, core-v0.6, T3 of
  core-20261119-160919-c6a7279): own Lagrangian lattice from the a = 1 snapshot (snapped
  to (i + 1/2)/32 within 5.6e-17), own exact slab moment I_xx = c0 + c1 a + c2 a^2 (the
  history's value at t = 0 equals mine to 3e-16 relative): largest error over 1.2 <= a <=
  7.5625 relative to max |I_xx - c0|: 9.107e-6 (spectral), 3.094e-3 (seven_point);
  claimed 9.1e-6, 3.1e-3. Positions at a = 4 against q + a psi: 1.44e-5 (4.5e-4 of the
  displacement amplitude, spectral), 6.2e-5 (seven_point). CONFIRMED. First pass of my
  window stopped at a = 7.541 (9.04e-6); the claim's window includes the last record a =
  7.5625.
- V10a, run core-20261121-214108-0960a46 (initial-data solver T1, core-v0.4 branch runs;
  own reader of NRIDSOL1, own continuum psi = 1 + M erf(r/(sqrt2 sigma))/(2r)): first
  pass gave absolute errors at the centre cells -1.76e-3, -4.80e-4, -1.23e-4 (stencil),
  -3.72e-3, -1.03e-3, -2.65e-4 (code), five times below the claim; the claim's numbers
  are the relative error of psi - 1: -9.10e-3, -2.43e-3, -6.17e-4 and -1.92e-2, -5.22e-3,
  -1.33e-3, all reproduced to three digits; orders 1.91/1.98 (stencil), 1.88/1.97 (code):
  second order. Monitor after the code solve 1.55e-11, 1.09e-11, 2.59e-11 (the interface
  says 1.5e-11 to 2.6e-11; the n64 run is 1.1e-11). CONFIRMED; "error of psi - 1" should
  say "relative error of psi - 1".
- V10b, run core-20261121-214230-ad24f6b (second pass, core-v0.6, test C of
  core-20261119-153510-d1eaa30; own NRIDBLK1 reader): monitor after the solve on the two
  levels of g_smr1 2.44e-12 and 2.02e-11 (claim 2.4e-12 to 2.0e-11); g_smr2 5.9e-13 to
  1.9e-11. Central error: with my eight-cell measure -5.20e-3 (refined) and -5.22e-3
  (uniform dx 0.5); the claim's -5.01e-3 and -5.03e-3 are the mean over r < 1 (read in
  tracks/core/analysis/idsolve2/test_c.py after my first measure differed), which my code
  reproduces: -5.0136e-3 and -5.0331e-3. Refined equals uniform to 0.4 per cent by
  either measure. CONFIRMED. g_smr2 (finest dx 0.25 = lattice spacing) gives +2.9e-4, a
  different regime (one particle per cell), not claimed.
- V6 first attempt core-20261121-212800-3365cf3: failed by my driver (a block cannot be
  created on the command line; athena exit 1 at once). Second attempt
  core-20261121-212817-0f0f28b: the athena runs A completed (east 7 s, os 481 s) but my
  parser of the cycle in the restart header failed, so B did not run. Third attempt
  running (header parsed from athenak/src/outputs/restart.cpp lines 219-236).

## Entry 3, 2026-11-21T21:48Z: outcome V11

- V11 first attempt core-20261121-214423-6aa60c3: a0b analysis done, the fresh runs
  failed (relative input path; athena could not open it). Second attempt
  core-20261121-214458-603e123: stock runs done, `ghost_falloff` runs failed (a parameter
  absent from the input cannot be set on the command line). Third attempt
  core-20261121-214547-7a21ed3: all done.
- Own derivation: sixth-order second derivative reading ghosts from p-point Lagrange
  extrapolation gives the boundary-cell error coefficient 201/180 = 1.1167 (p = 2), and
  0.1167, -0.0111 in the next two cells, as `z4c_faces.md` H1 says; my estimate of the
  boundary-cell |H| at the face centre 8 x 1.1167 m / 15.5^3 = 2.399e-3; orders 3, 4
  relative to 2: 0.1753, 0.0410.
- Measured (a0b, branch faces; own .bin reader, chi at t = 0 equals psi^-4 to 3e-8):
  1.8953e-3 = 0.790 of my estimate (claim 1.9e-3, 0.79); e3/e2 0.184, e4/e2 0.0480
  (claim 0.18, 0.048). The release core-v0.6 executable gives the same value to all
  digits (stock, order 2 and 4). Fall-off ghosts on the release: 1.53e-4 (order 2) and
  7.9e-6 (order 4) after one step: 12.4 and 11.5 times lower (claim about 12 at every
  order). At t = 0 the monitor is 8.5e-9 with either fill (the ghosts are not extrapolated
  before the first step). Prediction (ratio 8-16, stock within 10 per cent) held.
  CONFIRMED.
