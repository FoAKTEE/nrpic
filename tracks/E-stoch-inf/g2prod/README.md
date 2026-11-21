# g2prod: USR production ladder of gate G2 on the release card build (E-stoch-inf)

Started 2026-11-21 by the lead of batch 5. Criteria: `../spec/scope/SCOPE.md` section 4c (fixed
before the runs). Predictions per run: `JOURNAL.md` entry 1. Executable: release core-v0.6,
`/data/haiyangw/nrpic/.work/build_gpu_v06/src/athena` (cards), `.work/build_cpu_v06/src/athena`
(processor restart check).

Files:
- `inputs/usr_prod.athinput`: the deck of the scouting pair U256/U256m plus a restart output.
- `inputs/timing.list`: 40-step timing at 256^3, 320^3, 384^3.
- `queue.txt`: the runs the sequencer submits, in order (label, card-hours ceiling of the chain,
  purpose | athena arguments).
- `scripts/sequencer.sh`: keeps at most two card jobs of E eligible, submits the next queue line
  through `harness/bin/nrpic-run` (chain launcher, kind production, gate G2), closes finished
  runs with `nrpic-run finish`, retries submissions refused by the allotment every 15 min.
  State, log and pid in `/data/haiyangw/nrpic/scratch/E-stoch-inf/g2prod_seq/`.
- `scripts/restart_check.sh`: processor check R0 that a restart of this deck is exact.

See and stop: `../HANDOFF.md` (exact commands). Analysis: not yet (JOURNAL entry 2 when the runs
have finished); it reuses `../usr/scripts/` and `../window/scripts/`.

Results: none yet (runs pending; ids in `../STATUS.md` and the sequencer's `state.tsv`).
