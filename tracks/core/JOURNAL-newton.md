# JOURNAL of core, work package newton (branch `core/newton`)

Append-only. Predictions are written before a test runs, outcomes after, also when the
prediction failed. Runs are registered under `tracks/core/runs/<run_id>/manifest.json`
(outputs under `scratch/core/<run_id>/`). Labels: [VERIFIED] read or measured in this
session (with locator), [BACKGROUND], [JUDGEMENT], [TO VERIFY].

## 2026-11-15 session newton-1

### P0 Pre-check: does the multigrid of this tree work before any change?

Setup: the hydro test problem `binary_gravity` (two homogeneous spheres, analytic
potential and acceleration compared after one cycle by the problem generator itself),
unmodified executable built from `main` (b7b431d), processor build, uniform mesh, isolated
domain with the multipole boundary of the multigrid module (`mg_bc = multipole`,
`mporder = 4`), spheres of radius 0.08 at x = 0.1 and x = -0.15 in the unit box, N = 32
and 64 cells per side, MeshBlocks of 16^3.

Prediction (written before the run): the solver runs and returns the potential of the two
spheres; the L2 norm of the relative potential error falls by about a factor four from
N = 32 to N = 64 (seven-point Laplacian, second order), and is below one per cent at
N = 64. Refuted if the solver stops with an error, if the error does not fall with N, or
if it is of order one (a sign or normalisation fault of the multipole boundary).

Note: runs core-20261115-112103-b7b431d and core-20261115-112104-b7b431d stopped at once
with "Parameter 'mg_bc' in block 'gravity' on command line not found" (a parameter that is
not in the input file cannot be added on the command line); no physics was run. The input
copy `scratch/core/tmp/binary_gravity_iso.athinput` adds the three parameters.

Outcome of P0 (runs core-20261115-112129-b7b431d, N = 32; core-20261115-112130-b7b431d,
N = 64; `run.log` of each) [VERIFIED]:
- the solver runs with the multipole boundary; the defect norm falls by a factor 3.8 to
  4.8 per V cycle (one pre- and one post-smoothing sweep), 20 cycles take 0.12 s (N = 32)
  and 0.53 s (N = 64) on one core;
- printed "Potential L2" 2.593e-2 (N = 32) and 1.340e-2 (N = 64), ratio 1.93; maximum
  relative potential error 1.763e-2 and 4.49e-3, ratio 3.93.
The prediction "the L2 norm falls by a factor four" FAILED as written, and for a reason in
my reading, not in the solver: the number the problem generator prints as L2 is the square
root of the volume mean of the relative error (binary_gravity.cpp, lines 349 to 371:
`lpot_l1 += perr*vol`, then `sqrt(sum/vol)`). The mean relative error itself is 6.72e-4
and 1.80e-4, ratio 3.74, and the maximum error falls by 3.93: second order, as expected of
the seven-point Laplacian. Below one per cent at N = 64: yes (maximum 0.45 per cent).
Not refuted: no error stop, no order-one error. The multigrid module is usable on an
isolated uniform mesh; what it lacks for particles is a source other than the gas density.

### Implementation, first version (commit below)

New file `athenak/src/particles/nrpic_newton.cpp`; hooks in `particles.hpp`,
`particles.cpp`, `nrpic.cpp`, `nrpic_io.cpp`, `gravity/mg_gravity.{hpp,cpp}`,
`driver/driver.cpp`, `pgen/pgen.cpp`, `CMakeLists.txt` (listed with line numbers in
`tracks/core/interfaces/newtonian_mode.md`, section 4).

Smoke test (not registered, no number is taken from it for the record): one unit mass and
24 tracers, isolated 64^3 box. It ran; the far field approaches -1/r^2. It showed a force
of the mass on itself of order m/dx^2. Before believing or disbelieving it I wrote an
independent numpy model of the scheme (cloud-in-cell deposit, seven-point Poisson solve
with Fourier transforms on a periodic box, gradient of the Catmull-Rom interpolant;
`scratch/core/tmp/selfforce.py`): it gives the same three components to seven digits. So
the force is a property of the scheme "cloud-in-cell deposit, Catmull-Rom gather" (the
deposit and the gather kernels differ, so the force of a particle on itself does not
cancel), which the relativistic mode shares, and not a fault of the implementation. It
vanishes for a particle at a cell centre and for a regular lattice of particles (uniform
deposited density). It is measured properly in test T1 below.

