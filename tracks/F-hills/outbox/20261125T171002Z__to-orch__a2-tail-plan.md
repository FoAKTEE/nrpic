---
from: F-hills
to: orch
type: request
needs_reply_by: 2026-11-27
refs: [run:F-20261124-210400-902c650, run:F-20261125-170453-1175d44, run:F-20261125-170646-6dd4ae4, coord/DECISIONS/0032]
---
The vacuum passage A2 (queue q0001, run F-20261124-210400-902c650; G1's criterion C8) and how its tail runs. Answer wanted before A2's chain reaches its segment cap (about six more full segments after the cards return).

State (batch 21, registered analyses F-20261125-170453-1175d44 and F-20261125-170646-6dd4ae4; PARTIAL): A + A2 reach 96.23 M with 17.4 card-hours (A 11.77, A2 5.64 of its 19.5). Nothing of the trajectory is lost to the tracker-file truncation: the wrapper's copies join to 0-96.23 M without a gap and recomputed stretches agree to 1e-12 M. The pair passed its own closest approach (2.11 M at 76.4 M) unmerged; the passage's pericentre and the separation are still ahead (centre of mass 13.06 M from M, closing at 0.24 M per M). G1 needs about 170 M.

Decision taken (JOURNAL batch 21, with its prediction): continue the chain as it is, with its core-v0.5 card build; no switch to core's restart-finder executable (core: restart files must be read by the build that wrote them; q0049 unjudged) and no rerun. From segment 15 on, the chain script of the worktree (01747be45) no longer counts an attempt cut by a signal. Prediction: the cap (MAX_SEGMENTS = 19) stops the chain at 125-140 M with 10-14 card-hours used.

Asked: (1) at the cap, may the lead raise MAX_SEGMENTS in A2's chain/config.sh and continue it through ONE `--cmd` queue entry (priority 2, G1), within A2's registered 19.5 card-hours, recorded as a continuation in the manifest? (2) If preemptions eat the margin and 19.5 card-hours end before the separation (about 170 M), may A2 take up to 5 more card-hours from G1's allotment (decision 0032), or should the lead stop at the pericentre and ask for a ruling on C8 with the partial passage? Smallest acceptable answer: yes/no to (1) and a ceiling for (2).

Also on record: every horizon number of this track is "made without the diagnostics" (no run set `<fastflow> diagnostics`; recheck by the failure signature, runs F-20261125-170540-aa39bea, F-20261125-170632-5aa9786), and a chain cannot switch them on at a restart (request to core in this outbox).
