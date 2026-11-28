# stage/G1/verifier-tail: second part of the fresh verification of G1 (F-hills)

Helper package of batch 34 (2026-11-27), processors only, 0 card-hours. It reruns the first
verifier's readers (`../verifier/scripts/`, unchanged) on the completed passage P1b (A + A2,
0-186.0 M) and reads, with readers of its own, what those do not: the finder's status files (from
133 M), the summaries' residual column, the chain's logs, the waves against retarded time. The
report is the dated second part of `../VERIFIER.md` (sections 10-17); predictions and outcomes
(PT1-PT21) are in `JOURNAL.md`.

## Contents

| Path | What |
|---|---|
| `scripts/vtail.py` | status reader (self-test on synthetic files with restart repeats and two kinds of failure), status against the summary signature, fates from trackers with the remnant mass, tracker overlaps by segment pair, (2,2) amplitude of rPsi4; figures fig_t_fates, fig_t_horizons, fig_t_waves_overlaps |
| `scripts/vbranch.py` | branches of the heavy finder (86.6 M to the capture, finding F1) and of finder 1 (160-179 M) by the summary's hrms and the status columns; (2,2) amplitude against u = t - r*; fig_t_branches |
| `scripts/vlogs.py` | A2's 46 segment logs: MeshBlocks at start and end, card-memory peak, exits, error lines |
| `scripts/vhrms.py` | accepted searches of A and A2 by residual class (hrms) before the capture; fig_t_hrms |
| `scripts/vf0.py` | finder 0 row by row around the capture (137-148 M) |
| `scripts/figstyle.py` | copy of `python/nrpic/figstyle.py` |
| `results/` | JSON outputs of the registered runs (vpassage, vmesh from part 1's readers; vtail, vbranch, vlogs, vhrms, vf0) |
| `figures/` | the seven figures I read (part 1's fig_v_passage and fig_v_horizons redrawn to 186 M; fig_t_*) |

## Results (registered runs; details in `../VERIFIER.md` sections 11-13, 17)

- **F-20261128-003721-95f3c15** (part 1's `run_all.sh`, unchanged): join 0-186.0 M, 77 files per
  tracker, no gap, overlaps up to 1.25e-9 M (A2-A2, 104 M); pair closest 2.1096 M at 76.37 M; c.o.m.
  minimum 4.525 M at 140.6 M; Newton identical to part 1; rms H at most 6.19e-5; every waveform
  sample to 186 M.
- **F-20261128-004301-ce51e1f** (vtail): m1 within 1 M of M from 138.33 M; common horizon of M and
  m1 from 137.5 M (1.12015 -> 1.1228, chi 0.253 at 186 M); m2 passes at 8.733 M (134.31 M), 17.53 M
  at 186 M, energy marginal and not conserved; the summary signature equals the status found flag
  at all 3 x 1697 searches.
- **F-20261128-004549-2a094fb** (vbranch): F1 decided for 86.6-131 M by hrms (upper branch 1.00422 at
  1e-8, lower branches and part 1's decline at 1e-4); finder 1 at 160-179 M finds a branch with hrms
  0.15-0.23 after 6 flow iterations (finding F5); waves rise from u = 95-97 M at 40, 48, 70 M.
- **F-20261128-004718-796bd33** (vlogs): MeshBlocks 1968-2514, memory peak 78789 MiB, exits 0/143.
- **F-20261128-004800-5f93427** (vhrms): member finders accept 3.8-29 percent of searches with hrms
  above 1e-2 before the capture; the heavy finder none before 136.9 M.
- **F-20261128-005105-f29eb5a** (vf0): finder 0's found surfaces to 141.09 M have small mean
  expansion but hrms 2e-3 to 7.5e-2 (corrects part 2's section 12, see section 17).
- Verdicts: C8 met in substance (186 M against the criterion's 200 M to be stated); A2-3, A2-4 and
  A2-5's heavy clause refuted, A2-5's member, mesh and constraint clauses met; A2-1, A2-2 stay
  refuted.

## How to rerun (from `/data/haiyangw/nrpic/wt/F-hills`, each about a minute on one core)

```
harness/bin/nrpic-run submit --kind scouting --gate G1 --cores 1 \
  --package tracks/F-hills/stage/G1/verifier-tail --purpose "..." \
  -- bash tracks/F-hills/stage/G1/verifier/scripts/run_all.sh '$NRPIC_RUN_DIR'
# then, the same way:
#   -- python tracks/F-hills/stage/G1/verifier-tail/scripts/vtail.py --out '$NRPIC_RUN_DIR'
#   -- python tracks/F-hills/stage/G1/verifier-tail/scripts/vbranch.py --vtail <vtail.json of the run above> --out '$NRPIC_RUN_DIR'
#   -- python tracks/F-hills/stage/G1/verifier-tail/scripts/vlogs.py --out '$NRPIC_RUN_DIR'
#   -- python tracks/F-hills/stage/G1/verifier-tail/scripts/vhrms.py --out '$NRPIC_RUN_DIR'
#   -- python tracks/F-hills/stage/G1/verifier-tail/scripts/vf0.py --out '$NRPIC_RUN_DIR'
```

The readers take the run directories of A (F-20261121-203144-b2cf16b) and A2
(F-20261124-210400-902c650) from `vtail.py` (`RUN_A`, `RUN_A2`).

## Not done

Criteria (i) and (ii) (F-pre-1 against 0911.1136, 1804.02911; F-pre-2 against 2404.16270 and the
Kerr part), EIH, P1's spin and radiated energy, junk at P1b's spheres, the energy radiated in P1b
(the record ends before the capture's signal passes r >= 48 M), C25 and D34 item by item, and a
polished-finder test of F1 and F5 on A2's restart files (needs a run; not mine to queue).

## Requests

- To the lead (F-hills), from `../VERIFIER.md` sections 16-17: state 186.0 M against criterion
  (iv)'s 200 M and leave its acceptance to the orchestrator; state m2's fate as undecided; quote
  the heavy hole on the converged (upper, low-hrms) branch, 1.00422, and say part 1's decline and
  the lower branches are unconverged; flag accepted searches with hrms above 1e-2 in the member
  drifts and m2's unconverged branch at 160-179 M; "1.55e-3 by 133 M" -> "by about 135 M";
  give the source of "MeshBlocks 2584" (the segment logs give 2514 at most); say that the capture's
  wave is recorded only at r = 40 M and without ring-down.
- To core: the status file marks as found a surface accepted after 6 flow iterations with an
  expansion residual (hrms) of 0.15-0.23 (A2, finder 1, 160.6-179.2 M; card build core-v0.5, no
  polishing). Say whether `polish_iterations_<n>` of core-v0.8 removes it on this case, or record
  the case in `coord/INTERFACES/finder_stop.md`.
- To the orchestrator (through the lead): whether criterion (iv)'s "trackers until t = 200 M" is
  met by a record that ends at 186.0 M.
