# JOURNAL of core, work package mp (several black holes with momentum and spin)

Branch `core/multi-puncture`, worktree `wt/core-mp`. Append-only, newest at the bottom.
Predictions are written before a test runs, outcomes after. Labels: [VERIFIED] read from
a source with a locator or measured in a registered run, [BACKGROUND], [JUDGEMENT],
[TO VERIFY]. Units G = c = 1.

## 2026-11-15  session mp-1

### Read

- Rules, charter to "Owners", decision 0010, the brief by the named line ranges.
- `athenak/src/pgen/nrpic/nrpic_cf.cpp` (punctures at rest: `psi = 1 + sum u_c`,
  `K_ij = 0`); `athenak/src/pgen/tests/z4c_boosted_puncture.cpp` (Lorentz-boosted
  Schwarzschild slice in isotropic coordinates, not conformally flat, with its analytic
  shift and a precollapsed lapse; only `punc_velocity_x1` enters the geometry);
  `athenak/src/pgen/z4c/two_punctures/` (wrapper of the external TwoPunctures library,
  which is not in this tree and is not used: decision 0010);
  `athenak/src/z4c/compact_object_tracker.cpp` (tracker velocity is minus the shift at
  the tracker, `<z4c> co_<n>_*`), `z4c.cpp` lines 241-283 (trackers and finders are built
  in the Z4c constructor from the input), `fastflow.cpp` (finder; `use_puncture_<n>`
  centres it on a tracker), `z4c_amr.cpp` (`method = tracker`), `z4c_wave_extr.cpp`.
- Two-black-hole runs of this repository: `problems/puncture/tracers_headon.athinput`,
  `problems/jeans/jeans.athinput`; `notes/results_brief_selfgravity.md` part D item 3
  (finder flow constant must shrink for light black holes: 0.05 for 0.1 to 0.19 M).
- Sources (fetched with the helper, read only):
  - Brandt & Bruegmann, arXiv:gr-qc/9703066v2, `main.tex` lines 60-73 (conformal
    scaling `K^ph_ab = psi^-2 K_ab`, momentum constraint `nabla_a K^ab = 0`, Hamiltonian
    constraint `lap psi + (1/8) K^ab K_ab psi^-7 = 0`), lines 116-122 (Bowen-York
    curvature with momentum and spin, Eq. 5), lines 180-215 (sum over punctures; regular
    part `u` solves the Hamiltonian constraint on R^3). [VERIFIED]
  - Lousto & Zlochower, arXiv:0711.1165v2, `second.tex` lines 222-271 (closed-form `u`
    to second order in P and J for one puncture, with the cross term), lines 277-290
    (superposition for several punctures, error "inverse of the distance squared";
    `M_ADM = sum m + (2/5) J^2/m^3 + (5/8) P^2/m`), lines 436-442 (their three-black-hole
    grids: 11 levels, boundaries at 640 M, finest M/80). [VERIFIED]

### Design decisions [JUDGEMENT]

1. Curvature evaluation in its own header `athenak/src/pgen/nrpic/nrpic_bowen_york.hpp`
   (namespace `nrpic_by`); hooks in `nrpic_cf.cpp`: one include, one reader call after
   the lapse options, one loop adding the corrections to `psi`, one block adding
   `psi^-2 Abar_ij` to `vK_dd` (after the existing `= 0.0`, with `+=`, so that the
   table-based curvature of `core/id-extrinsic` can be set before it), one log line.
2. Regular correction, per puncture: `none`, `approx` (the closed form of 0711.1165,
   no file) and `table` (multipoles about one axis from a file, format `mp1`, written
   by `python/nrpic/bowen_york.py`, which solves the full equation for one puncture
   with P and S along one axis). A mesh solver comes later (decision 0010, item 4).
3. Trackers, initial refined regions and horizon finders for every puncture are
   written into the input parameters before the mesh is built
   (`nrpic_puncture_setup.hpp`, called from `main.cpp` for new runs, opt-in with
   `<problem> puncture_setup = true`), because the Z4c constructor builds trackers and
   finders before the problem generator runs and the initial mesh must already resolve
   the punctures. Finder flow constant = (bare mass)^2: the flow step is
   `alpha * integral(H |grad F| Y)`, of order alpha/length, against a radius of order
   length (`fastflow.cpp`, UpdateFlowSpectralComponents and the definition of rho).
4. Old inputs must behave bit-identically: new parameters are read only when present.

### Reference checks done before any code test (Python, no simulation)

`tracks/core/analysis/mp/check_bowen_york.py` on `python/nrpic/bowen_york.py`:
Abar is traceless and symmetric to 1e-16 and divergence free to 6e-10 (sixth-order
differences, h = 0.01); the surface integrals give P_ADM = P and J_ADM = S to 1e-15;
the closed form of 0711.1165 satisfies `lap u = -(1/8) psi_BL^-7 Abar^2` to 2e-8..4e-4
of the largest source on spheres r = 0.02..10 (difference error) for P only, S only and
P with S (so the cross term has the right sign); the multipole solver without
iteration agrees with the closed form to 2e-6 and reproduces
`M_ADM = m + (5/8) P^2/m + (2/5) S^2/m^3` to 8 digits. Full solution, m = 1:
`M_ADM` = 1.00623 (P = 0.1), 1.05474 (0.3), 1.20401 (0.6), 1.49932 (1.0). [VERIFIED]

### Predictions (written before the tests)

**R. Regression.** `problems/puncture/tracers_headon.athinput` (two punctures at rest,
adaptive mesh, tracers), a few cycles, old executable (source of `main`) against new:
every data file identical byte for byte (history, tracker, horizon summary, particle
trajectories, restart dump apart from nothing). Refuted by any differing byte in a
data file.

