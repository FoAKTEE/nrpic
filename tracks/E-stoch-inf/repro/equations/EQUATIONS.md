# The equations of arXiv:2401.08530 and arXiv:2512.14649, checked and mapped to the code

Package `repro/equations` of Track E (decision 0028). P0 = arXiv:2401.08530 v2
(`kb-data/raw/arxiv/2401.08530/v2/src/Stochastic_Inflation.tex`), P1 = arXiv:2512.14649 v2
(`kb-data/raw/arxiv/2512.14649/v2/src/PRD_v2.tex`); `P0:<line>`, `P1:<line>` are lines of
those files. Code paths are relative to `athenak/src/` at the merge of main into
`track/E-stoch-inf` on 2026-11-22 (c0ecdd15; release core-v0.6 source). All evidence: registered run
E-20261123-022009-a53e7ee (`scratch/E-stoch-inf/E-20261123-022009-a53e7ee/`; figures copied to
`fig/`). Misprints: `ERRATA.md` (rows E1-E17).

Verdicts: CONFIRMED; CONFIRMED WITH A CORRECTION (the correction is an ERRATA row);
NOT CONFIRMED (what fails, and what the code follows).

Method in one paragraph. `scripts/adm_lin.py` linearises the nonlinear ADM left-hand sides of
P0:128-169 (= P1:284-296, 338-392) about flat FLRW for one plane wave, on the metric P0:177-193
with alpha_b = 1. Time derivatives act on jets; the background is parametrised by H(t) and
p(t) = phidot_b/M with Hdot = -p^2/2, so V, V', V'' follow from the background equations and
every identity holds for any background (slow roll is never assumed). The gauge families are
substituted as jets of R (and of the gauge functions, arbitrary), second and higher time
derivatives of R are removed with the MS equation P0:277 (for the coarse-grained case with its
source, P0:570), and each residual is reduced to a rational function and compared with zero
or with the printed source. All checks are exact identities; none is numerical except items
(c), (d-MC).

## (a) Linear theory and the gauge families (P0 sections II, III; P1 appendix A)

