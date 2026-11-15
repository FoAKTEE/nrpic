# secondary_infall: D-pre-3 of Track D (helper package)

Newtonian secondary infall of collisionless dust onto a point mass (the black hole) in an
Einstein-de Sitter background, as semi-analytic references and a spherical-shell
reference calculation (decision 0010: no standalone simulation code; the particle version
runs later in AthenaK's Newtonian mode, branch `core/newton`, and in full relativity).
From these references it fixes the parameters of the AthenaK runs: `RUNS.md`.

Units G = c = 1, M = initial mass of the hole, eps = H_i M, t_i = 2/(3 eps). The set-up is
the scoping run's (`../scope/`): uniform dust in the unperturbed Hubble flow at t_i around
the seed.

## What is here

| File | What it is |
|---|---|
| `JOURNAL.md` | predictions written before each run, outcomes after (also the failed ones) |
| `RUNS.md` | the first Newtonian-mode run and the first full-relativity run, parameters, predicted numbers and profiles, cost |
| `common.py` | figure style loader, checksums, closed-form radial Kepler orbit (turnaround and collapse times) |
| `register_run.py` | runs one script as a registered run (manifest under `../runs/<run_id>/`, output under `scratch/D-bh-dress/<run_id>/`); refuses to run with uncommitted changes in this directory |
| `rd_checks.py` | test 1: radiation-era turnaround and the radial-orbit factor against what 1901.08528 and 2106.07480 print |
| `selfsimilar.py` | test 2: the self-similar collisionless infall onto a point-mass seed (Bertschinger type), fixed-point iteration |
| `shells.py` | test 3: spherical dust shells with shell crossing; centre passing (Newtonian-mode reference) or absorbing (capture by the hole, full-relativity proxy); optional tangential velocity dispersion with capture for L < 4 M_bh |
| `analyze.py` | combines tests 2 and 3, checks against the closed forms, growth curves, predicted profiles, run-parameter table with the scoping cost model |
| `figs/` | copies of the figures of the registered runs (run ids below) |
| `run_plan_D-bh-dress-20261115-125613-248fdaf.txt` | the run-parameter and cost table of the analysis run (copied from its output) |

## Figures (all looked at; run ids in `JOURNAL.md`)

- `figs/rd_checks.png`, `figs/rd_boost_mc.png`: test 1 (run D-bh-dress-20261115-122051-bf0d6b1).
- `figs/selfsimilar.png`: test 2 (run D-bh-dress-20261115-123813-97afeea).
- `figs/growth.png`, `figs/profiles_eps0.01.png`, `figs/profiles_eps0.03.png`,
  `figs/selfsim_check.png`, `figs/phase_space.png`, `figs/angular_momentum.png`: test 3 and
  the run plan (analysis run named in `JOURNAL.md`).

## How to rerun

From the worktree root (`wt/D-bh-dress`), with the package committed (the helper refuses
otherwise), one core each:

    S=tracks/D-bh-dress/secondary_infall
    python3 $S/register_run.py $S/rd_checks.py "test 1"
    python3 $S/register_run.py $S/selfsimilar.py "test 2" -- --taumax 300
    for c in absorb_e0.01 absorb_e0.03 pass_e0.01_s0.5 pass_e0.03_s0.5 pass_e0.1_s0.5_a100 \
             absorbL_e0.01_sig0.02 absorbL_e0.01_sig0.05 absorbL_e0.01_sig0.1 absorbL_e0.01_sig0.2 \
             absorb_e0.03_rw3 pass_e0.03_s0.5_rw3; do
        python3 $S/register_run.py $S/shells.py "test 3 $c" -- --config $c; done
    python3 $S/register_run.py $S/analyze.py "analysis" -- --ss <test-2 output dir> \
        --shells <the test-3 output dirs>

Wall times on one core: test 1 15 s, test 2 2 min, shells 2 s to 6 min each, analysis 1 min.
Python 3.10 with numpy 2.2, scipy 1.15, matplotlib 3.10 (no extra packages).

## Requests

See `RUNS.md`, section "Requests to other owners".
