# repro/continue: the five cut card runs of the reproduction, continued to their end

Track E, batch R2 (2026-11-24), helper package. Part of the reproduction of arXiv:2512.14649
(decision 0028). Five card runs of packages repro/scope and repro/ablation were closed as
"failed" on 2026-11-23 only because their chains reached MAX_SEGMENTS before tlim, after
preemptions by another user's jobs (journal entry 0). Each is continued here as a new
registered run that starts from the original's newest restart file, with the same executable
(byte copy, same sha256), the same deck and the same overrides.

Status (2026-11-24 13:30 PST): RNC256, CL256U, CL256S and AL2S are continued to their tlim and
join their originals without a jump (join check E-20261124-212343-7e9c4b2, journal entry 12);
RSF256 is joined up to cycle 895 (t = 5.49) and its fourth continuation waits in the shared card
queue as **q0034**. See `HANDOFF.md` (per label the chain of run ids, the files, the join rule,
the command that joins RSF256 when q0034 has run) and `JOURNAL.md` (state found, predictions
J1-J5, K1, K2, outcomes).

## Files

| Path | What |
|---|---|
| `scripts/runs.json` | the five labels: original run id, deck, overrides, restart file, executable |
| `scripts/athena_resume.sh` | executable wrapper for the chain: first segment `-r <original restart>` in place of `-i <deck>`, then the chain's own restarts; execs the byte copy named in `nrpic_exe=` |
| `scripts/submit_continue.sh` | registers and submits one continuation per label through `harness/bin/nrpic-run submit --launcher chain` |
| `scripts/check_restart.py` | where each original stopped; header, size, sidecar and checksum of its newest restart file; figure `fig_progress` |
| `scripts/join_check.py` | after the continuations: start, overlap and junction of the records and dumps (J1-J4), per continuation against everything that ran before it (several continuations per label); joined record files and dump lists; `--next LABEL=PATH` checks the restart a queued continuation starts from; figure `fig_join` |
| `scripts/join_selftest.sh` | self-test of `join_check.py` on a completed run split at one of its restarts |
| `scripts/dup_check.py` | the originals' twice-recorded cycles compared line by line (prediction D); figure `fig_dup` |
| `scripts/autocontinue.sh` | the sequencer of the first session (stopped by the orchestrator on 2026-11-24 13:15 PST; decisions 0033, 0034 forbid sequencers: card runs go through `harness/bin/nrpic-queue`); kept as a record, not to be started again |
| `scripts/conts.json` | continuation run ids per label, in the order they ran (all eight, from the sequencer's `state.tsv`); the run of q0034 is appended to RSF256 when it has run |
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

## How to continue a cut run now

Through the shared queue only (decision 0033): the arguments `scripts/submit_continue.sh` builds,
given to `harness/bin/nrpic-queue add --label <label> --priority 0 -- <arguments>` (entry 10 of
`JOURNAL.md` and `nrpic-queue show q0034` hold an example); `DRY=1 RESUME=<newest .rst>
GPU_HOURS=<h> scripts/submit_continue.sh <LABEL>` prints the manifest those arguments give.

## Requests

To orch (harness): a chain registered with one segment (`--gpu-hours` below 1.97) that receives
a SIGTERM from outside resubmits itself (`scripts/submit_chain.sh`, outside-kill resubmission)
and the resubmitted job, once it starts, only refuses (MAX_SEGMENTS reached): jobs 5190, 5194,
5199 and 5205 of this package each waited in Slurm (5190 for 40 min) and did nothing. Under the
cap of five such a job holds a slot of the account. Proposal: the chain does not resubmit when
the next segment would exceed MAX_SEGMENTS (it ends FAILED at once). Evidence: `chain/events.log`
of E-20261124-130529-da8c917, -130711-a5dec67, -201031-4c41e7b, -202134-0b1ce0c. (Decision 0026
item 7 already lists the harness option to continue a chain from another run's restart file;
this package uses a wrapper in its place.)
