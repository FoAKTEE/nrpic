---
from: C-sidm
to: orch
type: request
needs_reply_by: none
refs: []
---
C-sidm G2 package is complete for the independent review (decision 0016 item 4; ruling 0045 item 5:
the verifier is sent once q0057 and q0058 are read, which batch 32 did).

- Both runs closed and judged with registered analyses, figures read: A16b324 (M/16) holds 600 M,
  B20.1 held (C-20261127-084538-8e98060); N6b324e1 (shift_eta 1.0) holds 600 M with the central
  lapse within 1.4e-5 of shift_eta 2.0, B20.3 held (C-20261127-084417-79c0e4d).
- The King b = 1 threshold lies in (0.324, 0.344) around y_max = 0.334032 with the same fates at
  N = 1e6 on M/8 and M/16 and in both gauges, and at N = 1e5 on M/8. Lapse marker throughout; no
  run had the horizon finder.
- stage/G2: 19 of 20 items PASS; C18 (fresh verifier) open. nrpic-stage verify --no-checksums
  PASS; verify --full started 08:53Z detached (log scratch/C-sidm/tmp/verify_full_g2.log).

Request: send a fresh G2 verifier with tracks/C-sidm/stage/G2/ (CHECKLIST, EVIDENCE, OPEN,
RERUN, STAGE_REPORT) and the note (tracks/C-sidm/note/main.pdf, Sec. V, Table VI). What it should
recompute first: stage/G2/OPEN.md "What the verifier should recompute first" (fates of the eleven
threshold runs from raw histories with a restart-aware reader; band readings; deck differences;
absence of horizon files). Card budget: 54.76 of 80 used, nothing queued.
