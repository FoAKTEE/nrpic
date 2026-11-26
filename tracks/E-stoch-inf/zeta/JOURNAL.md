# JOURNAL of package zeta (Track E, gate G3)

## entry-1 (2026-11-25 07:40 PST, lead of E, batch 19): the 32^3 mirrored pairs for Z0 and Z2, before the run

Four runs (`inputs/pairs32.list`): 32^3 USR deck `usr/inputs/usr_base.athinput` with nmax2 = 64, the deck's
seed, noise_mode_scale = +-1/4, +-1/2, dumps at t = 0 and tlim with the metric, release processor build
`.work/build_cpu_v07/src/athena`, two at a time on two cores.
- P1 (health): all four reach tlim with exit 0 and finite fields; each takes between 2 and 30 minutes.
- P2 (mirror): the box means of phi at tlim of the + and - members differ by less than 1e-3 of the rms of
  their difference field (the mean is even in s; the field's odd part has no k = 0 mode).
Z0-Z2 themselves are judged by the reader against `../g3/JOURNAL.md` entry 4 once it exists.

## entry-2 (2026-11-25 07:50 PST): predictions for `pairs_check.py`, written while the pairs run, before any reading

`pairs_check.py` reads the last dump of each member: P2 as in entry 1, and a preview of the second order of
the linear variable R_lin = (H/Pi) dphi (not a criterion; Z0-Z2 judge zeta once the reader exists).
- P3: the local quadratic coefficient a of the even part on O^2 - <O^2> agrees between s = 1/4 and 1/2
  (a(1/2)/a(1/4) in [0.8, 1.25]); refuted outside: then the even part of R_lin holds a part that is not a
  local quadratic of the odd part (as the per-run part of G2's constraints), and Z2's 2 per cent bar needs
  the same split for zeta.
- P4: skewness of the odd part below 0.01 in magnitude at both amplitudes (32^3 box, 32768 cells: one-box
  noise about 0.014, so only a gross error shows).

## entry-3 (2026-11-25 07:52 PST): outcomes of entries 1-2

Runs E-20261125-153148-cfad424 (four 32^3 runs, 544-552 s each on one core) and reading
E-20261125-155027-a9037d9 (`pairs_check.json`, `fig_pairs_check.png` looked at; the s = 1/4 points lie
under the s = 1/2 points in both panels).
- P1 HOLDS: all four reach tlim = 10.4375 with exit 0 and finite fields.
- P2 HOLDS: |<phi>(+) - <phi>(-)| / rms(difference) = 7.3e-10 (s = 1/4) and 0 (s = 1/2).
- P3 HOLDS: a = 1.83848e-4 (s = 1/4) and 1.83856e-4 (s = 1/2), ratio 1.00004; the residual of the even part
  about a (O^2 - <O^2>) is 0.7797 of its rms at both amplitudes. The even part of R_lin scales exactly as the
  square of the odd part (no part that does not scale, at this level), but only about 40 per cent of its
  variance is the LOCAL quadratic of O; the rest is non-local (products of modes at other positions).
- P4 HOLDS: skewness of O 0.00746 at both amplitudes (the same realisation, scaled).
Reading [JUDGEMENT]: a sigma_O = 6.2e-6 at s = 1/2 means a local-quadratic skewness of R_lin of about 6 a
sigma = 4e-5 in this 32^3 box; the 128^3 box gave a_R = 2.8e-4 (review run E-20261125-131002-ceefa2f)
against 0.0078 for one-patch delta N. With R35 (one-patch phi at N_f already skewed), Z2 for zeta and A4's
direct comparison will tell whether NR's d phi lacks the one-patch non-Gaussianity. Inputs for Z0 and Z2
exist now (the pairs); the reader with the map is the next step.

## entry-4 (2026-11-25 08:08 PST, lead of E, batch 20): the zeta reader, Z0-Z2, the TO VERIFY of 4d.3, A4 preview; predictions before any reading

`zeta_reader.py` (new): zeta = -1/2 ln(chi/<chi>) + Delta N_bg(phi, v) - <same> per cell at the last dump, with
v = dphi/dN = Pi/H_cell, H_cell = -K/3 (alpha = 1 on the geodesic slice; checked), Delta N_bg the e-folds of a
homogeneous Friedmann-Klein-Gordon universe (G = 1, the deck's potential) from (phi, v) to phi_e: fourth-order
Runge-Kutta in phi as the independent variable (fixed number of steps, all cells at once), phi_e the field of
the background (own integration from the deck's phi0, pi0 at N*) at N_e = N* + 15. The independent
integrator of Z1: scipy DOP853 in cosmic time with an event at phi_e, scalar per state (other variables, other
scheme, other code path). Order-of-magnitude expectation [JUDGEMENT, from the landmarks file
`usr/results/landmarks.csv`]: at N_f the field sits 4.07e-5 (code units) beyond the inflection point on the
attractor (eps2 = -0.0276 against 2 v/x = 0.0278), where Delta N ~ 1/x, so the map's local coefficient is
a_map = v/x = 6.95e-3 and the one-point skewness of zeta from the map is 6 a_map sigma (128 band: 0.021, the
reference's 0.0199; 32^3 band |n| <= 8: about 0.003).
- LM (TO VERIFY of 4d.3): with phi_code = phi_Mpl / sqrt(8 pi), t_code = H* t and lambda_code = 8 pi Lambda / H*^2,
  HiggsInflection(Lambda = 1.86e-6, v = 0.198) at phi0 = -1.2, N* - N0 = 3 gives the deck's vev, lambda (to 1e-6
  relative), phi0, pi0 at N* (1e-6 relative), and the landmarks (eps2 = 0 up, eps2 = 3 up, inflection point,
  eps2 = 3 down, eps2 = 0 down) of `sdn/linear.ClassicalBackground` agree with those of the own code-unit
  integration within 1e-4 in N. Refuted outside.
- Z0: rms(O_zeta + O_R)/rms(O_R) about 1e-4 at s = 1/4 (bar 1e-3).
- Z1: first and second five-point coefficients of the reader's map within 0.1 per cent of DOP853 (bar 1 per
  cent) along phi, along Pi, and along the box's (d phi, d Pi) relation, eps = rms of the box's d phi (and d Pi).
- Z2: a_zeta(1/4) and a_zeta(1/2) within 2 per cent; a_zeta in [6.0e-3, 8.0e-3]. Part (iii) as written in A3
  (a_zeta within 2 per cent of the independent map's quadratic coefficient a_map): I expect it to FAIL narrowly
  or pass at the edge, because the field's own even part adds: zeta = -(d phi_1 + d phi_2)/v + a_map zeta_1^2, so
  a_zeta = a_map - a_R with a_R = 1.84e-4 of R_lin (entry 3), a 2.6 per cent shift. Pre-registered here, before
  any reading, as Z2(iii'): |a_zeta - (a_map - a_R)| / a_map below 0.5 per cent, a_R measured on the same pairs.
  Z2(iii) is judged as written; (iii') is the test of the map that (iii) meant. The scope is not changed here.
- A4 preview (32^3, not the judged A4): the box's d phi at N_f against a reference of the same band (ref_spec.py
  with NLAT = 8, s0.01_lattice, 1e6 paths): variance ratio box/reference within the box's Gaussian sample
  scatter (about 5 per cent for one 32^3 box: computed from the mode count, written with the outcome); the
  intrinsic skewness 3 <O^2 E>/sigma_O^3 / s of the pair (sample variance cancels at leading order), for d phi
  and for zeta, against the reference's skew_phi(N_f) and skew(dN at N_e): consistent within the reference's
  two standard errors (about 0.005 at 1e6 paths).

## entry-5 (2026-11-25 08:15 PST): smoke of the reader (unregistered), before the registered reading

An unregistered smoke run at 400 RK4 steps (scratch/E-stoch-inf/tmp/smoke_zeta) ran end to end after entry 4
was written. Seen there, and therefore not a prediction any more: Z0 3.0e-5; a_zeta 6.763e-3 at both
amplitudes; Z2(iii) -2.9 per cent, (iii') -0.25 per cent; LM within 4e-7 in N; Z1 along phi and along the box
relation within 2e-5, but along Pi alone the second coefficient differs by 14 per cent, where it is 1.2e-9 in N
at eps = box rms. Added after that smoke and before the registered run, as diagnostics not judged: Z1 along Pi
at 10 and 100 times eps. Prediction for them: the disagreement falls at least tenfold at 10 eps if it is the
precision floor of the finite difference (refuted if it does not fall: then the two maps differ along Pi and
the reader's Pi dependence must be checked before it judges anything). The registered run uses 4000 steps.

## entry-6 (2026-11-25 08:22 PST): outcome of entries 4-5 (run E-20261125-161456-8d3f43c), and one prediction before a rerun of Z1

Reading E-20261125-161456-8d3f43c (4000 RK4 steps; `zeta_tests.json`, `fig_zeta_tests.png` looked at: O_zeta on
the diagonal against -O_R; the even part of both amplitudes on one line, closer to a_map - a_R than to a_map;
Z1 errors per direction).
- LM HOLDS: the deck is HiggsInflection(1.86e-6, 0.198) mapped to code units: vev, lambda, phi0, pi0 equal the
  prediction to 1.1e-14 relative (H* = 9.3623e-6 Mpl); landmarks within 1.3e-9 in N (USR onset 1.2e-12,
  inflection point 6.8e-11, USR end 1.3e-9), except the eps2 = 0 down crossing, 4.0e-7 (a flat zero of
  dln eps1/dN), all far below 1e-4. N at the deck's tlim = 10.000000000000 after N* (N_f). The TO VERIFY of 4d.3
  is settled [VERIFIED].
- Z0 PASSES: 3.0e-5 at s = 1/4 and at 1/2 (bar 1e-3; predicted about 1e-4). alpha - 1 at most 3.0e-13; every
  cell rolls forwards (v_min 2.83e-7).
- Z1: along phi and along the box relation PASS (first coefficient 2.7e-9 and 6.8e-11, second 7.0e-5 and 4.7e-5);
  along Pi alone the second coefficient FAILS as written (0.142 against 1 per cent), first passes (2.7e-6).
  The diagnostics (entry 5): 5.1e-3 at 10 eps, 3.0e-6 at 100 eps: the disagreement falls 28-fold and then
  4700-fold, so it is a precision floor (entry 5's prediction holds). Which side: the reader's second
  coefficient per unit eps^2 is 1.33418e-9, 1.33414e-9, 1.33413e-9 at 1, 10, 100 eps (smooth); DOP853's is
  1.16849e-9, 1.34097e-9, 1.33414e-9: the floor is the independent integrator's (N = ln a at an event, about
  1e-10 in N), not the reader's. Not yet a cause: tested next.
- Z2: (i) PASS: a_zeta = 6.76274e-3 (s = 1/4) and 6.76271e-3 (s = 1/2), ratio 0.999996; inside the predicted
  [6.0e-3, 8.0e-3]; a_zeta sigma_lin(128) = 3.3e-3 inside g3 entry 4's [0.002, 0.008]. (iii) as written FAILS:
  a_zeta/a_map - 1 = -2.89 per cent (a_map = 6.96379e-3, DOP853 along the box relation; predicted to fail by
  about 2.6). (iii') PASSES: (a_zeta - (a_map - a_R))/a_map = -0.25 per cent (bar 0.5).
- A4 preview HOLDS: box variance of d phi at s = 1 over the 8-band reference's (E-20261125-160705-5f75bb4) =
  1.031, one box's Gaussian scatter 3.1 per cent; intrinsic skewness of d phi 7.4e-5 against 0.0002 +- 0.0020;
  of zeta 0.00270 against the reference's delta-N skewness 0.0026 +- 0.0020; zeta variance 1.032 of the
  reference's. The 32^3 box carries the one-patch non-Gaussianity through the map; its field is Gaussian to the
  reference's precision.

Prediction for the rerun with a second independent map (DOP853 in N on (phi - phi_e, v), event at phi_e, rtol
3e-14; added to `zeta_reader.py`, the first one kept): along Pi alone at eps = box rms the reader agrees with it
within 1 per cent in both coefficients, and along phi and the box relation within 0.1 per cent. Refuted if along
Pi the second coefficient still differs by more than 1 per cent: then the floor is not the t-integrator's alone
and the reader's Pi dependence is examined before it judges anything.

## entry-7 (2026-11-25 08:33 PST): the rerun of entry 6 was stopped; Z1 along Pi stays failed as written

Run E-20261125-161757-fb0eb95 (the reader with the second independent map, DOP853 in N at rtol 3e-14) ran Z0 and
Z2 again (identical to E-20261125-161456-8d3f43c) and then spent over ten minutes in the 25 Z1 states; stopped by
`nrpic-run stop` at 08:29 (status failed, on record). A timing check outside the record: at rtol 1e-13 one call
needs 3.4e6 right-hand-side evaluations (40 s): in N the attractor equation is a small difference of two large
terms and the step control cannot meet tolerances near rounding. Entry 6's prediction was not tested. The
second map is now off by default (ZETA_USE_DOPN=1 turns it on). Status of Z1: FAILED as written along Pi alone at
eps = box rms (0.142); passes along phi, along the box relation, and along Pi at 10 eps (5.1e-3) and 100 eps
(3.0e-6). The reader's own coefficient is the same at 1, 10, 100 eps to 4e-5; the independent integrator's moves
by 15 per cent: the evidence points at the independent integrator, but no cause is named until a test that could
fail (a quadruple-precision or a series solution of the attractor map along Pi). Since the box's perturbations lie
on the box relation (corr(d phi, d Pi) = 1 - 6e-12), the Pi-alone direction carries no weight in zeta; whether
the reader judges G3 runs with Z1 failed in that direction is put to the orchestrator.

## entry-8 (2026-11-25 18:25 PST, lead of E, batch 23): the verifier's two changes to the tests (decision 0042 item 1), prediction before the run

Decision 0042 item 1: the failure of Z1 along the momentum alone (rel c2 = 0.142 against DOP853, run
E-20261125-161456-8d3f43c) is a failure of the test's reference, below its round-off; it stays on record as failed as
written, with that cause; expected values come from the variational coefficients at the box's own background.
`z1_variational.py` applies both changes of g3/zeta_verify/README.md Requests 1-2: expected c1 = g.d and c2 = d.Hess.d
from zv_lib's variational equations (long double, RK4 in N, steps 1e-3 and 5e-4), at the lockstep record of the 32^3
pair at N_f (zp4/usr.sf.00001.modes), with the cells' convention v = Pi/H at fixed K; the reader's map unchanged
(V, dV, map_rk4 verbatim through ast, 4000 steps), same eps as the record. Z2(iii) and (iii') with a_map of the same
derivatives along the box relation.
Prediction (refuted outside): Z1 passes in all three judged directions, |rel c1| below 1e-6 and |rel c2| below 2e-4
(the verifier: reader +3.4e-5 along Pi, -6.1e-5 along phi and the relation, at the lead's state); the diagnostic
directions Pi x10, x100 agree to the same level. Z2(iii) about -2.87 per cent (fails as written; A14 (b) foresaw it),
(iii') about -0.23 per cent (passes the 0.5 per cent bar) (the verifier's lockstep values, VERIFY.md section 2).
