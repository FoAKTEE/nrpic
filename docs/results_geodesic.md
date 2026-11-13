# Single-test-particle geodesic campaign (NRPIC in AthenaK)

Reproduction of Sec. "Kerr geodesics" of arXiv:2611.12831 (`refs/arxiv_2611.12831/src/main.tex`,
lines 767-855) with the AthenaK particle module, extended to Schwarzschild orbits and to the
metric stored on the AthenaK mesh. All numbers below are as measured on 2026-11-13. Every value
in the tables is regenerated from the files in `problems/kerr/results/` and
`problems/schwarzschild/results/` by `analysis/geodesic/make_tables.py`.

## Setup

**Executables.** GPU: `.work/build_gpu_dev/src/athena` (Kokkos/CUDA, A100, `Release`,
md5 `951bd5b5...`; the checksum was logged before every run and never changed). CPU (part D only):
`.work/build_check/src/athena` (serial, `RelWithDebInfo`, md5 `24e95112...`), run directly on the
login node. Both executables were built from the same `nrpic_kernels.hpp`, `nrpic_metrics.hpp` and
`nrpic_mesh.hpp` (all three are older than both binaries); `nrpic.cpp`, `nrpic_io.cpp` and
`particles.hpp` were edited by the lead after the CPU build (see anomaly 9).

**How the GPU runs were launched.** Every run is defined in `analysis/geodesic/run_campaign.py`
(name, input file, overrides). The command of each run is the project helper,

```
ATHENA_EXE=/data/haiyangw/nrpic/.work/build_gpu_dev/src/athena TIME=00:20:00 JOB_NAME=geo \
  scripts/gpu_run.sh runs/geodesic/<name> <athinput> <overrides...>
```

written verbatim to `runs/geodesic/<name>/cmd.sh` (with `run.json`). Because the two GPUs were
shared with long jobs and every new allocation waited in the queue, the runs were executed in
batches: `run_campaign.py batch <patterns>` takes ONE allocation
(`srun -p preempt --gres=gpu:1 -c 1 -t 00:58:00 -J geo runs/geodesic/batches/batch.<ts>.sh`)
and the batch script calls `scripts/gpu_run.sh` with the same command lines one after the other
(inside an allocation that sees a GPU the helper runs athena directly; this is its documented
behaviour). The batch scripts and their logs are in `runs/geodesic/batches/`.
CPU runs: `.work/build_check/src/athena -i <athinput> -d runs/geodesic/<name> <overrides>`.

**Overrides common to all runs.** `particles/tolerance=2.0e-14 particles/max_iterations=200
particles/hist_dcycle=1 particles/traj_dcycle=1 particles/traj_ntrack=1 time/ndiag=20000`, plus
`particles/dt=<dt> time/tlim=<t_end>` and the initial state
`particles/p0_x{1,2,3}=... particles/p0_u{1,2,3}=... particles/p0_m=0.0` (17 significant digits).
Pusher: `particles/pusher=midpoint` (mid) or `particles/pusher=boris particles/triad=symmetric`
(bsym) / `particles/triad=cholesky` (bchol). Metric: `particles/metric=kerr_schild_sph` (ks),
`kerr_schild` (cks), `boyer_lindquist` (bl), `lattice` with `particles/lattice_dx=<dx>` (lat),
`mesh` (mesh). `hist_dcycle=1` makes the history record the non-convergence count and the
iteration count of every step. The full override list of every run is stored in the result
JSON files (`runs.<name>.overrides`).

**Error measures.** Invariants E, L_z, Q are evaluated with the exact metric of the run's
coordinate system (`nrpic.kerr.invariants`) at every recorded step and compared with their values
at t = 0 (relative errors; absolute for Q of equatorial orbits, where Q = 0). Position error:
max(|dr|/M, |dtheta|, |dphi|) against the exact state, phi unwrapped to the exact value,
Cartesian positions converted to (r, theta, phi_KS) first. Exact states: Mino-time quadrature
(`kerr.MinoOrbit`, 30 digits) for bound orbits, closed form for the circular orbit, quadrature in
r for the plunge; reference trajectories between exact checkpoints: DOP853, rtol = atol = 2.5e-14.
Convergence orders are least-squares slopes of log(error) against log(dt) or log(dx) over all
step sizes, with the pairwise orders listed as well.

**Figures** (style `python/nrpic/figstyle.py`; mapping in `analysis/geodesic/geo_style.py`).
Colour = method: blue reference (exact solution, published value), red implicit midpoint,
yellow Boris (DGREM) with symmetric triad, green Boris with Cholesky triad, orange CPU
executable. Line style = metric input: solid analytic metric in spherical coordinates (KS or
BL), dashed analytic Cartesian Kerr-Schild, dotted Cartesian Kerr-Schild reconstructed with the
cubic Hermite interpolation (virtual lattice or AthenaK mesh). Several dt or dx of one method:
shades of the method colour (light = large step). Black dashed: power-law guides. Grey:
pericentre time, horizon radius.


## Summary

**C. Kerr-Schild e = 0.99 passage, headline** (exact pericentre r_p = 1.8983272737 M at
t_p = 98.94834714 M; the GPU numbers equal the standalone-build numbers given with the task in
all four printed digits):

| combination (dt = 0.01 M, t = 230 M) | max dE/E | max dL_z/L_z | max dQ/Q | paper (E / L_z / Q) | final-position error | r_p / M | t_p / M |
|---|---|---|---|---|---|---|---|
| midpoint, analytic spherical KS | 2.781e-08 | 0 | 1.254e-07 | 2.8e-8 / round-off / 1.3e-7 | 4.49e-04 | 1.898325 | 98.949 |
| Boris (symmetric triad), analytic spherical KS | 9.046e-08 | 1.136e-08 | 7.825e-07 | 9.0e-8 / 1.1e-8 / 7.8e-7 | 1.57e-03 | 1.898334 | 98.946 |
| midpoint, Hermite lattice dx = 0.025 M | 2.162e-06 | 5.304e-06 | 5.060e-05 | 2.2e-6 / 5.3e-6 / 5.1e-5 | 1.59e-02 | 1.898260 | 98.977 |
| Boris (Cholesky triad), Hermite lattice dx = 0.025 M | 2.046e-06 | 3.788e-06 | 5.289e-05 | 2.0e-6 / 3.8e-6 / 5.3e-5 | 1.90e-02 | 1.898248 | 98.981 |

**Convergence orders** (least-squares slopes over all step sizes; pairwise orders in the tables):

* dt, analytic metric. Passage (spherical KS, dt = 0.08 ... 0.005 M): midpoint 2.001, Boris
  symmetric 1.996, Boris Cholesky 1.995; passage in Cartesian KS (dt = 0.08 ... 0.00125 M):
  2.03-2.04 (pairwise 2.00 for dt <= 0.02). Schwarzschild eccentric and plunge, all pushers,
  spherical and Cartesian KS: 2.000-2.001; circular orbit in Cartesian KS 2.000 (in spherical KS
  the circular orbit is integrated exactly up to round-off). BL orbits (dt = 0.02, 0.01 M):
  error ratio 3.99-4.00.
* dx, metric on the AthenaK mesh (Hermite reconstruction, dx = 0.5, 0.25, 0.125 M,
  dt = 0.01 M): Schwarzschild circular 2.64 (final position), 3.10 (energy); Schwarzschild
  eccentric 3.17 (final position; pairwise 4.44 and 1.91; max over checkpoints 2.58), 2.95
  (energy); Kerr a = 0.9 inclined orbit 2.89 (final position), 3.29 (energy), 2.66 (Q). The
  reconstructed metric at the particle converges at third order. Mesh and virtual-lattice runs
  agree to <= 1.2e-9.

**CPU-GPU** (passage input, dt = 0.01 M, 23002 records): max |x_CPU - x_GPU| = 1.4e-14
(midpoint, analytic spherical KS) and 1.8e-8 (Boris Cholesky, Hermite lattice; round-off
amplified by the near-separatrix passage); not bitwise identical; invariant errors and final
errors agree to 4 digits.

**Run health.** 176 runs (174 GPU, 2 CPU), all terminated normally, no NaN, no particle lost,
zero unconverged implicit iterations in any step of any run (the history was written every
cycle), at most 11 iterations per step. Disagreements and anomalies are listed at the end; the
main one is that the passage's Hermite-grid position error at dt = 0.01 M is dominated by the
time-step error in Cartesian coordinates, not by the interpolation as the paper states.


## A. Schwarzschild (a = 0), single particle

**Orbits** (designed with `analysis/geodesic/make_schwarzschild_reference.py`, ICs and exact
solutions in `problems/schwarzschild/ref/orbits.json`):

* `circ`: circular, r = 8 M, equatorial, E = (1-2M/r)/sqrt(1-3M/r), L = sqrt(Mr)/sqrt(1-3M/r),
  u_r^KS = 2ME/(r-2M); t_end = 1000 M (7.0 orbits). Exact: phi = Omega t, Omega = sqrt(M/r^3).
* `ecc`: eccentric bound, p = 8 M, e = 0.3 (6.154 M <= r <= 11.43 M), orbital plane inclined by
  30 deg (theta in [60, 120] deg), starts at pericentre; t_end = 1000 M (3.2 radial periods,
  T_r = 311.09 M; periapsis advance 6.506 rad per radial period). Exact: Mino-time quadrature
  (`kerr.MinoOrbit` at a = 0).
* `plunge`: E = 0.99, L = 3.9 M (below the critical L = 3.92 M for this E: no turning point;
  E^2 - V_max = 0.00446 at r = 4.111 M), plane inclined by 45 deg, starts inbound at r = 10 M,
  winds 8.93 rad (1.4 turns) in its plane, crosses the horizon at t = 75.066 M (KS time) and
  is stopped at t_end = 77.52 M where r = 1.018 M (before the singularity; KS coordinates are
  regular at the horizon). Exact: quadrature in r of dt_KS/dr and dpsi/dr written in a form
  regular at r = 2M (30 digits).

The exact solutions agree with a free-running DOP853 integration (rtol = atol = 2.5e-14) to
<= 1.7e-11 (position) over the full runs. Inputs: `problems/schwarzschild/geodesic.athinput`
(analytic and lattice) and `problems/schwarzschild/geodesic_mesh.athinput` (mesh), both with
`bh_spin = 0`; run names `schw/<orbit>_<pusher>_<ks|cks>_dt<dt>` and
`schw_mesh/<orbit>_<pusher>_<mesh|lat>_dx<dx>`. Example:

