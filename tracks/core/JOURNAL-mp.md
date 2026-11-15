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

`scratch/core/tmp/check_by.py`, `check_by2.py` on `python/nrpic/bowen_york.py`:
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

Closed forms only (no simulation; `scratch/core/tmp/bg_check.py`), rms of H over the
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
