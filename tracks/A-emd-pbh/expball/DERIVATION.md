# Expanding dust ball: independent derivation of the initial data (A-pre-1)

Helper of A-emd-pbh, 2026-11-15. Units G = c = 1. Sign of the code (and of
`coord/INTERFACES/spherical_id_format2.md`):
K_ij = -(1/(2 alpha)) (d_t gamma_ij - D_i beta_j - D_j beta_i), so expansion has K < 0.
Every symbolic statement below is checked by a script in `sym/` (run them with
`python3 sym/<script>.py`, exit status 0 when all checks pass); every number carries a run
id of `tracks/A-emd-pbh/runs/` (copies in `manifests/`). Labels: [VERIFIED] = checked here
by a script or a run (not a literature claim); [BACKGROUND] = standard result not checked
here against a source; [JUDGEMENT] = a choice of this package.

Contents: 1 spacetime, 2 the slice, 3 constraints and conformal form, 4 trapped and
anti-trapped spheres, 5 growing-mode data with a bound core, 6 exact evolution,
7 finite-difference check, 8 the two relations of the brief, 9 the orchestrator's item 1,
point by point.

## 1. The spacetime

**Comoving form.** Lemaitre-Tolman-Bondi dust, t the proper time of the dust, r a comoving
label:

    ds^2 = -dt^2 + R_r^2 dr^2/(1 + 2E(r)) + R(t,r)^2 dOmega^2,
    Rdot^2 = 2 m(r)/R + 2 E(r),        8 pi rho = 2 m_r/(R^2 R_r).

With Rdot^2 = 2m/R + 2E imposed (and its derivatives, Rddot = -m/R^2), every component of
G^a_b - 8 pi rho u^a u_b vanishes. [VERIFIED: `sym/sym_ltb_4d.py` part (a), 6 checks.]
m is the Misner-Sharp mass (below, g^ab d_a R d_b R = 1 - 2m/R) and E the bound energy per
unit mass; both are constant along the dust as long as shells do not cross.

**Proper-time form.** With the areal radius R as coordinate and tau = t, R_r dr = dR - v dtau
with v = Rdot:

    ds^2 = -dtau^2 + (dR - v dtau)^2/(1 + 2E) + R^2 dOmega^2,   v = +sqrt(2m/R + 2E),

where m and E are now functions of (tau, R) carried by the dust,
(d_tau + v d_R) m = (d_tau + v d_R) E = 0. Directly in these coordinates,
G^a_b = 8 pi rho u^a u_b with u^a = (1, v, 0, 0) and rho = d_R m/(4 pi R^2) (at fixed tau).
[VERIFIED: `sym_ltb_4d.py` parts (b) and (d); the advection rules are substituted for every
tau-derivative of m and E up to second order.]

**Marginally bound special cases** (E = 0): v = sqrt(2M/R) is vacuum, Schwarzschild in the
outgoing (time-reversed) Painleve-Gullstrand form; v = H(tau) R with dH/dtau = -(3/2) H^2 is
spatially flat FLRW dust with 8 pi rho = 3 H^2, and a ball of radius R_b has
2M/R_b = (H R_b)^2. [VERIFIED: `sym_ltb_4d.py` part (c), 11 checks.] Both pieces share the
time function tau (proper time of comoving dust inside, of marginally bound radial
geodesics outside), so the slice tau = const is one smooth spacelike surface through the
ball and its exterior.

## 2. The slice tau = const

From the proper-time form: lapse alpha = 1 (g^{tau tau} = -1), shift beta^R = -v
(beta^i = alpha^2 g^{tau i}), 3-metric

    gamma = dR^2/(1 + 2E(R)) + R^2 dOmega^2.

The dust four-velocity u^a = (1, v) has u_tau = -1 and u_R = 0: the dust is at rest with
respect to the normal observers, so u_i = 0 for every particle, S_i = 0 and the energy
density measured by the normal observers equals the rest-mass density rho.
[VERIFIED: `sym_ltb_4d.py` (b), lapse, shift and u_a checks.]

