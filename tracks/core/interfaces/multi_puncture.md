# Interface proposal: several black holes with linear momentum and spin

Status: PROPOSED by core (branch `core/multi-puncture`, 2026-11-15). For the
orchestrator (acceptance into `coord/INTERFACES/`), Track F (three black holes), Track D
(black hole with matter) and the first paper (moving punctures in a cluster).
Evidence: `tracks/core/JOURNAL-mp.md` (predictions and outcomes), run manifests under
`tracks/core/runs/`, analysis and figures under `tracks/core/analysis/mp/`.
Units G = c = 1. Labels: [VERIFIED] measured in a registered run or read from a source
with a locator; [BACKGROUND]; [JUDGEMENT]; [TO VERIFY].

## 1. What exists

In the problem generator `nrpic_cf` (conformally flat data, `gamma_ij = psi^4 delta_ij`,
`psi = 1 + sum_c u_c`), every component of type `puncture` may now carry

- a linear momentum and a spin: Bowen-York extrinsic curvature;
- a regular correction of its conformal factor: none, a closed form (second order in
  momentum and spin, rescaled by the conformal factor of the other punctures), or a
  table of multipoles read from a file;
- on request a tracker, an initial refined region and an apparent-horizon finder,
  written into the input parameters before the mesh is built.

Punctures superpose with the matter components of `nrpic_cf` (tables, Gaussians,
spheroid) and with particles exactly as before. Without the new parameters the
generator behaves bit-identically (section 8, test R).

Source: `athenak/src/pgen/nrpic/nrpic_bowen_york.hpp` (curvature and corrections),
`athenak/src/pgen/nrpic/nrpic_puncture_setup.hpp` (trackers, regions, finders), hooks in
`nrpic_cf.cpp` and `main.cpp` (section 10). Reference solutions and table writer:
`python/nrpic/bowen_york.py`. No elliptic solver is involved; one on the mesh comes
later (decision 0010, item 4).

## 2. Parameters

All in `<problem>` with `pgen_name = nrpic_cf`; `<c>` is the component index.

| Parameter | Meaning | Default |
|---|---|---|
| `comp<c>_type = puncture`, `comp<c>_mass`, `comp<c>_x1..3` | as before: bare mass `m` and position | position 0 |
| `comp<c>_p1`, `_p2`, `_p3` | Bowen-York linear momentum `P` (Cartesian) | 0 |
| `comp<c>_s1`, `_s2`, `_s3` | Bowen-York spin `S` | 0 |
| `comp<c>_corr` | `none`, `approx` or `table`: regular correction `u_c` added to `psi` | `none` |
| `comp<c>_corr_file` | `table`: file, format `mp1` of `docs/FORMATS.md` | none |
| `comp<c>_corr_axis1..3` | `table`: symmetry axis | header of the file, else direction of `P`, else of `S` |
| `corr_background` | `approx`: rescale with the conformal factor of the other punctures (section 3) | `true` |
| `lapse` | as before; `precollapsed` gives `alpha = psi^-2` with the corrections in `psi` | `one` |
| `puncture_setup` | `true`: tracker, refined region and horizon finder for every puncture | off |
| `puncture_radius` | radius of the finest region around a puncture in units of its bare mass | 2 |
| `puncture_level` | refinement level of the lightest puncture | `<mesh_refinement> num_levels` - 1 |
| `puncture_horizons` | `false`: no finders | `true` |
| `comp<c>_radius`, `comp<c>_level` | override radius (length) and level of one puncture | from the two rules below |

`puncture_setup` numbers the punctures `n = 0, 1, ..` in the order of their components
and writes, for each, `<z4c> co_<n>_type = BH`, `co_<n>_x/_y/_z`, `co_<n>_mass`,
`co_<n>_radius`, `co_<n>_reflevel`; a block `<refined_region_punc<n>>` (cube of
half-width radius at that level); and in `<fastflow>` `use_puncture_<n> = n`,
`flow_iterations_<n> = 400`, `flow_alpha_beta_const_<n> = m^2`,
`mass_tol_<n> = 1e-5 m`, `hmean_tol_<n> = 100 max(1, m)`, `start_time_<n> = 0`,
`stop_time_<n> = 1e30`, and, if absent, `num_horizons`, `npunct`, `find_every = 16`,
`ntheta = 16`, `lmax = 8`, `metric_drvts = interpolant`. With adaptive refinement it sets
`<z4c_amr> method = tracker` and an `<amr_criterion_punc>` block with `method = user`
unless the input has its own. Rules:

