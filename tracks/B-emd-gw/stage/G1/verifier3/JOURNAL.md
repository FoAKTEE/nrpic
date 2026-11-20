# Journal of stage/G1/verifier3 (independent verifier of G1 criterion 1 and of the spatial-gauge piece)

Helper of B-emd-gw, wave 3 round 1, started 2026-11-20 14:13 PST (`date`). Fresh context: I
did not produce the runs I check. Read so far (allowed list of the task): CLAUDE.md,
coord/CHARTER.md to "Owners", decision 0010, harness/RULES.md, docs/FORMATS.md, the set-up
files of waves/ (inputs/flat_oblique.athinput, expanding.athinput, card64.list,
card64_x10.list, scripts/make_expanding_ic.py, run_flat.sh, run_expanding.sh), the generator
`git show core/requests-b:athenak/src/pgen/tests/z4c_linear_wave.cpp` (the task named
`athenak/src/pgen/z4c_linear_wave.cpp`; the file lives in `pgen/tests/`), the binary writer
`git show core/requests-b:athenak/src/outputs/binary.cpp`, `athenak/src/pgen/nrpic/nrpic_cosmo.cpp`
lines 1-230, `athenak/src/z4c/z4c_adm.cpp` (ADM <-> Z4c), cosmo/README.md "Units and gauge",
gw_diag/README.md (definitions). Not read (forbidden until my V3 numbers are committed):
waves/README.md Results/Open, waves/JOURNAL.md, stage/** outside this directory, note/,
the owner's STATUS/HANDOFF/JOURNAL/PLAN, scratch/orch reports.

## Entry 1 (14:20): V1 predictions, before any check

Exact solutions I derive (by hand first; the script `scripts/v1_exact.py` checks them):

(F) Flat box [-1/2,1/2]^3, k = (1,1,1) cycles, K = 2 pi k, omega = |K| = 2 pi sqrt 3,
alpha = 1, beta = 0. Linear TT wave h_ij = A_+ e+_ij sin(P) + A_x ex_ij sin(P + phi_x),
P = K.x - omega t, gamma_ij = delta_ij + h_ij, K_ij = -(1/2) d_t h_ij, so
At_ij = chi (K_ij - gamma_ij K/3) = (omega/2)[A_+ e+ cos P + A_x ex cos(P+phi_x)] at first
order (chi = 1, K = 0 at first order). This is the generator's closed form with
pi |k| = omega/2. Linear ADM: d_t K_ij = R_ij = -(1/2) lap h_ij for TT h, so
d_t^2 h = lap h: exact for omega = |K|.
Predictions P1.1-P1.4:
- P1.1 the generator's (axx..azz) equal theta-hat theta-hat - phi-hat phi-hat and
  (bxx..bzz) equal theta-hat phi-hat + phi-hat theta-hat for khat = (1,1,1)/sqrt 3, with
  theta-hat, phi-hat the usual spherical unit vectors of khat (theta from +z, azimuth from
  +x); both transverse and traceless, e:e = 2, e+:ex = 0, to round-off (< 1e-15).
  Refuted if any of these fails by more than 1e-14 (then the cross polarization is not what
  the comment says, or not TT).
- P1.2 the closed form satisfies the linearized ADM equations (sympy residual identically 0);
  refuted by a non-zero residual (sign of At, factor pi|k|).
- P1.3 for this wave E_ij = (|K|^2/2) h_ij, B_ij = -(1/2) sym(eps_ikl d_k (d_t h)_lj)
  (coordinate components) and Psi_4 = -(E - iB)_ij mbar^i mbar^j with
  mbar = (theta-hat - i phi-hat)/sqrt 2 equals d_t^2 h_+ - i d_t^2 h_x for the wave moving
  along +khat and 0 for the reversed direction. Refuted if the sympy check of the 3+1
  formulas (E from R_ij + K K_ij - K_ik K^k_j, B from eps D K) linearized in A disagrees.

(X) Expanding box, side 4, k = (pi/2)(1,1,0), |K| = pi/sqrt 2 = 2.2214. Background:
lapse d_t alpha = -(1/3) alpha^2 K, zero shift, Einstein-de Sitter with H = 1 at a = 1:
alpha = a = (1 + t/2)^2, K = -3 a'/a^2 = -3 a^(-3/2) (prime = d/dt, t conformal time).
Perturbation gamma_ij = a^2 (delta_ij + h_ij), h TT, lapse unperturbed at first order.
Mode equation h'' + 2 (a'/a) h' + |K|^2 h = 0, a'/a = 2/(t+2). With tau = t + 2 the
solutions are j_1(|K| tau)/(|K| tau) and y_1(|K| tau)/(|K| tau). Initial slice of
make_expanding_ic.py: psi = 1, K = -3, alpha = 1, Ahat_ij = -(1/2) h'_ij(0) with
h'_ij(0) = eps_+ e+ cos(K.x) + eps_x ex cos(K.x + phi_x): from K_ij = -(1/2 alpha) d_t gamma_ij
at t = 0, a = 1, a'(0) = 1, K_ij = -(delta + h) - h'/2, so the traceless part is -h'/2 and
h(0) = 0. Hence h_+(x,t) = eps_+ T(t) cos(K.x), h_x = eps_x T(t) cos(K.x + phi_x) with
T = c1 j1(x)/x + c2 y1(x)/x, x = |K|(t+2), T(0) = 0, T'(0) = 1. The Z4c variables give
h = gt - delta (chi removes a^2) and h' = -2 a At (At = chi (K_ij - gamma K/3) = -h'/(2a)).
Weyl parts, coordinate components (my derivation): E_ij = (|K|^2/2) h_ij + (a'/(2a)) h'_ij
(= -(1/2)(h'' + (a'/a) h') by the mode equation), B_ij = -(1/2) sym(eps_ikl d_k h'_lj)
(independent of a: eps_i^kl = a^-1 [ikl], K_lj = -(a'/a^2) gamma_lj - (a/2) h'_lj).
Predictions P1.5-P1.7:
- P1.5 the closed form T(t) matches an independent numerical integration of the mode
  equation (solve_ivp, rtol 1e-12) to 1e-9 relative on t in [0, 10], and its ODE residual
  (finite differences of the closed form) is at the level of the difference error.
  Refuted otherwise.
- P1.6 a = (1+t/2)^2 and alpha = a solve the lapse condition and the Friedmann equation
  with rho_0 = 3/(8 pi) (sympy, identically).
- P1.7 the sympy linearization of E_ij and B_ij of the 3+1 formulas for the metric
  a^2(delta + eps T(t) e cos(K.x)) with K_ij = -(1/2a) d_t gamma_ij gives exactly the
  expressions above. Refuted by any non-zero residual (then my Weyl reference for X is
  wrong and V3-X must use the sympy expression instead).
