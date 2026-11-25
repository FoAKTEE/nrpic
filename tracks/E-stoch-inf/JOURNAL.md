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

Addendum (same session, 15:50Z). `nrpic-stage verify E-stoch-inf G0 --no-checksums` failed
`compare` only on `note/tables/claims.{md,json}` (42 -> 43 agreeing numbers): the claims check
reads SCOPE.md and SPEC.md, which this session edited. Prediction LN2 before the rerun: a
registered rerun of `note/scripts/ledger.py` gives `ledger.tex` and `parameters.tex` identical
to the committed ones, and `claims.*` that differ only in line locators and in the rows whose
wording changed (cost and overhead in SCOPE 8/9, SPEC 11.2). Refuted by any other change.
The full verify with checksums was stopped twice (by PID) because the disk was shared with
two other leads' verifies (20 GB read in 11 minutes); G0 and G1 are verified without
checksums; the final ladder analysis was checksum-verified separately (nrpic-run verify
E-20261115-194633-9e04ed8, 101 files PASS). A first G1 verify ran by mistake from the main
checkout (the `cd` applied to a background subshell only); it wrote an export under
`scratch/orch/tmp/stage-verify/`, left in place.
- LN2 outcome (run E-20261119-154548-7885cdb): CONFIRMED. `ledger.tex` and `parameters.tex`
  byte-identical; `claims.md` identical once the file:line locators are removed (the "42 -> 43"
  of the compare was the line number of SCOPE.md's derived-parameter row, shifted by one line by
  the locator-key edit). The new `claims.*` are committed into `note/tables/`.
- Stage checks: `nrpic-stage verify E-stoch-inf G0 --no-checksums` PASS on 1d25517c (16 checks,
  ledger rerun included); G1 verify PASS on d480131e and rerun after the last commits; reports
  written with the decision paragraphs (G0: complete for review; G1: not met, not complete).

## 2026-11-21T06:35Z  session lead wave 3, batch 2a (Opus)  commits 08ef0ccd..  runs see below

Lead review of the wave-3 packages that finished in batch 1 (`g1verify`, `ladder`); stage
packages G0 and G1; outbox; owner files. State found: main merged (release core-v0.4 on main,
CLAUDE.md names `.work/build_{gpu,cpu}_v04`); no pause flag; no card job of this owner queued
or running. The packages `note`, `a4res`, `usr`, `window` of round 1 were cut at 14:35 PST on
2026-11-20 and are not finished: uncommitted files of `note/scripts/` (six modified, five new),
`a4res/scripts/` (three new), `usr/JOURNAL.md` and `usr/scripts/` (two new) are left alone
(HANDOFF lists them). Two card jobs of those packages ran to completion while their sessions
were gone (Slurm 4740 window scan, E-20261120-222424-0eb754b, 23 min; 4742 usr group 1,
E-20261120-222621-ba66218, 9.4 min); their manifests still say "submitted" and no analysis
exists; left to their packages.

Plan of the lead check (artefacts, not conclusions): (1) rerun the final analysis steps of
both packages unchanged from their registered inputs (`stage/review3/scripts/rerun_all.sh`)
and compare every JSON leaf with the registered output and with the committed copy
(`compare_json.py`); (2) own code on the raw dumps for the new ladder results
(`stage/review3/scripts/lead3_check.py`, built on the lead's wave-2b `stage/G1/scripts/lead_check.py`;
parameters read from the code's logged command line, amplitudes from core's twin
`mode_alpha`, LSODA references); (3) read every figure of both packages.

Predictions, written before either run (refuted where stated):
- LR (reruns): every numeric leaf of the twelve reruns (g1verify v123, v45, v45 addendum, v6,
  v7, v7 on the G1 executable; ladder final2, a6_64, l5 card, l5 scaling, seed-2 judge and
  comparison) equals the registered output bit for bit, apart from path-like strings; every
  committed copy equals its registered output. Refuted by a numeric leaf that differs by more
  than 1e-12 relative (a difference at 1e-15 would be thread-order rounding, recorded, not
  refuting) or by a committed copy that differs from its run's output.
