# VERIFIER: gate G2 of Track E (ultra-slow-roll case), fresh verifier

Helper package `stage/G2/verifier/` of owner E-stoch-inf, batch 14 (2026-11-25, 02:16 to 03:15
UTC). Decision 0016 item 4, ruling 0035 item 1. Criteria: `spec/scope/SCOPE.md` section 4c as
written (U-A0 to U-A4' (a)-(d), U-R, U-S, U-W, the floor, the clause on the maxima). Package
judged: the release ladder of `g2prod` on the card build core-v0.6 (11 runs, `g2prod/queue.txt`)
and the window scan that U-W cites. Processors only, 0 card-hours, at most 4 cores. Journal
with predictions and outcomes, including the failed ones: `verifier/JOURNAL.md` entries 1-6.

## 1. What was checked and how

Independence. I wrote my own reader of the NRSFDMP2 dumps from the interface text
(`scalar_field_2.md` 4), my own extraction of R^NR from the papers' definition (TH
`appendix.tex`:515-521, P1 `PRD_v2.tex`:524-526, including the gt_ij term of Phi), my own
background and continuum Mukhanov-Sasaki reference (DOP853, rtol 1e-12, from phi0, pi0 of the
deck and the mode file at N*), and drew alpha_n with the track's own Philox re-implementation
(`noise/ref/philox_ref.py`), not core's twin. No script of `g2prod/`, `usr/` or `window/` was
used. I read the lead's verdicts (`stage/G2/CHECKLIST.md`, `OPEN.md`, `g2prod/JOURNAL.md`
entries 2-3) only after every number below was committed (commit 25b2cc3b); the two checks of
section 3.4 were added after that reading, with predictions first (entry 5).

Tests of the tools before any verdict:
- V0 (run E-20261125-022126-26671c3): a synthetic dump with 40 known plane waves in phi, chi
  and gt_ij is read back bit for bit; the R^NR coefficients agree to 9.6e-13 of their rms
  (4.4e-15 with 1e3 times larger amplitudes: the 1e-12 is the rounding of the stored O(1)
  fields), nothing leaks outside the planted set; the 4c floor formula returns a planted floor
  to 0.15 percent.
- V2 (same run): alpha_n of philox_ref and of core's twin are identical on 2000 modes per seed.
- V1 (run E-20261125-022507-b13c79b): H(t = 0) = 1 + 4e-16; USR from cN = 2.5234 to 6.5503;
  eps1 minimum 9.716e-13; N(tlim) = 10 + 1.7e-13; lattice rms of W R at N_f 0.893707 (0.89366 in
  4c); the lockstep `.modes` record of U256ap at N_f agrees with my R_k to 1e-7 (low shells),
  8.0e-5 (q2 <= 1024) and 2.55e-3 (top shell, RK4 phase error). Reference self-error 1e-9.
- V3 (run E-20261125-022710-0eb5db0): R^NR of U256ap and U256bp at t = 0 equals
  L^-3/2 W(N*) R(N*) alpha_n, sign included, to 5.0e-12 and 7.4e-12: reader, extraction, phase
  convention, alpha and the slice agree.

Registered analysis runs (manifests `tracks/E-stoch-inf/runs/<id>/`): E-20261125-022126-26671c3
(V0, V2), E-20261125-022137-182e82c (first reference try, stopped by me at 39 GB of dense
output, on record as failed), E-20261125-022507-b13c79b (reference), E-20261125-022200-68c072e
(records), E-20261125-022232-6a83ff0 (R^NR coefficients of 548958 band modes at N_f, 10 runs),
E-20261125-022710-0eb5db0 (modes judge), E-20261125-022612-d2d99fa (window scan),
E-20261125-022309-d346f12 (constraint parts, 21 dumps x 7 runs, 68 GB read one variable at a
time), E-20261125-022918-f71678d and E-20261125-023427-6fb6400 (follow-ups),
E-20261125-023609-01d8feb (release against scouting; common mode). Figures (all looked at):
`verifier/fig/`.

## 2. Table per criterion

Verdict on the criterion: PASS or FAIL as 4c is written, from my number. Verdict on the
package's claim: CONFIRMED (my number agrees with the package's number and verdict), NOT
CONFIRMED (I could not reproduce or could not check it), WRONG (my number contradicts it).

