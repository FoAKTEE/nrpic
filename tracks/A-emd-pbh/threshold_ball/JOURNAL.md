# JOURNAL of threshold_ball (A-emd-pbh)

## Entry 1, 2026-11-21 12:40 PST (lead of batch 5; committed 12:41:43 as c48bd33b, first submission 12:41:49): predictions before any card run

Design: DESIGN.md (design run A-20261121-202520-3164672, data run A-20261121-202812-cae4436,
smoke tests A-20261121-203156-d094c56 failed: `diagnostics` not declared in the decks, then
A-20261121-203211-6d3ce73 exit 0 on both decks with every option; the finder exits a failed
search after 2 flow iterations, "mean radius neg").

Measures (as conv_ball, compare.py of runs_ball with `--gauge leak --leak 8 --nest 32:<1/h_f>`):
ddet = proper time of the tracked particles at the finder's mean radius at first detection minus
the exact tau_AH of the shell there; dmmed = median over detections of the finder's irreducible
mass against the exact horizon mass of the same slice; BH = horizon found in at least three
consecutive searches spanning at least 5 M_AH, and every later search finds it.

Predictions (each with what refutes it):

- T1 (BH side, mesh B: delta_c = 1.0, 0.7, 0.5, 0.45, 0.42). Each forms a persistent apparent
  horizon before its tlim. |ddet| <= 0.2 M for delta_c >= 0.7 and <= 0.5 M for 0.42-0.5 (the
  horizon has about 8 cells of M/32 across its coordinate radius at 0.42 against 13 at 1.5; conv_ball
  B gave +0.068 M at 1.5). |dmmed| <= 5e-3 for delta_c >= 0.7 and <= 1e-2 below (conv_ball B
  2.1e-3 at 1.5). Refuted by a member without a persistent horizon by tlim, or by errors above
  these bounds.
- T2 (late side, mesh B: 0.40, 0.35, 0.20). No search succeeds before the tracked particles at
  the core edge reach proper time 45 (no false horizon in the expanding or turning ball); 0.40
  then forms its horizon before tlim 54 (exact 46.415), 0.35 before tlim 62 (exact 54.980); 0.20
  forms none to t = 70 and its core edge is contracting at t = 70 (exact turnaround 55.568).
  Refuted by any detection with particle proper time below 45, or by a missing horizon of 0.40
  or 0.35 by tlim.
- T3 (bracket). The code's bracket at t_end = 45 in the invariant measure equals the exact one,
  A_c(45) in (0.40, 0.42], with the BH member's horizon at proper time 43.66 +- 0.5 and the late
  member's at 46.42 +- 0.5. Refuted if either member lands on the other side of 45.
