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

## Entry 2 (2026-11-25, 05:18 PST): item 2, what the source does, design, predictions

Read in the source [VERIFIED by reading]: `FastFlow::FastFlowLoop` (`z4c/fastflow.cpp`)
starts from the surface of the last successful search and ends at the first iteration
whose mass differs from the iteration before by less than `mass_tol_<n>` (absolute; 1e-2
when absent, 1e-5 m from `puncture_setup`). A search that starts within the tolerance of
the last surface therefore ends at its second iteration without moving the surface more
than one flow step: the reported surface lags the horizon until the change per step
exceeds the tolerance. This is the reading of Track D's plateaus (request
`finder-stopping-rule`: masses 1.3e-4 apart at `mass_tol` 1e-5, the reported mass about
six tolerances from the converged one [numbers of Track D, not recomputed here]); six
tolerances correspond to a contraction of about 0.86 per iteration [JUDGEMENT: geometric
series, 1/(1 - 0.86) = 7].
`Particles::NrpicPush` (`particles/nrpic.cpp:455`) uses a horizon for excision only while
`rr_min < 4.0*initial_radius`.

Design.
- `<fastflow> polish_iterations_<n> = N` (0 when absent): after the mass rule is first
  met the flow goes on for N iterations and the surface is then accepted; if
  `flow_iterations_<n>` ends first, the last surface is accepted. Failure checks stay
  active. A rule on the residual (summary column 9) is not added: its floor depends on
  the cell size and the angular grid (7e-9 in D's runs), so a threshold below the floor
  would end every search at the iteration limit; a fixed number of iterations has a
  fixed cost.
- `<particles> ah_exc_max_growth = g` (4 when absent): the factor of the guard.
Both are read only when present, so that the parameter dump of runs without them keeps
its bytes.

Predictions (deck `problems/tests/finder_polish.athinput`: vacuum puncture m = 1, finest
cells M/8, test particles, to t = 8 M, finder every 4 cycles; script
`analysis/restart_finder/finder_test.py`; processor build):
- P8. Deck as it is (`polish_iterations_0 = 0`) with the new executable and with the
  release: every output byte-identical.
- P9. Mass of the tight rule (`mass_tol` 1e-9, 4000 iterations) as reference. With
  `mass_tol_0 = 1e-2` and `polish_iterations_0 = 100`: within 2e-5 of the reference at
  every search (I expect below 1e-6: 0.86^100 = 3e-7 of the starting error). With
  `mass_tol_0 = 1e-2` alone: off by more than 2e-5 at most searches (the surface hardly
  moves once the change per iteration is below 1e-2). With the production rule 1e-5
  alone: off by up to about 1e-4 at some searches while the horizon moves in the
  coordinates (first 8 M of a puncture). With 30 polishing iterations: between the two
  (0.86^30 = 1e-2). Refuted for the new rule by any search more than 2e-5 from the
  reference, or by a search that the mass rule finds and the polished one loses.
- P10. Guard: with `ah_exc_max_growth = 0.6` (guard at 0.6 M; the horizon starts at
  0.5 M and grows) removals by reason 3 stop at the first search with `rr_min >= 0.6`
  and none follows; without the option (guard at 4 M) they continue to the end; until
  that time the two removal records are identical. With `ah_exc_max_growth = 4.0`
  written out: every output byte-identical to the run without the option. Refuted by a
  reason-3 removal after the guard radius is passed, or by a differing byte at 4.0.
- P11. Track D's V-1L dumps (M/8, 100 to 450 M; `finder_probe.py`, threaded build, one
  cycle from each dump, horizons: new rule from the stored radius, tight rule, D's
  production rule from outside, new rule from outside): the new rule with `mass_tol`
  1e-2 and 100 polishing iterations lies within 2e-5 of the tight rule at every dump,
  from the stored radius and from 2 M; the production rule from outside reproduces D's
  low plateau (about 6e-5 below). Refuted by a dump where the new rule is more than
  2e-5 off.
