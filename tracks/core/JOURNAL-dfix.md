# JOURNAL of core, work package dfix (branch `core/requests-adf`)

Append-only. Predictions are written before a test runs, outcomes after, also when the
prediction failed. Runs are registered under `tracks/core/runs/<run_id>/manifest.json`
(outputs under `scratch/core/<run_id>/`). Labels: [VERIFIED] read or measured in this
session (with locator), [BACKGROUND], [JUDGEMENT], [TO VERIFY].

## 2026-11-15 session dfix-1

Read: `CLAUDE.md`, charter to "Owners", brief lines 493-553, 688-706, 834-860, decisions
0010 to 0015, the rulings after wave 1, core's `HANDOFF.md`, `STATUS.md`,
`stage/G2/OPEN.md`, and the eleven requests of tracks D, A and F named in the task
(triage: `tracks/core/interfaces/REQUESTS_ADF.md`).

### T1 The tracer defect (request D `tracer-push-release-build`)

What Track D saw [VERIFIED from the message, run D-bh-dress-20261115-121313-284ec4f]: with
the card executable of release core-v0.2, the six tracers of
`problems/puncture/horizon_calib.athinput` do not follow their geodesics: one is removed
at t = 0.31 M, five leave outward near light speed.

What I read before any run [VERIFIED, file and line of this branch at 3da9086]:
- all six tracers of that input have `p<n>_m = 0.0` (lines 132-179), and the input calls
  them "massless tracers": test particles without sources on timelike geodesics;
- `athenak/src/particles/nrpic.cpp` line 462: `eps = (pr(IPM,p) > 0.0) ? 1.0 : 0.0`, and
  line 502 hands `eps` to `PushMidpoint` in the branch `metric = mesh` only. With
  `eps = 0` the pusher uses `W = sqrt(gamma^ij u_i u_j)` (`nrpic_kernels.hpp`,
  `LorentzFactorEps`): a null geodesic. The analytic-metric branches (lines 505-522) call
  the six-argument `PushMidpoint`, which sets `eps = 1`;
- the rule "no rest mass: null geodesic" entered with commit 4467852 (cosmology C0, null
  particles for light rays); the tracer inputs are older (935da4d). The light rays of
  `cosmo/ic/ray_ic.py` never carry m = 0: their mass is `-max(t_e, 1e-30)` (line 41).

Hypothesis H1: since 4467852 a particle with m = 0 on the mesh metric is pushed as a
photon with momentum k_i = u_i; nothing differs between card and processor builds, and
nothing is wrong with the reading of `p<n>_u<i>`. The tracer at rest (tag 5, u_i = 0) has
W = 0, its velocity alpha u^i/W is 0/0, the state turns non-finite and the particle is
removed in the first step.

Predictions, written before the runs (release executables of core-v0.3, unchanged):
- R1 (processors, `horizon_calib.athinput`, tlim = 1): tag 5 is removed in the first
  cycle (`n_excised = 1` in the first history record after t = 0); tags 0 to 3 move with
  the coordinate speed of light of the initial slice, alpha/psi^2 = psi^-4 with
  psi = 1 + 1/(2 r): 0.7260 at r = 6, 0.7847 at r = 8, 0.8227 at r = 10, measured from
  the first trajectory records (within 2 per cent: the lapse starts to evolve). A
  timelike tracer would move at psi^-4 [u^2/(1 + u^2)]^(1/2), u^2 = u_y^2/psi^4:
  0.3233 at r = 6, 0.2959 at r = 8, 0.2739 at r = 10.
- R2 (the same with `particles/p<n>_m = 1e-300` for n = 0..5 on the command line;
  `deposit = false`, so the mass has no other effect): no particle is removed, tags 0 to
  3 move at the timelike speeds above and keep their coordinate radius to 1e-3 over 1 M.
- R3, R4: the card executable gives the same as R1 and R2 (speeds equal to 1e-6).
H1 is refuted if R2 still shows the outward motion or the removal (then the reading of
the momenta or the push itself is at fault), or if R1 on processors is healthy while the
card run is not (then the defect is in the card build).

Registration: `harness/bin/nrpic-run submit` stops in `budget_state()` with
`KeyError: 'outputs'` (line 163, `is_live`: a hand-written manifest of wave 1 under
`tracks/core/runs/` has no `outputs` key). Runs of this package are therefore registered
by hand with `tracks/core/analysis/dfix/runreg.py` (same fields; the manifest is written
before the command starts). Reported in the requests of this package.