### R1 Regression of the relativistic mode (prediction)

Five short existing problems (`tracks/core/tools/regress_relativistic.py`: Kerr geodesic
with the midpoint and the Boris pusher, deposit on a statically refined flat mesh, the
periodic cosmology problem with Z4c at 16^3, the Oppenheimer-Snyder ball with Z4c on a
refined mesh), each run with the executable built from `main` (b7b431d,
`.work/baseline/athena_cpu`) and with the new one, processor build.
Prediction: every output file (histories, trajectories, snapshots, restart files) is
identical byte for byte. Refuted by any differing file. The only change inside a kernel
of the relativistic mode is the selection `W = newton ? 1 : W_rel` in the deposit; if the
compiler evaluated W_rel differently because of it, the deposit sums would differ in the
last digits.

Outcome of R1 (processor build, commit 728637a; report
`scratch/core/regress/report_cpu_728637a.json`) [VERIFIED]: no file differs.
| case | baseline run | new run | files compared, all identical |
|---|---|---|---|
| geo | core-20261115-113535-728637a | core-20261115-113536-728637a | 2 (history, trajectory; 2000 steps) |
| boris | core-20261115-113537-728637a | core-20261115-113538-728637a | 2 |
| dep | core-20261115-113539-728637a | core-20261115-113543-728637a | 1 (history of 20 steps, 10^4 particles, refined mesh) |
| east | core-20261115-113547-728637a | core-20261115-113555-728637a | 12 (histories, 7 snapshots, trajectories; Z4c, 20 steps) |
| os | core-20261115-113602-728637a | core-20261115-114026-728637a | 16 (histories, 4 snapshots, 5 restart pairs; Z4c, refined mesh, 3 steps) |
The prediction held. (The run ids of the baseline carry the commit of the worktree at the
time, 728637a; the baseline executable itself is the build of b7b431d, sha256 in each
manifest.)

### T1 Field of a point mass on an isolated domain (prediction)

Setup: `problems/newton/isolated.athinput`, box [-2, 2]^3, multipole boundary of order 4
about the centre of mass, one unit mass at (0.031, 0.017, -0.011) and 2000 massless
tracers at rest, log-uniform in distance between 0.05 and 1.8 (`make_ic.py point`, seed
1), cloud-in-cell deposit, no filter, Catmull-Rom gather, N = 32, 64, 128 cells per side
(dx = 1/8, 1/16, 1/32). One step of 1e-6: the momentum of a tracer after the step
divided by the step is the acceleration it feels. The potential is read at eight probes
(distances 0.5 to 2.1 from the origin) from the lapse columns of the history.

Prediction (written before the runs):
1. The acceleration approaches -r_hat/r^2 with a relative error that falls as (dx/r)^2:
   at fixed positions with r >= 0.5 the rms relative error falls by a factor 4 (3 to 5)
   per doubling of N; its size at N = 64 is about one per cent at r = 8 dx and a few
   times 1e-3 at r = 20 dx (the unregistered smoke run suggested these sizes).
2. Inside r of about 2 dx the force is softened and anisotropic at order one (cloud and
   mesh), with a scatter that depends on where the tracer sits in its cell.
3. The potential at the probes agrees with -1/r to second order in dx.
4. The mass feels its own field: the force on it is of order 0.5 m/dx^2 and its
   components scale as 1/dx^2 between resolutions for the same position in the cell
   (the position in the cell changes with N here, so only the order is predicted).
Refuted by: a far-field error that does not fall with N or falls at first order (boundary
or ghost-cell fault); an error of the monopole (the force times r^2 not tending to -1 at
large r/dx); a potential error at the probes of first order.

### T2 Field of a homogeneous ball on an isolated domain (prediction)

Setup: the same box and solver; ball of radius 1 and mass 1 centred at (0.031, 0.017,
-0.011), 1 099 136 equal-mass particles on a lattice of spacing 1/64, 2000 massless
tracers uniform in distance between 0.05 and 1.8 (`make_ic.py ball`), N = 32, 64, 128.
Reference: the exact field of the ideal ball (linear inside, inverse square outside).

Prediction:
1. Away from the surface (|r - 1| > 0.25, two cells of the coarsest mesh) the rms error
   of the acceleration, in units of GM/R^2, falls by about a factor 4 per doubling
   (second order), and is below 1e-3 at N = 128.
