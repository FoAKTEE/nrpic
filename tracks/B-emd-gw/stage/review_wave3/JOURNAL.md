# JOURNAL of the lead's wave-3 review (B-emd-gw, batch 2a, 2026-11-20 night)

Predictions are written and committed before the review runs they concern; outcomes are
appended below, also where a prediction fails. Scripts: `scripts/`. Runs: manifests under
`tracks/B-emd-gw/runs/`, outputs under `scratch/B-emd-gw/<run id>/`. The review itself is
`../REVIEW-wave3.md`. Times PST.

## 2026-11-20 22:55, state found

- No session of this owner was running; no card job of the owner queued or running (squeue).
- Seven runs of the cut round 1 (14:00-14:35) had finished unattended, all exit 0, and were
  never closed. Closed now with `nrpic-run finish` (manifests committed, outputs checksummed):
  B-20261120-222841-acfe21d (card job 4745: waves F2 at N = 64, step test XS at N = 16-64),
  B-20261120-222849-3b921b7 (waves F2 at N = 16, 32, 48, processors),
  B-20261120-222849-e5673dc (waves XS at N = 16, 32, processors),
  B-20261120-222955-c8e16e3 (card job 4746: flrw_conv J1, legs F and B at 32^3),
  B-20261120-223006-24448ac (flrw_conv P1 at 16^3), B-20261120-223236-e213594 and
  B-20261120-223241-f1efd4f (first_source r3, analyze_scan of the 128^3 and the 1 and 27 per
  cell runs). None of them is analysed: they belong to packages still in progress.
- Stranded files: the note v2 package had finished ("End of the package (14:36 PST)" in
  note/JOURNAL.md) and left its last outputs uncommitted; every file of note/figures and
  note/tables equals the outputs of run B-20261120-223319-cc5320d (cmp over 28 files, 0
  differences); committed (e1773add). Left alone, package in progress: `gw_diag/gwdiag/gauge.py`,
  `gw_diag/tests/test_gauge.py`, `waves/scripts/check_gauge.py` (waves round 1, step 4).

## Predictions L1-L3 (before any review run)

Independence: I read the helpers' reports and both the waves README and verifier3's
VERIFIER.md before writing these, so this is a recheck of artefacts, not a blind one.

**L1 (criterion 1, two readings compared).** A script compares every number that both
`waves/results/{final,x10_64}_results.json` and `stage/G1/verifier3/results/v3_summary.json`
give (TT amplitude and phase errors at the last dump, both polarizations, F and X, N = 16..64,
x10) after checking that the committed JSON copies equal the registered outputs.
Prediction: all agree to 1 per cent of the error (most to the printed digits) except the X
plus amplitude at N = 48 and 64 at x1, where the waves value exceeds the verifier's by 1.2e-8
and 1.6e-8 absolute (verifier3 V3 table); at x10 the two differ by less than 2e-9. Refuted if
any other pair differs by more than 1 per cent.

