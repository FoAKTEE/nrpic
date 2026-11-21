# HANDOFF of core

Written for a reader with no memory of the last session. Rewritten at the end of every session.

State (2026-11-21, batch 3, session core-lead-5): release candidate core-v0.6 is written
on `core/nrpic` and pushed: `tracks/core/RELEASE-v0.6.md`, first line
`RELEASE core-v0.6 984bde68c6201c8f100ced3d6a7effbea9cafd80 REGRESSION PASS`. Merged on
top of release core-v0.5, one merge commit each: core/newton-2 (a1fffa58), core/z4c-faces
(1419f19a), core/id-solver-2 (984bde68, the source commit). Executables:
`/data/haiyangw/nrpic/scratch/core/exe/core_nrpic_v06/` (four, with COMMIT, SHA256SUMS,
READY, branches/). It is NOT on main yet: the release clerk merges and tags.
Owner: core, branch `core/nrpic`, worktree `/data/haiyangw/nrpic/wt/core`.
Run next: `cd /data/haiyangw/nrpic/wt/core && git merge --no-edit main && harness/bin/nrpic-run status core-20261121-132052-f330004`

ONE RUN IS PENDING: the card check of the merged card executable, run
core-20261121-132052-f330004, Slurm job 4800 (0.3 card-hours asked; queued behind seven
jobs of other owners at 13:45Z). Prediction K6 is in the journal (entry of
2026-11-21T12:55Z). To close it (the worktree must be clean for `nrpic-run submit`):
1. `harness/bin/nrpic-run finish core-20261121-132052-f330004`
2. the two `nrpic-run submit ... card_v06.py` and `... card_v05.py` commands printed in
   `tracks/core/RELEASE-v0.6.md`, section "Card check of `athena_gpu`"
3. look at `fig_card_v06.png` and `fig_card_v05.png`; write the outcome against K6 into
   that section (replace "PENDING" there and in the second line of the file), into the
   line `athena_gpu` of `scratch/core/exe/core_nrpic_v06/READY` and into the journal;
   commit, push. `card_v06.py` judges the six new cases (bounds: Newtonian history 1e-10,
   histories with the faces options 1e-7, solver iterations equal and psi_max to 1e-12,
   1e-9 on the refined mesh); `card_v05.py` the nine cases of core-v0.5 (K1 to K6 of that
   release). If a bound fails by a ratio of rounding-level residuals in a constraint
   column (as trk column 15 for core-v0.5), say so and judge on the absolute numbers.

Files to read first: `tracks/core/STATUS.md`; the last entry of `tracks/core/JOURNAL.md`
(with the faults of the session); `tracks/core/RELEASE-v0.6.md`;
`tracks/core/stage/G2/OPEN.md` (first section, core-v0.6: branches left out, limits a
to o); `tracks/core/CHANGELOG.md`, section core-v0.6.

Decided in this session (journal, 12:55Z):
- the default `id_far = multipole` of the initial-data solver stands (it changes solved
  data against core-v0.5 on meshes with no periodic face; `id_far = robin` restores the
  bytes for matter at rest);
- the nine never-set members of the mesh header needed no change: zero since core-v0.4.

Left out of core-v0.6, for the next release:
- core/clump-table: not closed when the candidate was built. At 13:37Z its tip
  (099882b3) had "merge notes for core's lead in the interface text"; read its report
  and READY when its session has returned, then review, merge, regress as below.
- core/oblate: tip 4f01a81f of 2026-11-20, does not hold core-v0.5; it must merge main
  and publish executables with READY first.

How the release checks run (registered; the worktree clean at `nrpic-run submit`):
byte regression `analysis/release/regress_v04.py --base OLD --new NEW --out DIR --cores 3`
(6 min) and `fig_regress_v04.py RUNDIR --out DIR`; quick tests `quick_v06.py --new NEW
--base OLD --out DIR --regress REGRESSION_RUN` (3 min; `--redraw OLDDIR` draws again);
the solver's `analysis/idsolve2/regress_m1.py` (it overwrites the package's
`regress_m1.json` and `figs/regress_m1.pdf`: restore them with `git checkout --`) and
`regress_r2.py --tag _<release> --same <case directories>`; a build that is not a byte
reference: `hst_pair_v06.py REGRESSION_RUN --out DIR`; card `nrpic-run submit --launcher
batch --list analysis/release/card_v06.list --exe <gpu> --gpu-hours 0.3`. For the next
release: copy `quick_v06.py`, `card_v06.py` and the list, put in the examples of the
branches merged then, take core-v0.6 as the base.

Executables (read-only): candidate `scratch/core/exe/core_nrpic_v06/`; release
core-v0.5 `.work/build_{gpu,cpu}_v05` (main checkout) and `scratch/core/exe/core_nrpic_v05/`;
older releases `.work/build_{gpu,cpu}_v04`, `_v03`. Build directories of the candidate
in `wt/core/.work/`: `build_cpu_v06rc`, `build_gpu_v06rc`, `build_omp_v06rc`,
`build_cpu_mpi_v06rc` (the card list of job 4800 names `build_gpu_v06rc`: do not rebuild
there before the job has run).

Open with other owners:
- orch/clerk: merge `core/nrpic` into main, tag `core-v0.6`, release builds, copy
  `z4c_faces.md`, `id_solver2.md`, `REQUESTS_NEWTON2.md`, `newtonian_mode.md` to
  `coord/INTERFACES/`, announce the default far field of `id_solve` (section "For the
  release clerk" of `RELEASE-v0.6.md`).
- Tracks: no outbox message was written in this session; the packages newton2 and faces
  wrote theirs. Tracks A, D, F should learn of the far-field default with the clerk's
  announcement.
- Requests triaged in `REQUESTS_WAVE3.md` and accepted without a branch are unchanged
  (W1, W2, W6, W15, W16, W18, W22).

Traps:
- A full commit hash is copied from `git rev-parse`: this session first wrote forty
  digits by hand into the release file (corrected before the push; journal).
- `regress_m1.py` and `analyze_k.py` of package idsolve2 copy their results into the
  package directory: tracked files change or new files appear, and `nrpic-run submit`
  refuses a dirty tree until they are restored or committed.
- `an_batch.sh k1.txt` of package faces ends with status 1 although the data agree: it
  lists the card's log files as missing.
- Exit status 3 of an AthenaK run is the guard's stop; `athena_cpu_omp` is not a byte
  reference; `runs/` in .gitignore hides `tracks/core/runs/` (a hand-written manifest
  needs `git add -f`).
- The clock: `date -u`. Temporary files of the lead: `scratch/core/tmp/lead_v06/`.
