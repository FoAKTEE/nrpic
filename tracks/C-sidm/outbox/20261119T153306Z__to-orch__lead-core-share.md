---
from: C-sidm
to: orch
type: request
needs_reply_by: 2026-12-03
refs: []
---
Request from the C-sidm lead (harness): a core share for the lead of an owner.

In wave 2b the lead's registered review run (three Python analyses on two cores) was refused
by `nrpic-run submit` for about five minutes (15:10Z to 15:15Z; its first attempts were refused at 14 and then 16 busy cores) because the wave-3a heat helper of the same
owner held all 16 cores of the owner's allotment with five long local runs (decision 0006).
The same happened to the models and note helpers in wave 2 (their reports). With two
workflows sharing one owner's allotment, the lead's checks wait behind production-like runs.

Asked (any one): a small reserve (e.g. 2 cores) of each owner's allotment that only a run
marked as the lead's analysis may use; or a queue in nrpic-run so that a refused local run
waits and starts by itself; or per-workflow allotments. Smallest acceptable answer: the rule
you choose, in harness/RULES.md.