- level of puncture `c` = `puncture_level - round(log2(m_c / m_lightest))`: cells
  proportional to the mass (a hole twenty times heavier gets cells sixteen times
  larger);
- the tracker gets 0.999 of the radius, the refined region all of it (section 4);
- the finder flow constant is `m^2` because the flow step relative to the horizon
  radius scales as the constant over the mass squared (update rule in `fastflow.cpp`;
  consistent with the constants that worked in the first paper's runs,
  `notes/results_brief_selfgravity.md` part D item 3). [VERIFIED for m = 10: section
  8, finder diagnostics] The stock tolerance `hmean_tol = 100` is an absolute bound on
  the surface integral of the expansion, which grows in proportion to the mass; with
  it a hole of mass 10 is rejected at the first step, hence `100 max(1, m)`;
- values the input file gives itself in `<fastflow>` are kept (a common-horizon finder
  can be added by hand with an index beyond the punctures and a larger
  `num_horizons`; not tested); tracker parameters `co_<n>_*` in the input are an
  error;
- a restart takes everything from the parameters stored in the restart file; the
  set-up routine runs only for new runs.

The command line can change only parameters that are present in the input file
(AthenaK rule): list `comp<c>_p1` and the like with value 0 if a variant is to switch
them on.

Example (the scouting configuration of section 8, test 3):

    <problem>
    pgen_name       = nrpic_cf
    ncomp           = 3
    comp0_type      = puncture
    comp0_mass      = 0.5
    comp0_x1        = -88.0
    comp0_x2        = 5.0
    comp0_p1        = 0.1013
    comp0_p2        = 0.1216
    comp0_corr      = approx
    ...
    comp2_type      = puncture
    comp2_mass      = 10.0
    comp2_x1        = 8.0
    comp2_p1        = -0.3608
    comp2_p2        = -0.2433
    comp2_s3        = 30.0
    comp2_corr      = approx
    lapse           = precollapsed
    puncture_setup  = true
    puncture_radius = 1.8

Inputs in the tree: `problems/puncture/by_static.athinput` (no evolution),
`by_boost.athinput`, `boosted_ref.athinput` (stock generator, for comparison),
`by_binary.athinput`, `by_triple.athinput`, `problems/tests/regress_cf.athinput`,
`problems/tests/puncture_setup_restart.athinput`.

## 3. The data

Each puncture at `x_c` contributes [VERIFIED: Brandt & Bruegmann,
arXiv:gr-qc/9703066v2, `main.tex` lines 116-122, Eq. 5]

    Abar_ij = 3/(2 r^2) [P_i n_j + P_j n_i - (delta_ij - n_i n_j) P.n]
            + 3/r^3 [(S x n)_i n_j + (S x n)_j n_i],     n = (x - x_c)/r,

and the generator sets `K_ij = psi^-2 sum_c Abar_ij`, `K = 0`, zero shift. Sign and
normalisation: the surface integrals of the code's convention give `P_ADM = P` and
`J_ADM = S` for one puncture (Python check, 1e-15), a puncture moves along `+P` and
the horizon finder returns `S` (tests 1b).

Mass parameters. `m` is the bare mass. For one corrected puncture the ADM mass is
`m + (5/8) P^2/m + (2/5) S^2/m^3` to second order [VERIFIED: arXiv:0711.1165v2,
`second.tex` lines 285-287; reproduced to 8 digits by the multipole solver]; the full
solution for `m = 1` gives 1.00623, 1.05474, 1.20401, 1.49932 for `P` = 0.1, 0.3, 0.6,
1.0 (`python/nrpic/bowen_york.py`). Horizon masses measured in the tests are in
section 8.

### Satisfied

- Momentum constraint, in vacuum, for any number of punctures: `Abar_ij` is traceless
  and divergence free. On the mesh the residual is truncation error only (sixth-order
  convergence with `nghost = 4`, linear in `P`). [VERIFIED: test 1a]
- Hamiltonian constraint of one isolated puncture, with `corr = table` and a table of
  the full solution: residual at the truncation error of the puncture itself.
  [VERIFIED: test 1a (v)]

### Violated, and by how much

