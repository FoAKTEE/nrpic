# Independent verification of Track E's G1 material (slow-roll ladder 32^3-256^3)

Verifier: helper g1verify of E-stoch-inf (decision 0016 item 4; item C16 of the G1
checklist), a fresh reader given the artefacts and not the conclusions. Two sessions:
2026-11-20 14:21-14:35 PST (cut by the five-hour limit) and 2026-11-20 18:55 PST onwards
(2026-11-21 UTC). Worktree commit at start: bc5e277 (session 1), 36824dc (session 2, after
`git merge main`).

Read before the verdicts: `CLAUDE.md`; `coord/CHARTER.md` to "Owners" and section 9.8 (the
G1 criterion); decisions 0010, 0013 (Track E), 0016-0020; `spec/scope/SCOPE.md` section 4
item 4 (definitions and thresholds A1-A8; the amendment note under A2 quotes two ladder
numbers, 6.2e-3 and 1.2e-4 at 256^3, which I could not avoid seeing) and section 4b (A4',
A5' as proposals); `spec/SPEC.md` sections 1-7; core's interface
`core/scalar-2:tracks/core/interfaces/scalar_field_2.md` and the READY of
`scratch/core/exe/core_scalar-2/` (they quote core's own 32^3-128^3 test numbers, which are
core's verification, not the track's G1 results); `coord/INTERFACES/rng.md` sections 2-3,
`athenak/src/utils/rng.hpp`, the header of `core/scalar-2:.../scalar_field_noise.cpp`, the
NRSFDMP1 comment of `athenak/src/scalar_field/scalar_field_io.cpp`; every run manifest used;
the ladder inputs (`ladder/inputs/*.athinput`, `*.list`, `modes_n*.txt`) and the noise
unit-test inputs (`analysis/inputs/u64/`); the sources P1 = arXiv:2512.14649 v2
`PRD_v2.tex` 400-545 and 690-790, BZ = arXiv:2606.14853 v2 `Manuscript.tex` 140-290, TH =
arXiv:2610.32592 v1 `appendix.tex` 380-525, P2 = arXiv:2502.06783 v3 `main_V2PRD.tex`
395-460 (kb-data/raw/arxiv, read only).

Not read before the verdicts: the owner's STATUS, HANDOFF, JOURNAL, RISKS, PLAN-wave3;
`stage/REVIEW-wave2.md`; everything under `stage/G1/`; `ladder/README.md`, `JOURNAL.md`,
`results/`, `fig/`; `note/`; the packages a4res, usr, window; `spec/ref/` (the track's MS
reference); the wave reports of `scratch/orch`. The comparison with the track is the last
section, written after the verdicts.

Labels: [VERIFIED] recomputed here with the run id given; [JUDGEMENT] my inference;
[TO VERIFY] open. Predictions and outcomes, failed ones included: `JOURNAL.md`.
All my code is in `scripts/` (own reader, own Philox and Box-Muller, own background and
Mukhanov-Sasaki, own R^NR extraction, own odd/even split); nothing of `spec/ref/` or
`python/nrpic/sf_inflation.py` is used. Core's `read_dump` was used once, as the check of my
reader (C0).

## Runs

| Run id | What | Status |
|---|---|---|
| E-20261120-222844-dbca87f | C0: my reader vs core's read_dump (bit for bit), my Philox vs numpy.random.Philox, my alpha vs core's twin, my background fixing vs the deck, my Bunch-Davies modes vs the mode files, lists and checksums, my R^NR at t = 0 | completed |
| E-20261120-223154-d42de1a | pass 1: R^NR per mode and box means from all dumps of P256 (18) and L256p (10), sha256 of each dump checked | completed (closed with `finish` in session 2) |
| E-20261121-025750-d1b6139 | pass 2: the same for L32p, L64p, L128p, Q64p, Q128p (card) and L64p_proc (processors) | completed |
| E-20261121-030207-fb6f090 | V1, V2, V3 analysis (records of all 34 runs, my MS full and deformed) | completed |
| E-20261121-030657-c1afe38 | V4/V5 data: odd/even parts of H and M_i from the mirrored pairs, wave-vector bands, shell spectra, halved pairs, controls, records (289 dumps hashed) | completed |
| E-20261121-031936-16d6ae5 | V4/V5 analysis, first attempt | failed (exit 1: my script used a wrong record column name) |
| E-20261121-031951-82984f8 | V4/V5 analysis: dominance, halving, controls, strict A4 and A4', spatial order, floor | completed |
| E-20261121-032413-0672bf9 | all figures; V4/V5 addendum (halving with the non-scaling floor, L128/L256 even parts with the floor removed, control maxima) | completed |
| E-20261121-030412-42dd156 | V6, first version (the even part of H still held its box mean) | completed, superseded |
| E-20261121-030522-c6907b6 | V6: Richardson orders from the Courant runs | completed |
| E-20261121-030415-22d518b | V7, first attempt | failed (exit 1: my script read a processor manifest without batch entries) |
| E-20261121-030520-5a23d64 | V7: bit-identity of the noise unit test (layouts, restart), card vs processor, cost | completed |
| E-20261121-031049-27cdc06 | V7c: the G1 executable (core/scalar-2 processors) on the L32p set-up with 8 MeshBlocks, and restarted from cycle 12 (1 core, 98 s) | completed |
| E-20261121-031251-c48670d | V7c comparison with the registered L32p | completed |

All on processors (0 card-hours). Every run used is registered and finished; the sha256 of
every dump I read was compared with the producing run's `sha256sums.txt` (P256 and L256p in
pass 1, the others in pass 2, V6, V7, the constraint pass).

