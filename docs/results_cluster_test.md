# Test-particle cluster in a fixed black hole spacetime

Validation of the particle module with clusters of 10^2, 10^3 and 10^4 massive test
particles in a fixed Schwarzschild (a = 0) or Kerr (a = 0.9 M) black hole spacetime:
(i) analytic Cartesian Kerr-Schild metric, (ii) the same metric stored on a statically
refined mesh and reconstructed at the particles (cubic Hermite), with the stress-energy
deposited on the mesh (cloud-in-cell, binomial filter) but not fed back. All numbers below
are as measured on 2026-11-13 (GPU: one A100 per job). Units G = c = M = 1.

Scripts: `problems/cluster_test/` (initial data, inputs, `run_campaign.sh`),
`analysis/cluster_test/` (`make_all.sh` regenerates every figure and
`analysis/cluster_test/results/*.json`), runs in `runs/cluster_test/<name>/`.

## 1. Setup

### Initial data (`problems/cluster_test/make_cluster.py`)

1. Centre-of-mass orbit: equatorial geodesic (Q = 0) with a radial turning point at
   Kerr-Schild (= Boyer-Lindquist) radius r_0 = 10 M, prograde, L = f_L L_circ(r_0); E from
   R(r_0) = 0 (larger root). f_L = 1 is the exact circular orbit (Bardeen-Press-Teukolsky):
   E = 0.9561828875, L = 3.7796447301 (a = 0); E = 0.9522402386, L = 3.4572992962
   (a = 0.9). The BL state (u_r = 0, u_theta = 0, u_phi = L) is converted BL -> Cartesian KS
   with `nrpic.kerr.convert_state` and rotated about z (an isometry) so that the centre is
   at x_c = (sqrt(r_0^2 + a^2), 0, 0). Check: E and L of the converted state agree with the
   formulas to 4e-16.
2. Positions: x_p = x_c + sigma_x eta_p, eta_p ~ N(0,1)^3 in the Cartesian KS coordinates,
   sigma_x = 0.5 M.
3. Momenta: orthonormal frame of the normal observers with the symmetric triad,
   e^i_(a) = (gamma^{-1/2})^{ia} (symmetric positive square root of gamma_ij, by
   eigen-decomposition). The frame components of the centre's spatial four-velocity,
   uhat_c = gamma^{-1/2}(x_c) u^c, are carried unchanged to each particle and an isotropic
   Gaussian is added: uhat_p = uhat_c + sigma_v xi_p, xi_p ~ N(0,1)^3, sigma_v = 0.02;
   u_i(p) = gamma^{1/2}(x_p) uhat_p. (sigma_v is a dispersion of W v measured by the local
   normal observer; for these speeds that is the 3-velocity dispersion to a factor W ~ 1.06.)
4. Masses: m_p = 1e-6 M / N.
5. Each particle is classified with its exact invariants and the radial potential
   R(r) = [E(r^2+a^2) - aL]^2 - Delta[r^2 + (L - aE)^2 + Q]: plunging if the allowed region
   containing its radius reaches r_+, escaping if it reaches infinity, else bound.

Families (`make_campaign_ic.py`, files in `runs/cluster_test/ic/`):

| family | centre | sigma_x, sigma_v | N (seeds) | exact classification |
|---|---|---|---|---|
| bound | circular, r_0 = 10 M | 0.5 M, 0.02 | 1e2, 1e3, 1e4, independent draws | all bound (see below) |
| plunging, a = 0 | f_L = 0.96: E = 0.95149, L = 3.62846, apocentre 10 M, pericentre 7.33 M | 0.5 M, 0.02 | 1e4 | 3727 plunge, 6273 bound |
| plunging, a = 0.9 | f_L = 0.72: E = 0.92609, L = 2.48926, apocentre 10 M, pericentre 2.52 M | 0.5 M, 0.02 | 1e4 | 3339 plunge, 6661 bound |

