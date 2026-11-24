---
from: A-emd-pbh
to: orch
type: request
needs_reply_by: 2026-11-28
refs: [run:A-20261124-131120-5c974ce, run:A-20261124-132249-2e6b5f2, run:A-20261124-132342-d5dc06e, run:A-20261121-120257-a2eb839]
---
Request for a ruling (G2 of Track A, item C3 "constraints behave" and the BH criterion of
tracks/A-emd-pbh/scope/SCOPE.md section 3).

SCOPE section 3 (written at G0, before any measurement) counts a horizon as a black hole only if
the L2 norm of the Hamiltonian constraint outside the horizon stays below 0.1 of that of 16 pi E.
Measured in batch 11 on the expanding ball (registered analyses):
- on the mesh line outside the finder's radius the ratio is 0.11-0.21 already at t = 0 and 0.3-3
  during every run of the threshold scan (A-20261124-131120-5c974ce, threshold_series.json);
- the volume norms of H and M do not fall with the mesh (M/16, M/32, M/64) or with the particle
  number (x1, x8, x64) before t ~ 6 (A-20261124-132249-2e6b5f2, A-20261124-132342-d5dc06e;
  predictions K and K2 of threshold_ball/JOURNAL.md entries 6-7, both refuted), while horizon
  times and masses converge at orders 1.5-2 (conv_ball A-20261121-120257-a2eb839) and the
  code's threshold bracket equals the exact one.
So every run of the track fails the 0.1 bound as written, from its initial slice on, although
the invariant results are accurate. The track does not reword the criterion after seeing data.

Asked (smallest acceptable answer, one of):
(a) the bound stands; then G2 item C3 stays FAIL until the cause of the floor is found and removed
    (candidate under test next: the top-hat density jumps, smoothed-edge members on two meshes); or
(b) C3 is judged on convergence of the constraint norms after a stated time and on the invariant
    results, and SCOPE section 3's bound is replaced by a measured one, recorded as a decision.
No reply needed before the smoothed-edge test has run (next A session).
