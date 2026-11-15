---
name: run
description: Register, start, follow and close a simulation or analysis run of the NRPIC-cosmology program with harness/bin/nrpic-run (manifest, checksums, budget of decision 0006). Use whenever a run, a test on the cards or a reproducible analysis is to be started, and to check the GPU-hour budget.
argument-hint: [submit|status|finish|verify|budget|stop] [args]
---
Every simulation and analysis run is registered (CLAUDE.md rule 4). `harness/bin/nrpic-run` does
it; never start athena, scripts/gpu_run.sh, gpu_batch.sh, submit_chain.sh or sbatch directly.

Before: write the prediction in JOURNAL.md (expected outcome, what would refute it); commit
everything (a dirty worktree is refused; the manifest records the commit).

Start (relative paths are relative to the worktree root):
- On the processors: `harness/bin/nrpic-run submit --kind scouting --gate G1 --purpose "..."
  [--cores N] [--background] -- python3 tracks/<ID>/analysis/x.py ...`; the command runs in the
  worktree root with $NRPIC_RUN_DIR = scratch/<ID>/<run_id>/ for its output.
- Several short AthenaK runs in one job on one card: `--launcher batch --list <file> [--wall
  00:45:00]`, lines `<name> <athinput> [athena args]` (wraps scripts/gpu_batch.sh).
- One run longer than an hour: `--launcher chain --gpu-hours H -- <athinput> [args]` (wraps
  scripts/submit_chain.sh; at most floor(H / 59 min) segments). The input needs a restart output
  block.
- `--exe` defaults to the main checkout's card executable; give your own build
  (`harness/bin/nrpic-env build gpu`) only if you changed source. `--input` adds files to checksum,
  `--parent` names runs whose outputs are inputs.
- Production runs: `--kind production --preregistered tracks/<ID>/stage/G<k>/PLAN.md#<anchor>`;
  refused before the previous gate's pass tag exists.

Follow and close: `nrpic-run status [<run_id>]`, `nrpic-run stop <run_id>`, then
`nrpic-run finish <run_id>` (records exit status, wall time, GPU-hours, sha256sums.txt; commits the
manifest). `nrpic-run verify <run_id>` re-checks outputs and inputs. `nrpic-run budget` shows the
GPU-hours used and reserved per gate against decision 0006; beyond the allotment the run is
refused, and raising it is asked of the user through the orchestrator.

After: the outcome in JOURNAL.md (failed predictions too), a figure for every test (look at it),
numbers in notes only with the run id.
