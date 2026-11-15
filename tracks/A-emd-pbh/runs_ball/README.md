# runs_ball: first full-relativity runs of Track A (SR-1, SR-2)

Helper package of A-emd-pbh, wave 2 (2026-11-15). The expanding dust ball of data set 2t
(expball smoothed top-hat core, Delta = 1 inside R1 = 2.4 M, compensated at 6 M, inside an
Einstein-de Sitter ball with H R_b = 0.5 and a C^4 taper; run
A-emd-pbh-20261115-130609-947c898) evolved with the release card executable of core-v0.3
and compared with the exact solution (`expball/exact.py`) in invariants only.
Specification: `stage/G1/STATUS.md` section 3. Predictions and outcomes, with every run id:
`JOURNAL.md` (entries 1-4). Figures: `figs/` (each looked at).

## Results (details and numbers with run ids in JOURNAL.md entry 3)

| | SR-1, lapse 1, shift 0 (geodesic slicing) | SR-2, conformal-time lapse + Gamma-driver |
|---|---|---|
| runs (dx = M/2; dx = M) | A-emd-pbh-20261115-153843-7172b66; -155056-ec1b816 | A-emd-pbh-20261115-153845-7172b66; -155056-ec1b816 |
| reaches | t = 33.0 (dx = M/2), 30.3 (dx = M): non-finite, growing H at the core edge | t = 53 (end) |
| core turnaround, mean proper-time error (dx = M/2) | -0.022 M (-0.13 per cent) | +0.043 M (+0.26 per cent) |
| largest radius R_max, mean error (dx = M/2) | +0.07 per cent | +0.10 per cent |
| core shells, largest abs(R/R_exact - 1) at tau = 16.9 (dx = M; M/2) | 5.6e-2; 6.2e-3 | 2.1e-2; 7.5e-3 |
| first horizon, horizon mass | not reached (unstable at t = 33 < 44.35) | none: the collapsed core lies inside one cell (largest 2m/R on the axis 0.34; exact R_AH = 0.161 M) |
| gauge pathology | grid-scale constraint violation, first in the outer ball, then at the core edge; grows faster on the coarser mesh | lapse pulse from the edge of the core reaches the centre at t ~ 6.5 at both resolutions, central lapse 1.85 instead of 1.34; the core reaches its crunch proper time at t ~ 35 and its dust re-expands through the centre |

The horizon-formation time and the horizon-mass error against the source paper's level
(about 1e-3, `refs/arxiv_2611.12831/src/main.tex` lines 945 and 1484) were NOT measured:
see the Requests. Figures of the pathologies: `figs/sr1_n256_gauge.png`,
`figs/sr1_n256_fields.png`, `figs/sr1_n128_fields.png`, `figs/sr2_n256_gauge.png`,
`figs/sr2_n256_fields.png`, `figs/sr2_n256_horizon.png`, `figs/sr2_n128_gauge.png`;
resolution comparison `figs/fig_resolution_summary.png`.

dx = M/4 to t = 20 (prediction R, JOURNAL entry 4; outcome entry 6, written by the lead):
A-emd-pbh-20261115-164539-0b18e84 (SR-1) and -164541-0b18e84 (SR-2), analysis
A-20261115-182657-53da696. R1, R3, R4 hold; R2 holds for SR-1 (mean turnaround error
-0.0125 M, core |eps| at tau = 16.894 7.6e-4) and fails for SR-2 on the turnaround time
(+0.031 M); core-shell errors fall at apparent order 3.0-4.3 between M/2 and M/4.

## What is here

| file | content |
|---|---|
| `common.py` | model of data set 2t, readers of trajectories, histories, formatted-table lines, horizon summaries, snapshots; areal radius and Misner-Sharp mass in spherical symmetry (fourth-order dR/dr along the line) |
| `prep.py` | reorders the lattice particles so that the tracked ones come first (tag = position; `--nlat 76` makes the h = M/4 lattice); exact references per tracked particle and global (turnaround, trapping, crunch, horizon mass on slices of constant proper time m_AH(tau), central a(tau) and rho_c(tau)); step plan of SR-1 from the exact coordinate speed of light |
| `compare.py` | the comparison: areal radius against proper time per particle, turnaround, trapping (R = 2m) and crunch times, Misner-Sharp mass and compactness on the x axis, finder mass against the exact horizon mass of the same slice, central lapse and density, constraints, gauge maps; numbers JSON, series npz and five figures per run |
| `fields.py` | z = 0 slices of the field dumps (E, lapse, H, Theta) |
| `summary.py` | resolution comparison of several runs (`fig_resolution_summary`) |
| `sr1.athinput`, `sr2.athinput` | input decks (dx = M/2 over [-64, 64]^3; other meshes by command-line overrides) |
| `run_cpu.sh` | processor driver (SR-1 with restart segments); the release processor executable is single-threaded, so it was not used for production (JOURNAL entry 2) |
| `runreg.py` | registration by hand (`local`, `card`, `finish`) when `harness/bin/nrpic-run` refuses the shared worktree |
| `after_m4.sh` | analysis of the dx = M/4 runs once they have finished |
| `figs/` | PNG copies of the figures |

