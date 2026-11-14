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

## Unperturbed near-critical model y_c = 0.756 to 800 M (13:50)

`st/yc0756_unpert` (10^4 particles, static cells of M/4, four passes plus compensation,
no perturbation). Figures: `analysis/diag/figs/cluster_osc_yc0756.png`,
`paper/figures/fig_nearcritical.png` (with both perturbed runs and the extrema of the
original's curve, which I read from its rendered figure).
- Central lapse minus equilibrium (0.7518): within 0.01 to t = 150 M; then an
  oscillation with minima at 207, 262, 306, 362, 415, 474, 532, 581, 657, 720, 771 M
  (spacings of 45 to 59 M up to 580 M). Half-swing of successive extrema: 0.015 at 207
  to 260 M, 0.023 to 0.025 at 284 to 341 M, 0.031 to 0.036 at 362 to 474 M (largest
  0.036 at 415 M), 0.011 to 0.025 from 560 M on. Range of the lapse 0.696 to 0.772.
- Mean of successive extrema: 0.013 below equilibrium at 207 to 260 M, 0.012 to 0.020
  below at 362 to 474 M, 0.032 to 0.037 below at 745 to 771 M. Mean lapse of the whole
  run 0.739. The mean Lorentz factor of the particles rises by 1.2 to 1.5 percent at
  the end. All 10^4 particles kept. Radius enclosing 90 percent of the rest mass 5.6 to
  7.3 M (6.15 M at the start), 10 percent radius 1.6 to 2.8 M (2.32 M).
- Against the prediction (11:58 entry): period 50 to 55 M: yes (45 to 59 M). Half-swing
  growing to 0.03 to 0.05 between 200 and 500 M and then no longer growing: yes (0.036
  at 415 M, smaller afterwards). All particles kept: yes. Mean within 0.01 of
  equilibrium: no. The mean is 0.01 to 0.02 low from 200 M and 0.03 to 0.04 low at the
  end, and is still falling when the run stops; the core is slowly becoming more
  compact. Whether that ends in collapse later was not followed.
- Comparison with the original's perturbed run (its figure, read by eye, accuracy
  about 10 M and 0.005): there the oscillation grows from the start, the extrema reach
  0.696 and 0.777 at 250 to 275 M (half-swing 0.04), the spacing of maxima is 50 to
  55 M, the swing decays by 600 M, and the lapse then falls slowly, 0.735 at 800 M and
  0.70 at 2000 M (stated in its text). The unperturbed run here has the same period,
  the same largest swing (0.036 against 0.04), the same decay and the same slow fall of
  the lapse (0.72 at 800 M against 0.735); its largest swing comes about 150 M later.
- What this supports and what it does not. Supported: the behaviour the original shows
  for its perturbed model is the behaviour of the unperturbed model here, earlier by
  150 M. A homologous change of the density by ten percent of either sign does
  something else (+10 percent: collapse at 147 M; -10 percent: oscillation about 0.78).
  Not shown: what the original's perturbation was. A perturbation that starts the same
  oscillation at a larger amplitude without changing the mean structure would give its
  curve; no run here tests a particular form.

## Prolate collapse, complete to 45 M (14:05)

`prolate/e09_v8` (10^4 Monte Carlo particles with reflection and half-turn symmetry,
four passes plus compensation, finest cells M/16, at most 1352 MeshBlocks).
- Largest Kretschmann scalar on the axis: 63 at t = 20 M at z = -5.0 M, 527 at
  22.25 M at z = -4.6 M, 761 at 25 M at z = -2.7 M, largest value 1203 at 27.75 M at
  z = -0.66 M, 464 at 30 M. The maximum starts near the ends of the spindle and moves
  inward, as the original describes (two maxima near the ends, within the matter).
- First apparent horizon found at t = 32.0 M (searches every 0.25 M), irreducible mass
  0.929. The original shows the configuration "after apparent-horizon detection" at
  32 M and gives focusing at 20.5 M and the narrow spindle at 27.75 M.
- Particles are removed from t = 33.8 M; all 10^4 are removed by the end (removed rest
  mass 1.0981, the rest mass of the data). Smallest lapse 0.017 at the end.
- Horizon mass: rises to 0.9494 at t = 44.25 M and is 0.9489 at 44.75 M. That is five
  percent below the total mass M. The original states agreement of the horizon mass
  with the initial mass to 1e-3 for this test.
- Open at this point: where the five percent are. Two checks, written before their
  results. (i) Misner-Sharp mass of the last slices (the black hole is nearly
  spherical by then): if the slice mass outside the horizon is 1.00, the horizon
  reading is low on this mesh; if it is 0.95, the spacetime has lost the mass. (ii)
  The Monte Carlo dust ball with the published rule, which is running (`os/mc_nocap2`):
  if a random sample of 10^4 particles by itself costs several percent of horizon mass
  through its noise, that run also ends between 0.93 and 0.98 of M; if it ends within
  0.5 percent of M, the deficit belongs to the prolate collapse (its shape, or its
  finest cells of M/16 against M/26 in the dust runs).

## Monte Carlo dust ball with the published rule: refinement runs away (14:03)

`os/mc_nocap` (block limit 640) stopped at t = 6.6 M asking for 785 blocks;
`os/mc_nocap2` (limit 1800) stopped at t = 8.8 M asking for 1884. The lattice run
needs 456 blocks in all. `os/mc_adapt` (unlimited cap, limit 640) stopped at t = 10 M
asking for 974; `os/mc_adapt2` (limit 1800) is running.
- With a random sample of 10^4 particles, one plain filter pass and clouds on the
  finest level, the curvature-based refinement follows the sampling noise: every
  refinement makes the source noisier (one eighth of the particles per cell), which
  asks for more refinement. The lattice has no such noise.
