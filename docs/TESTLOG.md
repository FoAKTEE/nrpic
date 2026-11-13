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

Addendum (07:28), third seed of the unperturbed y_c = 0.5 model with compensation:
central lapse 0.60, 0.70, 0.80, 0.85 at t = 41.5, 70.0, 91.5, 122.2 M. All three seeds
expand, on schedules that agree to 4 M at lapse 0.60 and to 12 M at 0.85.

## Dust collapse: cloud at the finest level against adaptive cloud level (07:32), prediction 4

Same particles (published lattice rule), same mesh rules, corrected finder; only
`deposit_adaptive` differs. `os/nocap_v4` (60 M) against `os/adapt_v4` (to 36 M).
Figures: `analysis/diag/figs/os_history_cap_v4.png`, `os_constraints_cap_v4.png`.

| | cloud at the finest level | adaptive cloud level |
|---|---|---|
| central lapse, difference between the two runs | below 4e-3 throughout, mostly below 1e-3 | |
| central density reading after the first refinement (t = 8 to 10 M) | 0.28 to 0.40 of the other run | follows the cycloid |
| constraint norm at the first refinement (t = 7.3 M) | jumps from 0.3 to 1.6 | no jump |
| largest constraint norm (t = 17 to 18 M) | 2.0 | 4.5 |
| constraint norm at t = 36 M | 0.2 | 0.66 |
| first horizon, t / M and mass | 16.43, 1.0114 | 16.47, 1.0113 |
| horizon mass at t = 20, 25, 30, 35 M | 1.0115, 1.0106, 1.0098, 1.0095 | 1.0119, 1.0140, 1.0165, 1.0183 |
| horizon mass at t = 50, 59 M | 1.0100, 1.0100 | (run stopped) |

Against the prediction:
- Density reading: as predicted (the uncapped run repeats the drop, the capped run does
  not).
- Lapse: this was the open question. The answer is that the dynamics at the centre do
  not notice the granular source: the lapse histories agree to a few 1e-3.
- Horizon mass "within one percent of the total in both": the mass that went in is
  1.0118 (see the lattice entry). At formation both read 1.0113 to 1.0114. Afterwards
  the uncapped run stays within 0.2 percent and settles at 1.0100; the capped run
  drifts up by 0.7 percent and is still rising when it stops. The upward drift noted
  earlier belongs to the adaptive cloud level, not to the collapse.

What this says about the level cap, as far as these two runs go: it removes the jump
of the constraint violation when the mesh refines under diffuse matter and gives a
usable density, and it does not change the collapse of the centre. Near the forming
black hole it makes things worse: constraint violations two to three times larger from
t = 13 M on, and a drifting horizon mass.

Reading to be tested: the mesh is refined to resolve the metric, so a cloud of one leaf
cell never spans a large change of the metric; a cloud several levels coarser does,
and spreads a particle's energy and its covariant momentum components over places
where the same particle would have different values. New option
`deposit_max_coarsen` (a cloud is at most this many levels coarser than the block its
particle is in; default 31 = no limit). Runs `os/adapt_mc1` and `os/adapt_mc2`
(corrected initial data, limit 1 and 2) queued after the build. Written before the
runs: if the reading is right, limit 1 keeps the first refinement free of the jump and
brings the late constraint norm (below about 2.5 at its maximum) and the horizon-mass
drift after removal (below 0.2 percent) to the values of the uncapped run, with limit 2
in between. If the late behaviour stays that of the unlimited adaptive run, the cause
is elsewhere in the adaptive path.

## Growing oscillation: constraint damping (07:41)

`st/osc/k1_0p1` (constraint damping 0.1) against the base run (0.02), same sample.
The damping acted: the Hamiltonian-constraint norm falls faster and ends at 0.019
instead of 0.031 (momentum 0.009 against 0.016). The lapse history is the same to
3e-4: every extremum at the same time with the same value (last minimum -0.0111
against -0.0108 at t = 280 M). The reading "constraint damping feeds back on the mode"
predicted a strong dependence on the value and is ruled out.

## Growing oscillation: time step (07:44)

`st/osc/dt2` (half the time step) against the base run: the same history to 4e-4
(last minimum -0.0104 against -0.0108 at t = 281 and 280 M; amplitude fit
0.0006 + 1.33e-5 t against 0.0006 + 1.34e-5 t). The time lag of the frozen source is
not the cause, as the estimate written beforehand had it.

Ruled out so far by a run each: the sample (three seeds), the particle number (10^3
against 10^4), the constraint damping (0.1 against 0.02), the time step. Still to
come: no constraint damping, parabolic relaxation, cancelling the cloud width,
continuation to 600 M.

## What the original shows for these two models (its figure files, 07:50)

The source package of the original contains its figures. Read off them, by eye:
- Stable model y_c = 0.819 (figure of the cluster sequence): the central lapse is drawn
  on an axis from 0 to 1 and stays near 0.81 for 300 M, with a broad rise of roughly
  0.01 around t = 150 to 250 M. An oscillation of 0.01 with a period of 70 M, as in our
  compensated runs, is at the limit of what that figure can show; the broad rise has
  the shape of the excursion our plain-filter runs make (0.027 with four passes, 0.018
  with two). Nothing here contradicts the original, and the original cannot confirm or
  exclude the growth we see.
- Unperturbed y_c = 0.5 (migration figure): the lapse leaves 0.56 after about 50 M,
  passes 0.8 near t = 125 M and 0.9 near 230 M, stays there to 350 M and falls back to
  about 0.57 near t = 450 to 520 M before settling around 0.85. Ours passes 0.8 at
  88 M (compensated) and 59 M (plain filter): the same expansion, starting earlier.

Addendum (07:49): without constraint damping (`st/osc/k1_0`) the lapse history is again
the same (last minimum -0.0107 at t = 280 M). Three values of the damping, one history.

## Growing oscillation: parabolic relaxation (07:53)

`st/osc/ch0p05` (relaxation length 0.05) against the base run. The relaxation works:
the Hamiltonian-constraint norm is 0.077 against 0.121 at t = 5 M and ends at 0.0145
against 0.031 (momentum 0.0085 against 0.016). The lapse history is the same to 1e-4.
The constraint violation carried along does not drive the oscillation.