Set-ups confirmed from the lists [VERIFIED by reading `ladder/inputs/*.list`; C0 checked
that the lists are unchanged since submission]: L = `noise_nmax2 = 64` (k_max/dk = 8) with
`modes_n64.txt`; Q64 = nmax2 256, Q128 = 1024, P256 = 4096 (k_max = N/4, P1's set-up);
suffix p/m = `noise_mode_scale` +1/-1, ph/mh = +-1/2; NC = `noise_pi_sign = -1`; the m, h
and NC runs have `dump_metric = false` (no gt_ij, At_ij), so R^NR is measured on the p runs
only. Ends: P256, L32p/m, L64p/m, L128p/m, Q64p, Q128p at t = 8.5 (N - N* = 8.10); P256m,
L256p/m, Q-m/h, NC, L32ph/mh, L64p/m_proc at t = 4.5 (4.39). Card runs are core/scalar-2
a58e95b `athena_gpu`, processor runs its `athena_cpu`.

## Verdicts

### V1 (A1) Background: box means against my Friedmann and Klein-Gordon integration — CONFIRMED

[VERIFIED, run E-20261121-030207-fb6f090] My integration in code time (`scripts/ref.py`,
DOP853 at rtol 1e-13) from the deck's phi0, pi0, mass, which my own potential-position
fixing of P1/P2 reproduces to 1.2e-15 (C0). Over every row of the history record
(`sr.sf.hst`, every cycle) of all 34 catalogue runs (ladder, halved, controls, Courant):
max |<phi>/F - 1| = 3.2e-12, |<Pi>/F - 1| = 8.6e-12, |<K>/F - 1| = 3.6e-12; my own means of
the p-run dumps agree (at most 7.8e-12). Threshold 1e-4: passed by eight orders of magnitude
on every rung, controls included. The code's lockstep background (record columns phi_b,
Pi_b, ln_a) equals mine to 2.3e-11. Two observations, neither in A1: (i) the e-folds
-ln<chi>/2 differ from my ln a by 5.5e-6 (N = 32), 3.3e-7 (64), 2.0e-8 (128), 1.3e-9 (256):
the RK4 error of chi ~ exp(-2t), which converges at order 4.06 in the Courant factor (V6);
my prediction of 1e-8 failed at N <= 64. (ii) The lapse stays uniform but drifts from 1 by
-2.5e-13 (L32p) and -4.9e-13 (L64p) at t = 8.5, linear in the number of steps (rounding).
Figure `fig/fig_v1.png`.

### V2 (A2) R^NR per mode against W R alpha; the shell spectrum — CONFIRMED

[VERIFIED, runs E-20261120-223154-d42de1a, E-20261121-025750-d1b6139, E-20261121-030207-fb6f090]
My extraction (`scripts/rnr.py`): Phi_k = (X_k/<X> )/2 + (1/4) k_i k_j/k^2 (gt_ij)_k and
R^NR = Phi - <K>/(3<alpha><Pi>)(phi - <phi>) (TH appendix.tex:517-520, P1 PRD_v2.tex:522-526),
mode coefficients by my own FFT with the cell-centre phase exp(-i pi (n_x+n_y+n_z)/N);
reference L^-3/2 W(k,t) R_k(t) alpha_n with my full MS integrated from each run's mode file,
W of P1:503-506 with the Friedmann a, H, and my alpha_n (Philox-4x64-10 of rng.md, checked
against numpy's independent Philox on 7160 keys and against core's twin to 5e-16). At t = 0
my R^NR equals the reference to 1e-10 for |n| = 1 (C0), so convention and alpha are right.

