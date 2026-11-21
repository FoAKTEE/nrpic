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
| `JOURNAL.md` | entry 1 (reading, step-1 expectation), 2 (step-1 outcome), 3 (predictions and analysis rules before the card job), 4 (outcome), 5 (post-hoc check, close) |
| `scripts/stencil_symbols.py` | step 1: symbols q, kap of the centred differences parsed from `athenak/src/utils/finite_diff.hpp`, mu/k^2 = (kap - q^2)/k^2, the ladder's A2 references with each symbol |
| `scripts/a4lib.py` | set-ups, members, dump schedule, core's twin extracted with `git show` from `core/scalar-3`, even-part model [JUDGEMENT], floor model of the ladder |
| `scripts/twin_predict.py` | step 2: CodeTwin predictions per dump and set-up, cross-check on the ladder's runs |
| `scripts/make_list.py` | writes `inputs/card.list` (24 runs) |
| `scripts/a4_analysis.py` | step 4: odd/even parts, measured floors, halving, twin comparison, verdicts, figures |
| `scripts/post_checks.py` | post-hoc checks of JOURNAL entry 5 (Q6 first dump, odd halving at 5 floors) |
| `scripts/figstyle.py` | copy of `harness/style/figstyle.py` |
| `inputs/card.list` | the card job (format of `../ladder/inputs/jobC.list`) |
| `results/symbols.json` | step 1 numbers (run E-20261120-222312-6ee4bc5) |
| `results/prediction.json`, `results/cross.json` | step 2 (run E-20261121-130841-c406130) |
| `results/a4res.json`, `results/verdicts.md`, `results/post.json` | step 4 and post-hoc checks (run E-20261121-152010-371d5f1) |
| `fig/` | `fig_symbols.png` (step 1), `fig_prediction.png` (step 2), `fig_parts_H.png`, `fig_parts_M.png`, `fig_ratio.png`, `fig_checks.png`, `fig_post.png` (step 4) |

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
    # analysis (2 cores at most), then the post-hoc checks, inside one registered run:
    ... a4_analysis.py --job /data/haiyangw/nrpic/scratch/E-stoch-inf/E-20261121-131000-b23055b \
        --pred ../results/prediction.json --out "$NRPIC_RUN_DIR" && \
        post_checks.py --ana "$NRPIC_RUN_DIR/a4res.json" --out "$NRPIC_RUN_DIR"
    # (the exact commands are in the manifests under tracks/E-stoch-inf/runs/<run id>/)

## Results

Runs: step 1 E-20261120-222312-6ee4bc5; step 2 (twin prediction) E-20261121-130841-c406130;
card job E-20261121-131000-b23055b (Slurm 4798, `core_scalar-2/athena_gpu` a58e95b, 24
runs, 11.2 card-minutes = 0.19 card-hours); analysis E-20261121-151643-c2c0f5a and its
rerun with the post-hoc checks E-20261121-152010-371d5f1 (`results/`, `fig/`).

Step 1 [VERIFIED by own arithmetic on the coefficients of `finite_diff.hpp`]: mu/k^2 =
0.110, 3.54e-2, 1.32e-2, 2.59e-3, 7.10e-4, 2.44e-4, 4.44e-5 at 4, 5, 6, 8, 10, 12, 16 cells
per wavelength, equal to core's 0.110, 2.6e-3, 4.4e-5 at 4, 8, 16. The ladder's
stencil-k^2 A2 reference used the sixth-order symbol; its 6.25e-3 difference to the
continuum reference is reproduced (6.255e-3); the second-order symbol would give 0.83, so
core's remark on SCOPE 4 A2 does not hold (`fig/fig_symbols.png`).

Step 4 (SR, one mode file, seed 20261115; s = +-1 and +-1/2; rules fixed in JOURNAL entry
3 before the job; odd/even parts in absolute rms, floors measured from the halving):