State of the question: the history of the central lapse is reproduced to a few 1e-4
under changes of the constraint damping (three values), the relaxation, and the time
step, and its timing by other seeds and by a tenth of the particles. It is a
deterministic consequence of the initial particle distribution on this mesh with this
filter. That leaves the spatial side (cell size, cloud and filter, mesh layout), the
way the initial data are built, and the possibility that the motion is simply the
collisionless evolution of the small common offset the runs start with: in a core
where all particles share one radial period, a small coherent velocity offset bunches
the particles in radial phase, and the bunching grows in proportion to time until phase
mixing stops it. That would be linear growth, independent of N, of the time step and
of the constraint handling, which is what is seen; it is a reading, not a result. It
predicts that the amplitude saturates (the 600 M continuation) and that the growth is
proportional to the size of the initial offset (the run that also cancels the cloud
width, if that makes the offset smaller).

## Growing oscillation: continuation to 600 M (07:58)

`st/osc/long` continues the base run (seed 1, unperturbed, four passes plus
compensation). Extrema of the lapse minus equilibrium after t = 300 M: +0.0061 (316),
-0.0065 (359), +0.0126 (392), -0.0103 (423), +0.0088 (464), -0.0262 (495), +0.0112
(534), -0.0249 (564). Half the peak-to-peak swing: about 0.008 near t = 300 M, 0.011
near 400 M, 0.018 near 500 M and 0.018 near 550 M. The mean over each 100 M stays
within 0.004 of equilibrium, the mean Lorentz factor of the particles within 0.003 of
its initial value, and no particle is lost.

Against the two readings: the amplitude kept growing to t = 500 M and did not grow
between 500 and 565 M. Two extrema are not enough to call that saturation. A further
continuation to 1200 M is queued (`st/osc/long2`). What can be said now: over 600 M
the stable model stays bound and centred, with an oscillation of the central lapse
that has reached two to three percent.

Decision (08:00): the cluster runs on static meshes without the adaptive cloud level
(least compact model, Monte Carlo sampling at three particle numbers, reconfiguration,
migration) are released; nothing found so far gives a reason to change their settings,
and the oscillation question is followed on the stable model in parallel. The collapse
runs that use the adaptive cloud level (compact clusters, prolate collapse, cluster
with clumps) stay held until the dust runs with limited cloud coarsening are in.

## Dust collapse with corrected initial data, adaptive cloud level (08:11)

`os/adapt_sc`: particle masses sum to the continuum rest mass (surface-layer
correction). First horizon at t = 16.39 M with mass 0.9971; 0.9996, 1.0003, 1.0006 at
t = 17, 18, 20 M. The run with the published lattice rule read 1.0106 to 1.0119 at the
same times. With consistent initial data the horizon mass after formation equals the
total mass to 6e-4.
Later: 1.0012, 1.0026, 1.0047, 1.0061, 1.0068, 1.0067, 1.0065 at t = 22, 25, 30, 35,
40, 50, 59 M. The drift of the adaptive cloud level is there again, 0.6 percent, and
it levels off after t = 40 M.

## Dust collapse with corrected initial data, cloud at the finest level (08:16)

`os/nocap_sc` (published deposition rule, corrected lattice masses) against
`os/adapt_sc`:

| | cloud at the finest level | adaptive cloud level |
|---|---|---|
| first horizon, t / M and mass | 16.39, 1.00035 | 16.39, 0.9971 |
| horizon mass at t = 18, 20, 22 M | 1.0003, 1.0001, 1.0000 | 1.0003, 1.0006, 1.0012 |
| at t = 25, 30, 40, 59 M | 0.9995, 0.9990, 0.9988, 0.9987 | 1.0026, 1.0047, 1.0068, 1.0065 |
| largest constraint norm | 1.9 at t = 17.3 M | 4.7 at t = 18.2 M |
| constraint norm at t = 60 M | 0.031 | 0.142 |
| constraint norm at the first refinement (t = 7.5 M) | 1.25 | 0.37 |

- With the published deposition rule and consistent initial data the horizon mass equals
  the total mass to 3e-4 for the first 6 M after formation and settles 0.13 percent
  below it. This is the reproduction of the original's statement that the horizon mass
  is consistent with the total mass, at 9328 particles.
- The second pair repeats the first: the adaptive cloud level removes the jump at the
  first refinement and makes the late collapse worse (constraint norm 2.5 times larger
  at its peak, horizon mass drifting up by 0.65 percent).

## Growing oscillation: cancelling the cloud width as well (08:20)

`st/osc/ccloud` (compensation coefficient 4/4 + 1/12) against the base run. Figure:
`analysis/diag/figs/cluster_osc_ccloud.png`.
- Largest rise of the lapse within 130 M: 0.0045 against 0.0065. The slow excursion
  shrinks by a third.
- The first maximum, at t = 24 M, is unchanged (+0.0035 against +0.0037), and so is
  the oscillation: amplitude fit 0.0005 + 1.5e-5 t against 0.0006 + 1.3e-5 t, last
  minimum -0.0119 against -0.0108.
