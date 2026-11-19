# JOURNAL of first_source (helper package of B-emd-gw, wave 2)

Predictions are written before the run they concern; outcomes are appended below them,
also when a prediction fails. Run ids are under `tracks/B-emd-gw/runs/`.

## Set-up (2026-11-15, before any run of this package)

Configuration (action 1 of `HANDOFF.md`, `stage/G1/STATUS.md`): crossed waves with
amplitude ratios (1, eps, 0), eps = 0, 0.1, 0.3, 1; delta = 0.01; box 4 (initial Hubble
radii); 64^3 cells; two particles per cell and direction (2,097,152 particles); production
configuration of `cosmo/README.md` (input `inputs/crossed.athinput`, conformal-time lapse,
zero shift); end at a = 140 = 1.4/delta; Z4c variables in single precision every 0.1 and in
double precision (restart files) every 1.0 of conformal time. A fifth run, eps = 1 in a
second spatial gauge (Gamma-driver shift `shift_Gamma = 0.75`, `shift_eta = 1`, advection
of shift and lapse; same slicing condition), is the gauge check of P6.

Notation. Code time tau is conformal time with a = (1 + tau/2)^2 and conformal Hubble rate
Hc = 1/(1 + tau/2) (`tracks/B-emd-gw/scope/scripts/regime_estimates.py` lines 7-8, the
units of `cosmo/README.md`). k = 2 pi/4 = pi/2; K1 = (k, k, 0), K2 = (k, -k, 0),
|K| = sqrt(2) k = 2.221. Potential of the initial data:
Phi = sum_i phi_i sin(k x_i), phi_i = -(3/2)(H/k)^2 delta r_i, r = (1, eps, 0)
([VERIFIED] `cosmo/ic/make_east.py` lines 9-11, 40-45). h = tilde gamma - delta; Lambda the
flat TT projector of `gw_diag`. The + amplitude at K1 is
c_+(K1) = (2/N^3) sum_x (1/2) e+_ij (Lambda h)_ij cos(K1.x), e+ = u u - z z,
u = (1, -1, 0)/sqrt 2 (coordinates of `make_east.py`, box [0, 4)).

Reference before shell crossing [from the track's derivation: `scope/SCOPE.md` section 3
and the lead note there, run B-emd-gw-20261115-113148-4e5c33b, rederived by the lead in run
B-emd-gw-20261115-131027-03b1119 check d]: the quasi-static second-order TT strain of the
weak-field equation of arXiv:1604.06065 is h^TT = (20/3) Lambda[d_i Phi d_j Phi]/|K|^2, which
at K1 is h_+ = -(5/6) phi_x phi_y cos(K1.x) and at K2 is +(5/6) phi_x phi_y cos(K2.x) in its
own basis u = (1, 1, 0)/sqrt 2 (I checked the two signs by hand before writing this:
Lambda(e_x e_y + e_y e_x) = -(1/2) e+ at K1 and +(1/2) e+ at K2). With phi_x phi_y =
(9/4)(H/k)^4 delta^2 eps: static value s = -(5/6) phi_x phi_y = -3.080e-5 eps at
delta = 0.01. The initial data are conformally flat (h = 0, Lambda A = 0), so the mode
starts from zero; it follows g'' + 2 Hc g' + |K|^2 (g - 1) = 0, g(0) = g'(0) = 0
(`scope/scripts/regime_estimates.py`, check 3A): c_+(K1)(tau) = s g(tau).

Gauge [JUDGEMENT, my derivation, written here so that it can fail]:
(i) At first order the code's gauge is the Newtonian gauge: with alpha = a(1 + Phi),
gamma = a^2 (1 - 2 Psi) delta, zero shift, the slicing condition d_t alpha = -(1/3)
alpha^2 K holds at first order exactly when Phi' = -Psi', i.e. for the constant potential of
the growing mode. Then the code's Lambda h equals the Poisson-gauge strain at second order,
and gauge differences enter at the next order through products of second-order gauge
generators.
(ii) Spatial gauge on the code's slice. If the code coordinates x' and coordinates x in which
the conformal metric has no traceless scalar or vector part are related by
x = x' + xi(x'), M_ki = d_i xi_k, then exactly to second order in (M, h_T)
Lambda h' = Lambda h_T + G,  G = Lambda[M^T M - (2/3)(div xi)(M + M^T)],
with xi recovered from the measured traceless non-TT part of h'
(xi_i = -i k_j h_ij/k^2 + (i/4) k_i (k k h)/k^4 in Fourier space). G is the "second-order
gauge piece of the flat projection" of the wave-1 caveat; h_T^TT = Lambda h' - G is the
TT strain on the code's slice in spatially transverse coordinates. The slicing part of the
gauge freedom is not removed by G.

## Predictions for the scan and the second gauge (written before the initial data were made)

P0 (initial data). make_east.py reaches Hamiltonian and momentum residuals below 1e-9 and
1e-7 for all four eps (wave 1 at delta 0.05: 2.7e-10, 1.1e-8, run
B-emd-gw-20261115-115902-a3207d7). Refuted if larger.

P1 (null, eps = 0). At every dump to a = 140, through shell crossing, the largest TT
amplitude at any nonzero wave vector, of h and of tilde A, is below 1e-12 of the rms
traceless part of the same field (exit criterion of `scope/SCOPE.md` section 6), in the
double-precision restart dumps and in the single-precision dumps (rounding keeps exact
plane symmetry). Refuted by any dump above 1e-12; a value between 1e-16 and 1e-12 that grows
in time would mean round-off seeds (atomic deposition) amplified by transverse instability.

P2 (amplitude before shell crossing). c_+(K1)(tau) = s g(tau) with
s = -3.080e-5 eps, within 2 percent for 2 <= a <= 10 (fourth-order corrections, of relative
size delta^2 [JUDGEMENT: (k, k, 0) receives no third-order term, because no three of the
first-order wave vectors +-k e_x, +-k e_y add up to it]). The same with the opposite sign at
K2 in its basis. Including the junk oscillation: the phase of the oscillation of
c_+ - s about s matches g(tau) - 1 to 0.1 rad at a <= 10. Refuted if the amplitude is off by
more than 2 percent at a <= 10 or has the wrong sign, or if the oscillation has another
period (2 pi/|K| = 2.83).

P3 (linearity in eps). c_+(K1)/eps for eps = 0.1, 0.3, 1 agrees to 1 percent for a <= 10;
later the departures grow, with the eps = 0.1 and 0.3 curves closer to each other than to
eps = 1 (corrections in eps^2 phi_y^2). Refuted if the eps = 0.1 and 0.3 curves differ by
more than 1 percent at a <= 10.

