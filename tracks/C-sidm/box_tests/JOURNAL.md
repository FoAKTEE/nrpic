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

## 2026-11-15 T0b: first outcome (run C-20261115-165932-c04cf46)

With the key cycle = the dump's `cycle` field (20), the replay reproduces, for all six
dumps (2 seeds x plain, sub, f2), the cell index, n_sub and the number of momentum
updates of every one of the 1e4 particles, the collided momenta to 2.2e-16 to 4.4e-16 of
max(1, |u|), and leaves every other particle bit-identical; the neighbouring key cycles 19
and 21 do not (other updates, momenta off by O(1)). The summary flag was false because my
driver compared the replay's totals with the coll.hst record labelled `ncycle` = 20; the
replay's totals (e.g. plain s1: 5045 tested, 27 collisions) equal those of the record
labelled 21. Cause, checked: coll.hst labels a record with the number of completed steps
(collisions.md section 5, "number of completed steps"), the dump and the key use
`pmesh->ncycle` of the step being taken (sections 3.10, 5); after the mismatch I read the
lines that write them (`nrpic_collide.cpp` 331, 333, 519, 801, 812: `ncyc = pm->ncycle + 1`
for the record, `pm->ncycle` for the dump and the key). The documentation is consistent;
the off-by-one is easy to trip over (request to core: one sentence in section 5). Driver
corrected to compare with record c + 1; rerun. Also seen: the f2 dumps (8^3 mesh, cell
factor 2) give exactly the same tested pairs and collisions as the sub dumps (4^3 mesh),
as collisions.md section 8 states for blocks of f^3 cells.

T0b rerun (run C-20261115-170155-13ff01f): PASS in all six dumps. Replay = code for every
particle (cell, n_sub, updates); n_tested and n_coll equal to the record of the dumped
step (plain: 5045/27 and 5042/26; sub and f2: 15153/459 and 15423/512); sum_P to 4.4e-16
to 2.2e-15 relative; max_P to the last digit; collided momenta within 2.2e-16 to 4.4e-16
of max(1, |u|) (about 20 percent exactly equal); untouched particles bit-identical; 28 to
104 odd cells per step (triples) replayed. Prediction confirmed. Figure
`figs/t0b_replay_cpu.png` (looked at).

T10 third run (C-20261115-165902-f9b1c8f): PASS. 1, 8, 64 MeshBlocks and the restarts
from cycles 0, 37, 74 give bit-identical final snapshots (1e5 particles, 3.86e5 collisions,
n_sub up to 4) and identical integer columns in every common coll.hst record; seed 8
differs in 100 percent of the particles. MPI variant not run (no MPI in the release
build). Prediction confirmed. Figure `figs/t10_repro_cpu.png` (looked at).

## 2026-11-15 T1 and T2: outcome (run C-20261115-165500-c67e036)

All 16 collisional runs pass T2(a), (b), (c) and T1 per step; no truncation.
- T2(a): z from -2.10 to +1.58.
- T2(b): mean sum_P per step / expectation (sample theta) from 0.99991 to 1.00010, z from
  -2.20 to +2.92 (range corrected at the end of the session from the run's JSON; the
  first entry said 0.99987 to 1.00008). With the nominal theta of the generator the ratio stays within 1e-3 but
  z reaches 35.6 (theta = 1e-3, sub, s1) and 26.5: the 4 se clause would have failed
  there, as the prediction feared; the sample temperature, declared before the run, is the
  one T2(c) defines. Diagnostic: the mean Moller speed of the tested pairs (sum_P/sum_W)
  equals <v_Mol>(theta_sample) within 1.0e-4 at every temperature (-9.8e-5 to +8.7e-5),
  and sum_W per step equals (1/2) N rho_0 sigma dt within 6e-5.
- T2(c): theta unchanged to 7.5e-13 sigma (energy exactly conserved).
- Sub-cycled variant: max_nsub 5-6, mean n_sub 2.36 (theta = 1e-3) to 3.23 (theta = 10),
  max_P 0.098-0.115 (pmax 0.1; core reports up to 0.113), n_trunc = 0. My prediction said
  n_sub 3-8: the mean is lower at theta = 1e-3 (2.4), the maximum within.
