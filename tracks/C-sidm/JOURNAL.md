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
