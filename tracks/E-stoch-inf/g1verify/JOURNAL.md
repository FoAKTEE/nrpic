# Journal of g1verify (independent verifier of Track E's G1 material)

Helper of E-stoch-inf, wave 3, package g1verify (decision 0016 item 4; item C16 of the G1
checklist). Predictions are written before the runs they concern; outcomes after, including
the failed ones. Labels: [VERIFIED] recomputed here with a run id, [JUDGEMENT] my inference,
[BACKGROUND] standard, [TO VERIFY] open.

## Entry 0 (2026-11-20 14:21 PST, 22:21Z): set-up, what was read

Worktree commit at start: bc5e277 (merge of main), e2f926e when this directory was made
(other helpers commit in the same worktree).

Read: CLAUDE.md; coord/CHARTER.md to "Owners" and section 9.8; decisions 0010, 0013 (Track E
item), 0016-0019; SCOPE.md section 4 item 4 (A1-A8 definitions and thresholds; the amendment
note under A2 quotes two numbers of the ladder, 6.2e-3 and 1.2e-4 at 256^3, which I could
not avoid seeing) and section 4b (A4', A5' as proposals); SPEC.md sections 1-7; core's
interface `scalar_field_2.md` and the READY of core_scalar-2 (both quote core's own test
numbers at 32^3-128^3; they are core's verification, not the track's G1 results); the run
manifests and the ladder inputs (`ladder/inputs/*.athinput, *.list, modes_n*.txt`);
P1 = arXiv:2512.14649 v2 PRD_v2.tex lines 400-545 and 690-790; BZ = arXiv:2606.14853 v2
Manuscript.tex lines 140-290; TH = arXiv:2610.32592 v1 appendix.tex 380-525; P2 =
arXiv:2502.06783 v3 main_V2PRD.tex 395-460 (all from kb-data/raw/arxiv, read only);
coord/INTERFACES/rng.md sections 2-3; athenak/src/utils/rng.hpp (Philox, CellEntity,
DiskPoint, NegLog52, Normal2) and the header comment and NoiseDrawAlpha of
core/scalar-2:athenak/src/scalar_field/scalar_field_noise.cpp (to rebuild alpha_n and the
phase convention x0 = lower corner, cell centres (g + 1/2) dx).

Not read (before the verdicts): STATUS, HANDOFF, JOURNAL, RISKS, PLAN-wave3 of the owner;
stage/REVIEW-wave2.md; everything under stage/G1/; ladder/README.md, JOURNAL.md, results/,
fig/; note/; the packages a4res, ladder (beyond inputs), usr, window; spec/ref/ (the track's
reference), the wave reports of scratch/orch.

