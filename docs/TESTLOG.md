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

Further checks of the corrected finder (CPU restarts of t = 50 M dumps, 06:12 to 06:20):

| slice | finder setting | finder mass | slice mass (Misner-Sharp) |
|---|---|---|---|
| dx = M/8 | original | 0.977110 | 1.0015 to 1.0017 |
| dx = M/8 | corrected, tolerance 1e-5, 16 angles | 1.001338 | |
| dx = M/8 | corrected, tolerance 1e-9, 16 angles | 1.001398 | |
| dx = M/8 | corrected, tolerance 1e-9, 32 angles, l_max 16 | 1.001582 | |
| dx = M/16 | original (GPU run) | 0.94055 | 1.000014 |
| dx = M/16 | corrected, tolerance 1e-5, 16 angles | 0.999738 | |

- The original finder gets worse at M/16 (5.9 percent low, and erratic in time): the
  blocks are 1 M wide there, so more block faces cut the horizon. A resolution error
  would shrink; a block-face error does this.
- With the correction the finder agrees with the slice to 3e-4 at the production
  settings; of that, 6e-5 is the stopping tolerance and 1.8e-4 the 16-point angular
  grid. With both tightened the difference is below 1e-4.
- Evolution error of the puncture itself, |slice mass - 1| at t = 50 M: 3.9e-2, 1.5e-3,
  1.4e-5 for dx = M/4, M/8, M/16 at the puncture.

## Compensated filter on the stable cluster: result (06:19)

Seed 1, four binomial passes plus the compensation pass, against four passes without it
and against no filter. Figure: `analysis/diag/figs/cluster_ctl_compensated.png`.

| filter | lapse rise within 130 M | lowest lapse in 300 M | late constraint norm | filtered / deposited energy - 1 |
|---|---|---|---|---|
| none | 0.0044 | 0.7849 | 0.14 | 0 |
| four passes | 0.0273 | 0.8094 | 0.011 | -3.4e-3 |
| four passes, compensated | 0.0065 | 0.7985 | 0.031 | -9.8e-5 |

- Prediction was a rise of 0.002 to 0.005 and constraint norms near 0.011. Measured:
  0.0065 and 0.031. The outward excursion is gone (a factor 4.2 down, to the level of
  the unfiltered run, whose history it follows for the first 110 M); the prediction for
  the rise was slightly too low and the one for the constraint norm too optimistic by a
  factor of three, because the compensated response passes more of the middle
  wavenumbers. The softening hypothesis stands: the excursion came from the second
  moment of the filter.
- A second effect of the same origin, not anticipated: the plain filter lowers the
  proper-volume integral of the energy density by 0.34 percent (it averages E, which
  carries 1/sqrt(gamma), across a non-uniform sqrt(gamma)); with compensation the
  change is 1e-4.
- With compensation the mass-shell radii stay within about 4 percent of equilibrium
  for 300 M. What remains is a seed-specific motion (a lapse dip of 0.011 near
  t = 280 M, which the unfiltered run of the same seed shows with 0.024). Other seeds
  with compensation have not been run yet.

Decision: cluster runs use four passes with compensation. Dust-collapse tests keep the
published plain filter until the two are compared on them.

## Production relaunch with the corrected executable (queued 06:22)

All production jobs that were still waiting carried the earlier executable (finder
defect, no compensation) and were cancelled before they ran. Relaunched with
`.work/build_gpu_v4` (source at commit 78d1d42 or later), run directories `*_v4`:
cluster models with four filter passes plus compensation; dust and prolate collapse with
the published plain filter; `metric_drvts = interpolant` everywhere.

Predictions written before any of these runs started:
1. `puncture/hcal/dx8_fixed` (GPU check of the corrected finder, 12 M): horizon mass at
   t = 10 M within 5e-4 of the slice mass (about 1.0015), rms expansion below 1e-6;
   the original gave 0.9778 and 1.1e-2.
2. `st/dir_yc0500_plain` and `_comp` (y_c = 0.5, no perturbation, 200 M): with the
   plain filter the cluster expands from the start (lapse rising from 0.55), as the
   stable model did; with compensation the first 50 M stay within a third of that
   excursion, and which way it finally goes is set by the sample and is not predicted.
   The original reports that its unperturbed y_c = 0.5 run expands and migrates while
   the same model with a one-percent inward kick collapses; a systematic outward bias
   of a plain filter would produce exactly that pair. If the plain run does not expand,
   this reading is wrong.
3. `st/ctl/s2_nf4c`, `s3_nf4c` (stable model, seeds 2 and 3, compensated): lapse rise
   within 130 M below 0.01 for both; later excursions of order 0.01 that differ
   between seeds.
