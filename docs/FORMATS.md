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
