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

## 03:55: debug runs (unregistered, `scratch/A-emd-pbh/tmp/`), and a fourth test

Debug invocations of `vonneumann.py` (17 points per dimension) and `lapse_toy.py` ran
into `scratch/A-emd-pbh/tmp/` to find script errors; their numbers are not used. Seen in
them before the registered runs: T2 limit 0.660 for the shift mode with `diss = 0.5`
(inside the predicted 0.6 to 0.8); toy maxima 19.0 (plain 1+log) and 3.03 (damped), as
predicted. While checking the column layout of `east.cstat.hst` I also saw the bh1 and
bh2 records at t = 1.06, 1.31, 1.56, 1.81 (bh2/bh1 of the largest relative Hamiltonian
constraint about 0.9, 1.4, 2.6, 4.4), after the T3 prediction was written.

The toy froze the top-hat at or before its turnaround under every background-subtracted
condition (K - K_b, the mean-curvature driver, K + 2/tau_local), whereas 2610.23218 reports
for K + 2/tau_local a lapse minimum near 0.5 only after the collapse time
(`main.tex:218-222`), with a shift and an inhomogeneous peak. So the toy may freeze too
early: it lacks the term `-D^i D_i alpha` of the K equation, which pushes K down where
the lapse has a minimum. T4 measures this on a run of this code.

### T4 Toy against the 3D lapse driver run (analysis of existing output)

`runs/cosmo/east_d0.05_n64_kd` (conformal-time lapse plus `lapse_kdriver = 1`, zero
shift, 64 cells): the lapse at the overdensity (probe at x_i = 1) relative to the largest
lapse falls to 7.5 percent at a = 20.5 (cosmo TESTLOG 617-624). The toy's collapse epoch X
is set so that its top-hat lapse peaks at the same background a as the 3D probe lapse;
then the ratios after the peak are compared.
Prediction: a rough estimate (driver rate alpha_b (K_c - K_b), about 2 per unit
conformal time at a = 15 to 20) gives a fall by e^-2.7, i.e. a ratio of order 7 percent,
so I expect agreement within a factor 2 at the last finite record of the 3D run.
Refuted if the toy's ratio there is more than a factor 2 away from the 3D one; a toy far
below the 3D value would mean the lapse-gradient term (absent from the toy) slows the
lapse collapse, and the toy's freezing statements for the subtracted conditions cannot be
used.

## 03:40 to 04:00: outcomes of T1 to T4

Runs (manifests in `tracks/A-emd-pbh/runs/<run_id>/manifest.json`, outputs under
`scratch/A-emd-pbh/<run_id>/`, one processor core each, no cards):
T2 `A-emd-pbh-20261115-113608-374a41a` (first figure had a clipped label) and
`A-emd-pbh-20261115-113755-cac3c4b` (same numbers, figure fixed); T1
`A-emd-pbh-20261115-113614-374a41a`; T3 `A-emd-pbh-20261115-113807-43300e5` (lapse panel
blown up by the broken last records) and `A-emd-pbh-20261115-113921-ca3786e` (same
numbers, axis fixed); T4 `A-emd-pbh-20261115-113810-e02c969`. Figures, inspected:
`figs/lapse_toy.png`, `figs/vonneumann.png`, `figs/bh2_onset.png`, `figs/kd_compare.png`.

### T1 (run -113614-374a41a, `stdout.txt`, `lapse_toy.json`)
- P1.1 confirmed: plain 1+log top-hat maximum 19.01 (= 1 + 6 ln 20.13, b_max/b_i = 20.13);
  background 25.15 at a = 56 (1 + 6 ln 56 = 25.15). 2610.23218 states "alpha ~ 20".
- P1.2 confirmed: damped condition maximum 3.03 (paper: "from 20 to 2").
- P1.3 confirmed: conformal-time lapse, background alpha = a (56.04 at the first record
  past a = 56); top-hat reaches its crunch at t = 25.71 (a = 192; run on to a = 1e4 X):
  no singularity avoidance. Same for `lapse_volume` (crunch at t = 25.70).
- P1.4 confirmed: conformal + driver, top-hat lapse 0.067 against a background lapse of
  168 at the end; the top-hat is frozen just past turnaround (tau_c/tau_crunch = 0.539).
