# Outputs that survive a restart: tracker file, mesh history, conservation record

Owner core. Release **core-v0.8** (branch `core/restart-finder`, batch 18, 2026-11-25,
merged into `core/nrpic` at b755cdcf; item 1 of `tracks/core/NEXT_SOURCE.md`). Ready to be
copied to `coord/INTERFACES/restart_outputs.md` by the release clerk. Evidence and every
number: `tracks/core/JOURNAL-restart-finder.md` (predictions before, outcomes after, run
ids); scripts `tracks/core/analysis/restart_finder/restart_test.py`, `restart_extra.py`;
deck `problems/tests/restart_outputs.athinput`. Executables of the release:
`/data/haiyangw/nrpic/scratch/core/exe/core_nrpic_v08/` (READY there); the branch's own
`scratch/core/exe/core_restart-finder/` holds builds of the same source.

In one paragraph: a run that is cut (preemption, time limit, `scancel`) and continued
with `-r <restart file>` wrote three of its files differently from a run that was never
cut: the tracker file `<base>.co_<n>.txt` started again at every start and lost the
earlier trajectory; the mesh history got its two header lines again; and the
conservation record `<base>.cons.hst` lost one record when the restart file was written
one or two cycles before the record was due. All three are corrected, without an option.
A run that is never continued is not changed (section 5).

## 1. What changes, and for whom [VERIFIED: section 4]

| File | Release core-v0.7 | Now |
|---|---|---|
| `<base>.co_<n>.txt` (compact-object tracker; every deck with `<z4c> co_<n>_type` or `puncture_setup`) | opened with truncation at the first record of every start: a continued run holds the records from its own first cycle on, the earlier ones are gone | a run started with `-r` keeps the file, removes the records of cycles at or after its first cycle, and appends; header (two lines) only when it starts a new file |
| `<base>.z4c.user.hst`, `<base>.z4c.hst` and the other histories of `file_type = hst` | two header lines again at every start | no header when the run is started with `-r` and the file exists and is not empty |
| `<base>.cons.hst` (`<particles> cons_dcycle > 0`) | the record due one or two cycles after the restart is missing | no record is missing (one rank, uniform mesh; section 3) |

Nothing has to be set. A chain that was cut many times gives, in these three files, the
lines of the run that was never cut.

## 2. How a continued run is recognized

`main.cpp` sets `<job> restart_file` when the run is started with `-r` (it did so before
this work; the companions `.prt`, `.amr`, `.sf` are found through it). The tracker and
the history writer ask for that parameter. A fresh start (`-i` only) behaves as before
in every respect: the tracker file is started again, the mesh history is appended to
with a header (also when a file of an older run lies in the directory; unchanged).

## 3. The three corrections

**Tracker** (`z4c/compact_object_tracker.cpp`: `OpenOutput`, `TrimForRestart`). The
record of cycle n is written during that cycle with the cycle number before the
increment, so a run continued at cycle N writes the records N, N+1, ... and the earlier
segments own those below N. At its first record a continued run reads the existing
file, keeps the header and the records of cycles below N, drops the others and a last
line without its end (a segment that was killed after its last restart file, by SIGKILL
or a node failure, has written records beyond the restart; without the removal they
would be in the file twice), rewrites the file through `<name>.tmp` only if a line was
dropped, and appends. If there is no file with a header, it starts one. A continued run
that ends before its first record leaves the file untouched.

**Mesh history** (`outputs/history.cpp`, `WriteOutputFile`). When the run is continued
and the file is not empty the header is taken as written.

**Conservation record** (`particles/nrpic_io.cpp`: `NrpicConsStartRestart`,
`NrpicConsWriteRestart`, `NrpicConsReadRestart`). The record of cycle R is built from
the ten fields of cycle R-1, the four densities of cycle R-2, the densities of cycle R,
and the two steps between them. A restart file of cycle N holds none of them. Now:
- at the start of a continued run the ten fields are evaluated from the state of the
  restart (deposited sources, metric, extrinsic curvature), exactly as a fresh run
  evaluates those of t = 0. This serves the record due at N+2 and costs one evaluation;
- when a record is due at N+1, the particle restart file `<rst>.prt` ends with a block
  `NRPCNS01`: the four densities of cycle N-1 on the active cells and the step before
  the dump (format: `docs/FORMATS.md`). Size 32 bytes per cell (4096 cells: 131 120
  bytes). The block is written only into restart files of cycles N with
  (N+1) mod `cons_dcycle` = 0: with `cons_dcycle = 1` into every restart file, with
  `cons_dcycle = 4` into one in four on average.

## 4. Tests (processors; every run registered, outputs under `scratch/core/<run id>/`)

T1, run core-20261125-133539-961dcbd (`restart_test.py`; deck
`problems/tests/restart_outputs.athinput`: 16^3 cells in eight MeshBlocks, periodic, 4096
particles with deposit, a tracker that moves and crosses a periodic face, history,
conservation record every four cycles, 48 cycles; cuts by SIGTERM):

