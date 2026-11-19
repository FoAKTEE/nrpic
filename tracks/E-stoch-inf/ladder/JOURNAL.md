# Journal of the ladder package (E-stoch-inf, wave 2)

Helper of owner E-stoch-inf; package `tracks/E-stoch-inf/ladder/`. Task: the slow-roll
(SR) ladder of the specification toward gate G1 (`../spec/SPEC.md` 7.2-7.3, thresholds A1-A8
of `../spec/scope/SCOPE.md` section 4), run with core's published executables of branch
`core/scalar-2` (a58e95b, `scratch/core/exe/core_scalar-2/`, READY present at 08:43 PST =
16:43Z), at most two card-hours.

## Entry 1, 2026-11-15 17:25Z: set-up and predictions, written before any ladder run

### What was read

- Core's READY note and interface `tracks/core/interfaces/scalar_field_2.md` (core/scalar-2):
  `<problem> id = stochastic` (initial slice at N* of SPEC 5.3 with the corrected delta Pi),
  `<scalar_field> noise_mode_scale`, `con_dcycle` (record `sr.sf.con.hst`), dump layout
  NRSFDMP2 with `dump_metric`, `dump_constraints`.
- Core's own results at 32^3-128^3 with k_max/dk = 8 (READY, interface section 6): constraint
  ratios <|H|/[H]> <= 4.7e-11, <|M|/[M]> <= 3.7e-4 at 32^3; a first-order truncation part
  converging at order 5.5-5.8 on N = 32, 64, 128 and a second-order part independent of N;
  R^NR per mode within 2.8e-3 of W R alpha for all 1054 modes at 32^3 over 3.1 e-folds.
  Core has not run 256^3 beyond ten steps, nor beyond t = 3.2 with dumps, nor the freezing
  criterion. These are core's numbers [TO VERIFY by this package]; this package checks
  them with its own reader, its own linear reference and its own amplitudes.

### Inputs (no simulation yet)

