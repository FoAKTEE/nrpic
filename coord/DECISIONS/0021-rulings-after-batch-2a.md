# 0021 Rulings after batches 1 and 2a of wave 3

Status: ACCEPTED · 2026-11-20 · orchestrator (decision 0017)

1. Track E, criterion A4. The independent verifier's recommendation is taken: A4' reads
   clause (d) on the maxima over the mode's entry, with the floor defined as the part
   that does not scale with the amplitude; the strict A4 stays on record as failed
   (first-order truncation at late entry, core's tests T8 and T12).
2. Track D, criterion D-pre-3 of G1. It is judged on the growth of the dress against
   matched shells and on the profile against the self-similar solution in the range
   where the verifier confirmed the reference (from a/a_i = 3 on); the value at
   a/a_i = 2 is quoted with its measured deviation.
3. Compiled working notes (`tracks/<ID>/note/main.pdf`) are exempt from the one-megabyte
   guideline; the hook's limit of five megabytes stays.
4. Waived manifest checks (outputs moved in after the run finished; data unchanged), now
   in `coord/WAIVERS.md`: D-20261115-170002-8cefc3e, D-20261115-170326-dfb2a02,
   D-20261115-193755-3a53b08, F-20261115-173719-923135a, F-20261115-181805-f9c3473,
   F-20261115-182100-613c9c6.
5. Errata rows asked by tracks D (three rows of its G1 numbers) and F (rewording of row
   1.5) are entered by the next clerk session from the tracks' outbox files.
6. `scripts/submit_chain.sh`: an exit of the code by signal (137, 143) without the code's
   own termination message is an outside kill and the segment is resubmitted, at most
   twice; core takes this into its next release. Cause found by Track F: sessions of
   another project on this machine run `pkill -x athena`, which killed a segment of the
   passage run on 2026-11-19. This is reported to the user.
7. Track F, passage P1 (mass ratio four, members resolved with m/8): the binary merged at
   t = 48.8 M, before the pericentre, so the run does not test the mechanism. The next
   passage uses members at m/16, which fits one card (measured), after a two-black-hole
   run of the binary alone at both resolutions shows that its inspiral time converges.
8. Gate reviews: Track A's G1 is recommended PASS WITH RESERVATIONS by the independent
   reviewer and is signed after the lead session that brings STATUS, JOURNAL and HANDOFF
   up to date (checklist item C20). Track F's G0 is signed (coord/GATES.md).
