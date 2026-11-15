# File formats shared by the Python tools and the AthenaK problem generators

All binary data are little-endian. Units are geometrized, G = c = 1.

## Particle file (`*.nrp`)

| bytes | content |
|---|---|
| 8 | ASCII magic `NRPIC001` |
| 8 | int64 `N`, number of particles |
| 56 N | float64, N records of 7 values: `x y z u_x u_y u_z m` |
| 4 N | int32, species id of each particle (0 by default) |

`x y z` are the coordinates used by the run (Cartesian for mesh runs).
`u_x u_y u_z` are the covariant spatial components `u_i` of the four-velocity
(momentum per unit rest mass) in the same coordinates. `m` is the rest mass.

## Puncture correction table (`*.tab`, format `mp1`)

Regular correction `u_c` of the conformal factor of one Bowen-York puncture
(`<problem> comp<c>_corr = table`, `comp<c>_corr_file`), as multipoles about one axis
through the puncture:

    u_c(x) = sum_q u_{l_q}(r) P_{l_q}(mu),   r = |x - x_c|,   mu = (x - x_c).axis / r,

with `P_l` the Legendre polynomials. Plain text. Header lines begin with `#`; those of
the form `# key = value` are read:

| key | value | required |
|---|---|---|
| `l` | the multipole orders of the data columns, in order, each between 0 and 12, at most six | yes |
| `tail` | one exponent per column: beyond the last row the column continues as `u_l(r_N) (r_N/r)^tail` | no (default `l + 1`, the exterior harmonic) |
| `axis` | three numbers, the symmetry axis (normalised by the reader) | no |
| `format`, `mass`, `momentum`, `spin`, `nonlinear`, `m_adm`, `u_centre`, `columns` | written by the table writer for the reader of the file; ignored by the code (`nonlinear = 1`: full solution of the puncture equation, `0`: second order in momentum and spin) | no |

Each data row is `r  u_{l_1}  u_{l_2} ...` on a uniform grid `r_k = k dr`, `k = 0 .. N-1`,
starting at `r = 0`, with at least eight rows. Interpolation is four-point Lagrange
(cubic), as for the radial table. The axis is, in this order: `comp<c>_corr_axis1..3` of
the input, the `axis` of the header, the direction of the momentum, the direction of
the spin. The table is added to `psi` as it is (no rescaling); `psi` enters the lapse
options `isotropic` and `precollapsed`.

Writer: `python3 -m nrpic.bowen_york --mass m --momentum P --spin S [--lmax 8]
[--linear] [--background d] [--dr ..] [--rlast ..] --out file.tab` (momentum and spin
along the axis; even orders `l = 0, 2, .., lmax`; `dr = m/100` and `rlast = 200 m` by
default; `--background d` writes `Lambda u(m/Lambda, P/Lambda^4, S/Lambda^4)` with
`Lambda = 1 + d` for a puncture in the conformal factor of others,
`d = sum_j m_j/(2 d_j)`).

## Radial table (`*.tab`)

Plain text. Lines starting with `#` are comments. Each data row is

    r   u   alpha

on a uniform grid `r_k = k dr`, `k = 0 .. N-1`, starting at `r = 0`, with
`u(r) = psi(r) - 1` the conformal-factor excess of a spherically symmetric,
conformally flat, time-symmetric slice (`gamma_ij = psi^4 delta_ij`, `K_ij = 0`,
`r` the isotropic radius) and `alpha` the lapse. The table must extend beyond
the matter. Outside the table the generators continue with the vacuum form
`u = M/(2 r)`, where `M = 2 r_N u(r_N)` is taken from the last row, and, when the
tabulated lapse is used, `alpha = (1 - M/2r)/(1 + M/2r)`.
Interpolation inside the table is cubic, so `dr` should resolve the profile
(at least a few thousand points across the matter).

## Radial table with extrinsic curvature (`*.tab`, format 2)

Spherical initial data that are not time-symmetric (an expanding or contracting ball,
a black hole in a vacuum bubble). The interface text with the reasons is
`tracks/core/interfaces/spherical_id_format2.md` (proposal for
`coord/INTERFACES/spherical_id_format2.md`). Plain text; header lines begin with `#`
and must include

    # format = 2
    # columns = rbar u KL KT alpha betar
    # exterior = pg | zero

and may include `# breaks = r_1 r_2 ...` (at most four). Each data row is

    rbar   u   KL   KT   alpha   betar