- Against the prediction ("if the cloud width is what is left, the rise drops well
  below 0.006"): it drops a little. The cloud width is a minor part of what is left;
  the common initial offset and the growing oscillation come from elsewhere. Since the
  offset did not change, this run says nothing about whether the growth is
  proportional to it.

Where the oscillation question stands. Ruled out by a run each: sample, particle
number, time step, constraint damping, constraint relaxation, cloud width. Not
determined: the cause of the common initial offset (0.4 percent in lapse within
25 M, 0.1 to 0.2 percent in the mean Lorentz factor), and why the oscillation grows.
One reading (bunching in radial phase in an isochronous core) fits and is untested.
Open tests: continuation to 1200 M (queued), halved cell size, a different sampler
(the Monte Carlo runs now released), an imposed offset of known size.

## Dust collapse: cloud coarsening limited to one level (08:35), against its prediction

`os/adapt_mc1` (adaptive cloud level, at most one level coarser than the particle's
block; corrected initial data) between the two runs of the previous entry:

| | cloud at the finest level | at most one level coarser | unlimited |
|---|---|---|---|
| constraint norm at the first refinement (t = 7.5 M) | 1.25 | 0.89 | 0.37 |
| largest constraint norm | 1.9 | 2.8 | 4.7 |
| constraint norm at t = 60 M | 0.031 | 0.10 | 0.14 |
| horizon mass at formation | 1.0004 | 1.0006 | 0.9971 |
| horizon mass at t = 20, 25 M | 1.0001, 0.9995 | 1.0011, 1.0011 | 1.0006, 1.0026 |
| horizon mass at t = 40, 59 M | 0.9988, 0.9987 | 0.9923, 0.9903 | 1.0068, 1.0065 |

The prediction fails. Limiting the coarsening to one level does not bring the late
behaviour to that of the uncapped run: the constraint norm peaks higher than uncapped,
and the horizon mass drifts by one percent, downward this time. The picture "a cloud
wider than the metric scale does the damage, so a little coarsening is harmless" is
too simple. What the three runs do show: the drift of the horizon mass after the
matter is removed is 0.13, 1.1 and 0.65 percent, smallest by far with the published
rule, and its sign is not systematic. Why any coarsening, even by one level, disturbs
the black hole this much is not determined.

Decision: collapse runs use the published rule (cloud at the finest local level). The
level cap stays in the code as an option for diffuse matter on a mesh that is refined
for other reasons; it is not used near black holes.

Addendum (08:38), coarsening limited to two levels (`os/adapt_mc2`): the same as the
unlimited adaptive run to plotting accuracy (horizon mass 1.0065 at t = 59 M against
1.0065, largest constraint norm 4.5 against 4.7). The unlimited rule rarely asks for
more than two levels in this problem. The scan is complete: horizon-mass drift after
removal of the matter -0.13, -1.1, +0.65, +0.65 percent for clouds at the finest level,
at most one, at most two, any number of levels coarser.

## Least compact cluster model, y_c = 0.900 (08:43), prediction 5

`st/yc0900_v4`: 10^4 stratified particles, one-percent inward kick, four passes plus
compensation, dx = M/2, 300 M. Figure: `analysis/diag/figs/cluster_history_yc0900_v4.png`.
No particle lost. Central lapse between 0.886 and 0.892 (equilibrium 0.8891). Radii
enclosing 10 to 90 percent of the rest mass within about 4 percent of their initial
values (10 percent radius 5.66 -> 5.42 M, 90 percent radius 13.96 -> 14.20 M). Mean
Lorentz factor constant to 2e-4. Centre of mass within 0.03 M. As predicted: the model
holds. Its lapse oscillation is three to four times smaller than that of y_c = 0.819
and grows ten times more slowly (amplitude fit 0.0008 + 4e-6 t).

Queued (08:52): `st/osc/dx2`, the base stable-cluster run with half the cell size
(dx = M/4 over the cluster, same particles, four passes plus compensation). Written
before the run: if the common initial offset and the growth come from the spatial
discretization at second order, the first maximum of the lapse (+0.0035 at t = 24 M)
and the amplitude at t = 280 M (0.011) both drop by about four; if the motion is the
dynamics of the model as sampled, both stay. The filter length halves with the cell, so
the source is noisier in this run; a larger irregular part is expected either way.

## Test particles around a head-on collision of two black holes (09:20)

`puncture/headon_v4`: two punctures of bare mass M/2 at rest at x = -5 M and +5 M,
moving-puncture gauge, refinement following the punctures, corrected horizon finder,
160 M; six tracers with angular momentum about the collision axis (one released at
rest on the symmetry plane). New script `analysis/diag/tracers_headon.py`, figure
`analysis/diag/figs/tracers_headon_v4.png`.
- The one exact invariant, L_x = y u_z - z u_y (axisymmetry about the collision axis in
  any gauge that keeps it): relative change below 1.4e-4 for every tracer up to
  t = 40 M, below 4.4e-4 up to t = 60 M (the punctures meet near t = 49 M), and below
  1.0e-3 over the whole run. The largest values come in a burst between t = 90 and
  115 M that all five orbiting tracers show at the same time, after which the change
  is back near 1e-4. What passes them at that time (they are 10 to 16 M from the axis)
  was not determined; the mesh is Cartesian with refinement boxes, so the numerical
  spacetime is axisymmetric only up to its truncation error.
- The tracer released at rest falls in and is removed at the lapse threshold at
  t = 77.6 M; its L_x stays at 4e-14 (round-off).
- Common apparent horizon first found at t = 49.25 M. Its mass is 1.0020 at t = 55 M
  and 1.0021 to 1.0025 from t = 60 M to the end (rms expansion on the surface 1e-6 at
  the end), against a total mass of 1; between t = 60 and 110 M successive searches
  alternate between two values 5e-4 apart. A merged black hole cannot be heavier than
  the total mass, so the excess of 0.25 percent is an error of the evolution at this
  resolution; the single puncture at dx = M/8 gained 0.18 percent in the same way.
  The radiated energy of this collision is smaller than that and is not resolved here.

## Stable cluster with Monte Carlo sampling, N = 10^2, 10^3, 10^4 (09:25)

`st/yc0819_mc_n{100,1000,10000}_v4`: independent random draws instead of the stratified
sampler, no perturbation, four passes plus compensation, 500 M. Figure:
`analysis/diag/figs/cluster_osc_mc.png` (with the stratified run to 600 M).
- N = 10^4: the same oscillation as with the stratified sampler, at the same times and
  sizes. Extrema of the lapse minus equilibrium, Monte Carlo against stratified:
  +0.0059 at 99 M (+0.0065 at 108), -0.0056 at 209 (-0.0062 at 208), -0.0078 at 278
  (-0.0108 at 280), +0.0084 at 316 (+0.0061 at 316), -0.0079 at 347 (-0.0065 at 359),
  +0.0125 at 386 (+0.0126 at 392), -0.0155 at 419 (-0.0103 at 423), +0.0128 at 458
  (+0.0088 at 464). This was the open test "a different sampler": the oscillation and
  its phase do not come from the stratification either. They belong to the model on
  this mesh.
- N = 10^3: the same up to t = 190 M; afterwards deeper minima (-0.016 to -0.024) and
  a mean that drifts down by 0.011; mean Lorentz factor up by 0.005.
- N = 10^2: the cluster does not hold. The central lapse falls from 0.81 to 0.68 at
  t = 200 M and 0.58 at t = 500 M, the mean Lorentz factor rises from 1.047 to 1.138,
  and the total momentum wanders to 0.025 of the rest mass. A hundred particles are a
  collisional system on this time scale.
- Particle-number statement for the stable model, from the stratified and Monte Carlo
  runs together: 10^4 and 10^3 particles keep the cluster for 300 M with the common
  oscillation; 10^2 do not.

## Stable cluster to 1200 M: the oscillation saturates (09:42)

Base run (seed 1, unperturbed, four passes plus compensation) continued through
`st/osc/long` and `st/osc/long2`. Half the swing of the (4 M smoothed) central lapse in
successive windows of 100 M, from t = 100 M: 0.005, 0.007, 0.010, 0.018, 0.021, 0.022,
0.019, 0.020, 0.019, 0.015 (the last for 1000 to 1100 M). The amplitude grows until
about t = 500 M and then stays between 0.015 and 0.022, two to three percent of the
lapse, for the following 600 M. The mean lapse ends 0.006 to 0.008 below equilibrium.
All 10^4 particles are kept; the mean Lorentz factor stays within 0.004 of its initial
value.

Against the two readings written before the continuation: "keeps growing" fails,
"saturates" holds. That is what the bunching reading predicted; it remains a reading,
since the size of the initial offset has not been varied in a controlled way. What is
established: the stable model stays bound and centred for 1200 M at ten thousand
particles, with a core oscillation that is the same for every sample and sampler and
is bounded at two to three percent in the central lapse.

Corrections and completions to earlier entries (found while the paper figures were
reduced, 10:00):
- "Stable model, compensated, three seeds": seed 3 was read while it was still running.
  Complete to 300 M, its fourth minimum is 0.7990 at t = 277 M (seeds 1 and 2: 0.7985
  at 281 M and 0.7924 at 277 M).
- "Horizon mass calibration: results", row dx = M/4: -3.9e-2 is the median of the
  Misner-Sharp mass over a wide shell; at this resolution the mass is not constant in
  radius, and at the horizon it is 0.9656 at t = 50 M (-3.4e-2).
- Extrema quoted for the long stable-cluster run are those of the 4 M smoothed lapse;
  the raw extrema are up to 4e-4 larger in size.
- "Growing oscillation: cancelling the cloud width": that run differs from the base run
  by up to 3.6e-3 (it lowers the slow excursion); the other four controls stay within
  6.5e-4 of the base run.

## Compact model y_c = 0.605 with the one-percent inward kick (10:08), prediction 5

`st/yc0605_v5`: 10^4 stratified particles, adaptive mesh, published deposition rule,
four passes plus compensation, 150 M. Figure:
`analysis/diag/figs/cluster_history_yc0605_v5.png`.
- No horizon and no particle lost in 150 M. The original reports a horizon at
  t = 109 M for this model.
- The central lapse (0.629 at t = 0) oscillates with a period of about 38 M and a
  growing swing: maxima 0.641, 0.650, 0.655 at t = 52, 90, 128 M; minima 0.616, 0.590,
  0.534 at t = 77, 104, 142 M. The radius enclosing 10 percent of the rest mass swings
  between 0.9 and 1.7 M at the end (1.42 M at the start); the half-mass radius is
  2.84 M until t = 120 M and 2.29 M at t = 150 M. Mean Lorentz factor 1.122 -> 1.136.
- The mesh refines at the last two minima (MeshBlocks 456 -> 512), and each refinement
  comes with a jump of the constraint norms (0.27 -> 1.1 at t = 104 M, 0.77 -> 1.2 at
  t = 140 M).
- Against the prediction ("collapses and forms a horizon"): not within 150 M. Whether
  the growing oscillation ends in collapse is not known from this run. Continuation to
  300 M submitted from the last dump (same directory).
- Difference from the original that is established: there the lapse of this model
  declines smoothly to collapse; here the same kind of core oscillation as in the
  stable model sits on top, growing by a factor of 2.5 to 3 per cycle in its minima.

## Reconfiguration test, first attempt: collapse (10:12); and what the original's figure shows

`st/reconf_yc0756_v4`: y_c = 0.756, 10^4 stratified particles compressed homologously
by (1.1)^(-1/3) in radius (density up by ten percent, velocities unchanged), static
mesh with dx = M/4, four passes plus compensation; chain stopped after its first
segment (t = 817 M).
- Central lapse 0.7520 at t = 0 (the equilibrium value), then 0.742, 0.749, 0.738,
  0.712, 0.688, 0.630, 0.585, 0.512, 0.401 at t = 5, 10, 30, 60, 80, 100, 120, 130,
  140 M: a contraction with small wiggles, ending in collapse. All particles are
  removed at the lapse threshold between t = 151.5 and 154.2 M; this input has no
  horizon finder and no mesh refinement, so the end of the collapse is not resolved.
- The original reports for this test no collapse: a core-halo structure, all particles
  kept. Its figure of the central lapse (read by eye): start near 0.75, an oscillation
  with a period of about 50 M whose swing GROWS for the first 250 to 300 M, to between
  0.695 and 0.775, then decays over the next 400 M, and a slow decline to 0.70 by
  2000 M.
- Two things follow.
  (1) The growing core oscillation that this log has chased on the stable model since
  06:47 is in the original's own data: growth of a coherent oscillation at the core
  period, saturation, decay. That it appears there with 10^6 particles, another code and
  another mesh is the strongest evidence so far that it is the collisionless response
  of these monoenergetic models to a coherent perturbation and not an artifact of this
  rebuild. (Still not a controlled test of ours.)
  (2) Our initial data for this test are inconsistent: the particles are compressed,
  the metric is the one of the unperturbed equilibrium (the lapse at t = 0 equals the
  equilibrium value, which gives it away). The original does not say how its
  perturbation is defined or how the initial metric is obtained. A near-critical model
  is the place where that matters.
- Next: initial data in which the conformal factor solves the Hamiltonian constraint
  for the perturbed particle distribution (radial solve), then the run again on the
  adaptive mesh with the horizon finder. No prediction is made for the outcome: the
  model is near critical, and with consistent data either the original's oscillation or
  a collapse is possible; the comparison quantity is the lapse history of the first
  300 M (initial value, period, growth of the swing).

## Consistent initial data for perturbed clusters (10:35)

`python/nrpic/st_cluster.py` (`PerturbedST`), used by `make_ic.py` by default when a
density or velocity perturbation is requested (file stem suffix `_hc`;
`--no-consistent-table` gives the old behaviour). The conformal factor solves the
Hamiltonian constraint for the perturbed matter, Laplacian psi = -2 pi D / psi with D
the coordinate energy density of the particles, by a radial fixed-point iteration.
42 tests pass. Figure: `analysis/diag/figs/ic_dpert_consistency.png`.

For y_c = 0.756 compressed by ten percent in density:

| | psi at the centre | lapse at the centre | total mass |
|---|---|---|---|
| unperturbed (and the old table) | 1.13940 | 0.75181 | 1 |
| consistent | 1.14339 | 0.74863 | 0.99689 |

- The old table violates the constraint by 9 percent of the central source; the new one
  satisfies it to 1e-9 (the round-off floor of the check).
- The consistent central lapse, 0.7486, is where the original's lapse curve starts.
- For the one-percent velocity kick the change of psi is 9e-7 (second order). The kick
  itself, with K_ij = 0 kept, violates the momentum constraint at first order in the
  kick; this applies to every kicked run here (and is not addressed).
- Two slips in the derivation I had handed over were corrected by the agent who
  implemented it (a factor 2 pi in the monopole; which conformal factor lowers the
  momenta in the sampler); the tests check the corrected forms.

Reconfiguration rerun submitted: `st/reconf_yc0756_hc`, same particles as the run that
collapsed, consistent table, adaptive mesh with the horizon finder, cells of M/4 inside
8 M, to 600 M. No prediction for the outcome (near-critical model). Comparison
quantities: lapse at t = 0 (0.7486 expected by construction), period and growth of the
swing over the first 300 M against the original's figure.

## Compact model y_c = 0.500 with the one-percent inward kick: collapse (10:43), prediction 5

`st/yc0500_v5`: 10^4 stratified particles, adaptive mesh, published deposition rule,
four passes plus compensation, corrected horizon finder, 120 M. Figure:
`analysis/diag/figs/cluster_history_yc0500_v5.png`.
- The central lapse stays between 0.545 and 0.556 until t = 50 M, dips to 0.514 at
  70 M, recovers to 0.536 at 80 M and then falls: 0.38, 0.23, 0.045, 0.016 at t = 90,
  100, 110, 120 M. The mass shells contract together from t = 85 M.
- Apparent horizon first found at t = 104.3 M. Its mass grows as the rest of the
  cluster falls in: 0.831 at first detection, 0.949 at 106.3 M, 0.992 at 109.3 M,
  0.9992 at 114.3 M, 1.0000 at 119 M; the total mass is 1.
- Removal at the lapse threshold starts at t = 104.6 M; at t = 120 M three of the 10^4
  particles are left and 1.0235 of 1.0238 in rest mass has been removed.
- As predicted, the model collapses to a black hole whose horizon mass equals the total
  mass. The horizon appears at 104 M here against 73 M in the original (2e6 particles),
  which itself calls its collapse time dependent on the particle number and the initial
  noise. The other compact model, y_c = 0.605, is also late here (no collapse by 150 M
  against 109 M). The common direction of the difference is noted; its cause is not
  determined.
- After removal starts, the centre of mass and the momentum sums of the diagnostics are
  those of the few particles left and carry no information.

## Prolate collapse, first production attempt: the mesh outgrows the memory (10:49)

`prolate/e09_v5`: 10^4 Monte Carlo particles, cells of M/4 over the spheroid at the
start (512 MeshBlocks), published deposition rule, two plain filter passes, up to eight
levels. The run stops at t = 17.1 M (smallest lapse 0.71, long before any black hole):
the refinement asks for 1912 MeshBlocks, above the limit of 1536; at 1408 blocks the
run already used 48 GB of the 80 GB of the card. The dust-collapse run with a lattice
start grew from 288 to 456 blocks over its whole collapse.

Reading, not tested: the Monte Carlo sample is noisy on cells that hold 0.2 particles
on average, the noise reaches the metric, the refinement indicator responds to it, and
each new level makes the source more granular. This is the situation the level cap was
meant for, and the cap cannot be used here later, near the black hole.

Second attempt `prolate/e09_v6` (submitted): cells of M/2 over the spheroid at the
start (1.6 particles per cell), four filter passes with compensation, block limit
2200, otherwise the same. Written before the run: if the reading is right, the block
count stays within a few hundred of its starting value until the lapse has fallen well
below 0.5; if the count climbs as before, the refinement is driven by the collapsing
spheroid itself (a spindle 20 M long needs fine cells along its whole length) and the
number of levels has to be limited instead.

## Unbound model y_c = 0.283 with the one-percent inward kick: dispersal (11:09), prediction 5

`st/yc0283_v5` (negative binding energy), same settings as the other compact models;
the job reached t = 268.6 M of 300 M at the time limit. Figure:
`analysis/diag/figs/cluster_history_yc0283_v5.png`.
- The central lapse (0.405 at t = 0) dips to 0.388 at t = 31 M and then rises: 0.49,
  0.76, 0.86, 0.94, 0.964, 0.976 at t = 60, 80, 100, 150, 200, 268 M.
- All particles are kept. The half-mass radius goes from 1.69 M to 47.6 M and the mass
  shells move apart at constant speed from t = 100 M on; the mean Lorentz factor falls
  from 1.325 to 1.047.
- As predicted, and as in the original (which notes that the spherical calculation of
  the 1980s reported a black hole for this model): the cluster disperses.

State of the five-model sequence at 10^4 particles: y_c = 0.900 and 0.819 hold for
300 M; 0.500 collapses to a black hole (horizon at 104 M, mass equal to the total);
0.283 disperses; 0.605 has not collapsed by 150 M and is being continued.

## Migration of the unperturbed y_c = 0.5 model, first 913 M (11:39)

`st/migration_yc0500_v4` (10^4 stratified particles, no perturbation, four passes plus
compensation, static mesh; chain continues to 2500 M). All particles kept. Extrema of
the central lapse against the values read by eye from the original's figure (2e6
particles):