| Id | Threshold | My number (run) | Package's number (g2prod 2.2-2.3, CHECKLIST) | Criterion | Package's claim |
|---|---|---|---|---|---|
| U-A0 | 1e-5 in N | max over landmarks and runs 1.61e-9 (256^3), 6.6e-10 (320^3), 4.3e-10 (control) (022200) | 1.6e-9, 6.6e-10 | PASS | CONFIRMED |
| U-A1 | 1e-3 rel. | max over rows 4.17e-5 (<Pi>, s = +-1, at N_f), 1.04e-5 (+-1/2), 2.52e-6 (+-1/4); <phi> 1.2e-9, <K> 2.4e-11 (022200) | 4.17e-5 | PASS | CONFIRMED |
| U-A2' (A, B) | max D_n < 0.02, k <= 32 dk | seed A 1.0894e-4 at (0,32,0); seed B 1.0871e-4 at (0,0,32); to k_max 4.506e-3 (both); single runs 5.9e-2, 7.8e-2 (small-alpha modes); U-A2n 2.533e-4 (A), 2.535e-4 (B) for k <= 32 dk, 2.877e-4 over the band (022710) | 1.0894e-4, 1.087e-4, 4.506e-3, 4.51e-3; even/odd 2.5335e-4, 2.5348e-4 | PASS | CONFIRMED |
| U-A3 | 10 percent | single runs 0.99230-1.00161 (A), 0.99678-1.00185 (B); odd parts 0.999916-0.999919 (61 modes, k <= 3 dk) (022710) | 0.99230-1.00161, 0.9968-1.0019, odd 0.99992 | PASS | CONFIRMED |
| U-A4'(a) | 4.00 +- 0.05 where e_{1/2} > 3 f | H: 9 judged dumps (0, 5-12), 3.9916-4.0424; M: 11 judged (0, 4-13), dump 13 (cN 6.525) = 3.9245, the others within 0.013 (022309) | H 3.992-4.042 at 9 dumps; M 3.925 at cN 6.52, 10 of 11 within | FAIL (M, one dump) | CONFIRMED (the failure) |
| U-A4'(b) | reported | f/o_{1/2} per dump (M): 1.0 at dumps 1-5 (odd part is all floor), 0.43 at 6, 0.031 at 7, 1.5e-3 to 9.3e-3 at 8-13; dump 13 also has o_{1/2} > 3 f (022309) | both readings reported, "the stricter decides"; dump 13 in both | reported | CONFIRMED |
| U-A4'(c) | < 1e-9 and < 1e-1 | proper runs: <abs H'/[H]> max 1.19e-12 to 3.03e-12, <abs M/[M]> max 8.09e-3 (320^3) to 2.52e-2 (256^3, the same at s = 1, 1/2, 1/4); control 1.28e-7 and 0.50 (022200) | 1.28e-12 to 3.03e-12; 0.0081-0.0252; control judged out [JUDGEMENT] | PASS on the proper runs (the control fails by design) | CONFIRMED |
| U-A4'(d) | >= 1e3 | ratio of the maxima over cN <= ln 32 (dumps 0-6): 2.38e5 (control H' against the proper odd part; the same with E(1) subtracted); pointwise 2.4e5-1.7e6 after N* (022309) | 1.19e5 (cross reading, decides), 2.38e5 (single) | PASS | CONFIRMED |
| U-R (i) | factor 2.0-4.5 | 1.0894e-4 / 5.182e-5 = 2.10 (022710) | 2.10 | PASS (5 percent margin) | CONFIRMED |
| U-R (ii) | 1e-3 / 1e-2 | 1.18e-4 (k <= 32 dk), 4.6e-3 (to 64 dk) (022710) | 1.18e-4, 4.6e-3 | PASS | CONFIRMED |
| U-R (iii) | 5 percent | 3.5e-5 (band), 1.07e-4 (k <= 32 dk) (022710) | 3.5e-5, 1.1e-4 | PASS | CONFIRMED |
| U-S | 5e-3 of 0.89366; U-A2', U-A3 | band rms of U256bp 0.894109 (+4.49e-4); full lattice the same; seed B's own lattice value 0.893953; U-A2', U-A3 above (022710) | 0.894109, 4.5e-4 | PASS | CONFIRMED |
| U-W | shifts <= 1e-3 (to 16 dk), <= 2e-2 (to 32 dk); per shell below the bound | 1.870e-4, 9.13e-3 (g2); per-mode errors of all five windows equal the window package's table to its digits; the per-shell bound |e_w| + |e_b| holds by construction (4 shells of s10 exceed it by the factor 1/(1 + e_b)) (022612) | 1.9e-4, 9.1e-3 | PASS | CONFIRMED |
| Floor, clause on maxima | as defined | applied as written: no dump dropped, maxima over all modes, no small-alpha exclusion, pairs at equal recorded times (|dt| = 0 at every dump) | the same | - | CONFIRMED |
| "USR case reproduced" (4c) | all of the above | not met as written: U-A4'(a) fails at one dump of M | C7 FAIL | FAIL | CONFIRMED |

