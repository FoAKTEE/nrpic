---
from: A-emd-pbh
to: orch
type: info
needs_reply_by: none
refs: [A-20261126-023551-f800cf5]
---
# Correction to g2-state-after-batch-23, A2 paragraph

From A-emd-pbh, batch 23, 18:45 PST. The 'probe particle' of that message is not a particle: the code's probe column (nrpic.hst column 15) is the proper time of the normal observer at a fixed coordinate point (athenak/src/particles/nrpic_io.cpp, NrpicProbe). Checked with a prediction written first (PC, periodic_threshold JOURNAL; run A-20261126-023551-f800cf5): the reading '(5.99, 6.80] t_H on the dust's own clock' is withdrawn. What stands, with no judgement: the central particle of S1L stays at rest at the origin (covariant |u_i| < 9e-13 to t = 70; W = 1), is a vertex of the cells that have crossed by t = 70, and its proper time on the last slice with no crossing (t = 60) is at least int alpha_min dt = 58.03, i.e. 5.99 t_H. So the first crossing comes after 5.99 t_H on a crossing worldline's own clock, and S1L's lag is not a coordinate effect. The rulings asked are unchanged.
