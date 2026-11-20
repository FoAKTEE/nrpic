# Requests of package p1 (F-hills, wave 3 round 1)

Drafts for the F-hills lead to post. Evidence: `JOURNAL.md` entry 0 of this package.

## 1. To orch (owner of `scripts/submit_chain.sh`): an outside SIGTERM is classified as FAILED

What happened [VERIFIED]. Segment 7 of the chain of run F-20261119-150017-b45ec5f (Slurm job
4684) ended at 2026-11-19 19:35:43 PST with `STATUS FAILED (athena exit status 143)`. It was not
a preemption: the machine has one partition (`preempt`, PriorityTier 10, `PreemptType =
preempt/partition_prio`), `sacct` records 4684 as FAILED with ExitCode 1:0 (the chain script's
own `exit 1`, line 269), and the TERM trap of the batch script (lines 173-177) did not fire. The
signal came from `pkill -x athena`, run at 03:35:41.6Z by a Claude Code session of another
project of the same Unix account to stop its own processes; P1's executable had the process
name `athena` (the wrapper `exec`s `.work/build_gpu_v03/src/athena`). AthenaK has no signal
handler, so it died at once; the chain saw rc = 143, `term = 0`, and stopped (line 236). The
next user's job started on the freed card in the same second, which made it look like a
preemption.

Proposed rule. When athena exits with 143 or 137 (128 + SIGTERM / SIGKILL), with no AthenaK
termination message in the segment log and the chain's TERM flag unset, the chain treats it as
an outside interruption: log "athena killed by signal N (not via the batch script)" and
resubmit from the newest restart, as it does on SIGTERM (lines 264-265), at most twice in a row
(a third kill in a row is FAILED, so a deterministic crash that ends in a signal cannot loop).

Further proposals:
- Run the real executable under a run-specific process name (for example a copy or hard link
  `chain/ak-<6 chars of the run id>`), so that `pkill -x athena` in any session does not reach
  chained card runs. P1 does this now by hand through the wrapper's `NRPIC_REAL_ATHENA`
  (`scratch/F-hills/tmp/p1/exe/p1-ak03-gpu`, byte-identical to the release card executable).
- Tell the user that sessions outside this program on `anta` use `pkill -x athena`, which kills
  every AthenaK process of the account, the program's card jobs included (CLAUDE.md forbids
  pattern kills only inside the program).
- `--status` could print the last attempt's exit code and the cause, so that a reader does not
  have to read the segment log and `sacct` to tell a crash from a kill.

## 2. To core: tracker files are truncated on restart (reminder)

`athenak/src/z4c/compact_object_tracker.cpp` line 78 (release core-v0.3) opens
`<base>.co_<n>.txt` without `std::ios::app`, also when the run starts from a restart file, so a
chained run keeps only the rows of its last segment. Asked in
`outbox/20261119T151428Z__to-core__tracker-files-on-restart.md`; no answer found. On
`core/cosmo-amr` (commit 3f681d42) the open moved into `OpenOutput()`, still with truncation.
P1 depends on `nr_first/scripts/athena_keep_trackers.sh` copying the files before every segment;
a restart that starts from an older restart file (as after segment 7) makes the kept copy and
the new file overlap by the lost interval, which `nrread.read_tracker_merged` resolves (later
file wins). Request: open with `std::ios::app` when `pmesh->restart` is set (header only on a
fresh start), or name the file per segment.

## 3. To the F-hills lead

- P1 was resumed with MAX_SEGMENTS = 18 (11 more segments, about 9.2 card-hours) instead of the
  planner's 26, to keep this package's cap of 10 card-hours. If the chain stops on
  MAX_SEGMENTS before t = 280, resume it with the command in `README.md` and a higher value
  (each segment 0.84 card-hours); the lead decides.
- P1 prediction item 1, tree 1716-2400 MeshBlocks, is refuted on the low side (1156-1366 from
  t = 47 M on); details in `JOURNAL.md`. Nothing to do; the cost is lower than announced.
