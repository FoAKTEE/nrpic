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
