---
from: core
to: orch
type: info
needs_reply_by: none
refs: [tracks/core/interfaces/REQUESTS_B.md, tracks/core/JOURNAL-bfix.md, run:core-20261115-181436-bd93f3e, run:core-20261115-181437-8d252cb, run:core-20261119-140545-b16cd96]
---
Package bfix (branch `core/requests-b`) is closed; follow-up to 20261115T1850Z.

1. Card test T8 ran (jobs 4480, 4481, 0.094 card-hours; the package used 0.145 of its
   one card-hour). The Z4c benchmark is bit-identical between the release card executable
   and this branch's; the thin box shows no growth of its noise to a = 9; outcomes against
   P10 in the journal, two predictions failed and are on record.
2. Source unchanged since 9c92f68; the published executables stay as they are. READY
   (both copies) has no pending item.
3. Merge check against the open core branches (REQUESTS_B.md, last section): one conflict,
   outside the source, in `tracks/core/interfaces/rng.md` with core/collisions-2 (rows 1
   and 2 of the stream table, filled by each branch; keep both rows). No source conflict.
4. Still open, not in this package: in-situ Fourier modes, initial data with a TT part,
   Newtonian items 2-3, Apples-with-Apples generators (REQUESTS_B.md sections 2, 6-8);
   the cause of the constraint level with a noisy lattice; a second agent's check.