First look, before the runs ended (R1, R2 need about two minutes per cycle on one core;
run core-20261115-152835-920d573, records of cycle 4, t = 0.125 M) [VERIFIED]: R1 speeds
0.72603, 0.78467, 0.82271 for tags 0 to 2 and no record of tag 5; R2 speeds 0.32334,
0.29592, 0.27385 and tag 5 present. Both as predicted to four digits. The outcome entry
follows when the runs and the card runs R3, R4 (queued behind other owners' jobs) end.

### T1 correction and its regression (written before the regression runs)

Correction [JUDGEMENT]: a particle with m = 0 is a tracer on a timelike geodesic for
every metric source (the meaning of the seven tracer inputs under `problems/`, and what
the analytic-metric branches always did); null particles are the light rays, m = -t_e < 0
(`cosmo/ic/ray_ic.py` writes nothing else). The rule of releases core-v0.2 and core-v0.3
stays available as `<particles> zero_mass = null` (default `tracer`). At start-up the
code prints how many particles have m = 0 and how they are pushed. Changed lines:
`particles.hpp` (comment of `NrpicRealIndex`, `NrpicOptions::zero_mass_null`,
`NrpicReportMassless`), `nrpic.cpp` (`NrpicInit`: option; `NrpicPush`: `eps`),
`nrpic_io.cpp` (`NrpicReportMassless`, called from `NrpicStartup`).

Regression set-up: `problems/tests/tracer_mesh_circular.athinput`, the static mesh
metric of `docs/TESTLOG.md` "Mesh path (CPU, 2026-11-13)" (Schwarzschild, Kerr-Schild,
dx = 0.25 M, circular orbit at r = 8 M, dt = 0.1 M, 300 M; record of that entry: r in
[8.0000, 8.0012] M, relative errors 8.4e-7 in E, 5.1e-6 in L_z), particle with m = 0.

Predictions:
- (a) release executable core-v0.3 (it ignores `zero_mass`): the particle is a photon; it
  leaves the mesh (|x^i| = 12 M) before t = 15 M and is counted as escaped.
- (b) corrected executable: r stays in [8.0000, 8.0012] M for 300 M, relative errors of
  E = alpha W - beta^i u_i and L_z below 1e-6 and 6e-6 (the record of the old entry).
- (c) corrected executable, `p0_m = 1e-300`: trajectory file identical to (b), byte for
  byte.
- (d) corrected executable, `zero_mass = null`: trajectory file identical to (a), byte
  for byte (the option restores the released rule exactly).
The correction is refuted if (b) leaves the band or (c) differs from (b); the claim that
the option preserves the released behaviour is refuted if (d) differs from (a).

Outcome of the T1 regression (run core-20261115-154303-da69f6a; numbers from
`tracks/core/analysis/dfix/t1_tracer.py`, figure `figs/t1_regress.png`, looked at)
[VERIFIED]:
- (a) release: photon; last record at t = 15.6 M and r = 15.55 M (it leaves through a
  corner region of the cube), `n_escaped = 1`. The prediction "before t = 15 M" FAILED by
  0.6 M: I had taken r = 12 M as the edge, the cube reaches 12 sqrt(2) M in the orbital
  plane. The qualitative prediction (photon, escapes) holds.
- (b) corrected: r in [7.999998, 8.001151] M over 300 M; relative errors 2.6e-7 in E and
  5.05e-6 in L_z. Inside the record of the old entry ([8.0000, 8.0012], 8.4e-7, 5.1e-6).
- (c) equals (b) byte for byte (192128 bytes); (d) equals (a) byte for byte (10048
  bytes).
Not refuted. H1 is the cause on the static mesh as well; the correction restores the
recorded behaviour and the option reproduces the released one exactly.

### T2 The restart defect (request D `restart-skips-dump`)

Read [VERIFIED]: `Driver::Finalize` (driver.cpp, lines 655-661 at 3da9086) calls
`WriteOutputFile` of every output; every writer then does `last_time += dt` (for the
restart writer `outputs/restart.cpp` lines 196-200), also when the final output is not
on the schedule. The parameter dump inside the restart file carries the advanced values,
so the continued run waits for `last_time + dt` and skips one scheduled output of every
kind (`scripts/README.md`, "Restart caveats", first item, records the same).

Correction [JUDGEMENT]: in `Driver::Finalize` a final output that falls between two
scheduled times (single-precision test `time < last_time + dt`, the comparison of
`Driver::Execute`) leaves the schedule where it was: `last_time` is set back by dt before
the writer adds it (so that the dump inside the restart file is unadvanced too) and
restored exactly afterwards. A final output on the schedule (run ending at tlim) behaves
as before. One hook, `driver/driver.cpp`, in the loop of `Driver::Finalize`; no writer is
touched.

Set-up: `problems/tests/restart_schedule.athinput` (static mesh metric, one tracer;
restart dumps every 50 M, tables every 25 M, tlim = 300 M), script
`tracks/core/analysis/dfix/t2_restart.py`.

Predictions (written before the run):
- uninterrupted, either executable: restart files at t = 0, 50, ..., 300 (seven), tables
  at 0, 25, ..., 300 (thirteen);
- release core-v0.3, stopped at the cycle limit at t = 123.4 M and continued from the
  file written there: the restart dump of t = 150 M and the table of t = 125 M are
  missing (next restart dump at 200 M, next table at 150 M);
- corrected, the same sequence: nothing missing; the extra files at t = 123.4 M exist;
  the final particle state equals that of the uninterrupted run bit for bit;
- corrected, stopped at the wall clock limit (`-t 00:00:03`, particle step 0.002 M so
  that the run lasts about ten seconds) and continued: nothing missing.
The correction is refuted if a scheduled output is missing in a corrected case, or if the
uninterrupted corrected run writes other files than the release.

Runs: core-20261115-154650-cf9f921 failed at once (relative path of the executable, no
physics run). core-20261115-154659-cf9f921: the three deterministic predictions hold
(numbers in the outcome below), but the wall-clock case ended at the time limit: 150000
cycles take less than the three seconds I allowed, so it tested nothing. Changed before
the next run: particle step 1e-4 M and `-t 00:00:02` (a hand trial stopped at
t = 24.85 M with "Terminating on wall clock limit"), and the wall-clock case is run with
the release executable too. Added prediction: release, stopped at the wall clock near
t = 25 M and continued: the restart dump of t = 50 M and the table of the next scheduled
time are missing; corrected: nothing missing.

Outcome of run core-20261115-154739-a7a0010 [VERIFIED, `t2_restart.json` in the run
directory]: uninterrupted runs and the cycle-limit cases as predicted (release: restart
dump of 150 M and table of 125 M missing; corrected: nothing missing, final state equal
bit for bit). Release with the wall-clock stop (it stopped at t = 64.0 M): dump of 100 M
and table of 75 M missing, as predicted. The corrected executable with the wall-clock
stop (t = 25.0038 M) FAILED: restart dumps at 75.0038, 125.0038, ... 275.0038 M, the
scheduled 50, 100, ..., 250 M all missing. Cause, read in the writer and confirmed by the
rerun below: my first hook set `last_time` back by dt before the writer; with the last
dump at t = 0 that gives -50, and a negative `last_time` is the writers' mark for "never
written" (`restart.cpp` lines 196-198), so the writer stored the stop time as the new
origin of the schedule. The cycle-limit case stopped after the dump of 100 M and did not
reach that branch. Second version of the hook: the interval `out_params.dt` is zero while
the writer runs (no writer uses it for anything but the advance; checked with grep over
`outputs/*.cpp`), so `last_time` is unchanged bit for bit and never negative. Prediction
for the rerun: all three corrected cases complete; the release cases as before.

Outcome of T2, second version (run core-20261115-154901-d8ad7ec; figure
`tracks/core/analysis/dfix/figs/t2_restart.png`, looked at) [VERIFIED]:
- uninterrupted, release and corrected: restart files at 0, 50, ..., 300 M, thirteen
  tables; the same file lists for both executables;
- release, cycle limit at t = 123.4 M: dump of 150 M and table of 125 M missing;
  release, wall clock (stopped at t = 68.4 M): dump of 100 M and table of 75 M missing;
- corrected, cycle limit: nothing missing, extra files at 123.4 M, final particle state
  equal to the uninterrupted run bit for bit;
- corrected, wall clock (stopped at t = 26.7 M, i.e. before the first interval had
  passed, the case the first version got wrong): nothing missing.
Not refuted. Request D `restart-skips-dump` is met for every output kind with a `dt`
schedule. Line of `scripts/README.md` "Every wall-clock stop ... is skipped" is corrected
with this change.

### T3 Accretion diagnostics (requests D `accretion-diagnostics`, `analytic-metric-excision`)

Implemented (new file `athenak/src/particles/nrpic_accretion.cpp`; hooks listed in
`tracks/core/interfaces/REQUESTS_ADF.md`): record of removed particles
(`removal_record`), counts of particles, rest mass and energy m E through coordinate
spheres about a fixed centre or a puncture tracker (`acc_nsphere`, `acc_radius<n>`,
`acc_tracker`), pericentre counter in a new integer slot (`peri_count`), the lapse
threshold and the removal of flagged particles for the analytic metrics. E is
alpha W - beta^i u_i at the particle. New options are read only if present, so the
parameter dump inside the restart files of existing inputs does not change.

Set-up: `problems/tests/accretion_static.athinput` and
`tracks/core/analysis/dfix/t3_accretion.py`: Schwarzschild in Kerr-Schild coordinates,
static mesh metric (dx = 0.25 M) and the analytic metric; three dust shells of 64
particles at rest at r0 = 6, 8, 11 M and two families of four bound orbits, (p, e) =
(10, 0.3) and (9, 0.2), started at the apocentre; lapse threshold 0.62 (r = 1.2489 M);
spheres at 4 and 10 M; 800 M, step 0.05 M. References, computed by the script before
the run, independent of the code (closed forms and quadrature in Schwarzschild
coordinates, mapped to Kerr-Schild time): E = (1 - 2/r0)^(1/2) = 0.816497, 0.866025,
0.904534; times to reach the threshold 19.2874, 28.9256, 45.4598 M; pericentre times
172.60, 520.87 M and 152.12, 458.43, 764.74 M; crossings of r = 10 M inwards at 16.82 M
(shell 3), 111.5, 459.8 M and 63.5, 369.8, 676.1 M, outwards at 235.1, 583.3 M and 242.2,
548.5 M.

Predictions (written before the run):
- sphere 4 M at the end: 192 inwards, none outwards, sum of m E 0.165572 (mesh within
  1e-3 relative: the metric is interpolated; analytic within 1e-5);
- sphere 10 M at the end: 84 inwards (64 + 4 x 2 + 4 x 3), 16 outwards, sums of m E
  0.077018 and 0.015311 (same tolerances);
- at every record, for both spheres: (rest mass inside now) - (inside at t = 0) =
  m_in - m_out - m_excised to rounding (1e-15), and the same for the numbers exactly;
- removal record: 192 records, all reason 2 (lapse), none of species 3, 4; each at a
  time in [t_exc, t_exc + 0.05 M] within 0.01 M (analytic) or 0.1 M (mesh), at
  r <= 1.2489 M, lapse below 0.62, pericentre count 0; E at removal equal to the exact
  value within 1e-4 (analytic) and within 5 per cent (mesh: five cells from the
  singularity);
- pericentre counters in the snapshot at 800 M: 2 for each particle of the first
  family, 3 for the second, 0 for every remaining infall particle (there are none left);
  the history counts of "one or more" and "two or more" passages step at the exact
  pericentre times;
- stopped at cycle 8000 and continued: `acc.acc.hst`, `acc.removed.bin`,
  `acc.nrpic.hst` and the last snapshot identical to the uninterrupted run, byte for
  byte.
Refuted if a count differs, if the identity fails, or if the continued run differs.

Outcome of T3 (run core-20261115-160245-727e96a, 82 s on three cores; numbers in
`t3_accretion.json` of the run directory; figure
`tracks/core/analysis/dfix/figs/t3_accretion.png`, looked at) [VERIFIED]:
- sphere 4 M: 192 in, 0 out; sum of m E 0.1655715755 (mesh) and 0.1655715753
  (analytic) against 0.1655715852: -5.8e-8 and -5.9e-8 relative;
- sphere 10 M: 84 in, 16 out; m E in 0.0770181179 (mesh), +3.3e-9; m E out
  0.0153111051, +6.7e-8; analytic +1.9e-9 and +2.2e-8;
- identity content = in - out - removed: largest deviation 8.3e-17 in rest mass, 0 in
  number, at every one of the 801 records, both spheres, all cases;
- removal record: 192 records, all reason 2, none of the bound orbits; times 19.30,
  28.95, 45.50 M, inside [t_exc, t_exc + dt] = [19.287, 19.337], [28.926, 28.976],
  [45.460, 45.510]; radii 1.219 to 1.241 M, lapse 0.6155 to 0.6188; E at removal within
  1.2e-5 (mesh) and 3.5e-6 (analytic) of the exact value; counters 0;
- counters of the bound orbits at 800 M: (2, 2, 2, 2) and (3, 3, 3, 3); the history
  counts step at the exact pericentre times (figure, right panel);
- the continued run equals the uninterrupted one byte for byte in `acc.acc.hst`,
  `acc.removed.bin`, `acc.nrpic.hst` and the last snapshot.
Not refuted. One prediction was too pessimistic: I allowed 5 per cent for E at removal
on the mesh and measured 1.2e-5 (the particle is removed at r = 1.22 to 1.24 M, where
the cubic reconstruction of the Kerr-Schild fields at dx = 0.25 M is still good).
The statement "E is exact at the sphere" holds here because the metric is stationary;
in an evolved spacetime E is the instantaneous alpha W - beta^i u_i and Track D's
definition (a) needs the sphere in the region where the gauge has settled [JUDGEMENT].

### T4 Point mass and background term in the Newtonian mode (requests D
`newtonian-mode-point-mass`, A `newton-mode-and-ball-ic` item 1, external acceleration)