on the uniform grid `rbar_k = k drbar`, `k = 0 .. N-1` (at least eight rows), with

- `u = psi - 1` as in format 1 (`gamma_ij = psi^4 delta_ij`, `psi = 1 +` the sum of
  the `u` of all components of the run);
- `KL`, `KT` the radial and the tangential eigenvalue of `K^i_j`, so that
  `K_ij = psi^4 [KT delta_ij + (KL - KT) n_i n_j]` with `n^i = (x - x_c)^i / rbar` and the
  full `psi`; trace `K = KL + 2 KT`, negative for expansion;
- `alpha` the lapse and `betar` the radial shift, `beta^i = betar n^i`.

A break is a radius, strictly between two rows, at which the columns may be
discontinuous (a sharp dust surface: `KL` jumps); the cubic interpolation takes its four
rows from one side of every break. Beyond the last row `u` continues as in format 1;
`exterior = pg` continues `KL`, `KT` as `rbar^(-3/2)` and `betar` as `rbar^(-1/2)`
through the last row and keeps the last `alpha` (exact for a Painleve-Gullstrand
exterior with `psi = 1`), `exterior = zero` sets `KL = KT = betar = 0`. Other header
lines `# key = value` are copied to the log of the run.

The problem generator `nrpic_cf` recognises the format by the header line; one
component of a run may be such a table. Start options: `<problem> lapse = table` takes
the `alpha` column of component `lapse_comp` (the other lapse choices are unchanged);
`<problem> shift = zero | table` (default `zero`) takes `betar` of component
`shift_comp`. The generator of a table answers for the constraints of the table with
its matter; dust at rest in the slice has `u_i = 0` in the particle file.

Python: `nrpic.io.write_tab2`, `read_tab2` and the class `Table2`, which evaluates a
table by the rule of the problem generator; `nrpic.expanding_ball` (class `Ball`: the
marginally bound expanding dust ball, sharp or with a smooth edge, and a bound ball that
turns around; exact radii against proper time; `residuals_1d`, the offline check of the
constraints of any table); command line `problems/ic/make_ball.py`, input
`problems/ball/ball.athinput`.

## Run outputs of the particle module

All binary files are written by one rank in native byte order. `<base>` is
`<job> basename`.

| File | Content |
|---|---|
| `<base>.nrpic.hst` | text, one record every `hist_dcycle` cycles: time, cycle, particle number, sum m, sum m W, sum m u_i (3), mesh integrals of E and S_i times sqrt(gamma) dV before the filter (4), lapse and energy density at the probe (average of the eight cells around `probe_x1..3`), proper time of the normal observer at the probe, minimum lapse on the mesh, number and rest mass of excised particles, number and rest mass of particles that left the mesh, maximum pusher iterations, number of unconverged pushes, number of MeshBlocks, and (since the 27-column version) the mesh integrals of E and S_i after the filter. Restarts append; keep the last record of each time. |
| `<base>.traj.bin` | float64 records of 8 (time, tag, x^i, u_i) for particles with tag < `traj_ntrack`, every `traj_dcycle` cycles |
| `<base>.trajmet.bin` | mesh-metric runs: float64 records of 12 (time, tag, alpha, beta^i, gamma_xx, xy, xz, yy, yz, zz) reconstructed at the same particles and times |
| `<base>.part.NNNNN.bin` | snapshot every `snap_dt`: 8 bytes `NRPSNAP1`, float64 time, int64 N, int64 cycle, N records of 7 float64 (x^i, u_i, m), N int32 tags, N int32 species |
| `<base>.curv.hst` | text, every `curv_dt`: time, maximum of the absolute Kretschmann scalar over cells with lapse above the excision value and its position, maximum energy density and its position, slice file number |
| `<base>.curv.NNNNN.bin` | `curv_slice = true`: 8 bytes `NRPCURV1`, float64 time, int64 number of records, records of 7 float64 (x, z, dx, I, E, alpha, sqrt(gamma)) for the cells cut by the plane y = `curv_plane_y` (the y of a record is the centre of the cell containing that plane) |
| `rst/<base>.NNNNN.rst.prt` | particle restart file next to each mesh restart file: 8 bytes `NRPRST02`, int64 N, 7 float64 of module state, 4 int64 of counters, N records of 7 float64, N records of 3 int32 (grid ID, tag, species) |

The Z4c history `<base>.z4c.user.hst` holds volume integrals of the squared constraint
residuals (divide by its Volume column and take the square root for a norm).

