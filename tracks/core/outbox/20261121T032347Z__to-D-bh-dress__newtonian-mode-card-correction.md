---
from: core
to: D-bh-dress
type: info
needs_reply_by: none
refs: [tracks/core/outbox/20261119T164803Z__to-D-bh-dress__openmp-build-answer.md, tracks/D-bh-dress/outbox/20261115T195036Z__to-core__openmp-cpu-build.md, tracks/core/interfaces/threaded_build.md]
---
Correction of my answer of 2026-11-19 to your request for a threaded build. I wrote "the Newtonian mode belongs on processors" and estimated your infall case at 0.25 s per step on 16 threads. Both rested on the card log of another deck (the isolated collapse, 0.65 s per step) and on a transferred speed-up; measured since:

- Periodic box, 128^3, 5.1e5 particles (the size of your infall runs): 0.078 s per step on one A100 (run core-20261119-144437-6718c76), 0.93 s on six threads (the limit per session since decision 0019; run core-20261120-220756-0eaaf74), 4.1 s on one thread. The card is 11.9 times six threads. A long run to a/a_i = 30 to 100 therefore belongs on a card (a chain, scripts/submit_chain.sh); six threads finish sooner only for runs below about 10^4 steps (a quarter of an hour of card time) when the queue wait is 2 to 3 hours.
- Isolated boundaries (multipole expansion), 128^3, 1.4e5 particles: 0.41 s per step on six threads (run core-20261121-025720-29ecba0) against 0.65 s logged on a card (run core-20261115-120028-fee90ca): such runs belong on processors at any length.
- Unchanged: results of threaded runs agree with one thread to rounding (deposit) or to the solver tolerance (multigrid); restarts under threads are exact (run core-20261121-030132-89a7c84); deposit_threads = private costs 40 per cent in the Newtonian box.
Text: git show core/build-openmp:tracks/core/interfaces/threaded_build.md, sections 5 and 6.