| Case | Release core-v0.7 | New build |
|---|---|---|
| cut at cycle 24 | tracker file lacks 24 records; mesh history 4 header lines against 2 | all 17 output files byte-identical to the uninterrupted run |
| cut at 25 | tracker lacks 25; header 4 against 2 | byte-identical |
| cut at 26 (two cycles before a record) | tracker lacks 26; header; `cons.hst` lacks the record at t = 1.6875 | byte-identical |
| cut at 27 (one cycle before) | tracker lacks 27; header; `cons.hst` lacks that record | byte-identical |
| cut twice (14, then 27) | not run | byte-identical |
| continued from the restart file of cycle 20 after the first segment ran to 27 | not run | tracker file byte-identical; the other appended files hold cycles 20 to 27 twice (section 6) |

The last restart file and its `.prt` of every continued run equal those of the
uninterrupted run. The uninterrupted run of the new build equals that of the release
byte for byte. Figure: `fig_restart_test.png` of the run.

T2, run core-20261125-134353-9f7fdc3 (`restart_extra.py`): case S2 of
`analysis/preempt/term_test.py` (problems/tests/term_signal_particles.athinput, SIGTERM,
restart file at cycle 26): new build, none of 21 files differs and the record at
t = 1.6875 is present; release: `tsq.cons.hst` (that record missing) and
`tsq.z4c.user.hst` (four header lines against two). Case S1 (no particles, stop at cycle
101): new build, none of 27 files differs; release: the mesh history header. Figure:
`fig_restart_extra.png` of the run.

T4, run core-20261125-134356-4a92c73: byte regression of the serial build against
release core-v0.7, twelve set-ups, 75 of 75 items identical.

T3, run core-20261125-142953-bf5a228 (figure: core-20261125-145908-fbd5598,
`fig_tracker_restart.png`): `problems/puncture/by_binary.athinput` reduced to three
refinement levels (176 MeshBlocks, outflow faces), 8 cycles, cut at 4 by `time/nlim`,
threaded builds on one thread. Both tracker files of the continued run of the new build
are byte-identical to those of the uninterrupted run (8 records, header once); those of
release core-v0.7 hold the 4 records from cycle 4 on. No round-off difference appeared
in these 8 cycles; longer runs on such meshes can show one (section 6).

T1 again with the final serial build: run core-20261125-142556-a424739, all checks hold.
The card check: section 7.

## 5. What does not change

- A run that is never continued: no byte (T1, the uninterrupted run against the
  release; byte regression, section 7).
- The state of a continued run: the three corrections touch output files and one
  diagnostic array; restart files written later are identical (T1).
- The summary of the horizon finder, the particle histories and the trajectory files
  appended before and append now.

## 6. Limits [VERIFIED where a test is named, else JUDGEMENT from the source]

- Only the tracker file is cleaned of records beyond the restart. A segment that was
  killed without a restart file at its end (SIGKILL, node failure) leaves the cycles
  between its last restart file and its end twice in the other appended files (mesh
  history, `nrpic.hst`, `cstat.hst`, `cons.hst`, trajectories), as before (T1, case
  "continued from the restart file of cycle 20"). A stop on SIGTERM writes its restart
  file at the last cycle and leaves no such overlap (`preempted_runs.md`).
- A cut by `time/nlim` is not an interruption: a run that ends by itself writes final
  outputs of every kind (one more table, one more history record), so its continuation
  differs from an uninterrupted run in those, as before.
- Conservation record on several ranks: the block is not written (the arrays live on
  the ranks); the record due two cycles after the restart is recovered, the one due at
  the next cycle is still lost. Not tested on several ranks.
- The record needs the fields evaluated at the restart to equal those of the
  uninterrupted run. They do on processors in T1 (identical digits). On a card the
  deposit is not reproducible from run to run, so a continued card run differs from an
  uninterrupted one in the last digits of every record anyway.
- Asymptotically flat set-ups with refinement: the mesh state after a restart differs
  at round-off (CLAUDE.md), so the tracker lines of a continued run equal those of the
  uninterrupted run only to that precision (T3).
- The drift-control file of upstream AthenaK (`WriteDriftControl`) is not touched.

## 7. Restart files across releases, and what is still open

Restart files across releases [VERIFIED, T2, run core-20261125-134353-9f7fdc3]: a
restart file of the new build whose `.prt` ends with the block is continued by release
core-v0.7 to the end (its reader stops before the block); a restart file of core-v0.7
is continued by the new build to the end. In both cases the record due at the next
cycle is missing, because one of the two executables has no densities of the cycle
before, and no other record is touched. A chain that changes executable at a restart
loses at most that one record.

On a card [VERIFIED, card build of source 01d4aeeb, run core-20261126-070946-7971fde
(shared-queue entry q0049, job 5364), judged by run core-20261126-114747-a6f2385, journal
entry 23]: the restart deck with restart files every seven cycles gives the 48 tracker
cycles with one header, the twelve records of `cons.hst` identical to those of the
processor build, and the block in the restart files written one cycle before a record;
the card continues a restart file that the processor build wrote on SIGTERM at cycle 27
(with the block) and writes the six remaining records identical to those of the
processors, the first at t = 1.6875. Restart files therefore pass between the card and the
processor builds of core-v0.8 in both directions as far as tested (processor to card).

Still open: several ranks (not tested; from the source only the record due two cycles after a restart is recovered,
section 6), and the record of a restart written by a build of core-v0.7 (lost, as above).