- Hamiltonian constraint without correction: `H = -psi^-12 Abar_ij Abar^ij`
  exactly (the curvature part of the residual is algebraic), proportional to `P^2`.
  [VERIFIED: test 1a (i), (ii)]
- With `corr = approx` (closed form of arXiv:0711.1165, Eqs. 1 to 6): the residual of
  an isolated puncture is `Abar^2 psi^-5 (psi_BL^-7 - psi^-7)`, fourth order; 0.040 of
  the uncorrected root mean square at `P = 0.3 m`, 0.11 at `S = 0.4 m^2`.
  [VERIFIED: test 1a (iv), (vi)]
- Several punctures. Near puncture `c` the others add
  `Lambda_c - 1 = sum_{j != c} m_j/(2 d_cj)` to `psi`, and the source carries `psi^-7`.
  The plain sum of isolated corrections (the recipe of arXiv:0711.1165) then
  overshoots: for two punctures three masses apart it leaves a LARGER residual than no
  correction (3.83e-3 against 2.87e-3), and for the three-black-hole configuration it
  gains only a factor 1.7. The local equation with a constant background is the
  isolated one with rescaled parameters, so `approx` uses

      u_c = Lambda_c u_isolated(m_c/Lambda_c, P_c/Lambda_c^4, S_c/Lambda_c^4),

  which lowers the two-puncture residual 4.6 times and the three-black-hole one 9.8
  times (closed form; 2.65 times in the norm the code reports on the scouting mesh,
  where the truncation error of the light punctures is the larger part).
  `corr_background = false` gives the plain sum. [VERIFIED: tests 1a (viii), 3 at
  t = 0] What remains: the cross terms `Abar_c : Abar_j`, the gradient of the
  background across a puncture, and the fourth order.
- `Lambda_c` counts punctures only. Matter components (tables, Gaussians) near a
  moving puncture also raise `psi`; their effect on the correction is not included
  [TO VERIFY when Track D needs a moving black hole inside matter].
- With matter that moves, the momentum constraint has a source `8 pi psi^4 Stilde^i`
  that Bowen-York punctures do not supply: `coord/notes/design_wave2_initial_data.md`,
  section 3 (smeared Bowen-York curvature), not part of this package.

### Table of a correction

`python3 -m nrpic.bowen_york --mass m --momentum P --spin S --out file.tab` solves the
puncture equation for one puncture with `P` and `S` along one axis by multipoles and
writes format `mp1` (`docs/FORMATS.md`); `--linear` writes the second-order solution
(identical on the mesh to `approx`, test 1a), `--background d` the rescaled one. A
table is used as it is.

## 4. Trackers, refinement, horizons: what to expect

- The tracker integrates minus the shift at the puncture (`tracker_mode = ode`). With
  zero initial shift its speed starts at zero and approaches the coordinate speed of
  the hole only over tens of `m` (section 8, test 1b); the stock boosted-puncture
  generator, which starts with the boosted shift, loses it within `1/eta` and shows
  the same slow rise.
- Block count. With 16^3 MeshBlocks a tracker on a block corner of every level needs
  2x2x2 refined parents per level (56 leaves); off the corners in all directions it
  needs 3x3x3 (about 190 leaves per level and hole). Do not choose the radius equal
  to a multiple of the finest block size when the puncture starts on a block corner:
  round-off in the tracker then decides which neighbours are refined (journal, first
  attempt of 1b). Set `max_nmb_per_rank` for the generic count.
- Refined regions are rounded outward to whole parent blocks; a wave zone slightly
  larger than a block boundary can double the mesh (journal, second launch of 1b).

- The finder stops when the mass changes by less than `mass_tol` between two steps.
  A flow constant that is too small therefore passes for convergence without moving
  the surface (diagnostics of section 8); do not lower the constant below `m^2`
  without tightening `mass_tol`.
- Shift damping. `<z4c> shift_eta` is one number in code units. With holes of
  masses 0.5 and 10 and `shift_eta = 2`, `eta m` is 1 and 20; the heavy hole's tracker
  then barely moves (section 8, tests 3 and E20). [VERIFIED for the tracker; what it
  does to a long run is open, section 9]

## 5. Cost

All measured on one A100, RK4, `nghost = 4`, 16^3 MeshBlocks, finder every 16 cycles.

- The initial data cost nothing next to the evolution: closed forms per cell; a table
  adds a file of 20 000 rows per puncture.
