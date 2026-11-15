# JOURNAL of box_tests (helper of C-sidm, wave 2)

Box tests of the collision operator of release core-v0.3 with the release executables
(`/data/haiyangw/nrpic/.work/build_cpu_v03/src/athena`, serial Kokkos, no MPI;
`.../build_gpu_v03/src/athena`, one A100), against `../collide/TESTS.md` (criteria fixed in
wave 1; not changed here; a new criterion would be a new test) and the option names of
`coord/INTERFACES/collisions.md`. Entries are appended; predictions are written before the
run they concern, outcomes after it, failed predictions included.

## 2026-11-15 S0 smoke run (formats only)

Purpose: learn the header of `box.coll.hst`, the dump layout and the snapshot names of the
release executable on a 1e4-particle box (theta = 0.1, sigma = 10, 4^3 cells, 20 steps,
dump at cycle 5). No criterion. Expectation: the run ends with rc 0; the dump parses with
the layout of collisions.md section 5 (18 doubles and 7 int32 per particle, file length
exact); lapse 1, gamma = identity, proper volume 1/64 in every record.

Outcome (run C-20261115-164809-cd53539): rc 0, 0.14 s. Header of `box.coll.hst` has the 31
columns of collisions.md section 5 by name (`n_coll`, `n_trunc`, `sum_P`, `dE`, `dP1..3`,
`sum_MW`, `sum_W`, ...). The dump `box.coll_dump.5.bin` parses with the layout of section 5
to the last byte (18 doubles and 7 int32 per particle); alpha = 1, gamma = identity,
proper volume 1/64 = 0.015625 in every record; triad gauge word 1; n_sub 2 and 3 (measured
rule). Finding F1: `box.nrpic.hst` column `sum_mW` is 0 at every record, because it is the
sum of the last deposit and `deposit = false` in the box (documented:
`coord/INTERFACES/diagnostics.md` line 46, "0 without deposit"). TESTS.md T1 names that
column for the drift over 1e4 steps; the same quantity, sum M W over the particles, is
taken here from the exactly rounded sums of the snapshots (and from `coll.hst` `sum_MW`,
which in the flat box is the same sum). This is a change of the file the number is read
from, not of the criterion.

## 2026-11-15 Design numbers (run C-20261115-165028-a559ab8, before any test)

`scripts/design.py`, track references only. T2 (sigma, dt chosen so that max P ~ 0.02 and
a particle moves half a cell rms per step): theta = 1e-3: sigma 0.1447, dt 0.2855, 1472
expected collisions per step; 0.1: 0.2025, 0.03185, 1993; 1: 0.3265, 0.01713, 2744; 10:
0.3548, 0.01566, 2778 (<v_Mol> = 0.071254, 0.618059, 0.980849, 0.999979; the Monte Carlo
of 4e6 pairs agrees within -1.3 to +1.4 standard errors). Variant `sub`: sigma x 25.
T3/T4 (sigma = 1, rho_0 = 1, theta_1 = 3 theta_2, n1 = n2): theta_2 = 1e-3: tau_rel =
14.955, exact initial slope of theta_1 - theta_2 = -1.33738e-4 (0.99384 of the
non-relativistic form), theta_eq = 2.00124e-3, entropy gap 0.04476; theta_2 = 1: tau_rel
= 1.97343, slope -1.01346 (0.2382 of the non-relativistic form), theta_eq = 2.01481, gap
0.12202. T9 (theta_A = 0.03, theta_B = 0.01): tau_rel = 4.985, theta_eq = 0.020112.
T11 (theta = 1, beta = 0.6): 0.62774 collisions per particle per lab time.

## 2026-11-15 T1 and T2: predictions (before the runs)

Set-up: `scripts/t1t2.py` on the design JSON; mj box, N = 1e6, 32^3 cells (30.5 per cell),
200 steps, four temperatures x {plain, sub} x seeds {1, 2} = 16 collisional runs, plus two
collisionless baselines for the cost. Processor executable. The temperature in T2(b) is
the gas temperature from <W - 1> of the initial snapshot, the quantity T2(c) names (the
nominal temperature of the generator differs from it by ~1e-3 relative, which moves
<v_Mol> by ~5e-4, as much as the tolerance; the ratio with the nominal temperature is
reported too). In T1 the momentum defects dP_i are normalised by sum M W (the pair-energy
scale of T0), since sum M u_i is zero by construction.

Predictions:
- T2(a) passes in all 16 runs (|z| < 4; expected |z| ~ 1). Refuted if the accepted count
  differs from sum_P by more than 4 sqrt(sum_P) in any run.
