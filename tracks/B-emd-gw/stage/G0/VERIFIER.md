# Independent verification of the G0 and G1 material of Track B (wave 2)

Verifier helper of owner B-emd-gw, 2026-11-15. I was given the artefacts (derivations,
code, test scripts, raw outputs under `tracks/B-emd-gw/` and `scratch/B-emd-gw/`), not
the conclusions: STATUS.md, HANDOFF.md, REVIEW.md, EVIDENCE.md, OPEN.md, stage/G1/STATUS.md
and the JOURNAL files were not read before the checks below were done (section 4 is the
comparison, written afterwards). Labels: [VERIFIED] recomputed or read at the source here,
[JUDGEMENT] my inference, [TO VERIFY] open. Predictions and outcomes, in the order they
were written: `JOURNAL.md` in this directory. Scripts: `verifier/scripts/`. Runs: the
manifests under `tracks/B-emd-gw/runs/<run id>/`, outputs under `scratch/B-emd-gw/<run id>/`.

## 1. The claims chosen

The scoping text is `scope/SCOPE.md`. The plan rests on eight claims, five from G0
(sections 2, 3, 8 of SCOPE.md) and three from the G1 criteria of the track sheet (brief
line 741: the two diagnostics agree on analytic linear waves; the Newtonian baseline
reproduces the scaling of the literature) plus the periodic Z4c baseline (B-pre-1).

| Claim | Verdict |
|---|---|
| C1 Item 3: a plane-symmetric collapse has no TT part at nonzero k; E(2) needed; one global harmonic TT mode on the torus | CONFIRMED (one caveat) |
| C2 First-source reference: h_+ = -(5/6) phi_x phi_y cos(K.x) at K = (k,k,0), only (+-k,+-k,0) | CONFIRMED (one wrong number in a side estimate) |
| C3 Junk TT of conformally flat data decays as 1/a; 1.8 percent at a = 60 | CONFIRMED |
| C4 Check 1E: the GR growing-mode pancake needs an x-dependent transverse metric | CONFIRMED |
| C5 Risk 4: the code's slicing is the Newtonian slicing at first order | CONFIRMED (and strengthened) |
| C6 B-pre-1: AthenaK's Z4c propagates a linear wave in a periodic box, converging | CONFIRMED for k along an axis; the oblique-wave generator gives non-TT data |
| C7 B-pre-3: Fourier TT and Psi_4 agree on analytic linear waves | CONFIRMED |
| C8 B-pre-4: the Zel'dovich baseline reproduces sigma^(7/2), omega_peak ~ sigma^(3/2) | CONFIRMED at emission; NOT CONFIRMED for Omega_GW today (see below) |

## 2. Per claim

### C1. Plane symmetry radiates nothing (item 3; SCOPE.md section 2)

Recomputed with sympy (`v1_symbolic.py`, run `B-20261115-165114-277a0eb`): the projector
transverse to x keeps exactly ((S_yy - S_zz)/2)(e_y e_y - e_z e_z) + S_yz(e_y e_z + e_z e_y);
invariance under all rotations about x, and also under the 90-degree rotation alone, forces
S_xy = S_xz = S_yz = 0 and S_yy = S_zz, so the TT part vanishes; translations alone allow
S = f(x) diag(0, s, -s) with nonzero TT; the reflection y -> -y alone leaves S_yy - S_zz.
For gamma = diag(X^2, Y^2, Y^2)(x) the traceless divergence-free E(2) tensor is
A^i_j = C Y^-3 diag(1, -1/2, -1/2), a single global mode. [VERIFIED]
Rerun of the track's own `check_item3.py` (run `B-20261115-165608-171ff45`): output
identical to the committed `scope/results/check_item3.json`.
Break attempt: the projection of K_ij on that mode is -(1/alpha) d_t(X/Y) per unit x; it
is the total derivative -d_t int X/Y dx stated in SCOPE.md only when the lapse does not
depend on x. With the code's lapse (alpha = gamma^(1/6) times a function of x) it is a
weighted integral. Caveat on wording, not on the conclusion.

### C2. Second-order TT strain of the first source (SCOPE.md section 3, lead note)