Set-ups confirmed from the lists (`ladder/inputs/job{A,B,C}.list`, `proc32.list`,
`proc64.list`, `a6proc.list`) [VERIFIED by reading]: L = noise_nmax2 64 (k_max/dk = 8) with
modes_n64.txt; Q64 = nmax2 256, Q128 = 1024, P256 = 4096 (k_max = N/4, P1's set-up);
p/m = noise_mode_scale +1/-1; ph/mh = +-0.5; NC = noise_pi_sign -1. The m, h and NC runs
have dump_metric = false (no gt_ij, At_ij in their dumps), so R^NR (needs gt_ij) is
measured on the p runs only. Run ends: P256, L32p/m, L64p/m (card), L128p/m, Q64p, Q128p at
t = 8.5; P256m, L256p/m, Q-m/h, NC, L32ph/mh, L64p/m (processors) at t = 4.5. Dumps every
0.5 in t at the first cycle past each multiple, so dump times differ between resolutions
(at most one step); the Courant runs dump at common cycles x (0.25/theta).

Own code (scripts/): `nrsf.py` (reader of NRSFDMP2 and the records), `alpha.py` (Philox
4x64-10 vectorised in numpy, polar Box-Muller of rng.md; alpha_n per wave vector),
`ref.py` (physical background with P2's potential-position fixing, Bunch-Davies modes from
N0, code-unit background, full and deformed MS in cosmic time, window). Smoke tests before
any registered run (not evidence): own Philox equals numpy.random.Philox on all 1054 modes of
nmax2 = 64; own BD integration reproduces modes_n64.txt at n = 1, 2, 8 to 1e-13 in modulus
and relative phase; own fixing gives the input's phi0, pi0, mass to rounding.

## Entry 1 (2026-11-20 14:45 PST): predictions for C0 (infrastructure), V1, V2, V3

Written before run C0/V1-V3 (no NR dump has been read by my code yet).

C0 infrastructure.
- P-C0a: my reader and core's `read_dump` (core/scalar-2) give bit-identical arrays for all
  22 variables of a single-MeshBlock dump. Refuted by any differing element.
- P-C0b: my Philox words equal numpy.random.Philox (independent implementation) for every
  sampled key, also for nmax2 = 4096; the AGM and library logarithms give alpha within
  1e-12 relative; <|alpha|^2> = 1 within 3/sqrt(M).
- P-C0c: at t = 0 my extraction of R^NR (Phi from chi and gt_ij by TH appendix.tex:518,
  R = Phi - <K>/(3<alpha><Pi>) (phi - <phi>), TH:520, P1:524) equals L^(-3/2) W(0) R_n(0)
  alpha_n with the phase exp(i pi (n_x + n_y + n_z)/N) of the cell centres, within 1e-9
  relative for |n| = 1 (W = 1/2); for smaller W the relative error grows as rounding/W.
  Refuted if |n| = 1 is off by more than 1e-6 or the phase is wrong (then my convention or
  alpha is wrong, not necessarily the code).

V1 (A1, threshold 1e-4 relative).
- P-V1: on every rung the box means of phi, Pi, K (records every cycle, and my own means of
  the dumps) follow my Friedmann + Klein-Gordon integration to between 1e-13 and 1e-9
  relative; the deviation falls with the step (Courant runs) until the second-order mean of
  the perturbations (~R^2 ~ 1e-10) or rounding takes over. e-folds -ln<chi>/2 = ln a within
  1e-8. Refuted: any deviation above 1e-4 (A1 fails), or a deviation that does not fall
  with the step while above 1e-10.

V2 (A2, threshold 0.02 for k <= k_max/2 at N_f).
- P-V2a: per mode |R^NR_n/(L^(-3/2) W R_n alpha_n) - 1| at the last dump, maximum over
  k <= k_max/2: L32 1e-4 to 1e-3 (sixth-order dispersion at k dx = pi/4, 3.8e-4 in k^2 by
  SPEC 7.2's arithmetic), L64 ~ 64 times less, L128 and L256 at a floor of order 1e-6 (the
  second-order part of R^NR, ~R ~ 1e-5 times O(0.1)); P256 at k <= 32: 1e-4 to 1e-3 (again
  k dx = pi/4). All pass 0.02. Refuted: any mode above 0.02, or no fall from L32 to L64.
- P-V2b: the alpha-normalised shell spectrum at N_f over the analytic slow-roll power at
  crossing H_k^2/(8 pi^2 eps1_k Mpl^2) is 1 + O(eps1), between 0.98 and 1.03 for every shell;
  the raw shell spectrum scatters around that by 1/sqrt(M_shell).

V3 (A3, threshold 1 percent in the ratio; drift below 2.5e-3 per e-fold).
- P-V3: for every mode with N_f - N_k >= 6 (k <~ 7.9 at N_f = 8.1) the NR power ratio
  between the first dump past N_k + 4 and N_f equals the full-MS ratio within 1e-4 (it is a
  ratio of one mode, no alpha needed); the NR drift d ln|R_n|^2/dN over that interval is
  below 1e-3 per e-fold and within 1e-4 of the full MS, and far from the deformed
  (FLRW-lattice) drift -4 eps1 ~ -0.045 to -0.054. Refuted: ratio off by more than 1 percent
  (A3 fails), or a drift near the deformed one.

## Entry 2 (2026-11-20 18:57 PST, 02:57Z on 11-21): second session; C0 outcome; pass 1 closed

Second session of this package (the first was cut at 14:35 PST by the five-hour limit). I
re-read CLAUDE.md, CHARTER to "Owners" and 9.8, decisions 0010, 0013 (E), 0016-0020, SCOPE 4
item 4 and 4b, SPEC 1-7 and the interface scalar_field_2.md sections 2-4 myself; nothing of
the forbidden list (entry 0) was opened. The worktree held, from session 1: scripts nrsf,
alpha, ref, rnr, catalog, check_infra, permode, v123 (committed d42de1a) and constraints.py
(uncommitted, a dev run in scratch/E-stoch-inf/g1verify_tmp/condev, not evidence).

C0 outcome (run E-20261120-222844-dbca87f, completed, exit 0) [VERIFIED]:
- P-C0a CONFIRMED: my reader and core's read_dump (core/scalar-2) give 0 differing elements
  in all 22 variables of dump 5 of L32p, L64p, L128p.
- P-C0b CONFIRMED: 0 of 7160 sampled Philox keys differ from numpy.random.Philox at nmax2 =
  4096 (548958 modes); AGM against numpy.log: 7.6e-10 relative at most (inside 1e-12? NO:
  the prediction said 1e-12; the AGM form of rng.hpp is an approximation of the logarithm at
  that level, so my "bit-exact intent" AGM and the library log differ by 7.6e-10. Failed
  sub-prediction, harmless: alpha from the AGM agrees with core's twin mode_alpha to 5.0e-16
  absolute, which is what matters). <|alpha|^2> = 1.00057, inside 3/sqrt(M) = 4.0e-3.
- Background: my fixing gives the deck's phi0, pi0, mass to 1.2e-15 relative; H(0) = 1 in
  code units; N(t = 8.5) = 8.0989, N(4.5) = 4.3876.
- Mode files: modes_n64.txt equals my Bunch-Davies integration to 6e-13 (modulus) and 2e-13
  (phase). modes_n256/1024/4096.txt equal mine to 1.6e-6 (modulus) and 2.7e-6 rad (phase):
  integrated with a looser tolerance, 1e4 below the A2 threshold and 1e3 below A3's. Noted.
- Lists and manifests: all six lists unchanged since submission (sha256 equal), mode-file
  checksums equal, card list copies in the run directories equal.
- P-C0c CONFIRMED: at t = 0, |R^NR_n/(L^-3/2 W R_n alpha_n) - 1| = 1.1e-10 to 7.5e-10 for
  |n| = 1 (W = 1/2) on L32p, L64p, L128p, 0.8e-9 to 2.2e-9 for |n|^2 = 2, 3; 1e-7 to 1.6e-6
  for |n|^2 >= 4 where W < 1e-3 (rounding/W as predicted). Phase within 1.5e-6 rad. So my
  extraction, the phase convention and alpha are right.

Pass 1 (run E-20261120-223154-d42de1a, completed exit 0 at 23:02Z, closed with nrpic-run
finish now): R^NR_n per mode and box means from all 18 dumps of P256 and all 10 of L256p,
the sha256 of every dump equal to the run's sha256sums.txt (18 + 10 of 28). Wall 1851 s.
No analysis of these numbers yet.

## Entry 3 (2026-11-20 19:10 PST): predictions for V4, V5, V6, V7

Written before constraints.py, v6 or v7 have run on the registered data (the dev run of
session 1 in g1verify_tmp/condev was on L32 only and I have not read its numbers).

Reasoning [JUDGEMENT, from SPEC 2-7 and the stencils, not from the track]: the sources are the
continuum linear solution (continuum k, the frozen mode functions); the evolution uses sixth-
order differences and RK4 at Courant 0.25. The linear constraints then hold only up to the
truncation error: a part FIRST order in the amplitude s (odd in s) of relative size
eps(k dx) (Laplacian symbol (k dx)^6/560: 2.7e-2 at k dx = pi/2, 4e-4 at pi/4, 6e-6 at pi/8,
1e-7 at pi/16) plus the RK4 error (omega dt)^4 ~ (0.25 k dx)^4/120. The second-order part
(even in s) is the physical one of P1:538-541, ~1e-10 of [H]. Rough size of the linear terms of
H at crossing: eps1 R H^2 x O(10) ~ 4e-6 of the background terms, so odd/[H] ~ 3e-7 x eps.
Rounding: H holds second differences, so rounding/[H] ~ 1e-16 sqrt(n_steps) (N/2pi)^2 x O(1)/12,
growing as N^2 to N^2.5.

V4 (constraints).
- P-V4a: odd part of H (rms over the box, over <[H]>) in the paper's set-up (P256, Q128, Q64;
  k_max dx = pi/2 at every N) reaches 1e-9 to 1e-8 when the last shells enter and does not
  fall with N; it exceeds the even part (mean removed), which sits at 3e-11 to 3e-10 near
  the end of the entry. In the L set-up the odd part falls with N: L32 ~ P-set level, L64
  comparable to the even part, L128 and L256 well below it.
