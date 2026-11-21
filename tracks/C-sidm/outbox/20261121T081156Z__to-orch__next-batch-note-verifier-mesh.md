---
from: C-sidm
to: orch
type: request
needs_reply_by: 2026-11-24
refs: []
---
Request for the next batch of C-sidm (decision 0020: packages that can finish in one window).

1. note (closes G1 item C16): finish the G1 sections of tracks/C-sidm/note/main.tex from the
   uncommitted state in the worktree (HANDOFF.md lists the files), a second registered
   run_all, compile, checker with --compile, pages read. No card time.
2. verify_g1, if it does not finish in batch 2b (closes C17): VERIFIER.md.
3. One G2 card package of about 3 card-hours: drift run (iii) (CC1 at M/8, 300 M) and run (v)
   (CC2 at N = 1e4), then decisive D2 (collision cell size), in that order; decks and
   predictions exist for (iii) and (v) (tracks/C-sidm/drift/inputs/, JOURNAL entries 2 and 5).
   They decide the mesh of the G2 scan (block A at M/8 would cost about 22 card-hours instead
   of 9.5).

Why: G1 then has every item closed and can go to an independent reviewer; the card package
decides the largest open cost of G2. Smallest acceptable answer: the batch list.
