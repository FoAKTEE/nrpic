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