P4 (mode content). For a <= 20 and eps >= 0.1 the four modes (+-k, +-k, 0) carry more than
90 percent of the mean square of Lambda h; Lambda h is independent of z to round-off (the
data do not depend on z). Refuted otherwise.

P5 (gauge piece in the zero-shift gauge). The rms traceless non-TT part of h grows roughly
as a before shell crossing (as in the wave-1 scouting on the cosmology dumps,
`gw_diag/figs/cosmo_tt.png`); the spatial-gauge piece G at K1 is below 5 percent of c_+ for
a <= 20 and grows roughly as a^2 relative to it [JUDGEMENT: G/s ~ (non-TT part)^2/(phi_x
phi_y) ~ delta^2]. Refuted if G at K1 exceeds 5 percent of c_+ at a <= 20.

P6 (second gauge, eps = 1, Gamma driver). (a) The run reaches a = 140 with finite fields
(not certain: the shift driver of `cosmo/TESTLOG.md` lines 809-822 failed on refined blocks
at delta = 0.05; this mesh is uniform). (b) After a = 10 the rms traceless non-TT part of h
is at least three times smaller than in the zero-shift run. (c) Before shell crossing the
raw c_+(K1) of the two runs differ by about the difference of their G; after the
correction (h_T = Lambda h - G in each run) the difference falls to below 30 percent of the
raw difference wherever the raw difference exceeds 1e-3 of |s|. This is the test in which
the gauge explanation can fail: if the corrected curves differ as much as the raw ones, the
spatial-gauge piece is not what separates the two gauges. (d) The magnetic Weyl part B
(invariant under spatial coordinate changes at second order, since B vanishes at first order
for scalar perturbations) agrees between the two runs better than the raw Lambda h does.

P7 (the wave-1 caveat on the existing cosmology dumps, `runs/cosmo/dav_c256_n128_t` and
`_pcs4bt`, 14 restart dumps each, a = 1 to 1000). Caveat hypothesis: the late rise of rms
h^TT (from 1.2e-9 at a <= 550 to 2.4e-9 and 4.2e-9 at a = 1000) is the spatial-gauge piece.
Then rms(Lambda h - G) stays within 30 percent of 1.2e-9 to a = 1000 while rms(G) rises as
(rms non-TT)^2. Refuted if rms(Lambda h - G) rises above 1.5 times 1.2e-9 at the last dump
in either run: the rise is then not (only) the spatial-gauge piece. Before applying G to
real data: T0, on exact pure-gauge Minkowski data with random spatial coordinates
(`gw_diag/gwdiag/analytic.py`, gauge_mode with slicing off), Lambda h - G falls as eps^3
(slope 3.0 +- 0.1) while Lambda h falls as eps^2; with the slicing on, the residual stays
at eps^2 (G does not remove the slicing part).

## Initial data, run B-20261115-161656-03d75e1 (outcome of P0, partly)

The run was killed after 15 min by the `timeout 900` I had wrapped around the blocking
`nrpic-run submit` (my error, not the code's): eps = 0, 0.1, 0.3 had finished, eps = 1 was in
its tenth outer iteration (change of psi 6.3e-10) and its directory is empty. Manifest closed
as failed (exit -15). The three finished cases are complete (logs end with the residual
summary) and are used. P0 for them: CONFIRMED. Hamiltonian residual 4.8e-12, 1.3e-11, 4.0e-11,
momentum 3.1e-17, 1.1e-16, 1.5e-16 (eps = 0, 0.1, 0.3); max |psi_N| 6.07e-3, 6.68e-3, 7.89e-3;
max |Ahat| 1.27e-4 to 1.60e-4; largest displacement 0.10 cells; 2,097,152 particles each
(`eps*.log` of the run). eps = 1 is rebuilt in a separate run, without a timeout.

## T0 and the reference (runs B-20261115-164221-6a6b779, B-20261115-164157-40b9f6d)

T0, outcome: CONFIRMED. On exact pure-gauge Minkowski data (32^3, two seeds, eps = 1e-4 to
1e-2) the fitted slopes are 2.000 for Lambda h and 3.000 to 3.001 for Lambda h - G with the
slicing off; with the slicing on both stay at 2.000 (G does not touch the slicing part).
Dealiasing (3/2 padding) changes nothing at these smooth fields (slopes equal to 1e-13).
Figure `t0_gauge.png` of the run, looked at. Unit tests (`tests/test_gauge.py`, 5 pass): the
inverse xi(h) reproduces the traceless non-TT part to 1e-12; a TT wave under a random
spatial gauge is recovered after the correction to below 1 percent of the raw error; the
companion piece G_A of tilde A (added after T0, see below) removes the first-order term
(raw slope 1.00, residual slope 2.0).

Reference (run B-20261115-164157-40b9f6d; `reference.json`, figure `reference.png`, looked
at): s = -3.0797e-5 eps; g = 1.0993, 1.0336, 1.0140, 1.0089, 1.0073 at a = 10, 20, 40,
60, 140; |g - 1| envelope falls as 1/a (check 3A reproduced); period 2.83 in tau. Predicted
c_+(K1)/eps = -3.385e-5 at a = 10 (on a crest of the junk), -3.183e-5 at a = 20. The
outputs of this run were first written to a directory literally named `$NRPIC_RUN_DIR` in the
worktree root (nrpic-run does not expand the variable in argv; my error); I moved the four
files into the run directory after `finish` (`sha256sums.moved.txt` there) and removed the
empty directory. The scripts now default to the environment variable.

## P7b (written before the run on the cosmology dumps)

Companion of G for the extrinsic curvature: tilde A transforms like the conformal metric,
so Lambda tilde A' = Lambda tilde A_T + G_A, G_A = Lambda[M^T A + A M - (2/3)(tr M) A +
(xi . grad) A] (fslib/gauge.py, gauge_piece_A, tested as above). rho_kin of the wave-1
scouting (`gw_diag/figs/cosmo_tt.png`, middle panel) rises from ~1e-19 rho_bar at a ~ 100 to
3e-14 .. 2e-13 at a = 1000. Prediction: if this rise is the spatial-gauge piece, rho_kin
computed from Lambda tilde A - G_A is below 10 percent of the raw value at the last dump in
both runs. Refuted if it is above 50 percent there.

## Outcome of P7 and P7b, run B-20261115-164616-a6d9477 (`late_rise.json`, `late_rise.png`, looked at)

Before the registered run I tried `late_rise.one` on the last dump of the quadratic-cloud
run as a development check (a = 1001: rms Lambda h 2.488e-9, G 2.06e-10); the registered run
reproduces these numbers. The predictions above were committed before that check
(commit 55574b0).

