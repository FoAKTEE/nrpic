# Outer faces of the spacetime solver (Z4c): what the stock conditions do, and the options of `core/z4c-faces`

Owner core. Branch `core/z4c-faces` (wave 3a). Evidence and every number:
`tracks/core/JOURNAL-faces.md` (predictions before, outcomes after, run ids); scripts,
plans, inputs and figures: `tracks/core/analysis/faces/`. Executables:
`/data/haiyangw/nrpic/scratch/core/exe/core_z4c-faces/` (READY there says what is tested).

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
| `sbc_damp_gam` | rate lambda (0) | adds -lambda (Gt^i - Gt^i_d) to d_t Gt^i in the boundary cells, Gt^i_d = -d_j gt^ij from centred second-order differences (det gt = 1): damping of the Gamma constraint where H5 makes it |
| `sbc_damp_theta` | rate lambda (0) | adds -lambda Theta to d_t Theta in the boundary cells |
| `sbc_speed` | `unit`, `lapse`, `metric` | speeds of R[f]: unit (stock; `sbc_v_khat` for Khat, default sqrt 2); lapse: alpha and sqrt(f alpha) for Khat with d_t alpha = -f alpha Khat, plus shift advection beta^k d_k f (arXiv:1212.2901); metric: the coordinate speeds alpha sqrt(chi/gt_ss), sqrt(f alpha chi/gt_ss), plus shift advection |

Source: `z4c/z4c_sbc_ext.hpp` (options), `z4c/z4c_bcs_falloff.cpp` (ghost fill, new
file), `z4c/z4c_Sbc.cpp` (`Z4cRadiativeOp`, `Z4cGammaFromMetric`, `Z4cBoundaryRHSNonwave`; new
functions, the stock `Z4cSommerfeld` path is untouched). Hooks in shared
files: `z4c/z4c_tasks.cpp` two lines (after `Z4cBCsCoarse` in `Z4c::Prolongate`, after
`Z4cBCs` in `Z4c::ApplyPhysicalBCs`), `z4c/z4c.hpp` one declaration, `z4c/z4c.cpp` one
comment, `CMakeLists.txt` one source file, `z4c/z4c_Sbc.cpp` the first line of
`Z4cBoundaryRHS` (`if (sbc.Extended()) return Z4cBoundaryRHSNonwave(...)`).
Not supported: `ghost_falloff` with `reflect` or `inflow` faces beside outflow faces is
applied after the stock fill and has not been tested; periodic faces are untouched.

## 4. Recommended settings

Filled in from the outcomes; see section 6.

## 5. What is not tested

Filled in at the end of the package.

## 6. Outcomes

Filled in from the journal.