**1a. Initial data on the mesh at t = 0 (no evolution).** One puncture m = 1 at the
origin (a cell corner), cubes of half-width 4 with 32, 64, 128 cells (dx = 1/4, 1/8,
1/16), sixth-order differences (nghost = 4).
 (i) Without correction the Hamiltonian residual of the code equals
     `-psi_BL^-12 Abar_ij Abar^ij` at every cell with r >= 0.75: the relative
     difference falls with resolution by about 2^6 per halving while it is above
     round-off (at least a factor 20 per halving). Refuted by a difference that does
     not fall (wrong component, wrong power of psi).
 (ii) Its size is proportional to P^2: for P = 0.1, 0.2, 0.4 the root-mean-square over
     the cells with psi <= 2 has ratios 1 : 4 : 16 within one percent at dx = 1/16.
 (iii) The momentum-constraint residual converges to zero at the same order and is
     proportional to P (ratios 1 : 2 : 4).
 (iv) With `corr = approx` the residual equals
     `Abar^2 psi^-5 (psi_BL^-7 - psi^-7)` (psi = psi_BL + u_approx); its
     root-mean-square over the same cells is smaller than without correction by a
     factor that scales as 1/P^2 (residual proportional to P^4): about 7 u/psi, that
     is of order 0.05 at P = 0.3.
 (v) With `corr = table` (full solution, l <= 8) the residual keeps falling with
     resolution; at dx = 1/16 its root-mean-square is below one percent of the
     uncorrected one.
 (vi) Spin S = 0.4 along z and P with S not parallel: (i) and (iv) hold with the full
     Abar^2 including the cross term.
 (vii) Two punctures with momenta: (i) holds with the summed curvature; with
     `approx` the residual equals
     `psi^-5 sum_c psi_c^-7 Abar_c^2 - psi^-12 (sum_c Abar_c)^2`, psi_c the factor of
     puncture c alone.

**1b. One boosted puncture evolved.** m = 1, P = 0.3 along x, domain +-64, finest
cells 1/32 following the tracker (`puncture_setup`), moving-puncture gauge of the
existing inputs, to t = 40.
 - The tracker moves along +x (the direction of P). Refuted by motion along -x.
 - Its speed starts at zero (zero initial shift), rises during the gauge transient and
   is within 10 percent of P/M_ADM = 0.284 (corrected data, M_ADM = 1.0547) when
   averaged over 20 < t < 40; for the uncorrected data (energy at infinity m = 1) the
   expectation is P/m = 0.30, and the two cases differ by less than 10 percent, so
   that this test cannot tell them apart unless the scatter is below 3 percent.
   [JUDGEMENT] Refuted by a mean speed below 0.2 or above 0.4.
 - The existing generator `z4c_boosted_puncture` with velocity 0.284 moves at its
   velocity from t = 0 (its shift is the boosted one); between t = 20 and 40 the two
   speeds agree within 10 percent, and the positions differ by the lag of the
   Bowen-York puncture accumulated in the transient (a few M).
 - Horizon mass at the first search: 1.011 +- 0.005 with `approx`
   (sqrt(M_ADM^2 - P^2) = 1.0112), lower by up to one percent without correction; the
   horizon mass stays constant to one percent to t = 40.
 - Constraint norms (history) stay bounded; with `approx` the Hamiltonian norm at
   t = 0 is the smaller one, as in (iv).
 - Speed against momentum: runs with P = 0.15 and 0.6 (corrected) give mean speeds
   within 10 percent of P/M_ADM = 0.148 and 0.498.

**2. Two punctures for a few M.** m = 0.5 each at x = +-5, P = +-(0, 0.0791, 0)
(Newtonian circular momentum `(M/4) sqrt(M/d)`, M = 1, d = 10), `approx`, finest
cells 1/32, to t = 40.
 - The mass-weighted mean of the two trackers stays at the origin (symmetry) to 1e-3.
 - The punctures start to move along +-y, with speeds approaching P/m = 0.158 within
   20 percent between t = 15 and 40; the line joining them turns counter-clockwise
   (L_z > 0), by between 0.5 and 1.3 rad at t = 40 (Newtonian rate
   sqrt(M/d^3) = 0.0316, minus the lag of the transient).
 - The coordinate separation stays within 10 +- 1 (a Newtonian momentum is slightly
   below the relativistic circular one, so it shrinks slowly).
 - Two horizons are found, masses 0.5 to 0.52 each.
 Refuted by a drifting centre, by clockwise turning, or by a separation that changes by
 more than 2 within 40 M.

**3. Three black holes, scouting.** Binary m = 0.5 + 0.5 (separation 10) and a black
hole of mass 10 at distance 100, spin 0.3 M^2 on the heavy one, momenta of a parabolic
approach in the centre-of-momentum frame, `approx`, finest cells m/8 at the light
ones.
 - It runs to the end without non-finite values; three trackers and three horizons.
 - Heavy horizon found with the default flow constant m^2 = 100. Refuted if it is not
   found (then the scaling argument of design decision 3 is wrong).
 - At t = 0 the Hamiltonian norm with `approx` is below that without correction by a
   factor of at least 3; what remains is the cross terms and the fourth order.
 - Junk radiation: a burst in psi_4 passing the extraction spheres at the light-travel
   time; its energy below 1e-3 of the total mass. [JUDGEMENT]

### Outcome of R (regression)

- Processors, `problems/tests/regress_cf.athinput` (table, Gaussian, spheroid and
  puncture in one run, two cycles): runs `core-20261115-113321-a5197ba` (executable built
  from `main`) and `core-20261115-113400-a5197ba` (this branch). All twelve binary dumps
  (z4c, adm, con at cycles 0 to 2 and the end) and the history are identical byte for
  byte. [VERIFIED]
- Card, `problems/puncture/tracers_headon.athinput`, 24 cycles with the finder on from
  t = 0: runs `core-20261115-113546-a5197ba` (old) and `core-20261115-113600-a5197ba`
  (new). Trackers, horizon summary, particle history, trajectories, metric at the
  particles, Z4c history and the particle restart files are identical byte for byte.
  [VERIFIED]
- The mesh restart files differ in 35 bytes (processors) and 7 bytes (card) at one
  place, offsets 8896-8931 and 15943-15949: inside the binary header after `<par_end>`,
  where both executables write uninitialised memory (the bytes are fragments of
  parameter text and of symbol names, different in each executable). Everything after
  it, 90 MB of field data, is identical. This is not caused by the change; the prediction
  "apart from nothing" was too strict for these files. [VERIFIED]
