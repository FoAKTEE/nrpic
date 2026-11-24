# VERIFIER: fresh verification of the reproduction of arXiv:2401.08530 (P0) and arXiv:2512.14649 (P1)

Verifier: package `repro/verify` of Track E, 2026-11-24 (Opus). Predictions:
`JOURNAL.md` entry 1 (committed 58f241a5 before any computation); outcomes: entries 2 and 3.

## 0. Method

- Read: P0:782-881, P0:1034-1076 and the lines quoted below; P1:395-543, P1:697-791; the
  papers' own figures (P0 plot2v2, plot2bv2, plot4v2; P1 Figs. 2, 3, 4 rendered into scratch,
  never committed); `coord/INTERFACES/scalar_field_2.md` (dump layout, mode file, record
  columns). From the reproduction I took only the claims (ledger column "quantity"/"value",
  first columns of ERRATA.md) and the locations of the raw outputs. I read no README verdict,
  RESULTS.md, note text or journal of another package.
- Own code (`scripts/`): `onepatch.py`, `onepatch_seeds.py` (P0 one patch), `lattice.py`
  (NRSFDMP2 reader and R^NR extraction, self-test on analytic multi-block fields passes to
  1e-15), `compare.py` (my Klein-Gordon/Friedmann background and Mukhanov-Sasaki integration in
  code units from the mode file's data at t = 0, the window of P1:504, amplitudes alpha_n from
  core's twin `python/nrpic/rng.py` with the code's keys), `records.py`, `entrywin.py`,
  `background.py` (records, rungs, sign flip, backreaction), `errata.py` (sympy).
- R^NR = Phi + (H/Pi_b) dphi (P0:273, P1:524), Phi from the SVT metric of P0:178
  (gamma = a^2[(1 - 2 Phi) delta + 2 E_,ij]): Phi = (1/2) dln chi + (1/4) khat khat : d gt.
  The data decide sign and E term (section 2, row "R^NR per mode").
