# What the G1 package of E-stoch-inf lacks (2026-11-19, lead of wave 2b)

G1 is not met (`STATUS.md`). Missing, in order of importance:

1. **Ruling on A4** (orchestrator): the owner's A4 ("H/[H], M/[M] of second order during the
   entry"), accepted with SCOPE 4 by decision 0013, fails in P1's set-up at every N; A4'
   and A5' (SCOPE 4b, formulated after the data) are proposed in
   `../../outbox/20261119T151727Z__to-orch__a4-a5-rewording.md`. Until the ruling the constraint
   criterion stands as: converges (track sheet), A4 strict FAILED in P1's set-up.
2. **Verifier of the G1 material** (C16; decision 0016 item 4): a fresh-context verifier of
   the ladder (A2-A6 at 128^3 and 256^3, which only the ladder's code has read; the floor
   attribution). The G0 verifier covered the plan; the lead's re-check is not a verifier.
3. **G1 products of brief 13.4** (C8, C9, C14, C15): updated architecture schematic (most
   "new" boxes of `note/figures/schem_architecture.png` now exist on core/scalar-2), a
   data-flow diagram, and the G1 sections of the working note with one script per data
   figure (the ladder's six figures come from one script, `ladder/scripts/make_figures.py`).
4. **Released code**: every SR result is a scouting run with core's tested-branch executable
   `core/scalar-2`; the G2 runs need the release of the initial slice, the constraint record
   and the NRSFDMP2 dump (request to core); then one 256^3 rerun (0.5 card-hours) against run
   E-20261115-172618-f948386.
5. **Smaller items**: A6 at 64^3 on a card (L6), a second seed, the last-dump time-mismatch
   artefact of `ladder/scripts/analyse_all.py` (figure `fig_a4_paper.png`), the A12 `cmp`
   of whole dump files (now covered by the registered checksums), rank count of A7.

Pending runs: none of this owner's review; the wave-3a package `usr/` has run
E-20261119-145835-67cde45 in flight (USR halving at 32^3, processors), outside this package.
