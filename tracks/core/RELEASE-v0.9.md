RELEASE core-v0.9 ad54460ed0675330e82f9813419b89284f06ecfa REGRESSION PASS, CARD CHECK PASS

Card check of the card executable of this source: PASS, every prediction held, run
core-20261128-052151-e5a2d55 (shared-queue entry q0094, label core-ff-card2, Slurm job
5601, COMPLETED 2026-11-28 05:39Z, eight cases in 24 s, 0.0067 card-hours), judged by the
registered analysis core-20261128-072820-d5fa2ca (`analysis/faces_finder/card_check.py`,
figure `fig_card_check.png` looked at). The first attempt q0086 (job 5544) was preempted
after 5 s and its run core-20261128-002929-335815e is closed as stopped.

# Release core-v0.9: branch core/faces-finder on top of core-v0.8

Prepared by the lead of core on 2026-11-28 UTC (2026-11-27 PST; batch 35), made final
after the card check in batch 40 (2026-11-28T07:40Z). The commit of
the first line is the source commit (last change of `athenak/`); `core/nrpic` holds it
through the merge 8139c969, and `git diff ad54460e 8139c969 -- athenak/src` is empty
[VERIFIED at 8139c969]; `python/`, `problems/`, `scripts/`, `docs/` are those of release
core-v0.8 (the branch did not touch them). Options, changes without an option, which runs
they change, what is not done: `tracks/core/CHANGELOG.md`, section core-v0.9. Interface
texts (to be copied to `coord/INTERFACES/` by the clerk): `tracks/core/interfaces/
level_faces.md`, `restart_parameters.md`, `finder_box.md`. Predictions and outcomes:
`tracks/core/JOURNAL.md`, entry 2026-11-28T02:02Z (R9, T9, Q9, V8), and
`JOURNAL-faces-finder.md` (D, C0, C1, R, S1-S4, CM, T, K); the card check: `JOURNAL.md`,
entry 2026-11-28T07:27Z and its outcome.

## What it adds, in one paragraph

Four options of the horizon finder, off when absent: `<fastflow> start_scan_<n>,
start_scan_rmin_<n>, start_scan_rmax_<n>` (start radius from a scan of round spheres;
reason 8 when none is trapped) and `trapped_tol_<n>` (accept only a star-shaped surface
whose rms expansion times area mass is below the value; reason 7 otherwise), with three
optional columns of the status file. Three changes without an option: the linear cloud
with `deposit_fine_shape` on a refined mesh leaves no dipole at a level face; the
compensated deposit (`deposit_comp_c > 0`) is conservative across faces between levels;
a run continued with `-r` takes parameters its restart file does not hold from the
command line. And a finding that needs no new source: in periodic boxes the finder's
default flow function is the reason for the cap of iterations; `<fastflow> flow = shear`
cures it in every release.

A fact for every deck that uses the finder, in every release (decision 0049 item 3; Track
C `finder-start-stop-defaults`): without `<problem> puncture_setup = true` the finder
searches only if the deck names `<fastflow> start_time_<n>` and `stop_time_<n>`; the
defaults (the largest double, -1) never search (`finder_box.md` section 0).

## Processor evidence (merged tree, serial build `wt/core/.work/build_cpu_v09rc`, 180 s on 6 jobs, sha256 b7a48e9a...)