- Two earlier card runs (`-113512-`, `-113513-`) failed at start: the command line can
  only change parameters that exist in the input (`output2/dcycle`). Failed manifests
  kept.

### Outcome of 1a (first pass, source a1fe80f)

Runs: the 31 registered runs with labels `s_*` of `run_static.sh`
(`core-20261115-114152-c89b6e3` to `-114238-`); numbers from
`tracks/core/analysis/mp/static_check.py`. Earlier launches of the same labels are
marked superseded or failed in their manifests (quotes stripped by xargs; parameters
missing from the input; a comment line with a second '=' that the stock binary reader
cannot parse).
 - K_ij on the mesh equals `psi^-2 Abar_ij` to 2e-8 to 5e-8 of its largest value, for
   momentum, spin, both, and two punctures (the output is single precision). The
   Hamiltonian residual minus that of the same mesh with P = 0 equals
   `-psi^-12 Abar^2` to 2.5e-6, 3.3e-7, 5.0e-8 at dx = 1/4, 1/8, 1/16: the part of the
   residual that comes from the curvature is algebraic. [VERIFIED]
 - (i) holds: over the cells with r >= 0.75 the difference between the residual of the
   code and the closed form is 1.88, 1.84e-2, 3.15e-4 of the closed form's rms at
   dx = 1/4, 1/8, 1/16 (factors 102 and 58 per halving; sixth order is 64).
 - (ii) holds: rms over the history cells 1.665e-4, 6.661e-4, 1.499e-3, 2.665e-3 for
   P = 0.1, 0.2, 0.3, 0.4 (1 : 4.00 : 9.00 : 16.01), equal to the closed form to four
   digits.
 - (iii) holds: momentum residual 6.96e-8, 1.393e-7, 2.089e-7, 2.785e-7 (linear in P);
   6.89e-4, 1.99e-5, 2.09e-7 at dx = 1/4, 1/8, 1/16.
 - (iv) holds: with `approx` the rms is 6.017e-5 (code) against 5.990e-5 (closed form)
   at P = 0.3, 0.040 of the uncorrected 1.499e-3; closed form 7.77e-7, 1.22e-5, 5.99e-5,
   1.81e-4 for P = 0.1 to 0.4 (P^4 with higher-order terms; the code value at P = 0.1,
   5.5e-6, is the truncation error of the puncture itself, 5.4e-6 with P = 0).
 - (v) holds: with the table of the full solution the rms is 3.77e-2, 5.11e-4, 4.51e-6
   at dx = 1/4, 1/8, 1/16: at dx = 1/16 it is the truncation error of the puncture
   (5.44e-6 with P = 0) and 0.3 percent of the uncorrected residual. A table of the
   second-order solution reproduces `approx` to all printed digits (6.017e-5).
 - (vi) holds: spin 0.4: 2.598e-3 (code) / 2.599e-3 (closed form) without, 2.944e-4 /
   2.939e-4 with `approx`; momentum and spin not parallel: 4.748e-3 / 4.749e-3 and
   7.508e-4 / 7.504e-4 (the cross term is in).
 - (vii) holds as stated (code 2.868e-3 / closed form 2.869e-3 without correction,
   3.834e-3 / 3.834e-3 with `approx`), but shows what I had not expected: for two
   punctures 3 apart (masses 1 and 0.5) the sum of isolated corrections leaves a
   LARGER residual than no correction (3.83e-3 against 2.87e-3).
 Figures looked at: `figs/static_convergence.png` (sixth-order lines, P^2 and P^4),
 `figs/static_profile.png` (code on top of the closed form outside r = 0.6; the table
 case on top of the P = 0 truncation curve; two punctures: red not below blue).

### Changed my mind: the isolated corrections need the background factor

Closed forms only (no simulation; `tracks/core/analysis/mp/check_bowen_york.py`, part 6), rms of H over the
cells with psi_BL <= 2: two punctures 3 apart 2.87e-3 (none), 3.88e-3 (isolated
corrections); binary of test 2 (d = 10): 2.41e-4, 3.89e-5; a light moving puncture 20
from a ten times heavier one at rest: 1.29e-3, 3.03e-3. Reason: near puncture c the
others add Lambda_c - 1 = sum m_j/(2 d_cj) to psi, the source carries psi^-7, and the
isolated correction, made for psi_c = 1 + m_c/2r, overshoots by
((Lambda_c + m_c/2r)/(1 + m_c/2r))^7. The local equation with a constant background is
the isolated one with m/Lambda, P/Lambda^4, S/Lambda^4, and its solution times Lambda
is the correction (derivation in `nrpic_bowen_york.hpp`). The same closed-form check
gives 6.23e-4, 5.60e-6 and 4.21e-5 for the three cases. This goes into `approx` as the
default (`corr_background = true`); `false` keeps the plain sum of arXiv:0711.1165.
[JUDGEMENT until the code run below]

**Prediction 1a (viii), before the rerun with the new source.** Two punctures of
(vii) with `approx` and the background factor: the residual of the code equals the
closed form with Lambda (rms 6.2e-4 at dx = 1/16, a factor 4.6 below no correction);
with `corr_background = false` the old value 3.83e-3 returns; the single-puncture
cases are unchanged to all printed digits (Lambda = 1). Refuted if the code value with
the background factor is not below 1e-3.

**Revised prediction for test 3 (t = 0).** With `approx` and the background factor the
Hamiltonian norm is below the uncorrected one by a factor of at least 3; with the plain
sum it is not (it may be larger).

### Outcome of 1a (viii), source ae695ce (processor runs `core-20261115-115118-4745494` to `-115123-`)

Prediction held. Two punctures, dx = 1/16, rms of H over the history cells: 2.868e-3
without correction, 6.200e-4 with `approx` and the background factor (closed form
6.178e-4; factor 4.6), 3.834e-3 with the plain sum (`corr_background = false`, as
before the change). Single-puncture cases unchanged to all printed digits (P = 0.3
`approx` 6.017e-5, table 4.512e-6, momentum with spin 7.508e-4). Figures regenerated
and looked at: `figs/static_profile.png`, right panel: the background-rescaled
correction lies 5 to 10 times below the uncorrected residual along the axis, the plain
sum above it outside the punctures. [VERIFIED]

