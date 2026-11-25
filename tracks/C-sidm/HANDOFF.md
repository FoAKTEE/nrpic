# HANDOFF of C-sidm

For a reader with no memory of the last session. That session was the batch-17 lead session of
2026-11-25 (11:46-12:45 UTC): it closed and read the two queue runs N6c and M16, changed the
queue, and updated stage/G2.

State in three lines:
1. G0 and G1 are signed. G2 is open and NOT ready for a verifier: 7 of 20 items pass, 4 fail
   (C1, C2, C7, C9), 9 open; `stage/G2/OPEN.md` maps every missing item to a queue entry.
2. N6c (C-20261124-221122-928c9eb): the collisionless control of the threshold model
   (King b = 1, y0 = 0.334032) on M/8 holds 600 M at N = 1e6, where at N = 1e5 it collapsed at
   534.8 M: particle-noise relaxation (NS.1 held, NS.2 failed; C-20261125-122010-fb3cc08). So
   the threshold is read at N = 1e6; the bracket y0 = 0.324 / 0.344 is queued.
3. M16 (C-20261125-044843-2d048b6): collisional t_c 158.42 M on M/16 (163.41 on M/8, 206.64 on
   M/4; C-20261125-122020-031b67e). Predictions of the queued runs: JOURNAL 2026-11-25T11:56Z
   (B17.4) and 12:01Z (B17.5, B17.6); B17.1-B17.3 were withdrawn unqueued.

Owner: C-sidm. Branch: `track/C-sidm`. Worktree: `/data/haiyangw/nrpic/wt/C-sidm`.
Start with:
`cd /data/haiyangw/nrpic/wt/C-sidm && git merge --no-edit main && git status --short && harness/bin/nrpic-ctx inbox && harness/bin/nrpic-queue list --owner C-sidm && squeue -u $USER -o '%i %j %T %M' && test -e /data/haiyangw/nrpic/locks/PAUSE && echo PAUSED`

## Card runs: the shared queue (harness/RULES.md "Shared card queue")

- Card runs reach Slurm only through `harness/bin/nrpic-queue add` (decision 0033). Every entry
  runs `tracks/C-sidm/longruns/seq/qitem.sh <item>` (parameters in `longruns/seq/queue.txt`).
- When an entry shows `done`, close its run: `tracks/C-sidm/longruns/seq/qitem.sh close <run_id>`
  (it takes minutes: the restart files of a 600 M run are 60 GB and are checksummed). For a run
  that was continued in place this FAILS now (`nrpic-run finish` refuses a manifest with a
  `continuations` field): close it by hand (status, exit_code, ended, outputs in the manifest;
  commit) until the harness is fixed (asked of orch).
- Decks of batch 17 stay on the core-v0.6 card build (qitem.sh EXE) without `dt_gauge`, for
  series continuity with their controls (ruling asked).

## Runs still to run, and what reads them

| Queue id | Label | Prio | Item / run id | Read with | Predictions |
|---|---|---|---|---|---|
| q0046 | N6b344 | 2 | new: y0 0.344 kicked in, N = 1e6, M/8, 600 M | `longruns/scripts/nseries.py` (labels N1e6 etc.; add N6c as control) and `xcheck_b11.py` | B17.5 |
| q0047 | N6b324 | 2 | new: y0 0.324 kicked in, N = 1e6, M/8, 600 M | as above | B17.6 |
| q0048 | D2eta1 | 2 | new: D2 f = 2 seed 1 with shift_eta 1.0, 220 M | `d2_analysis.py` with label eta1 beside the M/8 runs | B17.4 |
| q0018 | N4c | 2 | new: N = 1e4 control of y0 0.334032, 600 M | `nseries.py` with N1e4, N1e5, N1e6 | NS.3 |
| q0022 | A334s2c-cont | 5 | C-20261124-053105-2fcc8af from about 249 M | blockA_delta.py; nseries.py | control t_c scatter at N = 1e5 |
| q0023 | A334s3c-cont | 5 | C-20261124-082221-7f03a8e from about 28 M | as above | as above |
| q0024 | D2f2s2-cont | 5 | C-20261124-035054-c06503f from about 116 M | d2_analysis.py | D2.3 seed pair; judges the M/8 -> M/16 shift |

Removed in batch 17 (serve no G2 item once the threshold is read at N = 1e6): q0019-q0021,
q0025-q0027 (kicked N = 1e5 continuations). Not in the queue but owed: A324s1c+
(C-20261123-032324-938ecbd) DONE at 600 M, to be closed by hand and read with blockA_delta.py
(an unregistered look shows the y0 = 0.324 control at N = 1e5 crossing alpha_min 0.3 at about
600 M [TO VERIFY]).

## Next, in order

1. When q0046/q0047 end: close, run nseries.py with the bracket and N6c, look at the figure,
   judge B17.5/B17.6 in the journal. If both hold, C7/C9 are met at one mesh and one N.
2. Close A324s1c+ by hand; rerun blockA_delta.py on all 15 block A runs (complete windows).
3. The convergence legs of the bracket (M/16 at N = 1e6, a gauge variant): predictions first,
   then queue them if orch grants card-hours (outbox 20261125T122226Z); then figures, note
   sections and a G2 verifier (OPEN.md lists what it must cover).

## Packages still in progress (none has uncommitted files)

- longruns: the queue above. models: paused since 2026-11-20. threshold_scan: block A done at
  N = 1e5 (unfit); the scan moves to N = 1e6. decisive: D2 read with M/16; seed pair pending.

## Traps

- Commit with explicit paths (`git commit -- <paths>`), never `git add -A`; nrpic-run and
  qitem.sh commit manifests (wait while `/data/haiyangw/nrpic/.git/worktrees/C-sidm/index.lock`
  exists). `nrpic-run submit` refuses while tracked files of the track are modified: commit first.
- History of a run continued in place: later rows replace earlier ones from their first time
  on (all readers of longruns/scripts do this).
- Card runs with deposition are not byte-reproducible; read effects against controls.
- `nrpic-stage verify` was run with `--no-checksums` (the full pass would hash several TB of
  restart files).
- Never kill by pattern; at most 6 cores; temporary files in scratch/C-sidm/tmp/.
