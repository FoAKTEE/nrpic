# JOURNAL of the source item gauge-2 (core, batch 4b of wave 3): the relaxed lapse, second pass

Branch `core/gauge-2`, worktree `wt/core-s1`. Task: decision 0022 item 3. With `<z4c>
lapse_leak` the horizon mass of a black hole in vacuum drifts late in a run (Track D, run
V-1GB); find the cause, correct the condition, keep the expanding-matter tests.
First pass: `tracks/core/JOURNAL-gauge.md`, `coord/INTERFACES/cosmo_gauge.md` section 7.
Predictions are written before each test and not changed afterwards; outcomes are
appended, failed ones included. Times are PST of 2026-11-21 unless said otherwise.

## Entry 1 (08:50-09:25): what was read, what Track D's files already show, the reduced set-up, predictions

### Read

Decision 0022 item 3; `cosmo_gauge.md` sections 7 and 8; `JOURNAL-gauge.md` handoff;
`athenak/src/z4c/z4c_gauge_ext.hpp`; Track D's `g2runs/README.md`, `g2runs/JOURNAL.md`
entries 6 to 9, `drift_controls/JOURNAL.md` entry 1, `puncture_drift/README.md`, and the
input `g2runs/inputs/v1gb_bnd384.athinput` (worktree `wt/D-bh-dress`, branch
`track/D-bh-dress`).

### What Track D's output files show (read by me, no run of mine)

Horizon summaries of V-1B (plain 1+log, `scratch/D-bh-dress/D-20261120-222625-63abd72/
v1b.horizon_summary_0.txt`), V-1GB (`lapse_leak = 0.5`, `.../D-20261121-125909-06f856e/
v1gb.horizon_summary_0.txt`) and of the time-symmetric puncture of D-pre-4 at the same
finest cells M/8 (`.../D-bh-dress-20261115-121313-284ec4f/punc.horizon_summary_0.txt`),
columns 3 (mass) and 11 (mean coordinate radius) [VERIFIED, those files]:

| t / M | V-1B mass, radius | V-1GB mass, radius | mass difference | D-pre-4 puncture radius |
|---|---|---|---|---|
| 5 | 0.999814, 0.975 | 0.999814, 0.975 | 0 | 0.897 |
| 10 | 1.000034, 1.270 | 0.999952, 1.271 | -8.1e-5 | 1.179 |
| 15 | 1.000666, 1.517 | 1.000566, 1.400 | -1.0e-4 | |
| 20 | 1.001016, 2.055 | 1.000909, 1.375 | -1.1e-4 | 1.197 |
| 50 | 1.000939, 2.038 | 1.001041, 1.325 | +1.0e-4 | 1.345 |
| 100 | 1.000937, 2.147 | 1.001186, 1.086 | +2.5e-4 | 1.451 |
| 140 | 1.000950, 2.179 | 1.000627, 0.972 | -3.2e-4 | |
| 180 | 1.000922, 2.193 | 1.001431, 0.900 | +5.1e-4 | |
| 199.5 | 1.000928, 2.196 | 1.002450, 0.875 | +1.5e-3 | 1.551 (200 M) |

Three things follow before any run [VERIFIED as numbers; reading JUDGEMENT]:
1. The two runs are the same to rounding until t = 5 M and separate between 10 and 15 M,
   first in the coordinate radius of the horizon: under plain 1+log it jumps from 1.5 to
   2.06 M between 15 and 20 M and stays there; under the relaxed lapse it stays near
   1.4 M and then shrinks at about 3e-3 per M, without sign of stopping (0.875 M = 7.0
   cells of M/8 at 200 M).
2. The relaxed run is not simply "the standard trumpet": a time-symmetric puncture on the
   same cells (plain 1+log, lapse never above 0.9972) has a horizon that grows slowly,
   1.2 M at 20 M to 1.55 M at 200 M, with a flat mass (plateau from 100 to 210 M,
   `puncture_drift/README.md`). In V-1GB the horizon shrinks through and below that size.
3. The lapse exceeds 1 in V-1GB for a reason that the first pass did not weigh: the
   slice of the Einstein-Straus data has K_T = -f(R) sqrt(2M/R^3) in the vacuum bubble
   (header of `v1.tab`): the normal observers of the vacuum bubble diverge, so 1+log
   raises the lapse there (to 1.43 in V-1B, D's `g2runs/JOURNAL.md` entry 7) and the
   relaxation term holds it near exp(-2 T K) (1.04 to 1.015). The term therefore acts on
   the whole vacuum bubble from the first M on, not on a small overshoot.

### Candidate causes and how each could fail

- C1 overshoot of a settling puncture in the wave zone. Already excluded for a puncture
  on a slice with K = 0 [VERIFIED by the first pass: test P identical byte for byte over
  20 M; largest lapse 0.9972 in Track D's 500 M run]: there the term is exactly zero. It
  is not the mechanism of V-1GB either, where the lapse excess is 4 per cent over the
  whole bubble, from the slice.
- C2 the kink of max(ln(alpha/alpha_0), 0). Test: the same run with a smooth onset
  (new option). Fails as a cause if the horizon history does not change.
- C3 the term acts near the hole (inside about 8 M), on the lapse profile of the trumpet.
  Test: the term switched off inside a radius around the hole. Fails as a cause if the
  horizon still shrinks.
- C4 the term acts in the vacuum bubble away from the hole: it removes the lapse front
  that plain 1+log makes on this slice (the front arrives at the hole at 15 to 20 M and
  leaves the coordinates around the hole stretched: radius 2.06 M) and afterwards holds
  the bubble on a slice whose normal observers keep diverging, so the coordinates keep
  stretching (chi falls, D's entry 7) and the horizon moves inward through the mesh.
  The mass then drifts because a horizon of fixed areal radius is covered by ever fewer
  cells. Tests: C3's test from the other side (switching off inside 8 M leaves the
  shrinking; switching off wherever there is no matter gives plain 1+log exactly);
  dependence of the mass error on the number of cells across the horizon (two
  resolutions).
- C5 the finder on a drifting slice. Track D compared with the Misner-Sharp mass of the
  slice (`g2runs/JOURNAL.md` entry 8, run D-20261121-150025-05937b2): the slice mass
  follows the finder's dip and late rise with an offset of 1.5e-4 to 2.1e-4, so the
  growth is in the slice [VERIFIED by D; not repeated here unless time allows].

### Reduced set-up (test V)

`problems/es/v1_small.athinput`: Track D's V-1GB with (kept) the data `v1.tab`, `v1.nrp`
and the puncture, the gauge, the finder and particle settings, the 2:1 nest; (changed)
outer faces at +-64 M instead of +-384 M, MeshBlocks of 16^3 instead of 24^3, no restart
and constraint slices. Two sizes:
- V8: finest cells M/8 on +-4 M (288 MeshBlocks of 16^3, 1.18e6 cells, step M/32). For
  the cards.
- V4: finest cells M/4 on +-4 M with MeshBlocks of 8^3 (root 4 M on +-64 M, 288
  MeshBlocks, 1.47e5 cells, step M/16). For processors. Measured with the threaded
  release executable on six threads: 2.33 processor-seconds per step (48 steps,
  `scratch/core/tmp/g2_time_b8`), so 100 M = 1600 steps take about 31 minutes on two
  threads. (MeshBlocks of 16^3 at M/4: 0.95e6 cells, 10.6 processor-seconds per step,
  `scratch/core/tmp/g2_time_c4`: too slow.) A processor run at M/8 would take hours.
The processors therefore carry the cause tests at M/4, where the horizon has half as many
cells as in Track D's runs; the cards carry M/8.

### Prediction V4-a (reproduction on processors, release core-v0.6 executable), written before the runs

Runs: V4 with `lapse_leak = 0` (control) and `lapse_leak = 0.5`, 100 M each.
- (a) Radius: the two agree to 1 per cent until t = 8 M; at t = 20 M the control has a
  horizon radius above 1.8 M and the relaxed run below 1.5 M; from 30 M to 100 M the
  relaxed radius falls monotonically to below 1.2 M while the control stays above
  1.9 M. Refuted if the relaxed radius stays within 10 per cent of the control at 50 M
  (then the reduced mesh or M/4 does not show the effect and the set-up must change).
- (b) Mass [JUDGEMENT]: at M/4 the control's horizon (8 cells in radius) keeps its mass
  within 3e-3 over 40 to 100 M (largest minus smallest); the relaxed run (5.5 falling to
  4.5 cells) departs from the control by more than 3e-3 somewhere in 40 to 100 M and its
  own spread over 40 to 100 M is at least three times the control's. Refuted (C4's last
  link, "fewer cells, larger error", does not show at M/4) if the relaxed run's spread is
  below twice the control's.
- (c) Faces at 64 M: no feature in the control's mass above 1e-3 that starts between 45
  and 100 M (the faces' signal needs about 64/1.3 = 49 M to reach the hole; in Track D's
  V-1 with faces at 192 M the late drift was 1.4e-4) [JUDGEMENT].

## Entry 2 (09:15): card job A, test V8 with the release executable; prediction written before submission

The cards are busy (two jobs of F running, one of core and one of another user waiting),
so the job that needs no new source goes in first: V8 (finest cells M/8, 288 MeshBlocks
of 16^3, faces at +-64 M) for 200 M with `lapse_leak = 0.5` and with plain 1+log, release
core-v0.6 card executable, list `tracks/core/analysis/gauge2/card_a.list`. The step time
on a card is not measured yet: from core's ES test of the first pass (1.8e6 cells in
blocks of 16^3, 0.19 s per step, run core-20261115-202901-b4430da) I expect 0.125 s per
step, 6400 steps = 13 to 14 minutes per run, 0.45 card-hours for the pair; each run has a
wall limit of 21 minutes, so the job cannot take more than 0.72 card-hours.

