---
paths:
  - "athenak/src/**"
  - "python/**"
  - "problems/**"
  - "cosmo/**"
  - "tracks/*/analysis/**"
  - "tracks/*/note/scripts/**"
---

# Numerics and runs (CLAUDE.md rules 4-6; brief 9.2, 13.3; decisions 0006, 0010)

- One code base: every simulation capability lives in this repository's AthenaK (`athenak/src/`),
  written by core; tracks specify, supply reference solutions and tests, and check independently.
  No outside simulation code is adopted, built or run.
- Every simulation and analysis run is registered: `harness/bin/nrpic-run submit --kind
  scouting|production --gate G<k> --purpose "..." [--launcher local|batch|chain] -- ...`; close it
  with `nrpic-run finish <run_id>`. Production runs need `--preregistered <plan>#<anchor>` and the
  previous gate's pass tag. Card jobs go through `scripts/gpu_batch.sh` and
  `scripts/submit_chain.sh`, wrapped by `nrpic-run` (budget of decision 0006).
- Prediction first: write in `JOURNAL.md` what you expect and what would refute it before the run;
  afterwards the outcome, failed predictions included. Name a cause only after a run in which it
  could have failed. Null results and failed runs stay on record.
- Convergence is three-way (particle number, mesh spacing, gauge or boundary) for G2 and later;
  report the order measured, not the order hoped for.
- A number enters a note only with a run id or a knowledge-base locator. Numbers come from the
  source, never from the brief.
- Every test gets figures as well as numbers, and you look at each PNG yourself.
- Threads: at most the cores of your allotment (16; kb 8); `nrpic-env exec --threads N` sets
  OMP_NUM_THREADS and the BLAS variables. Builds only in `build/` of your own worktree
  (`nrpic-env build`); if you change no source, use the main checkout's executables read-only.