- T1 per step: |dE|/sum_MW at most 2.8e-19, |dP_i|/sum_MW at most 9.4e-20, i.e. 1.1e-7 of
  the bound 1e-14 sqrt(n + 1); the exactly rounded sum of M W of the final snapshot equals
  that of the initial one to the last bit in all 16 runs (up to 1.39e7 collisions), the
  momentum sums to <= 3e-19 of sum M W. Prediction confirmed.
- KS of the final |u| against MJ(theta_sample) (diagnostic): p from 0.095 to 0.985.
- Processor cost (one core, 1e6 particles, 32^3 cells, machine shared, load ~45): 0.60 s per
  step plain (one sub-step), 0.76-0.86 s per step with 2.4-3.2 sub-steps on average, 0.28-
  0.30 s per step without collisions; per tested pair 5.8e-7 to 6.4e-7 s (plain) and
  3.3e-7 to 3.7e-7 s (sub-cycled: the per-cell set-up is shared by the sub-steps); per
  particle and step 3.0e-7 s at one sub-step. Prediction (within twice core's 0.54/0.27 s)
  confirmed: 1.1 times.
Figures `t2_rate_cpu.png`, `t1_step_cpu.png` looked at (tick labels of the middle and
right panels of the first overlap; a cleaner version is made by `figures.py` at the end).

## 2026-11-15 Card: cost per pair and T10b, predictions (before the run)

List `inputs/card_T2.list`, release card executable, one A100, the particle files and the
overrides of the processor runs T2 theta = 0.1 and 1 (plain and sub, seed 1), a run
without collisions, and 2000-step versions at theta = 0.1 (plain, sub, off) to separate
the start-up from the per-step cost (timing from the `elapsed` lines every 100 cycles).
Predictions: the card runs take the same collisions as the processor runs, digit for
digit, in the 200-step runs (core reports this for its boxes, collisions.md section 8),
so T10b (statistics within 4 sigma) passes trivially; if the counts differ, T2(a)-(c) must
still pass on the card. Cost: below 1e-8 s per tested pair (core: 1e6 particles x 200
steps in 2-4 s including start-up), i.e. at least 50 times the processor. Card time below
0.1 card-hour.
Submitted as run C-20261115-170447-cb3b230 (Slurm job 4464); the queue held nine jobs of
other owners at submission.

## 2026-11-15 T3, T4, T5: predictions (before the runs)

`scripts/t345.py`: twotemp (theta_1 = 3 theta_2, n1 = n2 = 5e5), theta_2 in {1e-3, 1},
seeds 1 and 2, sigma = 1, rho_0 = 1, 16^3 cells (244 per cell, so that the occupation
effect core reports at 12-98 per cell stays out of the way), dt = 0.005 tau_rel. Run A to
0.25 tau_rel with snapshots every 0.01 tau_rel, run B (same file, seed, dt) to 15 tau_rel
with snapshots every 0.25 tau_rel; the analysis is `collide/analysis/an_box.py relax` of
wave 1, unchanged, on A's snapshots followed by B's later ones (B at 0.25 tau_rel must
equal A's last snapshot bit for bit).
Predictions:
- T4: slope/exact = 1 + dt/(2 tau_rel) = 1.0025 (first-order splitting, the
  forward-Euler excess nu^2 dt/2 that core measured, collisions.md section 8) within the
  noise; |ratio - 1| < 0.01 in all four runs, so the criterion (4 se + 1 percent and at
  most 5 percent) passes. The non-relativistic form would give 1/0.2382 = 4.2 times the
  rate at theta_2 = 1; a code with |v_a - v_b| would give 1.27 (TESTS.md): both refuted
  by the criterion.
- T3: at 15 tau_rel KS p > 1e-3 against MJ(theta_eq) in all four runs; <u^2/W>/3 and
  both population temperatures at theta_eq within 4 sigma.
- T5: s(0) = s_mixture within 4 se; no decrease beyond 4 sqrt 2 se between snapshots
  0.25 tau_rel apart; s(15 tau_rel) = s_MJ(theta_eq) within 4 se (gaps 0.0448 and 0.1220,
  se ~1.5e-3).
- T1 over the 3000-step runs: per-step criterion holds; exactly rounded sum M W unchanged
  to < 1e-15 relative.
Refuted by any of the four runs failing a criterion.
Started as run C-20261115-170539-28432c3 (A runs: 50 steps in 32 s; B runs: ~0.6 s/step).

## 2026-11-15 T1 over 1e4 steps, T9: predictions (before the runs)

T1 long (`scripts/t1long.py`): twotemp theta_1 = 0.3, theta_2 = 0.1, 1e5 particles, 16^3
cells, sigma = 4, dt = 0.01, 1e4 steps, seeds 1 and 2 (~1e3 collisions per step, ~1e7 in
the run, ~200 per particle). Prediction: the exactly rounded sum M W of the snapshots
every 1000 steps equals the initial one to the last bit or within 1e-16 relative (T1/T2
showed bit equality after 1.4e7 collisions); the coll.hst sum_MW (a plain floating sum)
moves by < 1e-14; per-step criterion with the same margin as in T2 (~1e-7 of the bound);
n_trunc = 0. Refuted by a drift above 1e-11 or any step above the bound.

T9 (`scripts/t9.py`): `make_box unequal` (8e5 of mass M at theta_A = 0.03, 2e5 of mass 4M
at theta_B = 0.01), sigma = 1, 16^3 cells, nanbu, dt = 0.02 tau_rel = 0.0997, 750 steps
(15 tau_rel = 74.8), 8 seeds; plus the seed-1 file with coll_weights = equal for one
step. Predictions: both classes end at one temperature (|z| < 4 in all 8 seeds) and pass
KS against MJ at their final temperature (p > 1e-3); the energy drift per seed is a
random walk of relative size ~1e-3 of the thermal energy (core: 0.4 percent scatter
after 25 collision times with 2e5 particles; with 1e6 particles and ~15 tau_rel I expect
~0.1-0.2 percent), with a mean over the 8 seeds within 4 se of zero; the same for the
momentum components; updates per collision 1.53-1.54 (20/13 = 1.538 if the Moller
speeds of the three pair kinds were equal); the run with coll_weights = equal exits
non-zero at start-up with a message that names the masses. Refuted by any seed failing,
by a mean drift beyond 4 se, or by the equal-weights run proceeding.

## 2026-11-15 T1 over 1e4 steps: outcome (run C-20261115-170741-248af65)

PASS, both seeds: 1.559e7 collisions per run (156 per particle), max n_sub 2, max_P
0.0998, n_trunc 0. The exactly rounded sum M W is bit-identical at all 11 snapshots
(every 1000 steps) to the initial one; the momentum sums move by <= 2.4e-18 of sum M W;
the coll.hst float sum_MW wanders within +-4.6e-14 (rounding of the plain sum, no
trend); per step |dE|/sum_MW <= 3.5e-19 (8.8e-7 of the bound). Prediction confirmed.
Wall 512-551 s for 1e4 steps of 1e5 particles (0.05 s per step, 2 processes on a loaded
machine). Figure `figs/t1_long_cpu.png` looked at.

## 2026-11-15 T11: design (run C-20261115-171719-7daad65) and predictions (before the run)

Design: (a, b) theta = 1, beta = 0.6: 0.62774 collisions per particle per lab time,
5.022e6 expected in 200 steps of 0.08 (1e6 particles); lab means of the drifting MJ gas
<W> = 4.66305, <u_x> = 3.27783, <u_x^2/W> = 2.76670, <u_y^2/W> = theta/gamma = 0.8.
(c) theta 3 and 1, both drifting at 0.6: the conserved lab means <W> = 8.72811,
<u_x> = 6.19686 fix the end state at theta_f = 2.01532, beta_f = 0.59922 (the drift of a
lab-homogeneous box changes by -7.8e-4 because the lab energy and momentum densities of
the start hold the pressure terms of two temperatures); reading "drift unchanged, theta
from the energy" gives theta = 2.01318. End-state <u_x^2/W> 5.32672 (alternative 5.33246),
<u_y^2/W> 1.61343 (1.61054), start values 5.31812 and 1.6.
Predictions: (a) z within +-2 in both seeds (Poisson sigma 2240 on 5.0e6); a code with
|v_a - v_b| would be 1.48 times high (TESTS.md). (b) all four lab moments unchanged
within 4 se (W and u_x exactly, by conservation). (c) end-state moments equal those of
MJ(theta_f, beta_f) within 4 se and both KS p > 1e-3; <u_y^2/W> moves from 1.6 to 1.613,
about 6 se, so the relaxation itself is resolved, while the two readings of theta_eq
differ by only ~1 se in each moment: the test does not decide between them at 1e6
particles (said now, before the run). Refuted by any criterion failing.
T11 submission: refused twice by nrpic-run (4 cores, then 1 core: the owner's 16 cores at
a time were taken by the live runs of this package and of the other helpers); resubmitted
once T3-T5 frees its cores. No manifest was written for the refused submissions.

## 2026-11-15 Finding F3: the snapshot header's cycle lags the history by one

Read from the smoke run C-20261115-164809-cd53539 (no new run): the snapshot written
after 5 steps (time 0.05, dt 0.01) carries cycle 4 in its NRPSNAP1 header, while
`box.nrpic.hst` and `box.coll.hst` label the same time with cycle 5 (likewise 9/10,
14/15, 19/20; in T10 the final snapshot at time 2.0 after 100 steps says 99). The
initial snapshot says time 0, cycle 0. So the header holds the number of the step being
taken (`pmesh->ncycle` before the increment) next to the time after the step.
`docs/FORMATS.md` line 123 says only "int64 cycle". Not a defect of the collision
operator; it matters to anyone who aligns snapshots with history records or collision
dumps by cycle (the dump of `coll_dump_cycle = c` and the snapshot labelled c both
belong to the step recorded as c + 1 in the histories). Request to core: document the
convention (FORMATS.md, collisions.md section 5) or align the labels.

## 2026-11-15 T3, T4, T5: outcome (run C-20261115-170539-28432c3)

All four runs (theta_2 = 1e-3 and 1, seeds 1 and 2) pass T3, T4 and T5; B at 0.25
tau_rel is bit-identical to A's last snapshot in all four (A and B are the same
trajectory). 1.13e7 (theta_2 = 1e-3) and 1.47e7 (theta_2 = 1) collisions per run, n_sub = 1
throughout, exactly rounded sum M W of the final snapshot equal to the initial one to
the last bit, T1 per step passes. Wall 1930-2000 s for 3000 steps (0.65 s per step).
- T4, slope/exact (exact from the sample's own initial temperatures): theta_2 = 1e-3:
  0.9924 (se 0.50 percent), 0.9792 (se 0.64 percent); theta_2 = 1: 0.9959 (0.32
  percent), 1.0088 (0.27 percent). Criterion (|d| <= 4 se + 1 percent and <= 5 percent):
  pass in all four. My prediction |ratio - 1| < 0.01 FAILED for theta_2 = 1e-3, seed 2
  (2.1 percent low, 3.3 se below the expected 1.0025), and the noise is about twice what I
  assumed (se 0.3-0.6 percent, not ~0.3). Both theta_2 = 1e-3 seeds are low (-1.5 and
  -3.3 se from 1.0025); two runs cannot tell a systematic of a few tenths of a percent
  from noise. Not chased further here [JUDGEMENT]: the criterion was set with this noise
  in mind, the theta_2 = 1 pair straddles 1, and core's time-step study (collisions.md
  section 8) found the dt -> 0 slope at 1.000(4) and 0.995(4) of the non-relativistic
  form at theta = 0.01. A tighter T4 needs more particles or more seeds (open item O3).
  The non-relativistic rate (4.2 times the exact one at theta_2 = 1) and |v_a - v_b|
  (1.27 times) are excluded by a wide margin.
- T3 at 15 tau_rel: KS p = 0.084, 0.77, 0.99, 0.92; |<u^2/W>/3 - theta_eq| = 3.5e-9,
  1.8e-9, 8.1e-6, 6.3e-6, i.e. < 0.01 se in all four (energy is exact); population
  temperatures at the end differ from theta_eq by -6.4e-7/+6.4e-7 and +1.8e-6/-1.8e-6
  (theta_2 = 1e-3; se ~2.3e-6) and -1.2e-3/+1.2e-3, +9e-5/-9e-5 (theta_2 = 1; se ~1.7e-3),
  all below 1 se.
- T5: s(0) - s_mixture = -2.8e-4, -3.6e-4, -2.6e-4, -1.5e-4 (se 1.5e-3, 2.4e-3); the
  entropy rises monotonically (no pair 0.25 tau_rel apart decreases beyond 4 sqrt 2 se);
  s(end) - s_MJ(theta_eq) = -2.5e-5, +1.0e-5, +3.2e-5, +4.3e-5 (< 0.03 se). The gaps
  0.0449/0.0449 and 0.1231/0.1215 are resolved at ~30 and ~50 se.
Figures `relax_T345_*.png` (four, looked at): temperatures follow the two-MJ guide to
equilibrium, the entropy climbs from the mixture value to s_MJ, the final |u| histogram
lies on MJ(theta_eq). The T4 window is too compressed there to judge the slope by eye;
a zoom is made by `t4zoom.py` at the end.

## 2026-11-15 T9: outcome (run C-20261115-170814-8a54b43)

PASS. Eight seeds, 1e6 macroparticles (8e5 of M, 2e5 of 4M), nanbu, 750 steps to 15.0
tau_rel, 1.51e7 collisions per run, n_sub up to 5, n_trunc 0, rest masses unchanged to
the bit.
- Same temperature at the end: z = (theta_A - theta_B)/sigma from -1.16 to +0.56.
- Maxwell-Juttner at the class's own final temperature (declared criterion): KS p from
  0.089 to 0.93 for both classes in all seeds. Against theta_eq of the initial energy
  (reported): p down to 1.7e-4 (seed 3, class A), because nanbu's energy random-walks:
  seed 3 ended 0.49 percent of the thermal energy above its start, so its temperature is
  above theta_eq.
- Drifts of the exactly rounded sums over the run: energy dE/E_kin = +0.0019, -0.0015,
  +0.0049, +0.0029, +0.0019, +0.0027, -0.0008, +0.0020; mean dE = 5.4e-5 (se 2.2e-5,
  z = +2.42); momenta z = +0.40, +2.19, +1.08. Within the criterion (4 se). Six of eight
  energy drifts are positive and the mean is +0.18(7) percent of the thermal energy: a
  bias of nanbu's energy at this level is neither shown nor excluded by eight seeds
  [JUDGEMENT]; core's own run found -0.0020(21) (collisions.md section 8). Open item O4.
- Updates per collision 1.5398-1.5402 (prediction 1.53-1.54; 20/13 = 1.538 for equal
  Moller speeds of the three pair kinds).
- coll_weights = equal on the same file: rc 1 at start-up with "### FATAL ERROR in nrpic
  collisions / <particles> coll_weights = equal, but the colliding particles have unequal
  rest masses (smallest and largest: 6.25e-07 and 2.5e-06); use equal masses or
  coll_weights = nanbu".
Prediction confirmed, except that my expectation of a 0.1-0.2 percent energy scatter was
low: the per-seed scatter is 0.2 percent around a +0.18 percent mean. Figure
`figs/t9_unequal_cpu.png` looked at (the right panel's label overlaps the middle panel;
cosmetic).

## 2026-11-15 T11: outcome (run C-20261115-174651-0ad8612)

PASS, both seeds, all three parts (n_trunc 0, n_sub up to 4).
- (a) Accepted collisions over 200 lab steps against the analytic expectation with the
  sample's (theta, beta) = (1.00077, 0.599993) and (1.00156, 0.599704): 5024748 vs
  5022176 (z = +1.15) and 5025501 vs 5025067 (z = +0.19); accepted vs sum_P z = +0.52,
  -0.21. A code with |v_a - v_b| (1.48 times) is excluded. Prediction confirmed.
  Reported, not a criterion: the mean sum_P per step exceeds the same expectation by
  2.8e-4 and 1.8e-4, which is z = 5.8 and 4.1 against the step-to-step standard error;
  in the non-drifting T2 runs at theta = 1 the same comparison gave -0.3 and +1.3. See
  the diagnostic below.
- (b) Lab moments at 16.0 (10 lab collision times) against t = 0: all |z| < 1.2
  (<W> and <u_x> unchanged by conservation; <u_x^2/W>, <u_y^2/W> within noise).
- (c) Drifting two-temperature start (3 and 1, beta = 0.6), 470 steps (37.6 = 15
  tau_rel(rest) gamma_b): end-state moments against MJ(theta_f, beta_f) of the conserved
  lab means (seed 1: 2.01675, 0.59944; seed 2: 2.01460, 0.60000) within |z| <= 1.0; KS
  of lab u_x p = 0.21, 0.92 and of |u_perp| p = 0.84, 0.89. As said before the run, the
  alternative reading (drift fixed, theta from the energy) is not distinguishable here.
Figure `figs/t11_drift_cpu.png` looked at: the end-state lab u_x histogram lies on the
drifting MJ reference, well away from the start.

## 2026-11-15 Diagnostic D1 of the T11(a) sum_P excess: prediction (before the run)

`scripts/t11diag.py` on the T11 run: sum_P = sum_W x (mean Moller speed of tested
pairs). Expectation [JUDGEMENT]: the occupation part sum_W per step equals (1/2) N rho
sigma dt within its noise (as in T2: within 1e-4), so the excess sits in the mean
Moller speed of the tested pairs; a Monte Carlo over 4e6 random pairs of the initial
snapshot then tells whether the sample itself carries it (the generator's boosted
sampler) or the tested pairs differ from random pairs (the operator). If the Monte Carlo
also shows +2e-4 the operator is cleared and the generator or the analytic reference is
in question; if not, the operator's pair selection or v_Mol in a drifting gas is.

D1 outcome (run C-20261115-180041-f00f777): the occupation part is clean (sum_W per step
/ (1/2) N rho sigma dt = 1.000039(18), 0.999983(19)); the excess sits in the mean Moller
speed of the tested pairs, 1.000240(44) and 1.000196(40) of <v_Mol>(theta_s)/gamma_s^2
(z = 5.5, 4.9). The Monte Carlo over 4e6 random pairs of the initial snapshot gives
1.00024(35) and 1.00033(35): too coarse to say whether the sample itself carries the
offset. Prediction half confirmed (occupation clean), half undecided.

## 2026-11-15 Diagnostic D2: random pairs of the snapshots at 2e8 pairs (prediction first)

Same script with 2e8 random pairs per snapshot (se ~2.5e-5), initial and final snapshot
of both T11ab seeds. Prediction [JUDGEMENT, because in the gas at rest (T2) the tested
pairs matched <v_Mol> to 1.6e-4 with no sign of a bias]: the sample's random-pair mean is
itself ~2e-4 above <v_Mol>(theta_s)/gamma_s^2 and equals the tested-pair mean within 3 se,
which clears the operator and puts the offset in the boosted generator or in my analytic
reference for the drifting gas. Refuted if the random-pair mean equals the reference
within 3 se while the tested pairs stay 2e-4 above it: that would point at the operator's
pair statistics in a drifting gas (to be reported to core with this reproduction).

## 2026-11-15 Card: outcome (runs C-20261115-170447-cb3b230, analysis C-20261115-180525-94ddd22)

Slurm job 4464 ran the eight entries in 51 s (0.014 card-hour), all rc 0.
- T10b PASS: in the four 200-step runs the card takes the same tested pairs and the same
  collisions as the processor at every step (n_tested and n_coll identical record by
  record), sum_P within 9e-14, final momenta within 8.9e-15 (not bitwise: the card's
  arithmetic differs in the last digits); T2(a)-(c) and T1 pass on the card with the same
  z values as the processor runs. Prediction confirmed.
- Cost on one A100, 1e6 particles, 32^3 cells, from the `elapsed` lines (cycles 100 to
  2000 of the long runs): 3.25 ms per step with collisions at one sub-step, 6.37 ms with
  2.79 sub-steps on average, 1.18 ms without collisions; the collision part costs
  3.9e-9 s per tested pair (2.1e-9 s per particle and step) and 3.4e-9 s per tested pair
  when sub-cycled. The 200-step runs give 3.5e-9 to 4.2e-9. Processor (one core, same
  problems): 5.7e-7 to 6.7e-7 s per tested pair at one sub-step, 3.3e-7 to 3.5e-7
  sub-cycled. Ratio processor/card for the collision part: 96 to 173. Start-up 0.2-4.7 s.
  Prediction (< 1e-8 s per pair, >= 50 times the processor) confirmed.
Figure `figs/cost_gpu.png` looked at.

## 2026-11-15 D2: outcome (run C-20261115-180434-fd05776)

Lab-frame Moller speed of 2e8 random pairs (se 5e-5 relative) of the T11ab snapshots,
relative to <v_Mol>(theta_s)/gamma_s^2:
- seed 1: initial snapshot 1.000501 (z = +10.0), final snapshot 0.999627 (z = -7.5);
  tested pairs over the run 1.000240(44), between the two;
- seed 2: initial 1.000241 (z = +4.8), final 1.000234 (z = +4.7); tested 1.000196(40),
  0.7 se from the initial sample.
So a sample of 1e6 particles has its own all-pairs mean Moller speed, which differs from
the ensemble value by several 1e-4 and wanders by as much while collisions redistribute
the momenta at fixed energy and momentum (seed 1: by 8.7e-4 within the 200 steps). This
is the finite-sample fluctuation of a pair average (a U-statistic: relative scatter
~2 sd(h1)/(<v> sqrt N) with h1 the mean Moller speed of one particle against the gas;
a few 1e-4 at N = 1e6 if the part of h1 not fixed by the conserved energy and momentum
has sd ~0.1-0.2 of <v>) [JUDGEMENT; the size is inferred from these numbers, not
computed]. The tested pairs follow the sample (seed 2 within 0.7 se; seed 1 between its
start and end values). In the gas at rest of T2 the temperature measured from the sample
absorbs most of this, because there h1 depends mainly on the energy; in the drifting gas
the anisotropy of the sample (u_x against u_perp) is not fixed by conservation and
carries it. Cause of the T11(a) sum_P excess: the reference, not the operator. My D2
prediction (sample ~2e-4 high, tested pairs equal to it within 3 se) held for seed 2 and
for seed 1 only after allowing for the sample's change during the run.
Consequence for test design (for the lead): a rate check at the 1e-4 level must compare
the tested pairs with the sample's own pair mean at the same time (or use sum_P/sum_W
against a pair Monte Carlo of the same snapshot), not with the ensemble formula; the
step-to-step standard error does not contain the sample's fluctuation. The criteria of
T2(b) and T11(a) as written are not affected (both pass), but T2(b)'s 4 se clause is
fragile in a drifting gas or at higher precision.

## 2026-11-15 Record of runs not named above

C-20261115-165428-20023eb: pipeline check of `t1t2.py` at N = 2e4, 20 steps, theta = 0.1
(not a test; it showed overlapping labels in the first T2 figure, fixed before the T2 run).
All 18 runs of this package are registered with nrpic-run and closed (17 completed, one
failed: C-20261115-165742-2c645f8, the first T10 attempt, driver defect described above).