```
ATHENA_EXE=/data/haiyangw/nrpic/.work/build_gpu_dev/src/athena TIME=00:20:00 JOB_NAME=geo \
  scripts/gpu_run.sh runs/geodesic/schw/ecc_mid_cks_dt0.01 problems/schwarzschild/geodesic.athinput \
  particles/pusher=midpoint particles/metric=kerr_schild particles/bh_spin=0.0 particles/dt=0.01 \
  time/tlim=1000.0 particles/tolerance=2.0e-14 particles/max_iterations=200 \
  particles/hist_dcycle=1 particles/traj_dcycle=1 particles/traj_ntrack=1 time/ndiag=20000 \
  particles/p0_x1=6.153846153846153 particles/p0_x2=0.0 particles/p0_x3=3.768143997376471e-16 \
  particles/p0_u1=0.45863025005813407 particles/p0_u2=0.5080813315909193 \
  particles/p0_u3=0.29334089356424076 particles/p0_m=0.0
```

Mesh runs add `particles/metric=mesh` and the mesh size, e.g. for the eccentric orbit at
dx = 0.125 M: `mesh/nx1=192 mesh/x1min=-12.0 mesh/x1max=12.0 meshblock/nx1=48 mesh/nx2=192
mesh/x2min=-12.0 mesh/x2max=12.0 meshblock/nx2=48 mesh/nx3=96 mesh/x3min=-6.0 mesh/x3max=6.0
meshblock/nx3=48` (4 x 4 x 2 MeshBlocks; dx = 0.5 and 0.25 use 24^3 blocks, 2x2x1 and 4x4x2).
The circular orbit uses [-10,10]^2 x [-2,2] M with blocks (20,20,8), (20,20,16), (40,40,32)
(2x2x1, 4x4x1, 4x4x1). The lattice comparison runs use `particles/metric=lattice
particles/lattice_dx=<dx>` with the same ICs (lattice nodes = mesh cell centres).

#### A0. Orbits and initial states

- **circ**: circular orbit, r = 8 M, equatorial plane; E = 0.9486832980505138, L_z = 3.5777087639996634, Q = 4.79923e-32, t_end = 1000.0 M; IC (ks) x = [8.0, 1.5707963267948966, 0.0], u = [0.31622776601683794, 0.0, 3.5777087639996634]; IC (cks) x = [8.0, 0.0, 4.898587196589413e-16], u = [0.31622776601683794, 0.4472135954999579, 1.9363366072701937e-17]
- **ecc**: eccentric bound orbit, p = 8 M, e = 0.3, orbital plane inclined by 30 deg, starts at pericentre; E = 0.9525397501207398, L_z = 3.1266543482518108, Q = 3.25866, t_end = 1000.0 M; IC (ks) x = [6.153846153846153, 1.5707963267948966, 0.0], u = [0.45863025005813407, -1.8051747296260965, 3.1266543482518108]; IC (cks) x = [6.153846153846153, 0.0, 3.768143997376471e-16], u = [0.45863025005813407, 0.5080813315909193, 0.29334089356424076]
- **plunge**: plunging orbit, E = 0.99, L = 3.9 M, plane inclined by 45 deg, starts inbound at r = 10 M, crosses the horizon, stopped at r ~ 1 M; E = 0.99, L_z = 2.7577164466275357, Q = 7.605, t_end = 77.52 M; IC (ks) x = [10.0, 1.5707963267948966, 0.0], u = [-0.05462787028011834, -2.7577164466275352, 2.7577164466275357]; IC (cks) x = [10.0, 0.0, 6.123233995736766e-16], u = [-0.054627870280118354, 0.27577164466275356, 0.27577164466275356]

#### A1. Final-position error vs dt, analytic metric

| orbit | pusher | metric | dt=0.08 | dt=0.04 | dt=0.02 | dt=0.01 | dt=0.005 | order (final) | pairwise | order (max over checkpoints) |
|---|---|---|---|---|---|---|---|---|---|---|
| circ | midpoint | ks | 1.477e-11 | 8.590e-12 | 2.102e-11 | 1.253e-10 | 2.570e-10 | -1.211 | -1.04, -2.58, -1.29, 0.78 | -1.211 |
| circ | Boris sym | ks | 9.557e-11 | 8.590e-12 | 2.110e-11 | 7.095e-11 | 2.570e-10 | -0.590 | -1.86, -1.75, -1.30, 3.48 | -0.619 |
| circ | midpoint | cks | 1.020e-03 | 2.550e-04 | 6.375e-05 | 1.594e-05 | 3.985e-06 | 2.000 | 2.00, 2.00, 2.00, 2.00 | 2.000 |
| circ | Boris sym | cks | 1.019e-03 | 2.547e-04 | 6.368e-05 | 1.592e-05 | 3.988e-06 | 1.999 | 2.00, 2.00, 2.00, 2.00 | 1.999 |
| circ | Boris chol | cks | 1.105e-03 | 2.763e-04 | 6.908e-05 | 1.727e-05 | 4.318e-06 | 2.000 | 2.00, 2.00, 2.00, 2.00 | 2.000 |
| ecc | midpoint | ks | 1.721e-04 | 4.303e-05 | 1.076e-05 | 2.689e-06 | 6.724e-07 | 2.000 | 2.00, 2.00, 2.00, 2.00 | 2.000 |
| ecc | Boris sym | ks | 1.567e-04 | 3.917e-05 | 9.793e-06 | 2.448e-06 | 6.120e-07 | 2.000 | 2.00, 2.00, 2.00, 2.00 | 2.000 |
| ecc | midpoint | cks | 1.595e-03 | 3.988e-04 | 9.969e-05 | 2.492e-05 | 6.230e-06 | 2.000 | 2.00, 2.00, 2.00, 2.00 | 2.000 |
| ecc | Boris sym | cks | 1.620e-03 | 4.049e-04 | 1.012e-04 | 2.531e-05 | 6.333e-06 | 2.000 | 2.00, 2.00, 2.00, 2.00 | 2.000 |
| ecc | Boris chol | cks | 1.806e-03 | 4.515e-04 | 1.129e-04 | 2.822e-05 | 7.055e-06 | 2.000 | 2.00, 2.00, 2.00, 2.00 | 2.000 |
| plunge | midpoint | ks | 3.248e-03 | 8.115e-04 | 2.029e-04 | 5.071e-05 | 1.268e-05 | 2.000 | 2.00, 2.00, 2.00, 2.00 | 2.000 |
| plunge | Boris sym | ks | 2.617e-03 | 6.540e-04 | 1.635e-04 | 4.087e-05 | 1.022e-05 | 2.000 | 2.00, 2.00, 2.00, 2.00 | 2.000 |
| plunge | midpoint | cks | 1.193e-02 | 2.974e-03 | 7.432e-04 | 1.858e-04 | 4.644e-05 | 2.001 | 2.00, 2.00, 2.00, 2.00 | 2.001 |
| plunge | Boris sym | cks | 1.275e-02 | 3.179e-03 | 7.943e-04 | 1.985e-04 | 4.964e-05 | 2.001 | 2.00, 2.00, 2.00, 2.00 | 2.001 |
| plunge | Boris chol | cks | 1.305e-02 | 3.254e-03 | 8.129e-04 | 2.032e-04 | 5.079e-05 | 2.001 | 2.00, 2.00, 2.00, 2.00 | 2.001 |

#### A2. Invariant errors (max relative; Q absolute for the circular orbit)

| orbit | pusher | metric | dE / dQ / dLz, dt=0.08 | dE / dQ / dLz, dt=0.04 | dE / dQ / dLz, dt=0.02 | dE / dQ / dLz, dt=0.01 | dE / dQ / dLz, dt=0.005 | order dE |
|---|---|---|---|---|---|---|---|---|
| circ | midpoint | ks | 0 / 9.4e-29 / 0 | 0 / 9.4e-29 / 0 | 0 / 9.4e-29 / 0 | 0 / 9.4e-29 / 0 | 0 / 9.4e-29 / 0 | nan |
| circ | Boris sym | ks | 8.7e-14 / 9.4e-29 / 5.2e-13 | 7.0e-16 / 9.4e-29 / 2.5e-15 | 1.1e-14 / 9.4e-29 / 6.5e-14 | 3.2e-14 / 9.4e-29 / 1.9e-13 | 1.2e-16 / 9.4e-29 / 0 | 1.36 |
| circ | midpoint | cks | 2.3e-11 / 4.5e-31 / 8.8e-15 | 1.5e-12 / 4.5e-31 / 1.3e-13 | 9.0e-14 / 4.5e-31 / 1.5e-14 | 9.7e-15 / 4.5e-31 / 2.5e-14 | 4.8e-15 / 4.5e-31 / 2.9e-14 | 3.17 |
| circ | Boris sym | cks | 2.3e-11 / 1.6e-25 / 3.2e-12 | 1.3e-12 / 7.0e-25 / 6.3e-12 | 2.0e-12 / 2.2e-24 / 1.3e-11 | 4.2e-12 / 9.7e-24 / 2.5e-11 | 8.4e-12 / 4.0e-23 / 5.0e-11 | 0.12 |
| circ | Boris chol | cks | 9.4e-08 / 4.5e-31 / 5.7e-07 | 2.4e-08 / 4.5e-31 / 1.4e-07 | 5.9e-09 / 4.5e-31 / 3.5e-08 | 1.5e-09 / 4.5e-31 / 8.8e-09 | 3.7e-10 / 4.5e-31 / 2.2e-09 | 2.00 |
| ecc | midpoint | ks | 5.6e-08 / 1.4e-06 / 0 | 1.4e-08 / 3.6e-07 / 0 | 3.5e-09 / 8.9e-08 / 0 | 8.8e-10 / 2.2e-08 / 0 | 2.2e-10 / 5.6e-09 / 0 | 2.00 |
| ecc | Boris sym | ks | 1.6e-08 / 2.6e-06 / 4.8e-08 | 4.0e-09 / 6.5e-07 / 1.2e-08 | 1.0e-09 / 1.6e-07 / 3.0e-09 | 2.5e-10 / 4.1e-08 / 7.6e-10 | 6.2e-11 / 1.0e-08 / 1.9e-10 | 2.00 |
| ecc | midpoint | cks | 5.3e-07 / 1.4e-13 / 5.7e-14 | 1.3e-07 / 1.9e-13 / 1.1e-13 | 3.3e-08 / 2.8e-14 / 2.1e-14 | 8.4e-09 / 3.4e-14 / 3.1e-14 | 2.1e-09 / 3.8e-14 / 2.8e-14 | 2.00 |
| ecc | Boris sym | cks | 5.2e-07 / 3.9e-12 / 1.9e-12 | 1.3e-07 / 7.9e-12 / 3.9e-12 | 3.3e-08 / 1.6e-11 / 7.9e-12 | 8.2e-09 / 3.1e-11 / 1.6e-11 | 2.1e-09 / 6.3e-11 / 3.2e-11 | 2.00 |
| ecc | Boris chol | cks | 6.4e-07 / 3.7e-06 / 9.6e-07 | 1.6e-07 / 9.3e-07 / 2.4e-07 | 4.0e-08 / 2.3e-07 / 6.0e-08 | 1.0e-08 / 5.8e-08 / 1.5e-08 | 2.5e-09 / 1.4e-08 / 3.8e-09 | 2.00 |
| plunge | midpoint | ks | 1.5e-04 / 8.5e-05 / 0 | 3.7e-05 / 2.1e-05 / 0 | 9.2e-06 / 5.3e-06 / 0 | 2.3e-06 / 1.3e-06 / 0 | 5.7e-07 / 3.3e-07 / 0 | 2.00 |
| plunge | Boris sym | ks | 2.3e-04 / 2.9e-04 / 1.7e-05 | 5.6e-05 / 7.4e-05 / 4.3e-06 | 1.4e-05 / 1.8e-05 / 1.1e-06 | 3.5e-06 / 4.6e-06 / 2.7e-07 | 8.8e-07 / 1.2e-06 / 6.7e-08 | 2.00 |
| plunge | midpoint | cks | 1.1e-03 / 1.1e-14 / 5.0e-15 | 2.6e-04 / 1.1e-14 / 5.0e-15 | 6.5e-05 / 1.2e-14 / 5.8e-15 | 1.6e-05 / 2.4e-14 / 1.1e-14 | 4.1e-06 / 2.0e-14 / 1.0e-14 | 2.02 |
| plunge | Boris sym | cks | 1.8e-03 / 2.9e-13 / 1.4e-13 | 4.2e-04 / 6.8e-13 / 3.5e-13 | 1.0e-04 / 1.5e-12 / 7.0e-13 | 2.6e-05 / 2.8e-12 / 1.4e-12 | 6.5e-06 / 5.5e-12 / 2.7e-12 | 2.02 |
| plunge | Boris chol | cks | 7.8e-04 / 1.6e-04 / 3.6e-05 | 1.9e-04 / 3.9e-05 / 8.9e-06 | 4.7e-05 / 9.7e-06 / 2.2e-06 | 1.2e-05 / 2.4e-06 / 5.5e-07 | 2.9e-06 / 6.1e-07 / 1.4e-07 | 2.02 |