- T4 (meshes at the bracket). Mesh A (M/16; about 4 cells across the horizon's coordinate radius)
  finds no persistent horizon for 0.42 or 0.40 before tlim [JUDGEMENT; BH-1 at uniform M/8 with
  3.4 cells found none, run A-20261119-144419-13d5601]. Mesh C (M/64) finds the horizon of 0.42
  with |ddet(C)| <= |ddet(B)|/2 and |dmmed(C)| <= |dmmed(B)|/2. Refuted by a persistent horizon on
  A, or by C not halving B's errors.
- T5 (conv_ball C-R1.25, core_gauge, as conv_ball's C with the 1.25 ball). ddet within 0.02 M and
  dmmed within 1e-3 of conv_ball's C (0.017 M and 2.1e-4; README of conv_ball), i.e. the ball
  radius does not change the finest-mesh errors. Refuted by larger differences.
- T6 (health and cost). Every member ends at tlim (Slurm state COMPLETED, chain status DONE,
  no guard stop); the L2 norm of H outside the horizon stays below 0.1 of that of 16 pi E (the BH
  criterion of SCOPE section 3). Mesh B on the core-v0.6 card build costs 0.25-0.40 s per cycle
  (core_gauge B 0.262 s with outer 16 M). Refuted by a guard stop, a constraint ratio above 0.1,
  or a cost outside that band (the cost is read from the first B chain before the others run).

Gauge note (decision 0025 item 3): the members are collapse runs with M/32 or finer at the centre
and stop 4-8 M after the exact tau_AH, far short of the late vacuum drift of the relaxed lapse
(about a hundred M); they keep lapse_leak = 8 as conv_ball. No null test or long run around an
existing black hole is in this queue.

## Entry 2, 2026-11-21 12:45 PST: submissions

Sequencer started 12:41:49 (pid 2666191, state scratch/A-emd-pbh/sequencer_threshold/). Queue
line 3 -> B-d0.42, run A-20261121-204149-c48bd33, Slurm 4838 (chain, MAX_SEGMENTS 2, v0.6
executable confirmed in chain/config.sh); line 4 -> B-d0.40, run A-20261121-204250-0bf45c7,
Slurm 4845. Both PENDING behind other owners' jobs at 12:44. The rest of the queue (lines 5-13)
waits for the sequencer. Outcomes go into entry 3 onward; how to read them: HANDOFF.md of the owner.

## Entry 3, 2026-11-24 13:00Z (lead of batch 11): state of the scan; continuation of C-d0.42

All twelve queue lines (3-13) were submitted by the sequencer, which ended normally on
2026-11-23 10:40 PST ("queue finished; exit"). Chains DONE at tlim: lines 3, 4, 6-12. Line 5
(A-d0.42 and A-d0.40, batch A-20261121-235851-d2200d7): both members exit 3 (guard stop), read
in entry 4. Line 13, C-d0.42 = A-20261122-173202-f98c79f: cut by preemptions (nine SIGTERMs on
2026-11-23; segments 12-14 each restarted from t = 40 and were killed before t = 42), closed as
FAILED with MAX_SEGMENTS = 14 reached, at t = 41.99 of 51; newest restart `rst/ball.00017.rst`
(t = 40). No guard stop or non-finite field in any segment log. Continued in place, not repeated:
same run directory, executable (cmp-identical to the v0.6 card build), deck and arguments,
MAX_SEGMENTS 21, restart cadence dt 4 -> 2 by `output2/dt=2.0` (cadence only). Prediction T4
for mesh C stands as written in entry 1.

## Entry 4, 2026-11-24 13:20Z (lead of batch 11): outcomes T1-T6 (analysis A-20261124-131120-5c974ce)

Runs closed with nrpic-run finish (DONE at tlim): lines 3, 4, 6-12; line 5 (A-mesh batch
A-20261121-235851-d2200d7) failed, both members exit 3 at the guard. Analysis: `scripts/analyse.py`
(around `compare_tb.py`, a marked copy of conv_ball's compare.py that keeps every line output and
reads chain logs), registered as A-20261124-131120-5c974ce; table `threshold.md`, verdicts
`threshold.json`, figures `fig_threshold_outcome.png` and `fig_threshold_slice_or_finder.png`
(both looked at). ddet = proper time of the tracked particles at the finder's radius at first
detection minus the exact tau_AH of the shell there; dmmed = median over detections of
m_irr/m_exact(slice) - 1.

| member | exact tau_AH | persistent from t | tau_det | ddet | dmmed | s/cycle |
|---|---|---|---|---|---|---|
| B-d1.00 | 15.386 | 17.000 | 15.513 | +0.126 | -3.8e-4 | 0.304 |
| B-d0.70 | 23.405 | 25.250 | 23.472 | +0.059 | -1.9e-3 | 0.313 |
| B-d0.50 | 35.160 | 37.188 | 35.131 | -0.040 | -9.4e-3 | 0.321 |
| B-d0.45 | 40.054 | 42.250 | 40.117 | +0.043 | +1.9e-3 | 0.324 |
| B-d0.42 | 43.656 | 45.875 | 43.686 | +0.015 | +2.8e-3 | 0.324 |
| B-d0.40 | 46.415 | 48.625 | 46.402 | -0.045 | +3.2e-4 | 0.323 |
| B-d0.35 | 54.980 | 58.312 | 54.929 | -0.142 | +2.4e-3 | 0.327 |
| B-d0.20 | 114.574 | none to 70 | - | - | - | 0.333 |
| A-d0.42 | 43.656 | none (guard 47.92) | 43.442 | -0.232 | -3.8e-2 | 0.090 |
| A-d0.40 | 46.415 | none (guard 50.66) | 46.103 | -0.331 | -4.6e-2 | 0.089 |
| C-R1.25 | 9.551 | (no status file) | 9.603 | +0.040 | -1.2e-4 | 1.868 |

- T1 HOLDS: every B member with delta_c >= 0.42 forms a persistent horizon (found in every
  search from its first detection on, no isolated finds before it); |ddet| 0.126 and 0.059 for
  1.0 and 0.7 (bound 0.2), 0.040, 0.043, 0.015 for 0.50-0.42 (bound 0.5); |dmmed| 3.8e-4 and
  1.9e-3 (bound 5e-3), 9.4e-3, 1.9e-3, 2.8e-3 (bound 1e-2; 0.50 is close to its bound).
- T2 HOLDS: no detection with particle proper time below 45 in 0.40, 0.35, 0.20 (earliest
  46.40 and 54.93); 0.40 and 0.35 form persistent horizons before tlim (coordinate 48.6 and
  58.3; 0.35 had 14 isolated finds between 57.3 and 58.3, all after proper time 54.9); 0.20 has
  none to t = 70 and its core edge has turned around (701 tracked core particles past their
  maximum radius) and is contracting at t = 70. The turnaround proper time of 0.20 is read 4.3 M
  late on average against the exact 55.57: the maximum of R(tau) is flat there and the
  three-record parabola is ill-conditioned [JUDGEMENT; not used for any verdict].
- T3 HOLDS: the code's bracket at t_end = 45 in the invariant measure equals the exact one,
  A_c(45) in (0.40, 0.42]: tau_det 43.686 (exact 43.656) and 46.402 (exact 46.415), both within
  0.05 of the exact values (bound 0.5).
- T4: mesh A finds no persistent horizon for 0.42 or 0.40, as written, but not for the reason I
  gave: A FOUND the horizon (three searches each, first at t = 45.625 with tau_det 43.44,
  ddet -0.23; and 48.375, ddet -0.33) and then both runs stopped at the guard (non-finite Z4c
  fields in whole MeshBlocks of level 4, first at (-0.44, -0.44, -1.44), 2.3 M after first
  detection; alpha_min jumped 0.26 -> 0.69 in the last step; 61,032 of 77,704 particles excised by
  then). My reason (about 4 cells across the horizon's coordinate radius cannot hold a horizon)
  is REFUTED; the prediction's outcome holds only because the runs died. The guard stop is a
  failed run; its cause is not named (no run has tested one). Mesh C half: C-d0.42 is still
  running (continued in place, entry 3), not judged.
- T5 PARTLY REFUTED: C-R1.25 dmmed -1.2e-4 against conv_ball C -2.1e-4 (within 1e-3, holds),
  but ddet +0.040 against +0.017, a difference of 0.024 > 0.02. The ball radius changes the
  finest-mesh first-detection time by more than predicted (conv_ball's mesh-B legs differ by
  -0.003 at R 1.25 and +0.040 at R 1.35; README of conv_ball).
- T6 PARTLY REFUTED: all eight B members ended at tlim without a guard stop; cost 0.30-0.33 s per
  cycle on mesh B (band 0.25-0.40, holds); C-R1.25 1.87 s (model 2.25). Refuted: (i) both A members
  stopped at the guard; (ii) the constraint ratio ||H||/||16 pi E|| over the mesh line outside
  the finder's radius is 0.11-0.21 at t = 0 and 0.3-3 during every run (largest 1.6-5.9 per
  member; threshold_series.json), never below 0.1 (panel d). The criterion of SCOPE section 3 was set without a
  measurement; the data's own t = 0 value already exceeds it (deposit noise of PCS clouds without
  filter against the table metric [JUDGEMENT]). Kept as written; the G2 package asks orch to rule.

Slice or finder (verify_bh's open point, [TO VERIFY] since batch 5): on the B members the finder's
m_irr at first detection equals the mass of the slice's own outermost marginally trapped sphere on
the mesh line (Misner-Sharp mass, 2m/R = 1 with K_T > 0) within 0.3-1.5 per cent (0.70: 3.4 per
cent), and both sit above the exact mass of the shell at their radius by up to 4-7 per cent at the
first detection of the threshold members and settle within 1 per cent within about 1 M (figure
slice_or_finder). So the first-detection excess is carried by the slice, not added by the finder
[VERIFIED for the B members, line outputs every 0.25 M; the line time is up to 0.25 M after the
finder's]. On mesh A the finder drifts 4-5 per cent below the line's mass after first detection.

## Entry 5, 2026-11-24 13:35Z: predictions G1-G3 for the A-mesh guard stop (processors, before the runs)

A-d0.42 (mesh A, M/16) stopped at the guard at t = 47.92, 2.3 M after its first detection
(entry 4). Its restart file at t = 44 (`A-d0.42/rst/ball.00011.rst`, 248 MB, 344 MeshBlocks of
8^3 cells) lets the processor build repeat the last 4 M cheaply (threaded release v0.6, 4
threads, tlim 48.5). Three runs from that restart:
- G1 repeat, deck as on the card: the guard stops the run at t = 47.9 +- 0.2 with non-finite
  Khat/A_ij in whole MeshBlocks [JUDGEMENT: the blow-up grows from the fields, not from card
  round-off]. Refuted by a run that reaches 48.5, or stops more than 0.2 away.
- G2 `z4c/lapse_leak = 0` from t = 44 (decision 0025 item 3 forbids the relaxation around an
  existing black hole; here it acts through and after horizon formation): if the relaxation
  term is the cause, G2 reaches 48.5. I expect it NOT to be the cause (lapse_leak x dt = 0.125,
  far below the bound 2.5 of periodic_diag U8/U9), so G2 stops like G1 [JUDGEMENT].
- G3 `particles/alpha_exc = 0.3` (particles excised earlier, before the lapse collapses
  steeply): if the abrupt excision near the horizon on the coarse mesh is the cause, G3 reaches
  48.5. I expect G3 to stop like G1 as well; the jump of excisions in the guard step (1,784
  particles) looks like a consequence of the non-finite lapse, not its cause [JUDGEMENT].
If all three stop at ~47.9, no named candidate is the cause and the line outputs of G1 (tab every
0.25) locate the growth; if G1 does not repeat, the card failure was not deterministic and the
A members are rerun on the card.

## Entry 6, 2026-11-24 13:45Z: prediction K for the constraint norms on three meshes (before the analysis)

G2 items C3 (constraints behave) and C12 (constraint norms against time) have no evidence yet.
`scripts/constraint_conv.py` reads the volume L2 norms of H and M (z4c history) and the cstat
mean |H| of conv_ball's A, B, C (delta_c = 1.5; one particle per finest cell on every mesh) and of
the threshold pair. Prediction K [JUDGEMENT]: before the horizon (t <= 10) ||H||_2 falls from A to
B to C, at an order between 0.5 and 2 (the metric error falls at second order, the deposit noise
per cell does not fall at fixed particles per cell); ||M||_2 likewise; the threshold members'
||H||_2 stays within a factor 3 of conv_ball B at equal mesh until their horizons form. Refuted by
a norm that grows from A to C at any t <= 8, or by an order below 0.3 at t = 8.

### Entry 6 outcome (run A-20261124-132249-2e6b5f2, fig_constraint_conv.png looked at): K REFUTED

||H||_2 does not fall with the mesh before t ~ 6: orders A->B, B->C are -0.09/-0.24 at t = 1,
-0.18/-0.13 at t = 2, -0.08/+0.01 at t = 4 (the norm grows slightly from A to C: refuted as written);
it falls only late, 0.47/0.46 at t = 8 and 0.04/0.76 at t = 10. ||M||_2 at t = 0 GROWS with the mesh
(12.5, 21.4, 39.1: order -0.8), then falls weakly (1.0/0.58 at t = 8). cstat mean |H| is flat to
t ~ 5 (2.05e-2 on all three at t = 2) and falls at order 0.35-0.5 from t = 8. The threshold
members' norms stay bounded (0.06-0.2) until their collapse, then jump at the horizon (interior
included). Reading [JUDGEMENT, to be tested]: at one particle per finest cell on every mesh, the
constraint norms are set by the deposit noise per cell, which does not fall with the mesh; the
truncation part shows only late. The test that can refute it is the particle-number leg at fixed
mesh (entry 7).

## Entry 7, 2026-11-24 13:50Z: prediction K2 (particle-number leg of the constraint norms, before the analysis)

conv_ball has A with 1, 8 and 64 times the particles (A, A-N8, A-N64) and B with 1 and 8 (B, B-N8).
K2: at fixed mesh, ||H||_2 and ||M||_2 at t = 1-6 fall with the particle number roughly as
N^(-1/2) (a factor 2-3.5 per factor 8) [JUDGEMENT: deposit noise]. Refuted if the factor per x8 is
below 1.5 at t = 2 and 4 on both meshes (then the noise is not the particles' and the constraint
floor has another cause).

### Entry 7 outcome (run A-20261124-132342-d5dc06e, fig_constraint_conv.png panel d looked at): K2 REFUTED

At fixed mesh the norms do not fall with the particle number before t ~ 6: the factor per x8
particles is 1.01-1.06 at t = 1, 1.02-1.10 at t = 2, 1.03-1.20 at t = 4 (A x1->x8, A x8->x64, B
x1->x8, for H and M), 1.08-1.38 at t = 6; only at t = 8 does it reach 2.2-3.3 (x1->x8; x8->x64
still 1.1). So the early constraint floor (t ~ 1-6) is neither mesh truncation (entry 6) nor
particle noise: it is fixed in physical space and does not fall with either resolution
[VERIFIED for these three meshes and three particle numbers]. Candidate, not tested: the
top-hat data's density jumps at R1 and R2 (data set 3 has unsmoothed edges; a jump gives a
constraint residual that refinement does not remove), with the momentum constraint at t = 0
GROWING with the mesh (order -0.8) as a jump would. The test that can refute it: the same member
with smoothed edges (prep_bh.py --edge-w) on two meshes. Not run this session.

## Entry 8, 2026-11-24 13:55Z: prediction T7 (C-d0.40, the late member on mesh C), before the run

Where the finite-duration threshold lies on each mesh, from tau_det interpolated linearly in delta_c
to 45 (entry 4 numbers): exact 0.4103; mesh B 0.4103 (43.686 at 0.42, 46.402 at 0.40); mesh A
0.4083 from the first detections of the guard-stopped members (43.442, 46.103). Mesh C has only
0.42 (running). Needs: the nestC lattice of delta_c = 0.40 (data run on processors, prep_scan.py
--only dc0p4C) and a C chain to t = 54 (about 9 card-hours; queue_b11 line 2).
T7: C-d0.40 forms no horizon before particle proper time 45 and a persistent one with tau_det =
46.415 +- 0.1 (B: -0.013); with C-d0.42 the interpolated threshold on C is 0.4103 +- 0.0005.
Refuted by a detection with proper time below 45, or tau_det outside the band.

## Entry 9, 2026-11-24 13:50Z: prediction K3 (where the early constraint floor sits), before the analysis

Entries 6-7 leave two candidates for the floor that falls with neither mesh nor particle number:
(a) the density jumps of the compensated top hat (core edge at rbar ~ 2.65, compensation edge
~ 3.88, matter edge 4.25 M); (b) the static refinement boundaries, fixed in physical space on every
mesh of the series (|x| = 1, 2, 4, 8, 16 M). conv_ball's C had its largest line |H| at t = 0 at
r = 1.016 (C_numbers.json of A-20261121-120257-a2eb839), next to the finest level's boundary.
K3 [JUDGEMENT]: on the x line of B-d0.42, A-d0.42, B-d1.00 and C-R1.25 (every line kept by
compare_tb), the location of the largest |H| for 0.5 <= t <= 6 lies within one local cell of a
refinement boundary in most outputs (b), not at the jumps (a). Refuted if most peaks sit within
0.1 M of the jump radii instead. The analysis cannot refute both; a peak elsewhere (e.g. the
centre) names neither.

### Entry 9 outcome (run A-20261124-134637-bd0d6eb, fig_hpeak.png looked at): K3 REFUTED, neither candidate

Of 23 line outputs per member in t 0.5-6, the largest |H| sits within 1.5 local cells of a
refinement boundary in 0-3 and within 0.1 M of a density jump in 0-3 (B-d0.42: 0 and 0; A-d0.42: 3
and 3; B-d1.00: 2 and 1; C-R1.25: 1 and 2). Before t ~ 2 the peak lies between the core edge and
the matter edge (x 1.5-3.9, mostly in the compensating shell), from t ~ 2.5 at the centre (x < 1.6). The
|H| profile is broad and noisy (1e-2 to 1e-1 over x < 5 at t ~ 2, ~1e-2 at t ~ 5) rather than
spiked at any radius. So the early floor is not localized at the refinement boundaries nor at the
jumps; its cause is not named. Next test that can name one: the floor's dependence on the time
step at fixed mesh and particles (cfl 0.25 against 0.125) and on the source options
(source_extrap off), one short card batch each to t = 6.

## Entry 10, 2026-11-24 14:00Z: prediction K4 (time step and source extrapolation), before the runs

Member A of conv_ball (data set 3, delta_c = 1.5, nest16_L16, one particle per finest cell),
release v0.6 processor build, t = 0 -> 6, three runs: K4-ref (deck as is, cfl 0.25), K4-dt
(cfl_number 0.125), K4-src (particles/source_extrap = false). Mesh refinement A->B->C halves the
step with the cell and left the floor unchanged (entry 6), so [JUDGEMENT]:
- K4a: K4-dt's ||H||_2 at t = 2, 3, 4, 5 within 10 per cent of K4-ref (the step alone is not the
  floor). Refuted by a change above 10 per cent.
