# 0035 Rulings after batch 13; release v0.7

Status: ACCEPTED · 2026-11-24 · orchestrator (decision 0017)

1. The reproduction of arXiv:2512.14649 and arXiv:2401.08530 is complete (decision 0028;
   `coord/digests/reproduction-state.md`). The reproduction note
   `tracks/E-stoch-inf/repro/note/` also carries the G2 sections of Track E: the track's
   older note points to it. Track E's G2 package gets a fresh verifier for the criteria
   of its scope section 4c, which the reproduction's verifier did not cover.
2. Step limit (amends decision 0027 item 2). Core derived the gauge sector's bounds and
   bracketed them by runs of the code: 0.47 of a cell in flat space with the 1+log lapse,
   0.55 with a frozen or harmonic lapse, 0.56 on Track A's expanding root mesh. The rule
   "0.6 or below" was too weak in flat space; CLAUDE.md now says 0.45. The option `<z4c>
   dt_gauge` (off when absent) keeps the step below the bound; a start-up warning is on
   for everybody.
3. Preempted runs (decision 0032 item 2). On the termination signal AthenaK now finishes
   its cycle, writes its restart outputs and exits; a 256-cell restart file is written in
   about three seconds against the thirty seconds Slurm allows here. The chain script no
   longer counts an attempt cut by a signal as a segment and queues nothing after the
   last one. Two older restart defects found on the way go to core's open list (a record
   of the constraint history lost at a continuation; the mesh history header repeated).
4. Release core-v0.7 is merged now from `core/noise-level2` (reviewed on Fable),
   `core/step-limit`, `core/gauge-2` (the mitigation of the relaxed lapse, named as such)
   and, if closed, `core/clump-table`. The cards have been held by another partition for
   most of two days, so the card checks of the merged build are handed to the shared
   queue and the release is tagged with those checks named as pending, as release v0.6
   was.
5. Knowledge base: the brief's seeds 806, 807, 810, 811 and 812 (bibliographic and
   tooling items) do not bear on gate G1 of any track. arXiv:0707.4654 and
   arXiv:1006.1632, on disk but in no manifest, leave the downloads table; their files
   stay. A claims package and then a fresh verifier for KB-G3 follow.