Runs with unconverged steps: 0 of 99; largest iteration count 11.

#### A3. Mesh metric (dt = 0.01 M), errors vs dx

| orbit | pusher | metric | dx=0.125: final (max) | dx=0.25 | dx=0.5 | order final | pairwise | order max | max dE/E (asc. dx) | order dE | analytic Cart. KS same dt: final / dE |
|---|---|---|---|---|---|---|---|---|---|---|---|
| circ | midpoint | mesh | 1.144e-03 (1.1e-03) | 6.840e-03 (6.8e-03) | 4.435e-02 (4.4e-02) | 2.64 | 2.58, 2.70 | 2.64 | 8.5e-08, 6.7e-07, 6.2e-06 | 3.10 | 1.6e-05 / 9.7e-15 |
| circ | midpoint | lat | 1.144e-03 (1.1e-03) | 6.840e-03 (6.8e-03) | 4.435e-02 (4.4e-02) | 2.64 | 2.58, 2.70 | 2.64 | 8.5e-08, 6.7e-07, 6.2e-06 | 3.10 | 1.6e-05 / 9.7e-15 |
| circ | Boris sym | mesh | 1.144e-03 (1.1e-03) | 6.838e-03 (6.8e-03) | 4.434e-02 (4.4e-02) | 2.64 | 2.58, 2.70 | 2.64 | 8.5e-08, 6.7e-07, 6.2e-06 | 3.10 | 1.6e-05 / 4.2e-12 |
| circ | Boris sym | lat | 1.144e-03 (1.1e-03) | 6.838e-03 (6.8e-03) | 4.434e-02 (4.4e-02) | 2.64 | 2.58, 2.70 | 2.64 | 8.5e-08, 6.7e-07, 6.2e-06 | 3.10 | 1.6e-05 / 4.2e-12 |
| ecc | midpoint | mesh | 2.566e-04 (5.8e-04) | 5.555e-03 (5.6e-03) | 2.082e-02 (2.1e-02) | 3.17 | 4.44, 1.91 | 2.58 | 4.8e-07, 4.3e-06, 2.9e-05 | 2.95 | 2.5e-05 / 8.4e-09 |
| ecc | midpoint | lat | 2.566e-04 (5.8e-04) | 5.555e-03 (5.6e-03) | 2.082e-02 (2.1e-02) | 3.17 | 4.44, 1.91 | 2.58 | 4.8e-07, 4.3e-06, 2.9e-05 | 2.95 | 2.5e-05 / 8.4e-09 |
| ecc | Boris sym | mesh | 2.571e-04 (5.8e-04) | 5.544e-03 (5.5e-03) | 2.082e-02 (2.1e-02) | 3.17 | 4.43, 1.91 | 2.58 | 4.8e-07, 4.3e-06, 2.9e-05 | 2.95 | 2.5e-05 / 8.2e-09 |
| ecc | Boris sym | lat | 2.571e-04 (5.8e-04) | 5.544e-03 (5.5e-03) | 2.082e-02 (2.1e-02) | 3.17 | 4.43, 1.91 | 2.58 | 4.8e-07, 4.3e-06, 2.9e-05 | 2.95 | 2.5e-05 / 8.2e-09 |

| mesh run | max \|alpha err\| | max \|beta err\| | max \|gamma err\| | unconv / max it |
|---|---|---|---|---|
| circ_bsym_mesh_dx0.125 | 2.94e-08 | 9.88e-08 | 2.10e-07 | 0/5 |
| circ_bsym_mesh_dx0.25 | 2.60e-07 | 7.78e-07 | 1.72e-06 | 0/5 |
| circ_bsym_mesh_dx0.5 | 2.30e-06 | 6.72e-06 | 1.55e-05 | 0/5 |
| circ_mid_mesh_dx0.125 | 2.94e-08 | 9.88e-08 | 2.10e-07 | 0/5 |
| circ_mid_mesh_dx0.25 | 2.60e-07 | 7.78e-07 | 1.72e-06 | 0/5 |
| circ_mid_mesh_dx0.5 | 2.30e-06 | 6.72e-06 | 1.55e-05 | 0/5 |
| ecc_bsym_mesh_dx0.125 | 8.35e-08 | 4.24e-07 | 8.57e-07 | 0/5 |
| ecc_bsym_mesh_dx0.25 | 6.88e-07 | 3.30e-06 | 7.21e-06 | 0/5 |
| ecc_bsym_mesh_dx0.5 | 5.26e-06 | 2.78e-05 | 5.68e-05 | 0/5 |
| ecc_mid_mesh_dx0.125 | 8.35e-08 | 4.24e-07 | 8.57e-07 | 0/5 |
| ecc_mid_mesh_dx0.25 | 6.88e-07 | 3.30e-06 | 7.21e-06 | 0/5 |
| ecc_mid_mesh_dx0.5 | 5.26e-06 | 2.78e-05 | 5.68e-05 | 0/5 |

| case | max \|x_mesh - x_lattice\| | max \|u_mesh - u_lattice\| | bitwise identical |
|---|---|---|---|
| circ_mid_dx0.5 | 1.131e-11 | 7.315e-13 | False |
| circ_mid_dx0.25 | 1.120e-11 | 7.403e-13 | False |
| circ_mid_dx0.125 | 2.379e-11 | 1.481e-12 | False |
| circ_bsym_dx0.5 | 5.957e-11 | 3.832e-12 | False |
| circ_bsym_dx0.25 | 1.290e-10 | 8.541e-12 | False |
| circ_bsym_dx0.125 | 3.141e-10 | 2.132e-11 | False |
| ecc_mid_dx0.5 | 5.196e-11 | 3.949e-12 | False |
| ecc_mid_dx0.25 | 5.353e-11 | 4.341e-12 | False |
| ecc_mid_dx0.125 | 2.893e-11 | 2.356e-12 | False |
| ecc_bsym_dx0.5 | 1.228e-09 | 1.059e-10 | False |
| ecc_bsym_dx0.25 | 1.229e-09 | 9.298e-11 | False |
| ecc_bsym_dx0.125 | 2.234e-10 | 1.762e-11 | False |

**Findings.**
* Second-order convergence in dt for both pushers (and both Boris triads), in spherical and in
  Cartesian KS, for the eccentric orbit and the plunge (fitted orders 2.000-2.001, pairwise
  1.999-2.004), and for the circular orbit in Cartesian KS (2.000). Scaled by (dt/0.01 M)^2 the
  whole position-error histories of the five dt collapse onto one curve (`diag_schw_dt.png`).
* The circular orbit in spherical KS has no truncation error: r, theta, u_i are constant and
  phi is linear in t, which the implicit midpoint and the Boris update (constant triad) reproduce
  exactly. The errors (8.6e-12 to 2.6e-10) are round-off, growing with the number of steps, so
  no order can be fitted there (negative "orders" in table A1 are this effect, not a failure).
* Invariants: E errors scale as dt^2 everywhere except where they are at round-off. The
  midpoint conserves L_z exactly in spherical coordinates (cyclic) and, in Cartesian KS, L_z and
  Q = L^2 - L_z^2 to 1e-13 (quadratic invariants of the symplectic midpoint rule). Boris with the
  symmetric triad keeps Q to 1e-11 in Cartesian KS; with the Cholesky triad (a gauge tied to the
  coordinate axes) Q and L_z errors are second order, 5.8e-8 and 1.5e-8 at dt = 0.01 for the
  eccentric orbit.
