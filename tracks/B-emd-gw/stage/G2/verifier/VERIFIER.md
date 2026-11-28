# Verifier's report, gate G2 of Track B (B-emd-gw)

Fresh-context verifier (checklist item C18; decisions 0016 item 4, 0046 item 2, 0048 item 3),
batch 35, 2026-11-27, 17:56 to 18:30 PST. Processors only, no card run. Package:
`tracks/B-emd-gw/stage/G2/verifier/` (predictions and outcomes in `JOURNAL.md`, committed
before and after each recomputation; scripts in `scripts/`; figures in `figs/`, all looked at).
Sections 1 to 5 were written before I read any verdict of the lead; section 6 compares.

## 1. What I read, what I did not, and how I recomputed

- Claims: the end of `stage/G2/OPEN.md` ("what to recompute first"; the file is 49 lines and I
  read it whole, so its first paragraph with the lead's states was read too, which limits the
  freshness for C1, C2, C3), `stage/G2/REPRODUCE.md`, note section VI and Tables V, VII and
  VIII of `note/tables/ledger.tex`, `scope/SCOPE.md` sections 4 to 7, the track sheet
  (charter 9.5), `shear/SPEC.md` sections 4 to 7 (the shearing-dust quantity and criteria).
- Definitions only (so that my number is the same quantity) from the lead's scripts: the band
  rms of `compare_legs.py` (`band_rms2`), the halo definition of `analyze.py` (FoF, b = 0.2 of
  the mean spacing, at least 100 particles, common limit 100 m_N with m_N = rho_c L^3/64^3),
  the measures' shell binning in `analyze_gr.py`. Nothing of theirs was imported or run. My FoF
  turned out to be the same textbook construction as theirs (KD-tree pairs, connected
  components); FoF groups are unique for given positions and link length, so this shares no
  free choice.
- Not read before this report: journal outcome entries, `stage/REVIEW-wave3.md`, the verdict
  column of `stage/G2/CHECKLIST.md` (I extracted the item texts with a filter),
  `STAGE_REPORT.md`, `VERIFY_RESULTS.md`.
- My readers (`scripts/vlib.py`) were written from `athenak/src/outputs/binary.cpp` and
  `docs/FORMATS.md` and tested first on analytic cases (run `B-20261128-021054-577fc9d`):
  a synthetic dump of 2 x 2 x 2 meshblocks written in shuffled order read back exactly; a
  synthetic particle snapshot exactly; my flat TT projector returns a random TT field to
  1.5e-16, is idempotent to 1.5e-15, removes a pure-gauge field d_i xi_j + d_j xi_i to 5e-32
  and a trace field to 7e-33 of its power; FoF recovers four Gaussian clumps (one across the
  periodic face) exactly. A dry run before it failed (Nyquist planes; JOURNAL entry 3).
- Exact solutions written by me: F (flat wave, k = 2 pi (1,1,1), L = 1): the forward
  combination W_ij = h^TT_ij(k) + i h'^TT_ij(k)/|k| (h' = -2 alpha A_ij) of the t = 0 dump,
  carried by exp(-i|k|t); X (matter era, k = 2 pi (1,1,0)/4): h = C1 j1(x)/x + C2 y1(x)/x,
  x = k(t + 2), fitted per polarization to h and h' of the t = 0 dump (h'' + 4h'/(t+2) +
  k^2 h = 0 for a = ((t+2)/2)^2). The reference is the exact evolution of the dumped initial
  slice, not of the analytic data; the code's initial data themselves are not checked here.

## 2. Claim by claim

Verdicts: REPRODUCED (digits stated), NOT REPRODUCED, NOT CHECKABLE (why). Run ids of mine.

### 2.1 Linear and expanding-box waves (note Table V) — run `B-20261128-021125-515c0cc`