### Test 1b, first attempt: failed on the block limit; what it showed

- Run `core-20261115-115339-7a60df2` (P = 0.3, `approx`, finest cells 1/32, tracker radius
  1.0 = two finest MeshBlocks, puncture on a block corner): 400 MeshBlocks at the start;
  stopped at cycle 144 (t = 1.125) with "Number of MeshBlocks ... on new tree = 1184
  exceeds max_nmb_per_rank = 1024". Until then: horizon found from the first search,
  mass 1.01098 at t = 0.25 (predicted 1.011 +- 0.005: held), tracker moving along +x
  (sign prediction held), v_x = 0.033 at t = 1.1. [VERIFIED]
- Why the block count jumped [JUDGEMENT, not isolated by a run]: the 400-block mesh
  exists only while the tracker sits exactly on a block corner of every level (2x2x2
  refined parents per level). The tracker criterion refines every block whose nearest
  point is closer than the radius; with the radius equal to a block edge the test is
  `1 - y_t < 1`, true as soon as the round-off drift of the tracker in y and z (8e-17
  at t = 0.5 in the tracker file) exceeds half a unit of round-off. A tracker off the
  corner in all three directions needs 3x3x3 refined parents per level, about 190
  leaves per level: 1184 blocks is that state, not a runaway. The diagnostic run
  `core-20261115-115551-7a60df2` was cancelled in the queue.
- Cost measured on the reference run `core-20261115-115342-7a60df2` (stock generator,
  400 to 600 blocks): 4.0 cycles per second at the start, 3.4 after 800 cycles, that
  is about 6.5e6 zone-cycles per second with 16^3 MeshBlocks (2.0e7 on a uniform mesh,
  docs/TESTLOG.md line 46). A moving black hole with seven levels then costs about an
  hour of card time for 40 M; my estimate before the test was five minutes.
- Consequences [JUDGEMENT]: finest cells 1/16 instead of 1/32 for all evolved tests
  (six levels), tracker radius 0.9 (not a multiple of the block size), block limit
  2048, and shorter runs for tests 2 and 3 than predicted above. The 1/32 reference
  run is stopped once it has passed t = 12 and serves as the resolution check of the
  reference only.
- Early observation on the reference (same run): the tracker of the stock generator
  starts at v_x = 0.280, falls to 0.040 at t = 1.5 and rises again (0.108 at t = 7.5).
  The prediction "moves at its velocity from t = 0" is refuted for the first M: the
  Gamma-driver relaxes the analytic shift within 1/eta. Whether the speeds agree later
  is still open.

### Revised set-up and predictions for 1b (written before these runs)