| Check | Run | Result |
|---|---|---|
| R9 byte regression against release `.work/build_cpu_v08/src/athena`, twelve set-ups, 3 cores | core-20261128-020122-3a1a3dd (figure core-20261128-020936-0826227) | 75 of 75 items identical, classes a, b, a+b, other empty: REGRESSION PASS (R9 held). Figure looked at: twelve bars, one colour |
| T9 the branch's tests again with the merged build, outputs against the branch session's runs byte for byte (`rerun_compare.py`) | core-20261128-021251-d4575ac (first pass -021119-fb199ef failed on the scripts' own summary files: wall times, executable path) | 416 output files (AthenaK outputs, input decks, the scripts' tables): 371 identical, 45 identical after the run directory's name is replaced (input decks and restart files store the path), none differs, none missing; the scripts' verdicts equal. T9 HOLDS. Figure looked at |
| Q9 `restart_test.py` (restart outputs across cuts at every residue of the record interval and a chain) against release core-v0.8 | core-20261128-020910-9292e5d | ALL OK, 20 checks "ok": the uninterrupted run equals core-v0.8 byte for byte; cuts at 24, 25, 26, 27 and the chain give every output file byte-identical to the uninterrupted run, restart and `.prt` files identical. Q9 held. The reference cuts with core-v0.8 (labelled "v0.7" by the script) lose no tracker or `cons.hst` record and write two header lines, as written before the run. Figure looked at |
| M9 MPI build of the merged tree (`.work/build_cpu_mpi_v09rc`, `mpi_smoke_v08.py`): one rank against the serial build, two ranks against one | core-20261128-022409-4720043 | held: 17 files identical; two ranks equal to one rank (0.0). Uniform mesh: level faces between ranks (not corrected) not exercised. Figure looked at |
| Branch tests of the source session (deposit at level faces, conservation on three levels, cap between levels, parameters on restart, finder on Track A's files, threaded build) | `JOURNAL-faces-finder.md` entries 2 to 6 | held, except the split of C0 between the two faces (entry 4) and the standard flow's "not found within 400" of S2 (entry 5): both on record |

## T9 (the branch's tests with the merged build)

| Test (merged build) | Run | Verdict | Branch run compared |
|---|---|---|---|
| `dep_compare.py`, 16 deposit cases across a level face | core-20261128-020214-a173064 | as the branch: D held (`cic_fs` = `cic`, 14 tables identical to core-v0.8), C0 line sum 32 held, the split between the two faces failed as in entry 4 (-0.00755, -0.03377): closed failed by that check | core-20261127-234848-7d666df |
| `comp_cons.py`, random particles on three levels, ten steps | core-20261128-020250-1981d90 | COMP CONS PASS: largest error of the E integral 2.7e-14 (`pcs_c2`; core-v0.8 9.9e-4) | core-20261127-234843-fa6c2e9 |
| `diag_restart.py`, parameters added on restart | core-20261128-020255-72e53c6 | F1a to F1e held: case a (`-r rst fastflow/diagnostics=true`) starts and writes the status file | core-20261127-234458-4baaaa4 |
| `finder_bytes.py`, finder without the new options | core-20261128-020317-73134bb | PASS: files of core-v0.8 byte for byte | core-20261128-000807-e413b5e |
| `finder_box.py` on Track A's S1L restart file (t = 220), weighted flow, scan, `trapped_tol` | core-20261128-020447-28dbb9f | exit 0; every horizon file byte-identical to the branch run | core-20261127-235215-27c6606 |
| `cap_mid.py`, cap between the levels | core-20261128-020922-7d1da68 | CAP MID PASS | core-20261128-002502-76a25c3 |

## Executables

Published 2026-11-28T07:37Z by the lead of core in a new directory,
`/data/haiyangw/nrpic/scratch/core/exe/core_nrpic_v09/` (COMMIT, SHA256SUMS, READY there):
`athena_cpu` (serial; the build of R9, T9 and Q9, sha256 b7a48e9a...), `athena_cpu_mpi`
(Open MPI; the build of M9, a44b7c85...), `athena_cpu_omp` (threaded; copy of the branch's,
2e31b69e...) and `athena_gpu` (one A100; the executable that q0094 ran, 20172cae...), all
of the source tree ad54460e (`git diff ad54460e 2b741dee -- athenak/src python problems
scripts docs` empty at the time of publication). The branch's directory
`scratch/core/exe/core_faces-finder/` stays (its READY points here). The release builds
`.work/build_{cpu,gpu}_v09` in the main checkout are the clerk's.

## Card check

Run core-20261128-052151-e5a2d55: eight runs of the card build in one job (list
`analysis/faces_finder/card.list`), all with status 0. Judged against the processor runs
core-20261127-234848-7d666df (deposit across a level face), core-20261127-234843-fa6c2e9
(conservation on three levels) and core-20261127-235215-27c6606 (finder on Track A's S1L
file) by `card_check.py`; prediction K in `JOURNAL-faces-finder.md` entry 5, unchanged;
outcome in `JOURNAL.md` after the entry 2026-11-28T07:27Z.

| Prediction | Outcome |
|---|---|
| K1 the planar lines of `cic`, `cic_fs`, `pcs_comp` equal the processor run to 1e-12; `cic_fs` = `cic` to 1e-13; line sum of `pcs_comp` 32 to 1e-10 | held: `cic` and `cic_fs` 0.0 in every cell, `pcs_comp` 2.0e-15 (in the coarse cells beyond the face only); `cic_fs` - `cic` = 0.0; line sum 32.0 |
| K2 the three compensated cases on the refined mesh conserve the E integral against the sum of m W to 1e-12 at every record (a card-only failure would mean the level-face kernel is wrong on the device) | held: 9.92e-16 or 0 at each of 12 records in all three cases (one unit in the 16th digit the history prints); the processors gave 2.1e-14 to 2.7e-14 |
| K3 S1L with the weighted flow: every member found, masses within 1e-6 relative of the processors, column 16 within 1e-4, scan start within 1e-6 | held: six of six found with the processors' iteration counts; masses equal to 1e-15, column 16 to 3e-16, scan start 0.1615097240063816 identical |
| K4 a continued run takes `fastflow/diagnostics=true` on the command line | held: status 0, a status file with one record, the log line "Parameter added on restart from the command line" |

Verdict of the lead [VERIFIED for K1 to K4; JUDGEMENT that this suffices]: the release
passes its card check. The card check does not time the extra ghost exchanges, does not
test a chain, and runs the finder on one file.

## Not done in this release

Level faces between MPI ranks are not corrected (that face keeps two fluxes; several
ranks untested); the cost of the compensated deposit is measured only on processors in a
test without the spacetime solver (cubic cloud with c2 11.9 s before, 12.1 s now; plain
pass with the linear cloud 5.3 s and 10.7 s; run core-20261127-234843-fa6c2e9), not on a
card and not inside a coupled run; the ripple of the deposit at a level face for a
lattice of particles stays; the weighted flow on punctures, the scan for a horizon tied
to a puncture and parameters added inside a chain are untested; the false acceptance of
Track A's chain (P0L6 at t = 118.12) is not retested (no restart file between t = 110 and
120). CHANGELOG, section core-v0.9.