- LW1 (seed 2 of P256, own code): seed read from the log 20261120, nmax2 4096; A2 maximum over
  |n| <= 32 at N_f 2.12e-4 within 10 percent (set by a mode with small |alpha|), over all modes
  4.49e-3 within 10 percent; A3 max |Q(N_f)/Q(N_k+4) - 1| below 1e-5, |drift| below 1.5e-4 per
  e-fold; A1 phi, Pi, K below 4e-12, 1.3e-11, 4e-12; e-folds minus ln a below 1e-8. Refuted if
  A2 differs by more than 10 percent from 2.12e-4 or any verdict changes.
- LW2 (P256 constraint split): odd/even of H at time-matched dumps at most 25.1 within 2
  percent, at t = 4.0; the index-paired last dump has times 0.0038 apart and odd/even 385
  within 5 percent. Refuted if the matched maximum exceeds 50 or the index-paired value is
  below 100 (then the verifier's explanation of the 385 would be wrong).
- LW3 (records): whole-record maxima <|H|/[H]>, <|M|/[M]>: P256 5.10e-11, 3.99e-4; P256s2
  5.11e-11, 4.00e-4, within 1 percent; P256 to t = 4.6: H 5.10e-11 at t = 4.547.
- LW4 (A6 at 64^3): Richardson orders of the perturbations of phi, chi, K in 3.8-4.2 at the
  dumps t >= 0.98, of <chi> 4.03 within 0.1; odd part of H at Courant 0.25 over that at 0.0625:
  0.97 and 1.62 within 5 percent at t = 0.49, 0.98, within 1.5e-3 of 1 at the dumps with
  e-folds >= 2.4. Refuted if an order leaves 3.5-4.5.
- LW5 (L5, card): even part of H at s = 100 over s = 50: 4.0000 within 1e-4 at every dump
  after t = 0; first-order M after one step 5.94e-7 (stencil) and 6.08e-7 (continuum) of
  <[M]> within 5 percent, continuum minus stencil 1.309e-7 within 5 percent (reference 1.293e-7).
  Refuted if the stencil's first-order M is below 1e-8 or the difference is not 1.29e-7 within
  30 percent.
- LW6 (L5 step test, 32^3): first-order M at Courant 0.25 over 0.125, common dumps with
  t <= 0.25: 15.5-19.5. Refuted if at most 4 (a ratio near 2 would be a first-order
  stage-timing defect of the hook).
- LR1 (risk R1 on processors, added 06:39Z before its run; the release core-v0.4 contains
  core/scalar-2 since 2026-11-21): L32p and L32m of `ladder/inputs/proc32.list` rerun with the
  release processor executable `.work/build_cpu_v04/src/athena` (`stage/review3/scripts/r1_run.sh`)
  give dumps equal word for word in all variables, times and cycles to those of
  E-20261115-172636-ce98836 (core/scalar-2 a58e95b) at every common dump, and identical records;
  the release may write one more final dump (its correction "final outputs no longer advance
  last_time"). Refuted by any differing word: then the SR results of G1 depend on the
  executable, and the size of the difference decides whether the 256^3 rung must be rerun.

Outcomes (06:47Z). Runs E-20261121-063551-7957a3d (LR, 4 cores, 11 min) and
E-20261121-063816-64ac0dc (LW1-LW6, 2 cores, 8 min; its first attempt
E-20261121-063758-d643396 FAILED on a recursion in my parameter reader, fixed in 64ac0dc5);
figures `stage/review3/fig/fig_rerun.png`, `fig_lead3.png` looked at; results copied to
`stage/review3/results/`.
- LR CONFIRMED: all 38136 numeric leaves of the twelve reruns equal the registered outputs bit
  for bit, and every committed copy equals its run's output; one string leaf differs (the npz
  path in `P256s2_judge.json`, a path written by the rerun).
- LW1 CONFIRMED: seed 20261120 and nmax2 4096 read from the code's command line; A2 2.121e-4
  over |n| <= 32 (ladder 2.12e-4), 4.494e-3 over all modes; A3 3.80e-6 (ladder 4.4e-6: the
  choice of the dump taken as N_k + 4, as between the ladder and the verifier on seed 1), drift
  1.380e-4 per e-fold, 2.1e-6 from the reference; A1 2.16e-12, 6.31e-12, 2.15e-12; e-folds
  1.28e-9 off.
- LW2 CONFIRMED: odd/even of H at the time-matched dumps of P256/P256m at most 25.15 (t = 4.0);
  the index-paired last dump has t = 4.50377 against 4.50000 and odd/even 384.8. The verifier's
  explanation of the "385" holds; the even part at that pair is 1.6e-13, a quarter of the
  plateau, i.e. the mismatch distorts the even part.
- LW3 CONFIRMED: maxima P256 5.105e-11 / 3.994e-4 (H at t = 4.547), P256s2 5.112e-11 /
  3.999e-4; P256 to t = 4.6: M 3.25e-4.
- LW4 CONFIRMED in the parts that test A6, REFUTED in one sub-claim: <chi> order 4.03 at every
  dump; odd part of H at Courant 0.25 over 0.0625: 0.968, 1.613 at t = 0.49, 0.98 and
  1.00006-1.00047 from N = 2.42 on; orders of the perturbations of phi 3.89-4.03, chi 3.84-4.04
  at t >= 0.98, and of K 3.92-4.02 from t = 1.47 on, but 3.52 at t = 0.98 (and 3.47 at t = 0.49),
  outside my 3.8-4.2. My norm is the maximum over the box, the ladder's the rms (3.82-4.01 for
  K); with the maximum the early K perturbation (before the entry) sits at the edge of A6's
  band. Not a failure of A6 at t >= 0.98 (3.5-4.5) [JUDGEMENT: the max norm picks single cells
  where the time error of K is not yet in its asymptotic regime].
