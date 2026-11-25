# Preempted runs: restart file on SIGTERM, chains that do not count a cut attempt

Owner core. Branch `core/step-limit` (batch 13, 2026-11-24), second item of the package;
for release v0.7 (decision 0032 item 2). Evidence and every number:
`tracks/core/JOURNAL-step-limit.md`, entries 10 to 13 (predictions before, outcomes after,
run ids); scripts: `tracks/core/analysis/preempt/term_test.py`,
`scripts/tests/test_submit_chain.py`; decks `problems/tests/term_signal_periodic.athinput`,
`term_signal_particles.athinput`. Executables:
`/data/haiyangw/nrpic/scratch/core/exe/core_step-limit/` (READY there says what is tested).

In one paragraph: jobs of another user in the partition `priority` cancel ours for hours.
Slurm sends SIGTERM and 30 s later SIGKILL. AthenaK had no handler: the run died on the
first signal and the segment was lost back to its last scheduled restart file; the chain
script counted every such attempt as a segment and, when the segments were used up,
queued one more job only to fail in it. Now (a) AthenaK finishes the cycle in progress on
SIGTERM, writes its restart outputs and nothing else, and exits with status 143; (b) the
chain script lets it do so, does not count an attempt cut by a signal, and ends at its
cap without the extra job. No option: a run that receives no signal is byte-identical
with release core-v0.6 (section 4).

## 1. The grace period on anta [VERIFIED: `scontrol show config`, `scontrol show partition preempt`, 2026-11-24]

`KillWait = 30 sec`, `PreemptMode = CANCEL`, `PreemptType = preempt/partition_prio`,
`OverTimeLimit = 0`; partition `preempt`: `GraceTime=0`, `MaxTime=01:00:00`. A job that is
preempted, cancelled or over its time limit gets SIGCONT and SIGTERM, and SIGKILL after
KillWait: 30 s [the two numbers are the configuration read on the machine; that Slurm
waits KillWait after the SIGTERM of a preemption with zero grace time is its documented
behaviour, BACKGROUND; it was not timed with a job, which would have needed a place in
the queue of five].

Does a 256-cell restart file fit? Measured on the serial processor build (run
core-20261124-235925-5ee2c95): the restart file of 256^3 cells of Z4c in 64^3
MeshBlocks has 4.20 GB (22 fields with their ghost cells) and was written in **3.2 s**
(1.3 GB/s into the page cache of `/data`). The particle companion `.prt` has 90 bytes
per particle [VERIFIED: 1,513,947,560 bytes for 16,777,216 particles,
`scratch/B-emd-gw/B-20261124-223926-33194d9/rst/pop.00005.rst.prt`]: 1.5 GB for 256^3
particles, at the measured rate another 1.2 s. What is added on a card, not measured
[JUDGEMENT]: the cycle in progress (0.2 to 3 s for the decks in use) and the copy of the
fields to the host (4 GB, about a second). So a 256-cell run with 256^3 particles needs
5 to 10 s of the 30: it fits with a factor 3 or more, unless the file system is slow at
that moment (at 200 MB/s the mesh file alone takes 21 s). A restart file cut by the SIGKILL is not used: the next start
stops on it before the set-up ends (section 3, last paragraph), and the chain script
then renames it and continues from the one before.

## 2. AthenaK: stop on SIGTERM

Source: `athenak/src/utils/term_signal.{hpp,cpp}` (new). Hooks: `main.cpp` (include;
`term_signal::Install()` after `Kokkos::initialize`; the return value),
`driver/driver.cpp` (include; the last condition of the main loop in `Driver::Execute`;
in `Driver::Finalize` the skip of the other outputs and of the problem's final function,
the timer and the message), `CMakeLists.txt` (one line).

- The handler only sets a flag and notes the time of the first signal. It stays
  installed: Slurm sends SIGTERM at the preemption and again at the end of the grace
  time, and the job wrappers forward it too. SIGKILL stops a run at once, as before.
  SIGINT is not handled (Ctrl-C ends a run at once, as before).
- `Driver::Execute` asks for the flag once per cycle, as the last condition of its loop
  (under MPI one reduction over the ranks, so that all leave after the same cycle). The
  cycle in progress is completed with its scheduled outputs, refinement and new step,
  exactly as at a stop on the wall-clock limit `-t`.
- `Driver::Finalize` then writes every restart output (`file_type = rst`) once, with the
  companions of the particles, the refinement record and the scalar field, and no other
  output; the schedule of the restart output is left where it was (as at a wall-clock
  stop, package dfix), so the continued run writes its scheduled outputs at the times of
  the uninterrupted run. The final function of a test problem (error norms) is skipped.