- K4b: K4-src's within 10 per cent of K4-ref as well. Refuted by a change above 10 per cent (then
  the extrapolated source is implicated).
- K4c: K4-ref repeats conv_ball's card member A (A-20261121-075926-d10c2c1/A, core_gauge
  build) to within 5 per cent in ||H||_2 at t = 2-5 (different build and card vs processor).
If K4a and K4b hold, the floor is independent of mesh, particle number, step and source timing,
which points at the initial data or the gauge, the next two candidates.

### Note to entry 4 (run A-20261124-140131-48c636c, fig_threshold_interp.png looked at)

The threshold on each mesh by linear interpolation of tau_det to 45 (no prediction; arithmetic on
entry-4 numbers): mesh B 0.41033, exact 0.41026 (difference 7e-5); mesh A 0.40829 (from first
detections of the guard-stopped members, difference -2.0e-3). Card time of the eleven closed scan
runs and P0L (manifests at finish): 7.32 card-hours in all (B members 0.25-0.83 each, C-R1.25 2.02,
A batch 0.16, P0L 0.77).

### Entry 5, partial outcome (run A-20261124-132016-ecf12c3, still running when the pause flag was found at 06:18 PST)

- G1 HOLDS: the processor restart from t = 44 stops at the guard at exactly t = 47.921875, cycle 3067,
  first non-finite cell MeshBlock 31 (level 4) at (-0.4375, -0.4375, -1.4375), as on the card: the
  blow-up is deterministic in the fields, not card round-off [VERIFIED].