2. In the shell |r - 1| < dx the error is of first order in dx (the cloud smears the
   density jump over one cell), so the maximum error over all tracers falls only by
   about a factor 2 per doubling.
3. The potential at the probes: second order.
Refuted by first-order or no convergence away from the surface, or by an error that does
not depend on N (a fault of the multipole boundary would show as such a floor).

First runs of T1 and T2 (commit 728637a): point core-20261115-114713-728637a (N = 32),
core-20261115-114723-728637a (64), core-20261115-114733-728637a (128); ball
core-20261115-114714-728637a, core-20261115-114724-728637a, core-20261115-114740-728637a.

FAILED, T2, and the cause is in the solver control, found in the run log and not
guessed: the potential of the ball at cycle 0 was not converged (defect norm 1.7e2,
1.3e3, 1.1e4 in the history at N = 32, 64, 128; potential at the probes 13 per cent off
at every N). `run.log` of core-20261115-114724-728637a, lines 11 to 14: "MG initial defect
= 48.0063", "MG iteration 0: defect = 1318.32", and the solve ends. With `threshold = 0`
the stock rule (`multigrid_driver.cpp`, SolveIterative: stop when a cycle lowers the
defect by less than ten per cent) ends the solve at the first V cycle whenever that
cycle raises the defect, which it does from a zero potential with the multipole boundary
and a smooth source. The second solve of the same run, started from that potential,
converged to 5.7e-12 in 24 cycles (lines 19 to 45). The point-mass runs were not affected
(first cycle 334 -> 174, 3867 -> 1362, 30125 -> 10817, then to 6e-13 ... 7e-11).
The three ball runs are void. Change: `MGGravityDriver::SolveSource` with `threshold = 0`
now runs V cycles until two in succession fail to lower the defect by ten per cent (the
stock path of the gas is not touched). The number of cycles is a new history column.

Outcome of T1 from the valid point-mass runs (to be repeated with the changed solver
control; the numbers below are of commit 728637a) [VERIFIED]:
- far field (the same 846 tracers with r >= 0.5): rms relative error 1.61e-2, 4.94e-3,
  1.33e-3 at N = 32, 64, 128; orders 1.70 and 1.89 (ratios 3.26 and 3.72). Prediction 1
  held (ratio between 3 and 5); by r/dx at N = 64 the rms error is about 0.6 per cent
  between 8 and 16 cells and 0.17 per cent beyond 16 cells, as predicted in size.
- inside two cells the rms relative error is 0.23 to 0.3 (softened, anisotropic):
  prediction 2 held.
- potential at eight probes: maximum relative error 7.6e-3, 2.0e-3, 1.8e-3. Prediction 3
  FAILED as a statement about the maximum over eight probes: the probe at distance 0.47
  has errors -7.6e-3, -7.3e-4, -1.8e-3 (not monotonic; the error of a point mass depends
  on the direction and on the position in the cell and changes sign), the other seven
  fall monotonically (for example at distance 0.77: -6.6e-3, -2.0e-3, -1.5e-4). Eight
  probes are too few to measure an order; the force on 846 tracers is the measurement.
- force of the mass on itself times dx^2: components up to 0.36, 0.58, 0.47 at the
  three resolutions: of order 0.5 m/dx^2 as predicted (prediction 4 held).

Repeat of T1 and T2 with commit 9d84282 (runs: point core-20261115-115136-9d84282,
core-20261115-115145-9d84282, core-20261115-115155-9d84282; ball
core-20261115-115137-9d84282, core-20261115-115146-9d84282, core-20261115-115203-9d84282).
The startup solves now converge (27, 26, 25 V cycles to a defect of 5e-13, 6e-12, 6e-11;
5 cycles at the next step). T1: the same numbers as before to all printed digits.

T2, first analysis, against the ideal ball of radius 1 [VERIFIED]:
- away from the surface: rms error 7.98e-4, 3.80e-4, 3.37e-4 (orders 1.07, 0.17): a
  floor. Prediction 1 FAILED as analysed.
- shell |r - 1| < dx: 2.25e-2, 1.24e-2, 6.7e-3 (orders 0.86, 0.89); maximum over all
  tracers 6.9e-2, 3.6e-2, 1.6e-2: first order at the surface, prediction 2 held.