- P-V4b: halving (s = 1 -> 1/2) divides the odd part by 2.00 and the even part (mean removed)
  by 4.00, each within 2 percent where it is above the floor (L32, Q64, Q128).
- P-V4c: the record <|H|/[H]> of the proper runs is below 1e-8 at all times; <|M|/[M]> is
  first order or larger (1e-5 to 1e-2), largest when the k dx ~ pi/2 shells enter.
- P-V4d: negative controls (noise_pi_sign = -1): odd part of H at least 1e3 times that of
  the proper run of the same set-up during the entry; record <|H|/[H]> ~ 1e-6 to 1e-5,
  <|M|/[M]> ~ 0.1 to 1 (P1:541).
- P-V4e: strict A4 (record ratios scale with s^2 under halving) FAILS in the paper's set-up
  once the odd part dominates (record halving factor drifting from ~4 towards ~2); A4'
  (a), (b), (d) pass; A4'(c) passes for H and is at risk for M (the odd part of M over [M]
  is zeroth order in s).
Refuted: an odd part that falls with N in the P set-up, a halving factor of the even part
outside 3.9-4.1 above the floor, or a negative control within a factor 100 of the proper run.

V5 (A5, spatial order, L32/L64/L128 at k_max/dk = 8).
- P-V5a: order of the odd part of H and M, log2(odd_N/odd_2N) at equal times, between 4 and
  6.5 from 32 to 64 (sixth-order space, fourth-order time with dt ~ dx) and from 64 to 128
  until the 128 odd part reaches the floor. Refuted: an order below 3.5 or above 7 above the
  floor.
