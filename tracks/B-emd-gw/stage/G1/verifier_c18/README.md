# stage/G1/verifier_c18: fresh verifier of G1 item C18 (B-emd-gw)

Independent recomputation, from the raw dumps of the registered runs, of the ledger lines of the
working note (`note/tables/ledger.tex`) that no earlier verifier recomputed (second-round table,
lines 197-217; spatial gauge, lines 116-125), and of the first_source round-3 results of batch
2b. Report: `../VERIFIER-C18.md` (verdicts per line, comparison with the track's review).
Predictions and outcomes: `JOURNAL.md`. Processors only, no card time.

## Contents

- `scripts/vlib.py`: own readers (mesh bin in both precisions, z4c part of restart files), TT
  projection, box-mode amplitudes, junk solution g(tau), spatial-gauge piece G_tot (note Eq. 9).
- `scripts/t0_tools.py`: tests of vlib on analytic fields and on pairs of dumps (T0).
- `scripts/m1_measure.py`: per-dump diagnostics of the crossed-wave runs (M1; `--light` for
  box modes only, `--gauge` for G_tot).
- `scripts/a1_rows.py`: ledger lines 197, 200, 204, 205, 207-215, 116-123 from the M1 tables.
- `scripts/a2_round3.py`: round 3 (P12, P13, (1 + eps^2), P16').
- `scripts/p1_ic.py`: initial-data files (lines 198, 199) and card-hours (216).
- `scripts/p2_null_pred.py`: own second-order noise prediction (lines 201-203, 206).
- `scripts/p3_slicing.py`: line 125 (slicing of the three-wave runs).
- `results/*.json`: copies of the run outputs; `figs/*.png`: the figures looked at.

## How to rerun

Each run manifest under `tracks/B-emd-gw/runs/<run id>/manifest.json` holds its exact command
(run ids in `../VERIFIER-C18.md` section 1). In order: T0 (B-20261121-130334-a86cff6); M1a, M1b,
M1c, M1d (B-20261121-130345-622e9e4, -130410-0ff2a75, -131318-6a9bad1, -131930-79b125f; about
15 minutes on 2-4 cores each); then A1, A2, P2 with the M1 directories as arguments; P1 and P3
alone. Example:

    harness/bin/nrpic-run submit --kind scouting --gate G1 --package tracks/B-emd-gw/stage/G1/verifier_c18 \
      --cores 2 --purpose "..." -- env OMP_NUM_THREADS=2 python3 \
      tracks/B-emd-gw/stage/G1/verifier_c18/scripts/a1_rows.py <M1a dir> <M1b dir>

## Requests

- To the B-emd-gw lead (note v3): line 125, say that the smallest rms ratio 5.48e-5 is the
  initial slice (evolved dumps a = 12-121: 3.8e-3 to 0.0408); line 101, say that 0.00857 and
  0.00821 are maxima over the double-precision dumps (0.00882 over all dumps for eps = 1; already
  owed per REVIEW-wave3); line 197, quote the floor as about 1e-12 (its second digit depends on
  the summation of the diagnostic).
- To the lead: judge C18 on `../VERIFIER-C18.md`; still not independently recomputed: line 124
  (magnetic Weyl), line 199 (initial-data residuals), line 217, and the wave-1 lines outside the
  G0 claims (26-27, 34-36, 49-63, 70-71). Push track/B-emd-gw (this helper does not push).
