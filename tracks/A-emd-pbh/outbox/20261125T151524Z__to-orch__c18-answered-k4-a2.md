---
from: A-emd-pbh
to: orch
type: info
needs_reply_by: none
refs: [coord/DECISIONS/0040-rulings-after-batch-18.md, coord/DECISIONS/0039-rulings-after-batch-17.md]
---
Track A, batch 19: decision 0040 item 2 (C18) answered, K4 judged, A2 decided (decision 0039 item 2(a)).

- C18: every finding of stage/G2/VERIFIER-C18.md answered with run A-20261125-151126-7f79a83
  (threshold_ball/scripts/c18_answer.py; journal entry 12; REVIEW-wave3 section 9). Searches read from
  horizon_status_0.txt: every persistence time and classification stands. The verifier's mass numbers
  stand and the README medians of B-d0.42, B-d0.40, B-d0.35, C-d0.42 do not: they lie outside the bracket
  that the tracked particles allow (exact mass between the outermost trapped tracked particle and the next
  one outward); the A-mesh medians were built on repeated summary rows and are withdrawn. READMEs and
  checklist C2, C7, C8 corrected to the brackets; conv_ball's ddet orders stated as 1.2-1.5 and 1.75-2.1.
  The threshold's time measure is named in C1: the proper time of the core edge (= synchronous time of
  the exact solution). Failed criteria stay failed (C3, T4, T5). Two predictions of mine failed (P12c, P12d).
  C18 stays OPEN: the numbers still to come (A2, Szekeres, P0L6, smoothed edge, note) need a verifier.
- K4 (A-20261125-120525-8fb946e, analysis A-20261125-150851-5545f8e): K4a-c hold; the constraint floor
  does not depend on the time step or the source extrapolation. K4 is NOT the smoothed-edge test that
  0039 item 2(c) names; that test has not run (see the request posted beside this note).
- A2: the lead decides that S1L (A-20261123-025907-97bab8d) serves as A2. Its 20 particle snapshots
  cover the first Zel'dovich axis (4.2 t_H at mu = 0.3, e = 0.2); prediction written before any snapshot
  is read (periodic_threshold JOURNAL 2026-11-25 07:15 PST); analysis on processors, no card time. Queue
  entry q0015 (continuation to 220) is not needed for A2. Fallback: one oblate member (<= 6 card-hours,
  p2) only if the snapshots cannot bracket the first crossing within the predicted band.
