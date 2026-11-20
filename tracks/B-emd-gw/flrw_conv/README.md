# flrw_conv: G2 criterion (a) of Track B

Scale-factor error and linear growth rate of the particle FLRW run, converging in
particle number and mesh, in the production configuration (helper package of B-emd-gw,
wave 3 round 1). Design, predictions and outcomes: `JOURNAL.md`.

State (2026-11-20 14:35 PST): PAUSED by locks/PAUSE. Design, predictions, initial data and
analysis scripts done; card job J1 queued (Slurm 4746, run B-20261120-222955-c8e16e3);
16^3 processor runs P1 running (B-20261120-223006-24448ac); J2 and J3 not submitted; no
outcome yet. Restart instructions: last entry of `JOURNAL.md`.

## Contents

| Path | What |
|---|---|
| `JOURNAL.md` | design, cost, predictions (entry 1), outcomes |
| `inputs/flrw_prod.athinput` | leg F deck: homogeneous dust, production configuration, box 1.35085 |
| `inputs/mode_prod.athinput` | leg B deck: test B of arXiv:1904.07841, production configuration, step limit 0.002 |
| `scripts/build_ic.sh` | initial data with `cosmo/ic/make_lattice.py` and `make_east.py` |
| `scripts/ic_stats.py` | deposited contrast and potential of the leg-F initial data |
| `scripts/run_cpu.sh` | processor runs on core's threaded executable |
| `scripts/omp_places.py` | thread placement (copy of `scripts/omp_places.py` of core/build-openmp) |
| `scripts/figstyle.py` | figure style (copy of `harness/style/figstyle.py`) |
| `scripts/flrwlib.py` | readers, references a(t) and D(a), growth-rate estimators, decaying-mode fit |
| `scripts/analyze_f.py`, `scripts/analyze_b.py` | analyses and figures of legs F and B |
| `inputs/batch_j1.list`, `batch_j2.list`, `batch_j3.list`, `cpu_p1.list` | card jobs J1-J3 and processor runs P1 |

## Runs

| Run id | What | State |
|---|---|---|
| B-20261120-222902-6b0be3c | initial data, leg F all meshes, leg B 16/32 | completed |
| B-20261120-222908-8aede2c | initial data, leg B 64/128 | completed |
| B-20261120-223448-7f7c034 | initial data, Poisson-like start (A3) | completed |
| B-20261120-222955-c8e16e3 | card job J1 (Slurm 4746): F and B at 32^3 | pending in the queue |
| B-20261120-223006-24448ac | processor runs P1: F and B at 16^3 | running |

## Requests

None yet.
