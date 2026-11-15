# JOURNAL of the work package secondary_infall (D-pre-3)

Append-only, newest at the bottom. Predictions are written before a run, outcomes after.
Units G = c = 1, M = initial mass of the seed (the black hole), eps = H_i M, t_i = 2/(3 eps)
(Einstein-de Sitter). Locators `file:line` of a paper are relative to
`kb-data/raw/arxiv/<id>/v2/src/`.

## 2026-11-15T12:20Z  helper secondary_infall  predictions before any run

did: read CLAUDE.md, the charter to "Owners", decision 0010, the brief ranges 30-68,
232-238, 279-313, 394-405, 766-783, 834-860; the scoping package (`../scope/`, run
D-bh-dress-20261115-120304-795eee9); the Newtonian-mode interface on `core/newton`
(`tracks/core/interfaces/newtonian_mode.md`) and the format-2 initial data on
`core/id-extrinsic`. Fetched 1901.08528 v2 and 2106.07480 v2 and read them at the
source (the parts on turnaround, the profile and the matter era; locators below). Read
1805.09034 `main.tex:186-218` (dress mass law used for the merger rate).

What the two papers print that this package can check [VERIFIED, read at the source]:
- 1901.08528 is about the radiation era: r_ta = (2 G M t_ta^2)^(1/3), "better than
  0.1 %" (`PBH-UCMH-ArXiv-v2.tex:166-169`); the analytic estimate (4 G M t^2)^(1/3)
  (`:163`); the ratios of the two estimates to the true turnaround radius are 0.964 and
  0.999 (`:497`); radial orbits after turnaround raise the frozen-in r^(-9/4) density by
  53 % (`:468`); its N-body slopes 2.28 and 2.35 (`:346`, `:354`).
- 2106.07480, radiation era: r_infl^3 = eta_ta r_S c^2 t^2, eta_ta = 1.086
  (`sections/cosmo_setup.tex:63-68`, `sections/appendix.tex:123-133`); the four
  trajectories of its Table 1 (`sections/appendix.tex:85-97`), e.g. y0 = 0.1,
  tau0 = 1e-3: y_ta = 10.142, tau_ta = 31.00; in the matter era secondary infall gives
  r^(-9/4) (Bertschinger 1985; `sections/numerical_results.tex:71`,
  `sections/cosmo_setup.tex:108`); with absorption by the hole Bertschinger finds 3/2
  where the hole dominates (`sections/numerical_results.tex:73`).
- 1805.09034 uses rho ~ r^(-3/2) (`main.tex:196-200`), truncation radius ~ (1+z)^(-1)
  (`:208`) and M_halo = (R_tr/R_eq)^(3/2) M_PBH (`:216-218`), i.e. M_halo ~ a^(3/2).
Neither of the two named papers treats the matter era with numbers; the matter-era
self-similar solution (Bertschinger 1985, not on arXiv) is computed here [BACKGROUND for
its published values, which are not read at a source].

### Test 1: the radiation-era turnaround and the radial-orbit factor (prediction)
Script `rd_checks.py`: r'' = -M/r^2 - r/(4 t^2) in the reduced variables of both papers
(y = r/(2M), tau = t/(2M)), DOP853 at rtol 1e-12, turnaround at y' = 0.
1a. The four rows of 2106.07480 Table 1 are reproduced to the printed digits (|dy_ta| <=
    0.001, |dtau_ta| <= 0.01, y_ta^3/tau_ta^2 to 2e-5). Refuted by a larger difference.
1b. Started deep in the expansion-dominated regime (y0^3/(2 tau0^2) -> infinity) the
    ratio y_ta^3/tau_ta^2 tends to a constant eta_inf in [1.085, 1.090] (the paper's
    1.086). Refuted outside.
1c. The ratios of 1901.08528 `:497` cannot both hold: for any eta the two estimates
    differ by the factor 2^(1/3) = 1.26 while the printed ratios 0.964 and 0.999 differ by
    1.036. With eta_inf ~ 1.086 I expect (2 t^2)^(1/3)/y_ta = eta^(-1/3) = 0.973 and
    (4 t^2)^(1/3)/y_ta = 1.226. Refuted if some start reproduces both printed numbers.
1d. The radial-orbit factor of 1901.08528 appendix A is (2/pi) B(1/2, n - 3/2) for a
    frozen-in profile r^(-n) in the hole's Kepler potential (my derivation), 1.5255 for
    n = 9/4 ("53 %"); quadrature and a Monte-Carlo sample of orbit phases agree with it
    to 2e-3. Refuted if any differs from 1.53 by more than 0.01.

### Test 2: the matter-era self-similar solution (prediction)
Script `selfsimilar.py`: Bertschinger's collisionless self-similar infall for a point-mass
(delta) seed, radial orbits through the centre, mass profile M(r,t) = M_ta(t) m(r/r_ta),
r_ta ~ t^(8/9), M_ta ~ t^(2/3), G M_ta t^2 / r_ta^3 = pi^2/8 (cycloid); fixed-point
iteration on m(lambda), orbits integrated to tau = t/t_ta = 300 and continued as
stationary beyond.
2a. Converged inner slope d ln m / d ln lambda = 3/4 +- 0.02 on lambda in [3e-3, 3e-2]
    (rho ~ r^(-9/4) +- 0.02). Refuted otherwise.
2b. The outermost caustic (first apocentre after turnaround) at lambda_1 in [0.30, 0.45]
    (my recollection of Bertschinger: 0.364, [BACKGROUND], not read at a source).
2c. Inner normalisation: rho / rho_frozen in [3, 6], with rho_frozen(r) the background
    density at the turnaround time of the shell now at r (rho_frozen/rho_b(t) =
    lambda^(-9/4)). Refuted outside.
