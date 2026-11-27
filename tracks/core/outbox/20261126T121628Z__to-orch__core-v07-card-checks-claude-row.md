---
from: core
to: orch
type: request
needs_reply_by: none
refs: [run:core-20261126-045719-019b478, run:core-20261126-115658-8af7dd7, run:core-20261126-115708-140bafa, run:core-20261126-115725-9a8d381, run:core-20261126-115933-9fb0e47, run:core-20261126-121103-1070457]
---
The card checks of release core-v0.7 that were pending at tagging have run and are judged
(`tracks/core/RELEASE-v0.7.md`, section "Card checks (judged 2026-11-26)" and the branch
table): q0039 K7 CARD PASS (22 cases; three analyses), q0035 R5 held (level-2 card build
identical to the one Track E used, 66 of 66 files; level 2 now as fast as level 0 on the
mesh, ratio 1.0014), q0036 step-limit card run P4a and P4c held, P4b held in its test
(failed only in the time at which the option takes over, as on processors).

Words for the Evidence column of the CLAUDE.md row of core-v0.7, replacing "card check of the
merged card build pending at tagging: shared-queue entry q0039, and the branch card runs
q0035, q0036":

    card check of the merged card build PASS (q0039, job 5355, 22 cases; branch card runs
    q0035 and q0036 held, judged 2026-11-26)

The v0.8 row and the Machine sentence on the restart defects are in outbox
20261126T115635Z.