- Mode files of the SR case, rows `|n|^2 Re R Im R Re dR/dtau Im dR/dtau` at N* in code
  units: `inputs/modes_n64.txt` = core's `problems/scalar/sr_stochastic_modes.txt` (56 shells,
  Bunch-Davies at N0); `inputs/modes_n{256,1024,4096}.txt` from core's
  `make_case.py --case quadratic --kstart 100` (run E-20261115-171633-f574079; the manifest
  says "failed (exit 1)" because the last command of the run, `tail -3` on several files, is
  invalid; the three generators finished and wrote their files and logs, checked by hand:
  216, 856, 3416 lines; case.json phi0 = -2.66679478988, pi0 = 0.0297300406809, mass =
  0.18287765590, eps1* = 1.11071e-2, eps2* = -2.21331e-2, H*/Mpl = 9.4869151038e-6, equal to
  the values of core's example input and to SPEC 6).
- Base input `inputs/sr_base.athinput` (core's example with dumps every 0.5 time units of
  phi, Pi, chi, gt_ij, K, At_ij, alpha, H, M_i, E; con record every cycle; Courant 0.25;
  seed 20261115 as core, so that core's 32-128 numbers can be compared).

### Runs planned (lists `inputs/*.list`)

| Name | N | nmax2 (k_max/dk) | s = noise_mode_scale | noise_pi_sign | tlim (e-folds) | Where |
|---|---|---|---|---|---|---|
| P256 | 256 | 4096 (64) | +1 | +1 | 8.5 (8.04) | card, job A |
| P256m | 256 | 4096 | -1 | +1 | 4.5 (4.4) | card, job B |
| L256p, L256m | 256 | 64 (8) | +1, -1 | +1 | 4.5 | card, jobs B, C |
| L128p, L128m, L64p, L64m | 128, 64 | 64 | +1, -1 | +1 | 8.5 | card, job C |
| Q128p (8.5), Q128m, Q128ph, Q128mh (4.5) | 128 | 1024 (32) | +1, -1, +1/2, -1/2 | +1 | | card, job C |
| Q64p (8.5), Q64m, Q64ph, Q64mh (4.5) | 64 | 256 (16) | same | +1 | | card, job C |
| NC128p, NC128m; NC64p, NC64m | 128, 64 | 1024, 256 | +1, -1 | -1 | 4.5 | card, job C |
| L32p, L32m (8.5); L32ph, L32mh, NC32p, NC32m (4.5) | 32 | 64 (8) | | | | processors |

"L" = the convergence set-up of P1:747-773 (fixed modes, k_max/dk = 8, N varied); "P" and
"Q" = the paper's set-up k_max = N k_sigma*/4 (four cells per shortest wavelength,
P1:512) at N = 256, 128, 64 (at N = 32 it coincides with L32); "NC" = negative control
P1:541 (the sign of the Pi kick flipped). Estimated card time from core's measurements
(1.23 s per step at 256^3 with 4096 modes; 0.155 s at 128^3): job A 31 min, job B 31 min,
job C 27 min, together about 1.5 card-hours; requested walls 45 + 38 + 37 min = 2.0.

### Definitions used by the analysis (`scripts/ladder_analysis.py`, written next)

- Coefficients of a dump field f on the cell centres x = (j + 1/2) h of the box [0, 2 pi)^3:
  c_n[f] = N^-3 sum_x f(x) exp(-i n.x), n in the hemisphere of NOISE_SPEC with
  0 < |n|^2 <= nmax2 (code units: k = |n|, dk = 1).
- R^NR_n = c_n[chi]/(2 <chi>) + (1/4) sum_ij nhat_i nhat_j c_n[gt_ij] + (H_b/Pi_b) c_n[phi],
  H_b = -<K>/(3 <alpha>), Pi_b = <Pi> (P1:522-526 with the corrected factors of TH
  appendix:513-522, SPEC 9 E6; box means of the same dump).
- Linear reference R^lin_n(t) = s L^(-3/2) W_k(t) R_k(t) alpha_n: R_k(t) integrated by this
  package (DOP853, rtol 1e-12) from the mode-file values at t = 0 with
  d2R/dt2 + (3 - eps2) H dR/dt + (k/a)^2 R = 0 on its own Friedmann background in code
  units started from (phi0, pi0); W = (1 + tanh[s_w ln(a H/k)])/2, s_w = 5; alpha_n from
  Track E's independent Philox re-implementation `noise/ref/philox_ref.py:mode_alpha`
  (seed 20261115, degree of freedom 0, epoch 0).
- D_n(t) = |R^NR_n/R^lin_n - 1| (complex ratio, phase included); Q_n(t) =
  |R^NR_n|^2/|R^lin_n|^2; N_k: e-fold where k = a H on the reference background.
- Constraints: odd and even parts of the dump fields under s -> -s,
  H_o = (H(+) - H(-))/2, H_e = (H(+) + H(-))/2 (same for M_i), rms relative to the box
  mean <[H]> (column 10 of `sr.sf.con.hst`); the box ratios <|H|/[H]>, <|M|/[M]> of the
  record (columns 4, 7).

### Thresholds (written by the owner before this package, SCOPE 4; restated, not changed)

- A1: box means of phi, Pi, K within 1e-4 relative of the Friedmann reference (SR).
- A2: D_n(N_f) < 0.02 for every mode with |n| <= k_max/2 (SR, N_f = N* + 8).
- A3: for every mode with N_f - N_k >= 6: |Q_n(N_f)/Q_n(N_k + 4) - 1| < 0.01; equivalently
  the drift of ln|R^NR_n|^2 from N_k + 4 on below 2.5e-3 per e-fold in magnitude (the FLRW
  lattice drifts at -4 eps1 = -0.046 to -0.054, SPEC 7.3).
- A4: H/[H] and M/[M] of second order during the entry (scaling with s^2 when s is halved;
  even part dominating the odd part); magnitude within a factor 10 of P1's 1e-10 for H
  (P1:538-539); the sign-flip control of first order (P1:541).
- A5: on the ladder N = 32, 64, 128 (k_max/dk = 8) the convergent part converges at an order
  between 4 and 6 before the floor.

### Predictions (each with what would refute it)

- P1 (A2, P256 at N_f = 8.04): max D_n over |n| <= 32 below 2e-3 (core: 7.6e-5 for |n| <= 4 at
  32^3, eight cells per wavelength or more); over all modes up to |n| = 64 below 1e-2 (core:
  2.8e-3 at 32^3 for the upper shells at four cells per wavelength). Refuted if any mode
  with |n| <= 32 has D_n >= 0.02 (then A2 fails).
- P2 (A3, P256 and L32-L128 at N_f): every mode with N_f - N_k >= 6 (|n|^2 <= about 60)
  has |Q_n(N_f)/Q_n(N_k + 4) - 1| < 1e-3 and |drift| of ln|R^NR|^2 below 2.5e-3 per e-fold,
  equal to the drift of R^lin within 2e-4 per e-fold. Refuted (A3 fails) if any of these
  modes reaches 0.01, or if the drift approaches the FLRW value -0.05.
- P3 (spectrum): shell means of |R^NR|^2 over |R^lin|^2 equal 1 within 1e-3 for
  |n| <= 32 at N_f; the shell spectrum Delta[R^NR] scatters about Delta[R^lin] within the
  cosmic variance of the shell (relative standard deviation 1/sqrt(M_shell), M_shell
  hemisphere modes); Delta[R^lin](N_f) / [H_k^2/(8 pi^2 eps1_k Mpl^2)] lies in 1.005-1.015
  for |n| <= 7 (SPEC 7.3: 1.010-1.012). Refuted if the shell ratio departs from 1 by more
  than 3/sqrt(M_shell) in more than 1 percent of the shells, or the alpha-corrected ratio by
  more than 2e-3.
- P4 (A4 at the paper's set-up, P256 and P256m; Q128, Q64 with s = +-1/2): the odd part of
  H (first order: truncation of the stencils on the shells with fewer than eight cells per
  wavelength) is comparable to or larger than the even part while the upper shells enter
  (N about 3 to 4.4 at 256^3), as core found at 32^3 (odd 7.5e-11 against even 2.8e-11 in H
  at N = 1.6, `scratch/core/core-20261115-163726-7be94e4/summary.json`); so at four cells
  per wavelength H is not purely of second order during the late entry, and the halving
  test gives factors between 2 and 4 rather than 4. Early in the entry (only shells with
  eight or more cells per wavelength inside) the factor is 4 within 5 percent. The
  magnitude <|H|/[H]> stays below 1e-9 (within a factor 10 of P1's 1e-10). Refuted if the
  odd part stays below a tenth of the even part through the entry at 256^3 (then A4 passes
  in its strict form).
- P5 (A5, ladder L32-L256 with s = +-1): rms of the odd part of H converges at order 5.3 to
  6.0 between 32 -> 64 and 64 -> 128 at every dump during the entry (t = 0.5-2.5); between
  128 -> 256 the order drops where the odd part at 256 reaches the rounding floor of H
  (about 1e-15 of [H]); the even part (box mean removed) is the same at 128 and 256 within
  1 percent; the box ratio <|H|/[H]> converges toward the even-part curve (P1's plateau,
  P-g). Same for M with the order between 4 and 6. Refuted (A5 fails) if any order on
  32 -> 64 -> 128 falls outside 4 to 6.5 during the entry, or the even part changes by
  more than 5 percent between 128 and 256.
- P6 (negative control NC32, NC64, NC128): <|H|/[H]> at least 1e3 times the proper run
  during the entry and odd in s (ratio odd/even rms above 10); <|M|/[M]> between 0.05
  and 0.5 (core at 32^3: H 9.8e-8, M 0.16-0.21). Refuted if the control's H is within a
  factor 100 of the proper run.
- P7 (A1, by-product): box means of phi, Pi, K in the record within 1e-10 of this package's
  Friedmann reference at every N (core: 6.4e-13 at 32^3); refuted above 1e-4 (A1 fails).
- P8 (cost): P256 runs at 1.1 to 1.5 card-seconds per step; one 8-e-fold realisation at
  256^3 costs 0.45-0.6 card-hours (downgrade threshold of SCOPE 4 item 5: 5 card-hours).
- P9 (convergence of A2 on the L ladder): at a fixed dump after the entry (t = 2.5 and
  t = 4.5), max D_n over all 1054 modes falls by about 2^5-2^6 from 32 to 64 and then
  reaches a floor below 1e-4 set by second-order effects (nonlinear couplings, R ~ 5e-5).
  Refuted if it does not fall between 32 and 64.

## Entry 2, 2026-11-15 17:45Z: submissions, a failed processor run, the self-test, the N = 32 rung

Submissions (all scouting, executables of core/scalar-2 a58e95b, sha256 in the manifests):
card jobs A E-20261115-172618-f948386 (Slurm 4469), C E-20261115-172625-416fec0 (4470),
B E-20261115-172629-312a82c (4471), all pending behind ten other jobs at 17:40Z.

Failed run, on record: E-20261115-172521-e098160 (processors, stopped after 28 s). nrpic-run
passes its command without a shell, so the literal argument '$NRPIC_RUN_DIR' was not
expanded and the six 32^3 runs wrote into a directory of that name inside the worktree. I
stopped them by process id, moved the directory into the run's output directory
(`misplaced_literal_run_dir/`), and made `scripts/run_list_cpu.sh` take the directory from
the environment and refuse a relative one. Rerun: E-20261115-172636-ce98836 (completed;
L32p and L32m 8.5 time units in 505-520 s, the 4.5-unit runs in 268-274 s, serial).

Self-test E-20261115-172935-ddfade0 on core's 32^3 dumps (run core-20261115-160134-3fde433):
this package's reader equals core's `read_dump` bit for bit (largest difference 0); R^NR at
t = 0 equals s L^-3/2 W R alpha_n within 7.5e-10 for the three modes with W > 1/2 (W = 1/2
exactly at |n| = 1); amplitudes of another seed give a median deviation of 1.4-2.7 (the
extraction sees the realisation). Core's figure for the slice was 1.1e-11; the 7.5e-10 here
is at the level of second-order terms and of the window at W = 1/2, far below every threshold
[JUDGEMENT; not traced further].

Outcomes at N = 32 (k_max/dk = 8, which at N = 32 is also the paper's four cells per shortest
wavelength), analysis run E-20261115-173540-b69c63f, figures `fig/proc32/`, numbers
`results/proc32/`:
- A1 (L32p, 8.1 e-folds): box means of phi, Pi, K within 6.4e-13, 4.5e-12, 3.6e-12 of this
  package's Friedmann reference (threshold 1e-4; P7 predicted below 1e-10: confirmed). The
  e-fold count -ln<chi>/2 differs from ln a by 5.5e-6 (time integration at Courant 0.25;
  core: 5.5e-6). [Corrected at 17:52Z: the first version of this line quoted the numbers of
  the 4.4-e-fold run NC32p (6.3e-13, 7.7e-12, 3.5e-12, 3.3e-6) instead of L32p.]
- A2 at N_f = 8.10: max D_n = 8.8e-5 over the 128 modes with |n| <= 4 (threshold 0.02;
  pass), 4.1e-3 over all 1054 modes (the top shell |n|^2 = 64). The deviation is set during
  the entry (N = 1.5 to 3.5) and constant afterwards (`fig_a2_modes.png`, right). At N = 3.0
  it is 2.8e-3, as core reports for its own run to N = 3.14 (2.8e-3).
- A3: 1051 modes with N_f - N_k >= 6; max |Q_n(N_f)/Q_n(N_k + 4) - 1| = 4.6e-6 (threshold
  0.01; pass by a factor 2000); max |drift of ln|R^NR|^2| = 1.38e-4 per e-fold (threshold
  2.5e-3), equal to the full-MS drift of the same modes within 1.4e-6 per e-fold. An FLRW
  lattice would drift at -4 eps1 = -0.046 or so. P2 confirmed at N = 32.
- Spectrum: shell sums of |R^NR|^2 over |R^lin|^2 within 1.7e-4 of 1 for |n| <= 4; no shell
  outside 3/sqrt(M_shell) of the ensemble spectrum; Delta[R^lin](N_f) over the slow-roll
  formula 1.0104-1.0109 for |n| <= 7 (SPEC 7.3: 1.010-1.012). P3 confirmed.
- Constraints (pair L32p/L32m, halving pair L32ph/L32mh, `fig_a4_paper.png`,
  `fig_a5_parts.png`): the odd part of H (first order in the amplitude) rises from 5e-13 of
  <[H]> at N = 0.5 to 5.4e-11 at N = 2.5 and dominates the even part from the dump at N = 1.5
  on (the dumps at N = 1.0 and 1.5 bracket the crossing; largest ratio odd/even 745); the
  even part (box mean removed) is 2.8e-12 at t = 0 (second-order violation of the slice),
  7e-13 at N = 0.5-2, then falls. The halving test separates them exactly: even part factor
  4.00 (second order), odd part factor 2.00 (first order) at every dump. M behaves the same
  way: odd part up to 3.2e-4 of <[M]> at N = 2.5 against an even part of 7e-6. A uniform
  part of H (box mean of the even part, +2.9e-12 of <[H]>) does not depend on the
  amplitude: it is the residual of the time integration of the background that core
  identified, and it makes the record ratio <|H|/[H]> between s = 1 and s = 1/2 close to 1
  before the entry (thick line in `fig_a4_paper.png`). So at N = 32 with four cells per
  shortest wavelength, A4 in its strict form ("second order during the entry") FAILS for
  both constraints from N = 1.5 on, as P4 predicted, while the magnitude <|H|/[H]>
  stays below 4.7e-11 (within a factor 10 of P1's 1e-10). Whether the odd part is the
  truncation error that converges away is A5, which needs N = 64 and up.
- Negative control (NC32p/m): odd part of H 7e-8 to 1e-7 of <[H]> during the first two
  e-folds (1e4-1e5 times the proper run), odd part of M 0.16-0.21 of <[M]>; P6 confirmed.

Prediction before the 64^3 processor hedge (E-20261115-*, list `inputs/proc64.list`, L64p
and L64m to t = 4.5): the odd part of H at N = 64 is 2^5.3 to 2^6 times smaller than at 32 at
every dump of the entry (after interpolation to common times, since the dump times differ
by up to one step between resolutions); the even part (box mean removed) agrees with
N = 32 within 10 percent where it dominates the noise of the decomposition.

## Entry 3, 2026-11-15 17:42Z: the inputs checked against Track E's own reference

Prediction (written before the run): the mode files of core's `make_case.py` agree with
Track E's E-pre-1 reference `spec/ref/ms_reference.py` (own background and Bunch-Davies
integration, sympy potential) within 1e-8 at N* for shells started at the same point, and
phi0, pi0 of the input agree with that background within 1e-12.

Outcome, run E-20261115-174008-7aee5ff: R_k and dR_k/dtau within 7.2e-10 (complex values,
`modes_n64.txt`, from N0, six shells up to |n|^2 = 64) and 4.2e-11 (`modes_n4096.txt`, from
k/aH = 100, seven shells up to 4096); moduli within 2e-11; H*/Mpl, phi*, pi* in code units
equal to 1e-15. Confirmed. So the inputs are those of the specification, and the
comparisons of A2-A3 (which start the reference from the file values) and of the spectrum
against the slow-roll formula test the evolution, not the input.

Also checked (dry tests, not results): the reference with t_eval at the dump times gives the
same N = 32 numbers as with dense output to the last digit printed; the 256^3 reference
(548958 modes, 3414 shells) takes 0.7 s, the amplitudes 4.6 s.

## Entry 4, 2026-11-15 17:43Z: the extraction factor of R^NR (SPEC 9 E6) tested by a run

SPEC 9 E6 records the corrected extraction factors of the thesis (TH appendix:518-520) as a
hand derivation [JUDGEMENT]. Prediction: on the last dump of L32p the factor 1/4 of the
anisotropic term gives the smallest deviation from the linear solution; leaving the term
out, doubling it or flipping its sign raises max D_n for |n| <= 4 to the size of that term,
about eps1 R, i.e. 5e-3 relative. Outcome, run E-20261115-174214-74becdd: max D_n for
|n| <= 4 is 8.8e-5 with 1/4, 5.1e-3 without the term, 5.2e-3 with 1/2, 1.0e-2 with -1/4.
Confirmed: the evolution satisfies the corrected extraction of SPEC 9 E6 (to about 2
percent of the factor), which can be relabelled [VERIFIED by run] (a request to the lead,
who owns SPEC).

## Entry 5, 2026-11-15 18:55Z: the N = 64 rung on processors (hedge), A5 from 32 to 64

Runs: E-20261115-173719-e810503 (L64p, L64m to t = 4.5, 69 min serial each, 22.5 s per
step, 1.16e4 zone-cycles/s); analysis E-20261115-184737-92c4fa1 (32 and 64 together;
figures there under `fig/`, copied to `fig/proc32_64/`).

Prediction of entry 2 (odd part of H at 64 smaller by 2^5.3-2^6 during the entry; even
part equal within 10 percent where it dominates) against the outcome:
- Odd part of H, order 32 -> 64 on common times (log-linear interpolation of the 64 run to
  the dump times of the 32 run): 5.64, 5.60, 5.54, 5.54, 5.55 at t = 1.5, 2.0, 2.5, 3.0,
  3.5 (the entry and its tail); M: 5.91, 5.64, 5.55, 5.56, 5.57. Confirmed, and inside the
  A5 band 4-6. Core measured 5.5-5.8 on its own runs.
- Before the entry of the upper shells the odd part is small (5e-13 of <[H]> at N = 32,
  3.7e-14 at N = 64) and converges more slowly: H 3.77 and 4.20 at t = 0.5 and 1.0, M 3.10
  and 3.61. Not predicted. [JUDGEMENT, not tested] the time integration at a fixed Courant
  factor contributes an odd part of order 4 in 1/N (dt scales with h), and a part that
  converges at third order (M) has not been identified; the N = 128 rung shows whether
  these early orders rise or stay. Read strictly ("order between 4 and 6"), A5 holds during
  the entry and fails for M in the first e-fold, where the odd part is 50-300 times below
  its peak.
- Even part of H (box mean removed): equal at 32 and 64 within 4 percent up to t = 2.0
  (where it dominates the odd part at 64), within 12 percent later where it is 1e-14-5e-14
  of <[H]>. Confirmed where it matters: the second-order violation does not depend on the
  resolution, which is P1's plateau (P-g).
- At N = 64 (eight cells per shortest wavelength) the odd part of H exceeds the even part
  only from N = 2.0 (largest ratio 15 against 745 at N = 32); the record <|H|/[H]> peaks
  at 2.6e-12 (32: 4.3e-11), <|M|/[M]> at 1.5e-5 (32: 3.4e-4).
- A2 at t = 4.5 (N = 4.39): max D_n 2.0e-6 for |n| <= 4 and 9.4e-5 over all 1054 modes,
  against 4.0e-3 at N = 32 at the same time: a factor 42 (order 5.4). P9 confirmed for the
  first step.
- A1: box means within 3.1e-12 (phi), 6.5e-12 (Pi), 3.4e-12 (K); e-folds from <chi> within
  2.0e-7 (5.5e-6 at N = 32: ratio 28, close to 2^4 = 16 to 2^5, the step halved).

A2 with the reference that uses the stencil's k^2 per wave vector (the wording of SCOPE 4,
"the reference uses the lattice's discrete wave number"; added to `ladder_analysis.py`
before this analysis): at N = 32 the deviation is 8.1e-4 for |n| <= 4 (continuum shells:
8.8e-5), at N = 64 it is reported in `results/proc32_64/L64p_judge.json`. The NR
modes follow the continuum mode functions more closely, as expected when the field is
injected by the sources at horizon crossing from the code's own (continuum) mode
functions [JUDGEMENT]; both pass 0.02 by a factor 25 or more.

## Entry 6, 2026-11-15 19:20Z: the 256^3 production in the paper's set-up (job A)

Run E-20261115-172618-f948386 (Slurm 4469, P256: N = 256, nmax2 = 4096, 548958 modes in
3414 shells, 1386 steps to t = 8.5 = N* + 8.10, 18 dumps of 2.95 GB): exit 0, 1811 s wall,
0.503 card-hours, 1.30 s per step with the dumps and the constraint record every step
(1.29e7 zone-cycles/s), peak GPU memory 19.6 GB. Analysis E-20261115-191327-63c7397
(figures `fig/P256/`, numbers `results/P256/`).

Predictions of entry 1 against the outcome:
- P1 (A2): max D_n over the 68532 modes with |n| <= 32 is 1.21e-4 (predicted below 2e-3;
  threshold 0.02): PASS. Over all 548958 modes 4.5e-3 (predicted below 1e-2). The
  deviation grows as about |n|^4 above |n| = 10 (`fig_a2_modes.png`, left), is set during
  the entry and constant afterwards (right). [JUDGEMENT] the |n|^4 growth and the size at
  the top (omega dt = 0.39 at |n| = 64) point to the fourth-order time integration of the
  sub-horizon phase; test A6 (Courant factor halved) would tell.
- A2 against the stencil-k^2 reference (SCOPE wording): 6.2e-3, worse than the continuum
  shells, and the two references differ by 6.3e-3 at |n| = 32. The stencil reference
  accumulates the dispersion error of the sub-horizon phase from N* to crossing (about 32
  radians for |n| = 32, times half of the 3.8e-4 error in k^2), while in this scheme a
  mode enters the lattice only through the window, from the code's own mode functions.
  So for this scheme the continuum reference is the right one, and the SCOPE wording
  should say so (request to the lead). Both pass 0.02.
- P2 (A3): 1051 modes with N_f - N_k >= 6 (|n|^2 <= 62); max |Q_n(N_f)/Q_n(N_k + 4) - 1| =
  3.4e-6 (threshold 0.01): PASS by a factor 3000; max |drift| of ln|R^NR|^2 from N_k + 4 =
  1.38e-4 per e-fold (threshold 2.5e-3: PASS), equal to the full-MS drift within 1.7e-6 per
  e-fold. The FLRW-lattice behaviour (-4 eps1 = -0.049 per e-fold here) is excluded by a
  factor 350 in the drift. Super-horizon modes freeze as in full linear theory.
- P3 (spectrum): shell sums of |R^NR|^2 over |R^lin|^2 within 1.6e-4 of 1 for |n| <= 32
  (predicted 1e-3); 0.35 percent of the shells beyond 3/sqrt(M_shell) of the ensemble
  spectrum (predicted below 1 percent; 0.27 percent expected for Gaussian scatter);
  Delta[R^lin](N_f) over H_k^2/(8 pi^2 eps1_k Mpl^2) = 1.0104-1.0109 for |n| <= 7 (SPEC 7.3:
  1.010-1.012). PASS on every count (`fig_spectrum.png`).
- P7 (A1): box means within 2.0e-12 (phi), 8.6e-12 (Pi), 2.0e-12 (K) of the Friedmann
  reference; e-folds from <chi> within 1.3e-9: PASS.
- P8 (cost): 1.30 s per step, 0.50 card-hours per 8-e-fold realisation (predicted 1.1-1.5 s
  and 0.45-0.6): confirmed; a tenth of the downgrade threshold (5 card-hours, SCOPE 4
  item 5).
- Constraint record: <|H|/[H]> at most 5.1e-11, <|M|/[M]> at most 4.0e-4 (32^3 in the same
  set-up: 4.3e-11, 3.4e-4), within a factor 10 of P1's 1e-10 for H. Their split into odd
  and even parts needs the mirrored run P256m (job B, pending at 19:20Z).

## Entry 7, 2026-11-19 14:16Z (wave 2b): resumption, runs closed, prediction for A12

Wave 2 stopped on 2026-11-15 after entry 6 (usage limit). State found on 2026-11-19: the
worktree clean, card jobs B (E-20261115-172629-312a82c, Slurm 4471, 29.7 min) and C
(E-20261115-172625-416fec0, Slurm 4470, 25.1 min) completed with exit 0, and the final
analysis of all rungs E-20261115-194633-9e04ed8 (started 19:46Z) had finished at 19:54:34Z
with exit 0 (`.nrpic/result.json`) but its manifest still said "running". Closed with
`nrpic-run finish` today, with the two runs of the analysis package the task names:
E-20261115-170727-d15df12 (processor U2 then U4, exit 0, U2 6012 s, U4 2845 s) and
E-20261115-180526-6b68c33 (U4 on a card, Slurm 4479, exit 0, 300 cycles in 3.8 s).

Prediction for the U4 validation (A12 of the noise contract), restated from the analysis
package's journal (`../analysis/JOURNAL.md`, P5 at 17:05Z and P5' at 18:05Z on 2026-11-15,
written before either run): U4 = U2 restarted from the restart file at cycle 150 gives
dumps at cycles 200 and 300 bit-identical to U2, on processors (processor U4 against
processor U2) and on the card (card U4 against card U2 of run E-20261115-170645-3b21217).
Refuted by any differing bit in any common field.

## Entry 8, 2026-11-19 14:23Z: predictions for the temporal convergence test A6 (before any run)

Why now: A6 (SCOPE 4: "order 4 +- 0.5 in theta", fixed seed, Courant factor halved twice;
L6 of `../codebase/DESIGN_REVIEW.md` 8.1) is recommended for G1 and has not run; entry 6
attributed the |n|^4 growth of D_n at the top shells of P256 to the time integration
[JUDGEMENT], which only a run at another Courant factor can test. Also read since: the
spatial derivatives are of sixth order (NGHOST = 4: coefficients 1/90, -3/20, 3/2, -49/18
in `athenak/src/utils/finite_diff.hpp:219-237`) [VERIFIED by reading]; the integrator is
`rk4` (input).

Set-up (`inputs/sr_a6.athinput`, list `inputs/a6proc.list`, processors): the L32 case
(N = 32, nmax2 = 64, which at N = 32 is also the paper's set-up) at theta = 0.25, 0.125,
0.0625, s = +-1, to cycle 90 x 0.25/theta (t = 90 pi/64 = 4.418, N = 4.31 e-folds, after the
entry of every shell), dumps every 10 x 0.25/theta cycles, so the three runs dump at the
same times (t = 10 k pi/64). Differences Delta(theta_a, theta_b) between runs at equal
times; order p = log2[Delta(0.25, 0.125)/Delta(0.125, 0.0625)].

Estimate behind the predictions [JUDGEMENT]: at fixed theta the L ladder converged at order
5.4-5.6 in N (entry 5; A2 by 42 from 32 to 64), near the spatial order 6, not near 4. If the
error at N = 32 is S h^6 + T dt^4 with dt = theta h, an order of 5.5 means T is about 15
percent of the total at N = 32, theta = 0.25. RK4 for an oscillation with omega dt = 0.39
(top shell |n| = 8, theta = 0.25) gives a phase error of about (omega dt)^4/120 = 2e-4 per
radian, against a sixth-order stencil error of 1.8 percent in k^2 at four cells per
wavelength (symbol 2.422 against (pi/2)^2 = 2.467).

- PA6a (order): the per-mode differences of R^NR (largest over the modes with W > 1/2,
  relative to |R^NR|) and the rms differences of the perturbations of phi, chi and K fall at
  order 4 +- 0.5 at every dump with t >= 0.98 (where they exceed 1e-12 relative); the box
  means (background) as well. Refuted (A6 fails) if any of these orders lies outside
  3.5-4.5 where the difference is above 1e-12 relative, in particular an order near 1
  (sources not evaluated at the stage times, D4 of the design review).
- PA6b (which error dominates A2's top shells): halving theta changes the deviation from
  the linear solution D_n of the top shells (|n|^2 = 49-64) at the last dump by 3 to 25
  percent, and the next halving by less than 2 percent: the deviation at four cells per
  wavelength is mostly spatial (sixth-order stencils), so entry 6's attribution to the
  time integration is wrong. Refuted if D_n of the top shells falls by more than a factor 4
  at the first halving (then it is temporal, as entry 6 guessed).
- PA6c (constraints): the uniform part H0 (box mean of the even part of H) falls by 16 +- 3
  per halving after the entry (fourth order in the step, core's T12: H0 17.1 times smaller
  at N = 64); the odd part of H during the late entry (t = 1.5-3.5) changes by less than 25
  percent between theta = 0.25 and 0.0625 (spatial truncation, first order in s); the even
  part with its mean removed (the second-order violation) by less than 5 percent.
  Refuted if the odd part falls by 16 per halving (then the "first-order truncation at
  late entry" of A4 would be temporal, and the rewording proposed for A4 would have to say
  so).
- Cost: 2.9 s per step on one core (entry 2): 4.4, 8.7 and 17.4 min for theta = 0.25,
  0.125, 0.0625.

## Entry 9, 2026-11-19 14:28Z: outcomes of jobs B and C and of the final analysis (all rungs)

Runs: job B E-20261115-172629-312a82c (P256m, L256p; 0.496 card-hours), job C
E-20261115-172625-416fec0 (L256m, L64, L128, Q64, Q128 with halving, NC64, NC128; 0.418
card-hours), analysed with the processor rungs and job A in E-20261115-194633-9e04ed8
(written on 2026-11-15 19:54Z, read today; `results/final/`, figures `fig/final/`, all six
looked at). Card time of the package: 0.503 + 0.496 + 0.418 = 1.42 card-hours of the two
allowed. Then the floor analysis E-20261119-142713-32c883a (supersedes -142625-82a7990,
which lacked the even-part check; `results/floor/`, `fig/floor/fig_floor.png`, looked at).

Verdicts on the thresholds (SCOPE 4, restated in entry 1):
- A1 PASS on every rung: box means of phi, Pi, K within 1.1e-12, 8.6e-12, 2.0e-12; the
  e-fold count from <chi> within 5.5e-6 (N = 32), 3.3e-7 (64), 2.0e-8 (128) over 8.1
  e-folds, falling by 16.6 and 16.3 per doubling (fourth order in the step, which halves
  with h); 7.5e-10 at 256 over 4.4 e-folds.
- A2 PASS on every rung (max D_n over |n| <= k_max/2 at the last dump): L32 8.8e-5, L64
  2.7e-6, L128 2.5e-6, L256 1.7e-6 (at N = 4.39), Q64 9.7e-5, Q128 9.9e-5, P256 1.21e-4
  (threshold 0.02). P9 CONFIRMED: over all 1054 modes at N_f = 8.1 the deviation falls from
  4.08e-3 (32) to 9.65e-5 (64), a factor 42 (2^5.4), then 7.1e-6 (128); for |n| <= 4 it
  stops at 2.5e-6 from 64 on (the second-order part of R^NR that core's T12b identified at
  N = 64, `git show core/scalar-2:tracks/core/JOURNAL-scalar2.md`, entry 14).
- A3 PASS on every rung with 8.1 e-folds (L32, L64, L128, Q64, Q128, P256; 1051 modes
  each): max |Q_n(N_f)/Q_n(N_k + 4) - 1| between 2.7e-6 and 4.6e-6 (threshold 0.01), drift
  of ln|R^NR|^2 1.38e-4 to 1.41e-4 per e-fold, equal to the full-MS drift within 1.8e-6
  (threshold 2.5e-3; the FLRW lattice: -0.05). L256 ran 4.4 e-folds only (no mode with
  N_f - N_k >= 6).
- Spectrum (P3) CONFIRMED on every rung: shell ratios against the reference with the same
  alpha_n within 1.9e-4 (Q64), 1.7e-4 (Q128), 1.6e-4 (P256), 3.6e-6 (L64), 3.9e-7 (L128);
  shells beyond 3/sqrt(M_shell) of the ensemble: 0 to 0.59 percent (Q128), below the 1
  percent of P3.
- Negative control (P6) CONFIRMED at N = 32, 64, 128: <|H|/[H]> up to 4.0e4, 1.5e5, 1.3e5
  times the proper run; odd/even at least 6.7e4 in the first two e-folds; <|M|/[M]> 0.20,
  0.21, 0.22 (predicted 0.05-0.5).
- Cost (P8) CONFIRMED: 1.13-1.30 card-seconds per step at 256^3; one 8-e-fold realisation
  0.50 card-hours.

A4 (constraints of second order during the entry) FAILS in the paper's set-up
(k_max = N/4, four cells per shortest wavelength) at every N from 32 to 256, as P4
predicted and as core's T12 found at 32 and 64:
- The part of H odd in s (first order in the amplitude) exceeds the even part (second
  order) during the late entry by up to 745 (N = 32), 655 (Q64), 869 (Q128), 385 (P256).
  It first exceeds it at N = 1.51, 1.99, 2.96, 3.44 e-folds, where ln(N/8), the crossing of
  the first shell with fewer than eight cells per wavelength, is 1.39, 2.08, 2.77, 3.47
  (dumps every 0.5 e-folds): the first-order part comes in with the shells that the
  sixth-order stencils resolve with fewer than eight cells per wavelength.
- Halving s separates the parts exactly where they are above the floor: odd part 2.00
  (first order), even part 3.99-4.00 (second order) at N = 32 at every dump after t = 0,
  at Q64 from N = 1.5 and at Q128 from N = 2.5 (`fig/floor/fig_floor.png`, middle).
- The magnitude passes: <|H|/[H]> at most 4.3e-11 (32), 4.8e-11 (Q64), 4.4e-11 (Q128),
  5.1e-11 (P256), within a factor 10 of P1's 1e-10; <|M|/[M]> at most 3.8e-4. The peak
  does not fall with N in this set-up, because the top shells always have four cells per
  wavelength.
- In the convergence set-up (k_max/dk = 8) A4 holds from N = 128 on: the largest odd/even
  ratio is 15 at L64, 0.27 at L128 and 0.53 at L256 (where the odd part is the floor).
- The record ratio <|H|/[H]> is no order test (core's T12): its halving factor lies at
  0.8-0.9 at N = 32 and 3.3-4.5 at N = 64 before the late entry (thick lines of
  `fig/final/fig_a4_paper.png`), because of the amplitude-independent uniform residual H0
  of the time integration and the negative box mean of the second-order part. P4's "early
  factor 4 within 5 percent" holds for the even part, not for the record.
- Artefact found: the last dump of a run with tlim = 4.5 comes after a shortened step
  (t = 4.500), while its partner with tlim = 8.5 dumps at the same cycle at t = 4.516
  (Q64), 4.504 (Q128, P256). The pairs Q64p/Q64m, Q128p/Q128m, P256/P256m, L32p/L32ph
  therefore compare different times at their last dump, which leaks the odd part into the
  even part there (the even halving factors 16.0 and 9.0 at the last dump of N = 64, 128).
  The last dumps of these pairs are left out of every verdict above; `floor_analysis.py`
  drops them by checking the times.

A5 (convergence before the floor), with P5 against the outcome:
- P5 REFUTED as written: the order of the odd part of H between 32 and 64 is 3.79 and 4.20
  at t = 0.5, 1.0 (predicted 5.3-6.0), and between 64 and 128 it is -1.57, -0.64, 1.66 at
  t = 0.5-1.5; between 128 and 256 it is negative at every dump to t = 3.5 (-2.5 to -0.8),
  not only "where the 256 part reaches a floor of about 1e-15": the floor is 6e-13 of
  <[H]> at N = 0.5 and 7e-15 at N = 3.4 at N = 256, ten to six hundred times the predicted
  value. The even part changes by 1-15 percent between 128 and 256 (predicted within 1).
- The floor: the odd part at 256 grows with N, as N^2.48 for H and N^2.63 for M between 128
  and 256 at t <= 1.5; it does not depend on the amplitude (halving factor 1.000-1.002 at
  Q128 for N <= 2, 0.998 at t = 0 at every N); it falls in time roughly as the physical
  gradients (a^-2). If it is noise uncorrelated between the s = +1 and s = -1 runs, it must
  enter the even part as much as the odd part: adding it in quadrature predicts
  even_128/even_256 = 0.858, 0.922, 0.982, 0.992, 0.936, 0.972, 0.981 at t = 0.5-3.5,
  against the measured 0.857, 0.923, 0.979, 0.991, 0.910, 0.964, 0.979 (the model
  overcorrects at t >= 2.5, where the 128 odd part is no longer pure floor). Between 64 and
  128 the even part agrees within 2.2 percent. [JUDGEMENT, formed after seeing the summary
  of 2026-11-15, not by a prediction] the floor is rounding of double precision in the
  second derivatives (an error of order eps/h^2 per step, accumulated as a random walk over
  a number of steps proportional to N, hence N^2.5), redshifted with the gradients. No run
  in another precision tests it.
- Entry 5's open point (low early orders 3.1-4.2 between 32 and 64) is explained by the
  same floor: at those times the 64 part lies within a factor 1.1-1.9 of the floor model
  for M and 1.9 for H at t = 0.5. [Amended by entry 11: at N = 32 the early odd part is
  the fourth-order time error, so 32 -> 64 at a fixed Courant factor converges there at
  order 4, lowered by the floor at 64.]
- A5 with "before the floor" made operational (the finer part at least 3 times the floor
  model F(N, t) = odd_256(t) (N/256)^q; factor and model fixed after the summary was seen,
  before this script ran): orders 4.20-5.82 for H and 5.55-5.91 for M on 32 -> 64 -> 128;
  PASS (band 4-6). The highest order of the band is approached, not exceeded; the scheme is
  sixth order in space and fourth in time (A6 below decides how the two mix).
- The uniform residual H0 after the entry converges at fourth order in the step: the
  record <|H|/[H]> at N_f = 8.1 is 3.12e-12 (32), 1.83e-13 (64), 1.12e-14 (128), factors
  17.0 and 16.4 (`sr.sf.con.hst` of L32p in E-20261115-172636-ce98836, of L64p and L128p in
  E-20261115-172625-416fec0, last rows). <|M|/[M]> at N_f: 1.6e-7, 1.2e-8, 2.9e-8 (the
  floor of M rises with N).

So "the constraints converge" (G1) holds for the part that the scheme is supposed to make
converge (odd part at order 5.5-5.9, H0 at order 4), the second-order violation is
independent of the resolution (P1's plateau, even part within 2.2 percent between 64 and
128), and above both sits a rounding floor that grows as N^2.5 and limits what 256^3 can
show during the first two e-folds (6e-13 of <[H]>, still a hundred times below P1's 1e-10).

## Entry 10, 2026-11-19 14:34Z: outcome of A12 (prediction of entry 7)

Run E-20261119-141654-c2a10d1 (`noise/validate/validate_noise.py`, `results/a12/`):
- Processors: U4 (restarted at cycle 150) against U2 of run E-20261115-170727-d15df12:
  A12 PASS, the noise fields stoch_c0 and stoch_c2 at cycles 200 and 300 bit-identical
  (largest difference 0); the base run passes A0-A8, A10 (A9 not applicable), as the
  analysis package found for it on 2026-11-15.
- Card: U4 of run E-20261115-180526-6b68c33 against the card U2 of
  E-20261115-170645-3b21217: A12 PASS, bit-identical; A0-A8, A10 pass.
- Beyond the validator, which reads the noise fields only: the whole dump files
  u.sf.00002.dump and u.sf.00003.dump (25 MB each, every field of the dump) and the mode
  files of U4 equal those of U2 byte for byte on both platforms (`cmp`, by hand, not
  registered).
P5 and P5' of the analysis package HOLD. The validator's figures (noise statistics of the
base run, `val_*_a12/fig_val_*.png` in the run directory) were looked at; a bit-identity
has no figure of its own.

## Entry 11, 2026-11-19 14:55Z: outcome of A6 (predictions PA6a-c of entry 8)

Runs E-20261119-142317-c851f27 (six processor runs, 470 s at theta = 0.25, 800-850 s at
0.125, 1630 s at 0.0625, exit 0), analysis E-20261119-145230-ff0dff2 (supersedes
E-20261119-145115-7388a05: the same numbers, a cleaner figure, and "not applicable"
instead of "fail" where no difference lies above 1e-12; `results/a6/a6.json`,
`fig/a6/fig_a6.png`, looked at). The dump times of the three Courant factors agree to
1e-9 by construction (checked by the script).

- PA6a CONFIRMED, A6 PASS: between theta = 0.25/0.125 and 0.125/0.0625 the differences
  fall at order 3.93-4.08 at every dump from t = 0.98 on for R^NR (all modes with
  W > 1/2: 4.02-4.05 during the entry, 3.96-3.97 after it), the perturbations of phi, chi
  and K (4.01-4.08) and the box mean of chi (4.06 at every dump). The largest per-mode
  difference of R^NR between 0.25 and 0.125 is 2.9e-4 after the entry, so the time error
  at the Courant factor of the ladder is below 3e-4 of R. Not testable: the box means of
  phi and K, whose differences (1e-14 to 3e-12 relative) are at rounding and grow with the
  number of steps (order -1.1 for phi); the predicted order 4 for "the box means as well"
  holds only for chi. No sign of a degraded order from the sources (D4 of the design
  review): the sources are evaluated at the stage times, as SPEC 2.4 asks.
- PA6b CONFIRMED, and entry 6's [JUDGEMENT] REFUTED: the deviation from the linear
  solution of the top shells (|n|^2 >= 49) at the last dump is 3.97e-3, 3.75e-3, 3.74e-3
  at theta = 0.25, 0.125, 0.0625: the first halving changes it by 5.7 percent (predicted
  3-25), the second by 0.4 percent (predicted below 2). The deviation at four cells per
  wavelength is 94 percent spatial (sixth-order stencils), not the time integration.
  For |n| <= 4: 8.7e-5, 8.0e-5, 7.96e-5 (92 percent spatial); only the lowest shells
  (|n| <= 2, D_n of a few 1e-6 at 0.25) are dominated by the time error (`fig_a6.png`,
  lower left).
- PA6c CONFIRMED: during the late entry (N = 1.5-3.4) the odd part of H changes by at most
  4 percent between theta = 0.25 and 0.0625 (ratios 1.041, 1.003, 1.000 per halving at
  N = 1.46, 1.94, 2.42; 1.000 after), that of M by at most 12 percent (1.000 after N = 2):
  the first-order part of A4's failure is spatial truncation. The even part with its mean
  removed is independent of theta (ratios 0.999-1.000). The box mean of the even part
  (H0 and the mean of the second-order part) after the entry is 2.9e-12, 1.7e-13, 1.0e-14
  of <[H]>, factors 17.1 and 16.6 per halving (predicted 16 +- 3), and the differences of
  that mean converge at order 4.10 at every dump: H0 is the fourth-order time error.
- Not predicted: before the late entry (N = 0.49, 0.98) the odd part of H at theta = 0.25
  (5.4e-13 of <[H]>) is 15.6 times that at 0.125 (M: 15.9), i.e. the early first-order part
  at N = 32 is the fourth-order time error, not truncation and not the floor. So entry 5's
  [JUDGEMENT] ("the time integration at a fixed Courant factor contributes an odd part of
  order 4 in 1/N") is now supported by a run; at N = 64 the floor takes over (entry 9).

What this means for A4 and A5 [JUDGEMENT]: at a fixed Courant factor the odd part has two
sources, the time error (fourth order, dominant before the late entry at N = 32) and the
spatial truncation of the shells with fewer than about eight cells per wavelength (sixth
order, dominant during the late entry at every N of the paper's set-up); above both sits
the rounding floor. The A5 band "4 to 6" brackets exactly these two orders.