Implemented: `athenak/src/particles/nrpic_external.hpp` (the external acceleration and
potential at a particle), read in `NrpicNewtonInit`, added in the two half kicks
(`NrpicNewtonKick`, `NrpicNewtonPush`) and in the potential-energy sum of the history
(counted in full, the mesh potential once per pair). Options `newton_pm_mass`,
`newton_pm_x1..3`, `newton_pm_soft`, `newton_pm_soft_frame` (comoving or physical),
`newton_bg_t0`. The point mass is not deposited and does not move. The accretion
diagnostics of T3 bracket the Newtonian push as well (energy 1 + p^2/2a^2 + Phi/a).

Set-up: `problems/tests/newton_point_mass.athinput` (isolated, 32^3 cells over
[-2, 2]^3, step 0.002), `..._periodic.athinput` (periodic, a = (1 + 0.05 t)^2), script
`tracks/core/analysis/dfix/t4_newton.py`; particles of rest mass 1e-10, G = M = 1.

Predictions (written before the run):
- kepler (s = 0; orbits (a, e) = (1, 0.5) and (0.8, 0.3) from the apocentre, 20 time
  units): distance to the exact Kepler orbit below 1e-3 at all times (leapfrog phase
  error); pericentre counters 3 and 4; sphere r = 1: 8 inwards, 7 outwards, sums of m E
  3.375e-10 and 3.000e-10 within 2e-3 relative (the momentum is half a kick behind);
  energy column C of the history constant to 1e-5 relative;
