# C-sidm/equilibria: initial data near the instability threshold (C-pre-4)

Relativistic cluster equilibria close to the collisionless instability threshold of the
families of gr-qc/0601112 and 2009.08163, sampled as particle files for AthenaK's
`nrpic_cf` problem generator, each checked against the papers' printed values. The
directory also holds the conversion between Knudsen number and cross-section per unit mass
(`CONVERSION.md`). Predictions and outcomes of every test are in `JOURNAL.md`.

## What is here

| File | Content |
|---|---|
| `evstatic.py` | Static spherically symmetric Einstein-Vlasov solver for `f = Phi(E) (L - L0)^l_+`, Phi the polytrope `(1 - E/E0)^k_+` or the King model `exp(1 - E/E0) - 1` (2009.08163 lines 631, 635; gr-qc/0601112 line 633 for k = 0). Moments by Gauss-Jacobi quadrature, structure ODE in areal radius, isotropic map, `Equilibrium` (profiles in units of the ADM mass), radial `.tab` writer, six-coordinate stratified sampler (exact conditional inverse CDFs, anisotropic shells included), Lane-Emden reference |
| `paper_values.py` | The printed numbers checked against, with file:line locators |
| `models.py` | The 13 near-threshold models (table below) |
| `make_equilibria.py` | Writes `.nrp`, `.tab`, `.json` per model (formats of `docs/FORMATS.md`, conventions of `problems/ic/make_ic.py`) |
| `check_equilibria.py` | Offline checks (Tests 1-2 of `JOURNAL.md`): paper values, Newtonian limit, mass-radius turning point, matching, TOV, Hamiltonian constraint, sampler, moments, invariants, file round trip |
| `knudsen.py` | Knudsen number against `sigma/m` with the relativistic (Moller) rate; collisions per particle per dynamical time; resolution at N = 10^4 |
| `figures.py`, `fig_knudsen.py` | Figures (style `python/nrpic/figstyle.py`) |
| `smoke_athenak.py`, `fig_smoke.py` | Test 4: AthenaK's processor build reads a new table and particle file (two cycles against the paper's y_c = 0.819 model) |
| `runreg.py` | Registers a processor run: `tracks/C-sidm/runs/<run_id>/manifest.json`, output in `scratch/C-sidm/<run_id>/` |
| `results/` | `checks.json` (run C-sidm-20261115-121626-e99907d), `models_index.json` (run C-sidm-20261115-120610-b4592be), `knudsen.json` (run C-sidm-20261115-122915-cdc395c), `athenak_smoke.json` (run C-sidm-20261115-125308-54870b9) |
| `figs/` | `binding_energy`, `king_mass_radius`, `profiles_threshold`, `constraint_residual`, `sampling_threshold`, `shell_angular_momentum`, `knudsen_conversion`, `knudsen_profiles`, `athenak_smoke` (PDF and PNG); drawn by run C-sidm-20261115-130010-69e27db from the registered outputs (PNG byte-identical to these) |

## The models (ADM mass M = 1; 10^4 particles each, stratified, seed 1)

Particle files, tables and JSON are in `scratch/C-sidm/C-sidm-20261115-120610-b4592be/`
(not committed; regenerate as below). Stem: `<tag>_stratified_N10000_s1`.

| tag | family | y0 | role | E_b | Z_c = 1/alpha_c - 1 | R/M | rbar_s/M |
|---|---|---|---|---|---|---|---|
| king_y0p31400 | King | 0.314 | stable (2009.08163 l.1146) | 0.035489 | 0.47880 | 13.974 | 12.955 |
| king_y0p32400 | King | 0.324 | stable (l.1146) | 0.035564 | 0.49529 | 13.794 | 12.775 |
| king_y0p33403 | King | 0.334032 | threshold, computed y_max | 0.035589 | 0.51191 | 13.630 | 12.610 |
| king_y0p34400 | King | 0.344 | unstable (l.1146) | 0.035564 | 0.52851 | 13.481 | 12.461 |
| king_y0p35400 | King | 0.354 | unstable (l.1146) | 0.035492 | 0.54524 | 13.346 | 12.325 |
| poly05_y0p27766 | k = 1/2 | y_max - 0.02 | stable side | 0.035590 | 0.46083 | 10.901 | 9.876 |
| poly05_y0p28766 | k = 1/2 | y_max - 0.01 | stable side | 0.035684 | 0.47852 | 10.708 | 9.682 |
| poly05_y0p29766 | k = 1/2 | 0.297664 | threshold, computed y_max | 0.035715 | 0.49628 | 10.530 | 9.504 |
| poly05_y0p30766 | k = 1/2 | y_max + 0.01 | unstable side | 0.035684 | 0.51412 | 10.367 | 9.340 |
| poly05_y0p31766 | k = 1/2 | y_max + 0.02 | unstable side | 0.035593 | 0.53203 | 10.216 | 9.189 |
| arshell_y0p13320 | shell, L0 = 0.1 | 0.133196 | stable (gr-qc/0601112 Table 1, Z_c = 0.39) | 0.041280 | 0.39000 | 5.088 | 4.026 |
| arshell_y0p13545 | shell, L0 = 0.1 | 0.135452 | threshold, computed E_b maximum | 0.041288 | 0.39626 | 5.038 | 3.975 |
| arshell_y0p14768 | shell, L0 = 0.1 | 0.147675 | unstable for A > 1 (Table 1, Z_c = 0.43) | 0.041042 | 0.43000 | 4.791 | 3.724 |

