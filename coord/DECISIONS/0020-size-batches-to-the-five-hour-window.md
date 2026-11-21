# 0020 Batches are sized to the five-hour window

Status: ACCEPTED · 2026-11-20 · orchestrator

Measured on 2026-11-20: wave 3 started about 51 agents at 14:00 PST. The account's
five-hour usage window went from 3 to 97 per cent in 33 minutes (the weekly window from
51 to 76), while most agents were still reading in. The pause flag was written at 14:33
(five-hour window, reset 18:50 PST); with three points left most agents were cut at the
limit instead of winding down.

What follows:
1. On one account the five-hour window sets the throughput, not the number of agents:
   that window is about a quarter of the weekly one, and one agent uses nearly two per
   cent of it in its first half hour. About a dozen packages can be carried to their end
   in one window [JUDGEMENT from this one measurement]; about four windows fit in a week.
2. More agents than that do not add work: they are cut in the middle and pay the
   reading-in again after the reset. So from now on one batch per five-hour window, at
   most about twelve agents, each on a package it can finish, in this order: the merge of
   core's wave-2 branches and its release clerk; core's packages closest to completion;
   then the tracks' packages nearest a gate (one round, at most three helpers, one or two
   owners per window).
3. Pause thresholds: 80 per cent of the five-hour window (so that agents can still wind
   down), 95 per cent of the weekly window (user instruction, decision 0018).
4. More throughput needs more accounts at the same time: a second session signed in to
   another account can drive other owners with the same scripts (each owner has its own
   worktree and branch, so sessions do not collide).

## Amendment after batch 1 (2026-11-20 22:30 PST)

Batch 1 (thirteen sessions, 18:53 to 22:25 PST) finished with every session returning:
it took the five-hour window from 0 to 50 per cent and the weekly window from 0 to 13
per cent. So one window carries about twenty sessions to the end of their packages, not
twelve, and a week about ninety. Half of a session's use falls in its first half hour.
Batches are sized to about eighteen sessions per window from now on, and a session that
is started late in a window counts against the next one for most of its work.