P7: REFUTED. The spatial-gauge piece is real and of the size the caveat estimated in form,
rms G = 0.13 to 0.17 (rms non-TT)^2 at every dump from a = 12 to 1001 in both runs, but it
is an order of magnitude below the rise: at a = 1001 rms G = 2.06e-10 (quadratic cloud) and
2.23e-10 (cubic) against rms Lambda h = 2.488e-9 and 4.312e-9, and rms(Lambda h - G) =
2.496e-9 and 4.315e-9, i.e. the corrected strain rises exactly as the raw one (from
1.20e-9 at a = 415 in both). G sits at low wave numbers (spectral peak at |k|L/2pi = 5,
2-3 percent of its mean square above 20), while 93 and 97 percent of the rise of the mean
square between a ~ 340 and 1001 lies at |k|L/2pi >= 20, 56 and 73 percent above 40, with
its peak at 67 and 69 (the per-axis Nyquist number is 64).
P7b: REFUTED as well: G_A is negligible (rms 1.4e-14 against rms Lambda A 1.7e-11 at
a = 1001); rho_kin with and without G_A agree to 1e-3 at every dump.
Not predicted: rho_kin/rho_grad stays at 0.010 to 0.020 during the rise (both runs): the TT
part that rises is not freely propagating radiation (for which the two would be equal on
average) but a quasi-static field at the grid scale.

Reading [JUDGEMENT]: the late rise is not the second-order spatial-gauge piece of the flat
projection. The slicing part of the gauge freedom is not computed; with the code's
first-order gauge equal to the Newtonian one (section "Gauge" (i) above) the second-order
time shift T obeys T = -E' for zero shift (E the scalar part of h, growing as a), so the
slicing products scale as (grad T)^2 ~ (2/(k tau))^2 (d d E)^2, i.e. below G by
4/(k tau)^2 < 2e-4 for k >= 2 pi/L at tau ~ 60 [JUDGEMENT, scaling argument, not computed].
What the rise is instead: a near-grid-scale TT field (peak beyond the per-axis Nyquist
number), depending on the deposit by a factor 1.7 in rms (2.5e-9 vs 4.3e-9) and appearing
when the structure becomes nonlinear at the grid scale (a > 600): resolution-limited
small-scale structure or particle and deposit noise, not a resolved gravitational-wave
signal. It is an upper bound on the TT content at those scales, rho_GW/rho_bar < 3e-12
(quadratic) and < 1.3e-11 (cubic) at a = 1001, and the low-k part (|k|L/2pi < 10), the only
part that is resolved, does not rise. Settling between "resolved small-scale physics" and
"noise" needs the same run at 256^3 or with more particles per cell (not run).

Correction to the last sentence above (checked after the commit, same run, band sums of the
shell spectra of `late_rise.json`): the low-k part does rise, mildly. rms of Lambda h in
|k|L/2pi < 10 goes from 1.197e-9 (a = 342) to 1.290e-9 (a = 1001) with the quadratic cloud
and from 1.211e-9 (a = 335) to 1.328e-9 with the cubic cloud (+8 and +10 percent; Lambda h - G:
1.309e-9 and 1.348e-9, so G does not remove it either); the band 10 <= |k|L/2pi < 20 rises
twentyfold, from 1.6e-11 to 3.3e-10 and 3.9e-10; the band >= 20 from 7.7e-11 and 2.1e-11 to
2.1e-9 and 4.1e-9. The deposit dependence is 3 percent below 10, 19 percent in 10-20 and a
factor 1.9 above 20. So the resolved part (below |k|L/2pi ~ 20, where the two deposits agree)
does grow in the nonlinear stage, by an amount the deposit does not change; that part is a
candidate for a physical TT signal of nonlinear structure (quasi-static: rho_kin/rho_grad
~ 0.02), the grid-scale part is not resolved.

## P8: processor companion at 32^3 (written before its initial data were made)

The card job waits behind about eleven others (squeue at 16:55 UTC). The same five cases at
32^3 (two particles per cell and direction, 262,144 particles; serial processor build of
core-v0.3) run now on five cores. The k-mode wavelength is 32 cells there, so before shell
crossing the box modes are resolved at both meshes. Predictions: P0-P6 hold at 32^3 with the
same thresholds; c_+(K1) at 32^3 and 64^3 agree to 1 percent for a <= 20 once both exist
(refuted otherwise); after shell crossing they may differ.

## Initial data eps = 1, run B-20261115-164104-886798f

P0 for eps = 1: CONFIRMED (Hamiltonian residual 3.9e-12, momentum 2.5e-16, max |psi_N|
1.21e-2, max |Ahat| 3.9e-4; 2,097,152 particles; files complete). The run is recorded as
failed (exit 2): I edited `build_ic.sh` (mesh size as a variable) while bash was still
reading it, and the closing loop of the script broke after make_east.py had finished. The
outputs are those of make_east.py and are used. Lesson: never edit a script that a running
job executes.

## P9 (written before scripts/slicing_check.py ran): is the code's slicing Newtonian at first order?

The scaling argument for the slicing products above rests on "Gauge" (i): the code's first-
order gauge is the Newtonian one. Test on the same cosmology dumps (and later on the scan):
in the Newtonian gauge alpha gamma^(1/6) = a^2 at first order, while alpha and gamma^(1/6)
carry +Phi and -Phi. Prediction: in the linear stage (a <= 100) rms delta ln(alpha
gamma^(1/6)) is below 10 percent of rms delta ln alpha, and delta ln alpha and
delta ln gamma^(1/6) are anticorrelated (correlation below -0.9). Refuted if the product
varies as much as the lapse: then the slicing differs from the Newtonian one at first order,
the gauge products are not suppressed as argued, and the argument fails.

## Outcome of P9, run B-20261115-170610-c82b10c (`slicing_check.json`, `.png`, looked at)

CONFIRMED. On both cosmology runs rms delta ln alpha = 2.00e-5 to 2.03e-5 at every dump from
a = 1 to 1001 (constant, the size of Phi), rms delta ln gamma^(1/6) the same, correlation
-0.99999 at a = 1 to -0.9991 at a = 121, and rms delta ln(alpha gamma^(1/6)) = 0.4 to 4
percent of the lapse variation for a <= 121 (below the 10 percent of the prediction), growing
as a to 33 percent at a = 1001. So the first-order slicing is Newtonian; the departure grows
like a second-order quantity (Phi delta).

## P10 (written before scripts/slicing_products.py ran)

With T = 2E/eta (zero shift, E from the scalar part of h, growing as eta^2) the slicing
products Lambda[dT dT] and Lambda[T d_eta h^S] are below rms G by the factor 4/(k eta)^2 or
so; at a = 1001 (eta ~ 63, the G spectrum peaking at |k|L/2pi = 5) that is ~1e-5 [JUDGEMENT,
order-one coefficients of the transformation not derived]. Prediction: both below 1e-2 of
rms G at every dump after a = 100. Refuted if either reaches rms G: then the slicing could
matter as much as the spatial piece and P7's reading would need the slicing computed.

