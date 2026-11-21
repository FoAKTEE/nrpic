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