4. `os/adapt_v4` against `os/nocap_v4` (same particles and mesh, cloud level adaptive
   against cloud at the finest level): open question, no prediction for the lapse; for
   the central density reading the uncapped run should repeat the drop to about half
   of the cycloid after the first refinement and the capped run should not. Horizon
   mass with the corrected finder: within one percent of the total mass in both; a
   value below 0.98 would mean mass is really missing and would need explaining.
5. `st/yc0605_v4`, `yc0500_v4` (one-percent inward kick, compensated): both collapse
   and form a horizon (original: at t = 109 M and 73 M); `yc0283_v4` expands;
   `yc0900_v4` and `yc0819_v4` stay within a few percent of equilibrium.

Addendum (06:27), two passes with compensation: lapse rise within 130 M 0.0061 (plain
two passes: 0.0176), lowest lapse 0.7967 at t = 279 M, energy integral changed by
-7.9e-5. The history coincides with the four-pass compensated one to 0.002 throughout
(0.8125 against 0.8126 at t = 50 M, 0.8035 against 0.8049 at t = 200 M). With
compensation the result no longer depends on the number of passes; the motion that is
left is common to both and to the unfiltered run of the same seed.

## Corrected finder on GPU (06:28), against prediction 1

`puncture/hcal/dx8_fixed`, 12 M. Horizon mass 0.999860, 1.000044, 1.000189, 1.000323 at
t = 5, 8, 10, 11.5 M with rms expansion 7e-9 (original finder: 0.9812, 0.9776, 0.9778,
0.9782 with 1.1e-2). At t = 0 the GPU and CPU values agree to the six digits printed
(0.991521).

The prediction said "within 5e-4 of the slice mass (about 1.0015)". The agreement holds:
the slice's Misner-Sharp mass at the horizon in the t = 12 M dump is 1.000635, the
finder at 11.5 M reads 1.000323, a difference of 3e-4, the same as at t = 50 M
(stopping tolerance plus 16-point angular grid). The number I had put in for the slice
mass was wrong: 1.0015 is its value at t = 50 M. At t = 12 M the excess is 6e-4 at the
horizon and still zero (4e-6) further out; it is produced near the puncture during the
gauge transient and spreads outward afterwards.

## Unperturbed y_c = 0.5: plain against compensated filter (06:39, 06:50), prediction 2

Same sample (seed 1), no perturbation, static mesh of the migration test, 200 M.

| central lapse reaches | plain filter, t / M | compensated, t / M |
|---|---|---|
| 0.60 | 19.5 | 37.8 |
| 0.65 | 30.2 | 52.2 |
| 0.70 | 37.5 | 64.0 |
| 0.80 | 59.2 | 88.0 |
| 0.85 | 81.0 | 110.8 |

- Plain filter: expands from the start, lapse 0.552 -> 0.929 at t = 200 M, mean Lorentz
  factor 1.172 -> 1.008, no particle lost. As predicted, and as the original describes
  its migration run (lapse from about 0.56 to 0.91 in the first expansion).
- Compensated: expands too, 18 to 30 M later. Its excursion is 24 and 27 percent of the
  plain one at t = 20 and 30 M and 42 percent at t = 50 M; the prediction "within a
  third for the first 50 M" holds to t = 35 M and fails after.
- The direction was not predicted and is outward for this sample in both runs. Whether
  the compensated run expands because of what is left of an outward bias (the stable
  model keeps a rise of 0.006 with compensation), because of this sample, or for
  another reason is not determined. Seeds 2 and 3 with compensation are queued
  (`st/dir_yc0500_comp_s2`, `_s3`).
- The reading that the plain filter alone decides between migration and collapse is
  therefore not established; what is established is that it advances the expansion.
- The long migration run is started with compensation (`st/migration_yc0500_v4`).

## Stable model with the one-percent inward kick, compensated (06:47)

`st/yc0819_v4`, seed 1, 300 M. Figure: `analysis/diag/figs/cluster_history_yc0819_v4.png`.
No particle lost; centre of mass within 0.018 M; mean Lorentz factor constant to 1e-3.
The central lapse oscillates about the equilibrium value 0.8094 with a period of about
75 M and the minima deepen: maxima 0.8119, 0.8111, 0.8167, 0.8190, 0.8170 at t = 24,
54, 105, 181, 255 M; minima 0.8087, 0.8074, 0.8066, 0.7991, 0.7875 at t = 40, 73, 155,
208, 282 M. The 10 percent mass radius swings between 2.5 and 3.5 M at the end
(equilibrium 3.13 M). The unperturbed compensated runs of the same seed show the dip
near t = 280 M with 0.011 to 0.013, the unfiltered one with 0.024; the plain four-pass
runs show no such growth after their initial excursion (ripple 0.003).

