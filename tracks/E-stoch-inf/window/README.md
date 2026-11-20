# window: sensitivity of the USR spectrum to the window function (E-stoch-inf, test L9)

Second G2 criterion of Track E, "sensitivity to window-function parameters"
(`coord/CHARTER.md` 9.8; test L9 of `../codebase/DESIGN_REVIEW.md` 8.1). The window of the
stochastic sources is W = (1 + tanh[s ln(sigma a H/k)])/2 (`coord/INTERFACES/scalar_field.md`
7.3; options `<scalar_field> noise_sharpness` = s, `noise_sigma` = sigma; production s = 5,
sigma = 1 as P1, arXiv:2512.14649 `PRD_v2.tex`:506, 519). This package scans
(s, sigma) = (5, 1), (2.5, 1), (10, 1), (5, 0.5), (5, 2) for the USR (inflection) case at
128^3 with nmax2 = 1024 (k_max = N/4 = 32 dk), each with its mirrored realisation, against
the linear reference of each window; the slow-roll case at 64^3 is the contrast.
Predictions and outcomes: `JOURNAL.md` (entries 1 and later).

## Contents

| Path | What |
|---|---|
| `inputs/usr_256.athinput` | copy of `../usr/inputs/usr_256.athinput` (USR set-up of P1); the list overrides mesh, nmax2, mode file, s, sigma and the mode scale |
| `inputs/sr_base.athinput` | copy of `../ladder/inputs/sr_base.athinput` (slow-roll contrast) |
| `inputs/card_window.list` | the card job: 10 USR runs at 128^3 (5 windows x +-1) and 6 slow-roll runs at 64^3 (5 windows at +1, baseline at -1) |
| `scripts/window_lib.py` | windows, cases, the quadratic reference; imports `../usr/scripts/usr_lib.py` read-only (reader, modes, R^NR, MS reference) |
| `scripts/window_reference.py` | step 1, linear reference per window: W at N*, crossings against the USR phase, prediction at N_f, one-point variance of W R |
| `scripts/analyse_window.py` | step 4, analysis of the card job: per-mode NR against each window's reference, odd and even parts, shifts against the baseline with errors, sensitivity per parameter, one-point rms, constraint records, figures |
| `scripts/figstyle.py` | copy of `harness/style/figstyle.py` |
| `results/reference/` | outputs of the reference run E-20261120-222802-bffb812 (`reference_{usr,sr}.json`, `shells_{usr,sr}.csv`) |
| `fig/fig_ref_*.png` | reference figures (windows and one-point rms in time; crossings and the slice at N*) |

## How to rerun

From the worktree root (`/data/haiyangw/nrpic/wt/E-stoch-inf`), with the worktree's `.venv`:

    # reference (25 s on 2 cores)
    harness/bin/nrpic-run submit --package tracks/E-stoch-inf/window --kind scouting --gate G2 \
      --launcher local --cores 2 --purpose "..." -- bash -c 'cd tracks/E-stoch-inf/window/scripts && \
      export OMP_NUM_THREADS=2 && python3 window_reference.py --out "$NRPIC_RUN_DIR"'
    # card job (one Slurm job, about 25 min on one A100)
    harness/bin/nrpic-run submit --package tracks/E-stoch-inf/window --kind scouting --gate G2 \
      --launcher batch --exe /data/haiyangw/nrpic/scratch/core/exe/core_scalar-2/athena_gpu \
      --list tracks/E-stoch-inf/window/inputs/card_window.list --gpu-hours 0.5 --wall 00:30:00 --purpose "..."
    # analysis of the job's output directory (dumps read one at a time)
    harness/bin/nrpic-run submit --package tracks/E-stoch-inf/window --kind scouting --gate G2 \
      --launcher local --cores 2 --purpose "..." -- bash -c 'cd tracks/E-stoch-inf/window/scripts && \
      export OMP_NUM_THREADS=2 && python3 analyse_window.py --runs <job output dir> --out "$NRPIC_RUN_DIR"'

## Results

Linear reference (run E-20261120-222802-bffb812, JOURNAL entry 2):

| Window | W(N*) of the shells abs(n)^2 = 1, 2, 3, 4 | last crossing cN (W = 0.95) | shells crossed before USR | one-point var / baseline at cN = 1, 3, 4, 5, N_f |
|---|---|---|---|---|
| b (5, 1) | 0.5, 0.030, 0.0041, 0.00098 | 3.515 (3.810) | 119 (k <= 11.87) | 1 |
| s25 (2.5, 1) | 0.5, 0.150, 0.060, 0.030 | 3.515 (4.104) | 119 | 0.919, 0.984, 0.947, 1.000, 1 |
| s10 (10, 1) | 0.5, 0.00098, 1.7e-5, 9.5e-7 | 3.515 (3.662) | 119 | 1.055, 1.037, 1.003, 1.000, 1 |
| g05 (5, 0.5) | 0.00098, 3.1e-5, 4.0e-6, 9.5e-7 | 4.208 (4.503) | 30 (k <= 5.92) | 0.41, 0.625, 0.479, 1.000, 1 |
| g2 (5, 2) | 0.999, 0.970, 0.808, 0.5 | 2.821 (3.116) | 473 (k <= 23.77) | 1.81, 2.92, 1.003, 1.000, 1 |

The linear prediction of the coarse-grained R at N_f does not depend on the window (power
shift at most 1.6e-14); the ensemble rms of W R at N_f is 0.494 for every window (0.4946 for
the realisation of the runs). The slice at N* holds W(N*) R per shell with the run's own s
and sigma (source read, JOURNAL entry 0).

Card job: pending (see below).

## Requests

None yet.