| | here | original |
|---|---|---|
| start | 0.552 | 0.56 |
| first maximum | 0.913 at t = 228 M | about 0.91, t = 230 to 350 M |
| first minimum | 0.578 near t = 450 M | about 0.57 to 0.60, t = 450 to 520 M |
| second maximum | 0.892 at t = 650 M | about 0.90, t = 680 M |
| second minimum | 0.763 near t = 800 M | about 0.76, t = 830 M |

The large expansion, the recontraction and the following oscillation of the original
are reproduced with ten thousand particles, in size and in timing to within what can be
read from the published figure; the start of the expansion is earlier here (see the
direction tests). Mean Lorentz factor 1.172 at the start, 1.012 at its lowest.

## Compact model y_c = 0.605, continued: collapse (11:52), prediction 5

`st/yc0605_v5` continued from 150 M. The central lapse falls from 0.62 at t = 160 M to
0.53, 0.36, 0.17 at t = 170, 180, 190 M. Apparent horizon first found at t = 191.0 M
(mass 0.789), removal of particles from t = 191.9 M. Horizon mass 0.908, 0.953, 0.990,
0.9973, 0.9985, 0.9972, 0.9994 at t = 195, 200, 210, 220, 240, 260, 280 M: it reaches
the total mass to within 0.3 percent once the cluster has fallen in. Seven of the 10^4
particles are left at t = 297 M.
The prediction (collapse and a horizon) holds, 82 M later than the original's 109 M.
With y_c = 0.500 (104 M against 73 M) both compact models collapse later here than in
the original.

