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
