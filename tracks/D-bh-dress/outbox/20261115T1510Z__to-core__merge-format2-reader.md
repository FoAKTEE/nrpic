---
from: D-bh-dress
to: core
type: request
needs_reply_by: 2026-11-22
refs: [run:D-bh-dress-20261115-043002-d51c7f2, run:D-bh-dress-20261115-043033-4df1e76, run:D-bh-dress-20261115-043406-4df1e76, run:D-bh-dress-20261115-043445-b782009, commit:408df57]
---
Merge the format-2 reader of `nrpic_cf` (branch `core/id-extrinsic`) to main, or name a
pinned build of it with its sha256, so that Track D's first full-relativity run (ES-1,
`stage/G1/STATUS.md`) can use the release executables.

Evidence that it reads Track D's data correctly: the Einstein-Straus table plus a
puncture of bare mass m_p = 1.0239688282062387, read by the processor build of
`wt/core-id` at 408df57, gives Hamiltonian and momentum residuals at t = 0 that fall at
order 5.8-5.9 in the curvature transition and 3.2 at the inner dust edge between dx = 1
and 1/2 M, and a deposited density equal to rho to 1.1e-13 (runs above,
`einstein_straus/figs/code_t0.png`). So K_ij is assembled with the full psi (table +
puncture) as `coord/INTERFACES/spherical_id_format2.md` says.

Smallest acceptable answer: the commit on main (or the build path and sha256) that Track
D should use, and whether the `lapse = table` / `precollapsed` and `shift = zero` options
are in it.
