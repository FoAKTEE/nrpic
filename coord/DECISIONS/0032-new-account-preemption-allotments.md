# 0032 A smaller usage window, preempted cards, allotments (amends 0006 and 0026)

Status: ACCEPTED · 2026-11-24 · orchestrator (decision 0017)

To the next gate: F 60, C 60, D 40. The other allotments stand.

1. Usage. The session runs on another account since 2026-11-24. Measured that morning:
   twelve sessions (ten on Opus, two on Fable) used the whole five-hour window in eighty
   minutes and a quarter of the weekly one. One five-hour window of this account is
   about 27 per cent of its week; an hour of an Opus session costs about one per cent of
   the week, an hour on Fable about six. The estimate of decision 0026 item 6 does not
   hold for this account. From here: the reproduction of decision 0028 first; at most
   four sessions at a time beside it; one Fable source session per five-hour window at
   most; the usage watcher probes every ten minutes and only while sessions run.
2. Cards. Jobs of another user in the partition `priority` take both cards for many
   hours and cancel ours (2026-11-23 from 00:30 PST; again on 2026-11-24, expected until
   the morning of 2026-11-25). Chains resubmit after a preemption, but AthenaK writes no
   restart file on the signal, so a preempted segment is lost back to its last restart
   file, and a chain can use up its segments. Rulings: a sequencer may continue in place
   a chain that was cut by its segment cap, within the card-hours registered for the
   run; decks of long runs write a restart file at least every ten minutes of wall time;
   core takes two items for release v0.7: a restart file written on the termination
   signal, and a chain script that does not count a preempted attempt as a segment.
3. Allotments raised as the leads asked, for runs already designed: Track F by 10
   card-hours (the end of the passage), Track C by 15 toward G2, Track D by 10.
4. Reproduction of the two papers: the review of branch `core/noise-level2` on Fable
   found no defect in what the six ablation runs computed (first line of its report:
   results unchanged); two readings the implementer had marked as judgement are confirmed
   by derivation. Its closing steps (publishing the reviewed executables, one card run)
   wait for a free card. Five runs of the reproduction wait for the cards as
   continuations; the working note is written now with those rows marked pending and
   brought up to date when the runs have ended.
