# tracks/C-sidm/scope: G0 scoping package of Track C (S3)

Helper package of owner C-sidm, written 2026-11-15. Read `SCOPE.md` first.

## Contents

| File | What it is |
|---|---|
| `SCOPE.md` | Problem statement, what the first paper established and what Track C must add, equilibrium families and parameter ranges, Knudsen-number conversion, exit criteria, test plan for the rows of brief section 10 held by Track C, risks with numbers, compute estimate, open items |
| `REFERENCES.md` | Every reference used, read at the source, with `file:line` locators; corrections to the brief |
| `JOURNAL.md` | Predictions P1-P4 written before the runs, and their outcomes |
| `scripts/register_run.py` | Registers one processor run: manifest in `tracks/C-sidm/runs/<run_id>/`, output in `scratch/C-sidm/<run_id>/` |
| `scripts/seq_monoenergetic.py` | Monoenergetic sequence, binding-energy maximum, check of the Wu-Most models (uses `python/nrpic/st_cluster.py`) |
| `scripts/king_sequence.py` | Independent solver of the truncated Maxwell-Boltzmann (relativistic King) equilibria of arXiv:2108.11967; maxima of the fractional binding energy, adiabatic-index criterion, b = 1 King check against arXiv:2009.08163 |
| `scripts/knudsen_costs.py` | Knudsen numbers of the candidate models, conversion to sigma/m, Monte Carlo collision requirements, measured costs parsed from the first paper's AthenaK logs |
| `figures/*.png` | Copies of the figures of the three registered runs (looked at; see JOURNAL) |

## Runs (all on the processors, one core, seconds each)

| Run id | Script | Result |
|---|---|---|
| `C-sidm-20261115-115344-eb8b752` | `seq_monoenergetic.py` | threshold y_c = 0.67961 (z_c = 0.4553); Wu-Most Table reproduced |
| `C-sidm-20261115-115348-eb8b752` | `king_sequence.py` | 2108.11967 Table reproduced to 8e-5; King b = 1 maximum and zero at y_0 = 0.33403, 0.78452 |
| `C-sidm-20261115-115400-eb8b752` | `knudsen_costs.py` | physical Kn_c 4e-20 to 2e-12; MC needs ~1e6 particles at Kn_c = 0.1; costs 1.7-17.5 s per M |

The third run reads AthenaK logs under `/data/haiyangw/nrpic/runs/` (main checkout,
untracked); their sha256 sums are in its manifest.

## How to rerun

From the worktree root, with the scripts committed:

    python3 tracks/C-sidm/scope/scripts/register_run.py --purpose "..." \
        --input python/nrpic/st_cluster.py -- python3 tracks/C-sidm/scope/scripts/seq_monoenergetic.py
    python3 tracks/C-sidm/scope/scripts/register_run.py --purpose "..." \
        -- python3 tracks/C-sidm/scope/scripts/king_sequence.py
    python3 tracks/C-sidm/scope/scripts/register_run.py --purpose "..." \
        --input tracks/C-sidm/scope/scripts/king_sequence.py \
        -- python3 tracks/C-sidm/scope/scripts/knudsen_costs.py

Each writes JSON and PDF/PNG figures to `scratch/C-sidm/<run_id>/`. Needs numpy, scipy,
matplotlib (system Python 3 of anta has them). The manifests are ignored by the
repository's `runs/` rule and must be added with `git add -f` on their exact paths, as
`harness/lib/nrpic_harness.py` (commit_paths, force_add) does.

## Requests

To the lead of C-sidm (who owns STATUS, JOURNAL, HANDOFF, RISKS and the outbox):
1. Post the brief corrections of `REFERENCES.md` (last section) to the orchestrator:
   direction of the mean-free-path transition (brief 384); arXiv:2602.17487 as
   collisional reference (brief 520, row 852); 1707.08666 in row 843; the G2 phrase
   "the literature value" of the threshold.
2. Ask for a raise of the GPU allotment of decision 0006 before G2 (estimate about
   45 card-hours for G2, 80-160 for G3, SCOPE.md section 8); G1 fits in the present 20.
3. Have the sibling package `tracks/C-sidm/gravothermal/` (truncated Maxwell-Boltzmann
   module `tmb.py`) compare its equilibria with run `C-sidm-20261115-115348-eb8b752`
   (independent implementations; maxima of eps_b listed in SCOPE.md 3.2).

To core (through the lead's outbox):
4. Initial data for the King family as particles (C-pre-4): the profiles exist here;
   needed is the `nrpic_cf` table route with the Hamiltonian-constraint solve used for
   the monoenergetic models.
5. A view on the Kn -> 0 reference run of the same King model with AthenaK's dynamical-
   spacetime GR hydrodynamics (`athenak/src/dyn_grmhd/` with Z4c) and an ideal-gas law.
6. A measurement of the cost per pair collision once a prototype of the collision
   operator exists (the G2 and G3 estimates assume it below the push cost).

To kb:
7. The identifier of "Gurian 2025" (collisional Boltzmann treatment of SIDM, cited by
   2601.17117 SIDM_MS.tex:672 and 2506.17641 sidmacc.tex:218); a check of the redshift
   definition in gr-qc/0601112 (SCOPE.md 3.3) against the authors' later papers.