- plummer (s = 0.3; circular orbits at r = 1 and 0.5 with v = r (r^2 + s^2)^(-3/4)):
  radius constant to 1e-5, distance to the exact position below 1e-4 over 20 units;
- background (t0 = 1): r/r0 = (1 + t)^(2/3) for particles started with v = 2 r0/3 and
  (1 + t)^(1/3) for v = r0/3, to 1e-6 relative over three time units;
- expand (periodic, comoving softening 0.1): distance to an independent ODE solution
  (DOP853, 1e-12) below 1e-3 over 20 units of conformal time (a from 1 to 4); C of the
  history constant to 1e-5 of a|W|, while a (K + W) itself changes by more than 1e-2 of
  a|W| (so that the constancy of C tests the potential-energy sum and int K da);
- expand_phys (softening 0.1/a): distance to its own ODE solution below 1e-3.
Refuted if an orbit leaves its exact curve beyond the bound (wrong force law, wrong G,
wrong softening rule, wrong time level of the background term) or if a count differs.

Run core-20261115-160746-19e3afe stopped at once: the two new inputs had no `<problem>`
block (`pgen_name = nrpic_newton`); nothing was computed. Added, rerun.

### T5 Common horizon of a pair among several punctures (request F
`pairwise-common-horizon`)

Read [VERIFIED, `athenak/src/z4c/fastflow.cpp` at 3da9086]: `PuncAreClose()` (lines
1606-1612) compares `PuncMaxDistance()`, the largest distance between all `npunct`
punctures, with `merger_distance` times `PuncSumMasses()`, the sum of all masses; a
surface with `wait_until_punc_are_close_<n>` is therefore not searched while any puncture
is far away, as Track F wrote.

Implemented (hooks in `z4c/fastflow.{hpp,cpp}`): `<fastflow> punc_pair_a_<n>`,
`punc_pair_b_<n>` make surface n the common horizon of these two punctures: the trigger
compares their distance with `merger_distance` times the sum of their two masses, and
`use_puncture_massweighted_center_<n>` centres the surface on their centre of mass;
`merger_distance_<n>` replaces the common threshold for one surface. Without the new
parameters nothing changes (they are read only if present).

Set-up: `problems/tests/pair_horizon.athinput`, Brill-Lindquist data of three punctures
of bare mass 0.5 at x = -0.2, +0.2 and 12 (finest cell 1/16 around the pair), two cycles,
three waiting surfaces: 0 the pair (0, 1), 1 all punctures, 2 the pair (0, 2);
`merger_distance = 1`.

Predictions (written before the run):
- corrected executable: surface 0 is searched from the first call and found; its mass is
  between 1.005 and 1.030 (bare masses 1.0 raised by the third hole to 1.0208, minus
  less than one per cent outside the common horizon, plus the finder's error at this
  resolution, +0.36 per cent for a single hole at dx = M/8 in `docs/TESTLOG.md` line
  ~200); its centre is the origin; its mean coordinate radius is near 0.5 (isotropic
  radius M/2). Surfaces 1 and 2 write no record (their punctures are 12.2 apart).
- release core-v0.3 with the same input (it ignores `punc_pair_*`): surface 0 follows
  the rule "all punctures" and writes no record either.
Refuted if surface 0 is not found or its mass is outside the band, or if surface 1 or 2
is searched.

### T6 Existing set-ups, byte for byte (written before the run)

Script `tracks/core/analysis/dfix/t6_regress.py`: release executable core-v0.3 against
the changed source on processors: the seven cases of
`tracks/core/tools/regress_relativistic.py` (geo, boris, dep, east, os, jeans, binary),
three cases of the Newtonian mode (cold ball, point mass with tracers, plane wave in the
expanding box) and `problems/tests/mesh_static.athinput`.
Prediction: every output file of every case is identical, restart files included (new
options are read only if present, so the parameter dump does not change; the
pericentre slot is not written unless a diagnostic is on). Two exceptions I expect and
would accept only after reading the difference: none. A set-up whose tracers have
m = 0 on the mesh metric would differ by design (T1); none of these cases has one
[TO VERIFY by the run: `mesh_static` has a particle of mass 1e-3, `newton_point` has
tracers with m = 0 in the Newtonian mode, which never used the null rule].
Refuted by any differing file.

Outcome of T5 (run core-20261115-161025-3f75eb8, processors, 212 s; figure
`tracks/core/analysis/dfix/figs/t5_pair.png`, looked at) [VERIFIED]:
- corrected: surface 0 (pair 0, 1) has a record at each of the two calls: mass 1.019897
  at t = 0 and 1.019870 at t = 0.0156 M, rms expansion 3.3e-5 and 7.4e-5, mean
  coordinate radius 0.490 and 0.482; inside the band [1.005, 1.030] and 0.09 per cent
  below (0.5 + 0.5)(1 + 0.5/24) = 1.02083. Surfaces 1 (all punctures) and 2 (pair 0, 2)
  have no record;
- release core-v0.3, same input: no record on any surface.
Not refuted. The pair rule finds the common horizon that the released rule does not
search for while a third hole is far away. Not tested here: a merger during an
evolution (the surface appearing when two moving holes approach); the trigger is the
same function, the first guess is `initial_radius_<n>`, which the user must set near
the expected radius [JUDGEMENT].