Prediction V8-a:
- (a) V8 with the relaxed lapse reproduces V-1GB: horizon radius within 4 per cent of
  1.325, 1.086 and 0.875 M at t = 50, 100 and 199.5 M; mass drift from its value at
  100 M with a dip between -2e-4 and -9e-4 in 120 to 160 M and a rise to more than
  +6e-4 at 199.5 M (V-1GB: -5.6e-4 and +1.27e-3). The near faces do not matter for this
  run [JUDGEMENT from Track D's ES-1GB = ES-1G]. Refuted if the drift over 100 to
  199.5 M stays inside [-1.5e-4, +1.5e-4] (then the reduced set-up does not show the
  defect and the faces or the size of the M/8 region matter).
- (b) V8 with plain 1+log: radius within 4 per cent of V-1B's until 50 M (2.04 M at
  50 M). Mass drift from 100 M inside [-3e-4, +3e-4] to 199.5 M [JUDGEMENT: V-1B had
  5e-5 with faces at 384 M and V-1 -1.4e-4 with faces at 192 M from 165 M on; here the
  faces are at 64 M and their signal can arrive from 50 M on]. If the control leaves
  that band the reduced set-up is not a clean control after the arrival time, and the
  clean control stays Track D's V-1B.
- (c) The relaxed run separates from the control in mass by less than 3e-4 before 100 M
  and by more than 1e-3 at 199.5 M.

## Entry 3 (09:13-09:20): the processor runs of V4 were mis-sized and stopped; the plan after that

Runs core-20261121-170823-ee64248 (control) and core-20261121-170829-197d265 (relaxed),
V4 on two threads each, had reached t = 2 M after 4.5 minutes: 15 processor-seconds per
step, not 2.3. My error: the line "cpu time used" of AthenaK's summary is wall time, so
the 112 s of the 48-step timing run on six threads were 670 processor-seconds (6.3e4
cell-steps per wall second on six threads, about 1e4 per processor-second with blocks of
8^3; 1.5e4 with blocks of 16^3). 100 M of V4 would cost 6 processor-hours per run. Both
runs were stopped (`nrpic-run stop`, status stopped). Prediction V4-a is NOT TESTED; the
radius and mass comparison moves to the card runs of entry 2 (V8, the same prediction in
kind: V8-a).

Consequences for the plan [JUDGEMENT]:
- Every run with a black hole goes to a card: job A (queued, Slurm 4812) for the
  reproduction, one job B for the cause tests and the tests of the corrected condition.
  Job B can only be submitted when core has fewer than two jobs in the queue (4810 of
  another core session is waiting in front of 4812).
- Processors: byte regression, the identity of the corrected condition with plain
  1+log in vacuum on a coarse mesh, the homogeneous universe, the expanding ball at
  cells of 1 M.

## Entry 4 (09:20): the source of the second pass; predictions of the processor tests T1 to T3

### Source (commit 90f52f4d, `athenak/src/z4c/z4c_gauge_ext.hpp` only)

    d_t alpha += - (alpha/T) w_m(rho) w_h(x) F(ln(alpha/alpha_0))

Three factors, each read only if its parameter is present in `<z4c>`; with none of them
(or all three at zero) the kernel runs the statement of the first pass unchanged:
- `lapse_leak_rho = rho_c`: w_m = S(2 rho/rho_c - 1), S(s) = s^2 (3 - 2 s) clamped to
  [0, 1]; rho is the energy density of the matter source that Z4c::CalcRHS reads at
  that stage (the sources, or the densities times 1/sqrt(gamma), or the assembled
  total). Exactly zero at and below rho_c/2, so vacuum, tracers of mass 1e-30 and a run
  without a matter module are plain 1+log bit for bit; one above rho_c.
- `lapse_leak_hole = r_h`: w_h = product over all compact-object trackers of
  S(|x - x_A|/r_h - 1): zero within r_h, one beyond 2 r_h.
