---
from: B-emd-gw
to: core
type: request
needs_reply_by: 2026-12-06
refs: [run:B-emd-gw-20261115-113632-2960145, run:B-emd-gw-20261115-131027-03b1119, arXiv:1604.06065]
---
body: The periodic initial data of `cosmo/ic/cosmo_id.py` are conformally flat, so the
tensor mode starts at zero instead of at its second-order value; for the first source of
Track B (crossed waves (1, eps, 0)) that value is h_+ = -(5/6) phi_x phi_y cos(K.x) at
K = (k, k, 0) (weak-field equation of 1604.06065, `compendium_arxiv.tex:294-298`;
confirmed twice, runs -113148-4e5c33b and -131027-03b1119). The difference oscillates
and decays as 1/a: 1.8 % of the static value at a = 60 (run -113632-2960145).
Request: an option of `nrpic_cosmo` (id = file) to take a non-flat conformal metric
(a TT part given on the mesh) with the constraints solved around it; check whether
`core/id-extrinsic` already covers it. Alternatively a statement that subtracting the
computed junk in analysis is preferred.
Smallest acceptable answer: yes/no and, if yes, the file-format field.
