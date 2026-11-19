# JOURNAL of E-stoch-inf

Append-only, newest at the bottom, one entry per session:
`## <UTC time>  session <name>  commits <a>..<b>  runs <ids>` followed by
did / found / evidence / changed my mind about / open. Predictions are written here before
a test runs, outcomes after.

## 2026-11-15T13:55Z  session lead (Opus)  commits e303538..  runs see below

Lead session of the first wave. The four helpers (spec = E-pre-1, codebase = E-pre-2,
langevin = E-pre-3, noise = E-pre-4) finished; their journals are
`spec/JOURNAL.md`, `codebase/JOURNAL.md`, `langevin/JOURNAL.md`, `noise/JOURNAL.md`.
This entry records the lead's independent check of their artefacts, the check of core's
implementation on `core/scalar-field` (836ac86), and the G0 package.

### Predictions, written before the lead's runs (13:55Z)

L-R (reruns, `analysis/lead/rerun_helper.sh`, one registered run per package). Every
deterministic script reproduces its helper's numbers: numeric JSON leaves identical or
within 1e-9 relative (same code, same seeds, same machine). The langevin quadratic
reference rerun with 1e5 instead of 1e6 realisations (other effective sample): var/var_lin
at sigma = 0.01 within 3 of its standard errors (about 0.004) of the helper's 0.9981, and
sigma = 1 within 0.01 of 1.4492. Refuted by any deterministic leaf off by more than 1e-9
or a statistical one off by more than 3 standard errors.

