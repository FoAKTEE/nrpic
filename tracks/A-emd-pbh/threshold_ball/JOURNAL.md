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
  the finder's radius is 0.12-0.21 at t = 0 and 0.3-3 during every run (largest 1.6-3.8 per
  member), never below 0.1 (panel d). The criterion of SCOPE section 3 was set without a
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
