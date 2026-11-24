# HANDOFF of A-emd-pbh

Written for a reader with no memory, by the lead of batch 11 (wave 3), 2026-11-24 ~07:00 PST.

State in three lines: G0 and G1 are signed (coord/GATES.md). G2 has an interim package (stage/G2:
9 PASS, 10 OPEN, 1 FAIL) that is NOT ready for review: the threshold scan of the expanding ball
holds (code bracket = exact bracket), but the constraint norms do not converge before t ~ 6 (C3
FAIL, cause not named) and the periodic box's horizon is not found (finder fails on four levels).

Owner: A-emd-pbh, branch `track/A-emd-pbh`, worktree `/data/haiyangw/nrpic/wt/A-emd-pbh`.
Run first: `cd /data/haiyangw/nrpic/wt/A-emd-pbh && git merge --no-edit main && git status --short && squeue -u $USER -o "%.8i %.28j %.8T %.10M" | grep " A-" ; tail -5 /data/haiyangw/nrpic/scratch/A-emd-pbh/sequencer_b11/sequencer.log; cat /data/haiyangw/nrpic/scratch/A-emd-pbh/sequencer_b11/done.txt; harness/bin/nrpic-run status | grep -v completed | grep "A-2026112[1-9]"; harness/bin/nrpic-ctx inbox`

Files to read first: `STATUS.md`; `threshold_ball/JOURNAL.md` entries 3-10; `periodic_threshold/JOURNAL.md`
entries of 2026-11-24 (13:00Z to D0); `stage/G2/OPEN.md` and `CHECKLIST.md`; `stage/REVIEW-wave3.md`
section 7; `RISKS.md` rows 27-35.

## Card runs and what reads them

| run id (Slurm) | what | state at 07:00 PST | read by |
|---|---|---|---|
| A-20261122-173202-f98c79f (5150) | C-d0.42, mesh C (M/64), continued in place from t = 40 to 51 (MAX_SEGMENTS 21, rst dt 2) | PENDING | `threshold_ball/scripts/analyse.py --member C-d0.42` (T4 mesh-C half; add `--member B-d0.42` for the pair) |
| A-20261123-025907-97bab8d (5149) | periodic S1L, continued in place from t = 50 to 220 (MAX_SEGMENTS 9, rst dt 10) | PENDING, Slurm estimate 2026-11-25 05:09 | `periodic_threshold/scripts/job2_q.py` (Q1-Q3 again) and `analyse_scouting.py --gauge leak --run S1L=<dir>` (S1-S3, entry 2026-11-21 13:20Z) |
| queue_b11 line 1 | P0L6: P0L on six static levels (`inputs/peak_leak6.athinput`), chain 7 card-h | waits in the sequencer | compare_ltb.py, job2_q.py, line_trapped.py; predictions D1-D5 |
| queue_b11 line 2 | C-d0.40, mesh C, data run A-20261124-133456-2d00507 (dc0p4C), chain 14 card-h | waits in the sequencer | analyse.py: needs a MEMBERS line `"C-d0.40": (<run dir>, "32:64", "dc0p4", "nestC", 54.0)` whose prep is `A-20261124-133456-2d00507/dc0p4C/nestC` (DATA differs: add a data-dir field) ; prediction T7 |

Both continued chains are the SAME registered runs (no new manifest): close each with `harness/bin/nrpic-run
finish <run id>` once `scripts/submit_chain.sh --status /data/haiyangw/nrpic/scratch/A-emd-pbh/<run id>`
says DONE (finish counts every Slurm job in chain/events.log). If a chain again closes FAILED with
MAX_SEGMENTS reached before tlim (preemption), continue it in place with the same command as in the
journals (entry 3 of threshold_ball, 2026-11-24 13:00Z of periodic_threshold): `ATHENA_EXE=/data/haiyangw/nrpic/.work/build_gpu_v06/src/athena JOB_NAME=<run id> MAX_SEGMENTS=<higher> scripts/submit_chain.sh <rundir> <deck> <same args as chain/config.sh EXTRA_ARGS>`.

## The sequencer

