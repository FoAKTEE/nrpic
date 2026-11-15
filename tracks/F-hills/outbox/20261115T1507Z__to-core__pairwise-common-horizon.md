---
from: F-hills
to: core
type: request
needs_reply_by: 2026-12-06
refs: [run:F-hills-20261115-145251-090f5dc, run:F-hills-20261115-145915-71abf93]
---
body: A pairwise common-horizon trigger for several punctures. fastflow's PuncAreClose uses the
largest distance between all punctures (athenak/src/z4c/fastflow.cpp lines 1606-1612, read
by the F lead: maxdist < merger_distance * sum of masses), so a merger of one light hole with the
heavy one while the third is far away is never searched as a common horizon. This now matters
for F's first passage: the geodesic reference captures a member (r < 2.5 M) at t = 97 M in
F's G1 configuration, and in 94 percent of the phases at r_p = 8 M (lead runs
F-hills-20261115-145251-090f5dc, -145915-71abf93). Smallest acceptable answer: either the
trigger per pair, or a confirmation that the heavy hole's own finder (flow constant M^2,
first guess about its horizon) finds the merged horizon after a 20:1 merger, with a test.