* The plunge is the hardest case: max dE/E 2.3e-6 (midpoint) and 3.5e-6 (Boris) at dt = 0.01
  in spherical KS (1.6e-5 and 2.6e-5 in Cartesian KS), reached at t_end; in spherical KS
  |dE/E| exceeds 1e-7 only after t = 71.7 M (r < 2.7 M) and 1e-6 after t = 76.6 M (r < 1.45 M,
  inside the horizon). The errors remain exactly second order.
* No unconverged implicit iteration in any Schwarzschild run; at most 11 iterations per step
  (plunge, dt = 0.08 M).
* **Mesh metric.** The mesh runs agree with the lattice runs of the same spacing to <= 1.2e-9
  (round-off: block-local versus global index arithmetic), for both orbits and both pushers, on
  multi-block meshes with block crossings. The Hermite reconstruction limits the accuracy: at
  dx = 0.125 M the final-position error is 1.1e-3 (circular) and 2.6e-4 (eccentric) against
  1.6e-5 and 2.5e-5 for the analytic Cartesian metric at the same dt. Observed orders in dx:
  final position 2.64 (circular; pairwise 2.58, 2.70) and 3.17 (eccentric; pairwise 4.44, 1.91,
  irregular because the final error is a snapshot of an oscillating error; the maximum over the
  checkpoints gives 2.58); energy error 3.10 and 2.95; the reconstructed lapse, shift and metric
  at the particle converge at third order (ratio 8.8 per halving), as expected for Catmull-Rom
  values.

## B. Kerr a = 0.9, Boyer-Lindquist orbits

ICs and end times from `problems/kerr/ref/initial_conditions.json`: equatorial eccentric
`p0_x = (6.0, 1.5707963267948966, 0.0)`, `p0_u = (0.0, 0.0, 3.144275)`, t_end = 4550 M
(20.009 T_r); inclined `p0_x = (8.0, 1.2207963267948965, 0.0)`, `p0_u = (0.0, 0.9, 2.9)`,
t_end = 3850 M (18.026 T_r). Input `problems/kerr/geodesic.athinput` with
`particles/metric=boyer_lindquist particles/bh_spin=0.9 time/tlim=4550.0` (or `3850.0`).
**Step sizes: dt = 0.02 M and 0.01 M** for the midpoint and Boris (symmetric triad); Boris with
the Cholesky triad at dt = 0.01 M. The BL spatial metric is diagonal, so the two triads coincide
analytically; their errors agree to 3-4 digits (round-off level differences). The figure `fig_bl_trajectories.pdf` shows
the Boris (symmetric triad) runs at dt = 0.01 M. Final-position errors are measured against the
exact final states of the reference JSON.

#### B. Boyer-Lindquist orbits (a = 0.9)

**equatorial eccentric, t_end = 4550 M.** Exact: r in [6.000000, 11.605636], theta in [1.570796, 1.570796], T_r = 227.401414 M, final (r, theta, phi) = [6.006379892, 1.570796327, 173.732515678]

| run | r range / M | max dE/E | max dLz/Lz | max dQ/Q | final pos err | (dr, dth, dphi) | periapsis advance / rad per T_r (exact) | max \|t_peri err\| | theta range; mean nodal advance / rad (reference traj.) | unconv / max it | time [s] |
|---|---|---|---|---|---|---|---|---|---|---|---|
| ecc_bchol_dt0.01 | 6.000000 - 11.605636 | 1.593e-10 | 2.543e-11 | 9.872e-28 (abs) | 2.330e-06 | -3.37e-07, +0.00e+00, -2.33e-06 | 2.3965710 (2.3965710) | 5.2e-05 |  | 0 / 5 | 58 |
| ecc_bsym_dt0.01 | 6.000000 - 11.605636 | 1.593e-10 | 2.539e-11 | 9.872e-28 (abs) | 2.330e-06 | -3.37e-07, +0.00e+00, -2.33e-06 | 2.3965710 (2.3965710) | 5.2e-05 |  | 0 / 5 | 74 |
| ecc_bsym_dt0.02 | 6.000000 - 11.605637 | 6.372e-10 | 1.012e-10 | 9.872e-28 (abs) | 9.307e-06 | -1.35e-06, +0.00e+00, -9.31e-06 | 2.3965712 (2.3965710) | 2.1e-04 |  | 0 / 6 | 38 |
| ecc_mid_dt0.01 | 6.000000 - 11.605636 | 8.234e-11 | 0 | 9.872e-28 (abs) | 1.495e-07 | -1.50e-07, +0.00e+00, -1.12e-07 | 2.3965711 (2.3965710) | 2.3e-05 |  | 0 / 6 | 49 |
| ecc_mid_dt0.02 | 6.000000 - 11.605636 | 3.293e-10 | 0 | 9.872e-28 (abs) | 5.967e-07 | -5.97e-07, +0.00e+00, -4.34e-07 | 2.3965713 (2.3965710) | 9.2e-05 |  | 0 / 6 | 25 |

**inclined, t_end = 3850 M.** Exact: r in [8.000000, 8.517104], theta in [1.124609, 2.016983], T_r = 213.577677 M, final (r, theta, phi) = [8.00363643, 1.836921977, 157.5441796]

| run | r range / M | max dE/E | max dLz/Lz | max dQ/Q | final pos err | (dr, dth, dphi) | periapsis advance / rad per T_r (exact) | max \|t_peri err\| | theta range; mean nodal advance / rad (reference traj.) | unconv / max it | time [s] |
|---|---|---|---|---|---|---|---|---|---|---|---|
| inc_bchol_dt0.01 | 8.000000 - 8.517104 | 8.814e-12 | 1.168e-10 | 2.617e-09 | 7.426e-07 | -6.76e-08, +4.83e-07, +7.43e-07 | 2.4559129 (2.4559127) | 5.1e-05 | 1.12461-2.01698; 0.4090450 (ref. 0.4090450) | 0 / 5 | 49 |
| inc_bsym_dt0.01 | 8.000000 - 8.517104 | 8.820e-12 | 1.169e-10 | 2.617e-09 | 7.426e-07 | -6.76e-08, +4.83e-07, +7.43e-07 | 2.4559129 (2.4559127) | 5.1e-05 | 1.12461-2.01698; 0.4090450 (ref. 0.4090450) | 0 / 5 | 63 |
| inc_bsym_dt0.02 | 8.000000 - 8.517103 | 3.524e-11 | 4.669e-10 | 1.047e-08 | 2.977e-06 | -2.70e-07, +1.93e-06, +2.98e-06 | 2.4559133 (2.4559127) | 2.1e-04 | 1.12461-2.01698; 0.4090453 (ref. 0.4090450) | 0 / 6 | 32 |
| inc_mid_dt0.01 | 8.000000 - 8.517103 | 9.776e-11 | 0 | 4.541e-09 | 1.887e-06 | -5.51e-08, +6.72e-08, +1.89e-06 | 2.4559129 (2.4559127) | 4.2e-05 | 1.12461-2.01698; 0.4090450 (ref. 0.4090450) | 0 / 5 | 42 |
| inc_mid_dt0.02 | 8.000000 - 8.517103 | 3.910e-10 | 0 | 1.817e-08 | 7.555e-06 | -2.20e-07, +2.67e-07, +7.56e-06 | 2.4559135 (2.4559127) | 1.7e-04 | 1.12461-2.01698; 0.4090453 (ref. 0.4090450) | 0 / 6 | 22 |

