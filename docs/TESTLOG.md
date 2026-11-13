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

## Restart (CPU, 2026-11-13)

Dust collapse on a small mesh (8 MeshBlocks, 9328 particles, adaptive cloud level):
20 cycles uninterrupted against 10 cycles, restart, 10 cycles. Particle positions agree
to 9e-16, momenta to 3e-16; every column of the particle history (lapse, density,
proper time, sums) is identical to the printed digits; counters and output schedule are
restored from the particle restart file.

## Stable cluster y_c = 0.819, 10^4 stratified particles (GPU, 2026-11-13)

dx = M/2 over the cluster, four filter passes, inward velocity perturbation of one
percent, 300 M: no particle lost; central lapse oscillates between 0.804 and 0.838 about
the equilibrium value 0.8091; the radii enclosing 10 to 90 percent of the rest mass stay
within about 10 percent of their equilibrium values; constraint norms decay by a factor
of ten in the first 100 M and then stay flat; centre of mass moves 0.2 M.
Figure: `analysis/diag/figs/cluster_history_yc0819_full.png`.

## Apparent-horizon finder settings (2026-11-13)

The flow finder stops when the mass changes by less than `mass_tol` between iterations.
With 1e-3 the surface it returns in the dust-collapse run has a mean expansion of -0.03
and a mass of 0.974. Whether the stopping rule is the reason for the low mass was not
tested at the time; the vacuum puncture below, run with 1e-5, reads 0.972 to 0.979, so
the stopping rule is at most part of it (see the calibration entry). With 1e-7 it never meets the criterion at these resolutions and uses all its
iterations every cycle (about 10 s per cycle). Production runs use 1e-5, at most 400
iterations, and a search every 16 cycles (`fastflow/find_every`, added here).

## Stable cluster: block size, perturbation, net momentum (GPU, 2026-11-13)

Three runs of y_c = 0.819 with the same 10^4 stratified particles, 300 M each.
Figure: `analysis/diag/figs/cluster_history_yc0819_compare.png`.

- 32^3 against 16^3 MeshBlocks (same cells, different block decomposition): identical
  histories to plotting accuracy (lapse, mass-shell radii, centre of mass); constraint
  norms differ by 5 percent at late times. The 16^3 layout runs 300 M in 8 minutes.
- With and without the one-percent inward velocity perturbation (same sample): the same
  motion, lapse 0.809 -> 0.837 at t = 115 M -> 0.810 at t = 230 M; afterwards the
  perturbed run falls to 0.804 and the unperturbed one stays at 0.810 to 0.813. The
  applied perturbation is therefore not what drives the excursion. What does drive it is
  not established by these runs. Two candidates, which predict different things:
  (a) sampling noise of this particular sample: other seeds give excursions of similar
  size with different sign and timing, and the size grows as N^(-1/2);
  (b) a systematic offset between the deposited source (cloud plus four filter passes,
  width about 0.75 M at dx = M/2) and the smooth equilibrium the metric starts from, or
  the relaxation of the initial constraint violation (norm 0.11 at t = 0): every seed
  gives the same outward-first excursion, and its size changes with the number of filter
  passes and with dx, not with N.
  Controls queued: seeds 2 and 3, and seed 1 with zero and two filter passes (see below).
  One excursion in 300 M does not define a period; 230 M is of the order of the orbital
  period at the surface, 2 pi (R^3/M)^(1/2) = 200 M. (An earlier version of this entry
  attributed the motion to sampling noise and its duration to closeness to the
  binding-energy maximum. Neither was tested, and the second is wrong: the maximum of
  the binding energy lies between y_c = 0.756 and 0.605.)
- Centre of mass: moves by (-0.02, 0.09, 0.20) M in 300 M. The sample has a net momentum
  per unit mass of (-1.3, 3.9, 8.8) 1e-4. The drift rates are 0.55, 0.74 and 0.76 of
  these in x, y, z, the same sign in every component and the size expected from
  dx/dt = alpha gamma^ij u_j / W. This points to the net momentum of the sample as the
  cause; the shift at the centre was not looked at. Direct check queued: the same sample
  with the net momentum removed should stay centred to well below 0.2 M.
  Consequence already applied: `problems/ic/make_ic.py` subtracts the mass-weighted mean
  of u_i for the cluster models by default (`--keep-net-momentum` restores the raw
  sample), and the particle files of all runs still queued at this time were shifted in
  place with `problems/ic/zero_momentum.py` (net momentum 1e-17 afterwards). At N = 100
  the raw sample has a mean velocity of 0.02, about half the cluster radius in 300 M.
- Change of the total sum m u_i over 300 M: below 7e-5 of the rest mass in every
  component. This is the net self-force of the discretized field on the sample; noise
  and mesh effects are not separated here.

## Stable cluster controls: what drives the excursion (queued 2026-11-13 05:03)

y_c = 0.819, 10^4 stratified particles, no velocity perturbation, net momentum removed,
dx = M/2, 300 M, under `runs/st/ctl/`:

| run | seed | filter passes |
|---|---|---|
| s1_nf4 | 1 | 4 |
| s2_nf4 | 2 | 4 |
| s3_nf4 | 3 | 4 |
| s1_nf0 | 1 | 0 |
| s1_nf2 | 1 | 2 |

