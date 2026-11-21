---
from: A-emd-pbh
to: orch
type: request
needs_reply_by: none
refs: [run:A-20261121-064515-aa13c8f, run:A-20261121-064537-2bcf310]
---
Waiver request for gate G1 of A-emd-pbh (coord/WAIVERS.md): A-20261121-064515-aa13c8f, the gate reviewer's failed first check run (exit 1, on record in stage/G1/GATE_REVIEW.md section 1, commit 2bcf3104). Its input script scratch/A-emd-pbh/gate_review_G1/review_checks.py was edited by the reviewer before the rerun A-20261121-064537-2bcf310 (completed, sha256 4d72c147... recorded), so nrpic-stage verify reports 'input changed since the run' for the failed attempt. The script as rerun is now kept in tracks/A-emd-pbh/stage/G1/gate_review/review_checks.py. Smallest acceptable answer: the run id in coord/WAIVERS.md with this reason.
