# JOURNAL of package stage/G2/verifier (E-stoch-inf, fresh verifier of gate G2)

## Entry 1, 2026-11-25 02:20 UTC: set-up and predictions (before any test or analysis ran)

Task: recompute, with own readers and own reference, the number each criterion of
`spec/scope/SCOPE.md` section 4c is judged by, on the release ladder of `g2prod` (queue file
`g2prod/queue.txt`; run ids from `runs/*/manifest.json`); processors only, at most 6 cores,
no card time. Not read before this entry: g2prod JOURNAL entries 2-4, `stage/REVIEW-wave3.md`,
`stage/G2/CHECKLIST.md` (and the rest of `stage/G2/`). Read: SCOPE 4/4b/4c, usr JOURNAL
entries 2, 9-10 (pre-registration of U-A0..U-A6), g2prod README, queue.txt, JOURNAL entry 1
(the per-run predictions), the interface texts `scalar_field{,_2,_3}.md` (dump layout,
record columns, sources), P1 (`PRD_v2.tex`:518-545) and TH (`appendix.tex`:505-525) for the
extraction of R^NR.

Runs (release card build core-v0.6, deck `g2prod/inputs/usr_prod.athinput`):

| Label | Run id | s | seed | N |
|---|---|---|---|---|
| U256ap | E-20261121-211214-0377aab | +1 | A 20261115 | 256 |
| U256am | E-20261121-214629-da64fb7 | -1 | A | 256 |
| U320ap | E-20261122-023427-0ac3f0b | +1 | A | 320 |
| U320am | E-20261122-110042-ffcb4b3 | -1 | A | 320 |
| U256bp | E-20261122-033244-564627b | +1 | B 20261116 | 256 |
| U256bm | E-20261122-071038-d9f933b | -1 | B | 256 |
| U256hp | E-20261122-113320-9bbb52b | +1/2 | A | 256 |
| U256hm | E-20261122-152116-0542096 | -1/2 | A | 256 |
| U256nc | E-20261122-190341-0419be6 | +1, noise_pi_sign = -1, to t = 3.75 | A | 256 |
| U256qp | E-20261123-230004-861aea7 | +1/4 | A | 256 |
| U256qm | E-20261123-230507-a6246b1 | -1/4 | A | 256 |
| window scan (U-W) | card job output E-20261120-222424-0eb754b (scouting build core_scalar-2), 128^3, nmax2 = 1024 | +-1 | A | 128 |

Own tools (`scripts/`): a reader of the NRSFDMP2 layout written from `scalar_field_2.md`
section 4 (sequential reads of one variable at a time, never a whole dump); the extraction
R^NR_n = Phi_n + (H/Pi_b) delta phi_n with Phi_k = (1/2)(X_k/<X> - 1) + (1/4) k_i k_j/k^2
(gt_ij - delta_ij)_k and H/Pi_b = -<K>/(3 <alpha> <Pi>) of the dump (TH appendix.tex:515-521,
P1:524-526); coefficients c_n = F[n] exp(-i pi (n_x + n_y + n_z)/N)/N^3 on the hemisphere of
`scalar_field.md` 7.1 (cell centres); amplitudes alpha_n from the track's own Philox
re-implementation `noise/ref/philox_ref.py` (not core's twin; core's twin only as a
cross-check on a sample); background and continuum mode functions integrated here from
(phi0, pi0) of the deck and the mode file at N* (DOP853, rtol 1e-12), not taken from
`usr_reference.json` or the `.modes` lockstep record (both only compared).

Interpretations fixed now (before any number is seen) where 4c leaves a choice:
- "one 256-cell dump in memory at a time": one variable of each member of a pair at a time
  (2 x 134 MB at 256^3); a full dump is never loaded.
- U-A0 landmarks (usr JOURNAL entry 2): USR onset (eps2 rises through 3), eps2 maximum, USR
  end (eps2 falls through 3), eps1 minimum, N_f; dN = record e-folds (column 3, cubic
  interpolation in time) minus the reference N(t). Threshold 1e-5 at every landmark.
