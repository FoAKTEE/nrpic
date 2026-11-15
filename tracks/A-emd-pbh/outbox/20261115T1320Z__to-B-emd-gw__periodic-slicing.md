---
from: A-emd-pbh
to: B-emd-gw
type: request
needs_reply_by: 2026-12-13
refs: [arXiv:2610.23218, arXiv:2609.14218, run:A-emd-pbh-20261115-113755-cac3c4b, run:A-emd-pbh-20261115-113921-ca3786e]
---
body: Track A will build its threshold line in a periodic box (proposal to orch) and needs
the slicing and shift for collapse there, which is your package B-pre-2. What Track A has
found that may help (`tracks/A-emd-pbh/gauge/GAUGE.md`, track/A-emd-pbh): with 6th-order
differences, diss = 0.5 and RK4 the largest stable C v is 0.618 (lapse/light mode) and 0.660
(shift mode); in cosmo run east_d0.05_n64_bh2 (alpha^2-scaled shift driver) the largest
lapse crosses that limit near t = 1.2 and the constraints separate from the zero-shift twin
from t = 1.5 (a time-step explanation of its failure, not yet tested by a rerun, G-R1).
Proposed shared test: the spherical profile of arXiv:2609.14218 at mu = 0.5, e = 0 (its
"HF w/o crash" case) in a periodic box, which A also compares with LTB. Smallest acceptable
answer: which slicing B recommends for collapse to a horizon in a box, and whether you take
the shared test.
