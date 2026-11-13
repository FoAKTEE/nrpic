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
  Horizon mass 0.974 M as reported by the finder at the time. WITHDRAWN: the finder had
  a defect that makes it read low by 2 to 3 percent (see "Horizon mass calibration:
  results"); to be remeasured.
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

## Stable cluster controls: results

- Net momentum (s1_nf4 against the earlier unperturbed run, same sample, 05:16): with
  the mean momentum removed the centre of mass stays within 0.018 M of the origin for
  300 M (its offset at t = 0 is 0.018 M; the positions were not recentred), against a
  drift to 0.22 M before. Lapse, mass-shell radii and constraint norms are unchanged to
  plotting accuracy. Prediction held: the drift was the net momentum of the sample.
  Figure: `analysis/diag/figs/cluster_ctl_momentum.png`.
- Seeds (s1_nf4 against s2_nf4, 05:24): the excursion is common to both. Central lapse
  0.8094 -> 0.8367 at t = 116 M (seed 1) and 0.8383 at t = 121 M (seed 2), back to
  0.8133 and 0.8113 at t = 230 M. The seed-dependent part is a ripple of about 0.003
  on top, a tenth of the excursion. The sampling-noise explanation predicted different
  sign or timing between seeds and is ruled out as the main cause.
  Figure: `analysis/diag/figs/cluster_ctl_seeds.png`.
- The excursion is a physical expansion and recontraction, not a coordinate effect: the
  central energy density (20 M averages) goes 5.0e-4 -> 3.4e-4 (t = 115 M) -> 5.5e-4
  (t = 230 M) for seed 1 and 5.1e-4 -> 3.1e-4 -> 5.9e-4 for seed 2 (equilibrium
  5.47e-4), and the mean Lorentz factor sum m W / sum m goes 1.04689 -> 1.0371 ->
  1.0452, a fifth of the kinetic energy given up and taken back.
- The original reports "only small-amplitude oscillations" for this model at the same
  dx = M/2 with 2e6 particles (no number given). Ours: mass-shell radii out by about 15
  percent and back.
- Working hypothesis, written before the filter variants finish: the source is softened
  by the cloud and the filter (variance per dimension dx^2/6 for the cloud plus dx^2/2
  per filter pass: 0.54, 0.29, 0.04 M^2 for four, two, zero passes at dx = M/2), the
  metric it produces is shallower than the equilibrium one the particle velocities were
  drawn for, and the cluster expands towards the softened equilibrium and overshoots.
  If so, the lapse excursion (0.028 with four passes) scales with that variance: about
  0.015 with two passes and about 0.002 with none. If the three variants show the same
  excursion, the hypothesis is wrong and the next suspects are the time lag of the
  source (frozen over a step; test: half the time step) and the relaxation of the
  initial constraint violation.
- Seed 3 (05:32): peak lapse 0.8369 at t = 120 M, 0.8138 at t = 230 M. Three seeds:
  peaks 0.8367, 0.8383, 0.8369 at t = 116, 121, 120 M. The excursion is the same for
  every sample.
- Filter passes (seed 1; 05:40 and 05:48). Peak rise of the central lapse above
  equilibrium within the first 130 M against the smoothing variance per dimension:

  | passes | variance / M^2 | predicted rise | measured rise | at t / M |
  |---|---|---|---|---|
  | 0 | 0.042 | about 0.002 | 0.0044 | 89 |
  | 2 | 0.292 | about 0.015 | 0.0176 | 112 |
  | 4 | 0.542 | (reference) | 0.0273 | 116 |

  The excursion grows with the smoothing as predicted, close to linearly, with a
  remainder of 0.002 to 0.004 at zero passes that is of the size of the seed ripple.
  This supports the softening hypothesis and does not yet prove it: the number of passes
  also changes the noise level. Decisive test: a filter with the same number of passes
  whose second moment is cancelled (below).
- Without filter the run shows no outward excursion, and from t = 115 M on something
  else: the lapse falls in irregular steps to 0.785 at t = 270 M, the outer mass shells
  move in (90 percent radius 8.03 -> 7.37 M), the constraint norms are 13 times those of
  the four-pass run (0.14 against 0.011) and sum m u_i wanders by 1e-4. Cause not
  determined; a noise-driven origin would show as seed dependence and as a faster drift
  at smaller N, neither of which has been run.
  Figure: `analysis/diag/figs/cluster_ctl_filter.png`.

## Compensated filter (source, 2026-11-13)

New option `<particles> filter_compensate = true`: after the `nfilter` binomial passes,
one pass with weights (-c, 1+2c, -c) per dimension, c = nfilter/4 (`filter_comp_c`
overrides c). The binomial passes widen every cloud by nfilter dx^2/2 per dimension;
this pass cancels that second moment. Combined response (1-s)^n (1+ns) with
s = sin^2(k dx/2): equal to one up to fourth order in k dx, monotonically decreasing,
zero at the Nyquist wavenumber. Standard in plasma particle-in-cell codes.

Single particle at a cell centre, flat space, uniform level (CPU): the line profile
through the particle equals the expected one-dimensional kernel to the printed digits
(1e-7) for 4 passes without and for 4, 2, 1 passes with compensation; second moment
2.0000 cells^2 without and 0.0000 with; negative lobes 5, 6 and 10 percent of the peak
for 4, 2, 1 passes; volume integral of E equal to the particle sum to 1e-15, and to
6e-8 in the one case where the wider kernel reaches a refinement boundary (the filter
is not exactly conservative across levels; this was already so for the binomial passes
and is what the post-filter columns of the particle history record).

Prediction for the stable cluster with four passes plus compensation, written before
the run: the lapse rise within 130 M drops from 0.027 to the zero-pass value (0.002 to
0.005) while the constraint norms stay near those of four passes (0.011). If the rise
stays near 0.027 the softening hypothesis is wrong.

Addendum to the filter-pass controls (two-pass run complete, 05:47): the two-pass
history has the shape of the four-pass one at 0.65 of its height; late-time constraint
norms 0.14, 0.026, 0.011 for zero, two, four passes. Three-way figure:
`analysis/diag/figs/cluster_ctl_filter.png`.

## Horizon mass calibration: results (2026-11-13, 05:50 to 06:05)

Misner-Sharp mass m of the evolved slice from the restart dumps (script
`analysis/diag/tracers_exact.py`, written for the tracer check; m is constant in R for
exact Schwarzschild and equals the horizon mass) against the mass the finder reports,
all at t = 50 M:

| run | m - 1 (slice) | finder mass - 1 | finder rms expansion |
|---|---|---|---|
| dx = M/4 | -3.9e-2 | -6.5e-2 | 1.9e-2 |
| dx = M/8 (baseline) | +1.5e-3 | -2.29e-2 | 1.2e-2 |
| dx = M/8, tolerance 1e-8 | (same slice) | -2.29e-2 | 1.2e-2 |
| dx = M/8, 32 angles, l_max 16 | (same slice) | -1.19e-2 | 8.8e-3 |

Against the predictions written before the runs:
- Evolution resolution: the slice itself is 3.9 percent light at M/4 and 0.15 percent
  heavy at M/8. That part converges and is small at M/8.
- Finder stopping: the tight tolerance takes the mean expansion from -2e-3 to +2e-5 and
  changes the mass by 3e-5. The stopping rule is not the cause of the offset. My first
  explanation of the low horizon mass ("the finder stops early") is refuted.
- The finder reads 2.4 to 3 percent below the slice at both resolutions, its rms
  expansion does not go down with more iterations, and the result depends on the
  angular resolution. None of the three should happen for a sphere.

Cause, found by reading the finder and confirmed by an A/B run. The finder
(`z4c/fastflow.cpp`, vendored AthenaK) stores finite-difference derivatives of the
metric on the active cells of each MeshBlock and interpolates that array to the surface
with a stencil of 2 NGHOST points per dimension. The ghost cells of the array are never
filled (they keep their allocated zeros), so every surface point within NGHOST cells of
a block face gets a wrong derivative. A horizon centred on the origin, where eight
blocks meet, is cut by three such faces.

New option `<fastflow> metric_drvts = interpolant`: the derivatives are taken from the
interpolant of the metric itself, whose ghost cells are filled
(`InterpolateLagrangeDeriv` in `utils/inline_interpolator.hpp`). A/B on the same data,
the t = 50 M dump of the baseline run restarted on CPU for one cycle, identical finder
settings:

| derivatives | finder mass | rms expansion | mean radius |
|---|---|---|---|
| stored (original) | 0.977110 | 1.2e-2 | 1.2699 |
| interpolant | 1.001338 | 6.3e-9 | 1.3455 |

The original setting reproduces the GPU value (0.97711). With the interpolant the
surface is a sphere to 6e-9 in expansion and its mass agrees with the Misner-Sharp
mass of the slice (1.0015 to 1.0017) to 2 to 4 parts in 1e4. The remaining mean
expansion, -4e-3, is the stopping tolerance (worth 3e-5 to 6e-5 in mass).

On the exact initial slice (true mass 1, horizon at r = M/2, four cells from the
puncture at dx = M/8) the two settings give 1.0036 and 0.9915 with rms expansion 0.13
and 0.005: there the interpolation of the metric itself next to the puncture limits
the result, and neither number should be quoted.

Consequences: every horizon mass recorded before this entry (0.974 after dust collapse,
0.972 to 0.979 for the puncture) was produced by the defect and is withdrawn. Collapse
runs are to be made with `metric_drvts = interpolant`.
