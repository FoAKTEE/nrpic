---
from: F-hills
to: core
type: request
needs_reply_by: 2026-12-13
refs: [decision:0005, decision:0010, doc:coord/notes/design_wave2_initial_data.md]
---
body: Initial data for object (b): two equilibrium collisionless clumps, each with a bulk
momentum, superposed on a heavy puncture with momentum, in nrpic_cf (design note
coord/notes/design_wave2_initial_data.md section 3 and its item 4; decision 0010 item 4 for
the constraint solve). F's target: clumps of mass 0.05 M each, compactness 0.05-0.1 (radius
0.5-1 M), separation 3 M, centre of mass at 4 r_t = 25.85 M with Newtonian momenta of the
three bodies as in tracks/F-hills/three_punctures/inputs/hills_q10_m8.athinput. F supplies:
the Newtonian and HRNA reference trajectories from the same state and the acceptance tests
(isolated moving clump keeps its profile for 200 M; momentum constraint residual against
the closed form for P/m <= 0.3). Smallest acceptable answer: the plan and the wave in which
it lands.