| Rung | max over k <= k_max/2, last dump (N - N* = 8.10; L256p 4.39) | at t ~ 4.5 | all k <= k_max, last dump |
|---|---|---|---|
| L32p | 8.8e-5 at n = (4,0,0), k dx = pi/4 | 8.7e-5 | 4.1e-3 at (8,0,0) |
| L64p | 2.7e-6 | 2.0e-6 | 9.7e-5 |
| L128p | 2.5e-6 | 1.75e-6 | 7.1e-6 |
| L256p | 1.7e-6 (t = 4.5) | 1.74e-6 | 3.1e-6 |
| Q64p | 9.7e-5 | 9.5e-5 | 4.0e-3 |
| Q128p | 9.9e-5 | 9.2e-5 | 4.1e-3 |
| P256 (68532 modes with k <= 32) | 1.21e-4 at (0,32,0), k dx = pi/4 | 1.03e-4 | 4.5e-3 at (0,0,64) |

Threshold 0.02: passed by a factor 165 or more at k <= k_max/2, and still by 4.4 at k_max
itself. The error grows with k as the sixth-order dispersion (`fig/fig_v2.png`, top right);
in the L set-up it falls by 44 from 32 to 64 (order 5.4) and then sits at a floor of
~2e-6 on the lowest modes from 64 to 256 (the second-order part of R^NR [JUDGEMENT]: it
cannot be separated, the m runs carry no gt_ij).
Shell spectrum of P256 at the last dump (my alpha removed): Delta_R / (H^2/(8 pi^2 eps1 Mpl^2)
at crossing) = 1.0104-1.0116 over every shell k <= 32 (my full MS: 1.0104-1.0114; NR and MS
differ by 1.6e-4 at most); Q64p, Q128p, L-rungs: 1.0104-1.0134. The raw shell spectrum
(alpha not removed) scatters around the MS with pull rms 1.007 (max 4.1 over 854 shells),
i.e. cosmic variance only. The departure from the analytic slow-roll power, +1.0 to +1.3
percent, is the known slow-roll correction (my MS gives it too), not an error of the code.

### V3 (A3) Freezing of super-horizon modes (criterion of arXiv:2606.14853) — CONFIRMED

[VERIFIED, run E-20261121-030207-fb6f090] For each of the 1051 modes with N_f - N_k >= 6
(k <= 7.87 dk; crossing k = a H from my background) on every t = 8.5 rung (L32p, L64p,
L128p, Q64p, Q128p, P256): the per-mode power ratio |R_n(N_f)|^2/|R_n(N_k+4)|^2 (first dump
at or past N_k + 4; no alpha needed) equals my full-MS ratio within 2.4e-6 (L64p, L128p) to
3.2e-6 (P256, Q128p); threshold 1 percent. The drift of ln|R_n|^2 from N_k + 4 to N_f is
-1.4e-4 to -3.3e-5 per e-fold (threshold 2.5e-3) and equals the full MS within 1.7e-6. My
deformed (FLRW-lattice) equation of BZ (Manuscript.tex:192-194, 220-222, rewritten for R in
e-folds, `scripts/ref.py`) drifts by -0.0516 to -0.0530 per e-fold (-4 eps1) and ends 9 to
17 percent below the full MS: the NR data sit 3e4 times closer to the full MS than the
tolerance is wide, and 1e4-1e5 times closer than to the FLRW-lattice behaviour.
Figure `fig/fig_v3.png`.

### V4 Constraints: records, odd and even parts, halving, controls — CONFIRMED that the constraints behave as second-order physics plus a converging first-order discretisation error; strict A4 FAILS, A4' PASSES (with (d) read on the maxima)

[VERIFIED, runs E-20261121-030657-c1afe38, E-20261121-031951-82984f8, E-20261121-032413-0672bf9]
Odd part (C(s) - C(-s))/2 and even part (C(s) + C(-s))/2 of H and M_i from the mirrored
pairs, at dumps of equal cycle and time; rms over the box, divided by the record's <[H]>
(<[M]>) of the s = +1 run. "Floor" below = the part that does not scale with s (SCOPE 4b's
definition): rms(C(s) - 2C(s/2)) for the odd part, rms(C(s) - 4C(s/2)) for the even part,
measured on the halved pairs; elsewhere the out band |n|^2 > 9 nmax2 of the odd part.

