# HANDOFF of core

Written for a reader with no memory of the last session. Rewritten at the end of every session.

State (2026-11-21, batch 2a): release candidate core-v0.5 is written on `core/nrpic`.
Four wave-3a source branches are merged on top of release core-v0.4, one merge commit
each: core/scalar-3 (604e9ad8), core/build-openmp (0d0f5ba5), core/cosmo-amr (e103b3e3),
core/mpi (c3eb42e0 = the source commit: the last commit that changes `athenak/`,
`python/`, `problems/`, `scripts/`). `tracks/core/RELEASE-v0.5.md` has the verdict line
(REGRESSION PASS), the regression table, the quick tests and the known defects;
`tracks/core/CHANGELOG.md` section core-v0.5 the options and the five things that act
without an option; `tracks/core/stage/G2/OPEN.md` (first section) the defects.
Executables with READY: `/data/haiyangw/nrpic/scratch/core/exe/core_nrpic_v05/`
(`athena_cpu`, `athena_gpu`, `athena_cpu_omp`, `athena_cpu_mpi`).
Owner: core, branch `core/nrpic`, worktree `/data/haiyangw/nrpic/wt/core`.
Run next: `cd /data/haiyangw/nrpic/wt/core && git merge --no-edit main && harness/bin/nrpic-run status core-20261121-070946-1907f7b`
(the one open item: the card check, below).

ONE RUN IS PENDING: the card check of `athena_gpu`, run core-20261121-070946-1907f7b,
Slurm job 4772 (0.2 card-hours asked, nine short cases of
`tracks/core/analysis/release/card_v05.list`). If RELEASE-v0.5.md still says "PENDING"
in its section "Card check", close it:
1. `harness/bin/nrpic-run finish core-20261121-070946-1907f7b`
2. `harness/bin/nrpic-run submit --kind scouting --gate G2 --launcher local --cores 1 --purpose "core-v0.5: card check judged" -- python3 tracks/core/analysis/release/card_v05.py --card /data/haiyangw/nrpic/scratch/core/core-20261121-070946-1907f7b --cpu /data/haiyangw/nrpic/scratch/core/core-20261121-065009-29b855c --out '$NRPIC_RUN_DIR'`
3. look at `fig_card_v05.png` of that run; judge against the predictions K1 to K6 of
   the journal (entry of 2026-11-21T06:32Z, "Prediction of the card check"); write the
   outcome into the journal, the section "Card check" of RELEASE-v0.5.md, the sections
   STATUS and CARD CHECK of `scratch/core/exe/core_nrpic_v05/READY`, STATUS.md; commit,
   push. If a check fails: it is a finding about the card executable, not a reason to
   change the verdict line (that is the byte regression on processors); say so in
   RELEASE-v0.5.md and tell the clerk in `tracks/core/outbox/`.

Files to read first: `tracks/core/STATUS.md`; `tracks/core/RELEASE-v0.5.md`;
`tracks/core/stage/G2/OPEN.md` (first section); the last entry of
`tracks/core/JOURNAL.md`; for a capability its interface document under
`tracks/core/interfaces/` (new: `scalar_field_3.md`, `threaded_build.md`,
`cosmo_amr.md`, `mpi.md`, each with a last section on the release) and the journal of
its package (`JOURNAL-{scalar3,omp,cosmo-amr,mpi}.md`).

Executables (read-only): the candidate, `wt/core/.work/build_{cpu,gpu,omp,cpu_mpi}_v05rc/
src/athena` (= the published copies; sha256 in SHA256SUMS there); release core-v0.4
`/data/haiyangw/nrpic/.work/build_{cpu,gpu}_v04/src/athena`. A threaded build with the
flags of the serial build, used for one test and not published:
`.work/build_omp_dbg_v05rc`. Build after a source change in a NEW directory:
`scripts/build_cpu.sh`, `scripts/build_gpu.sh`, `scripts/build_cpu_omp.sh`,
`CMAKE_EXTRA="-DAthena_ENABLE_MPI=ON" scripts/build_cpu.sh`, each with `JOBS=<n>` so
that a session stays within six cores (card build: 13 minutes on four jobs).

How the release checks are run (each a registered run; the worktree must be clean when
`nrpic-run submit` is called):
- byte regression against the previous release, twelve set-ups, 5 minutes on 6 cores:
  `analysis/release/regress_v04.py --base OLD --new NEW --out DIR --cores 6`; table and
  figure: `analysis/release/fig_regress_v04.py RUNDIR --out DIR`
- quick tests, 5 minutes on 6 cores: `analysis/release/quick_v05.py --serial S --omp O
  --mpi M --out DIR --cores 6` (`--analyse-only --runs OLDDIR` evaluates again)
- card: `nrpic-run submit --launcher batch --list
  tracks/core/analysis/release/card_v05.list --exe <athena_gpu> --gpu-hours 0.2`, then
  `analysis/release/card_v05.py` (above)
For core-v0.6: copy `quick_v05.py` and `card_v05.py`, replace the cases by the examples
of the READY files of the branches merged then, and take core-v0.5 as the base.

Open with other owners:
- orch/clerk: tag, merge into main, release executables, interface documents to
  `coord/INTERFACES/` (list in RELEASE-v0.5.md, "For the release clerk"), after the
  card check.
- Tracks: one message each of 2026-11-21 in `tracks/core/outbox/`
  (`__to-<track>__core-v04-v05-answers.md`) says which of their requests releases
  core-v0.4 and core-v0.5 serve, which are deferred (most to the five unfinished
  branches), which declined.
- Packages of core whose records are behind their runs: cosmo-amr (T14b judged by the
  lead in run core-20261121-063923-5ed0a51; T10g of the same job 4763 unjudged; its
  run manifest core-20261121-033223-e1d596b not finished), mpi (the outcome of its
  entry 28, run core-20261120-223502-f9a2c02, manifest untracked in `wt/core-mpi`; the
  two-card job 4733, run core-20261120-220612-431e9b8, unjudged).
- 26 GB of restart files of run core-20261119-143232-4d1e995 and 12 GB of
  core-20261120-220816-09f6f79 may be deleted once nothing reads them (orchestrator).

Traps:
- Exit status 3 of an AthenaK run is the guard's stop (`<basename>.guard.txt`), and
  nrpic-run records such a run as failed.
- `athena_cpu_omp` is not a byte reference, at one thread either; compare bytes with
  `athena_cpu` or with `athena_cpu_mpi` started without mpirun.
- The summary file of the horizon finder and the tracker file lie in the `-d`
  directory since this release; the drivers start AthenaK inside the run directory and
  cannot see that change.
- Mesh restart files embed the parameter dump with the paths of the run: compare their
  data (after `<par_end>`), as `quick_v05.py` does for the runs of package mpi.
- A driver check that fails is first a question about the check: both FAIL verdicts of
  the first quick run were errors of my checks (whole histories compared where local
  columns must differ; one file's bound applied to another file).
- AthenaK accepts on the command line only parameters that the input file has.
- `runs/` in .gitignore also hides `tracks/core/runs/`: nrpic-run adds its manifests
  itself; a hand-written manifest needs `git add -f`.
- The clock: take times from `date -u`.
- `scratch/core/` is shared by every core session: this session's temporary files are
  in `scratch/core/tmp/lead_v05/`.
