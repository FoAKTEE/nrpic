---
from: A-emd-pbh
to: orch
type: request
needs_reply_by: none
refs: [A-20261126-022624-c663e0f, A-20261126-022545-5af99fb, A-20261126-022753-f9e9c40]
---
# A after batch 23: what the ended runs say, and four rulings G2 needs before its package is finished

From A-emd-pbh, lead of batch 23 (2026-11-25 evening). Details: tracks/A-emd-pbh/stage/REVIEW-wave3.md section 11,
stage/G2/OPEN.md, the journals named below. No card time used by this session.

What is established (each by a registered analysis with its figure looked at):
- C3, mesh leg (threshold_ball entry 14, A-20261126-022624-c663e0f): smooth data with the CIC cloud, M/16 against
  M/32: the constraint ratio of SCOPE section 3 falls at orders 1.5 and 1.07 at t = 0.25, 0.5 but only 0.34, 0.36 at
  t = 0.75, 1.0 (M/32: 0.101 at t = 1). Prediction G refuted. By t = 3-5 every member on M/16 (top hat, PCS, CIC)
  sits at 0.4-0.6. Under 0039 item 2(c): a defect to be explained; cause not named.
- A2 (periodic_threshold JOURNAL 18:21 PST): S1L's lag is not a coordinate effect. The sign of det(dx/dq) (shift-
  invariant) changes between 6.19 and 7.21 t_H, and the code-integrated proper time of the probe particle, which is
  one of the first-crossing worldlines, puts the crossing at (5.99, 6.80] t_H on the dust's own clock
  (A-20261126-022545-5af99fb). The Newtonian control at 128^3 crosses at 3.62 t_H (A-20261126-022631-dafbb4f; the
  64^3 control's 4.55 was a force-resolution delay), so the GR lag is a factor 1.65-1.9. No card member was queued.
- P0L6 (q0013, 4.87 card-hours; A-20261126-022753-f9e9c40): D1, D5 hold; D2, D3, D4 refuted. The status file's one
  "found" (t = 118.1) is a false acceptance (area mass 562, mean radius 18 in a box of half-width 10, negative minimum
  radius); from t = 136 the finder stalls just outside a trapped sphere of 16-21 level-6 cells. Request to core sent.
- Szekeres (q0040, q0041): N64 and N128 stop at the guard at tau 30.25 and 37.47 (P17 refuted for N128); N256 ran one
  segment only (the queue entry gave no segment count: MAX_SEGMENTS = 1), tau 21.2 of 40. Orders from N64/N128 in
  szekeres JOURNAL entry 11; N128/N256 is read by a detached analysis (A-20261126-023245-1dd80ad, ~3-4 h).

Rulings asked (G2 is not sent to its verifier before them):
1. C3: may G2's package be completed and reviewed with C3 FAILED on record (the bound kept), or is the
   particle-number leg of the smooth member (processors, next session) required first?
2. C1 (ii): state the periodic LTB test as "shells verified to 1-4 per cent outside r0 = 1.5; the horizon finder
   fails on this slice (failure on record, request to core)", or wait for core's finder answer and a processor rerun
   of the finder on P0L6's restart files?
3. C1 (iii): continue Szekeres N256 from its restart file to tau 40 (about 0.8 card-hour, priority 2, one wrapper
   entry), or judge the series at tau <= 20 where all three members exist (N64 and N128 do not reach 40 anyway)?
4. A2: is a half-amplitude GR member of S1L (tests the candidate "nonlinear zeta-delta relation at zeta 0.3", about
   2 card-hours to its crossing) wanted before G2, or is it a G3 item with A2 failed on record?
