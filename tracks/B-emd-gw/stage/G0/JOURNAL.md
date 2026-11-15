# Journal of the verifier package (B-emd-gw, stage G0/G1 material, wave 2)

Helper: independent verifier. Read before starting: CLAUDE.md, CHARTER (to "Owners"),
brief lines 366-379, 727-745, 834-860, orch rulings after wave 1, decisions 0010-0015,
`scope/SCOPE.md` (the scoping text that names the claims), the code and scripts of the
packages. Not read before the checks were done: STATUS.md, HANDOFF.md, REVIEW.md, the
track's and the packages' JOURNAL files, stage/G0/EVIDENCE.md, stage/G0/OPEN.md, stage/G1/STATUS.md.

## 2026-11-15, entry 1: the claims chosen and the predictions (written before any check ran)

Eight claims on which the plan of `scope/SCOPE.md` and the G1 criteria of the track sheet
(brief line 741) rest. For each: what I expect, and what would refute it.

C1. Item 3: an exactly plane-symmetric collapse has no TT part at any nonzero wave
    vector; the TT projector along x keeps only (T_yy - T_zz)/2 and T_yz; rotations
    about x (E(2)) are needed, translations alone are not; the 90-degree lattice rotation
    suffices; on the torus a single global TT mode A^i_j = c Y^-3 diag(1,-1/2,-1/2)
    exists for diag(X^2,Y^2,Y^2)(x), and K projected on it is -d/dt int X/Y dx.
    Prediction: all of it holds symbolically (sympy). Refuted by: a nonzero TT component
    under the stated symmetry, a second independent symmetric TT tensor, or a divergence
    that does not vanish for f = Y^-3. Caveat I expect: the total-derivative form needs
    unit (or uniform) lapse.
C2. First-source reference: for Phi = phi_x sin(kx) + phi_y sin(ky) (growing mode,
    Einstein-de Sitter, metric (1-2Phi)delta + h of arXiv:1604.06065 eq. (ij)), the
    quasi-static second-order TT strain lives only at (+-k,+-k,0), with real-space
    h_+ = -(5/6) phi_x phi_y cos(K.x) at K = (k,k,0) (basis e_+ = uu - zz,
    u = (1,-1,0)/sqrt2), Fourier coefficient (5/12)phi_x phi_y; 1.54e-5 at delta = 0.01,
    eps = 1, L = 4. Prediction: my hand derivation gives (4/3 - 2 + 4) = 10/3 for the
    source coefficient (kinetic stress of the dust plus the two potential terms) and
    -(5/6); a numerical check with my own polarization-basis projector (not the scope's
    Lambda code) reproduces it to rounding. The "TT fraction 1.73 eps up to eps = 0.18,
    0.5 above" I expect to be sqrt(3) eps up to eps = 1/(2 sqrt3) = 0.289 (so 0.18 is a
    grid point, not the crossover). Refuted by: a different coefficient, or TT power at
    other modes.
C3. Junk TT of the conformally flat data: the oscillating part decays as 1/a (slope
    -0.997, envelope times a constant to 0.7 percent between a = 10 and 100) and is 1.8
    percent of the static value at a = 60. Prediction: the exact homogeneous solutions
    of h'' + (4/tau) h' + G^2 h = 0 are j1(x)/x and y1(x)/x (x = G tau), envelope
    proportional to 1/x^2 = 1/(4 G^2 a); with h = h' = 0 at a = 1 the value at a = 60 is
    within 10 percent of 1.8 percent. Also: K^TT of the initial data is zero, so h' = 0
    is the right initial condition (to be read in `cosmo/ic/cosmo_id.py`). Refuted by: an
    envelope slope outside -0.95 to -1.05, or an initial A^TT that is not zero.
C4. Check 1E: with transverse metric a(t)^2 independent of x, dust at rest and
    X = a(1 + D psi'), the Hamiltonian constraint forces dD/dt = -(3/2) H D (decaying mode
    only). Prediction: holds; the slice diag(X^2, a^2, a^2) is flat, so the growing mode
    (which carries 3-curvature) cannot be represented. A constant D is a coordinate mode.
    Refuted by: a growing solution of the constraint with this ansatz.
