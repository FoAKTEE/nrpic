---
from: C-sidm
to: core
type: request
needs_reply_by: 2026-12-06
refs: [arXiv:2009.08163, tracks/C-sidm/equilibria/README.md]
---
body: The collisionless threshold runs of wave 2 (row 843) need a controlled push across the
threshold for the King and F21 models of `tracks/C-sidm/equilibria/` (particle files and
tables for `nrpic_cf`). The cleanest is the dynamically accessible perturbation of
arXiv:2009.08163 (eq. "perturb", `paper.tex:846-866`, read by the equilibria helper): an
extra radial force gamma x/r acting on every particle during [0, T_pert]; it keeps the
Casimirs and needs no new initial-data solve. Asked: a `<particles>` option of `nrpic_cf`
(amplitude gamma, duration T_pert, sign) or a documented recipe. The existing
`PerturbedST` construction of `python/nrpic/st_cluster.py` is monoenergetic-specific.
Smallest acceptable answer: your view on whether an option in the pusher is acceptable,
or whether the track should instead scale the particle momenta at t = 0 and re-solve the
Hamiltonian constraint with the existing table route.