No claim of the package that I recomputed is WRONG. Two statements of the package texts are
not borne out, both already marked by the package itself: the 4c note that the M record doubles
at s = 1/2 (at 256^3 its maximum is the same at every s: it is the first-order truncation part,
2.52e-2) and the reference in CHECKLIST C3/C5/C7 to `g2prod/JOURNAL.md` entry 4, which is not
written (OPEN item 1).

## 3. The failure on record and what the quarter-amplitude pair shows

3.1 Recomputed. The even part of M with the 4c floor removed scales by 3.9245 between s = 1 and
1/2 at dump 13 (cN = 6.525, the end of USR); H is not judged there (e_{1/2} = 1.32e-14 < 3 f).
The numbers: o = 1.0881e-11, 5.4407e-12, 2.7211e-12 and e = 1.0418e-12, 2.6991e-13, 9.751e-14
at s = 1, 1/2, 1/4; f = 5.05e-14 (run E-20261125-022309-d346f12).

3.2 Not a higher order in s. With the 4c floor from the pairs (1/2, 1/4) the factor at that dump
is 4.127 (not judged by 4c's own rule, e_{1/4} < 3 f): the deviation has the opposite sign and
is larger. g2prod entry 3 Q-a ("3.98 +- 0.015; refuted if the deviation is not at most half that
of (1, 1/2)") is refuted by these numbers, so by the package's rule no s^4 cause is named.

3.3 What the three amplitudes do show. With D1 = E(1) - 4 E(1/2) and D2 = E(1/2) - 4 E(1/4)
(fields, box means removed): rms(D2)/rms(D1) = 0.997 and corr(D1, D2) = -0.245 at dump 13, and
1.000 and -0.235 at every dump 1-13 for H and for M (fig_constraints.png, right panels). These
are the values of E(s) = s^2 A + F_s with F_s independent between the pairs and of equal rms
sigma at every s (ratio 1, correlation -4/17); an s^4 term would give 1/16 and +1, a part common
to all runs 1 and +1. sigma from D1 and from D2 agree within 0.3 percent at every dump 1-13. At
dump 13 sigma = 7.30e-14 while the 4c floor f is 5.05e-14 (0.69 sigma): f is the difference
4 o_{1/2}^2 - o_1^2 of two numbers equal to 1e-4, and where the odd part is ten (here) to a
thousand (dumps 8-12) times the even part, a third-order part of the odd part shifts it by tens
of percent (f/sigma = 0.65 to 1.75 at dumps 8-13). With sigma in place of f the M factor at
dump 13 is 3.9988, and every dump judged with e_{1/2} > 3 sigma lies within 4.000 +- 0.0045 (H)
and +- 0.0012 (M); the 1/2 -> 1/4 factors judged the same way lie within 1.3e-4 of 4 (run
E-20261125-023427-6fb6400, fig_floor3.png).

Reading [VERIFIED by these runs, under the model the D statistics support]: the even parts of H
and M are second order in s to 1e-3 wherever they stand above the per-run part; the one miss of
U-A4'(a) is an artefact of the floor estimator of 4c, not of the evolution and not of a higher
order in s. U-A4'(a) as written stays FAILED: 4c fixed its floor before the runs, ruling 0030
item 2 forbids rewording, and the three-amplitude floor uses a pair 4c did not define. Whether
this reading may be cited at the review is for orch.

3.4 Two checks added after reading the package (run E-20261125-023609-01d8feb): at N_f all 22
dumped variables of U256ap/am equal those of the scouting pair U256/U256m bit for bit, as the
package says, so F_s is deterministic, not card non-determinism [JUDGEMENT: rounding of O(1)
fields carrying small perturbations; not separated]; the common-mode part of the odd-part error
over k <= 16 dk is -4.107e-5, -9.87e-6, -2.07e-6 at s = 1, 1/2, 1/4 (package: -4.107e-5,
-9.87e-6), i.e. a s^2 + b with a = -4.16e-5 and b = +5.3e-7; Q-b of entry 3 is not refuted, Q-c
holds (U-A0 1.6e-9, U-A1 2.5e-6, U-A3 0.99809-1.00042, records 1.19e-12 and 2.51e-2, even/odd
6.334e-5). Richardson in s^2 over the three pairs (run E-20261125-022918-f71678d) separates the
odd-part error into a third-order part (median 4.2e-5 of |p|, sets max D_n below 25 dk and on
63 percent of the modes k <= 32 dk) and the discretisation part (1.306e-4 at the axis modes
|n| = 32 at 256^3, 4.53e-5 at 320^3: factor 2.88, order 4.7).

## 4. What I could not check

- The mode file at N* (`usr/inputs/modes_usr_n4096.txt`) against Bunch-Davies data at N0: I
  started my reference from it, as the code does; its own correctness rests on the usr package.
- The window scan runs on the scouting build core_scalar-2 at 128^3, not on the release; 4c
  accepts that and I only recomputed its numbers.
- U-R (i) at 320^3 without a 320^3 half pair: the linear part there is estimated by subtracting
  the third-order part measured at 256^3 (assumed resolution-independent; the common mode differs
  by 0.75 percent between the two N, which supports it).
- What the per-run part F_s is: I showed it is deterministic, independent between amplitudes
  and of equal size at every s; I did not show it is rounding.
- No processor rerun of any card run (no card time, and a 256^3 processor run is about an hour
  of a core per 200 steps); `nrpic-stage verify` was not run.
- The SR run P256v6 and everything outside 4c's USR criteria.

## 5. The three weakest points of the package

1. U-A4'(a) hangs on an ill-conditioned floor. The 4c floor is a difference of two odd-part
   norms that agree to 1e-4 exactly where the criterion bites (late USR, odd part 10 to 1000
   times the even part), so the judged factors scatter by up to 0.075 from a cause that is
   neither physics nor discretisation; and at cN < 2.5 the odd parts are all per-run part
   (f/o = 1), so (a) judges nothing during most of the mode entry, where P1's second-order claim
   (P1:538-541) is made. The record of the failure is right; the criterion does not measure what
   it was meant to.
2. U-R (i) passes by 5 percent (2.10 against 2.0) and measures the wrong thing: at 320^3 the
   maximum over k <= 32 dk sits on the third-order part, which does not depend on N, so any finer
   rung would fail the clause while the discretisation part keeps converging (order 4.7).
3. The quarter-pair reading is not in the record. CHECKLIST C3, C5 and C7 cite g2prod entry 4,
   which does not exist; my numbers refute entry 3's Q-a (the s^4 hypothesis). Two clauses carry
   readings chosen by the judge rather than by 4c: U-A4'(c) "every release run" includes the
   control, which fails by design, and U-A4'(d) has two readings of the control's odd part
   (1.19e5 and 2.38e5; both pass). The per-shell clause of U-W holds by construction, so U-W
   rests on its two numerical bars only.

## 6. Requests

- To the lead of E-stoch-inf: write g2prod entry 4 (Q-a refuted, Q-b and Q-c hold; numbers in
  section 3) or reconcile `g2prod/scripts/judge_q.py` with them; point CHECKLIST C3/C5/C7 to it;
  C18 can cite this file. Consider proposing to orch, for later gates and not as a rewording of
  4c, a floor from three amplitudes (sigma = rms(D1)/sqrt 17) and a U-R clause on the
  discretisation part (Richardson in s^2).
- To orch: say whether the three-amplitude reading of section 3.3 may stand beside the
  U-A4'(a) failure at the independent review (ruling 0030 item 2).
- None to core; no card time asked.