`threshold_ball/scripts/sequencer.sh` (now logs "waiting: ..." when it waits, decision 0030 item 4),
started 05:45:30 PST with setsid nohup, pid in `scratch/A-emd-pbh/sequencer_b11/sequencer.pid` (207327),
queue `tracks/A-emd-pbh/periodic_threshold/queue_b11.txt`. It submits the next line when fewer than
two Slurm jobs named `A-*` are queued or running. The old sequencer (sequencer_threshold) ended
normally on 2026-11-23 10:40 after its 15 lines.
- See it: `ps -p $(cat /data/haiyangw/nrpic/scratch/A-emd-pbh/sequencer_b11/sequencer.pid)`.
- Stop: `touch /data/haiyangw/nrpic/scratch/A-emd-pbh/sequencer_b11/STOP` (or kill the numeric pid).
- Restart (skips lines in done.txt): `cd /data/haiyangw/nrpic/wt/A-emd-pbh && rm -f /data/haiyangw/nrpic/scratch/A-emd-pbh/sequencer_b11/STOP && setsid nohup tracks/A-emd-pbh/threshold_ball/scripts/sequencer.sh tracks/A-emd-pbh/periodic_threshold/queue_b11.txt /data/haiyangw/nrpic/scratch/A-emd-pbh/sequencer_b11 >> /data/haiyangw/nrpic/scratch/A-emd-pbh/sequencer_b11/nohup.out 2>&1 < /dev/null &`
- TRAP: done.txt keys on line numbers; add lines at the END only. A line is refused while its
  `--package` has uncommitted changes (5 tries, then skipped).

## Processor runs of this session

- A-20261124-132016-ecf12c3 (G1-G3, A-mesh guard stop from the t = 44 restart): G1 repeated the card
  stop exactly (t = 47.921875, cycle 3067, same first cell) [VERIFIED]; G2 (lapse_leak 0) and G3
  (alpha_exc 0.3) see threshold_ball entry 5 outcome (written at the end of the session if they
  finished; otherwise read `scratch/A-emd-pbh/A-20261124-132016-ecf12c3/run.log` and `G2/`, `G3/`,
  then `nrpic-run finish`).
- K4 (entry 10): see the end of threshold_ball/JOURNAL.md for its run id and outcome.

## Packages and what remains

| Package | State | What remains |
|---|---|---|
| `threshold_ball/` | scan judged (entry 4); constraint tests K-K3 refuted (6-9); K4 (10) | mesh C at threshold (C-d0.42, C-d0.40); README.md with the results table; cause of the constraint floor; A-mesh guard stop |
| `periodic_threshold/` | job 2 judged (Q, P, F, D0); S1L continuing; P0L6 queued | S1-S3; D1-D5; README table and DESIGN 7.1; request to core only if the finder fails with the horizon resolved |
| `conv_ball/` | done | second agent on its G2 reading (C18) |
| `verify_bh/` | done; slice-or-finder answered by the scan (entry 4) | nothing |
| `szekeres/` round 1 | cut 2026-11-20 | card series N = 64, 128, 256 to tau = 40 (G2 C1) |
| `periodic_diag/`, `runs_ball/`, `g1close/` | done | nothing |

## Decisions pending

- orch: constraint-bound-ruling (outbox 20261124T133627Z): the 0.1 bound of SCOPE section 3 fails from
  t = 0 in every run; ruling asked after the next constraint test.
- core: refined-mesh-cfl05-result (info, 20261124T133506Z) answers their step-limit-in-work;
  periodic-gamma-driver-step (W31, in work in core's batch 11); bh1r-inte-deficit-two-levels.
- kb: Szekeres conformal-flatness locators (acknowledged) to be cited when szekeres resumes.

## Traps

- With a Gamma-driver keep cfl_number <= 0.6 (decision 0027); lapse_leak x dt below ~2 on the coarsest level.
- No `<z4c> lapse_leak` around an existing black hole for long runs (decision 0025 item 3); the ball
  collapse runs stop 4-8 M after the horizon forms.
- The processor build reads card restart files (F2, G1-G3): cheap processor diagnostics from restarts.
- Chain histories repeat times after a restart from an older restart file: readers must keep the
  records written last (job2_q.py, constraint_conv.py do).
- Markdown tables: never write `||H||` inside a table row (the pipes split the cell).
- Helpers sharing the worktree: commit path-limited; kill processes by numeric PID only.