C5. Risk 4: the code's slicing (`lapse_harmonic = 1/3`, zero shift: alpha / gamma^(1/6)
    fixed) is the Newtonian slicing at first order for the data of make_east.py.
    Prediction: holds, because the data start with alpha = sqrt(1+2 psi_N) and
    gamma^(1/6) = psi^2 = 1 - psi_N, and the conformal Newtonian gauge with static Phi
    satisfies d_t alpha = -(1/3) alpha^2 K exactly. A consequence I expect (my own, not
    in the scope): the second-order TT strain is then the same in the code's gauge and in
    Poisson gauge, because the first-order gauge generators vanish. Refuted by: a lapse
    or K that the code evolves differently (Khat vs K, a different initial lapse).
C6. B-pre-1: AthenaK's Z4c with the production numerics propagates a linear TT wave in a
    periodic box with an error that converges. Prediction: own runs of the processor
    executable at nx1 = 16, 32, 64 (thin box, 10 crossings) give errors in gamma_yy
    against the exact solution falling at an order between 4 and 6 (sixth-order
    differences, RK4, Kreiss-Oliger), with an amplitude loss dominated by dissipation at
    16 cells. Refuted by: no convergence or an order below 3.
C7. B-pre-3: the Fourier-TT diagnostic and Psi_4 of package `gw_diag` agree on analytic
    linear waves. Prediction: the package tests pass; my own analytic waves (oblique
    lattice vectors, both polarizations, an expanding background a = 3 with K = -3H/a
    trace) give |Psi_4| = c omega^2 |h| with one constant c for all directions and both
    polarizations, the TT amplitude exact to rounding, and a pure-gauge perturbation of
    amplitude 1e-4 leaves TT at the 1e-8 level (second order). Refuted by: direction or
    background dependence of c above the finite-difference error, or a first-order TT
    response to a gauge mode.
