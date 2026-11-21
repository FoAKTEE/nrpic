# stage/G1/verifier_c18: fresh verifier of G1 item C18 (B-emd-gw)

Independent recomputation, from the raw dumps of the registered runs, of the ledger rows of the
working note (`note/tables/ledger.tex`) that no earlier verifier recomputed, and of the
first_source round-3 results. Report: `../VERIFIER-C18.md`. Predictions and outcomes:
`JOURNAL.md`. Processors only, no card time.

## Contents

- `scripts/vlib.py`: own readers (mesh bin in both precisions, z4c part of restart files), TT
  projection, mode amplitudes, junk solution g(tau), spatial-gauge piece G_tot.
- `scripts/t0_tools.py`: tests of vlib on analytic fields and on pairs of dumps (T0).
- `scripts/m1_measure.py`: per-dump diagnostics of the crossed-wave runs (M1).
- `results/`, `figs/`: copies of summaries and the figures looked at.

## How to rerun

See the run manifests named in `../VERIFIER-C18.md` (each holds its exact command).

## Requests

(filled at the end)
