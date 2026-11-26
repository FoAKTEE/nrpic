# Journal of the fresh verifier of gate G2 (Track A, checklist item C18; decisions 0016 item 4, 0046 item 1)

Helper of A-emd-pbh, batch 29, 2026-11-26 (PST). Processors only, 0 card-hours. Labels as in the brief.

## Entry 0, 2026-11-26 14:40 PST: what was read before any recomputation

- Read for the claims: stage/G2/RERUN.md, stage/G2/VERIFY, Table V of the note (note/tables/ledger_g2.tex,
  label tab:ledger_g2 = Table V in main.aux), note section V (main.tex 175-213), scope/SCOPE.md section 7 and 3
  (lines 95-103, 183-214), szekeres/DESIGN.md, the prediction entries 8 and 12 of szekeres/JOURNAL.md.
- Disclosure: while locating the predictions A2, AZ1, AZ2, A2X and A2H in periodic_threshold/JOURNAL.md I read
  the lead's outcome subsections that follow them (lines 924-1207), and decision 0046 item 1 quotes the A2H
  bracket. So for item 2 I am not blind to the lead's numbers; I recompute them with readers of my own and
  say so in VERIFIER.md. I have not read stage/REVIEW-wave3.md, the verdict column of stage/G2/CHECKLIST.md,
  STAGE_REPORT.md, OPEN.md or the outcome entries 11 and 13 of szekeres/JOURNAL.md.
- `harness/bin/nrpic-stage verify A-emd-pbh G2 --full` started detached at 14:18 PST, log
  scratch/A-emd-pbh/tmp/stage-verify-full-verifier-20261126-141818.log (pid 499738).

## Entry 1, 2026-11-26 14:45 PST: my references and predictions, before any reader of mine has run

### V1 Szekeres series (N64, N128, N256), reference of my own

Reference [derivation, this entry; BACKGROUND: quasi-spherical Szekeres dust, simultaneous bang, R(t,r) the LTB
radius of the shell, rho = (M' - 3 M bn)/(4 pi R^2 (R' - R bn))]. With R = M^(1/3) t^(2/3) g(k t^(2/3) M^(-2/3)):
R'/R - bn = Q/3 + G(t) P, Q = M'/M - 3 bn (depends on the direction, not on t), P = k'/k - (2/3) M'/M (neither),
G = d ln R/d ln k at fixed t, M. Hence, per fluid element,
  rho = rhobar/(1 + c G(t)),  K = d ln rho/dt = -3 H_T - c dG/dt/(1 + c G),  c = 3P/Q constant,
rhobar = 3M/(4 pi R^3), H_T = Rdot/R. The shell enters only through s = k^(3/2)/M: bound shells
t = (eta - sin eta)/s, H_T = s sin(eta)/(1 - cos eta)^2, rhobar = (3/4pi) s^2/(1 - cos eta)^3,
G = -1 + (3/2) sin eta (eta - sin eta)/(1 - cos eta)^2 (hyperbolic functions for unbound shells; k = 0 is EdS).
Per cell, from the initial slice only: KT = transverse eigenvalue of K^i_j (field file: K and psi^-6 Ahat_ij),
H_T t_i fixes eta_i (t_i = 2/(3 H), H = 1/16), then s, rhobar_i, G_i; rho_i from the particle masses
(m / (psi^6 h^3)); c = (rhobar_i/rho_i - 1)/G_i. The longitudinal eigenvalue KL is NOT used: it is a check.
No use of the lead's labels r, bn, of its conformal map or of `szekeres/` code. Masks: core = cells with KT equal
to the central value, outside = cells with H_T t_i = 2/3 (EdS), shell = the rest (tolerances in the script).
The non-spherical signal: on a shell (bin of s) 1/c is linear in bn with bn = +-|b| at the extremes, so the LTB
element of the same shell has 1/c_LTB = midpoint of the extremes of 1/c in the bin.

- V1.0 (self-check of the reference): at tau = 0 the KL predicted from (KT, rho_i) equals the file's KL to
  better than 1e-6 H_i in every cell, and my K(tau = 0) equals the code's dumped K to 1e-12 H. Refuted otherwise:
  then the data are not simultaneous-bang Szekeres or my reading is wrong, and V1.1-V1.4 are void.
