# D-pre-2: the dark-matter spike in the probe limit

Work package of D-bh-dress (helper). Reference: Sadeghian, Ferrer & Will 2013,
arXiv:1305.2619 ("SFW", source `kb-data/raw/arxiv/1305.2619/v1/src/SFWpaper.tex`); Kerr
sequel Ferrer, da Rosa & Will 2017, arXiv:1707.06302 ("FdRW", `.../1707.06302/v2/src/`).
Predictions and outcomes, including the failed ones: `JOURNAL.md`. Units G = c = m_BH = 1
(written Gm), R_S = 2 Gm, horizon radius 2 Gm.

## Contents

| File | What it is |
|---|---|
| `spike_lib.py` | Semi-analytic reference (decision 0010: reference solution, no time evolution): Schwarzschild orbits (turning points, radial action, coordinate-time radial period, capture angular momentum L_c(E), E_min(r)), Hernquist DF and the inverse of its radial action (table), adiabatically grown DF f(E, L), densities for constant f and for a Hernquist cusp: relativistic with the canonical or the SFW-printed radial action, Newtonian with the Gondolo-Silk (GS) capture ansatz. |
| `paper_curves.py` | Digitizer of the printed curves (SFW Figs. 1, 3 from their PDF vector paths; FdRW fig_rho_a, fig_rho_hern from their PGF). Standard library only, run with `python3 -I`; output to scratch, never committed. |
| `spike_reference.py` | P1: the reference against the printed numbers and curves; `figs/ref_constf.png`, `figs/ref_hernquist.png`. |
| `sample_spike.py` | P2 initial data: species 0 drawn from the final DF (stationary), species 1 loss-cone boundary probes; `.nrp` files for AthenaK. |
| `spike_geodesic.athinput` | AthenaK input: `nrpic_geodesic`, analytic Cartesian Kerr-Schild metric, a = 0, midpoint pusher. |
| `drive_runs.py` | Runs the CPU executable on several particle files in parallel. |
| `analyze_spike.py` | P2 analysis: binned density against the reference, invariants, horizon crossings against exact geodesics; `figs/stationarity_profile.png`, `figs/stationarity_time.png`, `figs/invariants_losscone.png`, `figs/losscone_dt0.05.png`, `figs/losscone_dt0.025.png`. |
| `compare_dt.py` | P2e: crossing-time offsets for two time steps; `figs/crossing_dt.png`. |
| `particle_budget.py` | P3: particle number to resolve the profile inside 20 Gm; `figs/particle_budget.png`. |
| `register_run.py` | Writes `tracks/D-bh-dress/runs/<run_id>/manifest.json` around a command. |

## How to rerun (from this directory; the run ids are in `../runs/`)

```
python3 register_run.py --purpose P1 -- python3 spike_reference.py --out {OUT}            # 2 min
python3 register_run.py --purpose IC -- python3 sample_spike.py --out {OUT} --n0 48000 --n1 2400 --nfiles 12 --ecut 0.99 --seed 20261115
python3 register_run.py --cores 12 --purpose A -- python3 drive_runs.py --ic <IC> --out {OUT} \
    --files spike_0.nrp ... spike_11.nrp -- time/tlim=20000 particles/snap_dt=250 particles/dt=0.05   # 19 min
python3 register_run.py --purpose B -- python3 drive_runs.py --ic <IC> --out {OUT} --files spike_lc.nrp \
    -- time/tlim=1500 particles/snap_dt=2 particles/dt=0.05     # and dt=0.025 for B2
python3 analyze_spike.py --ic <IC> --runs <A>/spike_* --out <dir>    # or --runs <B>/spike_lc
python3 compare_dt.py --a <analysis of B> --b <analysis of B2> --out <dir>
python3 particle_budget.py --out <dir>
```
Executable: `/data/haiyangw/nrpic/.work/build_cpu_c1/src/athena` (main, read-only); no
source was changed and no card-hour was used.

## Results

RESULTS_PLACEHOLDER

## Requests

REQUESTS_PLACEHOLDER
