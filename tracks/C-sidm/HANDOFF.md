# HANDOFF of C-sidm

For a reader with no memory of the last session. That session was the batch-20 lead session of
2026-11-25 (15:54-16:30 UTC, processors only): it closed block A, rechecked every collapse time
of the G2 package against horizon files (decision 0040 item 3), and queued the mesh and gauge
legs of the N = 1e6 bracket (ruling 0039 item 3).

State in three lines:
1. G0 and G1 are signed. G2 is open and NOT ready for a verifier: 7 of 20 items pass, 4 fail
   (C1, C2, C7, C9), 9 open; `stage/G2/OPEN.md` maps every missing item to a queue entry.
2. Block A at N = 1e5 on M/8 is closed (C-20261125-160056-a5b7282): all three controls collapse
   (534.8, 549.3, 599.99 M); the kin members still bracket y_max (0.344 at 229.79 M; 0.324 holds
   600 M). The threshold is read at N = 1e6, where the control N6c holds 600 M.
3. No run of C-sidm ever had the horizon finder (C-20261125-160207-05b6db1): every t_c is the
   alpha_min = 0.3 lapse marker; say so beside each number.

Owner: C-sidm. Branch: `track/C-sidm`. Worktree: `/data/haiyangw/nrpic/wt/C-sidm`.
Start with:
`cd /data/haiyangw/nrpic/wt/C-sidm && git merge --no-edit main && git status --short && harness/bin/nrpic-ctx inbox && harness/bin/nrpic-queue list --owner C-sidm && squeue -u $USER -o '%i %j %T %M' && test -e /data/haiyangw/nrpic/locks/PAUSE && echo PAUSED`

## Card runs: the shared queue (harness/RULES.md "Shared card queue")

- Card runs reach Slurm only through `harness/bin/nrpic-queue add` (decision 0033). Every entry
  runs `tracks/C-sidm/longruns/seq/qitem.sh <item>` (parameters in `longruns/seq/queue.txt`).
  The track must be committed (clean) when the dispatcher runs an entry: nrpic-run refuses a
  dirty tree.
- When an entry shows `done`, close its run with `harness/bin/nrpic-run finish <run_id>` (it
  now accepts runs continued in place; `qitem.sh close` still passes `--status`, avoid it for
  continued runs). Closing a 600 M run hashes about 70 GB (5 min for A324s1c+).
- All decks stay on the core-v0.6 card build without `dt_gauge`, cfl_number 0.25 (ruling 0039
  item 3: members on the executable and step rule of their control).

## Runs still to run, and what reads them

| Queue id | Label | Prio | Item / run id | Read with | Predictions |
|---|---|---|---|---|---|
| q0046 | N6b344 | 2 | y0 0.344 kicked in, N = 1e6, M/8, 600 M | `longruns/scripts/nseries.py` (add N6c as control) and `xcheck_b11.py` | B17.5 |
| q0047 | N6b324 | 2 | y0 0.324 kicked in, N = 1e6, M/8, 600 M | as above | B17.6 |
| q0055 | A16b344 | 2 | y0 0.344 kin, N = 1e6, M/16 (|x| < 1.95 M), 600 M | nseries.py beside N6b344 | B20.2 |
| q0057 | A16b324 | 2 | y0 0.324 kin, N = 1e6, M/16, 600 M | nseries.py beside N6b324 | B20.1 |
| q0056 | N6b344e1 | 2 | y0 0.344 kin, N = 1e6, M/8, shift_eta 1.0 | nseries.py beside N6b344 | B20.3 |
| q0058 | N6b324e1 | 2 | y0 0.324 kin, N = 1e6, M/8, shift_eta 1.0 | nseries.py beside N6b324 | B20.3 |
| q0048 | D2eta1 | 2 | D2 f = 2 seed 1 with shift_eta 1.0, 220 M | `d2_analysis.py` with label eta1 | B17.4 |
| q0018 | N4c | 2 | N = 1e4 control of y0 0.334032, 600 M; run C-20261125-132112-edf3fbc, Slurm job 5297 pending | `nseries.py` with N1e4, N1e5, N1e6 | NS.3 |
| q0022 | A334s2c-cont | 5 | C-20261124-053105-2fcc8af from 249 M | blockA_delta.py; nseries.py | seed scatter at N = 1e5 |
| q0023 | A334s3c-cont | 5 | C-20261124-082221-7f03a8e from t = 0 (its only restart file is the t = 0 one; four earlier segments each restarted at 0) | as above | as above |
| q0024 | D2f2s2-cont | 5 | C-20261124-035054-c06503f from about 116 M | d2_analysis.py | D2.3 seed pair |

Predictions: JOURNAL 2026-11-25T11:56Z (B17.4), 12:01Z (B17.5, B17.6), 16:02Z (B20.1-B20.3),
2026-11-24T13:14Z (NS.3). Cost of the legs [JUDGEMENT]: 6.5 card-hours per M/16 member, 2.7 per
gauge member; watch the first M/16 member's real cost (RISKS row 5).

## Next, in order

1. When q0046/q0047 end: close, run nseries.py with the bracket and N6c, look at the figure,
   judge B17.5/B17.6 in the journal.
2. When the legs end: the same against B20.1-B20.3; then C2/C7/C9 can be judged as a bracket of
   +-3 per cent on two meshes, two gauges and two N (the N = 1e5 kin members of block A).
3. Then figures, note sections (decision 0039 item 9: once, in the session that judges the last
   runs) and a fresh G2 verifier (OPEN.md lists what it must cover, now including the decks of
   make_decks_b20.py and the two t_c the horizon recheck did not cover: 206.64 and 163.41 M).

## Packages still in progress (none has uncommitted files)

- longruns: the queue above. models: paused since 2026-11-20. threshold_scan: block A done at
  N = 1e5 (unfit); the scan is at N = 1e6. decisive: D2 read with M/16; seed pair pending.

## Traps

- Commit with explicit paths (`git commit -- <paths>`), never `git add -A`; nrpic-run and
  qitem.sh commit manifests (wait while `/data/haiyangw/nrpic/.git/worktrees/C-sidm/index.lock`
  exists).
- History of a run continued in place: later rows replace earlier ones from their first time
  on (all readers of longruns/scripts do this); a segment that restarts from t = 0 therefore
  truncates the history (A334s3c).
- Horizon numbers, if a later run has the finder: read found/not found only from
  `horizon_status_<n>.txt` (`<fastflow> diagnostics = true`), never from the summary file
  (decision 0040 item 3); the v0.6 finder's outputs do not survive a chained restart.
- Card runs with deposition are not byte-reproducible; read effects against controls.
- `nrpic-stage verify` with checksums hashes several TB of restart files. This session ran it
  with `--no-checksums` only and did NOT start a detached checksum pass: when it ends it rewrites
  stage/G2/VERIFY_RESULTS.*, and a dirty track makes `nrpic-run submit` (called by qitem.sh at
  dispatch) refuse the queued entries. Run the pass inside a session that waits for it and
  commits its results (one pass with `--full` before the gate review).
- Never kill by pattern; at most 6 cores; temporary files in scratch/C-sidm/tmp/.