- LW5 CONFIRMED: even factor of H 3.9999936-4.0000001; first-order M after one step 5.943e-7
  (stencil), 6.083e-7 (continuum), continuum minus stencil 1.3091e-7 (reference 1.293e-7).
- LW6 CONFIRMED: A/B of the first-order M 15.55, 15.53, 16.02, 17.25, 19.46 at t = 0.05-0.25;
  later it falls to 0.36 at t = 0.785 (the spatial part at 32^3, as the ladder recorded).
- LR1 CONFIRMED (run E-20261121-064707-77ec326, 2 cores, 436 s per rung; `stage/review3/fig/fig_r1.png`
  looked at): L32p and L32m on the release core-v0.4 processor build equal the core/scalar-2 runs
  of E-20261115-172636-ce98836 word for word: 18 dumps each, 12976128 and 5898240 64-bit words,
  0 differing, times and cycles bit-equal; `sr.sf.hst` and `sr.sf.con.hst` identical in all
  175 rows; no extra final dump. So on processors the SR results of G1 do not depend on which
  of the two executables made them; the card build is not tested (next card job).

Session close (06:58Z). Did: reviewed `g1verify` and `ladder` from their artefacts
(`stage/REVIEW-wave3.md`): all their analyses rerun bit for bit, the new ladder results
recomputed with own code, every figure looked at, every helper outcome compared with its
prediction (git ancestry checked); tested risk R1 on processors (release = branch, word for
word); copied the verifier's report into `stage/G1/`, corrected `stage/G1/STATUS.md` by the
verifier's findings D1-D8, recollected, verified and reported G1; reworded the L5 row of
`codebase/DESIGN_REVIEW.md` (ladder request 7); acknowledged six messages; posted three
(orch: a4-ruling-with-verifier, resume-cut-packages; core: scalar-checks-from-e).
Found: nothing wrong in either package's wave-3 results; the stage package's "385" was wrong
and is corrected; one sub-prediction of mine failed (K's max-norm order 3.52 at t = 0.98).
Evidence: runs E-20261121-063551-7957a3d, -063816-64ac0dc, -064707-77ec326; failed on record
-063758-d643396; figures `stage/review3/fig/fig_rerun.png`, `fig_lead3.png`, `fig_r1.png` and
the packages' 14 figures listed in `stage/G1/EVIDENCE.md` section 9.
Changed my mind about: R1 (the scouting caveat is now a card-build question only); the
verifier's "floor" reservation belongs in the A4' ruling itself, so it went to orch.
Open: A4' ruling (orch); the cut packages note, usr, window, a4res (HANDOFF lists what
remains; their files untouched); P256 on the release card build (0.5 card-hours). No card job
of this owner queued or running. Card-hours this session: 0 (processors only, at most 6 cores).

