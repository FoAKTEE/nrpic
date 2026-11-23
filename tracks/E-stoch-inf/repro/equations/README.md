# repro/equations: the equations of arXiv:2401.08530 and arXiv:2512.14649, checked and mapped

Helper package of Track E (owner E-stoch-inf) in the reproduction of decision 0028, batch R1
(2026-11-22). The equations of both papers are checked with sympy and short numerical tests,
and every source term and step of the stochastic scheme of arXiv:2512.14649 is mapped to the
lines of `athenak/src/scalar_field/` (read only). No card time, no AthenaK run.

## Contents

| Path | What |
|---|---|
| `EQUATIONS.md` | the result: verdict per item (a)-(e) with locators, and the map of the code |
| `ERRATA.md` | misprints of the papers found here (E1-E17), each [VERIFIED] by a named check |
| `JOURNAL.md` | predictions before the runs, outcomes after |
| `scripts/adm_lin.py` | linearisation of the nonlinear ADM left-hand sides (plane wave, jets, exact background) |
| `scripts/check_equations.py` | items (a) and (b): linear equations, five gauge families, GI relations, coarse-grained residuals, negative controls, constraint propagation, BSSN, usual SI limit, P1:241-259 |
| `scripts/check_noise_amp.py` | item (c): Heaviside-window noise amplitude of P0 appendix D against numerical MS modes, SR and USR |
| `scripts/check_langevin.py` | item (d): the Langevin pair of P0 section V (sympy) and a Monte Carlo test of the Ito term |
| `scripts/check_code_map.py` | item (e): the formulas of `scalar_field_noise.cpp` (window, eps2, S_R, kick factors) against P1 |
| `scripts/make_figures.py` | matrix figure of all symbolic checks |
| `scripts/figstyle.py` | copy of `python/nrpic/figstyle.py` (figure style) |
| `scripts/run_all.sh` | runs everything into one directory |
| `fig/` | the figures of the registered run (looked at) |

## How to rerun

From the worktree root, with the worktree's `.venv` (sympy 1.14, scipy 1.15, numpy 2.2):

    harness/bin/nrpic-run submit --kind scouting --gate G2 --package tracks/E-stoch-inf/repro/equations \
        --purpose "repro/equations: sympy and numerical checks" -- bash tracks/E-stoch-inf/repro/equations/scripts/run_all.sh

or by hand `bash tracks/E-stoch-inf/repro/equations/scripts/run_all.sh <outdir>` (one core,
about 6 minutes; check_equations.py takes most of it). Outputs: `equations/results.json`,
`noise_amp/noise_amp.json`, `langevin/langevin.json`, `code_map/code_map.json`, `figures/`,
one `log.txt` per part. No script reads a downloaded file; the papers are cited by line only.

## Runs

| Run id | What | Cost |
|---|---|---|
| E-20261123-022009-a53e7ee | all checks (run_all.sh): 72 entries of check_equations, 10 of check_code_map, Langevin, noise amplitude, figures | 1 core, about 5 min, no card |

## Results in one paragraph

All source terms of both papers (S_Pi, S_K, S_Kt, S_A, zero sources of X, gt, Gamma and of the
constraints) are CONFIRMED as exact first-order identities in all five gauge families with
arbitrary gauge functions, and the constraints propagate without source under the sourced
evolution with the printed signs and are violated at first order when one sign is flipped.
Seventeen misprints are recorded (ERRATA.md), none of which the code inherits. Two statements
are NOT CONFIRMED: the USR noise amplitude of P0 appendix D (with the paper's own formula it
is sigma^2/3 of the printed value) and the Ito term of the lapse equation of P0 section V
(alpha^5, not alpha^3). The code follows P1 in every source term; it differs in scheme (rate at
each stage of a low-storage RK4, Fourier modes per shell, no FFT, no level-2 backreaction).

## Requests

- To `../langevin/` (same owner): use the corrected Ito term (alpha^5 <S^2>, or the Stratonovich
  form without a correction term) and note that the printed USR amplitude of P0 appendix D is
  not what the paper's own window treatment gives (ERRATA E14, E15). The figures of P0 section V
  were made with the printed amplitude, so a reproduction of the figures uses it, as a stated
  choice.
- To the lead (note): ERRATA E1-E17 for the working note; none changes the code.
- To core: none required. For information: level 2 backreaction (P1:487, 520) is not
  implemented (`scalar_field_noise.cpp:162-165`); P1 reports it changes the spectrum only at a
  small relative level, so it is not needed for the comparison against linear theory.