### Card runs (written before they ran; the queue held the first card job of this
package, the reproduction R3/R4, from 15:40 UTC on)

Case list `tracks/core/analysis/dfix/cases/card_checks.list`, card executable of this
branch. Predictions:
- t1_circ: r in [8.0000, 8.0012] M, as on processors;
- t3_acc: 192 / 84 / 16 crossings, 192 removal records, counters (2,2,2,2), (3,3,3,3);
  sums of m E equal to the processor run within 1e-12 relative;
- t4_kepler: counters (3, 4), 8 crossings inwards and 7 outwards;
- t5_pair: surface 0 found with mass 1.0199 within 1e-4, surfaces 1 and 2 without
  record;
- mem2700 (`by_triple.athinput`, `max_nmb_per_rank = 2700`, three finders): peak card
  memory 71 GB within 2 GB (26.3 MB per slot, `multi_puncture.md` section 5);
- bench16, bench32 (the same problem, 96 cycles, MeshBlocks of 16^3 and of 32^3 with
  560 slots): the 32^3 run needs fewer than 560 MeshBlocks, its zone-cycles per second
  are 1.5 to 2.5 times those of the 16^3 run and its memory per cell is lower; if it
  needs more slots the run stops with the mesh error and the benchmark must be repeated
  with a smaller wave zone;
- t1_accept (`horizon_calib.athinput`, 250 M, corrected executable): the four circular
  tracers stay on their orbits: areal radius within 3 per cent of its start for 250 M
  (the earlier run `single_v3` on a similar mesh: 2.5, 1.1, 0.9, 1.1 per cent,
  `docs/TESTLOG.md` "Test particles around an evolved puncture"), L_z to 1e-3; the
  plunging tracer and the one released at rest are removed at the lapse threshold
  (in `single_v3` at 126 M and 54 M). Track D's bound of 1 per cent may fail for the
  innermost orbit, as it did in `single_v3`.

Outcome of T4 (run core-20261115-160805-5d1663f, about 14 minutes on five cores under
load; numbers in `t4_newton.json` of the run directory) [VERIFIED]:
- kepler: distance to the exact orbit at most 6.8e-5 and 6.6e-5; counters (3, 4);
  sphere 8 in, 7 out; sums of m E 3.3728e-10 and 3.0021e-10 against 3.375e-10 and
  3.000e-10 (-6.6e-4, +7.0e-4); energy drift 7.1e-6. As predicted.
- plummer: radius constant to 1.4e-6 and 2.8e-6; distance to the exact position at most
  1.4e-5 and 5.2e-5. As predicted.
- background: largest relative error of r 1.3e-7 (growing mode) and 2.5e-7 (decaying
  mode). As predicted.
- expand (comoving softening): distance to the ODE solution at most 1.9e-4 and 1.8e-4
  (predicted below 1e-3: holds); C constant to 4.1e-5 of a|W| while a (K + W) changes by
  0.30 of it. The bound 1e-5 on C FAILED by a factor four.
- expand_phys (softening 0.1/a): distance to its ODE solution 2.6e-3 and 5.9e-3. The
  bound 1e-3 FAILED.
What I think happened, not yet tested [JUDGEMENT]: both bounds were guesses of the
leapfrog error for orbits that turned out to pass within the softening length of the
seed (r_min = 0.098 and 0.078 against s = 0.1; with the shrinking softening 0.058 and
0.041 against s = 0.025 at the end), where the step 0.002 resolves the pericentre
poorly (omega dt up to about 0.2). The alternative is an error of the force law or of
the softening rule in the code. They differ in a run with half the step: an
integration error of a second-order scheme falls by four in the distance and in the
drift of C, a wrong rule does not converge to the ODE solution.
Prediction for the follow-up (case list `t4_conv_cpu.list`, step 0.001, same particle
files): ratios of the largest distance (step 0.002 over 0.001) between 3 and 5 for
both orbits of both cases, and of the drift of C in the comoving case between 3 and 5.
Refuted (and the softening rule suspect) if a ratio is near one.

Outcome of T6 (run core-20261115-161129-f905e98 and its fourteen sub-runs
core-20261115-161130-f905e98 to -162357-bcde1a1; report `t6_regress.json` and
`relativistic.json` in the run directory) [VERIFIED]:
- geo (2 files), boris (2), dep (1), east (12), os (16, restart files included),
  binary (1), mesh_static: identical;
- jeans: `bin/JeansWave.hydro_w.00001.bin` differs; newton_ball, newton_point,
  newton_wave: the last restart file differs (16, 10, 10 other files identical).
The prediction "no exception" FAILED. I read the four differences byte by byte: in each
file exactly one text line of the parameter dump differs, the `last_time` of the output
block that wrote the file (0.1 against 0; 0.15 against 0.1; 1e+30 against 0, twice), and
everything behind the dump is identical. All four files are the extra output of a run
that stops at the cycle limit between two scheduled times: the released writer stored
the advanced `last_time` in the file, the corrected `Driver::Finalize` stores the
unadvanced one. That is the correction of T2, seen in the header of the file itself; I
had not thought of the dump inside binary dumps. No field, particle or history value
differs in any case. A byte regression of the integration must therefore mask the
`last_time` lines of final off-schedule files (as it masks the 36 unset header bytes).