Cause of the growth not determined. It orders with the constraint norm of the runs
(plain 0.011, compensated 0.031, none 0.14), which would fit excitation by particle
noise that the compensated filter lets through at intermediate wavenumbers; a slow
instability of the scheme would look similar in one run. Discriminating runs already
queued: seeds 2 and 3 (noise: timing and size differ between seeds; instability: same
growth), N = 10^3 and 10^2 (noise: amplitude grows as N^(-1/2)).

Addendum to the y_c = 0.5 direction tests (figure
`analysis/diag/figs/cluster_dir_yc0500.png`): the expansion is large in both runs. The
half-mass radius goes from 2.29 M to 15.7 M (plain) and 11.8 M (compensated) at
t = 200 M and is still growing, more slowly; the 90 percent radius reaches 20.9 M and
17.4 M. The original also reports a first expansion by two orders of magnitude in
central density before recontraction. The finest level of this mesh covers |x| < 7.9 M,
so most of the matter is on coarser cells (M/2 to 1 M) from t = 100 M on.

## Stable model, compensated, three seeds (06:56), prediction 3

Extrema of the central lapse (equilibrium 0.8094), unperturbed, four passes plus
compensation:

| seed | rise within 130 M | minima (t / M : value) |
|---|---|---|
| 1 | 0.0065 | 74 : 0.8114, 158 : 0.8069, 208 : 0.8031, 281 : 0.7985 |
| 2 | 0.0084 | 67 : 0.8100, 141 : 0.8053, 215 : 0.7990, 277 : 0.7924 |
| 3 (to t = 247 M) | 0.0061 | 69 : 0.8101, 139 : 0.8075, 217 : 0.8033 |

- First part of the prediction holds (rise below 0.01 for every seed).
- Second part fails: I predicted later excursions "that differ between seeds". They do
  not. All three seeds oscillate with the same period (about 72 M), the same phase
  (minima near 70, 140, 215, 280 M) and minima that deepen at the same rate (by a
  factor of about 1.6 per period). The reading "excited by particle noise" predicted
  seed-dependent timing and is ruled out as the main cause. The oscillation is started
  by something common to all samples and then grows.
- A stable equilibrium should not have a growing radial oscillation. Candidates, each
  with a run that can fail it (queued 06:57 under `runs/st/osc/`, all seed 1, four
  passes plus compensation, unperturbed):

  | run | change | reading it tests | expected if that reading is right |
  |---|---|---|---|
  | dt2 | half the time step | the source is frozen over a step, so gravity lags the matter | growth per period roughly halves |
  | k1_0p1, k1_0 | constraint damping 0.1 and 0 (default 0.02, i.e. a time of 50 M, close to the period) | constraint damping feeds back on the mode | growth changes strongly with the value |
  | ch0p05 | parabolic relaxation of the Hamiltonian constraint | the constraint violation carried along (norm 0.03) drives it | growth reduced |
  | long | continue the base run to 600 M | growth against beating of two close modes | keeps growing, or turns over |
  | N = 10^3, 10^2 (already queued) | fewer particles | deterministic origin | same phase and period |

  My own estimate for the time-lag reading, written before the run: a restoring force
  delayed by half a step gives a growth rate omega^2 dt/4 = 2e-4 per M for
  omega = 2 pi/72 M and dt = M/8, forty times less than the 8e-3 per M observed, so I
  expect dt2 to change little. If it halves the growth, the estimate is wrong.
- The cluster production runs (sequence, N scaling with Monte Carlo sampling,
  reconfiguration, migration, cluster with clumps) are held until this is understood;
  dust collapse, prolate collapse and the head-on tracers do not depend on it and
  proceed after the diagnostics.

Shape of the growing oscillation (script `analysis/diag/cluster_osc.py`, figure
`analysis/diag/figs/cluster_osc_seeds.png`), observations only:
- Amplitude (half the difference of successive smoothed extrema) against time, fitted
  by a straight line: slopes 1.3e-5, 5.0e-5, 3.4e-5 per M for seeds 1, 2, 3 with
  compensation; it reaches 0.007 to 0.013 at t = 280 M. The growth looks linear in time
  rather than exponential; 300 M do not decide between the two.
- The mean of the oscillation drifts down by 0.001 to 0.004 with compensation and by
  0.016 without filter.
