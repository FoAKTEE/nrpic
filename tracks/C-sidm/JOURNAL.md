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