## Newtonian mode of the particle module (`<particles> pusher = newton`)

Interface and column table: `tracks/core/interfaces/newtonian_mode.md`; reader:
`python/nrpic/newton.py` (`read_newton_hst`, `NEWTON_COLUMNS`).

| File | Content |
|---|---|
| `<base>.newton.hst` | text, one record every `hist_dcycle` cycles, 50 columns: time, cycle, scale factor, rest mass, kinetic energy, potential energy (particle sum and mesh sum), the Layzer-Irvine constant and its integral, momentum, angular momentum, centre of mass, the second moment `sum m x_i x_j` and its first three time derivatives (6 components each; the third is a difference quotient over the last step and has its own time column), extrema of the potential, largest momentum and acceleration, defect norm and number of V cycles of the Poisson solve, the step |
| `<base>.nrpic.hst`, snapshots, trajectories | as in the relativistic mode, with these readings: the momentum slots hold `a dx/dt`; `sum_mW` and `int_E` are rest mass; the lapse columns (`alpha_probe`, `alpha_min`, `alpha_max`, probes) hold the potential `Phi` of `lap Phi = four_pi_G (rho - <rho>)`; the proper-time columns have no meaning |
| `rst/<base>.NNNNN.rst.prt.nwt` | state of the mode next to the particle restart file: 8 bytes `NRPNWT01`, 50 float64 (30 particle sums of the last synchronised state, time, scale factor, Layzer-Irvine integral, 6 third derivatives and their time, largest momentum, defect norm, 6 mesh sums, largest acceleration, number of V cycles), 5 int64 (extents of the potential array), the potential including ghost cells as float64 |

## Initial-data solver of the particle module (`<particles> id_solve = true`)

Interface: `tracks/core/interfaces/id_solver.md`; readers:
`tracks/core/analysis/idsolve/idlib.py` (`read_idsolve_txt`, `read_idsolve_bin`).

| File | Content |
|---|---|
| `<base>.idsolve.txt` | text, written during the solve at the start of a new run: a header with the options, one record per outer (Newton) iteration with 13 columns: iteration; largest residual over the largest sum of the absolute terms of the right side (the quantity compared with `id_tol`); largest and root-mean-square residual used by the iteration; largest and root-mean-square Hamiltonian constraint of the monitor of the code (`Z4c::ADMConstraints`) over the active cells; largest and root-mean-square residual with the seven-point Laplacian; smallest and largest psi; conjugate-gradient steps, V cycles and relative residual of the linear solve that followed (zero in the last record). Last line (comment): converged or not, totals, the monitor before and after. |
| `<base>.idsolve.bin` | `id_dump = true`: 8 bytes `NRIDSOL1`, 3 int64 (n1, n2, n3: cells of the uniform mesh), 6 float64 (x1min, x1max, x2min, x2max, x3min, x3max), int64 number of fields (7), then per field n3*n2*n1 float64, first index fastest: psi (solved), K, Abar_ij Abar_ij, E (source of the code for the solved psi), H of the constraint monitor at the last evaluation, the seven-point residual there, H of the monitor at the first evaluation (trial or psi = 1). At the faces of a mesh that is not periodic the monitor inside the solver sees the 1/r continuation of psi; the first field dump of the run (`<base>.field.00000.bin`) holds the monitor of the state as the evolution starts from it (outflow ghost cells). |
| `<base>.idsolve.txt` with `id_vector = true` | six more columns per record: 14 the largest residual of the vector equation over its scale (compared with `id_tol`), 15 and 16 its largest and root-mean-square value, 17 the largest \|M\| of the constraint monitor, 18 the norm of the mean removed from the residual (periodic mesh; 0 otherwise), 19 V cycles of the vector step that followed; one more summary line (`# vector equation: ...`) |
| `<base>.idvector.bin` | `id_vector = true` and `id_dump = true`: 8 bytes `NRIDVEC1`, the header of `<base>.idsolve.bin` (3 int64, 6 float64, int64 number of fields, 15), then 15 fields of n3*n2*n1 float64, first index fastest: W_x, W_y, W_z; the right side s_i of the vector equation (`8 pi psi^6 S_i + (2/3) psi^6 d_i K - d_j Abar_ij(trial)`, 3); its residual in stencil form (3); M_i of the constraint monitor at the last evaluation (3) and at the first (3). Reader: `tracks/core/analysis/idsolve/run_vector.py` (`read_idvector_bin`). |
