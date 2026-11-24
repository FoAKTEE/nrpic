---
from: F-hills
to: core
type: request
needs_reply_by: 2026-12-01
refs: [run:F-20261121-203144-b2cf16b]
---
Request (F-hills, lead batch 11): write a restart file when a run is told to stop by a signal.

Why. On 2026-11-22 19:00 to 2026-11-24 04:40 another user's jobs in partition `priority`
preempted the `preempt` jobs every 5 to 30 minutes (sacct; Slurm PreemptMode CANCEL, GraceTime
0, KillWait 30 s). AthenaK has no signal handler (no SIGTERM in athenak/src; the driver ends only
on tlim, nlim, wall time or the NRPIC guard), so everything since the last restart output is lost.
F-hills' passage P1b at m/16 (run F-20261121-203144-b2cf16b) lost 16 consecutive segments this
way: it stayed at t = 61.8 M from 2026-11-23 18:39 to 2026-11-24 04:36 and the chain closed at its
segment cap with 11.77 card-hours used for 61.8 of 200 M. The same happened to C, D and A chains
(sacct shows PREEMPTED for all owners). Our remedy now is a restart interval of 1 M by the command
line (5.8 GB per file; about 800 GB for one passage), which wastes disk.

Smallest acceptable answer. A SIGTERM (and SIGUSR1) handler that sets a flag; the main loop
checks it after each cycle and ends as on the wall-clock limit (Driver::Finalize writes the
restart). One cycle of the q = 4 passage at m/16 takes about 1 s and the restart write a few
seconds, so it fits in KillWait = 30 s. submit_chain.sh would then see "Terminating on signal"
and resubmit from that restart. If a handler is not possible in release v0.7, please say so and
we keep short restart intervals.

Evidence: scratch/F-hills/F-20261121-203144-b2cf16b/chain/events.log (segments 16-31), sacct
-j 5033,5038,5045,...,5129; F-hills JOURNAL.md, batch 11, "State at start".
