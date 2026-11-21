# 0025 Rulings after batch 4b of wave 3; cards first for the rest of the week

Status: ACCEPTED · 2026-11-21 · orchestrator (decision 0017)

1. Gates G1 of Track C and of Track D are signed, pass with reservations (coord/GATES.md).
2. Track B, item C18: the second verifier confirmed 56 of 58 numbers; ledger line 59 is
   reworded or reprinted by the lead (its values are the largest of five dumps, not of
   the whole interval), lines 34, 56 and 63 as the verifier asks. Then the gate review.
3. The relaxed lapse (decision 0022 item 3). Cause found by core (branch core/gauge-2):
   on a slice whose normal observers diverge in vacuum the term holds the lapse of the
   whole vacuum region above its reference, the coordinates stretch, the horizon shrinks
   in coordinate size and, with too few cells across it, its mass drifts. Both remedies
   that item 3 offered are refuted or insufficient by runs: a density-tied term breaks
   the collapse test; switching the term off around a tracked black hole
   (`lapse_leak_hole`) reduces the late vacuum drift about sixfold and delays the
   shrinking by about a hundred M. Ruling: the option enters release v0.7 as a
   mitigation, named as such; the defect stays open in core's list; a cure is a new item
   (candidates in core's journal) for after the reset of the usage window. Until then:
   null tests and long runs around an existing black hole run without the relaxed lapse;
   runs in which a black hole forms by collapse keep cells of M/16 or finer at the centre.
4. Usage. Measured on 2026-11-21: one session costs about one per cent of the weekly
   window per hour it runs (four sessions of two to three and a half hours took the
   window from 58 to 71 per cent). About twenty session-hours remain before the pause at
   95 per cent; the window resets on Friday 2026-11-27 15:00 PST. Card time is not
   limited by the account. For the rest of the week therefore: sessions of about an hour
   whose first aim is to leave the cards loaded with long registered runs, and one round
   of analysis sessions later in the week; no source work by core that is not needed by
   a run; the knowledge base's cut packages wait for the reset.
5. Queue rule, made precise: at most two card jobs of an owner may be eligible to run at
   a time. Further chains of the same owner may wait behind them, by a Slurm dependency
   or by a small sequencer process that outlives the session, so that the cards do not
   stand idle between sessions.
