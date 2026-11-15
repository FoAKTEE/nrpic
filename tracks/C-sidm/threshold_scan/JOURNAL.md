# JOURNAL of C-sidm/threshold_scan (wave 2, helper of C-sidm)

Package: the first cluster runs of Track C with the release card executable (core-v0.3):
the collisionless control and the collisional runs CC1/CC2 of `../stage/G1/STATUS.md`
section 4 (King b = 1 at the threshold and just below it, Kn = infinity, 10, 1), with
predictions first; inputs and cost of the longer threshold scan. Card time: at most three
card-hours in this wave. Predictions are written here before each run; outcomes after it,
also when a prediction fails. Run ids: `tracks/C-sidm/runs/<run_id>/manifest.json`.

## 2026-11-15 Entry 1: plan, and the particle files at N = 10^5

Set-up chosen [JUDGEMENT], following the lead's section 4 of `../stage/G1/STATUS.md`
where the code allows it:

- Mesh: that of the first paper's static runs at dx = M/4 (`problems/st/st_migration.athinput`,
  domain [-512, 512]^3 M, 64^3 root cells, 16^3 MeshBlocks, one refined region of level 6
  inside |x|, |y|, |z| < 7.9 M). The lead asked for dx = M/4 over the whole cluster; the
  octree does not allow a level-6 region between 8 and 16 M without refining whole
  shells of 448 blocks per level (2:1 balance), about 2900 blocks against 400. The level-6
  cube holds 99.2 percent (threshold model) and 98.8 percent (y0 = 0.314) of the
  particles of the N = 10^4 files of run C-sidm-20261115-120610-b4592be (computed in this
  session from those files: fraction with max(|x|, |y|, |z|) < 8 M); the rest sits in cells
  of M/2. The cost of that mesh is measured: 400 MeshBlocks, 200 M in 654 s on one A100
  (log of the first paper's run `runs/st/dir_yc0500_comp/athena.20261113-062219.log`,
  main checkout), 3.27 s per M.
- Particles: 10^5, regenerated with the equilibria package (lead: "regenerated at
  N = 1e5"), stratified, seed 1.
- Collisions: `coll_cell_factor = 1` (collision cell = mesh cell, M/4 in the core),
  `coll_pmax = 0.1`, `coll_subcycle = measured`, `coll_weights = equal`,
  `coll_budget = true`, `coll_hist_dcycle = 1` (a record holds one cycle only, so every
  cycle must be written to count all collisions), `<job> rng_seed = 1`.
- Kn = lambda_c/H_c (lead's definition, `../stage/G0/REPORT.md` section 2), sigma~ =
  K/Kn with K = 1/(rho0_c H_c) of each model.
- 300 M per run, no perturbation.

Test 1 (particle files). Prediction: `make_equilibria.py` writes both models at
N = 10^5 with every invariant of the N = 10^4 files of run -120610: equal masses M0/N,
zero net momentum to rounding, all Killing energies E <= E0 (largest E/E0 within 1e-3 of
one), sum m W/psi within 3e-4 of M = 1 (2.3e-4 at N = 10^4 for the threshold model, run
-120610 JSON; the stratified sampler should do no worse at 10 times the number). Refuted
if any of these fails.