2d. Mass inside the outermost caustic m(lambda_1) in [0.55, 0.85].

### Test 3: the time-dependent shell calculation from the runs' initial data (prediction)
Script `shells.py`: N cold spherical dust shells around the seed, unperturbed Hubble flow
at t_i (the set-up of the scoping run), Plummer softening s of all forces, leapfrog with a
global step from the smallest dynamical time; shells pass through the centre (signed
radius) or are absorbed by the hole. By Birkhoff only the shells that turn around before
t_end matter.
3a. Before any crossing every shell turns around at the closed-form time of the scoping
    run to 3e-4 (relative). Refuted by a larger error (integrator or set-up).
3b. M_ta / M - 1 = c(a) a/a_i with c(2) = 0.2627 and c(10) = 0.4997 (scoping run, table
    `scoping_table.txt`) to 0.5 %.
3c. Absorbing, radial: the hole mass is M + mu(t), mu the dust mass whose closed-form
    Kepler collapse time is < t (exact while no shell crosses another before absorption),
    to 0.5 %; asymptotically (M_bh - M)/M -> 0.5648 * 2^(-2/3) a/a_i = 0.356 a/a_i; the
    infall stream gives rho ~ r^(-3/2) where the hole dominates.
3d. Passing through, eps = 0.1, s = 5 M, to a/a_i = 100: in self-similar units the
    profile on lambda in [0.03, 0.3] is within 20 % (bin averages) of Test 2, slope
    -2.25 +- 0.1 between lambda = 0.02 and 0.2, outermost caustic within 5 % of Test 2.
3e. Dress mass (dust that has passed the centre at least once) for the run set-up:
    in [0.08, 0.3] M at a/a_i = 2 and [0.4, 1.0] M at a/a_i = 4, the same for every eps
    in these units (Newtonian scaling r ~ eps^(-2/3), t ~ eps^(-1)).
3f. With a tangential velocity dispersion sigma_i at t_i and capture of every particle
    with L < 4M (1305.2619 `SFWpaper.tex:120`, via `../scope/REFERENCES.md`) when it
    reaches r < 4M: for eps = 0.01, sigma_i = 0.02 captures > 90 % of the collapsed mass
    by a/a_i = 4, sigma_i = 0.1 between 30 and 80 %.

## 2026-11-15T12:22Z  outcome of Test 1, runs D-bh-dress-20261115-121837-987643b (failed),
## D-bh-dress-20261115-121936-5c715b5, D-bh-dress-20261115-122051-bf0d6b1

Run 121837 failed on a mathtext label (no numbers used). Run 121936 had a biased
Monte-Carlo comparison (bin average against the value at the bin centre: -0.84 % for
r^(-9/4) and these bins); run 122051 repeats with bin averages and a second integrator.
Numbers below are from run 122051 (`rd_checks.txt`); figures `figs/rd_checks.png`,
`figs/rd_boost_mc.png` looked at (trajectories leave the Hubble flow and the printed apices
sit on mine; eta(S) rises from 0.996 at S = 10 to a plateau; MC bins scatter about the
bin-averaged quadrature).
1a. Partly refuted at the stated tolerance. y_ta^3/tau_ta^2 agrees with the printed column
    to 1.3e-5 in all four rows (e.g. row B 1.085559 against 1.08557). The apices
    themselves are 1.4e-4 to 4.0e-4 (relative) further out than printed: y_ta = 8.3064,
    10.1434, 12.2733, 14.7259 against 8.305, 10.142, 12.27, 14.72; tau_ta = 22.981,
    31.006, 41.262, 54.223 against 22.98, 31.00, 41.25, 54.21. DOP853 (rtol 1e-12) and
    Radau (rtol 1e-11) agree to 1e-6, so the difference is in the printed integration,
    whose accuracy the paper itself calls sub-percent (`sections/appendix.tex:119`).
    Consequence: none for this package (eta is what is used).
1b. Holds: eta_inf = 1.087885 (start S = y0^3/(2 tau0^2) -> 1e8); the printed 1.086 is the
    value at the paper's start S ~ 500 (1.08556), 0.17 % below the limit. The approach is
    slow (eta = 1.0767 at S = 100, 1.0868 at 1e3, 1.08777 at 1e4).
1c. Holds, and one printed number is explained: no start reproduces both ratios of
    1901.08528 `:497`. (4 G M t_ta^2)^(1/3)/r_ta = 1.2250 and (2 G M t_ta^2)^(1/3)/r_ta =
    0.97231 in the limit. The printed 0.964 is reproduced by the radius at which the two
    accelerations balance along the path, divided by the turnaround radius: 0.96440 at
    S = 500, 0.96472 in the limit (their "analytic estimate" is defined by equating the two
    terms, `:154`). The printed 0.999 requires eta = 1.003, which occurs only for a start at
    S ~ 12 (eta = 0.996 at S = 10, 1.032 at S = 17.8), where the balance ratio is 0.95, not
    0.964. So r_ta^3 = 2 G M t_ta^2 (`:167-169`, "better than 0.1 %") is low by 8.8 % in
    r^3 (2.8 % in r) against r_ta^3 = 2.1758 G M t_ta^2 here; 2106.07480's 2.172 is right
    to 0.2 % [VERIFIED by run 122051; the cause of 1901.08528's number is not known].
1d. Holds: closed form (2/pi) B(1/2, 3/4) = 1.525520 = quadrature to 1e-15; Monte Carlo
    (4e6 orbits) over the bin-averaged exact expectation 0.99785 (weighted mean over bins
    with r < 15, largest single-bin statistical error 1.35 %, largest deviation 3.6 % in
    the bin at r = 1.6). The printed "53 %" is 52.6 % rounded.