- `lapse_leak_onset = delta`: F(x) = x^2/(x + delta) for x > 0 instead of max(x, 0).
Why the density and not K [JUDGEMENT]: on the slice of the Einstein-Straus data K < 0
both in the dust and in the vacuum bubble, so K cannot tell them apart; what differs is
that the vacuum has a stationary slice which plain 1+log finds (Track D's V-1B), and the
dust has none (its lapse grows as 1 + 6 ln a without the term). The hole radius is the
other candidate of decision 0022; it needs a radius of the order of the bubble if cause
C4 is right, and is there for the cause test C3 and as an alternative.

### Predictions, written before the runs

T1 (coarse vacuum mesh, 64^3 cells of 2 M, no refinement, 10 M; the puncture is not
resolved, the test is one of the code path):
- restricted to the matter (`lapse_leak = 0.5`, `lapse_leak_rho = 1e-8`) writes the
  bytes of plain 1+log in every output file (after the parameter dump of the mesh
  slices). Refuted by one differing data byte.
- the first pass differs from plain 1+log: its largest lapse stays below 1.08 while
  plain 1+log exceeds 1.1 before 10 M. If the two were identical the test would not
  exercise the term.
- `lapse_leak_hole = 1000` with a tracker at the puncture: the files of plain 1+log
  with the same tracker; a tracker alone changes no file that both runs write.
- `lapse_leak_onset = 1e-9` equals the kink to 1e-6 in the constraint history.
T2 (homogeneous dust universe, rate 5/H_0, t = 2/H_0, density 0.119 falling to about
6e-3): with `lapse_leak_rho = 1e-3` the histories of the lapse and of the volume equal
those of the first pass to 1e-10 relative (the weight is exactly one; the product by
1.0 may change the last bit). Refuted by a difference above 1e-10.
T3 (L1, marginally bound ball R_b = 10 M, cells 1 M, 10 M; T = 1 M and 0.5 M;
`lapse_leak_rho = 1e-5` against a ball density of 2.4e-4 falling to 8.5e-5):
- (a) first pass, new executable against release core-v0.6: every file identical.
- (b) [JUDGEMENT] with the restriction the exterior vacuum is plain 1+log: its lapse
  rises above the capped interior (I expect 1.3 to 2.0 just outside the surface at
  10 M, against exp(6 T H) = 1.31 and 1.14 inside), and the difference spreads into the
  ball by diffusion over sqrt(2 T t) = 4.5 M (T = 1 M) and 3.2 M (T = 0.5 M), not as a
  front that focuses at the centre. So: core shells within a factor 2 of the first
  pass (3.1e-3 at T = 1 M in the first pass, cells 1 M), every other group within a
  factor 2 as well, central lapse within 5 per cent of the homogeneous value. Refuted,
  and the density weight alone not acceptable for a ball in vacuum, if a group is worse
  by more than a factor 2 or the central lapse departs by more than 5 per cent.

## Entry 5 (09:25): card job B; predictions written before submission

List `tracks/core/analysis/gauge2/card_b.list`, card executable of this branch. Nine
runs in the order of their weight, each with a wall limit; the limits sum to 48.5
minutes, the expected card time is about 31 minutes (0.5 card-hours) [JUDGEMENT, the
step time on a card is still unmeasured: job A has not started]. With job A (0.45
expected, 0.72 at most) the item stays below its 1.5 card-hours also if every run of job
B uses its limit (0.72 + 0.81 = 1.53 is the bound; I stop job B if job A used its limit).

Chosen density scales rho_c (`lapse_leak_rho`): Einstein-Straus dust 2e-7 (plateau
3.7e-6 at the start, `es.json`; 1.1e-6 at 100 M); ball of L1 1e-5 (2.4e-4 falling to
8.5e-5); bound ball of L2 and L3 1e-4 (1.9e-3, 9.8e-4 at turnaround).

Predictions.
- ES-c, `es-rho`: Track D's Einstein-Straus data (core's copy of the first pass: dust
  lattice 2 M, 87128 particles), 100 M, T = 2 M, relaxation only in the dust.
  (a) The horizon's coordinate radius exceeds 1.8 M by t = 25 M and stays between 1.8
  and 2.4 M until 100 M (the vacuum bubble is sliced as Track D's V-1B: 2.02 M at 25 M,
  2.15 M at 100 M). Refuted if it is below 1.6 M at 50 M.
  (b) The horizon mass varies by less than 1e-4 (largest minus smallest) over 40 to
  100 M (V-1B: 1.4e-5; the first pass V-1GB: 2.2e-4). Refuted above 2e-4.
  (c) Wall tracers (R_0 = 36 M): areal radius at their proper time within 5e-4 of the
  exact curve until tau = 100 M (first pass: 6.2e-5 until 30 M; Track D's ES-1G 1.7e-4
  until 206 M; plain 1+log 2.2e-3). Refuted above 2.2e-3: then the corrected condition
  follows the wall worse than no relaxation at all.
  (d) Lapse at the dust tracers (R_0 = 48 M) within 3 per cent of the homogeneous
  model; largest lapse on the mesh below 1.5, inside the bubble.
  (e) No dust inside the wall tracers; the 14 tracers from 6 M removed near 15.5 M.
- ES-f, `es-leak` (same mesh, relaxation everywhere as in the first pass): radius below
  1.45 M at 25 M and below 1.15 M at 100 M; mass varying by more than 2e-4 over 40 to
  100 M; wall within 3e-4. This is the defect on the same mesh.
- L3-c, `collapse-rho`: the bound ball through its collapse, T = 0.5 M, cells M/8,
  relaxation only in the matter. Horizon first found between 26 and 30 M (first pass
  29 M, plain 1+log 18 M), then in every search; mass between 0.997 and 1.001 (first
  pass 0.9980 to 1.0003); mean coordinate radius at 44 M between 0.7 and 1.1 M (first
  pass 0.73 M); interior shell groups (outer at 2.5 m, mid at 4 m) median error below
  2 per cent (first pass 1.0 and 0.73). Refuted by a missing horizon, a mass outside
  0.995 to 1.003, or a group above 5 per cent.
- L1-c, `ball-l1-rho` (cells M/2, T = 1 M): core shells below 2.4e-3 (first pass
  1.16e-3), central lapse within 5 per cent of the homogeneous value.
- L2-c, `ball-l2-rho` (cells M/4, T = 0.5 M): core, mid, outer, surface below 1.9e-2,
  5e-3, 8.6e-3, 1.3e-2 (twice the first pass); largest R/R_0 of the turnaround between
  1.245 and 1.252.
- V8-c, `v8-rho` (12 M): horizon summary and histories equal to the control of job A at
  the same times, byte for byte unless the card's deposit of the 1e-30 tracers changes
  a last bit; in that case equal to 1e-12 relative.
- Cause tests on V8, 30 M, compared with job A at 20 and 30 M (Track D: control 2.06
  and 1.91 M, first pass 1.38 and 1.42 M):
  C2 `v8-onset` (delta = 0.02, about half the lapse excess in the bubble): radius below
  1.5 M at 20 and 30 M. The kink is the cause only if the radius is above 1.8 M.
  C3 `v8-hole6` (term off within 6 M of the puncture, in full beyond 12 M): radius
  below 1.6 M at 20 and 30 M. The action near the hole is the cause only if the radius
  is above 1.8 M.
  C4 `v8-hole20` (off within 20 M, in full beyond 40 M): radius above 1.6 M at 20 or
  30 M, because the lapse front of plain 1+log forms between 8 and 30 M [JUDGEMENT:
  K_T = -f sqrt(2M/R^3) of the table is largest near R = 20 to 26 M]. If this run also
  stays below 1.5 M, the front is not what sets the size and C4 is wrong in that part.

## Entry 6 (09:50-10:00): outcomes of T1 to T3; the matter weight hurts the surface of a ball; job B revised before it ran

Run core-20261121-172451-79e29b3 (processors, serial executables: this branch
`.work/build_cpu_g2`, source 90f52f4d, against release `.work/build_cpu_v06`; 15 runs,
24 minutes on six cores; numbers `tracks/core/analysis/gauge2/results/ptests.json`,
figure `figs/ptests_ball.png`, looked at: six panels, four curves each, the dashed
"matter only" curves leave the solid ones in the outer and surface panels from tau = 3 M
on). An earlier start, core-20261121-172332-7167b70, failed at once on a relative
executable path of the driver and is on record as failed.

Outcome T1 (coarse vacuum mesh):
- HELD: restricted to the matter = plain 1+log, every file (6 identical, the 2 mesh
  slices identical after their parameter dump; none different).
