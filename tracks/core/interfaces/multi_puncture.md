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
`mass_tol_<n> = 1e-5 m`, `hmean_tol_<n> = 100`, `start_time_<n> = 0`,
`stop_time_<n> = 1e30`, and, if absent, `num_horizons`, `npunct`, `find_every = 16`,
`ntheta = 16`, `lmax = 8`, `metric_drvts = interpolant`. With adaptive refinement it sets
`<z4c_amr> method = tracker` and an `<amr_criterion_punc>` block with `method = user`
unless the input has its own. Rules:

- level of puncture `c` = `puncture_level - round(log2(m_c / m_lightest))`: cells
  proportional to the mass (a hole ten times heavier gets cells eight times larger);
- the finder flow constant is `m^2` because the flow step relative to the horizon
  radius scales as the constant over the mass squared [JUDGEMENT from the update rule
  in `fastflow.cpp`; consistent with the constants that worked in the first paper's
  runs, `notes/results_brief_selfgravity.md` part D item 3; test 3 below];
- values the input file gives itself in `<fastflow>` are kept (a common-horizon finder
  can be added by hand with an index beyond the punctures and a larger
  `num_horizons`); tracker parameters `co_<n>_*` in the input are an error;
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

## 5. Cost

(filled from the runs of section 8)

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

(filled from the runs)

## 9. Limits and open items

(filled at the end)

## 10. Lines touched in shared files

- `athenak/src/pgen/nrpic/nrpic_cf.cpp`: additions only, 25 lines: four comment lines
  at the end of the file header; `#include "pgen/nrpic/nrpic_bowen_york.hpp"` after the
  other includes; four lines after the component loop (reader call); three lines after
  the loop that sums `psi` (corrections); thirteen lines after the loop that sets
  `g_dd` and `vK_dd = 0` (curvature, added with `+=`).
- `athenak/src/main.cpp`: one include and two lines after
  `pinput->ModifyFromCmdline(argc, argv)`.
- New files: the two headers above; nothing added to `CMakeLists.txt`.
- Merge with `core/id-extrinsic` (state 1311b8e): textually clean (`git merge-tree`).
  One thing must be changed by whoever merges: its `CFSetExtrinsic` assigns
  `adm.vK_dd(...) = psi4*(...)` in a pass after the main loop, which would erase the
  Bowen-York curvature when a table of format 2 and a moving puncture are used
  together; with `+=` there (the main loop has set zero) both add.