- G2 (lapse_leak = 0 from t = 44): stops at the guard too, but 0.5 M later (t = 48.42, cycle 3099) and
  first at another place (MeshBlock 79, level 5, (0.031, -0.219, -0.219), near the centre). The
  relaxation is not the cause of the blow-up; it moves it [JUDGEMENT]. My "stops like G1" holds
  for the stop, not for time and place.
- G3 (alpha_exc 0.3): running (t = 45.9 at 06:19); read `G3/athena.log` and `G3/ball.guard.txt`, then
  `harness/bin/nrpic-run finish A-20261124-132016-ecf12c3`.
Entry 10 (K4) was NOT started: the pause flag appeared first. Start it with
`harness/bin/nrpic-run submit --kind scouting --gate G2 --package tracks/A-emd-pbh/threshold_ball --launcher local --cores 6 --parent A-20261121-075356-1ad4c81 --purpose "threshold_ball K4 (entry 10)" -- bash tracks/A-emd-pbh/threshold_ball/scripts/k4_floor.sh '$NRPIC_RUN_DIR'`
then k4_compare.py on its directory (registered).

## Entry 11, 2026-11-25 03:55 PST (lead of batch 17): judging C-d0.42 (T4, mesh-C half), before the analysis

C-d0.42 = A-20261122-173202-f98c79f ended DONE at tlim 51 (chain events.log: segment 17, job 5216,
"finished: time=5.100000e+01 cycle=13056", 2026-11-24 14:39 PST; queue entry q0012 done); closed with
`nrpic-run finish` this session. Judged against entry 1 as written, nothing changed: BH = found in at
least three consecutive searches spanning at least 5 m_AH and in every later search (dispersal = no
such run of searches by tlim); T4 mesh-C half: |ddet(C)| <= |ddet(B)|/2 = 0.0075 M and |dmmed(C)| <=
|dmmed(B)|/2 = 1.4e-3 (B-d0.42: +0.015, +2.8e-3, entry 4); refuted by C not halving B's errors. Also
read, no bound set before: T1's bounds for 0.42 (|ddet| <= 0.5, |dmmed| <= 1e-2), T6 (end state,
guard, constraint ratio, cost against the C-R1.25 1.87 s per cycle). Seen before the analysis (raw
status file, no measure computed): the finder's first success on C is at coordinate t = 45.906 (B:
45.875) and 163 of 1119 searches succeed. Analysis: `scripts/analyse.py --member C-d0.42 --member
B-d0.42` (registered below). Mesh-C bracket: C-d0.42 alone gives only the upper end (tau_det < 45
or not); the lower end needs C-d0.40 (queue q0014, prediction T7 of entry 8).

### Entry 11, note before the common-window measurement (no prediction: the figures were seen first)