Hypothesis for the floor, to be tested (it can fail): the reference, not the code. The
lattice has 1 099 136 points inside the unit sphere, 0.097 per cent more than (4 pi/3)
64^3 = 1 098 067, so the particles sample a ball of density M/(N h^3), 0.097 per cent
below 3M/(4 pi): the interior field is lower by that fraction, of the size of the floor.
Test: repeat the analysis with the radius of the homogeneous ball of the same mass and
that density, 1.000324. If the hypothesis is right the error away from the surface falls
at second order to N = 128; if a floor of the same size remains, the cause is elsewhere
(the multipole boundary would be the next suspect).

Outcome of the test of the hypothesis (same six runs, analysis with the radius 1.000324
of the ball the lattice samples; `tracks/core/analysis/newton/field_ball.json`,
`field_ball.png`; the analysis against the nominal radius is kept as
`field_ball_ideal_radius.*`) [VERIFIED]: the floor is gone.
- away from the surface (|r - R| > 0.25, 1340 tracers): rms error in units of GM/R^2
  7.25e-4, 1.83e-4, 5.09e-5 at N = 32, 64, 128; orders 1.99 and 1.85. Prediction 1 of T2
  holds with the corrected reference (second order; below 1e-3 at N = 128).
- shell |r - R| < dx: 2.23e-2, 1.22e-2, 6.4e-3 (orders 0.87, 0.93); maximum over all
  tracers 6.8e-2, 3.6e-2, 1.5e-2: first order at the surface (prediction 2 held).
- potential at the nine probes: maximum relative error 6.43e-3, 1.60e-3, 3.94e-4, orders
  2.01 and 2.02 (prediction 3 held).
The hypothesis could have failed and did not. What I had wrong was the reference: a
lattice ball is not the ideal ball at the 1e-3 level.
Figures inspected: `field_point.png` (force times r^2 scatters around -1 inside about
four cells and tends to it beyond; the relative error follows (dx/r)^2 for all three
resolutions on one curve), `field_ball.png` (interior and exterior on the exact curve;
error peaked at the surface; inside r = 0.8 the three resolutions share an error of 1e-5
to 1e-4 that rises with r and does not depend on N: the cubic shape of the lattice ball,
again a property of the particle set).

T1 potential, corrected statement: rms over the eight probes 3.9e-3, 9.4e-4, 6.5e-4; one
probe is not monotonic (see above).

### T3 Cold collapse of a homogeneous ball from rest against the cycloid (prediction)

Setup: `problems/newton/isolated.athinput`, box [-2, 2]^3, multipole boundary, ball of
mass 1 and nominal radius 1 centred on the origin, equal-mass particles at rest on the
lattice of the cell centres (one particle per cell: 17 256 at N = 64, 137 376 at N = 128;
`make_ic.py ball --spacing dx --ntracer 0`), cloud-in-cell, no filter, Catmull-Rom
gather, fixed step 0.002 (N = 64) and 0.001 (N = 128), to t = 1.0. Reference: the
cycloid of the homogeneous ball that the lattice samples (radius 1.001914 and 1.000286,
free-fall times 1.113911 and 1.111197), the same s(t) = r/r_0 for every shell;
t = 1.0 is 0.90 of the free-fall time, where s = 0.35 and the ball has a radius of 5.6
cells (N = 64) or 11 cells (N = 128).

Prediction (written before the runs):
1. Mean over the particles of r/r_0 against s(t): within 0.5 per cent at half the
   free-fall time and within 3 per cent at t = 1.0 for N = 64; the deviation at N = 128
   is smaller by a factor of two at least. Sign: the collapse lags (r/r_0 above the
   cycloid), because the cloud softens the field in the outermost cell of the ball
   (test T2: first-order error at the surface, the force too weak there).
2. The collapse stays homologous in the interior: the rms spread of r/r_0 over the
   particles with r_0 < 0.8 is below one per cent at t = 1.0; the outermost shell
   (r_0 > 0.9) deviates most.
3. Energy K + W: relative change below 1e-3 up to half the free-fall time and below
   5 per cent at t = 1.0 for N = 64, smaller at N = 128.
4. Second moment: I_xx/I_xx(0) follows s^2, and dI, d2I, d3I the analytic derivatives,
   to within twice the relative error of point 1 (d3I within 10 per cent at t = 1.0).