- U-A1: max over all record rows of |<X>/X_ref - 1| for X = phi, Pi, K, every release run.
- U-A3: per-mode ratio |c_n|^2/|s L^-3/2 W R alpha_n|^2 for k <= 3 dk (61 modes) at N_f, on the
  single run s = +1 and on the odd part; judged on the max of |ratio - 1| (10 percent).
- U-A2n and U-R (iii): sqrt(sum |E_n|^2 / sum |O_n|^2) over the band modes (|n|^2 <= 4096);
  the same over k <= k_max/2 reported.
- U-A4'(d): the control has no mirrored partner, so its "odd part" is its H' (mean removed);
  ratio max_dumps rms(H'_nc) / max_dumps rms(O_H) over the dumps with cN <= ln 32; also
  rms(H'_nc - E_H) with E_H the even part of the proper pair, and pointwise ratios.
- U-W: per shell q, shift_w(q) = P_w(q)/P_b(q) - 1 of the odd-part shell power; the
  NR-vs-reference bound per shell is |P_b/P_ref - 1| + |P_w/P_ref - 1| (same alpha, same
  linear reference R(N_f) for every window, because W(N_f) = 1 for all band modes).
- U-S one-point rms: band-limited (from the coefficients, |n|^2 <= 4096) as the judged
  number, full lattice reported.

Predictions (each refuted outside its range):

- V0 (reader and extraction on an analytic field): a synthetic NRSFDMP2 file with a known
  set of plane waves in phi, chi and gt_ij returns the coefficients of R^NR to 1e-13 of
  their rms, nothing outside the set above 1e-14; the floor formula of 4c returns a known
  floor f within 1 percent on synthetic odd parts o_s^2 = s^2 l^2 + f^2.
- V1 (own reference): H(t = 0) from the Friedmann constraint with phi0, pi0 of the deck = 1
  within 1e-9 (time unit 1/H*); USR from cN = 2.52 to 6.55 (SCOPE 2, +-0.01); eps1 minimum
  near 1e-12; lattice rms sqrt(L^-3 sum |W R|^2) at N_f = 0.89366 within 2e-4
  (`usr/results/usr_reference.json`); my R_q(N_f) against the lockstep `.modes` record at
  N_f within 3e-3 for every shell (RK4 phase error 2.55e-3 at 64 dk, g2prod entry 1).
- V2 (alpha): philox_ref and core's twin give identical alpha_n on a sample of 2000 modes.
- V3 (extraction at t = 0): R^NR_n of U256ap at t = 0 equals L^-3/2 W(N*) R(N*) alpha_n
  within 1e-9 relative for the modes with W > 1/2 (|n| = 1), sign included.
- V4 U-A0: |dN| < 1e-6 at every landmark, every release run. Pass.
- V5 U-A1: largest relative deviation in <Pi>, between 1e-7 and 5e-4, late (cN > 5); <phi>,
  <K> below 1e-6 relative. Pass on every run (control included up to t = 3.75).
- V6 U-A2' seed A: max D_n (k <= 32 dk) = 1.09e-4 +- 10 percent; to k_max <= 5e-3; seed B
  <= 2e-4; half pair within 5 percent of the s = 1 value; quarter pair likewise. U-A2n of
  the +-1 pair 2.5e-4 +- 10 percent; halves at s = 1/2, quarters at s = 1/4 (+-5 percent).
- V7 U-A3: |ratio - 1| <= 1e-2 on single runs (scouting 0.9923-1.0016), <= 1e-3 on odd parts.
- V8 U-A4'(a): even halving of H within 3.95-4.05 at every judged dump; of M within the
  band except at one dump near cN = 6.5 (the failure on record named by the task and by
  queue.txt). Quarter pair: if the miss is a higher order in s (E = a s^2 + b s^4), the
  deviation from 4 of the 1/2 -> 1/4 ratio at that dump is about a quarter of that of
  1 -> 1/2 and of the same sign; if it comes from a part that does not scale like s^2 (floor,
  card rounding), the deviation of the 1/2 -> 1/4 ratio is larger than that of 1 -> 1/2.
  I do not know which; the second would refute "higher order in s".
- V9 U-A4'(b): f/o_{s/2} below 0.05 at every dump of the entry; f grows relative to the odd
  part only late (cN > 7).
- V10 U-A4'(c): records <|H'|/[H]> max 2e-12 to 5e-12 at s = +-1, below 1e-9 on every
  release run except the control; <|M|/[M]> max 2e-2 to 3e-2 at s = +-1, 4e-2 to 6e-2 at
  s = +-1/2 and 8e-2 to 1.2e-1 at s = +-1/4, i.e. the quarter pair may exceed the bar 1e-1
  (the bar was set before the quarter pair existed). Control: far above both bars.
- V11 U-A4'(d): ratio >= 1e3 (1e3 to 1e5).
- V12 U-R: (i) factor 2.4-4.5; (ii) shell power within 1e-3 (k <= 32 dk), 1e-2 (to 64 dk);
  (iii) even/odd within 5 percent.
- V13 U-S: band rms of seed B within 3e-3 of 0.89366; equal to its own realisation's lattice
  sum within 2e-3.
- V14 U-W: max shift 1.9e-4 (+-20 percent) to k_max/2 = 16 dk and 9.1e-3 (+-20 percent) to
  32 dk; every shell within its bound.

## Entry 2, 2026-11-25 02:35 UTC: outcomes of V0-V7, V10, V12-V14 (runs listed per item)

- V0 (run E-20261125-022126-26671c3): reader reads the synthetic file back bit for bit; the
  R^NR coefficients of the 40 planted modes agree to 9.6e-13 of their rms and nothing outside
  the set exceeds 9.5e-12. **Prediction (1e-13, 1e-14) refuted**, for a cause the same run
  could have refuted: with all amplitudes 1e3 times larger the errors fall to 4.4e-15 and
  1.1e-15, so the 1e-12 is the rounding of the stored O(1) fields (gt_ii = 1 + 1e-7, ulp
  2.2e-16) relative to coefficients of 3e-5, not the reader. Full-lattice rms = band rms to
  1e-16. Floor formula: recovered f/f_true = 1.0014 (independent floors) and 1.0015 (common
  floor). V2: alpha of philox_ref and of core's twin identical on 2000 modes of each seed.
- V1 (run E-20261125-022507-b13c79b; the first try E-20261125-022137-182e82c was stopped by
  me at 39 GB of dense output and is on record as failed): H(t = 0) = 1 + 4e-16; USR from
  cN = 2.523421 to 6.550320 (SCOPE 2: 2.52, 6.55); eps1 minimum 9.716e-13 at cN = 8.331;
  N(tlim) = 10 + 1.7e-13; own lattice rms at N_f 0.893707 (0.89366 given; 5.3e-5 apart);
  reference self-error (rtol 1e-12 against 1e-10) 9.8e-10 relative; lockstep `.modes` of
  U256ap at N_f against mine: 2.55e-3 at the top shell (q2 = 4096), 8.0e-5 for q2 <= 1024,
  1e-7 at the lowest shells (fig_reference.png, looked at: k^5 growth). Holds.
- V3 (run E-20261125-022710-0eb5db0): R^NR at t = 0 equals L^-3/2 W(N*) R(N*) alpha_n with
  the same sign to 5.0e-12 (U256ap) and 7.4e-12 (U256bp) on the 3 modes with W > 1/2. Holds:
  the extraction, phase convention, alpha and slice agree.
- V4 U-A0 (run E-20261125-022200-68c072e): max |dN| over the landmarks 1.61e-9 (256^3),
  6.6e-10 (320^3), 4.3e-10 (control to t = 3.75); all record rows the same. Holds.
- V5 U-A1 (same run): max relative deviation 4.17e-5 in <Pi> at N_f (s = +-1), 1.04e-5
  (+-1/2), 2.52e-6 (+-1/4): second order in s, at cN = 10; <phi> 1.2e-9, <K> 2.4e-11.
  Holds.
- V10 U-A4'(c) (same run): <|H'|/[H]> max 2.89e-12 (A +-1), 1.73e-12 (B), 3.03e-12 (320),
  1.28e-12 (+-1/2), 1.19e-12 (+-1/4), all at cN < 0.4: holds. <|M|/[M]> max 2.52e-2 (256^3
  at s = +-1, +-1/2, +-1/4 alike, at cN = 6.64), 8.09e-3 (320^3). **Prediction for s = 1/2
  and 1/4 refuted** (I predicted 4e-2 to 1.2e-1 from the note in 4c that the record doubles
  at s = 1/2): the maximum does not depend on s, so at the end of USR it is the first-order
  part (truncation, falls by 3.1 from 256 to 320); only the late values scale (at N_f 2.13e-3,
  3.84e-3, 5.60e-3). No run reaches the bar 1e-1. Control: 1.28e-7 and 0.50.
- V6 U-A2' (run E-20261125-022710-0eb5db0): max D_n (k <= 32 dk) 1.0894e-4 (A, mode
  (0,32,0)), 1.0871e-4 (B, (0,0,32)); to k_max 4.506e-3 (both, (64,0,0)). Holds for A and B.
  **Half and quarter pairs: 1.242e-4 and 1.289e-4, not within 5 percent of 1.09e-4 (refuted)**:
  at the axis modes D(s) = 1.293e-4 - 2.04e-5 s^2 fits all three, i.e. a third-order part of
  the odd part lowers D at s = 1 (follow-up below). U-A2n (band) 2.877e-4 (A), 2.874e-4 (B):
  **prediction 2.5e-4 +- 10 percent refuted for the band**, holds for k <= 32 dk (2.53e-4);
  it halves exactly (1.438e-4, 7.19e-5). Removing the gt_ij term of Phi changes max D by 1e-8
  (gt part 1.3e-7, chi part 4.6e-7 of the rms of R^NR: R^NR is carried by delta phi).
- V7 U-A3: single runs 0.99230-1.00161 (A), 0.99678-1.00185 (B); odd parts 0.999916-0.999919
  (s = 1), 0.99998 (1/2), 0.999995 (1/4): the odd-part deficit 8.4e-5 is third order. Holds.
- V12 U-R: (i) 1.0894e-4 / 5.182e-5 = 2.10 (**prediction 2.4-4.5 refuted**, criterion
  2.0-4.5 met by a margin of 5 percent); the 320 maximum sits at (13,15,-20), a mode whose
  |alpha| is in the lowest 1e-4 of all; (ii) shell power 1.18e-4 (k <= 32 dk), 4.6e-3 (to 64
  dk); (iii) even/odd 2.87664e-4 against 2.87654e-4, 3.5e-5 apart. Holds.
- V13 U-S: band rms of U256bp 0.894109, 4.49e-4 above 0.89366 (bar 5e-3); its own
  realisation's lattice value 0.893953 (NR 1.7e-4 above it). Holds.
- V14 U-W (run E-20261125-022612-d2d99fa): max shift 1.870e-4 (k <= 16 dk, g2), 9.13e-3 (k <=
  32 dk, g2); per-mode errors of each window equal the package's table to its digits. Holds.
  The per-shell clause "less than the NR-vs-reference bound" uses the bound |e_w| + |e_b|,
  which holds by construction (the window README says so): 4 shells of s10 exceed it by the
  factor 1/(1 + e_b) only.
- Figures looked at: fig_records.png, fig_reference.png, fig_modes.png, fig_window.png (below).

Prediction for the follow-up `extra_modes.py` (before it runs): the Richardson-in-s^2 linear
part L from s = 1, 1/2 agrees with that from s = 1/2, 1/4 to below 1e-5 of |p| for k <= 32 dk;
max D_lin (k <= 32 dk) about 1.3e-4 at an axis mode |n| = 32; the third-order share at s = 1
is at most about 4e-5 (the low-k plateau of fig_modes.png); D_lin at the axis modes falls from
256 to 320 by 2.4 to 3.8 (order 4 to 6). Refuted outside these ranges.

## Entry 3, 2026-11-25 02:50 UTC: outcomes of V8, V9, V11 and of the follow-up on max D_n; prediction for the floor follow-up

- Follow-up on max D_n (run E-20261125-022918-f71678d, fig_extra_modes.png looked at): the
  Richardson-in-s^2 linear parts from (1, 1/2) and (1/2, 1/4) agree to 3.3e-7 of |p| (holds);
  max D_lin (k <= 32 dk) 1.306e-4 at (0,0,32) (holds); third-order share at s = 1 up to 5.2e-5
  (median 4.2e-5; **I predicted at most about 4e-5: refuted by 30 percent**); it exceeds the
  linear error on 63 percent of the modes k <= 32 dk and sets the whole plateau below 25 dk.
  D_lin at the axis modes |n| = 32 falls from 1.306e-4 (256) to 4.53e-5 (320, third-order part
  of 256 subtracted): factor 2.88, order 4.7 (holds, 2.4-3.8).
- V8 U-A4'(a) (run E-20261125-022309-d346f12, constraints.json, fig_constraints.png looked
  at): pairs at equal recorded times (|dt| = 0 at all 21 dumps). H: judged dumps 0, 5-12, all
  within 4 +- 0.05 (worst 4.042 at dump 9, cN 4.54): holds. M: judged dumps 0, 4-13; dump 13
  (cN = 6.525) gives 3.9245, outside the band; all others within 0.013 of 4. **The failure on
  record is reproduced.** Quarter pair at that dump: 1/2 -> 1/4 halving 4.127 with the floor
  from (1/2, 1/4) (not judged, e_q < 3 f): deviation of the opposite sign and larger, so my
  "higher order in s" alternative is refuted. The three-amplitude fields: rms(D2)/rms(D1) =
  0.997 and corr(D1, D2) = -0.245 at dump 13, and 1.000 / -0.235 at every dump 1-13 for H and
  M: exactly the values of a part F_s of the even part that is independent between the
  pairs and of the same rms at every s (D1 = F_1 - 4 F_1/2 gives ratio 1 and correlation
  -4/17 = -0.235); an s^4 term would give 1/16 and +1, a common s-independent part 1 and +1.