## 2026-11-21T12:58Z  session lead wave 3, batch 3 (Opus)  commits f9a0eb01..  runs see below

Lead review of the packages that finished since batch 2a: `note` (G1 products) and `usr` (USR
case on the cards, G2 material), both of batch 2b. State found: main merged (f9a0eb01; releases
core-v0.4 and core-v0.5 on main; decision 0021 item 1 adopted A4'); no pause flag; no card job
of this owner queued or running; untracked `a4res/scripts/{a4lib,make_list,twin_predict}.py`
(package `a4res`, still cut, left alone); `window` untouched since 2026-11-20 (card job 4740
finished, manifest E-20261120-222424-0eb754b still "submitted", left to its package). Inbox:
two info messages (release core-v0.5; core's answers on core-v0.4/v0.5).

Git ancestry of the helpers' predictions (checked before the runs below): usr entry 9.3 is in
ba66218 (14:26 PST), before job 4742 started (14:36:46 PST, sacct); entry 10 (the amended H bar
of U-A4) is first committed in 7f764776 (23:50 PST), after that job ran, so its pre-registration
rests on its own time stamp; entries 12.1, 13, 14.1, 14.3 are each in the commit of the run they
predict or earlier (a0cc3eb2, 1f579fe3 before job 4783 at 01:40 PST, 19571c7f, 2f068acc). note
N9-N12 are in the commits of the runs they predict (1849987a, 7fbe919a, 6112292a).

Predictions of the lead check, written before any run of this session (refuted where stated):
- LR4 (reruns from the registered outputs, unchanged scripts): (a) usr group 1
  (`analyse_cards.py --group g1` on E-20261120-222621-ba66218), `floor_split.py` on the rerun's
  summary and `quick_records.py`; (b) the U256/U256m pair analysis (`--group u256` on both runs);
  (c) `lockstep_shells.py` as in E-20261121-103157-96fee1d; (d) the note's `run_all.py`. Every
  numeric leaf of (a)-(c) equals the registered output to 1e-12 relative (threaded FFTs at 3
  workers may reorder sums: a difference below 1e-12 is recorded, not refuting) and every
  committed copy in `usr/results/runs/` equals its run's output; (d) every PNG of
  `note/figures/` equals the rerun's in pixels (bytes may differ only by metadata) and
  `note/tables/ledger_g1.{md,tex}`, `claims.md` are byte-identical. Also the single-run
  section U256 of the pair summary equals the summary of E-20261121-084815-63462b8 in every
  numeric leaf they share, to 1e-12. Refuted by any larger difference.
- LU1 (own code on the raw dumps, the verifier's reader `g1verify/scripts/nrsf.py`, numpy FFT;
  not the helper's card_lib): at N_f of U256 and U256m, R_phi = (H_b/Pi_b)(phi - <phi>) with
  H_b = -<K>/(3<alpha>), Pi_b = <Pi>, which the helper finds to carry 1.00 of R^NR (chi part
  6.1e-6, anisotropic 1.6e-6). Predicted: rms 0.89452 within 1e-4 in both runs; skewness
  +0.00237 (U256) and +0.00061 (U256m) within 1e-4; max |R| 4.568 and 4.557 within 0.01; the
  even/odd ratio of the mode coefficients, sqrt(sum|even|^2 / sum|odd|^2), 2.53e-4 over
  0 < |n|^2 <= 1024 and 2.88e-4 over 0 < |n|^2 <= 4096, each within 10 percent. Refuted if
  outside (the chi and anisotropic parts are too small to move any of these by more).
- LU2 (own code, group-1 halving at 128^3, dumps 4, 6, 8 at cN 2.06, 3.06, 4.05): raw halving
  factors of the odd and even parts of H and M (rms over cells; even parts with box means
  removed; U128p/m against U128hp/hm), and the floor-corrected even factor with
  f^2 = (4 o_h^2 - o_1^2)/3, equal to `floor_split` E-20261121-080134-a0cc3eb at those dumps
  within 1e-6 relative (same definitions, independent code): raw even M 3.9918, 3.9108, 3.8323;
  raw odd M 1.0008, 1.8007, 1.3580; corrected even M 4.0000, 3.9999, 4.0007; raw even H 3.9802,
  3.9648, 3.9625. Refuted by a difference above 1e-3 (a different definition would show as
  a percent-level difference).
- LU3 (records, own parse of `usr.sf.con.hst`): the whole-record maxima of <|M|/[M]> 2.519e-2
  (U256) and the value at N_f 2.127e-3; U256m equal to U256 in these two to 4 digits
  (entry 15: "records equal to 4 digits"); card time of jobs 4742, 4774, 4783 from sacct
  0.157, 0.617, 0.612 card-hours (one card each). Refuted by a difference in the 4th digit.

Outcomes (13:31Z). Runs E-20261121-130021-0140e4e (LR4, 3 cores, 30 min) and
E-20261121-130236-e39e143 (LU1-LU3, 2 cores, 21 s); figures `stage/review3/fig/fig_rerun4.png`,
`fig_lead4.png` looked at; results copied to `stage/review3/results/batch3/`.
- LR4 CONFIRMED in (a), (b), (d): group 1 0/4220 numeric leaves differ, floor split 0/241, quick
  records 0/294, pair 0/12289, single-run U256 section = summary of -084815-63462b8 in all 4279
  shared leaves; note: 12 PNGs byte-identical, six tables byte-identical; every committed copy
  equals its run. REFUTED in (c): 13 of 56 lockstep leaves differ, all from the 256^3 code-time
  reference (lowest shell 9.3072e-8 against 9.2992e-8, 8.6e-4 relative; L1 ratios 6.5e-7; L3
  8e-9). Cause read, not tested: my script exported OPENBLAS_NUM_THREADS=3, the registered run
  left it unset [JUDGEMENT]. No verdict changes.
- LU1 CONFIRMED: rms 0.8945204/0.8945199, skewness 0.0023740/0.0006108, max abs R 4.5678/4.5567,
  even/odd 2.533496e-4 (68532 modes) and 2.8766e-4 (548958 modes), all as the helper's to six or
  more digits, from the phi part alone.
- LU2 CONFIRMED against the file (18 numbers, relative difference 0); my written prediction
  FAILED for dump 4: I had copied the values of the dump at cN 1.55 (index 3), not 2.06.
- LU3 CONFIRMED for the maxima (2.5193e-2, 2.5195e-2) and the card time (0.157, 0.617, 0.612);
  FAILED for "equal to 4 digits" at N_f: 2.1269e-3 against 2.1283e-3 (7e-4 relative): the
  record of abs M is not even in s once the even part of M is as large as the odd part.
- Also found while the runs ran: a helper session of this batch works on `a4res` in this
  worktree (commits c4061303-aed608d2; card job 4798, run E-20261121-131000-b23055b, pending);
  the lead leaves it alone. `nrpic-stage verify G1 --no-checksums` (on 67413b28): every check
  passes except `clean` (my uncommitted review) and `runs` (my rerun then still running, and
  a4res's submitted job).

Session close (13:45Z). Did: reviewed `note` and `usr` from their artefacts
(`stage/REVIEW-wave3.md` Part B: helper predictions with git ancestry, reruns, own code, every
figure, the ledger row by row); closed the manifest of window's finished job 4740; judged all 18
G1 items PASS (`stage/G1/CHECKLIST.md`, `STATUS.md`, `OPEN.md`, `EVIDENCE.md` 10-11); applied the
note's requests (NOTATION, WRITING_GUIDE, ladder README A1 row); acknowledged two messages;
posted four (core: lockstep-record-substep; orch: usr-acceptance-after-data,
schedule-window-r1-a4res, g1-package-complete). Found: nothing wrong in the results of either
package; usr entry 10 cannot be dated before its job by git (rescues no verdict); "records equal
to 4 digits" holds for maxima only; note journal heading time out of order (cosmetic). Changed
my mind about: G1 completeness (C6 by decision 0021, C8-C15 delivered, C16's ledger part by the
B4 cross-check). Open: the G1 gate review (orch); U-A2'/U-A4' ruling; window analysis; a4res job
4798; P256 on the release card build. Card-hours this session: 0.

## 2026-11-21T20:19Z  session lead wave 3, batch 5 (Opus)  commits 3ac9fcb7..  runs see below

Aim (decision 0025 items 4-5): leave the cards loaded with G2 production runs, unattended, after
fixing the USR G2 criteria (decision 0023 item 1); review the finished packages `window` and
`a4res` from their artefacts.

Done before any run (commits 43dcc9cc, then the time correction): SCOPE section 4c (floor
f^2 = max(0, (4 o_{s/2}^2 - o_s^2)/3), clause on the maxima, U-A2', U-A4'(a)-(d), U-R, U-S,
U-W); package `g2prod` with deck, queue, sequencer, restart check and its predictions
(`g2prod/JOURNAL.md` entry 1: R0, T, P256v6, U256a, U320, U256b, U256h, U256nc).

Submitted (12:29 PST): timing E-20261121-202929-43dcc9c (Slurm 4827), P256v6
E-20261121-202935-31520bc (Slurm 4828); R0 on processors E-20261121-202941-da16544; sequencer
pid 2542133 (scratch/E-stoch-inf/g2prod_seq/). Review reruns: window E-20261121-203008-f104a3e,
a4res E-20261121-203016-7209255.

Predictions of the lead's checks (written before they ran):
- LC1 (a4res rerun): every numeric leaf of a4res.json and post.json equal (the analysis is
  deterministic on processors); refuted by any difference beyond 1e-12 relative.
- LC2 (window rerun): summary_usr.json, summary_sr.json, posthoc_usr.json equal up to BLAS
  thread-count rounding (<= 1e-9 relative) - the batch-3 rerun of usr found 8.6e-4 on lockstep
  leaves from the BLAS thread count, so a difference up to 1e-3 on fitted leaves would not
  refute a verdict; refuted if any verdict (W1-W8) changes.
- LC3 (own reader, stage/review5/scripts/lead5_check.py on the raw dumps of
  E-20261121-131000-b23055b, not a4res's code): largest odd/even of H over the dumps with t > 0:
  N64q16 0.455, N64q25 0.9997, N64q64 15.5 within 2 percent (a4res README); refuted beyond 2
  percent; a different box-mean or norm convention would show as a common factor.

Outcomes of the checks:
- R0 HELD (E-20261121-202941-da16544): restart of the production deck is byte-exact at 32^3 on
  the release processor build (details g2prod/JOURNAL.md).
- LC1: no difference in 5502 numeric leaves of a4res (rerun E-20261121-203016-7209255). This
  "prediction" was written after the rerun had finished and been compared (12:34 vs commit at
  12:35 PST); it is a post-hoc statement and is recorded as such in stage/REVIEW-wave3.md C.
- LC2 HELD, better than predicted: window rerun E-20261121-203008-f104a3e identical in all 1079
  numeric leaves and both tables (no BLAS-order difference).
- LC3 HELD (E-20261121-203540-a9b5d10, own reader): 0.4548, 0.9997, 15.45 against 0.455,
  0.9997, 15.5; figure looked at.
- Review written: stage/REVIEW-wave3.md Part C. Nothing WRONG in either package; Q6 (a4res) and
  W6, W2 per-mode clause, W3b premise, P-b (window) stay on record as failed predictions.

Session close (about 12:50 PST). Did: SCOPE 4c (G2 criteria before production), package g2prod
(deck, predictions, sequencer, restart check), submitted T and P256v6 on the release card build,
sequencer running for nine USR chains; reviewed a4res and window; G2 checklist collected; one
message acknowledged (release core-v0.6), two posted (core: a4res claims; orch: criteria, cards,
allotment, A4 information). Card-hours used this session: 0 (both jobs still queued at close).
Changed my mind about: the odd halving of U-A4' - with two amplitudes it is 2 by construction
of the floor, so SCOPE 4c judges only the even halving. Open: everything that the g2prod runs
will decide; the allotment for the last three labels; the timing before U320ap.

## 2026-11-22 17:45-19:15 PST, lead of batch 10a (analysis round after the card runs)

Read: CLAUDE.md, CHARTER to Owners, HANDOFF, g2prod JOURNAL entry 1, SCOPE 4c, decisions
0026-0028, brief 674-686 and 785-802. Sequencer: had ended by itself at 13:49 PST, all eleven
g2prod runs completed and closed (7.51 card-hours). Decision 0028 (merged into this branch by a
repro session) put three repro sessions into this worktree; I committed path-limited only.

Predictions: those of g2prod entry 1 (written 2026-11-21 before the runs); the reading of each
written as g2prod entry 2.0 before any analysis ran (17:55 PST); entry 3 (s = +-1/4 pair) before
its queueing.

Outcomes (details g2prod/JOURNAL.md entry 2): T held on time, memory band at 384^3 missed low;
P256v6 identical to the tested-branch run (G1 reservation 2 answered); seed A identical per mode
to the scouting pair; seed B U-S held; U320 predicted band of the factor (2.4-4.5) FAILED at 2.10
while U-R (bar 2.0-4.5) passes; U-A2' at s = 1/2 +14 percent (prediction "unchanged" FAILED);
U-A4'(a) FAILED at one dump of M (3.925 at cN 6.52) - prediction refuted, criterion failed as
written; control held (1.19e5). Finding: the flat odd-part error is a common factor of all
modes scaling as s^2 (the halving pair was the run in which this could have failed).

My own analysis defects: one-dump crash (E-20261123-015650-493cff5, failed) and seed B read
with seed A's realisation (E-20261123-014905-2bf3570, per-mode numbers invalid); both fixed in
analyse_g2.py and rerun.

Did: analyses and judge (6 registered processor runs, at most 6 cores); figures looked at; stage
G2 checklist judged, EVIDENCE/OPEN rewritten, verify and report; REVIEW-wave3 Part D; outbox to
orch (ruling on U-A4'(a), C2 gauge leg); queued U256qp/qm in the restarted sequencer (pid
3538144, waits for repro's two card jobs). Card-hours used this session: 0.
Changed my mind about: the odd part of a mirrored pair is not first order alone in USR at
256^3: a third-order common factor (4e-5) is visible, so per-mode resolution tests at 1e-4 need
smaller s or the s^2 part removed.

## 2026-11-24 15:27-16:15 PST, lead of batch 13 (after the reproduction)

Read: CLAUDE.md, CHARTER to Owners, HANDOFF (of batch 10a), coord/digests/reproduction-state.md,
decision 0030 item 2 (Track E ruling), repro/note README (verdicts, requests), repro/verify README
(requests), repro/figs RESULTS/HANDOFF/CARD_COSTS, repro/continue HANDOFF/journal, g2prod entry 3.

Did: pushed the reproduction's commits; closed what its packages left to the lead (commit 51b52c00):
conts.json with the fourth RSF256 continuation (K2 held; read from join_check.json of
E-20261124-225720-444aecc), SETUP_AUDIT item 4 corrected to N* + 8.10 (ln a 8.0989 at t = 8.5 in the
joined record, column 21; the audit's 8.04 was wrong), CARD_PLAN.md actual costs (reproduction 8.99
card-hours from the manifests), RESULTS.md S14 (99.5th: QUANT index 7). Review: stage/REVIEW-wave3.md
Part E. Package `floor` (new): predictions F1-F5 written and committed (bb70b5fe) before the two runs
were queued as q0037 FL128h and q0038 FL256h (priority 2, release card build, noise_mode_scale = 0.5).
The quarter pair U256qp/qm had run (2026-11-23) but was never read: analysis E-20261124-233223-51b52c0
started on 3 cores (predictions: g2prod entry 3, written 2026-11-22 before submission). Stage G2:
collect, checklist (C2 PASS by ruling 0030; C12 PASS; C3/C7 FAIL on record), OPEN.md rewritten with
the lacks and the review question, verify, report. Outbox: orch (G2 after the reproduction), core
(figstyle). Inbox: five messages acknowledged (core level-2 branch, review, executables; orch queue).

Predictions written this session: floor F1-F5 (before submission). No outcome yet.
Card-hours used this session: 0 (1.25 asked at the ceilings of q0037/q0038).
Changed my mind about: the HANDOFF of batch 10a said the quarter pair waited in the sequencer; it had
run and the sequencer had closed it on 2026-11-23 20:06 PST, unread for 20 hours.
Addendum 16:07 PST: `nrpic-stage verify` started 15:37 was stopped by its PID at 16:05 (checksum pass
at run 67 of 270, competing for the disk with the quarter-pair analysis, which had then finished its
reference pass, 21 dumps in 1881 s, and was reading the runs). `nrpic-stage report` was run on the
verify of 2026-11-23. The analysis E-20261124-233223-51b52c0 was still running at the close; its
judge `g2prod/scripts/judge_q.py` is committed (449b8b2c), not yet run.

## 2026-11-24 19:32-20:20 PST, lead of batch 15 (Opus): G2 records after the fresh verifier, note sections, stage

Predictions first, outcomes after, all on record in the package journals:
- g2prod entry 4.0 (expectation before judge_q from the verifier's numbers) -> 4.1: held. Q-a
  REFUTED (4.1275, prediction 3.98 +- 0.015), Q-b holds by its rule (-2.0725e-6; 0.03e-6 outside the
  stated band -2.5e-6 +- 0.4e-6), Q-c holds. Runs E-20261125-033357-a608cda, -033450-4c4a31c (figure
  fix: the common-mode panel was useless in the first version). 4.2: the three-amplitude reading
  recorded beside the failure, labelled after the data (ruling 0036 item 2).
- repro/note entries 19-26: predictions for R11-R16 written before each run; all held. Failed
  checks found and fixed by rerun: a halving legend and the ladder and ledger caption wrote the noise
  amplitude as s (the note's window steepness) -> lambda; an overfull equation; a caption over five
  lines; the appendix landing among the ledger floats (\clearpage); the compiled PDF at 5.56 MB above
  the 5 MB hook (one commit carried a 5.14 MB copy before I noticed; schematics now vector PDF, 5.05
  MB). The pre-commit hook refused one commit with the 5.3 MB PDF; recommitted without it.
- Stage G2: collect (20 items kept), CHECKLIST complete, EVIDENCE rows, OPEN, REVIEW-wave3 Part F;
  verify with --no-checksums (full checksum pass 1-2 h); report.
- Inbox: four infos acknowledged (core SIGTERM restart, orch core-v0.7 release and checksum, kb
  claims superseded). Outbox: two posts to orch.
Card-hours this session: 0. Floor runs q0037/q0038 still waiting in the shared queue (not read).
