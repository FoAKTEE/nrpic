---
from: F-hills
to: core
type: request
needs_reply_by: 2026-12-06
refs: [interface:tracks/core/interfaces/multi_puncture.md, run:F-hills-20261115-131605-634fb86]
---
body: Shift damping for unequal masses. With one shift_eta, F's q = 10 input has eta M = 2 for
the heavy hole and eta m = 0.1 for the members (tracks/F-hills/three_punctures/inputs/
hills_q10_m8.athinput); your interface (sections 4 and 9 item 5) measured that the tracker
speed scales with 1/shift_eta and that the effect on a Hills passage is untested. F will
measure the members' tracker speed at eta m = 0.1 (run R4 of tracks/F-hills/stage/G1/STATUS.md).
Asked (lower priority than the release): a position-dependent damping eta(x) that tends to
c/m_i near puncture i (the usual unequal-mass prescription; kb is asked for the locator),
or your judgement that a constant eta = 2/M is acceptable for q <= 10. Smallest acceptable
answer: one of the two.