**Finding about the requested nominal cluster.** With r_0 = 10 M, sigma_x = 0.5 M,
sigma_v = 0.02 about 20 % of a Schwarzschild cluster is on plunging orbits (the low-L tail:
particles displaced inward keep the centre's velocity; the spread is sigma_L ~ 0.28 against
a margin L_circ - L_sep ~ 0.3). For the bound family the Gaussian is therefore conditioned
on bound orbits by rejection: 24 of 100, 231 of 1000 and 2404 of 10^4 Schwarzschild draws
were redrawn; for a = 0.9 none, none and 2 of 10^4. The bound family is also not compact
in energy: E ranges 0.947-0.995 (a = 0) and 0.922-0.986 (a = 0.9). In the analytic runs
(N = 10^4) r stays between 4.95 and 118.9 M (a = 0) and 2.57 and 61.5 M (a = 0.9); the
largest radius reached exceeds 24 M (edge of the dx = 0.25 M region) for 5.7 % and 1.6 % of
the particles, 36 M for 1.0 % and 0.18 %, and 64 M for 9 particles (a = 0) and none.

### Mesh (`problems/cluster_test/cluster_mesh.athinput`)

[-64, 64]^3, 16^3 MeshBlocks, 6 levels, 1128 MeshBlocks, 4.62e6 cells, nghost = 2:

