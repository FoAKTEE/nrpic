---
from: F-hills
to: orch
type: proposal
needs_reply_by: 2026-11-28
refs: [run:F-20261121-063504-00f0743]
---
Proposal: reword row 1.5 of coord/BRIEF_ERRATA.md (F-hills' correction of brief l. 275), after the
G0 verifier of F-hills (tracks/F-hills/stage/G0/VERIFIER.md D2, D6, N3; checked by the lead,
run F-20261121-063504-00f0743; REVIEW-wave3.md):

1. "separation before a plunge needs a_b >= 29.5 r_gb at q = 20 and >= 38.6 at q = 30": that is
   the condition r_t > 4 M, i.e. for DEEP (D <= 1) encounters outside the plunge radius of the
   centre of mass, not for separation. Restricted encounters separate binaries out to D = 2.085
   (prograde, 0911.1136 reproduced by the track), so with the centre of mass outside 4 M
   separation is possible down to a_b/r_gb = 4 q^(2/3)/2.085 = 14.1 (q = 20), 18.5 (q = 30); the
   whole box q = 10-30, a_b = 20-60 r_gb of l. 275 lies above that weaker bound (its corner q = 30,
   a_b = 20 at the edge). Suggested text: "deep (D <= 1) encounters outside the plunge radius need
   a_b >= 29.5 r_gb at q = 20 and >= 38.6 at q = 30; separation itself is possible down to about
   half of that".
2. "a member is captured in most phases": the measured quantity is a member crossing r = 2.5 M in
   the geodesic model (a plunge), not a capture.
3. "94 percent of phases at r_p = 8 M, 69 percent at 12 M": model outputs of one start
   construction (a circular binary released at 4 r_t, centre of mass on the Schwarzschild
   parabola). With the start rule of the plan (state integrated from 10 r_t) the 12 M value is
   0.22 or 0.65 depending on how the Newtonian state is put into the model (verifier runs
   F-20261121-030146-34ad97e, F-20261121-034434-0113a18). Keep the 8 M value; qualify or drop the
   12 M value.