## Reconfiguration rerun with consistent initial data: it contracts again (11:52)

`st/reconf_yc0756_hc` (ten-percent compression, conformal factor solving the constraint
for the compressed matter). Central lapse 0.7488 at t = 0 (0.7486 by construction),
then 0.7448, 0.7480, 0.7466, 0.7376, 0.7351, 0.7213, 0.7124, 0.6857, 0.6295, 0.5761 at
t = 5, 10, 20, 30, 40, 50, 60, 80, 100, 120 M. The inconsistent run had 0.742, 0.749,
0.747, 0.738, 0.736, 0.72, 0.712, 0.688, 0.630, 0.585 at the same times. The two
histories agree to 0.01: the inconsistency of the first attempt was not what made it
collapse. A ten-percent compression of this near-critical model leads to collapse in
this code, with either initial metric.

The original's perturbed run oscillates and keeps all its particles. What its "density
perturbation of ten percent" is (sign, shape, how the metric is obtained) is not
stated. One reading that can be tested: a reduction instead of an increase. Submitted:
`st/reconf_yc0756_hc_m`, the same model expanded homologously (density down by ten
percent), consistent initial data (central lapse 0.7552, total mass 1.0034), adaptive
mesh, 600 M. Written before the run: if the original perturbed downward, this run
shows what its figure shows: an oscillation of the central lapse with a period near
50 M whose swing grows over the first 250 to 300 M to several hundredths and then
decays, all particles kept. If this run does something else (a quiet oscillation of
constant size, or a slow expansion), the reading is wrong and the difference from the
original stays unexplained.

