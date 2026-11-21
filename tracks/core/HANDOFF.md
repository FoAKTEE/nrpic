# HANDOFF of core

Written for a reader with no memory of the last session. Rewritten at the end of every session.

State (2026-11-21, batch 2b, session core-lead-4): release core-v0.5 is on main (tag on
c3eb42e0; release executables `/data/haiyangw/nrpic/.work/build_{gpu,cpu}_v05/src/athena`,
named in CLAUDE.md). This session closed what the merge left open: the card check of the
candidate (PASS), the release processor build against the candidate (75 of 75 identical),
the open card results of packages cosmo-amr (T14b Sf, T10g) and mpi (job 4733, P7g), the
answers to every track (`tracks/core/outbox/20261121T0812*__to-<track>__core-v04-v05-answers.md`
plus two replies of 08:13Z to A and C, `szekeres-dumps-kij-answer`, `collisions-ranks-and-heat-answer`), the triage of the new requests
(`tracks/core/interfaces/REQUESTS_WAVE3.md`, rows W1 to W23 and section 3), the inbox (0
unacknowledged at 08:13Z), and `scripts/submit_chain.sh` (decision 0021 item 6).
Owner: core, branch `core/nrpic`, worktree `/data/haiyangw/nrpic/wt/core`.
Run next: `cd /data/haiyangw/nrpic/wt/core && git merge --no-edit main && harness/bin/nrpic-run status core-20261121-075439-58c2787`

ONE RUN IS PENDING: the release card build on the card-check list, run
core-20261121-075439-58c2787, Slurm job 4775 (0.1 card-hours asked; queued for
"Resources" at 08:13Z). Prediction G is in the journal (entry of 2026-11-21T07:47Z). To
close it (the worktree must be clean for `nrpic-run submit`):
1. `harness/bin/nrpic-run finish core-20261121-075439-58c2787`
2. `harness/bin/nrpic-run submit --kind scouting --gate G2 --launcher local --cores 1 --purpose "release card build judged against processors (G i)" -- python3 tracks/core/analysis/release/card_v05.py --card /data/haiyangw/nrpic/scratch/core/core-20261121-075439-58c2787 --cpu /data/haiyangw/nrpic/scratch/core/core-20261121-065009-29b855c --out '$NRPIC_RUN_DIR'`
3. `harness/bin/nrpic-run submit --kind scouting --gate G2 --launcher local --cores 1 --purpose "release card build against the candidate's card run (G ii)" -- python3 tracks/core/analysis/release/card_pair.py --a /data/haiyangw/nrpic/scratch/core/core-20261121-075439-58c2787 --b /data/haiyangw/nrpic/scratch/core/core-20261121-070946-1907f7b --out '$NRPIC_RUN_DIR'`
4. look at `fig_card_v05.png` and `fig_card_pair.png`; write the outcome against G (i)
   K1 to K6 and (ii) s3g, usr byte-identical, deposit cases within 1e-12 per history
   column) into the journal and into the row "PENDING" of the section "Release builds
   against the candidate" of `tracks/core/RELEASE-v0.5.md`; commit, push. If G (ii)
   fails for s3g or usr, it says that two card executables of one source, or two runs
   of one card executable, are not bit-identical without deposit; that is a finding,
   not a defect of the release (G (i) is the check that matters).

Files to read first: `tracks/core/STATUS.md`; the last entry of `tracks/core/JOURNAL.md`;
`tracks/core/RELEASE-v0.5.md`; `tracks/core/interfaces/REQUESTS_WAVE3.md` (what the
tracks asked and where each request goes); `tracks/core/stage/G2/OPEN.md` (first section,
core-v0.5 defects).

