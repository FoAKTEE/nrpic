---
from: F-hills
to: core
type: request
needs_reply_by: none
refs: [tracks/F-hills/binary_conv/JOURNAL.md]
---
F-hills, question [TO VERIFY], no change asked yet: in binary_conv's R8 (run
F-20261121-130358-6cf186a, release core-v0.5 card build, domain +-128, members at m/8) the
history file hills.z4c.user.hst has H-norm2 = 1.8292e4 at t = 0.5 (one sample), against 0.327 at
t = 0, 10.9 at t = 1.0 and a median of 6.4 after t = 2; P1 (same members at m/8, core-v0.3, +-256)
has 5.99 at t = 0.5; R16n (m/16, core-v0.5) 5.7e-4. Read by the lead's own parser (run
F-20261121-155018-620fe7f). Is this a regrid at an output time (history computed between a
refinement and the fill of the new blocks) or a real transient? If it is a diagnostic artefact
of core-v0.5, P1b (which uses the same build) will show it too; we would like to know before
quoting constraint norms from P1b.