| set-up | cells per shortest source wavelength | largest odd/even, H (t) | M (t) | even part halving | odd part halving | measured odd / twin | strict A4 | A4' (a, b, c) |
|---|---|---|---|---|---|---|---|---|
| N64q16 | 16.0 | 0.455 (1.77) | 0.314 (2.26) | 3.980-3.999 | untested at 10 f_o (1.973-1.979 at 5 f_o, post hoc) | 1.004-1.056 | holds | a, c hold; b untested |
| N64q25 | 12.8 | 1.000 (2.01) | 0.795 (2.50) | 3.981-3.999 | 1.993-1.997 | 1.000-1.052 | holds (ratio 0.9997) | holds |
| N64q36 | 10.7 | 2.81 (2.14) | 2.45 (2.77) | 3.981-4.000 | 1.994-2.000 | 1.000-1.049 | fails | holds |
| N64q64 | 8.0 | 15.5 (2.50) | 13.8 (3.02) | 3.981-4.000 | 1.997-2.000 | 1.000-1.049 | fails | b, c hold; a: halving holds, agreement with N128q64 fails at t = 0.147 only (Q6) |
| N128q100 | 12.8 | 0.939 (2.76) | 0.858 (3.25) | 3.984-3.999 | untested at 10 f_o (1.972-1.991 at 5 f_o, post hoc) | 1.002-1.057 | holds | a, c hold; b untested |
| N128q64 | 16.0 | 0.273 (2.50) | 0.240 (3.01) | 3.984-3.997 | untested (odd part of the half pair below 2 floors) | 1.043-1.059 | holds | c holds; b untested; a as N64q64 |

(`results/verdicts.md` is the script's own table; its words "A4' fails in b" for three
set-ups mean "no qualifying dump", JOURNAL entry 4.) Crossing of 1 by the largest ratio
(log-log interpolation): 12.80 cells (N = 64 family), 12.66 (N = 128 pair). The twin's
prediction of the largest ratio held within 2 percent for H. Odd part between 8 and 16
cells: order 5.80-5.84 against the twin's 5.89. Record: <|H|/[H]> <= 2.6e-12, <|M|/[M]>
<= 1.5e-5 in all 24 runs. Failed prediction: Q6, the even parts at 8 and 16 cells (K = 8)
differ by 10.9 percent at the first dump after t = 0 (within 3.1 percent at every other
dump, 7e-5 at t = 0); cause not found (JOURNAL entry 5). Figures: `fig_ratio.png`
(ratio against time and largest ratio against cells, with core's scan and the twin),
`fig_parts_H.png`, `fig_parts_M.png`, `fig_checks.png`, `fig_post.png`.

## For the A4 ruling

1. Strict A4 holds where the shortest source wavelength has at least 12.8 cells (N64q25, N64q16, N128q100, N128q64; ratio 1.000, 0.455, 0.939, 0.273) and fails at 10.7 and 8 cells (ratio 2.8 and 15.5): card run E-20261121-131000-b23055b, analysis E-20261121-152010-371d5f1.
2. Core's criterion is confirmed: the largest first/second-order ratio crosses 1 at 12.8 cells (N = 64) and 12.7 (N = 128) against core's 12.7; the first-order part equals core's linear twin within 6 percent wherever it is above the floor; mu/k^2 reproduced (E-20261120-222312-6ee4bc5).
3. At 12.8 cells the margin is nil (ratio 0.9997 at N = 64); about 16 cells gives a factor 2-4 (0.27-0.46).
4. P1's set-up has 4 cells (k_max = N/4), a factor 3.2 below the threshold: strict A4 there needs nmax2 <= (N/12.7)^2 (406 at N = 256, k_max 20 instead of 64) or N >= 813 for k_max = 64. A4' (decision 0021) holds where testable, except that the even parts at 8 and 16 cells (A4'(a)) differ by 10.9 percent at the first dump after t = 0 (within 3.1 percent at all 35 others).

## Requests

- To core (via the lead): claims C1-C3 of `tracks/core/interfaces/scalar_field_3.md`
  section 4 (mu/k^2, the crossing at 12.7 cells, nmax2 <= (N/12.7)^2) are confirmed by
  this package (runs above) and can cite it; C4 (the remark that the ladder's stencil
  reference may use the second-order symbol) is not confirmed: the ladder used the
  sixth-order symbol.
- To the lead: forward "For the A4 ruling" to the orchestrator. Optional: the 3-minute
  card run of JOURNAL entry 5 (common dump times) if Q6's first-dump deviation matters
  for A4'(a).
