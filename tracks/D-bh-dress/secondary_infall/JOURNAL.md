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

# Wave 2: first Newtonian-mode run (helper newton_infall, 2026-11-15)

Executable: release core-v0.3 processor build `/data/haiyangw/nrpic/.work/build_cpu_v03/src/athena`
(Serial Kokkos, one core per run). The release has no fixed point mass
(`outbox/20261115T1510Z__to-core__newtonian-mode-point-mass.md`; core's `core/requests-adf`
has it in work, no executable published: `scratch/core/exe/core_requests-adf/READY` absent).
The hole is therefore a CLUMP: 19952 equal-mass particles of total mass 1 on a cubic lattice
inside r < 0.3 M, cold, at the origin, which is a vertex of the mesh (`nm_ic.py`). Dust:
500032 equal-mass particles on the lattice (i + 1/2) h, h = 0.372 M, for 3 M <= r < 18.35 M
(1.2 x the initial radius of the shell that turns around at a/a_i = 4), Hubble flow
v = eps x, eps = 0.03. The system is symmetric under the 48 reflections and axis
permutations; so is the mesh about the origin. Box [-68, 68]^3 M, isolated, multipole
boundary of order 4.

## 2026-11-15T17:10Z  predictions: field calibration and timing probe

F1 (clump alone, 3000 massless tracers at rest, log-uniform in r on [0.05, 30] M, one step
of 1e-6; nx = 64 and 128, dx = 2.125 and 1.0625 M). The radial acceleration g_r r^2/M:
(a) rms relative error below 1e-2 for r > 4 dx and below 3e-3 for r > 16 dx (core's point
mass, interface section 5.2: 6e-3 at 8-16 cells, 1.3-1.7e-3 beyond 16 cells);
(b) inside ~2 dx the force is softened; a Plummer law g = M r/(r^2 + s^2)^(3/2) fitted on
r < 4 dx gives s_eff in [0.5, 1.0] dx at both resolutions (so s_eff scales with dx);
(c) the transverse force inside 2 dx up to ~30 per cent of the radial (anisotropic softening,
interface 5.2: 0.23-0.57 relative error inside 2 cells).
Refuted if (a) fails by more than a factor 2, or s_eff lies outside [0.3, 1.5] dx.

F2 (clump + dust + tracers, nx = 128, one step): g_r r^2 against 1 + (4 pi/3) rho_i
(r^3 - 27) for 3 M < r < R_edge: rms relative error below 1e-2 on [4 dx, R_edge - 2 dx]
(the dust lattice h = 0.37 M is finer than dx = 1.06 M; the density jumps at 3 M and at the
edge are smeared over one cell, interface 5.3). Inside the vacuum core (0.3 < r < 3 M) the
dust contributes no force to below 1 per cent of the clump's. Refuted if either fails by
more than a factor 2.

P1 (timing, nx = 128, 20 steps, 520k particles): 1-3 s per step on one core with
newton_mg_tol = 1e-6 (interface 5.8: 3.2 s at 128^3 and 1.4e5 particles with threshold 0,
13-19 V cycles; the tolerance cuts the cycles to a third). Refuted if above 6 s per step
(then the 128^3 run to a/a_i = 4, ~1500 steps, does not fit a few hours on processors).

## 2026-11-15T17:20Z  outcome F1, F2, P1 (runs D-20261115-170112-d70352c nx 64, -170122-7c4da35 nx 128,
## -170124-1b2ea1a nx 128 with dust, -170127-877c84f timing; analysis registered next as nm_field)

