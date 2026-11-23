# repro/scope: map, set-up audit and card runs for the reproduction of arXiv:2512.14649

Package of Track E (E-stoch-inf), batch R1 (2026-11-22), decision 0028. Paper: "Stochastic
Inflation in Numerical Relativity" (P1, `kb-data/raw/arxiv/2512.14649/v2/src/PRD_v2.tex`; never
copied into git, its figures never committed). Builds on the track's earlier reproduction of both
scenarios against the linear solution (`../../ladder/`, `../../usr/`, `../../g2prod/`,
`../../window/`, `../../a4res/`, `../../spec/scope/SCOPE.md`) and does not redo it.

## Contents

| Path | What |
|---|---|
| `REPRO_MAP.md` | every figure (9), table (1) and quantitative statement (S1-S33, with line) of P1: what P1 shows, which registered run of ours reproduces it, what is missing (analysis, run, option) |
| `SETUP_AUDIT.md` | P1's set-up item by item (26 items) against our decks: same, equivalent (why) or different (what it can change); errata of P1 found on the way |
| `inputs/sr_paper.athinput`, `inputs/usr_paper.athinput` | decks "as in the paper": the decks of P256/P256v6 and U256ap with output options only (dumps with [H], [M], denser dump times, restart output) |
| `inputs/small.list` | card batch: 64-cell runs of Fig. 1 and the N = 32, 64, 128 rungs of the convergence series (k_max/dk = 8), both cases |
| `queue.txt` | the eight card runs in order (label, ceiling, launcher, deck, purpose, options) |
| `scripts/sequencer.sh` | unattended submission, at most two E card jobs eligible, closes finished runs (copy of `g2prod/scripts/sequencer.sh` with a deck per line and the pause flag) |
| `scripts/smoke.sh`, `scripts/check_dump.py` | processor smoke test S0 of both decks (32^3, 8 cycles) and its check (standard library) |
| `CARD_PLAN.md` | card-hours per run (ceiling, estimate, basis, disk) against the allotment; actual costs to fill in |
| `outbox_draft/core_noise_level2.md` | draft request to core: `noise_level = 2` (P1's level-2 backreaction) for Fig. 9 |
| `JOURNAL.md` | entry 0 (S0 prediction and outcome), entry 1 (predictions P1-P7 of the card runs, before submission) |
| `HANDOFF.md` | for repro/figs: per figure the run ids, files and readers; the sequencer |

## Runs

| Run | What | State |
|---|---|---|
| E-20261123-020506-a459085 | S0 smoke test, release processor build, 1 core, 41 s | PASS (JOURNAL entry 0) |
| E-20261123-020704-2b99463 | SMALL (Slurm 4929) | pending |
| E-20261123-021204-2f573ec | USF256 (Slurm 4931) | pending |
| (sequencer) | RSF256, UL1, RL1, RNC256, CL256U, CL256S | queued behind the two above |

## How to rerun

From `/data/haiyangw/nrpic/wt/E-stoch-inf`:

    # smoke test (processors, registered)
    harness/bin/nrpic-run submit --kind scouting --gate G2 --package tracks/E-stoch-inf/repro/scope \
      --launcher local --cores 1 --allow-no-venv --input /data/haiyangw/nrpic/.work/build_cpu_v06/src/athena \
      --purpose "..." -- bash tracks/E-stoch-inf/repro/scope/scripts/smoke.sh \
      /data/haiyangw/nrpic/.work/build_cpu_v06/src/athena '$NRPIC_RUN_DIR'
    # card runs: the sequencer submits queue.txt line by line (see HANDOFF.md to start, see, stop)
    setsid nohup bash tracks/E-stoch-inf/repro/scope/scripts/sequencer.sh \
      > /data/haiyangw/nrpic/scratch/E-stoch-inf/repro_scope_seq/nohup.out 2>&1 < /dev/null &
    # one line by hand (example, USF256):
    harness/bin/nrpic-run submit --kind production --gate G2 \
      --preregistered "tracks/E-stoch-inf/repro/scope/JOURNAL.md#entry-1" --package tracks/E-stoch-inf/repro/scope \
      --launcher chain --gpu-hours 1.97 --exe /data/haiyangw/nrpic/.work/build_gpu_v06/src/athena \
      --purpose "..." -- tracks/E-stoch-inf/repro/scope/inputs/usr_paper.athinput

## Requests

- core: `noise_level = 2` (P1's level-2 backreaction), `outbox_draft/core_noise_level2.md`; optional
  `noise_k_sign`, `noise_a_sign`. For the lead of E to post.
- lead of E: post the draft; push the manifests the sequencer commits; judge U-A2' and U256nc in
  batch 10a as planned (the map cites them as pending there).
- orch: none (the plan stays within the package cap of 8 card-hours and the G2 allotment).