- Record ratios (every cycle): <|H|/[H]> max 5.1e-11 in the paper's set-up at every N
  (Q64 4.8e-11, Q128 5.0e-11, P256 5.1e-11), 2.6e-12 in the L set-up at N >= 64 (at t = 0:
  the slice); <|M|/[M]> max 3.8e-4 to 4.0e-4 (paper's set-up), 1.5e-5 to 1.8e-5 (L, N >= 64).
- Even part (second order), mean removed: 2.85e-12 at t = 0 (the slice), a plateau of
  ~7e-13 through the entry, the same at every N of a set-up (t = 2: 5.7-6.0e-13 on L32-L256,
  7.0-7.1e-13 on Q64-P256), decaying after the last crossing. With each run's floor removed in
  quadrature the even parts of L128 and L256 (same modes) agree within 0.8 percent at every
  dump (raw: up to 17 percent at t = 0.5, where L256 is floor-dominated).
- Odd part (first order in s: the discretisation error of the linear solution): in the
  paper's set-up it exceeds the even part from t = 2.0 (Q64), 3.0 (Q128), 3.5 (P256), i.e.
  when shells with k dx ~ pi/4 enter (ln(N/8) e-folds after N*), and peaks at 6.0e-11
  (Q64, t = 3.0) and 5.5e-11 (Q128, t = 4.0): independent of N, because k_max dx = pi/2 at
  every N. P256's peak is not in the data (P256m ends at t = 4.5; its odd part is 1.7e-11 at
  t = 4.0 and rising). In the L set-up it falls with N: maximum 5.4e-11 (L32), 1.2e-12 (L64,
  still above the even part after t = 2), in-band 2e-14 (L128) and 3e-16 (L256), below the
  even part.
- Halving (L32, Q64, Q128; where the part exceeds ten times its non-scaling floor): odd part
  of H 1.9989-2.0000, even part 3.986-4.000; odd part of M 1.9975-2.0000, even part of M
  3.990-4.000. With the out-band floor instead, Q64 (1.77) and Q128 (odd 1.43, even 3.66)
  deviate at t <= 2, where the parts are within a few times the rounding: in the paper's
  set-up the out band is a corner of the cube and holds only about a fifth of the rounding.
- Negative controls (noise_pi_sign = -1): record <|H|/[H]> max 9.8e-8 to 9.9e-8,
  <|M|/[M]> 0.21-0.22, i.e. first order. Odd part of the control over that of the proper
  run: 2e3 to 3.6e6 during the early entry, falling to 122 (NC32, t = 3.0), 89 (NC64,
  t = 3.5), 179 (NC128, t = 4.0) at the end of the entry; ratio of the two maxima over the
  run 1874, 1709, 1853.
- Strict A4 (SCOPE 4 item 4: H/[H] and M/[M] of second order, scaling with s^2 under
  halving; the control first order): FAILS on the data. The record halving factor
  F_H = R_H(s)/R_H(s/2) during the entry ranges 0.83-1.99 (L32), 2.0-4.6 (Q64), 2.0-4.1
  (Q128); F_M 1.0-2.0. Two causes, both measured: the record holds the uniform residual of
  the time integration (box mean of H, order s^0, 2-3e-12 on L32 and 3-5e-13 on Q64/Q128;
  order 4.1 in the Courant factor, V6), and the first-order discretisation part that
  dominates once k dx ~ pi/4 shells enter. The control is first order (passes).
- A4' (SCOPE 4b, a proposal): (a) even part halving 3.986-4.000 above the floor: PASS;
  two finest resolutions within 5 percent: PASS in the L set-up (L128/L256 within 0.8
  percent after the floor is removed; raw within 2.5 percent wherever L256's even part is
  more than five times its floor); in the paper's set-up the clause is ill-posed after
  t ~ 3 because Q128 and P256 inject different shells (they agree within 2.6 percent at
  t = 1.5-3.0 and differ by 50 percent to a factor 10 later). (b) odd part halving
  1.9989-2.0000 and convergence at 5.5-5.9 (V5): PASS. (c) record <|H|/[H]> <= 5.1e-11
  (limit 1e-9) and <|M|/[M]> <= 4.0e-4 (limit 1e-3): PASS. (d) control's odd part >= 1e3 x
  proper: PASS on the maxima over the run (1709-1874), FAIL pointwise at the end of the
  entry (89-179). (d) as written has no time qualifier; I read it on the maxima and flag it.
