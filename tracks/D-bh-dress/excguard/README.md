# excguard: core's excision guard on Track D's long deck (G3, first item)

The card test that decision 0045 item 2 puts first in the scope of G3: ES-FL (dust filling the vacuum
bubble around a black hole of mass M, cells of M/8 at the hole) with `<particles> ah_exc_max_growth = 8`
at `initial_radius_0 = 0.8` (guard radius 6.4 M), the converged finder of release core-v0.8
(`polish_iterations_0 = 100`, `mass_tol_0 = 1e-5`, `diagnostics = true`), to 260 M, 40 M past the time
at which ES-FL lost horizon excision (219.5 M).

- Input: `inputs/esflg8.athinput`, written by `tools/make_input.py` from `../g2long/inputs/esfl.athinput`.
- Predictions and refutations: `JOURNAL.md` entry 1 (written before any run).
- Readers: `../g2runs/tools/esf_criteria.py`, `../g2long/tools/d4_timing.py`, `../g2long/tools/fk_compare.py`.
- Comparisons: ES-FL D-20261121-203150-15f2bad, FK D-20261123-022725-a553496, control V-1L (g2long).

Results: none yet (the run is queued; see `JOURNAL.md` and `../HANDOFF.md` for its queue id).