## Two runs out of memory at start; memory rule for adaptive runs (11:53)

- `st/osc/dx2` (half cell size): my override put level 7 over the whole 15.9 M region,
  which the nesting rule turned into 3200 MeshBlocks. Resubmitted as `st/osc/dx2b` with
  level 7 inside 7.9 M only (456 blocks): the cells are halved where the oscillation
  lives (the core and 85 percent of the mass), not over the whole cluster.
- `jeans/n1e4_v5`: 1128 MeshBlocks, block limit 3072. With adaptive refinement the
  arrays are sized for the block limit, not for the blocks in use: measured 31 to 32
  MiB per allowed block (16^3 cells, four ghost cells) in three adaptive runs (32.3 GB
  at a limit of 1024, 20.4 GB at 640, 48.3 GB at 1536). A limit of 3072 asks for
  about 97 GB on an 80 GB card. Resubmitted as `jeans/n1e4_v6` with a limit of 1500.
- The second prolate attempt, not yet started, had a limit of 2200 (70 GB); replaced
  by `prolate/e09_v7` with 2000.

Addendum (12:05), end of the reconfiguration rerun with ten-percent compression
(`st/reconf_yc0756_hc`, stopped after the collapse): apparent horizon first found at
t = 147.2 M (mass 0.990), all particles removed between t = 148.8 and 160 M, horizon
mass 0.9962 to 0.9970 from t = 149 to 160 M. The total mass of this initial data set is
0.99689 (it is lighter than the unperturbed cluster because it is more tightly bound);
the horizon mass at the end, 0.99698, equals it to 1e-4. The collapse is resolved this
time (adaptive mesh, finder), and it conserves the mass of the consistent initial data.

Corrections to the cluster-sequence entries, found while the sequence figure was
reduced from the full histories (12:10); the entries had been written from values
sampled every 10 M:
- y_c = 0.283: the run ends at t = 270.06 M (not 268.6 M); the half-mass radius of
  47.6 M is the value at 270 M. Its central lapse starts at 0.4054 where the equilibrium
  model has 0.3994, 1.5 percent higher (the probe averages the eight central cells of
  M/4; for the other models the offset is 0.1 to 0.3 percent).
- y_c = 0.500: the central lapse before the collapse ranges from 0.538 (t = 35.5 M) to
  0.561 (46.2 M), not 0.545 to 0.556; removal of particles starts at t = 104.41 M.
- y_c = 0.605: the half-mass radius is not constant at 2.84 M until 120 M; it swings
  between 2.62 and 2.91 M between t = 100 and 125 M.
- A difference from the original not noted before: after the horizon forms the central
  lapse falls to 0.02 to 0.05 here, while the original's curves level off near 0.2.
  This is a statement about the coordinates at the centre; which gauge setting makes
  the difference was not looked into.
Figure for the paper: `paper/figures/fig_clusters.png` (radii about the origin, as in
the original; the diagnostic figures use the centre of mass; the two differ by less
than 0.6 percent while most particles are present).

## Near-critical model with the density reduced by ten percent: slow breathing (12:22)

`st/reconf_yc0756_hc_m`, first 409 M (chain continues to 600 M). All particles kept.
Central lapse 0.7554 at t = 0 (0.7552 by construction), rising to 0.811 at t = 100 M
and 0.819 at t = 160 M, falling to 0.728 at t = 251 M, rising again to 0.827 at
t = 400 M, with ripples of about 0.01 on top. This is a slow breathing of the whole
cluster with a period of 250 to 300 M and a swing of 0.05.

Against the prediction: the original's figure shows an oscillation with a period near
50 M whose swing grows and decays, around a lapse that stays near 0.73 to 0.76. This
run does something else. The reading "the original reduced the density" is not
supported. Neither sign of a homologous ten-percent perturbation reproduces the
original's curve: compression collapses, expansion breathes slowly.

What the original's curve does look like is the core oscillation of our weakly
perturbed models (growing, at the core period, then levelling off). Test of that
reading, submitted: `st/yc0756_unpert`, the same model without any imposed
perturbation, static mesh with cells of M/4, compensated filter, 800 M. Written before
the run: an oscillation of the central lapse at a period of 50 to 55 M whose
half-swing grows to between 0.03 and 0.05 somewhere between t = 200 and 500 M and then
stops growing, around a mean lapse within 0.01 of the equilibrium value 0.752, all
particles kept. If the swing stays below 0.02, or the model collapses or breathes
slowly instead, the reading is wrong.

## Near-critical model with the density reduced by ten percent, complete to 600 M (12:34)