**Findings.** Radial range 6.000000-11.605636 M (exact 6.000000-11.605636; paper "6.00 <= r <=
11.61") and 8.000000-8.517104 M with theta in [1.12461, 2.01698] (both hemispheres) for the
inclined orbit, all runs. Invariant errors <= 6.4e-10 (E), <= 4.7e-10 (L_z; exactly conserved by
the midpoint, L_z is cyclic in BL), <= 1.8e-8 (Q). Final-position errors 1.5e-7 to 9.3e-6, a
factor 3.99-4.00 between dt = 0.02 and 0.01 (second order). Precession: the mean periapsis
advance per radial period is 2.3965710 rad (equatorial; exact 2.3965710) and 2.4559129 rad
(inclined; exact pericentre phases 2.4559127, Omega_phi T_r - 2 pi = 2.4558758, the difference
being the oscillation of the pericentre-to-pericentre interval); pericentre times agree with the
exact ones to <= 5e-5 M (dt = 0.01). The mean nodal advance of the inclined orbit over 23
ascending nodes is 0.4090450 rad per node-to-node interval (reference trajectory, same
estimator: 0.4090450; Omega_phi T_theta - 2 pi = 0.4089332). No unconverged step: the
absolute tolerance 2e-14 is below the spacing of doubles for phi > 128 (2.8e-14; phi reaches
174 and 158), but the fixed-point iteration still ended on exact fixed points (max 6
iterations).


## C. Kerr-Schild e = 0.99 passage (a = 0.9 M, t = 230 M)

Initial state (paper Eq. (ks-passage-ic)): spherical KS `p0_x = (20.0, 1.5707963267948966, 0.0)`,
`p0_u = (-0.20131797516752664, 1.4049911031746785, 2.4328)`; Cartesian KS (lattice and `cks`
runs) `p0_x = (20.0, 0.9, 1.2246467991473533e-15)`,
`p0_u = (-0.20131797516752664, 0.11258069111746129, -0.07024955515873393)` (from
`problems/kerr/ref/initial_conditions.json`). Input `problems/kerr/geodesic.athinput`, overrides
`particles/bh_spin=0.9 particles/lattice_dx=0.025 time/tlim=230.0` plus pusher, metric and dt.
Example (midpoint, analytic spherical KS, dt = 0.01):

```
ATHENA_EXE=/data/haiyangw/nrpic/.work/build_gpu_dev/src/athena TIME=00:20:00 JOB_NAME=geo \
  scripts/gpu_run.sh runs/geodesic/kerr_passage/mid_ks_dt0.01 problems/kerr/geodesic.athinput \
  particles/pusher=midpoint particles/metric=kerr_schild_sph particles/bh_spin=0.9 \
  particles/lattice_dx=0.025 particles/dt=0.01 time/tlim=230.0 particles/tolerance=2.0e-14 \
  particles/max_iterations=200 particles/hist_dcycle=1 particles/traj_dcycle=1 \
  particles/traj_ntrack=1 time/ndiag=20000 particles/p0_x1=20.0 \
  particles/p0_x2=1.5707963267948966 particles/p0_x3=0.0 particles/p0_u1=-0.20131797516752664 \
  particles/p0_u2=1.4049911031746785 particles/p0_u3=2.4328 particles/p0_m=0.0
```

The four combinations of the paper (midpoint and Boris, analytic spherical KS input and Hermite
lattice) reproduce the paper's numbers and the standalone build exactly (all 4 digits). The
paper does not state the triad gauge; the analytic-input Boris value matches the symmetric triad
and the lattice Boris value matches the Cholesky triad, so these are the combinations shown in
`fig_ks_passage.pdf`; the other gauge is listed as well.

#### C1. Maximum relative invariant errors, dt = 0.01 M, t = 230 M

| pusher | metric input | max dE/E | max dLz/Lz | max dQ/Q | paper (E, Lz, Q) | standalone build (E, Lz, Q) | unconverged steps / max iter |
|---|---|---|---|---|---|---|---|
| midpoint | analytic sph. KS | 2.781e-08 | 0 | 1.254e-07 | 2.8e-8, round-off, 1.3e-7 | 2.781e-08, 0.000e+00, 1.254e-07 | 0 / 5 |
| midpoint | lattice dx=0.025 | 2.162e-06 | 5.304e-06 | 5.060e-05 | 2.2e-06, 5.3e-06, 5.1e-05 | 2.162e-06, 5.304e-06, 5.060e-05 | 0 / 6 |
| midpoint | analytic Cart. KS | 6.154e-07 | 2.172e-14 | 1.226e-06 | - | - | 0 / 6 |
| Boris sym | analytic sph. KS | 9.046e-08 | 1.136e-08 | 7.825e-07 | 9.0e-08, 1.1e-08, 7.8e-07 | 9.046e-08, 1.136e-08, 7.825e-07 | 0 / 5 |
| Boris sym | lattice dx=0.025 | 3.194e-06 | 6.285e-06 | 4.890e-05 | - | - | 0 / 6 |
| Boris sym | analytic Cart. KS | 8.107e-07 | 2.102e-07 | 1.062e-06 | - | - | 0 / 6 |
| Boris chol | analytic sph. KS | 6.204e-08 | 7.173e-08 | 6.561e-07 | - | - | 0 / 5 |
| Boris chol | lattice dx=0.025 | 2.046e-06 | 3.788e-06 | 5.289e-05 | 2.0e-06, 3.8e-06, 5.3e-05 | 2.046e-06, 3.788e-06, 5.289e-05 | 0 / 6 |
| Boris chol | analytic Cart. KS | 2.978e-06 | 4.526e-06 | 3.513e-06 | - | - | 0 / 6 |

#### C2. Final-position error at t = 230 M vs dt

| pusher | metric | dt=0.00125 | dt=0.0025 | dt=0.005 | dt=0.01 | dt=0.02 | dt=0.04 | dt=0.08 | fitted order (all dt) | pairwise orders |
|---|---|---|---|---|---|---|---|---|---|---|
| midpoint | analytic sph. KS | - | - | 1.12e-04 | 4.49e-04 | 1.80e-03 | 7.19e-03 | 2.88e-02 | 2.001 | 2.00, 2.00, 2.00, 2.00 |
| Boris sym | analytic sph. KS | - | - | 3.93e-04 | 1.57e-03 | 6.28e-03 | 2.50e-02 | 9.92e-02 | 1.996 | 2.00, 2.00, 2.00, 1.99 |
| Boris chol | analytic sph. KS | - | - | 4.59e-04 | 1.84e-03 | 7.34e-03 | 2.93e-02 | 1.16e-01 | 1.995 | 2.00, 2.00, 2.00, 1.98 |
| midpoint | analytic Cart. KS | 2.69e-04 | 1.08e-03 | 4.31e-03 | 1.73e-02 | 6.96e-02 | 2.87e-01 | 1.32e+00 | 2.032 | 2.00, 2.00, 2.00, 2.01, 2.04, 2.21 |
| Boris sym | analytic Cart. KS | 3.07e-04 | 1.23e-03 | 4.91e-03 | 1.97e-02 | 7.94e-02 | 3.28e-01 | 1.56e+00 | 2.038 | 2.00, 2.00, 2.00, 2.01, 2.05, 2.25 |
| Boris chol | analytic Cart. KS | 3.20e-04 | 1.28e-03 | 5.13e-03 | 2.05e-02 | 8.29e-02 | 3.43e-01 | 1.65e+00 | 2.041 | 2.00, 2.00, 2.00, 2.01, 2.05, 2.27 |
| midpoint | lattice dx=0.025 | 8.92e-05 | 8.70e-04 | 4.14e-03 | 1.59e-02 | 7.02e-02 | - | - | 2.343 | 3.29, 2.25, 1.94, 2.14 |
| Boris sym | lattice dx=0.025 | 6.53e-05 | 9.69e-04 | 4.91e-03 | 1.80e-02 | 7.76e-02 | - | - | 2.464 | 3.89, 2.34, 1.87, 2.11 |
| Boris chol | lattice dx=0.025 | 5.50e-05 | 1.03e-03 | 5.11e-03 | 1.90e-02 | 8.06e-02 | - | - | 2.525 | 4.22, 2.32, 1.90, 2.08 |

Interpolation effect alone: max |(r/M, theta, phi)_lattice - (r/M, theta, phi)_Cartesian analytic| at t = 230 M, same pusher and dt:

| pusher | dt=0.00125 | dt=0.0025 | dt=0.005 | dt=0.01 | dt=0.02 | dt=0.04 | dt=0.08 |
|---|---|---|---|---|---|---|---|
| midpoint | 3.37e-04 | 2.08e-04 | 1.69e-04 | 1.34e-03 | 5.48e-04 | - | - |
| Boris sym | 3.42e-04 | 2.59e-04 | 4.77e-05 | 1.70e-03 | 1.78e-03 | - | - |
| Boris chol | 3.47e-04 | 2.55e-04 | 7.71e-05 | 1.52e-03 | 2.30e-03 | - | - |

Max relative energy error vs dt:

| pusher | metric | dt=0.00125 | dt=0.0025 | dt=0.005 | dt=0.01 | dt=0.02 | dt=0.04 | dt=0.08 |
|---|---|---|---|---|---|---|---|---|
| midpoint | analytic sph. KS | - | - | 6.95e-09 | 2.78e-08 | 1.11e-07 | 4.45e-07 | 1.78e-06 |
| Boris sym | analytic sph. KS | - | - | 2.26e-08 | 9.05e-08 | 3.62e-07 | 1.45e-06 | 5.79e-06 |
| Boris chol | analytic sph. KS | - | - | 1.55e-08 | 6.20e-08 | 2.48e-07 | 9.93e-07 | 3.97e-06 |
| midpoint | analytic Cart. KS | 9.62e-09 | 3.85e-08 | 1.54e-07 | 6.15e-07 | 2.46e-06 | 9.86e-06 | 3.96e-05 |
| Boris sym | analytic Cart. KS | 1.27e-08 | 5.07e-08 | 2.03e-07 | 8.11e-07 | 3.24e-06 | 1.30e-05 | 5.23e-05 |
| Boris chol | analytic Cart. KS | 4.65e-08 | 1.86e-07 | 7.44e-07 | 2.98e-06 | 1.20e-05 | 4.88e-05 | 2.14e-04 |
| midpoint | lattice dx=0.025 | 8.76e-07 | 8.96e-07 | 9.12e-07 | 2.16e-06 | 4.81e-06 | - | - |
| Boris sym | lattice dx=0.025 | 8.77e-07 | 8.66e-07 | 1.08e-06 | 3.19e-06 | 7.33e-06 | - | - |
| Boris chol | lattice dx=0.025 | 8.67e-07 | 1.03e-06 | 1.94e-06 | 2.05e-06 | 1.21e-05 | - | - |

**Final-position error and convergence.** For analytic spherical KS input both pushers are
second order (fitted orders in table C2; midpoint 4.49e-4 at dt = 0.01 against the paper's
~4.5e-4 read off its panel (c)). The Hermite-lattice runs give 1.6e-2 (midpoint) and 1.9e-2
(Boris, Cholesky) at dt = 0.01, as in the paper's panel (c) (~1.5-2e-2).
**Disagreement with the paper's interpretation.** The paper attributes the grid error to the
metric interpolation ("the accuracy of both methods is limited by the interpolation error of
the spacetime"). For the final-position error at dt = 0.01 M the measurements do not support
this. (i) The lattice error falls as dt^2 between dt = 0.02 and 0.0025 M (table C2). (ii) The
analytic *Cartesian* KS runs, which involve no interpolation, have almost the same error at the
same dt (dt = 0.01: midpoint 1.73e-2 against 1.59e-2 on the lattice, Boris Cholesky 2.05e-2
against 1.90e-2); they converge at second order from dt = 0.08 down to 0.00125 M. The time-step
error of both pushers is about 40 times larger in Cartesian than in spherical KS coordinates for
this passage. (iii) The interpolation alone, measured as the difference between the lattice and
the Cartesian-analytic final states at equal dt and pusher, moves the final position by only
5e-5 to 2.3e-3 (table "interpolation effect alone"), one to two orders of magnitude below the
time-step error at dt = 0.01. The two contributions become comparable only at dt ~ 0.001 M (at
dt = 0.00125 M: lattice 8.9e-5, Cartesian analytic 2.7e-4, difference 3.4e-4; they partly
cancel). The interpolation does dominate the invariant errors: at dt = 0.01 the lattice dQ/Q
(5.1e-5) is 40 times the Cartesian analytic value (1.2e-6) and dE/E 3.5 times; for dt -> 0 the
lattice dE/E levels off at 8.8e-7 (midpoint) while the Cartesian analytic value keeps falling as
dt^2 (9.6e-9 at dt = 0.00125).

**Pericentre.** Exact r_p = 1.8983272737 M at t_p = 98.94834714 M. Measured (parabolic
refinement of the discrete minimum of r(t), all dt = 0.01 runs): see the table below
(`r_p`, `t_p` columns): analytic spherical KS r_p = 1.898325 (midpoint), 1.898334 (Boris sym),
t_p = 98.949 / 98.946; lattice r_p = 1.898260 / 1.898248, t_p = 98.977 / 98.981.

Components (dr/M, dtheta, dphi) of the final error and invariants for every dt:

| run | final err | (dr, dth, dphi) | max dE/E | max dLz/Lz | max dQ/Q | r_p / M | t_p / M | unconv / max it | athena time [s] |
|---|---|---|---|---|---|---|---|---|---|
| bchol_cks_dt0.00125 | 3.201e-04 | -2.55e-04, +5.55e-05, +3.20e-04 | 4.646e-08 | 7.062e-08 | 5.481e-08 | 1.898326 | 98.9489 | 0 / 5 | 25.8 |
| bchol_cks_dt0.0025 | 1.281e-03 | -1.02e-03, +2.22e-04, +1.28e-03 | 1.859e-07 | 2.825e-07 | 2.193e-07 | 1.898322 | 98.9504 | 0 / 5 | 13.2 |
| bchol_cks_dt0.005 | 5.125e-03 | -4.08e-03, +8.90e-04, +5.13e-03 | 7.436e-07 | 1.130e-06 | 8.773e-07 | 1.898306 | 98.9567 | 0 / 5 | 6.7 |
| bchol_cks_dt0.01 | 2.054e-02 | -1.64e-02, +3.59e-03, +2.05e-02 | 2.978e-06 | 4.526e-06 | 3.513e-06 | 1.898244 | 98.9819 | 0 / 6 | 3.4 |
| bchol_cks_dt0.02 | 8.285e-02 | -6.62e-02, +1.48e-02, +8.29e-02 | 1.197e-05 | 1.819e-05 | 1.411e-05 | 1.897992 | 99.0839 | 0 / 7 | 1.7 |
| bchol_cks_dt0.04 | 3.430e-01 | -2.77e-01, +6.62e-02, +3.43e-01 | 4.882e-05 | 7.409e-05 | 5.748e-05 | 1.896957 | 99.5169 | 0 / 7 | 0.9 |
| bchol_cks_dt0.08 | 1.649e+00 | -1.39e+00, +4.06e-01, +1.65e+00 | 2.142e-04 | 3.218e-04 | 2.500e-04 | 1.892187 | 101.8361 | 0 / 9 | 0.5 |
| bchol_ks_dt0.005 | 4.594e-04 | +3.54e-04, -7.96e-05, -4.59e-04 | 1.551e-08 | 1.793e-08 | 1.640e-07 | 1.898329 | 98.9476 | 0 / 5 | 5.5 |
| bchol_ks_dt0.01 | 1.837e-03 | +1.41e-03, -3.18e-04, -1.84e-03 | 6.204e-08 | 7.173e-08 | 6.561e-07 | 1.898335 | 98.9453 | 0 / 5 | 2.8 |
| bchol_ks_dt0.02 | 7.343e-03 | +5.65e-03, -1.27e-03, -7.34e-03 | 2.482e-07 | 2.869e-07 | 2.624e-06 | 1.898359 | 98.9363 | 0 / 6 | 1.4 |
| bchol_ks_dt0.04 | 2.929e-02 | +2.25e-02, -5.03e-03, -2.93e-02 | 9.926e-07 | 1.148e-06 | 1.050e-05 | 1.898453 | 98.9005 | 0 / 6 | 0.7 |
| bchol_ks_dt0.08 | 1.158e-01 | +8.88e-02, -1.93e-02, -1.16e-01 | 3.970e-06 | 4.588e-06 | 4.198e-05 | 1.898828 | 98.7596 | 0 / 7 | 0.4 |
| bchol_lat_dt0.00125 | 5.500e-05 | +5.50e-05, -3.41e-06, -2.71e-05 | 8.674e-07 | 4.413e-06 | 5.148e-05 | 1.898326 | 98.9497 | 0 / 5 | 102.2 |
| bchol_lat_dt0.0025 | 1.026e-03 | -8.07e-04, +1.80e-04, +1.03e-03 | 1.029e-06 | 4.007e-06 | 5.175e-05 | 1.898322 | 98.9514 | 0 / 5 | 54.9 |
| bchol_lat_dt0.005 | 5.112e-03 | -4.16e-03, +8.92e-04, +5.11e-03 | 1.941e-06 | 2.585e-06 | 5.322e-05 | 1.898306 | 98.9584 | 0 / 5 | 28.8 |
| bchol_lat_dt0.01 | 1.903e-02 | -1.50e-02, +3.33e-03, +1.90e-02 | 2.046e-06 | 3.788e-06 | 5.289e-05 | 1.898248 | 98.9813 | 0 / 6 | 15.4 |
| bchol_lat_dt0.02 | 8.055e-02 | -6.43e-02, +1.44e-02, +8.06e-02 | 1.212e-05 | 1.652e-05 | 7.091e-05 | 1.897999 | 99.0821 | 0 / 7 | 8.1 |
| bsym_cks_dt0.00125 | 3.069e-04 | -2.37e-04, +5.31e-05, +3.07e-04 | 1.266e-08 | 3.270e-09 | 1.656e-08 | 1.898326 | 98.9489 | 0 / 4 | 33.6 |
| bsym_cks_dt0.0025 | 1.227e-03 | -9.49e-04, +2.12e-04, +1.23e-03 | 5.066e-08 | 1.313e-08 | 6.632e-08 | 1.898322 | 98.9504 | 0 / 5 | 17.7 |
| bsym_cks_dt0.005 | 4.911e-03 | -3.80e-03, +8.51e-04, +4.91e-03 | 2.027e-07 | 5.255e-08 | 2.654e-07 | 1.898307 | 98.9564 | 0 / 5 | 9.2 |
| bsym_cks_dt0.01 | 1.968e-02 | -1.52e-02, +3.43e-03, +1.97e-02 | 8.107e-07 | 2.102e-07 | 1.062e-06 | 1.898246 | 98.9807 | 0 / 6 | 4.7 |
| bsym_cks_dt0.02 | 7.936e-02 | -6.16e-02, +1.41e-02, +7.94e-02 | 3.244e-06 | 8.412e-07 | 4.251e-06 | 1.898000 | 99.0791 | 0 / 6 | 2.6 |
| bsym_cks_dt0.04 | 3.281e-01 | -2.57e-01, +6.30e-02, +3.28e-01 | 1.299e-05 | 3.370e-06 | 1.708e-05 | 1.896989 | 99.4946 | 0 / 7 | 1.3 |
| bsym_cks_dt0.08 | 1.560e+00 | -1.28e+00, +3.80e-01, +1.56e+00 | 5.227e-05 | 1.356e-05 | 6.945e-05 | 1.892380 | 101.6608 | 0 / 8 | 0.7 |
| bsym_ks_dt0.005 | 3.925e-04 | +3.01e-04, -6.81e-05, -3.93e-04 | 2.262e-08 | 2.842e-09 | 1.956e-07 | 1.898329 | 98.9477 | 0 / 5 | 8.6 |
| bsym_ks_dt0.01 | 1.570e-03 | +1.21e-03, -2.72e-04, -1.57e-03 | 9.046e-08 | 1.136e-08 | 7.825e-07 | 1.898334 | 98.9458 | 0 / 5 | 4.4 |
| bsym_ks_dt0.02 | 6.275e-03 | +4.82e-03, -1.09e-03, -6.28e-03 | 3.618e-07 | 4.541e-08 | 3.130e-06 | 1.898354 | 98.9381 | 0 / 6 | 2.3 |
| bsym_ks_dt0.04 | 2.504e-02 | +1.92e-02, -4.31e-03, -2.50e-02 | 1.447e-06 | 1.810e-07 | 1.252e-05 | 1.898435 | 98.9076 | 0 / 6 | 1.2 |
| bsym_ks_dt0.08 | 9.918e-02 | +7.58e-02, -1.66e-02, -9.92e-02 | 5.788e-06 | 7.132e-07 | 5.007e-05 | 1.898754 | 98.7874 | 0 / 7 | 0.6 |
| bsym_lat_dt0.00125 | 6.528e-05 | +6.53e-05, -4.90e-06, -3.53e-05 | 8.770e-07 | 4.440e-06 | 5.145e-05 | 1.898326 | 98.9496 | 0 / 4 | 111.1 |
| bsym_lat_dt0.0025 | 9.687e-04 | -7.33e-04, +1.70e-04, +9.69e-04 | 8.655e-07 | 4.237e-06 | 5.155e-05 | 1.898322 | 98.9513 | 0 / 5 | 60.2 |
| bsym_lat_dt0.005 | 4.911e-03 | -3.85e-03, +8.55e-04, +4.91e-03 | 1.081e-06 | 3.748e-06 | 5.208e-05 | 1.898306 | 98.9581 | 0 / 5 | 31.5 |
| bsym_lat_dt0.01 | 1.798e-02 | -1.37e-02, +3.14e-03, +1.80e-02 | 3.194e-06 | 6.285e-06 | 4.890e-05 | 1.898251 | 98.9799 | 0 / 6 | 16.8 |
| bsym_lat_dt0.02 | 7.758e-02 | -6.00e-02, +1.38e-02, +7.76e-02 | 7.327e-06 | 9.440e-06 | 5.727e-05 | 1.898005 | 99.0782 | 0 / 6 | 8.8 |
| mid_cks_dt0.00125 | 2.694e-04 | -2.09e-04, +4.66e-05, +2.69e-04 | 9.615e-09 | 1.126e-13 | 1.916e-08 | 1.898326 | 98.9488 | 0 / 4 | 21.3 |
| mid_cks_dt0.0025 | 1.078e-03 | -8.34e-04, +1.87e-04, +1.08e-03 | 3.846e-08 | 4.983e-14 | 7.663e-08 | 1.898323 | 98.9501 | 0 / 5 | 11.1 |
| mid_cks_dt0.005 | 4.313e-03 | -3.34e-03, +7.48e-04, +4.31e-03 | 1.538e-07 | 3.231e-14 | 3.065e-07 | 1.898309 | 98.9554 | 0 / 5 | 5.6 |
| mid_cks_dt0.01 | 1.728e-02 | -1.34e-02, +3.01e-03, +1.73e-02 | 6.154e-07 | 2.172e-14 | 1.226e-06 | 1.898256 | 98.9767 | 0 / 6 | 2.8 |
| mid_cks_dt0.02 | 6.961e-02 | -5.41e-02, +1.23e-02, +6.96e-02 | 2.462e-06 | 5.093e-14 | 4.906e-06 | 1.898041 | 99.0630 | 0 / 6 | 1.4 |
| mid_cks_dt0.04 | 2.866e-01 | -2.25e-01, +5.43e-02, +2.87e-01 | 9.859e-06 | 2.501e-14 | 1.965e-05 | 1.897161 | 99.4245 | 0 / 7 | 0.8 |
| mid_cks_dt0.08 | 1.323e+00 | -1.08e+00, +3.13e-01, +1.32e+00 | 3.960e-05 | 6.115e-14 | 7.919e-05 | 1.893227 | 101.2350 | 0 / 9 | 0.4 |
| mid_ks_dt0.005 | 1.122e-04 | -8.68e-05, +1.91e-05, +1.12e-04 | 6.952e-09 | 0 | 3.136e-08 | 1.898327 | 98.9485 | 0 / 5 | 4.8 |
| mid_ks_dt0.01 | 4.487e-04 | -3.47e-04, +7.64e-05, +4.49e-04 | 2.781e-08 | 0 | 1.254e-07 | 1.898325 | 98.9491 | 0 / 5 | 2.4 |
| mid_ks_dt0.02 | 1.795e-03 | -1.39e-03, +3.06e-04, +1.80e-03 | 1.112e-07 | 0 | 5.017e-07 | 1.898319 | 98.9513 | 0 / 6 | 1.2 |
| mid_ks_dt0.04 | 7.186e-03 | -5.56e-03, +1.23e-03, +7.19e-03 | 4.449e-07 | 0 | 2.007e-06 | 1.898295 | 98.9602 | 0 / 6 | 0.6 |
| mid_ks_dt0.08 | 2.882e-02 | -2.23e-02, +4.96e-03, +2.88e-02 | 1.780e-06 | 0 | 8.027e-06 | 1.898199 | 98.9960 | 0 / 8 | 0.3 |
| mid_lat_dt0.00125 | 8.919e-05 | +8.92e-05, -1.04e-05, -6.73e-05 | 8.758e-07 | 4.439e-06 | 5.146e-05 | 1.898326 | 98.9496 | 0 / 4 | 94.0 |
| mid_lat_dt0.0025 | 8.696e-04 | -6.55e-04, +1.52e-04, +8.70e-04 | 8.956e-07 | 4.205e-06 | 5.164e-05 | 1.898323 | 98.9512 | 0 / 5 | 51.5 |
| mid_lat_dt0.005 | 4.144e-03 | -3.23e-03, +7.22e-04, +4.14e-03 | 9.120e-07 | 4.024e-06 | 5.196e-05 | 1.898309 | 98.9568 | 0 / 5 | 26.7 |
| mid_lat_dt0.01 | 1.594e-02 | -1.21e-02, +2.78e-03, +1.59e-02 | 2.162e-06 | 5.304e-06 | 5.060e-05 | 1.898260 | 98.9766 | 0 / 6 | 14.3 |
| mid_lat_dt0.02 | 7.016e-02 | -5.41e-02, +1.25e-02, +7.02e-02 | 4.811e-06 | 8.419e-06 | 5.927e-05 | 1.898037 | 99.0660 | 0 / 6 | 7.5 |

Exact: r_p = 1.8983272737 M, t_p = 98.94834714 M; final state (r, theta, phi) = [23.483692534044632, 1.1622462450960478, 27.713606456353084].

All passage runs: 0 unconverged steps; at most 8 implicit iterations per step (dt = 0.08).

## D. CPU vs GPU

Same input as the GPU runs of part C, on the serial CPU executable (login node):

```
.work/build_check/src/athena -i problems/kerr/geodesic.athinput \
  -d runs/geodesic/kerr_passage_cpu/mid_ks_dt0.01 <same overrides as kerr_passage/mid_ks_dt0.01>
.work/build_check/src/athena -i problems/kerr/geodesic.athinput \
  -d runs/geodesic/kerr_passage_cpu/bchol_lat_dt0.01 <same overrides as kerr_passage/bchol_lat_dt0.01>
```

#### D. CPU vs GPU

| run | records CPU/GPU | max \|dt\| | max \|dx\| (all records) | max \|du\| | max \|d(r,th,ph)\| | final \|dx\| | bitwise identical | first differing record | CPU max dE/E | CPU final pos err |
|---|---|---|---|---|---|---|---|---|---|---|
| bchol_lat_dt0.01 | 23002 / 23002 | 0 | 1.814e-08 | 9.681e-10 | 9.911e-10 | 1.814e-08 | False | 8 | 2.046e-06 | 1.903e-02 |
| mid_ks_dt0.01 | 23002 / 23002 | 0 | 1.421e-14 | 4.607e-15 | 1.421e-14 | 1.421e-14 | False | 26 | 2.781e-08 | 4.487e-04 |

The trajectories are not bitwise identical (different compilers, FMA contraction and math
libraries), and the step times agree exactly. For the midpoint with analytic input the maximum
difference over all 23002 records is 1.4e-14 in position (ulp level). For Boris with the Hermite
lattice the difference starts at 1.7e-18 in record 8 and grows through the passage to
1.8e-8 in position (1e-9 in (r, theta, phi)) at t = 230; this is the amplification of round-off
by the near-separatrix passage (README: dr = -2.3e4 dE/E), six orders of magnitude below the
run's own error (1.9e-2). The implicit iteration counts differ in 1 (midpoint) and 28 (Boris
lattice) of 23002 steps. All invariant errors and the final-position error agree to 4 digits
(`diag_cpu_gpu.png`).



## E. Kerr a = 0.9 on the AthenaK mesh

Orbit: the paper's inclined BL orbit (8.00 M <= r <= 8.52 M, theta in [1.1246, 2.0170]),
transformed to Cartesian KS (`initial_state.cks` in the reference JSON; the run starts at the KS
time t0 = 3.6018507721 M of the initial event, so the exact state at run time t is taken at
t_KS = t0 + t). t_end = 600 M (2.8 radial periods), dt = 0.01 M. Input
`problems/kerr/geodesic_mesh.athinput` (`<adm> dynamic = false`, `particles/metric=mesh`,
`deposit = false`) on [-10,10]^2 x [-5,5] M with `mesh/nx1=40,80,160 mesh/nx3=20,40,80` for
dx = 0.5, 0.25, 0.125 M and MeshBlocks of 20^3, 20^3, 40^3 cells (2x2x1, 4x4x2, 4x4x2 blocks:
the particle crosses MeshBlock boundaries many times). For comparison the same orbit was run with
the virtual lattice (`particles/metric=lattice particles/lattice_dx=<dx>`, whose nodes coincide
with the mesh cell centres) and with the analytic Cartesian metric.

#### E. Kerr a = 0.9 on the mesh (inclined orbit in Cartesian KS, dt = 0.01 M, t = 600 M)

| run | pusher | metric | dx/M | max dE/E | max dLz/Lz | max dQ/Q | final pos err | max pos err (checkpoints every 50 M) | reconstruction err alpha / beta / gamma | unconv / max it |
|---|---|---|---|---|---|---|---|---|---|---|
| inc_bsym_cks | Boris sym | analytic Cart. KS | - | 5.239e-10 | 5.844e-11 | 1.928e-09 | 3.367e-06 | 3.674e-06 | - | 0 / 5 |
| inc_bsym_lat_dx0.5 | Boris sym | lattice | 0.5 | 8.937e-06 | 8.651e-05 | 4.318e-04 | 3.172e-03 | 8.758e-03 | - | 0 / 5 |
| inc_bsym_lat_dx0.25 | Boris sym | lattice | 0.25 | 7.942e-07 | 8.140e-06 | 6.106e-05 | 4.634e-04 | 7.102e-04 | - | 0 / 5 |
| inc_bsym_lat_dx0.125 | Boris sym | lattice | 0.125 | 9.411e-08 | 1.215e-06 | 1.076e-05 | 5.757e-05 | 1.118e-04 | - | 0 / 5 |
| inc_bsym_mesh_dx0.5 | Boris sym | mesh | 0.5 | 8.937e-06 | 8.651e-05 | 4.318e-04 | 3.172e-03 | 8.758e-03 | 2.5e-06 / 1.1e-05 / 2.1e-05 | 0 / 5 |
| inc_bsym_mesh_dx0.25 | Boris sym | mesh | 0.25 | 7.942e-07 | 8.140e-06 | 6.106e-05 | 4.634e-04 | 7.102e-04 | 2.9e-07 / 1.3e-06 / 2.6e-06 | 0 / 5 |
| inc_bsym_mesh_dx0.125 | Boris sym | mesh | 0.125 | 9.411e-08 | 1.215e-06 | 1.076e-05 | 5.757e-05 | 1.118e-04 | 3.4e-08 / 1.6e-07 / 3.2e-07 | 0 / 5 |
| inc_mid_cks | midpoint | analytic Cart. KS | - | 5.227e-10 | 1.531e-14 | 2.287e-09 | 3.353e-06 | 3.660e-06 | - | 0 / 5 |
| inc_mid_lat_dx0.5 | midpoint | lattice | 0.5 | 8.937e-06 | 8.652e-05 | 4.318e-04 | 3.171e-03 | 8.758e-03 | - | 0 / 5 |
| inc_mid_lat_dx0.25 | midpoint | lattice | 0.25 | 7.952e-07 | 8.145e-06 | 6.106e-05 | 4.633e-04 | 7.101e-04 | - | 0 / 5 |
| inc_mid_lat_dx0.125 | midpoint | lattice | 0.125 | 9.371e-08 | 1.217e-06 | 1.077e-05 | 5.741e-05 | 1.118e-04 | - | 0 / 5 |
| inc_mid_mesh_dx0.5 | midpoint | mesh | 0.5 | 8.937e-06 | 8.652e-05 | 4.318e-04 | 3.171e-03 | 8.758e-03 | 2.5e-06 / 1.1e-05 / 2.1e-05 | 0 / 5 |
| inc_mid_mesh_dx0.25 | midpoint | mesh | 0.25 | 7.952e-07 | 8.145e-06 | 6.106e-05 | 4.633e-04 | 7.101e-04 | 2.9e-07 / 1.3e-06 / 2.6e-06 | 0 / 5 |
| inc_mid_mesh_dx0.125 | midpoint | mesh | 0.125 | 9.371e-08 | 1.217e-06 | 1.077e-05 | 5.741e-05 | 1.118e-04 | 3.4e-08 / 1.6e-07 / 3.2e-07 | 0 / 5 |

| series | final err (ascending dx) | fitted order | pairwise | order dE | order dQ |
|---|---|---|---|---|---|
| mid_mesh | 5.741e-05, 4.633e-04, 3.171e-03 | 2.89 | 3.01, 2.77 | 3.29 | 2.66 |
| mid_lat | 5.741e-05, 4.633e-04, 3.171e-03 | 2.89 | 3.01, 2.77 | 3.29 | 2.66 |
| bsym_mesh | 5.757e-05, 4.634e-04, 3.172e-03 | 2.89 | 3.01, 2.77 | 3.28 | 2.66 |
| bsym_lat | 5.757e-05, 4.634e-04, 3.172e-03 | 2.89 | 3.01, 2.77 | 3.28 | 2.66 |

| mesh run | max \|x_mesh - x_lattice\| | max \|u_mesh - u_lattice\| | bitwise identical |
|---|---|---|---|
| kerr_mesh/inc_bsym_mesh_dx0.125 | 1.958e-10 | 1.281e-11 | False |
| kerr_mesh/inc_bsym_mesh_dx0.25 | 5.531e-11 | 3.348e-12 | False |
| kerr_mesh/inc_bsym_mesh_dx0.5 | 5.707e-11 | 3.059e-12 | False |
| kerr_mesh/inc_mid_mesh_dx0.125 | 4.285e-12 | 2.509e-13 | False |
| kerr_mesh/inc_mid_mesh_dx0.25 | 6.004e-12 | 3.496e-13 | False |
| kerr_mesh/inc_mid_mesh_dx0.5 | 9.448e-13 | 4.743e-14 | False |

The mesh runs agree with the lattice runs to <= 2e-10 in position (not bitwise: the mesh path
computes the stencil from block-local indices), which verifies the full in-code path (metric
filled by the problem generator into the `<adm>` arrays including ghost cells, copy into the
particle metric array, MeshBlock ownership and reassignment, Hermite reconstruction on the
mesh) for a spinning black hole. The errors converge at third order in dx (final position
2.9, energy 3.3, Carter constant 2.7); the reconstructed lapse at the particle has errors
2.5e-6, 2.9e-7, 3.4e-8 (third order, as expected for Catmull-Rom values). At dx = 0.125 M the
position error (5.7e-5) is still 17 times the time-step error of the analytic run (3.4e-6).


## Failures, disagreements and anomalies

1. **Interpretation of the passage's grid error (disagreement with the paper's text, not with
   its numbers).** The paper states that the accuracy of both pushers on the Hermite grid "is
   limited by the interpolation error of the spacetime". For the final-position error at
   dt = 0.01 M we find the opposite: it is dominated by the time-step error in Cartesian
   coordinates (analytic Cartesian KS without interpolation: 1.73e-2 against 1.59e-2 on the
   lattice, both proportional to dt^2), while the interpolation alone shifts the final position
   by 5e-5 to 2.3e-3. The interpolation dominates the invariant errors (Q: 40x, E: 3.5x the
   Cartesian analytic values at dt = 0.01). All of the paper's numbers are reproduced.