Mesh: domain +-64, root cells 2, six levels (finest 1/16 within 0.9 of the tracker),
cells of 1/2 within 18 of the origin, extraction spheres at 12 and 16, puncture
starting at x = -4, to t = 40. Runs: (A) P = 0.3 `approx`, (B) P = 0.3 `none`, (C)
stock generator with v = 0.2844 and rest mass 1.0112, (D) P = 0.6 `approx` to t = 30,
(E) P = 0.043, S = 0.3 along z, `approx` (the heavy black hole of test 3 in its own
units).
 - Unchanged: tracker along +x; horizon mass 1.011 +- 0.005 for (A) and constant to one
   percent; lower by up to one percent for (B).
 - Speed, revised after the early reference data: the tracker speed of all cases is
   still rising at t = 20; averaged over 30 < t < 40 it lies between 0.6 and 1.05 of
   P/M_ADM (0.284 for A, 0.498 for D with M_ADM = 1.204), and (A), (B), (C) agree
   with each other within 15 percent over that window. Refuted by a mean outside
   [0.17, 0.30] for (A).
 - (E): horizon spin S = 0.30 +- 0.01 (the finder's S column) and horizon mass
   between 1.00 and 1.05 (m + (2/5) S^2/m^3 = 1.036 is the ADM mass to second order);
   the puncture drifts along +x at less than 0.05.
 - Junk radiation: the energy through the sphere at 16 integrated over the run is below
   1e-3 of the mass for (A) and (E) and larger for (B) than for (A). [JUDGEMENT]
 - Block count stays below 2048; refuted if the block limit is hit again.

### Outcome of test 3 at t = 0 (processors; runs `core-20261115-120209-212dce7` approx, `-120210-` none, `-120211-` plain sum)

Mesh of `problems/puncture/by_triple.athinput`: 1100 MeshBlocks at the start, cells of
1/16 (m/8) at the light holes, 1 (m/10) at the heavy one. Norm as the Z4c history forms
it (sum of H^2 sqrt(gamma) dV over the cells with psi^4 <= 16 over the sum of
sqrt(gamma) dV; `triple_static.py` reproduces the history value from the dumped field
to four digits, 2.253e-5, which checks reader and mask):

| data | code (history) | closed form on the same cells | code minus closed form |
|---|---|---|---|
| no correction | 2.253e-5 | 2.148e-5 | 8.8e-6 |
| closed form, background factor (Lambda = 1.077, 1.077, 1.005) | 8.50e-6 | 2.19e-6 | 8.1e-6 |
| closed form, plain sum | 1.496e-5 | 1.233e-5 | 7.8e-6 |

 - The closed form says: the background-rescaled corrections lower the residual 9.8
   times, the plain sum 1.7 times. The binary region carries it (2.12e-5 of 2.15e-5
   without correction); the heavy hole's region goes from 3.5e-6 to 2.7e-7.
 - Prediction "at least a factor 3 with the background factor" FAILED for the norm the
   code reports: 2.65 (2.253e-5 to 8.50e-6), because on this mesh the truncation error
   of the light punctures themselves is 8e-6, four times the residual left by the
   correction. It holds for the closed form (9.8). Prediction "not with the plain sum"
   held (1.5 in the code, 1.7 closed form).
 - Momentum-constraint norm (history): 5.2e-7, 4.7e-7, 4.5e-7: truncation only.
 - Memory: the three processes with `max_nmb_per_rank = 4096` and three finders used
   108 GB each (26 MB per MeshBlock slot), more than a card has; the block limit of the
   card runs must stay near 2500. [VERIFIED: resident size seen with ps while they ran]
 Figure looked at: `figs/triple_static.png` (code on the closed form outside the
 punctures; the plain sum barely below the uncorrected curve at the light holes).

### Revised set-up and predictions for tests 2 and 3 (written before these runs)

Cost forces smaller runs than first planned (see the first attempt of 1b). Block limit
2400 in both (card memory).

**2. Two punctures** (`problems/puncture/by_binary.athinput`): m = 0.5 each at
x = +-5, P = +-0.0791 along y, `approx` with the background factor (Lambda = 1.025),
finest cells 1/16 = m/8 within 0.9 of each tracker, to t = 30.
 - Mean of the two tracker positions within 1e-3 of the origin.
 - Each puncture starts along its momentum (+y at x = +5); the line joining them turns
   counter-clockwise by between 0.2 and 1.0 rad at t = 30 (Newtonian rate 0.0316 per M,
   less the slow rise of the tracker speed seen in the reference run of 1b).
 - Tracker speeds at t = 30 between 0.5 and 1.1 of P/m = 0.158.
 - Coordinate separation within 10 +- 1.
 - Two horizons from the first search, masses between 0.510 and 0.520 (Brill-Lindquist
   horizon mass m (1 + m'/(2d)) = 0.5125 [BACKGROUND] plus P^2/(8m) = 0.0016), constant
   to one percent.
 - Block count below 2400.
 Refuted by a drifting centre, clockwise turning, a separation outside [9, 11], or a
 missing horizon.

**3. Three black holes** (`problems/puncture/by_triple.athinput`), `approx` with the
background factor, to t = 16 (3.2 light-crossing times of the binary's separation,
1.6 M of the heavy hole).
 - Runs to the end, no non-finite values (history volume constant to 1e-3), block
   count below 2400.
 - Three horizons from the first search. Masses: light holes between 0.535 and 0.57
   (m Lambda = 0.5385 plus kinetic terms P^2/(8m), second order: 0.545 for A, 0.559
   for B); heavy hole between 10.1 and 10.5 (m Lambda = 10.05; ADM mass with spin to
   second order 10.36) with the finder's default flow constant m^2 = 100; heavy
   horizon spin S_z = 30 +- 1.
 - Light holes move toward +x and +y (their momenta), the heavy one toward -x, -y.
 - Hamiltonian norm of the history stays within a factor 30 of its initial value
   8.5e-6.
 - Junk radiation cannot be measured in 16 M at this distance; it is estimated from
   the single-hole runs (A) and (E) of 1b: the energy fractions found there, times the
   masses.
 Refuted by a crash, a missing horizon (in particular the heavy one), or a norm that
 grows without bound.

### Prediction for the restart check (before it runs)

`problems/tests/puncture_setup_restart.athinput` on processors (three levels, puncture
with momentum and spin off the block corners, two tracers, finder every second cycle):
eight cycles uninterrupted against cycles 5 to 8 from the restart dump of cycle 4. The
restarted run builds tracker and finder from the parameters stored in the dump
(`puncture_setup` is skipped on a restart) and reads the tracker position from it.
Expected: tracker positions, horizon mass and the particle history of cycles 5 to 8
agree to 1e-10 relative (a Z4c restart is not bitwise, scripts/README.md); the horizon
is found in both. Refuted by a missing tracker or finder after the restart, or by
differences above 1e-8.

### 1b, second launch cancelled: the wave zone was too large

Run `core-20261115-120038-70a5190` (A) started with 1156 MeshBlocks, 448 on level 1 and
500 on level 2: the refined region of +-18 for the wave extraction is rounded outward
to whole parent blocks and became +-32 at level 2 and the whole domain at level 1. At
6.5e6 zone-cycles per second that is 31 minutes per run. Cancelled after 30 s, with
the four runs queued behind it (`-120040-`, `-120041-`, `-120043-`, `-120044-`, never
started). New wave zone: cells of 1/2 within 15.9 of the origin (the eight level-1
blocks around it), spheres at 10 and 14; initial mesh 428 MeshBlocks (`athena -m 1`).
Predictions unchanged, with "the sphere at 14" for the energy.

(Note on this file: the two references to check scripts under `scratch/core/tmp/` in
the entries above were replaced by the in-tree script
`tracks/core/analysis/mp/check_bowen_york.py`, which contains the same checks and was
rerun: all pass, same numbers.)

### Outcome of the restart check (processors; `core-20261115-120935-9211dcd` uninterrupted, `core-20261115-121543-2e16f45` restarted from its dump of cycle 4)

The restarted run has its tracker and its finder (built from the parameters in the
dump) and the two tracers. Tracker rows of cycles 4 to 7: identical in all 19 printed
digits. Horizon summary at t = 0.125 and 0.1875: identical in all 16 digits (masses
1.023427462744472, 1.018949192206834). Particle history: identical. Z4c history
(six printed digits): identical except the last digit of the Theta norm at one time
(7.17374e-07 against 7.17375e-07). Prediction held within what the files print; the
"1e-10" could only be tested on the tracker and horizon files. Observation: on this
coarse mesh (cells 1/8, puncture with momentum 0.3 and spin 0.2 off the block
corners) the finder returns no horizon at t = 0 and 0.0625 and finds it from
t = 0.125 on, in both runs. [VERIFIED]

### Final source (hooks moved, 3b7e537): verification of the rebuilt processor executable

 - `problems/tests/regress_cf.athinput`: run `core-20261115-121953-c94f288` against the
   executable of `main` (`core-20261115-113321-a5197ba`): all 13 data files identical
   byte for byte. [VERIFIED]
 - Bowen-York cases against the build before the move: `s_two_approx_n64`
   (`core-20261115-122035-c94f288` against `-115119-4745494`) identical byte for byte;
   `s_p0.3_table_n64` and `s_ps_approx_n64` (`-122036-`, `-122037-` against
   `-114158-c89b6e3`, `-114227-c89b6e3`): field data identical, the files differ only
   in the parameter dump of their header (the line `corr_background` added to the
   input since). [VERIFIED]
 - Trial merge with `core/id-extrinsic` (1311b8e) by `git merge-tree`: no conflict
   markers. Its `CFSetExtrinsic` assigns `vK_dd` after the main loop: with a table of
   format 2 and a moving puncture in the same run the Bowen-York curvature would be
   overwritten; `+=` there fixes it (not my file to change on that branch).
 - The card executable of the final source is built in `.work/build_gpu_final`; the
   runs already queued use the build of 7a60df2 (same kernel code; only the place of
   the reader call and of a log line differ).

### Test 3 started; heavy horizon not found in the first searches; diagnostic

Card run `core-20261115-120834-d08c476` (t3) at t = 1: light horizons found from the
first search (0.5358 and 0.5448, inside the predicted ranges), heavy horizon not found
(nan rows). Two explanations, to be told apart by four one-cycle runs on processors
with the verbose finder (`problems/tests/by_horizon_coarse.athinput`: the heavy hole
alone, same cells of m/10, flow constant 100, 25, 5, 1), written before they finish:
 - H1, the flow constant m^2 = 100 is too large: the flow overshoots with 100 and
   converges with a smaller constant;
 - H2, the mesh at m/10 is too coarse for the finder at the start: no constant
   converges at the first search (the restart check on cells of m/8 also missed the
   first two searches and then found the horizon).
 Prediction [JUDGEMENT]: H2, and the card run finds the heavy horizon later.

### Outcome of the finder diagnostic: neither hypothesis; the cause is `hmean_tol`

Processor runs, one cycle, the heavy hole alone on cells of m/10:
 - first guess a sphere of radius m/2 (what the finder takes for a single puncture),
   flow constants 100, 25, 5, 1 (`core-20261115-122312-8e699b1`, `-122314-`,
   `-122315-`, `-122316-`): horizon found in every case, Christodoulou mass 10.348
   (irreducible 10.244), S_z = 29.981 for S = 30 (sign and size of the Bowen-York
   spin confirmed by the finder's integral). [VERIFIED] The search stops after two or
   three steps because the stopping rule is "mass changed by less than mass_tol": with
   a small flow constant it stops where it started (constant 1: radius 5.0001 after
   one step), so a too small constant passes for convergence.
 - first guess a sphere of radius m = 10 (what the finder takes when other punctures
   are far away, as in the three-black-hole run), same four constants
   (`-122626-`, `-122627-`, `-122628-`, `-122630-`): every search ends at step 0 with
   "Failed, hmean > 100": the surface integral of the expansion is 186.6 there, and
   the tolerance `hmean_tol` = 100 that `puncture_setup` writes (the value of the
   existing inputs) is an absolute number while the integral grows in proportion to
   the mass. H1 (constant too large) and H2 (mesh too coarse) are both wrong; my
   prediction of H2 failed.
 Fix: `puncture_setup` writes `hmean_tol_<n> = 100 max(1, m)`.

**Prediction before the check of the fix** (processors, same input, first guess of
radius 10, constant 100, `hmean_tol_0 = 1000`): the flow contracts from radius 10 to
the horizon near 5 and stops with Christodoulou mass 10.348 +- 0.005 and S_z = 29.98
within 400 steps. Refuted by a failure (negative radius, no convergence): then the
scaling of the flow constant with m^2 is wrong for a first guess twice too large.

### Outcome of the check of the finder fix (processors, `core-20261115-122832-1cf6d89`)

Prediction held: from a first guess of radius 10 with flow constant 100 and
`hmean_tol_0 = 1000` the flow contracts monotonically (radius 10, 9.37, 8.81, ...,
5.07; integrated expansion 187 falling to 1.9) and stops at step 31 with Christodoulou
mass 10.3483 (irreducible 10.2443) and S_z = 29.981. The flow constant m^2 is stable
for a first guess twice too large. [VERIFIED] The three-black-hole card run in
progress was started before the fix and will have no heavy horizon; a short card run
with the final executable is to show the three horizons together.

### Predictions for the card checks of the final executable (before they run)

 - `problems/puncture/tracers_headon.athinput`, 24 cycles, executable of the final
   source (`.work/build_gpu_final`): data files identical byte for byte to those of the
   executable of `main` (run `core-20261115-113546-a5197ba`); restart files identical
   except the uninitialised header bytes.
 - Three black holes to t = 1 with the final executable (`hmean_tol_2 = 1000` from the
   fixed set-up): three horizons from the first search; heavy hole: Christodoulou mass
   10.40 +- 0.05 (10.348 alone, times the background factor 1.005), S_z = 30 +- 0.1;
   light holes 0.5358 and 0.5448 as in the first card run.

### Outcome of test 3, evolution (card run `core-20261115-120834-d08c476`, executable of 7a60df2, to t = 16)

Numbers from `tracks/core/analysis/mp/multi_check.py` (`multi_check.json`), figure
`figs/triple_evolution.png` (looked at).
 - Ran to the end: 1024 cycles in 574 s (0.159 card-hours), 8.8e6 zone-cycles per
   second, 1100 MeshBlocks at the start, 1226 at the end (168 created, 42 removed),
   peak card memory 63.1 GB with the block limit 2400 and three finders. History volume
   constant to 2e-5, all norms finite. Prediction held.
 - Light horizons found in all 64 searches. Masses: A 0.5410 at t = 0, between 0.5353
   and 0.5483, 0.5483 at the end; B 0.5497, between 0.5448 and 0.5589, 0.5578 at the
   end. Inside the predicted ranges; they scatter by one percent during the first
   2.5 M (the transient of the punctures on cells of m/8) and then rise by 0.5 percent
   to t = 16. Spins below 1.2e-3.
 - Heavy horizon: never found (64 searches). Prediction FAILED; cause found and fixed
   (the finder tolerance `hmean_tol`, entries above), to be shown in the short run with
   the final executable.
 - Trackers: light holes moved by (+1.05, +1.09) and (+2.48, +1.20), along their
   momenta (prediction held), speeds 0.099 and 0.201 at the end, that is 0.63 and 0.70
   of P/m (0.158 and 0.287), still rising. The line between them turned by +0.14 rad,
   separation 10.00. The heavy hole's tracker moved by (+2.4e-4, +3.0e-4): hardly at
   all, and not toward -x, -y. Prediction FAILED.
   Candidate explanation [JUDGEMENT, not tested yet]: the tracker follows minus the
   shift, the shift is damped at the rate `shift_eta` = 2 in code units, that is
   eta m = 1 for the light holes and 20 for the heavy one, so the shift at the heavy
   puncture builds up twenty times more slowly in units of its own mass; 16 time units
   are 1.6 m of the heavy hole.
 - Constraint norms (history): H 8.5e-6 at t = 0, peak 5.2e-3 at t = 2.0, 7.8e-5 at
   the end; momentum 4.7e-7, peak 5.6e-5, 3.9e-5 at the end. Prediction "within a
   factor 30" FAILED: the norm rises 600 times in the first two M and settles nine
   times above its start. The rise comes with the gauge transient of the light
   punctures on cells of m/8 (the horizon masses scatter at the same time); the
   residual of the initial data (2e-6 closed form) is far below what the evolution of
   the punctures produces on this mesh. The quality of the initial data cannot be
   read from the evolved norm at this resolution.

**Prediction for a test of the explanation of the slow heavy tracker** (card, short):
the single hole of 1b (E) (m = 1, P = 0.043, S = 0.3) run again with
`z4c/shift_eta = 20` to t = 5. If the damping is the reason, the tracker speed at
t = 1.6 is at least five times smaller than in run (E) with `shift_eta = 2`, and the
displacement at t = 1.6 is below 1e-3. If the speeds are equal within a factor 2 the
explanation is wrong.

### Outcome of test 2 (card run `core-20261115-120835-d08c476`, executable of 7a60df2, to t = 30)

Numbers from `multi_check.py` (`multi_check.json`), figure `figs/binary_evolution.png`
(looked at: two symmetric arcs, counter-clockwise, bending inward).
 - 1920 cycles in 700 s (0.194 card-hours), 8.4e6 zone-cycles per second, 568
   MeshBlocks at the start, 932 at the end (392 created, 28 removed), peak card memory
   58.5 GB (block limit 2400, two finders).
 - Mean of the two trackers within 3.6e-14 of the origin, z below 4e-14. Held.
 - Both punctures start along their momenta; the line turns counter-clockwise by
   0.527 rad at t = 30 (Newtonian rate would give 0.95). Held.
 - Tracker speed: 0.075 within 2.5 M, then a slow rise to 0.109 at t = 30, 0.69 of
   P/m = 0.158. Held (range 0.5 to 1.1), but the speed is not settled.
 - Coordinate separation: 10.00, 9.88 at t = 10, 9.08 at t = 30, shrinking faster with
   time. Inside 10 +- 1 at t = 30 as predicted, though it would leave that band soon
   after. With the trackers at 0.7 of the circular speed the punctures fall inward in
   these coordinates; whether that is the lag of the gauge (the tracker follows minus
   the shift, which starts at zero) or the orbit itself cannot be told from this run
   [TO VERIFY at higher resolution and with a longer run].
 - Horizons found in all 120 searches of each hole; masses 0.5096 at t = 0, between
   0.5034 and 0.5166 during the first 2.5 M, 0.5156 at the end; the two agree to 3e-7.
   Predicted 0.510 to 0.520 and constant to one percent: the first value is 0.0004
   below the range and the early scatter is 1.3 percent: FAILED by these margins; from
   t = 3 on the masses are within the range and drift by +0.3 percent.
 - History norms: H 9.6e-5 at t = 0 (truncation at the punctures on cells of m/8;
   the closed-form residual with the correction is 5.6e-6), peak 2.2e-3 at t = 1.25,
   8.4e-4 at t = 30; momentum 1.8e-6, peak 5.6e-4, 4.6e-4 at the end. Bounded, but as
   in test 3 set by the evolution of the punctures, not by the initial data.

### Outcome of test 1b (card runs, executable of 7a60df2, finest cells 1/16)

Runs: (A) `core-20261115-121046-0c197fb` P = 0.3 `approx`; (B) `-121049-` P = 0.3
`none`; (C) `-121047-` stock generator v = 0.2844; (D) `-121052-` P = 0.6 `approx` to
t = 30; (E) `-121050-` P = 0.043, S = 0.3 `approx`; and the stopped 1/32 reference
`core-20261115-115342-7a60df2` (to t = 10.5). Numbers from `boost_check.py`
(`boost_check.json`); figures `figs/boost_evolution.png`, `figs/boost_waves.png`
(both looked at). Each 40 M run: 554 to 575 s (0.154 to 0.160 card-hours), 7.7e6
zone-cycles per second, 428 MeshBlocks at the start and 456 at the end (block count
prediction held).

| run | mean tracker speed 10-20 | 20-30 | 30-40 | at the end | horizon mass first | last |
|---|---|---|---|---|---|---|
| A | 0.1365 | 0.1582 | 0.1748 | 0.1813 | 1.01072 | 1.01081 |
| B | 0.1384 | 0.1595 | 0.1760 | 0.1825 | 1.00009 | 1.00459 |
| C | 0.1327 | 0.1554 | 0.1726 | 0.1793 | 1.01099 | 1.01094 |
| D | 0.2333 | 0.2727 | (ends at 30) | 0.2928 | 1.04462 | 1.04108 |
| E | 0.0197 | 0.0226 | 0.0249 | 0.0257 | 1.03531 | 1.03464 |

 - Direction: all trackers move along +P. Held.
 - Speed. (A) over 30 < t < 40: 0.1748 = 0.615 of P/M_ADM (0.2844): inside the revised
   band [0.6, 1.05], at its lower edge; the original prediction (within 10 percent of
   P/M_ADM between t = 20 and 40) FAILED. (A), (B), (C) agree within 2 percent in every
   window (predicted 15): the Bowen-York puncture and the stock boosted slice move
   alike from t = 5 on, and the 1/32 reference lies on the 1/16 one where it exists
   (speed 0.1279 against 0.1278 at t = 10.47, displacement 1.0263 against 1.0261;
   at t = 5: 0.1054 against 0.1070). So the slow rise is the gauge (the shift builds
   up slowly), not the data and not the resolution.
 - Speed against momentum: the ratio of the tracker speed to P/M_ADM is the same for
   the three momenta at equal times: over 20 < t < 30 it is 0.556 (P = 0.3), 0.547
   (P = 0.6, M_ADM = 1.204), 0.545 (P = 0.043 with spin, M_ADM = 1.036 to second
   order); over 10 < t < 20 it is 0.48, 0.47, 0.47. The tracker speed is proportional
   to P/M_ADM with a factor that depends on time only. The corrected and uncorrected
   data cannot be told apart by it (0.7 percent), as expected.
 - Horizon mass. (A): 1.01072 at the first search, 1.01081 at the end (predicted
   1.011 +- 0.005; sqrt(M_ADM^2 - P^2) = 1.0112); constant to 2e-4. (B): 1.00009,
   that is 1.05 percent lower (predicted "up to one percent"), dips to 0.997 at t = 5
   and rises to 1.0046: the uncorrected data settle to a hole 0.6 percent lighter than
   the corrected ones. (D): 1.0446 falling to 1.0411 (full solution: sqrt(1.20401^2 -
   0.36) = 1.0439). (E): 1.0353 (Christodoulou), S = 0.2997 at every search (predicted
   0.30 +- 0.01: held; sign as given).
 - Hamiltonian norm (history): at t = 0 2.3e-6 (A), 5.4e-5 (B), 5.6e-7 (C), 3.2e-5 (D),
   7.5e-6 (E); from t = 8 on all runs sit at 2e-5 (the 1/32 reference at 3.8e-6). The
   correction lowers the initial norm 23 times; after the gauge transient the norm is
   that of the evolved puncture on this mesh, the same for the exact boosted slice.
 - Burst of radiation, energy through the spheres over the run (news with constant and
   linear drift removed; without the removal in brackets):
   r = 14: A 1.42e-4 (9.0e-4), B 1.59e-4 (9.5e-4), C 5.9e-5 (4.9e-4), D 1.91e-3
   (1.2e-2), E 7.3e-6 (3.8e-4); r = 10: A 2.9e-4, B 3.2e-4, C 2.4e-4, D 1.74e-3,
   E 1.6e-5. The stock boosted slice (C) has no burst in its data; its numbers are the
   floor of this estimate (the field of a hole moving off-centre inside the sphere and
   the gauge transient): 6e-5 at 14 and 2.4e-4 at 10. Above that floor: (A) about
   1e-4 m at 14 (not resolved at 10), (D) 1.8e-3 m at both radii, a ratio of 16 to 20
   for twice the momentum, that is E about 1.3e-2 (P/m)^4 m. (B) exceeds (A) by 12
   percent; (E) is below the floor. Predictions held (below 1e-3 for A and E, B above
   A); the estimate is good to a factor two at best.
 - Early reference observation stands: the stock generator's tracker starts at 0.280,
   falls to 0.040 by t = 1.5 and then follows the same curve as the Bowen-York data.

(Correction to the entry above, made in place: the comparison of the two resolutions of
the reference first carried a number for the 1/16 run, 0.1284, that I had not computed;
the values now given, 0.1278 at t = 10.47 and the displacements, are read from the
tracker files of `core-20261115-115342-7a60df2` and `core-20261115-121047-0c197fb`.)

### The last three card runs wait behind seven jobs of other owners; substitutes on processors (predictions before they run)

Queued on the cards and not started: the regression with the final executable, the
three black holes to t = 1 with the final executable, and the single hole with
`shift_eta = 20`. The scheduler's estimate for them is several hours. Substitutes that
answer the same questions on processors:
 - Three black holes, one cycle, final processor executable (`time/nlim=1`; the finder
   searches after the first step): prediction as for the card run: three horizons at
   the first search, heavy hole 10.40 +- 0.05 with S_z = 30 +- 0.1, light holes 0.541
   and 0.550 (the values at t = 0 of the 16 M run).
 - Shift damping: `problems/tests/puncture_setup_restart.athinput` (m = 1, P = 0.3,
   S = 0.2, cells 1/8) for 52 cycles (t = 1.625) with `shift_eta` = 2 and 20.
   Prediction: the tracker speed at the end is at least five times smaller with 20
   than with 2. If the two agree within a factor 2 the damping does not explain the
   heavy tracker of test 3.

### Outcome: three horizons with the final source (processors, `core-20261115-131206-372e977`, one cycle)

Prediction held. First search of the three finders: light holes 0.5409674769678748 and
0.5497393844448359, the same digits as the first search of the 16 M card run with the
earlier executable; heavy hole Christodoulou mass 10.3996, S_z = 29.9815 (alone:
10.348; times the background factor 1.0052: 10.402). The heavy horizon is found with
the mass-scaled tolerance and the flow constant m^2 = 100 in the full configuration.
[VERIFIED]

### Merge check repeated properly

My first trial merge with `core/id-extrinsic` was read with a grep that treated the
output as binary and reported nothing; read as text it showed one conflict, in
`docs/FORMATS.md` (both branches inserted a section at the same place), and none in
`nrpic_cf.cpp`. The section now stands before "Radial table" (`core/newton` appends at
the end of that file). Trial merges with `main` (a1c2237), `core/id-extrinsic`
(6fa6472), `core/newton` (ce329f5), `core/rng` (a6e5c46), `core/nrpic` (c37eeca),
`core/collisions` (3436846), `core/scalar-field` (b28ecca): no conflict markers.
[VERIFIED] `CFSetExtrinsic` of `core/id-extrinsic` still assigns `vK_dd` with `=`
after the main loop (line 369 of its `nrpic_cf.cpp`).
