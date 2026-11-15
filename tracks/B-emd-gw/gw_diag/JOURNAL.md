# JOURNAL of gw_diag (B-pre-3, helper of B-emd-gw)

Predictions are written before the test runs; outcomes are appended below each, also when
the prediction fails.

## 2026-11-15 Definitions taken from the source

- [VERIFIED] York's covariant TT decomposition `Q^ab = Q_TT^ab + (LV)^ab + gamma^ab Q/3`,
  `(LV)^ab = D^a V^b + D^b V^a - (2/3) gamma^ab D_c V^c`, `D_a (LV)^ab = D_a (Q^ab - gamma^ab Q/3)`:
  arXiv:2111.09163 v2, `kb-data/raw/arxiv/2111.09163/v2/src/prd_v1.tex` lines 163-175.
- [VERIFIED] `rho_K = (M_pl^2/2) K^TT_ab K_TT^ab` (Eq. rhoK, line 260), with `K_ab = (1/2) L_n gamma_ab`
  (line 225; opposite sign to AthenaK, irrelevant for a quadratic quantity); "rho_K = rho_Isaacson/2"
  for linear tensor modes (footnote, line 272); in Newtonian gauge `K_TT^ij = hdot^tt_ij/(2 a^2)` and
  `rho_K = (M_pl^2/8) hdot^tt_ij hdot^tt_ij` (Eqs. Aijnewton, rhoknew, lines 496 and 501).
- [VERIFIED] AthenaK conventions read from the source: Z4c variable order
  (`athenak/src/z4c/z4c.hpp` lines 48-56); `psi^4 = chi^(4/chi_psi_power)`, default
  `chi_psi_power = -4` (`z4c.cpp` line 125, `z4c_adm.cpp` lines 220-233);
  `K_ab = psi^4 A_ab + (Khat + 2 Theta) gamma_ab / 3`; Weyl scalar
  (`z4c_calculate_weyl_scalars.cpp`): radial triad about the origin, Gram-Schmidt in the order
  phi, r, theta, output multiplied by r; finite differences of order 2, 4, 6 for nghost 2, 3, 4
  (`utils/finite_diff.hpp`).

## 2026-11-15 Derivations used by the module [JUDGEMENT until the tests below pass]

D1. Trace removal before the projection. With `gamma = a^2 (delta + h)` and zero shift,
`K_ij = -(1/2 alpha) (2 a adot (delta + h) + a^2 hdot)`. `Lambda K` contains `-(a adot/alpha) h^TT`, a term
that is not a time derivative of the wave; the trace-free part with respect to the full metric,
`A_ij = K_ij - gamma_ij K/3 = -(a^2/2 alpha) hdot_ij`, does not. Hence the module projects
`tilde A_ij = chi A_ij = -(1/2) d_tau h_ij` (Z4c's variable) and never `K_ij` itself:
`d_tau h^TT = -2 Lambda(tilde A)`, `rho_kin = Lambda(tilde A)_ij Lambda(tilde A)_ij / (16 pi G)` = rho_K
of 2111.09163 to the order of the projection.

D2. Psi_4 sign. Linear wave along +z in TT gauge, `K = -hdot/2`: `R_ij = -(1/2) hddot_ij`, so
`E = -(1/2) hddot`; `B_ij = sym(eps_i^kl d_k K_lj)` gives `B_xx = -hddot_x/2`, `B_xy = hddot_+/2`,
`B_yy = hddot_x/2`. With `mbar = (x - i y)/sqrt 2`: `(E - iB) mbar mbar = -hddot_+ + i hddot_x` and
`(E + iB) mbar mbar = 0`. So `Psi_4 := -(E - iB) mbar mbar = hddot_+ - i hddot_x`, and the reversed
direction gives zero. AthenaK's expression (`rpsi4 + i ipsi4 = 2 Y_ab mbar^a mbar^b` with
`Y = -Rnn/4 + R_acb u^c/2 - R_dacb u^d u^c/4`, `mbar = (v - i w)/sqrt 2`) evaluates for the same wave
to `hddot_+ - i hddot_x` before the factor r, i.e. the same convention.