2. **Triad gauge not stated in the paper.** The paper's analytic-input Boris errors
   (9.0e-8, 1.1e-8, 7.8e-7) are reproduced with the symmetric triad, its Hermite-grid Boris
   errors (2.0e-6, 3.8e-6, 5.3e-5) with the Cholesky triad. With the other gauge the numbers
   differ (table C1: Cholesky/analytic 6.2e-8, 7.2e-8, 6.6e-7; symmetric/lattice 3.2e-6, 6.3e-6,
   4.9e-5).
3. **No convergence order for the circular orbit in spherical KS**: the motion is exactly
   linear in (t, phi) there and both pushers integrate it without truncation error; the
   measured errors are round-off (1e-11 to 3e-10). Second order is shown in Cartesian KS.
4. **Irregular dx order for the eccentric Schwarzschild orbit on the mesh**: pairwise 4.44 and
   1.91 for the final-position error (fitted 3.17); the error oscillates along the orbit and the
   final value is a snapshot. Max over checkpoints: 2.58; energy error: 2.95.
5. **CPU and GPU are not bitwise identical** (expected: different compilers and FMA contraction).
   Differences are 1.4e-14 for the midpoint with analytic input, but grow to 1.8e-8 (position)
   for Boris on the lattice because the near-separatrix passage amplifies round-off. The
   implicit iteration count differs in 1 and 28 of 23002 steps.
