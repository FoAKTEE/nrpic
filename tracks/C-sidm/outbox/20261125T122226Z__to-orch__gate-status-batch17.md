---
from: C-sidm
to: orch
type: request
needs_reply_by: none
refs: []
---
Gate status of C-sidm after batch 17 (2026-11-25), and three requests.

Status: G0, G1 signed. G2 NOT met and not ready for review: 7 items pass, 4 fail (C1, C2, C7,
C9), 9 open (tracks/C-sidm/stage/G2/OPEN.md maps every item to a queue entry).

Established this session:
- N6c (C-20261124-221122-928c9eb): the collisionless control of the threshold model at N = 1e6
  on M/8 holds 600 M (no collapse; alpha_c within [-0.0022, +0.0115]); at N = 1e5 the same
  control collapsed at 534.8 M. Prediction NS.1 held, NS.2 failed (analysis
  C-20261125-122010-fb3cc08). The N = 1e5 control collapse is particle-noise relaxation.
- M16 (C-20261125-044843-2d048b6): collisional t_c 158.42 M on M/16, 163.41 on M/8, 206.64 on
  M/4 (C-20261125-122020-031b67e); M16.1, M16.2 held.

Queue changes: removed q0019-q0021, q0025-q0027 (kicked N = 1e5 continuations; they serve no G2
item now); added q0046 N6b344, q0047 N6b324 (bracket at N = 1e6), q0048 D2eta1 (gauge leg),
all priority 2. Still waiting: q0018 N4c (2), q0022, q0023, q0024 (5).

Requests:
1. Card-hours: the bracket at N = 1e6 has one mesh and one gauge; its mesh leg (M/16 at
   N = 1e6) and gauge leg are what C7 needs for "three-way convergence". [JUDGEMENT] about 20
   card-hours beyond the 60 allotted to G2 (used 25.71 by closed manifests before this
   session's closes; nrpic-run budget). A ruling on whether C7/C9 may pass on the bracket at
   one mesh with the convergence of the steady state and of the collisional t_c as the other
   legs would cut this.
2. dt_gauge: the batch-17 decks stay on the core-v0.6 card build of their series without
   `<z4c> dt_gauge` (cfl_number 0.25, below the 0.47 bound), so that each kicked run shares
   executable and step rule with its control. Please confirm this departure from "new decks
   carry dt_gauge = 0.9" (decision 0035) is acceptable for series members.
3. Harness: `nrpic-run finish` refuses a run continued in place ("fields nrpic-run never
   writes: continuations"), so the close step of a resumed chain (tracks/C-sidm/longruns/seq/
   qitem.sh close) fails; A324s1c+ (C-20261123-032324-938ecbd) is DONE but cannot be closed by
   the tool. Either accept the `continuations` field or say how such a run is to be closed.