- P-V5b: the floor (the part that does not scale with s: the out-of-band part |n|^2 > 9 nmax2
  of the odd part, which no physics fills to third order, and odd(s) - 2 odd(s/2)) grows as
  N^2 to N^2.5, its shell spectrum rises with k (second differences of white rounding:
  ~k^4 in power), it is of the same size in the odd and the even part and in the proper and
  halved pairs, and its level is 1e-14 to 1e-12 of [H] at 128-256. If all four hold, the
  attribution to double-precision rounding is supported; a floor that scales with s, or is
  flat in N, refutes it.

V6 (A6, temporal order, T25/T12/T06 at N = 32, s = +-1).
- P-V6: at common times, log2(|X_0.25 - X_0.125| / |X_0.125 - X_0.0625|) = 4.0 +- 0.3 for the
  perturbations of phi, Pi, chi, K (box mean removed), for R^NR of the low modes and for the
  odd and even parts of H. Refuted (A6 fails) by an order outside 3.5-4.5 while the
  difference X_0.125 - X_0.0625 is above 100 times rounding; an order near 1 or 2 would point
  at the stage times of the time-dependent source (SPEC 2.5).

V7 (A7 and cost).
- P-V7a: the card dumps of U1, U2, U3 (1, 8, 64 MeshBlocks; release core-v0.3) are
  bit-identical in every variable, the noise fields included, at every dump; the processor
  U4 (restart at cycle 150) is bit-identical to the processor U2 at the dumps after the
  restart, and the card U4 to the card U2. Card against processor differs at 1e-16 to 1e-13
  relative (not part of A7). Refuted by a single differing element within one platform.
- P-V7b: one 256^3 realisation (P256 to t = 8.5) costs 0.5-1 card-hour on one A100.

## Entry 4 (2026-11-20 19:12 PST): outcomes V1, V2, V3 (run E-20261121-030207-fb6f090)

Pass 2 (run E-20261121-025750-d1b6139, completed): per-mode R^NR and box means from every dump
of L32p, L64p, L128p, Q64p, Q128p (18 each) and L64p_proc (10), sha256 of every dump equal
to the run's list. V1-V3 analysis: run E-20261121-030207-fb6f090 (completed exit 0; its
submit wrapper had a 110 s timeout by my mistake: I killed the wrapper, pid 490263, by
number so the run continued; it finished normally at 03:06:20Z).

