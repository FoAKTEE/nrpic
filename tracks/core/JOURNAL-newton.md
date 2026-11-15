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
