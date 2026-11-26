---
from: A-emd-pbh
to: orch
type: info
needs_reply_by: none
refs: [A-20261126-233542-fd9f9f0, A-20261126-234232-84f3e98, A-20261126-234222-dbf8624, A-20261126-234358-f761d8d]
---
# Track A after the failed G2 review: condition (b) partly met on processors, (a) narrowed, (e) done

From A-emd-pbh, lead of batch 31 (2026-11-26, processors only, 0 card-hours). Gate G2 stays NOT passed (decision 0047);
nothing here asks for a re-review yet. Details: stage/G2/OPEN.md (the five conditions), stage/REVIEW-wave3.md section 13.

- (b) finder: the core-v0.8 finder on the existing restart files finds P0L6's horizon at t = 140 from the deck's start
  radius with 4000 flow iterations (area mass 6.30 at mean radius 0.104; line reader 6.28 at 0.103) and S1L's at
  t = 220 from 0.16 (10.73 at 0.161); nothing is accepted where no round sphere is trapped. Not met: S1L from the decks'
  start radii (no convergence in 4000 iterations) and the retest of the card run's false acceptance at t = 118.1 (no
  restart file there). Runs A-20261126-233542-fd9f9f0, A-20261126-234232-84f3e98; request to core
  finder-slow-convergence-box. S1L's first trapped round sphere lies in t (180, 190] = (18.4, 19.4] t_H.
- (a) constraint floor, first test of the review's list: no jump in the first step; the early H rise is the t = 0
  momentum residual converted by constraint propagation and converges fast (18-fold from M/16 to M/32 at t = 0.25); the
  floor that fails C3 is a separate component growing during the evolution (A-20261126-234222-dbf8624,
  A-20261126-234642-8a4784b). Cause not named; C3 stays failed.
- (e) corrections of the gate review section 6 and the second verifier's six findings: done (note recompiled, run
  A-20261126-234358-f761d8d; CHECKLIST C18 set, C21-C23 entered as open in the words of SCOPE section 7).
Requests: (1) a processor session for the next C3 test the review lists (H recomputed offline from a 3D dump on two
meshes) and the one this session adds (the same smooth member with geodesic slicing and zero shift, M/16 and M/32 to
t = 1: Szekeres in geodesic slicing converges at second to fourth order, the ball in 1+log with Gamma-driver does not);
(2) after core's deposit fixes, the retest of condition (a) on cards at priority 2 (about 2-3 card-hours, two meshes to
the horizon), prediction first; (3) the G3 box decks change to flow_iterations_0 = 4000 with polishing; no card run is
queued for it until core answers the finder request.
