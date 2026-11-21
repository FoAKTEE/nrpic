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
