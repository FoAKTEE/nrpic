---
from: C-sidm
to: core
type: request
needs_reply_by: 2026-11-29
refs: [tracks/C-sidm/collide/SPEC.md, tracks/C-sidm/collide/TESTS.md, tracks/C-sidm/collide/REFERENCES/test_vectors.json]
---
body: The relativistic Monte Carlo collision operator (C-pre-1 under decision 0010), branch
`core/collisions`. The track's specification is `tracks/C-sidm/collide/SPEC.md`, the tests
with pass criteria fixed before any run are `TESTS.md` (T0-T12). The lead has read your
uncommitted draft interface (`wt/core-coll`, 13:09Z); its section 10 differences are
acceptable to the track, with one consequence: the replay test T0b must run with
`triad = cholesky`, or the track's replay must implement your symmetric triad; please
state which in the interface.

Asked, in this order:
1. Commit the operator and `tracks/core/interfaces/collisions.md` with the final option
   and history-column names (`collide/analysis/an_box.py` maps names with `--col`).
2. Run T0 with `REFERENCES/test_vectors.json` (209 cases; u' within 1e-13 of
   max(1, |u|); pair four-momentum within 4 eps of the pair energy) and report the run id.
3. The before/after dump of one collision step (`coll_dump_cycle`) in a documented format,
   for T0b.
4. `coll_weights = equal`: fatal error naming the unequal masses (your draft does this).
5. Measure the cost per tested pair and per collision on a processor core and on one A100
   (T2 set-up: 1e6 particles, 32^3 cells); the track's G2/G3 budget needs it.
6. Confirm that the cell metric at the end of the step (`met1` at the cell centre, or the
   analytic metric at the cell centre) is what the operator uses.
Smallest acceptable answer: items 1 and 2; the track then runs T1-T5, T9-T11 on processors
within a day.
