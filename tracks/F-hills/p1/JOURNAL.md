# JOURNAL of package p1 (F-hills, wave 3 round 1): resuming the passage P1

Run F-20261119-150017-b45ec5f (`scratch/F-hills/F-20261119-150017-b45ec5f`, written only by its
chain). Labels [VERIFIED] (a run, a log or a file at its locator), [JUDGEMENT], [BACKGROUND],
[TO VERIFY]. Times: the machine logs in PST (UTC - 8); UTC where marked Z.

## Entry 0 (2026-11-20 22:15Z): what ended segment 7, before any resubmission

State found [VERIFIED, files of the run directory]:
- `chain/STATUS` = FAILED; `chain/events.log` last line `2026-11-19 19:35:43 seg=7 job=4684
  STATUS FAILED (athena exit status 143)`; segment counter `chain/segment` = 7; `chain/config.sh`
  ATHENA_WALL 00:50:00, SLURM_TIME 00:59:00, MAX_SEGMENTS 26, EXE_SRC = the tracker wrapper.
- `chain/athena` (sha256 0b71067a...) equals `nr_first/scripts/athena_keep_trackers.sh` and the
  manifest's exe; `chain/input.athinput` equals `nr_first/inputs/p1_q4.athinput` (45c73f71...);
  the release card executable is unchanged (f9f2dc12..., as in the manifest).
- Seven segments ran (Slurm 4650, 4669, 4672, 4675, 4678, 4681, 4684). Segments 1-6 ended on the
  wall-clock limit at t = 14.27, 30.57, 47.65, 65.88, 85.11, 103.34 (logs `chain/seg00k.*.log`,
  lines "Terminating on wall clock limit"). `sacct`: 50:05-50:09 each; segment 7 00:25:06, state
  FAILED, ExitCode 1:0. Sum 5 h 25 min 45 s = 5.43 card-hours.
- `chain/seg007.job4684.a1.log`: read `rst/hills.00021.rst` (1352 MeshBlocks), "Setup complete",
  last line `elapsed=1.456147e+03 cycle=28700 time=1.121094e+02`, then only the footer `# exit=143
  end=2026-11-19T19:35:43-08:00`; no AthenaK termination message, no error text. The gpumem csv
  runs to 19:35:43.037 at 70843 MiB and 94-100 percent utilisation: the card was busy and full to
  the last sample, no memory growth.
- Restart files (headers read: time, cycle, MeshBlocks): 00019 t = 95.0 (24320, 1296), 00020
  t = 100.0 (25600, 1226), 00021 t = 103.336 (26454, 1352; wall-clock stop), 00022 t = 110.0
  (28160, 1156; written 19:28). Sizes follow 20.8 kB + 2433044 B per MeshBlock to within 133 B
  for 00000, 00021 and 00022, so 00022 is complete.

Why the planner's reading (preemption) is wrong [VERIFIED]:
- The machine has one partition (`scontrol show partition`: preempt, PriorityTier 10), and
  `PreemptType = preempt/partition_prio`: a job can only be preempted by one of a partition with
  a higher tier, and there is none. A preempted job is recorded as PREEMPTED (or CANCELLED);
  4684 is FAILED with ExitCode 1:0, which is the chain script's own `exit 1` after it wrote
  FAILED (submit_chain.sh line 269). The batch script was not signalled (its TERM trap, lines
  173-177, did not fire: the outcome would have been TERM and a resubmission, line 264).
- Another user's job 4685 was submitted at 19:10:34 (`sacct -j 4685`: Submit), waited, and
  started at 19:35:43 because 4684 had just freed the card, not the other way round.

Cause [VERIFIED to the second; JUDGEMENT only in that the signal itself is not logged]:
- At 2026-11-20T03:35:41.642Z (19:35:41.6 PST) a Claude Code session of another project of the
  same Unix account (its transcript under `~/.claude/projects/`, session bffc8ad0) ran the shell
  command `pgrep -fa "[r]un_regressions.py" | cut -c1-120; pkill -f "[r]un_regressions.py";
  sleep 1; pkill -x athena; ...` to stop its own regression run. `pkill -x athena` sends SIGTERM
  to every process of the user whose name is exactly `athena`. P1's process had that name: the
  wrapper ends with `exec "$REAL"`, REAL = `.work/build_gpu_v03/src/athena`. One second later
  (19:35:43) P1's athena exited with 143 = 128 + SIGTERM. AthenaK installs no signal handler
  (`grep -rn "SIGTERM\|signal(" athenak/src` finds nothing), so it died at once, without a
  restart file. The chain script and `_athena_job.sh` have other process names (the spooled
  batch script; `_athena_job.sh`), were not signalled, and the chain classified the exit as a
  failure (submit_chain.sh line 236).
- It is the only command of that kind in that transcript in the hours around (15 kill commands
  with "athena" in it over its whole history; this is the only bare `pkill -x athena`). The same
  session is still active (transcript written at 14:04 PST today).