fig_threshold_slice_or_finder.png and C-d0.42_horizon.png of A-20261125-115027-17b419e (looked at)
show that dmmed is taken over different windows on the two meshes: the exact same-slice mass exists
only where the tracked particles cover the horizon's shells (C: t 46.1-47.2 and 50.9-51, inside the
first-detection transient; B: 47.1-47.2, 48.2-48.8, 50.5-51). `scripts/t4_common.py` measures on the
line times both meshes share after t = 46.75 (line Misner-Sharp mass against the exact shell mass)
and compares the finder masses of C and B directly. This is a measurement to replace a median over
unequal windows; it is not a test of T4, which stays judged as written.

### Entry 11 outcome (analysis A-20261125-115027-17b419e, common window A-20261125-115550-fe60ff1; fig_threshold_slice_or_finder.png, C-d0.42_horizon.png, fig_t4_common.png looked at)

(A-20261125-115530-a4f7dcd, the first run of t4_common.py, returned NaN for C and the spacing of
the finder rows instead of the search interval: a defect of the script, fixed and rerun; kept on record.)

| member | persistent from t | tau_det | ddet | dmmed (unequal windows) | line MOTS vs shell, t >= 46.75 (median abs) | search interval | s/cycle | cr_max |
|---|---|---|---|---|---|---|---|---|
| B-d0.42 | 45.875 | 43.686 | +0.0153 | +2.8e-3 (n 21) | 5.2e-3 (18 times) | 0.0625 | 0.324 | 1.56 |
| C-d0.42 | 45.906 | 43.705 | -0.0135 | +2.36e-2 (n 37) | 2.1e-3 (16 times) | 0.03125 | 2.198 | 1.94 |

- Outcome by the rule: C-d0.42 forms a BLACK HOLE (found in every one of the 163 searches from
  t = 45.906 to 51, no isolated finds before; 5.1 M of searches, more than 5 m_AH = 2.0). Its
  tau_det 43.705 < 45, so on mesh C the member 0.42 lies on the BH side at t_end = 45 as on B and in
  the exact solution: the upper end of the bracket holds on mesh C, A_c(45) <= 0.42 [VERIFIED]. The
  lower end on C needs C-d0.40 (not run).
- T4 mesh-C half REFUTED as written: |ddet(C)| = 0.0135 against the bound 0.0075 (|ddet(B)| = 0.0153;
  the sign flips), and dmmed(C) = +2.36e-2 against the bound 1.4e-3. Neither error halved.
  Reading [JUDGEMENT]: (i) ddet on B is already below one search interval in proper time (0.0625 in
  coordinate time between searches on B), so the prediction asked for a halving below the
  resolution of the measure; (ii) dmmed is a median over the times where the exact same-slice mass
  exists, which differ between the meshes (C: inside the first-detection transient, 46.1-47.2;
  B: later), so the two medians do not measure the same thing. On the times both meshes share after
  t = 46.75 the line MOTS mass against the exact shell mass is 2.1e-3 on C against 5.2e-3 on B
  (ratio 0.41, a factor 2.4) and the finder masses of C and B agree within 3.3e-3 (after 46.75; 1.4e-2
  at the transient near 46.3). This is a measurement made after the figures were seen, not a
  prediction that held.
- Also read: C's first detection carries a larger excess over the exact shell mass at its radius
  than B's (+11.6 per cent against +2.1 per cent; line MOTS at t = 46: 8.5 against 0.6 per cent),
  falling below 1 per cent by t = 46.75. The excess is in the slice, as on B (finder and line MOTS
  agree). Cause not named.
- T6 for C: DONE at tlim 51, no guard stop, 2.20 s per cycle (C-R1.25 1.87), constraint ratio up to
  1.94 (> 0.1, as every member: C3 stays FAIL).
- Slice measures do halve: core trapping dtau mean -0.096 on C against -0.209 on B; turnaround
  dtau mean -0.027 against -0.054 (compare logs of A-20261125-115027-17b419e).

### Entry 8, withdrawn before its run (2026-11-25 04:20 PST, lead of batch 17)

Queue entry q0014 (a-cd040, C-d0.40 on mesh C, 14 card-hours asked) is removed from the shared
queue unrun: no item of stage/G2/CHECKLIST.md waits for the lower end of the mesh-C bracket (C7
passes on conv_ball; the bracket on mesh B equals the exact one, entry 4; C-d0.42 holds the upper
end on C, entry 11). T7 stays on record as a prediction not tested. The data set dc0p4C
(A-20261124-133456-2d00507) is kept for a later bracket-convergence run (G3 if wanted).

### Entry 5, outcome of G3 and of the whole test (batch 17; analysis A-20261125-120158-b76bfe3, fig_guard_g123.png looked at)

- G3 (particles/alpha_exc = 0.3 from the t = 44 restart) REFUTES my expectation "stops like G1": it
  reaches tlim 48.5 without a guard stop ("Terminating on time limit", athena.log), 0.58 M past G1's
  stop (47.92) and past G2's (48.42). So excising the particles earlier, while the lapse is still 0.3,
  removes the blow-up on mesh A at least to t = 48.5 [VERIFIED for this one restart; whether it cures
  or only delays it is not known beyond 48.5]. The abrupt excision near the collapsing lapse is now a
  candidate cause of the guard stop that a run could have refuted and did not [JUDGEMENT].
- In none of the three variants is the horizon persistent on mesh A: found in 5 (G1), 6 (G2), 9 (G3) of
  32-36 searches after t = 44, intermittently, first at 45.625 in all; G3's last success is 47.75 and
  every later search fails ("iteration limit reached without convergence of the mass"). The masses of
  the successful searches FALL with time (G3: 0.389 at 45.75 to 0.363 at 47.75), which an apparent
  horizon's area should not do: on M/16 the finder does not hold the horizon even where the run stays
  finite (as entry 4 saw: 4-5 per cent drift below the line mass).
- Consequence for the scan: mesh A stays outside the threshold bracket (T4's A half holds only as
  "no persistent horizon"); a mesh-A rerun with alpha_exc 0.3 would not give a persistent horizon by
  this evidence. Not queued.

### Entry 10, started (batch 17, 2026-11-25 04:05 PST)

K4 runs as A-20261125-120525-8fb946e (processors, detached, 6 cores: three members of 2 threads, v0.6
threaded build, tlim 5 as in k4_floor.sh; entry 10 names t = 2-5). Predictions K4a-K4c stand as
written. Judge with `scripts/k4_compare.py` on its directory (registered) after
`harness/bin/nrpic-run finish A-20261125-120525-8fb946e`.

## Entry 12, 2026-11-25 07:10 PST (lead of batch 19): answers to the fresh verifier of C18, predictions before the analysis