- P12. Cost: one flow iteration costs the same with or without the option, so a search
  with N polishing iterations costs at most N iterations more; timed on processors here
  and on a card in the card check.

## Entry 3 (2026-11-25, 05:36 PST): T1 first attempt stopped, by_binary too slow on the serial build

Run core-20261125-131225-9591922 (T1 with `--by-binary`): the periodic cases finished,
then the two-puncture deck at three levels ran at about 80 s per cycle on the serial
build (ten tracker records in 14 minutes); three runs of 24 cycles would have taken 95
minutes. Stopped by `nrpic-run stop` (recorded as failed; no summary was written, no
number is taken from it). The script now takes the threaded builds for that deck
(`--by-exe`, `--by-threads`) and 8 cycles cut at 4; T1 is run again without the deck and
the deck in a run of its own. Before the registered attempt an unregistered trial of the
script (debugging, `scratch/core/tmp/rf_smoke`, removed) showed that a cut by
`time/nlim` cannot serve as the reference of an interrupted run: a run that ends by
itself writes final outputs of every kind (one more table file, one more history record),
which an interrupted run does not have. The cuts are therefore made by SIGTERM.

## Entry 4 (2026-11-25, 05:40 PST): outcome of T1 (item 1), run core-20261125-133539-961dcbd

Registered run, serial processor build of commit 961dcbd (source of 1fb387d8), against
`.work/build_cpu_v07`; 256 s on one core; `summary.json`, `fig_restart_test.png` (looked
at: the tracker of the release starts at the cut, that of the new build is the whole
line; the records at t = 1.6875 are missing for the release cut at 26 and 27 and present
for the new build; header lines 4 against 2).

- P1 (release, before) HELD. Cut at cycle 24, 25, 26, 27 (the cycle of the continuation
  read back from its log): files differing from the uninterrupted run are the tracker
  file (24, 25, 26, 27 records missing), the mesh history (4 header lines against 2) and,
  for 26 and 27 only, `rso.cons.hst` (one record missing, t = 1.6875). Nothing else.
- P2 HELD. New build, cuts at 24, 25, 26, 27 and the run cut twice (14, then 27): all 17
  output files (760 873 bytes) byte-identical to the uninterrupted run; the last restart
  file and its `.prt` identical too. The weakest link held: the fields evaluated at the
  restart give the same digits as those of the uninterrupted run (cuts at 26 and 27).
  `.prt` sizes 2 933 160 bytes without and 3 064 280 bytes with the block (131 120 bytes
  = 8 + 32 + 8 + 4 x 4096 x 8).
- The uninterrupted run of the new build equals that of the release byte for byte (17
  files): the change does not touch a run that is not continued.
- P4 HELD. Continued from the restart file of cycle 20 after the first segment had run
  to 27: tracker file byte-identical to the uninterrupted run; `cons.hst`, `cstat.hst`,
  `nrpic.hst`, the mesh history and the two trajectory files hold the records of cycles
  20 to 27 twice, as before this work (not changed here; said in the interface text).
- Not yet run: P3 (S2 of `term_test.py`), P5 (two punctures), P6 (byte regression).

## Entry 5 (2026-11-25, 05:44 PST): prediction for T2 (restart files across executables)

Besides P3 (S2 and S1 of `term_test.py`), `restart_extra.py` continues a restart file of
the new executable that carries the block `NRPCNS01` with the release executable, and a
restart file of the release with the new executable.
- P13. Both continuations run to the end with status 0. Read in the source of the
  release: its reader of the `.prt` file stops after the accretion block or after eight
  bytes that are not `NRPACC01`, so the block is not read [VERIFIED by reading; the run
  is the test]. The release loses the record at t = 1.6875 as before. The new
  executable continuing a file of the release (cut at cycle 27, no block) lacks that
  record too, because the densities of cycle 26 are in no file, and no other record;
  cut at cycle 26 it would lose none (the fields of the restart suffice, as in T1).
  Refuted by a non-zero status, or by any other record missing or added.