- Lost work: t = 110.0 to 112.11 (2.1 M, about 7 min of card time) plus the tracker rows to
  112.38, which the resumed chain recomputes.

What would refute this: a log showing that athena of job 4684 got its signal from Slurm
(slurmd log, not readable here), or a command time in the transcript more than a few seconds
from 19:35:43. Neither is the case in what I can read.

Consequence for the resume [JUDGEMENT]: a second `pkill -x athena` by that or another session
would kill P1 again. The wrapper honours `NRPIC_REAL_ATHENA`; I point it at a byte-identical
copy of the release card executable named `p1-ak03-gpu`
(`scratch/F-hills/tmp/p1/exe/p1-ak03-gpu`, sha256 f9f2dc12..., equal to the manifest's input;
`ldd`: absolute library paths, no RPATH), so the process is no longer called `athena`. This
does not protect against `pkill -f athena` (the cmdline of `_athena_job.sh` contains "athena",
and it forwards TERM). sbatch exports the environment (default `--export=ALL`; `clean_sbatch`
removes only SLURM_* and SBATCH_*), so the variable reaches every resubmitted segment; if it
were lost, the wrapper falls back to the release path, the same binary.
Budget: my cap is 10 card-hours (5.43 used before); MAX_SEGMENTS = 18 allows 11 more segments,
11 x 0.836 h = 9.2 card-hours, instead of the 19 that MAX_SEGMENTS = 26 would allow.

## Entry 1 (2026-11-20 22:40Z): prediction for the resumed chain, written before submission

1. The first resumed segment (number 8) reads `rst/hills.00022.rst` (t = 110.0, cycle 28160,
   1156 MeshBlocks): it is the newest by modification time and complete. Refuted if it renames
   a file to `.bad` (submit_chain.sh lines 226-235) or starts from another file.
2. Trackers: the wrapper copies the live `hills.co_*.txt` (seg 7, t = 103.34-112.38) to
   `trk_keep/<stamp>/`; the resumed segment writes from t = 110.0. After
   `nrread.read_trackers` joins them, every tracker has rows without a gap larger than two
   output intervals across t = 103-120 and no jump in position at t = 110 larger than the
   step-to-step motion. Refuted by a gap or a jump.
3. Rate: each full 50-min segment advances 15-21 M (segments 2-6: 16.3-19.2 M; segment 7 at
   1.54 cycles/s = 18.1 M per 50 min). Refuted outside that band.
4. Tree: P1 prediction item 1 (JOURNAL.md of the track, line 306) gave 1716-2400 MeshBlocks.
   That band is ALREADY refuted on the low side by the segments run so far (trees 1576, 1282,
   1366, 1310, 1352 at the starts of segments 3-7, 1156 at t = 110; restart headers and logs),
   and the outcome entry says so. For the rest of the run I predict 1000-1800 MeshBlocks
   [JUDGEMENT: the nests of the bound member and the hole overlap; the leaving member's nest
   adds blocks again] and never above the 2700 slots. Refuted by a slot-limit stop or a tree
   outside 1000-1800.
5. Cost: 170 M remain; at 15-21 M per segment that is 9-11 segments, 7.5-9.2 card-hours, inside
   MAX_SEGMENTS = 18. Refuted if a segment fails for a reason other than an outside signal, or
   if the chain reaches MAX_SEGMENTS before tlim = 280.
6. The process of the resumed segments is called `p1-ak03-gpu` (checked with `ps` when a
   segment runs). Refuted if `ps` shows `athena`.

## Entry 2 (2026-11-20 22:21:54Z): chain resumed

`squeue -u $USER` before: no F-hills job (jobs of core and C only); `chain/jobid` 4684 no longer
known to Slurm. Command (from `/data/haiyangw/nrpic/wt/F-hills`, at 22:21:53Z):

    ATHENA_EXE=/data/haiyangw/nrpic/wt/F-hills/tracks/F-hills/nr_first/scripts/athena_keep_trackers.sh \
    NRPIC_REAL_ATHENA=/data/haiyangw/nrpic/scratch/F-hills/tmp/p1/exe/p1-ak03-gpu \
    MAX_SEGMENTS=18 JOB_NAME=F-20261119-150017-b45ec5f \
    scripts/submit_chain.sh /data/haiyangw/nrpic/scratch/F-hills/F-20261119-150017-b45ec5f \
        /data/haiyangw/nrpic/wt/F-hills/tracks/F-hills/nr_first/inputs/p1_q4.athinput

Result [VERIFIED]: `chain started ...: job 4738`; `--status`: STATUS QUEUED, job 4738 PENDING
(Priority); events.log `2026-11-20 14:21:54 seg=7 job=login submitted job 4738`; config.sh
rewritten with MAX_SEGMENTS=18, the same EXE_SRC, ATHENA_WALL and SLURM_TIME. The planner's
command had MAX_SEGMENTS=26; I set 18 to keep the 10 card-hour cap (entry 0). Not through
`nrpic-run submit`: same run id, directory, input and executable content.