- P1.5 confirmed and sharper than written: background-subtracted 1+log (and the driver
  `lapse_kdriver = 2`, identical in the toy) freezes the top-hat at its turnaround
  (tau_c/tau_crunch = 0.5047, b = 0.9999 b_max). The 2610.23218 variant K + 2/tau_local
  freezes it while still expanding (tau_c/tau_crunch = 0.139, linear contrast 0.45);
  analytically alpha = 1 - 2 ln[(1+delta)/(1+delta_i)] in that toy, zero at
  1 + delta = e^(1/2) (1 + delta_i). Softplus freezes it at 0.85 b_max after turnaround
  (alpha = 1 + 6 ln(b/b_max) from turnaround), linear contrast 1.38.
- P1.6 confirmed: coordinate time to a = 56 is 278.7104 (cosmic) and 12.9666
  (conformal), toy within 1e-7; ratio 21.5. Steps at fixed dt = C dx scale the same way.

### T2 (runs -113608-374a41a, -113755-cac3c4b)
Largest stable C v: scalar wave 0.664 (no dissipation), 0.618 (diss 0.5), 0.503 (diss
1.0); shift subsystem with b = 3/4 0.728, 0.660, 0.536. Prediction (0.6 to 0.8 for the
shift mode with diss 0.5; 0.6 to 0.75 for the scalar) confirmed. Dissipation lowers the
limit. For the alpha^2-scaled driver in the conformal-time slicing with cfl 0.25 the
limit is passed at alpha = 2.64, t = 1.25.

### T3 (run -113921-ca3786e)
bh2/bh1 of the largest relative Hamiltonian constraint: 1.00 at t = 1.00, 1.43 at 1.25,
1.91 at 1.50, 4.34 at 1.75; above 2 from t = 1.5625 on; Theta above 2 from t = 1.50;
the largest momentum constraint exceeded 2 once at t = 0.8125 (transient) and stays above
2 from 1.5625. The largest lapse of bh2 crosses the T2 limit (2.642) at t = 1.203 (it runs
above a(t): 2.77 at t = 1.25). bh1 shows no such growth before t = 2.2.
Prediction confirmed for H and Theta: separation after the limit, not before t = 1.0.
The cosmology log's "unstable on the refined blocks" and this time-step explanation are
not exclusive (the finest level sets dt, and Gamma^i is non-zero only there), but the
time-step reading predicts something the other does not: halving cfl_number moves the
onset to alpha = 5.3 (t = 2.6), and the unscaled driver (`shift_Gamma = 0.75`,
`shift_alpha2Gamma = 0`, speed 1) is stable at cfl 0.25. Not run (needs a card, about
0.15 card-hours from the 505 s of bh2's log); listed as a request.
The linear amplification of the fastest grid mode from T2 (ln A = 15 by t = 1.4, 84 by
1.6) is far larger than the observed growth of the constraint maxima; the instability
needs Gamma^i != 0 to be seeded and saturates nonlinearly. The model gives the onset,
not the growth.

### T4 (run -113810-e02c969)
Refuted. Toy collapse epoch X = 29.9 puts its top-hat lapse maximum at the 3D value
(a = 15.75), but the toy maximum is lower (7.7 against 10.5) and the fall afterwards much
slower: overdensity/largest lapse 0.50 vs 0.45 (toy) at a = 17.3, 0.31 vs 0.41 at 18.6,
0.12 vs 0.37 at 20.0, and at the last sound record (t = 7.046875, a = 20.47, read from
`east.nrpic.hst`: 1.4166 / 20.904) 0.068 vs about 0.36, a factor 5. (The script's own
last row, a = 20.53, is the broken record and is meaningless.) The 3D peak, from
constraint-solved data in the conformal-time slicing at 4 Hubble radii, collapses faster
than the top-hat with the same lapse-maximum epoch. Consequence: the toy orders the
conditions in the expansion phase (lapse growth, exact pointwise relations) and the step
cost; its freezing epochs are qualitative only and do not rank the background-subtracted
conditions. That ranking needs runs of the code (requests in `GAUGE.md`).

## 04:20: deliverables written; what is not done

`GAUGE.md` and `DIAGNOSTICS.md` written from the reading and T1-T4; `README.md` lists
contents, the rerun and the requests. Two corrections found while writing: the finder's
mass column is the Christodoulou mass (`fastflow.cpp:821`), not the irreducible mass
named in `paper/sections/method.tex:197` (equal at zero spin; use the area column); the
run manifests cannot be committed because the ignore rule `runs/` also matches
`tracks/<ID>/runs/` (left on disk, request to the orchestrator).
Not done: no run of the code (G-R1 to G-R4 need cards, source from core, or A-pre-1's
tables); the spin bias of the finder in an expanding background is derived, not
measured; the exterior K of the expanding ball, -(3/2)(2M/r^3)^(1/2), is my derivation
and awaits A-pre-1; the toy's freezing epochs are qualitative (T4 refuted).
