# JOURNAL of C-sidm

Append-only, newest at the bottom, one entry per session:
`## <UTC time>  session <name>  commits <a>..<b>  runs <ids>` followed by
did / found / evidence / changed my mind about / open. Predictions are written here before
a test runs, outcomes after.

## 2026-11-15T13:10Z  session C-sidm lead (wave 1 review)  predictions before the review runs

Helper packages under review (their own journals hold their predictions and outcomes):
`scope/JOURNAL.md`, `collide/JOURNAL.md`, `gravothermal/JOURNAL.md`,
`equilibria/JOURNAL.md`. The lead reruns and cross-checks from the artefacts with
`review/rerun_packages.sh` (+ `review/compare_reruns.py`) and `review/crosscheck.py`.

- prediction L1 (reruns): every test suite passes (collide REFERENCES 62, collide analysis 3,
  gravothermal test_tmb all); the scope JSON outputs, the polytrope check, the equilibria
  checks (243 pass flags) and the T6-0 step analysis equal the registered outputs to 1e-12
  relative (deterministic codes, fixed seeds, the same processor executable, sha256
  91f2e2c2...); the 31 T6-0 particle snapshots are bit-identical. Refuted by any failing
  test or any number differing by more than 1e-12.
- prediction L2 (X1): the closed form <v_Mol> = 4 K3(2 zeta)/(zeta K2(zeta)^2) agrees with a
  direct 3D Gauss quadrature over both momenta (written by the lead, no Gondolo-Gelmini
  reduction) within 1e-5 relative for theta = 1e-3..100 (the limit is the kink of the
  angle-averaged speed at |p1| = |p2|); collide's rate.vmol_mean equals the closed form to
  1e-12. Refuted by a difference above 1e-5.
- prediction L3 (X2): scope's and gravothermal's truncated Maxwell-Boltzmann solvers (two
  independent codes) agree to 1e-6 relative in eps and 1e-6 absolute in Z(0) at b = 0.1 and
  0.5; their eps maxima agree in Z(0) within 1e-4; both match F21 Table 1 rows
  main.tex:492, 495, 498, 501 (transcribed by the lead) within 1.5e-4 relative in M, E_rest,
  eps, Z(0), v(0).
- prediction L4 (X3): scope's solver at b = 1 and equilibria's evstatic King model agree to
  1e-6 in E_b and Z_c; both put the first maximum at y0 = 0.33403 within 1e-5.
- prediction L5 (X4): with the track's Kn definition (lambda = 1/(rho0 sigma_m),
  H = (v1^2/(4 pi rho0))^(1/2)), Kn sigma~ of the King threshold is about 169 from both the
  scope solver and equilibria's rho0_c, H_c (agreement 1e-4); scope's definition (energy
  density in H) gives about 199; equilibria's Kn uses l = 0.77 lambda (consistency 1e-12).
- prediction L6 (X5): omega_0^2 of the b = 0.1 model with gamma = 1 + p/u is positive at
  w0 = 3.50 and 3.58 and negative at 3.595 and 3.68 for N = 600 and 1200 (gravothermal's
  onset w0 = 3.5871, Z(0) = 0.6348). Refuted by a sign pattern that moves the zero out of
  [3.58, 3.595] or depends on N.

## 2026-11-15T13:25Z  session C-sidm lead (wave 1 review)  outcome L1, prediction L1b

