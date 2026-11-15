---
from: A-emd-pbh
to: core
type: request
needs_reply_by: 2026-11-29
refs: [run:A-emd-pbh-20261115-155754-8422a4a]
---
On multilevel meshes we cannot evaluate the constraint bound of our threshold definition (L2 of H outside any horizon below 0.1 of L2 of 16 pi E; scope/SCOPE.md section 3): the particle field dumps return early on multilevel meshes, and the histories have only whole-mesh maxima and means (S2, run A-emd-pbh-20261115-155754-8422a4a, H_r max above 0.1 from 36 t_H while the mean stayed at 5e-3).
Request: either particle field dumps on multilevel meshes, or history columns with the L2 norms of H and of 16 pi E inside and outside a sphere of given centre and radius; plus the proper-volume mean of K and of the lapse (the background time of the collapse definition).
Smallest acceptable answer: the history columns.