Outcome of the T1 reproduction (processor run core-20261115-152835-920d573, still
running at this entry: 28 of 32 cycles, about two minutes per cycle on one loaded core;
card run core-20261115-154030-5ba192a, 245 s of card time, Slurm job 4438; figure
`tracks/core/analysis/dfix/figs/t1_repro.png`, looked at) [VERIFIED]:
- R1 (release, m = 0, processors): `n_excised = 1` in the first history record
  (t = 0.3125 M: Track D's "excised at t = 0.31 M"), tag 5 absent from the first
  trajectory record on; speeds 0.72603, 0.78467, 0.82271 (predicted 0.7260, 0.7847,
  0.8227);
- R2 (release, m = 1e-300, processors): nothing removed; speeds 0.32334, 0.29592,
  0.27385 (predicted 0.3233, 0.2959, 0.2739); radii 6.000, 8.000, 10.000 at t = 0.875 M;
- R3, R4 (card): the same speeds to the five digits printed, the same removal; with
  m = 0 the tracers are at r = 15.7, 17.3, 18.9 M at t = 20 M (Track D: "leave outward
  near light speed"); with m = 1e-300 at 6.44, 8.34, 10.27 M (the slow outward drift of
  the coordinates of a moving-puncture slice, known from `single_v3`).
H1 is not refuted in any of the three ways it could have been: the positive mass
restores the motion with the unchanged executable, processors and card agree, and the
speeds are the null and the timelike ones. Cause: the null rule for m = 0 on the mesh
metric. The card build has no defect of its own.

### T7 Flux sphere on a moving puncture (written before the run)

T3 has a fixed centre. With `acc_tracker` the centre moves during the step: the distance
before the push is taken to the tracker position at t^n (saved in `NrpicSaveMetric`),
after the push to the position at t^n+1. Set-up
`problems/tests/accretion_tracker.athinput` (Bowen-York puncture with momentum 0.3,
adaptive mesh on the tracker, 24 cycles, processors) and
`tracks/core/analysis/dfix/t7_tracker.py`: 4000 particles of rest mass 1e-12 in the shell
1.9 < r < 2.1 around the puncture, half moving in, half out; sphere of radius 2 on
tracker 0.
Predictions:
- the centre in `atr.acc.hst` equals the tracker file `atr.co_0.txt` at every record
  (to the digits of that file), and it moves (displacement above 1e-4 M in 0.75 M);
- at every record: inside(t) - inside(0) = n_in - n_out - n_excised exactly, and the
  rest masses to rounding (1e-24 for masses of 1e-12);
- the number inside counted by the script from each snapshot with the tracker position
  of that time equals the history column (unless a particle is within 1e-12 of the
  sphere);
- several hundred crossings in each direction (about half of the particles start
  within reach of the sphere).
Refuted if the identity fails by even one particle (a centre taken at the wrong time
level miscounts particles near the sphere) or if the snapshot count differs.

## 2026-11-15 session dfix-2 (continuation; same branch, after `git merge main` at b7034c9)

Read again: `CLAUDE.md`, charter to "Owners", this journal, `REQUESTS_ADF.md`, the
manifests of the runs left open by dfix-1. The merge of main changed nothing under
`athenak/`, `problems/`, `python/` (`git diff --stat 0f014b4 HEAD` over those paths is
empty); the executables `.work/build_{cpu,gpu}/src/athena` were linked at 08:09:59 and
08:13:00 local time, after the last source edit (08:08:34, `z4c/fastflow.*`), and
`make -n` in both build directories compiles nothing: they are the source of 3f75eb8,
which equals the source at HEAD.

### Outcome of T7 (run core-20261115-163129-a200caf, processors, 1066 s; numbers in
`t7_tracker.json` of the run directory; figure `figs/t7_tracker.png`, looked at)
[VERIFIED]
- identity at every one of the 25 records: number inside now minus inside at t = 0
  equals n_in - n_out - n_excised exactly (largest deviation 0), rest mass to 9.3e-24
  (masses 1e-12: rounding);
- content counted by the script from the four snapshots with the centre of the same
  record equals the history column (1990, 1997, 2074, 2048); the closest particle was
  5.7e-6 from the sphere, so no count was decided by rounding;
- 1021 crossings inwards, 963 outwards, none removed; the centre moved by 2.4e-3 M in
  0.75 M (right panel of the figure);
- check (a) FAILED as written: the largest deviation of the centre from the nearest row
  of `atr.co_0.txt` is 0.03125, which is exactly one step dt (the script took the larger
  of the position and the time deviation). Read in the data: the history row of
  t = 0.03125 holds x = 0.09999997756473271, the tracker file row "iter 0, time 0"
  holds 0.09999997756473270882; the history row of t = 0 holds the input position
  (0.1, -0.2, 0.05) exactly, which no row of the tracker file holds. Read in the source:
  `Z4c::TrackCompactObjects` (`z4c/z4c_tasks.cpp` lines 320-326) calls `EvolveTracker`
  and then `WriteTracker` at the last stage of a step, and `WriteTracker`
  (`z4c/compact_object_tracker.cpp` lines 251-253) prints `pmesh->ncycle` and
  `pmesh->time` before the driver advances them. So the tracker file labels the
  position of t^{n+1} with n and t^n: an upstream labelling, one row early.
  Hypothesis: the centre of the diagnostics is the right one (position at the time of
  its record), and only the comparison was misaligned.
  Prediction for the corrected check (written before the re-judgement): the centre of
  history record k >= 1 equals tracker row k-1 in all three coordinates to the 16 to
  19 printed digits (|difference| < 1e-15), record 0 equals the input position exactly,
  and the time of record k equals the time of tracker row k-1 plus 0.03125. Refuted if
  any coordinate differs by more than 1e-15 (the centre would then be taken at another
  time level than its record, which the identity of the counts cannot see when the
  centre moves 1e-4 M per step against particles 5.7e-6 M from the sphere).

### Card checks: what ran, and the predictions for judging it (written before the
judgement)

Run core-20261115-161528-ff00411 (Slurm job 4456) started at 17:12 UTC and was stopped by
its 50-minute limit [VERIFIED, `sacct`]: t1_circ and t3_acc completed in 1.2 s and 8.5 s
of card time; t4_kepler took about 0.33 s per step (one multigrid solve per step on a
32^3 mesh of 4^3 MeshBlocks: launch-bound on a card) and reached t = 18.02 of 20; the
remaining cases (t5_pair, mem2700, bench16, bench32, t1_accept) never started. My
mistake of planning: the Kepler case was put on the card without timing its step there.
Card time of this package: 0.0681 (T1 reproduction) + 0.8383 = 0.906 card-hours of the
one allowed; no further card job in this package.

Predictions for the judgement (those of "Card runs" above, adapted to what ran, plus a
comparison with the processor runs that I did not write down before):
- t1_circ: r in [8.0000, 8.0012] M for 300 M, relative errors of E and L_z below 1e-6 and
  6e-6; the trajectory differs from the processor trajectory (run
  core-20261115-163155-0f014b4, case b_new) by less than 1e-8 M in position at every
  record (rounding of a different instruction order, grown over 3000 steps);
