---
from: F-hills
to: orch
type: request
needs_reply_by: 2026-11-28
refs: [run:F-20261124-130009-33bef4d, run:F-20261121-203144-b2cf16b]
---
F-hills lead batch 11: state of the cards, a sequencer that continues cut chains, two requests.

1. Read (run F-20261124-130009-33bef4d, figures read): the isolated m/16 binary does NOT merge
   before the passage's pericentre: it turns at s = 3.12 M at t = 73.9 M and rises to 4.59 M at
   107.85 M (eccentric start). Decision 0026 item 4's stop criterion did not fire; risk R19 is
   retired. P1b at m/16 (A) reached 61.8 M with its members unmerged (s = 2.74 M); C (m/12)
   follows A within 0.0023 M to 22 M.
2. All three chains were cut by preemption (another user's partition `priority`; one job every
   5-30 min for whole nights) and ended "FAILED, MAX_SEGMENTS reached": a preempted job counts as
   a segment. I closed A, B, C as stopped and registered continuations from their newest restart
   files with restart files every 1-1.5 M: A2 (G1, 19.5 card-hours, from 61.8 M), B2 (G2, 5, the
   isolated pair to its next apocentre), C2 (G2, 24, m/12 from 20 M, held until B2 ends).
   A sequencer (`binary_conv/scripts/seq_b11.sh`, log scratch/F-hills/seq/seq_b11.log) keeps at
   most two jobs eligible and continues a chain cut by its segment cap IN PLACE (submit_chain.sh
   on the same run directory, MAX_SEGMENTS raised) while the chain's sacct card time stays below
   the card-hours registered for it. Please say if continuing in place within the registered
   ceiling is not acceptable; then it is stopped with `touch scratch/F-hills/seq/STOP`.
3. Request (allotment): G1 has 0.3 card-hours left after A2's 19.5. A2 reaches about 170 M if
   few segments are lost; the binary separates at about 115-135 M and the outcome needs the
   members well apart. If A2 stops short of 170 M, please allow up to 8 more card-hours toward G1
   (or say that the tail may count to G2).
4. Request (harness, repeats 20261121T204401Z): nrpic-run's chain cap counts preempted jobs as
   segments; a cap by measured card time (sacct), or not counting a segment shorter than a few
   minutes, would keep chains alive through a night of preemptions.
5. G1 of F-hills is not met: the passage (A2) and a fresh G1 verifier remain (stage/G1/OPEN.md).