y0 = ln E0 - mu at the centre (inner edge for the shell) as in 2009.08163 (line 661); for
the King and polytrope rows the threshold is the first E_b maximum, which 2009.08163 finds
to be the onset of instability (lines 1083-1092). The shell is anisotropic (f depends on L
through the cut-off L >= L0), with an inner vacuum (rbar < 2.27 M at the threshold).

Each `.json` carries the model summary, the `<problem>` and `<particles>` settings of
AthenaK (`pgen_name = nrpic_cf`, `comp0_type = table`, `lapse = table`, as
`problems/st/st_cluster.athinput`), the removed net momentum, the particle invariants
(max E/E0, min L) and the particle form of the constraint, sum m W/psi = M.

## Checks (all pass; run C-sidm-20261115-121626-e99907d)

- 2009.08163 Table (lines 948-960): y_max, y_zero of the King model and three polytropes
  within 1e-3 (King 0.33403 / 0.78452 vs 0.334 / 0.784; k = 0.5: 0.29766 / 0.69303 vs
  0.298 / 0.693; seven of eight within half a printed unit).
- gr-qc/0601112 Tables 1, 2, 4 (k = 0): 27 of 29 (Z_c, E_b) rows inside the range allowed by
  the printed rounding; the two misses by 7e-5 and 1.9e-4. Z_c is the standard 1/alpha(0) - 1
  (the square root printed on its line 694 does not reproduce the tables).
- Newtonian limit: rho_c/rho_mean of the k = 0.5, 1, 1.5 polytropes at y0 = 1e-3 within
  1 percent of Lane-Emden n = 2, 2.5, 3.
- King mass-radius curve: first M maximum (y0 = 0.0982) before the E_b maximum, as stated in
  2009.08163 lines 1160-1167.
- Per model: matching to isotropic Schwarzschild to round-off; anisotropic TOV residual
  < 1e-6; Hamiltonian constraint of the written table < 1e-6 of the largest source away
  from the matter edges (1e-8 typical); rest mass by the isotropic integral to 1e-11;
  stratified radial and polar ECDF within 1/N, equal-mass shell counts exact; shell moments
  (n, rho, p_r, p_t) within 4.5 standard errors for both samplers; KS tests of radii and
  Killing energies for plain Monte Carlo; every particle E <= E0 and L >= L0; file round trip.
- AthenaK (run C-sidm-20261115-125308-54870b9, processor build of main): `nrpic_cf` reads
  the King threshold files; np, sum m and the deposited energy agree with the file to
  round-off; the initial Hamiltonian-constraint norm equals that of the paper's
  y_c = 0.819 model on the same mesh (ratio 0.93 of the squared integrals).

## How to rerun

From this directory (processors, 4 threads, a few minutes each):

    python3 runreg.py --purpose "..." -- python3 make_equilibria.py --out {out} --N 10000 --seed 1
    python3 runreg.py --purpose "..." -- python3 check_equilibria.py --ic <build run dir> --out {out}
    python3 runreg.py --purpose "..." -- python3 knudsen.py --out {out} --N 10000
    python3 figures.py --checks <check run dir> --out figs
    python3 fig_knudsen.py --run <knudsen run dir> --out figs
    python3 runreg.py --purpose "..." -- python3 smoke_athenak.py --ic <build run dir> --stem <stem> --out {out}
    python3 fig_smoke.py --run <smoke run dir> --out figs

Another particle number or seed: `make_equilibria.py --N ... --seed ... [--sampler mc]`;
a single family: `--only king` (or a tag).

## Not done here

- No AthenaK evolution of these models beyond the two-cycle read test (the collisionless
  threshold with three-way convergence is Track C's work that depends on core, G2).
- gr-qc/0601112 Case 3 (k = 1): its ansatz (E0 - E)^1 depends on the normalisation of E0
  (lines 670-674) and is not reproduced.
- Perturbed models (the papers perturb by A f_s, gr-qc/0601112 line 677, or by a
  dynamically accessible kick, 2009.08163 lines 846-853): not generated; the existing
  `PerturbedST` construction of `python/nrpic/st_cluster.py` is monoenergetic-specific.

## Requests

- core: a problem-generator option, or a documented recipe, for the dynamically accessible
  perturbation of 2009.08163 (eq. perturb, lines 846-866: an extra radial force gamma x/r
  during [0, T_pert]); it keeps the Casimirs and needs no new initial-data solve, so it is
  the cleanest way to push these equilibria across the threshold in AthenaK.
- core (for the collision module, C-pre-1): see CONVERSION.md, section "Resolution at
  N = 10^4": below Kn ~ 0.3 the mean free path is shorter than the central inter-particle
  spacing at 10^4 particles.
- C-sidm lead: choose the family for S3 (the King model is the truncated Maxwellian and the
  natural stand-in for a gravothermal core [JUDGEMENT]); the threshold models are ready.
