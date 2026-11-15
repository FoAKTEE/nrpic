# JOURNAL of the gauge package (A-pre-4), helper of A-emd-pbh

Predictions are written here before a test runs; outcomes are appended afterwards, also
when a prediction fails. Labels: [VERIFIED], [BACKGROUND], [JUDGEMENT], [TO VERIFY].

## 2026-11-15 03:30 (local): reading done, three semi-analytic tests planned

Read: 2610.23218 (all of `main.tex`), 2608.13206 (`PRD.tex` 62-101, 212-501), 2609.14218
(`MDPBH.tex` 128-177, 248-552, 771-833, 1002-1190, 1373-1470), the Z4c gauge code
(`athenak/src/z4c/z4c.cpp:125-195`, `z4c_calcrhs.cpp:46-70, 681-775`, `z4c_newdt.cpp`),
`cosmo/README.md`, `cosmo/TESTLOG.md` (E1 entries, lines 339-360, 494-516, 563-630,
744-839), `paper/sections/method.tex:191-229`, `docs/TESTLOG.md:81-89, 310-385`, the
horizon finder `athenak/src/z4c/fastflow.cpp` (options, spin integrand 1354-1378), the
Weyl scalar code `z4c_calculate_weyl_scalars.cpp`, `analysis/diag/slicemass.py`,
`analysis/diag/tracers_exact.py`, `coord/INTERFACES/spherical_id_format2.md`.

Three tests, all outside `athenak/src` (reference calculations and analysis of AthenaK
output, decision 0010), on one processor core, no cards.

### T1 Lapse in homogeneous regions (toy, zero shift, uniform lapse per region)

Model: an Einstein-de Sitter region (the unperturbed part of the ball, `a`, `H_i = 1`,
`a_i = 1`) and a closed dust top-hat with the same big-bang time (cycloid `b(psi)`,
`tau(psi)`) that collapses when the background has expanded by `X = 56` (linear
contrast 0.03 at the start, the set-up of 2610.23218, `main.tex:76`). Each region keeps a
uniform lapse; `d tau/dt = alpha`, `K = -3 (db/dtau)/b`; the lapse obeys each candidate
condition. Spatial lapse gradients, the shift and the region boundary are ignored, so the
toy is only a statement about the centre of a region before gauge waves from its edge
arrive [JUDGEMENT].

Predictions (derived before the run from the exact zero-shift relations
`alpha - ln(gamma) = const` for `d_t alpha = -2 alpha K` and
`alpha / gamma^(1/6) = const` for `d_t alpha = -(1/3) alpha^2 K`):
- P1.1 Plain 1+log: background `alpha = 1 + 6 ln a` exactly (25.2 at a = 56); top-hat
  maximum `alpha = 1 + 6 ln(b_max/b_i)`, about 19 (b_max/b_i about 20). 2610.23218 reports
  "a large increase in the lapse alpha ~ 20" at the peak (`main.tex:208`). Refuted if the
  toy's top-hat maximum is outside 15 to 25.
- P1.2 Damped `g = exp(-alpha) K` (2610.23218 `main.tex:232-236`): maximum about
  `ln(e + 6 ln(b_max/b_i))`, about 3.0 (paper: "from 20 to 2"). Refuted if outside 1.5 to 5.
- P1.3 Conformal-time lapse (`lapse_harmonic = 1/3`): background `alpha = a` to the
  integrator tolerance; top-hat `alpha / b` constant, so the top-hat reaches its crunch at
  a finite coordinate time (no singularity avoidance; cosmo TESTLOG 204-212).
- P1.4 Conformal-time lapse plus `lapse_kdriver = 1`: the top-hat lapse falls below a
  tenth of the background lapse before the crunch (cosmo TESTLOG 617-624 reports 7.5
  percent at the overdensity before the 64-cell run failed). Refuted if the top-hat
  reaches its crunch with a lapse above 0.1 of the background.
- P1.5 Background-subtracted 1+log (2608.13206 eq. cosmological_lapse; in the toy
  identical to `lapse_kdriver = 2` with `lapse_oplog = 0`): background lapse stays 1; the
  top-hat lapse decreases from the start and freezes the top-hat before its crunch.
- P1.6 Steps at fixed `dt = C dx` (as `z4c_newdt.cpp` sets it): to bring the background
  from a = 1 to 56, cosmic-time slicings need coordinate time 278.7, the conformal-time
  slicing 12.97 (`a = (1 + t/2)^2`), a ratio of 21.5. Refuted (script error) if the
  integrated times differ from these by more than 1e-6 relative.

### T2 Stability of gauge modes under the code's discretization (von Neumann)

Model: frozen coefficients, flat conformal metric, the discretization of the production
inputs (`nghost = 4`: sixth-order centred first and second derivatives, mixed derivatives
as products of first-derivative stencils, `athenak/src/utils/finite_diff.hpp`;
Kreiss-Oliger term of eighth differences times `diss 2^-8 / dx`, `z4c.cpp:168`,
`z4c_calcrhs.cpp:763-773`; RK4). Modes: (i) scalar wave `d_t^2 u = v^2 Lap u` (lapse
mode, light), (ii) the shift subsystem `d_t beta = b Gamma`, `d_t Gamma = Lap beta +
(1/3) grad div beta` (the longitudinal speed is `sqrt(4b/3)`, 2608.13206 eq.
shift_characteristic_speeds). Output: the largest stable Courant number `C dt/dx` times
speed, with and without dissipation.

Prediction: for the shift mode with `b = 3/4` (speed 1) and `diss = 0.5`, the largest
stable Courant number is between 0.6 and 0.8 (without dissipation: RK4 imaginary-axis
limit 2.83 over the largest symbol, which I estimate as 3.9 on the grid diagonal, so
0.73). For the scalar wave with speed 1: between 0.6 and 0.75. Refuted if either is
outside 0.4 to 1.0.

### T3 The shift-driver run of the cosmology extension (analysis of existing output)

`runs/cosmo/east_d0.05_n64_bh2` (main checkout, read only) used `shift_alpha2Gamma =
0.75` with the conformal-time lapse (`athena.log` line 3), so the longitudinal shift mode
moves at `alpha sqrt(4 b/3) = alpha` in coordinates, and the background lapse is
`alpha = a = (1 + t/2)^2`; `dt = 0.25 dx` on the finest level. Cosmo TESTLOG 809-819
calls the driver "itself unstable on the refined blocks" and leaves the cause open. My
alternative: a time-step (CFL) instability of the shift mode once `0.25 a` exceeds the
limit of T2. I read TESTLOG 809-819 (end at t = 1.97, constraint 4e-2 at t = 1.25 and
0.86 at t = 1.94) before writing this, so the end point is not a test.

Prediction: in `east.cstat.hst` of bh2 the largest relative Hamiltonian constraint and
Theta depart from those of `east_d0.05_n64_bh1` (same mesh and data, zero shift) only
after the background lapse has passed the T2 limit, `a_crit = C_crit / 0.25` (with
C_crit from T2: a_crit 2.4 to 3.2, t_crit 1.10 to 1.58), and grow faster than
exponentially after that. Refuted if the two runs separate clearly (factor 2) before
t = 1.0 (a = 2.25), or if bh1 shows the same growth in the same interval. If refuted,
the instability is not the time step, and the refined-block explanation of the cosmology
log stands.