- HELD in kind, one number failed: the first pass differs from plain 1+log in 5 files;
  largest lapse 1.548 with plain 1+log and 1.108 with the first pass (I wrote "below
  1.08"; 1.108 is Track D's 1.109).
- HELD: `lapse_leak_hole = 1000` with a tracker = plain 1+log with the same tracker
  (7 + 2 files); a tracker alone changes no shared file. `lapse_leak_onset = 1e-9`
  equals the kink exactly in the constraint history.
Outcome T2 (homogeneous universe, rate 5): HELD, relative differences of the lapse and
of the volume between `lapse_leak_rho = 1e-3` and the first pass exactly 0; lapse at
the end 1.262437.
Outcome T3 (L1 at cells 1 M):
- (a) HELD: first pass, new executable = release core-v0.6, 17 of 17 files identical,
  for T = 1 M and 0.5 M. The statement of the first pass is untouched.
- (b) REFUTED for T = 0.5 M, held for T = 1 M:

| run | core | mid | outer | surface | central lapse off homogeneous | largest lapse on the mesh |
|---|---|---|---|---|---|---|
| first pass, T = 1 M | 3.08e-3 | 1.26e-3 | 3.34e-3 | 6.71e-3 | 2.8 per cent | 1.245 |
| matter only, T = 1 M | 3.46e-3 | 2.16e-3 | 6.22e-3 | 7.05e-3 | 2.2 per cent | 1.400 |
| first pass, T = 0.5 M | 1.67e-3 | 8.2e-4 | 2.78e-3 | 6.05e-3 | 0.2 per cent | 1.127 |
| matter only, T = 0.5 M | 2.31e-3 | 3.28e-3 | 1.12e-2 | 1.27e-2 | 0.2 per cent | 1.372 |

  Largest ratio to the first pass 1.86 (T = 1 M) and 4.04 (T = 0.5 M, outer and mid
  shells). The figure shows why [VERIFIED as a profile; reading JUDGEMENT]: outside the
  ball the lapse of plain 1+log rises to 1.37 to 1.40 by 10 M (peak near r = 24 M, still
  growing), inside it is held at 1.08 to 1.15, and the whole difference sits across the
  surface (1.10 to 1.22 within 2 M at r = 10 to 12 M). The centre is not reached (the
  central lapse is as good as in the first pass, so there is no focusing front), but
  the shells near the surface move through a steep lapse gradient, more so with the
  shorter T, and lose a factor 2 to 4. For the outer shells this is worse than plain
  1+log (3.6e-3 at cells M/2 in the first pass).
- So the density weight alone is not a correction that "keeps the expanding-matter
  tests": it trades the hole in vacuum for the surface of the matter. By the same
  reading the wall of the Einstein-Straus bubble (dust next to vacuum sliced by plain
  1+log) should lose accuracy with it.

What this changes [JUDGEMENT]. The vacuum next to expanding matter wants the relaxation
(first pass), the vacuum next to a black hole does not; the density cannot tell the two
apart, the distance from the hole can. The second candidate of decision 0022, the
switch-off around a tracked black hole (`lapse_leak_hole`), leaves L1, L2 and L3
exactly as in the first pass (no tracker: the first-pass statement runs; processor test
T4 added) and keeps the relaxation at the wall; what is open is whether a hole whose
neighbourhood is free but whose far zone is still held keeps its size. Job B (Slurm
4814, run core-20261121-173538-c8c2aec) had not started and was cancelled (status
stopped); its second version `card_b2.list` tests both candidates on the Einstein-Straus
data and the tracker candidate on V8 for 150 M. The first pass on the same
Einstein-Straus mesh is dropped for card time (reference: Track D's ES-1G, run
D-20261119-142633-6f72922). Expected 43 minutes (0.72 card-hours), wall limit 50
minutes; with job A at its expected 0.52 the item stays at 1.24 card-hours.

Predictions for the second version of job B (the predictions of entry 5 stand for
`es-rho` (a), (b), (d), (e), `collapse-rho`, `ball-l1-rho`, `ball-l2-rho`, `v8-rho`,
`v8-onset`, `v8-hole6`, with these amendments made after T3 and before the run):
- `es-rho` (c), amended: I now expect the wall tracers to be worse than 5e-4: between
  1e-3 and 2e-2 at tau = 100 M, by the surface effect of T3. The prediction of entry 5
  (within 5e-4) stays on record and will be judged as written.
- `ball-l1-rho`, `ball-l2-rho`, amended: by T3 I expect the outer and surface groups
  above twice the first pass (L2 with T = 0.5 M: outer above 8.6e-3); entry 5 stays on
  record.
- ES-h, `es-hole` (relaxation everywhere except within 16 M of a tracker at the
  puncture, in full beyond 32 M; the wall is at 33 M in the coordinates):
  (a) wall tracers within 3e-4 of the exact curve until tau = 100 M and the lapse at
  the dust tracers within 3 per cent of the homogeneous model (as the first pass: the
  relaxation acts on both sides of the wall);
  (b) horizon radius above 1.3 M at 50 M and at 100 M (the first pass: 1.33 M at 50 M,
  1.09 M at 100 M in vacuum, smaller with dust), and horizon mass varying by less than
  1.5e-4 over 40 to 100 M [JUDGEMENT, even odds: the far zone is still held and may
  still stretch the coordinates at the hole]. Refuted, and the tracker candidate not a
  correction at this radius, if the radius is below 1.2 M at 100 M.
- V8-h, `v8-hole16` (vacuum, 150 M): radius above 1.3 M at 100 and 150 M; mass drift
  from 100 M inside [-1.5e-4, +1.5e-4] to 150 M (job A's relaxed run should show the
  dip of -3e-4 to -6e-4 by 140 M). Refuted if the radius at 150 M is below 1.15 M or the
  drift leaves [-3e-4, +3e-4].

## Entry 7 (10:15): outcome of job A (V8); the faces at 64 M limit the reduced set-up to 50 to 70 M; job C

Job A: run core-20261121-171151-90f52f4 (Slurm 4812, 09:53 to 10:12 PST). `v8-leak` ran
to 200 M in 858 s (0.136 s per step: the step time on a card is now measured, 8.7e6
cell-steps per second with blocks of 16^3); `v8-ctl` was stopped by me at t = 62 M
(`nrpic-run stop`, status stopped) when it was clear that the faces spoil both runs;
0.32 card-hours in all. Processor test T4 (run core-20261121-175314-27d9c53):
`lapse_leak_hole` without a tracker writes the bytes of the first pass, 17 of 17 files.
Byte regression against release core-v0.6 (run core-20261121-175311-bc4afdd,
`regress_v04.py`, serial builds): PASS, 75 of 75 items identical in the twelve set-ups.

Analysis core-20261121-181206-ddc687e (`results/v_numbers_jobA.json`, figure
`figs/v_jobA.png`, looked at after this entry was written; the numbers below are from
the table the script printed).

Outcome V8-a:
- The reduced mesh reproduces Track D's runs while the faces are silent [VERIFIED]:
  relaxed run against V-1GB, mass within 8e-6 and radius to three digits from 50 to
  70 M (1.001135, 1.216 M at 70 M against 1.001127, 1.216 M); control against V-1B,
  1.000963, 2.041 M at 50 M against 1.000939, 2.038 M.
- (a) REFUTED as written: from t = 72 M the relaxed run leaves V-1GB (-2.1e-4 at 74 M,
  -1.7e-3 at 86 M, lowest -2.9e-3 at 127 M, +6.65e-3 at 199.5 M; radius 0.779 M at
  199.5 M against 0.875 M). The signal of the outflow faces at 64 M reaches the hole
  after 71 M, also with the relaxed lapse. My judgement "the near faces do not matter
  for this run" was wrong: Track D's pair with faces at 192 and 384 M agreed to 188 M
  because the signal of faces at 192 M needs about 213 M at this speed (0.9), not
  because the relaxed lapse shields the hole.
- (b) the control: radius HELD (2.041 M at 50 M); the mass leaves the band at 55 M
  (0.998851 at 60 M, -2.8e-3 at 62 M): the faces again, arriving after about 53 M at
  the speed of the plain 1+log lapse (1.2). As foreseen in kind, larger than I wrote.
- (c) not testable beyond 50 M. Up to 50 M the two runs differ by less than 2e-4 in mass
  (-1.9e-4 at 15 M, +8e-5 at 50 M) and by 0.65 in radius (1.325 against 2.041 M).
- On the +x axis at 50 M (finest level): plain 1+log has the lapse above 1 from 5 M
  outward (1.05 at 5 M, 1.32 at 20 M, largest 1.47 at the face), chi 0.87 to 0.88 at 5
  to 20 M and an outward shift of 0.44 at 1 M; the relaxed run has the lapse 0.88 at
  5 M and 1.04 at 20 M, chi 0.68 and 0.58 (falling), shift 0.25. These are Track D's
  numbers of V-1B and V-1GB (their entry 7).

So at cells of M/8 the late mass drift cannot be had cheaply: it needs 150 to 200 M and
therefore faces beyond 200 M (Track D's size). What the reduced set-up shows cheaply is
the cause's first link, the horizon radius. For the last link (fewer cells, larger mass
error) the cells are made coarser instead of the run longer:

Job C (`card_c.list`), test V4: the same data, finest cells M/4 on +-8 M, faces at
+-128 M (signal at the hole after about 105 M with plain 1+log, 140 M relaxed), 100 M,
288 MeshBlocks, 1600 steps = 3.6 minutes per run: plain 1+log, first pass, and the
tracker candidate with r_h = 16 and 32 M. 0.24 card-hours; with A (0.32) and B (0.72
expected) the item is at 1.28 card-hours.

Prediction V4 (written before submission):
- (a) `v4-ctl`: radius within 6 per cent of V-1B at 50 and 100 M (2.04, 2.15 M); mass
  between its largest and smallest value over 40 to 100 M within 3e-3 [JUDGEMENT: 8
  cells in the radius].
- (b) `v4-leak`: radius within 6 per cent of V-1GB (1.33 M at 50 M, 1.09 M at 100 M:
  5.3 falling to 4.3 cells). Mass: its spread over 40 to 100 M at least three times the
  control's, and it differs from the control by more than 3e-3 at some time in 40 to
  100 M. Refuted (the shrinking does not turn into a mass error at this level) if the
  spread is below twice the control's.
- (c) `v4-hole16`, `v4-hole32` [JUDGEMENT, even odds]: the radius at 100 M is at least
  1.5 M with r_h = 32 M and at least 1.3 M with r_h = 16 M, and the mass spread over 40
  to 100 M is below twice the control's for both. If the radius of `v4-hole32` at
  100 M is within 10 per cent of `v4-leak`, the far zone alone shrinks the hole and
  the tracker candidate is no correction at any radius that fits inside a bubble.

## Entry 8 (10:40): first look at job B while it runs; why the hole shrinks; prediction for job D

Job B (run core-20261121-175300-77c17ae, Slurm 4815) started at 10:12 when job A was
stopped. First look at its first three runs (unregistered reads of the files while the
job runs; the judged numbers follow from registered analyses in entry 9):
- `es-rho` (relaxation only in the dust): the largest lapse on the mesh reaches 1.95,
  the horizon mass swings by 4e-3 from 55 M on, tracer groups are off by per cents.
- `es-hole` (relaxation off within 16 M of the puncture): horizon radius 1.6 M and
  steady, mass flat from 78 M, wall tracers at the 6e-4 level.
- `v8-hole16` to 72 M (before the faces): radius 1.4 to 1.75 M, not shrinking.
Processor test T5 (run core-20261121-182235-6083050): `lapse_leak_hole` without a tracker
writes the bytes of the first pass on the first 16 steps of L2 (bound ball, cells M/2;
9 of 9 files) and the first 8 steps of L3 (collapse mesh; 7 of 7 files).

Why the hole shrinks under the first pass [JUDGEMENT; consistent with every run so far,
tested by the tracker runs]. Without shift, 1+log keeps alpha - 2 ln sqrt(gamma) constant
along the normal observers: the lapse can only fall back to its stationary value if the
volume element comes back too, so plain 1+log cannot stretch the coordinates for good.
The relaxation term breaks exactly this: d(alpha - 2 ln sqrt(gamma))/dt = -(alpha/T)
ln(alpha/alpha_0), so wherever the lapse is held above alpha_0 the volume element of the
normal observers grows by (1/2T) times the time integral of ln(alpha/alpha_0) (with T =
2 M and an excess of 0.07 falling to 0.015 that is a factor e in 200 M). In the dust that
is the intended comoving expansion. In the vacuum bubble it is a stretching of the
coordinates, and the normal observers carry it inward: they drift towards the puncture
through the mesh at the speed of the shift (0.06 at 5 M, 0.25 at 1 M in job A), so the
stretched elements made between 7 and 12 M, where the first pass holds the lapse just
above 1, reach the horizon after 50 to 150 M. That is the delayed, slowing shrinking of
V-1GB, and the reason a switch-off radius must cover the zone from which the normal
observers reach the hole during the run (the shift is 0.002 at 20 M: from 16 M the
drift takes more than 500 M).

Job D (`card_d.list`): the first pass on the Einstein-Straus mesh of job B (same input
as `es-hole` with `lapse_leak_hole = 0`), 100 M, about 9 minutes (0.15 card-hours; the
item then stands at about 1.43 of 1.5). It is the reference on the same mesh, which I
had dropped from job B.
Prediction ES-f2 (written before submission): horizon radius within 5 per cent of
Track D's ES-1G (1.40 M at 25 M, 1.06 M at 100 M); horizon mass rising, largest minus
smallest over 40 to 100 M between 1.5e-4 and 4e-4; wall tracers (R_0 = 36 M) between
2e-4 and 7e-4 and the group at 40 M between 1e-3 and 2e-3 until tau = 100 M, that is, the
same as `es-hole` within a factor 2 (the wall error of this mesh is set by its cells of
2 M, not by the switch-off) [JUDGEMENT]. If the first pass follows the wall three times
better than `es-hole`, the switch-off costs accuracy at the wall and the radius 16 M is
too close to it.

## Entry 9 (10:55-11:10): outcomes of job B; the density weight is refuted and removed; job F replaces C and D

Job B: run core-20261121-175300-77c17ae (Slurm 4815, 10:12:49 to 10:53:26, nine runs, all
exit 0, 0.68 card-hours; with job A the item stands at 1.00). Registered analyses:
core-20261121-184901-d62073f (`es2.py`: Einstein-Straus, collapse),
core-20261121-184940-09e7911 (`ball2.py`), core-20261121-185349-b7f87a8 (`vanalysis.py`),
core-20261121-185408-5ecd05b (`vident.py`). Numbers `results/es2_numbers_jobB.json`,
`ball2_jobB.json`, `v_numbers_jobB.json`, `vident_v8rho.json`; figures
`figs/es_g2_es-rho.png`, `es_g2_es-hole.png`, `es2_horizon_jobB.png`,
`collapse_g2_collapse-rho.png`, `ball2_jobB.png`, `v_jobB.png`, all looked at.

### The density weight (`lapse_leak_rho`): REFUTED as a correction

| test | first pass | relaxation only in the matter |
|---|---|---|
| ES-c `es-rho`, horizon mass, largest minus smallest over 40 to 99.5 M | (Track D's ES-1G: 2.7e-4) | 4.2e-3 (0.99878 to 1.00295), swinging from 55 M on |
| ES-c, horizon radius at 25, 50, 75, 100 M | (ES-1G: 1.40, 1.33, 1.18, 1.06 M) | 2.03, 1.41, 1.66, 2.07 M |
| ES-c, wall tracers (R_0 = 36 M) until tau = 30 M / 100 M | 6.2e-5 / not run | 2.3e-2 / 6.3e-2 |
| ES-c, tracers at 20, 28, 48, 56 M until 100 M | (30 M: 7e-5, 1.2e-4, 6.8e-5, 2.4e-4) | 2.9e-2, 2.8e-2, 1.1e-2, 3.0e-2 |
| ES-c, largest lapse on the mesh; lapse at the dust tracers off the homogeneous model | 1.11; 1.3 per cent | 1.95; 4.6 per cent |
| L1-c `ball-l1-rho` (cells M/2, T = 1 M): core, mid, outer, surface | 1.16e-3, 5.8e-4, 2.0e-3, 4.1e-3 | 1.15e-3, 2.2e-3, 3.9e-3, 5.9e-3 |
| L2-c `ball-l2-rho` (cells M/4, T = 0.5 M): core, mid, outer, surface | 9.2e-3, 2.5e-3, 4.3e-3, 6.4e-3 | 2.7e-2, 5.6e-2, 8.7e-2, 0.30 |
| L2-c, turnaround R/R_0 (exact 1.25); largest lapse | 1.2478; 1.17 | 1.251 to 1.261; 1.88 |
| L3-c `collapse-rho`: turnaround R/R_0 and its proper time (exact 1.25 at 9.54 M) | 1.250 to 1.251 at 9.5 to 9.6 M | 1.32 to 1.35 at 11.8 to 14.2 M |
| L3-c, horizon mass | 0.9980 to 1.0003 from 29 M | 0.968 at 26 M, 1.025 to 1.038 from 30 M |

- ES-c (a) refuted in its sense (the radius swings between 1.4 and 2.1 M), (b) REFUTED
  (4.2e-3 against 2e-4), (c) REFUTED also in the amended form (6.3e-2, above 2e-2), (d)
  FAILED (4.6 per cent, lapse 1.95), (e) held (no dust inside the wall tracers; 28
  tracers removed: the groups from 6 M and from 10 M).
- L1-c held as written (core 1.15e-3, central lapse within 2.0 per cent); the mid shells
  are 3.8 times worse than the first pass.
- L2-c REFUTED (every group 3 to 47 times worse); L3-c REFUTED (turnaround and horizon
  mass wrong by per cents: this is no longer a matter of coordinates, the evolution
  itself has lost its accuracy).
- Reading [JUDGEMENT, the lapse profiles of `ball2_jobB.png` and the largest lapse are
  VERIFIED]: next to expanding matter the vacuum's normal observers diverge too; left
  to plain 1+log its lapse grows (1.88 outside the bound ball, 1.95 in the bubble, 2.36
  in the collapse run) against a capped lapse in the matter, and the step sits on the
  surface: the front of the first wave again, now from outside. The entry-4 argument
  ("the vacuum has a stationary slice which plain 1+log finds") is true only far from
  moving matter.
- V8-c HELD: on a card, with the branch executable, the relaxed lapse restricted to the
  matter writes the lines of plain 1+log run with the release executable (25 lines of
  the horizon summary, 15 and 41 of the two histories, to t = 12 M).

### Cause tests C2 and C3 (V8, 30 M)

| run | horizon radius at 15, 20, 30 M | mass minus control at 15, 20, 30 M |
|---|---|---|
| plain 1+log (control) | 1.517, 2.055, 1.907 | 0 |
| first pass | 1.400, 1.375, 1.415 | -1.9e-4, -1.1e-4, -7.3e-5 |
| C2 smooth onset, delta = 0.02 | 1.411, 1.388, 1.418 | -2.3e-4, -9.6e-5, -7.1e-5 |
| C3 off within 6 M (full beyond 12 M) | 1.439, 1.429, 1.440 | -2.5e-4, -8.6e-5, -4.4e-5 |
| off within 16 M (full beyond 32 M) | 1.528, 1.899, 1.386 | +5e-7, +1.1e-4, +9.3e-5 |

- C2 (the kink) is NOT the cause: a smooth onset changes the radius by 1 per cent
  (prediction held).
- C3 (the action near the hole) is NOT the cause: with the term off inside 6 M the
  radius follows the first pass within 4 per cent (prediction held).
- C4 stands: freeing the bubble out to 16 M lets the lapse front form (largest lapse
  1.62 in `es-hole`) and the horizon follow the control to 20 M (1.90 against 2.06 M).

### The tracker candidate (`lapse_leak_hole = 16`)

| quantity | first pass | off within 16 M of the puncture |
|---|---|---|
| ES-h `es-hole`, horizon radius at 25, 50, 75, 100 M | ES-1G: 1.40, 1.33, 1.18, 1.06 M | 1.59, 1.61, 1.63, 1.65 M |
| ES-h, horizon mass over 40 to 99.5 M | ES-1G: 1.00098 to 1.00125 (2.7e-4, rising) | 1.00085 to 1.00129 (4.4e-4: wiggles between 33 and 78 M, flat afterwards) |
| ES-h, wall tracers until tau = 30 / 60 / 100 M | 6.2e-5 / not run / not run | 2.1e-4 / 4.3e-4 / 6.3e-4 |
| ES-h, tracers at 20, 28, 40, 48, 56 M until 30 M | 7.0e-5, 1.2e-4, 4.6e-4, 6.8e-5, 2.4e-4 | 3.8e-4, 5.2e-5, 4.8e-4, 8.3e-5, 2.1e-4 |
| ES-h, lapse at the dust tracers off the homogeneous model; largest lapse | 1.3 per cent; 1.11 | 1.2 per cent; 1.62 (the front inside 16 M, gone by 80 M) |
| V8-h `v8-hole16`, radius at 30, 40, 50, 60, 65 M | 1.415, 1.371, 1.325, 1.270, 1.242 | 1.386, 1.448, 1.588, 1.722, 1.749 |
| V8-h, mass over 35 to 65 M | 1.001015 to 1.001099 (8.4e-5) | 1.000971 to 1.001054 (8.2e-5); control V-1B 1.7e-5 |

- ES-h (b) radius HELD (1.61 and 1.65 M, steady); mass band FAILED as written (4.4e-4
  against 1.5e-4), not refuted (the refutation was a radius below 1.2 M). (a) the wall:
  FAILED (6.3e-4 against 3e-4 at 100 M); at equal proper time, 30 M, the wall is 3.4
  times less accurate than in the first pass on the same lattice (2.1e-4 against
  6.2e-5) and the bubble tracers at 20 M 5 times; the dust groups at 40, 48 and 56 M are
  unchanged. The outer groups (56, 66, 78 M) reach 3e-3 to 5e-3 at 100 M from tau = 50 M
  on: the faces of this mesh at 128 M [JUDGEMENT from the arrival times], not the gauge.
  Lapse at the dust tracers HELD (1.2 per cent).
- V8-h: radius HELD in the part that can be judged (not shrinking: 1.75 M at 65 M,
  1.58 M at 100 M); the mass drift 100 to 150 M is NOT TESTABLE with faces at 64 M
  (their signal is in every run from 71 M on). Until 65 M the mass band is that of the
  first pass (8e-5), five times the control's.
- So the tracker candidate removes the cause (the horizon no longer shrinks, on the
  Einstein-Straus data for 100 M) at a price at the wall (a factor 3.4 at 30 M; 6.3e-4 at 100 M,
  where plain 1+log has 2.2e-3 at 200 M in Track D's run). It is NOT
  shown here that the late mass drift of 100 to 200 M is gone: no run of this package
  reaches that time with silent faces yet. Job F is aimed at exactly that.

### Decision on the source

`lapse_leak_rho` gives wrong evolutions next to matter (L2, L3, ES) and `lapse_leak_onset`
changes nothing. Both are removed from the source: `athenak/src/z4c/z4c_gauge_ext.hpp`
keeps `lapse_leak_hole` only (the kernel no longer reads the matter sources). The
executables that ran jobs A to B are kept as
`scratch/core/gauge2/exe/athena_{cpu,gpu}_90f52f4`. Processor test T7 compares the
cleaned build with the old one on a run with the switch-off active, and with the release
on the first pass; the byte regression is repeated.

Prediction T7 (before the run): first pass, cleaned build = release (L1, 8 steps), every
file; switch-off within 8 M on the coarse vacuum mesh, cleaned build = build 90f52f4,
every file (the arithmetic of the weighted term is unchanged: rate x alpha x excess x
weight); radius beyond the mesh = plain 1+log; and the run with 8 M differs from both
the first pass and plain 1+log (the weight is active). Byte regression against release
core-v0.6: PASS, 75 of 75.

### Job F (replaces C and D, cancelled while pending; `card_f.list`)

The remaining 0.5 card-hours go to the test that the task names and that nothing so
far answers: the late drift in vacuum with the corrected condition. `v8far-hole16`: V8
with the faces at +-256 M (400 MeshBlocks, 0.19 s per step expected, 20 minutes, 0.34
card-hours), 200 M, cleaned card build; compared with Track D's V-1B and V-1GB, which
this mesh reproduced to 8e-6 while the faces were silent. Then `v4-ctl` and `v4-leak`
(prediction V4 (a), (b) of entry 7; 0.12 card-hours). The first pass on the
Einstein-Straus mesh (job D) and the tracker runs at M/4 are dropped; prediction ES-f2
is therefore NOT TESTED at 100 M (its 30 M part is answered above by the first-pass run
of 2026-11-15: the wall is 3.4 times better there, so by my own criterion the radius
16 M is too close to a wall at 33 M).
Prediction V8-f (written before submission): with the switch-off at 16 M the horizon
radius stays above 1.4 M from 35 M to 199.5 M (V-1GB: 0.875 M at the end) and the mass
drift from its value at 100 M stays inside [-1.5e-4, +1.5e-4] until 199.5 M (V-1B:
[-4.8e-5, +2.0e-5]; V-1GB: [-5.6e-4, +1.27e-3]) [JUDGEMENT, two chances in three: in
`v8-hole16` the radius fell from 1.58 to 1.31 M between 100 and 150 M, which I attribute
to the faces of that run]. Refuted, and the radius 16 M only a delay, if the radius
falls below 1.2 M or the drift leaves [-4e-4, +4e-4].

## Entry 10 (11:25): the cleaned source verified on processors; state while job F waits

Source commit 984110c3 (`lapse_leak_hole` only), builds `.work/build_cpu_g2b` and
`.work/build_gpu_g2b` (scripts/build_cpu.sh, scripts/build_gpu.sh).
Outcome T7 (run core-20261121-190712-c3e50b6, `results/ptests_T7.json`): HELD in every
part. First pass, cleaned build = release core-v0.6 (L1, 8 steps): 9 of 9 files.
Switch-off within 8 M on the coarse vacuum mesh, cleaned build = build 90f52f4d: 9 of 9
files, so the card results of jobs A and B carry over to the cleaned source as far as
the processors can show. Radius beyond the mesh = plain 1+log: 7 files identical, 2
identical after the parameter dump. The run with 8 M differs from the first pass and
from plain 1+log in 6 files each (the weight is active).
Byte regression of the cleaned build against release core-v0.6 (run
core-20261121-190715-f702a98, `regress_v04.py`): PASS, twelve set-ups, 75 of 75 items.
The example `problems/es/es_gauge_hole.athinput` starts with the cleaned processor
build (344 MeshBlocks, two steps; unregistered smoke test in `scratch/core/tmp/
g2_example`): "Z4c gauge: lapse excess over 1 relaxes at the rate 0.5, off within 16 of
every tracker (in full beyond 32)".

Card job F (run core-20261121-190709-8b205e5, Slurm 4821, card build of 984110c3) was
submitted at 11:07 and waits behind a job of Track F and one of another user.
Card time used so far: job A 0.32, job B 0.68 card-hours; job F is expected to take
0.46 (limit 0.55), which brings the item to 1.46 of 1.5.

## Entry 11 (12:15-12:30): outcome of job F; what the correction does and does not do; handoff

Job F: run core-20261121-190709-8b205e5 (Slurm 4821, 11:43:35 to 12:13:15, three runs,
all exit 0, 0.49 card-hours, card build of the cleaned source 984110c3). Analyses
core-20261121-200532-b95d775 (`results/v_numbers_jobF.json`, `figs/v_jobF.png`) and
core-20261121-201340-af2287a (`results/v_numbers_jobF_v4.json`, `figs/v_jobF_v4.png`),
both figures looked at. Card time of the item: 0.32 + 0.68 + 0.49 = 1.49 of 1.5
card-hours.

### Outcome V8-f: the late drift in vacuum with `lapse_leak_hole = 16` (M/8, faces at 256 M, 200 M)

| t / M | plain 1+log (V-1B): mass, radius | first pass (V-1GB) | off within 16 M (`v8far-hole16`) |
|---|---|---|---|
| 50 | 1.000939, 2.038 | 1.001041, 1.325 | 1.000994, 1.588 |
| 100 | 1.000937, 2.147 | 1.001186, 1.086 | 1.001036, 1.638 |
| 120 | 1.000923, 2.166 | 1.000811, 1.022 | 1.001213, 1.567 |
| 160 | 1.000933, 2.187 | 1.000854, 0.932 | 1.001183, 1.444 |
| 199.5 | 1.000928, 2.196 | 1.002450, 0.875 | 1.001215, 1.306 |
| mass drift from 100 M, 100 to 199.5 M | [-4.8e-5, +2.0e-5] | [-5.6e-4, +1.26e-3] | [0, +2.08e-4] |
| mass, largest minus smallest, 120 to 199.5 M | 6.8e-5 | 1.8e-3 | 4.4e-5 |
| mass, largest minus smallest, 40 to 199.5 M | 6.8e-5 | 1.8e-3 | 3.7e-4 |

- FAILED as written, not refuted: the drift from 100 M reaches +2.08e-4 at 116.5 M
  (band +-1.5e-4) and the radius is below 1.4 M at 30 to 37 M (1.38 M) and from 170 M on
  (1.31 M at the end); the refutation marks (radius below 1.2 M, drift beyond 4e-4) are
  not reached.
- What the run shows [VERIFIED]: the mass has transient wiggles of up to 2e-4 between
  65 and 116 M (the lapse front of the freed zone dying out; they are in `es-hole` and
  in `v8-hole16` at the same times, so the bump I had put down to the faces in entry 9
  was this), then it is flat within 4.4e-5 from 120 to 199.5 M, 2.5e-4 above the
  control. The dip and the late rise of the first pass are gone: over 100 to 199.5 M
  the band is 2.1e-4 instead of 1.8e-3. It is not the control's 6.8e-5.
- What it also shows [VERIFIED]: the horizon radius is steady near 1.6 M only until
  about 110 M and then falls again, 1.57, 1.44, 1.31 M at 120, 160, 199.5 M, at
  -3.5e-3 per M over the last 50 M (the first pass falls at -1.5e-3 per M there, from
  0.95 M). chi at 5 M is 0.84, 0.86 at 50, 100 M and 0.74 at 180 M. So a radius of 16 M
  delays the shrinking by about 100 M and starts it from a larger horizon; it does not
  stop it. At this rate the horizon would be back at 0.9 M near 320 M [JUDGEMENT,
  extrapolation]. My estimate of entry 8 (several hundred M from 16 M at the speed of
  the shift) was too long by a factor 3 to 4: the transport is not only the drift of
  the normal observers, or the partially held zone between 16 and 32 M counts for more
  than its weight suggests. Not resolved here.

### Outcome V4 (a), (b): the defect with coarser cells (M/4, faces at 128 M, 100 M)

- (a) HELD: control radius 2.014 M at 50 M and 2.115 M at 99 M (V-1B 2.038, 2.147);
  mass between largest and smallest over 40 to 99 M 1.7e-3 (a slow fall).
- (b) HELD: first-pass radius 1.319 M at 50 M, 1.040 M at 99 M (V-1GB 1.325, 1.086 M at
  100 M); its mass leaves the control by +5.1e-3 at 50 M, +9e-3 at 70 M and -2.1e-2 at
  99 M; spread over 40 to 99 M 3.1e-2, 18 times the control's.
- So the cheapest set-up that shows the defect in the mass itself is V4: finest cells
  M/4, faces at 128 M, 100 M, 4 minutes per run on a card (0.07 card-hours), against
  0.78 card-hours for Track D's V-1GB. The radius histories at M/4 lie on Track D's at
  M/8 to 1 to 4 per cent; the mass error of the relaxed run grows as its horizon falls
  from 5.5 to 4.2 cells, the control with 8 cells stays smooth. This is the last link
  of cause C4 (fewer cells across a shrinking horizon), in a run in which it could
  have failed.

### Where the item stands

Established: the cause (the relaxation term stretches the coordinates of a vacuum whose
normal observers diverge, and the horizon shrinks into too few cells); two candidate
causes excluded by runs (kink, action near the hole); the density weight refuted as a
correction and removed; `lapse_leak_hole` implemented, bit-identical when absent or
without a tracker, and tested: Einstein-Straus 100 M (horizon 1.6 M, steady; mass band
4.4e-4 with its transient, flat after 78 M; wall 2.1e-4 at 30 M, 6.3e-4 at 100 M),
vacuum 200 M (late band 2.1e-4, flat within 4.4e-5 after 120 M).
NOT established: "a black hole in vacuum is left as with plain 1+log to the level of
the control". With r_h = 16 M the late band is 2.1e-4 against the control's 6.8e-5, there
is a transient of 2e-4 before 120 M, the horizon shrinks again after 110 M, and the wall
of the Einstein-Straus bubble is followed 3.4 times less closely at 30 M than by the
first pass. The option is a mitigation for runs up to about 200 M, not the cure.

### Handoff (for a reader with no memory)

State. Branch `core/gauge-2` (worktree `wt/core-s1`), pushed. Source: one file changed
against release core-v0.6, `athenak/src/z4c/z4c_gauge_ext.hpp` (commit 984110c3); no
shared file touched (the hooks of the first pass in `z4c.hpp`, `z4c.cpp`,
`z4c_calcrhs.cpp` are unchanged). Executables: `scratch/core/exe/core_gauge-2/`
(athena_gpu, athena_cpu, COMMIT, SHA256SUMS, READY), built from 984110c3; the builds
that ran jobs A and B (commit 90f52f4d, with the two removed factors) are kept in
`scratch/core/gauge2/exe/`. Interface text: `tracks/core/interfaces/cosmo_gauge.md`
section 9 (proposal for `coord/INTERFACES/cosmo_gauge.md`). Example:
`problems/es/es_gauge_hole.athinput`; reduced vacuum set-up
`problems/es/v1_small.athinput`. Everything else: `tracks/core/analysis/gauge2/`
(`README` is this journal; `make_inputs.py --check`, the card lists `card_*.list`,
`vanalysis.py`, `es2.py`, `ball2.py`, `ptests.py`, `vident.py`, `figs/`, `results/`).

Failed or untested predictions, kept on record: V4-a not tested (processor runs
mis-sized, stopped); T1 one number (largest lapse of the first pass 1.108, not below
1.08); T3 (b) for T = 0.5 M (refuted: the density weight costs the surface shells a
factor 4); V8-a (a) refuted (faces at 64 M), (c) not testable; ES-c (a) to (d) refuted
or failed (density weight); L2-c, L3-c refuted (density weight); ES-h wall and mass band
failed (not refuted); V8-h mass part not testable; ES-f2 not tested at 100 M (job D
cancelled), its 30 M part answered against the first-pass run: the wall is 3.4 times
better without the switch-off; T7 held; V8-f failed as written (not refuted); V4 (c) not
tested (tracker runs at M/4 dropped for card time).

Open (new lines of work, none started):
1. A cure instead of a delay. The far zone that stays held keeps stretching and reaches
   the hole after about 100 M with r_h = 16 M. Candidates [JUDGEMENT]: a larger radius
   where the matter allows it (not tested; in vacuum r_h can be any size); a term that
   holds the lapse of expanding matter without giving up alpha - 2 ln sqrt(gamma) in
   vacuum (the density weight did that and failed on the lapse step at the surface, so
   it would need a transition layer wider than a cell around the matter); a shift
   condition that takes the stretching out again.
2. Einstein-Straus beyond 100 M with the option, and the first pass on the same mesh to
   100 M (dropped here for card time): Track D's ES-1GB and V-1GB with
   `lapse_leak_hole = 16` to 200 M would be the direct test of their null-test floor.
3. Other radii (between 6 and 16 M, and above), several trackers, a moving hole, MPI.
4. Holes that form in the run (Track A, L3): no tracker exists before the collapse, the
   option does nothing for them; the first pass's advice (finer cells at the centre)
   stands. Track A's horizon mass 2e-2 high at first detection was not looked at here.
5. The outer faces: an outflow face at 64 M changes the horizon mass by 2e-3 to 3e-3
   after 53 M (plain 1+log) or 71 M (relaxed), at 128 M the tracers beyond 56 M lose
   accuracy from 50 M on. Reduced set-ups need the faces further than the run is long.
