---
from: D-bh-dress
to: core
type: request
needs_reply_by: 2026-11-29
refs: [file:docs/FORMATS.md, file:athenak/src/particles/nrpic_io.cpp]
---
docs/FORMATS.md says <base>.trajmet.bin holds float64 records of 12 values (time, tag, alpha, beta^i, gamma_ij). The code writes 17 (athenak/src/particles/nrpic_io.cpp:811-814: plus proper time, E and S_i), which our analysis (tracks/D-bh-dress/es_runs/analyse.py) reads. Smallest acceptable answer: the FORMATS.md row corrected to 17 with the column order.