- The log ends with

      Terminating on signal SIGTERM
      restart outputs written after the cycle in progress: 1 in 0.004 s, done 0.284 s after the signal reached rank 0; exit status 143
      time=1.345345e+01 cycle=101

  and the exit status is **143** (128 + SIGTERM), the status a run killed by the signal
  had before: no wrapper takes the run for complete (`nrpic-run`, `cpu_run.sh`,
  `gpu_batch.sh` and the chain script see what they saw, plus the line and the file).
- A run that reaches its time or cycle limit, or stops on the guard or the wall clock,
  in the cycle in which the signal arrives ends as it would have: all outputs, its own
  status. A signal during the set-up (initial data, a long elliptic solve) is answered
  when the set-up has ended: no cycle is run, the restart file of the initial slice is
  written under the next number.
- An input without a restart output writes nothing ("restart outputs written ...: 0")
  and exits with 143.
- Continue with `athena -r rst/<newest>.rst` (the chain script does). The restart file
  written on the signal has the next free number, so the later ones are shifted by one
  against an uninterrupted run.

## 3. What a run stopped on the signal and continued reproduces [tests S, run core-20261124-234903-61e194c]

Serial processor build, two decks: Z4c in a periodic box without matter (flat space
with noise, 1+log lapse, Gamma-driver, 240 steps: S1; the same with two signals 0.3 s
apart: S1d; with the signal during the set-up: S0) and particles coupled to Z4c in a
periodic box (matter universe, 16^3 cells in eight MeshBlocks, 4096 particles with noise
in position and momentum, 80 steps: S2, S2b). Each is run once without interruption and
once with SIGTERM part-way and a continuation from the restart file written on the
signal; every file is compared.

| | S1 | S1d | S0 | S2 | S2b |
|---|---|---|---|---|---|
| stopped with cycle (of) | 101 (240) | 61 (240) | 0 (240) | 26 (80) | 28 (80) |
| exit status, message | 143, yes | 143, yes | 143, yes | 143, yes | 143, yes |
| back at the prompt after the signal | 0.29 s | 0.30 s | 0.07 s | 0.40 s | 0.39 s |
| files compared (bytes) | 27 (0.15 MB) | 27 | 27 | 21 (1.15 MB) | 21 |
| last restart file: data (5.77 MB), `.prt` | identical | identical | identical | identical, identical | identical, identical |
| last restart file: parameters that differ | `<job> restart_file`, `file_number` of the restart output | the same | the same | the same | the same |
| files not byte-identical | mesh history (header) | the same | the same | mesh history (header), `tsq.cons.hst` (one record) | mesh history (header) |

The state is reproduced bit for bit: the last restart files agree in every byte of
their data and of the particle companion, and every table, snapshot, trajectory file,
particle history and constraint record is byte-identical. Two files are not, for
reasons that every restart has had and that the reference case R2 shows with the
release executable (core-v0.6, the same deck stopped by `time/nlim=26` and continued):

1. The mesh history `<basename>.z4c.user.hst` of the continued run has its two header
   lines a second time, where the continuation opened the file; its data lines are
   identical. (A release run stopped by the cycle or wall-clock limit has, in
   addition, the record of its final output twice and its tables renumbered, because
   `Driver::Finalize` writes every output there; the stop on the signal writes none of
   these.)
2. The conservation record of the deposited matter (`<particles> cons_dcycle`,
   `<basename>.cons.hst`) needs the deposits of the two cycles before; they are not in
   the restart file. A continuation that starts one or two cycles before a record is
   due loses that one record (S2: the record of cycle 27 after a stop with cycle 26; R2
   loses the same record), one that starts on another cycle loses none (S2b, stop with
   cycle 28: byte-identical). Known defect of the diagnostic, not of the state; listed
   for `stage/G2/OPEN.md`.

Not tested here: several MPI ranks (the reduction is two lines; the MPI build was not
rebuilt), a card run (the handler touches no device code; the card build of this branch
was not rebuilt with it: section 6), refinement (`.amr` companion), the scalar field
(`.sf`), asymptotically flat set-ups (their restarts differ at round-off with outflow
faces and refinement: CLAUDE.md), a signal that arrives inside a long elliptic solve
(answered only after it).

A restart file that the SIGKILL cut is recognised at the next start [VERIFIED with
files cut by hand to 30 and 90 per cent, with a cut `.prt` and with a missing `.prt`;
unregistered, `scratch/core/tmp/trunc_test`]: "CC z4c data not read correctly from rst
file, restart file is broken", "particle restart file ... is truncated", "cannot open
particle restart file ...", each with exit status 1 before "Setup complete". The chain
script matches "restart file" in these lines, renames the file `*.rst.bad` and tries the
one before (three attempts per job).

