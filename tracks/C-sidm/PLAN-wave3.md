# PLAN of C-sidm for wave 3

Written by the planner of each round (decision 0019 item 3). Each round adds a section; the
helpers' briefs are the tasks the workflow hands out, summarised here.

## Round 1 (2026-11-20, planner; worktree at 8cf2c965 after merging main d507d77)

Pause flag absent at 22:08 UTC (weekly usage 51 per cent, `locks/usage.json`).

### State found

- G0: package complete for the orchestrator's review since wave 2b (`stage/G0/OPEN.md`);
  not yet signed in `coord/GATES.md`.
- G1: NOT MET. Open items of `stage/G1/CHECKLIST.md`: C2 (growth-rate fit not validated
  on runs), C6 (heat conduction T6-T8 of C-pre-1), C9 and C10 (schematics), C14 (one
  script per G1 figure), C16 (working note without G1 results), C17 (fresh verifier of the
  G1 material).
- The heat package (wave 3a helper) was cut off by the usage limit on 2026-11-19. What
  exists: references, predictions, processor results T6(a), T6(b), T6(c), T7 at
  theta = 0.003 (kappa/kappa_1 = 1.019 +- 0.004, analysis C-20261119-161930-acd257b), the
  collisionless check, T8 part 2 (`heat/README.md`). Stranded: card jobs A and B (runs
  C-20261119-150335-73fd40f, C-20261119-150347-e100007; Slurm 4652, 4653) COMPLETED on
  2026-11-19 with every case rc = 0 (`batch.list.status`) but were never reduced or closed
  (manifests "submitted", 51 GB and 42 GB of snapshots); the processor run
  C-20261119-155433-a287f9c ended with exit 0 at 17:09 UTC (its `run.log`) but its
  manifest says "running"; the T8 processor runs (C-20261119-154032-e450dfc,
  -162015-d97abac, -162353-7985a9a) and T7 at theta = 0.1 and 1 were never analysed.
- Card executable of core/collisions-2: core's journal (`git show
  core/collisions-2:tracks/core/JOURNAL-coll2.md`, entry 2026-11-19 14:30 UTC, part D)
  traces the FAIL lines of `CARD_TESTS.log` to rounding (same pairs tested and accepted in
  every step, momenta within 2.1e-14); core's wave-3 session analyses the 150 M cluster
  job (run core-20261119-143232-4d1e995) today. Not merged into a release yet (no
  `core_nrpic_v04`, no tag beyond core-v0.3).
- Slurm: no job of the owner queued or running (`squeue`, 22:01 UTC). Budget (`nrpic-run
  budget`): G2 used 1.73, reserved 1.84 (the heat jobs; actual allocation 0.52), left
  41.43 of 45.
- Inbox: three info messages (kb locators applied, kb snapshot a782f1e, core's threaded
  processor build); none needs an answer from a helper. No answer from core to the four
  requests of 2026-11-19 (ADM energy diagnostic, refined mesh with collisions and
  non-finite stop, format findings, card tests). `core/mpi` does not run collisions on
  several ranks (its READY), so the MPI variant of T10 cannot run yet.
- git status clean: no stranded files.

### Gate aimed at

G1 (all open checklist items: packages 1 to 4), with the long card work of G2 started in
parallel (packages 5 and 6), because card time is the slow resource and the questions
they answer (defect, seed scatter, mesh drift) gate the G2 scan of `threshold_scan/SCAN.md`.

### Packages

| # | Key (directory) | Goal | Deliverables | Why now | Card cap |
|---|---|---|---|---|---|
| 1 | `heat` | close T6-T8 (G1 C6) from the finished runs | stranded runs closed; card jobs A and B reduced and closed; T8 (processor and card), T7 at eps 0.05, T7 at theta 0.1 and 1, card-processor consistency analysed with predictions first; JOURNAL outcomes; README results and a verdict for C6 | the only blocker of C6; the data exist and wait | 0 |
| 2 | `models` | growth-rate fit fixed and validated on runs (G1 C2) | `growth.py` with the fix of diagnosis D1; tests G1-G6 rerun; validation on the first paper's runs and a reading of the wave-2 cluster runs; JOURNAL, README, figures | C2 is open and the G2 scan's analysis depends on it | 0 |
| 3 | `note` | working note with the G1 results (C9, C10, C14, C16) | updated architecture schematic, new data-flow diagram, one script per G1 data figure from registered runs, G1 sections and ledger, checker passed with --compile, pages read | four checklist items; the material is complete enough | 0 |
| 4 | `verify_g1` | fresh-context verifier of the G1 material (C17) | blind verdicts recomputed from run outputs with own code (heat, rate and conservation, T12, thresholds and onsets), then `stage/G1/VERIFIER.md` comparing with the claims | decision 0016 item 4; new results carry the gate | 0 |
| 5 | `decisive` | runs D1 (operator defect, seed scatter) and D3 (stable King model) of `stage/REVIEW-wave2.md` section 7 | decks, predictions, card runs, analysis of collapse against controls, JOURNAL, README | the reading of every collisional run depends on them; prerequisite (core's reading of the card executable) exists, with a go/no-go rule | 3.0 |
| 6 | `drift` | origin of the outward excursion of the collisionless controls (RISKS 3) | processor analysis of the wave-2 controls, M/8 controls, continuations to 1000 M (SCAN.md block A'), recommendation for the scan's mesh | decides the mesh of the G2 scan (9.5 card-hours) before it is spent | 3.0 |

Card total 6.0 card-hours of the 41.4 left (decisions 0014, 0016); packages 5 and 6 each
hold at most one job in the queue, so the owner never has more than two. Processors: heat
4 cores, every other package 2 (14 of the owner's 16; at most 6 per session).

Not planned this round (round 2 or the lead): repeats of T3-T5, T9, T11 with
`coll_energy = particle` (cheap, processors); T10b for T4; the MPI variant of T10 (needs
collisions on several ranks in core); D2 with collisions (after D1 and package 6); the
G2 scan blocks A-D (after packages 2, 5, 6); the G0 gate review (the round's reviewer).

### Commits

Helpers commit only their own paths (`git add <paths>` and `git commit -m ... -- <paths>`,
never `git add -A`; retry while `/data/haiyangw/nrpic/.git/worktrees/C-sidm/index.lock`
exists) and push `track/C-sidm`; none of them merges main.
