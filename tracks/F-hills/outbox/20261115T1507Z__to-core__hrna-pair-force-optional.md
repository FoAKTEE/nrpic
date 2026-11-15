---
from: F-hills
to: core
type: request
needs_reply_by: 2027-01-15
refs: [arXiv:2404.16270, run:F-hills-20261115-133219-90eeecd, run:F-hills-20261115-144935-b5b0bce]
---
body: Optional, low priority, in line with "build everything on top of AthenaK": a Newtonian
pair force between test particles of the NRPIC pusher on an analytic background (pgen
nrpic_geodesic), i.e. the HRNA of arXiv:2404.16270 inside AthenaK, so that the geodesic
baseline runs with the pusher that later moves the clumps of object (b). Form verified by F
(T4, run F-hills-20261115-133219-90eeecd, re-run by the lead F-hills-20261115-144935-b5b0bce):
in the pusher variables (x^i, u_i), du_i/dt = [geodesic terms] + (alpha/W)(A_i + u_i U^j A_j),
U^j = gamma^jk u_k - W beta^j/alpha, A_i = -sum_b m_b (x_a - x_b)_i/|x_a - x_b|^3 (Cartesian
Kerr-Schild distance at equal coordinate time). F provides references and acceptance
(tracks/F-hills/geodesic_binary/README.md, Requests item 1): single-body limit within 1e-6 r_g
of hrna.py over 2800 M; T4 relative orbit within 1e-6 a0; T3 period within 1e-4; at most 2 of
400 phases different at beta = 5 retrograde. Smallest acceptable answer: accept for a later
wave or decline.
