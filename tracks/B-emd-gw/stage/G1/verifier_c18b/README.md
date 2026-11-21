# stage/G1/verifier_c18b: second verifier of G1 item C18 (B-emd-gw)

Second independent recomputation (decision 0023 item 2) of the ledger rows of the working
note that had no independent value: lines 34-36, 49-63, 70-71, 124, 199, 217 of
`tracks/B-emd-gw/note/tables/ledger.tex`. Report with the verdict per row:
`tracks/B-emd-gw/stage/G1/VERIFIER-C18b.md`. Predictions and outcomes: `JOURNAL.md`.
Processors only, 0 card-hours.

Result: 58 numbers on 22 lines; 56 CONFIRMED; line 59 (two numbers) NOT CONFIRMED as worded
(they are the largest of five dump epochs, not the largest over a = 22-42: 0.00751 and 0.00254);
none WRONG. Qualifications on lines 34, 56, 63, 124, 199 in the report, section 3.

## Contents

| path | what |
|---|---|
| `scripts/pancake.py` | lines 49-60: own readers of trajectories, snapshots, cstat.hst, NRFIELD2 dumps and newton.npz; crossings, departures at a = 10, constraint means, plane symmetry; figure |
| `scripts/small_rows.py` | lines 34-36 (virial frequency, cost from the AthenaK logs), 61 (sacct), 63 (homogeneous runs), 70 (ellipsoid energy, mpmath at 50 digits), 71 (second-order lapse); figure |
| `scripts/residuals.py` | line 199: own PCS deposit, the code's compensation pass, spectral constraint residuals of the jittered initial data, interpolation sensitivity, Nyquist-plane share; figure |
| `scripts/weyl.py` | line 124: own restart reader (checked against the t = 0 field dump and det/trace identities), full nonlinear magnetic Weyl part (checked on an analytic TT wave), gauge medians; figure |
| `scripts/r2second.py` | line 217: own third reduction of the 30 compared numbers from the per-dump case files, against the comparison files and the printed values; figure |
| `scripts/figstyle.py` | copy of `python/nrpic/figstyle.py` |
| `results/*.json` | copies of the JSON outputs of the registered runs below |
| `figs/*.png` | copies of the figures (each looked at) |

Registered runs (manifests in `tracks/B-emd-gw/runs/<id>/`, outputs in `scratch/B-emd-gw/<id>/`):
B-20261121-165713-459347e (superseded first pancake pass), B-20261121-170003-23f500e (pancake),
B-20261121-170159-535438f (small rows), B-20261121-170611-c616c57 (residuals),
B-20261121-171152-4241a93 (Weyl), B-20261121-171519-ad8f227 (second reading).

## How to rerun

From the worktree root, with the worktree's `.venv` (numpy, scipy, matplotlib, mpmath):

    harness/bin/nrpic-run submit --kind scouting --gate G1 --launcher local --cores 1 \
      --package tracks/B-emd-gw/stage/G1/verifier_c18b --purpose "..." -- \
      bash -c 'OMP_NUM_THREADS=1 python3 tracks/B-emd-gw/stage/G1/verifier_c18b/scripts/pancake.py "$NRPIC_RUN_DIR"'

and the same for `small_rows.py`, `residuals.py` (2 cores, ~1 min, reads 3 x 145 MB),
`weyl.py` (4 cores, ~6 min, reads 46 restart files of 90 MB) and `r2second.py`. Inputs are
the raw outputs under `scratch/B-emd-gw/` and `runs/cosmo/` named at the top of each script;
`small_rows.py` calls `sacct` for jobs 4373 and 4388.

## Requests

- To the B lead (note v3, not to other owners): reword or recompute ledger line 59; optionally
  state the sampling of lines 34 and 56; list the cstat.hst of `runs/cosmo/dtexp_test/lim`
  (sha256 ed6353a8...) among the checksummed inputs of the run behind line 63.
- Not done here and still open for C18 if the lead wants them: the round-3 items P16'
  per-shell fractions and P16'(v), which are not ledger rows.