- V9 U-A4'(b): f/o_{s/2} for M is 1.0 at dumps 1-5 (the odd part is all floor there: o = 5.4e-12
  at every s at cN = 0.53), 0.43 at dump 6, 0.031 at 7, 1.5e-3 to 9.3e-3 at 8-13, 0.05-1 after;
  H likewise. **Prediction (below 0.05 during the entry) refuted for cN < 3**: early on the odd
  parts of both constraints do not scale with s at all.
- V11 U-A4'(d): ratio of the maxima over cN <= ln 32 (dumps 0-6) 2.38e5 (H' of the control
  1.70e-6 against the odd part 6.9e-12); pointwise 2.4e5 to 1.7e6 after t = 0 (26 at t = 0,
  before any kick). Holds (>= 1e3). fig_control.png looked at.

Reading [JUDGEMENT, to be tested next]: at dump 13 the odd part of M (1.09e-11) is ten times
its even part, and the 4c floor f^2 = (4 o_{1/2}^2 - o_1^2)/3 is then a difference of two
numbers equal to 1e-4, which a third-order part of the odd part (O = s L + s^3 T) shifts by
about -(1/2) L.T; f = 5.05e-14 there, while the noise level of the even part read from the
three amplitudes is sqrt(rms(D1)^2/17) = 7.30e-14.

Prediction for `floor3.py` (before it runs; it reads only constraints.json): (i) the noise
level sigma from D1 and from D2 agree within 2 percent at every dump 1-13; (ii) with sigma in
place of f, the M halving at dump 13 lies within 3.97-4.01 and every dump judged with
e_{s/2} > 3 sigma lies within 4 +- 0.05 for H and M; (iii) the 1/2 -> 1/4 halving with sigma,
where e_{1/4} > 3 sigma, also lies within 4 +- 0.05; (iv) the floor from (1/2, 1/4) is closer
to sigma than the floor from (1, 1/2) at the dumps 9-13 where the odd part dominates.
Refuted if dump 13 of M stays outside the band with sigma.
