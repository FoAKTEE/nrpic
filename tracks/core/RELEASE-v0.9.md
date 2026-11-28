RELEASE core-v0.9 ad54460ed0675330e82f9813419b89284f06ecfa REGRESSION PASS, CARD CHECK PENDING: NOT RELEASED

NOT RELEASED. The release clerk does not merge or tag this candidate until the card check
of its card executable has run and been judged (shared-queue entry q0094, label
core-ff-card2, priority 2; the first attempt q0086, Slurm job 5544, was preempted after
5 s although the queue listed it as done). When it has passed, this file is rewritten in
the form of `RELEASE-v0.8.md` (first line "CARD CHECK PASS") and the executables are
published under `scratch/core/exe/core_nrpic_v09/`; not before.

# Release candidate core-v0.9: branch core/faces-finder on top of core-v0.8

Prepared by the lead of core on 2026-11-28 UTC (2026-11-27 PST; batch 35). The commit of
the first line is the source commit (last change of `athenak/`); `core/nrpic` holds it
through the merge 8139c969, and `git diff ad54460e 8139c969 -- athenak/src` is empty
[VERIFIED at 8139c969]; `python/`, `problems/`, `scripts/`, `docs/` are those of release
core-v0.8 (the branch did not touch them). Options, changes without an option, which runs
they change, what is not done: `tracks/core/CHANGELOG.md`, section core-v0.9. Interface
texts (to be copied to `coord/INTERFACES/` by the clerk): `tracks/core/interfaces/
level_faces.md`, `restart_parameters.md`, `finder_box.md`. Predictions and outcomes:
`tracks/core/JOURNAL.md`, entry 2026-11-28T02:02Z (R9, T9, Q9, V8), and
`JOURNAL-faces-finder.md` (D, C0, C1, R, S1-S4, CM, T, K).

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

## Processor evidence (merged tree, serial build `wt/core/.work/build_cpu_v09rc`, 180 s on 6 jobs, sha256 b7a48e9a...)

| Check | Run | Result |
|---|---|---|
| R9 byte regression against release `.work/build_cpu_v08/src/athena`, twelve set-ups, 3 cores | core-20261128-020122-3a1a3dd (figure core-20261128-020936-0826227) | 75 of 75 items identical, classes a, b, a+b, other empty: REGRESSION PASS (R9 held). Figure looked at: twelve bars, one colour |
| T9 the branch's tests again with the merged build, outputs against the branch session's runs byte for byte (`rerun_compare.py`) | core-20261128-021251-d4575ac (first pass -021119-fb199ef failed on the scripts' own summary files: wall times, executable path) | 416 output files (AthenaK outputs, input decks, the scripts' tables): 371 identical, 45 identical after the run directory's name is replaced (input decks and restart files store the path), none differs, none missing; the scripts' verdicts equal. T9 HOLDS. Figure looked at |
| Q9 `restart_test.py` (restart outputs across cuts at every residue of the record interval and a chain) against release core-v0.8 | core-20261128-020910-9292e5d | ALL OK, 20 checks "ok": the uninterrupted run equals core-v0.8 byte for byte; cuts at 24, 25, 26, 27 and the chain give every output file byte-identical to the uninterrupted run, restart and `.prt` files identical. Q9 held. The reference cuts with core-v0.8 (labelled "v0.7" by the script) lose no tracker or `cons.hst` record and write two header lines, as written before the run. Figure looked at |
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

## Card check (PENDING)

Shared-queue entry q0094 (core-ff-card2, priority 2, 0.2 card-hours asked), list
`tracks/core/analysis/faces_finder/card.list`, executable
`/data/haiyangw/nrpic/scratch/core/exe/core_faces-finder/athena_gpu` (built from
ad54460e; untested on a card). Prediction K of `JOURNAL-faces-finder.md` entry 5,
unchanged: K1 the three planar deposit cases equal the processor run in every cell of the
line to 1e-12, `cic_fs` equals `cic` to 1e-13, line sum of `pcs_comp` 32 to 1e-10; K2 the
three compensated cases on the refined mesh conserve to 1e-12 at every record (a
card-only failure would mean the level-face kernel is wrong on the device); K3 the S1L
probe with the weighted flow: every member found, masses within 1e-6 relative of the
processor run, column 16 within 1e-4, scan start within 1e-6; K4 a continued run takes
`fastflow/diagnostics=true` on the command line. To judge it, from `wt/core`:

    sacct -j <job> --format=JobID,State,ExitCode,Elapsed   # COMPLETED, not PREEMPTED
    harness/bin/nrpic-run finish <run id of q0094>
    harness/bin/nrpic-run submit --kind scouting --gate G2 --launcher local --cores 1 \
      --purpose "judge the card check of core-v0.9 (K1-K4)" -- \
      python3 tracks/core/analysis/faces_finder/card_check.py --card <its output dir> \
      --dep /data/haiyangw/nrpic/scratch/core/core-20261127-234848-7d666df \
      --cons /data/haiyangw/nrpic/scratch/core/core-20261127-234843-fa6c2e9 \
      --s1l /data/haiyangw/nrpic/scratch/core/core-20261127-235215-27c6606 --out '$NRPIC_RUN_DIR'

## Executables

None published for the release yet. For scouting, the branch's executables of the same
source stay at `/data/haiyangw/nrpic/scratch/core/exe/core_faces-finder/` (athena_cpu,
athena_cpu_omp, athena_gpu; COMMIT ad54460e; READY). After the card check passes:
`scratch/core/exe/core_nrpic_v09/` with athena_cpu (the R9 build), athena_cpu_mpi (to be
built), athena_cpu_omp and athena_gpu (copies of `core_faces-finder`, same tree),
COMMIT, SHA256SUMS, READY.

## Not done in this release

Level faces between MPI ranks are not corrected (that face keeps two fluxes; several
ranks untested); the cost of the compensated deposit is measured only on processors in a
test without the spacetime solver (cubic cloud with c2 11.9 s before, 12.1 s now; plain
pass with the linear cloud 5.3 s and 10.7 s; run core-20261127-234843-fa6c2e9), not on a
card and not inside a coupled run; the ripple of the deposit at a level face for a
lattice of particles stays; the weighted flow on punctures, the scan for a horizon tied
to a puncture and parameters added inside a chain on a card are untested; Track A's
false acceptance at t = 118.12 cannot be retested. CHANGELOG, section core-v0.9.
