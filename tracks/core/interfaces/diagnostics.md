# Interface: outputs and diagnostics (proposal for `coord/INTERFACES/diagnostics.md`)

Status: PROPOSAL (core, 2026-11-15), written from the code at commit b7b431d
(`athenak/src/particles/nrpic_io.cpp`, `nrpic_curvature.cpp`, `z4c/fastflow.cpp`,
`outputs/history.cpp`) and checked against the files written by the processor
executable in test D1 of this package (run `core-20261115-112600-b7b431d`; readers in
`check/read_outputs.py`, written from this document). `<base>` is `<job> basename`.
All binary files: native byte order (little-endian on this machine), written by one
rank. Tests: `docs/TESTLOG.md` (DT), `cosmo/TESTLOG.md` (CT).

This document supersedes the "Run outputs of the particle module" table of
`docs/FORMATS.md`, which is out of date in four places (history now 32 + 3 nprobe
columns; `.trajmet.bin` 17 values; snapshots carry the proper time; restart format
`NRPRST05`).

## 0. Cadence options (`<particles>`)

| Option | Default | File |
|---|---|---|
| `hist_dcycle` | 1 | `.nrpic.hst` every this many cycles (0 off) |
| `cstat_dcycle` | 0 | `.cstat.hst` |
| `cons_dcycle` | 0 | `.cons.hst` (uniform mesh only) |
| `line_dcycle` | 0 | `.line.bin`, `.line.txt` (uniform mesh) |
| `traj_dcycle`, `traj_ntrack` | 0, 0 | `.traj.bin`, `.trajmet.bin` for particles with tag < `traj_ntrack` |
| `snap_dt` | -1 (off) | `.part.NNNNN.bin` every `snap_dt` in time |
| `curv_dt`, `curv_slice`, `curv_plane_y` | -1, false, 1e-6 | `.curv.hst`, `.curv.NNNNN.bin` |
| `field_time1` ... `field_time16`, `field_constraints` | none, false | `.field.NNNNN.bin` (uniform mesh) |
| `probe_x1..3`, `nprobe`, `probeN_x1..3` | origin, 0 | probe columns of the history (at most 8 extra probes) |

All records written during a run belong to the end of a step, t^n+1; a record of the
initial state (t = 0, cycle 0) is written at start-up for every enabled file except
`.cons.hst`. After a restart the text files are appended to without a new header (in a
new directory they have no header); a run that is restarted from an earlier dump
repeats the records after that dump, so readers keep the last record of each time.

## 1. `<base>.nrpic.hst` (text) [checked in D1]

Header lines start with `#`; the last one names the columns `[k]=name`.