- outcome L1 (run C-sidm-20261115-131135-3077a99, 608 s, 4 threads): FAILED in two items,
  held in the rest. Held: collide 62 + 3 tests pass; gravothermal unit tests pass; the
  three scope outputs (948, 2451, 2853 numbers) and the equilibria checks (318 numbers,
  243/243 pass flags) are identical to the registered outputs. Failed: (1) gravothermal's
  polytrope check differs at 5e-10 relative in omega^2 (N = 600) and 1.5e-10 in the zero
  location; its conclusion (FEM zero at the mass maximum to 2.7e-8, 1.5e-8, 2.5e-8) is
  unchanged; the original ran with one thread, the rerun with four. (2) The T6-0 rerun
  differs: 0/31 snapshots identical and the analysis' noise statistic changes by 28 percent,
  although the analysis still passes ("pass_collisionless": true). Positions in step.nrp are
  identical, momenta are not; `make_box.py` changed after the original run (commit abd9c2e:
  for an odd population, n//2 mirrored pairs plus one particle at rest instead of
  (n+1)//2 pairs truncated; the step box has n1 = 33333), so the rerun at HEAD used other
  initial momenta. No cause is claimed yet; L1b tests both explanations.
- prediction L1b (`review/rerun_followup.sh`): (a) the polytrope check with one thread is
  byte-identical to run C-sidm-20261115-121524-5cebcf5; (b) T6-0 with the collide code of
  commit 313d399 (git archive) reproduces step.nrp, the 31 snapshots and the history of run
  C-sidm-20261115-121302-313d399 byte for byte with the same processor executable. Refuted
  by any differing file.

## 2026-11-15T13:30Z  session C-sidm lead (wave 1 review)  outcome L1b, prediction L7

- outcome L1b (run C-sidm-20261115-132327-eab8e41): held. With one thread the polytrope
  check is byte-identical to run C-sidm-20261115-121524-5cebcf5; with the collide code of
  commit 313d399 all 33 T6-0 files (step.nrp, 31 snapshots, history) are byte-identical to
  run C-sidm-20261115-121302-313d399. The two differences of L1 are therefore the LAPACK
  thread count and the change of make_box.py in abd9c2e, not a defect of the codes.
- found: core committed the operator at 13:19Z (3436846 on `core/collisions`: design,
  kernels `nrpic_collide.hpp`, task `nrpic_collide.cpp`, predictions; "nothing is tested
  yet"). The kernel header is standalone (NRPIC_STANDALONE).
- prediction L7 (`review/t0_kernel.py 3436846`): core's committed kernels CollGammaRelM1,
  CollMoller and CollScatter pass T0 of collide/TESTS.md on all 208 equal-mass test vectors
  with -O0, -O2 and -O3 -march=native -ffp-contract=fast: every component of u' within
  1e-13 max(1, |u|) of the 60-digit reference (expected ~1e-15, like the oracle), pair
  four-momentum conserved to 4 eps of the pair energy, v_Mol within 1e-13 relative.
  Refuted by any failing case. The unequal-mass vector is outside an equal-mass kernel.

## 2026-11-15T13:40Z  session C-sidm lead (wave 1 review)  commits 06a05c7..(this entry's commit)  runs C-sidm-20261115-131130-3077a99, -131135-3077a99, -132327-eab8e41, -132624-13a77db

- outcome L7 (run C-sidm-20261115-132624-13a77db, 2 s): held for the T0 criteria: all 208
  equal-mass vectors pass at -O0, -O2 and -O3 -march=native with contraction; largest
  error 3.2e-16 of max(1, |u|), pair four-momentum within 1.32 eps. Refuted in my own
  extra v_Mol criterion for one vector: "identical_velocities" returns v_Mol = 0 exactly
  against a reference of 4.3e-31, which is the round-off of the 60-digit evaluation of an
  exact zero (207 others within 1e-13). Core found the same and compares absolutely there
  (a7dc8ab); its own T0 (1a050f3, run core-20261115-132556-a7dc8ab) gives 3.3e-16 and 1.4 eps.
- did: reviewed the four helper packages from their artefacts (`stage/G0/REVIEW.md`);
  reran every test and reference run (L1, L1b); independent cross-checks X1-X5 (L2-L6, all
  held); re-read 27 source statements at file:line; opened 29 of 35 figures; wrote the G0
  package (`stage/G0/REPORT.md`, `EVIDENCE.md`, `OPEN.md`, `CHECKLIST.md`), the G1 status,
  11 outbox messages, STATUS, HANDOFF, RISKS.
- decided [JUDGEMENT, REPORT section 2]: S3 family = F21 truncated Maxwell-Boltzmann at
  b = 0.1 (King b = 1 and monoenergetic for verification); Kn = lambda_c/H_c with
  lambda = 1/(rho0 sigma_m), H = (v1^2/(4 pi rho0))^1/2 (K = 168.9 for the King threshold
  model); Kn -> 0 anchor = exact pulsation onset; collisionless scans are G2 work in wave 2.
- changed my mind about: scope's G1 item (a) (moved to G2); scope's Kn (energy density in H,
  factor 1.18) and equilibria's Kn (transport mean free path, factor 0.77) replaced by one
  track definition.
- open: `stage/G0/OPEN.md` (working note, schematics, fresh verifier, Juttner Gamma_1 onset,
  F21 b = 0.1 particle files, growth-rate pipeline, literature); G1 waits for core's tested
  executable (T0b-T12); helper journals: `scope/JOURNAL.md`, `collide/JOURNAL.md`,
  `gravothermal/JOURNAL.md`, `equilibria/JOURNAL.md`.

## 2026-11-15T19:40Z  session C-sidm lead (wave 2 review)  commits 5f5767da..(this session)  runs (below)

Predictions of the lead's independent rechecks, written before any of them ran. Code:
`stage/review_wave2/` (own readers of the AthenaK files, own Maxwell-Juttner functions;
the track's references `collide/REFERENCES/` only where TESTS.md names them).

- L8 box tests (`rv_box.py`, registered outputs of runs -165500, -170155, -165902,
  -170539, -170741, -170814, -174651): (a) T2: for all 16 runs, accepted collisions vs
  summed sum_P |z| < 4; mean sum_P per step over (1/2) N rho0 sigma <v_Mol>(theta from
  <W - 1> of the first snapshot) dt within 2e-4 of 1 and |z| < 4 (helper: 0.99991-1.00010);
  (c) theta of the last snapshot equal to the first to < 1e-10. (b) T1: max |dE|/sum_MW per
  step <= 1e-18, exactly rounded sum M W of first and last snapshot equal to the bit in all
  T2, T1-long and T3-T5 runs. (c) T10: final snapshots of mb1, mb8, mb64, rst0-rst2 byte-
  identical in the particle records; seed 8 differs in > 99 percent of particles. (d) T4:
  my own quadratic fit over [0, 0.15 tau_rel] with relax.dtheta_dt of the sample's initial
  temperatures gives slope/exact within 1 se of the helper's 0.9924, 0.9792, 0.9959,
  1.0088. (e) T9: final class temperatures equal within 4 se in all 8 seeds; mean energy
  drift z between 1.5 and 3.5 (helper +2.42). (f) T0b: the helper's replay on the six
  registered dumps passes again (same numbers). (g) T11: accepted vs sum_P |z| < 2.
  Refuted by any T2/T1/T10 criterion failing or any recomputed number differing from the
  helper's beyond its stated precision.
- L9 models (`rv_models.py`): (a) my reader of the 13 particle files at N = 1e5 (own cubic
  table interpolation) gives sum m W/psi - 1 within 1e-6 of the JSON value (-2.2e-5 to
  -4.0e-5), E/E0 <= 1 for every particle, equal masses, |sum m u_i| < 1e-15. (b) The fluid
  onset with the Juttner Gamma_1 = 1 + 1/c_v at the energy-matched temperature, computed
  with the verifier's Rayleigh-Ritz operator (not the models helper's FEM) and my own
  Juttner functions, lies at Z(0) = 0.5331 +- 0.0005 for b = 0.1, and with theta = p/n at
  0.5317 +- 0.0005; with F21's gamma = 1 + p/u at 0.6348 +- 0.0002 (V4: 0.63482). Refuted
  if the Juttner onset differs by more than 0.002 (that would change the anchor decision).
  (c) The rerun of validate_growth.py reproduces growth_validation.json (G1 18/18).
- L10 threshold scan (`rv_scan.py`, histories of runs -171058, -171059-4b70228,
  -171059-35441e3): alpha_min < 0.3 first at 72.5, 77.8, 184.3, 206.8 M (+-0.5 M, the
  record spacing); controls keep N = 1e5 and never fall below 0.3; sum_m + m_excised +
  m_escaped equal to the initial rest mass to < 1e-13; excised fraction 20 M after the first
  excision 0.82-0.91; alpha_probe of the controls rises by 0.033 and 0.018 (+-0.002);
  collisions per particle before alpha_min < 0.3 (2 n_coll/N summed) 13.4, 15.3, 2.5, 2.9
  (+-0.2). Refuted by any number outside these bands.
- L11 note claims (`rv_note.py`): the three differences of note/tables/claims.md are
  confirmed from the run outputs (Table 1 B at w0 = 4.5 above 1.1e-4; fastest phase bound
  8.5e4 < 1e5; R/M and r_core/M ranges wider than 20-26 and 1.5-2.1 for Z(0) = 0.40-0.80).
  Refuted if the files support the lead's original wording.
- outcome L8-L11 (run C-20261115-193332-48771b4, 30 min on 2 cores; figures rv_box,
  rv_models, rv_scan, rv_note looked at): all held. Details in `stage/REVIEW-wave2.md`.
  Beyond the predictions: the T4 ratio moves by up to 0.4 percent (0.5-1.4 se) when the
  0.15 tau_rel window takes one snapshot more (sample tau_rel vs design tau_rel); the
  J_pu onset (1 + p/u of an untruncated Juttner gas at the Tolman temperature) coincides
  with the eps maximum to 3e-5 in Z(0) (0.54038 vs 0.54041), not explained; my E/E0 maxima
  of the particle files (0.99997 for tmb01_Z0p5404) differ from the JSON's 0.99992 (both
  below 1; not chased). The verifier suite rerun gives byte-identical JSON (5/5).
- prediction L12 (`rv_kn.py`, K = 1/(rho_0c H_c) of the 13 wave-2 models from their JSON):
  King y0 = 0.334032 gives 168.9 +- 0.1 (run C-sidm-20261115-131130-3077a99) and
  tmb01_Z0p5404 142.6 +- 0.1 (verifier, run C-20261115-170630-1037f6a); K falls with Z(0)
  along each family. Refuted by either value off by more than 0.1.
- outcome L12 (run C-20261115-193751-d3872ff, `rv_kn.png` looked at): held. K = 168.895 for
  the King threshold model and 142.6 for tmb01_Z0p5404; K falls with Z(0) along each family
  (written into `equilibria/CONVERSION.md` section 5 by the wave-2 lead). The wave-2 lead was
  cut off by the account's usage limit after this outcome; its STATUS, HANDOFF, outbox posts
  and the commit of the stage files were not done (done in wave 2b, entry below).

## 2026-11-19T15:15Z  session C-sidm lead (wave 2b review)  predictions before the review runs

Predictions of the lead's rechecks of wave 2b, written before any of them ran. Code:
`stage/review_wave2/rv_box2b.py`, `rv_cc.py`, `rv_king_onset.py` (own readers of `rvlib.py`;
the helpers' scripts are not imported, except `gravothermal/tmb.py` and
`models/fluid_onset.py` for L15, which are the track's reference solvers).

- L13 box_rerun (registered outputs of C-20261119-141502-95f0200, -141711-7db7a6a,
  -141806-af19c1c, -143041-f94e350, -143049-0cf699a, -141431-a351ac7, -143146-226b0e0
  against the release runs C-20261115-170155-13ff01f, -165500-c67e036, -165902-f9b1c8f,
  -172003-6422b6a): (a) R1: every one of the 6 x 6 output files byte-identical to the release
  run. (b) R2: n_tested, n_coll, n_updated, max_nsub, n_trunc of every coll.hst record equal
  to R1 in all six cases; n_noroot = n_balance = 0 and max_dlam = 0. (c) R3: in all 16 T2
  runs the integer columns equal the release run in every one of the 200 steps; my T2(b)
  ratio (sum_P over (1/2) N rho0 sigma <v_Mol>(theta of <W - 1> of the first snapshot) dt)
  in [0.9999, 1.0002] and within 1e-9 of my wave-2 recheck of the release run (same sum_P to
  1e-14, same first snapshot); T1 bound held. (d) R4: final particle records of mb8, mb64,
  rst0-rst2 byte-identical to mb1; seed 8 differs in > 99 percent; 385554 collisions.
  (e) R5: n_tested and n_coll of the curved run and its flat twin identical in all 200 steps
  of all four pairs; my own expectation 0.5 N^2 M sigma <v_Mol>(theta) alpha0 dt / psi0^6
  (theta from <W - 1> of the orthonormal momenta u/psi0^2 of the first snapshot) gives a
  ratio within 2e-4 of 1 and |z| < 4 in each, and within 1e-6 of the helper's ratios.
  (f) R6 from coll.hst alone: with coll_energy = particle the canonical energy changes per
  collision by +1e-21 to +3e-21 of sum M H_p at each Kn and step; in cell mode at Kn = 0.01
  the sum M W_p changes per collision (both steps pooled) by +4e-11 to +1.2e-10 of its sum;
  columns 1-29 of the cell-mode Kn = 1 record equal the release smoke run's; columns 30-31
  differ by less than 1e-13 absolute. (g) Timing: collision part per tested pair, particle
  over cell, 1.68 +- 0.02 from the wall times of `timing.json`. Refuted by any mismatch.
- L14 the collisional cluster runs (histories of C-20261115-171058-c26cfad,
  -171059-4b70228, -171059-35441e3; `rv_cc.py`): (a) the accumulated change of sum M W_p
  (coll.hst dE_particles) up to alpha_min < 0.3, over its initial value, is 1.6e-3, 1.7e-3
  (Kn = 1) and 1.8e-4, 2.2e-4 (Kn = 10) within 10 percent (helper's numbers); (b) so the
  accumulated defect at the time of collapse differs by a factor 7-10 between Kn = 1 and 10,
  and so do the collisions per particle (13.4, 15.3 against 2.5, 2.9); neither a fixed
  injected energy nor a fixed number of collisions per particle marks the collapse
  [refuted if either ratio is within a factor 2 of 1]; (c) at Kn = 10 the injected energy
  before collapse, in units of the rest mass M0 (sum_M of the history), exceeds the
  binding-energy difference between CC2 (y0 = 0.314, E_b = 0.035489) and the threshold
  model (E_b = 0.035589), 1.0e-4 of M0 [refuted if below it]. Reading, not a test: such a
  defect cannot be dismissed on size grounds as a cause of the Kn = 10 collapses.
- L15 fluid onset of the King family (b = 1 of the F21 kernel, V3), `rv_king_onset.py`
  with `tmb.py` and the omega^2 operator of `models/fluid_onset.py`: (a) tmb at b = 1 with
  w0 = 1 - exp(-y0) reproduces the King rows of `equilibria/README.md` (Z_c and R/M at
  y0 = 0.314 and 0.334032) to 1e-4 relative [refuted beyond 1e-3: then tmb is not the King
  model and L15 stops]; (b) the onset with F21's gamma = 1 + p/u and with the Juttner
  Gamma_1 at the energy-matched temperature (J_E) both lie below the collisionless E_b
  maximum y0 = 0.334 (as for b = 0.1-0.5), with J_E in y0 in [0.20, 0.334); whether J_E lies
  below y0 = 0.314 (CC2 fluid-unstable) I give 50 percent. The N = 600 and 1200 roots agree
  to 1e-5 in y0.
- prediction L16 (written after looking at `rv_cc.png` of run C-20261119-151502-cb831a8, before
  the run below): the accumulated defect at Kn = 10 reaches the binding margin only in the
  last 10-20 M before alpha_min < 0.3. Test of "trigger or consequence" from the histories
  (`rv_cc_onset.py`): t_dep = first time the central lapse alpha_probe of the collisional run
  falls 0.01 below that of its collisionless control (same model). Prediction: Kn = 10,
  t_dep in [100, 170] M for both models, injected energy at t_dep below 0.3 of the margin
  (< 3e-5 M0); Kn = 1, t_dep in [20, 50] M, injected energy at t_dep below the margin.
  Refuted if the injected energy at t_dep exceeds the margin in either Kn = 10 run. If it
  holds: the contraction starts before the defect reaches the size of the stability margin,
  so the defect is not needed to start it [JUDGEMENT; a smaller contribution is not
  excluded].
- outcome L13-L15 (run C-20261119-151502-cb831a8, 4 min on 2 cores; figures `rv_box2b.png`,
  `rv_cc.png`, `rv_king_onset.png` looked at). L13 held in every clause: (a) R1 36/36 files
  byte-identical; (b) R2 integer columns equal in all 25 records of the six cases, n_noroot
  = n_balance = 0, max_dlam = 0, dumps NRPCOLD2; (c) R3 integer columns identical to the
  release in all 3200 steps, my T2(b) ratio 0.999906-1.000096 (z_b -2.20..+2.92, z_a
  -2.10..+1.58), within 4.4e-16 of my recheck of the release run, sum_P within 7.8e-16, T1 at
  1.05e-7 of the bound, theta unchanged to 3.3e-13; (d) R4 mb8, mb64, rst0-rst2 byte-identical,
  seed 8 differs in every particle, 385554 collisions; (e) R5 identical n_tested and n_coll in
  all 200 steps of all four pairs, twin rate ratio 1.4172488 = alpha0 psi0^6, my analytic
  ratios 1.0000896, 0.9999717, 1.0000718, 1.0000525 (|z| <= 2.35), equal to the helper's to
  1e-6; (f) R6 particle mode: canonical energy +1.73 to +1.99e-21 of the sum per collision
  (both steps, all Kn); cell mode at Kn = 0.01, both steps pooled: +9.1e-11 of sum M W_p
  (+1.44e-10 of sum M H_p); columns 1-29 of the cell-mode Kn = 1 record identical to the
  release smoke run, columns 30, 31 differ by 1.7e-14, 1.3e-15; (g) collision part per tested
  pair particle/cell 1.676 (1.57-1.81 over the repeat combinations). Cosmetic: the third panel
  of rv_box2b.png has a clipped y-label and x-tick.
  L14 (a) held: accumulated defect to alpha_min < 0.3 is 1.567e-3, 1.749e-3 (Kn = 1),
  1.766e-4, 2.161e-4 (Kn = 10) of sum M W_p. (b) FAILED in one clause: the defect ratio
  Kn = 1 / Kn = 10 is 8.9 and 8.1 (in 7-10) but the ratio of collisions per particle is 5.4
  and 5.3 (13.44/2.48, 15.26/2.88), not 7-10; the refutation condition (a ratio within a
  factor 2 of 1) is not met, so neither a fixed injected energy nor a fixed number of
  collisions per particle marks the collapse. (c) held: at Kn = 10 the injected energy before
  alpha_min < 0.3 is 1.93e-4 and 2.34e-4 M0, 1.9 and 2.3 times the binding margin 1.000e-4 M0.
  L15 (a) held: tmb at b = 1 reproduces Z_c, R/M and E_b of the five King JSON models to
  3e-10; its eps maximum is at y0 = 0.3340322 (V3: 0.334032). (b) partly FAILED: the onset
  with the Juttner Gamma_1 at the energy-matched temperature lies at y0 = 0.321433 (Z_c =
  0.49105, R/M = 13.839; N = 600 and 1200 agree to 1.8e-8), with theta = p/n at 0.320542,
  inside the predicted [0.20, 0.334); but with F21's gamma = 1 + p/u the onset lies at
  y0 = 0.372062, ABOVE the collisionless maximum, not below (my prediction misremembered
  b = 0.1, where F21's 0.6348 also lies above the eps maximum 0.5404). The 50-percent call:
  J_E lies above 0.314, so CC2 is on the stable side of the fluid onset (by 0.0074 in y0,
  0.0055 in alpha_c), CC1 beyond it.
- outcome L16 (run C-20261119-151944-08f3220, `rv_cc_onset.png` looked at): the reading
  held, one clause FAILED. The central lapse of every collisional run falls steadily below
  its control's from the start; the drop reaches 0.01 at t_dep = 44.25 M (cc1_kn10), 46.0 M
  (cc2_kn10), 20.25 M (cc1_kn1), 21.25 M (cc2_kn1), after 0.35 and 1.6 collisions per
  particle; I predicted t_dep in [100, 170] M at Kn = 10 (FAILED, it is three times earlier).
  The injected energy at t_dep is 0.016 and 0.013 of the binding margin (Kn = 10) and 0.12,
  0.11 (Kn = 1), below the predicted bounds; it reaches the margin only at 180.4 and 201.6 M
  (Kn = 10), 54.0 and 58.7 M (Kn = 1), i.e. during the final run-up. So the release
  operator's defect is not what starts the contraction relative to the control; whether it
  speeds up the late phase is not decided by these runs. Reading [JUDGEMENT]: collisional
  heat transport out of the King core (gravothermal contraction) moving a model that lies
  within 0.006-0.015 in alpha_c of the onsets over the relativistic threshold is the leading
  physical hypothesis; the decisive runs are in `stage/REVIEW-wave2.md` section 7.

## 2026-11-19T15:40Z  session C-sidm lead (wave 2b)  commits 89522594..(this entry's commit)  runs C-20261119-151502-cb831a8, C-20261119-151944-08f3220

- did: merged main (decision 0016, harness of wave 2b); inspected and committed the wave-2
  lead's uncommitted stage files and manifest fields (0559b367; its C19/C20 PASS claims were
  premature and are corrected); checked the wave-2b box_rerun helper from its registered
  outputs (L13) and the first collisional cluster runs (L14, L16) with own readers; computed
  the Juttner fluid onset along the King family (L15); review sections 6-8 in
  `stage/REVIEW-wave2.md`; G0 and G1 checklists re-collected and filled, OPEN and EVIDENCE
  brought to wave 2b; TESTS.md 2a T12 twin note; nine outbox messages (kb, core x5, F-hills,
  orch x2); all eight inbox messages acknowledged; STATUS, HANDOFF, RISKS rewritten.
- found: every box_rerun number recomputed agrees (L13). The release operator's energy defect
  does not start the core contraction of the collisional King runs: the relative lapse drop
  reaches 0.01 at 44-46 M (Kn = 10) when 1.3-1.6 percent of the binding margin has been
  injected (L16). The King-family fluid onset (Juttner Gamma_1) is y0 = 0.32143, so CC1 is
  fluid-unstable and CC2 fluid-stable by 0.0055 in alpha_c, a margin smaller than the
  controls' numerical drift (0.018-0.033).
- changed my mind about: the defect as the likely cause of the Kn = 10 collapse (the helper's
  suggestion to rerun with coll_energy = particle stays, as D1, but for the late phase and
  the seed scatter); threshold_scan's reading "collisional threshold below y0 = 0.314" is not
  supported while the mesh drift exceeds the margin.
- failed predictions: L14(b) collisions-per-particle ratio (5.3-5.4, not 7-10); L15(b) F21
  gamma onset above, not below, the collisionless maximum; L16 t_dep at Kn = 10 (44-46 M, not
  100-170 M). Readings kept, as stated in the outcomes.
- open: D1-D3 (no card job submitted: the collisions-2 card executable awaits core's
  statement and the heat helper holds both card slots); review of the heat package when it
  ends; G1 remainder (`stage/G1/OPEN.md`). Card-hours used this session: 0.

## 2026-11-21T07:51Z  session C-sidm lead (wave 3, batch 2b)  predictions before the review runs

State found: worktree merged with main (core-v0.5); G0 signed (coord/GATES.md, 2026-11-20).
Packages of round 1 since the last lead: heat (closed), decisive (closed, job 5 pending),
drift and models (paused at the usage flag of 2026-11-20 22:33 UTC), note (cut at 22:35 UTC,
uncommitted files), verify_g1 (cut at 22:35 UTC; a helper of batch 2b works on it now in this
worktree). Card jobs: decisive job 5 (Slurm 4770, run C-20261121-062408-49fa14a) and drift (i)
(Slurm 4741, run C-20261120-222533-ce50a86) both COMPLETED (sacct), both closed by me with
`nrpic-run finish` at the start of this session. No card job of the owner queued. This lead
session spends no card time (none named in its task).

Predictions (written before the runs; own code in `stage/review_wave3/`):
- L17 decisive job 5 (helper's prediction, decisive/JOURNAL.md entry 10, stands as written):
  the cell seeds 2 and 3 of CC1 at Kn = 10 collapse (linear crossing of alpha_min = 0.3)
  within 1.5 M of each other and of 184.02 M. Mine [JUDGEMENT]: both in [182.5, 186.5] M;
  the mode effect is NOT shown by the decision rule (|mean(part) - mean(cell)| < 3 sigma),
  and the difference is below 1.5 M. Refuted if a cell seed lies outside [181, 187] M or if
  the rule shows a mode effect.
- L18 own reader of `cc.nrpic.hst` (time, alpha_min; linear interpolation of the first
  crossing of 0.3) reproduces the t_c of every D1/D3 run in the helper's summary.json within
  0.01 M; the D3 control d3_kninf cosine fit A(1 - cos 2 pi t/P) + c gives P within 5 percent
  of 282 M and A within 10 percent of 0.0022. Refuted by a larger difference.
- L19 drift (i) cc2_kninf_M8 (helper's M8.1-M8.4 of drift/JOURNAL.md entry 2 stand as
  written). Mine [JUDGEMENT, 50 percent]: R = A(M/8)/A(M/4) in [0.4, 1.0]; the period
  P(M/8) within 15 percent of 355 M; the run reaches 300 M with np = 1e5 and sum_m
  bit-identical. Refuted if R is outside [0.4, 1.0] (sharp side: R > 1.0 means the finer mesh
  does not reduce the excursion).
- L20 drift entry 6 on decisive's d3_kninf: P(0.26) in [260, 380] M and below P(CC2) = 355 M,
  A(0.26) < 0.0086 (helper's prediction; judged here from L18's fit).
- L21 heat: a rerun of `heat/scripts/summary_c6.py` reproduces the numbers of
  C-20261121-030328-e3ffc6d exactly (same inputs); my own weighted mean of the per-seed T7
  values at theta 0.003 agrees with 1.0250 +- 0.0025 to 1e-4. Refuted by a difference.
- L22 models: a rerun of the unit tests `models/test_growth_v2.py` passes U1-U5 with the
  numbers of C-20261120-222454-8721534; figures drawn by me from the two npz files show
  (a) the v2 synthetic fits centred on the true rate with the 'first' reference biased high
  by 2-5 percent, (b) concave ln|d| on the three y_c = 0.5 compensated samples. Refuted by a
  different U-test outcome or by figures that contradict the helper's numbers.

## 2026-11-21T08:05Z  session C-sidm lead (wave 3, batch 2b)  outcomes L17-L22

Runs: decisive analysis C-20261121-075202-1a37fb9, own recheck C-20261121-075336-49f92da,
drift analysis C-20261121-075359-26e3b31, own heat/models recheck C-20261121-075535-b35b8fb;
figures `rv_clusters.png`, `fig_cc2_M8.png`, `rv_heat.png`, `rv_models.png` looked at.
- L17 FAILED. CC1 Kn = 10 cell seeds 2, 3: t_c = 185.29 and 178.86 M; s3 lies outside my
  [182.5, 186.5] M and outside the refutation bound [181, 187] M. The mode effect is not shown
  (ratio 1.32 < 3), as I predicted, but the difference 2.66 M is above my 1.5 M. Reading: the
  collapse time of the threshold model scatters by about 3 M from seed to seed (sd of five
  runs 2.83 M), fifteen times CC2's 0.21 M.
- L18 HOLDS. My t_c equal the package's to the last digit for all 15 runs; my grid cosine
  fits give P = 399.25, 355.5, 282.25 M and A = 0.01541, 0.00859, 0.00221 (package 399, 355,
  282 M; 0.0022).
- L19 FAILED. R = A(M/8)/A(M/4) of CC2's control is 0.22 (cosine), 0.25 (sine with trend),
  0.10 (largest 20 M mean), below my [0.4, 1.0]; the M/8 record has no cosine form (my grid
  fit runs to the edge) and contracts slowly after 200 M (alpha_c -0.0041 at 300 M). The
  helper's M8.1 holds, M8.2 fails (drift/JOURNAL.md entry 8). The M/4 excursion is numerical.
- L20 HOLDS (P(0.26) = 282 M in [260, 380] and below 355 M; A = 0.0022 < 0.0086).
- L21 HOLDS. Rows and extrapolations of T7 equal the package's within 3e-16: 1.02497 +-
  0.00251, 1.09571 +- 0.00514, 0.99145 +- 0.00350 at theta 0.003, 0.1, 1.
- L22 HOLDS. v2 medians on synthetic signals within 0.04 percent of the truth; 'first' biased
  high (+7.5, +6.1, +1.6 percent in the median); ln|d_s| of the three y_c = 0.5 compensated runs
  concave from the start (local slope 0.07-0.08 falling below 0.01 per M by 100 M).

## 2026-11-21T08:20Z  session C-sidm lead (wave 3, batch 2b)  commits f96faec0..(this entry's commit)  runs C-20261121-075202-1a37fb9, C-20261121-075336-49f92da, C-20261121-075359-26e3b31, C-20261121-075535-b35b8fb

- did: merged main (core-v0.5); closed the two finished card jobs (decisive job 5, drift run
  (i)) with `nrpic-run finish` and analysed them with the packages' scripts; rechecked heat,
  decisive, drift and models from their registered outputs with own code
  (`stage/review_wave3/`); drew the models validation figures the paused package lacked;
  committed the note's figures and schematics that are byte-identical to its registered run
  (the rest of the note's uncommitted work left to it); review `stage/REVIEW-wave3.md`;
  outcome entries in `decisive/JOURNAL.md` (15) and `drift/JOURNAL.md` (8), their READMEs;
  `collide/TESTS.md` section 2b (wording of T6-T8, no criterion loosened); G1 checklist
  re-collected and judged (C2, C6, C9, C10, C14 now PASS; C16, C17 open), EVIDENCE, OPEN,
  REVIEW updated, verify and report; five outbox messages (orch x2, core x2, kb); eight inbox
  messages acknowledged; STATUS, HANDOFF, RISKS rewritten.
- found: heat confirmed to the last bit (C6 met). The threshold model's collapse time scatters
  by about 3 M between seeds (cell seed 3 at 178.86 M). The outward excursion of the M/4
  controls is a mesh effect (0.10-0.25 of it left at M/8), and the M/8 control contracts
  slowly after 200 M instead. The growth rate on the first paper's runs is window-dependent
  (concave ln d), so rates are quoted with their interval.
- changed my mind about: the reading of wave 2b that the controls' excursion is a physical
  pulsation of the model (drift D1): at M/8 it is mostly gone; and about one seed being
  enough for collapse times (true for CC2, not near the threshold).
- failed predictions: L17 (CC1 cell seeds within [182.5, 186.5] M), L19 (R in [0.4, 1.0]);
  the helpers' decisive entry 10 (job 5) and drift M8.2 failed as well.
- open: note G1 sections (C16), VERIFIER.md (C17, verify_g1 working), models step 5, drift
  runs (iii) and (v), decisive D2, T10b for T4, the CE deficit series at G2. Card-hours used
  this session: 0 (round 1 of wave 3 in total 4.13).

## 2026-11-21T15:50Z  session C-sidm lead (wave 3, batch 4a)  predictions before the review runs

State found: worktree clean, merged with main (core-v0.6, rulings 0021, 0022; nothing in them
for Track C). Packages finished since the lead of batch 2b: verify_g1 (VERIFIER.md, commit
8329cf06), note v1 (batch 3, commit 2484c878), drift (batch 3, partial: run (vi) Slurm 4804
RUNNING since about 15:37 UTC, run (v) not submitted). Pause flag absent. This lead spends no
card time of its own; run (v) of drift (0.3 card-hours, inside the package's cap of 3.0) may be
submitted when (vi) has ended.

Predictions (own code in `stage/review_wave3/rv_batch4a.py`, written before it runs):
- L23 (verifier item 1) My own reader of `box.coll.hst` of the T10 runs (release
  C-20261115-165902-f9b1c8f): total n_coll of mb1, mb8, mb64 = 385554, of seed8 = 385838.
  Refuted if seed8 has 385554 (then REVIEW-wave2.md:49 was right).
- L24 (verifier item 2) Rerunning `verify_g1/v5_t9ks.py` from the registered T9 outputs
  reproduces its JSON numbers to the printed digits: KS p = 1.7e-4 for the light class of seed 3
  against the temperature of the initial energy, p >= 0.084 against the other two references.
  Refuted if a number differs.
- L25 (note) The checker of note/README.md with --compile reports 0 undefined references and
  citations and the PDF has 16 pages; six ledger rows (decisive t_c 184.02, 185.29, 178.86 M;
  drift ratios 0.22, 0.25, 0.10; card T8 changes -0.0052, -0.0001, -0.0104; growth-fit bias
  6.9e-4) equal the JSON of their runs to the printed digits. Refuted by any mismatch.
- L26 (drift run (iii), own reader of `cc.nrpic.hst`, centred 20 M running mean): largest 20 M
  mean of alpha_probe - alpha_probe(0) for CC1 on M/8 0.0046 +- 0.0003 at 196 +- 6 M, on M/4
  0.0330 +- 0.0005; ratio 0.138 +- 0.01; +-5 M mean at 300 M -0.0020 +- 0.0003; H-norm2 mean
  over 100-300 M 7.9e-3 +- 0.3e-3 (M/8) and 8.5e-4 +- 0.3e-4 (M/4). Refuted outside.
- L27 (drift D2, own reader of traj.bin/trajmet.bin from docs/FORMATS.md and a different
  coherent part: 800 cells of 20 x 20 quantiles in E_K(0) and |x x u|(0) times the sign of x.u):
  D over 25-300 M within 25 percent of the package's (4.04, 6.47, 3.79, 5.83 e-8 per M) for
  all four controls; D(M/8)/D(M/4) in [1.2, 2.2] for both models. Refuted otherwise; a D of
  mine well below the package's would mean its 200 cells leave coherent motion in the
  'incoherent' part.
- L28 (drift run (vi), if it ends in this session; the helper's VI.1-VI.4 stand as written).
  Mine [JUDGEMENT, 55 percent, against the helper's VI.2]: the slow contraction of CC2 on M/8
  does not turn within the segment; the 40 M mean of alpha_c - alpha_c(0) at the segment end
  (about 650-700 M) lies in [-0.015, -0.004], and alpha_c stays above 0.5 (no collapse).
  Refuted by a minimum of the 40 M mean before the end followed by a rise of more than 0.002,
  or by a value outside the interval.

## 2026-11-21T15:55Z  session C-sidm lead (wave 3, batch 4a)  outcomes L23-L27

- L23 HOLDS (run C-20261121-155049-ecf8893): T10 collisions 385554 (mb1, mb8, mb64), 385838 (seed8).
- L24 HOLDS (run C-20261121-155116-ba83d16): the rerun of verify_g1/v5_t9ks.py gives a JSON
  identical to the verifier's run C-20261121-081415-b8c9d29 (light class, seed 3: KS p 1.72e-4
  at the theta of the initial energy).
- L25 HOLDS (run C-20261121-155226-8ea9e47; the first attempt C-20261121-155220-5c0d480 FAILED on
  a JSON key of my script): checker --compile 0 undefined references and citations, 1 overfull
  box of 1.09 pt, 16 pages; six ledger rows equal their runs' JSON.
- L26 HOLDS: CC1 M/8 largest 20 M mean 0.00455 at 195.75 M, M/4 0.03295, ratio 0.138; at 300 M
  -0.00202; H-norm2 7.86e-3 (M/8), 8.53e-4 (M/4).
- L27 HOLDS: D with my 800 equal-count (E_K, |x x u|, sign x.u) cells is 0.97-1.01 of the
  package's (25-300 M); D(M/8)/D(M/4) = 1.67 (CC1), 1.54 (CC2).

## 2026-11-21T16:36Z  session C-sidm lead (wave 3, batch 4a)  outcome L28

- L28 FAILED on its interval, held otherwise (runs C-20261121-163109-c8fff37 own reader;
  C-20261121-163135-57f9296 package's compare.py; first attempt C-20261121-163051-16356b2 FAILED
  on the header-less history of the restarted run): CC2 on M/8 does not turn by 680 M and does
  not collapse (alpha_c >= 0.652), but the 40 M mean at the end is -0.0216, below the predicted
  [-0.015, -0.004]. The helper's VI.2 (bounded) failed as well; VI.1, VI.3, VI.4 hold
  (drift/JOURNAL.md entry 16).

## 2026-11-21T16:45Z  session C-sidm lead (wave 3, batch 4a)  commits bf279bd3..(this entry's commit)  runs C-20261121-155049-ecf8893, C-20261121-155116-ba83d16, C-20261121-155226-8ea9e47, C-20261121-163109-c8fff37, C-20261121-163135-57f9296 (failed: C-20261121-155220-5c0d480, C-20261121-163051-16356b2)

- did: merged main (core-v0.6; rulings 0021, 0022, nothing for Track C); predictions L23-L28
  before any check; own recheck script `stage/review_wave3/rv_batch4a.py` (own readers of the
  histories and trajectory files, own coherent part for D2) and `rv_note_b4a.py`; reviewed
  verify_g1, note v1 and drift batch 3 into `stage/REVIEW-wave3.md` sections 9-12; answered
  every item of VERIFIER.md (REVIEW-wave2 count corrected, `collide/TESTS.md` 2c, heat README,
  box_tests README, scope/REFERENCES, G0 locator appended); closed run (vi) (Slurm 4804) and
  analysed it with the package's compare.py and own code (drift entry 16); G1 checklist C9,
  C14, C16-C19 updated, OPEN, EVIDENCE, REVIEW, STATUS of G1 rewritten, collect, verify (one
  FAIL: the (vi) manifest was still 'submitted' at the snapshot commit; rerun after finishing
  it); four inbox messages acknowledged; outbox to orch (next batch; G1 review); STATUS,
  HANDOFF, RISKS rewritten.
- found: the verifier's numbers stand; no number of the track recomputed by it or by me is
  wrong. The CC1 control on M/8 keeps 0.138 of its M/4 excursion (both models: the excursion
  is the mesh). The package's energy-diffusion rates survive a different coherent part
  (0.97-1.01). The stable CC2 control on M/8 contracts steadily to 680 M (alpha_c -0.022, r50
  -6.3 percent), no turn, no runaway.
- changed my mind about: whether M/8 at N = 1e5 is fit for block A; it is not until the
  contraction's source is known (run (v) next).
- failed predictions: L28 (interval); drift VI.2; earlier in batch 3, M8.2', M8.5', D2.2. Failed
  runs: C-20261121-155220-5c0d480 and C-20261121-163051-16356b2 (my scripts).
- open: run (v); block A; decisive D2; models step 5; T5/T8 second check (G2 verifier); the G1
  review. Card-hours used by this session: 0 (run (vi), 0.87, was the drift package's).

## 2026-11-21T20:25Z  session C-sidm lead (wave 3, batch 5: cards first)  predictions before any submission

Aim of the session (decision 0025 items 3-5): leave the cards loaded with this owner's long
runs, registered and sequenced. All runs below are collisionless or collisional King
clusters without a black hole at the start, so the relaxed lapse (`<z4c> lapse_leak`) is not
used in any of them (item 3). Executable: release core-v0.6 card build
(`/data/haiyangw/nrpic/.work/build_gpu_v06/src/athena`) except run (v), which forms a pair
with the N = 1e5 control of wave 2 (C-20261115-171059-4b70228, core-v0.3) and keeps its
executable so that only N differs. Package of the new runs: `tracks/C-sidm/longruns/`
(README there has the run table and the sequencer).

Reference quantities, windows and noise model, named now, before any of the runs:
- alpha_c(t): central lapse of the history (`cc.nrpic.hst`), as in drift; alpha_min(t);
  areal half-mass radius r50 of the trajectory files (drift `compare.py`).
- Collapse: alpha_min < 0.3 (SCAN.md), time t_c by linear crossing of the history.
- Kick signal: Delta(t) = alpha_c,kick(t) - alpha_c,ctrl(t), kicked run minus the unkicked
  control of the same model, seed, mesh, N and executable; window means over the 100 M
  windows [0,100], ..., [500,600] M.
- Noise model: sigma_w = max(sample sd of the window mean of Delta over the three seeds of
  the threshold model, rms ripple of the control about a 50 M running mean); a signal is a
  window mean beyond 3 sigma_w. Until the seeds exist, sigma_w = 2.5e-3 [JUDGEMENT: the
  ripple of N = 1e5 on M/8 is 8e-4 (drift N.2) and the two-model ripple is only weakly
  shared (drift M8.5', +0.25), so three times the ripple].

R(v) drift run (v): cc2_kninf at N = 1e4 on M/4, 300 M, core-v0.3 (the drift package's
deck `drift/inputs/cc2_kninf_N1e4.athinput`, list `job_v.list`). Predictions N.1-N.6 of
`drift/JOURNAL.md` entries 5, 11 and 14 stand unchanged; the decisive ones are N.4 and N.6
(contraction of the N = 1e4 run against the N = 1e5 control below -0.003 in alpha_c at
280-300 M and dE_K below -0.005 if noise relaxation; within +-0.003 / +-0.002 if not).
Criterion for block A: if N.4 and N.6 say noise relaxation, block A at N = 1e5 is read
only through Delta (control subtracted) and the threshold seeds are repeated at N = 1e6
later; if not, N = 1e5 stands.

H heat series (conductivity against cell size and step, `heat/README.md` "Open, for G2"):
theta = 0.003, eps = 0.2, 4e6 particles, transverse 16 x 16 cells; k lambda = 0.2 with two
new seeds (6, 7) at dx = lambda/8, lambda/4, lambda/2 and dt = 0.05 t_coll at lambda/8
(8 cases); k lambda = 0.1 with seed 6 at dx = lambda/8, lambda/4, lambda/2 (3 cases).
Predictions [JUDGEMENT, from heat finding 8: c = 0.115 +- 0.025 per (dx/lambda)^2]:
H.1 kappa(lambda/2)/kappa(lambda/8) - 1 in [+0.010, +0.050] at k lambda 0.2 (seed mean);
H.2 zero-cell extrapolation kappa_0/kappa_1 in [0.975, 1.020]; H.3 dt 0.05 against 0.1 at
lambda/8 changes kappa by less than 1 percent (|z| < 2 with the seed scatter); H.4 the
k lambda 0.1 slope agrees with the 0.2 slope within 2 sigma. Refuted: H.1 outside the
interval (no trend or a trend twice that of the card T8), H.3 above 2 percent.

D2 decisive D2 (is the collisional contraction set by the collision cell?): CC2 (y0 = 0.314,
seed 1 particle file of wave 2) on the M/8 mesh (drift `m8_deck`), Kn = 10,
`coll_energy = particle`, `coll_cell_factor` f = 1, 2, 4 (collision cells M/8, M/4, M/2;
mean occupation about 0.3, 2.3, 18 particles at the centre), collision seed 1; f = 2 also
with collision seed 2; collisionless control cc2_kninf_M8 of the same particle file on the
same executable; 300 M each. On M/4 with f = 1 (cells M/4) CC2 collapsed at t_c = 206.64 M
(mean of the particle-mode seeds, decisive README) after 2.89 collisions per particle.
D2.1 [JUDGEMENT] collisions per particle per M independent of f within 5 percent (the
operator samples pairs without bias when cells are far below the mean free path); D2.2
t_c(f = 2) on M/8 within 10 percent of 206.64 M; D2.3 t_c(f = 1) and t_c(f = 4) within 10
percent of t_c(f = 2), and the f = 2 seed pair within 2 M. Refuted (the contraction is a
cell artefact) if t_c or the collision rate moves by more than 20 percent between f = 1
and f = 4. The control: no collapse in 300 M; alpha_c - alpha_c(0) at 280-300 M in
[-0.010, +0.002] (drift run (i) on v0.3: -0.004 at 300 M).

A block A of the threshold scan (collisionless threshold of the King b = 1 sequence, y_max
= 0.334032): M/8 mesh, N = 1e5, 600 M, coherent one-percent radial kicks of make_scan.py;
models y0 = 0.324, 0.334032, 0.344; seeds 1, 2, 3 at 0.334032 and seed 1 at the two others;
for every (model, seed) the unkicked control and the kicks in and out (15 runs). Predictions
[JUDGEMENT]:
A.1 y0 = 0.344 (unstable side): kin collapses (alpha_min < 0.3) before 600 M; kout has
Delta > +3 sigma_w in the windows 400-600 M and rising (migration outward).
A.2 y0 = 0.324 (stable side): neither kick collapses; |Delta| of the window means 400-600 M
below 3 sigma_w or not growing from window to window (bounded oscillation).
A.3 y0 = 0.334032: no collapse of any of the nine runs before 600 M; the signs of Delta of
kin (negative) and kout (positive) hold in at least two of the three seeds in the window
500-600 M; the seed sd of Delta at 500-600 M is below 3e-3.
A.4 controls: none collapses; alpha_c - alpha_c(0) at 500-600 M in [-0.040, -0.005] for all
three models (the M/8 contraction of drift run (vi), -0.019 at 600 M for y0 = 0.314,
larger for the more compact models).
Refuted: A.1 by no collapse and no falling Delta of 0.344 kin (threshold above 0.344 on this
mesh, or growth slower than 600 M); A.2 by a collapse of 0.324 kin (threshold below 0.324 or
the mesh contraction destabilises); A.4 by a control that collapses on its own (then M/8 at
N = 1e5 is unfit for the scan and the bracket cannot be read from it).

T timing: before the long chains, one batch job of short segments on core-v0.6 (the
threshold control and the three D2 decks, 20 M and 10 M) measures the step time. Prediction:
8.2-8.4 s per M for the collisionless M/8 deck (core-v0.3: 8.22-8.30, drift entry 9);
collisional f = 1 at most 1.5 times that. If the collisionless step is above 12 s per M the
sequencer is stopped and the chains re-sized (MAX_SEGMENTS 4 holds up to 20 s per M at 600 M).
Card-hours expected: (v) 0.3, T 0.15, H 0.5, D2 5 x 0.8 = 4, A 15 x 1.4 = 21; about 26 of the
37.6 left in the allotment of 45 toward G2.

## 2026-11-21T20:35Z  session C-sidm lead (wave 3, batch 5: cards first)  commits 12183c5d..(this entry's commit)  runs C-20261121-202459-12183c5 (card, pending), C-20261121-202552-8f91fb3, C-20261121-202552-883e2c2, C-20261121-203004-c2c14e7 (card, pending), C-20261121-203340-75ea9bc

- did: merged main (decision 0025: G1 of C signed with reservations; cards first); wrote the
  predictions, criteria, windows and noise model of every run before submission (entry
  20:25Z); submitted drift run (v) (Slurm 4826, core-v0.3); made the particle files of seeds
  2 and 3 of the threshold model (C-20261121-202552-8f91fb3) and the heat-series particle
  files and lists (C-20261121-202552-883e2c2); wrote 15 block A decks (M/8, 600 M, control
  and kicks, seeds 1-3 at y0 = 0.334032, seed 1 at 0.324 and 0.344), five D2 decks (M/8,
  Kn = 10, coll_cell_factor 1, 2, 4, and the control) and a timing list; wrote the sequencer
  `longruns/seq/seq.sh` and its queue (23 items) and started it with setsid nohup (pid in
  scratch/C-sidm/seq/seq.pid); it submitted the timing job (Slurm 4829); wrote the block A
  reader `longruns/scripts/blockA_delta.py` and smoke-tested it on two drift M/8 controls
  relabelled as a pair (C-20261121-203340-75ea9bc, figure read: the control's alpha_c -
  alpha_c(0) is -0.004 at 300 M as in drift entry 16, ripple rms 7.6e-4 against the 8.0e-4 of
  N.2; code path only, no block A result); review section 13; outbox to orch
  (cards-loaded-batch5); STATUS, HANDOFF, RISKS (rows 5, 18-20).
- changed before submission, recorded here: the sequencer's stop rule for the timing job is
  "slower than about 18 s per M" (0.45 of the core-v0.3 zone-cycle rate), not the 12 s per M
  of prediction T, because four 50-min segments hold 600 M up to about 20 s per M; T's
  predicted interval (8.2-8.4 s per M) is unchanged and is judged when the job ends.
- found: nothing new in science; the decks and kicks check (review section 13).
- failed predictions: none judged this session (no run ended). Failed runs: none.
- open: everything queued; judge R(v), T, H, D2, A as the runs end; G2 stage package; the
  question to orch on the pause flag. Card-hours used by this session: 0 so far (all jobs
  pending at 20:35 UTC); expected about 26 over the coming days.

## 2026-11-24T12:59Z  session C-sidm lead (batch 11, analysis round)  state found; resume rule before any resubmission

State found at 12:51Z: the sequencer (pid 2542601) had submitted all 23 queue items; 13 card
runs ended DONE (run (v), timing, heat_C1, heat_C2, A334s1c/i/o, A344s1c/i, A324s1i, D2ctl,
D2f1s1, D2f2s1, D2f4s1), ten chains closed FAILED with "MAX_SEGMENTS reached" and one
(A334s3o) was on its last allowed segment. Cause of the ten failures, from the chain event
logs and `sacct -a`: from 2026-11-23 about 13:00 PST another user submitted short jobs to
the higher-priority partition `priority` every 5-20 min (still at 04:54 PST today);
`PreemptMode = CANCEL` and AthenaK writes no restart on SIGTERM, so each preemption threw
away the work since the last restart (every 100 M, about 14 min of card time) and used one of
the 4 (or 2) segments. None of the ten failed by the physics or by the guard: each event log
ends "STATUS FAILED (MAX_SEGMENTS=4 reached)" (D2f2s2: 2). t_end of the cut runs: A344s1o
420.5, A324s1c 19.5, A324s1o 407.8, D2f2s2 116.5, A334s2c 249, A334s2i 245, A334s2o 190,
A334s3c 0.25, A334s3i 103.8, A334s3o 101.3 M.

Rule for the continuation, fixed now, before any resubmission (task: continue a cut run from
its newest restart file, never repeat it):
- each cut chain is continued in place (same run directory, same executable, same deck, same
  process name, JOB_NAME = its run id) from its newest restart file (last_time read from the
  file: 0, 400, 400, 100, 200, 200, 100, 100, 0 M for the nine above, in that order), with
  `output2/dt=10` on the command line so that a restart is written every 10 M (about 80 s of
  card time; disk about 1.1 GB per restart, 18 TB free) and with 12-20 more segments allowed;
  the manifest gets a `continuations` entry and is re-closed with `nrpic-run finish --status`
  when the chain ends. A334s3o (pending job 5147, which would have failed at once on its
  segment cap) had its chain/config.sh edited at 12:55Z: MAX_SEGMENTS 4 -> 24 and
  EXTRA_ARGS output2/dt=10 (original kept in scratch/C-sidm/tmp/config.A334s3o.orig).
- the restart cadence changes no physics; restarts are exact for the particle state and the
  mesh state differs at round-off with outflow faces and refinement (decision 0027 item 3), so
  a continued run is read like any card run with deposition: against its control, never byte
  for byte. The history reader (blockA_delta.py read_hist) keeps the later segment where a
  restart rewrote times already written.
- the predictions of the continued runs are those written before the first submission
  (entry 2026-11-21T20:25Z: A.1-A.4, D2.1-D2.3); nothing in them is changed.
- the sequencer is changed (decision 0026 item 2): it submits while the pause flag exists and
  logs that it does; it logs why the next item waits whenever the reason changes (decision
  0030 item 4); it knows `resume` items (queue.txt, batch-11 block).
- card-hours: 17.59 used by the batch-5 queue so far (sum of the closed manifests) plus about
  0.6 for A334s3o; remaining work about 3850 M, about 9 card-hours at 8.3 s per M plus the
  preemption overhead; 45 - 7.41 - 17.59 = 20.0 left of the G2 allotment before it.

## 2026-11-24T13:12Z  session C-sidm lead (batch 11)  outcomes of R(v), T, H, D2 and block A (interim), judged against entry 2026-11-21T20:25Z

Every number below comes from a registered analysis run of this session; the figures were
read before the judgement.

R(v), drift run (v) (C-20261121-202459-12183c5, N = 1e4 on M/4, against the N = 1e5 control
C-20261115-171059-4b70228; analyses C-20261124-130021-5c9c207 compare.py, -130222-6a4924d
diffusion.py; figures fig_cc2_N.png, fig_diffusion.png read):
- N.1 H-norm2(0) ratio 9.95 (and 9.97 over 100-300 M): in [5, 20]. HOLDS.
- N.2 ripple ratio 3.22: in [2, 5]. HOLDS.
- N.3 amplitude ratio 1.51 (cosine fit; 1.44 sine with trend, 1.51 maximum of the 20 M
  mean): in neither interval ([0.75, 1.33] mesh-set, about 3 noise response). FAILED. The
  period part holds (310 M against 355 M, 13 per cent shorter, within 20).
- N.4 alpha_c(1e4) - alpha_c(1e5): about -0.009 at 300 +- 5 M (-0.0049 against +0.0041),
  below -0.003, with sum mW/sum m rising relative to the control (+0.0025 against -0.0016 at
  300 M). HOLDS by its letter (noise-relaxation branch). The caveat written with it applies in
  a form it did not foresee: the difference is not monotonic; the N = 1e4 run pulsates with a
  1.5 times larger amplitude and a 13 per cent shorter period (it is above the control until
  about 230 M), so the 280-300 M window reads phase as well as trend [JUDGEMENT].
- N.5 D(1e4)/D(1e5) = 11.07 (25-300 M) and 11.41 (25-75 M): in [5, 15]. HOLDS: the energy
  diffusion of the particles scales as 1/N.
- N.6 mean dE_K of (v) minus that of the control at 300 M = -0.00507: below -0.005. HOLDS,
  by 1.4 per cent of the bar; at 275 M it was -0.0044 and at 250 M -0.0018, i.e. the same
  phase effect as N.4.
- Criterion R(v) (entry 20:25Z): N.4 and N.6 say noise relaxation, so block A at N = 1e5 is
  read only through Delta against its control, and the threshold seeds are to be repeated at
  N = 1e6. Recorded as decided by the rule; the reservation (phase, one seed, M/4 not M/8) is
  carried, and the N = 1e6 control on M/8 queued below tests the reading where it matters.

T, timing (C-20261121-203004-c2c14e7; analysis C-20261124-131129-e93be29, fig_step_time.png
read): collisionless M/8 deck 8.29 s per M: in [8.2, 8.4]. HOLDS. Collisional f = 1, 2, 4:
8.55, 8.53, 8.57 s per M, ratio 1.03 at most 1.5. HOLDS. Production segments of eight chains:
medians 7.7-8.3 s per M.

H, conductivity series (heat_C1 C-20261121-210524-36a658e, heat_C2 C-20261122-183030-2f3a471;
reductions C-20261124-130338-43b5ffa, -130338-c4ac85e; analysis C-20261124-131012-f920f45,
fig_heat_series.png read; noise of one case sqrt(s2/N) from the T7 seeds of
C-20261120-223001-eb81eb7, 0.0031 at N = 4e6):
- H.1 f(lambda/2)/f(lambda/8) - 1 at k lambda 0.2, seed mean: +0.0196 +- 0.0042: in
  [+0.010, +0.050]. HOLDS.
- H.2 f0 of f = f0 + c (dx/lambda)^2 at k lambda 0.2: 1.0149 +- 0.0026, c = 0.101 +- 0.017
  (chi^2 6.3 for one degree of freedom: seed 7 at lambda/4 lies 2.6 sd low): in
  [0.975, 1.020]. HOLDS.
- H.3 dt 0.05 against 0.1 at lambda/8: +0.45 +- 0.42 per cent (z 1.07; seeds +0.63 and
  +0.27): below 1 per cent and |z| < 2. HOLDS.
- H.4 c at k lambda 0.1: 0.055 +- 0.017 against 0.101 +- 0.017 at 0.2: z = -1.85, within 2
  sigma. HOLDS (narrowly).
- Consequence [JUDGEMENT, arithmetic on the two f0]: extrapolated to zero cell and to
  k lambda -> 0 in (k lambda)^2, kappa/kappa_1 = (4 x 1.0187 - 1.0149)/3 = 1.020 +- 0.004,
  equal to the G1 value 1.0208 +- 0.0034 (unweighted processor seeds). The cell term is
  quadratic, about +2 per cent at dx = lambda/2. G1 reservation 1 (conductivity not settled
  at the per-cent level) is answered by this series.

D2, collision-cell size (D2ctl C-20261122-103854-4670b59, f1s1 -144455-6e0992e, f2s1
-141414-399ad97, f4s1 -181011-60baef9, f2s2 -20261124-035054-c06503f cut at 116.5 M;
analysis C-20261124-130442-0819c88, fig_d2.png read; one failed analysis run of my own
script, C-20261124-130433-e84cb43, tuple unpacking, rerun):
- t_c (alpha_min = 0.3): f = 1 164.01 M, f = 2 163.41 M, f = 4 165.97 M; collisions per
  particle before t_c 2.23, 2.21, 2.19; collision rate per particle 0-100 M 8.85e-3,
  8.86e-3, 8.68e-3 per M.
- D2.1 rate independent of f within 5 per cent: f1/f2 0.999, f4/f2 0.979. HOLDS.
- D2.2 t_c(f = 2) on M/8 within 10 per cent of 206.64 M (M/4): 163.41 M, 21 per cent
  earlier. FAILED. The collisional collapse time depends on the mesh between M/4 and M/8.
- D2.3 t_c(f = 1), t_c(f = 4) within 10 per cent of t_c(f = 2): 0.4 and 1.6 per cent. HOLDS.
  The seed pair at f = 2 is open (seed 2 cut at 116.5 M; D100 0.0504 against 0.0536).
- Refutation rule (t_c or rate moving by more than 20 per cent between f = 1 and f = 4):
  not met (1.2 and 2.0 per cent). The collisional collapse of CC2 at Kn = 10 is not an
  artefact of the collision cell between cells of M/8 and M/2.
- Control: no collapse in 300 M (alpha_min >= 0.671), alpha_c - alpha_c(0) at 280-300 M =
  -0.0049: in [-0.010, +0.002]. HOLDS.

A, block A, interim (all 15 runs; ten were cut by preemption and are being continued;
analyses C-20261124-130506-2ddce1f and, with the ripple taken before 400 M,
C-20261124-130634-3338d9b; fig_blockA.png read):
- Controls collapse on their own: y0 = 0.334032 seed 1 at t_c = 534.8 M (alpha_c change
  +0.0024, +0.0044, -0.0024, -0.0188, -0.093 at 100-500 M), y0 = 0.344 at 549.3 M (+0.0031,
  +0.0073, +0.0045, -0.0076, -0.060). The y0 = 0.324 control is being continued from t = 0.
- Kicked runs, seed 1: y0 = 0.334032 kin t_c = 294.5 M, kout t_c = 449.0 M (the outward kick
  first expands, +0.016 at 100 M, then contracts and collapses 86 M before its control);
  y0 = 0.344 kin t_c = 229.8 M, kout not collapsed at 420.5 M (alpha_c -0.046 at 400 M and
  falling; being continued); y0 = 0.324 kin no collapse to 600 M (alpha_c between -0.007 and
  -0.028), kout -0.054 at 400 M and falling (cut at 407.8 M; being continued).
- A.4 (controls do not collapse; contraction at 500-600 M in [-0.040, -0.005]): FAILED (two of
  the three controls collapse before 600 M). By the refutation written with it, M/8 at
  N = 1e5 over 600 M is unfit for the scan, and the bracket cannot be read from block A.
- A.3 (no collapse of the nine threshold runs before 600 M): FAILED (seed-1 control, kin and
  kout all collapse). Seeds 2 and 3 are being continued.
- A.1 (y0 = 0.344: kin collapses before 600 M; kout has Delta > +3 sigma_w and rising in
  400-600 M): kin part HOLDS (229.8 M); kout part FAILED on the windows that exist (Delta
  +0.0089, +0.0183, +0.0076, -0.0167, -0.0463: falling and negative from 300 M).
- A.2 (y0 = 0.324: neither kick collapses; |Delta| 400-600 M bounded): kin part HOLDS so far
  (no collapse to 600 M); kout and Delta wait for the control and kout continuations.
- Noise model: the rule named before the runs (sigma_w = max(seed sd, ripple)) gives 0.07
  over the whole record because two controls and the seed-1 kin collapse inside windows; with
  the ripple before 400 M (post hoc, labelled in the reader) the ripple is 8e-4 and the seed
  sd of the pre-collapse windows 1.3e-4 (0-100 M) and 4.7e-3 (100-200 M, kin, two seeds).
- What block A does show [JUDGEMENT]: on this mesh and N the inward kick advances the collapse
  by 240 M at y0 = 0.334032 and by 320 M at 0.344, i.e. more for the more compact model, as an
  instability with a shorter growth time would; but the control collapse means that the
  secular contraction of the scheme (or of the particle noise) decides the fate within 600 M.
  No cause is named: the N = 1e6 and M/16 runs below are the ones in which each reading can
  fail.

## 2026-11-24T13:14Z  session C-sidm lead (batch 11)  follow-up runs: predictions before submission

Why these runs: block A failed A.3 and A.4 because the controls of the threshold model and of
y0 = 0.344 collapse on their own on M/8 at N = 1e5 (534.8 and 549.3 M), and D2 failed D2.2
because the collisional collapse comes 21 per cent earlier on M/8 than on M/4. Run (v) says,
by its written rule, that the control drift is particle-noise relaxation (D scales as 1/N,
N.5), but only on M/4 and with a phase confound (entry 13:12Z). Two readings remain for the
M/8 control collapse, and a run exists in which each can fail:
- relaxation: the drift is set by the particle noise (rate about 1/N);
- scheme: the drift is set by the discretisation on this mesh, independent of N.
Decks: tracks/C-sidm/longruns/inputs/{A8N_y0p33403_N1e6_s1_ctrl, A8N_y0p33403_N1e4_s1_ctrl,
D2M16_cc2_kn10_f4_s1}.athinput (make_decks_b11.py, run C-20261124-131231-74f067d; particle
files C-20261124-130731-e1d24de, N = 1e6, and -130732-a383ef5, N = 1e4, stratified seed 1);
release core-v0.6 card build; restart every 10 M; no lapse_leak (no black hole at the start);
cfl_number 0.25 with the Gamma-driver shift (decision 0027 item 2: at most 0.6).

N-series, reference the N = 1e5 control A8_y0p33403_s1_ctrl (C-20261121-214601-40dc927):
t_c = 534.8 M; alpha_c - alpha_c(0) = -0.0024 at 300 M, -0.0188 at 400 M.
- NS.1 [JUDGEMENT, 60 per cent] relaxation: the N = 1e6 control does not collapse by 600 M,
  and its alpha_c change at 400 M (20 M mean) is above -0.005.
- NS.2 scheme: t_c(N = 1e6) in [455, 615] M (534.8 +- 15 per cent).
- Decision: N = 1e6 decides between them. Between the two (no collapse but contraction at
  400 M below -0.005, or a collapse after 615 M within 600 M impossible) is reported as
  partial N dependence. If NS.1: the threshold reading needs N >= 1e6 (or collapse times only,
  against controls of the same N), and the seeds at N = 1e5 measure the noise of the drift;
  if NS.2: more particles do not help, the next test is the mesh (M/16 control) and the
  gauge or boundary leg, and core is asked about a secular error of the scheme.
- NS.3 N = 1e4 control: relaxation predicts a collapse before 300 M; scheme predicts
  [455, 615] M. A weak test: a 1e4 sample deviates from the model in its radial balance by
  about 1/sqrt(N), comparable to the one-per-cent kicks (the 1e5 kick-in collapsed at 294 M),
  so an early collapse alone does not name relaxation.
- Cost: N = 1e6 at most 1.5 times the N = 1e5 step (12.5 s per M; refuted above 16), about
  2 card-hours for 600 M; N = 1e4 at most 1.4 card-hours.

M/16 member of D2 (CC2, Kn = 10, coll_energy = particle, collision seed 1, coll_cell_factor 4,
so collision cells of M/4 as in the M/4 runs, f = 1, and the M/8 run f = 2; 220 M):
mesh series of t_c with collision cells of M/4: 206.64 M (M/4, mean of the particle-mode
seeds), 163.41 M (M/8, f = 2, seed 1).
- M16.1 [JUDGEMENT] t_c(M/16) in [140, 170] M (second order from M/8 would give 152.6, first
  order 141.8; most of the M/4 -> M/8 shift is the outward push of the M/4 mesh, drift entry
  12). Refuted above 170 M (the M/8 value is not in the asymptotic range) or below 140 M (no
  convergence: the collapse time keeps falling as the mesh is refined).
- M16.2 collisions per particle per M over 0-100 M within 5 per cent of 8.86e-3 (M/8, f = 2).
- Step time at most 3 times the M/8 deck (25 s per M), about 1.5 card-hours.

Queue order (seq.sh, two slots): the running A324s1c+ and A334s3o, then A344s1o+, A324s1o+,
N6c (N = 1e6), M16, A334s2c+, A334s3c+, N4c (N = 1e4), D2f2s2+, A334s2i+, A334s2o+,
A334s3i+. New chains get MAX_SEGMENTS 20 (SEG_FLOOR of seq.sh) because a preemption uses a
segment; the harness reserves only the gpu-hours of the queue line (2.5, 2.0, 1.5).
Card-hours: G2 used 25.00 by the closed manifests at 13:00Z (nrpic-run budget), about 11 more
for the continuations and about 6 for these three; 45 allotted.

## 2026-11-24T13:36Z  session C-sidm lead (batch 11, analysis round)  commits e1913da9..(this entry's commit)  runs C-20261124-130021-5c9c207, -130222-6a4924d, -130338-43b5ffa, -130338-c4ac85e, -130442-0819c88, -130506-2ddce1f, -130634-3338d9b, -130731-e1d24de, -130732-a383ef5, -131012-f920f45, -131129-e93be29, -131231-74f067d, -131249-b06c218, -132113-52c2abe (failed, own bugs, rerun: -130433-e84cb43, -130951-36beb5c, -131113-b196c0e, -131221-49d5fcc)

- did: merged main; found the batch-5 queue run through, with ten chains cut by preemption
  (cause verified from event logs and sacct); continued them in place from their newest
  restarts with a restart every 10 M (resume rule written first, entry 12:59Z); changed the
  sequencer (submits through the pause flag, logs why it waits, resume items, segment floor
  20) and restarted it (pid 4068739); judged R(v), T, H, D2 and block A (entry 13:12Z) with
  registered analyses and figures read; rechecked every collapse time with a reader of its
  own; made the N = 1e6 and 1e4 particle files and three follow-up decks, smoke-tested them
  on processors, wrote their predictions (entry 13:14Z) and queued them; opened stage/G2
  (checklist judged, evidence, what the gate lacks, what a G2 verifier must cover); review
  section 14; outbox to orch (card-hours, segment cap) and core (control drift, SIGTERM
  restart); acknowledged kb's conductivity-sources answer.
- found: the controls of the threshold model and of y0 = 0.344 collapse on their own on M/8
  at N = 1e5 (534.8, 549.3 M); the collisional collapse time does not depend on the collision
  cell (2 per cent between cells M/8 and M/2) but moves 21 per cent from M/4 to M/8; the
  conductivity is 1.020 +- 0.004 of the first Chapman-Enskog value at zero cell size and
  k lambda; the energy diffusion of the particles scales as 1/N.
- changed my mind about: block A at N = 1e5 on M/8 as the threshold scan (it cannot be, by
  its own refutation rule); the noise model of block A as written (it does not survive a
  collapse inside a window; ripple now taken before 400 M, labelled post hoc).
- failed predictions: N.3, D2.2, A.1 (kout part), A.3, A.4. Failed runs: four analysis runs of
  my own scripts (listed in the header), each rerun; ten card chains cut by preemption (not
  failures of the physics; continued).
- open: the continuations and follow-ups in the queue (HANDOFF.md table); the N6c verdict
  decides the next scan; a G2 verifier; card-hours (asked).
- card-hours: none submitted by hand this session; the sequencer's batch-5 queue used 17.59
  card-hours since 2026-11-21 (closed manifests) plus the running chains.

## 2026-11-24T21:08Z  session C-sidm batch 12 (card runs into the shared queue)  commits fa47d3fb..(this entry's commit)  runs: none new (one closed: C-20261124-120250-9e6a3ba)

- did: merged main (decision 0033 and the shared queue); found what the 12:00 PST stop left:
  the sequencer (pid 4068739) gone; A334s3o (C-20261124-120250-9e6a3ba) stopped with the chain
  helper after 2 min of segment 6 (job 5164, sacct CANCELLED; newest restart cc.00003.rst,
  history to 124 M); A324s1c+ (C-20261123-032324-938ecbd) left running as job 5206; the other
  eleven sequencer items had never reached Slurm, so no other C job was cancelled. Closed
  A334s3o as stopped (`nrpic-run finish --status stopped`) and added a resume line for it to
  queue.txt (cap 24 kept). Wrote `longruns/seq/qitem.sh` (one item of queue.txt -> one job:
  a new chain through nrpic-run submit with the sequencer's process name and segment floor 20,
  or an in-place resume through submit_chain.sh with a committed `continuations` entry;
  refuses outside the dispatcher; `close <run_id>`), dry-ran all twelve items (all pass,
  refusal outside the dispatcher checked), retired `seq.sh run`, and queued twelve entries:
  q0016 N6c, q0017 M16, q0018 N4c at priority 2 (stage/G2/OPEN.md items 1-2 wait for them),
  q0019-q0027 the nine continuations at priority 5 in the batch-11 order, no --after.
- found: nothing about the physics (no analysis in this session).
- changed my mind about: nothing; the order now puts N6c, M16, N4c ahead of A344s1o+ and
  A324s1o+ (priority rule of 0033 item 6), which the batch-11 order had first.
- failed predictions: none tested. Failed runs: none.
- open: all twelve entries waiting (HANDOFF.md table); A324s1c+ in Slurm; closing each run when
  its entry is done (`qitem.sh close <run_id>`).
- card-hours: none used by this session.

## 2026-11-25T11:56Z  session C-sidm lead (batch 17)  follow-up runs: predictions before submission

Written before the registered analyses of N6c and M16 of this session are run. A peek at the
history of N6c (C-20261124-221122-928c9eb), made with the reader `nseries.py` into
scratch/C-sidm/tmp before the run was closed and not a result, showed no collapse in 600 M;
these predictions are conditional on that reading being confirmed by the registered analysis
(if it is not, the entries below are removed again). Decks: make_decks_b17.py; executable of
their series, core-v0.6 card build (qitem.sh), no `dt_gauge` (cfl_number 0.25 below 0.47).

N6i, N6o: the threshold model y0 = 0.334032 at N = 1e6 on M/8, seed 1, kicked one percent
inward / outward (particle files of C-20261124-130731-e1d24de), 600 M; control N6c.
At N = 1e5 (seed 1): kin collapsed at 294.5 M, kout at 449.0 M, control at 534.8 M.
- B17.1 [JUDGEMENT, 55 per cent] N6i collapses before 600 M, later than the N = 1e5 kin
  (t_c in (294.5, 600) M). Refuted if it does not collapse by 600 M: then the N = 1e5 kin
  collapse was noise-assisted and the threshold model is on the stable side on M/8 (the
  numerical threshold above 0.334032), or the kick is too small to decide at N = 1e6.
- B17.2 N6o does not collapse by 600 M, and alpha_c(t) - alpha_c(0) is positive (expanded)
  over 100-300 M (20 M means). Refuted by a collapse before 600 M (as at N = 1e5) or by a
  negative change at 200 M.
- B17.3 Delta_i = alpha_c(N6i) - alpha_c(N6c) at 200 M (20 M means) below -0.01, and
  Delta_o = alpha_c(N6o) - alpha_c(N6c) at 200 M above +0.005: the kicks are resolved
  against the control's pulsation at this N. Refuted if either has the wrong sign.
D2eta1: D2 at f = 2, collision seed 1, on M/8 with shift_eta 1.0 (D2 has 2.0), 220 M.
- B17.4 t_c(alpha_min = 0.3) within 5 per cent of 163.41 M (f = 2) and collisions per
  particle per M over 0-100 M within 5 per cent of 8.86e-3. The 1+log lapse and its
  advection are unchanged; the cell-factor series spread t_c by 1.6 per cent at most, a
  bound for the run-to-run noise of cards. Refuted above 5 per cent: the collapse time read
  from the lapse depends on the shift damping, and the gauge leg of C2 needs a slicing-
  independent collapse marker (an apparent horizon) before it can pass.
Cost [JUDGEMENT, from N6c and D2]: N6i, N6o about 2.5 card-hours each, D2eta1 about 0.6.

## 2026-11-25T12:01Z  session C-sidm lead (batch 17)  the three entries chosen; predictions B17.5, B17.6 before submission

Changed before anything was queued: the cap is three new entries, and the gate item C9 reads
"the collisionless threshold is located ... and compared with the turning-point criterion".
The kicks of the threshold model itself (B17.1-B17.3) do not bracket it: a model at the turning
point is marginal and either outcome is consistent with y_max = 0.334032. So B17.1-B17.3 are
withdrawn unqueued (on record; decks A8N_y0p33403_N1e6_s1_kin/kout kept for the next round), and
the bracket models of block A are run at N = 1e6 instead, kicked inward. The particle files are
made in this session by make_ic_seeds.py --tag (runs C-20261125-115759-77a6999 for 0.344 and the
next one for 0.324; same stratified sampler and seed 1 as N6c). The entries: N6b344, N6b324 and
D2eta1 (B17.4 stands as written at 11:56Z).

At N = 1e5 on M/8 (seed 1): y0 = 0.344 kin collapsed at 229.8 M (control 549.3 M); y0 = 0.324
kin did not collapse to 600 M (alpha_c change between -0.007 and -0.028); JOURNAL 13:12Z of
2026-11-24, run C-20261124-130634-3338d9b.
- B17.5 [JUDGEMENT, 75 per cent] N6b344 (y0 = 0.344, kin, N = 1e6) collapses before 600 M,
  t_c in [200, 400] M. Refuted if it does not collapse by 600 M: then 0.344 is on the stable
  side on M/8 at N = 1e6, the N = 1e5 collapse was noise-assisted, and the numerical threshold
  lies more than 3 per cent above the turning point.
- B17.6 [JUDGEMENT, 80 per cent] N6b324 (y0 = 0.324, kin, N = 1e6) does not collapse by 600 M
  and alpha_c(t) - alpha_c(0) stays in [-0.03, +0.03] (20 M means, 0-600 M). Refuted by a
  collapse before 600 M (the scheme destabilises a model 3 per cent below the turning point)
  or by a contraction below -0.03.
- If both hold: on M/8 at N = 1e6 the threshold lies in (0.324, 0.344), which contains
  y_max = 0.334032; this is item C9 at one mesh and one N, and the mesh and gauge legs of the
  bracket stay open (they are the next card request, not queued here).
Cost [JUDGEMENT]: 2.5 card-hours each (the N6c line), D2eta1 0.6; the six N = 1e5 kicked
continuations removed in this session (stage/G2/OPEN.md) free more than that.
