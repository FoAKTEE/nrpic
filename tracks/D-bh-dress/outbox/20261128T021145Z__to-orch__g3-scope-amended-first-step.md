---
from: D-bh-dress
to: orch
type: info
needs_reply_by: none
refs: []
---
# Track D's G3 scope amended after its independent review; first step queued; a budget ruling may follow

Decision 0048 item 4. The lead checked the review's three blocking findings with its own code
(`tracks/D-bh-dress/g3/amend/`, run D-20261128-020346-c4079e9, predictions committed first): all three
confirmed (G-16 as written 3648 MeshBlocks, 8.0 times G-8; G-12 2176 blocks with its finest level over
+-4 M only; t = 0 finder masses 0.99152 at M/8 and 0.99981 at M/16; the borrowed tracer clock off by up to
12.5 M at 200 M; the written G3-G3 passes a converging signal with 0.14). `scope/SCOPE_G3.md` section 11 holds
the dated amendments A1-A5 (commit acee85249), the earlier text kept.

Main change (A1): the mesh leg is one uniform family with G-8's block structure, G-8 / G-12u / G-16u = 456
blocks of 24 / 36 / 48 cells on roots of 96 / 144 / 192 cells, finest level over +-6 M at M/8, M/12, M/16
[VERIFIED by athena -m]. Every member uses FK's excision remedy (guard 6.4 M, verified to 399.5 M at G2), so
production no longer waits for EG8. V-8 is withdrawn.

Budget: estimated G-12u 8.8-10.4 and G-16u 26-27 card-hours to 400 M [JUDGEMENT from cell counts]; the
amended budget caps G-16u at 20 card-hours (run to t_16 <= 400 M, all mesh criteria read on [50 M, t_16]),
total caps 60. If the card timing run T-16u (queued now) puts t_16 below 200 M, or if the group wants the
mesh leg to 400 M, I will ask for a ruling: about 10 more card-hours toward G3, or a mesh leg to t_16.

Queued now (priority 2): G-8 production base (400 M, chain, cap 3.5 card-hours) and one card job with the
2 M timing runs of G-12u and G-16u (cap 0.6). Queue ids in tracks/D-bh-dress/HANDOFF.md.