- T2(b): mean sum_P per step / expectation within 1e-3 of 1 in all runs and within 4 se.
  Core reports the mean Moller speed of the tested pairs equal to the Maxwell-Juttner
  value to 7.7e-5 (collisions.md section 8, its own runs). Risk named before the run: the
  cell occupation sum N_c (N_c - 1) of one configuration differs from its mean by ~2e-3
  relative and stays correlated over a few steps, so the step-to-step standard error can
  understate the true one; a failure of the 4 se clause with |ratio - 1| < 1e-3 would
  point there, and the diagnostic sum_P/sum_W (mean Moller speed of the tested pairs,
  free of the occupation) decides. Refuted if |ratio - 1| > 0.005 in any run.
- T2(c): theta constant to rounding (energy is conserved per pair): |z| << 1.
- Sub-cycled variant: n_sub between 3 and 8 (measured rule, v_bound = v1 + v2), n_trunc = 0,
  max_P below ~0.12.
- T1 per step: |dE|/sum_MW ~ 1e-18 (pair defects of order eps x pair energy, M = 1e-6),
  far below 1e-14 sqrt(n + 1) ~ 4e-13; |dP_i|/sum_MW smaller; exactly rounded snapshot sums
  change by < 1e-16 relative. Refuted if any step exceeds the bound or n_trunc > 0.
- Cost (processor, one core, 1e6 particles): about 0.5 s per step with collisions at one
  sub-step and 0.25 s without (core's numbers, collisions.md section 9), i.e. ~5e-7 s per
  tested pair. Refuted (as a number to plan with) if more than twice that.

## 2026-11-15 T10 and T0b: predictions (before the runs)

T10 (`scripts/t10.py`): twotemp box theta_1 = 0.3, theta_2 = 0.1, 1e5 particles, 16^3
cells, sigma = 5, dt = 0.02 (P_bound ~ 0.16, so n_sub ~ 2: sub-cycling active), 100
cycles, rng_seed 7; 1, 8 and 64 MeshBlocks; resumed from every restart file of the
8-block run (written every 37 cycles); rng_seed 8 as the negative control. MPI ranks: not
run, the release processor build has no MPI (CMakeCache: Athena_ENABLE_MPI=OFF).
Prediction: final snapshots bit-identical for 1, 8, 64 blocks and for every restart
(core reports the same with its own box, collisions.md section 8); the coll.hst integer
columns identical record by record; seed 8 changes more than 99 percent of the particles
(~2.5e5 collisions over 1e5 particles: each collides ~5 times). Refuted by any bit
difference, or by seed 8 leaving most particles unchanged.

T0b (`scripts/t0b.py`, `scripts/replay.py`): the replay is written from the text of
collisions.md (sections 3.1-3.7, 4, 5) with the track's oracle and `python/nrpic/rng.py`,
without core's twin `python/nrpic/collide.py`. T2 box at theta = 0.1, 1e4 particles, 4^3
cells, dump of cycle 20, triad = cholesky; variants plain (n_sub = 1), sub (sigma x 25) and
f2 (8^3 mesh, coll_cell_factor 2), seeds 1 and 2. Prediction: for every particle the cell
index, n_sub and the number of updates agree with the dump; n_tested and n_coll agree with
the coll.hst record of cycle 20; sum_P to < 1e-13 relative; collided momenta within ~1e-15
of max(1, |u|) (oracle and kernel agree to 3e-16 on the T0 vectors; a particle that
collides in several sub-steps accumulates a few such errors); untouched particles
bit-identical. The key cycle: collisions.md 3.10 says the key uses `pmesh->ncycle` of the
step being taken; whether that equals the dump's `cycle` field or differs by one is not
stated; the replay tries cycle, cycle - 1, cycle + 1 and records which reproduces the code
(a mismatch of the documented key would be a finding, not a failure of the operator).
Refuted by any differing tested or accepted pair, or a momentum beyond 1e-13.

T10 first attempt (run C-20261115-165742-2c645f8, failed, exit 1): a defect of my driver,
not of the code. The restart directory holds `box.NNNNN.rst` and `box.NNNNN.rst.prt`; the
driver resumed from every file, including the `.prt` particle files (the run from
`box.00000.rst.prt` stopped at once), and a resumed run in a new directory appends to
`box.coll.hst` without a header, which my reader refused. Fixed: only `*.rst` files; a
history without a header gets the column order of collisions.md section 5 (asserted equal
to the header of the fresh runs). Rerun below with the predictions unchanged.

T10 second attempt (run C-20261115-165821-5d4dc5c): 1, 8, 64 blocks and the restarts
from cycles 0, 37 and 74 give bit-identical final snapshots and identical integer columns
of every coll.hst record (sum_P differs by up to 1.2e-14 relative: the order of the sum
over blocks); seed 8 changes 100 percent of the particles. The summary flag said "pass:
false" only because the fourth restart file `box.00003.rst` is the one written at the end
of the run (cycle 100 = nlim): the run resumed from it takes no step and writes no
snapshot, which my driver counted as a failure. Driver corrected (such a restart is
recorded as skipped); rerun to get a clean summary and the figure.