C8. B-pre-4: the Newtonian (Zel'dovich) baseline reproduces the literature scaling
    Omega_GW propto sigma^(7/2), omega_peak propto sigma^(3/2) (arXiv:2403.15126,
    source lines 1031 and 1074). Prediction: the locators say it (read: yes); my own
    implementation of the Zel'dovich window |E_(1/3)(i w t_k) - (t_col/t_k)^(2/3)
    E_(1/3)(i w t_col)|^2 times lambda^4 gives exponents 3.5 +- 0.1 and 1.5 +- 0.05 for
    scaled lambda. Refuted by: other exponents. Expected limitation: this is a
    semi-analytic baseline; the N-body part of B-pre-4 waits for AthenaK's Newtonian mode.

## 2026-11-15, entry 2: added prediction for C6 (before the AthenaK runs)

Reading `athenak/src/pgen/tests/z4c_linear_wave.cpp` lines 104-112 for the oblique break
test: with phi = atan2(kx1, kx2) the generator's a_ij equals my e1e1 - e2e2
(e1 = d khat/d theta, e2 = (cos phi, -sin phi, 0)) in xx, yy, xz, zz but has the opposite
sign in xy and yz. For k = (1,1,0) that gives a = -khat khat + zz: traceless, not
transverse. Prediction for the oblique runs `ob_N16`, `ob_N32`: the momentum-constraint
norm at the first dump is at the first-order level (orders of magnitude above the
x-wave's), and the TT plus amplitude in the basis uu - zz is A/2 (the TT part of a),
travelling at c; the longitudinal khat khat : h part does not travel as a wave.
Refuted by: a TT amplitude of A, or constraint norms like the x-wave's.
For the x-waves (`x_N16` to `x_N128`, 10 crossings; `x_N32_long`, 50): order of the rms
error of h_+ between 4 and 6 at t = 10; amplitude loss and phase error falling with N.
Trial runs of the symbolic (C1, C4, C5), crossed-wave (C2) and junk (C3) scripts were made
in scratch/B-emd-gw/tmp/ to debug them; the registered runs follow.

## 2026-11-15, entry 3: outcomes C1-C5 (registered runs)

- C1, run `B-20261115-165114-277a0eb` (`v1_symbolic.json`): every prediction holds.
  TT along x keeps only (S_yy - S_zz)/2 and S_yz; SO(2) and the 90-degree rotation both
  force S_xy = S_xz = S_yz = 0, S_yy = S_zz; translations alone allow diag(0, s, -s) with
  nonzero TT; the reflection y -> -y alone leaves S_yy - S_zz. The divergence-free
  traceless E(2) tensor is f = C/Y^3 (one global mode). The projection of K on it is
  -d_t(X/Y)/alpha per unit x: a total time derivative only for a lapse independent of x
  (the caveat I expected; the scope states it for unit lapse implicitly).
- C4, same run: with transverse metric a^2 and dust at rest, dD/dt = -(3/2) H (D - C),
  D = C + B/t: a coordinate constant plus the decaying mode, no growing mode. With a
  curvature perturbation zeta(x) in the whole spatial metric the growing mode
  E = (9/10) t^(2/3) solves the linearized Hamiltonian constraint. Holds.
- C5, same run: conformal Newtonian gauge with static Phi satisfies
  d_t alpha = -(1/3) alpha^2 K exactly; the initial alpha / gamma^(1/6) of make_east.py
  equals the Newtonian one. Holds, with two notes: the code uses Khat = K - 2 Theta in the
  lapse equation (z4c_calcrhs.cpp lines 694-699), so alpha/gamma^(1/6) drifts by
  (2/3) alpha Theta (zero in the continuum); and `cosmo_id.py` builds Ahat = LW
  (longitudinal), so the initial K^TT is zero to second order and h^TT = 0 exactly.
- C2, run `B-20261115-165119-efd5ee7` (`v2_crossed.json`, figure read): the term-by-term
  source with the dust stress of make_east.py and a polarization-tensor projection give
  h_+ = -(5/6) phi_x phi_y cos(K.x), Fourier |h_+| = 1.5399e-5 at delta = 0.01, eps = 1,
  L = 4, to 1e-14 over the eps scan; only (+-k,+-k,0) carry TT; plane wave exactly 0;
  three waves: 12 modes. Without the dust stress the coefficient is 3/5 of it (1/2), so
  the reference depends on including rho v v. Fraction measure of the scope: with its
  source (10/3) dPhi dPhi it is min(sqrt(3) eps, 1/2) to 3e-16, so the crossover is
  eps = 1/(2 sqrt3) = 0.289, not 0.18 (a grid point of the scope's scan); with the full
  source the same measure is 1.24 eps, saturating at 0.69. The measure is not physical
  (it depends on which non-TT terms are counted). Peak potential 1.8238 delta;
  id.json of runs/cosmo/east_d0.01_n64_pcs4b: max_abs_psiN = 0.018216 (holds).
- C3, run `B-20261115-165123-9cb1745` (figure read): Bessel solution and numerical
  integration agree to 1.1e-10; slope of the maxima -0.9972 (a = 10 to 100), spread of
  envelope*a 0.66 percent from the maxima, 0.23 percent for the exact envelope; at a = 60
  1.807 percent (exact envelope) against the scope's 1.818 percent. Holds. Note: the junk
  is 33 percent of the static value at a = 3 and 10 percent at a = 10.
- Locators checked at the source (kb-data): 2403.15126 lines 1005, 1031, 1074 say
  delta^(7/2), omega_peak propto sigma^(3/2), Omega propto sigma^(7/2) = A_s^(7/4);
  2605.04487 lines 2277-2281 (99 percent by t/t_k = 45.0, shell crossing 22.5), 2395-2405
  (0.4-0.5 c at sigma = 0.1), 2512 and 2625 (several, about 3 orders); 1604.06065 lines
  294-298 (eq. ij). Throughput: the 64^3 log has 1404 cycles, 63.78 s, 5.770e6 zone-cycles/s,
  peak 1685 MiB; the 128^3 log 1301.8 s, 4.467e6 (holds). TESTLOG 1842-1852: a = 17.2 then
  failure (holds).
