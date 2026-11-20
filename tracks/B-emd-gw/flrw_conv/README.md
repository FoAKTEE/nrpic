# flrw_conv: G2 criterion (a) of Track B

Scale-factor error and linear growth rate of the particle FLRW run, converging in
particle number and mesh, in the production configuration (helper package of B-emd-gw,
wave 3 round 1). Design, predictions and outcomes: `JOURNAL.md`.

State: design and predictions written; runs in progress.

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

## Requests

None yet.