- Throughput 7.7e6 to 8.8e6 zone-cycles per second (2.0e7 on a uniform mesh of 32^3
  blocks, `docs/TESTLOG.md` line 46). One time step for all levels,
  `dt = 0.25 * finest cell`.
- MeshBlocks: 428 to 456 for one hole on six levels with a wave zone (runs A to E),
  568 growing to 932 for two holes on six levels, 1100 growing to 1226 for the three
  black holes on eight levels. The count per hole and level is 56 on a block corner and
  about 190 off it (section 4).
- Card time: 0.154 to 0.160 card-hours for one hole for 40 m at cells of m/16
  (2560 cycles); 0.194 for the binary for 30 M at m/8 (1920 cycles); 0.159 for the
  three black holes for 16 M at m/8 (1024 cycles). A Hills passage of several hundred
  M at m/16 of the light holes is of order 10 to 20 card-hours.
- Memory is allocated for `max_nmb_per_rank`, not for the current count: 46.6 GB for a
  limit of 2048 with one finder, 58.5 GB for 2400 with two, 63.1 GB for 2400 with
  three (about 22 MB per block slot plus 2 MB per finder). A card holds a limit of
  about 3000.
- This package used 1.3 of its 3 card-hours.

## 6. With particles

The matter components and the particle file are untouched: `psi` superposes, the
Bowen-York curvature is added to `K_ij` after the generator's own `K_ij = 0`.
`problems/tests/puncture_setup_restart.athinput` runs a Bowen-York puncture with
tracers and a restart (section 8). Self-gravitating matter around a moving puncture
has not been run in this package.

## 7. Files

`docs/FORMATS.md`: "Puncture correction table (`*.tab`, format `mp1`)". Run outputs
are those of Z4c: `<base>.co_<n>.txt` (trackers), `<base>.horizon_summary_<n>.txt`,
`<base>.z4c.user.hst`, `waveforms/`.

## 8. Tests

Predictions and outcomes in full: `tracks/core/JOURNAL-mp.md`. Scripts and figures:
`tracks/core/analysis/mp/` (`check_bowen_york.py`, `run_static.sh` + `static_check.py`,
`boost_check.py`, `multi_check.py`, `triple_static.py`, `restart_check.sh` +
`restart_compare.py`; `figs/*.png`). Run ids are directories under
`tracks/core/runs/`; all with status `done` unless said.

