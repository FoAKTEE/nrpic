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