## Outcome of P10, run B-20261115-170728-757e581 (`slicing_products.json`, `.png`, looked at)

CONFIRMED. rms Lambda[dT dT] / rms G = 9.4e-4 at a = 12, 8.7e-5 at a = 121, 9.2e-6 at
a = 1001 (quadratic cloud; cubic: 9.2e-4, 9.3e-5, 8.9e-6); rms Lambda[T d_eta h^S] is exactly
twice that (Lambda[E d d E] = -Lambda[dE dE]). At a = 1001 both are ~2e-15 to 4e-15 against
the rise of ~2e-9: the slicing products of the generators measured from the dumps cannot make
the rise. Caveat [JUDGEMENT]: the list of slicing products and their order-one coefficients is
mine, not derived in full; the conclusion holds unless a coefficient is larger than 1e4.

Answer to the wave-1 caveat (stage/G0/REVIEW.md lines 98-102), from P7-P10: the late rise of
the flat TT part in the cosmology dumps is not a second-order gauge effect. The spatial-gauge
piece G is computed exactly to second order (0.13-0.17 (rms non-TT)^2, peaking at
|k|L/2pi = 5) and is a tenth of the rise; the slicing products are 1e-5 of G; the first-order
gauge is Newtonian (P9). The rise sits at the grid scale, is deposit-dependent there, and is
quasi-static (rho_kin/rho_grad ~ 0.02), so it is not resolved radiation either; the resolved
band (|k|L/2pi < 20) grows by 8-10 percent (below 10) and twentyfold (10-20), deposit-
independent, which is the candidate physical TT response of nonlinear structure.

## Development check on the early 32^3 dumps: the cross terms with the homogeneous anisotropy (17:30 UTC)

Before the scan analysis I ran `fslib.modes` by hand (not registered) on dumps 5, 10, 19
(tau = 0.5, 1.0, 1.9; a = 1.6, 2.0, 3.8) of the running processor scan (run
B-20261115-165525-f7c2004) to check the pipeline. Findings, all to be confirmed by the
registered analysis:
- eps = 1 raw c_+(K1) = -1.3257e-5 and -3.8422e-5 against the reference s g(tau) =
  -1.3219e-5 and -3.8433e-5 (0.3 and 0.03 percent); K2 the opposite sign; eps = 0: largest TT
  mode 2.2e-16 against a traceless part of 3e-4.
- P6(c) with G as written FAILS on these dumps: at tau = 1.9 the raw difference of c_+(K1)
  between the zero-shift and the Gamma-driver run is +1.04e-8, the G-corrected difference
  -4.2e-8 (larger). Checks: the difference of the recovered displacements xi_ZS - xi_GD equals
  minus the time integral of the Gamma-driver shift to 5e-4 (correlation -0.9999999), so the
  two runs are the same slice in coordinates that differ by that displacement; transforming
  the Gamma-driver metric by it (exact Jacobian, argument shifted to second order) reproduces
  the zero-shift c_+(K1) difference (1.125e-8 against 1.038e-8) and halves the rms
  difference of Lambda h (7.7e-8 to 3.4e-8). The second-order expansion in that displacement
  splits into Q(d) = 4.16e-8 and cross terms -3.04e-8, of which -3.60e-8 come from the
  homogeneous traceless part of h, h0 = diag(9.04e-5, 9.04e-5, -1.81e-4) (the Bianchi-I-like
  anisotropy of the box, section 2 of scope/SCOPE.md), which no periodic xi removes and which
  G omitted.
- Fix: G_tot = G + Lambda[M^T A + A M - (2/3)(tr M) A + (xi . grad) A], A = Lambda h + h0
  (`fslib/gauge.py`, gauge_piece_total; new test with a homogeneous anisotropy and TT waves:
  G alone leaves second order, G_tot third order; 6 tests pass). With G_tot the K1
  difference at tau = 1.0 and 1.9 falls from 6.1e-9 and 1.04e-8 to 7.3e-10 and -8.7e-10;
  at tau = 0.5, where the gauge pieces are below the other differences, it goes from -4.8e-10
  to -2.2e-9.
So the prediction P6 as written for G is refuted on early 32^3 data, by a missing term in my
formula, not by the gauge hypothesis; the T0 test had no homogeneous part and could not see
it.

## P6' (revised P6, written before the registered scan analysis)

With G_tot in place of G: P6(c) holds on the full runs at 32^3 (and 64^3 when they exist):
wherever |raw difference| > 1e-3 |s|, the corrected difference is below 30 percent of the
raw one (median over those dumps), up to a = 20; later (nonlinear stage) it may fail.
P5 is re-stated with G_tot: |G_tot(K1)| below 5 percent of c_+ for a <= 20.
P7c (rerun of the cosmology dumps with G_tot): the cross terms are negligible there
(h0 and Lambda h are far below the non-TT part): rms G_tot within 10 percent of rms G at all
dumps; the conclusion of P7 unchanged.

## Outcome of P7c, run B-20261115-171804-42e975b (`late_rise.png` replaced by this run's figure, looked at)

CONFIRMED. With the cross terms the spatial-gauge piece changes by at most 0.8 percent in rms
at any dump (G_tot 2.045e-10 against G 2.058e-10 at a = 1001, quadratic cloud; 2.217e-10
against 2.231e-10, cubic); the homogeneous traceless part is h0 = 1.8e-6 there, the non-TT
part 3.6e-5. rms(Lambda h - G_tot) = 2.495e-9 and 4.315e-9 at a = 1001: the P7 numbers and
reading stand. `results/late_rise_summary.json` is now this run's (spectra dropped).

## Outcomes of P1-P6 at 64^3 (cards)

Runs: card batches B-20261115-164059-d802e82 (eps = 0, 0.3, 0.1; 0.25 card-hours, 5 min per
run, 12 GB per run) and B-20261115-165353-b592d43 (eps = 1 zero shift and Gamma driver;
0.17 card-hours); analyses B-20261115-174722-ba1048d and B-20261115-180834-c77a132 (217
single-precision and 23 double-precision dumps per case, no errors); figures and
`scan_summary.json`: run B-20261115-181552-8640a38 (an earlier plot run,
B-20261115-181359-eaae093, had wrong labels and plotted the wrong Weyl component; superseded).
All four figures looked at (`figs/scan_*.png`).

