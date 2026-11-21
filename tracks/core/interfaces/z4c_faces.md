# Outer faces of the spacetime solver (Z4c): what the stock conditions do, and the options of `core/z4c-faces`

Owner core. Branch `core/z4c-faces` (waves 3a and 3, closed 2026-11-21; source commit
f6f9a0d, which contains release core-v0.5). Evidence and every number:
`tracks/core/JOURNAL-faces.md` (13 entries: predictions before, outcomes after, run ids);
scripts, plans, inputs and figures: `tracks/core/analysis/faces/`. Executables:
`/data/haiyangw/nrpic/scratch/core/exe/core_z4c-faces/` (READY there says what is tested).

In one paragraph: with `outflow` faces the stock code fills the ghost cells by linear
extrapolation and applies a Sommerfeld condition that assumes a 1/r fall-off. That
makes a constraint layer at the faces from the first step (it is what dominated the
whole-mesh Hamiltonian norm of core's initial-data tests), drives every field that is
stationary but not 1/r, and sends an error inward at the speed of light. Four options
remove most of it: `ghost_falloff = true`, `extrap_order = 4`, `sbc_variant = nonwave`,
`sbc_speed = metric` ("the full set"). Until the faces are felt, the residual of the
interior then equals that of a run with the faces twice as far away; the whole-mesh mean
|H| falls 3.5 times (expanding ball) to 34 times (vacuum puncture) at t = 8. Without the
options every output is byte-identical with release core-v0.5.

## 1. What the stock code does at an outflow face [VERIFIED from the source]

Every non-periodic input of `problems/` sets `outflow` on all six faces; none sets
`<z4c> extrap_order` or `user_Sbc`.

1. Ghost cells of all 22 Z4c variables (`bvals/physics/z4c_bcs.cpp`): Lagrange
   extrapolation along the face normal through `extrap_order` cells (default 2: linear),
   after every Runge-Kutta stage; x1 faces first over the whole (k, j) range, then x2,
   then x3, so edges and corners are extrapolated from extrapolated cells.
2. Right-hand side of the outermost active layer (`z4c/z4c_Sbc.cpp`, `Z4cBoundaryRHS`):
   for Theta, Khat, Gamma^i, A_ij replaced by the Sommerfeld operator
   `-v (s^k d_k f + f/r)`, s = x/r from the mesh origin, v = 1 (sqrt 2 for Khat),
   asymptotic value 0, fall-off 1/r, centred second-order derivatives (they read the
   first ghost). chi, gt_ij, alpha, beta^i keep their full right-hand side, computed
   with the extrapolated ghosts. No lapse in the speeds, no shift advection (the scheme
   of GR-Athena++, arXiv:2101.08289, without its N_g + 1 point extrapolation).
3. Every other active cell, and the constraint monitor, use centred sixth-order stencils
   that reach three ghost cells (advection and dissipation four).

## 2. What that does (tests a0, a0b, a1, b1, c0, c0b of the journal)

Set-ups (processors, cells of 1 at the faces, faces at 16, a reference with the faces at
32 on the same cells): expanding dust ball (M = 0.5, R_b = 6, Painleve-Gullstrand
exterior, K ~ r^-3/2); Brill-Lindquist puncture (m = 1, K_ij = 0); Bowen-York puncture
(P = 0.3, A_ij ~ r^-2). Five mechanisms, each shown by a run in which it could have failed:

| | Mechanism | Evidence (journal entry, run) | Size |
|---|---|---|---|
| H1 | the monitor (and every centred stencil) reads linearly extrapolated ghosts: error -1.117 f'' dx^2 in the boundary cell, +0.117, -0.011 in the next two | a0b (entry 3, core-20261119-143938-eded041): puncture after one step, boundary-cell \|H\| 1.9e-3 = 0.79 of the stencil estimate 8 x 1.117 m/r^3; orders 3, 4: 0.18, 0.048 of it (stencil 0.175, 0.041) | constant in time; the "faces dominate the whole-mesh residual" of the id-solver package's test F (vacuum puncture: face layer 1.78e-4, whole box 1.05e-4, reference 1.6e-9) |
| H2 | Sommerfeld assumes f ~ 1/r; a stationary f ~ r^-n is driven at v (n-1) f/r | a1 (entry 3): ball boundary cell departs at dKhat/dt = -1.11e-3 (predicted -1.12e-3); c0 (entry 7): boosted puncture boundary-cell M_x after one step 1.8e-5 = the kink of A/r per step | from the first step, wherever K_ij != 0 at the faces: the momentum-constraint layer of the clump package |
| H3 | the full right-hand side of the cells next to the boundary cell reads the bad ghosts; the error travels inward | a1 (entry 4, 8): vacuum puncture shell 8 <= r < 12 at t = 8 has 2.1e-5 (order 2), 6.3e-6 (order 4) against 2.05e-6 with the faces at 32 | 10 times the truncation level of the shell by t = 8 at order 2 |
| H4 | dissipation across the face | a1 (entry 3): without dissipation the ball's face layer changes by 1.6 per cent | not a cause |
| H5 | Sommerfeld for Gt^i while gt_ij keeps its full right-hand side: the Gamma constraint is made in the boundary cell | a1 (entry 8): face layer of \|Gt - Gt(gt)\| the same at orders 2 and 4 (2.5e-6 to 4.3e-5 for the puncture, 7e-4 to 5.8e-3 for the ball), 1e-10 to 2e-8 in the reference | grows with time; the largest of the four measures in the ball |

How fast and how far: along the x axis the difference to the reference moves inward at
1.50 (Khat, gauge speed sqrt 2) and 1.07 (H, light speed) in the ball, 1.00 (H) in the
puncture (a1, entries 7 and 8). The ball's shell residual is 3.8 times the reference's at
t = 8; the puncture's 10 times (order 2) and 3 times (order 4).

## 3. Options (block `<z4c>`; all absent means the stock conditions, byte for byte)

AthenaK accepts on the command line only parameters the input file has: put the options
you want to vary into the input (`tracks/core/analysis/faces/inputs/*_ext.athinput` carry
all of them at their stock values).

| Option | Values (default) | What it does |
|---|---|---|
| `ghost_falloff` | `false`, `true` | Ghost cells at outflow, diode and vacuum faces extrapolate G = (f - f_inf) r^q with the stock Lagrange weights (order `extrap_order`), f_ghost = f_inf + G/r_ghost^q. f_inf = 1 for chi, gt_xx, gt_yy, gt_zz, alpha; 0 for the rest. Exact for f_inf + c/r^q; for f ~ r^-m the leading ghost error is \|m - q\|/(m + 1) of the stock one. Also applied to the coarse array before prolongation at a physical face. |
| `ghost_power_metric` | (1) | q of chi, gt_ij, alpha, beta^i |
| `ghost_power_curv` | (1) | q of Khat, A_ij, Gamma^i, Theta |
| `extrap_order` | 2, 3, 4 (2) | stock option: number of cells of the extrapolation (capped at nghost) |
| `sbc_variant` | `sommerfeld`, `nonwave` | `nonwave`: radiative condition with a non-wave part (Alcubierre et al., arXiv:gr-qc/0206072): d_t f_b = R[f]_b + (d_t f - R[f])_p (r_p/r_b)^q, p one cell inward along every boundary direction; exact for a stationary f ~ r^-(q-1). For Khat, Gamma^i, A_ij. |
| `sbc_power_khat`, `sbc_power_a`, `sbc_power_gam` | (3) | q of the non-wave part (3: stationary r^-2, Bowen-York; 2.5: r^-3/2, Painleve-Gullstrand) |
| `sbc_theta` | `sommerfeld`, `nonwave`, `cpbc` | Theta: Sommerfeld; non-wave as above (`sbc_power_theta`, 3); `cpbc`: d_t Theta = -alpha s^k d_k Theta + beta^k d_k Theta, the Theta condition of the constraint-preserving set of arXiv:1212.2901 |
| `sbc_speed` | `unit`, `lapse`, `metric` | speeds of R[f]: unit (stock; `sbc_v_khat` for Khat, default sqrt 2); lapse: alpha and sqrt(f alpha) for Khat with d_t alpha = -f alpha Khat, plus shift advection beta^k d_k f (arXiv:1212.2901); metric: the coordinate speeds alpha sqrt(chi/gt_ss), sqrt(f alpha chi/gt_ss), plus shift advection |

Removed: `sbc_damp_gam` and `sbc_damp_theta` (damping of the Gamma constraint and of
Theta in the boundary cells; commit cb50e22). The first was unstable in the expanding
ball (non-finite fields at t = 15 with rate 4, growth from t = 14 with rate 1), the
second gained nothing there; a non-zero value of either stops the run at start with a
message (journal entry 11).

Source (difference to release core-v0.5: 8 files, 671 added lines, none removed):

| File | What | Lines of shared files |
|---|---|---|
| `z4c/z4c_sbc_ext.hpp` (new) | struct `SbcExt`: the options as data, `Extended()`; the documentation of the formulas | |
| `z4c/z4c_sbc_ext.cpp` (new) | `SbcExt::Read`: reads the options that are present | |
| `z4c/z4c_bcs_falloff.cpp` (new) | `Z4c::GhostFalloff`: the ghost fill | |
| `z4c/z4c_Sbc.cpp` | new functions `Z4cRadiativeOp`, `Z4c::Z4cBoundaryRHSNonwave` after the stock code, which is untouched | first two lines of `Z4c::Z4cBoundaryRHS` (`if (sbc.Extended()) return Z4cBoundaryRHSNonwave(...)`) |
| `z4c/z4c_tasks.cpp` | | one line after `Z4cBCsCoarse` in `Z4c::Prolongate`, one after `Z4cBCs` in `Z4c::ApplyPhysicalBCs` (`if (sbc.ghost_falloff) GhostFalloff(...)`) |
| `z4c/z4c.hpp` | | one include, one member (`SbcExt sbc;` after `Options opt;`), two method declarations |
| `z4c/z4c.cpp` | | one line (`sbc.Read(pin);` after `user_Sbc`) |
| `CMakeLists.txt` | | two source files after `z4c/z4c_Sbc.cpp` |

A warning to whoever edits these: `z4c_sbc_ext.hpp` must stay free of function bodies
beyond the one-line `Extended()`. With the option reader inline in it (commits 6cd9972
to ca6b46c), g++ 11.4 compiled the unchanged `z4c_calcrhs.cpp` with two more fused
multiply-adds, and every run differed from the release in the last bits also without
the options (journal entry 12; `analysis/faces/compare_objects.py` finds such a change
without a run).

Not supported: `ghost_falloff` with `reflect` or `inflow` faces beside outflow faces is
applied after the stock fill and has not been tested; periodic faces are untouched; a
`user` face gets the stock fill, and the extended right-hand side only with
`user_Sbc = true`, as in the stock code.

## 4. Recommended settings

    <z4c>
    extrap_order    = 4          # needs nghost >= 4
    ghost_falloff   = true
    sbc_variant     = nonwave
    sbc_speed       = metric     # second order; see below

- The three first lines carry the gain and belong together: the non-wave part on linear
  stock ghosts makes the momentum layer of a boosted puncture worse (c0b: 1.9 times),
  and order 4 on the stock Sommerfeld rate amplifies the kink it makes in the ball (a1).
- `sbc_speed = metric` helped the ball (face-layer difference to the reference 26 per
  cent lower at t = 8; mean |H| 1.5 times lower in the interior and 1.6 times in the
  shell at t = 16) and cost the vacuum puncture 3 per cent in the shell and 40 per
  cent in the face layer at t = 12; `lapse` is within 1 per cent of `metric` in the
  ball at t = 8 and 9 per cent lower in the shell at t = 16. Either is acceptable; all
  long tests ran with `metric`.
- Powers: the defaults (ghost fill 1, non-wave part 3) are what was tested for all three
  set-ups. `ghost_power_curv = 1.5` and `sbc_power_* = 2.5` (the exact values of a
  Painleve-Gullstrand exterior) changed the measures of the ball by 1 and 13 to 20 per
  cent; there is no reason to tune them.
- `sbc_theta`: leave it at `sommerfeld`. `cpbc` and `nonwave` were tested in the ball
  and gain nothing (face-layer mean |Theta| 3 to 21 and 17 to 39 per cent higher).
- The origin of the mesh must be the centre of the matter and of the far field: r in
  every formula is the distance from (0, 0, 0).
- The faces still reflect. With the full set the ball's interior residual at t = 16 is
  8 times below the stock run and 55 times above a run with the faces at 32: distance of
  the faces remains the cure for late times; these options are not an absorbing boundary.
- Track D (long vacuum puncture, cells M/8, faces at 128 M, 345 M on a card): the
  horizon-mass excursions that its README attributes to the outer region fall from
  1.08e-4 to 6.1e-5 (210 to 260 M) and from 1.52e-4 to 3.3e-5 (295 to 345 M) with the
  full set; the mass agrees with Track D's run to 9e-6 before 180 M.

## 5. What is tested and what is not

Tested (processors unless said; every number with its run id in the journal):

| Test | Set-up | Result |
|---|---|---|
| r2 | new executable without the options against release core-v0.5: ball, vacuum and boosted puncture, `horizon_calib`, `by_binary`, `kg_wave_smr`, periodic linear wave | 45 output files, all byte-identical |
| a0, a0b, c0, c0b | the monitor next to a face at t = 0 and after one step | the stock layer follows the stencil numbers; fall-off ghosts lower it 12 times at every order |
| c1, s1 | expanding ball, faces at 16, to t = 16 | table of section 6; stable with every option value |
| c2, c5 | vacuum and boosted puncture with static refinement, faces at 16, to t = 12, references with the faces at 32 to t = 8 | table of section 6 |
| t1b | refined region that touches an outflow face (coarse-array path of the ghost fill) | face layer 1.2e-3 of the stock one, no excess at the fine/coarse junction |
| c3 | vacuum puncture with horizon finder, faces at 16 M, to t = 40 | horizon mass equal to the stock run to 8e-9 before t = 11; later the two differ by up to 1.3e-3, both under-resolved: decides nothing |
| D (card, executable of 6cd9972) | Track D's `drift_dx8` to 345 M | section 4, last item |
| m1 | the delivered executable against the one of the tests above, with the full set | agreement to rounding (3e-11) |
| e1 | the example input `problems/tests/z4c_faces.athinput` against the package inputs with the same values on the command line | arrays and history numbers exactly equal |

Not tested:
- the card executable of the delivered source on a card (built only; the card runs D
  used the source of 6cd9972, before the merge of core-v0.5). A check is pending: run
  core-20261121-083511-2cff9df (Slurm job 4782; `analysis/faces/specs/k1.txt` judges it).
- byte identity of the card executable without the options (processors only).
- several MPI ranks; the threaded processor build; adaptive refinement at a face;
  restart of a run with the options (they are read from the input again; no state).
- matter at or near a face, two bodies whose far field is not centred on the origin, a
  mesh that is not a cube, faces closer than 16 M or farther than 128 M.
- the scalar field of `<scalar_field>` (its own outer faces are untouched).
- runs longer than t = 40 on processors and 345 M on a card.
- `sbc_theta = nonwave | cpbc` and `sbc_speed = lapse` outside the ball.

## 6. Outcomes

Mean |H| at t = 8 (and later where given); "reference": the same cells with the faces at
32. Figure `analysis/faces/figs/summary.png`.

| Set-up, region | t | stock | full set | reference |
|---|---|---|---|---|
| ball, r < 8 | 8 | 4.03e-3 | 3.54e-3 | 3.53e-3 |
| ball, r < 8 | 16 | 1.69e-2 | 2.12e-3 | 3.9e-5 |
| ball, 8 <= r < 12 | 8 | 2.80e-3 | 7.94e-4 | 7.35e-4 |
| ball, whole box | 8 | 3.73e-3 | 1.08e-3 | 6.36e-4 |
| ball, whole box | 16 | 7.07e-3 | 1.70e-3 | 4.10e-4 |
| vacuum puncture, 5 <= r < 8 | 8 | 2.13e-5 | 1.63e-5 | 1.63e-5 |
| vacuum puncture, 8 <= r < 12 | 8 | 2.09e-5 | 2.14e-6 | 2.05e-6 |
| vacuum puncture, whole box r >= 5 | 8 | 1.07e-4 | 3.11e-6 | 1.23e-6 |
| vacuum puncture, whole box r >= 5 | 12 | 1.14e-4 | 1.83e-5 | |
| boosted puncture, 5 <= r < 8 | 8 | 2.63e-5 | 2.23e-5 | 2.23e-5 |
| boosted puncture, 8 <= r < 12 | 8 | 5.02e-5 | 4.37e-6 | 3.35e-6 |
| boosted puncture, whole box r >= 5 | 8 | 1.48e-4 | 1.26e-5 | 1.84e-6 |
| boosted puncture, whole box r >= 5 | 12 | 1.77e-4 | 3.31e-5 | |

Other measures with the full set against stock: momentum constraint in the face layer of
the boosted puncture at t = 4: 3.39e-6 against 4.29e-5 (reference 3.2e-8); Gamma
constraint |Gt - Gt(gt)| in the face layer at t = 4: 2.17e-6 against 1.90e-5 (vacuum),
1.13e-5 against 1.91e-4 (boosted), 4.6e-4 against 5.8e-3 (ball).

Failed predictions and negative results on record (journal): the byte regression of the
second source version (entry 12: an inline function in a header changed the compiler's
code for another file; corrected); damping of the Gamma constraint in the boundary cells
(unstable in the ball, entry 11; removed); `sbc_theta = cpbc` and `nonwave`, damping of
Theta (no gain); metric against unit speeds in the vacuum puncture (c2-c, entry 13:
3 per cent worse, not 10 per cent better); the non-wave part on linear ghosts (c0b,
entry 8); the "junction zone" of the first t1 analysis (entry 13: it lay where no
junction is).

Requests of other packages that this answers: test F of the initial-data solver
(`JOURNAL-idsolve.md`: "the outflow faces dominate the Hamiltonian residual over the
whole mesh whatever the data"): that is the monitor reading linearly extrapolated ghost
cells of the static far field, 8 x 1.117 m/r^3 in the boundary cell, constant in time
and not falling with the cell size; `ghost_falloff` with `extrap_order = 4` lowers it
240 times (boundary cell 7.9e-6 against 1.9e-3 after one step). The layer of the
momentum constraint that the clump package saw where K_ij is not zero: at t = 0 the
same reading of linear ghosts (first order in the cell size), afterwards the Sommerfeld
rate v (n - 1) f / r on a stationary f ~ r^-n; the full set lowers it 13 times at t = 4
for a Bowen-York puncture.
