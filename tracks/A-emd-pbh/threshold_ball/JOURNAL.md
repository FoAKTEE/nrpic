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