- V1.1 My shell rms |K - K_ex|/H(tau) reproduces Table V (N64: 0.0268, 0.0616, 1.04 at tau 10, 20, 30; N128:
  0.0043, 0.0123, 0.045; N256: 0.000277, 0.001 at 10, 20) to within 10 per cent (my mask differs at the
  shell's edges). Refuted if any row differs by more than 20 per cent.
- V1.2 The orders log2(e_N/e_2N) of the shell K error reproduce Table V within 0.15 (64->128: 2.64, 2.33, 4.53;
  128->256: 3.96, 3.62 at tau 10, 20); 128->256 at tau 30 (N256 continuation) between 3 and 4.5.
- V1.3 The error is at least 10 times below the signal max for N256 and 5 times for N128 at tau 10-30
  (prediction P20 as written); my signal max within 15 per cent of Table V's (0.68-0.69, 1.42-1.43, 3.45).
- V1.4 Where each member stops: N64 guard stop at tau = 30.25, N128 at 37.47, N256 reaches tau = 40 with
  finite fields (from the guard files and histories).

### V2 Triaxial runs S1L (mu = 0.3) and S1L-h (mu = 0.15), Newtonian controls

Reference [derivation, this entry]: dust in EdS, synchronous comoving gauge, linear growing mode D = a on every
scale (no k dependence for dust in that gauge [BACKGROUND]); first order Lagrangian x = q + a psi(q), so the
first crossing along the principal axis of the largest eigenvalue lambda_1 of -d psi_i/d q_j (at a = 1) is at
a_sc = 1/lambda_1. Clock: H_i = 1 at a = 1, so t_c = (2/3) a^(3/2) and coordinate time t = t_c - 2/3 (lapse ~ 1
in the background): a = (1 + 1.5 t)^(2/3). Horizon entry of the peak scale r_m: r_m a H = 1, a H = a^(-1/2),
a_H = r_m^2, t_H = (2/3) r_m^3; t/t_H = (1 + 1.5 t)/r_m^3. lambda_1 is read from snapshot 0 by me (centred
differences of x - q at the lattice point at the centre), r_m from the data's id.json.
- V2.1 My lambda_z(S1L) = 0.063 +- 0.002 and lambda_z(S1L-h) = 0.0315 +- 0.001 (first order in mu), giving
  4.35 +- 0.15 and 12.3 +- 0.5 t_H. Refuted outside.
- V2.2 My sign-of-Jacobian reader (forward differences on the periodic lattice, unwrapped) gives the S1L bracket
  (6.19, 7.21] t_H and the S1L-h bracket (13.85, 14.36] t_H, first cell at the centre, first axis z.
- V2.3 My reader on the Newtonian members gives a first crossing of N-z128 in (3.59, 3.73] t_H, N-z later
  (~4.5), so the converged Newtonian time is below Zel'dovich and GR lags both.
- V2.4 Hence: A2 as written (band [3.4, 5.0] t_H) FAILS; A2H (band [12.5, 15.2]) HOLDS; I expect the probe
  proper time on the last uncrossed slice of S1L-h above 13.5 t_H.

### V3 Periodic chain P0L6 (A-20261125-044641-7d5bd16)

- V3.1 With my own trajmet reader, areal radius R = sqrt(g_T) r of the round sphere through each tracked
  particle, and my own cycloid for each shell (M, E, bang time from the reference file B, checked by me at
  tau = 0 against the code's initial R and dR/dtau), the shells whose initial r exceeds 1.5 follow R_B(tau)
  within 1 to 4 per cent (max |R/R_B - 1|) up to their own trapping or the end of the run; inner shells worse.
  Refuted if an outer shell departs by more than 6 per cent before it is trapped.
- V3.2 horizon_status_0.txt: a surface is accepted (found = 1) near t = 118.1 whose area radius exceeds 2M of
  every shell inside it at that time (not trapped: false acceptance), and from t = 136 the finder reports no
  surface (found = 0 at every search) while tracked shells have R < 2 M_B (trapped spheres exist).

### V4 Item C3: ||H||/||16 pi E|| on the x line (weights x^2 dx, x > 0; no horizon before t = 5)

- V4.1 t = 0: top hat (K4-ref, card members A, B) above the bound 0.1 on both meshes; smoothed S2c-A 0.006,
  S2c-B 0.0006 (order ~3.4 between A and B); S1, S2 (TSC/PCS clouds) larger than S2c.
- V4.2 t = 0.25 to 1: every member grows to 0.05-0.15 by t = 1; the order between meshes A and B is below 1
  (0.13 -> 0.10 at t = 1 for S2c); C3 as written FAILS.
- V4.3 S2c-A8 (eight particles per cell) equals S2c-A within 10 per cent at t = 1 and 2 (sampling excluded),
  and differs at t = 0 (0.06 against 0.006) by its deposit.

### V5 Table V and two spot checks of the earlier verifier's rows

- V5.1 Every run id of Table V has a finished manifest and its output holds the number to the digits printed.
- V5.2 Spot checks (conv_ball A-20261121-120257-a2eb839): mesh A Delta t_det = 0.193 and mesh C 0.0166 are in
  the run's numbers file and follow from the raw horizon summary of the members within 1e-3 M.