| level | dx [M] | region (after AthenaK's expansion to parent blocks) |
|---|---|---|
| 0 | 2 | rest |
| 1 | 1 | [-64,64]^2 x [-32,32] |
| 2 | 0.5 | [-32,32]^2 x [-16,16] |
| 3 | 0.25 | [-24,24]^2 x [-8,8] (cluster) |
| 4 | 0.125 | [-4,4]^3 |
| 5 | 0.0625 | [-2,2]^3 (black hole, excision) |

Particles: `metric = mesh` (Cartesian KS on the mesh via `<adm>`, `pgen nrpic_geodesic`),
`deposit = true`, `nfilter = 2`, `deposit_max_level` default (finest), `alpha_exc = 0.62`
(equatorial lapse (1 + 2M/r)^{-1/2} = 0.62 at r = 1.25 M, inside r_+ = 2 M and 1.436 M; the
equatorial horizon lapse is 0.707 (a = 0) and 0.6465 (a = 0.9)). Outputs: history every
cycle, snapshots every 5 M (1 M for the plunging runs), trajectories of 16 particles every
10 cycles, `tmunu_E` z = 0.01 slice every 25 M, 3D `tmunu_E` every 50 M, 3D `tmunu_S{x,y,z}`
every 200 M (single precision). The analytic runs (`cluster_analytic.athinput`) use a dummy
8^3 mesh, `metric = kerr_schild`, no deposit; since particles are independent there, the
three bound clusters of one spin are run together (species 0, 1, 2 = N 1e2, 1e3, 1e4).

Time step dt = 0.05 M (20000 cycles for 1000 M), fixed-point tolerance 1e-12 (absolute,
on x^i and u_i), max_iterations = 100. Maximum iterations used: 5-6 (bound), 8 (plunging);
no unconverged push in any run. Duration: 1000 M = 5.03 (a = 0) and 4.89 (a = 0.9) orbital
periods of the centre (T = 2 pi (r_0^{3/2} + a) = 198.7 M, 204.3 M); plunging runs 500 M.
Executable `.work/build_gpu_v2/src/athena`, md5 e862a307dfbe6e1a1ea2b538e7033821 (built
04:14, 27-column history) for every run.

### Runs

All through `scripts/gpu_run.sh` with `ATHENA_EXE=.work/build_gpu_v2/src/athena TIME=00:20:00
JOB_NAME=tpc`, input `cluster_mesh.athinput` (mesh, plunge, thr) or `cluster_analytic.athinput`
(ana), plus `particles/particle_file=runs/cluster_test/ic/<file>` and the overrides below,
and `-t 00:18:00`. Exact command lines: header of each `runs/cluster_test/<name>/athena.log`
and `problems/cluster_test/run_campaign.sh`.

| run | particle file | overrides | job | wall [s] |
|---|---|---|---|---|
| mesh_a0.9_n10000_mid | bound_a0.9_n10000 | `particles/bh_spin=0.9` | 4103 | 696 |
| mesh_a0.9_n10000_boris | bound_a0.9_n10000 | `bh_spin=0.9 pusher=boris` | 4118 | 695 |
| mesh_a0.9_n1000_mid / n100_mid | bound_a0.9_n1000 / n100 | `bh_spin=0.9` | 4122 / 4123 | 667 / 642 |
| mesh_a0.0_n10000_mid / _boris | bound_a0.0_n10000 | `bh_spin=0.0` (`pusher=boris`) | 4114 / 4119 | 695 / 697 |
| mesh_a0.0_n1000_mid / n100_mid | bound_a0.0_n1000 / n100 | `bh_spin=0.0` | 4124 / 4125 | 666 / 642 |
| ana_a0.9_mid / _boris / _bchol | bound_a0.9_all | `bh_spin=0.9` (`pusher=boris`, `triad=cholesky`) | 4113 / 4120 / 4126 | 2.0 / 4.5 / 2.6 |
| ana_a0.0_mid / _boris / _bchol | bound_a0.0_all | `bh_spin=0.0` (same) | 4115 / 4121 / 4127 | 1.9 / 4.4 / 2.5 |
| plunge_a0.0_mid / _boris | plunge_a0.0_n10000 | `bh_spin=0.0 snap_dt=1.0 time/tlim=500` (`pusher=boris`) | 4116 / 4128 | 337 / 338 |
| plunge_a0.9_mid / _boris | plunge_a0.9_n10000 | `bh_spin=0.9 snap_dt=1.0 time/tlim=500` (`pusher=boris`) | 4117 / 4129 | 338 / 339 |
| mesh_a0.9_n10000_mid_dx2 | bound_a0.9_n10000 | `bh_spin=0.9 mesh/nx{1,2,3}=32 meshblock/nx{1,2,3}=8` (identical block layout, every dx doubled) | 4147 | 493 |
| thr_a0.9_prod / _nf0 | bound_a0.9_n10000 | `time/tlim=50 output{1..5}/dt=1e9 snap_dt=-1 traj_dcycle=0` (`nfilter=0`) | 4157 / 4158 | 33.1 / 7.2 |
| thr_a0.9_nodep | bound_a0.9_n10000 | as thr + `deposit=false` | 4159 | crashed, section 4 item 5 |

(`bh_spin` etc. are `particles/...`.) All runs ended with "Terminating on time limit" and
exit 0 except thr_a0.9_nodep.

## 2. Results

### (a) Per-particle conservation of E, L_z, Q (exact metric, every snapshot)

Relative errors |X(t)/X(0) - 1| at t = 1000 M over the N = 10^4 cluster: median / 99th
percentile / maximum over all snapshots. Q is near zero for near-equatorial particles
(Q_0 down to 2e-6), so |dQ|/K with the Carter constant K = Q + (L_z - aE)^2 is also given.

| a | run | dE/E | dL_z/L_z | dQ/Q | dQ/K |
|---|---|---|---|---|---|
| 0 | analytic, midpoint | 1.5e-8 / 1.3e-7 / 5.6e-7 | 4.6e-14 / 2.7e-12 / 8.6e-12 | 9.3e-14 / 5.4e-12 / 1.7e-11 | 3.4e-16 / 3.9e-14 / 3.7e-13 |
| 0 | analytic, Boris (symmetric) | 1.5e-8 / 1.5e-7 / 6.2e-7 | 1.6e-12 / 2.0e-12 / 4.6e-12 | 3.2e-12 / 4.2e-12 / 2.6e-11 | 1.1e-14 / 1.2e-13 / 3.0e-13 |
| 0 | analytic, Boris (Cholesky) | 1.6e-8 / 1.5e-7 / 5.2e-7 | 3.5e-8 / 7.8e-7 / 2.0e-6 | 8.7e-8 / 1.8e-6 / 5.9e-6 | 3.0e-10 / 1.3e-8 / 8.6e-8 |
| 0 | mesh, midpoint | 1.3e-7 / 2.8e-6 / 2.7e-5 | 5.4e-6 / 4.7e-5 / 1.2e-4 | 1.2e-4 / 1.5e-3 / 1.2e-2 | 3.6e-7 / 7.4e-6 / 6.1e-5 |
| 0 | mesh, Boris | 1.3e-7 / 2.7e-6 / 2.4e-5 | 5.4e-6 / 4.7e-5 / 1.2e-4 | 1.2e-4 / 1.4e-3 / 1.2e-2 | 3.6e-7 / 7.4e-6 / 6.1e-5 |
| 0.9 | analytic, midpoint | 8.1e-9 / 2.3e-7 / 4.7e-6 | 4.9e-14 / 5.2e-12 / 1.0e-11 | 9.3e-9 / 1.7e-7 / 7.2e-6 | 6.0e-11 / 2.7e-9 / 1.7e-7 |
| 0.9 | analytic, Boris (symmetric) | 9.7e-9 / 4.8e-7 / 9.5e-6 | 4.6e-10 / 6.1e-8 / 2.3e-6 | 8.0e-9 / 1.4e-7 / 6.1e-6 | 5.1e-11 / 2.3e-9 / 1.4e-7 |
| 0.9 | analytic, Boris (Cholesky) | 1.1e-8 / 3.1e-7 / 2.2e-5 | 5.1e-8 / 2.3e-6 / 5.2e-5 | 6.4e-8 / 2.4e-6 / 4.5e-5 | 4.5e-10 / 3.4e-8 / 1.1e-6 |
| 0.9 | mesh, midpoint | 1.2e-7 / 2.2e-5 / 1.3e-4 | 5.3e-6 / 1.1e-4 / 5.6e-4 | 1.1e-4 / 2.4e-3 / 3.7e-2 | 6.6e-7 / 2.8e-5 / 2.4e-4 |
| 0.9 | mesh, Boris | 1.3e-7 / 2.2e-5 / 1.3e-4 | 5.3e-6 / 1.1e-4 / 5.6e-4 | 1.1e-4 / 2.4e-3 / 3.7e-2 | 6.6e-7 / 2.8e-5 / 2.4e-4 |

N = 10^2 and 10^3 (mesh, midpoint): dE/E medians 1.2-1.4e-7, dL_z/L_z medians 5.3-8.1e-6,
the same as N = 10^4 (errors are per particle). Analytic species 0 and 1 likewise
(results/invariants.json).

- Analytic metric: the implicit midpoint pusher conserves L_z to round-off (1e-11 at most;
  it is a quadratic invariant, which the implicit midpoint rule preserves), and for a = 0
  also Q (= L^2 - L_z^2). E errors are bounded and oscillate (no drift over 5 orbits).
  The Boris pusher in the symmetric gauge has the same E errors, L_z to 1e-12 (a = 0) and
  4.6e-10 median (a = 0.9); the Cholesky gauge is 2-3 orders worse in L_z and Q.
- Mesh metric: errors are 9x (a = 0) and 15x (a = 0.9) larger in E (median) and about
  1e8x larger in L_z; they are
  identical for both pushers (the reconstruction error of the metric dominates). The E
  error is present from the first snapshot (5 M) and does not grow (median flat at
  1.2e-7): it is the difference between the reconstructed and the exact Hamiltonian along
  the orbit. L_z and Q errors grow slowly in the first orbit and then level off.
- The tail is set by the pericentre: at t = 1000 M, dE/E median / p99 is 2.4e-6 / 8.0e-5 for
  the 757 Kerr particles with r_min < 6 M and 1.1e-7 / 7.7e-7 for the other 9243
  (Schwarzschild: 1.2e-6 / 1.4e-5 for 335 particles, 1.3e-7 / 1.1e-6 for the rest).
  Binned in r_min (figs/mesh_resolution), the median error jumps by about 20x for r_min
  below 4-5 M (Kerr near-separatrix orbits whirling at 3-4 M).
- Mesh resolution (extra run with every dx doubled, same block layout, a = 0.9, N = 10^4):
  median dE/E 9.6e-7 vs 1.24e-7, dL_z/L_z 3.0e-5 vs 5.3e-6. Per-particle convergence order
  (median of log2 of the error ratio): 2.96 for E, 2.54 for L_z; binned medians give
  2.6-3.0 for r_min > 4 M and 4.1-4.4 for r_min < 4 M (E). The mesh-metric error converges
  at about third order.

### (b) Phase mixing

Order parameter |<exp(i phi)>| of the N = 10^4 cluster (mesh, midpoint): 0.98 (50 M), 0.82
/ 0.73 (100 M, a = 0 / 0.9), 0.26 / 0.16 (200 M), 0.071 / 0.085 (500 M), 0.0077 / 0.023
(1000 M); a uniform ring of 10^4 particles would give 0.0089. The cluster becomes an arc by
50-100 M, a trailing spiral by 200 M, wound rings by 500 M and an azimuthally mixed ring
by 1000 M (radially still banded for a = 0.9). The vertical spread grows from z_rms = 0.49 M
to 0.64-0.70 M within the first orbit and then oscillates (vertical epicycles; for
a = 0.9 the orbital planes precess). The deposited energy density follows the particles.
All four runs per spin (analytic and mesh, both pushers) give the same order parameter and
z_rms to plotting accuracy. Same particles compared one by one: mesh minus analytic
positions after 1000 M have median 4.4e-3 M (a = 0) and 3.2e-3 M (a = 0.9), 99th percentile
0.28 M and 0.079 M; analytic Boris minus analytic midpoint 7.5e-6 M and 4.6e-6 M (99th
percentile 1.3e-3 M and 6.4e-4 M).

### (c) Conservation of the deposited fields

History columns: int E sqrt(gamma) dV before (col 9) and after (col 24) the filter versus
sum m W, the same for S_i versus sum m u_i, every cycle. Relative to sum m W:

| run | before filter, E: max | before filter, S_i: max | after filter, E: at t = 0 / median / max | after filter, S_i: max |
|---|---|---|---|---|
| mesh_a0.9_n10000 (mid, Boris) | 1.0e-15 | 2.0e-16 | -2.25e-6 / -6.7e-5 / 9.0e-4 | 4.1e-4 |
| mesh_a0.9_n1000 | 1.0e-15 | 2.0e-16 | -2.25e-6 / -5.7e-5 / 1.9e-3 | 1.2e-3 |
| mesh_a0.9_n100 | 1.0e-15 | 2.0e-16 | -2.17e-6 / -3.2e-6 / 6.4e-3 | 4.1e-3 |
| plunge_a0.9_mid | 1.1e-15 | 2.0e-16 | -2.23e-6 / -9.6e-5 / 7.3e-3 | 3.1e-3 |
| mesh_a0.0_n10000 (mid, Boris) | 4.6e-5 (1.0e-15 away from the boundary) | 7.2e-6 | -2.14e-6 / -2.2e-6 / 5.5e-4 | 1.7e-4 |
| mesh_a0.0_n1000 | 1.0e-15 | 1.9e-16 | -2.15e-6 / -1.8e-5 / 1.9e-3 | 6.2e-4 |
| mesh_a0.0_n100 | 1.0e-15 | 1.9e-16 | -2.20e-6 / -2.5e-6 / 6.6e-3 | 4.7e-3 |
| plunge_a0.0_mid | 7.2e-5 (1.1e-15 away from the boundary) | 7.6e-6 | -2.23e-6 / -3.3e-5 / 2.1e-3 | 1.4e-3 |

- Before the filter the identity holds to round-off through refinement-level crossings
  (2716 and 6274 level changes between 5 M snapshots for the N = 10^4 bound runs, 15846
  and 120800 between 1 M snapshots for the plunging runs) and through 3726 and 3345
  excisions, with one exception: while a particle is within half a cell of the outer
  boundary (beyond the outermost cell centre, |x_i| > 63.5 M on level 1), the part of its
  cloud outside the domain is dropped. This
  happened in the a = 0 runs for the 4 (bound) and 1 (plunging) particles that left the
  mesh, in 2540 and 141 cycles. The weight outside the domain computed from the snapshots
  equals the history residual to 5e-15 and 1.1e-14 at every snapshot; at snapshots
  without such a particle the residual is at most 1.1e-15.
- After the filter the integrals move away from the particle sums: -2.2e-6 at t = 0 in
  every run (the cluster sits inside one level; the filter acts on E, not on E sqrt(gamma),
  and sqrt(gamma) varies across the filter stencil), and up to 1e-4-1e-3 as soon as
  particles reach refinement boundaries (from t ~ 40 M): 5.5e-4 / 9.0e-4 for N = 10^4,
  1.9e-3 for 10^3, 6.4-6.6e-3 for 10^2 (one particle is 1 % of the mass), 2.1e-3 / 7.3e-3
  for the plunging runs (particles crossing levels 3-5 near the black hole). The filter
  across levels is therefore not conservative at the 1e-3 level per particle at a level
  boundary.
- The filtered integrals recomputed from the single-precision 3D dumps with the exact
  sqrt(gamma) agree with the history columns to at most 2.7e-9.
- Rest-mass bookkeeping: sum m + excised + escaped equals the initial mass to 1e-14.

### (d) Convergence of the deposited density with N

d_N = ||E_N - E_{10^4}||_2 / ||E_{10^4}||_2 over all leaf cells, weight sqrt(gamma) dV,
nfilter = 2 in all runs, 3D dumps every 50 M. Because the three clusters are independent
draws, the three pairwise differences give the sampling noise s_N of each run
(d_ij^2 = s_i^2 + s_j^2).

| a | t | d_100 | d_1000 | exponent (raw) | s_100, s_1000, s_10000 | exponent from s (1e2-1e3) |
|---|---|---|---|---|---|---|
| 0 | 500 M | 2.89 | 0.955 | -0.481 | 2.88, 0.92, 0.24 | -0.493 |
| 0.9 | 500 M | 2.77 | 0.932 | -0.472 | 2.75, 0.89, 0.28 | -0.490 |
| 0 | 17 dumps, 200-1000 M | | | -0.480 +- 0.007 | | -0.508 +- 0.016 |
| 0.9 | 17 dumps, 200-1000 M | | | -0.479 +- 0.012 | | -0.496 +- 0.015 |

The density converges as N^{-1/2} (sampling noise); the raw exponent is shallower only
because the N = 10^4 reference carries its own noise. At these N the fields are noise
dominated: even the N = 10^4 field has a relative L2 noise of 0.24-0.28 on this mesh
(at 500 M the 10^4 particles occupy about 9000 cells of dx = 0.25 M, 1.1 particles per
occupied cell, 90 % of them holding a single particle; two filter passes). The
1e3-1e4 exponent from s is poorly determined (s_10000^2 is a small difference of large
numbers: -0.44 +- 0.14 and -0.59 +- 0.37).

### (e) Excision bookkeeping (plunging family, mesh, alpha_exc = 0.62)

| | a = 0, midpoint | a = 0, Boris | a = 0.9, midpoint | a = 0.9, Boris |
|---|---|---|---|---|
| excised (history) / rest mass | 3726 / 3.726e-7 | 3726 / 3.726e-7 | 3345 / 3.345e-7 | 3345 / 3.345e-7 |
| predicted plunging (exact invariants of the initial data) | 3727 | 3727 | 3339 | 3339 |
| predicted plunging and excised | 3726 | 3726 | 3339 | 3339 |
| predicted plunging, not excised | 1 | 1 | 0 | 0 |
| predicted bound, excised | 0 | 0 | 6 | 6 |
| left the mesh | 1 (predicted bound, E = 0.990) | 1 | 0 | 0 |
| first / last excision [M] | 40.90 / 337.95 | 40.90 / 338.00 | 40.75 / 407.85 | 40.75 / 403.45 |
| excised by t = 100 / 200 / 300 M (exact-geodesic prediction) | 1270 / 3548 / 3722 (1270 / 3548 / 3722) | same | 2966 / 3342 / 3342 (2967 / 3339 / 3339) | same |
| KS r at the last snapshot, min / median / max | 1.224 / 1.465 / 1.684 | 1.223 / 1.465 / 1.684 | 1.192 / 1.272 / 1.429 | 1.192 / 1.272 / 1.429 |
| exact lapse there, min / max | 0.616 / 0.676 | 0.616 / 0.676 | 0.619 / 0.646 | 0.619 / 0.646 |
| r at removal (exact geodesic continued from the last snapshot to alpha < 0.62), min / median / max | 1.223 / 1.237 / 1.249 | 1.223 / 1.237 / 1.249 | 1.145 / 1.246 / 1.249 | 1.145 / 1.246 / 1.249 |
| dE/E at the last snapshot, median / max | 9.0e-5 / 3.5e-4 | 1.2e-4 / 5.4e-4 | 9.6e-5 / 9.8e-4 | 8.5e-5 / 9.9e-4 |
| dL_z/L_z, median / max | 3.5e-5 / 1.9e-4 | 3.5e-5 / 1.9e-4 | 1.1e-4 / 1.0e-3 | 8.7e-5 / 1.1e-3 |
| dQ/Q, median / max | 9.0e-4 / 1.2e-2 | same | 2.7e-3 / 7.8e-2 | 2.7e-3 / 7.7e-2 |

- Exact-geodesic prediction (`predict_excision.py`, all predicted plungers integrated with
  the exact metric from t = 0): removals between 40.85 and 345.9 M (a = 0) and 40.7 and
  162.8 M (a = 0.9), at r 1.223-1.249 M (a = 0) and 1.145-1.249 M (a = 0.9). The measured
  counts follow it to the particle.
- Removal happens at r = 1.22-1.25 M (a = 0) and 1.15-1.25 M (a = 0.9), i.e. 0.61-0.62 r_+
  and 0.80-0.87 r_+, as designed. The radii at the last snapshot (1 M before removal at most)
  spread to 1.68 M (a = 0) because particles fall fast inside the horizon.
- Particles going deep accumulate errors of 1e-4 (E, L_z) and 1e-2 (Q) before removal
  (dx = 0.0625 M at r < 2 M); this is what changes the fate of marginal orbits:
  the a = 0 particle that was predicted to plunge (radial-potential minimum only 1.7e-3
  above zero, at r = 5.05 M) turned at r = 5.07 M after its L_z changed by 3e-5; the six
  a = 0.9 particles predicted bound had exact pericentres 1.82-1.85 M (barriers 5e-6 to
  2e-3) and errors of 1e-4-1e-3 at each deep passage; they plunged at 153-407 M.
- No particle was missed by the lapse criterion; the largest |cos theta| at the last
  snapshot was 0.26 (a = 0) and 0.35 (a = 0.9). In Kerr-Schild coordinates for a = 0.9 the
  lapse on the axis never drops below 0.688, so particles plunging far from the equator
  would not be excised by alpha_exc = 0.62; none did here.

### (f) Throughput (AthenaK "particle-updates/cpu_second", outputs included)

| run | N | ms per cycle | particle updates / s |
|---|---|---|---|
| analytic, midpoint (a = 0 / 0.9) | 11100 | 0.09 / 0.10 | 1.19e8 / 1.13e8 |
| analytic, Boris symmetric | 11100 | 0.22 / 0.22 | 5.10e7 / 4.96e7 |
| analytic, Boris Cholesky | 11100 | 0.12 / 0.13 | 9.05e7 / 8.66e7 |
| mesh, midpoint, N = 10^2 | 100 | 32.1 | 3.11e3 |
| mesh, midpoint, N = 10^3 | 1000 | 33.3 | 3.00e4 |
| mesh, midpoint, N = 10^4 | 10^4 | 34.8 | 2.88e5 |
| mesh, Boris, N = 10^4 | 10^4 | 34.8 | 2.87e5 / 2.88e5 |
| mesh, plunging, both pushers | 10^4 -> 6273 / 6655 | 33.7-33.9 | 2.12-2.13e5 |
| mesh, every dx doubled (8^3 blocks, 0.58e6 cells) | 10^4 | 24.7 | 4.06e5 |
| mesh, 1000 cycles, nfilter = 2 / nfilter = 0 | 10^4 | 33.1 / 7.2 | 3.02e5 / 1.39e6 |

The mesh runs cost 32-35 ms per cycle independently of N (10^2-10^4) and of the pusher;
the two filter passes account for about 26 of the 33 ms (the 1000-cycle timing runs include
the start and end data dumps, so 7.2 ms is an upper bound without filter). The pusher
itself takes 0.1-0.2 ms per cycle for 11100 particles. The quoted particle updates per
second of the mesh runs therefore measure the mesh work, not the pusher. Peak GPU memory
5.8 GB (production mesh), 2.1 GB (coarse mesh), 0.6 GB (analytic).

## 3. Figures (`analysis/cluster_test/figs/`, PDF and PNG)

- `invariants_time`: median (solid) and 99th percentile (dashed) of |dE/E|, |dL_z/L_z|,
  |dQ/Q| versus time for the N = 10^4 cluster, analytic and mesh metric, midpoint, Boris
  symmetric and (analytic) Boris Cholesky. Shows the 10x (E) and 1e8x (L_z) gap between
  mesh and analytic and that both pushers coincide on the mesh.
- `invariants_hist`: distributions of the same errors at t = 1000 M (log10). Separates the
  round-off peaks of the analytic midpoint runs from the mesh-error peaks.
- `mesh_resolution`: per-particle |dE/E| and |dL_z/L_z| at 1000 M versus the smallest radius
  reached, analytic, production mesh and every dx doubled (a = 0.9); binned medians. Shows
  the third-order convergence and the large errors for pericentres below about 4 M.
- `phase_mixing_a0.0`, `phase_mixing_a0.9`: particles in x-y (top) and cylindrical R-z
  (bottom) and the deposited E in the plane next to z = 0 (middle, log scale) at 0, 50,
  100, 200, 500, 1000 M (mesh, midpoint, N = 10^4). Arc, spiral, wound rings, ring.
- `phase_mixing_order`: order parameter, z_rms, and per-particle position differences to
  the analytic midpoint run, for all four N = 10^4 runs per spin.
- `deposit_conservation`: before- and after-filter residuals of the E and S_i integrals
  (maximum over 5 M bins), the 3D-dump check (markers), the weight outside the domain
  (crosses), and the rates of refinement-level changes and removals.
- `density_convergence`: d_N and the noise level s_N of each run versus time, d and s versus
  N at 500 M with N^{-1/2}, and the deposited E at 500 M for N = 10^2, 10^3, 10^4 (both
  spins).
- `excision`: excised number and rest mass versus time (both pushers) against the exact
  prediction; radius at the last snapshot and at removal; cumulative distributions of the
  invariant errors of the excised particles.
- `throughput`: particle updates per second and ms per cycle versus N for all runs, and the
  cycle cost with and without the filter.

## 4. Failures, anomalies, deviations

1. **Nominal cluster partly plunging (a = 0).** See section 1; the bound family is the
   Gaussian conditioned on bound orbits (19-24 % redrawn for a = 0, 2 of 10^4 for a = 0.9).
2. **Mesh-metric error.** Dominates everything for the mesh runs (both pushers identical);
   third-order convergent; large for orbits reaching r < 4 M (dE/E to 1.3e-4, dL_z/L_z to
   5.6e-4 for Kerr). It changed the fate of 7 marginal particles of the plunging family.
3. **Pre-filter identity broken at the outer boundary** by up to 4.6e-5 (bound, a = 0) and
   7.2e-5 (plunging, a = 0): cloud-in-cell weight beyond the domain is dropped for particles
   within half a cell of the boundary. Explained to 1e-14; not a deposition bug, but the
   identity holds only for particles at least half a cell inside the mesh.
4. **Filter not conservative across refinement levels**: post-filter integrals off by up to
   9e-4 (N = 10^4), 6.6e-3 (N = 10^2), 7.3e-3 (plunging a = 0.9); -2.2e-6 even on one
   level (filtering E rather than E sqrt(gamma)).
5. **Crash (input error of mine, plus a code issue).** thr_a0.9_nodep (`deposit = false`
   with `tmunu` outputs) segfaulted (exit 139) after "FATAL ERROR ... Output of Tmunu
   variable requested ... but no Tmunu object has been constructed": in
   `athenak/src/outputs/basetype_output.cpp` (around line 159) this check prints the error
   but, unlike its neighbours, does not exit. A no-output timing input
   (`cluster_mesh_timing.athinput`) was made, but the four re-run jobs (4183-4186) were
   cancelled unrun because they were queued to start 12 h later; the cost breakdown uses the
   nfilter = 0 run only.
6. **Input file edited by someone else during the campaign.** At 05:44 two lines
   (`filter_compensate = false`, `filter_comp_c = -1.0`, a new default-off option of the
   source) were added to `cluster_mesh.athinput`. The executable of the campaign predates
   the option and reported them as unused; runs from mesh_a0.9_n100_mid on read the edited
   file, with no effect. The copies of the input in the run directories (made at
   submission) do not contain these lines.
7. **Scheduling.** The first run used the blocking `gpu_run.sh` call. The queue then held
   about 7 h of production jobs, so the other runs were submitted with `gpu_run.sh`'s
   documented `BATCH=1` mode, each depending on the previous (`--dependency=afterany`), so
   that only one of my jobs ran at a time; every job had TIME=00:20:00 and JOB_NAME=tpc
   (`problems/cluster_test/run_campaign.sh`, `runs/cluster_test/campaign_chain.log`). One
   coarse-mesh job (4146, submitted with a wrong block layout) and the four timing jobs
   (4183-4186) were cancelled by me before they ran.
8. Throughput of the mesh runs is set by the filter, not the particles (section f).