`st/reconf_yc0756_hc_m`. Figure: `analysis/diag/figs/cluster_history_yc0756_dpert.png`
(with the compressed run). All 10^4 particles kept; centre of mass within 0.06 M.
- The entry written at t = 409 M called the motion a slow breathing with a period of
  250 to 300 M. With the whole run in view that holds only for the first 250 M (rise of
  the central lapse to 0.82, fall to 0.73). From t = 250 M on the lapse oscillates
  faster, between about 0.72 and 0.83, with successive extrema 60 to 100 M apart, and
  the mass shells oscillate together with it; the radius enclosing 90 percent of the
  rest mass ranges from 6 to 9 M (6.4 M at the start), the 10 percent radius from 1.8
  to 3.8 M (2.4 M at the start).
- So this run does show large oscillations with every particle kept and an extended
  outer part, which is the kind of outcome the original describes. It still differs
  from the original's curve in what can be compared: there the lapse oscillates about
  0.74 to 0.75 (at or slightly below the equilibrium value 0.752) from the start and
  with a period near 50 M; here it first moves up, and oscillates about 0.77.
- The statement of the previous entry stands in this form: neither sign of a homologous
  ten-percent perturbation reproduces the original's lapse curve; the reduced-density
  run shares its qualitative outcome (oscillation, no collapse), the compressed run
  does not.

## Prolate collapse, attempt with compensated filter: blocks again exceed the limit (12:49)

`prolate/e09_v7` (four passes plus compensation, block limit 2000; the override meant to
coarsen the starting mesh had no effect, because the input also fixes a static level-4
region, so the start is again 512 blocks with cells of M/4).
- Up to t = 15 M the block count stays at 512; the first attempt (two plain passes) had
  gone to 960 blocks before t = 5 M. The smoother source removed the early refinement.
- At t = 16 M the count rises to 764 and at t = 16.3 M the refinement asks for 2584
  blocks. The first attempt failed at the same stage (t = 17.1 M, smallest lapse 0.72
  in both).
- Against the prediction: both parts of it occur. The early refinement was driven by
  the noisy source and is gone; the later one comes back at the same time with the
  smoother source, so it belongs to the collapse itself (the spheroid is contracting
  towards a spindle 20 M long), as the alternative in the prediction said.
- Next attempt `prolate/e09_v8`: one level fewer (finest cells M/16 instead of M/32),
  otherwise as v7.

## Stable cluster at half the cell size: the oscillation does not shrink (12:58)

`st/osc/dx2b` (cells of M/4 inside 7.9 M, M/2 outside; otherwise the base run
`st/ctl/s1_nf4c`: same particles, four passes plus compensation, 300 M). Figure:
`analysis/diag/figs/cluster_osc_dx.png` (lapse minus equilibrium; amplitude and mean of
successive extrema; total particle energy).
- Central lapse minus its equilibrium value, extrema (time: value). Base: 24: +0.0037,
  108: +0.0065, 158: -0.0023, 208: -0.0062, 280: -0.0108. Half cell size: 23: +0.0036,
  107: +0.0035, 156: -0.0070, 204: -0.0110, 276: -0.0158. Fit of the half-swing:
  0.0006 + 1.34e-5 t (base), 0.0006 + 1.70e-5 t (half cell size).
- The first maximum is the same to three percent, and the half-swing grows at the same
  rate or slightly faster. What changes is the mean about which the lapse swings: it
  ends 0.0039 below equilibrium in the base run and 0.0073 below at half the cell
  size. The total particle energy moves by -2.0e-3 to +0.9e-3 (base) and -1.2e-3 to
  +2.2e-3 (half cell size) of its initial value.
- Against the prediction written at 08:52 (a second-order discretization error would
  drop both the first maximum and the amplitude at 280 M by about four): refuted. Both
  stay. The common initial offset and the growth of the oscillation do not come from
  the cell size of the mesh.
- Limit of this test: at half the cell size each cell holds one eighth of the
  particles, so the source is noisier there. The larger drift of the mean may come
  from that; no run separates the two. The cause of the oscillation stays not
  determined. Tested and excluded so far: random seed, sampler, particle number (10^3,
  10^4), time step, constraint damping, constraint relaxation, cloud width, cell size.

## Cluster with two overdensities: the moving fine regions outgrow the block limit (12:58)

`jeans/n1e4_v6` (block limit 1500, 1128 blocks at start, time step 3.9e-3 M, 59 s per
100 steps) stopped at t = 1.1 M: the refinement asked for 1800 blocks.
- Cause, read from the tracker files and the block counts in the history: the two
  overdensities move at their orbital speed (0.10 M in y by t = 1.1 M, the trackers
  follow), and the finest region around each (radius 0.4 M, blocks 0.25 M wide) then
  no longer lines up with the block layers. A sphere of 3.2 block widths covers four
  blocks per direction when aligned and five when not, and every coarser level has to
  wrap the larger set. The count went 1128, 1464, 1128, 1800 within 0.1 M.
- Resubmitted as `jeans/n1e4_v7`: finest region of radius 0.3 M around each tracker
  (2.4 block widths: three or four blocks per direction), block limit 2100 (about 72 GB
  by the measured 32 to 35 MiB per allowed block). Same particles and envelope.
- Cost: 100 M at this time step are 25600 steps, five to seven hours on one card.
- Written before the run. The original reports horizons at t = 8.475 and 8.525 M and a
  common horizon at 64.16 M. Each overdensity here has about 1200 particles. If their
  collapse is cold free fall, as in the dust ball, whose timing did not depend on the
  particle number, both horizons appear between 8 and 9.5 M, each with a mass below
  0.12 at formation that grows as the envelope falls in. The time to the common
  horizon depends on the orbit after formation, which the 7600 envelope particles
  resolve poorly; expected within 25 percent of 64 M. A first horizon later than 12 M
  would mean that the overdensities are supported by noise or by the softened field,
  and the mesh and filter then need another look before any comparison.

## Correction: central density with the level cap is above the cycloid, not on it (13:35)

Found by the agent that built the appendix tables from the run directories, checked by
me. The entries on the dust runs with the adaptive cloud level say that the cap "keeps
the central density on the cycloid". On the logarithmic axis of the figure a difference
of ten percent is not visible next to the drop by a factor of three of the uncapped
run. From the histories (central reading over the cycloid at the same central proper
time; the reading is the mean of the eight central cells after the filter):
- published rule (`os/nocap_sc`): 1.000 to t = 4 M, 0.993 to 1.002 to t = 6 M, then
  0.27 to 0.52 after the centre is refined to h/4 (t = 7.3 M), back to 1 by t = 12 M;