What changed on core/nrpic after the release (for the clerk's next merge; no file under
`athenak/`, `python/`, `problems/` changed):
- `scripts/submit_chain.sh`: an exit with status 137 or 143 without a "Terminating on"
  line, while the job got no signal, is an outside kill: resubmitted at most
  `MAX_OUTSIDE_KILLS` (2) times in a row; the executable runs as `chain/<PROC_NAME>`
  (hard link to `chain/athena`, default `nrc-<8 hex of the rundir>`, refused if it
  contains "athena"). Test: `python3 scripts/tests/test_submit_chain.py --out DIR` (fake
  sbatch, fake executable that kills its own pid; run core-20261121-080619-6a0793f).
  `scripts/README.md` describes it. Running chains keep the script they were started with.
- `docs/FORMATS.md`: snapshot row names the proper-time block.
- Interface texts: `cosmo_amr.md` (T14b, T10g), `mpi.md` (section 8 measured, 9),
  `collisions.md` (heat conduction tested by C), `cosmo_gauge.md` section 8 (D's ES-1G),
  `REQUESTS_ADF.md` 2.3 (what E is), `REQUESTS_WAVE3.md` (new).
- Analysis scripts: `analysis/release/card_pair.py`, `analysis/cosmo_amr/t14b_sf.py`,
  `analysis/mpi/card_analysis.py --out`.

Executables (read-only): release `.work/build_{gpu,cpu}_v05` (main checkout); candidate
and threaded/MPI builds `scratch/core/exe/core_nrpic_v05/` (READY: CARD CHECK PASS);
older releases `.work/build_{gpu,cpu}_v04`, `_v03`. Build after a source change in a NEW
directory (`scripts/build_cpu.sh`, `build_gpu.sh`, `build_cpu_omp.sh`, with `JOBS=<n>`
to stay within six cores).

How the release checks run (registered; the worktree clean at `nrpic-run submit`):
byte regression `analysis/release/regress_v04.py --base OLD --new NEW --out DIR --cores 6`
(5 min) and `fig_regress_v04.py RUNDIR --out DIR`; quick tests `quick_v05.py`; card
`nrpic-run submit --launcher batch --list analysis/release/card_v05.list --exe <gpu>
--gpu-hours 0.1`, judged by `card_v05.py` (against processors) and `card_pair.py`
(against another card run). For core-v0.6: copy `quick_v05.py` and `card_v05.py`, put in
the examples of the branches merged then, take core-v0.5 as the base.

Open with other owners:
- orch/clerk: merge core/nrpic into main (above); the errata rows of 0021 item 5 are the
  clerk's.
- Tracks: requests triaged in `REQUESTS_WAVE3.md`; accepted without a branch: tracker file
  appended on restart (F, W2), in-situ Fourier modes (B, W18), lapse excision relative to a
  reference lapse (D and cosmo-amr, W15), finder hrms criterion (F, W1), collisions on
  several ranks (C, W22), crossing record (D, W16), ADM-mass diagnostic (C, W6). Open
  questions without a run: D's ES-1G question 1 (W14), F's 1PN Bowen-York question (W17,
  for kb).
- 38 GB of restart files of runs core-20261119-143232-4d1e995 and
  core-20261120-220816-09f6f79 may be deleted once nothing reads them (orchestrator).

Traps:
- Exit status 3 of an AthenaK run is the guard's stop (`<basename>.guard.txt`); nrpic-run
  records such a run as failed (job 4763's manifest says "failed (exit 3)" for that reason).
- `athena_cpu_omp` is not a byte reference; compare bytes with `athena_cpu`.
- The guard names the first bad cell in loop order: when most cells fail at once (T10g),
  it says nothing about where the failure began.
- `t10_scout.py --more` appends a RESTART continuation; do not pass another run there.
- A fake executable with `#!/usr/bin/env bash` runs as `bash`; use `#!/bin/bash` to test
  process names.
- `runs/` in .gitignore hides `tracks/core/runs/`: a hand-written or copied manifest
  needs `git add -f` (the hook accepts it with a note).
- The clock: `date -u`. Temporary files of the lead: `scratch/core/tmp/lead_v05/`.
