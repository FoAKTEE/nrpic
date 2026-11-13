# Test log

Acceptance checks for each milestone of `PLAN.md`, recorded as measured. Figures for each
entry are under `analysis/*/figs/`.

## Pusher kernels (standalone build of `nrpic_kernels.hpp`, 2026-11-13)

Kerr a = 0.9 M, Kerr-Schild e = 0.99 passage, dt = 0.01 M, t = 230 M, iteration tolerance
2e-14. Maximum relative errors of the invariants, evaluated with the exact metric.

| Pusher, metric input | E | L_z | Q | Published E, L_z, Q |
|---|---|---|---|---|
| midpoint, analytic spherical Kerr-Schild | 2.781e-8 | 0 | 1.254e-7 | 2.8e-8, round-off, 1.3e-7 |
| Boris, symmetric gauge, analytic spherical | 9.046e-8 | 1.136e-8 | 7.825e-7 | 9.0e-8, 1.1e-8, 7.8e-7 |
| Boris, Cholesky (r, theta, phi), analytic spherical | 6.204e-8 | 7.173e-8 | 6.561e-7 | (does not match) |
| midpoint, Cartesian lattice dx = 0.025 M | 2.162e-6 | 5.304e-6 | 5.060e-5 | 2.2e-6, 5.3e-6, 5.1e-5 |
| Boris, Cholesky (x, y, z), lattice | 2.046e-6 | 3.788e-6 | 5.289e-5 | 2.0e-6, 3.8e-6, 5.3e-5 |
| Boris, symmetric gauge, lattice | 3.194e-6 | 6.285e-6 | 4.890e-5 | (does not match) |

Pericentre r_p = 1.898325 M at t = 98.95 M (exact 1.898327 M at 98.948 M). The same
numbers are obtained through AthenaK on CPU (midpoint, analytic: 2.781e-8, 0, 1.254e-7).

## Mesh path (CPU, 2026-11-13)

Schwarzschild, Cartesian Kerr-Schild metric on a 96^3 mesh in 27 MeshBlocks, dx = 0.25 M,
circular orbit at r = 8 M, dt = 0.1 M, 300 M: r stays within [8.0000, 8.0012] M; relative
errors E 8.4e-7, L_z 5.1e-6; deposition identity |int E sqrt(gamma) dV / sum m W - 1| at
most 1.0e-15 over 3000 cycles.

## Deposition on refined meshes (GPU and CPU, 2026-11-13)

Flat spacetime, three refinement levels, 10^4 particles with random momenta crossing all
level boundaries for 8 M: mesh integrals of E and S_i equal the particle sums to the
printed 16 digits on the GPU (pairwise sums) and to 4e-13 on the serial CPU build
(sequential summation), for the published scheme, for fixed level caps 1 and 0, with two
filter passes, and for the density-adaptive cap.

## Kretschmann scalar (CPU, 2026-11-13)

Brill-Lindquist puncture at t = 0, dx = 0.25 M: relative error against 48 M^2/R^6 with
sixth-order differences 5e-3 (1.5 < r < 2.5), 2e-4 (2.5 < r < 4), 1e-5 (4 < r < 6); with
second-order differences 1e-1, 2.5e-2, 8e-3.

## Z4c throughput (one GPU, 2026-11-13)

Uniform 128^3, RK4: 2.0e7 zone-cycles/s with nghost = 4 (1.9e7 with 32^3 MeshBlocks,
1.5e7 with 16^3), 3.5e7 with nghost = 2. Particle work (push, deposit, filter,
constraints) adds about 3 percent at 10^4 particles.

## Dust collapse, R_0 = 5 M, 9328 lattice particles (GPU, 2026-11-13)

- Static mesh dx = h = 0.303 M: central lapse equals the lapse bound to 1e-4 until
  tau_c = 2.6 M and leaves it at 3.3 to 3.5 M (published: about 3.5 M); central density
  follows the cycloid to 2e-4 until then and within 8 percent afterwards.
- Adaptive mesh, cloud at the finest level (published scheme): after refinement to
  dx = h/4 the central density drops to 0.44 of the cycloid (fewer particles than
  cells) and recovers as the dust contracts; apparent horizon first found at
  t = 16.33 M; all particles excised between t = 19.0 and 19.8 M (lapse threshold 0.1).
  Horizon mass 0.974 M with the finder's default stopping tolerance (1e-3 per iteration),
  which leaves a residual mean expansion of -0.03; rerun with tolerance 1e-7 pending.
- Deposition identity 1e-15 throughout, across all regrids; no unconverged pushes.