V1 [VERIFIED]: P-V1 CONFIRMED for phi, Pi, K. Maximum over all record rows of every one of
the 34 catalogue runs: |<phi>/F - 1| <= 3.2e-12, |<Pi>/F - 1| <= 8.6e-12, |<K>/F - 1| <=
3.6e-12 (A1 threshold 1e-4); my own dump means agree (<= 7.8e-12). The code's lockstep
background (record columns phi_b, Pi_b, ln_a) equals my integration to 2.3e-11.
Sub-prediction FAILED: e-folds -ln<chi>/2 against ln a differ by 5.5e-6 (N = 32), 3.3e-7
(64), 2.0e-8 (128), 1.3e-9 (256), not within 1e-8 at N <= 64. Cause tested in V6: the box
mean of chi converges at order 4.06 in the Courant factor, so this is the RK4 error of chi
~ exp(-2t) at dt = 0.25 dx (my estimate 32 dt^4/120 per unit time, 1.5e-6 at N = 32), not a
physics error. It does not enter A1 (phi, Pi, K). Also seen: alpha stays uniform but drifts
from 1 by -2.5e-13 (L32p) and -4.9e-13 (L64p) at t = 8.5, linear in the number of steps
(rounding); harmless.

V2 [VERIFIED]: P-V2a CONFIRMED. max over k <= k_max/2 of |R^NR/(L^-3/2 W R alpha) - 1| at the
last dump (t = 8.5, N = 8.10; L256p at t = 4.5): L32p 8.8e-5 (at n = (4,0,0), k dx = pi/4),
L64p 2.7e-6, L128p 2.5e-6, L256p 1.7e-6, Q64p 9.7e-5, Q128p 9.9e-5, P256 1.21e-4 (at
(0,32,0), k dx = pi/4; 68532 modes). At the last common dump t ~ 4.5: L32 8.7e-5, L64 2.0e-6,
L128 1.75e-6, L256 1.74e-6, P256 1.03e-4. All 70 to 165 times below 0.02. Over ALL modes up to
k_max (k dx = pi/2): max 4.1e-3 (L32), 4.5e-3 (P256), still below 0.02. L32 -> L64 falls by
44 (order 5.4), then a floor ~2e-6 at L64-L256 (low modes, n = (1,0,-2)): my prediction said
1e-6 from the second-order part of R^NR [JUDGEMENT, not separated: the m runs have no gt_ij].
P-V2b CONFIRMED: alpha-normalised shell spectrum / (H^2/(8 pi^2 eps1)) at crossing =
1.0104-1.0116 for every shell k <= 32 of P256 (my full MS: 1.0104-1.0114; NR/MS at most
1.6e-4 apart); raw spectrum against MS: pull rms 1.007, max 4.1 over 854 shells (the
Gamma-distributed shell means of few modes have a long upper tail).

V3 [VERIFIED]: P-V3 CONFIRMED on every t = 8.5 rung (1051 modes with N_f - N_k >= 6, k <=
7.87): |ratio_NR/ratio_MS - 1| between the first dump past N_k + 4 and N_f at most 2.4e-6
(L64p, L128p) to 3.2e-6 (P256, Q128p) against the 1 percent threshold; NR drift of ln|R|^2
-1.4e-4 to -3.3e-5 per e-fold (threshold 2.5e-3), equal to the full MS within 1.7e-6;
deformed (FLRW-lattice) drift -0.0516 to -0.0530 per e-fold (-4 eps1), deformed/full ratio
0.826-0.908, i.e. 9-17 percent off, 3e4 times the NR deviation.

## Entry 5 (2026-11-20 19:14 PST): outcomes V6 and V7 (runs E-20261121-030522-c6907b6, -030520-5a23d64)

V6 [VERIFIED] (first version E-20261121-030412-42dd156 had the box mean of H inside the even
part; the second, c6907b6, adds the even part without mean and the mean): P-V6 CONFIRMED where
the time error is resolvable. Orders log2(|D1|/|D2|), max norm, at the 9 common dumps
t = 0.49-4.42: odd parts of phi, Pi, chi, K, gxx, Axx 3.93-4.10; odd R^NR of |n|^2 <= 8
3.94-4.05; odd H 3.85-4.24 for t <= 2.45, then |D2| reaches 3e-14 (rounding of H at N = 32,
my estimate 3e-14) and the order is meaningless; <H> (the uniform residual, order s^0) 4.10
at every dump (3.1e-11 at Courant 0.25, i.e. 2.6e-12 of [H]); <chi> 4.06. Not testable: the
even parts (second order) of the fields and of H without mean: |D1|, |D2| = 2e-14 to 4e-13,
order -0.3 to -0.7 (random-walk rounding grows as the square root of the number of steps):
their time error is below rounding at N = 32. Box means of phi, Pi, K: differences 1e-14 to
8e-12, orders -1.3 to 3.9, at rounding.

