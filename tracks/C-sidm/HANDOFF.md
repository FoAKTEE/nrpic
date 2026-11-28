# HANDOFF of C-sidm

For a reader with no memory of the last session. That session was the batch-35 lead session of
2026-11-28 (01:55-02:30 UTC): it recorded G2 as signed, applied the gate review's corrections,
wrote the G3 scope, made the first-step decks and queued six card runs.

State in three lines:
1. G0, G1, G2 signed (coord/GATES.md; G2 pass with reservations, decision 0048 item 1). Working
   toward G3 with 80 card-hours. The G3 scope is `scope/SCOPE_G3.md`; it needs an independent
   review before any production run (requested from orch, outbox 2026-11-28).
2. First step of G3 (decision 0048): the b = 0.1 thermal-core bracket at N = 1e6 with the horizon
   finder; step 1a (four members, seed 1, mesh M/8) is queued. Nothing else of G3 runs before 1a
   is read.
3. The conductivity runs heat_C1/heat_C2 are rerun on core-v0.8 (their v0.6 snapshots were
   deleted by the old reduction); the reduction now writes into its own run directory.

Owner: C-sidm. Branch: `track/C-sidm`. Worktree: `/data/haiyangw/nrpic/wt/C-sidm`.
Start with:
`cd /data/haiyangw/nrpic/wt/C-sidm && git merge --no-edit main && git status --short && harness/bin/nrpic-ctx inbox && harness/bin/nrpic-queue list --owner C-sidm && test -e /data/haiyangw/nrpic/locks/PAUSE && echo PAUSED`

## Queued or running when the session ended (all priority 2, release card build core-v0.8)

| Queue id | Label | Run id when dispatched | Deck / list | Read with | Predictions |
|---|---|---|---|---|---|
| q0092 | heat_C1r | C-20261128-021624-9c11a74 (job 5567) | `longruns/inputs/heat_C1.list` (batch) | `heat/scripts/run_mode.py reduce <card run dir> --prep /data/haiyangw/nrpic/scratch/C-sidm/C-20261121-202552-883e2c2 --out '$NRPIC_RUN_DIR' --nproc 4` (registered), then `longruns/scripts/heat_series.py --out '$NRPIC_RUN_DIR' --noise C-20261120-223001-eb81eb7 --group T7_th0.003_e0.2 <reduction id C1> <reduction id C2>` | HR.0-HR.5, JOURNAL 2026-11-28T01:59Z |
| q0093 | heat_C2r | (waiting) | `longruns/inputs/heat_C2.list` | same | same |
| q0096 | G3A-C | (waiting) | `longruns/inputs/G3A_tmb01_Z0p5404_N1e6_s1_ctrl.athinput` (chain) | `longruns/scripts/nseries.py` (lapse, 20 M block means; as in RERUN.md section 2) plus `cc.horizon_status_0.txt` / `cc.horizon_summary_0.txt` of the run (H1 of the scope) | G3A.1-G3A.7, JOURNAL 2026-11-28T02:12Z |
| q0097 | G3A-56 | (waiting) | `G3A_tmb01_Z0p5600_N1e6_s1_kin` | same | same |
| q0098 | G3A-52 | (waiting) | `G3A_tmb01_Z0p5200_N1e6_s1_kin` | same | same |
| q0099 | G3A-60 | (waiting) | `G3A_tmb01_Z0p6000_N1e6_s1_kin` | same | same |

Before reading a finished entry: `sacct -j <job>` must say COMPLETED (the queue's known defect:
a preempted batch job can be listed as done); then `harness/bin/nrpic-run finish <run_id>`.
The G3A chains reserve 4 card-hours each (4 segments); if a chain runs out of segments, continue
it in place from its restart file (a `--cmd` wrapper as `longruns/seq/qitem.sh` resume does, but
with the core-v0.8 exe; qitem.sh itself is hard-wired to core-v0.6 and gate G2: do not use it for
G3 runs).

## Next, in order

1. Read q0092/q0093 (above); judge HR.0-HR.5; if HR.2 holds, the conductivity 1.020 +- 0.004 has
   a repeat with verifiable raw data; update OPEN.md of G2 and EVIDENCE.md.
2. Read q0096-q0099; judge G3A.1-G3A.7 and F1-F3; write predictions, then queue 1b (seeds 2, 3
   of the two members next to the threshold), 1c (M/16) and 1c' (M/4) per SCOPE_G3 section 2a.
   Seeds 2 and 3: `make_ic_seeds.py --maker models --seeds 2 3 --N 1000000 --tag <tag>`; decks
   need a variant of make_decks_g3a.py (seed and mesh arguments). Smoke-test every new deck
   (`longruns/scripts/smoke_g3a.sh`): the finder must write `cc.horizon_status_0.txt`.
3. Monoenergetic bracket (SCOPE_G3 2b): deck generator from `python/nrpic/st_cluster.py` tables
   still to write.
4. G2 leftovers (need one registered note run): the bracket legs' constraint histories in a
   package figure; `note/scripts/schem_ladder.py` labels "turning-point model" -> "model at the
   binding-energy maximum".

## Packages

- longruns: G2 complete; G3A decks and scripts (`make_decks_g3a.py`, `smoke_g3a.sh`) added.
- heat: `run_mode.py reduce` now requires `--out` and deletes nothing.
- scope: `SCOPE.md` G2 clause amended 2026-11-27 (decision 0048); `SCOPE_G3.md` new.
- note: wording corrected (binding-energy maximum; bracket not a converged location; finite-N
  controls; gauge leg = shift damping only); compiled, 19 pages, main.pdf 1.5 MB.

## Traps

- The finder: `<fastflow> num_horizons = 1` AND `start_time_0`, `stop_time_0` are needed (the
  defaults never search: z4c/fastflow.cpp:177-179, 286). `flow = shear` is one key for all
  horizons.
- Commit with explicit paths (`git commit -- <paths>`), never `git add -A`; nrpic-run commits
  manifests itself (wait while `/data/haiyangw/nrpic/.git/worktrees/C-sidm/index.lock` exists).
- History of a run continued in place: later rows replace earlier ones from their first time on
  (nseries.py does this; common.read_hist does not).
- The note forbids numbers in main-text prose and the checker's --forbid words (note/README.md).
- `nrpic-stage report` keeps the "Decision requested" text unless `--decision` is given.
- Never kill by pattern; at most 6 cores; temporary files in scratch/C-sidm/tmp/.
