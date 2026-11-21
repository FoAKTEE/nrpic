# window: sensitivity of the USR spectrum to the window function (E-stoch-inf, test L9)

Second G2 criterion of Track E, "sensitivity to window-function parameters"
(`coord/CHARTER.md` 9.8; test L9 of `../codebase/DESIGN_REVIEW.md` 8.1). The window of the
stochastic sources is W = (1 + tanh[s ln(sigma a H/k)])/2 (`coord/INTERFACES/scalar_field.md`
7.3; options `<scalar_field> noise_sharpness` = s, `noise_sigma` = sigma; production s = 5,
sigma = 1 as in P1, arXiv:2512.14649 `PRD_v2.tex`:506, 519). This package scans
(s, sigma) = (5, 1), (2.5, 1), (10, 1), (5, 0.5), (5, 2) for the USR (inflection) case at
128^3 with nmax2 = 1024 (k_max = N/4 = 32 dk). Each window is run with its mirrored
realisation and compared with its own linear reference. The slow-roll case at 64^3 is the
contrast. Predictions and outcomes are in `JOURNAL.md` (entries 1-5; failed predictions are
kept).

**Status: done.** Reference, card job (4740) and analysis have all run. The shifts and their
errors are stated below.

## Contents

| Path | What |
|---|---|
| `inputs/usr_256.athinput` | copy of `../usr/inputs/usr_256.athinput` (P1's USR set-up); the list overrides mesh, nmax2, mode file, s, sigma and the mode scale |
| `inputs/sr_base.athinput` | copy of `../ladder/inputs/sr_base.athinput` (slow-roll contrast) |
| `inputs/card_window.list` | the card job: 10 USR runs at 128^3 (5 windows x +-1) and 6 slow-roll runs at 64^3 (5 windows at +1, baseline at -1) |
| `scripts/window_lib.py` | windows, cases, the quadratic reference; imports `../usr/scripts/usr_lib.py` read-only (modes, R^NR, MS reference) |
| `scripts/window_reference.py` | step 1, linear reference per window: W at N*, crossings against the USR phase, prediction at N_f, one-point variance of W R |
| `scripts/analyse_window.py` | step 4, analysis of the card job: per-mode NR against each window's reference, odd and even parts, shifts against the baseline with errors, sensitivity per parameter, one-point rms, constraint records, figures. Dumps are read sequentially (`../usr/scripts/card_lib.read_fields`) |
| `scripts/posthoc_window.py` | post-hoc check (JOURNAL entry 4): where the second-order part shows, the common NR error of the shift, the constraint records |
| `scripts/figstyle.py` | copy of `harness/style/figstyle.py` |
| `results/reference/` | reference run E-20261120-222802-bffb812 (`reference_{usr,sr}.json`, `shells_{usr,sr}.csv`) |
| `results/scan/` | analysis run E-20261121-154733-0d1fbda (`summary_{usr,sr}.json`, `table_{usr,sr}.md`) and post-hoc run E-20261121-155344-78859e9 (`posthoc_usr.json`) |
| `fig/fig_ref_*.png` | reference: windows and one-point rms in time; crossings and the slice at N* |
| `fig/fig_{usr,sr}_*.png` | scan: `mode_errors` (per mode at the last dump), `shift_Nf` (shell shift against the baseline and its bound), `passage` (four shells in time), `passage_residual`, `onepoint`, `even`, `constraints`; `fig_usr_second_order` (post-hoc) |

## How to rerun

From the worktree root (`/data/haiyangw/nrpic/wt/E-stoch-inf`), with the worktree's `.venv`:

    # reference (25 s on 2 cores)
    harness/bin/nrpic-run submit --package tracks/E-stoch-inf/window --kind scouting --gate G2 \
      --launcher local --cores 2 --purpose "..." -- bash -c 'cd tracks/E-stoch-inf/window/scripts && \
      export OMP_NUM_THREADS=2 && python3 window_reference.py --out "$NRPIC_RUN_DIR"'
    # card job (one Slurm job; 23 min, 0.384 card-hours on one A100 for job 4740)
    harness/bin/nrpic-run submit --package tracks/E-stoch-inf/window --kind scouting --gate G2 \
      --launcher batch --exe /data/haiyangw/nrpic/scratch/core/exe/core_scalar-2/athena_gpu \
      --list tracks/E-stoch-inf/window/inputs/card_window.list --gpu-hours 0.5 --wall 00:30:00 --purpose "..."
    # analysis of the job's output directory (221 s on 2 cores; writes <run>.npz caches)
    harness/bin/nrpic-run submit --package tracks/E-stoch-inf/window --kind scouting --gate G2 \
      --launcher local --cores 2 --purpose "..." -- bash -c 'cd tracks/E-stoch-inf/window/scripts && \
      export OMP_NUM_THREADS=2 && python3 analyse_window.py --runs <job output dir> --out "$NRPIC_RUN_DIR" --case sr usr'
    # post-hoc check from the analysis caches (12 s)
    ... -- bash -c 'cd tracks/E-stoch-inf/window/scripts && python3 posthoc_window.py --ana <analysis run dir> --out "$NRPIC_RUN_DIR"'

## Results

### Linear reference (run E-20261120-222802-bffb812, JOURNAL entry 2)

| Window | W(N*) of the shells abs(n)^2 = 1, 2, 3, 4 | last crossing cN (W = 0.95) | shells crossed before USR | one-point var / baseline at cN = 1, 3, 4, 5, N_f |
|---|---|---|---|---|
| b (5, 1) | 0.5, 0.030, 0.0041, 0.00098 | 3.515 (3.810) | 119 (k <= 11.87) | 1 |
| s25 (2.5, 1) | 0.5, 0.150, 0.060, 0.030 | 3.515 (4.104) | 119 | 0.919, 0.984, 0.947, 1.000, 1 |
| s10 (10, 1) | 0.5, 0.00098, 1.7e-5, 9.5e-7 | 3.515 (3.662) | 119 | 1.055, 1.037, 1.003, 1.000, 1 |
| g05 (5, 0.5) | 0.00098, 3.1e-5, 4.0e-6, 9.5e-7 | 4.208 (4.503) | 30 (k <= 5.92) | 0.41, 0.625, 0.479, 1.000, 1 |
| g2 (5, 2) | 0.999, 0.970, 0.808, 0.5 | 2.821 (3.116) | 473 (k <= 23.77) | 1.81, 2.92, 1.003, 1.000, 1 |

In linear theory the coarse-grained R at N_f does not depend on the window: the power shift
is at most 1.6e-14. The ensemble rms of W R at N_f is 0.494 for every window. The slice at N*
holds W(N*) R per shell, built with the run's own s and sigma (source read, JOURNAL entry 0).

### Sensitivity of the USR spectrum to s and sigma (128^3, nmax2 = 1024; analysis run E-20261121-154733-0d1fbda, post-hoc E-20261121-155344-78859e9; JOURNAL entry 5)

Values are at the last dump, cN = 9.585. O and E are the odd and even parts of each mirrored
pair. The shift is P_w/P_b - 1 of the shell powers of O. Its bound is |e_w| + |e_b|, the
NR-against-reference power errors of the two runs. Because the linear shift is zero, the
NR shift is about e_w - e_b, so this bound holds by construction; part of e is common to
the windows and cancels in the shift (last column).

| window | per-mode error of O, k <= 16 / k <= 32 | shell shift k <= 16 (bound) | shell shift k <= 32 (bound) | linear shift | max shift of modes crossed before USR | passage residual / linear shift | E/O rms | one-point rms NR/ref - 1 | odd shift / baseline error at k < 6 |
|---|---|---|---|---|---|---|---|---|---|
| b (5, 1) | 1.08e-4 / 4.27e-3 | - | - | - | - | - | 1.44e-4 | 3.7e-4 | - |
| s25 (2.5, 1) | 1.15e-4 / 4.98e-3 | 2.5e-5 (1.9e-4) | 5.1e-4 (1.5e-2) | 1.3e-13 | 1.4e-6 | 2.6e-8 / 3.0e-4 | 1.42e-4 | 3.9e-4 | 0.005 |
| s10 (10, 1) | 1.05e-4 / 4.05e-3 | 7.3e-6 (2.2e-4) | 2.7e-4 (1.4e-2) | 0 | 6.2e-7 | 8.7e-9 / 3.0e-4 | 1.45e-4 | 3.6e-4 | 0.033 |
| g05 (5, 0.5) | 4.69e-5 / 1.54e-3 | 6.5e-5 (1.5e-4) | 5.6e-3 (8.9e-3) | 0 | 4.4e-7 | 8.1e-8 / 3.4e-3 | 1.26e-4 | 8.5e-5 | 0.034 |
| g2 (5, 2) | 2.60e-4 / 1.47e-2 | 1.9e-4 (1.9e-4) | 9.1e-3 (2.4e-2) | 0 | 1.7e-5 | 2.6e-7 / 1.1e-3 | 1.56e-4 | 6.7e-4 | 0.033 |

Sensitivity d ln P/d ln(parameter) of the odd shell power at the last dump (fit over three
windows; band maximum, with the error propagated from the power errors):

| parameter | k < 6 | 6 <= k < 12 | 12 <= k <= 16 | 16 < k <= 32 | linear |
|---|---|---|---|---|---|
| s (2.5, 5, 10) | 6.3e-7 (2.4e-5) | 1.8e-6 (2.5e-5) | 2.3e-5 (1.0e-4) | 5.6e-4 (7.5e-3) | 9.5e-14 |
| sigma (0.5, 1, 2) | 1.1e-6 (2.4e-5) | 1.3e-5 (2.6e-5) | 8.8e-5 (6.6e-5) | 1.06e-2 (1.19e-2) | 0 |

What this says:
- The window changes the evolved USR spectrum at N_f only through numerical error, which is
  consistent with linear theory (no dependence). Up to k_max/2 = 16 dk the shifts are at most
  1.9e-4 (sigma = 2) and 7.3e-6 to 6.5e-5 for the other windows, at least 100 times below
  U-A2's 0.02. Up to k_max they are at most 9.1e-3.
- sigma matters more than s. The shift grows with k and has a sign (`fig/fig_usr_shift_Nf.png`):
  sigma = 2 raises the top shells and sigma = 0.5 lowers them. A larger sigma puts each mode
  in at larger k/aH, so it is evolved for longer on the grid before it exits
  [JUDGEMENT, JOURNAL entry 1]. The per-mode error orders as sigma = 2 > 1 > 0.5, as
  predicted.
- Shells that left the window before USR change by at most 1.7e-5 per mode (sigma = 2) and
  1.4e-6 (s), with no trend above the error.
- During the passage (cN < 4.5) the NR difference between windows reproduces the linear
  difference to 2e-5 to 2.3e-4 of the latter. The one-point rms of W R follows each window's
  linear value within 6.8e-4 at every dump, where the linear variances differ by up to a
  factor 3. At N_f the five windows agree within 5.9e-4 (0.494607 to 0.494898; reference
  0.494565).
- Second order: E/O rms is 1.3e-4 to 1.6e-4, about 2.9e-4 times the rms of R (U256:
  2.8e-4, `../usr/README.md`:164). In a single run at 128^3 it is the main departure from
  linear theory for k up to about 17 dk (`fig/fig_usr_second_order.png`). Above that the
  first-order discretisation error dominates. The even part depends on sigma by 15 percent
  of itself and on s by 1 to 2 percent.
- Not window-independent: the constraint records. Late in USR, <|H|/[H]> and <|M|/[M]>
  differ from the baseline by factors up to 21.7 (sigma = 2) and down to 0.14 (sigma = 0.5)
  (prediction W6 refuted). At cN = 10, H is at the floor 2.1e-14 for every window. M is
  1.5e-3 to 1.65e-3 for sigma <= 1 and 6.0e-3 for sigma = 2 (`fig/fig_usr_constraints.png`).
  In SR the late records converge.
- Slow-roll contrast (64^3): per-mode error 3.6e-5 to 3.7e-4 for k <= 8; shell shift for
  k <= 8 at most 4.3e-4 (sigma = 2); baseline even/odd 2.9e-7 (`results/scan/table_sr.md`).

Prediction record (JOURNAL entry 5): W1, W3a, W4, W5, W7, W8, the cost prediction and P-a
hold. W2 holds as registered but failed its per-mode clause (max |E|/|ref| 2.4e-2 on single
small modes) and its claim that the second-order part does not show in one run. W3b holds
but its premise (linear shift of order max_t|ref|) failed for USR. W6 and P-b are refuted.

Card-hours: 0.384 (job 4740, run E-20261120-222424-0eb754b). Processor runs: reference
25 s, analysis 221 s and post-hoc 12 s, each on 2 cores.

## Requests

- To the E-stoch-inf lead: the G2 criterion "sensitivity to window-function parameters" can
  be stated from the table above. The spectrum at N_f is window-independent within the
  numerical error (at most 1.9e-4 up to k_max/2, 9e-3 up to k_max), as linear theory
  requires. The constraint records are not window-independent late in USR (W6 refuted).
  Their acceptance text should not assume they are. RISKS R8 can record the scan as done.
- To the E-stoch-inf lead / core (optional, no run requested here): the late-USR record
  <|M|/[M]> depends on sigma by up to a factor 21. A check of whether this is the injection
  history (first-order truncation of modes put in at k/aH = sigma) or the normalisation [M]
  needs a run where one of the two is changed. None was made here.