The verifier (stage/G2/VERIFIER-C18.md) reproduces classification, detection times and the bracket and does
not reproduce the mass medians of B-d0.42, B-d0.40, B-d0.35, C-d0.42 and conv_ball A. Decision 0040 items 2-3:
answer with a registered analysis; read found / not found only from horizon_status_0.txt. Script
`scripts/c18_answer.py` (all 15 members): status-file searches and persistence, stale summary rows, the finder
mass against three exact masses on the slice (committed smoothed sign change "lead"; shell of the outermost
trapped tracked particle "last"; the next tracked particle outward "next"), ddet under four interpolations.
Predictions [JUDGEMENT], written before the run:
- P12a: every persistence time of the READMEs and every classification is reproduced from the status files,
  and every BH member is found in every status row from its persistence start. Refuted by one difference.
- P12b: the committed convention over the rows the committed analysis used reproduces every README median to
  2e-4 (the READMEs were written from it).
- P12c: the README medians lie inside the bracket [median vs next, median vs last] for every member (the
  committed sign change is interpolated between those two particles). Refuted by a README median outside it;
  the verifier reports exactly that for B-d0.42, B-d0.40, B-d0.35, so P12c is at risk.
- P12d: ddet spread across the four interpolations at first detection is below 0.04 M on B and up to 0.1 M on
  C-d0.42 (verifier 5e). Refuted by a spread outside that.