6. **Latent tolerance issue, not triggered.** `tolerance = 2e-14` is absolute and is smaller than
   the spacing of doubles for |x| >= 128 (phi of the BL orbits reaches 174). The fixed-point
   iteration nevertheless converged (to exact fixed points) in every step of every run: zero
   unconverged steps in all 176 runs; the largest iteration count was 11 (plunge, dt = 0.08 M).
7. **No crashes, no NaN, no particle lost**: all runs terminated on the time limit with one
   particle left; the mesh runs never lost the particle across MeshBlock boundaries.
8. **Procedure.** The GPU runs were executed in batches inside single Slurm allocations (see
   Setup), not with one `srun` per run, because the shared GPUs made every new allocation wait;
   each run still went through `scripts/gpu_run.sh` with the documented command line. Batch 1
   reached its 45-minute budget before the 15 Cartesian plunge runs, which ran in batch 2.
9. **Source drift.** `athenak/src/particles/nrpic.cpp`, `nrpic_io.cpp` and `particles.hpp` were
   modified by the lead after the CPU executable was built (and `nrpic.cpp`/`particles.hpp`
   after the GPU executable); the pusher kernels and metric functors predate both builds. The
   GPU executable's checksum did not change during the campaign.
10. Performance note: a single-particle run costs about 100 us per cycle on the GPU
    (kernel-launch and host-transfer latency, history and trajectory written every cycle) and
    18 us per cycle on the serial CPU build.