Hand derivation from eq. (ij) of arXiv:1604.06065 (source `compendium_arxiv.tex`
lines 294-298, metric line 142, read here): with the growing-mode velocity
v = -(2/(3 Hc)) grad Phi and 8 pi a^2 rho = 3 Hc^2, the TT source is
TT[(4/3 - 2 + 4) Phi_,i Phi_,j] = (10/3) TT[Phi_,i Phi_,j] (dust stress, -2 dPhi dPhi,
-4 Phi ddPhi with TT[Phi ddPhi] = -TT[dPhi dPhi]); at K = (k,k,0) TT[Phi_,x Phi_,y terms]
= -(1/4) phi_x phi_y k^2 cos(K.x) e_+ with e_+ = uu - zz, u = (1,-1,0)/sqrt2, so
h_+ = -(5/6) phi_x phi_y cos(K.x). Numerically (`v2_crossed.py`, run
`B-20261115-165119-efd5ee7`, own source built term by term with the velocity of
`cosmo/ic/make_east.py`, own polarization-tensor projector): -(5/6) phi_x phi_y to 1e-14
over 25 values of eps from 1e-3 to 1; Fourier magnitude 1.5399e-5 at delta = 0.01,
eps = 1, L = 4 (SCOPE.md: 1.54e-5); TT only at (+-k,+-k,0); the plane wave gives exactly
0; three waves give 12 TT modes. Peak linear potential 1.8238 delta, and
`runs/cosmo/east_d0.01_n64_pcs4b/id.json` has max_abs_psiN = 0.018216. [VERIFIED]
Break attempts: (i) the coefficient depends on the dust stress: without rho v_i v_j it is
1/2 instead of 5/6; the code includes that stress, so the reference must too (it does).
(ii) The "TT fraction 1.73 eps up to eps = 0.18 and 0.5 above" of risk 1: with the scope's
own definition (max over modes of the TT strain over max of the traceless part of
(20/3) dPhi dPhi / k^2) it is min(sqrt(3) eps, 1/2) exactly (to 3e-16), so the crossover
is at eps = 1/(2 sqrt3) = 0.289; 0.18 is the last grid point of the scope's logarithmic
scan below it. WRONG as stated, harmless for the plan (the derived thresholds eps >= 0.03
and 0.3 are conservative: the correct numbers are 0.032 and 0.19). The measure itself is
not physical: with the full source the same ratio is 1.24 eps saturating at 0.69.
Rerun of `crossed_waves_tt.py`: identical to the committed JSON (465 numbers).

### C3. Junk TT of the conformally flat data (risk 2, check 3A)

The exact solution of h'' + (4/tau) h' + K^2 (h - h_s) = 0 with h = h' = 0 at a = 1 is
h_s + c1 j1(x)/x + c2 y1(x)/x, x = K tau, envelope sqrt(c1^2+c2^2) sqrt(1+1/x^2)/x^2
proportional to 1/a (`v3_junk.py`, run `B-20261115-165123-9cb1745`, figure read). Bessel
solution and numerical integration agree to 1.1e-10; slope of the maxima between a = 10
and 100: -0.9972 (scope -0.997); envelope*a constant to 0.66 percent from the maxima
(scope 0.7), 0.23 percent for the exact envelope; at a = 60: 1.807 percent (exact
envelope; scope 1.818 from the maxima). The initial condition is the right one: the data
have conformal metric delta_ij (h^TT = 0) and Ahat_ij = (LW)_ij longitudinal
(`cosmo/ic/cosmo_id.py` lines 154-177), so K^TT = 0 to second order. [VERIFIED]
Note: the junk is 33 percent of the static value at a = 3 and 10 percent at a = 10.

### C4. Check 1E (the GR pancake)