P1 (null): REFUTED AS WORDED, the null itself holds at round-off. The largest TT amplitude
of h is at most 2.1e-16 (double) and 2.8e-16 (single) at every dump to a = 140, and of tilde
A at most 1.1e-16 (double), i.e. at the round-off of metric components of order one; no
growth through shell crossing. Relative to the rms traceless part, which is small early
(7e-5 at a = 1.6), the ratio exceeds 1e-12 at the first dumps (h: 2.3e-12 single, 1.7e-12
double at tau = 0.5-1.0; tilde A up to 2.6e-10 in single precision, 4.2e-12 in double) and
falls to 1e-14 (h) and 5e-13 (A, double) later. My criterion was normalized to the wrong
quantity; the meaningful bound is absolute, ~1e-16 of the metric. Lambda h independent of z
to <= 3.3e-14 (double dumps; GPU atomics). The magnetic Weyl part of the null is 3.9e-13
(finite-difference round-off of K ~ 1).

P2 (amplitude): CONFIRMED. |c_+/(s g) - 1| <= 0.22 percent (eps = 0.1 and 0.3) and 0.44
percent (eps = 1) for 2 <= a <= 10, at K1 and with the opposite sign at K2; the junk
oscillation (period 2.83 in tau, envelope ~ 1/a) is followed through four periods with no
visible phase error (`figs/scan_kk0.png`). Later the strain departs from the second-order
value: +1.1 to +2.3 percent at a = 20, +6 to +11 at a = 40, +15 to +30 at a = 60, and it
grows in the nonlinear stage to 1.6 to 2.5 times s at a = 100-140 (eps = 1 peaks at a ~ 95,
c_+/s = 2.5).

P3 (linearity): CONFIRMED. c_+/eps for eps = 0.3 and 0.1 differ by at most 0.05 percent for
a <= 10 (eps = 1 against 0.1: 0.21 percent), and the 0.1/0.3 pair stays closer than the
pair with eps = 1 later (0.1 against 1.1 percent at a = 20, 0.9 against 14 at a = 60), as
predicted for corrections in eps^2.

P4 (mode content): REFUTED for 10 < a <= 20. The four box modes carry 99 percent of the TT
mean square at a <= 5, 93-96 percent at a = 10, but only 84 (eps = 0.1), 83 (0.3) and 74
(eps = 1) percent at a = 20, and 17-25 percent at a = 100-140: other modes grow earlier than
my fourth-order estimate allowed. z-independence: confirmed (above).

P5 (gauge piece in the zero-shift gauge): CONFIRMED with G_tot. |G_tot(K1)/c_+| <= 0.55
(eps = 0.1), 0.60 (0.3), 1.1 (eps = 1) percent for a <= 20; 1.6-4.0 percent at a = 40, up
to 11 percent at a = 80 (eps = 1). The rms non-TT part grows as a (1e-3 at a = 10, 1.3e-2
to 2.6e-2 at a = 140). The quadratic piece alone would be 3.5 to 7 percent at a = 20 and is
mostly cancelled by the cross terms with h0 (see the 32^3 development check).