## Figures

Paper figures (vector PDF, `python/nrpic/figstyle.py`, 8 in wide; a PNG copy of each is in
`analysis/geodesic/figs/`):

| file | script | content |
|---|---|---|
| `paper/figures/fig_bl_trajectories.pdf` | `analysis/geodesic/fig_bl_trajectories.py` | Left: equatorial-eccentric BL orbit (20 T_r) in the x-y plane; right: inclined orbit (18 T_r) in 3D; Boris, symmetric triad, dt = 0.01 M (yellow); event horizon black, equatorial ergosphere grey, initial points blue |
| `paper/figures/fig_ks_passage.pdf` | `analysis/geodesic/fig_ks_passage.py` | Top left: r(t); top middle: r < 4M segment in Cartesian KS with the horizon; top right: final-position error vs dt (spherical KS solid, Cartesian KS dashed, Hermite lattice dotted) with a dt^2 guide; bottom: dE/E, dL_z/L_z, dQ/Q vs t at dt = 0.01 M; grey lines: pericentre |
| `paper/figures/fig_schwarzschild_convergence.pdf` | `analysis/geodesic/fig_schwarzschild_convergence.py` | Top: final-position error vs dt for the circular, eccentric and plunging orbits (both pushers, spherical and Cartesian KS); bottom: mesh metric, final-position error vs dx (circular, eccentric; lattice as open markers, analytic Cartesian KS at the same dt dashed) and max dE/E vs dx |

Diagnostic figures (PDF + PNG in `analysis/geodesic/figs/`, one script each):

| file | script | content |
|---|---|---|
| `diag_schw_dt` | `diag_schw_dt.py` | per Schwarzschild orbit: trajectory, position error x (0.01M/dt)^2 for five dt (collapse = second order), position error and dE/E at dt = 0.01 M for all pusher/metric combinations |
| `diag_schw_mesh` | `diag_schw_mesh.py` | circular and eccentric orbits on the mesh: trajectory with MeshBlock boundaries, position error, dE/E and reconstructed-lapse error vs t for three dx |
| `diag_kerr_bl` | `diag_kerr_bl.py` | BL orbits: trajectories, position error against the reference trajectory, dE/E, dL_z/L_z or dQ/Q vs t for both dt and all pushers |
| `diag_kerr_passage` | `diag_kerr_passage.py` | passage: trajectory, position error vs t, final error vs dt, dE/E and dQ/Q vs t, max dE/E vs dt for all nine pusher/metric combinations |
| `diag_cpu_gpu` | `diag_cpu_gpu.py` | CPU and GPU trajectories near pericentre, max CPU-GPU difference vs t, dE/E of both |
| `diag_kerr_mesh` | `diag_kerr_mesh.py` | Kerr orbit on the mesh: trajectory (x-y, x-z) with MeshBlocks, final error vs dx, position error, dE/E and lapse reconstruction error vs t |

## Data and scripts

* `analysis/geodesic/run_campaign.py` - run definitions and launcher (`list`, `run`, `batch`).
* `analysis/geodesic/make_schwarzschild_reference.py` - Schwarzschild orbit design and exact
  solutions -> `problems/schwarzschild/ref/orbits.json`.
* `analysis/geodesic/analyze_kerr.py`, `analyze_schwarzschild.py` - error analysis ->
  `problems/kerr/results/{kerr_summary.json, kerr_histories.npz, ks_passage_histories.npz,
  ks_passage_convergence.json, bl_trajectories.npz, kerr_exact_extra.json}` and
  `problems/schwarzschild/results/{schw_summary.json, schw_convergence.json,
  schw_histories.npz}` (3.7 MB in total). The summaries hold, per run, the full override
  list, log file, run time, iteration statistics and every number of the tables.
* `analysis/geodesic/make_tables.py` - prints all tables of this document.
* `analysis/geodesic/geo_common.py` (paths, readers, error measures),
  `analysis/geodesic/geo_style.py` (colour and line-style mapping).
* New inputs: `problems/schwarzschild/geodesic.athinput`,
  `problems/schwarzschild/geodesic_mesh.athinput`, `problems/kerr/geodesic_mesh.athinput`.

To regenerate everything from the result files (no reruns):

```
python3 analysis/geodesic/fig_bl_trajectories.py
python3 analysis/geodesic/fig_ks_passage.py
python3 analysis/geodesic/fig_schwarzschild_convergence.py
for s in diag_schw_dt diag_schw_mesh diag_kerr_bl diag_kerr_passage diag_cpu_gpu diag_kerr_mesh; do
  python3 analysis/geodesic/$s.py; done
python3 analysis/geodesic/make_tables.py
```

To rerun: `python3 analysis/geodesic/make_schwarzschild_reference.py` (2.5 min), then
`python3 analysis/geodesic/run_campaign.py batch '<pattern>'` (GPU) and
`python3 analysis/geodesic/run_campaign.py run 'kerr_passage_cpu/*'` (CPU), then the two
analysis scripts (about 1 min each).
