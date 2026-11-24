# HANDOFF of C-sidm

For a reader with no memory of the last session. That session was the lead of batch 11 (the
analysis round after the card runs), 2026-11-24 from 12:50 to about 14:05 UTC.

State in three lines:
1. G0 and G1 are signed. G2 is open; `stage/G2/` exists (CHECKLIST judged, EVIDENCE, OPEN,
   STAGE_REPORT). G2 is not met: the threshold cannot be located on M/8 at N = 1e5 because the
   collisionless controls of y0 = 0.334032 and 0.344 collapse on their own (534.8, 549.3 M).
2. The sequencer runs the continuations of ten chains cut by preemption and three follow-ups
   (N = 1e6 and 1e4 controls, D2 on M/16) whose predictions are in JOURNAL.md 2026-11-24T13:14Z.
3. Outcomes of every batch-5 run that ended are in JOURNAL.md 2026-11-24T13:12Z; failed
   predictions: N.3, D2.2, A.1 (kout part), A.3, A.4.

Owner: C-sidm. Branch: `track/C-sidm`. Worktree: `/data/haiyangw/nrpic/wt/C-sidm`.
Start with:
`cd /data/haiyangw/nrpic/wt/C-sidm && git merge --no-edit main && git status --short && harness/bin/nrpic-ctx inbox && tracks/C-sidm/longruns/seq/seq.sh status && squeue -o '%i %j %u %T %M %P' && test -e /data/haiyangw/nrpic/locks/PAUSE && echo PAUSED`

## The sequencer (read `longruns/README.md` "Operating the sequencer" and "Preemption")

- Script `tracks/C-sidm/longruns/seq/seq.sh` (`run`, `status`, `stop`); state, log, pid in
  `/data/haiyangw/nrpic/scratch/C-sidm/seq/`. Alive: `kill -0 $(cat /data/haiyangw/nrpic/scratch/C-sidm/seq/seq.pid) && echo alive`
  (pid 4068739, started 2026-11-24 13:19:45Z).
- Restart after a stop or reboot: `cd /data/haiyangw/nrpic/wt/C-sidm && setsid nohup tracks/C-sidm/longruns/seq/seq.sh run >> /data/haiyangw/nrpic/scratch/C-sidm/seq/nohup.out 2>&1 < /dev/null &`
  Edit `seq.sh` only by writing a new file and `mv` onto it while a loop runs; stop the loop,
  then start it again.
- Since batch 11 it submits while the pause flag exists, logs why the next item waits, resumes
  cut chains in place (`resume` items) and raises the segment cap of new chains to 20.
- It keeps two C-sidm card jobs eligible. Do not submit card jobs by hand while it runs.
- It closes ended runs (`nrpic-run finish`, for resume items with `--status`) and commits the
  manifests locally. Push them (`git pull --no-rebase --no-edit && git push origin track/C-sidm`).

## Runs still going and what reads them

| Item | Run id | State at 14:00Z | Read with | Predictions |
|---|---|---|---|---|
| A324s1c+ (control 0.324) | C-20261123-032324-938ecbd | running from t = 10 M | `longruns/scripts/blockA_delta.py --ripple-tmax 400` with all 15 block A runs | A.2, A.4 |
| A334s3o (kout, seed 3) | C-20261124-120250-9e6a3ba | running from 110 M (cap 24 segments, edited by hand, see JOURNAL 12:59Z) | same | A.3 |
| A344s1o+, A324s1o+ | C-20261123-025228-6ecb543, -222003-02195a0 | queued (resume from 400 M) | same | A.1, A.2 |
| N6c | new run id when submitted | queued | a reader still to write: control t_c and alpha_c changes at 100-500 M of N = 1e4, 1e5, 1e6 (`xcheck_b11.py` gives both numbers now) | NS.1, NS.2 |
| M16 | new | queued | `longruns/scripts/d2_analysis.py` with label m16 (and the M/8 runs) | M16.1, M16.2 |
| A334s2c+, A334s3c+ | C-20261124-053105-2fcc8af, -082221-7f03a8e | queued | blockA_delta.py | A.3; control t_c scatter |
| N4c | new | queued | as N6c | NS.3 |
| D2f2s2+ | C-20261124-035054-c06503f | queued (from 100 M) | d2_analysis.py | D2.3 seed pair |
| A334s2i+, A334s2o+, A334s3i+ | C-20261124-061134-ab6cc0a, -075153-72499e7, -091733-b92f4e5 | queued | blockA_delta.py | A.3 |

`blockA_delta.py` now drops a window that a run covers only in part (fixed at the end of batch 11,
not yet rerun); the seed standard deviation of sigma_w therefore uses complete windows only.
A cut chain that fails again for lack of segments: add another `resume` line to `queue.txt`
(new item name, e.g. `A324s1c++`), commit, restart the loop.

## Decisions of this session

- Cut chains are continued in place from their newest restart, never repeated (resume rule,
  JOURNAL 12:59Z); restart every 10 M.
- R(v) by its written rule says noise relaxation; the N = 1e6 control on M/8 (N6c) tests it
  where it matters. NS.1 -> seeds at N = 1e6 (about 12 card-hours); NS.2 -> M/16 control,
  gauge or boundary leg (OPEN.md item 2), request to core with a reproducing input.
- The block A noise model is applied with the ripple before 400 M (post hoc, labelled).
- G2 is not ready for review; OPEN.md lists what a G2 verifier must cover.

## Packages still in progress (none has uncommitted files)

- longruns: the queue above. drift: closed with run (v) (its analysis is this session's).
- models: paused since 2026-11-20 (step 5, King runs alpha_coll minus control).
- threshold_scan: block A is in longruns; blocks B-D wait for the N6c/M16 verdicts.
- decisive: D2 read; M16 and the seed pair pending.

## Traps

- Commit with explicit paths (`git commit -- <paths>`), never `git add -A`; the sequencer
  commits too (wait while `/data/haiyangw/nrpic/.git/worktrees/C-sidm/index.lock` exists).
- `nrpic-run budget` does not count in-place continuations until they are closed again.
- History of a run continued in place: later rows replace earlier ones from their first time
  on (all readers of longruns/scripts do this). A restarted run in a new directory writes its
  history without a header (drift `controls.join_hst`).
- Card runs with deposition are not byte-reproducible; read effects against controls.
- Never kill by pattern; at most 6 cores; temporary files in scratch/C-sidm/tmp/.