P6 (second gauge, eps = 1) with G_tot (P6'):
(a) CONFIRMED: the Gamma-driver run reaches a = 140 with finite fields (rc = 0, 1404 cycles,
same step sequence), the first passing run of a shift condition in an expanding box with
particles here (cf. core's note that none existed, tracks/core/outbox/20261115T1510Z__to-B-emd-gw__newton-and-cosmo-findings.md item 3).
(b) CONFIRMED: rms non-TT part 1.6e-4 to 8.8e-4 against 2.5e-3 to 2.6e-2 in the zero-shift
run for a >= 10 (15 to 40 times smaller).
(c) CONFIRMED: the raw difference of c_+(K1) between the gauges is 0.12, 0.36, 1.5, 4.9, 11.5
percent of |s| at a = 5, 10, 20, 40, 60; after G_tot it is 0.002, 0.008, 0.03, 0.3, 1.2
percent (median ratio corrected/raw 0.084 over the 89 percent of dumps where the raw
difference exceeds 1e-3 |s|). It fails only around a ~ 80-110 (shell crossing), where the
raw difference passes through zero. With G alone (no cross terms) the "corrected"
difference is 5 times the raw one (median): the cross terms with the homogeneous anisotropy
are essential.
(d) CONFIRMED for a <= 64 away from the zero crossings of B: the x amplitude of the magnetic
Weyl part at K1 differs between the gauges by 5e-5 to 4e-3 of itself up to a = 36 and by
3e-3 to 6e-3 up to a = 64 (exceptions a = 6.3 and 42, where B passes through zero), against
1.6e-4 to 8.6e-2 for raw Lambda h; after a ~ 70 both differ by 10 percent or more.

Reading [JUDGEMENT]: the gauge question of the first source is settled to the order that
matters here: the zero-shift flat TT strain differs from the spatially transverse one by the
computed G_tot (< 1.1 percent before a = 20, ~10 percent near shell crossing), the second gauge
confirms that piece quantitatively, and the gauge-invariant (at this order) magnetic Weyl
part agrees between the gauges where the metric does not. The growth of c_+ after a ~ 20
(to 2.5 s) is present in both gauges and in B: it is not a gauge effect; whether it is
converged is P8 (32^3 against 64^3).

Not predicted, recorded (same analysis runs, double-precision dumps): the TT part of the
scan is quasi-static throughout: rho_kin/rho_grad = 0.04 at a = 4 and <= 0.01 from a = 12 to
140 (eps = 1 and 0.1), while rho_GW/rho_bar (kinetic plus gradient, G = 1) grows from
2.3e-9 (a = 4) to 3.5e-6 (a = 90-121) for eps = 1 and from 2.3e-11 to 8.8e-9 for eps = 0.1.
So what grows after shell crossing is the near-field strain of the box modes, not radiation;
a radiated signal would show rho_kin ~ rho_grad. The null has rho_GW/rho_bar <= 7e-27.

Check of the single-precision dumps (same analysis runs, bin and rst written at the same
cycle, 22 common dumps per case): c_+(K1) agrees to 4.1e-5 (eps = 1) and 3.2e-4 (eps = 0.1)
relative, G_tot(K1) to 5e-7 and 2e-6 of c_+. The time series from the bin dumps are
therefore good to well below the effects discussed above.

## Outcomes at 32^3 (processors) and P8

Runs: initial data B-20261115-165357-37d0477 (P0 at 32^3: Hamiltonian residuals 7e-13 to
1.2e-11, momentum <= 1e-16); processor scan B-20261115-165525-f7c2004 (five serial runs,
1.8 h, 7.5 s per cycle, all rc = 0; the Gamma-driver case also reaches a = 140); analysis
B-20261115-184650-2d155b6; figures and summary B-20261115-184817-aefdbbc
(`results/scan_summary_32.json`, `figs/scan_kk0_32.png`, `figs/scan_secondgauge_32.png`,
looked at); comparison B-20261115-184814-fe015de (`figs/res_compare.png`, looked at).

At 32^3 the outcomes of P1-P6 repeat those at 64^3: P2 0.20, 0.19, 0.38 percent (eps = 0.1,
0.3, 1; a = 2-10); P3 0.07 percent; P4 refuted the same way (box share 0.84, 0.83, 0.74 at
a = 20); P5 |G_tot/c_+| <= 1.1 percent for a <= 20; P6 median corrected/raw 0.093 (quadratic
piece alone 5.3); P1 absolute TT amplitudes at round-off, relative ratio above 1e-12 only at
the first dumps (h 2.2e-12 single, 3.5e-13 double).

P8: CONFIRMED, and more. c_+(K1) at 32^3 and 64^3 agree to <= 0.06 percent at a = 5-40 in
all four cases (largest |difference| for a <= 20: 0.09 percent for eps = 1 and the Gamma
driver; 0.45 and 0.62 percent for eps = 0.1 and 0.3, at the first dumps where c_+ is
small), 0.05-0.2 percent at a = 60, 0.4-0.5 percent at a = 80 (zero shift; -1.9 percent
Gamma driver) and within 3.2 percent at a = 100; the largest excursions, 5-7 percent, are
at a = 90-130 for eps = 1 where c_+ oscillates fast. The rms non-TT part agrees to 3e-4
(a <= 40) and 0.3 percent at a = 100 (2 percent in the Gamma-driver run). So the growth of the box-mode strain to 2-2.5 s
after shell crossing is independent of the mesh at these two resolutions (same particle
loading, two per cell and direction) [JUDGEMENT: two meshes and one loading are not a
convergence study; particle number and the 128^3 mesh are the missing legs].

# Second round (wave 2b, resumed 2026-11-19)

Task: next action 2 of `stage/REVIEW-wave2.md` and `HANDOFF.md`: the jittered-lattice null,
convergence in particle number (1, 8, 27 particles per cell) and in mesh (128 cells), and
delta = 0.0025 to widen the window of the second-order formula. At most 1.5 card-hours.
State found at the start (06:02 local): worktree clean, merged with main (0016 read); no run
of this round existed (sacct since 2026-11-15 lists no B job after 4463; no B-2026111[6-9]
directory under scratch); the wave-2 package (P0-P10, README "State") is complete.

## Set-up of the second round (written before any run of this round)

Executables. Card runs use core's tested branch executable
`scratch/core/exe/core_requests-b/athena_gpu` (decision 0013, scouting; READY: built from
9c92f68, card test T4 passed, "everything not named behaves as release core-v0.3"), because
it adds `double_precision = true` to bin outputs: `inputs/conv.athinput` writes the Z4c
variables in single precision every 0.1 (as the scan), in double precision every 1.0 (bin,
id z4cd; in place of restart files with particles, which would be 1.3 GB each at 27
particles per cell) and restart files every 5.0. Physics and numerics are those of
`inputs/crossed.athinput` (diff: the output blocks only). `fslib/binread.py` reads both
precisions (tests/test_binread.py: 2 tests; on a real single-precision dump of run
B-20261115-165353-b592d43 it returns the arrays of gw_diag's reader bit for bit, checked by
hand, not registered); `scripts/analyze_scan.py` analyses the double-precision dumps as kind
"dbin" (Weyl E, B included, as for the restart files).

Initial data. Convergence and small amplitude with `cosmo/ic/make_east.py` (the tool of the
scan; `scripts/build_ic2.sh`); the jittered null with core's `problems/cosmo/make_waves.py`
at commit 7db34a5 of core/requests-b (not on main; `scripts/build_ic_jitter.sh` extracts it
with git archive into the run directory and runs it from there), ratios (1, 0, 0),
delta = 0.01, 64^3, 2 per cell and direction, jitter A cells along y and z, seed 7 for every
A (the deviates are the same, so the noise displacement is exactly proportional to A).

Cases (eps = 1 for convergence: the largest late growth, c_+/s up to 2.55, and the largest
32/64 differences of P8):

| name | delta | eps | mesh | per cell | role |
|---|---|---|---|---|---|
| e1_p1_n64 | 0.01 | 1 | 64^3 | 1 | particle number |
| (cw_eps1 of B-20261115-165353-b592d43) | 0.01 | 1 | 64^3 | 8 | baseline (wave 2) |
| e1_rep | 0.01 | 1 | 64^3 | 8 | rerun of the baseline with this executable: run-to-run floor of the card (atomic deposition) |
| e1_p3_n64 | 0.01 | 1 | 64^3 | 27 | particle number |
| e1_p1_n128 | 0.01 | 1 | 128^3 | 1 | mesh (same particles as the baseline: 2,097,152) |
| d0025_e1, d0025_e0p3 | 0.0025 | 1, 0.3 | 64^3 | 8 | small amplitude, to a = 140 |
| jit0p3, jit0p1 | 0.01 | 0 | 64^3 | 8 | jittered null, A = 0.3, 0.1 cells |
| jit0 | 0.01 | 0 | 64^3 | 8 | initial data only: make_waves against make_east |

Not run, by cost [JUDGEMENT from timings]: 128^3 at 8 per cell (16.8M particles). The
wave-2 card runs took 295 s for 1404 cycles at 64^3 with 2.1M particles (log of
B-20261115-164059-d802e82/cw_eps0p1), the wave-1 run `runs/cosmo/east_d0.01_n128_tsc` 1302 s
for 2773 cycles at 128^3 with 2.1M particles; so ~0.18 s per cycle for 2.1M particles and
~0.26 s per cycle for the 128^3 mesh, and 128^3 at 8 per cell would take ~2808 x 1.7 s =
80 min (1.3 card-hours, longer than one job). Estimates of this round: 2 min (1 per cell),
15-17 min (27 per cell), 25 min (128^3), 5 min each for the others; about 1.1 card-hours.

Reference values. s = -(5/6) phi_x phi_y scales as delta^2: -3.0797e-5 eps at delta = 0.01
(run B-20261115-164157-40b9f6d), so -1.9248e-6 eps at delta = 0.0025.

## Predictions of the second round (written before the initial data were made)

P11 (jittered null). (a) The largest TT amplitude is above 1e-12 at every dump after the
first (the plane-symmetric null sits at 2.8e-16): the run measures the TT response to the
noise. (b) At the box modes K1, K2 the noise enters mainly through the cross term of the x
wave with the (0, +-k, 0) Fourier component of the noise potential, i.e. like a small y wave
of random phase. Order of magnitude: the jitter's displacement has Fourier amplitude
A h/sqrt(3 N_p) per mode, a density contrast 2 k A h/sqrt(3 N_p) = 2.3e-5 at A = 0.3
(N_p = 2,097,152, h = 1/16), an equivalent eps_n ~ 2.3e-3, and with the potential of a mode
without peculiar velocity (3/5 of its initial value once a^(-5/2) has decayed) |c(K1)| ~
3.08e-5 x 2.3e-3 x 0.6 ~ 4e-8, within a factor 3 (the relativistic dictionary at the box
scale, 1 + 3 (H/k)^2 = 2.2, may raise it). A sharp version is computed from the initial
data before the card run (P11b', below, after the initial data exist): the second-order
formula with Phi_x and the measured (0, +-k, 0) component of Psi = (1 - psi^4)/2, times a
response g_n(tau) to the source f(tau) = 3/5 + (2/5) a^(-5/2); measured and predicted
complex amplitudes at K1 and K2 agree within 40 percent in modulus and 0.5 rad in phase for
3 <= a <= 20. (c) Linearity: c(K1) at A = 0.3 over c(K1) at A = 0.1 is 3.0 within 5 percent for
a <= 20. (d) The rms TT of all modes sits at the grid scale; its ratio between A = 0.3 and
0.1 lies between 3 (cross term with the x wave) and 9 (noise times noise), below 4 for
a <= 10 by the estimate above (the cross term is ten times the noise-noise term at the grid
scale). (e) Through shell crossing of the x wave (a = 80-140) |c(K1)| of the null at A = 0.3
stays below 10 percent of |c(K1)| of the eps = 0.1 scan run at the same a. Refuted by any of
(a)-(e) failing; (b) failing in modulus by more than a factor 3 would mean the noise couples
to the box mode other than through the cross term.

P12 (particle number, eps = 1, 64^3, 1, 8, 27 per cell). (a) For a <= 40, |c_+(K1)/c_+(27) - 1|
<= 1e-3 for 1 and 8 per cell. (b) For 80 <= a <= 140 the differences fall with the number of
particles: max |c(8)/c(27) - 1| < max |c(1)/c(27) - 1|, and |c(8)/c(27) - 1| <= 3 percent for
a <= 100. (c) The rerun of the baseline (e1_rep) agrees with the wave-2 run to 1e-4 for
a <= 40 and 1e-2 to a = 140: this is the floor below which differences between runs mean
nothing. Refuted by (a), (b) or (c) failing; (b) failing means no convergence in particle
number after shell crossing at these loadings.

P13 (mesh, eps = 1). (a) For a <= 40 the 128^3 run (1 per cell) agrees with the 64^3 runs
(1 and 8 per cell) to 1e-3. (b) For 80 <= a <= 140 the rms over dumps of c(128^3, 1)/c(64^3,
8) - 1 (same particles, finer mesh) is below that of c(64^3, 8)/c(32^3, 8) - 1 (P8 runs).
Refuted if it is larger: no convergence in the mesh after shell crossing.

P14 (delta = 0.0025, eps = 1 and 0.3, 64^3, 8 per cell, to a = 140). The relative departure
dev = c_+(K1)/(s g) - 1 is, by the journal's estimate of the order of the first correction
at (k, k, 0) [JUDGEMENT, P2: no third-order term at that wave vector], of relative order
(delta a)^2. (a) max |dev| for 2 <= a <= 10 falls by at least a factor 3 against delta = 0.01
(to <= 0.15 percent for eps = 1, <= 0.08 percent for eps = 0.3). If it does not fall, the
departure at a <= 10 is an error of the second-order model or of the numerics, independent of
delta. (b) R(a) = dev(0.01, a)/dev(0.0025, a) lies between 8 and 24 at a = 20, 30, 40 (16 for a
pure (delta a)^2 law, 4 for a third-order term). (c) dev(0.0025, 4 a) = dev(0.01, a) within
50 percent for a = 10 to 35 (the collapse is not exact: k/Hc grows as sqrt(a)). (d) The window
in which |dev| <= 0.5 percent reaches a >= 30 at delta = 0.0025 (a ~ 10 at delta = 0.01).

P15 (initial data). make_east cases: Hamiltonian residual below 1e-9 and momentum residual
below 1e-7 (P0). Jitter cases: the tool's residuals as for the plain lattice (spectral solve;
the code's own residual is about one percent of the source term, core's REQUESTS_B.md
section 5 [BACKGROUND]). Parity (jit0 against make_east eps0 of run
B-20261115-161656-03d75e1): positions equal to 1e-13, psi of fields.bin to 1e-12. Refuted if
larger (then the null is not built like the scan).

## Initial data of the second round (outcome of P15, partly)

Runs B-20261119-141216-9c98929 (make_waves at 7db34a5: jit0p3, jit0p1, jit0) and
B-20261119-141249-2af0df8 (make_east: d0025_e1, d0025_e0p3); logs `<case>.log` there.
- delta = 0.0025: CONFIRMED. Hamiltonian residual 2.2e-11, 9.9e-12; momentum 6.0e-17,
  2.3e-16; largest displacement 0.025 cells; max |Ahat| 2.3e-5, 9.7e-6.
- Jitter: Hamiltonian residual of the tool 3.7e-11 (A = 0.3), 4.5e-12 (0.1): as predicted.
  Momentum residual REFUTED my "as for the plain lattice": 7.6e-4 (A = 0.3) and 2.8e-4 (0.1)
  against 3.1e-17 without jitter (same tool, jit0). It grows with A (ratio 2.7 for a ratio 3 in
  A). The particle momenta u_x(x) carry the x wave and the jittered positions modulate the
  deposited momentum density in y and z; the tool's solve does not remove that part
  [JUDGEMENT on the cause: the momentum constraint is solved for the traceless curvature
  with an ansatz that cannot absorb it; not checked in the tool's code]. So the jittered
  null starts with a momentum-constraint violation of that size, in addition to the
  evolution's one per cent (core's REQUESTS_B.md section 5). Recorded; the null run goes ahead.
- Parity (run B-20261119-142727-02878d1, `parity.json`): CONFIRMED and more: make_waves without
  jitter and make_east eps0 give bit-identical particle files and field files (all
  differences 0.0). The jittered null is built exactly like the scan.
- Smoke test of `inputs/conv.athinput` on the requests-b processor executable (run
  B-20261119-142500-72b1213, 8 cycles at 32^3): the input is accepted, both bin outputs and
  restart files are written, the double-precision dump has "size of variable=8", the same
  cycle and time as the single-precision dump of the same output time, and differs from it
  by 1.2e-7 absolute (5.9e-8 relative, the rounding of float32).

## P11b' (computed from the initial data before the card run; run B-20261119-142733-932e595)

`scripts/null_prediction.py`, `null_prediction.json` and `.png` there (looked at). Validation
on the eps = 0.1 scan data: phi_x = -6.0785e-3, phi_y = -6.0798e-4 from psi, static cross term
at K1 -3.0802e-6 against s = -3.0797e-6 (0.02 percent): the extraction and the formula are
right for the crossed waves. Jittered null (complex amplitudes c - i s in the basis of
fslib.modes; static = growing-mode normalization; the run is predicted to follow cross x
g_cross + nn x g_nn, late value 0.6 cross + 0.36 nn):

| case | K | static cross | static nn | predicted at a = 5 | at a = 10 | late, modulus |
|---|---|---|---|---|---|---|
| A = 0.3 | K1 | -6.21e-8 - 4.25e-8 i | 1.28e-8 + 3.71e-8 i | -3.11e-8 - 1.23e-8 i | -3.58e-8 - 1.30e-8 i | 3.48e-8 |
| A = 0.3 | K2 | 6.69e-8 - 4.72e-8 i | 7.85e-9 - 1.18e-8 i | 4.03e-8 - 3.04e-8 i | 4.72e-8 - 3.58e-8 i | 5.39e-8 |
| A = 0.1 | K1 | -2.07e-8 - 1.40e-8 i | 1.17e-9 + 4.67e-9 i | -1.14e-8 - 6.48e-9 i | -1.32e-8 - 7.37e-9 i | 1.38e-8 |
| A = 0.1 | K2 | 2.23e-8 - 1.56e-8 i | 1.25e-9 - 1.54e-9 i | 1.30e-8 - 9.30e-9 i | 1.52e-8 - 1.09e-8 i | 1.70e-8 |

The noise potential at (0, k, 0) has amplitude 1.48e-5 at A = 0.3 (my order-of-magnitude
estimate of P11: 1.4e-5 without the relativistic factor; that factor does not appear). The
noise-noise term at K1 is half the cross term at A = 0.3 (I had estimated a tenth), so P11(c)
as written ("ratio 3.0 within 5 percent") is contradicted by this computation before the
run: the predicted ratio |c(0.3)/c(0.1)| at K1 is 2.51 at a = 5 and 2.53 late, with a phase
difference of 0.16 rad. Superseding prediction (c'): the measured K1 ratio lies within 10
percent of 2.5 for 3 <= a <= 20, and the K2 ratio near 3.2 (5.39e-8/1.70e-8). (b) as
stated: modulus within 40 percent, phase within 0.5 rad of the table for 3 <= a <= 20.
(d) rms of all TT modes, static: cross 3.54e-7, nn 1.75e-7 (A = 0.3), 1.18e-7, 2.1e-8 (A =
0.1); late 0.6 cross + 0.36 nn: 2.29e-7 and 7.22e-8, ratio 3.2. Prediction: measured rms TT
within a factor 3 of these for 3 <= a <= 20 (grid-scale modes: the code's sixth-order
differences and dissipation are not in the spectral formula), ratio between 3 and 4.
Caveat [JUDGEMENT]: the code's slicing is Newtonian only for the growing mode (P9); for a
mode without peculiar velocity the slicing condition keeps alpha + psi-part fixed at its
initial value, not Phi = Psi, so slicing-gauge pieces of the cross term are not in this
prediction; neither is the momentum-constraint violation of the initial data.

## First outcomes of batch A (job 4637, run B-20261119-142833-19edd82, still running) and P16

P12c (run-to-run floor), analyses B-20261119-155418-80d45af (e1_rep) and comparisons
B-20261119-160535-6714ac1, B-20261119-154528-9306cb1 (`conv_eps1.png` looked at): CONFIRMED
with a wide margin. The rerun of the eps = 1 baseline on the requests-b card executable
reproduces the wave-2 release run: c_+(K1) from the double-precision dumps (dbin against the
wave-2 restart files, same cycles) agrees to 9.5e-13 relative for a <= 40 and 4.7e-13 for
80 <= a <= 140; from the single-precision dumps to 1.4e-10 and 2.4e-10 (isolated flips of a
float32 rounding; most dumps identical). The atomic deposition of the card does not grow
through shell crossing at this resolution, and the two executables give the same run. Any
difference above ~1e-9 between runs of this round is physical or numerical, not noise of
the card.

P11, A = 0.3 (analysis B-20261119-160530-7bdcb45, comparison B-20261119-161523-b681b5f,
`conv_null.png` looked at; A = 0.1 not yet analysed):
- (a) CONFIRMED: largest TT mode 1.3e-7 to 6.0e-7 at every dump after the first, against
  2.2e-16 in the plane-symmetric null.
- (b') box modes CONFIRMED: |measured|/|predicted| at K1 0.93 to 1.33 (median 1.04), phase
  difference 0.12 to 0.36 rad (median 0.23) for 3 <= a <= 20; at K2 0.74 to 1.00 (median
  0.94), phase -0.08 to -0.03 rad. The second-order formula with the noise potential read from
  the initial data, the 3/5 of a mode without peculiar velocity and the noise-noise term
  predicts the spurious box-mode strain to 5-30 percent.
- (e) CONFIRMED: |c(K1)| of the null over |c(K1)| of the eps = 0.1 scan run at the same time:
  at most 1.5 percent for 2 <= a <= 20, 2.5 percent for 20-80, 3.1 percent for 80-140.
- (d) REFUTED: rms TT of all modes is 3.9e-6 at a = 2.3, 2.8e-6 at a = 6-12, 5.2e-6 at a = 140,
  12 to 20 times the second-order estimate 2.29e-7 (and 1.2e-5 at the first dump, tau = 0.1,
  a = 1.10, with rms Lambda tilde A = 1.8e-4 there although it is 2.6e-8 in the initial data).
  rho_kin/rho_grad 0.37-0.40 at tau = 0.1-0.2, 0.07 at a = 2.3, 0.01 at a = 140. So the bulk of
  the TT field appears within the first 0.1 of conformal time and is not the second-order
  response. Not foreseen.

P16 (written before scripts/null_spectrum.py ran). Hypothesis: the rms TT of the jittered null
is leakage of the grid-scale non-TT part of h through the flat projector: the evolution
builds longitudinal tensors with sixth-order differences, whose Fourier symbol d(k) is not
parallel to k near the mesh scale, so Lambda(k) of d_i d_j phi is not zero there; the error
of the symbol grows as (k h)^6. If so: (i) at least 90 percent of the TT power lies at
|k|L/2pi >= 16 (k h >= pi/2); (ii) per shell, P_TT/P_nonTT rises with k by at least 1e3 between
|k|L/2pi = 4 and 24; (iii) the per-shell ratio is nearly the same for A = 0.3 and 0.1 (within a
factor 2), since leakage is linear in the field; (iv) the plane-symmetric null has no such
leakage (all its modes lie along x, where d(k) is parallel to k). Refuted if the TT power sits
at low k or the per-shell ratio is flat in k: then the TT field is a genuine response to the
noise (or the momentum-constraint violation of the initial data) and P11(d)'s estimate misses a
first-order source.