V7 [VERIFIED] (first attempt E-20261121-030415-22d518b failed: exit 1 on a processor manifest
without batch_entries, a bug of my script; second attempt 5a23d64 completed): P-V7a CONFIRMED.
Card U1/U2/U3 (1, 8, 64 MeshBlocks): 0 differing 64-bit words in all 12 variables (noise
fields rms 0.011, not trivially zero) at all 4 dumps; mode files byte-identical; records
equal in every column. Restart: processor U4 = U2 and card U4 = U2 bit for bit at cycles 200
and 300, time bits equal, mode files and records equal. sha256 of all 20 dumps read equal to
the runs' lists. Card against processor (information): U2 noise fields 4e-16 relative; the
slow-roll L64p perturbations 2e-9 to 4e-7 relative (not bit-identical, as predicted). P-V7b:
P256 took 1811 s wall, 0.5031 card-hours on one A100 (manifest of E-20261115-172618-f948386:
resources.walltime_s, gpu_hours); prediction 0.5-1 card-hour CONFIRMED.
Weak point found: A7 is tested on release core-v0.3 (noise unit test), not on the G1
executable core/scalar-2 with the slow-roll set-up. Hence P-V7c below.

P-V7c (prediction, before the run): core/scalar-2's processor executable on the L32p set-up
with 8 MeshBlocks of 16^3 gives dumps bit-identical to the registered L32p (one MeshBlock)
at t = 0, 0.50, 1.00 in all 17 variables, and a restart from cycle 12 gives the dump at
t = 1.00 bit-identical to both; the .modes files are byte-identical. The constraint and
history records may differ in the last bits (box sums over MeshBlocks in another order).
Refuted by a single differing word in a dump.

## Entry 6 (2026-11-20 19:32 PST): outcomes V4, V5, V7c

Constraint pass E-20261121-030657-c1afe38 (completed; 289 dumps hashed, all equal to the
runs' lists; P256 read by seek after its pass-1 check; my purpose text wrongly said L256p was
read by seek too: it was read whole and hashed). Analysis E-20261121-031951-82984f8 (the first
attempt E-20261121-031936-16d6ae5 failed on a record column name, my bug). Numbers are rms
over the box divided by the record's <[H]> (<[M]> for M) of the proper run.

V4 [VERIFIED]:
- P-V4a PARTLY FAILED. Shape confirmed: in the paper's set-up the odd part rises above the
  even part from t = 2.0 (Q64), 3.0 (Q128), 3.5 (P256), i.e. when shells with k dx ~ pi/4
  enter (ln(N/8) e-folds after N*), and peaks at 6.0e-11 (Q64, t = 3.0) and 5.5e-11 (Q128,
  t = 4.0): it does not fall with N. P256's peak is not captured (P256m ends at t = 4.5 and its
  last dump has the cycle but not the time of P256's; at t = 4.0 the odd part is 1.7e-11 and
  rising). Magnitude FAILED: I predicted 1e-9 to 1e-8 (20-200 times too high) and an even
  plateau of 3e-11 to 3e-10 (observed 7e-13, 40 times lower). L set-up as predicted: odd
  maximum 5.4e-11 (L32), 1.2e-12 (L64, comparable to the even plateau and above it after
  t = 2), in-band 2e-14 (L128) and 3e-16 (L256), far below.
- P-V4b CONFIRMED with the floor as SCOPE 4b defines it (the part that does not scale with
  s, rms(C(s) - 2C(s/2)) or rms(C(s) - 4C(s/2))): odd halving 1.9989-2.0000, even
  3.986-4.000 (L32, Q64, Q128). With my out-band "floor" instead, Q64 (1.77) and Q128 (1.43;
  even 3.66) fail at t <= 2: in the paper's set-up the out band |n|^2 > 9 nmax2 is a corner
  of the cube and holds only a fifth of the rounding, so it underestimates the floor.
- P-V4c CONFIRMED: record <|H|/[H]> max 5.1e-11 (P set, every N), 2.6e-12 (L set N >= 64,
  at t = 0, the slice); <|M|/[M]> max 4.0e-4 (P set), 1.5e-5 to 1.8e-5 (L set N >= 64),
  largest when the k dx ~ pi/2 shells enter.