D3. Helicity. A Fourier mode `exp(i(k.x - omega t))` with polarization `e^(+2) = (e_+ + i e_x)/sqrt 2`
turns counterclockwise about its direction of motion (helicity +2). A mode at k moving along -k
with the same label turns clockwise about k, i.e. counterclockwise about its motion: also +2.
(A first version of `helicity_spectrum` flipped the label of backward parts; corrected before any
test ran.)

D4. Scalar perturbations and Psi_4. For `gamma = (1 + 2 zeta) delta + 2 dd E` the linear
`E_ij = -(d_i d_j - delta lap/3) zeta` is not zero (the tidal field of the matter); B = 0 and
`Lambda E = 0`. So Psi_4 along a direction n is `-(k.mbar)^2 zeta` for a plane scalar mode, zero
only for n parallel to k. A scalar perturbation is invisible to the TT diagnostics but not to
Psi_4 off its wavevector: in a box with matter, Psi_4 measures tidal fields as well as waves.

## Predictions (written 2026-11-15 before the tests ran)

P1 (unit tests, `tests/`). (a) Lambda is idempotent, symmetric, traceless and transverse to
round-off (< 1e-12 relative). (b) A plane wave along each axis and along lattice diagonals,
on a non-cubic grid (nx != ny != nz, Lx != Ly != Lz), is returned by tt_project to round-off
(it is band-limited and exactly TT), and its h_+, h_x, rho_kin and rho_grad equal the input to
round-off when the arrays are given as h directly. (c) Built from gamma = delta + h, K = -hdot/2
through the conformal decomposition, the relative error in h^TT and in rho is O(A) (the O(A^2)
terms of det(gamma)^(-1/3)): at A = 1e-6 below 1e-5, and falling by 10 per decade of A.
(d) Hand-written circular waves: h_xx = A cos(kz - wt), h_xy = A sin(kz - wt) along +z has
helicity -2 (pattern clockwise about +z); h_xx = A cos(kz + wt), h_xy = A sin(kz + wt) moving along
-z has helicity -2. All energy must land in the predicted helicity (other < 1e-12 of the total).
Refuted if any of these fails.

P2 (Weyl on waves). E and B from gamma, K agree with the linear references E = -hddot/2,
B = -(1/2) sym(eps d hdot); the error falls as dx^p for orders p = 2, 4, 6 (fitted slopes within
0.3 of p) until it reaches the O(A^2) floor; spectral derivatives sit on the floor at every
resolution. Psi_4 along k equals hddot_+ - i hddot_x; Psi_4 along -k is below 1e-6 of it at
A = 1e-6 with spectral derivatives (only O(A) relative). Refuted if a slope or the sign of Psi_4
differs.

P3 (pure gauge, exact Minkowski in random coordinates, with slicing). h^TT, d_tau h^TT and rho
scale as eps^2 (slope 2 +- 0.1 in eps over 1e-6 ... 1e-2), i.e. zero at linear order. E, B and
Psi_4 vanish analytically at every order; numerically they converge to zero as dx^p at fixed eps,
and at fixed resolution scale as eps (slope 1). Refuted if the TT parts scale as eps or the Weyl
parts do not converge.

P4 (scalar mode). h^TT, d_tau h^TT, rho, B and Lambda E scale as eps^2; E agrees with the linear
E = -(dd - delta lap/3) zeta to O(eps^2) + truncation; Psi_4 off-wavevector is nonzero and equals
-E_lin mbar mbar (D4). Refuted if B or Lambda E scale as eps.

P5 (random superposition, 48 modes, |m| in 1..6, A = 1e-6 per mode). Shell spectra of rho_kin and
rho_grad equal the per-mode expectation of `analytic.waves_expected` to relative 1e-5 (O(A)), at
every time; total rho_kin + rho_grad constant in time to 1e-5 while rho_kin and rho_grad separately
oscillate (finite number of modes; their time average is equal); helicity energies match the
input fractions to 1e-5. d_tau h^TT from centred time differences of h^TT at spacing dt converges to
the 3+1 value as dt^2.