sympy (run `B-20261115-165114-277a0eb`): for gamma = diag(X^2, a^2, a^2),
X = a(1 + D psi'), dust at rest, the linearized Hamiltonian constraint gives
dD/dt = -(3/2) H (D - C), so D = C + B/t (coordinate constant plus decaying mode); with a
curvature perturbation zeta(x) in the whole spatial metric, E = (9/10) t^(2/3) (the growing
mode) solves it. The slice diag(X(x)^2, a^2, a^2) is flat, so it cannot carry the growing
mode. [VERIFIED] The GR reference solution for the pancake remains [TO VERIFY] as SCOPE.md
says.

### C5. The code's slicing (risk 4)

Read: `athenak/src/z4c/z4c_calcrhs.cpp` lines 689-699 (d_t alpha = -f alpha Khat with
f = lapse_harmonic alpha for the inputs of `first_source/inputs/crossed.athinput` lines
50-56), `make_east.py` lines 12-14 (alpha = sqrt(1 + 2 psi_N), K = -3H(1 - psi_N)).
sympy: the conformal Newtonian gauge with static Phi obeys d_t alpha = -(1/3) alpha^2 K
exactly, and the initial alpha/gamma^(1/6) of make_east.py equals the Newtonian one; the
momentum-constraint source of the data vanishes at first order (Ahat is second order).
So the code's slice is the Newtonian one at first order. [VERIFIED]
Strengthening [JUDGEMENT, derivation]: because the shift is zero and the first-order
slicing coincides with Poisson gauge, the first-order gauge generator between the code's
coordinates and Poisson gauge vanishes, and the second-order TT part of the conformal
metric is then the same in both (a second-order generator adds only d_(i xi_j)). The
caveat of SCOPE.md section 3(b) ("carried to the code's spatial gauge") is therefore
empty at second order for these data; it matters after shell crossing.
Small caveat: the code evolves alpha with Khat = K - 2 Theta, so alpha/gamma^(1/6) drifts
by (2/3) alpha Theta (zero in the continuum).

### C6. Linear waves in a periodic box with AthenaK (B-pre-1)

Own runs of the processor executable of core-v0.3 with the track's input
`periodic_z4c/inputs/lw_x.athinput` (production numerics) and own reader and exact
solution (`v4_lw_runs.sh`, `v4_lw_analysis.py`, run `B-20261115-165056-835fddf`, figures
read). Thin box, wave along x, A = 1e-6, 10 crossings: rms error of h_+ 2.1e-4, 4.5e-6,
2.0e-7, 8.1e-8 of A at N = 16, 32, 64, 128 (order 5.6 and 4.5, then 1.3: a floor near
1e-7 A, the size of roundoff in second differences 1e-16 N^2, not tested further);
amplitude loss order 6.9 and 6.7; phase error 2.5e-4, 6.2e-6, 2.6e-7 rad; after 50
crossings at N = 32 amplitude 0.9999926. [VERIFIED]
Break 1 (oblique wave, k = (1,1,0)): `athenak/src/pgen/tests/z4c_linear_wave.cpp`
lines 107-111 set a_xy = -(1/4)(3 + cos 2theta) sin 2phi and a_yz = +cos theta sin theta cos phi;
e1 e1 - e2 e2 with e1 = d khat/d theta, e2 = (cos phi, -sin phi, 0) has the opposite sign in
both. For k = (1,1,0) the data are a = -khat khat + zz: traceless, not transverse. Measured:
TT plus amplitude 0.5000 A at t = 0 (basis uu - zz), longitudinal khat khat:h rms 0.707 A,
momentum-constraint norm 9.7e-11 against 1.7e-24 for the x-wave; the TT half travels at c
(0.49999935 A at N = 32 after 5 periods), the rest decays. WRONG for the generator (not
for the evolution): any test with a wave vector off the coordinate axes must not use this
generator as a TT wave. Axis-aligned waves (the track's production cases) are unaffected.
Break 2 (seen, then tested): a homogeneous drift gxx - 1 = -(gyy + gzz - 2), independent of
N, growing as t^2, 6.6e-10 after 10 crossings; run `B-20261115-170431-c49964c` shows it
scales as A^2 (ratios 4.00, 16.0 for A x2, x4): a second-order k = 0 anisotropic mode of
the box, removed by the TT diagnostic's default k0 = "zero". Not a defect.

### C7. Fourier TT and Psi_4 agree (B-pre-3)

Package tests rerun (run `B-20261115-165608-171ff45`): 17 passed, 2 skipped (no real
restart or NRFIELD file given); `test_zeldovich.py` all pass (my first rerun,
`B-20261115-165526-23d8541`, collected it under pytest by mistake and aborted the pytest
part; on record). Break tests with my own fields (`v5_gwdiag.py`, run
`B-20261115-170546-4507b05`, figure read): plane waves along (1,0,0), (1,2,0), (1,1,1),
(0,1,2), plus, cross and mixed polarization, a = 1 and a = 3 (rescaled metric, proper
frequency |k|/a; a static rescaling, not an expanding background): TT read-back error
1e-10 of A; Psi_4 = d_t^2 h_+ - i d_t^2 h_x (the
documented convention) to 8.7e-7 relative with spectral derivatives (the O(A) nonlinearity)
and 9e-5 with sixth-order differences at 24 cells; backward partner 2e-9. Exactly flat
metrics in perturbed coordinates (eps = 1e-4, 1e-3): TT part scales as eps^2 (ratio 100.1),
E at 2e-13, B = 0; slicing mode K = -dd f: K^TT at 1e-17, B at 1e-16. On AthenaK output
(x-wave, N = 64, t = 10): h_+ from the TT projection matches the exact wave to 1.9e-7 A
(the evolution error), Psi_4 to 3.6e-7, TT and Psi_4 mutually to 1.8e-7 A. [VERIFIED]

### C8. Literature scaling of the Newtonian baseline (B-pre-4)

Locators read at the source: arXiv:2403.15126 `pII_GW_Vir_C2_Arx.tex` line 1005
(omega^7 sum|Q|^2 peaks at omega ~ 1/t_2 with amplitude proportional to delta_L^(7/2)/t_k),
line 1031 (sigma^(7/2), omega_peak proportional to sigma^(3/2), at fixed <t_max>/t_k), line
1074 (Omega_GW(f_0, t_0) proportional to sigma^(7/2) = A_s^(7/4)). arXiv:2605.04487
`main_v3.tex` lines 2277-2281, 2395-2405, 2512, 2625 say what SCOPE.md quotes. [VERIFIED]
Own implementation of the spectral shape of eq. (result_OmZ) (lines 1052-1062) with mpmath
(`v6_za_scaling.py`, run `B-20261115-170518-c1b61a3`, figure read): for one configuration
scaled by s, local exponents of the peak 3.495 at alpha = 0.002 falling to 3.22 at
alpha = 0.2; of omega_peak 1.500 rising to 1.63; omega_peak t_col = 2.26. So delta^(7/2) and
omega_peak ~ delta^(3/2) hold at emission, at small amplitude. [VERIFIED] The track's T1
and T2 rerun reproduce the committed numbers to 5e-12.
NOT CONFIRMED for Omega today: in eq. (result_OmZ) the emitted frequency is
omega_0 (1 + z_e) and the prefactor is omega_0, so the peak of Omega_GW in f_0 is the
emitted peak divided by (1 + z_e). With z_e taken at t_col (proportional to sigma^(-3/2))
during the matter era, 1 + z_e is proportional to sigma and the peak scales as sigma^(5/2)
(my run: 2.43 overall). The paper's sigma^(7/2) for Omega today (line 1074) holds only if
z_e does not depend on sigma [JUDGEMENT; TO VERIFY by reading the paper's ensemble
definition]. The track uses 7/2 for the emitted energy (SCOPE.md section 1), where it holds.
Limitation: the baseline is semi-analytic; the N-body part of B-pre-4 waits for AthenaK's
Newtonian mode (decision 0013).

## 3. The three weakest points of the plan

1. **The quantitative pre-shell-crossing comparison has almost no window.** The criterion
   of SCOPE.md section 6 (TT strain equal to the second-order reference within a
   truncation error falling at second order; 1 percent linearity) needs both the junk and
   the third-order corrections below the target. The junk is 1.08/a of the static value
   (C3: 10 percent at a = 10, 1.8 at a = 60) and the third-order terms are of relative
   size delta(a) ~ delta a [JUDGEMENT], i.e. 10 percent at a = 10 for delta = 0.01. The fix
   is to compare with the full second-order solution from the code's own initial
   condition (h_s plus the Bessel junk of C3, which is exact at second order), at
   delta = 0.0025 or below and early times; and to move to the Green's-function weak-field
   reference on AthenaK particles for later times, which is not built yet.
2. **The particle-noise floor (risk 1) is estimated, not measured, and the estimate is not
   a physical quantity.** It maps a mean momentum-constraint violation onto a TT level by
   sqrt(2/5) and compares it with a "TT fraction" that depends on which non-TT terms are
   counted (C2: 1.73 eps or 1.24 eps; crossover 0.289 not 0.18). The emission that
   dominates in the literature (post-shell-crossing, 2605.04487 lines 2512, 2625) is where
   the code's constraint violations are largest (SCOPE.md: 1.6e-2 and 0.17 at a = 100).
   The jittered-lattice null run decides it and has to come first.
3. **The relativistic regime is where the code currently stops.** The question "when do
   relativistic corrections matter" needs amplitudes approaching black-hole formation, but
   delta = 0.05 fails at a = 17.2 (`cosmo/TESTLOG.md` 1842-1852, read) and three lapse and
   shift attempts did not pass collapse; the first source sits at delta <= 0.02. The GR
   reference for the pancake is open (C4), the radiation-band estimate (check 3B, spherical
   Delta_vir = 18 pi^2 applied to sheets and filaments) is an order-of-magnitude guess, and
   the mode-by-mode quadrupole comparison in a periodic box is not the literature's
   isolated-patch comparison. Smaller: the AthenaK oblique-wave generator gives non-TT data
   (C6), so any 3D wave test must use axis-aligned k or corrected data.

Not checked here: the FLRW and linear-growth rows (`verify_cosmo`, G2 criteria), the
Newtonian-mode tests (`newton_tests`, in progress in this wave), `first_source` beyond its
unit test, the compute table beyond the two throughput logs (1404 cycles, 63.78 s,
5.770e6 zone-cycles/s, 1685 MiB; 1301.8 s, 4.467e6: as quoted).

## 4. Comparison with the track's own review (written after sections 1 to 3)

Read after commit ad7f707: `stage/G0/REVIEW.md` (lead's review, runs
B-emd-gw-20261115-131016-03b1119 and -131027-03b1119), then `stage/G0/OPEN.md` and
`stage/G1/STATUS.md`.

Agreement (same conclusion reached independently):
- Item 3, its amendments and check 1E (REVIEW, scope, L2 b, c); the global mode
  C Y^-3 diag(1, -1/2, -1/2).
- The crossed-wave coefficient -(5/6) phi_x phi_y cos(K.x) (REVIEW L2 d). The lead's
  1.3858e-5 is the same formula at eps = 0.9 (the cosmo/ ratio); mine 1.5399e-5 at eps = 1.
- The junk decays as 1/a (the lead by a hand argument; here the exact solution, the
  numbers 0.66 percent and 1.81 percent, and the check that K^TT of the data vanishes).
- The sign error of the oblique-wave generator (REVIEW periodic_z4c, OPEN item 13): found
  here from the source and measured in the evolution (TT half A/2 travels at c, the rest
  violates the momentum constraint at first order).
- The second-order closed-box backreaction (REVIEW L2 f: alpha - 1 = -1.64e-10 at t = 10):
  my x_N32 run has alpha - 1 of 1.61e-10 in magnitude at t = 10.
- Throughput numbers, the locators 1604.06065:142, 294-298, 2403.15126:1074,
  2605.04487:2395-2405; the track's tests pass and the scope and baseline scripts reproduce
  the committed numbers.

Found here, not in the review:
1. The TT-fraction crossover of risk 1 is eps = 1/(2 sqrt3) = 0.289, not 0.18, and the
   fraction measure depends on which non-TT terms are counted (C2). The review calls the
   noise criterion a JUDGEMENT bound without examining the number.
2. The overlap of K with the global TT mode is a total time derivative only for an
   x-independent lapse (C1).
3. The code's slicing is Newtonian at first order and, with zero shift, the second-order
   TT strain of the code's conformal metric equals the Poisson-gauge strain (C5,
   derivation, not tested numerically). This answers OPEN item 7 at second order: the
   reference needs no carrying to the code's gauge before shell crossing; K^TT is not
   needed for gauge safety at that order.
4. The homogeneous anisotropic drift of the conformal metric in the wave runs and its A^2
   scaling (run B-20261115-170431-c49964c): the anisotropic companion of the lead's
   alpha backreaction.
5. Omega_GW today: with eq. (result_OmZ) of 2403.15126 and z_e taken at t_col, the peak
   scales as sigma^(5/2), not sigma^(7/2) (C8). The review confirms line 1074 as a reading,
   which it is. Pointer for OPEN item 12 [JUDGEMENT]: the factor 144-392 by which the
   track misses the Omega prefactor of 2403.15126 line 1501 varies with the emission time
   theta = 28 to 126 exactly as theta^(2/3) (143.7 to 391.6 in
   `baseline/results/baseline_results.json` T7b; 2.7257 = (126/28)^(2/3)): the track's
   conversion `today()` divides by 1 + z_e taken at the emission time, while the paper's
   1e-6 sigma^(7/2) has no such dependence. So part of that factor is where the emission
   redshift is taken; the constant part (144 at theta = 28) remains open.
6. Weakest point 1 (the pre-shell-crossing comparison window, closed by junk early and
   third order late unless the reference is the full second-order solution from the
   code's own initial data) is not in the review or in OPEN.md.

In the review, not checked here: the five packages' bit-for-bit reproduction of every
number (I reran scope, baseline T1-T2 and the tests only), periodic_z4c's gauge-wave and
AwA tables, the Fourier-symbol prediction, the weyl-output lag, the late rise of h^TT in
the cosmology dumps (OPEN item 9), the manifest relabelling, verify_cosmo, the
self-similarity of the homogeneous ellipsoid, and the "(5/12)" normalization note (fixed
in SCOPE.md before I read it; my numbers use the real-space amplitude 5/6 and the Fourier
magnitude 5/12 as defined there).