| Test | Result | Runs |
|---|---|---|
| Reference module without simulation | `Abar` traceless, divergence free (6e-10); `P_ADM = P`, `J_ADM = S` (1e-15); closed form of arXiv:0711.1165 satisfies its equation for momentum, spin and both (4e-7 to 6e-6 of the source); multipole solver reproduces it (2e-6) and the ADM mass (1e-10) | `check_bowen_york.py` (no run) |
| R, old inputs unchanged | all data files identical byte for byte to the executable of `main`; restart files differ only in 7 to 35 bytes of uninitialised header memory (present before the change) | processors `core-20261115-113321-a5197ba` / `-113400-`, final source `-121953-c94f288`; card `-113546-` / `-113600-` |
| 1a, data on the mesh at t = 0 | `K_ij = psi^-2 Abar_ij` to single precision (2e-8 to 5e-8); `H` converges to `-psi^-12 Abar^2` at sixth order (1.88, 1.8e-2, 3.2e-4 at cells of 1/4, 1/8, 1/16); rms `H` 1 : 4.00 : 9.00 : 16.01 for `P` = 0.1 to 0.4; momentum residual linear in `P`, sixth order; `approx` leaves 0.040 of the residual at `P` = 0.3 (as its closed form), a table of the full solution leaves the truncation error of the puncture (0.3 percent); spin and cross term as the closed forms; two punctures: 2.87e-3 none, 3.83e-3 plain sum, 6.2e-4 with the background factor | 31 runs `s_*`, `core-20261115-114152-c89b6e3` to `-114238-`; `-115118-4745494` to `-115123-` |
| 1b, one hole evolved 40 m, cells m/16 | moves along `+P`; horizon mass 1.0107 at the first search for `P` = 0.3 corrected (predicted 1.011), constant to 2e-4; uncorrected 1.0001 rising to 1.0046; spin `S` = 0.2997 for 0.3; tracker speed equal to that of the stock boosted-puncture generator within 2 percent from t = 5 on, and the same at cells of 1/32 (0.1279 against 0.1278 at t = 10.5); it is 0.48, 0.55, 0.61 of `P/M_ADM` over t = 10-20, 20-30, 30-40, the same fraction for `P` = 0.043, 0.3, 0.6; `H` norm 2.3e-6 corrected against 5.4e-5 uncorrected at t = 0, both 2e-5 from t = 8 on, like the exact boosted slice | `core-20261115-121046-0c197fb` (A), `-121049-` (B), `-121047-` (C, stock generator), `-121052-` (D), `-121050-` (E); `core-20261115-115342-7a60df2` (C at 1/32, stopped at t = 10.5) |
| 2, two holes for 30 M, cells m/8 | symmetric to 4e-14; counter-clockwise by 0.53 rad; tracker speed 0.69 of `P/m` at the end and rising; coordinate separation 10 to 9.08; both horizons in all 120 searches, 0.5096 at t = 0, 0.5034 to 0.5166 in the first 2.5 M, 0.5156 at the end | `core-20261115-120835-d08c476` |
| 3, binary and a hole ten times heavier (mass 10 against 1), t = 0 | `H` norm of the code 2.25e-5 none, 8.5e-6 background factor, 1.50e-5 plain sum; closed form on the same cells 2.15e-5, 2.2e-6, 1.23e-5 (the rest is truncation at the light holes on cells of m/8) | processors `core-20261115-120210-212dce7`, `-120209-`, `-120211-` |
| 3, the same evolved 16 M | runs; three trackers; light horizons in all 64 searches (0.541 and 0.550 at t = 0, +1.3 and +1.5 percent at the end); heavy horizon not found (finder tolerance, fixed since); heavy tracker moves 4e-4 in 16 M; `H` norm 8.5e-6, peak 5.2e-3 at t = 2, 7.8e-5 at the end; momentum norm peak 5.6e-5 | `core-20261115-120834-d08c476` |
| Finder on the heavy spinning hole (m = 10, S = 30, cells m/10) | found from a first guess of radius m/2 for flow constants 1 to 100 (mass 10.348, `S_z` = 29.98); from the first guess of radius m used when other holes are far: rejected at step 0 with `hmean_tol = 100`, found in 31 steps with 1000 and flow constant 100 (mass 10.3483, `S_z` = 29.981) | processors `core-20261115-122312-8e699b1` to `-122316-`, `-122626-` to `-122630-`, `-122832-1cf6d89` |
| 3 with the final source, one cycle | three horizons at the first search: light holes 0.54097 and 0.54974 (the digits of the 16 M run), heavy hole 10.3996 with `S_z` = 29.98 | processors `core-20261115-131206-372e977` |
| Restart and particles with `puncture_setup` | tracker and horizon output identical in all printed digits after a restart; two tracers carried along | processors `core-20261115-120935-9211dcd`, `-121543-2e16f45` |
| Burst of radiation ("junk") | energy through a sphere at 14 m over 40 m, drift of the news removed: 1.4e-4 m (`P` = 0.3 corrected), 1.6e-4 m (uncorrected), 1.9e-3 m (`P` = 0.6), 7e-6 m (`S` = 0.3, `P` = 0.043); the stock boosted slice, which has no burst, gives 6e-5 m: the floor of this estimate. Above the floor: about 1.3e-2 (P/m)^4 m | runs A to E above |

Junk radiation of the three-black-hole data [JUDGEMENT, an estimate by adding the
single-hole numbers, not a measurement: 16 M are too short for the burst to reach an
extraction sphere]: light holes with `P/m` = 0.32 and 0.57, reduced by the background
factor (`P/(m Lambda^3)` = 0.25 and 0.46): 3e-5 and 3e-4; heavy hole (`P/m` = 0.04,
`S/m^2` = 0.3): below the floor, less than 6e-4; in all between 3e-4 and 1e-3 of the
binary's mass, below 1e-4 of the total mass. The bursts of the cross terms are not
in this estimate.

## 9. Limits and open items

1. No constraint solve. The Hamiltonian residual is what section 3 states; the cross
   terms between punctures are not corrected; a table exists only for one isolated
   puncture with momentum and spin along one axis. The elliptic solver on the mesh
   (decision 0010, item 4) replaces `approx` and `table` when it exists; the closed
   forms here are its first guess and its test case.
