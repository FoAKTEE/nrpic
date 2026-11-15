# Slow-roll ladder toward gate G1 (E-stoch-inf, wave 2 helper package)

The slow-roll (SR, quadratic) case of arXiv:2512.14649 run in this repository's AthenaK with
core's published executables of branch `core/scalar-2` (a58e95b,
`scratch/core/exe/core_scalar-2/`), judged by the owner's thresholds A1-A5 (SCOPE 4,
restated in `JOURNAL.md` entry 1 before any run): power spectrum against the linear
(Mukhanov-Sasaki) and slow-roll results, freezing of super-horizon modes by the criterion
of SPEC 7.3, convergence of the constraints. Predictions and outcomes: `JOURNAL.md`.
State of the runs and verdicts: `JOURNAL.md`, last entry.

## Contents

| Path | What |
|---|---|
| `inputs/sr_base.athinput` | base input: SR case in code units (G = 1, time unit 1/H*, box 2 pi), initial slice at N* (`id = stochastic`), Mukhanov-Sasaki sources, geodesic slicing, Courant 0.25, dumps every 0.5 time units with phi, Pi, chi, gt_ij, K, At_ij, alpha, H, M_i, E |
| `inputs/modes_n{64,256,1024,4096}.txt` | mode files (R, dR/dtau at N* per shell); 64 = core's `problems/scalar/sr_stochastic_modes.txt`, the others from core's `make_case.py --kstart 100` (run E-20261115-171633-f574079) |
| `inputs/jobA.list`, `jobB.list`, `jobC.list` | card batches (P256; P256m + L256p; L256m + N = 64, 128 rungs, halving, negative controls) |
| `inputs/proc32.list`, `proc64.list` | processor runs (N = 32 rung; N = 64 hedge to t = 4.5) |
| `scripts/ladder_lib.py` | own NRSFDMP2 reader, mode coefficients on the hemisphere, R^NR extraction, linear reference (background + MS per shell, window), amplitudes from `../noise/ref/philox_ref.py` |
| `scripts/ladder_analysis.py` | `extract` (per dump R^NR, reference, constraint statistics; A1), `pair` (odd/even parts under s -> -s), `judge` (A2, A3, shell spectrum) |
| `scripts/analyse_all.py` | runs the three on every ladder run found in given run directories |
| `scripts/verdicts.py` | A1-A5, negative control, cost per step -> `summary.json` |
| `scripts/make_figures.py`, `scripts/figstyle.py` | figures (style copied from `harness/style/figstyle.py`) |
| `scripts/selftest.py` | reader against core's reader; R^NR at t = 0 against the reference; seed control |
| `scripts/run_list_cpu.sh` | runs a list on the processors inside a registered run |
| `fig/proc32/`, `results/proc32/` | figures and JSON of the N = 32 rung (run E-20261115-173540-b69c63f) |

Definitions (R^NR, D_n, Q_n, N_k, odd/even parts): `JOURNAL.md` entry 1.

## How to rerun

From the worktree root, with the worktree's `.venv` (`harness/bin/nrpic-env create
--no-kokkos`):

    X=/data/haiyangw/nrpic/scratch/core/exe/core_scalar-2
    I=tracks/E-stoch-inf/ladder/inputs
    # processors (32^3, about 9 min serial per 8 e-folds)
    harness/bin/nrpic-run submit --package tracks/E-stoch-inf/ladder --kind scouting \
      --gate G1 --launcher local --cores 6 --background --input $X/athena_cpu \
      --input $I/proc32.list --purpose "..." -- \
      bash tracks/E-stoch-inf/ladder/scripts/run_list_cpu.sh $X/athena_cpu $I/proc32.list
    # cards (one Slurm job per list)
    harness/bin/nrpic-run submit --package tracks/E-stoch-inf/ladder --kind scouting \
      --gate G1 --launcher batch --exe $X/athena_gpu --list $I/jobA.list --wall 00:45:00 \
      --purpose "..."
    # analysis of any set of run directories (registered)
    harness/bin/nrpic-run submit --package tracks/E-stoch-inf/ladder --kind scouting \
      --gate G1 --launcher local --cores 8 --purpose "..." -- bash -c \
      'cd tracks/E-stoch-inf/ladder/scripts && export OMP_NUM_THREADS=8 && \
       python3 analyse_all.py --runs RUNDIR... --out "$NRPIC_RUN_DIR/res" && \
       python3 verdicts.py --res "$NRPIC_RUN_DIR/res" --rundirs RUNDIR... \
         --out "$NRPIC_RUN_DIR/summary.json" && \
       python3 make_figures.py --res "$NRPIC_RUN_DIR/res" --out "$NRPIC_RUN_DIR/fig"'

Trap: nrpic-run runs its command without a shell; write `$NRPIC_RUN_DIR` only inside
`bash -c '...'` (run E-20261115-172521-e098160 wrote into a directory named
`$NRPIC_RUN_DIR`).

Disk: a 256^3 dump with the metric and the constraints is 2.95 GB; job A writes 18 of
them (53 GB), job B 10 + 10 (13 + 30 GB), job C about 40 GB.

## Requests

(filled at the end of the package)