## For the release clerk

Merge `core/nrpic` into main; tag `core-v0.9` on the source commit of the first line
(ad54460e), or on the merge on main after comparing the source trees (`git diff ad54460e
<merge> -- athenak/src python problems scripts docs` empty); build `.work/build_gpu_v09`
and `.work/build_cpu_v09` from that source. Copy to `coord/INTERFACES/`: new
`tracks/core/interfaces/level_faces.md`, `restart_parameters.md`, `finder_box.md`;
changed `finder_stop.md` (two paragraphs: start and stop times; options added to a
continued run). CLAUDE.md row: the three changes without an option (item 2 changes every
refined run with `deposit_comp_c > 0`, Track A's nested meshes among them), the four
finder options, `flow = shear` for boxes, the start and stop times, executables
`scratch/core/exe/core_nrpic_v09/`. Compare a release build with core's `athena_cpu` by
`regress_v04.py` (75 items), not by checksums; a release card build can be checked with
`analysis/faces_finder/card.list` and `card_check.py` (0.01 card-hours by q0094).

How to repeat the checks:
```
cd /data/haiyangw/nrpic/wt/core
harness/bin/nrpic-run submit --kind scouting --gate G2 --launcher local --cores 3 --purpose "..." -- python3 tracks/core/analysis/release/regress_v04.py --base /data/haiyangw/nrpic/.work/build_cpu_v08/src/athena --new <athena_cpu> --out '$NRPIC_RUN_DIR' --cores 3
harness/bin/nrpic-run submit --kind scouting --gate G2 --launcher local --cores 1 --purpose "..." -- python3 tracks/core/analysis/faces_finder/card_check.py --card <card run dir> --dep /data/haiyangw/nrpic/scratch/core/core-20261127-234848-7d666df --cons /data/haiyangw/nrpic/scratch/core/core-20261127-234843-fa6c2e9 --s1l /data/haiyangw/nrpic/scratch/core/core-20261127-235215-27c6606 --out '$NRPIC_RUN_DIR'
```