**Extrinsic curvature.** Evaluating the code's definition with alpha = 1, beta^R = -v and
gamma_RR = 1/(1 + 2E), where at fixed R the slice-to-slice change of gamma_RR is
d_tau gamma_RR = 2 v E_R/(1 + 2E)^2 (E is carried by the dust, so it changes at fixed R):

    K^R_R = KL = -dv/dR,      K^theta_theta = K^phi_phi = KT = -v/R,

with dv/dR the total derivative along the slice, m and E both depending on R.
[VERIFIED: `sym/sym_slice.py` part (c).] Dropping d_tau gamma_RR (treating the spatial
metric as static, as one would for E = 0) gives instead KL = -v' + v E'/(1 + 2E), which is
wrong whenever E' != 0. [VERIFIED: same script; it prints the difference
v E'/(1+2E).] In comoving coordinates the same result is immediate:
K^r_r = -d_t ln(R_r/sqrt(1+2E)) = -Rdot_r/R_r = -dv/dR at fixed t.

For the homogeneous marginally bound ball, v = H R inside: K_ij = -H gamma_ij (KL = KT = -H);
outside, v = sqrt(2M/R): KT = -v/R, KL = +v/(2R). At the surface KT is continuous and KL
jumps from -H to +H/2, together with the density. [VERIFIED: `sym_slice.py` part (d').]

## 3. Constraints and the conformally flat form

For arbitrary m(R), E(R), with KL = -dv/dR, KT = -v/R and v^2 = 2m/R + 2E:

    3R = -4 (R E)'/R^2,
    3R + K^2 - K_ij K^ij = 4 m'/R^2 = 16 pi rho        (Hamiltonian),
    D_j (K^j_i - delta^j_i K) = 0,  i.e.  dKT/dR = (KL - KT)/R   (momentum, S_i = 0).

Both hold identically (no condition on m or E). [VERIFIED: `sym_slice.py` part (d), 5 checks;
numerically for the profiles of section 5 by `tests/test_expball.py::test_radial_constraints`,
residuals below 1e-9 of 6H^2.] The homogeneous ball gives 6H^2 = 16 pi rho (the Friedmann
equation) and the vacuum exterior gives zero for both constraints. [VERIFIED: (d').]

**Conformally flat form.** Every spherically symmetric 3-metric is conformally flat:
gamma = psi^4 (drbar^2 + rbar^2 dOmega^2) with

    R = psi^2 rbar,      d ln rbar/dR = 1/(R sqrt(1 + 2E)),
    ln(R/rbar) = int_R^{R_2} (1/sqrt(1 + 2E) - 1) dR'/R',

normalised so that rbar = R where E = 0 outwards (beyond R_2 below; then psi = 1 there).
[VERIFIED: `sym_slice.py` part (e), metric identities.] For a homogeneous closed core,
E = -a^2 R^2/2, the integral is ln[(1 + sqrt(1 - a^2 R^2))/(1 + sqrt(1 - a^2 R_1^2))]
[VERIFIED to 1e-14 by `tests/test_expball.py::test_conformal_map_tophat_closed_form`].
The shift in the isotropic coordinate: betar = beta^rbar = -v/(psi^2 sqrt(1 + 2E)).

**Cartesian assembly of table format 2.** With gamma_ij = psi^4 delta_ij and
K_ij = psi^4 [KT delta_ij + (KL - KT) n_i n_j], the Cartesian Hamiltonian and momentum
constraints computed from the full metric (Christoffel symbols and Ricci tensor) equal

    H = -8 psi^-5 (psi'' + 2 psi'/rbar) + 4 KL KT + 2 KT^2 - 16 pi rho,
    M_i = n_i { 2 [(1/rbar + 2 psi'/psi)(KL - KT) - KT'] },     ' = d/drbar,

and K^i_j n^j = KL n^i, trace K = KL + 2 KT. [VERIFIED: `sym_slice.py` part (e) at two
generic directions (2,3,6)/7 and (1,4,8)/9 with psi, KL, KT given by their Taylor
coefficients, 16 checks.] The radial momentum form is dKT/dR = (KL - KT)/R rewritten with
R = psi^2 rbar. So the interface's assembly is the right one.

## 4. Trapped and anti-trapped spheres

For the round sphere of areal radius R in the slice, with unit radial normal s
(s^R = sqrt(1 + 2E)) and the code's sign, the null expansions are

    theta_pm = pm D_i s^i - K + K_ij s^i s^j = (2/R) (v pm sqrt(1 + 2E)),
    theta_+ theta_- = (4/R^2) (2m/R - 1),       g^ab d_a R d_b R = 1 - 2m/R.

[VERIFIED: `sym_slice.py` part (f), 5 checks; the sign convention is checked on flat FLRW,
where theta_- = 2(HR - 1)/R changes sign at the Hubble radius.] With v > 0 a sphere is
anti-trapped (both expansions positive) iff 2m/R > 1, whatever E is. Hence:
**the slice contains no trapped or anti-trapped round sphere iff max_R 2m(R)/R < 1.**
For the homogeneous marginally bound ball, 2m/R = (H R)^2 inside and 2M/R decreasing
outside, so the condition is H R_b < 1. [VERIFIED, as above.] That non-round
(anti-)trapped surfaces are excluded too when no round one exists is the usual statement
for spherically symmetric slices [BACKGROUND; not checked here].

## 5. Data with a bound core: simultaneous bang time

A marginally bound ball expands for ever; turnaround and collapse need E < 0 somewhere.
Two of the three free functions of LTB data are fixed here by a choice [JUDGEMENT]:

1. the label is the areal radius on the slice, and the slice is t = t_i of the dust;
2. the bang time is the same for every shell, t_B = 0, so t_i = 2/(3H) is the age of every
   shell. In LTB the decaying mode is the bang-time inhomogeneity, so these data are pure
   growing mode [BACKGROUND]; consistent with this, the linear limits below reproduce the
   growing mode of Einstein-de Sitter. [VERIFIED: `sym/sym_growing.py` part (v).]

The remaining free function is Delta(R), the mean density contrast inside R on the slice:

    m(R) = (H^2/2) R^3 (1 + Delta(R)).

The age of a shell is t(R; m, E) = int_0^R dR'/v = (2/3) R^(3/2) (2m)^(-1/2) F(y),
F = 2F1(1/2, 3/2; 5/2; y), y = -E R/m [VERIFIED: `sym_growing.py` (i), against quadrature to
30 digits and a series to order 6; equals the cycloid for E < 0, (ii)]. Setting t = 2/(3H):

    F(y) = sqrt(1 + Delta),     E = -y m/R,     v = H R sqrt((1 + Delta)(1 - y)),
    rho = rho_b (1 + Delta + R Delta'/3),       rho_b = 3H^2/(8 pi),

[VERIFIED: (iv)], with linear limits y = (5/3) Delta - (40/21) Delta^2 + ...,
v/(HR) = 1 - Delta/3 + ... (the growing-mode velocity), and the classical collapse value
Delta_i (t_c/t_i)^(2/3) -> (3/20)(12 pi)^(2/3) = 1.68647 as Delta_i -> 0 [VERIFIED: (v);
the value is the textbook top-hat threshold, BACKGROUND]. The shell is still expanding iff
Delta < F(1)^2 - 1 = 9 pi^2/16 - 1 = 4.55 (F(1) = 3 pi/4, (iii)).

Consequences used below:
- **E is continuous wherever Delta is**, because E is fixed by (R, m) through the age. A
  top-hat in density therefore has continuous E and v; only E', v' and KL jump with rho.
  A top-hat in E itself (E jumping at fixed R) would make v jump: KL would contain a delta
  function (a thin shell of extrinsic curvature) and the shells would separate at once.
  So "top-hat" can only mean a top-hat in density (or in Delta).
- **Compensation.** If Delta = 0 for R >= R_2 (equal mass to an Einstein-de Sitter ball of
  the same radius), then E = 0, psi = 1 and rbar = R from R_2 outwards, the envelope is
  exactly Einstein-de Sitter and the exterior exactly the outgoing Painleve-Gullstrand
  slice of Schwarzschild with the ball's mass M = (H^2/2) R_b^3. This is what makes the
  `exterior = pg` continuation of table format 2 exact. An uncompensated core (E = -dM/R in
  the envelope and beyond) would make psi = 1 + dM/(2 rbar) outside, KT proportional to
  R^-3/2 with R != rbar, and the pg continuation inexact.

Profiles implemented (`expball/model.py`):

| name | Delta(R) | smoothness | role |
|---|---|---|---|
| `Flat` | 0 | sharp edge at R_b | homogeneous marginally bound ball (data set 1) |
| `TopHat(delta_c, R1, R2)` | delta_c in R < R1, delta_c R1^3 (R2^3 - R^3)/((R2^3 - R1^3) R^3) in R1 < R < R2 | rho, KL jump at R1, R2; psi in C^1 | classic compensated top-hat: homogeneous closed core, uniform underdense shell 1 + delta_u, delta_u = -delta_c R1^3/(R2^3 - R1^3) |
| `SmoothTopHat(delta_c, R1, R2)` | delta_c (1 - S((R - R1)/(R2 - R1))), S the C-infinity step e^{-1/u}/(e^{-1/u} + e^{-1/(1-u)}) | C-infinity inside the ball | homogeneous closed core joined smoothly to the envelope (data set 2) |
| `Smooth(delta_c, R2, n, p)` | delta_c (1 - (R/R2)^{2p})^n | C^{n-1} at R2 | kept for tests only (see below) |
| edge taper `edge_width = w` | rho = rho_b T((R - R_b)/w), T a C^4 smoothstep, E = 0 | removes the KL jump at R_b | option, not used by the data sets |

The `Smooth` profile was tried first for data set 2 and rejected [JUDGEMENT]: its centre
crunches first and the first trapped sphere appears at the centre at the moment of the
central crunch with zero mass (scouting call, recorded in JOURNAL.md, P3); with a
homogeneous core all core shells crunch together and the core edge is trapped before, as
in Oppenheimer-Snyder (section 6). With the taper the envelope keeps E = 0 but its bang
time is no longer uniform: the age (2/3) sqrt(R^3/(2m)) grows outward because m/R^3 falls,
so t_B' < 0, and with R = (9m/2)^(1/3) (t - t_B)^(2/3),
R_r = (9/2)^(1/3) [m' (t - t_B)^(2/3)/(3 m^(2/3)) - (2/3) m^(1/3) t_B' (t - t_B)^(-1/3)] > 0
for all t > t_B: no shell crossing [derived here; not checked by a script].

Density positivity (local contrast > -1) is checked by each profile; for data set 2,
delta_c = 1, R1 = 0.3 R_b, R2 = 0.75 R_b, the minimum density in the compensating shell is
0.4367 rho_b [VERIFIED: run A-emd-pbh-20261115-121643-6bfb707, `slice_exact.json`].

## 6. Exact evolution of the shells

Each shell keeps (m, E) until shells cross and obeys (dR/dtau)^2 = 2m/R + 2E. With
t = age_i + tau the time since its own bang:

    E < 0:  R = A (1 - cos eta),  t = T0 (eta - sin eta),  A = m/(-2E), T0 = m/(-2E)^(3/2),
    E = 0:  R = (9m/2)^(1/3) t^(2/3),
    E > 0:  R = A (cosh eta - 1), t = T0 (sinh eta - eta), A = m/(2E), T0 = m/(2E)^(3/2).

Turnaround t_ta = pi T0 at R_max = m/(-E); crunch t_c = 2 pi T0. The shell's sphere is
marginally trapped on the collapsing branch where R = 2m, i.e. cos(eta_AH) = 1 + 4E
[VERIFIED: `sym_growing.py` (vi)], t_AH = 2 t_ta - (4/3) m F(-2E). With the parametrisation
of section 5, t_ta/t_i = 3 pi/(4 sqrt(1 + Delta) y^(3/2)) [VERIFIED: (iv)], so a
homogeneous core (constant Delta) turns around and crunches as a whole.

These are proper times along dust world lines between the initial slice and events
defined by round spheres (turnaround: dR/dtau = 0; marginal trapping: R = 2m; crunch:
R = 0); they do not depend on the slicing, so they can be compared with the evolution
code through the proper time of its particles, which uses another gauge (1+log lapse,
Gamma-driver shift). The apparent horizon that a horizon finder reports on a slice is the
outermost marginally trapped sphere of that slice; when it first appears depends on the
slicing, but the event "shell R_i becomes trapped" does not. [JUDGEMENT on how to compare.]

Shell crossing: with simultaneous bang time and Delta decreasing outward, crunch times
increase outward. The code checks R(tau) monotonic in R_i on a grid of 400 to 2000 shells
up to the first crunch and finds none for every data set (section 7, P5, P7).

Code: `expball/exact.py` (`Shells`: R(tau), dR/dtau, tau_ta, tau_c, tau_AH, first horizon,
shell-crossing check). Tests: R(0) = R_i, dR/dtau against differences, R(tau_ta) = R_max,
R(tau_AH) = 2m, cycloid against hypergeometric form, flat ball
R = R_i (1 + 3 H tau/2)^(2/3) [VERIFIED: `tests/test_expball.py::test_shell_evolution`].

## 7. Finite-difference check of the constraints (G1)

Residuals on cell-centred Cartesian meshes (octant [0, 1.25 R_b]^3, N^3 cells), centred
differences of order p = 2 and 4, the conformally flat forms of section 3 (and, as a
cross-check at low N, the general-metric form with Christoffel symbols by finite
differences: `mesh.residuals_general`). Divided by 6H^2 = 16 pi rho_b. Run
A-emd-pbh-20261115-121654-6bfb707, repeated as -122121-aa1c84d with the same numbers
(N = 32 ... 256; JOURNAL.md P4 for all numbers);
H R_b = 0.5, M = 1, core delta_c = 1, R1 = 0.3 R_b, R2 = 0.75 R_b. Orders of the L2 norms for
the last two pairs of N, in the region farther than 0.1 R_b from every non-smooth radius:

| model | H, p = 2 | M, p = 2 | H, p = 4 | M, p = 4 | all cells |
|---|---|---|---|---|---|
| flat (sharp edge) | 0 (1e-15) | 2.00, 2.00 | round-off ~ h^-2 (4.7e-11 at N = 256) | 4.00, 4.00 | M: L1 order 0, L2 -0.5, Linf -1 (KL jump at R_b) |
| flat, C^4 edge taper | 0 | 1.96, 1.99 | round-off | 3.77, 3.90 | same orders in all cells |
| top-hat | 2.00, 2.00 | 2.00, 2.00 | 4.01, 4.00 | 4.01, 4.00 | H: L1 1, L2 1/2; M: no convergence (jumps at R1, R2, R_b) |
| smoothed top-hat | 1.98, 2.00 | 1.92, 1.98 | 3.75, 3.92 | 3.43, 3.79 | H as smooth region; M: edge as flat |

The flat-ball Hamiltonian residual is round-off: the order-4 second-derivative weights sum
to -6.94e-17 in double precision, which with 1/h^2 reproduces the measured values to three
digits. The smoothed top-hat approaches order 4 from below (its C-infinity step has large
high derivatives); with N = 512 (run A-emd-pbh-20261115-122117-aa1c84d) the last pair gives
3.98 (H) and 3.94 (M) at p = 4, 2.00 and 1.99 at p = 2. The jump of KL at a
density jump gives an O(jump/h) momentum residual in a one-cell band, because d_j K^j_i and
d_i K do not cancel discretely for a surface oblique to the axes; this is a property of
sampling discontinuous data on a mesh, and the C^4 taper removes it (all-cells order 3.9).

The table (four-point Lagrange in rbar, as the code's format-1 tables) converges at order 4
in its spacing; at the spacing written (rbar_m/4000) the residuals of the table fields equal
those of the exact fields to 6e-7 relative at N = 128. Particle noise of the Hamiltonian
residual with the linear (CIC) cloud: run A-emd-pbh-20261115-121659-6bfb707, README.

## 8. The two relations of the brief marked "derivation to be checked" (S1, lines 355-356)

(1) "In the flat (marginally bound) case the Friedmann equation gives 2GM/(Rc^2) = (HR/c)^2,
so as long as the areal radius of the ball is smaller than the Hubble radius there is no
anti-trapped surface on the initial slice."
**Correct** [VERIFIED: sections 1 and 4]: 2M/R_b = (H R_b)^2 follows from M = (4 pi/3) rho R_b^3
and 8 pi rho = 3 H^2; a round sphere is anti-trapped iff 2m/R > 1; inside 2m/R = (HR)^2
<= (H R_b)^2 and outside 2M/R < 2M/R_b. Precisions: "Hubble radius" is 1/H on the initial
slice; the statement concerns round spheres; with a bound core the condition becomes
max 2m(R)/R < 1 (E does not enter), not R_b < 1/H.

(2) "In the marginally bound case, on a slicing of Painleve-Gullstrand type the spatial
metric is flat and the lapse is 1, so the initial data are analytic; after a non-spherical
perturbation the constraints are solved once more."
**Correct for the first part** [VERIFIED: sections 1 and 2]: the slicing is the proper time
of the dust inside and the outgoing Painleve-Gullstrand time outside (the same function);
gamma_ij = delta_ij, alpha = 1, beta^i = -v n^i, K_ij = -d_(i v_j), with v = H R inside and
sqrt(2M/R) outside. Precisions: (a) "analytic" means closed form, piecewise: K_ij jumps at
the surface (KL from -H to +H/2) together with the density, which a finite-difference
code sees as an O(1/h) momentum-constraint band (section 7); (b) the exterior is the
outgoing (white-hole) form of Painleve-Gullstrand, harmless because 2M/R < 1 on the whole
exterior of the slice; (c) with a bound core the slice is curved but conformally flat
(one quadrature, section 3). The second part ("solved once more") is outside this package
[JUDGEMENT of the brief; see coord/notes/design_wave2_initial_data.md].

## 9. The orchestrator's item 1 (coord/notes/derivations_to_check.md), point by point

Agreements [VERIFIED by the scripts named above]: the proper-time metric and v; flat 3-metric,
unit lapse and beta^i = -v n^i in the marginally bound case; K_ij = -d_(i v_j), KT = -v/R,
KL = -v'; u_i = 0, S_i = 0, E = rho; K_ij = -H delta_ij and 6H^2 = 16 pi rho inside;
2M/R_b = (H R_b)^2; exterior KT = -v/R, KL = +v/(2R), both constraints zero; no anti-trapped
surface while H R_b < 1; the bound metric with (dR - v dtau)^2/(1 + 2E); conformal flatness by
one radial integration; dust at rest w.r.t. the normal observers; KT = -v/R and
**KL = -dv/dR also when E depends on R at fixed tau** (the item's open point), provided dv/dR is
the total derivative along the slice; comparison through invariants.

Disagreements and qualifications:
1. "E(r) < 0 in a core (a top-hat or a smooth profile)": a top-hat **in E** is not admissible
   (velocity jump, delta function in KL, shells separate at once). The top-hat must be in
   the density (or in Delta); with simultaneous bang time E is then continuous (section 5).
2. "Such data fit table format 2": yes, **if the core is compensated** (E = 0 at and beyond
   the last row, psi = 1 there); otherwise the `exterior = pg` continuation is not exact.
3. The anti-trapping criterion with a bound core is max 2m/R < 1 (independent of E), not
   H R_b < 1 (section 4).
4. Not in the item, needed for the table: betar = -v/(psi^2 sqrt(1 + 2E)) in the isotropic
   coordinate; alpha = 1.
5. Not in the item: the KL jump at the ball surface (and at the edges of a sharp top-hat)
   produces an O(jump/h) momentum residual on a mesh; a C^4 edge taper (option
   `edge_width`) removes it while keeping E = 0 and the exact solution.
6. Not in the item: the bang time must be chosen. Simultaneous bang time (pure growing
   mode) is used here; a density top-hat with an unperturbed Hubble flow instead (common in
   Newtonian set-ups) carries a decaying mode [BACKGROUND] and a different turnaround time.
7. The time-reversed Oppenheimer-Snyder solution named in the brief's A-pre-1 is the
   marginally bound case (the time reverse of collapse from rest at infinity); the
   Oppenheimer-Snyder test of the code (collapse from rest at finite R0, E < 0) time-reversed
   would be a ball that decelerates to rest at R0, not an expanding Einstein-de Sitter
   ball.
