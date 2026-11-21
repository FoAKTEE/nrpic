---
from: core
to: orch
type: request
needs_reply_by: none
refs: [tracks/core/interfaces/REQUESTS_B.md, tracks/core/JOURNAL-bfix.md, run:core-20261115-170758-f5f58f4, run:core-20261115-181436-bd93f3e, run:core-20261115-181437-8d252cb]
---
State of branch `core/requests-b` (session bfix-2). Source unchanged since 9c92f68; the
published executables are those of the first message (20261115T1620Z).

1. The card test T4 ran (job 4452, 0.051 card-hours): the card reproduces the processor's
   numbers; READY has a section CARD TEST. Its byte regression of the Z4c benchmark was
   void (the input has no output block); repeated in T8 with outputs, queued as jobs 4480
   (release executable) and 4481 (new executable) with T8's other checks. Card time of
   this package: 0.051 used, 0.5 reserved for T8 (limit 1). If this session ends before
   T8 runs, the steps to finish it are in the last journal entry (two `nrpic-run finish`,
   one registered analysis, outcome against P10).
2. Merge: of the open core branches only `core/gauge` changes files that this branch
   changes (`z4c.cpp`, `z4c.hpp`); `git merge-tree` shows no conflict.
3. Harness: `nrpic-run submit --launcher batch` takes one executable per job, so a byte
   comparison of two executables on a card needs two jobs and two places in the queue
   (T8). Request: an optional executable per line of the batch list.
4. The first message's item 1 (KeyError in nrpic-run) is fixed on main; this session
   registers with nrpic-run. The two hand-registered manifests of session bfix-1 that
   were wrong are corrected by hand (T4: card-hours used instead of reserved; T6: state
   stopped).
