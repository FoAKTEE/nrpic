# repro/continue: the five cut card runs of the reproduction, continued to their end

Track E, batch R2 (2026-11-24), helper package. Part of the reproduction of arXiv:2512.14649
(decision 0028). Five card runs of packages repro/scope and repro/ablation were closed as
"failed" on 2026-11-23 only because their chains reached MAX_SEGMENTS before tlim, after
preemptions by another user's jobs (journal entry 0). Each is continued here as a new
registered run that starts from the original's newest restart file, with the same executable
(byte copy, same sha256), the same deck and the same overrides.

Status: see `HANDOFF.md` (per label: original run, continuation run, files, how to read the two
as one run) and `JOURNAL.md` (state found, predictions J1-J5, outcomes).

## Files

| Path | What |
|---|---|
| `scripts/runs.json` | the five labels: original run id, deck, overrides, restart file, executable |
| `scripts/athena_resume.sh` | executable wrapper for the chain: first segment `-r <original restart>` in place of `-i <deck>`, then the chain's own restarts; execs the byte copy named in `nrpic_exe=` |
| `scripts/submit_continue.sh` | registers and submits one continuation per label through `harness/bin/nrpic-run submit --launcher chain` |
| `scripts/check_restart.py` | where each original stopped; header, size, sidecar and checksum of its newest restart file; figure `fig_progress` |
| `scripts/join_check.py` | after the continuations: start, overlap and junction of the records and dumps (J1-J4); joined record files and dump lists; figure `fig_join` |
| `scripts/join_selftest.sh` | self-test of `join_check.py` on a completed run split at one of its restarts |
| `scripts/dup_check.py` | the originals' twice-recorded cycles compared line by line (prediction D); figure `fig_dup` |
| `scripts/autocontinue.sh` | sequencer that outlives the session: closes the continuations, continues a cut one from its newest restart (5 card-hour cap, three per label), runs the join check at the end |
| `scripts/conts.json` | continuation run ids per label as submitted by this session (the sequencer's own list: `scratch/E-stoch-inf/repro_continue_seq/state.tsv`) |
| `scripts/figstyle.py` | copy of `python/nrpic/figstyle.py` |

## How to rerun

```
cd /data/haiyangw/nrpic/wt/E-stoch-inf
# restart check (registered, processors)
harness/bin/nrpic-run submit --kind production --gate G2 --package tracks/E-stoch-inf/repro/continue \
  --launcher local --cores 1 --purpose "..." -- python3 tracks/E-stoch-inf/repro/continue/scripts/check_restart.py --out '$NRPIC_RUN_DIR' --sha
# one continuation (card); LABEL from scripts/runs.json
tracks/E-stoch-inf/repro/continue/scripts/submit_continue.sh LABEL
```

The executables the wrapper execs are byte copies under `scratch/E-stoch-inf/tmp/continue/exe/`
(`rc-v06-gpu` = release core-v0.6 card build, `rc-nl2-gpu` = branch card build
core_noise-level2); rebuild them with `cp -p` from the paths in `scripts/runs.json` and check the
sha256 there.

## Requests

None so far. (Decision 0026 item 7 already lists the harness option to continue a chain from
another run's restart file; this package uses a wrapper in its place.)
