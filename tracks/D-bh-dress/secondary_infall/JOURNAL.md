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

## 2026-11-15T12:50Z  outcome of Test 2, runs D-bh-dress-20261115-122303-4e8e8af (stopped),
## D-bh-dress-20261115-123813-97afeea

Run 122303 stalled: the convergence metric over lambda in [1e-6, 0.98] sat at 0.05, the
sampling noise of m at lambda < 1e-4 with 4e5 samples; the piecewise-linear profile also
made the integrator take ~1.5e7 evaluations per orbit. Stopped by its process id after
7 iterations (manifest status failed, exit -15). Run 123813: Hermite interpolation,
1.5e6 samples, Gaussian smoothing of 3 grid cells (3.5 % in lambda) of the profile that
drives the next orbit, convergence on lambda in [1e-3, 0.98]: converged after 12
iterations, max |d ln m| = 2.0e-3 (7.5e-3 on [1e-6, 0.98]); 9 s per iteration. Figure
`figs/selfsimilar.png` looked at: the radial orbit returns to apocentres 0.895, 0.868,
0.852 ... of its turnaround radius, the phase-space spiral has its outer edge at
lambda_1, rho/rho_b is a power law over five decades with steps at the caustics.
2a. Refuted on the stated interval: d ln m/d ln lambda = 0.705 on [3e-3, 3e-2] (rho slope
    -2.295), 0.741 on [1e-4, 1e-3], 3/4 within 0.01 only below lambda ~ 1e-4. The
    approach to 9/4 is slow because the apocentres of a shell keep shrinking for many
    orbits (0.895, 0.868, 0.852, 0.843, 0.835 ...).
2b. Holds: lambda_1 = 0.3553 (my recollection 0.364 for Bertschinger's value, not read at
    the source, 2.4 % away; the smoothing blurs by 3.5 % in lambda).
2c. Refuted where stated, holds asymptotically at the edge: rho/rho_frozen = 3.02 on
    [1e-5, 1e-4], 2.95 on [1e-4, 1e-3], 2.77 on [1e-3, 1e-2], 2.49 on [1e-2, 3e-2],
    2.19 on [0.03, 0.1] (`selfsimilar_profile.npz`). The "A" printed in selfsimilar.json
    comes from a fit with slope 0.705 and is not the asymptotic coefficient; ignore it.
2d. Holds: m(lambda_1) = 0.654.
First passage through the centre at tau = t/t* = 2.03 (analysis run below).

## 2026-11-15T12:55Z  test 3 first pass (runs D-bh-dress-20261115-1235{16..30}-cff68f1), and
## predictions for the reruns

Development analysis (scratch/D-bh-dress/tmp/analyze_dev, not a registered result) showed:
(i) eps = 0.1 with s = 5M (run 123522) turned around only 10.9 M of dust by a/a_i = 100
against 55.9 M in closed form: the Plummer softening also weakens the self-gravity of the
dust within a few s of the centre, i.e. the deceleration of the Hubble flow there, so the
inner shells are less bound and the effective seed is weaker. Kept on record as a
softening result; not a test of self-similarity. (ii) The angular-momentum runs used a
fixed capture L < 4M, r < 4M while the hole grew to 1.8 M; the rule must use the current
hole mass. Both fixed in commit 8e548d6.
Predictions for the reruns, written before they run:
3d'. eps = 0.1, s = 0.5M, to a/a_i = 100: M_ta within 1 % of the closed form at
     a/a_i = 100 (55.9 M + M); on lambda in [0.03, 0.3] the stacked profile within 20 % of
     test 2 (bin averages); fitted slope on [0.02, 0.2] within 0.1 of test 2's on the same
     bins; dress (dust that passed the centre) over M_ta within 10 % of test 2's
     2.03^(-2/3) = 0.62.
3f'. With the capture rule scaled to the hole mass, the captured fraction rises against
     the first pass (run 123524 to 123530): sigma_i = 0.02 and 0.05 capture all of the
     collapsed dust by a/a_i = 4 (as before), sigma_i = 0.1 captures more than 92 %,
     sigma_i = 0.2 more than 69 %.

## 2026-11-15T13:00Z  outcome of Test 3; shell runs D-bh-dress-20261115-123516/123518/
## 123520/123522-cff68f1, 124330..124338-75000d9, 124552-5d687b5; analysis runs
## D-bh-dress-20261115-125449-60a62b8 (failed: empty fit range), 125507-a75a911,
## 125613-248fdaf (the one quoted)

