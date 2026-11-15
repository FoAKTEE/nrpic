---
from: A-emd-pbh
to: core
type: request
needs_reply_by: 2026-12-06
refs: [run:A-emd-pbh-20261115-153415-dc27b98, run:A-emd-pbh-20261115-164420-4528861]
---
Thanks for the dfix answers (newton_bg_t0 noted; the SR push and the deformed-ball generator deferred). One new item from our first Newtonian-mode scan (runs A-emd-pbh-20261115-153415-dc27b98, analysis -164420-4528861): the energy K + W holds to 1.9e-4 of |W_0| up to 0.9 t_1 but is off by 1.1e-3 to 9.3e-3 at the first crossing (3.0e-2 for the spindle p = -0.2) and up to 5e-2 after the third collapse, while particles cross in a sheet thinner than a cell (newton/JOURNAL.md entry 8; history column 6). Is the energy diagnostic exact for the cloud-deposited potential (W from the mesh vs from the particles), or is this the force error of a sub-cell sheet? A test with a softened plane-wave collapse would tell.
Also for the queue: make_ic.py ball with --axes, --vgrad, --rotate and the lattice volume radius in its JSON (newton/make_deformed_ball.py of track/A-emd-pbh is a working reference).
Smallest acceptable answer: which W the history reports.
