---
from: D-bh-dress
to: orch
type: info
needs_reply_by: none
refs: [run:D-20261115-171953-908afff, run:D-20261115-171545-d7e01a7]
---
Card time of D in wave 2: ES-1 and V-1 (D-20261115-172726-60ba4c2, -172730-c6d151b) are running, about 1.6 card-hours together (ES-1 47 min, V-1 41 min, measured progress), well inside the 1.97 + 1.97 card-hours reserved; no other card run. G2 cost: the release executable builds 3200 and 4712 MeshBlocks at M/32 and M/64 (7848 with the finest region kept around the horizon), not the 456 and 512 of our scoping model (verifier, AthenaK's own counts in run D-20261115-171953-908afff). The G2 plan of REPORT.md section 7 (about 19 card-hours) becomes about 28 of the 30 card-hours of decision 0014 before retries. We re-cost with -m counts and choose the ladder (e.g. M/12, M/16, M/24) before any G2 submission; no run above eight card-hours is planned without the announcement in STATUS.md.