- The control is therefore repeated with the filter of the prolate run (four passes
  plus compensation), which kept a random sample within 1352 blocks: `os/mc_nocap3`
  (published rule) and `os/mc_adapt3` (unlimited cap), block limit 2000. The
  predictions of 13:36 and 14:05 carry over unchanged to this pair.

## Prolate collapse: where the five percent are (14:12)

Check (i) of the previous entry. Figure: `analysis/diag/figs/slicemass_prolate_v8.png`
(Misner-Sharp mass against areal radius for the ten restart dumps; the slices before
the horizon forms are far from spherical and their profiles mean little).
- Horizon mass history from the finder: 0.929 at first detection (32.0 M), largest
  value 0.9666 at 33.75 M, then falling steadily: 0.9635 at 35 M, 0.9567 at 40 M,
  0.9489 at 44.75 M (0.0016 per M at the end, not levelling off).
- Slice at t = 45 M: 2m/R = 1 at R = 1.84 M, M_H = 0.92 with a spread of 0.03 over
  angle (the finder's 0.949 lies within it). The mass function is 0.92 to 0.95 out to
  R = 5 M, rises through 0.96 to 0.98 between 10 and 20 M, and reaches 0.999 at 50 to
  100 M (flagged "not flat" by the tool).
- Reading against the two outcomes I had written: neither as stated. The horizon
  reading is not low: the slice agrees with it. The spacetime has not lost the mass
  either: the total at large radius is 0.999. Five to eight percent of the mass lie
  outside the black hole, between 5 and 50 M, at a time when every particle has been
  removed, so it is field content: constraint-violating and radiative parts are not
  separated by this diagnostic.
- Constraint norm: largest value 49.7 at t = 27.7 M, the time of the largest
  curvature. The lattice dust run peaks at 1.9.
- What is established: at 10^4 particles and finest cells of M/16 the horizon forms
  at the original's time, and its mass is 3 percent low at its largest and still
  falling at the end of the run, where the original reports agreement to 1e-3 (2e6
  particles, cells of M/64). What is not: how much of the deficit comes from the
  particle number and how much from the cell size. Check (ii), the Monte Carlo dust
  ball, tests the particle number alone in spherical collapse.

## Corrections to the two prolate entries (14:25)

Found by the agent that made the figure from the run files, checked by me.
- Constraint norm. I compared two different measures. On one measure, the square root
  of the volume-normalized integral of H^2, the prolate run peaks at 6.31 (t = 27.5 M)
  and the lattice dust run at 1.90: a factor of 3.3, not 25. (The combined norm of the
  history file peaks at 49.7 against 4.34, a factor of 11.)
- Motion of the curvature maximum. It does not move inward smoothly. The axis carries
  several separate condensations of particles, and the maximum jumps between them:
  |z| = 5.0 M at t = 20 M, 3.9 M at 24.25 M, jump to 2.8 M at 24.5 M, jump to 0.7 M at
  26.25 to 28 M, back out to 1.8 M at 28.25 M, then 1.3 M at 30 M and 0.7 M at 32 M.
  Inward overall, in steps. The two maxima are mirror images by construction of the
  sample. Before t = 18.5 M the maximum is off the axis, and its value jumps by a
  factor of 280 when the two finest levels appear at 15.75 M (resolution, not
  dynamics).
- The spindle at 10^4 particles is a chain of separate condensations along the axis
  (figure `paper/figures/fig_prolate.png`, third panel), not a smooth line.
- Particle removal runs from 33.78 M to 38.80 M. Largest energy density 0.82 at
  t = 23.5 M at |z| = 4.2 M.
- The method section of the paper says that prolate runs keep one or two plain filter
  passes; the run used four passes plus compensation. To be corrected in the text.

## Cluster with two overdensities: collapse on time, then failure at t = 11.9 M (14:35)

`jeans/n1e4_v7` (6000 envelope particles, 2000 in each overdensity; finest cells M/64
within 0.3 M of each tracker; removal below a lapse of 0.05; at most 1828 blocks).
- The overdensities collapse on time: the radius holding half of one overdensity's
  particles about its densest point falls from 1.08 M (t = 0) to 0.30 M (8 M) and
  0.06 M (9 M). The tracker stays within 0.03 M of that point from t = 7 M on.
  Smallest lapse 0.066 at t = 9.05 M; at 9.18 M the lapse drops below 0.05 and 1676
  particles are removed in one step (both cores). The original finds its horizons at
  8.475 and 8.525 M.
- No apparent horizon is reported by the finder at any time up to the failure.
- After the first removal the smallest lapse returns to 0.08 and then stays between
  0.045 and 0.055, with particles removed a few at a time. Between 9.4 and 9.8 M the
  particle energy sum rises by 12 percent of M at constant particle number: the few
  hundred particles still falling in reach large Lorentz factors near the centres.
- Constraint norm (volume-normalized integral of H^2): 6 at t = 5 M, 126 at 8 M, 258
  at 9.5 M, 16 at 11.5 M. (Square roots: 2.5, 11, 16, 4; prolate peak 6.3, dust 1.9.)
- At t = 11.94 M 640 particles are removed in one step and the fields are NaN in the
  next output. Chain stopped.
- Reading, not yet tested: a black hole of mass 0.09 to 0.12 M is 6 to 8 cells of M/64
  per mass (the original refines to M/256). On such a mesh the lapse at cell centres
  bottoms out near the removal threshold, so matter inside the black hole is removed
  only when it passes within a cell of the centre; until then it moves at large
  Lorentz factor where the metric is least resolved and feeds large sources back.
  The finder's stencil (eight points) is wider than a horizon of three cells' radius.
- Two runs, written before their results.
  `jeans/n1e4_v8`: as v7 with removal below a lapse of 0.1 (the threshold of the dust
  and cluster runs). If lingering matter caused the failure, this run passes 12 M, the
  particle energy sum no longer rises by more than 2 percent of M after the first
  removal, and the constraint norm after formation stays below the 258 of v7. If it
  fails near the same time, the cell size at the black holes is the cause.
  `jeans/n1e4_v9`: one more level (cells of M/128 within 0.15 M of each tracker), same
  threshold of 0.1; twice the steps. If the cell size is the cause, this run passes
  where v8 fails, and reports horizons within 1 M of the first removal of particles.

## Cluster with two overdensities: no black hole had formed; my reading was wrong (14:50)

Check on `jeans/n1e4_v7` before the reruns started. Misner-Sharp mass about the
tracker of one overdensity on the restart dump at t = 10 M
(`analysis/diag/figs/slicemass_jeans_v7_t10.png`): the largest 2m/R is 0.47 (0.50
without shell widening). There is no trapped surface around the collapsed core at
t = 10 M, 0.8 M after 838 of its 2000 particles had been removed at a lapse of 0.05.
- So the finder was right to report nothing, and the reading of the previous entry (a
  black hole of 6 to 8 cells per mass with matter lingering inside) is not supported:
  at t = 10 M there was no black hole for matter to linger in.
- What the data show instead: the lapse in the core fell below the removal threshold
  before a horizon existed; the removal took 0.05 M of matter out of each core; the
  lapse then recovered (0.08) and the collapse did not complete. In the dust and
  prolate runs the horizon came first (dust: horizon at 16.4 M, first removal at
  18.9 M; prolate: horizon at 32.0 M with a smallest lapse of 0.087, removal from
  33.8 M). Whether a horizon would have formed here without the removal is not known.
- The two runs submitted at 14:35 (`v8`, `v9`, removal at a lapse of 0.1) were
  withdrawn before they started: a higher threshold removes the core earlier still.
- New runs, written before their results. Removal tied to the horizon: particles are
  removed inside 0.8 of the smallest coordinate radius of a found horizon; the lapse
  threshold is lowered to 0.02 and kept only as a guard against failure.
  `jeans/n1e4_v10`: mesh of v7 (cells of M/64 at the trackers).
  `jeans/n1e4_v11`: one more level (M/128 within 0.15 M of each tracker).
  If the early removal aborted the collapse, v10 reports a horizon around each
  overdensity between 8.5 and 10 M with a mass between 0.05 and 0.12 M, and particles
  are removed only after that. If no horizon is reported in v10 by t = 11 M while the
  lapse falls below 0.02, cells of M/64 cannot form these black holes, and v11
  decides whether M/128 can.

## Monte Carlo dust ball: published rule runs away with either filter (14:50)

`os/mc_nocap3` (published rule, four passes plus compensation, limit 2000) stopped at
t = 10.2 M asking for 2024 blocks (400 blocks at 6.3 M, 799 at 6.7 M, 1933 at
10.1 M). `os/mc_adapt3` (unlimited cap, same filter) has 400 blocks at t = 7.5 M and
is running. `os/mc_adapt2` (unlimited cap, one plain pass) is at t = 33 M: at most
1779 blocks; first horizon at 16.35 M (lattice 16.39 M) with mass 0.9949; 0.9999 at
20.1 M when the last particle is removed; 1.0012 at 33 M.
- On a random sample the published rule cannot be run to horizon formation within
  2000 blocks; the capped clouds can, and give a horizon mass within 0.1 percent of M
  when the matter is gone.
- For the comparison at equal settings asked for at 13:36, both rules are repeated
  with one refinement level fewer (finest cells h/4 instead of h/8), four passes plus
  compensation: `os/mc_nocap4`, `os/mc_adapt4`, block limit 2100. The prediction of
  13:36 applies to this pair.

## Cluster with two overdensities at M/64 with horizon-based removal: no horizon (15:22)

`jeans/n1e4_v10` (mesh of v7; removal inside 0.8 of a found horizon; lapse guard 0.02).
- No particle is removed up to t = 9.34 M. The smallest lapse falls through 0.098
  (8.80 M), 0.049 (9.18 M), 0.026 (9.34 M); the particle energy sum rises from 1.075
  to 1.55 of M (core particles at Lorentz factors of 3 to 4); the constraint norm
  (integral of H^2) reaches 572 at 9.5 M.
- The finder, searching every 0.0625 M around each tracker, reports no horizon.
- At 9.37 to 9.43 M the lapse passes the guard (0.02) and 1806 particles are removed;
  the smallest lapse then rises again (0.027 at 9.59 M). Run stopped.
- Against the prediction of 14:50: the second branch. No horizon is reported while the
  lapse falls below 0.02: cells of M/64 do not form these black holes, with or without
  early removal. (The first branch, a horizon between 8.5 and 10 M, did not occur.)
- Why this is plausible, as an estimate and not a tested statement: a black hole of
  0.1 M forming from regular data has an isotropic horizon radius near 0.05 M, three
  cells of M/64, while clouds and filter spread each particle over about two cells.
  The runs in which horizons formed had 8 cells (prolate, compact clusters) and 13
  cells (dust) per horizon radius; M/128 gives 6, the original's M/256 gives 13.
- `jeans/n1e4_v11` (M/128, guard 0.02) is running. Added `jeans/n1e4_v12`: M/128
  with the lapse guard off, removal only inside a found horizon. Written before the
  results: if six cells per horizon radius suffice, both report horizons around
  t = 9 to 10 M and v11 removes no particle before its first horizon; if v11 again
  removes the cores at the guard without a horizon while v12 finds one later, the
  guard is what prevents formation on a marginal mesh; if neither finds a horizon,
  this test needs the original's cell size, which costs four times the steps of v7
  (about a day on one card for 100 M).

## Monte Carlo dust ball: published rule against capped clouds at equal settings (15:50)

`os/mc_nocap4` (published rule) and `os/mc_adapt4` (unlimited cap): the randomly
sampled dust ball (9328 particles), four passes plus compensation, one refinement
level fewer than the lattice runs (finest cells h/4 = M/13), both to 60 M with 400
blocks at most.
- Published rule: first horizon at 16.20 M with mass 1.0019; 0.9983 at 20 M (all
  particles removed at 20.0 M); 0.9971 at 30 and 40 M; 0.9973 at 60 M.
- Capped: first horizon at 16.58 M with mass 0.9990; largest 0.9992; 0.9944 at 40 M;
  0.9946 at 60 M.
- Norm of the Hamiltonian constraint (largest value in the interval, published /
  capped): 0 to 5 M 0.80 / 0.57; 5 to 10 M 1.77 / 0.70; 10 to 15 M 1.42 / 2.46; 15 to
  20 M 2.93 / 3.79; 20 to 30 M 0.92 / 2.27; 30 to 60 M 0.39 / 1.16.
- Against the prediction of 13:36. The masses at 60 M differ by 0.27 percent of M:
  more than the 0.2 percent of the first branch, less than the 0.5 percent of the
  second. The constraint norm of the capped run is lower only before 10 M and is 1.3
  times higher at formation and three times higher afterwards, which the first branch
  excluded. So the first branch (the disturbance is the lattice beat alone) is
  refuted; the second (as large as on the lattice) is not met either.
- What the three sets of runs show together.
  Lattice, finest h/8: published rule -0.13 percent at 60 M; capped +0.65 percent
  (unlimited), -1.1 percent (one level); capped central density 11 to 49 percent high
  from the lattice beat.
  Random sample, finest h/8: published rule cannot be run (more than 2000 blocks by
  10 M with either filter); capped within 0.15 percent of M to 41 to 43 M (two runs).
  Random sample, finest h/4: published rule -0.27 percent; capped -0.54 percent;
  capped constraint norm three times higher after formation.
- Conclusions that these support: (1) coarser clouds raise the constraint violation
  around a forming black hole and shift its mass also without a lattice, by a few
  tenths of a percent; (2) on a lattice the shift is larger and comes with the beat;
  (3) on a random sample the capped clouds are what keeps the refinement bounded at
  the deepest level, and the black hole they give there is within 0.15 percent of M;
  (4) with finest cells of M/13 the horizon mass is 0.3 to 0.5 percent low with either
  rule (six to seven cells per horizon radius).
- For the prolate question (check (ii) of 14:05): the randomly sampled dust ball with
  the published rule and the prolate run's filter ends 0.27 percent below M (finest
  cells M/13, coarser than the prolate run's M/16). A random sample of 10^4 particles
  does not by itself cost several percent of horizon mass in spherical collapse. The
  prolate deficit of 3 to 5 percent belongs to that collapse (its caustic stage), not
  to random sampling as such.

## Corrections from the second audit of the tables (16:10)

Found by the agent that extended the appendix tables from the run files and the
original's text; checked by me.
- Prolate collapse, what the original reports. I wrote (14:05, and in the brief) that
  the original states agreement of the horizon mass with the total mass to 1e-3 for
  the prolate test. It does not: that statement (its conclusions, and its dust
  section) is about the Oppenheimer-Snyder collapse. For the prolate test the original
  gives no horizon mass. The deficit found here (3 percent at the largest value, 5
  percent at 45 M and falling) is therefore a limitation of this run, measured against
  the total mass, and not a difference from a published number.
- Constraint norm, wording. The history column is the sum of H^2 sqrt(gamma) dx^3 over
  the cells with chi >= 1/16; it is not divided by a volume. The numbers quoted
  (square roots 1.90, 6.31, and those of the dust controls) are right; "volume-
  normalized" in the entries of 14:25 and 14:35 is wrong.
- Capped Monte Carlo dust runs at full depth (`mc_adapt2`, `mc_adapt3`): they did not
  run to 60 M; the jobs reached their time limit at 43 and 41 M. Horizon masses quoted
  from single searches scatter by about 5e-4; the tables use medians over 2 M
  (1.0000 at 20 M for `mc_adapt2`, 0.9946 at 40 M for `mc_adapt4`).
- Density-lowered near-critical run: the mean lapse is 0.783 over the whole run and
  0.776 after 250 M.

## M/128 runs of the cluster with two overdensities: block count near the limit (16:05)

`jeans/n1e4_v11` reaches 2164 blocks at t = 5.9 M against a limit of 2200 (76.3 GB on
the card at that limit); `v12` has the same mesh. From the next restart segment on,
both use a limit of 2280 (about 79 GB) and a finest region of radius 0.125 M instead
of 0.15 M around each tracker. The horizon radius expected at formation is 0.05 to
0.1 M. This is a change of the mesh during the run and is recorded in the chain logs.

## Cluster with two overdensities at M/128: no horizon with either removal rule (17:00)

`jeans/n1e4_v11` (cells of M/128 within 0.15 M of each tracker, 0.125 M after the
first restart; removal inside a found horizon; lapse guard 0.02) and `jeans/n1e4_v12`
(same, guard off).
- The collapse is earlier than at M/64: the smallest lapse is 0.068 at t = 8.02 M
  (M/64: 9.05 M) and 0.047 at 8.19 M. The original's horizons are at 8.475 and 8.525 M.
- v11: no horizon reported. The lapse passes the guard at 8.30 M and 966 particles are
  removed; it returns to 0.04; further bursts follow (1594 removed by 9.3 M, 2187 by
  10.1 M, 3132 by 12.4 M). Still running.
- v12: no horizon reported and nothing removed. The particle energy sum rises from
  1.07 to 2.1 of M at 8.63 M and 3.4 at 8.91 M; the smallest lapse on the mesh is
  negative from 8.63 M (-0.003, then -0.016); the fields are NaN at 8.95 M. Stopped.
- Against the prediction of 15:22: the third branch (neither run finds a horizon).
- Particle snapshots (crude estimate, not a measurement): at t = 8.0 M a tenth of one
  overdensity's particles lie within 0.003 M of its densest point, a third of a cell;
  the collapse is from the inside out, so the first trapped region is far smaller than
  the black hole of 0.09 M that the original reports at t = 10 M.
- One more check before accepting that branch, written before its result. The finder
  has only ever been seen to work on horizons of eight or more cells in radius. Run
  `jeans/n1e4_v12d` repeats v12 from its dump at 6.28 M to 8.66 M with a restart dump
  every 0.25 M. If the Misner-Sharp profile about a tracker shows 2m/R >= 1 at 8.3 to
  8.6 M, a trapped surface exists on the mesh and the finder misses it: the test can
  then go on at M/128 once the finder is made to find it. If 2m/R stays below one up
  to the time the lapse turns negative, no horizon forms on this mesh.

## Correction: the black holes of the two overdensities do form; my check of 14:50 was wrong (17:10)

The Misner-Sharp check of 14:50 passed the centre to the tool in a form the tool does
not parse (`--center=x,y,z`); it silently used the origin. The profile I read (largest
2m/R of 0.47) was about the centre of the cluster, not about the collapsed core. I
noticed when two runs with different centres returned identical numbers. Repeated with
the centre at the tracker (header of the output checked):
- `jeans/n1e4_v7` (M/64, removal at a lapse of 0.05), dump at t = 10 M: a trapped
  region exists. Outermost 2m/R = 1 at areal radius 0.170 M, coordinate radius 0.050 M
  (three cells): M_H = 0.0849 with a spread of 0.007 over angle. The original gives
  0.0880 and 0.0877 M for its two black holes at t = 10 M. The mass function is flat
  (0.085 to 0.092 M) from 0.03 to 0.15 M around the core.
- `jeans/n1e4_v11` (M/128, guard 0.02), dump at t = 12.30 M: trapped region, outermost
  2m/R = 1 at areal radius 0.226 M, coordinate radius 0.078 M (ten cells): M_H = 0.1128
  with a spread of 0.005.
- The horizon finder reports nothing in either run at any time.
What this overturns and what it restores.
- Wrong: "no black hole had formed; the removal aborted the collapse" (14:50), and
  "cells of M/64 do not form these black holes" (15:22, 17:00). Black holes of the
  right mass form at M/64 and at M/128 with lapse-based removal.
- Restored in part: the reading of 14:35 that black holes form and the finder cannot
  see them. Its other half (matter lingering inside as the cause of the failure at
  11.9 M) remains untested.
- The rise of the smallest lapse after each burst of removal is not evidence against a
  black hole: on these meshes the lapse at cell centres near the puncture is a few
  hundredths.
- Open now: why the finder fails on a horizon of ten cells' radius. Candidate read
  from its source: the flow is abandoned when the mean expansion on the trial surface
  exceeds a fixed tolerance (100 in these inputs), and the expansion scales inversely
  with the black-hole mass, ten times larger here than in the dust and cluster runs.
  Test submitted (`jeans/finder_test`): restart from the v11 dump at 12.30 M, where a
  black hole of 0.113 M is known to exist, with the finder's log on, the tolerance
  unchanged for the first horizon and 10^4 for the second. Written before the result:
  if the tolerance is the cause, the log of the first horizon ends with "hmean >" and
  the second horizon is found with a mass within 0.01 of 0.113 M.
- Lesson recorded for the tool: an option it does not recognise must be an error, not
  a silent default. To be fixed in `analysis/diag/common.py`.

## Finder test: the flow overshoots on its first step; first trapped surface at 8.6 M (17:25)

`jeans/finder_test` (restart of v11 at 12.30 M with the finder's log on).
- Both individual searches start from a sphere of radius 0.12 M (area 0.905, mean
  expansion 1.27) and after one flow step have a mean radius of -0.20 M; the search
  ends with "meanradius < 0". This happens identically with the expansion tolerance at
  100 and at 10^4.
- Against the prediction of 17:10: refuted. The tolerance on the mean expansion is not
  what ends the search. The flow step is: each spectral coefficient is lowered by a
  constant times the spectral component of the weighted expansion, and the constant
  (1 in these inputs, as in every earlier run) is sized for a black hole of unit mass.
  For a black hole ten times smaller the first step is larger than the radius.
- `jeans/n1e4_v12d` (v12 repeated from 6.28 M to 8.66 M; the dump interval override
  did not take effect on restart, so only the final dump exists). Misner-Sharp profile
  about the tracker at t = 8.66 M: trapped region, outermost 2m/R = 1 at areal radius
  0.098 M (coordinate radius 0.02 M), M_H = 0.049 with a spread of 0.004; the largest
  2m/R is 1.007. So the first trapped surface has just formed at 8.66 M with no
  particle removed; the original's first horizons are at 8.475 and 8.525 M. The black
  hole then grows (0.085 M at 10 M in v7).
- Next test, written before its result: `jeans/finder_test2`, same restart, flow
  constant 0.05 for the first horizon and 0.1 for the second, 2000 iterations, mass
  tolerance 1e-7. If the step size is the cause, both horizons are found with masses
  within 0.01 of the Misner-Sharp value (0.113 M for the first).

## Second finder test: found; and why the runs fail after the black holes form (17:40)

`jeans/finder_test2` (same restart, flow constant 0.05 for the first horizon and 0.1
for the second, 2000 iterations, mass tolerance 1e-7).
- First horizon: found at every search, mass 0.11407, 0.11430, 0.11452 at t = 12.33,
  12.36, 12.39 M (Misner-Sharp at 12.30 M: 0.1128 with a spread of 0.005). The flow
  converges in about thirty iterations.
- Second horizon: found at two of three searches with 0.11418 and 0.11451; in the
  first search the flow reaches 0.1139 after three iterations and then, driven on by
  the tight mass tolerance, becomes unstable near iteration 90. The constant 0.05 is
  the safer one.
- Against the prediction: confirmed. The flow constant, sized for unit mass, was the
  reason the finder never reported these black holes.
Both lapse-removal runs fail a few M after formation: v7 (M/64) at 11.94 M, v11
(M/128) at 13.26 M. In both the particle number goes to zero within about six steps
over the whole cluster while the smallest lapse on the mesh stays where it was, and
the fields are NaN afterwards.
- Reading, with its test. Six steps for the whole cluster is the speed at which the
  five filter passes carry a NaN in the sources across the mesh, not the speed of any
  signal. A NaN can be born in the sources at a single cell without any particle
  there: the normalization divides every cell's sources by the square root of the
  metric determinant, and the host code forms the metric as the conformal metric
  divided by the evolved conformal factor chi without a floor. Next to a moving
  puncture chi at a cell centre can undershoot to zero or below (the guard-free run
  showed the lapse doing exactly that). In all earlier collapse runs the black hole
  sat at the origin, a cell corner; here the black holes move across cell centres.
- Change to the source normalization (my code): where the determinant is not positive
  and finite the sources are set to zero, and such cells are counted and reported.
- Written before the runs: if this is the cause, the runs pass the times at which v7
  and v11 failed, and the log reports cells with non-positive determinant at or before
  those times. If a run fails at the same time without such a report, the cause is
  elsewhere.
- Runs (published removal rule, lapse 0.05, no horizon-based removal; new finder
  constants; new executable): `jeans/n1e4_v13` continues v11's mesh (M/128) from its
  dump at 6.31 M; `jeans/n1e4_v14` continues the M/64 mesh from the dump of v10 at
  5.0 M.

## Reruns with working finder: horizons found; the failure is not a single bad cell (18:05)

`jeans/n1e4_v14` (M/64 from 5.0 M, published removal at a lapse of 0.05, finder flow
constant 0.05, guarded source normalization).
- First horizons from the finder: B at t = 10.125 M with mass 0.0885 M, A at 10.25 M
  with 0.0929 M (coordinate radius 0.053 M, 3.4 cells). The original gives 0.0880 and
  0.0877 M at t = 10 M. Before 10.1 M the finder does not converge on this mesh; the
  Misner-Sharp profile showed the trapped region at 10.0 M (0.085 M) in v7. Found in
  28 and 30 searches up to 11.94 M, where the masses are 0.1198 and 0.1185 M.
- The run fails at t = 11.926 M, the same step as v7.
- Against the prediction of 17:40: refuted as stated. The run did not pass the time at
  which v7 failed. The guard did report cells with a bad determinant, but not one cell
  beside a puncture before the failure: the first report, in the failing step itself,
  counts 10944 cells, then 92319, 329942, ... in the following steps. A region of that
  size after one step is what one spacetime update (four substeps, stencils of four
  cells) makes of a single bad value. So the bad value is born inside the spacetime
  update, with finite sources (the particle energy sum is normal in the step before),
  and not in the source normalization.
- Known so far about the failure: same step on the same mesh with two different
  executables and removal diagnostics; at M/128 (v11) it comes later, at 13.26 M; in
  both cases the black holes have reached about 0.12 M and a coordinate radius of
  about 0.08 M; no regridding in the steps before; trackers at rest on the mesh for the
  last 0.05 M; smallest lapse on the mesh unremarkable (0.046).
- Next: a build that reports where the bad cells are (centroid, extent, cell sizes) and
  a restart of the M/64 run from its dump at 10.0 M. No prediction is attached: this
  is a measurement of where the failure starts.
`jeans/n1e4_v13` (M/128 from 6.31 M, same settings) is running: horizons first found
at 9.52 M (0.0782 M) and 9.61 M (0.0801 M); 0.0827 and 0.0830 M at 9.83 M.

## Where the failure starts: at a puncture (18:15)

`jeans/diag_v14` (v14 repeated from its dump at 10.0 M with a build that reports where
cells with a bad determinant are).
- First report, t = 11.92578 M: 10944 cells, all with a non-finite determinant, all on
  the finest level (cells of M/64), centroid (2.828, 1.141, 0.047), x from 2.617 to
  3.039. The tracker of black hole B is at (2.805, 1.133, 0.055): the bad region is
  centred 1.5 cells from that puncture and spans 13.5 cells either way, which is what
  one spacetime step makes of one bad cell. The following steps spread it over the
  coarser levels.
- So the bad value is born within about two cells of the puncture of one black hole,
  inside the spacetime update, in a step whose sources have a normal energy sum.
- Not yet known: which term. Candidates are the matter still inside the horizon (its
  sources are finite in sum but could be large or badly behaved in single cells next
  to the puncture) and the spacetime evolution of a small moving puncture by itself.
- Intervention, written before its result. `jeans/diag_v14b`: the same restart with
  every particle inside 0.8 of the smallest horizon radius removed as soon as the
  finder reports a horizon (from 10.1 M on), in addition to the lapse rule. If matter
  close to the puncture produces the bad value, this run passes 11.93 M. If it fails
  at the same step, matter inside the horizon is not the cause and the spacetime
  evolution of the puncture is.

## Intervention: removing matter inside the horizon cures the failure (18:30)

`jeans/diag_v14b` (M/64, restart at 10.0 M; published lapse rule plus removal of every
particle inside 0.8 of the smallest radius of a found horizon).
- The run passes 11.926 M, where v7 and v14 failed, and reaches its end at 13.0 M with
  no cell of bad determinant reported. Horizons found in 42 and 43 searches; masses
  0.1222 and 0.1216 M at 12.1 M, 0.1281 and 0.1281 M at 12.9 M (coordinate radius
  0.092 M, six cells). 6407 particles left.
- Against the prediction of 18:15: the first branch. Matter close to the puncture
  produces the bad value; with it removed the spacetime evolution of the small moving
  puncture is stable on this mesh for at least the tested stretch.
- `jeans/n1e4_v13` (M/128, lapse rule only) failed at 12.256 M, five steps after a
  restart at 12.246 M (v11, with the lower lapse threshold, had failed at 13.26 M).
- Why the lapse rule alone is not enough here, as far as the data go: on these meshes
  the lapse at cell centres next to the puncture stays at 0.02 to 0.05, at or above
  the removal thresholds, so particles inside the horizon are removed only in the few
  cells nearest the puncture and the rest stay. Which quantity of theirs turns bad
  (the reconstructed metric at a particle next to the puncture is one candidate) was
  not isolated.
- Production runs with both removal rules, finder constants as tested, the build that
  reports bad cells: `jeans/n1e4_v15` (M/64) continues from the dump of the
  intervention run at 13.0 M; `jeans/n1e4_v16` (M/128) continues from the dump of v13
  at 12.246 M, four steps before v13 failed. Written before: v16 passes 12.26 M if the
  same cause was at work there; if it fails within a few steps of its start, the
  restart itself is involved and has to be looked at.

## M/128 chain failed at the same step; a defect of the horizon-based removal after restarts (18:40)

`jeans/n1e4_v16` (M/128 from the dump of v13 at 12.246 M, horizon-based removal on).
- Fails at t = 12.2559 M, the step at which v13 failed: 11072 cells with non-finite
  determinant, centred two cells from the puncture of black hole B. The finder's first
  success after the restart came at 12.2656 M (first horizon only), so the removal
  inside the horizon had not acted before the failure.
- Against the prediction of 18:30: it failed within a few steps of its start, which I
  had taken to implicate the restart. The comparison with v13 shows instead that the
  state in that dump fails five steps later with or without the new rule, because the
  rule had no horizon to work with yet. The test did not separate the two; it shows
  only that the removal must be active before the matter accumulates.
- Found while reading the first steps: v16 had nine particles fewer than v13 from its
  first step. After a restart the finder's flag "found" is restored from the dump
  while its radius is the initial placeholder (-1) and its centre the stored default,
  and my rule used them: 0.8 times the placeholder is a radius of 0.8 M about the
  default centre. Corrected: the rule waits for a successful search of the current
  run (radius positive), and ignores a surface more than four times its starting
  radius. The earlier intervention run (`diag_v14b`) was not affected: it restarted
  from a dump written before any horizon had been found. `v15`, started from a dump
  with horizons, was stopped after its first steps and is discarded.
- New production chains with the corrected build: `jeans/n1e4_v17` (M/64, from the
  dump of the intervention run at 13.0 M) and `jeans/n1e4_v18` (M/128, from the dump
  of v13 at 6.31 M, before the collapse, so that the removal acts from the first
  successful search on). Written before: v18 passes 12.26 M and 13.26 M with no bad
  cells; if it fails there again, removal inside 0.8 of the horizon is not enough at
  M/128 and the comparison with M/64 has to explain why.

## M/64 production chain: stable to 19.1 M, then over the block limit (19:00)

`jeans/n1e4_v17` (M/64, both removal rules, from 13.0 M).
- Runs from 13.0 to 19.125 M with both horizons found at every search (98 of 98);
  masses 0.1285 and 0.1287 M at 13.0 M, 0.1437 and 0.1433 M at 19.06 M; coordinate
  radius 0.108 M; no cell with a bad determinant reported. That is 7 M past the step
  at which the runs without the horizon rule failed.
- At 19.13 M one regridding asks for 2388 blocks (1856 before; limit 2100) and the
  run stops. Not a numerical failure. Periodic restart dumps were not written after
  the restart (only the dump at each wall-clock stop exists), so the chain resumes
  from 13.0 M.
- Resumed with a tracked finest region of radius 0.2 M instead of 0.3 M (the horizon
  radius is 0.11 M), a block limit of 2280, and wall-clock segments of 25 minutes.

## M/128 production chain passes both earlier failure points (19:40)

`jeans/n1e4_v18` (M/128 from 6.31 M; lapse rule plus removal inside 0.8 of a found
horizon from the first successful search at 9.5 M on).
- At t = 14.18 M: no cell with a bad determinant; horizons found in 147 and 150
  searches; masses 0.1258 and 0.1260 M (coordinate radius 0.092 M, twelve cells). The
  run passed 12.256 M (where v13 and v16 failed) and 13.26 M (where v11 failed), and
  went through a restart at 12.2 M without incident.
- Against the prediction of 18:40: confirmed. With the removal inside the horizon
  active from the first found horizon, the M/128 mesh behaves like the M/64 mesh.
- Also learned from the referee read of the draft: the original states that its code
  supports apparent-horizon-based excision besides lapse excision and found no
  significant difference between the two in its benchmarks. The rule used here is
  therefore not new; what is new is that on meshes with 3 to 12 cells per horizon
  radius the two differ, and the horizon-based one is needed.

## M/64 production chain: second stop on the block limit at 29.1 M (20:10)

`jeans/n1e4_v17` ran from 13.0 to 29.14 M (finest region of radius 0.2 M, limit 2280):
horizons found in 357 of 357 searches, masses 0.1522 and 0.1523 M at 29.1 M, no bad
cells; separation of the trackers 6.1 M at 10 M and 5.3 M at 28 M.
- Block count: 1842 at 18 M, falling to 1485 at 24 M, then 1940 at 24.9 M, 2234 at
  26 M, and a request for 2311 at 29.14 M (limit 2280). At the restart at 26.15 M the
  levels with cells of 4 M to M/4 hold 294 blocks each (112 at the start of the run).
- Cause, read from the level counts and the tracker positions: the refinement keeps
  nested spheres of fixed radius around each tracker (30, 12 and 6 M for the levels
  with cells of M, M/2 and M/4). The black holes have left the planes of symmetry of
  the mesh (z = 0.35 M, and they are no longer at x = +-3 M on the x axis), the
  spheres no longer line up with the block layers in any direction, and every coarser
  level has to wrap the larger set.
- Resumed from the dump at 26.15 M with the spheres reduced to 24, 10 and 4 M. This
  coarsens the envelope beyond 4 M from each black hole from cells of M/4 to M/2 (the
  cell size of the stable-cluster runs). The same change is set for the M/128 chain
  from its next restart segment on, before it reaches this stage.

## Block growth during the inspiral: my reading of 20:10 was wrong; smaller domain (20:35)

After the restart at 26.15 M with the spheres reduced to 24, 10 and 4 M the block
count did not fall (2241 at 27.1 M).
- Reading the refinement code: the nested spheres of fixed radius are centred on the
  origin, not on the trackers; only the finest region (radius 0.2 M) follows each
  tracker. Reducing the spheres could not help, and the "cause" of the previous entry
  is withdrawn.
- What the level counts show: 294 blocks on each of the five coarsest refined levels
  is one box seven blocks wide per level, where two separate nests four blocks wide
  give 112. The two fine nests have come within a few block widths of each other on
  the levels with blocks of 1 to 2 M; from that level outward every coarser level has
  to wrap their union. The count rose in steps as the separation fell from 6.1 to
  5.3 M, and each further halving of the separation moves the merging one level
  finer and adds a wider box on one more level.
- Consequence: on the domain of +-256 M (ten levels) the run needs more blocks than
  one card holds well before the merger; on the M/128 mesh (eleven levels) earlier
  still. `jeans/n1e4_v17` stopped at 27 M. The M/128 chain (`v18`) is left to run
  until it meets its limit; it serves as the comparison of the two meshes through
  formation and the first part of the orbit.
- New M/64 run from t = 0, `jeans/n1e4_v19`: domain +-80 M with root cells of 2 M
  (eight levels instead of ten, finest cells M/64 as before), every setting found
  necessary today in place from the start (finder flow constants, removal inside 0.8
  of a found horizon besides the lapse rule, tracked finest region of radius 0.2 M,
  block limit 2280). The outer boundary at 80 M is out of causal contact with the
  centre for the 100 M of the run also for gauge modes at sqrt(2) c. One run, no
  stitching.
- Written before the run: the evolution to 27 M repeats what the stitched runs gave
  (first found horizons near 10.3 M at 0.093 M; 0.150 M at 27 M; separation 5.3 M at
  28 M) to within the differences already seen between restarts (masses to 0.002 M).
  A larger difference would mean that the domain or the coarse-level layout matters.

## Fresh M/64 run on the smaller domain: state at 48 M and comparison with the old domain (23:10)

`jeans/n1e4_v19` (domain +-80 M, eight levels, all settings from the start; at 48 M,
1945 blocks at most, no bad cells, horizons found in 542 of about 560 searches from
10.5 M on). Figure: `paper/figures/fig_overdensities.png`. Black-hole positions for
the figure: the tracker files keep only the latest restart segment, so the exact
positions come from the headers of the restart dumps and from the current tracker
file, with a monotone cubic between them (error at most 0.014 M in the separation by
leave-one-out); before the first horizon, the densest point of each overdensity's
particles. Tracker files are now archived per segment for both runs.
- Horizon masses (A, B): first found at 10.50 and 10.56 M with 0.0976 and 0.0992 M;
  0.1448, 0.1442 at 20 M; 0.1538, 0.1527 at 30 M; 0.1626, 0.1622 at 40 M; 0.168 at
  44 M. The original: 0.0880, 0.0877 at 10 M and 0.1742, 0.1761 at 60 M.
- Separation of the black holes: 6.05 M at 10 M, 5.96 M at 20 M, 5.36 M at 30 M,
  4.11 M at 40 M, 2.54 M at 47.75 M. Orbital phase 0.22 of a turn by 47.75 M. No
  common horizon yet. The original merges at 64.16 M.
- Against the prediction of 20:35 (old domain against new, to 27 M): the masses agree
  to 0.0006 M, within the predicted 0.002 M. The separation does not: 5.52 M at 28 M
  on the new domain against 5.39 M at 27.5 M on the old one (predicted equal, 5.3 M).
  On the smaller domain the black holes approach more slowly; by the stated test the
  domain or the coarse-level layout matters for the orbit at the level of 0.15 M in
  the separation by 28 M. Which of the two, or whether it is the different history of
  restarts and settings of the old run, is not determined.
- M/128 against M/64 (`v18`, at 38 M): its black holes are about 0.01 M lighter from
  15 M on (0.1439, 0.1448 against 0.1538, 0.1527 at 30 M) and closer (5.15 against
  5.36 M at 30 M).
- Drift out of the orbital plane on the M/64 mesh: both black holes are at z = +0.6 M
  by 48 M (the old-domain run: +0.33 M by 27.5 M); the mean u_z of the particles
  grows from 0 to +0.015 and the envelope's centroid moves from z = +0.009 to
  +0.097 M. The M/128 run with the same particles stays within 0.06 M of the plane.
  The system as a whole gains momentum along z on the M/64 mesh. Cause not
  determined (it comes with the mesh, not with the domain).
- The finder first reports the horizons at 10.5 M (M/64) and 9.5 M (M/128); the
  trapped surface itself forms near 8.7 M (Misner-Sharp, 17:25 entry).