- t3_acc: 192 / 84 / 16 crossings, identity to 1e-15, 192 removal records, counters
  (2, 2, 2, 2) and (3, 3, 3, 3); sums of m E equal to the processor run (case mesh of
  core-20261115-163327-0f014b4) within 1e-12 relative; removal times equal;
- t4_kepler, window t <= 18.02: pericentre passages and crossings of r = 1 in the
  history equal to the exact events before the last record; distance to the exact
  orbit below 1e-4 (processor: 6.8e-5 over 20); trajectory equal to the processor run
  (case kepler of core-20261115-160805-5d1663f) within 1e-9 at every common record.
Refuted by any count that differs, by an identity off by more than rounding, or by a
card-processor difference beyond the bound (a defect of the card build in the new code).

Outcome of the T7 re-judgement (run core-20261115-180101-6d165b4) [VERIFIED]: centre of
record k >= 1 minus tracker row k-1: at most 5.6e-17 in any coordinate (the printing
of the history); record 0 equals the input position; record time minus row time minus
dt: 0 at every record. As predicted: the diagnostics take the tracker position of the
time of their record; the naive check of dfix-1 compared rows one step apart. A reader
of `<basename>.co_<n>.txt` must know that its row "n, t^n" holds the position at
t^{n+1} (upstream; written into `docs/FORMATS.md` with this package, see below).

Outcome of the T4 follow-up (judgement run core-20261115-180144-83abe17 of the runs
core-20261115-160805-5d1663f and core-20261115-162608-113493f; figure
`figs/t4_conv.png`, looked at) [VERIFIED]:
- comoving softening: largest distance to the ODE solution 1.92e-4, 1.84e-4 at
  dt = 0.002 and 4.81e-5, 4.61e-5 at dt = 0.001, ratios 4.00 and 4.00; drift of C over
  a|W| 4.14e-5 and 1.03e-5, ratio 4.00;
- physical softening (s/a): 2.64e-3, 5.92e-3 and 6.59e-4, 1.48e-3, ratios 4.00 and 3.99.
The prediction (ratios between 3 and 5) holds in all three: second-order convergence to
the independent solution, so the force law and both softening rules are right and the
two failed bounds of T4 were bounds of the integration error at that step, too tight
for orbits that pass inside the softening length. Not predicted, seen: with physical
softening C drifts by 5.6e-2 of a|W| at both steps (ratio 1.00). Reading [JUDGEMENT,
not tested by a separate run]: the Layzer-Irvine combination C assumes a potential
homogeneous of degree -1 in the comoving positions; with s/a the potential depends on
time explicitly and dC/dt has the extra term -sum m dPhi_ext/dt|_x, which the history
does not integrate. So C is a conservation check only for comoving softening (said so in
the interface document).

Outcome of the card checks (judgement run core-20261115-180353-7d7116d of the card run
core-20261115-161528-ff00411; figure `figs/dfix_card.png`, looked at) [VERIFIED]:
- t1_circ: r in [7.999998, 8.001151] M for 300 M, relative errors 2.6e-7 (E) and
  5.05e-6 (L_z), as on processors; card minus processor position at most 1.2e-12 M over
  3002 records (bytes differ, as expected of a card);
- t3_acc: 192 / 84 / 16 crossings and 4 particles inside 10 M at the end, as on
  processors; sums of m E equal to the processor run to 0 and 2.2e-16 relative; every
  history column within 9.0e-16 relative of the processor run; identity to 1.4e-17; 192
  removal records, the same tags at the same times, E within 1.7e-15 of the processor
  values; counters (2, 2, 2, 2) and (3, 3, 3, 3);
- t4_kepler to t = 18.02: 7 crossings inwards and 7 outwards, the exact numbers before
  that time; counters (2, 2) in the snapshot at t = 10, exact (2, 2); the history counts
  of passages lie between the exact counts at t - 2 records and at t at every record;
  distance to the exact orbit at most 6.6e-5; card minus processor at most 4.0e-13.
Not refuted in any item. The new code of this package gives on a card what it gives on
processors, to rounding. Not run on a card: T5 (pair horizon; host code, but the finder
interpolates on the card), the memory measurement at 2700 slots, the block-size
benchmark, and the 250 M acceptance run of `horizon_calib.athinput` (Track D's own
acceptance test, decision 0010; it needs about 25 minutes of a card).

### Repeats of T1, T2, T3 with the published executables (written before the comparison)

T1 (run core-20261115-154303-da69f6a), T2 (core-20261115-154901-d8ad7ec) and T3
(core-20261115-160245-727e96a) ran with earlier builds of this branch (sha256 of the
processor executable cd48eebf, 48f26e05, 45f399b2); dfix-1 repeated them with the
published one (17ee5e28; runs core-20261115-163155-0f014b4, -163203-0f014b4,
-163327-0f014b4) without recording the comparison. Between those builds only later
items were added (accretion, external gravity, pair horizon), each inactive in the
earlier inputs. Prediction: every output file of T1 and T3 present in both runs is
identical byte for byte; for T2 the files of the deterministic cases (u, c) are
identical and the wall-clock cases (w) differ, because their stop time is the wall
clock's (stopped at 68.4 and 26.7 M in the first run, at 11.0 and 26.9 M in the repeat).
Refuted if any file of T1, T3 or of the T2 cases u, c differs.

Outcome of the repeat comparison, first pass (run core-20261115-180556-eb25f13)
[VERIFIED]: T1 12 of 12 files identical. T3: 58 of 59 identical; `mesh_rs/rst/acc.00003.rst`
differs. T2: besides the wall-clock cases (w, expected), the restart files written after
the continuation in the cycle-limit cases (old_c 00004-00006, new_c 00004-00007) differ.
The prediction "every file of T1, T3 and the T2 cases u, c identical" FAILED as written.
Read in three of the files: the only differing line is `restart_file = <path>` in the
parameter dump, and the path contains the run directory; everything after `<par_end>` is
identical. I had not thought of the path in the dump. Prediction for the second pass
(script masks the two run-directory names): every differing file of T1, T3 and the T2
cases u, c is equal after masking; the w cases still differ.

Outcome, second pass (run core-20261115-180814-4652cf3) [VERIFIED]: T1 12 of 12 files
identical; T3 59 of 59 identical once the run directory is masked; T2: all 13 files that
differ outside the wall-clock cases are equal once masked, and the 13 that still differ
all belong to the wall-clock cases (their stop times differ). As predicted: the
published executables reproduce the first runs of T1 to T3 byte for byte.

