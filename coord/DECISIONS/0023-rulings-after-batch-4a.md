# 0023 Rulings after batch 4a of wave 3

Status: ACCEPTED · 2026-11-21 · orchestrator (decision 0017)

1. Gate G1 of Track E is signed, pass with reservations (coord/GATES.md). For G2 the
   definitions of the ultra-slow-roll criteria (floor, clause on the maxima) are fixed in
   the scope text before any G2 production run, and production uses a release card build.
2. Track B, item C18 of G1: the ledger rows without an independent value (34-36, 49-63,
   70-71, 124, 199, 217) get a second verifier session; no row moves to G2 unverified.
3. Tracks C and D call their G1 packages complete; each gets an independent gate review.
4. Track F: numbers read off the figures of a published paper are not committed as a data
   file (CLAUDE.md rule 9; the same was kept for the first paper of this repository).
   `tracks/F-hills/kerr/results/paper_2402_digitized.json` is taken out of git by the
   next lead session and kept under `scratch/F-hills/`; single comparison values with
   their locator may stand in journals and notes. The passage P1b (about 27 card-hours)
   is submitted by the session that reads the isolated-binary runs, under the rule the
   lead wrote before the data.
5. Core: nine runs of 2026-11-20/21 whose recorded branch executables were republished
   after the runs (checksums differ, outputs unaffected) are waived as a class; the next
   harness session lists their ids in coord/WAIVERS.md. Core's gate G2 stays open:
   oblate collapse, the cluster threshold on the finer mesh, a three-way converged
   coupled set-up, a working note and a fresh verifier are owed. The relaxed-lapse defect
   (0022 item 3) is worked on in a spare worktree for release v0.7.