| Item | Statement and locator | Verdict | Evidence (key in `equations/results.json`) |
|---|---|---|---|
| a0 | background equations P0:220-227 and appendix A P0:909-916 (V', V'', eps1ddot) | CONFIRMED WITH A CORRECTION: P0:911 Hddot (E7); P1:267 (E8) | `a0 ...` (5 PASS, the two misprints FAIL as predicted) |
| a1 | the linear field, trace-free and Hamiltonian equations P0:231-248 equal the linearised nonlinear LHS | CONFIRMED | `a1 linearised LHS == printed linear eq [field, Kt_xx, Kt_yy, Ham]` |
| a1' | linear momentum constraint P0:249 = P1:610 | CONFIRMED WITH A CORRECTION: prefactor -2/3, stray "+-" (E1) | `a1 momentum: ...` |
| a2 | "the linear equations match exactly the nonlinear LHS" (P0:174) for the K equation P0:231 | CONFIRMED WITH A CORRECTION: equal up to the linear Hamiltonian constraint (E2) | `a2 K: ... - Ham_lin` PASS |
| a3 | nonlinear trace-free equation P0:137-139, P1:344-348 | CONFIRMED WITH A CORRECTION: gamma_ij, not delta_ij, in the trace term (E3) | `a3 ...` |
| a4 | pure gravity / comoving P0:296-322, fixed curvature / flat P0:325-339, Newtonian P0:343-356, uniform N P0:360-389, generalised synchronous P0:392-405, each with arbitrary gauge functions, satisfy all six linear equations when R obeys MS | CONFIRMED (four families as printed); Newtonian CONFIRMED WITH A CORRECTION (E4, E5); uniform-N definition of delta N has the opposite sign (E6), the family itself is consistent | `a4 <family> satisfies the 6 linear eqs` (5 PASS), `a4 newtonian (delta phi as printed)` FAIL, `a4 uniform N: delta N = ...` |
| a5 | Phi_B, Psi_B, delta phi_gi, zeta_gi as functionals of R (P0:286-289 = P1:164-167), in every family; Phi_B = Psi_B on MS solutions (P0:293); P1 appendix A (P1:604-640) is the comoving-gauge case | CONFIRMED | `a5 <family>: GI relations` (5 PASS), `a5 Phi_B = Psi_B` |

## (b) Coarse-grained (stochastic) equations

| Item | Statement and locator | Verdict | Evidence |
|---|---|---|---|
| b1 | with R -> W R (time derivatives after the product, P0:577, P1:179) and Psi_B> = -eps1 a^2 k^-2 (H Rdot> - S_R) (P0:613, P1:201), the linearised LHS leave exactly S_Pi = sqrt(2 eps1) M S_R (field), S_K = -eps1 S_R, S_Kt_ij = a^2 eps1 (delta_ij/3 - k_i k_j/k^2) S_R (P0:669-671, P1:299, 371-372), and 0 in both constraints (P0:675-681, P1:378-392), in all five gauge families, independent of the gauge functions; the printed linear K equation P0:231 gives the same -eps1 S_R | CONFIRMED (gauge independence shown family by family with arbitrary gauge functions, as P0:684 and P1 section II claim) | `b1 <family>: residuals = printed sources, constraints 0` (5 PASS), `b1 <family>: printed linear K eq ...` (5 PASS) |
| b2 | negative controls: sign of S_R in Psi_B> flipped; Psi_B> := Phi_B> (the case P0:690 warns about; it is what P0's literal prescription gives for the Newtonian Psi of P0:351) | CONFIRMED that both violate the Hamiltonian and momentum constraints at first order in S_R (Ham residual -S_R a^2 p^2 (p^2 - 6 H^2)/(H^2 k^2) for Psi_B> := Phi_B>). The "strong gauge dependence" of P0:690 is a dependence on the family, not on the gauge functions: with Psi_B> := Phi_B> the Newtonian and synchronous residuals are identical to each other and contain no gauge function, but differ from the printed sources that the comoving, flat and uniform-N families give (those families never use Psi_B) | `b2 control: ...` |
| b5 | the constraints hold under the sourced evolution: in the gauge of the code (Psi = B = 0) the evolution equations with the printed sources give dH/dt = dM/dt = 0 on H = M = 0 at first order; flipping the sign of any one source (S_Pi, S_K or S_Kt) makes dH/dt or dM/dt nonzero at first order | CONFIRMED (see the result file for the residual of each flip) | `b5 constraint propagation ... printed sources`, `b5 negative control: sign of S_<X> flipped` |
| b6 | P1:241-259: Phi>, chi>, Psi> without a gauge, delta phi> free, and their time derivatives | CONFIRMED WITH A CORRECTION: P1:258 (E9) | `b6 ...` |
| b3 | BSSN form (P0:972-1031, P1:645-691): S_K^BSSN = S_K because the BSSN K equation differs from the ADM one by the Hamiltonian constraint; S_A = X_b S_Kt = a^-2 S_Kt because the BSSN A_ij LHS is X times the ADM Kt_ij LHS at first order; S_X = S_gt = S_Gt = 0 (definitions, momentum constraint unsourced) | CONFIRMED for the sources; CONFIRMED WITH A CORRECTION for the printed system: 4 pi in an M_Pl^-2 system (E12), sign of the momentum constraint (E13), extra alpha (E17, judgement) | `b3 BSSN K eq [M^-2/2] ...`, `b3 BSSN A_xx/A_yy LHS = X_b * ADM Kt LHS`, `b3 BSSN momentum constraint ...` |
| b4 | usual SI limit (P0 section IV E): S_R in e-folds (P0:718), the flat-gauge noises Sigma_phi, Sigma_pi (P0:538-541) combine into Sigma = H(Sigma_pi + d_N Sigma_phi + (3-eps1) Sigma_phi) (P0:552) = H^-1 S_Pi; delta pi of P0:726; the Pi equation in N_b time P0:708 | CONFIRMED WITH A CORRECTION: "Sigma = F^-1{S_Pi}" (P0:730) misses 1/H (E11); the Friedmann line (P0:530, 710; P1:108) misses 1/(3 M^2) (E10) | `b4 ...` |
| b7 | the source S_R follows from the window acting on the linear solution: MS[W R] = S_R for every mode (P0:570-575, P1:188-193) | CONFIRMED | `code_map.json`: `MS of W R = S_R` |

## (c) Noise amplitude of P0 appendix D (P0:1034-1076)

`scripts/check_noise_amp.py` integrates the background in e-folds (slow roll: quadratic
potential near eps1 = 0.005; USR: flat plateau, eps1 ~ e^-6N, eps2 = 6.000) and the MS equation
P0:718 from Bunch-Davies data at k/(aH) = 300, and evaluates at the crossing k = sigma a H the
variance per e-fold of the Heaviside-window noise, D = |f|^2 (d k_sigma^3/dN)/(6 pi^2), with
f = R' + (3 - eps1 - eps2) R (P0:1054 after the integration by parts P0:1050), against the
printed sqrt(D) ~ 3 H/(2 pi sqrt(2 eps1) M) (P0:1072).

| Case | sigma = 0.02 | 0.05 | 0.1 | 0.2 | 0.5 | 1 | Verdict |
|---|---|---|---|---|---|---|---|
| SR, amplitude / printed | 1.043 | 1.034 | 1.027 | 1.025 | 1.053 | 1.204 | CONFIRMED to 5 per cent for sigma <= 0.2; the excess is the change of H and eps1 between Hubble crossing and sigma crossing (|R| numerical / P0:1059 form = 1.044 ... 1.019 in the same columns) |
| USR, amplitude / printed | 1.33e-4 | 8.33e-4 | 3.33e-3 | 1.33e-2 | 8.33e-2 | 0.338 | NOT CONFIRMED: the ratio is sigma^2/3; R' = 3R(1+O(sigma^2)) in USR, so f = -sigma^2 R/(1 - i sigma) and the printed value follows only by dropping R' (then 1.0002 at sigma = 0.02); the step P0:1063 treats eps1 as constant (E15) |

The code does not use this amplitude (it evolves the mode functions and the smooth window of
P1); the finding matters for `../langevin/`, which reproduces the figures of P0 section V.

## (d) The Langevin pair of P0 section V (P0:782-842)

| Item | Statement | Verdict | Evidence (`langevin/langevin.json`) |
|---|---|---|---|
| D1 | dN/dN_b = sqrt(1 + (alpha^2 - 1)(1 - eps1/3)) from the long-wavelength Hamiltonian constraint P0:802 | CONFIRMED | `D1 ...` |
| D2 | drift of d alpha/dN_b, P0:825-826, from the field equation P0:812, phiddot = -H(eps1 + eps2/2) phidot, V' from the background | CONFIRMED; alpha = 1 is a fixed point; the linearised drift (eps1 + eps2 - 3) delta alpha equals super-Hubble CPT in the comoving gauge (Psi = -R'), as P0:830 states | `D2 ...`, `D4 ...` |
| D3 | Ito term P0:817 (alpha^3 <S_Pi^2>/phidot^2) and noise alpha^3 S (P0:826) | NOT CONFIRMED: Ito's lemma with the noise alpha S_Pi of P0:812 gives alpha^5 <S_Pi^2>/phidot^2; the printed alpha^3 corresponds to a noise without alpha, whose noise term would be alpha^2 S. Monte Carlo of dZ = (phidot/Z) sigma dW (alpha0 = 2, sigma = 0.1, 4e5 paths): mean drift 0.3075 +- 0.013 against 0.32 (alpha^5) and 0.08 (alpha^3) (E14) | `D3 ...`, `mc` |
| D5 | "the Stratonovich evolver of Mathematica" (P0:836) applied to an equation that carries an Ito correction | [JUDGEMENT] inconsistent as written: in Stratonovich form the chain rule has no correction term; whether the authors' run double counts cannot be decided from the text; P0:822 says the term is "practically" without effect | reading |

## (e) Map of the sources and of the stochastic scheme of P1 to `athenak/src/scalar_field/`

Conventions. Papers: M_Pl explicit (Mpl = 100 in the runs, P1:519), cosmic time with alpha = 1
(P1:483), K = -3H (P1:227), Pi = n.d phi, BSSN with X = det(gamma)^-1/3 (P1:675), metric shift
sign flipped between ADM and BSSN (P1:671). Code: G = c = 1 (M_Pl^-2 = 8 pi), coordinate time
with the background proper time running at alpha_b (box mean of the lapse), Z4c variables
(chi = X with chi_psi_power = -4, Khat = K - 2 Theta with Theta = 0 when use_z4c = false or
damping off; At_ij = chi Kt_ij), K = -3H (`scalar_field_slice.cpp:15-16`), Pi = n.d phi
(`scalar_field_rhs.cpp:143`).

| # | Paper item | Code (file:line) | Check | Verdict / difference |
|---|---|---|---|---|
| 1 | eps1, eps2 = -dln eps1/dN (P1:171) | `scalar_field_noise.cpp:496-497` | `eps1: ...`, `eps2: ...` PASS | CONFIRMED (G = 1 form of eps1; eps2 from the background KG equation) |
| 2 | window W = (1 + tanh[s ln(k_sigma/k)])/2, k_sigma = sigma a H (P1:503-505), s = 5, sigma = 1 (P1:506, 519) | `scalar_field_noise.cpp:547-551` (x, sech2, w1, w2), `:533-534` (d ln k_sigma/dt and its derivative), options `noise_window`, `noise_sharpness`, `noise_sigma` (`:129-135`) | `window first/second derivative` PASS, `d ln(sigma a H)/dt`, `d2 ln ...` PASS | CONFIRMED; derivatives in closed form (P1 does not print them); H and a are those of the background of level 0 or 1 |
| 3 | S_R = R Wddot + [2 Rdot + (3 - eps2) H R] Wdot (P1:193, 304) | `scalar_field_noise.cpp:540, 552-553` (fric = (3 - eps2) H, shell factor) | `MS of W R = S_R` PASS | CONFIRMED |
| 4 | mode functions R_k(t) obeying MS (P1:183) propagated in real space by P1:313-320 with an FFT at each step (P1:491-493) | per shell |n|^2, complex ODE in proper time `scalar_field_noise.cpp:536-545`, integrated with the low-storage RK of the fields stage by stage (`:694-720`) | reading | CONFIRMED in content, different in scheme: Fourier space per shell instead of a real-space field and FFT; isotropy makes the two equal for level 0 and 1 |
| 5 | backreaction levels 0, 1, 2 (P1:783-788; runs with level 2, P1:487, 520) | `scalar_field_noise.cpp:477-500` (level 0 Friedmann, level 1 box means), `:162-165` (level 2 refused) | reading | NOT CONFIRMED for level 2: not implemented (the code stops); P1:790 and Fig. 9 put the effect at a small relative level (SPEC 2.3) |
| 6 | alpha_k drawn once (P1:312), Gaussian, Hermitian (P1:121-128) | `NoiseDrawAlpha` `scalar_field_noise.cpp:447-470`, keys of the header `:14-24` | `../../noise/` A-tests | CONFIRMED in statistics; keyed by wave vector instead of a real-space white field (same realisation at every N; SPEC 5.4) |
| 7 | F^-1{.} hermitian inverse transform (P1:297, step iv-c P1:493) | `NoiseSynthesize` `scalar_field_noise.cpp:605-660`, normalisation L^-3/2 at `:531`, I_R = L^-3/2 sum 2 Re[S_R alpha_n e^{ik.x}] (header `:51`) | `../../noise/` | CONFIRMED; direct sums, no FFT; Fourier normalisation of SPEC 5.4 (the printed prefactors of P2 are inconsistent, SPEC 5.4) |
| 8 | S_Pi = sqrt(2 eps1) Mpl S_R (P1:299, 687) | `kick_pi_fac = pi_sign alpha_b Pi_b/H` `scalar_field_noise.cpp:557`, added `scalar_field_rhs.cpp:150-151` to d_t Pi | `kick Pi ...` PASS (both signs of Pi_b) | CONFIRMED WITH A DIFFERENCE OF CONVENTION: Pi_b/H = sqrt(2 eps1) Mpl for Pi_b > 0 (P1 assumes phidot_b > 0, P0:920); for Pi_b < 0 the code gives -sqrt(2 eps1) Mpl, which is what the derivation gives (delta phi_gi = (phidot_b/H) R, P0:271); factor alpha_b (proper-time rate); `noise_pi_sign = -1` is the negative control of b5 |
| 9 | S_K = -eps1 S_R (P1:371, 685) | `kick_k_fac = -alpha_b eps1` `:558`, added to rhs Khat `:741` | b1, b3 | CONFIRMED (Khat = K for Theta = 0); factor alpha_b |
| 10 | S_A = eps1 (delta_ij/3 - k_i k_j/k^2) S_R (P1:686); S_Kt = a^2 eps1 (...) S_R (P1:372) | `kick_a_fac = alpha_b eps1` `:559`, `:743-751` (At_ij += fa (delta_ij I_R/3 - T_ij), T_zz = I_R - T_xx - T_yy), projector qh_i qh_j/qh^2 of the stencil or of the continuum (`noise_projector`, `:167-174`) | b3 (`S_A = X_b S_Kt`) | CONFIRMED; the stencil projector is an option of the code (continuum = P1) |
| 11 | S_X = S_gt = S_Gt = 0, constraints unsourced (P1:691, 392) | `Kick` touches only Khat and At (`:725-755`) | b1 (constraints 0), b3, b5 | CONFIRMED |
| 12 | step iv-b: integral of the source over the step, "at each RK4 time step" (P1:489-494) | rate S_X(t_s) evaluated at every stage with data of the stage (`NoiseStage` `:667-690`, `NoiseModeRHS` per stage; header `:62-64`) | reading | DIFFERENT SCHEME [JUDGEMENT, SPEC 2.4]: the source is a smooth function of time for frozen alpha_k, so the rate at the stage time keeps the order of the integrator; P1's increment per step and Launay's thesis (per substep) are not followed literally |
| 13 | RK4, classical Butcher tableau (P1:698-709) | AthenaK `rk4` = low-storage RK4()4[2S] of Ketcheson 2010 (`driver/driver.cpp:146-147`), the noise data use the same update (`scalar_field_noise.cpp:694-720`) | reading | DIFFERENT SCHEME, same order (4) for smooth sources |
| 14 | step iv-d: addition to the BSSN right-hand sides (P1:494) | task `SF_Kick` after `Z4c_CalcRHS` (`scalar_field.cpp:200-201`); Pi kick inside the field RHS (`scalar_field_rhs.cpp:150-151`) | reading | CONFIRMED |
| 15 | field equation, BSSN form (P1:663-665) | `scalar_field_rhs.cpp:137-144` | reading | CONFIRMED (same signs: d_t Pi = ... + alpha (K Pi - V'), K = Khat + 2 Theta) |
| 16 | coarse-grained initial slice at t* (P1:488 item iii), geodesic gauge data of P2 | `scalar_field_slice.cpp:6-40` (A = W R, B = d(W R)/dtau; longitudinal hypersurface, which coincides with the geodesic-gauge slice of P2 with chi_0 = E_0 = 0 at t*) | `../../spec/` T4, b1 (constraints hold for any pair R>, Rdot>) | CONFIRMED with the corrected delta Pi of P2 (SPEC 5.3); `slice_delta_pi = printed` is the negative control |
| 17 | units Mpl = 100 (P1:519) | G = 1, phi_code = phi/(sqrt(8 pi) Mpl) (SPEC 2.5) | `eps1: ...` | DIFFERENCE OF CONVENTION only (ratios such as H/Mpl enter) |
| 18 | time variable: cosmic time, alpha = 1 (P1:483) | coordinate time; mode ODE and kicks multiplied by alpha_b (`:520-545, 557-559`) | reading | identical for alpha = 1; under another lapse the code's choice (background proper time) is a [JUDGEMENT] of core that P1 does not cover |
| 19 | tensor sources (P0:758-779; not in P1, P1:693) | none | reading | not implemented in either (consistent with P1) |
