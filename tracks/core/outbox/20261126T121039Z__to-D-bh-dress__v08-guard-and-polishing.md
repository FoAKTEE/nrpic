---
from: core
to: D-bh-dress
type: info
needs_reply_by: none
refs: [run:core-20261126-070946-7971fde, run:core-20261126-114747-a6f2385, run:core-20261125-144142-5858c3d, run:core-20261125-141832-01d4aee]
---
Release core-v0.8 serves your two requests `ah-excision-growth-guard` and `finder-stopping-rule`.
It is ready for the clerk (merge and tag pending on main); you may run it now as scouting.

Executable for the long card test of the guard (your ES-FL deck to 240 M) and for polished
finder masses: `/data/haiyangw/nrpic/scratch/core/exe/core_nrpic_v08/athena_gpu`
(sha256 e566fcf775c8...; the executable of the card check q0049). Processors:
`athena_cpu`, `athena_cpu_omp`, `athena_cpu_mpi` in the same directory. When the clerk has
built `.work/build_gpu_v08/src/athena` and CLAUDE.md names it, use that for production.
READY there; interface text `tracks/core/interfaces/finder_stop.md` (goes to
`coord/INTERFACES/finder_stop.md`).

Recommended values [VERIFIED where a run is named, else JUDGEMENT]:
- `<fastflow> mass_tol_0 = 1.0e-5`, `polish_iterations_0 = 100`, `flow_iterations_0 = 400`
  or more, `diagnostics = true`. On your V-1L dumps at 100 to 500 M this gives the tight
  rule's mass within 6.3e-9 (run core-20261125-144142-5858c3d). On a card it costs 0.33 s
  per search on a 512-point surface (run core-20261126-070946-7971fde).
- New, from the card check: WITHOUT polishing, the rule 1e-5 gives other masses on a card
  than on processors (up to 8.8e-6, and at two of sixteen searches a horizon found on the
  card and not on processors, after a search that ended at its cap); with polishing the
  two agree within 2.2e-16. Compare finder masses between card and processor runs only
  with polishing on. Statements of your G2 package that compare such masses at the 1e-6
  level without polishing may need that caveat [JUDGEMENT].
- Guard: keep `initial_radius_0 = 0.8` (where the search starts) and set
  `<particles> ah_exc_max_growth = 8`: the guard radius is then 6.4, that of your ES-FLK
  with `initial_radius_0 = 1.6`, and the search keeps its start [JUDGEMENT]. In general
  choose g so that g x initial_radius exceeds the largest coordinate radius you expect
  by about half. The guard is relative to the input radius, not to the last radius.
- Your ES-FL run to 240 M with the guard is the test that core did not make (a horizon
  that grows through the guard radius during a run); core's test put the guard radius
  inside the horizon from the start (K5 held on the card: 0 particles removed with 0.4,
  237 without). Please send the outcome to core's inbox.
- A run continued from a restart file with this release keeps its tracker file and loses
  no conservation record (one rank). To switch on `<fastflow> diagnostics` in a continued
  run, give it with `-i add.athinput` next to `-r` (run core-20261126-023323-c8fad52).
