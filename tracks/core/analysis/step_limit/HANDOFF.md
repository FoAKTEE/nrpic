# HANDOFF of the package step-limit (core, branch core/step-limit, worktree wt/core-s3)

For a reader with no memory. The owner's own HANDOFF (`tracks/core/HANDOFF.md`) belongs
to core's lead on `core/nrpic` and is not written from this branch.

State (2026-11-24 18:10 PST, batch 13): both items of the package are implemented,
tested on processors, documented and published. The last processor test (Track A's
refined deck with the option, journal entry 16) ended at 18:04. One thing is open: the
card job below.

1. Step limit of the gauge sectors, `<z4c> dt_gauge` (W31): `athenak/src/z4c/
   z4c_newdt_gauge.cpp` and hooks; `tracks/core/interfaces/step_limit.md`.
2. Preempted runs: `athenak/src/utils/term_signal.{hpp,cpp}` and hooks in `main.cpp`,
   `driver/driver.cpp`; `scripts/submit_chain.sh`; `tracks/core/interfaces/
   preempted_runs.md`.

Journal with every prediction and outcome: `tracks/core/JOURNAL-step-limit.md` (entries
0 to 8 first session, 9 onward second). Executables: `/data/haiyangw/nrpic/scratch/core/
exe/core_step-limit/` (source 5c4b644f; READY). How to rerun every test:
`tracks/core/analysis/step_limit/README.md`.

Card runs in the shared queue (`harness/bin/nrpic-queue show <id>`):

- **q0036**, label `step-limit-card`, priority 5, added 2026-11-24 15:32 PST: one batch
  job, list `tracks/core/analysis/step_limit/card_refined.list` (R0, R0g, R1 of Track A's
  refined periodic deck), executable `core_step-limit/athena_gpu`, 25 minutes of wall
  time at most. It is the test T4 on a card and the first run of the final card build.

Run next:

1. When q0036 has run: `harness/bin/nrpic-run finish <run id>` (the run id is in
   `nrpic-queue show q0036`), then the analysis
   `python tracks/core/analysis/step_limit/analyse_runs.py --run R0=<dir>/R0:0.01953125
   --run R0g=<dir>/R0g:0.01953125 --run R1=<dir>/R1:0.01953125 --bound 0.656 --tmax 6
   --name refined_card --out '$NRPIC_RUN_DIR'` through `nrpic-run submit`; judge P4a to
   P4c of journal entry 3 (with the bounds of entry 9); write the outcome as a new
   journal entry, strike the first item of section 5 of `READY.md`, publish it
   (`publish_exe.sh 5c4b644f ready`).
2. Merge into `core/nrpic` for release v0.7 (lines touched in shared files: section 8 of
   `step_limit.md`, section 2 of `preempted_runs.md`; outbox to orch of 2026-11-25T00:43Z).
3. Not done, named for a later session: the stop on SIGTERM on a card, on several MPI
   ranks and with refinement; a survey of the tracks' puncture and horizon decks with
   `dt_gauge = 1.0` before the option could become the default; the two restart defects
   of `*.cons.hst` and of the history header (for `stage/G2/OPEN.md`).