5. Consistency of the history columns, independent of the physics: the centred time
   difference of I_xx reproduces the column dI_xx, and that of dI_xx the column d2I_xx,
   to a relative error below 1e-4 (the truncation error of the difference at these
   steps); d3I_xx equals the difference quotient of d2I_xx by construction.
6. Linear and angular momentum stay at rounding level compared with M sqrt(GM/R) (the
   configuration is symmetric under reflections).
Refuted by: a deviation from the cycloid that does not fall with N; an energy error that
grows with N; a mismatch between the columns I, dI, d2I beyond the truncation error
(that would mean the acceleration in the sums is not the one applied to the particles).

### T4 Plane wave in a periodic expanding box against the Zel'dovich solution and against cosmo/newton (prediction)

Setup: `problems/newton/periodic.athinput`: box of side 4, periodic, comoving
coordinates and conformal time with a = (1 + t/2)^2 (H = 1 at a = 1), mean density
3/(8 pi); one particle per cell on the lattice of the cell centres, displaced along x by
the Zel'dovich solution at a = 1 with amplitude A = 0.25 at the fundamental wavenumber
k = pi/2 (`make_ic.py wave`); shell crossing at a = 1/A = 4, t = 2. Cloud-in-cell, no
filter, Catmull-Rom gather, step 0.005, to t = 3 (a = 6.25, beyond shell crossing),
snapshots every 0.25; N = 32 and 64. References: (i) the exact solution
x = q + a (A/k) cos(k q), p = a^(3/2) (A/k) cos(k q) up to shell crossing; (ii)
`cosmo/newton/pm.py` (spectral Poisson solve, spectral gradient, cubic interpolation)
with the same particle file, mesh, cloud and step; (iii) the scheme of the code written
in numpy (`python/nrpic/newton.py`: seven-point Laplacian by Fourier transform, gradient
of the Catmull-Rom interpolant), driven by the stepping of `pm.py`.
Measure: rms over the particles of the difference in x, divided by the rms displacement
a A/(k sqrt 2) of the exact solution at that time.

Prediction (written before the runs):
1. Against Zel'dovich before shell crossing: the relative error is of second order in
   dx. Reasoning: for the fundamental mode the window of the cloud, sinc^2(k dx/2), is
   cancelled by the seven-point Laplacian (whose symbol is k^2 sinc^2(k dx/2)); what
   remains is the gradient of the Catmull-Rom interpolant, low by (k dx)^2/6 at the
   nodes and high by (k dx)^2/12 midway (comment in nrpic_kernels.hpp). With
   (k dx)^2 = 0.0386 at N = 32 the force error is below 0.64 per cent, and the error of
   the displacement at a = 2.25 below 5e-3 at N = 32 and smaller by a factor of about
   four (3 to 5) at N = 64; at a = 3.5 below 2e-2 at N = 32.
2. Against `pm.py`: the two differ by terms of the same order, the uncompensated cloud
   window (k dx)^2/12 = 0.32 per cent in `pm.py` and the gradient above in the code:
   relative difference between 1e-4 and 1e-2 at N = 32 at t = 1.75, about four times
   smaller at N = 64.
3. Against the numpy scheme: agreement to 1e-8 or better at every snapshot, also after
   shell crossing. This is the test that can fail: a larger difference means that the
   implementation is not the scheme I describe (deposit, solver, ghost cells, gather or
   stepping), or that the multigrid solution is not converged.
4. Layzer-Irvine: C = a (K + W) + int K da stays constant to 2e-3 of the largest
   a |W| up to shell crossing at N = 64.
5. Total momentum: rounding level relative to sum m |p|.

### T7 The mode on a card (prediction, written before the job is submitted)

Setup: the collapse of T3 at N = 128 (64 MeshBlocks of 32^3, 137 376 particles, 1000
steps of 0.001), the same input and particle file as the processor run
core-20261115-115450-fee90ca, executable built with Kokkos CUDA from the same source
(`.work/athena_gpu_9d84282`), one A100.
Prediction: the run completes; the history agrees with the processor run to rounding
that grows with time (relative difference of K and W below 1e-9 at t = 0.5, particle
positions at t = 1.0 within 1e-8); not bitwise, because the particle sums are reduced
in a different order on the card and the compilers contract floating-point expressions
differently. Refuted by a crash, by a difference of order one in any history column
(a kernel that reads host data or a race in a reduction), or by a wall time longer
than the processor run (64 minutes expected there).

### T5 Restart (prediction)