Superseded, kept on record: 123524..123530-cff68f1 (capture rule not scaled to the hole
mass), 123522-cff68f1 (eps = 0.1 with s = 5M: M_ta = 11.87 M at a/a_i = 100 against 56.87 M
in closed form; softening of the dust's own gravity suppresses the turnaround), analysis
125507 (splashback by the maximum radius). Figures in `figs/` looked at: growth, profiles
(eps 0.01, 0.03), selfsim_check, phase_space, angular_momentum.
3a. Holds: absorbing run (s = 0), all 2759 shells that turned around: max relative error
    of the turnaround time 3.8e-7, of the absorption time at 2M 1.6e-6 (2573 shells,
    `shells_absorb_e0.01.json`). The passing runs have no shell with r_i > 100 s, so they
    are not checked this way; their M_ta agrees with the closed form to 1.4e-3 (eps 0.01)
    and 1.8e-3 (eps 0.03) over a/a_i <= 8 (analysis.json, checks).
3b. Holds where checked: c(2) = 0.262678 against the scoping's 0.262699 (8e-5); c(4) =
    0.4076, c(8) = 0.4843. c(10) not checked (the unsoftened runs stop at a/a_i = 8).
    Note for the lead: the scoping JOURNAL's "over a quadrupling 1.63 M" disagrees with its
    own table (M_ta/M = 2.628 at a/a_i = 4); this package finds 2.630.
3c. Holds: M_bh against the closed form to 4e-15 at every snapshot; (M_bh - M)/(M a/a_i) =
    0.096, 0.207, 0.277 at a/a_i = 2, 4, 8, rising towards 0.356 (not reached by 8). The
    hole doubles at a/a_i = 4.52. Infall profile: slope -1.42 on [3M, 0.1 r_ta] (a/a_i = 4
    and 8, eps 0.01; a/a_i = 8, eps 0.03), -1.37 on [3M, 0.3 r_ta]; the curve
    Mdot/(4 pi r^2 (2 M_bh/r)^(1/2)) lies on the shells below ~0.2 r_ta (figure). So
    r^(-3/2) holds where the hole dominates, flattening outwards as the infall speed falls
    below free fall from infinity.
3d'. Mixed: slope on [0.02, 0.2] at a/a_i ~ 100 is -2.468 against test 2's -2.396 on the
    same bins (holds, within 0.1); dress/M_ta = 0.606 against 2.0255^(-2/3) = 0.625 (holds,
    3 %); M_ta = 55.99 against 56.87 (refuted at 1 %: 1.5 % low, softening); rho on
    [0.03, 0.3] within 32 % per bin, not 20 % (refuted; the bins hold ~30 shells of
    ~0.1 M, and the cumulative mass agrees to 10.6 %). The figure shows the approach to
    test 2 moving inwards with a: at a/a_i ~ 10 the shells are below test 2 inside
    lambda ~ 0.05, at 30 and 100 they agree within the bin scatter down to lambda ~ 0.01.
    The splashback (radius holding 99 % of the dust that passed the centre) is 0.38-0.43
    r_ta for a/a_i <= 8 in all three eps, but 0.50 at 30 and 0.94 at 100 for eps = 0.1:
    a few per cent of the mass in light shells (log-spaced masses 1e-6 to 0.1 M) heated
    by heavy ones over thousands of orbits. Discreteness of the shell model, not the
    continuum; open (equal-mass shells would settle it). Test 2: lambda_1 = 0.355.
3e. Holds: dress = 0.189 M at a/a_i = 2 and 0.820 M at 4 (eps 0.01); 0.187/0.818
    (eps 0.03), 0.180/0.808 (eps 0.1): independent of eps to 1.5 % (Newtonian scaling).
    Dress reaches 0.25, 0.5, 1, 2 M at a/a_i = 2.22, 3.03, 4.54, 7.44.
3f (first pass). Refuted for sigma_i = 0.1: 92 % captured (fixed rule), not 30-80 %.
3f'. Holds: sigma_i = 0.02 and 0.05 capture all collapsed dust (0.83 M and 0.77 M) by
    a/a_i = 4; sigma_i = 0.1 captures 97.4 % (0.576 of 0.591 M), sigma_i = 0.2 74.0 %
    (0.211 of 0.285 M). The dispersion also lowers M_ta at a/a_i = 4 from 2.63 to 2.60,
    2.47, 2.10, 1.47 M. Conclusion [JUDGEMENT]: at the scales a full-relativity run can
    reach (r_ta of tens of M), cold or warm dust gives no dress that survives capture;
    a surviving dress needs L > 4 M_bh, i.e. tangential speeds that also change the infall.
Local growth exponent d ln M/d ln a of the dress: > 3/2 for a/a_i < 4.5, 1.3 at 8, -> 1
by a/a_i ~ 30 (eps 0.1 run). The a^(3/2) law of 1805.09034 (main.tex:216-218) and the
self-similar a^1 cannot be told apart in a run that ends at a/a_i <= 8; both differ from
what these runs will see, which the shell reference predicts directly.

## 2026-11-15T13:10Z  prediction for the set-ups of RUNS.md (vacuum core R_w = 3M, eps = 0.03)

Removing the dust inside R_w = 3M (0.012 M) acts on the outer shells like a seed of
0.988 M (energy E = -(M - 0.012)/r_i). Expect at a/a_i = 4: M_ta in [2.58, 2.62] M
(no-core value 2.627), dress in [0.77, 0.81] M (0.818), M_bh in [1.79, 1.83] M (1.833);
at a/a_i = 2 all three lower by 1-4 %. Refuted outside these ranges.

## 2026-11-15T13:15Z  outcome for the vacuum-core set-ups, runs
## D-bh-dress-20261115-125957-d087954 (absorbing), D-bh-dress-20261115-130000-d087954 (passing)

Holds at a/a_i = 4: M_ta = 2.595 (absorbing) and 2.593 (passing) M, dress = 0.796 M,
M_bh = 1.811 M, all inside the stated ranges. Refuted for the dress at a/a_i = 2: 0.1725
against 0.187 without the core, 7.7 % lower, not 1-4 %: the first dress is made of the
innermost dust, which is what the core removes (M_ta -1.0 %, M_bh -1.2 % there, as
predicted). Turnaround and absorption times against the closed forms: 5.0e-6 and 4.2e-6.
RUNS.md now quotes these numbers for the proposed runs; its density tables remain those of
the set-up without the core (stated there).