Written before the runs:
- Sampling noise predicts: seeds 2 and 3 differ from seed 1 in sign or timing of the
  lapse excursion while its size stays at a few percent; the filter variants of seed 1
  keep the timing of seed 1.
- A systematic source-smoothing or constraint-relaxation offset predicts: all three
  seeds rise first and peak near t = 115 M; the size is ordered with the number of
  filter passes.
- Both can be present; then the seed-to-seed scatter against the common part gives
  their ratio.
- Net momentum: s1_nf4 differs from the earlier unperturbed run only by the removed
  mean momentum; its centre of mass should stay within a few 0.01 M.

## Density-adaptive cloud level on GPU: conservation (2026-11-13)

Same flat-space statically refined test as before (random particles crossing three
levels), adaptive cloud level, 81 cycles. The energy integral equals the particle sum
exactly at every cycle; the three momentum integrals agree to 5e-15 relative. The CPU
runs of the same test sit at 1e-13 to 2e-12, the round-off of a sequential sum over
10^5 cells against the pairwise sum used on the device.
Figure: `analysis/diag/figs/dep_smr_adaptive.png`.

## Test particles around an evolved puncture (GPU, 2026-11-13)

Unit-mass puncture, precollapsed lapse, moving-puncture gauge, 250 M; dx = M/8 inside
|x| < 4 M, dx = M/2 to 1 M where the bound tracers move; six tracers on the mesh metric,
implicit midpoint pusher. Figure: `analysis/diag/figs/tracers_single_v3.png`.

- Circular orbits at areal radius 7.04, 9.03, 11.03 M and an inclined one at 9.03 M:
  the areal radius stays within 2.5, 1.1, 0.9 and 1.1 percent of its initial value while
  the coordinate radius grows by 1.1 M (gauge). L_z, exactly conserved in any gauge that
  keeps the spherical symmetry, holds to 1.1e-4, 2.4e-4, 3.9e-4, 2.0e-4.
- The coordinate energy alpha W - beta^i u_i is not conserved while the gauge evolves
  (swings of 2 to 6 percent in the first 40 M, as expected: the initial time vector is
  not the Killing vector). Once the coordinates near the orbit are stationary it must
  equal the Killing energy (1 - 2M/R)/(1 - 3M/R)^(1/2) of the circular orbit. Late-time
  values: 0.944831, 0.952531, 0.959324, 0.952534 against 0.945053, 0.952697, 0.959479,
  0.952697: low by 2.4e-4, 1.7e-4, 1.6e-4, 1.7e-4.
- Plunging orbit (tag 4) and radial infall from rest (tag 5): reach the black hole and
  are excised at lapse 0.05 at t = 126 M and 54 M. Their coordinate energy after the
  transient sits 0.3 to 0.8 percent below its initial value; for the radial case the
  Killing energy is 0.904762 and the recorded plateau is near 0.900. The particle falls
  through the region where the coordinates still drift (the horizon's coordinate radius
  grows from 1.12 M at t = 10 M to 1.48 M at t = 250 M), so this number does not
  separate gauge from error. Gauge-independent check still to do: areal radius against
  proper time compared with the exact radial geodesic.

## Horizon mass of a vacuum puncture: calibration (2026-11-13)

The same run gives the apparent-horizon mass of an exact unit-mass black hole as the
finder reports it on this mesh family (dx = M/8 at the puncture, stopping tolerance
1e-5 on the mass, 16 angular points, l_max = 8):

| t / M | mass | mean expansion | rms expansion | mean coordinate radius |
|---|---|---|---|---|
| 0 | 1.00356 | +1.5e-1 | 1.3e-1 | 0.532 |
| 10 | 0.97779 | -4.1e-3 | 1.1e-2 | 1.120 |
| 50 | 0.97711 | -2.2e-3 | 1.2e-2 | 1.270 |
| 100 | 0.97503 | +1.7e-3 | 1.2e-2 | 1.364 |
| 250 | 0.97171 | +6.1e-3 | 1.3e-2 | 1.479 |

The mass falls by 2.2 percent in the first 10 M and then by 2.2e-5 per M. There is no
matter and no excision in this run. The value 0.974 found after dust collapse is
therefore what this setup gives for a black hole of unit mass, and says little about
the mass that went in. Two candidate causes, with a test for each (queued, 60 M each,
`runs/puncture/hcal/`, input `problems/puncture/horizon_calib.athinput`):

| run | change | tests |
|---|---|---|
| dx4 | dx = M/4 at the puncture | evolution resolution |
| dx16 | dx = M/16 inside 2 M | evolution resolution |
| dx8_tight | stopping tolerance 1e-8, up to 4000 flow steps | finder stopping |
| dx8_ang | 32 angular points, l_max = 16 | finder angular resolution |

Written before the runs: if the evolution near the puncture is under-resolved, the
deficit at t = 50 M (2.3 percent at M/8) shrinks by a factor of four or more at M/16 and
grows at M/4, and the two finder variants reproduce 0.977. If the finder is the limit,
dx8_tight or dx8_ang moves towards 1 and dx16 stays near 0.977. A residual mean
expansion of 4e-3 corresponds to a radial offset of order 4 M^2 x 4e-3, about one
percent of the horizon radius, so a finder contribution at the percent level is possible.