L-B (`analysis/lead/lead_bg.py`, own integrator and own fixing formula, not the helper's).
Quadratic: phi0 = -14.0950, m = 1.73494e-6, eps1(N*) = 1.1107e-2 and V(N*) = 2.690e-2
(Mpl = 100 units) to 4 digits; inflection: USR (eps2 > 3) from about 2.5 to 6.5 e-folds
after N*, eps1 minimum near 1e-12. One slow-roll mode leaving at N* + 1.5: with metric
perturbations P_R(N_f) within 2 percent of H^2/(8 pi^2 eps1) at exit and a super-horizon
slope of ln P below 2e-3 per e-fold (3 to 6 e-folds after exit); without them a slope
within 15 percent of -4 eps1. Refuted by a digit mismatch of the background or slopes
outside these bands.

L-N (`analysis/lead/lead_dn.py`, iterated first-passage integrals, not the helper's
recursion). V2 of 2206.11234: <N> = 9.38603 and var N = 4.52154 to 1e-4 relative.
Refuted by a larger difference.

L-I (derivation, no run). The delta-Pi erratum of SPEC 5.3 follows from P2's own
dictionary (main_V2PRD.tex 297-313): delta Pi = d/dt delta phi^NR - phidot Psi_G with
chi^NR = int (Psi_G - Psi_B) dt; at t* (chi_0 = 0) the extra term is -sqrt(2 eps1) Mpl H
Psi_B whatever Psi_G is. Refuted if the dictionary gives a different term.

L-U (core's generator, `analysis/lead/u_runs.py`, runs U1-U8 of noise/NOISE_SPEC.md
section 9 with core's processor executable `wt/core-scalar/.work/exe/athena_cpu_836ac86`,
read only). Every deterministic test of the validator passes: A0 format, A1 exact
reconstruction from the keys (to 1e-11 of the rms; the dumps are double precision), A5,
A6, A8, A10, A11 (1, 8, 64 MeshBlocks bit-identical), A12 (restart at cycle 150
bit-identical), A13 (N = 32 against N = 64), A15 (seeds); the statistical tests pass at
the family-wise level 1e-3/D. Refuted by any deterministic failure; a single statistical
failure with all deterministic tests passing is read by the rule of NOISE_SPEC 10 (repeat
on U8). A smoke run of 4 cycles first measures the time per run.

13:58Z, smoke L-U0 (run E-20261115-135218-bdf4710; nrpic-run names runs with the short
owner id "E"): 4 cycles of the 64^3 base case took 78 s of processor time, 1.35e4
zone-cycles per second (the processor build of core's executable runs serially; Z4c
dominates). The 64^3 x 300-cycle base case would cost about 95 min per run, nine runs.
Change before the runs: a scaled base case `inputs/u_base32.athinput` (N = 32, nmax2 = 100,
hubble 1.1, 120 cycles, dumps every 40, restart at 60; U3 = 64 MeshBlocks of 8^3; U5a/U5b
N = 16 and 32 with nmax2 = 36). The predictions of L-U stand unchanged for this case;
statistical tests at shells with fewer than 100 effective modes report "n/a" by the
validator's rule. The 64^3 x 300 base case stays pending (card or a longer processor run).

### Outcomes so far (14:05Z)

- L-R spec (run E-20261115-135531-0c4e629): holds. All 1182 numeric leaves of
  summary/quadratic/inflection/norm_test identical bit for bit; ic_check identical.
- L-R noise (run E-20261115-135532-5ec2b09, exit 1): holds for every deterministic result
  (T-N0 bit-identity on 153684 + 2000 keys, self-test 49 leaves, T-N8 112 leaves identical;
  T-N1 counts; T-N5 reader bitwise across 1/8/64 MeshBlocks, 5.4e-8, axes 7e-2). The exit 1
  is one leaf: the maximum deviation of the library logarithm, 6.2e-13 against 1.16e-12
  (median 1.1e-15 in both), an environment property of numpy.log, not of the code path.
  Prediction refuted as worded for that one leaf; no consequence.
- L-R codebase (run E-20261115-140116-87c1cc5, exit 1): holds; d1, d3, d4, cost identical;
  in d2 only the six wall-clock "seconds" leaves differ (timings).
- L-B (run E-20261115-135532-3f958a1): holds. phi0 -14.094995, m 1.734945e-6, eps1(N*)
  1.110706e-2, V(N*) 2.69006e-2; inflection USR 2.5237 to 6.5498, eps1 min 9.72e-13 at 8.33.
  SR mode leaving at N* + 1.5: full P_R(N_f) = 1.0108, slope -5.8e-4/e-fold; without metric
  perturbations slope -0.0519 against -4 eps1 = -0.0513 (1.2 percent).
- L-N (same run): holds. <N> = 9.385995 +- 3e-6, var N = 4.5215404 +- 3e-9 (helper: 9.38603,
  4.521540).
- L-I (derivation): holds; written into SPEC 5.3. The printed eq. (17) has a Psi_G term
  (zero in the geodesic gauge, P2:490) where the Psi_B term belongs; it drops the chi-dot
  term of its own dictionary.
- L-U (run E-20261115-135523-a32c3a6): all nine AthenaK runs completed (U1-U3, U5a/b, U6-U8
  in 290-315 s each, U5a 37 s, U4 restart 137 s). Validations: Markov Heaviside passes
  everything; Markov tanh passes A0, A2-A8, A10 and FAILS A1 (exact reconstruction:
  1.07e-10 of the rms against 1e-11, worst stoch_c2 at cycle 120); the frozen validation
  did not run: the validator read U5a (N = 16) with U1's nmax2 = 100 and stopped ("cut
  reaches the Nyquist plane"). The second is a defect of the validator (it would have hit
  the specification's own base case, nmax2 = 256 at N = 32, the same way); fixed by the
  lead: `--res-lo-input`, `--res-hi-input`.

### Predictions before the follow-up runs (14:06Z)

L-U2 (`analysis/lead/lu_diag.py` on U6 and U1). The A1 excess of U6 is the conditioning
of sqrt(W(t) - W(t - dt)) for modes long past crossing (W near 1; both code and reference
form the difference naively, with libm and numpy exponentials that may differ by an ulp).
Expected: on modes with dW > 1e-6 the coefficient difference is below 1e-13 of the base
amplitude; on every mode it stays below the conditioning line 3 x 2u/(2 sqrt(dW)), u =
1.1e-16; in U1 (frozen, dW enters linearly) the A1 value is below 1e-11. Refuted by a large
difference on a mode with dW > 1e-6 (that would point to keys, times or the stage
bookkeeping) or by points above the line.

L-U3 (`analysis/lead/lu_validate.sh` on the outputs of E-20261115-135523-a32c3a6, each run
with its own input): frozen validation passes A0-A10 and A11 (1, 8, 64 MeshBlocks
bit-identical), A12 (restart at cycle 60 bit-identical), A13 (N = 16 against 32 within
eps_m), A15 (seeds); Markov Heaviside passes; Markov tanh fails A1 only, as before (the
contract is not loosened after seeing data). Refuted by any other failure.

### Outcomes of the follow-up runs (14:08Z)

- L-U3 (validations E-20261115-140502-2957846): holds. Frozen tanh: every test passes,
  A1 4.1e-14, A11 bit-identical for 1 vs 8 and 1 vs 64 MeshBlocks, A12 restart at cycle 60
  bit-identical, A13 2.4e-15 (N = 16 vs 32), A15 seeds independent. Markov Heaviside: all
  pass. Markov tanh: A1 only fails (1.07e-10 vs 1e-11), as predicted; the contract stays at
  1e-11. A1 passing in the frozen scheme confirms core's dump convention (the dump at
  cycle m holds the increment of the step ending at m: noise request C5 answered by data).
  The diagnostic part of this run failed on a syntax error in lu_diag.py (keyword names);
  rerun as E-20261115-140553-0b75e1e.
