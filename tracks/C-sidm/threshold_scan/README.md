# C-sidm/threshold_scan: first cluster runs with collisions, and the threshold scan inputs

Wave-2 package of Track C (helper of the lead, 2026-11-15). It prepares, predicts, runs on
the cards and analyses the first collisional cluster runs CC1/CC2 named in
`../stage/G1/STATUS.md` section 4 (King b = 1 of 2009.08163 at the collisionless threshold
y0 = 0.334032 and on the stable side y0 = 0.314; Kn = lambda_c/H_c = infinity, 10, 1;
N = 10^5; 300 M), and leaves the longer threshold scan as prepared inputs with its cost
(`SCAN.md`). Predictions and outcomes of every test: `JOURNAL.md`. Run manifests:
`../runs/<run_id>/manifest.json`; outputs under `/data/haiyangw/nrpic/scratch/C-sidm/<run_id>/`.

## Files

| File | Content |
|---|---|
| `common.py` | paths, the mesh of the runs, model loading (static metric from the table), Kn to sigma~ (K = 1/(rho0_c H_c)), readers of the AthenaK histories, snapshots and trajectories, Killing energy from `.trajmet.bin` |
| `make_ic.py` | particle files of CC1/CC2 at N = 10^5 through the equilibria package (run C-20261115-165832-fccee3a) |
| `make_decks.py` | the six decks `inputs/cc{1,2}_kn{inf,10,1}.athinput` from the first paper's static M/4 deck `problems/st/st_migration.athinput`, and the card lists `inputs/batch_{1,2,3}.list` |
| `predict.py` | predictions from the particle files alone: expected collisions per step (all pairs of every collision cell; the operator's random pairing), energy defect per collision at the particles' metric, Killing-energy change, production of particles above E0 and of unbound ones (run C-20261115-170404-af74c6d) |
| `smoke.py` | processor smoke of the decks: start-up, rest mass, first-step sum_P against the prediction (run C-20261115-172003-6422b6a) |
| `analyze.py` | analysis of the card runs: budgets, collision counts, lapse, mass radii, Killing-energy tail, figures `fig_cc_*.png` |
| `make_scan.py`, `SCAN.md`, `inputs/scan/` | inputs and cost of the longer threshold scan (not run) |
| `figs/` | copies of the figures looked at (PNG) |

## Rerun

From the worktree root, each step registered (`harness/bin/nrpic-run`, `--package
tracks/C-sidm/threshold_scan`):

    harness/bin/nrpic-run submit --launcher local --kind scouting --gate G2 --package tracks/C-sidm/threshold_scan --cores 4 --purpose "..." -- python3 tracks/C-sidm/threshold_scan/make_ic.py
    .venv/bin/python tracks/C-sidm/threshold_scan/make_decks.py          # writes inputs/ (commit them)
    harness/bin/nrpic-run submit --launcher local ... -- python3 tracks/C-sidm/threshold_scan/predict.py --K 16 --pairings 100
    harness/bin/nrpic-run submit --launcher local ... -- python3 tracks/C-sidm/threshold_scan/smoke.py --nlim 4 cc1_kninf cc1_kn10 cc1_kn1
    harness/bin/nrpic-run submit --launcher batch --kind scouting --gate G2 --package tracks/C-sidm/threshold_scan --list tracks/C-sidm/threshold_scan/inputs/batch_1.list --wall 00:55:00 --purpose "..."   (and batch_2, batch_3)
    harness/bin/nrpic-run submit --launcher local ... -- python3 tracks/C-sidm/threshold_scan/analyze.py <batch run ids>

The IC run directory is fixed in `common.IC_RUN`; another one needs `make_decks.py --ic-dir`.

## Requests

- core: (1) a dynamically accessible perturbation of `nrpic_cf` models (the lead's open
  request "perturbation-recipe" of 13:20Z; 2009.08163 lines 846-866); the prepared scan A
  uses the first paper's coherent one-percent kick meanwhile. (2) A pair-energy correction
  at the particles' own metric before the short-mean-free-path runs of G3: predicted defect
  in the King threshold model with M/4 collision cells at N = 10^5 is +1.7e-10 of sum M W
  per collision (run C-20261115-170404-af74c6d), 2e-4 over 300 M at Kn = 1 and about 2e-3
  at Kn = 0.1. (3) A diagnostic of the spacetime's energy (ADM mass by a surface integral,
  or a Komar-type volume integral) in a history file, so that the energy budget can be
  closed against the spacetime and not only through the matter sums.
- orchestrator: card time for `SCAN.md` (about 22-24 card-hours of C's 45 toward the next
  gate); these decks cannot run on processors (about 140 s per cycle on four threads, run
  C-20261115-172003-6422b6a, against 4800 cycles per 300 M).
- C-sidm lead: choose the perturbation of scan A (kick or the dynamically accessible
  force); the collision cells of CC1/CC2 hold 2.3 particles on average (about 20 in the
  core): fine for counts and budgets, low for relaxation fidelity (core's advice: about 100
  per cell); for G3 consider `coll_cell_factor = 2` or N = 10^6.