| Col | Name | Meaning |
|---|---|---|
| 1 | time | t of the record |
| 2 | ncycle | cycles completed |
| 3 | np | particles held |
| 4 | sum_m | rest mass of particles with m > 0 (floating-point sum in the code's order; differs from the exact sum by up to N eps, 6.7e-14 in D1) |
| 5 | sum_mW | sum m W of the last deposit (0 without deposit) |
| 6-8 | sum_mux..z | sum m u_i |
| 9-12 | int_E, int_Sx..z | `sum_C (E, S_i) sqrt(gamma) dV` before the filter (equals columns 5-8 to round-off; `deposit.md` section 6) |
| 13 | alpha_probe | lapse at probe 0, trilinear interpolation of the eight surrounding cell centres |
| 14 | E_probe | deposited (filtered, with Lambda) E at probe 0, same interpolation |
| 15 | tau_probe | proper time `int alpha dt` at probe 0, third-order rule |
| 16 | alpha_min | smallest lapse on the active cells |
| 17-18 | n_excised, m_excised | cumulative number and rest mass removed by excision and as non-finite |
| 19-20 | n_escaped, m_escaped | cumulative number and rest mass that left the mesh |
| 21 | push_maxit | largest iteration count of the last push |
| 22 | push_unconverged | pushes that hit `max_iterations` in the last step |
| 23 | nmb | MeshBlocks |
| 24-27 | int_E_filtered, ... | as 9-12 after the filter (without Lambda) |
| 28 | proper_volume | `sum sqrt(gamma) dV` |
| 29 | mean_K | proper-volume mean of K = Khat + 2 Theta |
| 30 | alpha_max | largest lapse |
| 31-32 | E_max, E_min | extrema of E (with Lambda) |
| 33 + 3k, 34 + 3k, 35 + 3k | alpha_probeN, E_probeN, tau_probeN | probe N = k + 1 |

Tests: DT "Mesh path (CPU)", "Restart (CPU)"; CT "C0, first test" (probes, proper time,
volume, mean K against the exact homogeneous solution); D1 (38 columns, restart
records identical).

## 2. `<base>.cstat.hst` (text) [checked in D1, 16 columns]

Requires `<z4c>` and `deposit = true`. Extrema and cell means over the active cells
(every cell the same weight, whatever its level; meaningful on uniform meshes).

| Col | Name | Meaning |
|---|---|---|
| 1 | time | |
| 2-3 | chi_min, chi_max | conformal factor chi |
| 4-5 | K_min, K_max | K = Khat + 2 Theta |
| 6-7 | E_min, E_max | deposited E |
| 8 | Theta_max | largest abs(Theta) |
| 9-10 | H_max, H_mean | abs(H), `H = R + (2/3) K^2 - A_ij A^ij - 16 pi E` |
| 11-12 | Hr_max, Hr_mean | abs(H) over the root of the sum of squares of its four terms |
| 13-14 | M_max, M_mean | `abs(M) = sqrt(gamma^ij M_i M_j)`, `M_i = D_j A^j_i - (2/3) d_i K - 8 pi S_i` |
| 15-16 | Mr_max, Mr_mean | abs(M) over the root of the sum of the squared norms of its three terms |
| 17-18 | Z_max, Z_mean | norm of the connection constraint (Gamma - Gamma(metric))/2 |
| 19 | Theta_mean | mean abs(Theta) |

Columns 17-19 are in the source since commit 010aace (2026-11-14 08:23 PST) and in the
card executable, not in the processor executable `.work/build_cpu_c1` (test D1 wrote 16
columns). Tests: CT "C5, tests A0 and A of paper 2" (introduced), "Open item of T1:
relaxation of the Hamiltonian constraint, outcome; where the violation sits" (17-19).

## 3. `<base>.cons.hst` (text) [checked in D1]

Uniform mesh only. Residuals of the energy and momentum equations of the deposited
matter on the mesh, `d_t D + d_c(alpha sqrt(gamma) S^c) = alpha K_ab sqrt(gamma) S^ab -
sqrt(gamma) S^c d_c alpha` and its momentum analogue, written for zero shift (the record
is not meaningful with a shift), fourth-order differences, time derivative from three
successive steps; each residual divided by the root of the sum of squares of its terms.

| Col | Name |
|---|---|
| 1 | time of the middle step of the three |
| 2-3 | CEr_mean, CEr_max |
| 4-5 | CPr_mean, CPr_max |
| 6-7 | abs(CE)/D mean, abs(CP)/D mean |

The first record comes two steps after the start; after a restart, two steps after the
restart (the two earlier fields are not in the dump). Test: CT "T1: conservation on the
mesh, and the interpolation of the metric"; D1 (7 records, restart records identical).

## 4. `<base>.line.txt` and `<base>.line.bin` [checked in D1]

Uniform mesh. The `.txt` holds a comment line, n, and the n cell centres in x1. Each
`.bin` record has 1 + 5 n float64: time, then n values each of chi, alpha, K, E, S_x
(grouped by field, increasing x1) along the line of the first cells in x2 and x3.
Test: CT "C5, test B of paper 2"; D1.

## 5. `<base>.field.NNNNN.bin` [checked in D1]

Uniform mesh. Written at start-up (`00000`) and at the step nearest each `field_timeK`
(file number K).

| bytes | content |
|---|---|
| 8 | `NRFIELD1` or, with `field_constraints = true`, `NRFIELD2` |
| 8 | float64 time |
| 24 | 3 int64 n1, n2, n3 |
| 4 n | float32 E (first index fastest), n = n1 n2 n3 |
| 4 n | float32 chi |
| 56 n | `NRFIELD2` only: 7 float64 arrays H, M_x, M_y, M_z, Khat, Theta, alpha |

Tests: CT "C5/T1: damping rate, outcome; the constraint field goes into the dumps",
"C5/T1: the constraint field, ..."; D1.

## 6. `<base>.traj.bin` and `<base>.trajmet.bin` [checked in D1]

Every `traj_dcycle` cycles, for every particle with tag < `traj_ntrack`, in array order.
`.traj.bin`: records of 8 float64 (time, tag, x, y, z, u_x, u_y, u_z).
`.trajmet.bin` (only with `metric = mesh`): records of 17 float64 (time, tag, alpha,
beta^x, beta^y, beta^z, gamma_xx, gamma_xy, gamma_xz, gamma_yy, gamma_yz, gamma_zz,
proper time of the particle, E, S_x, S_y, S_z), the metric reconstructed at the particle
at t^n+1 and the deposited sources gathered with cloud-in-cell weights at the
particle's level; same order as `.traj.bin`.
Tests: DT "Test particles around an evolved puncture"; CT "C3: luminosity distance
along light rays, outcome"; D1.

## 7. `<base>.part.NNNNN.bin` (snapshots) [checked in D1]

| bytes | content |
|---|---|
| 8 | `NRPSNAP1` |
| 8 | float64 time |
| 8 | int64 N |
| 8 | int64 cycle: the counter before the step that produced the state, i.e. column 2 of the history minus one (3 at t = 0.25 in D1, where the history has 4); 0 at start-up |
| 56 N | N records of 7 float64: x, y, z, u_x, u_y, u_z, m |
| 4 N | int32 tags |
| 4 N | int32 species |
| 8 N | float64 proper time of each particle (affine parameter for null particles; not advanced by the Boris pusher) |

Written at start-up and when the time first reaches the next multiple of `snap_dt`.

## 8. `<base>.curv.hst` and `<base>.curv.NNNNN.bin` [checked in D1]

Kretschmann scalar `I = R_abcd R^abcd` from the 3+1 variables and the sources (Gauss,
Codazzi and Ricci equations, `nrpic_curvature.cpp` lines 7-17), on the active cells,
every `curv_dt`.
`.curv.hst` columns: 1 time; 2 max abs(I) over cells with lapse at or above `alpha_exc`
(all cells if `alpha_exc <= 0`); 3-5 its cell centre; 6 max E; 7-9 its cell centre;
10 slice file number. The header names columns 6 and 10 "max E" and "file number" with
a blank inside, so a reader that splits the header on blanks must not count names.
`.curv.NNNNN.bin` (`curv_slice = true`): `NRPCURV1`, float64 time, int64 nrec, nrec
records of 7 float64 (x, z, dx, I, E, alpha, sqrt(gamma)) for the cells cut by the
plane y = `curv_plane_y` (on refined meshes cells of several sizes).
Tests: DT "Kretschmann scalar (CPU)" (48 M^2/R^6, 1e-5 at 4 < r < 6 with sixth-order
differences); D1 (mean of I on the slice about 3.6 against 15 H^4 = 3.65 for dust).

## 9. Restart files

`rst/<base>.NNNNN.rst` (AthenaK) and next to it `rst/<base>.NNNNN.rst.prt` (particle
module), written by an `<outputN> file_type = rst` block, including at t = 0. Layout of
the particle file, format `NRPRST05` (formats 02 to 04 are still read):

| bytes | content |
|---|---|
| 8 | `NRPRST05` |
| 8 | int64 N |
| 56 | 7 float64: tau_probe, alpha_probe, e_probe, mass_excised, mass_escaped, next snapshot time, next curvature time |
| 32 | 4 int64: n_excised, n_escaped, snapshot number, curvature number |
| 56 N | N records of 7 float64 (x^i, u_i, m) |
| 12 N | N records of 3 int32 (MeshBlock id, tag, species) |
| 8 N | float64 proper times |
| 192 | 24 float64: (tau, alpha, E) of probes 1-8 |
| 72 | 9 float64: lapse one step earlier at the probes (third-order proper time) |
| 8 | float64 previous step (-1 at start-up) |
| 8 | int64 1 if the source densities follow, else 0 |
| 40 + 8 P | if 1: 5 int64 dims and P = product of dims float64, the densities handed to the spacetime solver for the coming step (`source_density` and `source_extrap`) |

Restarts are exact: DT "Restart (CPU)"; CT "Restart of periodic runs" and "Step
limited by the expansion rate"; D1 (history, statistics, snapshot, curvature slice,
trajectories bitwise equal after a restart at t = 0.25).

