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
