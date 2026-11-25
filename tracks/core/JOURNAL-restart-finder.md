# Journal of core/restart-finder (source session for release core-v0.8)

Branch `core/restart-finder` (worktree `wt/core-s4`), from `main` at 0b5c3e7d (release
core-v0.7 and the script changes of 2026-11-25). Task: `tracks/core/NEXT_SOURCE.md`
items 1 to 3. Package directory for tests: `tracks/core/analysis/restart_finder/`.

## Entry 1 (2026-11-25, 05:03 PST): what the source does now, design, predictions

Read in the source of this branch [VERIFIED by reading]:

- Tracker file: `CompactObjectTracker::OpenOutput` (`z4c/compact_object_tracker.cpp:87`)
  opens `<base>.co_<n>.txt` with `ofile.open(name)`, which truncates, and writes two
  header lines, at the first record of every start. A record is written at the last
  stage of every cycle with the cycle number before the increment, so a run continued at
  cycle N writes records N, N+1, ...: the earlier segment owns the records below N.
- Mesh history: `HistoryOutput::WriteOutputFile` (`outputs/history.cpp:420`) appends and
  writes the header when `header_written` of this process is false: once per start.
- `<base>.cons.hst`: `Particles::NrpicWriteConservation` (`particles/nrpic_io.cpp:662`)
  writes the record of cycle R from three states: all ten fields of cycle R-1, the four
  densities of cycle R-2, the step before, and the densities of cycle R. The arrays
  (`cons_old`, `cons_d2`, `cons_dt_prev`, `cons_valid`) are not in the restart file, so a
  run continued at cycle N cannot write the records of cycles N+1 and N+2.
- A continued run is known by `<job> restart_file`, which `main.cpp:298` sets when the
  run starts with `-r`.

Design.

- (a) Tracker: in a continued run the file is kept; the lines of cycles at or after the
  cycle the run starts with are removed first (a segment killed from outside after its
  last restart file leaves such lines; without the removal the appended file would hold
  them twice), then records are appended; header only when the file is new. A fresh
  start truncates as before.
- (b) Mesh history: no header in a continued run when the file exists and is not empty.
- (c) Conservation record: at the start of a continued run the ten fields are evaluated
  from the state of the restart (as a fresh run does at t = 0), which serves the record
  due two cycles later; for the record due one cycle later the four densities of the
  cycle before the restart and the previous step are carried in the `.prt` companion, in
  a block `NRPCNS01` that is written only when the record is due at the next cycle
  (one rank). Other restart files keep their bytes.

Predictions (tests T1 to T4 of `analysis/restart_finder/restart_test.py`, processor
build, deck `problems/tests/restart_outputs.athinput`: the deck of S2 plus a uniform shift
and a tracker, `cons_dcycle = 4`):

- P1. Before the change (release executable `.work/build_cpu_v07`): a run cut at cycle K
  and continued differs from the uninterrupted run in exactly three kinds of file: the
  tracker file (records below K missing), the mesh history (header lines twice), and
  `cons.hst` (one record missing for K = 4m+2 and K = 4m+3, none for K = 4m and 4m+1).
- P2. After the change, for K = 24, 25, 26, 27 (all residues of the record interval) and
  for a run cut twice (K = 14, then 27): every output file of the continued run is
  byte-identical to the uninterrupted run; the mesh history has two header lines; the
  record at t = 1.6875 is present for K = 26 and 27. Refuted by any differing byte in a
  file other than logs and restart files. The weakest link is (c) for K = 4m+2 and
  4m+3: the fields recomputed at the restart must equal those of the uninterrupted run
  bit for bit (deposit, metric and curvature at the restart), else digits of the record
  differ.
- P3. Case S2 of `analysis/preempt/term_test.py` (stop by SIGTERM at cycle 25 or later)
  with the new executable: no differing file (`files_differing` empty); the same case
  with the release executable differs in the two history files as in run
  core-20261125-023641-7a1c47d.
- P4. A continuation from an older restart file than the newest (the first segment ran
  past it, as after a kill from outside): the tracker file equals that of the
  uninterrupted run; the appended histories hold the overlapping records twice, as they
  did before (not changed here).
- P5. `problems/puncture/by_binary.athinput` (outflow faces, refinement; reduced to three
  levels, 24 cycles, cut at 12): the tracker files of the continued run hold the same
  cycles as the uninterrupted run, header once; values equal or different at round-off
  only (a restart of an asymptotically flat refined mesh is exact only up to round-off:
  CLAUDE.md), I expect below 1e-9.
- P6. Byte regression of 75 items against `.work/build_cpu_v07`: 75 of 75 identical (no
  item of it continues a run; if one writes a restart file one cycle before a
  conservation record its `.prt` grows by the block: then that item differs and is
  named).
- P7 (item 3). One figure script run twice writes byte-identical PDF files with the new
  `figstyle.save`, and different ones with the old (the creation date differs when the
  two runs are at least a second apart).
