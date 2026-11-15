---
from: E-stoch-inf
to: core
type: request
needs_reply_by: 2026-11-29
refs: [run:E-20261115-135218-bdf4710, tracks/E-stoch-inf/codebase/figs/cost.json]
---
body: The processor build of `core/scalar-field` runs serially at 1.35e4 zone-cycles/s
(run E-20261115-135218-bdf4710), so every test of Track E above 32^3 needs a card. Please
build `core/scalar-field` for the cards (or tell us which commit and build directory to use
read-only) once the initial slice exists. Track E's card plan to G2 at Courant 0.25 is
about 1.5 to 2 card-hours of its 10 (two 256^3 cases at 0.4-0.5 each, the ladder N <= 128,
the temporal test, U9 and the 64^3 x 300 noise base case). Measuring the real overhead of
field, kicks and synthesis on the card (assumed 15 percent and 3e12 flop/s in the
estimate) is the first card run. Smallest acceptable answer: a path to a card executable
and its commit.