- unlimited cap (`os/adapt_sc`): 1.017 at t = 4 M, 1.105 at 6 M, 1.12 to 1.135 from
  6 to 10 M, back to 1 at 11 to 12 M;
- cap at most one level coarser (`os/adapt_mc1`): as the unlimited cap to t = 7.3 M,
  then 1.28 to 1.49.
Is the matter more concentrated with the cap, or only the deposited density? The
particle snapshots of the three runs agree: mean radius of the innermost 8, 64, 512
particles equal to 1e-3 at t = 6 and 8 M (0.24329 against 0.24324; 0.22247 against
0.22220), radii enclosing 2, 10, 50 percent of the mass equal to 1e-3. So the matter
is the same and the reading differs.
Explanation, with its test. The particles sit on a regular lattice that contracts
homologously; a cloud lattice of nearly the same spacing beats against it, and at the
centre of symmetry the beat has the same sign in all three directions. Written before
the calculation: if that is the cause, depositing the particle snapshot of the uncapped
run in Python with clouds on the lattice level (cells of h), spread uniformly on the
leaves, one binomial pass, mean of the eight central leaves, gives 1.10 times the
deposit with clouds on the leaf level at t = 6 M, and the ratios between the three
rules at t = 8 to 9 M (one-level cap over unlimited cap 1.21 to 1.27; published rule
over unlimited cap 0.28 to 0.33). Result: 1.017 at t = 4 M, 1.105 at t = 6 M; at t = 8
and 9 M the ratios are 1.20 and 1.25, and 0.28 and 0.33. Confirmed to the digits read.
The excess is a property of a regular lattice with about one particle per cloud cell;
it is not a different collapse and not an error of the conservative mapping.
What this changes: the sentence in the paper, and the table entry, must say that the
cap replaces the drop of the central reading to one third by an excess of up to 14
percent (49 percent with the one-level cap).

Other items from the same audit, checked against the run files:
- Migration: with the full history the first minimum of the central lapse is a double
  dip, 0.591 at t = 400 M and 0.541 at 437 M (earlier entry: 0.578 near 450 M, from
  values every 10 M); second maximum 0.894 at 631 M (entry: 0.892 at 650 M); second
  minimum 0.753 at 783 M (entry: 0.763 near 800 M). Three particles leave the outer
  boundary (t = 1816, 1999, 2405 M); "all particles kept" holds to 1800 M.
- Head-on run: common-horizon mass at the end 1.00257 (entry: 1.0021 to 1.0025).
- Tracers around the single puncture sit in cells of M/4 to M/2, not M/2 to M.
- In ten runs the input file copied into the run directory differs from what the code
  read, because the problem input was edited while the job was queued; the parameter
  dump of the first restart file is the record. The added keys had their defaults.

## Is the disturbance of a forming black hole by coarser clouds a lattice effect? (13:36)

The level cap was judged on the dust ball only, whose particles sit on a regular
lattice. The beat found above puts coherent errors of 10 to 50 percent into the source
at the centre; the earlier negative result (horizon mass after the matter is removed
drifts by -0.13 percent with the published rule and by +0.65 percent with the unlimited
cap) may therefore belong to the lattice and not to coarser clouds as such.
Control: the same dust ball sampled at random (Monte Carlo, 9328 equal-mass particles,
total rest mass equal to the continuum value), once with the published rule
(`os/mc_nocap`) and once with the unlimited cap (`os/mc_adapt`); everything else as in
`os/nocap_sc` and `os/adapt_sc`.
Written before the runs. If the lattice beat causes the disturbance, the two runs agree
in the horizon mass at t = 60 M to 0.2 percent of M, and the capped run has the lower
constraint norm throughout. If coarser clouds disturb the black hole by themselves, the
capped run ends 0.5 percent or more away from the published-rule run, as on the
lattice. A random sample is noisier than the lattice, so the horizon mass of either run
may differ from M by more than on the lattice; the test is the difference between the
two rules on the same particles.

## Migration of the unperturbed y_c = 0.5 model, complete to 2500 M (13:45)

`st/migration_yc0500_v4` (10^4 particles, static cells of M/4, four passes plus
compensation). Figure: `paper/figures/fig_migration.png` (central lapse with the
original's extrema, read by me from its rendered figure; radii enclosing 10, 50, 90
percent of the rest mass).
- Central lapse: 0.552 at the start (equilibrium 0.550); extrema (value at t/M): 0.913
  at 228; 0.591 at 400, 0.637 at 417, 0.541 at 437; 0.894 at 631; 0.753 at 783; 0.853
  at 940; 0.795 at 1072; 0.853 at 1184; 0.792 at 1329; 0.840 at 1472; 0.802 at 1583;
  0.833 at 1726; 0.804 at 1853; 0.826 at 2001; 0.816 at the end.
- Original, read from its figure: 0.56; plateau 0.905 from 200 to 320; oscillating
  between 0.55 and 0.63 from 440 to 520, lowest near 490; 0.90 at 670; 0.765 from 830
  to 880; 0.865 at 1040; 0.78 at 1160; 0.865 at 1320; 0.80 at 1450; 0.85 at 1600;
  about 0.83 to 0.84 near 2000. (My earlier reading of its first minimum, 0.57 to
  0.60, was of the middle of that band; the lowest point is 0.55.)
- Same sequence of states, same values of the first two maxima and of the first two
  minima to 0.01 to 0.02. Two differences: every extremum after the first maximum comes
  earlier here, by 50 M at the first minimum and by 130 M at the fifth maximum (full
  cycles of 250 to 290 M here against 290 to 310 M there); and the later swings are
  smaller here (0.795 to 0.853 against 0.78 to 0.865). The lapse about which the
  cluster settles is 0.82 here and 0.83 to 0.84 there; the model of equal binding
  energy on the stable branch has 0.859.
- Radii: half-mass radius 2.29 M at the start, 12.4 M at 230 M, 4.8 to 6.9 M after
  900 M, 5.5 M at the end; 90 percent radius 3.46 M at the start, 19 to 26 M after
  900 M. Four of 10^4 particles leave the outer boundary (4e-4 of the rest mass), none
  is removed.
- Cause of the shorter cycle: not determined. No run varies anything between the two
  (particle number 10^4 against 2e6, static against adaptive mesh, filter).
