# a4res: pre-registered test of the resolution criterion for the strict A4

Package of E-stoch-inf, wave 3 (`../PLAN-wave3.md`, key `a4res`). Question: does the strict
A4 of SCOPE 4 (H and M_i second order in the noise amplitude during the entry) hold once
the shortest source wavelength has enough cells, as core's package scalar3 states (first
order = defect of the discrete contracted Bianchi identity; largest first/second ratio
below 1 from 12.7 cells per shortest source wavelength; strict A4 needs
nmax2 <= (N/12.7)^2)? Predictions and outcomes: `JOURNAL.md`.

## Contents

| Path | What |
|---|---|
| `JOURNAL.md` | entry 1 (reading, step-1 expectation), 2 (step-1 outcome), 3 (predictions and analysis rules before the card job), 4 (outcome) |
| `scripts/stencil_symbols.py` | step 1: symbols q, kap of the centred differences parsed from `athenak/src/utils/finite_diff.hpp`, mu/k^2 = (kap - q^2)/k^2, the ladder's A2 references with each symbol |
| `scripts/a4lib.py` | set-ups, members, dump schedule, core's twin extracted with `git show` from `core/scalar-3`, even-part model [JUDGEMENT], floor model of the ladder |
| `scripts/twin_predict.py` | step 2: CodeTwin predictions per dump and set-up, cross-check on the ladder's runs |
| `scripts/make_list.py` | writes `inputs/card.list` (24 runs) |
| `scripts/a4_analysis.py` | step 4: odd/even parts, measured floors, halving, twin comparison, verdicts, figures |
| `scripts/figstyle.py` | copy of `harness/style/figstyle.py` |
| `inputs/card.list` | the card job (format of `../ladder/inputs/jobC.list`) |
| `results/symbols.json` | step 1 numbers (run E-20261120-222312-6ee4bc5) |
| `results/prediction.json`, `results/cross.json` | step 2 (run E-20261121-130841-c406130) |
| `results/a4res.json`, `results/verdicts.md` | step 4 (analysis run, see Results) |
| `fig/` | `fig_symbols.png` (step 1), `fig_prediction.png` (step 2), `fig_parts_H.png`, `fig_parts_M.png`, `fig_ratio.png`, `fig_checks.png` (step 4) |

## How to rerun

From the worktree root, with the worktree's `.venv`:

    harness/bin/nrpic-run submit --package tracks/E-stoch-inf/a4res --kind scouting --gate G1 \
      --launcher local --cores 1 -- bash -c 'cd tracks/E-stoch-inf/a4res/scripts && \
      ../../../../.venv/bin/python stencil_symbols.py --out "$NRPIC_RUN_DIR"'
    # same with: twin_predict.py --out "$NRPIC_RUN_DIR"
    python3 tracks/E-stoch-inf/a4res/scripts/make_list.py > tracks/E-stoch-inf/a4res/inputs/card.list
    harness/bin/nrpic-run submit --package tracks/E-stoch-inf/a4res --kind scouting --gate G1 \
      --launcher batch --exe /data/haiyangw/nrpic/scratch/core/exe/core_scalar-2/athena_gpu \
      --list tracks/E-stoch-inf/a4res/inputs/card.list --gpu-hours 0.5 --wall 00:45:00 --purpose ...
    # analysis (2 cores at most):
    ... a4_analysis.py --job scratch/E-stoch-inf/<card run id> \
        --pred tracks/E-stoch-inf/a4res/results/prediction.json --out "$NRPIC_RUN_DIR"

## Results

Card job 4798 (run E-20261121-131000-b23055b): pending at the time of writing.

## Requests

None yet.