Figure `fig/fig_v4.png`.

### V5 (A5) Spatial order of the odd part; the floor — CONFIRMED

[VERIFIED, runs E-20261121-031951-82984f8, E-20261121-032413-0672bf9] L set-up
(k_max/dk = 8 at every N), order log2(odd_N/odd_2N) of H at equal times (the finer run
interpolated in log to the coarser run's dump times):
- 32 -> 64: 5.54-5.64 for t >= 1.5 (both the whole odd part and its in-band part), 3.8-4.3
  at t <= 1 (the time error, dt ~ dx, dominates while only low shells are in; V6 measures 4).
- 64 -> 128: the whole odd part of L128 is floor-dominated except near t = 2.5 (order 5.82
  there, where it exceeds three times the floor: A5' admits only this point); its in-band
  part (|n|^2 <= nmax2) converges at 5.2-5.9 for t = 1.5-5.0 and 4.0-4.1 at t <= 1, then
  reaches its own floor (~2e-17) after t ~ 5.5.
- 128 -> 256: whole odd part floor-dominated at both N (orders negative); in-band part
  5.8-5.96 for t >= 2.
- M: 5.6-5.9 (32 -> 64, 64 -> 128 in the same windows).
So A5 (order between 4 and 6 before the floor) holds; with A5' ("before the floor" = the
finer odd part above three times the floor) it holds on 32 -> 64 (t >= 1.0: 4.2-5.6) and at a
single point of 64 -> 128.
The floor: the out band of the odd part grows as N^2.45-2.51 between 64, 128 and 256 at
t <= 3 (L), N^2.42-2.49 (paper's set-up), and falls in time as the expansion (1/a^2:
6.3e-13 at t = 0.5 to 3.3e-15 at t = 4.0 on L256). Double-precision rounding as its cause is
supported: (i) it does not scale with s (the out band is the same in the proper and the halved
pairs within 0.93-1.07); (ii) it is the same in the odd and the even part (within 1 percent);
(iii) the non-scaling parts of the even and the odd combination stand in the ratio 1.83-1.97 (1.84-1.85 after t = 0.5) =
sqrt(17/5), which is what four independent noises give (a deterministic s^0 term would
cancel in the odd part); (iv) its size, ~1.6e-13 of [H] per run at N = 128 and t = 0.5, is
about 40 machine epsilons of |chi| per second difference times (N/2pi)^2, and N^2 x sqrt(number
of steps) gives N^2.5; (v) its shell spectrum is flat (white: the rounding of the evaluation
of H) at late times and rises towards the corner of the cube during the entry. I predicted a
k^4 rise throughout; that part of the prediction failed. [JUDGEMENT on (iv)-(v); (i)-(iii)
VERIFIED.] Figure `fig/fig_v5.png`.

### V6 (A6) Temporal order from the Courant runs — CONFIRMED (where resolvable)

[VERIFIED, run E-20261121-030522-c6907b6; first version E-20261121-030412-42dd156]
T25/T12/T06 (N = 32, L set-up, Courant 0.25/0.125/0.0625, s = +-1, run
E-20261119-142317-c851f27; the dumps of the three Courant factors fall at the same times
to 1.3e-14). Richardson order p = log2(|X_0.25 - X_0.125| / |X_0.125 - X_0.0625|), max norm,
at the 9 dumps t = 0.49-4.42:

| Quantity | order | note |
|---|---|---|
| odd parts (first order) of phi, Pi, chi, K, gxx, Axx | 3.93-4.10 | |D2| ~ 1e-6 of the part |
| odd part of my R^NR, |n|^2 <= 8 | 3.94-4.05 | |
| odd part of H | 3.85-4.24 for t <= 2.45 | later |D2| reaches 3e-14, the rounding of H at N = 32 |
| box mean of H (the uniform residual, order s^0) | 4.10 at every dump | 3.1e-11 at Courant 0.25 = 2.6e-12 of [H] |
| box mean of chi | 4.06 | the e-fold error of V1 |
| even parts (second order) of the fields and of H without mean | -0.3 to -0.7 | |D1|, |D2| = 2e-14 to 4e-13: rounding (random walk ~ sqrt(steps)); time error not resolvable |

Order 4 +- 0.5 (A6) holds for everything whose time error is above rounding, which is the
whole first-order solution and the background residual. The second-order part of the
constraints has no measurable time error at N = 32 (it is below 4e-13 absolute, against
an even part of ~1e-10). So A6 is confirmed for the first-order dynamics; it is not tested
(and not testable with these runs) for the second-order part. Figure `fig/fig_v6.png`.

### V7 (A7) Reproducibility; cost — CONFIRMED

[VERIFIED, runs E-20261121-030520-5a23d64, E-20261121-031049-27cdc06, E-20261121-031251-c48670d]
On the files themselves (my reader, assembled by logical location, uint64 views):
- Noise unit test (release core-v0.3, 64^3, 300 cycles): card U1, U2, U3 (1, 8, 64
  MeshBlocks; run E-20261115-170645-3b21217) give 0 differing 64-bit words in all 12
  variables, the two noise fields included (rms 0.011), at all 4 dumps (1.26e7 words per
  comparison); the lockstep mode files are byte-identical and the records equal in every
  column. Restart: processor U4 (E-20261115-170727-d15df12) and card U4
  (E-20261115-180526-6b68c33), restarted at cycle 150, equal U2 bit for bit at cycles 200
  and 300 (time bits too), mode files and records equal. sha256 of all 20 dumps read equal to
  the runs' lists.
- The G1 executable itself (my run, core/scalar-2 `athena_cpu`, the L32p set-up of
  `proc32.list`): 8 MeshBlocks of 16^3 against the registered L32p (one MeshBlock): all 22
  variables bit-identical at t = 0, 0.54, 1.03; restarted from cycle 12: bit-identical to
  both at t = 1.03; mode files byte-identical. The records differ by box-sum rounding only
  (at most 1.7e-14 relative, apart from columns that are themselves rounding).
- Not tested: the rank count (the field runs on one rank; no MPI build in this material).
- Card against processor is not bit-identical (information, not A7): the noise fields of U2
  differ at 4e-16 relative, the slow-roll L64p perturbations at 2e-9 to 4e-7 of their
  maximum.

Cost [VERIFIED from the manifests]: one 256^3 realisation to N - N* = 8.10 (P256, run
E-20261115-172618-f948386, one A100): 1811 s wall, 0.5031 card-hours
(`resources.walltime_s`, `resources.gpu_hours`). P256m with L256p (both to 4.39): 1784 s,
0.4956 card-hours; job C (17 runs, 64^3-256^3): 1504 s, 0.4178 card-hours. Figure
`fig/fig_v7.png`.

## Summary against the G1 criterion (CHARTER 9.8)

"The power spectrum of the slow-roll case agrees with the analytic result" (V2): CONFIRMED,
per mode to 1.2e-4 at k <= k_max/2 (threshold 0.02) and as a spectrum to the analytic
slow-roll power within its own +1.0 to +1.3 percent slow-roll correction. "Super-horizon
modes freeze by the criterion of arXiv:2606.14853" (V3): CONFIRMED, 3e-6 against 1 percent,
1e4-1e5 times closer to the full MS than to the FLRW-lattice equation. "The constraints
converge" (V4, V5): CONFIRMED in the sense that the constraint violation is the
resolution-independent second-order part plus a first-order discretisation part that
converges at order 5.5-5.9 (L set-up) down to a rounding floor that grows as N^2.5; NOT in
the sense of the strict A4 of SCOPE 4, which fails at every N in the paper's set-up. A1, A6,
A7 (recommended): CONFIRMED (A6 for the first-order solution; A7 on the G1 executable too).

## Weak points a gate reviewer should doubt

1. One realisation per set-up and one seed (20261115). V2 and V3 are free of cosmic variance
   by construction (per mode, with alpha known), but any statement about a spectrum average
   rests on one draw.
2. Scouting executables (core/scalar-2 a58e95b), not a release (decision 0013). The A7 noise
   unit test that the track cites ran on release core-v0.3, a different executable; my V7c
   repeats layout and restart on the G1 executable but only on 32^3, one rank, processors,
   two dumps. The card build of the G1 executable is not checked for layout invariance.
3. P256's constraint split stops at t = 4.0 (P256m ends at t = 4.5, and its last dump does not
   match P256's in time). The k_max shell of P256 enters at t = 4.31, so the peak of P256's
   first-order part and its halving are not measured at 256^3; the claim "it does not fall
   with N" rests on Q64 and Q128 (and on P256 rising like them up to t = 4).
4. No halved pair exists at 256^3 or in the L set-up beyond 32^3: the halving factors come from
   32^3-128^3 only, and the non-scaling floor at 256^3 is extrapolated (N^2.5).
5. The "floor" is a definition. With the out band as floor (my first choice) A4'(a), (b) fail
   at Q64/Q128 for t <= 2; with SCOPE 4b's non-scaling part they pass. A reviewer should note
   that the verdict on A4' depends on this choice, made after the data (by the track, and by
   me after seeing that the out band holds only a fifth of the rounding in a corner).