Setup: (a) collapse of T3 at N = 32 (2176 particles, MeshBlocks of 16^3, step 0.004, to
t = 0.8, restart dump at t = 0.4); (b) plane wave of T4 at N = 32 (step 0.005, to t = 1,
dump at t = 0.5). Each is run once without interruption and once continued from the dump
in another directory, processor build. Prediction: the particle snapshots after the dump
time are identical byte for byte, and so are the records of `newton.hst` and `nrpic.hst`
for the cycles after the dump (including the Layzer-Irvine integral and the third
derivative of the second moment, which combine two states). Refuted by any differing
byte: the restart state (potential used as the starting guess, colour offset of the
smoother, diagnostic sums) would then be incomplete.

Outcome of T5 (commit 9d84282; `tracks/core/tools/compare_restart.py`) [VERIFIED]:
- collapse: uninterrupted core-20261115-120109-fee90ca, continued core-20261115-120126-fee90ca: the 4 snapshots written after the dump are
  identical byte for byte; the 100 records of `newton.hst` and of `nrpic.hst` for
  cycles 101 to 200 are identical as text.
- plane wave with expansion: uninterrupted core-20261115-120135-fee90ca, continued core-20261115-120211-fee90ca: 2 snapshots identical,
  100 records of each history identical.
The prediction held. Negative control (so that the test is known to be able to fail):
continued from the same dump without the state file `*.rst.prt.nwt`, run core-20261115-120249-fee90ca: the code
reports that it solves for the potential again; all 4 snapshots and all 100 records
differ, at rounding level (largest position difference 7.8e-16 at t = 0.8). So the
stored potential (starting guess of the next solve) is what makes the continuation
exact, and without it the continuation is correct to rounding.

Outcome of T3 at N = 64 (run core-20261115-115448-fee90ca, 500 steps, 203 s on one
core; `tracks/core/analysis/newton/collapse_N64.json`, figure `collapse_N64.png`
inspected) [VERIFIED]:
1. mean of r/r_0 against the cycloid: -9.7e-5 at half the free-fall time, +1.1e-4 at
   t = 1.0 (0.898 of the free-fall time). The bound of the prediction held with a wide
   margin (0.5 and 3 per cent), but the predicted sign (lag) FAILED for the mean: the
   particles with r_0 < 0.8 run ahead (-5.1e-4, -4.5e-3), those with r_0 > 0.9 lag
   (+7.4e-4, +1.07e-2), and the two cancel in the mean.
2. rms spread of r/r_0 over the particles with r_0 < 0.8 at t = 1.0: 0.90 per cent
   (bound one per cent: held, barely).
3. energy K + W: +8.9e-4 at half the free-fall time, +8.7e-4 at t = 1.0, maximum 1.45e-3
   (held). With the mesh potential energy instead, K + W_mesh drifts to +1.6 per cent:
   the particle sum is the consistent one (its gradient is the force applied).
4. second moment: I within 3.7e-4 (half) and 7.0e-3 (end); dI within 9e-4 and 1.3e-3;
   d2I within 1.9e-3 and 1.1e-3: held. d3I: the difference quotient deviates by 8.6 per
   cent rms and by -10 per cent at half the free-fall time: FAILED as predicted (ten per
   cent "at t = 1.0" held, -3.8 per cent, but the deviation is not small anywhere).
   Averaged over 57 steps (a tenth of the free-fall time) it agrees to +0.8 per cent at
   half the free-fall time and -0.1 per cent at the end. Reading: d2I carries an error
   of about 1e-3 that oscillates as the edge of the ball moves across cells; its time
   derivative is of the size of d3I itself early on. To be tested at N = 128: if the
   oscillating part of d2I is of second order in dx its derivative is of first order.
5. columns: centred difference of I against dI: 4.0e-5 (held). Centred difference of dI
   against d2I: 7.6e-4, above the bound of 1e-4: FAILED. Expected cause, to be tested
   with half the step (the difference must fall by four if it is truncation error of
   the difference, and stay if the acceleration in the sums were not the one applied):
   the fourth time derivative is dominated by the force fluctuation at the cell-crossing
   rate, which I had not counted. d3I equals the quotient of d2I to 9e-15 (construction).
6. momentum 2e-16 and angular momentum 2e-18 in units of M sqrt(GM/R) (R): held.
Solver: 14 V cycles per step on average to a defect of 6e-12 (`threshold = 0`).