F1 holds. (a) rms relative error of g_r beyond 4 cells 9.4e-3 (nx 64) and 7.9e-3 (nx 128);
beyond 16 cells 9.8e-4 (nx 128; nx 64 has no tracer there). (b) Plummer fit inside 4 cells:
s_eff = 0.609 dx (nx 64, 1.293 M) and 0.611 dx (nx 128, 0.649 M): the softening scales with
the cell. But the Plummer law is a poor description (fit rms 0.19-0.20 in g r^2/M): the mesh
force is almost zero inside 0.5 dx (-97 % at 0.25-0.5 dx, -72 % at 0.5-1 dx) and
OVERSHOOTS by up to 30 % at 1.3-2 dx (bin mean +7 to +8 % at 1-2 dx). The binned median
kernel f(r/dx) = g_r r^2/M is written for the shell reference (kernel_nx64.txt,
kernel_nx128.txt); the two resolutions overlay in r/dx. (c) transverse force rms 13.5-13.7 %
of g at 1-2 dx, 4.5 % at 2-4 dx, 1.7 % at 4-8 dx.
F2 holds. g_r against 1 + (4 pi/3) rho_i (r^3 - 27) on [3 M + 4 dx, R_edge - 2 dx]: rms
3.3e-3. The dust's own force (run with dust minus clump alone, same tracers): inside the
vacuum core at most 2.1e-4 of g (shell theorem holds on the mesh), in the dust rms 5.3e-4
and at most 1.9e-3; peaks at the two density jumps (3 M, 18.35 M), as interface 5.3 says.
P1 holds: 20 steps in 56.8 s of processor time with setup, about 2.7 s per step at
128^3 with 520k particles; the step stayed at the upper limit 0.25 (no fast particles yet).

## 2026-11-15T17:25Z  predictions: the Newtonian-mode infall runs N128 (nx 128, box +-68 M,
## dx 1.0625 M, to a/a_i = 4), N64 (nx 64, same box, dx 2.125 M) and N128L (nx 128, box
## +-176 M, dx 2.75 M, dust edge 24.5 M, to a/a_i = 8)

Reference numbers known now: wave-1 shell runs with the vacuum core 3 M and Plummer s = 0.5 M
(pass_e0.03_s0.5_rw3, D-bh-dress-20261115-130000-d087954): M_ta = 1.505, 2.045, 2.593 M and
dress = 0.173, 0.472, 0.796 M at a/a_i = 2, 3, 4. Before any output of these runs is read,
nm_shells.py will compute the same set-up with the mesh kernel measured above at the
snapshot times of the runs (the matched reference); the criteria below apply to it.
1. Turnaround mass (dust that has turned around, counted from the snapshots, plus the clump):
   within 2 % of the matched reference at every snapshot after a/a_i = 1.5, in all three runs.
   [the turnaround of a shell is set by the force at r >= its initial radius 3-25 M, where
   the mesh force is within 1 % beyond 4 cells]
2. Dress (dust that has passed its pericentre once): within 5 % of the matched reference
   at a/a_i = 4 in N128, within 10 % in N64, within 10 % at a/a_i = 8 in N128L; at
   a/a_i = 2 within 15 % (made of the innermost shells, r_i = 3-5 M, i.e. 1.4-5 cells).
3. Density rho/rho_b(t) of the dust in logarithmic bins: within 30 % per bin of the matched
   reference for 4 dx <= r <= r_ta at a/a_i = 2 and 4 (N128, N64), at a/a_i = 4 and 8
   (N128L); flatter than the reference inside 2 dx (transverse force: orbits miss the
   centre).
4. Against the self-similar solution (test 2, D-bh-dress-20261115-123813-97afeea), with
   r_ta from G M_ta t^2/r_ta^3 = pi^2/8 and the measured M_ta: at a/a_i = 4 the profile
   agrees within 30 % per bin only for lambda = r/r_ta in [0.1, 0.35] and lies off it
   inside lambda < 0.1 (the seed dominates there; wave-1 analysis 125613); dress/M_ta =
   0.3 at a/a_i = 4 and 0.45 at a/a_i = 8 against the self-similar 0.625; M_ta/(M a/a_i)
   = 0.65 at 4 and 0.60 at 8 against the asymptote 0.5648 (approached from above).
5. The clump: its centre of mass stays within 0.01 dx of the origin (symmetry of the set-up,
   broken only by rounding); its 90 % radius stays below 1 dx; the total momentum of all
   particles below 1e-4 M c (rounding and the kernel mismatch, interface 5.5: 2.5e-5).
   K + W changes by less than 1 % of |W(0)| over the run.
6. No particle leaves the box (dust edge at a_end 59.8 M of 68 M; N128L 155.2 M of 176 M).
7. Cost: N128 about 1700 steps at 2.7 s, 75-90 min; N64 10-20 min; N128L 1900-2500 steps,
   1.5-2 h. One core each.
Refuted where a number falls outside the stated band; then name the cause only after a
run that could have shown otherwise.

