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