- L-U2 (diagnostic E-20261115-140553-0b75e1e, `fig_lu_diag.png` looked at): main part
  holds: in U6 the modes with dW > 1e-6 agree to 4e-14 of their base amplitude, the
  differences grow like 1/sqrt(dW) for modes past crossing (sqrt of a difference of numbers
  near 1; one ulp of W between libm and numpy exp). U1 sits at the 1e-15 floor. Refuted as
  worded: "every mode below the line 3 x 2u/(2 sqrt dW)": at dW ~ 0.1 points reach 1.5 times
  the line, which is the FFT rounding floor (~1e-15) that the line omits. Cause of the A1
  excess named after this run: conditioning, not keys, times or stage bookkeeping.
- The A2 shell means of core's output at shells 1-7 equal those of the noise helper's
  synthetic self-test (1.58, 0.98, 1.08, 1.19, 0.91, ...): same amplitudes because they are
  keyed by wave vector whatever N is.

### Did / found / changed my mind about / open

Did: reran the four helper packages from their commits (runs E-20261115-135531-0c4e629,
-135532-5ec2b09, -140116-87c1cc5, -140502-f70b223), checked their central claims by
independent code (L-B, L-N) and by derivation (L-I), read core's noise and kick code
against SPEC, ran core's generator through the noise validator (L-U), fixed two small
defects (validator inputs for U5; manifest status values that broke `nrpic-run budget`),
aligned SPEC 5.3, 5.4, 2.5, 10 and added A8, wrote the G0 package (spec/scope/SCOPE.md v1 with
the owner's decisions and the recommendation; stage/G0/CHECKLIST.md, EVIDENCE.md, OPEN.md),
stage/G1/STATUS.md, RISKS.md, nine outbox messages, acknowledged C-sidm's stream-2 note.
Helpers' journals: spec/JOURNAL.md, codebase/JOURNAL.md, langevin/JOURNAL.md,
noise/JOURNAL.md.

Found: everything the helpers claimed and the lead re-ran holds; the defects were in
wording (SPEC 5.3), cross-package consistency (SPEC 5.4 keys), and the validator's U5
handling. Core's generator is right to rounding; one test-only scheme needs a
cancellation-free window increment.

Changed my mind about: the processor build as the place for the noise unit test (it runs
Z4c serially; the specified 64^3 x 300 case is 95 min per run), and about the G0 needing
an FFT request (superseded by the wave-vector keys and the separable synthesis).

Open: G0 products (REVTeX note v0, schematics, verifier report); group decision; G1 waits
for core's initial slice, diagnostics, card build; the R^NR analysis code is Track E's next
item; U9 and the 64^3 base case on a card. Tool guard: `stage/G0/REPORT.md` could not be
written (subagent report-file guard); the scoping content is in spec/scope/SCOPE.md.

L-R langevin (run E-20261115-140502-f70b223, 14:10Z): holds. V2 identical (94 leaves);
quadratic reference at 1e5 realisations within 3 standard errors of the helper's 1e6 run at
every variant (sigma = 0.01: 0.9966 +- 0.0043 against 0.9981; sigma = 1: 1.4433 +- 0.0067
against 1.4492, inside the predicted 0.01).
Side effect found and repaired: the langevin scripts also write into `langevin/results/`
and `langevin/fig/`, so the 1e5 rerun overwrote the committed 1e6 reference files in the
worktree; restored from git before committing (HANDOFF trap).

## 2026-11-19T14:58Z  session lead wave 2b (Opus)  commits 8f056963..  runs see below

Review of the helpers of waves 2 and 2b (analysis, note, verifier, ladder) from their
artefacts, then the stage packages G0 and G1. Predictions written before each check ran:

- LR1 (rerun of the ladder's final analysis, `analyse_all.py`, `verdicts.py`,
  `make_figures.py` at the current commit on the raw outputs of runs
  E-20261115-172636-ce98836, -173719-e810503, -172618-f948386, -172629-312a82c,
  -172625-416fec0): every numeric leaf of `summary.json` and of the per-run JSON equal to
  the committed `ladder/results/final/` within 1e-9 relative (deterministic scripts, same
  inputs). Refuted by any larger difference outside paths and wall times.
- LR2 (rerun of `floor_analysis.py` on the rerun's `res/` and of `a6_analysis.py` on run
  E-20261119-142317-c851f27): `floor.json` and `a6.json` equal to the committed ones within
  1e-9 relative. Refuted likewise.
- LR3 (independent A2/A3 on L32p, my own code: own dump reader, complex FFT, amplitudes from
  core's twin `python/nrpic/scalar_field.mode_alpha` instead of the track's
  `noise/ref/philox_ref.py`, own background and Mukhanov-Sasaki integration with LSODA in
  place of DOP853): at the last dump max D_n over |n| <= 4 is 8.8e-5 within 10 percent and
  over all 1054 modes 4.1e-3 within 10 percent; A3: every mode with N_f - N_k >= 6 has
  |Q_n(N_f)/Q_n(first dump after N_k + 4) - 1| < 1e-4 and a drift of ln|R^NR_n|^2 equal to
  that of the reference within 1e-5 per e-fold. Refuted if the D_n differ from the
  ladder's by more than 20 percent or if any threshold (0.02, 0.01, 2.5e-3) fails.
- LR4 (constraint records read directly from `sr.sf.con.hst`): <|H|/[H]> at the last row
  3.12e-12, 1.83e-13, 1.12e-14 for L32p, L64p, L128p (factors near 16); box means of phi,
  Pi, K within 1e-10 relative of my own Friedmann integration at every row (A1).
  Refuted by other record values or an A1 deviation above 1e-10.
- LR5 (odd and even parts of H from the dumps of L32p/L32m and L32ph/L32mh, own code):
  odd-part halving factor 2.00 +- 0.01 and even part (box mean removed) 4.00 +- 0.05 at
  every dump from t = 0.5 to 4.0; odd/even above 100 at t = 2.5; order of the odd part
  between L32 and L64 (log-linear interpolation in time) between 5.3 and 5.9 at
  t = 2.0-3.5. Refuted by factors outside these bands.
- LA1 (rerun of the analysis package's synthetic tests T1-T5): 15 of 15 pass, numbers equal
  to run E-20261115-171445-36152c4 within 1e-12 relative.
- LV1 (rerun of the verifier's V1, V4, V8 scripts): JSON equal within 1e-9 relative
  (V4 uses fixed seeds).
- Development run of `stage/G1/scripts/lead_check.py` (into `scratch/E-stoch-inf/tmp/devcheck`,
  not a result, disclosed): it ran through; it counted only 40 modes for A3 because the
  crossing e-folds were computed for k = |n|^2 instead of |n| (my bug, fixed before the
  registered run). Seen there before registering: A2, the record values, A1 and the parts of
  H (the predictions above are unchanged).
- LR3-LR5 outcome (run E-20261119-150238-b81e33f, `fig_lead_check.png` looked at): all
  CONFIRMED. A2 on L32p at N_f = 8.10: max D_n 8.76e-5 for |n| <= 4 (ladder 8.8e-5), 4.08e-3
  over all 1054 modes (ladder 4.08e-3, top shell |n|^2 = 64). A3: 1051 modes; largest
  |Q_n(N_f)/Q_n(N_k + 4) - 1| 2.7e-6 (ladder 4.6e-6 with interpolation to N_k + 4; mine takes
  the first dump after it), drift of ln|R^NR|^2 at most 1.38e-4 per e-fold, NR minus linear
  1.4e-6. A1 from the records: phi 6.4e-13, 6.8e-13, 1.2e-12; Pi 4.5e-12, 3.4e-12, 4.4e-12;
  K 3.5e-12, 4.9e-13, 1.2e-12 (L32p, L64p, L128p); record <|H|/[H]> at t = 8.5: 3.124e-12,
  1.832e-13, 1.115e-14, factors 17.05 and 16.43. Parts of H at N = 32: odd halving factor
  2.000 and even 3.997-4.000 at every dump from t = 0.54 to 3.53; odd/even 745 at t = 2.50;
  order of the odd part 32 -> 64 5.64, 5.60, 5.54, 5.54, 5.55 at t = 1.5-3.5 and 3.79, 4.20
  at t = 0.5, 1.0 (the early orders the ladder attributes to the time error and the floor).
- LN1 (prediction before the run, small defect fixed by the lead): `noise/ref/noise_ref.py`
  now forms the tanh window increment as sinh(s H dt)/(2 cosh x1 cosh x0) (request of the
  analysis package). With it the unchanged validator `validate_noise.py` gives for U6
  (Markov tanh) A1 = 4.0e-15 on the card output of run E-20261115-170645-3b21217 and
  3.3e-15 on the scaled processor output of E-20261115-172423-5234cce, each within a factor
  1.5, and every other test passes as before (the values `val_cf.py` gave with the same
  formula in memory). Refuted if A1 stays above 1e-11 or any other test changes its verdict.
- LN1 outcome (run E-20261119-150541-3210cd6, `val_card_u6/fig_val_card_markov_tanh.png`
  looked at): CONFIRMED. The unchanged validator with the fixed reference gives A1 = 4.57e-15
  (card U6) and 4.02e-15 (scaled processor U6), all tests pass on both; the frozen card
  validation (U1-U3, U5, U8) passes as before, its A1 now 5.3e-15 instead of 9.8e-14 because
  core's power model takes the same increment.
- LR1 STOPPED (run E-20261119-145853-ef835c2, closed as failed, exit -15): the full rerun read
  the cold 128^3 and 256^3 dumps through the ladder's memory map at 3.6 MB/s (the disk gives
  124 MB/s sequentially; load average about 100); the original analysis ran right after the
  card jobs with the dumps in the page cache. Two of about 45 steps in 8 minutes; about 150 GB
  to read. Replaced by LR1', written before it runs:
- LR1' (partial rerun at the current commit): the original intermediate outputs
  (`res/` of run E-20261115-194633-9e04ed8, checksums verified today with `nrpic-run verify`:
  101 files PASS) are copied except those of the 32^3 and 64^3 rungs (L32p, L32m, L32ph,
  L32mh, NC32p, NC32m, L64p, L64m, NC64p, NC64m and their pairs), which are recomputed from
  the raw dumps; then `verdicts.py`, `make_figures.py`, `floor_analysis.py` and
  `a6_analysis.py` (on the six A6 runs of E-20261119-142317-c851f27) run as the package
  runs them. Prediction: the recomputed per-run and pair JSON equal the originals, and
  `summary.json`, `floor.json`, `a6.json` equal `ladder/results/{final,floor,a6}/` within 1e-9
  relative (paths and times excepted). Refuted by any larger difference.
- LR1' outcome (run E-20261119-150842-ca70d37): CONFIRMED. The 17 recomputed JSON files of the
  32^3 and 64^3 rungs (2295 numeric leaves) are bit-identical to those of run
  E-20261115-194633-9e04ed8; `summary.json`, `floor.json`, `a6.json` bit-identical to
  `ladder/results/`; the eight figures pixel-identical (rms 0) to `ladder/fig/`.
- LA1, LV1 outcome (run E-20261119-150346-a513bc8): CONFIRMED, every leaf identical (T1-T5:
  48; V1 91, V2 288, V3 2, V4 37, V5 3, V8 9).
- A12 from the registered checksums: U4 dumps and mode files equal U2's on processors and on
  the card (sha256sums.txt of E-20261115-170727-d15df12, -170645-3b21217, -180526-6b68c33).

### Did / found / evidence / changed my mind about / open

Did: merged main (decision 0016); closed the verifier's stranded run E-20261115-174600-81652ff;
reviewed the helpers of waves 2 and 2b from their artefacts (`stage/REVIEW-wave2.md`): reruns of
the ladder's analyses, of the analysis package's tests and of the verifier's computations, my
own code on the SR ladder, the noise reference fixed and revalidated, every figure relied on
looked at; corrected SPEC (P-e, the P2 equation name, dead pointer, cost), SCOPE (cost, A2
wording, locator key FKTT, section 4b with the proposed A4'/A5', note on section 6), RISKS
(R15-R17); G0 checklist re-collected and every item PASS or NA (REVIEW.md, VERIFY, OPEN,
EVIDENCE 5); G1 package written (CHECKLIST, STATUS with each criterion met or not, EVIDENCE,
OPEN, REVIEW, the lead's check script, figure and results); seven outbox messages; seven
inbox messages acknowledged.

Found: every number of the ladder that I reran or recomputed holds (sections 1-2 of the
review); G1's spectrum and freezing criteria are met at 256^3 in P1's set-up; the
constraints converge but the owner's A4 fails in its strict form in P1's set-up, and A4's
"M/[M] second order" was never consistent with P1:540-541. The Markov-tanh A1 failure of wave 1
was the reference's, now fixed. The P2 equation we called "eq. (17)" is the 23rd numbered
environment (kb found it).

Evidence: runs E-20261119-150238-b81e33f, -150842-ca70d37, -150346-a513bc8, -150541-3210cd6;
stopped -145853-ef835c2; figures looked at: `stage/G1/fig/fig_lead_check.png`, the ladder's
eight, the note's seven, `analysis/fig/fig_t2_extraction.png`, `fig_plane_constraint_ratios.png`,
the U6 validator figure.

Changed my mind about: the cost margin (now measured, 0.503 card-hours per SR realisation, and
the Courant factor justified by A6, so the verifier's theta = 0.025 case is moot); A4 as written
(it was ill-posed for M and too strict for P1's own resolution).

Open: the orchestrator's ruling on A4'/A5'; a G1 verifier; the G1 schematics and note
sections; core's release of the scalar-2 set-up; the USR package of wave 3a (`usr/`, not
reviewed here, run E-20261119-145835-67cde45 in flight); A6 at 64^3 on a card, L5, L9, a
second seed. Card-hours used this session: none (1.43 of 10 in all).
