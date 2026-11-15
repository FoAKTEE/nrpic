# langevin: stochastic delta-N reference statistics (work package E-pre-3)

Reference statistics outside numerical relativity for Track E: a Langevin first-passage
solver for stochastic delta-N, its validation against analytic results printed in
1308.4754 and 2206.11234, reference distributions of delta N for the two test cases of the
reproduction specification (`../spec/SPEC.md`), and an assessment of the stochastic-lattice
comparison of 2405.10692. Everything here is a semi-analytic reference or an analysis tool
in the sense of decision 0010: zero-dimensional stochastic and ordinary differential
equations, no spatial simulation. Journal with predictions and outcomes: `JOURNAL.md`.

## Contents

| Path | What |
|---|---|
| `sdn/models.py` | potentials: quadratic with potential-position fixing, Higgs-like inflection with H0 fixing (locators in the file) |
| `sdn/langevin.py` | vectorised first-passage solvers: overdamped (Euler-Maruyama, Brownian-bridge crossing test, reflecting wall with exact image likelihood, importance sampling) and phase-space (RK4 drift + Ito noise with a 2x2 covariance, several end surfaces, Hermite crossing, importance sampling along the dominant noise direction) |
| `sdn/exact.py` | semi-analytic references: inverse Gaussian (drift-diffusion), moment recursion of the adjoint Fokker-Planck equation, BDF2 survival solver (density and Laplace transform), Sturm-Liouville eigenvalues, the closed-form characteristic function of quadratic inflation (2206.11234 appendix) |
| `sdn/linear.py` | classical background, flat-gauge linear modes with Bunch-Davies start, noise covariance tables at k_sigma = sigma a H, P_R(k), lattice shell counts |
| `scripts/run.py` | registers a run: `tracks/E-stoch-inf/runs/<run_id>/manifest.json`, output in `scratch/E-stoch-inf/<run_id>/` |
| `scripts/v1_drift_diffusion.py` | V1: exact drift-diffusion first passage (1308.4754) |
| `scripts/v2_quadratic.py` | V2: quadratic inflation, m = M_Pl (2206.11234, Fig. 2 set-up) |
| `scripts/ref_spec.py`, `scripts/ref_plot.py` | reference delta-N statistics for the two specification cases, and their figures |
| `scripts/ref_endinf.py` | end-of-inflation delta N of the inflection potential after USR |
| `results/*.json` | numbers of each registered run (the `run_id` field names the run) |
| `fig/*.png`, `fig/*.pdf` | figures (style `python/nrpic/figstyle.py`) |

## How to rerun

From the worktree root, with committed code (the wrapper refuses otherwise):

```text
P=tracks/E-stoch-inf/langevin/scripts
python3 $P/run.py --purpose "V1" --cores 8 -- python3 $P/v1_drift_diffusion.py      # ~2 min
python3 $P/run.py --purpose "V2" --cores 8 -- python3 $P/v2_quadratic.py            # ~2 min
python3 $P/run.py --purpose "ref" --kind production --cores 8 -- python3 $P/ref_spec.py inflection 1000000   # ~30 min
python3 $P/run.py --purpose "ref" --kind production --cores 8 -- python3 $P/ref_spec.py quadratic 1000000    # ~30 min
python3 $P/run.py --purpose "plots" --cores 4 -- python3 $P/ref_plot.py inflection /data/haiyangw/nrpic/scratch/E-stoch-inf/<run_id of ref_spec>
python3 $P/run.py --purpose "endinf" --cores 8 -- python3 $P/ref_endinf.py
```

Python 3.10 with numpy 2.2, scipy 1.15, mpmath 1.3, matplotlib 3.10 (system packages; no
virtual environment was needed). Seeds are fixed in the scripts (numpy SeedSequence).

RESULTS_PLACEHOLDER

## Requests

REQUESTS_PLACEHOLDER