2. The background factor uses bare masses and distances at t = 0, treats the
   background as constant across the puncture, and ignores matter components.
3. Moving matter: no curvature for its momentum (section 3).
4. The tracker is not the hole during the first tens of M. Its speed starts at zero
   and has reached 0.61 of `P/M_ADM` after 40 m (one hole) and 0.69 of `P/m` after
   30 M (binary); the stock boosted-puncture generator behaves the same, at two
   resolutions, so this is the gauge. Trajectories read from trackers therefore carry
   a lag of a few M that grows during that time. Whether the 9 percent decrease of the
   binary's coordinate separation in 30 M is that lag or the orbit (Newtonian
   momenta at d = 10 M) is not established. [TO VERIFY: longer run, PN momenta]
5. Shift damping and unequal masses (section 4): with one `shift_eta` the tracker of
   the heavy hole stays behind. What a tracker that lags by a sizeable fraction of the
   horizon radius does to the refinement, the finder (centred on the tracker) and the
   evolution over a Hills passage is not tested. A damping that scales with the local
   mass is source work in the gauge of Z4c, outside this package. [TO VERIFY]
6. Resolution. Evolved tests ran at m/16 (one hole) and m/8 (two and three holes).
   After the first M the constraint norms are set by the punctures on the mesh, not by
   the initial data (the exact boosted slice reaches the same norm), and at m/8 the
   horizon masses scatter by one percent during the first 2.5 M and drift by half a
   percent afterwards. No convergence series of an evolved multi-hole run exists.
7. Junk radiation: measured for single holes only, to a factor of two, with a floor
   of 6e-5 m from the near field of a hole moving inside the extraction sphere; the
   number for three holes is an estimate.
8. The heavy horizon of the three-black-hole configuration was missed in the 16 M
   run (set-up tolerance, fixed) and is found at the first search with the final
   source; it has not been followed in time.
9. Apparent-horizon finder: stopping rule and absolute tolerance as described in
   sections 2 and 4; no common-horizon finder is set automatically.
10. Not run here: self-gravitating matter around a moving puncture; more than one
    MPI rank (the particle module is single rank anyway).
11. Things of AthenaK met on the way, unchanged: the mesh restart file carries
    uninitialised bytes in its header (two runs of different executables differ
    there); the docstring of `athenak/vis/python/bin_convert.py` gives the wrong layout
    for `mb_geometry` (it is x1min, x1max, x2min, x2max, x3min, x3max) and its header
    parser fails on a parameter value that contains `=`.
12. Provenance: the evolved card runs of section 8 used the executable built from
    7a60df2; the source changed afterwards only in the place of the reader call and a
    log line in `nrpic_cf.cpp` and in two defaults of `puncture_setup` (tracker radius
    0.999 of the stated one, `hmean_tol`). The final source is verified by the
    regression pair and static cases on processors (journal) and by the two short card
    runs at the end of section 8.

## 10. Lines touched in shared files

- `athenak/src/pgen/nrpic/nrpic_cf.cpp`: additions only, 25 lines: four comment lines
  at the end of the file header; `#include "pgen/nrpic/nrpic_bowen_york.hpp"` after the
  other includes; four lines after the component loop (reader call); three lines after
  the loop that sums `psi` (corrections); thirteen lines after the loop that sets
  `g_dd` and `vK_dd = 0` (curvature, added with `+=`).
- `athenak/src/main.cpp`: one include and two lines after
  `pinput->ModifyFromCmdline(argc, argv)`.
- New files: the two headers above; nothing added to `CMakeLists.txt`.
- `docs/FORMATS.md`: one new section, placed before "Radial table" because
  `core/id-extrinsic` inserts after that section and `core/newton` appends at the end.
- Trial merges (`git merge-tree`) of this branch with `main` (a1c2237),
  `core/id-extrinsic` (6fa6472), `core/newton` (ce329f5), `core/rng`, `core/nrpic`,
  `core/collisions` and `core/scalar-field`: no conflict.
  One thing must be changed by whoever merges `core/id-extrinsic`: its
  `CFSetExtrinsic` assigns
  `adm.vK_dd(...) = psi4*(...)` in a pass after the main loop, which would erase the
  Bowen-York curvature when a table of format 2 and a moving puncture are used
  together; with `+=` there (the main loop has set zero) both add.
