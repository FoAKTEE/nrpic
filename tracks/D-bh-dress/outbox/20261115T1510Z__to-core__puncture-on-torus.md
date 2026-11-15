---
from: D-bh-dress
to: core
type: proposal
needs_reply_by: 2027-01-31
refs: [tracks/D-bh-dress/scope/SCOPE.md, arXiv:2302.07878, arXiv:1801.01083]
---
Later (G3): the only version of the null test that speaks to the claim that black holes
with "realistic behaviour at infinity" grow with a (arXiv:2302.07878
`paper_couple_rev.tex:100-101`) is the periodic one: a puncture in a dust-filled torus
with cosmological boundary conditions (SCOPE.md section 3.4, item 3). It needs a
constraint solve with a puncture in a periodic box (the existing torus solver of
`cosmo/ic/` has no puncture) and B's periodic conformal-time gauge near a hole. Proposal:
put it on core's list for wave 3; optional for G3, particle splitting near the hole.
Track D will supply the reference (Einstein-Straus-type lattice cell, mass inside the
comoving cell boundary) and the tests.