## 10. Outputs of AthenaK used with the module

- `<base>.z4c.user.hst` (an `<outputN> file_type = hst` block): time, dt, then volume
  integrals over cells with `chi >= <z4c> excise_chi` (default 0.0625) of C^2, H^2,
  M^2, Z^2, M_x^2, M_y^2, M_z^2, Theta^2, weighted with the proper volume
  `sqrt(gamma) dV`, and that volume (`outputs/history.cpp` lines 171-240). A norm is
  the square root of an integral over the volume column. The paper's norm is a
  coordinate-volume root mean square (main.tex L1497-1508).
- Apparent horizons (`<fastflow>`; `num_horizons`, `find_every`, `flow_iterations_N`,
  `flow_alpha_beta_const_N`, `mass_tol_N`, `initial_radius_N`, `center_x_N`, ...,
  `start_time_N`, `metric_drvts`): `<base>.horizon_summary_N.txt` with columns
  1 iter, 2 time (printed with `%g`, six significant digits), 3 mass (Christodoulou,
  `sqrt(M_irr^2 + S^2/(4 M_irr^2))`, `M_irr = sqrt(A/16 pi)`), 4-6 S_x, S_y, S_z,
  7 S, 8 area, 9 hrms, 10 hmean, 11 meanradius, 12 minradius (`z4c/fastflow.cpp` lines
  208-262, 379-386, 761, 821); and `<base>.horizon_shape_N.txt`. Use
  `metric_drvts = interpolant`: the default `stored` interpolates a derivative array
  whose ghost cells are not filled and reads masses two to six percent low (DT "Horizon
  mass calibration: results"; `notes/claims_brief.md` lines 67-71). The flow constant
  must scale with the expected mass (DT "Finder test: the flow overshoots on its first
  step").
- Psi_4 extraction (`<z4c> nrad_wave_extraction`, `extraction_radius_N`,
  `waveform_dt`): AthenaK's own format, not changed by this repository.

## 11. Proposed interface rules (JUDGEMENT)

1. Analyses read files only through readers that follow this document
   (`check/read_outputs.py` is one); a change of a layout changes its magic or adds
   columns at the end, and is announced as an interface change.
2. The constraint norm that tracks quote is named with its weighting: "proper-volume
   L2 over chi >= 0.0625" (`.z4c.user.hst`), "cell mean of abs(H)" (`.cstat.hst`), or
   the paper's coordinate-volume RMS.
3. `docs/FORMATS.md` is brought in line with sections 1, 6, 7 and 9 (request to the
   owner of `docs/`).
