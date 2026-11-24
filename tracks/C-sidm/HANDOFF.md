# HANDOFF of C-sidm

For a reader with no memory of the last session. That session was the short batch-12 session
of 2026-11-24 (21:00-21:30 UTC) whose one aim was to hand this owner's waiting card runs to
the shared card queue (decision 0033). The analysis state is that of the batch-11 lead
(JOURNAL 2026-11-24T13:12Z, 13:14Z, 13:36Z).

State in three lines:
1. G0 and G1 are signed. G2 is open; `stage/G2/` exists (CHECKLIST judged, EVIDENCE, OPEN,
   STAGE_REPORT). G2 is not met: the threshold cannot be located on M/8 at N = 1e5 because the
   collisionless controls of y0 = 0.334032 and 0.344 collapse on their own (534.8, 549.3 M).
2. Every C-sidm card run that still has to run is an entry of the shared queue (table below);
   the sequencer `longruns/seq/seq.sh` is retired (its `run` refuses). One chain is in Slurm
   outside the queue: A324s1c+ (job 5206).
3. Outcomes of every batch-5 run that ended are in JOURNAL.md 2026-11-24T13:12Z; failed
   predictions: N.3, D2.2, A.1 (kout part), A.3, A.4. Predictions of the queued runs: JOURNAL
   2026-11-21T20:25Z (block A, D2) and 2026-11-24T13:14Z (N6c, M16, N4c; resume rule 12:59Z).

Owner: C-sidm. Branch: `track/C-sidm`. Worktree: `/data/haiyangw/nrpic/wt/C-sidm`.
Start with:
`cd /data/haiyangw/nrpic/wt/C-sidm && git merge --no-edit main && git status --short && harness/bin/nrpic-ctx inbox && harness/bin/nrpic-queue list --owner C-sidm && squeue -u $USER -o '%i %j %T %M' && test -e /data/haiyangw/nrpic/locks/PAUSE && echo PAUSED`

## Card runs: the shared queue (harness/RULES.md "Shared card queue")

- Card runs reach Slurm only through `harness/bin/nrpic-queue add` (decision 0033). Never
  `sbatch`, `scripts/submit_chain.sh` or `gpu_batch.sh` directly, no sequencer.
- Every entry runs `tracks/C-sidm/longruns/seq/qitem.sh <item>`: it reads the item's line in
  `longruns/seq/queue.txt` (the committed parameters) and submits one job, either a new chain
  through `nrpic-run submit` (then process name and segment cap 20 in chain/config.sh, as
  seq.sh did) or an in-place resume of a cut chain from its newest restart
  (`scripts/submit_chain.sh` with MAX_SEGMENTS raised, JOB_NAME = run id; a `continuations`
  entry is committed in the manifest). Outside the dispatcher it refuses; `--dry-run` checks.
- The queue never closes runs. When an entry shows `done` in `nrpic-queue list`, close its run:
  `tracks/C-sidm/longruns/seq/qitem.sh close <run_id>` (finish, with `--status` from
  chain/STATUS for a continued run). Then push the manifests.
- The dispatcher commits nothing itself, but nrpic-run and qitem.sh commit manifests on this
  branch at dispatch: push them at the end of each session
  (`git pull --no-rebase --no-edit && git push origin track/C-sidm`).
- A new chain item: add its line to queue.txt, commit, `qitem.sh <item> --dry-run`, then
  `harness/bin/nrpic-queue add --label <label> --priority <2|5> --cmd 'tracks/C-sidm/longruns/seq/qitem.sh <item>'`.

## Runs still to run or running, and what reads them