| Claim | Mine | Verdict |
|---|---|---|
| F amplitude error -1.41e-4, -1.72e-6, -1.57e-7, -3.1e-8 (N = 16, 32, 48, 64) | -1.4092e-4, -1.7174e-6, -1.5742e-7, -3.1218e-8 | REPRODUCED, every printed digit |
| F phase error 2.53e-4, 1.22e-5, 2.27e-6, 7.07e-7 | 2.5310e-4, 1.2176e-5, 2.2728e-6, 7.0694e-7 | REPRODUCED, every printed digit (same sign convention) |
| X cross amplitude -7.05e-5, 1.32e-6, 4.25e-7, 1.4e-7 (t = 10, a = 36) | -7.0481e-5, 1.3169e-6, 4.2498e-7, 1.3989e-7 | REPRODUCED, every printed digit |
| X cross phase 8.3e-5, 3.06e-6, 5.88e-7, 2.76e-7 | 8.3039e-5, 3.0650e-6, 5.8797e-7, 2.7624e-7 | REPRODUCED, every printed digit |
| X plus over prediction - 1 at N = 48, 64: amplitude 0.0263, 0.0997; phase 0.102, 0.391 | plus over cross - 1: 0.026, 0.100; 0.102, 0.391 | REPRODUCED (the prediction equals the cross error at these N) |
| non-TT part of F small (rounding of the TT data) | non-TT over W at the last dump 0.8e-9 to 2.1e-9 | consistent |

Figure `figs/v1_waves.png`. The box-mean lapse of X (equal to a in this slicing) departs
from ((t+2)/2)^2 by -5.5e-8 to -7.0e-8 at t = 10; the ledger's "largest relative error of the
scale factor" (3.2e-8 to 5.1e-8) is a different measure, not compared. Not recomputed: the
Weyl diagnostic rows of Table V and the flat wave F2.

### 2.2 Population box: strain, gauges, halos, the zero-shift stop

Runs `B-20261128-021923-351e31f` (strain; earlier attempts `-021349-a57f21e` and
`-021412-072e411` failed on bugs of mine), `B-20261128-022328-1a9d681` (high-k cut),
`B-20261128-021413-6b4d7a1` (halos), `B-20261128-022330-6e6076d` (histories).

| Claim | Mine | Verdict |
|---|---|---|
| Band |k| <= 8 k_f, Gamma driver, 256^3/128^3 within 1.1 % to a = 64 (0.0109) and 2.8 % to a = 132 (0.0277) | from the analysis files: 0.010897 and 0.027699 (corrected), 0.010899 and 0.027544 (raw); my raw recomputation from the dumps equals the files' rms and band to 1e-15 at all 14 dumps read | REPRODUCED, 3 digits |
| (implicit) pairing of the two meshes by a | the 128^3 dumps lie 0.0082 later in t; interpolated to the 256^3 times: 0.0115 and 0.0271; exact per-mode band (no n^-2 shell weight) at a = 64: 0.0119 | the 1.1 % holds to 0.1 percentage point; not sensitive |
| gauge piece negligible in the shifted gauge | G_tot is 0.03 to 1.07 % of the rms; raw and corrected band ratios agree within 0.02 % | REPRODUCED |
| TT measure over all shells 0.851, above 16 k_f 0.805 at a = 121 (256/128) | 0.8511, 0.8050 (files) | REPRODUCED (from the files only) |
| High k: zero shift over Gamma driver above 16 k_f at a = 121: 946 (corrected) | 945.56 (files, corrected); raw: files 1864.09, mine 1864.09 with the files' shell cut, 1699.9 with all modes off the Nyquist planes | REPRODUCED within its definition; the number depends on the shell cut (section 5c) |
| corrected band, Gamma over zero shift, at a = 100: 0.803 | 0.8026 (files) | REPRODUCED (files) |
| halos >= 100 particles at a = 121, equal masses: 108 (zero shift), 98 (Gamma), 106 (Newtonian mode) | 108, 98, 106 (my FoF on the snapshots) | REPRODUCED exactly |
| median |M_GR/M_N - 1| of the ten largest at a = 121: 0.0264, 0.0123 | 0.0264, 0.0124 (all ten have a partner within 0.1) | REPRODUCED (last digit of the second) |
| largest halo M_GR/M_N - 1, 81 <= a <= 132: -0.109 to -0.069 (zero shift), +0.017 to +0.051 (Gamma) | at a = 121: -0.091, +0.029 (one epoch only) | consistent at the epoch checked |
| mass spread of the particle files: GR 0.0283, Newtonian 0.000197 | 0.0283, 0.0002 | REPRODUCED |
| 256^3/128^3 Gamma, equal masses: count above the common limit, smallest 0.484; largest-mass ratio 1.32 (a = 64), 1.13 (a = 121) | counts 8/11 = 0.727 (a = 64), 15/31 = 0.484 (a = 121); largest mass 1.3235, 1.1279; my 256^3 catalogues equal the lead's file (242, 8, 1.038; 431, 15, 1.905) | REPRODUCED at the two epochs checked; |15 - 31| = 16 > 2 sqrt(31) + 2 = 13.1: outside the counting band at a = 121, as claimed |
| 256^3 zero shift: K_max > 0 from a = 79.9, last record a = 101, K_max 0.0224 there | first positive record a = 79.88 (linear crossing 79.36), last finite record a = 101.25 with K_max 0.02244, guard stop at t = 18.21 | REPRODUCED, 3 digits. K_max does not stay positive between a = 80 and the stop |
| Gamma driver: largest K after t = 9 -0.000844 (256^3), -0.00141 (128^3); last a 143 | -0.000844, -0.00141, 142.5 | REPRODUCED |