- The mean Lorentz factor of all particles changes by at most 2e-3 in the compensated
  runs while the lapse dips by 0.011 to 0.017; in the plain-filter excursion a lapse
  change of 0.027 came with a change of 0.010. The late dips are therefore concentrated
  at the centre (the 10 percent mass radius swings, the outer shells hardly move) and
  are not a breathing of the whole cluster.
- The compensated runs also show, at a fifth of its size, the slow excursion of the
  plain filter (mean Lorentz factor lowest near t = 110 M, back at t = 210 M).
- Newtonian estimate of the radial period of a particle in the core, for the central
  density 5.5e-4: pi (3/(4 pi rho))^(1/2) = 66 M. The observed period, 72 M, is close
  to it; in a nearly harmonic core all particles share this period, so a coherent
  radial motion of the core does not phase-mix away. This says where the period comes
  from, not why the amplitude grows.

## Growing oscillation against particle number (07:06)

`st/yc0819_n1e3_v4` against `st/yc0819_v4` (both with the one-percent inward kick and
the compensated filter). Figure: `analysis/diag/figs/cluster_osc_N.png`.
- Amplitude at N = 10^3 and 10^4: 0.008 against 0.005 near t = 120 M, 0.012 against
  0.010 near t = 215 M, 0.008 against 0.009 near t = 258 M; slopes of the straight-line
  fit 3.7e-5 and 4.8e-5 per M. A noise-driven motion would be 3.2 times larger with ten
  times fewer particles. It is not.
- Same period; the extrema of the smaller sample come up to 20 M later in the first
  half and at the same times in the second.
- So the growth does not depend on the sample (three seeds) and not on the number of
  particles (10^3, 10^4). It belongs to the scheme or to the model. Remaining tests as
  listed above (time step, constraint damping, relaxation, longer run).

## Dust collapse: the published lattice rule at 10^4 particles carries 1.2 percent too much mass (07:05)

Found through the slice-mass tool (`analysis/diag/slicemass.py`, new; it reads the
Misner-Sharp mass profile of every restart dump of a spherical run and locates the
horizon where 2m/R = 1). On the earlier adaptive-mesh dust run the mass profile sits at
1.010 to 1.015 between the dust and a front that leaves the surface at t = 0 and moves
out at light speed, and at 1.000000 outside the front; the horizon mass from the slice
is 1.0077 and 1.0042 at t = 20 and 25 M, above the total mass of the initial metric.
Figure: `analysis/diag/figs/slicemass_os_amr_n26.png`.

Reason: the particle masses follow the published rule m_p = rho_0 psi^6 h^3 on the
lattice sites inside the surface. The number of sites inside a sphere differs from its
volume in cells by a fraction of order 1/n_lat; at n_lat = 26 there are 9328 sites for
a volume of 9203 cells, and the masses sum to 1.16874 against the continuum rest mass
1.15515 the initial metric is built for (+1.18 percent; between -0.7 and +2.5 percent
for n_lat = 14 to 27; the original uses n_lat = 124, where it is negligible). The
interior density is exact, which is why the central lapse and density had followed the
exact solution; the excess sits at the surface and shows up as a mass the initial
metric does not contain.

Change: generator option `--lattice-surface-correction` (the masses of the outermost
layer of one lattice spacing, 2120 of 9328 particles, are multiplied by 0.9424 so that
the total equals the continuum rest mass; interior unchanged). Off, the rule is the
published one.

The first adaptive run with the corrected finder (`os/adapt_v4`, published rule,
cancelled at t = 36 M when this was found; it had finished the collapse in ten minutes)
gives a horizon mass of 1.0106 at formation (first found t = 17.1 M) and 1.0119 at
t = 20 M, as the excess mass predicts, and then keeps rising after the last particle
is removed at t = 19.8 M: 1.0126, 1.0140, 1.0165, 1.0185 at t = 22, 25, 30, 36 M
(rms expansion on the surface below 1e-5). Cause of the rise not determined; the
slice-mass analysis of the same dumps is running. Both dust runs are resubmitted with
corrected initial data (`os/adapt_sc`, `os/nocap_sc`); the uncapped control with the
published rule (`os/nocap_v4`) runs as well.

## Test-particle clusters in Schwarzschild and Kerr (campaign finished 07:10)

Full account in `docs/results_cluster_test.md`, figures in `analysis/cluster_test/figs/`
(I looked at `invariants_time` and `deposit_conservation`). Gaussian clusters of 10^2
to 10^4 test particles around a circular orbit at 10 M, a = 0 and 0.9, 1000 M, on the
analytic metric and on the mesh metric (dx = M/4 where the cluster moves).
- Invariants per particle after 1000 M: analytic metric, median error of the energy
  1e-8 with either pusher, L_z at round-off with the midpoint pusher; mesh metric,
  1.2e-7 in energy and 5e-6 in L_z with either pusher (interpolation of the metric
  sets it; doubling the cell size gives order 3.0 and 2.5).