**L2 (third reading of the disputed number).** My own extraction of test X at N = 64 from the
raw double-precision dumps (x1: B-20261119-142124-feb2daf/expN64; x10:
B-20261119-155758-458cf17/expN64x10): H_p = 2 e_p:hat(gt - 1)(K)/(N^3 e_p:e_p) and
H_p' = 2 e_p:hat(-2 alpha At)(K)/(N^3 e_p:e_p) (zero shift), Z = H + i H'/|K|, against
A_p (T + i T'/|K|) with T from a numerical integration of T'' + 4 T'/(t + 2) + K^2 T = 0,
T(0) = 0, T'(0) = 1 (not the Bessel closed form), basis (theta-hat, phi-hat) checked on the
t = 0 dump. Prediction at t = 10: cross amplitude error 1.399e-7 +- 1e-9 and phase 2.762e-7
+- 2e-9 (both earlier readings); plus phase 3.85e-7 +- 2e-9; plus amplitude 1.378e-7 +- 3e-9
(the verifier's reading) and not 1.538e-7; at x10 both amplitudes within 1.398e-7 to
1.402e-7. Refuted if my x1 plus amplitude lies within 5e-9 of 1.538e-7, or more than 5e-9
from both readings (then a third convention is in play and the disagreement is not settled).

**L3 (population, the factor 3).** population/JOURNAL marks [TO VERIFY] that 2312.12499
main.tex:581 writes the curvature-density relation with 6/5 where Phi = (3/5) R (line 324)
and the code's dictionary give 3/5 behind the normalization of DESIGN.md. Prediction from
the report only: line 324 carries Phi = (3/5) R for matter domination, and line 581 carries
a factor that, combined with the Poisson equation, is twice the 3/5 route (the report's
"factor 3" is then in the power spectrum, or the two lines describe different variables).
Refuted if line 581 agrees with line 324 once the variables are matched. This is a reading
of the source (kb-data), no run.

## Outcome of L1 and L2 (run B-20261121-063617-6183015)

`lw3_crit1.json`, `lw3_crit1.png` in the run directory (copied to `results/`, `figs/`).

- Copies: the three committed JSON files equal their registered outputs byte for byte.
- **L1 HOLDS except one pair, marginally REFUTED as written**: the two readings agree to 1 per
  cent of the error or better on every number except the X plus amplitude at x1, N = 48 (waves
  4.3616e-7, verifier 4.2346e-7, +3.0 per cent) and N = 64 (1.5384e-7 against 1.3775e-7,
  +11.7 per cent), as predicted, and except the F cross amplitude at N = 64 (-3.2037e-8 against
  -3.1697e-8: 1.07 per cent, 3.4e-10 absolute), which my 1 per cent bound did not allow; at
  N = 64 the F amplitude error is 3e-8 and a 3e-10 difference is the round-off share of either
  processing [JUDGEMENT]. The X plus amplitude at x10 differs by 1.25 per cent, 1.75e-9
  absolute, inside the predicted 2e-9. Figure `figs/lw3_crit1.png` looked at: in (a) only
  those points lie above the 1 per cent line; in (b) and (c) the plus curves of x1 leave the
  cross from t = 4 on and the x10 plus curve lies on the cross curves.
- **L2 REFUTED**: my third reading gives at x1 plus amplitude error 1.53836e-7, phase 3.84155e-7;
  cross 1.39889e-7, 2.76239e-7; polarization ratio modulus -1.3947e-8, argument -1.0792e-7. That
  is the waves reading to 1e-6 of itself (1.53836e-7, 3.84155e-7), not the verifier's 1.3775e-7.
  At x10: plus 1.41541e-7, cross 1.40092e-7 (waves: 1.41542e-7, 1.40092e-7). The t = 0 check of
  the basis holds (H_p'/A_p = 1 to 2e-11, imaginary part 2e-16). So two readings with different
  code (waves/wlib and mine: direct sums over the cell centres, no projection) find the plus
  amplitude 1.39e-8 above the cross at x1 and 1.45e-9 at x10 (a 1/A excess, rounding in the
  data), while verifier3 finds plus = cross to 2e-9. My prediction took the verifier's side; it
  failed. The disputed number is a property of the verifier's processing, not of the dumps.

## L2b prediction (before the run): where verifier3's plus amplitude comes from

verifier3 projects the whole field with its Fourier Lambda (`diag.tt_project`, rfftn and irfftn
with the k = 0 and Nyquist planes removed), contracts with e_p in real space and takes the mode
coefficient with a second FFT. For a TT basis tensor e_p:Lambda h(K) = e_p:h(K) exactly, so the
two routes can differ only by rounding of the round trip or by the content the mask removes.
Prediction: applied to the last x1 dump with verifier3's own reader and basis, the direct
contraction e_p:c(K) gives 1.5384e-7 (plus) and the route through tt_project gives 1.3775e-7:
the difference sits in the projection step. Refuted if the direct contraction with its basis
and reader already gives 1.3775e-7 (then it is the reader or the basis, and I name neither as
the cause).

## Outcome of L2b (run B-20261121-063835-826c461): REFUTED; the cause is found elsewhere

- verifier3's projection route equals the direct contraction to 2e-16 (x1 and x10, both
  polarizations, with and without the mask): the prediction that the difference sits in the
  projection step is refuted. Its own route gives |Z_+| / (2 |Z_x|) - 1 = 1.39e-8 at x1, the
  same plus-cross modulus difference as waves and my reading.
- Reading `v3_summary.py` (lines 99-112) after the run: the summary builds
  Z = Re H + i Re H'/|K| and records the imaginary parts separately ("max spatial quadrature").
  So verifier3's amplitude error is that of the part of the mode in phase with cos(K.x) of the
  exact solution, while waves and I take the modulus of the complex amplitude. The plus
  polarization carries a spatial-quadrature part (a shift of the standing wave's nodes) of
  7.2e-9, 1.27e-8, 1.61e-8 at N = 32, 48, 64 (x1) and 1.75e-9 at x10, against 2.4e-13 for the
  cross (v3_summary.json): equal to the waves-minus-verifier differences of the plus amplitude
  (7.2e-9, 1.27e-8, 1.61e-8; x10 1.75e-9). [VERIFIED by the numbers of the two runs; the
  identification is arithmetic, not a new run.]
- Verdict on verifier3's X1 item: both readings are right for their definition. The README's
  plus amplitudes at N = 48, 64 are the moduli of the complex amplitude and include the
  rounding share of the plus polarization (1/A: it falls ninefold at x10), which lives in the
  spatial quadrature; verifier3's values leave that share out. What the track states: the X plus
  amplitude at N >= 48 at amplitude 1e-6 is rounding-limited by 1.3e-8 to 1.6e-8 relative; the
  truncation error at N = 64 is the cross value 1.399e-7, which the x10 run gives for both
  polarizations (1.40e-7 to 1.42e-7). Small defect, corrected in the stage documents and as a
  lead note in waves/README.md.

## Outcome of L3 (reading of kb-data/raw/arxiv/2312.12499/v2/src/main.tex; no run)

- Line 324: Phi = (3/5) R for modes entering in the early matter era. Lines 581-582:
  delta(k, a) = (6/5) (a/a_hor) R_k = (6/5) (a/a_rh) (k^2/H_eq^2) R_k. With the matter-era Poisson
  relation delta = (2/3) (k/calH)^2 Phi (the code's k^2 psi_N = (3/2) delta_N in units calH = 1,
  cosmo/ic/make_field.py:9) and (k/calH(a))^2 = a/a_hor in matter domination, line 324 gives
  delta = (2/5) (a/a_hor) R. So line 581 is three times the line-324 route in delta (nine in the
  power) [VERIFIED as a reading; which line the paper's numbers use is not checked].
- My prediction (a factor two, or a power-spectrum factor) is REFUTED: the factor is three in
  delta itself, as the population helper wrote. DESIGN.md follows line 324 and the code's
  Poisson relation, which is the standard matter-era result [JUDGEMENT]; the factor is a
  literature caveat for the comparison with 2312.12499, to be recorded by kb (request).

## Further checks without runs

- population/results/compare.json: P9 radiated ratio 7.98-18.75 (expected 11.31), near field
  6.14-11.05 (expected 8.0); Layzer-Irvine 4.7e-4 to 8.4e-4 (P7); 25 halos at a = 30 for fid and
  seed 2 (P3): as reported. P5: 11 of 16 matched, mass ratios -23.5 to +14.3 per cent (the report
  says -24 to +12: the upper end is 14.3). Figures pop_compare.png and pop_gw_fid.png looked at:
  they show what the report says; in pop_gw_fid.png (left) the legend lies over the red curve
  and the square labelled "halos of a = 20" sits at a = 30.
- verifier2 (wave 2b): compare.json gives 1.02 per cent at a = 75.8 (eps = 1, 32^3 against 64^3)
  and 1.93 per cent at a = 80 (Gamma driver), the values of its NOT CONFIRMED item 2; the linearity
  rows of the note's ledger (row 94: 0.000497, 0.00213) agree with its item 1.
- note v2: fig_waves.png and fig_r2.png looked at: panels, legends and predicted lines as the
  captions say; in fig_r2 (b, c) the y range reaches 1e3 above data that end near 2 (space, not
  an error). Ledger row 168 gives the spectral Weyl-TT difference 1.22e-11 without saying
  "forward combination"; row 101 gives 0.00821 sampled at the restart cadence (verifier3).

## 2026-11-21T15:50Z lead batch 4a: predictions L4-L7 (written before any run)

Packages under review: first_source round 3 (batch 2b), waves round 1 (batch 3),
stage/G1/verifier_c18 (batch 3). Independent code for L4 and L5 is verifier3's own reader,
TT projector and exact solution (stage/G1/verifier3/scripts/diag.py, exact.py, v3_measure.do_X),
not the waves package's wlib.

- L4 (waves F2, k = 2 pi (1,2,0)). With verifier3's reader and TT projector, the forward
  combination W = c_h + i c_h'/|k| of the TT mode at +k, referred to the first dump
  (amplitude |W_tot(t)|/|W_tot(0)| - 1 with |W_tot|^2 = |W_+|^2 + |W_x|^2, which does not
  depend on the polarization basis; phase arg(W_+(t)/W_+(0)) + |k| t) at the last dump
  (t = 1.78885) equals the waves values of f120_results.json (TT, amp_p_end, phase_p_end) to
  1 per cent at N = 16, 32, 48, 64, and the orders between successive N are within 0.1 of
  6.73/6.80/6.73 (amplitude) and 5.51/5.15/4.83 (phase). Refuted by any value beyond 1 per
  cent (unless below 1e-10 absolute) or an order off by more than 0.1.
- L5 (waves XS, time/space split of X). verifier3's do_X on the last dump (t = 10) of the
  step test at dt_expansion = 0.001 (card run B-20261120-222841-acfe21d, xdt3N16..N64) gives
  the cross-polarization errors of xdt_card_results.json (N = 64: amplitude -3.10e-9, phase
  1.92e-8) to 5 per cent; with verifier3's own e(0.01) at N = 64 (v3_summary.json, TT x:
  1.39888e-7, 2.76239e-7) the time part is 1.430e-7 (amplitude) and 2.570e-7 (phase) to 1 per
  cent. Refuted by a difference beyond these bounds.
- L6 (first_source round 3). The registered analyses conv_compare (B-20261121-075302-a9fcc43)
  and p16_compare at 64^3 (B-20261121-085202-b95efda), rerun from their registered inputs
  with the committed scripts, reproduce their JSON outputs bit for bit (processor, numpy,
  deterministic). Refuted by any differing number.
- L7 (verifier_c18). Its summary a3_summary.py rerun from its committed results reproduces
  run B-20261121-132955-cb150b2 (116 numbers, 103 within 1 per cent, 113 within 5 per cent);
  the line-125 claim (smallest rms ratio 5.48e-5 is the initial slice; evolved dumps 3.8e-3 to
  0.0408) and the line-101 claim (0.00882 over all dumps for eps = 1) are in its result files.
  Refuted by a differing count or a number not found as stated.

## 2026-11-21T15:55Z lead batch 4a: outcomes of L4-L7

- L4 CONFIRMED (run B-20261121-154933-a79da09, lw4_waves.json, figure lw4_waves.png looked
  at). F2 last-dump TT errors with verifier3's code against the waves values: amplitude
  -6.67738e-3, -6.30755e-5, -3.99670e-6, -5.75924e-7 (N = 16-64), relative difference 3.8e-9,
  1.2e-6, 2.5e-5, 2.9e-4; phase 4.32075e-3 ... 2.92636e-6, relative difference <= 1.7e-9.
  Orders 6.726/6.804/6.734 (amplitude) and 5.510/5.154/4.826 (phase): the waves orders to the
  third digit. The cross phase agrees as well (2.92495e-6 at N = 64).
- L5 CONFIRMED (same run). Cross errors at dt_expansion = 0.001, t = 10, with verifier3's
  do_X: N = 64 amplitude -3.10353e-9 (waves -3.10340e-9, 4e-5 relative), phase 1.92010e-8
  (6e-7); N = 16, 32, 48 agree to <= 4e-6. Time part at N = 64 with verifier3's own
  e(0.01): 1.42992e-7 (amplitude), 2.57038e-7 (phase), the waves values 1.4299e-7, 2.5704e-7.
- L6 CONFIRMED (run B-20261121-155017-9aec47a, lw6_rerun.json): conv_compare and
  p16_compare (64^3) rerun from their registered inputs give byte-identical summary JSON
  (142 and 137 values, none differs). Figures r2_conv_eps1.png and r2_p16_nowave_64.png
  looked at: they show what the README says (particle differences ~1e-4 to 2e-4 at all a,
  mesh differences ~1e-4 before a ~ 60 and up to 1e-1 after; TT/non-TT shell ratios near 1
  above |k| L/2pi ~ 10 at a <= 2.3 and not at a = 12.3).
- L7 CONFIRMED (run B-20261121-155045-343bee1): a3_summary.json and a3_summary.png
  byte-identical to run B-20261121-132955-cb150b2; 116 numbers, 103 within 1 per cent, 113
  within 5 per cent. p3_slicing.json: rms_ratio_min 5.48e-5 at a = 1 + 6.5e-9 (first dump of
  pcs4bt), the next dump 3.84e-3, rms_ratio_max 0.0408 for a <= 121: the line-125 claim
  holds as stated. Its figure is not drawn with figstyle (default matplotlib): style defect
  only.
- Small defect fixed: first_source/README.md P13 now states the window (80 <= a <= 140) and
  the interpolation behind 1.3e-2 (verifier_c18 got 1.38e-2 with its own interpolation).

## Batch 5 lead (2026-11-21 12:40 PST): check of verifier_c18b, prediction

Before the check: if verifier_c18b is right, the largest Hr_mean over all cstat records with
22 <= a <= 42 is about 0.0075 (one per cell) and 0.0025 (two per cell), above the printed
0.00706 and 0.00203, which my own reader must reproduce at the records nearest the five dumps;
and the record nearest a = 10 sits at a = 9.96 with the printed 1.58e-4 and 3.22e-5. Refuted
if my maxima over all records equal the printed values (then the verifier misread the window).
Outcome (run B-20261121-203426-ea1e945, figure lb5_line59.png looked at): prediction MET. Over
all 114 records with 22 <= a <= 42 the largest Hr_mean is 0.00751 (a = 22.56, one per cell)
and 0.00254 (a = 23.31, two per cell); at the records nearest the five dumps the largest are
0.00706 and 0.00203, the printed values. Nearest record to a = 10: a = 9.962, 1.576e-4 and
3.216e-5 (interpolated to a = 10.00: 1.641e-4 and 3.607e-5). The verifier's pancake.py and
small_rows.py rerun from the registered outputs give byte-identical JSON files.
