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

Outcome of Test 1 (run C-20261115-165832-fccee3a, 16 s per model): PASS. Both files have
10^5 equal masses M0/N (threshold model M0 = 1.0369019, stable 1.0367944), net momentum
below 4e-17, largest E/E0 = 0.99993 for both, sum m W/psi - 1 = -3.7e-5 (threshold) and
-3.5e-5 (stable), particles out to isotropic r = 12.19 M and 12.53 M. K = 1/(rho0_c H_c) =
168.895 (threshold, as the lead's 168.9) and 186.081 (y0 = 0.314), so sigma~ = 16.8895,
168.895 (CC1) and 18.6081, 186.081 (CC2) for Kn = 10, 1 (`common.kn_constant` from the
model JSON: n_c, p_c, p_T,c).

## 2026-11-15 Entry 2: predictions from the particle files (run C-20261115-170404-af74c6d)

`predict.py` reads only the particle files and the static metric: for every leaf cell of the
static mesh and every pair in it, the expected collisions per step of the operator
(coord/INTERFACES/collisions.md eq. 1), an isotropic scattering in 16 directions per pair,
and 100 draws of the operator's random pairing. Figures `fig_pred_cells.png`,
`fig_pred_energies.png` of the run directory (looked at; copies in `figs/`).

| Quantity (N = 10^5, dt = M/16) | CC1 (threshold) | CC2 (y0 = 0.314) |
|---|---|---|
| occupied cells; with >= 2 particles; largest occupation; mean occupation | 42878; 17960; 32; 2.33 | 45534; 18510; 28; 2.20 |
| particles in the M/4 cube | 0.992 | 0.989 |
| expected sum_P of step 1, Kn = 10 (sd over pairings) | 24.412 (0.054) | 23.692 (0.050) |
| expected sum_P of step 1, Kn = 1 | 244.12 (0.54) | 236.92 (0.50) |
| collisions in 300 M at the initial rate, Kn = 10; Kn = 1 | 1.172e5; 1.172e6 | 1.137e5; 1.137e6 |
| the same from equilibria/CONVERSION.md (nu_bar of run C-sidm-20261115-122915-cdc395c) | 1.172e5 (0.06 % apart) | 1.141e5 (0.3 % apart) |
| collisions per particle in 300 M, Kn = 10; 1 | 2.34; 23.4 | 2.27; 22.7 |
| change of sum M W (W at the particle's metric) per collision, over sum M W | +1.74e-10 | +1.26e-10 |
| change of the Killing energy sum M alpha W per collision | +2.40e-10 M | +1.74e-10 M |
| collisions putting a particle above E0; above E = 1 (unbound) | 0.102; 0.0085 | 0.102; 0.0080 |
| initial particles with E > E0 (1 - d) for d = 1e-3, 1e-2, 3e-2 | 2.6e-4, 0.017, 0.116 | 2.8e-4, 0.019, 0.126 |

Two independent estimates of the collision count (the particle pairs in the cells of the
actual mesh; the model's continuous profiles with the Moller average) agree to 0.3 percent,
and the mean of the sampled pairings equals the all-pair expectation (z = 0.2, 0.1): the
pair sum is the number to test the code against. The energy defect per collision is
positive in the M/4 cells (about +2e-5 in W_a + W_b per collision at r < 4 M; the M/2
cells beyond 8 M are noisy and carry few collisions).

Relaxation estimates [JUDGEMENT on the reading]: the King b = 1 model at this
compactness is far from Maxwell-Juttner (f = e^{1 - E/E0} - 1 is nearly linear in E0 - E,
since E/E0 > 0.72 for every particle, `fig_pred_energies.png`), so every collision changes
the energy distribution: one in ten puts a particle above the cut-off E0 (a bound halo
beyond the model radius), one in 120 makes a particle unbound (E > 1). At Kn = 10 the
average particle collides about twice in 300 M (about nine times at the centre, nu_c of
CONVERSION.md); at Kn = 1 about 23 times (about 90 at the centre), so the core relaxes
within the first tens of M.

Test 2 (processor smoke of the decks, before any card time). Prediction: with the release
processor executable, cc1_kninf, cc1_kn10 and cc1_kn1 start, read 10^5 particles and keep
the rest mass bit-identical for 4 cycles; cc1_kninf writes no collision history; the first
collision step has sum_P = 24.412 (Kn = 10) and 244.12 (Kn = 1) within
max(3 sd of the pairing, 0.5 percent): [24.25, 24.58] and [242.5, 245.8]; no truncated
probability, no unusable cell. Refuted by any failure; a sum_P outside the band would mean
the cell geometry, the volume or the lapse factor of the code differs from my reading of
the interface.