## How to rerun

    cd /data/haiyangw/nrpic/wt/A-emd-pbh
    R=tracks/A-emd-pbh/runs_ball
    .venv/bin/python $R/runreg.py local --cores 4 --purpose "..." -- .venv/bin/python $R/prep.py --out '$NRPIC_RUN_DIR'
    # card list file, one line per run (paths absolute):
    #   sr1 <wt>/$R/sr1.athinput particles/particle_file=<prep>/..._lat38_track.nrp particles/traj_ntrack=1705
    .venv/bin/python $R/runreg.py card --wall 00:40:00 --list <list> --purpose "..."
    .venv/bin/python $R/runreg.py finish <run id>
    .venv/bin/python $R/compare.py --prep <prep dir> --seg <run dir>/sr1 --gauge sr1 --dx 0.5 \
        --label sr1_n256 --out <dir> --figdir $R/figs
    .venv/bin/python $R/fields.py --seg <run dir>/sr1 --label sr1_n256 --out <dir> --figdir $R/figs

The SR-1 restart segments (cfl 0.03125 to t = 44.3568, then 0.0078125 to 44.4472, from
`rst/ball.00001.rst` of the previous segment, `output3..6/dt` 0.02 and 0.004) were
prepared but not run, because SR-1 became non-finite before t = 42.

## Requests

- **core** (gauge): neither tested slicing reaches the first horizon of an expanding
  ball with a bound core. Geodesic slicing with a fixed shift becomes non-finite at
  t = 33 (dx = M/2), the constraint violation growing at the edge of the collapsing core
  and faster on coarser meshes; the conformal-time lapse sends a pulse from the edge of
  the core (not only from a sharp surface, as core saw) that reaches the centre at
  t ~ 6.5 with the central lapse 1.85 against 1.34, the same at dx = M and M/2. Please
  try, in this order, a lapse driven towards the proper time of the dust (lapse equal to
  1/W of the local matter, or a driver relaxing to it) and the K_ref lapse of
  `outbox/20261115T1320Z__to-core__phase1-generator-and-gauge-options.md`; when one is
  published under `scratch/core/exe/core_gauge/`, this package repeats SR-1 with it
  (decks and comparison are ready).
- **core** (resolution of the first horizon): the first trapped sphere of data set 2t has
  areal radius 0.161 M (m = 0.0805 of M = 1.01); in near-Eulerian coordinates it lies
  inside one cell of dx = M/2. A horizon-mass test needs about five levels of refinement
  at the centre with a particle lattice matched to the finest level. Please state whether
  AthenaK can sub-cycle the levels in time (with one global step the finest level makes
  the run about 30 times dearer) and the recommended refinement for a collapse to a
  horizon 1/60 of the ball size.
- **core**: the time step ignores the coordinate speed of light (G2 OPEN item 12): SR-1
  needs restarts with a smaller `cfl_number` (six stages from cfl 0.25 to 0.0078 in the
  last 2.5 M); and a run that has gone non-finite continues with status 0 (OPEN item 11;
  SR-1 ran 9 M past its blow-up). The release processor executable runs on one thread
  (about 200 s per cycle at 128^3 on the loaded machine), so small runs go to the cards.
- **orch**: `harness/bin/nrpic-run submit` refuses whenever any helper of the same
  worktree has an untracked file, so helpers sharing a worktree cannot register through
  it; every run of this package was registered by hand (`runreg.py`). Proposal: check
  only tracked files and the run's own inputs, or allow untracked files outside the
  submitting package.
- **lead of A-emd-pbh**: for the G2 horizon-mass criterion choose data whose first
  trapped sphere encloses most of the bound mass (a larger or denser core, so that
  R_AH is several M), or plan for refinement; data set 2t is good for the turnaround and
  shell errors only. G2 "turnaround converges in mesh spacing": order from the dx = M/4
  runs (pending; dx = M is not in the asymptotic range).