### End of session dfix-2

Published: `scratch/core/exe/core_requests-adf/{athena_cpu,athena_gpu,COMMIT,READY}`
(source 3f75eb8; sha256 17ee5e28... and f423de38..., the executables of every test run
since core-20261115-161025-3f75eb8 and of the card checks). `READY` is a copy of
`tracks/core/analysis/dfix/READY.txt`. Answers to the tracks:
`tracks/core/outbox/20261115T1815Z__to-{D-bh-dress,A-emd-pbh,F-hills}__dfix-answers.md`.
State of every test: `interfaces/REQUESTS_ADF.md` section 4; lines of shared files:
section 5. Runs of this session were registered with `harness/bin/nrpic-run` (the
failure of dfix-1, KeyError 'outputs', is gone after the merge of main); the card-check
manifest of dfix-1 was completed by hand (its registering process had ended).
Open: the card cases that did not run (T5, T7, mem2700, bench16, bench32, t1_accept);
a merger during an evolution for the pair horizon; the deferred requests of section 1.
Lessons: time a case on the target device before putting it into a card job (the
Kepler case cost 0.8 card-hours that a processor does in minutes); a byte regression
must mask the run directory in the parameter dump of continued runs and the stored
last_time of final off-schedule outputs.

## 2026-11-19 session dfix-3 (wave 2b; after `git merge main` at 71acd0c)

Read: `CLAUDE.md`, charter to "Owners", brief 688-706 and 834-860, decisions 0010 and 0016,
this journal, `REQUESTS_ADF.md`, the section core:dfix of
`scratch/orch/wave2_reports/core.md`, `READY.txt`, the case list of the card checks, the
manifests of this package. State found [VERIFIED]: worktree clean at ae201e9; no run
manifest of this package untracked (every run directory under `scratch/core/` whose
commit is on this branch has its manifest under `tracks/core/runs/`); the merge of main
changed nothing under `athenak/` (`git diff 3f75eb8 HEAD -- athenak/` is empty), so the
published executables `scratch/core/exe/core_requests-adf/athena_{cpu,gpu}` (sha256
17ee5e28..., f423de38..., checked today) are still the source of this branch. Card job
4456 ended at its limit (`sacct`: TIMEOUT, 00:50:18). Card budget of this session: 0.75
card-hours.

### Card cases still missing: plan and predictions (written before any card job)

Cases: T5 (pair horizon), T7 (sphere on a moving tracker), mem2700 (peak card memory at
2700 MeshBlock slots with three finders). Executable: the published card executable
(f423de38). The lesson of job 4456 is applied: first a timing job, then the cases sized by
it.

Timing job (list `cases/card_timing.list`, Slurm limit 14 minutes, every case capped by
`athena -t`): T5 complete (it has only two cycles; cap 6 minutes), T7 to cycle 9 (two
finder calls, cycles 0 and 8; cap 3 minutes), the three-hole mesh at 2700 slots to cycle 4
(cap 3 minutes). Expected, from the processor runs and the card run of the three holes
(not a test): T5 two to four minutes (190 s of processor time, mostly the finder's host
loop, `scratch/core/core-20261115-161025-3f75eb8/new/athena.log`); T7 below one minute;
the three-hole mesh 0.56 s per cycle (574 s for 1024 cycles, run
core-20261115-120834-d08c476) plus its set-up. Sizing rule for the second job: case time
bounded by (T_timing x full cycles / timing cycles), Slurm limit 1.5 times the sum plus
two minutes, total of both jobs below 0.75 card-hours.

Predictions for the judgement (references: processor runs with the published processor
executable 17ee5e28):
- T5 on a card: surface 0 (pair 0, 1) has a record at both calls, mass within 1e-4 of the
  processor values 1.019897 and 1.019870 (the finder stops at `mass_tol = 1e-5`), mean
  coordinate radius within 1e-3 of 0.490 and 0.482; surfaces 1 and 2 write no record.
  Refuted if surface 0 is missing or off by more than 1e-4, or if surface 1 or 2 is
  searched (then the pair rule acts differently on a card).
- T7 on a card (full 24 cycles, same particle file, sha256 51603612...): at every one of
  the 25 records the content identity holds exactly in number and to 1e-23 in rest mass;
  the content counted from each snapshot with the centre of its record equals the
  history; the centre of record k >= 1 equals tracker row k-1 to 1e-15; and against the
  processor run core-20261115-163129-a200caf: the same crossing counts (1021 in, 963 out,
  0 removed) and the same contents (1990, 1997, 2074, 2048 at the snapshots), the centre
  within 1e-10 M and every particle within 1e-8 M at the snapshots (a vacuum Z4c
  evolution on a card differs from processors by rounding, which 24 steps do not grow to
  1e-8; a count differs only if a particle passes within that distance of the sphere at
  a step boundary, about 1e-5 likely for 4000 particles and 24 steps). Refuted if an
  identity fails, a count differs from the snapshot, or card and processors differ in a
  count or beyond these bounds (a defect of the device path of the tracker-centred
  spheres).
- mem2700 (full: 32 cycles, `max_nmb_per_rank = 2700`): runs without the mesh error with
  1100 MeshBlocks at the start; peak card memory 70.9e3 MiB within 2.0e3 MiB (26.27 MiB per
  slot from 63059 MiB at 2400 slots with three finders, run core-20261115-120834-d08c476;
  memory allocated for the slot limit, not for the blocks in use); the same peak already
  in the timing run at cycle 4. The history of the first 0.5 M equals that of the
  2400-slot run within 1e-10 relative (the slot limit should not change the evolution).
  Refuted if the peak is outside [68.9e3, 72.9e3] MiB (the per-slot model of
  `multi_puncture.md` section 5 is then wrong), or if the history differs beyond 1e-10.

Amendment, before the timing job started (it is queued as Slurm job 4631, run
core-20261119-140644-074f8e3): `by3.z4c.user.hst` prints six significant digits, so the
bound 1e-10 on the history of mem2700 can only be checked as equality of the printed
values at t = 0, 0.25, 0.5 (a relative difference above about 5e-7 would show). Judge
script `tracks/core/analysis/dfix/card2_judge.py`; smoke test on the processor runs
against themselves: zero differences, the figure readable.
