# repro/ablation: the ablation of the stochastic backreaction on the cards (Track E, batch R1c)

Part of the reproduction of arXiv:2512.14649 (P1 = `kb-data/raw/arxiv/2512.14649/v2/src/PRD_v2.tex`)
under decisions 0028, 0029, 0031. P1's Fig. 9 (`fig:ablationback`, P1:777-790) and the statement P1:520
("a detectable but <~ 1 per ten thousand relative change in power spectrum for all scales"): the
shell power of R^NR at N_f with backreaction level 2 and level 1, each against level 0, for both
scenarios, N = 256, one seed. As decided in 0031 item 1, all three levels use the mode equation of the
noise ON THE MESH (`noise_mode_eq = mesh`; level 2 implies it): the released levels 0 and 1 on shells
with the continuum k^2 differ from the mesh form at first order by the stencil and would swamp the
effect. Executable: branch `core/noise-level2` (source 6ca93cba),
`/data/haiyangw/nrpic/scratch/core/exe/core_noise-level2/athena_gpu`, READY in that directory, design
in `tracks/core/interfaces/noise_level2.md` on that branch (choices labelled [JUDGEMENT] there: the
background of the window at level 2 = box means, the reading of phidot_b and d_i d^i).

## What is in the directory

| Path | What |
|---|---|
| `JOURNAL.md` | entry 0: the inputs checked against `repro/scope/SETUP_AUDIT.md` and against what the figure needs; prediction and outcome of the parse check X0. Entry 1: predictions of the card runs (P-T5 smoke, P-A1 SR, P-A2 USR, P-A3 controls, refutation of the implementation, cost), written before any submission |
| `inputs/{sr,usr}256_{l0m,l1m,l2}.athinput` | core's six ablation decks (`git show core/noise-level2:tracks/core/analysis/noise_level2/inputs/ablation/<name>`) with output-only edits (header of each deck; JOURNAL entry 0): dumps every 0.5 / tlim/20 (18 / 21, last at N_f), no constraint or magnitude fields in the dumps, `noise_rmodes_dump = true` |
| `inputs/card/{sr,usr}64_l{0,2}.athinput` | core's four T5 decks, unchanged (`.../inputs/card/`) |
| `inputs/card/sr64_l1m.athinput`, `inputs/card/usr64_l0m.athinput` | core's l0 decks with level 1 on the mesh (SR) / level 0 on the mesh (USR) and the per-mode writer: the card runs every path of the 256^3 runs |
| `inputs/smoke.list` | the batch T5SMK (six 64^3 runs) |
| `queue.txt` | the ablation queue: T5SMK (head), then AL2S, AL2U, AL0S, AL0U, AL1S, AL1U (tail, gated by the smoke check) |
| `scripts/sequencer.sh` | the sequencer of repro/scope AND repro/ablation (replaces the scope copy; same state directory) |
| `scripts/smoke_check.py` | check of T5SMK: exit, tlim, finite records, dumps, `.rmodes`, card against core's processor run core-20261123-030705-6b6a4bd (cycles 0-30), timing, a 64^3 preview; `verdict.json` and `smoke_check.png` |
| `scripts/parse_check.sh` | X0: the eight edited or new decks at 32^3, two cycles, branch processor build |
| `outbox_draft/core_t5.md` | the message to core on T5 (the lead posts it, with the outcome once the check has run) |
| `HANDOFF.md` | for repro/figs: run ids, files, how to read and compare |

## Diffs of the inputs (how they were checked)

    git show core/noise-level2:tracks/core/analysis/noise_level2/inputs/ablation/sr256_l2.athinput | diff tracks/E-stoch-inf/repro/scope/inputs/sr_paper.athinput -
    diff <(git show core/noise-level2:tracks/core/analysis/noise_level2/inputs/ablation/sr256_l2.athinput) tracks/E-stoch-inf/repro/ablation/inputs/sr256_l2.athinput

Core's decks differ from the scope decks only by basename, `noise_level` and `noise_mode_eq = mesh`;
ours from core's only by the four output lines and the header.

## How to rerun

- Parse check (processors, one core, about one minute):
  `harness/bin/nrpic-run submit --kind scouting --gate G2 --package tracks/E-stoch-inf/repro/ablation --launcher local --cores 1 --allow-no-venv --purpose "..." -- bash tracks/E-stoch-inf/repro/ablation/scripts/parse_check.sh '$NRPIC_RUN_DIR'`
- Card runs: the sequencer submits them (below). By hand, one at a time, with the two-job rule:
  `harness/bin/nrpic-run submit --kind scouting --gate G2 --package tracks/E-stoch-inf/repro/ablation --launcher batch --gpu-hours 0.5 --exe /data/haiyangw/nrpic/scratch/core/exe/core_noise-level2/athena_gpu --list tracks/E-stoch-inf/repro/ablation/inputs/smoke.list --wall 00:30:00 --purpose "..."`
  and for each 256^3 deck
  `harness/bin/nrpic-run submit --kind production --gate G2 --preregistered "tracks/E-stoch-inf/repro/ablation/JOURNAL.md#entry-1" --package tracks/E-stoch-inf/repro/ablation --launcher chain --gpu-hours 1.97 --exe /data/haiyangw/nrpic/scratch/core/exe/core_noise-level2/athena_gpu --purpose "..." -- tracks/E-stoch-inf/repro/ablation/inputs/sr256_l2.athinput`
- Smoke check by hand: `harness/bin/nrpic-run submit --kind scouting --gate G2 --package tracks/E-stoch-inf/repro/ablation --launcher local --cores 1 --purpose "..." -- python3 tracks/E-stoch-inf/repro/ablation/scripts/smoke_check.py --run /data/haiyangw/nrpic/scratch/E-stoch-inf/<T5SMK run id> --ref /data/haiyangw/nrpic/scratch/core/core-20261123-030705-6b6a4bd --out '$NRPIC_RUN_DIR'`

## The sequencer

`scripts/sequencer.sh` replaced the scope sequencer on 2026-11-22 (the scope copy was stopped through
its STOP file; nothing it had submitted was touched). It reads `repro/scope/queue.txt` unchanged with
the release card build and the scope plan, and `queue.txt` here with the branch build and this plan.
Order: T5SMK first (head), then the remaining scope lines (RSF256, UL1, RL1, RNC256, CL256U, CL256S),
then the six ablation runs. The six wait for the smoke check (PASS) and stop at a cost of 5 card-hours
for this package. State, log, pid, STOP: `/data/haiyangw/nrpic/scratch/E-stoch-inf/repro_scope_seq/`.
Restart command and skip mechanism: header of the script. Never run the old scope copy beside it (two
sequencers would both count to two jobs and could submit a third).

## Requests

- **lead of E-stoch-inf**: (1) post `outbox_draft/core_t5.md` to core once the smoke check has run (or
  as it stands, saying the card run is queued); (2) RL1 and UL1 of the scope queue (level 1 on SHELLS,
  1.97 card-hours ceiling each, about 1.1 actual) are superseded for Fig. 9 by AL1S/AL1U here (decision
  0031 item 1); to drop them append `RL1\t-\tskipped\t<date>` and `UL1\t-\tskipped\t<date>` to
  `scratch/E-stoch-inf/repro_scope_seq/state.tsv` (the sequencer then passes them); keeping them gives
  only the shells/shells comparison of scope P4; (3) `repro/scope/HANDOFF.md` still names the scope
  copy's restart command: point it to `repro/ablation/scripts/sequencer.sh` (this package may not
  write there).
- **core**: T5 is queued as T5SMK (outcome to follow); nothing else is needed for the six runs.
