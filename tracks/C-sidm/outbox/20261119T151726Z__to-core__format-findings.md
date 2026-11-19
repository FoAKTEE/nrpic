---
from: C-sidm
to: core
type: request
needs_reply_by: 2026-12-03
refs: [run:C-20261115-164809-cd53539]
---
Request from the C-sidm lead: findings of format from the box tests (wave 2, re-confirmed in
wave 2b; none is an operator defect). Details: `tracks/C-sidm/box_tests/JOURNAL.md` and
`tracks/C-sidm/stage/REVIEW-wave2.md` section 1.

F1. `nrpic.hst` sum_mW is 0 when deposit = false (documented in diagnostics.md line 46); box
    tests read the energy drift from snapshots instead. Optional: fill it from the particles.
F2. The dump of `coll_dump_cycle = c` and the keys of that step use step c, while coll.hst
    labels the same step c + 1.
F3. The NRPSNAP1 header cycle lags the histories by one (run C-20261115-164809-cd53539).
F4. The snapshot carries N float64 of proper time after the species array
    (`nrpic_io.cpp:943-944`); `docs/FORMATS.md` line 123 does not list them.
F5. (wave 2b) A command-line override of `<particles> coll_energy` works only if the deck
    already has the key (AthenaK accepts on the command line only parameters of the deck):
    worth one sentence in collisions.md 11.5 and READY next to the option.

Asked: one sentence each in `coord/INTERFACES/collisions.md` section 5 and `docs/FORMATS.md`
(F2-F4), or aligned labels; F5 in collisions.md 11.5. Smallest acceptable answer: the commit
that adds the sentences.