6. A4'(d) passes only on the maxima; pointwise the control/proper ratio falls to 89 at the end
   of the entry. A4' was formulated after the data were seen (SCOPE 4b says so).
7. The absolute constraint levels are 40 times (proper: even rms 7e-13, record 2.6e-12 to
   5e-11) and 100 times (control: 1e-7) below P1's statements (~1e-10, ~1e-5, P1:538-541).
   The ratio control/proper (~1e5) matches P1. The cause is not established [TO VERIFY: the
   definition of [H] or of the box statistic in P1 against core's record].
8. The spatial order of the whole odd part beyond 64 cannot be measured: the floor dominates
   at 128 and 256 in the L set-up; the order 5.8-5.96 at 128 -> 256 is that of the in-band part
   (|n|^2 <= nmax2) only, a band I chose.
9. The R^NR floor of ~2e-6 at L64-L256 is attributed to the second-order part of R^NR by
   judgement; the m runs carry no gt_ij, so it is not separated by parity.
10. V6 tests only N = 32 and only to t = 4.42; the second-order part has no resolvable time
    error there.
11. V2's reference uses the code's own mode files; I checked them against my Bunch-Davies
    integration (6e-13 for n64, 1.6e-6 for n256-n4096), so a shared error of the initial
    mode functions is excluded only to that level.

## For the orchestrator's ruling: strict A4 against A4'

The strict A4 asks that the constraint ratios H/[H] and M/[M] be of second order during the
entry, i.e. scale with s^2 under halving. On these data that is false at every resolution
of the paper's set-up and on L32, for two reasons I measured independently of the track:
the record ratio contains a uniform residual of the time integration that does not depend on
s (it converges at order 4.1 in the Courant factor, V6, and is 3e-13 to 3e-12 of [H]), and a
first-order (odd in s) discretisation part that dominates once shells with fewer than about
eight cells per wavelength enter. That first-order part is not physics: it halves exactly
(1.9989-2.0000), converges at order 5.5-5.9 in the L set-up, and is independent of N in the
paper's set-up only because k_max dx = pi/2 is fixed there. The physical second-order part,
isolated by the mirrored pair, scales by 3.986-4.000 and is resolution-independent (L128 and
L256 within 0.8 percent after the floor is removed). So the strict A4 tests the wrong
object, and A4' tests the right one; its clauses (a)-(c) pass with margin. My reservations:
(d) needs a time qualifier (it fails pointwise at the end of the entry, by a factor ~10),
the floor of (a)/(b) should be named as the non-scaling part (my out-band floor fails them),
the "two finest resolutions" clause of (a) is only meaningful in a set-up with the same modes
at both resolutions (L), and A4' was written after the data were seen. My recommendation
[JUDGEMENT]: rule A4' in, with (d) read as "the maxima over the entry differ by at least
1e3" and the floor defined as the non-scaling part, and keep the strict A4 on record as
failed for the reason above.

## Comparison with the track's numbers (written after the verdicts above were committed, db88f63)

Read now, for the first time: `ladder/results/final/summary.json`, `ladder/results/floor/floor.json`,
`ladder/results/a6/a6.json`, `stage/G1/STATUS.md`, and, to understand two disagreements,
`ladder/results/final2/summary.json`. The verdicts above were not changed after reading them.

Agreements (within 10 percent; most to three digits): A1 per run (e.g. P256 phi 2.0e-12, Pi
8.55e-12, K 1.99e-12; L32p e-folds 5.52e-6: same as mine); A2 max over k <= k_max/2 on every
rung (L32p 8.76e-5, L64p 2.70e-6, L128p 2.54e-6, L256p 1.74e-6, Q64p 9.73e-5, Q128p 9.91e-5,
P256 1.208e-4) and over all k (4.08e-3, 9.65e-5, 7.09e-6, 3.13e-6, 4.00e-3, 4.07e-3, 4.49e-3),
the worst modes (|n|^2 = 16, 5, 1024), the alpha-corrected shell spectrum against the
reference (1.6e-4 to 1.9e-4) and its slow-roll ratio (1.0104-1.0109 for |n| <= 7); A3 drifts
(NR 1.382e-4, MS 1.385e-4, difference 1.444e-6 on L32p: identical to four digits) and the
exclusion of -4 eps1 (factor ~350); A5 orders 32 -> 64 (H 3.79, 4.20, 5.64, 5.60, 5.54, 5.54,
5.55; M 3.12, 3.62, 5.91, 5.64, 5.55, 5.56, 5.57: identical), 64 -> 128 (5.33-5.82) and the
negative orders at 128 -> 256; the floor exponent (2.48 fitted, mine 2.45-2.51); the first e-fold
where the odd part exceeds the even part (1.51, 1.99, 2.96, 3.44 for N = 32-256); the odd and
even parts themselves (e.g. odd H on L32 at t = 2.50: 5.351e-11 both); odd/even maxima at
N = 32, 64, 128 (745, 655, 869; mine 743, 659, 867); halving 2.00 and 4.00 away from the last
dump; record maxima at N = 64 and 256 (4.77e-11, 5.07e-11); controls' <|M|/[M]> 0.204-0.216;
A6 orders 3.93-4.08; cost 0.503 card-hours.

Disagreements above 10 percent:

| # | Quantity | Track | Mine | Reading |
|---|---|---|---|---|
| 1 | max odd/even of H at N = 256 (P256) | 385 (`final/summary.json`; `STATUS.md`: "385-870 ... at every N = 32-256") | 25 at t <= 4.0, the last time-matched dump | the track's own `final2/summary.json` gives 25.1 (last paired time 4.0): 385 came from pairing P256 at t = 4.5038 with P256m at t = 4.5000. STATUS.md still quotes it. |
| 2 | halving factors at the last listed dump | even 16.01 (N = 64), 9.02 (N = 128), 3.86 (N = 32); odd 1.93, 1.97 (`final/`) | 3.99-4.00 and 2.000 at every time-matched dump | the same time mismatch (h runs end at 4.5); `final2` drops these entries |
| 3 | A3 max |ratio_NR/ratio_MS - 1| | 4.57e-6 (L32p), 2.67e-6 (L64p), 2.69e-6 (L128p); STATUS "within 4.6e-6" | 2.72e-6, 2.37e-6, 2.38e-6 (68, 13, 13 percent apart; P256, Q64p, Q128p within 7 percent) | immaterial against 1 percent; the drifts agree to four digits, so the difference is in the dump taken as N_k + 4 or in the reference at that dump [JUDGEMENT] |
| 4 | A1 maxima quoted in STATUS ("1.1e-12 (phi), 2.0e-12 (K) on every rung") | 1.1e-12, 2.0e-12 | phi 2.0e-12 (P256), K 3.6e-12 (L32p); the track's own summary.json has the same 2.0e-12 and 3.63e-12 | STATUS understates by 1.8; immaterial (threshold 1e-4) |
| 5 | record <|M|/[M]> max at N = 256 | 2.72e-4 (`final`), 3.25e-4 (`final2`, window t <= 4.6) | 3.99e-4 (P256's whole record, t <= 8.5) | window, not a contradiction; A4'(c) passes either way |
| 6 | record <|H|/[H]> max at N = 128 | 4.43e-11 (`final`) | 5.04e-11 | `final2` gives 5.04e-11 (from the constraint record) |
| 7 | separation of the negative control | "4e4-1.5e5 times the proper run" (max over time of the record ratio) | odd-part ratio 2e3-3.6e6 early, minimum 89-179 at the end of the entry; ratio of maxima 1709-1874 | different statistics; STATUS's figure is the best case. It matters for A4'(d), which fails pointwise. |
| 8 | second-order part "independent of N within 2.2 percent" | 64 <-> 128: 0.978-1.015; the track's own 128 -> 256 ratios 0.85-0.99 | raw 128/256 up to 17 percent at t = 0.5; 0.8 percent after each run's floor is removed | STATUS's 2.2 percent holds for 64 <-> 128 only; 128 <-> 256 needs the floor removed |
| 9 | card against processor (A14) | 2.2e-15 | noise fields of U2: 3.2e-16 to 4.4e-16 of their maximum | different normalisation [JUDGEMENT]; not part of A7 |

Nothing in the track's numbers changes a verdict above. Items 1, 2 and 4 are errors in
`ladder/results/final/` or `stage/G1/STATUS.md` that the lead should correct (the track's
`final2` already corrects 1, 2 and 6).

Note ledger: the only ledger committed under `note/tables/` (HEAD of track/E-stoch-inf at
the time of writing) is `ledger.tex` of note v0 (G0, runs of 2026-11-15: references,
cost model); no G1 ledger was committed, so the recomputation of ten G1 ledger numbers was
not available.