| Queue id | Label | Prio | Item / run id | Read with | Predictions |
|---|---|---|---|---|---|
| (Slurm 5206, not from the queue) | A324s1c+ | - | C-20261123-032324-938ecbd, running from about 451 M | `longruns/scripts/blockA_delta.py --ripple-tmax 400` with all 15 block A runs | A.2, A.4 |
| q0016 | N6c | 2 | new run (N = 1e6 control of y0 0.334032 on M/8, 600 M) | a reader still to write: control t_c and alpha_c changes at 100-500 M of N = 1e4, 1e5, 1e6 (`xcheck_b11.py` gives both numbers) | NS.1, NS.2 |
| q0017 | M16 | 2 | new run (D2 on M/16, 220 M) | `longruns/scripts/d2_analysis.py` with label m16 (and the M/8 runs) | M16.1, M16.2 |
| q0018 | N4c | 2 | new run (N = 1e4 control, 600 M) | as N6c | NS.3 |
| q0019 | A334s3o-cont | 5 | A334s3o+: C-20261124-120250-9e6a3ba from about 120 M (stopped by orch 12:00 PST) | blockA_delta.py | A.3 |
| q0020 | A344s1o-cont | 5 | A344s1o+: C-20261123-025228-6ecb543 from 420 M | blockA_delta.py | A.1, A.2 |
| q0021 | A324s1o-cont | 5 | A324s1o+: C-20261123-222003-02195a0 from about 400 M | blockA_delta.py | A.1, A.2 |
| q0022 | A334s2c-cont | 5 | A334s2c+: C-20261124-053105-2fcc8af from about 249 M | blockA_delta.py | A.3; control t_c scatter |
| q0023 | A334s3c-cont | 5 | A334s3c+: C-20261124-082221-7f03a8e from about 28 M | blockA_delta.py | A.3; control t_c scatter |
| q0024 | D2f2s2-cont | 5 | D2f2s2+: C-20261124-035054-c06503f from about 110 M | d2_analysis.py | D2.3 seed pair |
| q0025 | A334s2i-cont | 5 | A334s2i+: C-20261124-061134-ab6cc0a from about 245 M | blockA_delta.py | A.3 |
| q0026 | A334s2o-cont | 5 | A334s2o+: C-20261124-075153-72499e7 from about 190 M | blockA_delta.py | A.3 |
| q0027 | A334s3i-cont | 5 | A334s3i+: C-20261124-091733-b92f4e5 from about 103 M | blockA_delta.py | A.3 |

Priority 2 for the three runs that `stage/G2/OPEN.md` items 1-2 name as what the gate waits
for; this puts them ahead of A344s1o+ and A324s1o+, which came first in the batch-11 order.
No `--after`: no run reads another's output; within a priority the queue keeps the order of
adding. Times "from" are the last history line before the cut, not the restart time.

`blockA_delta.py` drops a window that a run covers only in part (fixed at the end of batch 11,
not yet rerun); the seed standard deviation of sigma_w therefore uses complete windows only.

## Decisions of the batch-11 lead (still in force)

- Cut chains are continued in place from their newest restart, never repeated (resume rule,
  JOURNAL 12:59Z); restart every 10 M.
- R(v) by its written rule says noise relaxation; the N = 1e6 control on M/8 (N6c) tests it
  where it matters. NS.1 -> seeds at N = 1e6 (about 12 card-hours); NS.2 -> M/16 control,
  gauge or boundary leg (OPEN.md item 2), request to core with a reproducing input.
- The block A noise model is applied with the ripple before 400 M (post hoc, labelled).
- G2 is not ready for review; OPEN.md lists what a G2 verifier must cover.

## Packages still in progress (none has uncommitted files)

- longruns: the queue above. drift: closed with run (v).
- models: paused since 2026-11-20 (step 5, King runs alpha_coll minus control).
- threshold_scan: block A is in longruns; blocks B-D wait for the N6c/M16 verdicts.
- decisive: D2 read; M16 and the seed pair pending.

## Traps

- Commit with explicit paths (`git commit -- <paths>`), never `git add -A`; qitem.sh and
  nrpic-run commit manifests at dispatch (wait while
  `/data/haiyangw/nrpic/.git/worktrees/C-sidm/index.lock` exists).
- `nrpic-run budget` does not count in-place continuations until they are closed again.
- A preempted segment still counts as a segment: a continued chain that fails again with
  "MAX_SEGMENTS reached" gets a new resume line in queue.txt (e.g. `A324s1c++`), a commit and
  a new queue entry.
- History of a run continued in place: later rows replace earlier ones from their first time
  on (all readers of longruns/scripts do this).
- Card runs with deposition are not byte-reproducible; read effects against controls.
- Never kill by pattern; at most 6 cores; temporary files in scratch/C-sidm/tmp/.
- The sequencer's state (`scratch/C-sidm/seq/state.tsv`) is history now; do not restart it.
