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
