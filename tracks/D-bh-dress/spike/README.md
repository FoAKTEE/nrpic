# D-pre-2: the dark-matter spike in the probe limit

Work package of D-bh-dress (helper). Reference: Sadeghian, Ferrer & Will 2013,
arXiv:1305.2619 ("SFW"); Kerr sequel Ferrer, da Rosa & Will 2017, arXiv:1707.06302
("FdRW"). Predictions and outcomes: `JOURNAL.md`. Results: section "Results" below.

## Contents

| File | What it is |
|---|---|
| `spike_lib.py` | Semi-analytic reference (decision 0010: reference solution, no time evolution): Schwarzschild orbits (turning points, radial action, radial period, capture angular momentum, E_min), Hernquist DF and radial-action inversion table, adiabatically grown DF f(E, L), densities for constant f, Hernquist (relativistic with the canonical or the SFW-printed radial action; Newtonian with the GS capture ansatz). |
| `paper_curves.py` | Digitizer of the printed curves (SFW Figs. 1 and 3 from their PDF vector paths; FdRW fig_rho_a, fig_rho_hern from their PGF). Standard library only, run with `python3 -I`; output goes to scratch, never committed. |
| `spike_reference.py` | P1: reference calculation against the printed numbers and curves; figures `figs/ref_constf.png`, `figs/ref_hernquist.png`. |
| `sample_spike.py` | Draws test particles from the final DF (stationary species 0) and the near-separatrix loss-cone probe (species 1); writes the `.nrp` particle file for AthenaK. |
| `spike_geodesic.athinput` | AthenaK input: `nrpic_geodesic`, analytic Cartesian Kerr-Schild metric (a = 0), midpoint pusher. |
| `analyze_spike.py` | Reads the AthenaK snapshots: binned density against the reference, invariants, horizon crossings against the exact prediction; figures. |
| `figs/` | Figures of this package (our plots only; the digitized curves are drawn as reference lines). |

## How to rerun

```
cd tracks/D-bh-dress/spike
python3 spike_reference.py --out <scratch>/D-bh-dress/<run_id>          # P1, about 3 min
python3 sample_spike.py --out <scratch>/D-bh-dress/<run_id> ...            # P2 initial data
/data/haiyangw/nrpic/.work/build_cpu_c1/src/athena -i spike_geodesic.athinput \
    -d <rundir> particles/particle_file=<abs .nrp> ...                    # P2 run
python3 analyze_spike.py --run <rundir> --ic <ic dir> --out <dir>         # P2 analysis
```
Exact commands of each run: `tracks/D-bh-dress/runs/<run_id>/manifest.json`.

## Requests

(filled in at the end of the package)
