# repro/figs: the figures of arXiv:2512.14649 from our runs (Track E, batch R2)

Status: in progress (2026-11-24). See `JOURNAL.md` (predictions, outcomes), `RESULTS.md` (verdicts),
`CARD_COSTS.md` (actual card costs of the reproduction runs).

## Contents

- `figures/figlib.py`: readers (dumps through `ladder/scripts/ladder_lib.py`, `.modes`, records),
  lattice shells with the hemisphere count, P1's units, own Friedmann integration.
- `figures/dumppass.py`: one pass over the dumps of a run (contrast and constraint percentiles,
  binned spectra of R^NR, K, Kt, sqrt(3 Kt Kt/2), per-shell comparison with the linear reference).
- `figures/bitcheck.py`: bit identity of two dumps in their common variables.
- `figures/runs.py`: the run registry (label -> run id) and the analysis groups.
