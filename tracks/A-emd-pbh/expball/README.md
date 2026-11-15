# expball: initial data and exact solution of the expanding dust ball (A-pre-1)

Work package A-pre-1 of Track A (helper of A-emd-pbh, 2026-11-15). Reference solutions,
generator and offline checks only; nothing here is a simulation code (decision 0010). The
evolution is AthenaK's; the format-2 reader in the problem generator is core's
(`core/id-extrinsic`, not written yet).

## What is here

| path | content |
|---|---|
| `DERIVATION.md` | independent re-derivation: spacetime, slice, K_ij (KL = -dv/dR with E(R)), constraints, conformally flat form and the Cartesian format-2 assembly, anti-trapped criterion, growing-mode data with a bound core, exact shell evolution, G1 numbers, the two relations of the brief (S1 lines 355-356) and every agreement/disagreement with `coord/notes/derivations_to_check.md` item 1 |
| `sym/` | sympy/mpmath checks used by DERIVATION.md: `sym_ltb_4d.py` (27 checks), `sym_slice.py` (36), `sym_growing.py` (11), helper `geom.py` |
| `expball/model.py` | initial slice: profiles `Flat`, `TopHat`, `SmoothTopHat`, `Smooth`, edge taper; m, E, v, KL, KT, rho, psi, betar, rest mass; piecewise-Chebyshev interpolants (error ~1e-14) |
| `expball/exact.py` | exact solution: R(tau) of every shell, dR/dtau, turnaround, crunch and apparent-horizon (R = 2m) proper times, first trapped sphere, shell-crossing check |
| `expball/table.py` | table format 2 writer/reader (`coord/INTERFACES/spherical_id_format2.md`), evaluation with the four-point Lagrange rule of `nrpic_cf.cpp` and the `pg` continuation |
| `expball/particles.py` | samples at rest (u_i = 0): stratified, mc, mass-weighted lattice (surface layer corrected); particle writer of `python/nrpic/io.py` and stratified uniforms of `python/nrpic/sampling.py`, imported by path |
| `expball/mesh.py` | 3+1 fields on a Cartesian mesh (`.npz`), finite-difference Hamiltonian and momentum residuals (conformally flat form; general-metric cross-check), CIC deposit |
| `expball/runlog.py` | run manifests (`tracks/A-emd-pbh/runs/<id>/manifest.json`, copy in `manifests/`) |
| `scripts/make_dataset.py` | writes and registers one data set (table, particles, mesh, shell table, JSON) |
| `scripts/check_dataset.py` | end-to-end check of a written data set from its files |
| `scripts/run_convergence.py` | G1 test: residual norms and orders against N, table interpolation error |
| `scripts/run_noise.py` | Hamiltonian-residual noise of CIC-deposited particles against N and sampler |
| `scripts/fig_slice_exact.py` | figures of the initial slice and of the exact shells |
| `tests/test_expball.py` | 32 unit tests (`python3 -m pytest -q tests/`, 10 s) |
| `figures/` | figures of the registered runs (PNG and PDF), listed below |
| `manifests/` | copies of the run manifests (the repository's ignore pattern `runs/` also hides `tracks/A-emd-pbh/runs/`; see Requests) |
| `JOURNAL.md` | predictions before each test and outcomes, including failed predictions and a solver defect found and fixed |

## How to rerun (from this directory; numpy, scipy, sympy, matplotlib of the system Python)

    export OMP_NUM_THREADS=4 OPENBLAS_NUM_THREADS=4
    python3 sym/sym_ltb_4d.py && python3 sym/sym_slice.py && python3 sym/sym_growing.py
    python3 -m pytest -q tests/
    python3 scripts/make_dataset.py --model flat --HRb 0.5
    python3 scripts/make_dataset.py --model smooth_tophat --HRb 0.5 --delta-c 1.0 --R1 0.3 --R2 0.75
    python3 scripts/check_dataset.py /data/haiyangw/nrpic/scratch/A-emd-pbh/<run_id>
    python3 scripts/run_convergence.py                 # about 4 min, 4 cores
    python3 scripts/run_noise.py                       # about 2.5 min
    python3 scripts/fig_slice_exact.py

Every script registers itself as a run (scratch output under
`/data/haiyangw/nrpic/scratch/A-emd-pbh/<run_id>/`). Other options: `--model tophat`,
`--edge-width 0.1` (C^4 taper of the edge, in units of R_b), `--N`, `--nlat`, `--mesh-N`,
`--table-points` (rows across the matter, default 4000).

## The two data sets (units G = c = 1, M = Misner-Sharp = ADM mass of the ball = 1)

Common envelope: Einstein-de Sitter ball with H R_b = 0.5 on the slice, R_b = 8, H = 1/16,
age t_i = 2/(3H) = 10.667, Hubble radius 16, max 2m/R = 0.25 at R_b (no anti-trapped
sphere), vacuum outside (outgoing Painleve-Gullstrand slice of Schwarzschild, M = 1).
Lapse 1 and the shift of the dust's proper-time slicing are in the table; the code's gauge
differs, so compare through invariants (below).

**Data set 1, marginally bound homogeneous ball** — run `A-emd-pbh-20261115-121749-90764e1`,
`/data/haiyangw/nrpic/scratch/A-emd-pbh/A-emd-pbh-20261115-121749-90764e1/`:
`expball_flat_HRb0p5.tab` (format 2, 6001 rows, drbar = 0.002, to rbar = 12),
`..._strat_N100000_s1.nrp`, `..._lat58.nrp` (102208 particles), `..._mesh64.npz`
(64^3 over [-10, 10]^3), `..._shells.txt`, `.json`. psi = 1, K_ij = -H delta_ij inside,
rest mass = 1. No shell ever turns around; every shell follows
R(tau) = R_i (1 + 3 H tau/2)^(2/3) = R_i (1 + 3 tau/32)^(2/3); the edge is at R = 12.43,
25.49, 38.06 at tau = 10, 50, 100.

**Data set 2, bound core inside the Einstein-de Sitter ball** — run
`A-emd-pbh-20261115-121753-90764e1`, same file layout with stem
`expball_smooth_tophat_HRb0p5_dc1_R10p3_R20p75`. Smoothed top-hat (simultaneous bang time,
pure growing mode): mean contrast Delta = 1 inside R1 = 0.3 R_b = 2.4 (homogeneous closed
core), C-infinity step to Delta = 0 at R2 = 0.75 R_b = 6 (compensated; Einstein-de Sitter
from 6 to 8); local density 2 rho_b in the core, minimum 0.437 rho_b in the compensating
shell; psi(0) = 1.01384; rest mass 1.00631. Predicted proper times of the dust, measured
from the initial slice (`expball/exact.py`; run `-121753-90764e1`, and figures run
`A-emd-pbh-20261115-121643-6bfb707`):

| event | proper time tau | in units of t_i |
|---|---|---|
| turnaround of every core shell (R_i <= 2.4), at R_max = m/(-E) = R_i/y = 1.340 R_i (y = 0.74638) | 16.894 | 1.584 |
| first trapped sphere (R = 2m) of the run: shell R_i = 2.74 (grid of 400 shells, spacing 0.02), m = 0.0804 | 44.349 | 4.158 |
| core edge R_i = 2.4 trapped, m = 0.054 | 44.381 | 4.161 |
| crunch of the homogeneous core (R = 0 for all R_i <= 2.4) | 44.454 | 4.168 |
| no shell crossing before the crunch | — | — |

Shells outside the core turn around and collapse later (tau_ta and tau_c against R_i in
`*_shells.txt` and `figures/fig_exact_shells.png`); the envelope beyond R2 never turns
around. At the core crunch the ball edge is at R = 8 (1 + 3 x 44.454/32)^(2/3) = 23.9.

How to compare with AthenaK (G2 of the track sheet): the proper time of a particle along
its world line against the areal radius of its shell (sqrt(A/4pi) of the sphere through
the particles of one shell, or the Misner-Sharp radius); the Misner-Sharp mass inside a
shell, constant in time; the proper time of the shell's particles when the horizon finder
first reports an apparent horizon at that shell, against tau_AH(R_i).

## G1 result: constraint residuals converge at the expected order

Run `A-emd-pbh-20261115-121654-6bfb707`, repeated with corrected figure layouts as
`A-emd-pbh-20261115-122121-aa1c84d` (same numbers; its figures are those in `figures/`:
`fig_constraint_convergence.png`, `fig_residual_maps_N128.png`,
`fig_table_interpolation.png`), and `A-emd-pbh-20261115-122117-aa1c84d` (smoothed top-hat,
N = 128, 256, 512; `fig_constraint_convergence_smooth_tophat_N512.png`). Octant meshes
N = 32 ... 256, L2 norms divided by 6H^2, region farther than 0.1 R_b from every non-smooth
radius, orders of the last two pairs:

| model | order 2 (H, M) | order 4 (H, M) |
|---|---|---|
| flat ball | H = 0 (round-off); M 2.00, 2.00 | H round-off; M 4.00, 4.00 |
| flat ball, C^4 edge taper (all cells) | M 1.96, 1.99 | M 3.77, 3.90 |
| compensated top-hat | 2.00, 2.00 / 2.00, 2.00 | 4.01, 4.00 / 4.01, 4.00 |
| smoothed top-hat (data set 2) | 1.98, 2.00 / 1.92, 1.98 | 3.75, 3.92 / 3.43, 3.79; with N = 512: H 3.98, M 3.94 (p = 4), 2.00, 1.99 (p = 2) |

Over all cells, a density jump (ball edge; top-hat edges) leaves an O(1/h) momentum
residual in a one-cell band (L1 does not converge, L2 grows as h^-1/2) and, for the
top-hat, a first-order Hamiltonian band: properties of sampling discontinuous K_ij on a
mesh, removed by the edge taper. The format-2 table (spacing rbar_m/4000) reproduces the
exact-field residuals to 6e-7 relative (N = 128), and its interpolation error converges
at order 4 down to round-off. End-to-end checks of the written files: runs
`A-emd-pbh-20261115-121859-ac2eb52` (set 1) and `-121905-ac2eb52` (set 2).

Particle noise (run `A-emd-pbh-20261115-121659-6bfb707`, repeated as
`A-emd-pbh-20261115-122325-aa1c84d` with the same numbers and the figures in `figures/`:
`fig_particle_noise.png`, `fig_particle_noise_maps_N1e5.png`; fitted slopes -0.500 (mc),
-0.4995 (stratified), -0.67 (lattice, flat ball)): CIC on 64^3 cells over [-10, 10]^3, rms of
dH/6H^2 = (rho - rho_dep)/rho_b inside 0.8 rbar_m. Independent (mc) and stratified samples
follow the CIC Poisson value sqrt((2/3)^3/n_c) within 2 percent: 1.44, 0.83, 0.455, 0.264,
0.144 at N = 1e4, 3e4, 1e5, 3e5, 1e6 (n_c particles per cell; slope -1/2); the stratification
(in mass fraction, cos theta, phi) does not reduce the per-cell noise. The lattice gives
1.04, 0.236, 0.050, 0.082, 0.040: not monotonic (lattice/mesh beat), 3 to 9 times below
the random samples at N >= 1e5. Means are zero within 1e-2.

## Figures (each inspected)

- `fig_initial_slice`: rho/rho_b, Delta, KL/H and KT/H, psi - 1, 2m/R, 1 + 2E against R for the
  flat ball, the top-hat and the smoothed top-hat.
- `fig_exact_shells`: world lines R(tau) of shells, turnaround points, the R = 2m events,
  a zoom on the crunch of the core, tau_AH - tau_c(core) against the shell label.
- `fig_constraint_convergence`, `fig_residual_maps_N128`, `fig_table_interpolation`: G1.
- `fig_constraint_convergence_smooth_tophat_N512`: one more resolution for data set 2 (its
  x axis extends to 0.04 without data; the tick choice is fixed in the script).
- `fig_particle_noise`, `fig_particle_noise_maps_N1e5`: noise against N; maps in z = 0.

## Not done / limits

- Nothing has been run in AthenaK (the format-2 reader does not exist yet); the t = 0
  constraint norms of the code for these data are therefore not known.
- The four-point Lagrange evaluation of the table is assumed (as for format 1); if core
  chooses another rule the table check must be repeated.
- The lattice-noise prediction failed (JOURNAL P6) and the cause (lattice/mesh beat) was
  not tested.
- Non-spherical (Zel'dovich, triaxial) perturbations are out of scope (wave 2).
- The "no non-round anti-trapped surface" step of section 4 is quoted, not derived.

## Requests

- **core** (`core/id-extrinsic`): (1) evaluate format-2 tables with the same four-point
  Lagrange rule as `CFCubic` (or tell us the rule; `expball/table.py::lagrange4` mirrors
  `CFCubic`); (2) with the reader in place, report the Z4c constraint norms at t = 0 for
  data sets 1 and 2 at two resolutions, so that they can be compared with this package's
  offline numbers (expected: the momentum band at the ball edge, see G1); (3) the ball
  edge is a jump of KL (from -H to +H/2): if the deposit filter smooths the density but
  K_ij stays sharp, expect a constraint transient there; `--edge-width` makes a C^4 taper
  that removes it, if wanted.
- **orch**: the ignore pattern `runs/` in `.gitignore` also matches `tracks/<ID>/runs/`, so
  run manifests cannot be committed there without `-f`; proposal: `/runs/`. Meanwhile the
  manifests are mirrored in `expball/manifests/` (tracked).
- **orch/core**: decision 0010 places initial-data tools in `problems/ic/` and
  `python/nrpic/`; when this generator is accepted it could move there (owned by core).
- **lead of A-emd-pbh**: choose sharp edge or taper for the first G2 runs; data set 2
  needs the evolution to tau ~ 45 (about 4.2 t_i) with the outer edge growing to R ~ 24.
