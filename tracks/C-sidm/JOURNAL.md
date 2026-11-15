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