K4 (entry 10) is judged after this entry with `scripts/k4_compare.py`; predictions K4a-K4c stand as written.
Note on naming: decision 0039 item 2(c) calls K4 "the test of the smoothed edge". K4 is not that test: it
varies the time step and the source extrapolation on the unsmoothed top hat (entry 10). The smoothed-edge
test (entry 7's candidate) has not been run.

### Entry 12 outcome (analysis A-20261125-151126-7f79a83; fig_c18_mass_bracket.png looked at; first attempts A-20261125-150848-401a271 and A-20261125-150943-69ea256 failed on a member without a status file and in the figure, kept on record)

- P12a HOLDS: every classification and persistence time is reproduced from horizon_status_0.txt, and every BH
  member is found in every search from its persistence start (B-d1.00 ... B-d0.40 from their first find; B-d0.35
  first find 57.3125, 14 isolated finds, persistent from 58.3125; C-d0.42 163 of 936 unique searches, all from
  45.90625; entry 11's "1119" counted rows repeated by restarts). conv_ball A, B, C and C-R1.25 have no status
  file (made before `<fastflow> diagnostics`); their summaries contain no repeated rows. A-d0.42 and A-d0.40:
  3 finds each, 16 of 19 summary rows are repeats of the last surface.
- P12b HOLDS: the committed convention over the rows the committed analysis used reproduces every README median
  (to 1e-5). For A-d0.42 those rows were 17 of which 14 were repeats: its -3.8e-2 is withdrawn (true finds: the
  committed convention -2.1e-2; bracket [-2.6e-2, -0.8e-2]); A-d0.40's -4.6e-2 likewise (bracket [-4.5e-2, -2.7e-2]).
- P12c REFUTED: the README medians lie OUTSIDE the bracket [median vs next particle, median vs outermost trapped
  particle] for cb-A (7.4e-3 vs [5.1e-3, 7.2e-3]), B-d0.42 (+2.8e-3 vs [-5.6e-3, -0.5e-3]), B-d0.40 (+3.2e-4 vs
  [-9.6e-3, -3.7e-3]), B-d0.35 (+2.4e-3 vs [-7.7e-3, +0.5e-3]), C-d0.42 (+2.36e-2 vs [-4.2e-3, +5.9e-3]) and both A
  members. The running median of 9 places the trapped surface inside the outermost trapped tracked particle where
  tau_p - tau_AH is noisy (near threshold and in C-d0.42's first-detection transient), lowering the exact mass.
  My brackets agree with the verifier's to 6e-4 (B-d0.42 [-5.4e-3, -0.05e-3], C-d0.42 [-3.9e-3, +6.5e-3]): the
  verifier's numbers stand, the README's near-threshold medians do not. The bracket width (median 1.1e-3 to
  9.9e-3 relative) is the resolution of this diagnostic; READMEs corrected to the brackets.
- P12d REFUTED: the ddet spread over the interpolations at the first find is up to 0.27 M on B (B-d0.40, counting
  the two bracketing particles) and 0.12 M on C-d0.42; over the three interpolations alone 0.02-0.08 M on B,
  0.058 M on C-d0.42, 0.001 M on conv_ball C. conv_ball's ddet orders become 1.2-1.5 (A->B) and 1.75-2.1 (B->C).
- T4 (entry 11) stays FAILED as written: |ddet(C-d0.42)| = 0.0135 (v2), 0.0133, 0.044 against 0.0075 under every
  interpolation; its mass half cannot be judged (bracket width 9.7e-3 > bound 1.4e-3).
- Time measure: at B-d0.42's first detection (coordinate 45.875) the core edge reads 43.76 M, the finder radius
  43.69 M, the outer comoving layers 46.52 M (verifier 46.50). The threshold is stated in the core edge's proper
  time (= synchronous time of the exact solution); read in the outer layers' time the code's bracket would move
  to (0.42, 0.45]. CHECKLIST C1 now names this.

### Entry 10 outcome, K4 (run A-20261125-120525-8fb946e finished; analysis A-20261125-150851-5545f8e, fig_k4.png looked at)

- K4a HOLDS: ||H||_2 of K4-dt (cfl 0.125) within 0.2 per cent of K4-ref at t = 1-5 (ratios 1.000, 1.000, 0.998,
  0.998, 0.998).
- K4b HOLDS: K4-src (no source extrapolation) within 0.8 per cent (1.000, 0.999, 1.007, 1.000, 1.008).
- K4c HOLDS: K4-ref (processors, v0.6 threaded build) equals conv_ball's card member A to 1e-3 at t = 1-5.
- ||H||_2 rises from 2.2 at t = 0 to 11 at t = 0.25 and falls to 0.5-0.9 by t = 2-5 in all four; ||M||_2 falls
  from 12.5. The floor is independent of mesh (entry 6), particle number (entry 7), location (entry 9), time step
  and source timing (this entry) [VERIFIED on member A]. Remaining candidates named in entry 10: the initial data
  (the top hat's density jumps, whose residual does not fall with the mesh) or the gauge.
- K4 is NOT the smoothed-edge test that decision 0039 item 2(c) refers to; that test has not run. Item C3 stays
  FAILED as written. Next test (prediction to be written before it): data set 3 with smoothed edges (prep_bh.py
  --edge-w) on meshes A and B, initial slice and t <= 5 on processors, ratio of section 3 at t = 0 and the norms.

## Entry 13, 2026-11-25 08:05 PST (lead of batch 20): the smoothed-edge test for C3 (decision 0040 item 6), before any run

What `prep_bh.py --edge-w` smooths [VERIFIED, conv_ball/scripts/prep_bh.py lines 45-70, expball/expball/model.py
lines 120-150]: only the OUTER edge of the ball (the C^4 taper at R_b; data set 3 already has half width
w = 4.25 - 4.0816 = 0.168 M). The density jumps of the compensated top hat at R1 (core edge) and R2 (end of
the underdense shell) are untouched by it. A test of "the floor comes from the density jumps" therefore needs
the core profile smoothed as well: expball's SmoothTopHat (C-infinity step of Delta from R1 to R2). At
delta_c = 1.5 with R1 = 0.65 R_b and R2 = 0.95 R_b that profile needs negative density in the step (expball
raises); R1 = 0.40 R_b is admissible (lowest local contrast -0.896). prep_bh.py gets `--profile smooth_tophat`
(this session; no breaks are declared for it). Members (delta_c = 1.5, H R_b = 0.7, M = 1, one particle per
finest cell, decks nest16_L16 = mesh A and nest32_L16 = mesh B, core-v0.7 threaded processor build):
- W ("--edge-w" literally): data set 3's top hat with outer half width w = 0.918 M (rm = 5.0; jumps kept);
- S (smoothed): smooth_tophat, R1 = 0.40 R_b, R2 = 0.95 R_b, the same outer taper (rm = 5.0).
Runs: the t = 0 slices of W and S on A and B; S on A evolved to t = 5 (two threads; K4-ref took 6923 s to
t = 5, so this session reads t <= ~2 and the next one the rest); S on B evolved as far as two threads allow
(read at the end of this session; it may be continued). Reference top-hat numbers: K4-ref
(A-20261125-120525-8fb946e, mesh A, processors) and conv_ball's card member B (line ratio at t = 0: 0.22 on
A, 0.11-0.20 on B, verifier VERIFIER-C18.md).

Prediction C3S [JUDGEMENT; a jump in rho and K_L leaves an O(1) residual on a band one cell wide, whose L2
norm falls only as dx^(1/2) for H and grows as dx^(-1/2) for M; smooth data should converge at the scheme's
order where resolved]:
- (a) t = 0: the section-3 line ratio ||H||/||16 pi E|| of S is below 0.1 on A and on B and falls from A to B
  by a factor of at least 2. Refuted by a ratio >= 0.1 on either mesh, or a fall by less than 1.5.
- (b) t = 0: W's ratio stays within 25 per cent of the top hat's on the same mesh (the outer edge is not the
  floor). Refuted by W below 0.75 of the top hat's.
- (c) t = 0: the volume ||M||_2 of S falls from A to B (the top hat's grew at order -0.8, entry 6). Refuted by
  growth.
- (d) evolution on A: S's line ratio stays below 0.1 at every output read (t <= 5 when complete) and its
  ||H||_2 is below K4-ref's by a factor of at least 3 at t = 1 and 2. Refuted by a ratio >= 0.1 at any output
  or a factor below 3.
Consequences fixed now: if (a), (c) and (d) hold, the floor of the top-hat members is named as the density
jumps (on the outputs read), and the review is asked to judge G2's constraint item on smoothed members as
0039 item 2(c) says; if (a) or (d) fails, the floor is not the jumps, and C3 goes to the review with the
failure on record.

### Entry 13, amendment 08:12 PST (before any AthenaK run; the data run A-20261125-160221-b68396f FAILED)

The data run failed for both members: expball requires the core support inside the envelope, R2 <= R_b - w
(model.py line 317). So `--edge-w` on data set 3 (R2 = 0.95 R_b) is bounded by w <= 0.05 R_b = 0.204 M, against
0.168 M already: member W cannot be built, and prediction (b) is withdrawn untested (on record). Members now:
- S1: smooth_tophat, R1 = 0.40 R_b, R2 = 0.95 R_b, outer edge as data set 3 (rm = 4.25, w = 0.168 M): the inner
  jumps removed, the outer edge kept (on mesh A the edge at 4.25 M lies where cells are M/2, so w = 0.168 M is
  a third of a cell there, close to a jump);
- S2: smooth_tophat, R1 = 0.30 R_b, R2 = 0.80 R_b, outer half width w = 0.80 M (`--edge-w 0.8`, rm = 4.882):
  both smoothed (R1 = 0.40 with R2 = 0.80 needs negative density).
Predictions (a), (c) now apply to S2 (both edges smooth) and are stated for S1 as well; (d) applies to S2.
Added: (e) S1's t = 0 ratio lies between the top hat's and S2's; if S1 is as low as S2, the inner jumps carried
the floor, if S1 is as high as the top hat, the outer edge did. Refuted only in the sense that it names which.

### Entry 13, first outcome at t = 0 (data A-20261125-160436-462452d, runs A-20261125-160633-594a474 phase 1, analysis A-20261125-160849-8c01b54, fig_edge.png looked at)

Line ratio ||H||/||16 pi E|| at t = 0 (top hat / S1 / S2): mesh A 0.278 / 0.185 / 0.134; mesh B 0.174 / 0.146 / 0.116.
- (a) REFUTED: S2 (both edges smooth) stays above 0.1 on both meshes and falls from A to B by 1.15 only.
- (c) HOLDS, strongly: volume ||M||_2 of S2 falls from 3.64e-2 (A) to 6.1e-4 (B), a factor 60, while the top
  hat's grows (12.5 to 21.4); S1 (outer edge kept) 2.91 to 0.66. The momentum-constraint floor at t = 0 IS the
  jumps (inner and, above all, the outer edge) [VERIFIED on two meshes].
- (e) S1 lies between the top hat and S2 on both meshes: the inner jumps carry 0.09 of A's 0.278, the outer edge
  0.05, and 0.13 (A) / 0.12 (B) remain with smooth data.
- Volume ||H||_2 at t = 0: top hat 2.18 / 0.86 (A / B), S2 0.31 / 0.12: smoothing lowers it 7 times, and both fall
  by 2.5 from A to B.
- Where the remainder sits (panel c, t = 0, x line): |H| ~ 1e-8 inside the finest level (x < 0.9) on both meshes,
  a spike of ~1e-1 at the finest level's boundary (x = 1), and 1e-2 to 1e-1 on the levels of spacing >= M/8
  (x > 1 on A, x > 2 on B), for the top hat and for S1, S2 alike. Cause not named.
(d) waits for S2-A's evolution (running). S1-A's evolution is stopped by hand (PID 2597153, at its first cycles,
08:10 PST) to free one core for test D below; S1's t = 0 slices are kept.

### Entry 13, prediction D (before the runs): is the t = 0 remainder the deposit's or the metric's?

S2's slice on mesh A (nlim = 0) three more times: D-cic (deposit_shape = cic, no cloud compensation:
deposit_comp_c = deposit_comp_c2 = 0), D-pcs0 (pcs without compensation), D-ref (as S2-A0, a repeat).
[JUDGEMENT] If the remainder on the coarse levels is the deposit's (the cloud of one particle per local cell),
changing the cloud or switching off its compensation changes the line ratio by more than 30 per cent and |H| on
x in [1.2, 4] by more than a factor 2; if it is the metric side (table interpolation, finite differences of psi on
cells of M/8 to M/2), both stay within 10 per cent. D-ref repeats S2-A0 to 1e-12 (processors are reproducible).
Refuted (for the deposit reading) by changes below 10 per cent; neither reading named for 10-30 per cent.

### Entry 13, outcome of test D (run A-20261125-161039-cb046d7, fig_edge_d.png looked at): the deposit reading HOLDS

- D-ref repeats S2-A0 exactly (ratio 0.13381 both): processors reproducible, as predicted.
- D-cic (CIC, no compensation): line ratio 0.0064 at t = 0 (0.048 of S2-A0's 0.134); rms of H on x in [1.2, 4]
  0.052 of S2-A0's; inside the finest level |H| ~ 5e-10. D-pcs0 (PCS without compensation): ratio 0.089 (0.67),
  coarse rms 0.61. Both changes exceed 30 per cent: the remainder at t = 0 is the deposit's [VERIFIED, mesh A, t = 0].
- Where (panel b): the PCS deposit (with and without compensation) puts spikes into 16 pi E at the boundary of the
  finest level (x = 0.9-1.3: 0.33 to 0.61 against the smooth 0.44) and wiggles at x = 2 and 2.4; CIC is smooth
  there. Level boundaries sit at the same physical radii on every mesh of the series, which is why this part of
  the floor did not fall with the mesh (entry 6) or with the particle number (entry 7).
So at t = 0 the C3 floor is the density jumps of the top hat PLUS the PCS cloud at the refinement boundaries;
smooth data with a CIC cloud meet the bound by a factor 16 on mesh A. Whether that holds during the evolution is
test F.

### Entry 13, prediction F (before its runs): smooth data with the CIC cloud, evolved

S2 with `deposit_shape = cic`, `deposit_comp_c = deposit_comp_c2 = 0` (everything else as conv_ball's decks), meshes
A (to t = 5, one thread) and B (t = 0 slice, then to t = 1, two threads); S2-B with PCS (two threads, at cycle 0)
is stopped by hand to free its cores (PID 2597154, 08:12 PST); S2-A with PCS continues (the PCS twin of F on A).
[JUDGEMENT] F1: S2-cic's line ratio at t = 0 is below 0.02 on A and on B and falls from A to B. F2: on A it stays
below 0.1 at every output to t = 5, with ||H||_2 at t = 1 and 2 at least 3 times below K4-ref's and below the PCS
twin S2-A's. Refuted by a ratio >= 0.02 at t = 0, a rise from A to B, or any output >= 0.1 (F2). If F1 and F2 hold
(F2 is read by the next session), C3's floor is named: the top hat's jumps and the PCS cloud at level boundaries,
and the review is asked to judge C3 on smooth members with the CIC cloud (0039 item 2(c)); a change of the
deposit is then a request to the review, not a bound moved.

### Entry 13, outcome F1 (run A-20261125-161154-62ce3dc phase 1, analysis A-20261125-161248-eecc672, fig_edge.png looked at): HOLDS

S2 with the CIC cloud at t = 0: line ratio 6.36e-3 (A) and 5.78e-4 (B), a fall by 11 (order 3.5); volume ||H||_2
1.79e-3 to 1.09e-4 (16.4, order 4.0); volume ||M||_2 as with PCS (3.64e-2, 6.1e-4: the momentum constraint does not
see the cloud at t = 0). Smooth data with the CIC cloud meet the bound by factors 16 (A) and 170 (B) and converge
at fourth order at t = 0 [VERIFIED, two meshes]. F2 (evolution) runs: S2c-A to t = 5 (1 thread), S2c-B to t = 1
(2 threads), the PCS twin S2-A to t = 5 (2 threads); first reading of S2-A (PCS) to t = 0.25: ratio 0.134 -> 0.08,
volume ||H||_2 0.31 -> 0.7 (the top hat's goes 2.2 -> 12 in the same transient).
Judgement of C3 under decision 0039 item 2(c), as far as this session can: the floor of the top-hat members comes
from the density jumps and from the PCS deposit at the refinement boundaries, not from the evolution scheme
[VERIFIED at t = 0 on meshes A and B; F2 decides for t <= 5]. C3 stays FAILED as written for the members run so far.
If F2 holds, the review is asked to judge G2 on smooth members with the CIC cloud; the scan itself would have to be
rerun with them before G3 (the top-hat threshold scan carries the PCS floor).

### Entry 13, outcome F2 on mesh A so far (partial reading A-20261125-165215-e3fe168 of runs still going; fig_edge.png looked at): REFUTED

S2 with CIC on M/16 (S2c-A, read to t = 1.25): line ratio 0.0064 (t = 0), 0.050 (0.25), 0.098 (0.5), 0.097 (0.75),
0.129 (1.0), 0.156 (1.25): above 0.1 from t = 1. F2 is refuted on its first clause. Its other clauses hold so far:
volume ||H||_2 at t = 1 is 0.038, 57 times below K4-ref's (2.20) and half the PCS twin's (0.076). The PCS twin S2-A
rises to 0.53 at t = 4 (0.62 by 4.75), above the top hat's 0.39-0.45 there. So the evolution itself builds a
residual of order 0.1-0.6 of the source within one to five M on M/16, whatever the data and the cloud; the initial
data and the deposit set only the t = 0 value. Whether this part falls with the mesh is what S2c-B (M/32, to t = 1)
tells; it was at t = 0.08 when this was written. No cause is named for the growth.
C3 under 0039 item 2(c): the smoothed members do NOT meet the bound during the evolution on M/16; unless S2c-B shows
the violation falling with the mesh at a rate that would meet 0.1 on a mesh the track can run, the review decides
with the failure on record. "A violation that does not fall with the mesh is a defect to be explained": the
mesh leg (S2c-B) is the deciding run.