- Phase mixing into a ring; the azimuthal order parameter ends at the value of a
  random ring.
- Deposition identity before the filter: 1e-15 through up to 1.2e5 level crossings and
  through all removals, except while a particle sits within half a cell of the outer
  boundary (the part of its cloud outside the domain is dropped; up to 7e-5).
- After the filter the integrals differ from the particle sums by up to 9e-4
  (N = 10^4), 6.6e-3 (N = 10^2) and 7.3e-3 (plunging family) once particles cross
  refinement boundaries: the mesh filter is not conservative across levels. Known
  limitation for now; a filter applied to the cloud of each particle before it is
  mapped to the leaves would be conservative by construction (not implemented).
- Removal at the lapse threshold: 3726 and 3345 particles of the plunging families
  removed against 3727 and 3339 predicted from the exact invariants.
- Density noise against N: exponent -0.47 to -0.51.
- The mesh step costs 32 to 35 ms whatever N is, of which the two filter passes take 26.

## Dust collapse, adaptive cloud level: horizon mass from the slice against the finder (07:20)

`os/adapt_v4` (published lattice rule, particle mass 1.18 percent above the continuum
value; all particles removed between t = 19.0 and 19.8 M). Mass far from the hole
1.000001 in every dump. Figure: `analysis/diag/figs/slicemass_os_adapt_v4.png`.

| t / M | horizon mass from 2m/R = 1 | corrected finder | difference |
|---|---|---|---|
| 20.0 | 1.01088 | 1.01193 | +1.1e-3 |
| 25.0 | 1.01548 | 1.01397 | -1.5e-3 |
| 30.0 | 1.01666 | 1.01649 | -1.7e-4 |
| 35.0 | 1.01828 | 1.01830 | +2e-5 |

- The two independent measures agree, to 1e-3 right after the collapse (when the
  spread of m around the sphere is 4e-3) and to 2e-5 at t = 35 M.
- At formation (t = 17.1 M) the finder reads 1.0106; the particles carry 1.0118 times
  the mass of the initial metric. The horizon mass at formation equals the mass that
  went in to 0.1 percent.
- Afterwards the horizon mass rises by 0.7 percent in 15 M although no matter is left,
  at 2e-4 to 9e-4 per M, in both measures. In exact vacuum it cannot change. The older
  run with the cloud at the finest level went the other way (1.0077 at t = 20 M, 1.0042
  at t = 25 M). Cause not determined. Things that differ from the vacuum-puncture test,
  where the drift was 3e-5 per M: the interior is far from stationary when the matter
  is removed; removing the matter leaves a constraint violation of the size of the
  removed source inside the horizon; the horizon (coordinate radius 1.2 to 1.35 M) sits
  on the boundary between the two finest levels (dx = M/26 inside 1.21 M, M/13
  outside). Not yet tested which of these, if any, matters.
- Until that is settled the number to quote for the collapse is the horizon mass at
  formation, with the later drift given as its uncertainty.

Addendum (07:14), N = 10^2 (`st/yc0819_n1e2_v4`, same figure): a different regime.
The lapse swings by 0.01 to 0.02 from the first 20 M on, irregularly, dips by 0.037 at
t = 178 M, its mean drifts down by 0.029, and the mean Lorentz factor of the particles
rises by 0.077 (the kinetic energy more than doubles). With a hundred particles the
sample dominates within one period; with 10^3 and 10^4 the common growing oscillation
does.

## Unperturbed y_c = 0.5, compensated, second seed (07:17)

Seed 2 expands on the same schedule as seed 1: central lapse 0.60, 0.70, 0.80, 0.85
at t = 38.2, 67.5, 86.0, 109.8 M (seed 1: 37.8, 64.0, 88.0, 110.8 M). The outward
start with the compensated filter is therefore not a property of the sample either.
Something common to all samples still pushes outward, as in the stable model, where a
lapse rise of 0.006 is left with compensation.

One candidate with a test: the compensation pass cancels the widening by the filter
passes but not the width of the cloud itself (variance dx^2/6 per dimension, a twelfth
of what four passes add). Run `st/osc/ccloud` (stable model, seed 1, compensation
coefficient 4/4 + 1/12, which cancels both) is queued. Written before the run: if the
cloud width is what is left, the rise within 130 M drops well below 0.006; if it stays,
the remaining offset comes from elsewhere (for instance from the difference between
the continuum equilibrium and the equilibrium of the discretized field equations at
this cell size).