- P-V4d PARTLY FAILED: NC odd part / proper odd part 2e3 to 3.6e6 during the early entry, but
  only 120 (NC32, t = 3.0), 89 (NC64, t = 3.5), 180 (NC128, t = 4.0) at the end of the entry,
  where the proper run's discretisation part peaks and the control's first-order violation
  has decayed; ratio of the maxima 1874, 1709, 1853. Record of the controls: <|H|/[H]> max
  9.9e-8 (I predicted 1e-6 to 1e-5: FAILED, 10-100 times lower), <|M|/[M]> 0.21 (confirmed).
- P-V4e CONFIRMED: strict A4 fails (record halving factors F_H 0.83-1.99 on L32, 2.0-4.6
  on Q64, 2.0-4.1 on Q128 during the entry; F_M 1.0-2.0): the record carries the uniform
  s^0 residual (box mean of H: 2-3e-12 on L32, 3-5e-13 on Q64/Q128; order 4.1 in the Courant
  factor, V6) early and the s^1 discretisation part late. A4' (a), (b), (c) pass; (d)
  passes on the maxima and fails pointwise at the end of the entry.
- Not predicted: with each run's out-band floor removed in quadrature, the even parts of
  L128 and L256 (same modes) agree within 0.8 percent at every dump (raw: up to 17 percent at
  t = 0.5, where L256 is floor-dominated) [VERIFIED arithmetic on 82984f8, addendum script].

V5 [VERIFIED]: P-V5a CONFIRMED: spatial order of the odd part of H, 32 -> 64: 5.54-5.64 for
t >= 1.5, 3.8-4.3 at t <= 1 (time error, dt ~ dx, dominating while only low shells are in);
64 -> 128 (in-band part, the total is floor-dominated at 128): 5.2-5.9 for t = 1.5-5.0,
4.0-4.1 at t <= 1; 128 -> 256 (in-band): 5.8-5.96 for t >= 2. M likewise (5.6-5.9).
P-V5b: floor (out band) grows as N^2.45-2.51 between 64, 128, 256 at t <= 3 (L), N^2.42-2.49
(P); equal in the odd and the even part (within 1 percent) and in the proper and the halved
pair (0.93-1.07); the non-scaling parts satisfy rms(e - 4e_h)/rms(o - 2o_h) = 1.8-1.9 =
sqrt(17/5) of independent noise in the four runs; level 1.2e-13 (L128) and 6.3e-13 (L256)
at t = 0.5, falling as the expansion (1/a^2). Shape: FAILED in part: the floor spectrum is
flat (white) at late times and rises towards the corner of the cube only at t ~ 2.5 (I
predicted ~k^4 throughout): the white part is the rounding of the evaluation of H itself.
Attribution to double-precision rounding: supported by four of five predicted signatures.

V7c [VERIFIED] (E-20261121-031049-27cdc06 run, E-20261121-031251-c48670d comparison):
P-V7c CONFIRMED: 8 MeshBlocks vs one: all 22 variables bit-identical at t = 0, 0.54, 1.03;
restart from cycle 12: bit-identical at t = 1.03; mode files byte-identical; records differ
by box-sum rounding only (<= 1.7e-14 relative, except the e-fold column at t = 0, whose value
is itself rounding).

## Entry 7 (2026-11-20 19:35 PST, 03:35Z on 11-21): figures, verdicts, comparison; package closed

Figures: registered run E-20261121-032413-0672bf9 (make_figs.sh), every PNG looked at with
the Read tool (V1-V7; dev versions in g1verify_tmp/figdev looked at first, fixes: V3 deformed
curve shown only once W ~ 1, V5 tick labels and spectrum panel, V7 left out the processor's
shortened last dump). nrpic-run verify PASS on every run of this package and on the small
producing runs used (proc32, proc64, a6proc, U2/U4 processors, U4 card); the big card runs
(jobs A, B, C, the U card batch) were checked file by file through the sha256 of every dump
read (pass 1, pass 2, constraint pass, V7).

VERIFIER.md verdicts committed (db88f63) before the track's numbers were read; then the
comparison (c43e050): agreement to three digits on A1, A2, A3 drifts, A5 orders, odd/even
parts, cost; nine disagreements above 10 percent, none changing a verdict; the largest is the
track's P256 odd/even maximum 385 in `ladder/results/final/` and `stage/G1/STATUS.md`, which
comes from pairing dumps 0.0038 apart in time (the track's own final2 gives 25, as I do).
No G1 ledger was committed under note/tables, so that recomputation was not available.
Not done: nothing of V1-V7; open points are listed in VERIFIER.md (weak points) and README
(Requests).
