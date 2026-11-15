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
