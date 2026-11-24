---
from: D-bh-dress
to: orch
type: request
needs_reply_by: none
refs: [run:D-20261121-165420-5d1c245]
---
nrpic-stage verify D-bh-dress G2 --no-checksums (2026-11-24 10:07 PST, export of 72ebe935) fails only the
runs check: six card runs still open (expected) and run D-20261121-165420-5d1c245, the G1 gate reviewer's own
check, whose input /data/haiyangw/nrpic/scratch/D-bh-dress/tmp/gate_review_G1/review_checks.py changed after it
ran (sha256 differs). The run and its input belong to the gate review, not to D's work; D has not touched the
file. Request: say whether D should mark that manifest superseded (with a note naming the gate review) or
whether the reviewer re-registers it. Smallest acceptable answer: one line naming who fixes it.
