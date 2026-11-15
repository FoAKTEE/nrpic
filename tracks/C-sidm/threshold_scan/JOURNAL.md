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

## 2026-11-15 Entry 3: predictions for the six card runs (Test 3), written before submission

Runs: `inputs/cc{1,2}_kn{inf,10,1}.athinput`, release card executable
`.work/build_gpu_v03/src/athena`, 300 M each, three Slurm jobs of two runs
(`inputs/batch_{1,2,3}.list`). Predicted cost: 3.3-4.3 s per M (first paper's 3.27 s per M
on the same mesh at N = 10^4; particle and collision work at N = 10^5 adds little:
4.1e-8 s per particle and cycle from G0, run C-sidm-20261115-115400-eb8b752, gives 20 s per
run; core's operator 1e6 particles x 200 steps in 2-4 s) so 1000-1300 s per run, 0.6-0.75
card-hours per job, about 2 card-hours in all. Analysis: `analyze.py`.

Budgets (G2 criterion "the budgets of conserved quantities close in curved spacetime"):

- P3.1 Rest mass: sum_m bit-identical at every record in all six runs; n_excised =
  n_escaped = 0 (excision needs alpha < 0.1; a particle cannot reach 512 M from r < 13 M in
  300 M). Refuted by any change.
- P3.2 Deposit identity int_E = sum_mW to 1e-12 relative at every record.
- P3.3 Cell-frame pair energy: largest |dE| per collision in any record below 8 eps of the
  pair energy (core's criterion); sum of dP at rounding; n_trunc = 0, n_bad_cells = 0,
  max_P <= 0.12.
- P3.4 Energy at the particles' metric (coll_budget): the summed dE_particles over sum M W
  is positive and equals the predicted defect per collision (1.74e-10 for CC1, 1.26e-10 for
  CC2) times the number of collisions within a factor two (the prediction used the static
  metric and the initial distribution): about 2.0e-5 (CC1, Kn = 10), 2.0e-4 (CC1, Kn = 1),
  1.4e-5 and 1.4e-4 (CC2). Refuted if negative or outside the factor two.
- P3.5 The two histories describe one energy: sum_MW_particles of `cc.coll.hst` and sum_mW
  of `cc.nrpic.hst` at the same cycle agree to 1e-12 relative.

Collision counts:

- P3.6 First collision step: sum_P within the bands of Test 2 (CC1: [24.25, 24.58] and
  [242.5, 245.8]; CC2: 23.692 and 236.92 within 0.63 and 0.5 percent: [23.54, 23.84],
  [235.7, 238.1]).
- P3.7 Over the run: |collisions - sum of sum_P| / sqrt(sum of sum_P) < 4; collisions within
  10 percent of the constant-rate prediction at Kn = 10 (1.172e5, 1.137e5) and within 25
  percent at Kn = 1 (1.172e6, 1.137e6), where the structure changes [JUDGEMENT on both
  tolerances].

Collisionless controls (the first paper's stable cluster, `paper/sections/tables/tab_outcomes.tex`
lines 104-110 and 118-119: half swing of alpha_c growing from 0.005 to 0.018 over
100-500 M, ranges of r10 and r90 of 0.18 and 0.07 over 0-300 M, mean Lorentz factor
changed by 1.5e-3 at most, every particle kept):

- P3.8 cc2_kninf (stable side) and cc1_kninf (threshold): every particle kept;
  |alpha_c - alpha_c,eq| <= 0.02 (cc1_kninf: a slow drift up to 0.03 allowed);
  ranges of r10 <= 0.2 and of r90 <= 0.1 of their initial values; mean Lorentz factor
  changed by <= 2e-3; an oscillation of alpha_c with a period of 20-40 M (core radial
  period pi (3/(4 pi E_c))^(1/2) = 22.0 M and 23.6 M with E_c of the model JSON, the paper's
  formula, which gave 66 M against a measured 75 M for y_c = 0.819). No collapse of the
  threshold model within 300 M [JUDGEMENT: its growth rate is zero by construction; the
  code's collapse times in the first paper were later than the published ones].
- P3.9 Killing energies of the controls: fraction with E_K > E0 at 300 M <= 0.017 (the
  initial fraction within 1 percent of E0; metric oscillations of order 1e-2 at most);
  no particle with E_K > 1; |change of sum M E_K| <= 1e-3 M.

What collisions change within 300 M [JUDGEMENT, from the relaxation estimates above and
equilibria/CONVERSION.md]:

- P3.10 Kn = 10 (2.3 collisions per particle): fraction with E_K > E0 at 300 M in
  [0.04, 0.12] (linear 0.119 and 0.116 is the upper end; collisions also scatter tail
  particles back); unbound fraction (E_K > 1) in [0.003, 0.010]; alpha_c within 0.005 and
  r50 within 2 percent of the control at all snapshot times.
- P3.11 Kn = 1 (23 collisions per particle): fraction with E_K > E0 in [0.1, 0.6] (the
  linear estimate 1.19 saturates); unbound fraction in [0.02, 0.15] (the initial rate gives
  0.10; a relaxed core keeps a Maxwell-Juttner tail above the escape energy); the mass
  beyond 2 rbar_s at 300 M comparable to the unbound fraction; evaporation leaves the
  remainder more bound, so alpha_c at 300 M is below the control's by more than 0.01 (core
  contraction). Refuted if alpha_c ends above the control's mean of the last 50 M. CC1 at
  Kn = 1 does not form a horizon within 300 M (alpha_min > 0.1) [60 percent confidence; a
  collapse would show that collisions drive the threshold model unstable within tens of
  collision times].
- P3.12 Constraint norm: H-norm2 of the collisional runs at 300 M within a factor 1.5 of
  the control's (the energy defect of P3.4 is below the constraint noise).

## 2026-11-15 Entry 4: inputs of the longer threshold scan (prepared, not run)

`make_scan.py ic` regenerates the five King b = 1 models at N = 10^5 and writes, per model,
a coherent radial kick of one percent of each particle's speed, inward and outward (the
first paper's `--vpert`, here with the particle's own speed); `make_scan.py decks` writes
`inputs/scan/`. Test 4 prediction: king_y0p33403 and king_y0p31400 are byte-identical to
the files of run C-20261115-165832-fccee3a (same code, seed and thread count); for every
kicked file the mean radial three-velocity is about -+0.01 times the mean speed (0.0045 in
magnitude to within 30 percent, mean speed about 0.45 from CONVERSION.md), sum W changes by
less than 1e-4 relative (second order in the kick), and the fraction of particles pushed
above E0 lies in [0.002, 0.012] (about half of the 1.7 percent within 1e-2 of E0 move up
by a first-order change of E of up to 1e-2 E0). Refuted if any of these fails.

Outcome of Test 4 (run C-20261115-174556-3544e2c): partly FAILED, as follows.
- PASS: king_y0p33403 and king_y0p31400 (.nrp, .tab, .json) are byte-identical to those of
  run C-20261115-165832-fccee3a; sum W changes by 4.6e-6 to 1.0e-5 (below 1e-4); net
  momentum below 4e-17.
- Mean radial three-velocity: -0.00357 to -0.00374 (inward kick) and +0.00313 to +0.00328
  (outward) over the five models. Nine of ten inside the predicted band [0.00315, 0.00585];
  y0 = 0.314 outward (0.003127) is 0.7 percent below its lower edge. My band was centred
  on the central mean speed of CONVERSION.md (0.45-0.50); the particle-averaged speed is
  lower, about 0.34 (= the measured magnitude / 0.01). The difference between the two
  signs, -2.2e-4 in the mean, is the sample's own mean radial velocity.
- FAILED: fraction pushed above E0 is 1.1e-4 to 1.2e-4, not in [0.002, 0.012]. The kick
  changes E by about 0.01 alpha q^2/W, i.e. 1e-3 of E0 (largest E/E0 after the kick
  1.0014-1.0024), not 1e-2 as I assumed; half of the 2.6e-4 within 1e-3 of E0 (Entry 2)
  is 1.3e-4, which matches.
Decks of `inputs/scan/` (12) written from this run by `make_scan.py decks`.

Outcome of Test 2 (run C-20261115-172003-6422b6a; figure run C-20261115-175503-7c431e2,
`figs/fig_smoke_sumP.png`, looked at): PASS. All three decks start, read 10^5 particles and
keep sum_m bit-identical for four cycles; cc1_kninf writes no collision history (its only
warning is the unused `<job> rng_seed`, as expected without the operator). First collision
step: sum_P = 24.4163 (Kn = 10) and 244.1674 (Kn = 1) against 24.4120 and 244.1204
predicted (+0.017 and +0.019 percent, 0.09 sd of the pairing spread). Collision cells with
two or more particles 17994 (predicted 17960 at t = 0), particles per occupied cell 2.332
(2.33); one sub-step everywhere, largest pair probability 0.047 (Kn = 1); n_trunc = 0,
n_bad_cells = 0; cell-frame pair energy defect at most 4e-19 per record. Collisions in four
cycles 117 and 1020 against sum_P totals 97.8 and 978.1 (z = 1.94, 1.34; the two runs use
the same keys, so the counts are correlated). Cost on 4 processor threads: about 140 s per
cycle, so processors cannot run these decks (4800 cycles); the cards are needed.
The defect dE_particles over four cycles (8.0e-8 M in 1020 collisions at Kn = 1, i.e.
7.9e-11 M per collision against the predicted 2.0e-10 M) cannot test P3.4 yet: one
collision changes the sum by about 4e-9 M either way, so 1020 collisions give a standard
error of about 1.2e-10 M per collision.

## 2026-11-15 Entry 5: cell-size dependence of the energy defect (Test 5, prediction)

`predict_cells.py` repeats the defect estimate of predict.py for uniform collision cells of
M/8, M/4, M/2 and M over the CC1 particles. Prediction: the defect per collision scales as
h^2 (each ratio between successive sizes within 30 percent of 4), as the reading of Entry 2
(partners at potential depths that differ by order h) and core's measured ratios 0.22 and
0.10 for 2 to 1 M and 2 to 0.5 M in the y_c = 0.819 cluster suggest; the value at M/4 equals
that of predict.py (1.74e-10) within its noise. Refuted if a ratio lies outside [2.8, 5.2].

Outcome of Test 5 (run C-20261115-175636-b7b5252, `fig_pred_cellsize.png` looked at):
PASS. Defect per collision over sum M W: 4.8e-11 (M/8, standard error 1.3e-11), 1.74e-10
(M/4, as predict.py), 6.5e-10 (M/2), 2.5e-9 (M); successive ratios 3.6, 3.7, 3.9, so second
order in the cell side. Killing-energy change per collision 6.6e-11, 2.4e-10, 8.9e-10,
3.4e-9 M. Occupation: mean of occupied cells 1.2, 2.3, 6.7, 27; cells within r < M hold
2.3, 16, 129, 922. So the choice between relaxation fidelity (core: about 100 per cell)
and the energy defect is sharp in this model at N = 10^5: about 100 per cell in the core
needs M/2 cells (coll_cell_factor = 2 on the M/4 mesh), where the defect is 6.5e-10 per
collision, 7.6e-4 of sum M W over 300 M at Kn = 1 and about 8e-3 at Kn = 0.1 (at the
initial rate). The x-axis labels of the first version of the figure overlapped; the script
now labels the four sizes; the rerun C-20261115-175709-e5d0e07 gives a byte-identical
cells.json and the figure in `figs/`.

## 2026-11-15 Entry 6: outcome of Test 3, the six card runs

Runs: card jobs C-20261115-171058-c26cfad (cc1_kninf, cc1_kn1), C-20261115-171059-4b70228
(cc1_kn10, cc2_kninf), C-20261115-171059-35441e3 (cc2_kn10, cc2_kn1); analysis run
C-20261115-191420-8538aa4 (`summary.json`; figures `fig_cc_lapse_radii`, `fig_cc_controls`,
`fig_cc_collisions`, `fig_cc_budget`, `fig_cc_energy_tail`, all looked at, copies in
`figs/`). All six exit with status 0 in 1026-1037 s, 3.42-3.46 s per M (predicted 3.3-4.3);
1.73 card-hours in all (`nrpic-run budget`, G2).

Headline [the runs; reading JUDGEMENT]: both collisionless controls stay bound, while
all four collisional runs collapse within 300 M. Time at which the smallest lapse on the
mesh falls below 0.3, and first excision (alpha < 0.1):

| Run | alpha_min < 0.3 | first excision | collisions per particle before | rest mass excised 20 M / 50 M after first excision |
|---|---|---|---|---|
| cc1_kn1 | 72.5 M | 83.3 M | 13.4 | 0.82 / 0.90 |
| cc1_kn10 | 184.3 M | 193.8 M | 2.5 | 0.91 / 0.95 |
| cc2_kn1 | 77.8 M | 88.8 M | 15.3 | 0.82 / 0.89 |
| cc2_kn10 | 206.8 M | 216.5 M | 2.9 | 0.90 / 0.95 |

Before the collapse the inner shells contract (r10 down to about 0.2-0.3 of its initial
value) while r90 first grows by up to 20 percent at Kn = 1 (core-halo separation), and the
collision rate per step rises 9-14 times. A factor ten in the cross-section shortens the
collapse time by 2.5-2.7, not by ten. On the static M/4 mesh the evolution after the
collapse is not trustworthy: the constraint norm rises to 10-1900 and the state turns
non-finite at 204 M (cc1_kn1), 162 M (cc2_kn1) and 290 M (cc1_kn10); the code removes every
remaining particle and still exits with status 0 (core's G2 OPEN item 11). The excised
fractions above are therefore proxies of the collapsed mass, not horizon masses.

Predictions, one by one:

- P3.1 Rest mass: PASS where it applies. sum_m is bit-identical in every record before the
  first excision in all six runs; with excision, sum_m + m_excised + m_escaped equals the
  initial rest mass to at most 7.3e-15 relative; n_escaped = 0. The part "n_excised = 0"
  FAILED in the four collisional runs (they collapsed).
- P3.2 Deposit identity: PASS, at most 3.0e-15 (records with particles).
- P3.3 Cell-frame pair energy: PASS. Largest |dE| per collision in a record 4.4 times
  2 M_p eps (below 8); summed dP below 1.8e-18; n_trunc = 0; no unusable cell; largest pair
  probability 0.098 (Kn = 1, up to five sub-steps during the collapse).
- P3.4 Energy at the particles' metric: FAILED over the run, PASS in the early window.
  Before the collapse the defect per collision grows with the depth of the potential: summed
  to alpha_min < 0.3 it is 1.6e-3 (cc1_kn1), 1.7e-3 (cc2_kn1), 1.8e-4 and 2.2e-4 (Kn = 10)
  of sum M W, i.e. 1.4-2.3e-9 per collision, 8-18 times the initial-state value; with the
  collapse phase it reaches 2.2e-2 (Kn = 1) and 3.0e-3 (Kn = 10). In the first 25 M (collision
  counts 0.99-1.03 of the prediction, structure still near the initial one) the defect per
  collision is 1.22(22)e-10 (cc1_kn1; predicted 1.74e-10, 2.4 standard errors low),
  1.24(20)e-10 (cc2_kn1; predicted 1.26e-10), 0.88(60)e-10 (cc1_kn10), 0.22(51)e-10
  (cc2_kn10); the scatter of one collision is 5-7e-9 of sum M W, so the Kn = 10 values are
  noise-limited. Positive in sign and of the predicted size within a factor two at Kn = 1.
- P3.5 Histories: PASS, sum_MW_particles of `cc.coll.hst` equals sum_mW of `cc.nrpic.hst` at
  the same cycle to 3.9e-16.
- P3.6 First collision step: PASS. sum_P = 24.41630 and 244.16742 (CC1), 23.69597 and
  236.94446 (CC2) against 24.41204, 244.12038, 23.69207, 236.92071 (+0.010 to +0.019
  percent, at most 0.08 sd of the pairing). The CC1 card values equal the processor smoke
  values of Test 2 to 1e-15.
- P3.7 Counts: PASS for Poisson (|z| <= 2.4 at the end, largest excursion about 3, in
  cc2_kn10 near 210 M); collisions in the first 25 M are 0.99-1.03 of the constant-rate
  prediction. The 10 and 25 percent bands over the run FAILED: the contraction raises the
  rate (before the collapse 1.7-1.8 times the constant rate at Kn = 10 and 2.4-2.6 at Kn = 1).
- P3.8 Controls: partly FAILED. Every particle kept, no collapse (PASS). cc2_kninf:
  |alpha_c - alpha_c(0)| at most 0.0185 (PASS, <= 0.02), r10 and r90 ranges 0.081 and 0.059
  (PASS), mean Lorentz factor changed by 7.2e-3 (FAIL, > 2e-3). cc1_kninf: alpha_c rises by
  up to 0.0334 (FAIL, > 0.03), r10 range 0.136 (PASS), r90 range 0.106 (FAIL by 6 percent),
  mean Lorentz factor 0.0134 (FAIL). The predicted 20-40 M oscillation is present only as a
  ripple of about 1e-3; the dominant motion, not predicted, is a slow outward excursion of
  both controls: alpha_c rises until about 200 M and falls again by 300 M (`fig_cc_controls`),
  twice as large for the threshold model as for y0 = 0.314. The first paper's stable
  cluster had instead a growing core oscillation and a slow fall of the mean lapse.
- P3.9 Killing energies of the controls: fraction above E0 at 300 M 2.4e-3 (CC1) and
  8.2e-4 (CC2), no unbound particle (PASS); |change of sum M E_K| 0.0070 and 0.0017 M at
  300 M, up to 0.014 M at 200 M (FAIL, > 1e-3 M): E_K is not conserved while the metric
  follows the excursion, so this sum is no budget in an evolving spacetime.
- P3.10 Kn = 10: tail and evaporation PASS (fraction with E_K > E0: 0.055 at 175 M for CC1,
  0.061 at 200 M for CC2, in [0.04, 0.12]; unbound 0.0072 and 0.0086, in [0.003, 0.010];
  the unbound fraction follows the linear prediction of Entry 2 to about 175 M,
  `fig_cc_energy_tail`); structure FAILED (collapse instead of alpha_c within 0.005 of the
  control).
- P3.11 Kn = 1: unbound fraction at the last record before the collapse 0.017 (CC1, 50 M)
  and 0.024 (CC2, 75 M), at and above the lower edge of [0.02, 0.15]; fraction above E0
  0.081 and 0.105 (the band was for 300 M; the runs collapsed before); alpha_c below the
  control by far more than 0.01 (PASS); "no horizon within 300 M" FAILED (collapse at
  72.5 M and 77.8 M).
- P3.12 Constraint norm before the collapse: PASS (H-norm2 at 50 M: 1.40e-3 and 1.24e-3 at
  Kn = 1 against 1.03e-3 and 1.04e-3 for the controls; at 150 M: 8.0e-4 at Kn = 10 against
  8.4e-4).

Reading [JUDGEMENT, not tested by a control run]: (1) The energy defect is positive
(heating) and cannot by itself drive a contraction; whether it changes the collapse times
needs the pair-energy correction (request to core). (2) Both King models lie far beyond the
first mass maximum of their sequence (y0 = 0.0982, equilibria README), the turning point at
which a thermally relaxed (collisional) cluster loses stability [BACKGROUND, Katz-type
turning-point argument, not checked here]; collisions therefore find both of them unstable,
and the collisionless threshold y0 = 0.334 is not the relevant one once Kn is finite. A
collisional threshold would be bracketed by a collisional run of a less compact King model.
(3) The controls' outward excursion is the open question for the collisionless threshold
(G2): its size grows towards the threshold (0.018 at y0 = 0.314, 0.033 at 0.334); a cloud-
width softening of the M/4 deposit (the paper's "compensation that also cancels the cloud
width" changed alpha_c by 3.6e-3, `tab_outcomes.tex` line 108) is one candidate; the mesh
leg of SCAN.md block B tests it.