## 2026-11-15T17:20Z  observation during N128/N64 (before any snapshot was analysed): the clump runs off the vertex

The history (`infall.newton.hst`, column P_x) of N128 grows exponentially from rounding:
-6.8e-18 (t = 0), -2e-13 (5 M), -6.3e-12 (7.9 M), -9.3e-11 (10.1 M), -1.4e-9 (12.4 M), an
e-folding time of about 0.85 M; N64: -1.6e-15 (5 M) to -6.9e-12 (25 M), about 2.3 M. The ratio
2.7 is close to 2^(3/2) = 2.83, i.e. a rate ~ (G M/dx^3)^(1/2). Hypothesis [JUDGEMENT, to be
tested]: the self-force of a compact mass in this scheme (cloud-in-cell deposit, Catmull-Rom
gather; interface 5.2: "a particle feels its own field ... 0.5 m/dx^2 ... vanishes at a cell
centre") makes the mesh vertex where the clump sits an UNSTABLE equilibrium; the symmetric
set-up only delays the run-off until rounding errors have grown.

## 2026-11-15T17:22Z  prediction S1: stability of the clump at a vertex and at a cell centre

Clump alone (19952 particles, r < 0.3 M, mass 1, 3000 massless tracers), nx = 64, box +-68 M
(dx 2.125 M), fixed step 0.1, to t = 40 M, the clump displaced by 0.05 dx along x from
(V) a mesh vertex, (C) a cell centre. Prediction: (V) the displacement grows exponentially
with e-folding 1.5-3.5 M (the 2.3 M of N64) until it reaches 0.2-0.5 dx, then oscillates about
a stable point; (C) the displacement stays below 0.1 dx (oscillation about the cell centre).
Refuted if (V) does not grow, or (C) grows too (then neither point is stable and the clump
stand-in is unusable without the fixed point mass of core's request).

## 2026-11-15T17:16Z  outcome S1 (runs D-20261115-171245-a89f225 vertex, -171247-cde0674 cell centre;
## analysis D-20261115-171414-93fdf13, figure figs/nm_clumpstab.png)

(V) holds in part: from 0.05 dx the displacement grows (0.095 dx at t = 3 M, 0.21 at 5 M:
e-folding about 2.5 M, as the 2.3 M of N64) but it does not settle at 0.2-0.5 dx (refuted):
it reaches 0.96 dx at t = 15 M, comes back to 0.045 dx at 30 M and grows again, i.e. the
clump oscillates along x between two neighbouring vertices about the edge midpoint (0.5, 0, 0)
dx, with a period of about 30 M and a peak speed of 0.32 c (total momentum 0.32 M c; the
tracers carry none). (C) holds: at the cell centre the displacement stays below 0.065 dx
and oscillates with a period of about 8 M; but even this 0.05 dx offset gives the clump a
speed of 0.11 c (restoring acceleration ~ 0.07 GM/dx^2 per 0.05 dx). So the vertex is an
unstable and the cell centre a stable equilibrium of the clump's self-force [VERIFIED,
these two runs]. Consequence: the three infall runs started at 17:07 (N128, N64, N128L, clump
at a vertex) will have the hole running off the dust's centre by up to ~1 dx at speeds of
order (G M/dx)^(1/2)/2 once rounding has grown (N128 near t ~ 25 M, N64 near ~ 90 M, N128L:
|P| = 3.6e-7 at t = 70 M). They are kept running as the record of that failure mode; the
set-up is repeated with the configuration centred on a cell centre.

## 2026-11-15T17:18Z  prediction for N128c, N64c, N128Lc (as N128, N64, N128L, whole
## configuration displaced by (1/2, 1/2, 1/2) dx so that the clump sits at a cell centre)

Items 1-4, 6, 7 of the 17:25Z prediction unchanged (same matched references; the shell runs
are D-20261115-170824-788678f, -170826-20d5d4a, -170827-ba851f0 for N128; -170829-0d86d49,
-170831-b379b65 for N64; -170834-ac15adf, -170837-af64029, -170839-187b91b for N128L).
Item 5 replaced: the clump's centre of mass stays within 0.05 dx of the cell centre for the
whole run, its speed below 0.05 c, total momentum below 1e-2 M c (the box faces are not
symmetric about the cell centre, so the boundary seeds a small offset; the dust lattice is
symmetric about the clump); K + W within 1 % of |W(0)|. In the vertex runs, by contrast,
the clump displacement exceeds 0.3 dx before the end (N128 and N128L at least).

## 2026-11-15T17:55Z  outcome for N64c (cell centre, D-20261115-171505-62940f4) and N64 (vertex,
## D-20261115-170703-46ddffa); analysis D-20261115-174734-a688058 (nm_analysis.json, figures)

Matched references: shells with the nx 64 kernel (D-20261115-170829-0d86d49), Plummer
s = 1.293 M (-170831-b379b65), point s = 0.05 M (-170827-ba851f0). The three references differ
by less than 2.1 % in M_ta and the dress after a/a_i = 1.5 (softening hardly matters for the
masses; it matters for the inner profile).
N64c against the kernel shells:
1. M_ta holds: largest deviation after a/a_i = 1.5 is 0.12 %; M_ta = 1.506, 2.048, 2.597 M at
   a/a_i = 2, 3, 4 (wave-1 shells with s = 0.5 M: 1.505, 2.045, 2.593).
2. Dress holds: +1.4 % at a/a_i = 2, +0.15 % at 4; 0.174, 0.472, 0.797 M at 2, 3, 4.
3. Profile, 4 dx <= r <= r_ta: largest deviation 14 % (a/a_i = 2), 15 % (3), 31 % (4): the
   prediction (30 %) fails by one bin at a/a_i = 4, the bin of the outermost caustic (16-20 M,
   ratio 1.31: the shell caustic is sharp, the run's is smeared over a cell); outside the
   two bins around the caustic the largest deviation is 6.3 %, rms 3.7 %. Refuted: "flatter
   than the reference inside 2 dx"; inside 2 dx the ratio scatters between 0.4 and 1.3 with
   no systematic flattening at this resolution.
4. Self-similar comparison at a/a_i = 4 (r_ta = 40.5 M from M_ta, measured from the mean
   radial velocity 40.3 M): refuted for the profile: rho_run/rho_ss = 0.46, 0.59, 0.57, 0.72,
   1.02 at lambda = 0.11-0.35; the run lies below the self-similar profile by up to a factor
   2 down to lambda = 0.1 (its outermost caustic is at 16-20 M, lambda = 0.4-0.5, against
   lambda_1 = 0.355). Holds for the masses: dress/M_ta = 0.307 (predicted 0.3; self-similar
   0.625); M_ta/(M a/a_i) = 0.649 (predicted 0.65; asymptote 0.565 + 1/(a/a_i)); local growth
   exponent of the dress 1.67 at a/a_i = 4 (wave 1: > 3/2 below 4.5).
5. Clump holds: centre of mass within 2.0e-5 dx of the cell centre, 90 % radius at most
   0.18 dx, total momentum at most 9.6e-5 M c. Energy refuted: K + W oscillates by up to
   4.7 % of |W(0)| = 1.13 in the first a/a_i ~ 2 and ends 1.3 % low. The clump alone at the cell
   centre (S1-C, D-20261115-171247-cde0674, no dust) loses 5.4 % of its |W(0)| = 0.654 and
   oscillates the same way, so the error is the clump's sub-cell self-interaction (deposit
   and gather kernels differ), not the dust's motion [VERIFIED by S1-C]; energy is therefore
   no check of the dust in this set-up.
6. Holds: all 519984 particles stay in the box.
7. Refuted: 1781 s (N64c) and 1580 s (N64) instead of 10-20 min; 2.2 s per step at 64^3,
   the particles (520k, one core) dominate, not the mesh.
N64 (vertex) against the same reference: M_ta within 0.12 %, dress -0.4 % at a/a_i = 4: the
global masses do not notice the hole's wandering. The inner profile does: the clump leaves
the vertex at a/a_i ~ 2.8 (|P| from 1e-15 at a/a_i = 1.1 to 0.5 M c), its centre moves 0.9 dx,
its 90 % radius grows to 1.1 dx and one clump particle reaches 15.9 M; at a/a_i = 4 the dust
density inside 2 M is 2-7 times below the reference, the outermost caustic is smeared
(deviation 104 % at the caustic, 35 % outside it), dust is flung out to 60 M at up to 0.8 c
(`nm_phase.png`), and K + W ends 7.4 % low.