P6 (AthenaK output, run B-emd-gw-20261115-113218-0ea0f74 of periodic_z4c: z4c_linear_wave, k along x,
A = 1e-6, 32^3, restart files every 1/16 period). The reader assembles the mesh; h^TT is the pgen
wave h_ij = A e_ij sin(2 pi (x - t)) with e = diag(0, -1, 1) (pgen source,
`athenak/src/pgen/tests/z4c_linear_wave.cpp`), i.e. h_+ = A sin(2 pi (x - t)) in the basis of
pol_basis(+x) (theta-hat = -z, phi-hat = +y), h_x = 0; rho_kin + rho_grad = (2 pi)^2 A^2 / (32 pi)
constant in time to the evolution error (sub-percent at 32^3 over two periods [JUDGEMENT]);
d_tau h^TT from K agrees with time differences between dumps. Psi_4 from E, B with AthenaK's
radial triad agrees with AthenaK's weyl output divided by r to the float32 and stencil
differences (relative 1e-3 [JUDGEMENT]), where the output was computed at the same time.
Refuted if the amplitude, polarization or sign differ.

## Outcomes of the unit tests (2026-11-15, `python3 -m pytest tests/`)

First run: 10 passed, 2 failed.
- P1(a), (b), (d) passed as predicted: Lambda idempotent, traceless, transverse to round-off;
  plane waves along axes and lattice diagonals on a non-cubic grid returned to < 1e-12 with
  h_+, h_x, rho_kin, rho_grad exact; the hand-written circular waves along +z and -z put all
  their energy in helicity -2 (helicity +2 below 1e-12 of the total).
- P1(c) FAILED as stated: the relative error of h^TT, d_tau h^TT from (gamma, K) is O(A^2), not
  O(A): 3.7e-8 at A = 1e-4, 3.7e-4 at A = 1e-2 (slope 1.77 including a round-off point at 1e-6).
  Cause, checked afterwards in a run where it could have failed (inline script, 24x20x18 grid,
  six random waves): tilde gamma - delta - h is O(A) relative (1.6e-4 at A = 1e-4) but its
  trace-free part is O(A^2) (4.1e-8 at A = 1e-4, 4.1e-4 at A = 1e-2) — the O(h^2) term of
  det(gamma)^(-1/3) is a pure trace, which Lambda removes. The test now expects slope 2.
- Gauge-mode test FAILED and exposed a bug: with K = 0 (flat metric in curvilinear coordinates)
  the Ricci tensor with spectral derivatives was 1.5e-3 at eps = 1e-3, scaling as eps^2. Cause: in
  `weyl.ricci` the quadratic Christoffel terms were contracted with einsum labels "i, j" inside a
  loop over (i, j), so einsum summed over i and j. Checked against the direct formula
  R_ij = d_k G^k_ij - d_j G^k_ki + G^k_kl G^l_ij - G^k_jl G^l_ki (difference 0.16 before, round-off
  after the fix). After the fix: R = 1e-12 (spectral) for the flat metric; with slicing, E and B
  are 1e-12 (spectral) while R itself is 8e-4 (balanced by the K terms); FD4 E falls by 15 from
  16^3 to 32^3 (order 3.9). The plane-wave tests could not see the bug (it is O(A^2), A = 1e-8).
After the two corrections: 12 passed, 2 skipped (the real-file reader tests need GWDIAG_RST /
GWDIAG_NRFIELD).

## Amendments to P5 (written before validate_tt.py ran)

- After the P1(c) outcome the expected error of quantities built from (gamma, K) is O(A^2)
  relative plus round-off ~1e-16/A: at A = 1e-6 per mode, below 1e-9 (not 1e-5).
- With no pair k_m = -k_n among the modes, the spatial average of each mode is time
  independent, so rho_kin and rho_grad are separately constant, not oscillating (the original
  P5 sentence is wrong on its face). They oscillate in antiphase only for standing waves; a
  standing-wave case (modes at m and -m with equal amplitudes) is added: prediction
  rho_kin + rho_grad constant to < 1e-9 while rho_kin/rho_ref swings between 0 and 2 for a
  single standing mode.