Figures `figs/v2_strain.png`, `figs/v5_halos.png`. Not recomputed: the corrected strain
(G_tot) from the dumps (I used the files' corrected spectra), the 0.028 box, the
equal-mass halo comparisons at epochs other than a = 64 and 121, the zero-shift 256^3
halo counts (0.609 to 0.867), the strain of the particle leg (8 per cell).

### 2.3 Constraints (C3) — runs `B-20261128-021515-a6306af`, `-022330-6e6076d`

| Claim | Mine | Verdict |
|---|---|---|
| 8 per cell, 64^3/128^3, zero shift, Hr_mean: 1.32 to 2.34 over 25 <= a <= 141; >= 1.64 for a >= 49 | 1.324 to 2.340; 1.638 (a >= 36 and a >= 49); pairing variants 1.62 to 1.64 | REPRODUCED, 3 digits |
| the same, Mr_mean for a >= 49: 1.71 to 2.16 | 1.715 to 2.159 | REPRODUCED, 3 digits |
| ratio 1.32 at a = 25, smaller before a ~ 31 | 1.31 at a = 25 (interpolated); below 1 (0.95) at a = 1.9 to 2.6 | REPRODUCED |
| 1 per cell, 128^3/256^3, Gamma driver, Hr: 1.11 to 1.36 (25 <= a <= 141), 1.11 at a = 141; Mr 256/128 0.884 at a = 141 | 1.105 to 1.360 (nearest records), 1.106 to 1.380 (interpolated); 1.106; 1/1.1316 = 0.884 | REPRODUCED with nearest-record pairing |
| 1 per cell, zero shift, Hr: 1.11 to 1.36 (36 <= a <= 100, Table VII); 1.05 to 1.37 (Table VIII); "1.05 to 1.4" (note) | 1.13 to 1.17 (minimum) and 1.39 to 1.41 (maximum) over 36 <= a <= 100 in three pairings; 1.035 to 1.047 and 1.39 to 1.41 over 25 <= a <= 100 | NOT REPRODUCED to the printed digits (maxima 2 to 3 % higher, Table VII minimum not found); the note's "1.05 to 1.4" holds |
| particle leg, 128^3, one over eight per cell at a = 141: Mr 2.93, Hr 1.58 | last records (a = 140.74 in both): 2.932, 1.575 | REPRODUCED |
| continuation repeats the cut run to 4.23e-12 | 4.229e-12 over 6 common records | REPRODUCED |

Figure `figs/v3_constraints.png` (claimed bands shaded).

### 2.4 Shearing dust — runs `B-20261128-021337-d0c2105`, `-022420-5d1f804`

| Claim | Mine | Verdict |
|---|---|---|
| series 7 (beta = 0.125, HL = 4, 4 per cell along y): Delta 0.0537, 0.0538, 0.0538 at N_y = 64, 128, 256 | 0.0537486, 0.0538000, 0.0538206 (= cos/cos_lin - 1 of the stored values) | REPRODUCED (arithmetic on the stored ray results; the ray tracing itself not redone) |
| ratio of differences 0.401, finest minus Richardson -1.38e-5 | 0.4007 (order 1.32), -1.379e-5, Richardson 0.0538344 | REPRODUCED |
| cos(theta_lin) of the closed form | mine 0.1259217103254327 with b = beta (HL)^2 = 2, equal to the files'; second quadrature 4e-14 | REPRODUCED |
| no stream crossing before t_A = 4.12; smallest spacing 0.699 of the lattice spacing; first crossing at t = 9.25, 9.25, 9 | my ordering check from the particle snapshots: 0.6992, 0.6993, 0.6993 up to t_A; first crossing snapshot 9.25, 9.25, 9.00 | REPRODUCED |
| constraint means over 1 <= t <= t_A: Hr 3.62e-6, 2.73e-6, 2.55e-6; Mr 2.33e-4, 1.66e-4, 1.64e-4 | the same (plain record means; trapezoid within 0.4 %) | REPRODUCED; Mr falls 1.5 % from 128 to 256 |
| L2 as run (beta = 0.5, HL = 4, 4 per cell) moves away from CosmoGRaPH's -0.8183 with each refinement | -0.82180, -0.83123, -0.83915; distance 0.0035, 0.0129, 0.0208; differences' ratio 0.84 (no convergence) | REPRODUCED: fails as claimed |
| L2: "its streams cross before the observer's light rays arrive" (note section VI) | the L2 runs (`B-20261124-135516-34befaf`, `-135951-237e27b`, `-140856-911ded9`, and the 1-per-cell series) wrote only the t = 0 particle snapshot | NOT CHECKABLE from the outputs I found |

Figures `figs/v4_shear_crossing.png` (smallest spacing against t; Delta against N_y),
`v8_shear_cstat.png` in run `B-20261128-022420-5d1f804`.

## 3. Predictions of mine that failed as written

- V0 in an unregistered dry run: the TT round trip failed at the Nyquist planes; fixed by
  excluding them (as the lead's measures do) before any claim was read.
- V3: "my raw recomputation gives the files' ratio within 10 %" failed (1700 against 1864);
  cause found in a run that could have failed (`B-20261128-022328-1a9d681`): the files'
  spectrum stops at shell n/2 = 64; with that cut my value equals theirs to 1e-15.
- V5: "each extreme within 3 %" failed for the zero-shift one-per-cell pair (maxima 1.39 to
  1.41 against 1.36 and 1.37; Table VII minimum 1.11 against my 1.13 to 1.17).
- V7b: "my crossing check must find L2's streams crossing before t_A" could not be run (no
  snapshots): not checkable, not refuted.

## 4. What G2 can claim and what it cannot

Criteria: the track sheet's G2 (charter 9.5: sub-percent scale factor and growth rate
converging in particle number and mesh; weak-field agreement), decision 0013 for Track B
(the multi-code row is the shearing-dust comparison and full GR against the Newtonian mode),
decisions 0046 item 2 and 0048 item 3, the checklist items C1 to C3.

Can claim [VERIFIED by my recomputations]:
1. The periodic Z4c box propagates exact linear tensor waves, flat and in the matter era, with
   errors that converge (F amplitude order 6.4, 5.9, 5.6; phase about 4), and the TT
   diagnostic recovers them; every number of Table V that I recomputed holds to its digits.
2. In the Gamma-driver gauge the box-mode strain (|k| <= 8 k_f) of the halo-population box is
   the same on 128^3 and 256^3 within 1.1 % to a = 64 and 2.8 % to a = 132, insensitive to the
   time pairing and to the band weighting at the 0.1 % level.
3. With equal particle masses, full GR reproduces the Newtonian-mode halo population of the
   same particles at 128^3: counts 108 and 98 against 106 at a = 121, the ten largest within a
   median 2.6 % (zero shift) and 1.2 % (Gamma driver).
4. The zero-shift slicing breaks down in resolved cores (256^3 stop at a = 101 after K_max
   turns positive near a = 80); with the Gamma driver K_max stays negative after t = 9 on both
   meshes.
5. At eight particles per cell the mean constraints fall 1.6 to 2.3 times (Hamiltonian, from
   a = 36) and 1.7 to 2.2 times (momentum, from a = 49) when the spacing halves from 64^3 to
   128^3; at one particle per cell 1.05 to 1.4. This is decision 0046 item 2(b)'s statement of
   convergence at fixed sampling, on one pair of meshes.
6. Shearing dust without stream crossing (series 7) converges in the mesh (order 1.3; finest
   within 1.4e-5 of the extrapolated Delta), and no stream crosses before the rays arrive.

Cannot claim:
1. A mesh-converged halo catalogue at one particle per cell: the 256^3 Gamma-driver box has
   0.73 and 0.48 times the 128^3 count above the common limit at a = 64 and 121 (outside the
   counting band at 121) and a 32 % and 13 % heavier largest halo. G3 needs more particles
   per cell at the finer mesh (decision 0048 item 3 names the 256^3 member at eight per cell).
2. Convergence "in gauge": the band strain differs by 20 % between the gauges at a = 100 and
   the high-k field by a factor of order 10^3; the strain is a Gamma-driver-gauge quantity.
   Read as a choice of gauge, not as a leg that converged.
3. An order of convergence of the constraints: one pair of meshes at eight per cell, at a
   coarser spacing than the one-per-cell pair.
4. The shearing-dust L2 comparison (beta = 0.5): it moves away from CosmoGRaPH with each
   refinement and does not converge (ratio of differences 0.84). That stream crossing before
   the rays arrive is the cause is plausible from the series-7 contrast but is not shown by
   any L2 output I could find.
5. That the constraint solution converges where Delta does: in series 7 the mean momentum
   constraint over 1 <= t <= t_A falls only 1.5 % from N_y = 128 to 256 (Hamiltonian 7 %),
   so the converged observable sits on a constraint floor whose cause is not named.
6. The track sheet's sub-percent FLRW scale factor and growth rate (C7) and the strain's
   independence of particle number (8 against 1 per cell): not in my recomputation; I make no
   statement on them.

## 5. Findings and corrections for the lead

a. Note section VI: "From a ~ 36 on, ... its mean momentum constraint 1.7 to 2.2 times": from
   a = 36 the momentum ratio reaches down to 1.45 (a = 36 to 49); 1.7 to 2.2 holds from
   a = 49, as Table VIII says.
b. Tables VII and VIII, zero-shift one-per-cell Hamiltonian ratio (1.11 to 1.36; 1.05 to
   1.37): my three pairings give maxima 1.39 to 1.41 and, over 36 <= a <= 100, minima 1.13 to
   1.17. Name the pairing used or correct the numbers; the note's text "1.05 to 1.4" holds.
c. "Above 16 k_f about 950 times" (note, Table VII): state that the spectrum stops at shell
   n/2 = 64 (the cube's corner modes are excluded); with them the raw ratio is 1700 instead of
   1864, because 9 % of the shifted run's measure above 16 k_f lies in the corners.
d. L2 "streams cross before the rays arrive": give the run that shows it or label it
   [TO VERIFY]; the L2 runs I found have no snapshot after t = 0.
e. [JUDGEMENT] SPEC section 7 item 5 ("within max(3 x own numerical error, 0.01) of
   CosmoGRaPH") is met by a series that does not converge when the error is estimated from
   its own differences (L2: finest within 0.021 of -0.8183, three times its last difference
   is 0.024). The verdict "failed" rests on the non-convergence; the criterion should ask for
   convergence first.
f. The detached `nrpic-stage verify B-emd-gw G2 --full` (PID 2643528) ended at 18:21 PST:
   PASS, 0 failed checks, 13883 output files read again (1166.91 GB); it left
   `stage/G2/VERIFY_RESULTS.md` and `.json` modified and uncommitted (log
   `scratch/B-emd-gw/tmp/verify_full_b34.log`). Its package line still says "no verifier's
   report yet".

### Coverage of the ledger (C18 asks for every number of the Supplemental Material)

- Table VIII (convergence statements of G2), rows 273 to 279: recomputed, all but the GM3
  counts at a = 81, 100, 132 (I ran two of the five catalogue epochs) and the zero-shift
  one-per-cell Hamiltonian extremes (not reproduced, section 2.3).
- Table VII: rows 233, 234, 237, 238, 242, 243 (momentum part reproduced, Hamiltonian part
  not), 244, 246, 247, 260 recomputed; rows 239 (one epoch), 249 (high-k part not, band part
  not) in part; rows 231, 232, 235, 236, 240, 241, 245, 248, 250 to 259 not recomputed (the
  0.028 box, the cut particle leg, the superseded rest-mass reading, the zero-shift 256^3
  halos, the same-particle estimator).
- Table V (waves): the F and X error rows and orders recomputed to every digit; the Weyl rows,
  the polarization-ratio and non-TT rows only in part.
- Tables I to VI (G1 and the first source): not in this package (signed at G1).
So C18 as worded ("every number recomputed") is not met by this report; the numbers the gate
rests on (Table VIII and the strain, halo, stop and constraint rows of Table VII) are.

## 6. Against the lead's verdicts (written after sections 1 to 5)

Read only now: the verdict column of `stage/G2/CHECKLIST.md` (C1 to C20), `stage/REVIEW-wave3.md`
section "Batch 34", `population/JOURNAL.md` entries 2026-11-27 15:24 and 15:28, and the lines of
`shear/JOURNAL.md` on the L2 crossing (around its lines 60-66, 425-436, 446-514).

- C1 (PASS under 0046 item 2(a); L2 FAILED on record; series-7 constraint floor open): I
  agree, with every series-7 number reproduced. The lead's own review left the crossing
  measure unchecked ("left to the verifier"): I recomputed it from the snapshots and it
  holds (0.699; first crossing 9.25, 9.25, 9.00). One difference of reading: the claim that
  L2's streams cross before its rays arrive rests on a plane-parallel Zel'dovich estimate
  (t = 2.1 to 2.2, called conservative) and an observer-metric kink at t = 3.1, not on L2
  particle data. The same estimate put series 7's crossing at 10.7 to 14.9; the snapshots show
  9.0 to 9.25, so the estimate is not conservative as stated. For L2 the margin (2.1 against
  t_A = 6.5) is wide enough that the attribution likely survives [JUDGEMENT], but it is an
  inference, not a measurement, and should be worded so (my correction d).
- C2 (PASS "for the strain with that limit stated"): I agree on the numbers (band strain
  1.1 and 2.8 per cent; Omega 0.851; halo counts 8/11 and 15/31 at the epochs I ran; largest
  mass 1.32 and 1.13; 256^3 catalogue equal to the lead's file). I differ on the gauge leg:
  the checklist item asks for convergence in gauge, and the lead's evidence is a choice of
  gauge (the zero-shift high-k field identified as coordinates, the strain read in the driven
  gauge), while the band strain itself differs by 20 per cent between the gauges at a = 100.
  I would record C2 as passed for mesh and particle number of the band strain, with the gauge
  leg met only as an identified gauge dependence, and the halo catalogue failed at one
  particle per cell (the ruling the lead asked for). The particle-number leg (Q1, 2e-3) I did
  not recompute.
- C3 (PASS under 0046 item 2(b) and 0039 item 2(c)): I agree; the lead's interpolation (128^3
  in log a onto the 64^3 rows) and mine (log q in t, both directions, nearest records) give
  the same 8-per-cell extremes to the third digit. The lead's one-per-cell zero-shift range
  1.05 to 1.37 (and Table VII's 1.11 to 1.36) I do not reproduce at the maximum (1.39 to
  1.41); the conclusion (1.05 to 1.4 against 1.6 to 2.3) stands. The note's "from a ~ 36 on"
  for the momentum ratio contradicts the lead's own journal (1.45 at a = 36.7) and Table VIII
  (a >= 49).
- GM2 Omega part, GM3, C3a: the lead's "fails as written, not refuted" and "fails in part"
  match my numbers; I found no failed prediction recorded as held.
- C7 (FLRW, PASS) and C9's earlier shearing cases (S1 to S4, M1, L1, P10): not recomputed by
  me; no statement.
- C18: this report; it is in the helper's directory, the lead copies it to
  `stage/G2/VERIFIER.md`. Section "Coverage" says what it does not cover.
- The `--full` stage verify the lead left running ended PASS (0 failed checks, 13883 files,
  1166.91 GB read again) with `VERIFY_RESULTS.{md,json}` modified and uncommitted in the
  worktree; its package line predates this report.

Net: every number I recomputed that the gate rests on holds to its printed digits, with two
exceptions that change no conclusion (the zero-shift one-per-cell constraint maximum; the
high-k ratio's dependence on the shell cut) and one claim not checkable from the outputs (L2's
crossing time). My reading of the gate agrees with the lead's except that the gauge leg of C2
is a choice of gauge, not a convergence, and should be recorded as such.