## 4. No signal, no change [run core-20261125-000233-...: see the journal, entry 13]

Byte regression of the serial processor build with the handler against release
core-v0.6 (`analysis/release/regress_v04.py`, twelve set-ups, no signal sent, the option
`dt_gauge` of the first item absent): the result is in entry 13 of the journal and in
READY.

## 5. Chain script `scripts/submit_chain.sh`

- On SIGTERM the job resubmits at once, while it still can, and then waits for the
  executable instead of leaving (when the batch script ends, Slurm ends the job and the
  executable loses its grace period). The next segment cannot start before the
  executable is gone (lock `chain/lock`, waited for up to 300 s). `chain/events.log` then
  says "the run stopped by itself N s after the signal: restart outputs written ..." or,
  with an executable without the handler, "the run ended N s after the signal without a
  restart file of its own".
- **An attempt cut by a signal does not count as a segment**: SIGTERM to the job
  (preemption, `scancel` without `--stop`) or a kill of the executable from outside,
  before the attempt has run for `ATHENA_WALL`. `chain/uncounted` holds their number;
  `MAX_SEGMENTS` caps `chain/segment` minus that. An attempt signalled after
  `ATHENA_WALL` (the executable did not stop at its own limit: Slurm's time limit) has
  had its segment and counts. `--status` prints attempts, uncounted and the cap.
- `MAX_TERM_IN_A_ROW` (environment at start, default 20): after that many attempts in a
  row ended by SIGTERM the chain is FAILED ("ended by SIGTERM N times in a row"); a
  segment that ends by itself resets the count. Outside kills keep their own cap
  `MAX_OUTSIDE_KILLS` (2).
- **No job after the last segment**: when the last counted segment ends at the wall
  clock without finishing the run, the chain is set to `FAILED (MAX_SEGMENTS=N reached
  after attempt M (K not counted); the run is not finished: raise MAX_SEGMENTS and give
  the start command again)` in that job; before, one more job was queued, waited its
  turn (3.5 hours in `C-20261123-025228-6ecb543`) and failed at its first line. The
  status word and the text "MAX_SEGMENTS=N reached" are as before, so tools that look for
  them still find them. The start command on a chain that has used its segments is
  refused with a message instead of queueing a job that fails.
- An executable with the handler that receives SIGTERM from outside the job (another
  project's `pkill`) now leaves a restart file and the line "Terminating on signal
  SIGTERM" with status 143: the script treats it as the outside kill it is (resubmit, at
  most `MAX_OUTSIDE_KILLS` in a row), where the rule "143 without a termination line"
  alone would have called it a failure.
- Chains started with the older script continue: the new settings take their defaults
  when `chain/config.sh` has no line for them.

Test without Slurm and without AthenaK (`scripts/tests/test_submit_chain.py`, fake
`sbatch` and a fake executable; run core-20261125-000640-5c4b644, PASS, 58 checks): the
six scenarios of the earlier fake-kill test keep their outcomes; ten attempts cut by
SIGTERM to the job with `MAX_SEGMENTS=3` leave the chain QUEUED each time, the fake
executable writes its restart file after the forwarded signal and before the job
leaves, the resubmission precedes it, and the three counted segments then end the chain
with 13 `sbatch` calls in all and none after the last (I); two wall-clock segments with
`MAX_SEGMENTS=2` end with two calls, not three (K), and the start command is then
refused (N); three SIGTERM in a row with `MAX_TERM_IN_A_ROW=2` fail the chain (L); an
outside SIGTERM answered with a restart file is resubmitted and not counted (M); an
executable without the handler is resubmitted as before (O); a signal after
`ATHENA_WALL` counts (P). Not tested: a real preemption by Slurm (it needs a job of the
other partition), and the timing of the 30 s.

## 6. What the tracks do

- Nothing in the decks. Use an executable with the handler (`core_step-limit` once its
  READY names it, release v0.7 after) and the `scripts/submit_chain.sh` of a `main` that
  holds this branch; a chain picks up a new script at its next start command (the path
  is stored in `chain/config.sh`), a new executable likewise (it is copied at start).
- Keep the rule of decision 0032: a restart file at least every ten minutes of wall
  time. The signal handler saves the minutes since the last one in the usual case; it
  does not when the node dies, the file system stalls, or the write does not fit the
  30 s.
- `MAX_SEGMENTS` is again the number of full segments a run may use; preemptions no
  longer need a margin in it.
- A sequencer that continued chains "cut by their segment cap" finds them in the same
  state as before (STATUS FAILED, "MAX_SEGMENTS=N reached" in `events.log`), one job
  earlier.
