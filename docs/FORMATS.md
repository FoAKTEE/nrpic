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
