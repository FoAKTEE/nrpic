# Horizon finder in periodic boxes: what limits the flow, the weighted flow, a start scan, a check of the accepted surface

Owner core. Branch `core/faces-finder` (batch 34a, 2026-11-27), candidate for release
core-v0.9; proposal for `coord/INTERFACES/finder_box.md` (it extends `finder_stop.md` of
core-v0.8). Requests served: Track A `finder-false-accept-and-stall-p0l6` and
`finder-slow-convergence-box` (decision 0047 items 4 and 6; condition (b) of the track's
gate G2). Evidence and every number: `tracks/core/JOURNAL-faces-finder.md` (entries 1 to
3, 6); scripts `tracks/core/analysis/faces_finder/finder_box.py`, `fig_finder.py`,
`finder_bytes.py`, cases `case_*.json` there. Executables:
`/data/haiyangw/nrpic/scratch/core/exe/core_faces-finder/` (READY there). The restart
files are Track A's: S1L `scratch/A-emd-pbh/A-20261123-025907-97bab8d/rst/peak.00019.rst`
(t = 220, triaxial, four levels), P0L6 `scratch/A-emd-pbh/A-20261125-044641-7d5bd16/rst/
peak.00017.rst` (t = 140, six levels) and `peak.00016.rst` (t = 130, no trapped round
sphere by the track's scan).

## 1. What limits the convergence [VERIFIED for the step; the rate at a horizon by the Schwarzschild case]

The finder moves the surface r(theta, phi) by a_lm -> a_lm - A/(1 + B l(l+1)) rho_lm with
A = alpha/(lmax(lmax+1)) + alpha/2 (`flow_alpha_beta_const_<n>` = alpha, 1 when absent)
and a flow function rho chosen by one key for all horizons of the run:

```
<fastflow>
flow = standard      # rho = H |grad F|                 (when absent)
flow = shear         # rho = H |grad F| sigma, sigma = 2 r^2 / (...)   (Gundlach's weight)
flow = expansion     # rho = H
```

(`z4c/fastflow.cpp` 67 to 72 and 1428 to 1452; H the expansion, F = r - h.) For a round
sphere of coordinate radius r and areal radius R in a conformally flat metric |grad F| =
r/R and sigma = R^2, so one iteration moves the mean radius by

    standard:  delta r = - A H r/R          shear:  delta r = - A H r R.

The step of the standard flow has the dimension 1/length: the flow is not invariant
under the unit of length. Near a Schwarzschild horizon of mass m in isotropic
coordinates one iteration removes the fraction A/(4 m^2) of the distance to the horizon
with the standard flow (0.13 for m = 1, 0.0013 for m = 10) and the fraction A = 0.51 with
the weighted flow, whatever m. A puncture in units of its mass is the case the default
was made for. Track A's boxes hold holes of area mass 6.3 and 10.7 in code units, in
comoving coordinates whose R/r is 70 to 180.

Measured on S1L at t = 220 with release core-v0.8 (run core-20261127-233027-4fdb05d): from
0.6 the mean radius falls by 1.719e-4 per iteration (the formula above with the area and
the expansion integral of the status file gives 1.722e-4), from 0.2 by 3.4e-5, from 0.1 it
rises by 4.3e-5; nothing oscillates; the mass changes by 1e-3 to 4e-3 per iteration, so
`mass_tol = 1e-5` is never met and every search ends at its cap. That is the "stall" of
the card runs (reason 6), and the 915 to 3444 iterations of the track's processor runs.

## 2. The cure needs no new source: `flow = shear` [VERIFIED on both files, release core-v0.8 and this branch]

`fastflow/flow=shear` on the command line (the key is in the stored input of every run,
so it can be set in a continued run with any release), or `flow = shear` in the deck.
Searches with `mass_tol 1e-5`, `polish_iterations 100`, `flow_iterations 400`:

| File | Start radius | Found after | Area mass | Mean radius | Expansion integral |
|---|---|---|---|---|---|
| S1L t = 220 | 0.6 (the deck's), 0.2, 0.1, 0.03, 1.5 | 125 to 139 | 10.73958041 (the five equal to 1e-13) | 0.16195874 | -1.9e-5 |
| S1L, alpha = 0.5 | 0.6, 0.1 | 156, 157 | the same to 1e-12 | | |
| S1L, `mass_tol 1e-9`, no polishing | 0.6 | 47 | 10.73958041 | | |
| P0L6 t = 140 | 0.15 (the deck's), 0.6, 0.05 | 138 to 144 | 6.30324213 | 0.10398630 | 2.5e-5 |
| P0L6 t = 130 (nothing trapped) | 0.15, 0.6 | not found: mean radius negative (reason 4) after 16 and 18 iterations | | | |

Runs core-20261127-233526-05eba1f, core-20261127-233531-d12e417 (core-v0.8),
core-20261127-235215-27c6606, core-20261127-235657-57b524a, core-20261127-235631-a5e5818
(this branch). A hundred of the iterations are the polishing; from 0.6 the radius goes
0.600, 0.272, 0.206, 0.185, 0.175, ... The surfaces Track A found with the standard flow
(S1L: 10.73, 0.161, expansion integral -0.63 after 1927 iterations from 0.16) are the
same horizon, less converged: with the standard flow and a start scan (section 3) the
search ends after 241 iterations at mass 10.7274, 1.1e-3 below, with a surface that is
still nearly round (smallest radius 0.1596 against 0.1565 of the converged one).

Where no round sphere is trapped the weighted flow shrinks the surface to a point in
under twenty iterations and reports not found; the standard flow wanders to its cap
(from 0.15 to 0.107 and from 0.6 to 0.452 in 400 iterations on P0L6 at t = 130, run
core-20261127-235652-ac88116).

**Recommended for a box run** (Track A; any run whose horizon is not about one unit of
length in mass): `flow = shear`, `mass_tol_<n> = 1e-5`, `polish_iterations_<n> = 100`,
`flow_iterations_<n> = 400`, `trapped_tol_<n> = 0.01`, `diagnostics = true`; the start
radius of the deck may stay. 4000 iterations and a hand-made start radius are not
needed. Puncture runs of Tracks C, D and F (mass about one) keep the default flow: their
masses were calibrated with it, and the weighted flow was not tested on a puncture in
this session.

## 3. Two options, both off when absent

```
<fastflow>
start_scan_<n>      = N      # integer, 0 or >= 2; absent or 0: off
start_scan_rmax_<n> = r      # largest radius of the scan; absent: initial_radius_<n>
start_scan_rmin_<n> = r      # smallest radius; absent: start_scan_rmax_<n>/32
trapped_tol_<n>     = x      # real >= 0; absent or 0: off
```

Read only when the input holds them (the parameter dump of an input without them does
not change), at every start of a run: they can be given to a continued run on the
command line (`restart_parameters.md`).

**`start_scan_<n> = N`.** A search that would start from `initial_radius_<n>` (the first
search, and every search after one that was not found; not a horizon tied to a puncture,
whose start comes from the puncture) first evaluates N round spheres about the centre,
with radii spaced by a constant factor from rmin to rmax, and takes the outermost one on
which the surface integral of the expansion is negative. The start is put where the mean
expansion changes sign between that sphere and the next one outwards (linear in the
logarithm of the radius), or on the outermost sphere if that one is trapped too. If the
integral is negative on no sphere there is no flow: the search is not found with reason
8 and zero iterations, at the cost of N evaluations. A sphere with a point outside the
mesh counts as not trapped. With `verbose = true` the verbose file holds the table of
the scan.

**`trapped_tol_<n> = x`.** A surface that the mass rule (with its polishing) would accept
is accepted only if its smallest radius is positive and

    sqrt(area mean of H^2) x area mass < x

(1/m is the expansion of a round sphere of that area in flat space, so the number is the
rms expansion in that unit; it is 1.6e-3 on the converged horizon of S1L and 0.5 on a
sphere well outside it). Otherwise the flow goes on. A search that reaches its cap after
the mass rule was met on a refused surface ends with reason 7.

**Status file.** New reasons in column 4: `7` "iteration limit reached: mass rule met,
surface not trapped to trapped_tol", `8` "no round sphere of the start scan has a negative
expansion integral". For a horizon with either option three columns follow the centre:
`16:rms_expansion_x_area_mass` (of the last surface evaluated, found or not),
`17:scan_start_radius` (0 without a scan), `18:scan_trapped_spheres` (-1 without a scan).
A status file begun without the options keeps its header; the columns are counted from
the left. After reason 8, columns 6 to 10 describe the least expanding sphere of the scan.

## 4. Tests of the options [VERIFIED, processors, this branch; one cycle on each restart file]

| File, flow | Member | Outcome |
|---|---|---|
| S1L, standard | finder's default `mass_tol 1e-2` from 0.6, no check | **found** at iteration 2: radius 0.5998, mass 21.82, column 16 would be 0.5: a false acceptance |
| S1L, standard | the same with `trapped_tol 0.05` | not found, reason 7, 400 iterations, column 16 = 0.50 |
| P0L6 t = 130, standard | `mass_tol 1e-2` from 0.6, no check | **found** at iteration 2 (radius 0.5996, mass 15.33) where nothing is trapped |
| P0L6 t = 130, standard | the same with `trapped_tol 0.05` | not found, reason 7 |
| P0L6 t = 130, either flow | `start_scan 24` from 0.15 and 0.6 | not found, reason 8, no iteration |
| S1L, either flow | `start_scan 24` (0.01875 to 0.6) | 12 spheres trapped (0.0295 to 0.155), start 0.16151 (the horizon: 0.16196) |
| S1L, standard | scan, `trapped_tol 0.05`, cap 400 or 4000 | found after 241: mass 10.7274, column 16 = 0.042 (a tolerance of 0.01 would refuse it) |
| S1L, shear | `trapped_tol 0.05` | found after 127, the surface of section 2, column 16 = 1.565e-3 |
| S1L, shear | scan and check | found after 114 (100 of them polishing), the same surface |
| S1L, shear | scan and check, no polishing | found after 14: mass 10.739569 (1.2e-5 below) |
| P0L6 t = 140, either flow | `start_scan 24` (0.0047 to 0.15) | 10 spheres trapped, start 0.103970 (the horizon: 0.103986) |
| P0L6 t = 140, shear | scan and check | found after 113, mass 6.30324213, column 16 = 1.55e-3; without polishing 13, 6.303213 |
| P0L6 t = 140, standard | scan, `trapped_tol 0.05` | found after 102: mass 6.30262 (1e-4 below), column 16 = 6.8e-3; without the scan the search from 0.15 ends at its cap at radius 0.1295 |
| S1L and P0L6, shear | `mass_tol 1e-2`, no polishing, `trapped_tol 0.01` | found after 12 and 13 with masses 1.1e-3 and 4.2e-3 (relative) too high, column 16 = 1.9e-3 and 3.1e-3: the check does not replace a tight mass rule |
| P0L6 t = 130, both flows | searches without scan, `trapped_tol 0.05` | none found; column 16 of the last surface 0.11 to 1.0 |

Runs core-20261127-235152-d46d2d2 (S1L, standard), core-20261127-235215-27c6606 (S1L,
shear), core-20261127-235652-ac88116 and core-20261127-235631-a5e5818 (P0L6 t = 130),
core-20261127-235657-57b524a (P0L6 t = 140, shear), core-20261128-000217-460058c (P0L6
t = 140, standard); table `finder_table.json` and figure `fig_finder.png` of run
core-20261128-000846-a3722c7 (`fig_finder.py`; journal entry 6).

Without the options the finder writes the bytes of core-v0.8: `finder_bytes.py` on
`problems/tests/by_horizon_coarse.athinput` and `finder_polish.athinput` with
diagnostics (journal entry 6, READY).

## 5. What is not done, and limits

- **The false acceptance of P0L6 at t = 118.12 is not retested**: no restart file lies
  between t = 110 and 120. Its record (mass 562, mean radius 18.2, smallest radius -3.59,
  expansion integral 2.08e5: Track A's status file) fails `trapped_tol` twice over: the
  smallest radius is negative, and the mean expansion times the mass alone is 7.4. The
  same class of event, a mass rule met where nothing is trapped, is reproduced and
  refused on P0L6 at t = 130 and on S1L (first four rows of section 4), with the loose
  default tolerance and not with the tolerance 1e-5 of the track's deck. Whether the
  flow of that search would have been stopped earlier by the weighted flow is not known.
- The scan sees round spheres about the centre of the input. A horizon that holds no
  trapped round sphere about that centre (strongly aspherical, or off centre) is not
  searched for with `start_scan`; the weighted flow without the scan has no such limit
  [JUDGEMENT; S1L, the triaxial run, holds trapped round spheres from its first found
  horizon on, by Track A's dating].
- `trapped_tol` measures the residual of the surface on the finder's angular grid: its
  floor depends on `ntheta`, `lmax`, the cells and the slice (1.6e-3 here; 0.04 to 0.14
  for a puncture in its first 2 M by the numbers of `finder_stop.md` section 2). Give a
  value several times the floor of a converged surface of the run; 0.01 for Track A's
  boxes.
- `flow`, `ntheta`, `lmax` are one value for all horizons of a run.
- The weighted flow with alpha = 1 steps in flat space from r to -0.03 r: where nothing is
  trapped the search ends by "mean radius negative" (reason 4) or "area mass below
  1e-10" (reason 5), not by the cap. `flow_alpha_beta_const_<n> = 0.5` halves the step
  (found after 156 instead of 127 iterations on S1L).
- Card build: one check queued (READY, journal). Several ranks: not tested.