- Runs (all registered, processors only, 0 card-hours): E-20261124-181218-1e5f85e,
  E-20261124-181431-d45be89 (P0); E-20261124-182136-518eee2, E-20261124-182151-93742a3 (lattice
  reader, SR 18 dumps, USR 24 of 41 dumps); E-20261124-182829-775329c,
  E-20261124-183037-f2a8ebf (comparison); E-20261124-183222-02ff27c (sign flip, rungs,
  backreaction); E-20261124-183347-e15a95f (background, one-point); E-20261124-183618-c71832c
  (entry windows); E-20261124-182402-a2f56bb (errata); E-20261124-183303-303e6c3 (rerun of the
  note's `run_all.py`). Two lattice runs stopped before use (wrong sign of Phi):
  E-20261124-181756-14fc721, E-20261124-181817-059b3d5.

Verdicts: CONFIRMED (my independent value agrees within the stated or sampling precision),
NOT CONFIRMED (my value differs beyond that, or my method cannot reach the digits; the reason is
given), WRONG (my evidence contradicts the claim). No claim was found WRONG.

## 1. arXiv:2401.08530 (one patch)

| Claim | My evidence | Verdict |
|---|---|---|
| The converged background stops on the plateau | Analytic: on V = V0, pi' = -(3 - pi^2/2) pi gives Delta phi = (1/sqrt 6) ln[(sqrt 6 + 2.0001)/(sqrt 6 - 2.0001)] = 0.935981, stop at 9.0640187 > phi_c = 9.056 (P0:847); DOP853 rtol 1e-12: 9.0640187; RK4 0.01: 9.064019; Heun 0.01: 9.06393; Euler 0.001: 9.06321; Euler 0.005: 9.05997 | CONFIRMED (firm: closed form) |
| Only forward Euler at 0.01 e-folds reaches the slope, at N = 3.0435 (P0:842 "~3.04") | Euler 0.01 crosses at 3.04353; none of the five other integrations crosses. That the authors used this scheme is an inference from P0:842 (footnote: tuning depends on the 0.01 step), not proven | CONFIRMED (numbers); inference [JUDGEMENT] |
| Figures match the Ito reading of the printed SDE, not the Stratonovich one | 6 seeds x 50 000 paths, step 0.01, Euler-0.01 background. Widths std(alpha - 1) at N_b = 4, 5, 6: Ito 0.1168, 0.1321, 0.1210 (seed sd <= 0.0008); my read-off of P0 Fig. 3 (Gaussian peak heights) 0.117, 0.133, 0.122. std(N - N_b): Ito 0.0425, 0.1494, 0.1851 vs 0.042, 0.150, 0.188. Stratonovich: alpha 0.126, (0.142 as 68 % half-width at 5; std dominated by exploding paths), 0.1450 (+19 % at 6); N 0.0461, 0.1704, 0.2169 (+10, +14, +15 % above the read-off). Skewness of alpha (median N_b 4.5-6): Ito 1.116 +- 0.012, Stratonovich 1.562 +- 0.026; P0 Fig. 2 about 1.1. Mean N - N_b at 6: Ito 0.003, Stratonovich 0.084 (P0 Fig. 1 red curve about 0.015 +- 0.019 over 100 paths). Figures `fig_p0_moments_clipped.png` | CONFIRMED. Firmness: the Ito widths sit within 1-2 % of every read-off point at 4, 5, 6 for both variables; Stratonovich misses by 15-19 % at N_b = 6, three to four times my read-off uncertainty (about 5 %) |
| Ito term: alpha^5 <S^2>, not the printed alpha^3 (P0:817, P0:825) | Derivation: alpha = f(Z) = phidot_b/Z, f'' = 2 alpha^3/phidot_b^2, (dZ)^2 = alpha^2 S_Pi^2 dt (noise alpha S_Pi in the Z equation, P0:812), so (1/2) f''(dZ)^2 = alpha^5 S_Pi^2/phidot_b^2. Monte Carlo (4e6 paths, control variate): drift 0.32039 +- 0.00023 at alpha0 = 2 (alpha^5: 0.32, alpha^3: 0.08), 0.075987 +- 0.000054 at 1.5 (0.075938 vs 0.03375) | CONFIRMED (firm) |
| Appendix-D amplitude: USR over printed = sigma^2/3; SR close to 1 | Exact USR Mukhanov-Sasaki: 8.333e-4, 3.3333e-3, 1.3333e-2, 8.3332e-2 at sigma 0.05, 0.1, 0.2, 0.5 (= sigma^2/3; analytic: R_k ~ a^3 makes the bracket -A sigma^2 e^(-ik tau)). SR (quadratic): 1.063 at sigma = 0.1 with eps1 = 0.0124, 1.123 with eps1 = 0.0244 (the drift of H/sqrt eps1 since Hubble crossing) | USR CONFIRMED (firm); the ledger's SR 1.027 NOT CONFIRMED: it depends on the slow-roll background, which I did not take from the package |

## 2. arXiv:2512.14649 (lattice, 256^3, raw dumps, own reader)

| Claim | My evidence (at the final dump unless said) | Verdict |
|---|---|---|
| R^NR per mode equals the linear solution of the realisation | SR N_f = 8.099: median |R^NR_n / (L^-3/2 W R_q alpha_n) - 1| 1.7e-7 (|n| <= 8), 2.8e-5 (|n| <= 32), 9.1e-4 (all 548 958 modes), max 4.5e-3. USR N_f = 10.000: 2.7e-4, 2.6e-4, 1.1e-3 (medians), single modes up to 0.25. Without the E term SR median 5.3e-3; with the other sign of Phi 0.11: the data fix the definition. Figures `fig_lattice_sr.png`, `fig_lattice_usr.png` | CONFIRMED (SR firm; USR medians firm, single USR modes deviate at the 1e-1 level from nonlinear coupling) |
| Shell (bin) power against linear | Largest |P_NR/P_lin - 1| over the 3414 shells (exact |n|^2): SR 6.7e-3 (ledger 5.2e-3), |n| <= 32: 1.6e-4 (ledger 1.0e-4); USR 6.7e-3 (5.0e-3), 5.9e-4 (3.6e-4). Within 3/sqrt(M) of the ensemble MS power: 0.9965 both (ledger 0.9965 both). Power beyond k_max over the MS power at k_max: SR 1.1e-14 (8.7e-14), USR 1.2e-7 (1.3e-7) | Agreement CONFIRMED; the maxima NOT CONFIRMED to the digits (my linear reference is my own MS solution; the code's lockstep record differs from it by up to 2.5e-3 at the top shell) |
| Freezing of R | SR: shell power within 1e-4 of its final value for all bands from N = 7.2 (top band 0.4 % at N = 6.27, relaxing as about e^(-2.5 N), as the linear solution does); USR: enhancement through N = 4-7.5, then all bands within 1e-4 between the last two dumps (N = 9.75, 10.0). `fig_freeze_*.png` | CONFIRMED |
| Constraint ratios and magnitudes | My [H] = |R3| + (2/3)K^2 + |At At| + |16 pi E| equals the dumped Hmag to 3.3e-16; record columns equal my dump statistics to 5e-15 at all 18 (SR) and 24 (USR) dumps. Largest <|H|/[H]>: 5.1e-11 (SR, N = 4.43), 2.3e-11 (USR, N = 2.29), box mean removed 2.9e-12; <|M|/[M]>: 4.0e-4 (SR), 2.519e-2 (USR; P1:541 "around 1e-2"). P1:539 "~1e-10" | CONFIRMED (records and magnitudes); the H field itself is the code's: I did not recompute it from the metric with a stencil of my own |
| Sign-flip control | <|H|/[H]> flip/proper: SR median 6.0e4, max 7.4e4 (ledger 7.3e4; overlap only N < 0.39), USR median 1.0e4 (ledger 8.0e3), max 1.7e5; flipped <|M|/[M]> 0.16 (SR) and 0.50 (USR), as the ledger. Absolute flipped H/[H] about 1e-7 against P1:541's "~1e-5" | First-order violation CONFIRMED; USR median NOT CONFIRMED (window); the paper's printed 1e-5 is NOT reproduced (factor 100) |
| Backreaction levels | Level 2 against 0, USR: rms 1.04e-4 (ledger 1.0e-4), largest shell 9.2e-4 (7.0e-4), 52 % positive (0.52); SR at N = 7.19: largest 1.4e-4 (7.9e-5), rms |n| <= 32 1.7e-5 (1.5e-5). Level 1 against 0: 6.6e-7 SR, 7.0e-7 USR (ledger the same). Level 0 shells against mesh: 1.33e-2 (1.3e-2). All below P1:520's 1 per mille | CONFIRMED except the two level-2 maxima (binning: mine per exact |n|^2) |
| Two numbers of the convergence figures | USR H entry maximum, order 64 -> 128: 4.06 in four windows (ledger 4.05); SR H order 32 -> 64: 4.17 with the window [0, ln 8 + 0.5] (ledger 4.15), 5.53 if N < 0.5 is excluded. Spectra 32/64/128: 8.0e-3, 1.9e-4, 4.6e-6 (ledger 3.2e-3, 6.2e-5, 1.0e-6), factors 43 and 41 | USR order CONFIRMED (firm); SR order CONFIRMED only for one window; spectral values NOT CONFIRMED (convergence itself confirmed) |
| Slow roll at N_f | USR eps1 1.008e-12, eps2 (P1 convention -dln eps1/dN) -0.02762 (record finite difference -0.0275; P1:534 "-2.8e-2"); SR eps1 0.013532, eps2 -0.02694; eps2 = 3 crossed at N = 2.523, 6.550 | CONFIRMED |
| One-point amplitudes against P1 Figs. 2 and 4 | Ours: SR rms R 2.278e-5, dphi/phi_b 2.9e-7; USR rms 0.8945, max |R| 4.568. My read-off of P1: SR 68 % band of R about +-0.8e-4, of dphi/phi_b +-1.0e-6 (factor about 3.5); USR 68 % +-3.5, full band +-18 (factor about 4). P1 Fig. 3 puts the final SR spectrum at about 1e-10, the level of ours and of Delta = H^2/(8 pi^2 eps1) | Ledger row 33 (USR factor 2.3 to 4) CONFIRMED at its upper end; row 32 (SR) carries no number ("factor of about", the text is cut), my value is about 3.5; the cause is open [JUDGEMENT: P1's Fig. 2 seems inconsistent with its own Fig. 3 by that factor] |

## 3. Misprints (6 of 17), rederived with sympy (`errata.py`, run E-20261124-182402-a2f56bb)

| Item | Printed | My derivation | Verdict |
|---|---|---|---|
| E7, P0:911 | Hddot = 2 eps1 (1 - eps2/2) H^3 | eps1 (2 eps1 + eps2) H^3 (eps_{i+1} = -H^-1 d ln eps_i), checked on a test H(t) to 1e-12 | CONFIRMED |
| E8, P1:267 | V' = (-3 + eps1 + eps2/2) H phidot^-1 | (-3 + eps1 + eps2/2) H phidot, residual zero with Hdot = -eps1 H^2 | CONFIRMED |
| E10, P0:530, P1:108 | H^2 = V/(1 - pi^2/(6M^2)) | V/(3M^2(1 - pi^2/(6M^2))) (printed/true = 3 M^2) | CONFIRMED |
| E6, P0:371 | dN = Phi + k^2 E/3 | -(Phi + k^2 E/3) from (1/6) dln det gamma with P0:178 | CONFIRMED |
| E3, P0:138 | -(1/3) alpha^|k_|k delta_ij | gamma_ij: with delta_ij the trace is (1 - a^-2) D^2 alpha | CONFIRMED |
| E1, P0:249 | prefactor -2 | -2/3 from the full momentum constraint linearised (residual zero; with -2 nonzero). The equation "= 0" is unaffected; only its use as a residual is | CONFIRMED |

## 4. The note's ledger (109 rows)

Rerun: `run_all.py` of the note, unchanged (run E-20261124-183303-303e6c3), reproduces all 109
values of the committed `ledger.csv` exactly (only the run id in the source text differs).
From raw outputs with my own code, beyond sections 1-2 (my value in brackets):

- CONFIRMED: rows 1 (9.8e-13), 2 (6.4e-12), 4 (8.0989), 5 (1.12e-9), 6 (4.63e-5), 8 (2.523),
  9 (6.550), 10 (1.008e-12), 11 (-0.02762), 16 and 20 (0.9965), 21 (1.2e-7), 23 (2.294e-5 as
  the 68.27 % band; x 0.9945 for a central 68 % band = 2.281e-5), 24 (2.2780e-5), 25 (3.89, dump
  cadence 0.5), 27 (0.8947, 0.8898 as a 68 % band), 28 (0.8945), 29 (4.568), 31 and 34
  (my read-off), 41 (4.06), 43 (2.519e-2), 47 (7.4e4 max), 48 (0.16), 50 (0.50), 67 (1.04e-4),
  69 (0.52), 73 (6.6e-7), 74 (7.0e-7), 75 (1.33e-2), 79-82, 87-93, 95-99, 102-105, 107, 108.
- NOT CONFIRMED to the printed digits: 3 and 7 (eps2 differences; my finite differences of
  the records reach only 4e-9 and 5e-4), 14, 15, 18, 19, 17 (section 2), 26 (3.28 vs 3.44,
  dump cadence), 36 to 40 (entry maxima: no window of four reproduces 1.8e-12, 2.0e-12, 1.2e-5,
  2.2e-12, 3.2e-10; mine 2.6e-12/1.0e-12, 2.6e-12/0.83e-12, 1.46e-5/6.3e-6, 2.9e-12/0.97e-12,
  3.75e-10), 49 (1.0e4), 61-63, 65 (M order 4.64 or 5.54 vs 3.25), 68 (9.2e-4), 70 (1.4e-4),
  71 (1.75e-5), 83 (paths half lost at 5.36-5.38 vs 4.80), 94 (Ito skewness 1.116 +- 0.012 vs
  1.04, six standard deviations), 101 (alpha^3 -> 1 skewness -0.74, one seed, vs -0.96), 109.
- Window-dependent: 64 (SR H order 32 -> 64: 4.17 including N = 0, 5.53 without).
- Quotes of the papers, checked at the given lines: 12, 13, 22, 35, 44, 53, 76 (P1:520-541),
  84-86, 106 (P0:817-842): CONFIRMED. Row 35 (P1:534, "~10" for the furthest outliers) differs
  from P1's own Fig. 4 (full band about +-18) [JUDGEMENT].
- Ledger defects: rows 32, 77 and 78 carry cut text and no complete value ("factor of about",
  "falls by 16 per halving of the", "the level-2 curve to 1 per cent").
- Rerun only (not from raw outputs): 30, 42 (my subset of dumps gives 1.98e-11 against 2.4e-11;
  the record peak falls on a dump I did not read), 45, 46, 54-60, 77, 78, 100.
- Pending in the reproduction (no output yet): 51, 52, 66, 72.

## 5. What I could not check

- The constraint fields H, M_i themselves: I verified that records, dumps and magnitudes agree
  and that [H] follows P1:740, not that the dumped H is the Hamiltonian constraint of the dumped
  metric (would need the code's stencil to reach 1e-12).
- Extrinsic-curvature spectra (rows 54-60), dPi/Pi widths (row 30), USR dumps with odd index
  below 35, the pending continuations, P1 Fig. 8a read-off.
- The authors' one-patch implementation (Mathematica "Stratonovich evolver", P0:836) and their
  SR background for the appendix-D ratio.

## 6. The three weakest points of the reproduction

1. The one-point amplitudes differ from P1's Figs. 2 and 4 by a factor 3.5-4, and the flipped
   H/[H] (1e-7) is 100 times below P1:541's "~1e-5"; the spectrum level agrees with P1 Fig. 3.
   The reproduction documents the factor but does not resolve it; until it is resolved, "the
   one-point figures are reproduced" cannot be claimed.
2. About fifteen ledger numbers rest on definitions the ledger does not state (entry windows,
   bins, which "linear" reference, which percentile band); an independent reader of the same raw
   outputs obtains values that differ by 20 % to a factor 4 (rows 14-15, 36-40, 49, 61-65, 68,
   70) while agreeing on every qualitative statement. The digits printed are more precise than
   their definitions.
3. Paper I: the match rests on reproducing an integration artefact (forward Euler at 0.01) and on
   read-offs of KDE figures; the widths are robust, but the Ito skewness of the ledger (1.04)
   and the alpha^3 -> 1 skewness (-0.96) are not reproduced by an independent implementation of
   the same printed equations (1.116 +- 0.012, -0.74), so implementation details of the
   reproduction's integrator matter at the 10 % level for third moments. The lattice side lacks
   the five continued runs (SR sign flip covers only 0.39 e-folds; SR level 2 stops at N = 7.19;
   no 256^3 rungs).

## 7. After the verdicts (added once sections 1-6 were committed, 02d8175a)

Only then I read, in the note's scripts, the definitions behind the numbers I could not
confirm (`fig_conv.py`: entry window 0.05 < N <= ln 8; `fig_spectra.py`: shells with more than
10 modes, "linear" = the dump pass's injected power). Applied with MY readers (run
E-20261124-184028-36a685d; a first attempt E-20261124-184003-71eb0a8 failed on an empty shell
selection in my script):

- Entry maxima: SR 64^3 1.78e-12, 128^3 2.00e-12, M 128^3 1.23e-5, orders H 4.15 and M 3.25
  (32 -> 64); USR 128^3 box mean removed 2.25e-12, with the box mean 3.25e-10, order 4.05: rows
  36-41, 64, 65 are reproduced by my reader with their window. These rows move to CONFIRMED,
  with the window stated.
- Spectra, shells with more than 10 modes: SR 4.5e-3 (ledger 5.2e-3), |n| <= 32 1.1e-4
  (1.0e-4); USR 4.4e-3 (5.0e-3), 3.5e-4 (3.6e-4); rungs 3.4e-3, 7.9e-5, 2.3e-6 (3.2e-3, 6.2e-5,
  1.0e-6). Rows 15 and 19 CONFIRMED; rows 14, 18, 61-63 agree within a factor 2.3, the rest being
  the difference between my continuous-time Mukhanov-Sasaki reference and the code's own record.
- Weakest point 2 therefore narrows: the definitions exist in the scripts, but the ledger and
  (as far as the ledger shows) the note do not state them; rows 49, 68, 70, 71, 83, 94, 101, 109
  remain unexplained by me.

## 8. Update pass: the five continued runs (2026-11-24 14:05-14:35 PST; sections 1-7 unchanged)

Read for this pass, as a fresh reader: the claims (not the verdicts) of `repro/figs/RESULTS.md`
for Figs. 7, 8, 9 and the sign flip, the ledger rows without a verifier check (42, 48-52, 56,
68-75, 81-83), the run map `repro/continue/scripts/{runs,conts}.json` and queue entry q0034; the
section headings of RESULTS.md carry verdict words, which I saw. Predictions: `JOURNAL.md` entry 5
(committed 6ced7199 before any computation); outcomes: entry 6. Own code: `scripts/cont.py` (with
`lattice.py`, `compare.py`). Runs (processors only, 0 card-hours): E-20261124-220857-2b8e5dc
(records), E-20261124-221133-971cd6f (dumps), E-20261124-222329-dfc72d9 (two more definitions);
failed and kept: E-20261124-220850-3ef0c7f, E-20261124-221028-81db3d8. Figures (looked at):
`fig_joins.png`, `fig_convrec_256.png`, `fig_signflip_full.png`, `fig_convspec_256.png`,
`fig_backreaction_Nf.png` in those run directories.

### 8.1 Joins: every continuation joins its original without a jump

| Run | Original / continuations | Evidence | Verdict |
|---|---|---|---|
| RNC256 | E-20261123-045030-c20bcb3 / E-20261124-130629-61fe0b0 | 116 common record lines bit-identical (all 27 columns), dump 1 byte-identical; joined 0-734, t = 4.5, N = 4.3876 | CONFIRMED |
| CL256S | E-20261123-090727-4b6e5a5 / E-20261124-130952-4be980b | 37 common lines (cycles 979-1015) bit-identical; joined 0-1386, N = 8.0989 | CONFIRMED |
| CL256U | E-20261123-065855-265732a / E-20261124-130711-a5dec67 (cut), E-20261124-201048-33a3a39 | 125 and 157 common lines bit-identical; dumps 8, 9 byte-identical in all three; joined 0-1702, N = 10.000 | CONFIRMED |
| AL2S | E-20261123-152119-38957ba / E-20261124-131359-49afe29 | no overlap (1227 / 1228); second difference across the seam over the median of its 20 neighbours: 1.00 (efolds, <phi>, <K>), 2.2 (<abs H/[H]>), 0.87 (<abs M/[M]>); constant step | CONFIRMED (no jump at the level of the neighbours) |
| RSF256 | E-20261123-035925-8439d79 / -130529-da8c917, -201031-4c41e7b, -202134-0b1ce0c, all resumed from the original's sr.00000.rst (t = 0) | 29, 1 and 82 common lines bit-identical; dumps 1, 2 byte-identical; joined 0-895, t = 5.4917, N = 5.3242 of 8.10 | CONFIRMED to cycle 895; the rest PENDING (8.6) |

### 8.2 Sign flip over its full span, and the constraint ratios against their magnitudes

| Claim (ledger row) | My evidence (RNC256 against the joined RSF256 record, 734 cycles, same dt) | Verdict |
|---|---|---|
| Flipped run ends at N = 4.39 (52) | 4.3876 (t = 4.5) | CONFIRMED |
| Largest flipped <abs H/[H]> 9.9e-8 (51) | 9.907e-8 at N = 0.32 | CONFIRMED |
| Largest flipped <abs M/[M]> 0.22 (50) | 0.2159 at N = 4.18 | CONFIRMED |
| Median ratio 1.1e5 (49) | 1.055e5 over 0.5 <= N <= ln 64; 1.029e5 over 0.5 <= N <= 4.388 | CONFIRMED |
| Smallest ratio 1.4e3 "in the window" (48) | 1.386e3 at N = 4.158 = the edge of 0.5 <= N <= ln 64. Over the full span the smallest is 2.66e2, at the flipped run's last line (N = 4.388): from N of about 3.1 the proper run's <abs H/[H]> climbs to its bump (5.10e-11 at N = 4.43) while the flipped one decays (`fig_signflip_full.png`) | CONFIRMED for the stated window; over the full span the control's contrast is 2.7e2, not 1.4e3: the row should name its window |
| Ratios against absolute magnitudes | <[H]> lies in 10.83-12.00 (flipped), so <abs H>/<[H]> equals <abs H/[H]> to 1e-7 in both runs and the absolute ratio has the same median (1.03e5); flipped <abs H> at most 1.18e-6. For M the two means differ by up to 17 per cent. In all 11 dumps of RNC256 and 24 of RSF256 the record means equal my dump means to 2.9e-15 (abs H/[H], abs M/[M], [H], abs H); my [H] = abs R3 + (2/3)K^2 + At At + abs(16 pi E) equals the dumped Hmag to 4.4e-16 | CONFIRMED (the H field itself remains the code's, section 5) |
| Proper SR maxima over N <= ln 64: 3.43e-11, 1.18e-4; 2.72e-4 by N = 4.39 | 3.429e-11 and 1.179e-4, both at N = 4.158 (window edge, still rising); 2.68e-4 by N = 4.388 | CONFIRMED (the last within 1.5 per cent) |

The order of magnitude against P1:541 ("~1e-5") is unchanged: 1e-7, a factor 100 below (section 2).

### 8.3 The 256-cell members of the two convergence figures

Fig. 8 (records, run E-20261124-220857-2b8e5dc), time-matched median of finer over coarser for
0.5 <= N <= ln 8:

| Quantity (row) | 64/32 | 128/64 | 256/128 | Ledger | Verdict |
|---|---|---|---|---|---|
| SR <abs H/[H]> (72) | 0.186 | 1.167 | 1.109 | 0.19, 1.17, 1.11 | CONFIRMED |
| SR <abs M/[M]> (73) | 0.875 | 1.005 | 1.123 | 0.88, 1.00, 1.12 | CONFIRMED |
| USR <abs M/[M]> (74) | 0.783 | 1.002 | 1.073 | 0.78, 1.00, 1.07 | CONFIRMED |
| USR <abs H - <H>/[H]> (75) | 0.342 | 0.995 | 1.031 | 0.35, 0.99, 1.03 | CONFIRMED |

The factor per doubling of the plateau is 1 from 64 on (no convergence of the plateau, as claimed).
USR H with the box mean: entry maxima 9.198e-8, 5.380e-9, 3.247e-10, 1.9856e-11, orders 4.10, 4.05,
4.03 (row 42: 4.03, CONFIRMED), USF256 1.9731e-11 (CONFIRMED). After the entry at 256: SR H 3.53e-3,
SR M 1.91e-2, USR H - <H> 5.2e-3 of the entry-end value, USR M rising 2.77e4; at N_f the 256 levels
lie above 128's in SR M (7.9e-8 against 2.9e-8) and USR H (4.2e-14 against 2.1e-14): CONFIRMED. Not
among the claims: the late SR <abs H/[H]> does converge (3.1e-12, 1.8e-13, 1.1e-14, 1.1e-15 at N_f,
factors 17, 16, 10 per doubling).

Fig. 7 (spectra at N_f, runs E-20261124-221133-971cd6f and -222329-dfc72d9; my R^NR of the CL256S
dump 17 and of the three smaller rungs; shells of more than 10 modes):

| Measure | 32 | 64 | 128 | 256 | Factors per doubling |
|---|---|---|---|---|---|
| max abs(Delta_NR/Delta_lin - 1), lin = the code's lockstep record (my reading) | 3.17e-3 | 6.16e-5 | 1.00e-6 | 2.0e-7 | 51, 62, 5.0 |
| the same, lin = my MS solution | 3.41e-3 | 7.94e-5 | 2.29e-6 | 2.0e-7 | 43, 35, 11.5 |
| per-mode rms abs(R_NR/R_lin - 1) (lockstep), all / abs(n) <= 4 | 7.1e-4 / 1.6e-5 | 1.4e-5 / 4.8e-7 | 4.0e-7 / 3.73e-7 | 3.3e-7 / 3.73e-7 | |
| per-mode rms of the power ratio (lockstep), all / abs(n) <= 4 | 1.4e-3 / 3.1e-5 | 2.7e-5 / 8.2e-7 | 6.3e-7 / 5.68e-7 | 4.4e-7 / 5.68e-7 | |
| reference-free: per-mode rms abs(R_a - R_b)/abs(R_b), pairs 32-64, 64-128, 128-256; all / abs(n) <= 4 | 7.65e-4 / 1.6e-5 | 1.87e-5 / 3.6e-7 | 6.25e-7 / 1.3e-8 | | 41, 30 / 44, 27 |

Verdicts: rows 65-67 (3.2e-3, 6.2e-5, 1.0e-6) CONFIRMED against the lockstep record. Row 68 (256:
3.7e-7) NOT CONFIRMED: both my references give 2.0e-7 (at abs(n) = sqrt 2, as the claim places the
maximum); row 69 (order 1.48) NOT CONFIRMED: 2.3 (lockstep) or 3.5 (mine); rows 70-71 (per-mode rms
7.1e-7, 6.7e-7) NOT CONFIRMED to the digits under either reading (amplitude 4.0e-7, 3.3e-7; power
6.3e-7, 4.4e-7); the ledger does not state the definition behind its 256 values. The qualitative
claims are CONFIRMED and sharpened: (i) above abs(n) = 4 the 256 field keeps converging (the
128-256 difference is 30 times below the 64-128 one); (ii) below abs(n) = 4 the 128 and 256 fields
agree per mode to 1.3e-8, 30 times below their common departure from linear theory (3.73e-7 in
amplitude at both), while the lockstep records of 128 and 256 agree to 3.4e-9 (abs(n)^2 <= 6) and
the lockstep record of 256 agrees with my independent MS integration to 7.7e-8: the floor is a
property of the resolved field relative to linear theory, independent of dx, dt and of the linear
reference [VERIFIED]. That it is second order in the amplitude is [TO VERIFY] (the claim's own
test, a run at half the noise amplitude). My own section-4/7 number for 128 (2.3e-6 against my MS)
was the 128 field's top-shell lattice error, part of which the code's 128 lockstep record shares
(it differs from my MS by up to 1.2e-6 there); my prediction that my reference could not go below
1e-6 failed.

### 8.4 Slow roll, level 2 against level 0 at the final time

AL2S dump 17 (t = 8.5, N = 8.0989) against AL0S dump 17, my R^NR and shell sums (run
E-20261124-222329-dfc72d9):

| Row | Claim | Mine | Verdict |
|---|---|---|---|
| 81 | largest shell 7.93e-5 (lowest shells) | 7.932e-5 at abs(n) = 4.47 over the 3395 shells of more than 10 independent modes; 1.125e-4 at abs(n) = 22.6 if both hemispheres count (a 12-mode shell); 1.405e-4 at abs(n) = 3.46 over all exact abs(n)^2 shells | CONFIRMED with that definition |
| 82 | rms over abs(n) <= 32: 1.505e-5 | 1.505e-5 (independent modes); 1.557e-5 (both hemispheres); 1.748e-5 (all shells) | CONFIRMED with that definition |
| 83 | fraction positive 0.50 (49.7 per cent) | 49.66 per cent | CONFIRMED |
| - | per-mode relative rms 2.2e-4; the same to four digits as at t = 7.5 | 2.23e-4; the shell differences change by 1.2e-4 of their maximum between t = 7.504 and 8.5 | CONFIRMED |

The same definition also settles section 2's USR maximum: 7.03e-4 over shells of more than 10
independent modes (ledger row 77, 7.0e-4: CONFIRMED with it), 9.15e-4 over all shells.

### 8.5 P1:520 and the backreaction verdict under the right bound

The source line P1:520 reads "a detectable but $\lesssim 1$\textpertenthousand\text{} relative
change in power spectrum for all scales", with `textcomp` loaded at P1:43: the symbol is per ten
thousand, 1e-4, not per mille. The note is right; section 2's phrase "All below P1:520's 1 per
mille" read the wrong symbol (sections 1-7 are left as written; this paragraph replaces that
verdict). Under 1e-4:

- SR (N_f): every shell of more than 10 independent modes meets the bound (largest 7.9e-5); 3 of
  3414 sparse shells exceed it, at most 1.4e-4, all at abs(n) <= 32. P1:520 CONFIRMED for SR.
- USR (N_f): rms over all shells 1.04e-4, at the bound; 24 per cent of the shells exceed it (1.8 per
  cent for abs(n) <= 32, 32 per cent above), the largest by a factor 9 (9.15e-4; 7.0e-4 with more
  than 10 independent modes). P1:520's "for all scales" is NOT met by our USR level 2 above
  abs(n) of about 32. Whether P1's own Fig. 9 shows the same I did not read off in this pass.

### 8.6 Pending (RSF256 beyond cycle 895)

RSF256's fourth continuation is queue entry **q0034** (run E-20261124-214913-5956891, Slurm job
5215, PENDING when checked at 14:05 PST; it resumes from sr.00002.rst of E-20261124-202134-0b1ce0c
at cycle 652, so it overlaps cycles 653-895 and its join can be checked bit for bit with
`cont.py --only joins` after adding its run id to `RUNS["RSF256"]`). PENDING on it: ledger row 56
(SR per-cell constraint rows of the one-point figure), the constraint panels of P1 Fig. 2, P1 Fig.
3 from RSF256 itself, and the proper SR constraint record from N = 5.32 to N_f. Not pending: the
sign-flip control (its proper partner is joined beyond N = 4.39).

### 8.7 The three weakest points after this pass

1. Unchanged: the factor 3.5-4 in the one-point amplitudes and the factor 100 in the flipped
   H/[H] against P1 (section 6, point 1).
2. Narrowed again: of the new rows, those that depend on a definition the ledger does not state
   are 68-71 (the 256 member of Fig. 7: 3.7e-7, order 1.48, per-mode 7.1e-7 and 6.7e-7). Two
   independent references give 2.0e-7 and order 2.3-3.5; the claim that the convergence stalls at
   256 at the lowest shells stands, its digits do not. Rows 48 and 81-82 hold only with their
   window (0.5 <= N <= ln 64) and shell count (independent modes), which they should name.
3. Resolved for four of five continued runs (joins bit-exact, sign flip to N = 4.39, level 2 at
   N_f, 256 rungs in both convergence figures); RSF256 remains (8.6).
