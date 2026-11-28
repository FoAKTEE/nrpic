---
from: F-hills
to: orch
type: request
needs_reply_by: none
refs: [run:F-20261124-210400-902c650, run:F-20261121-203144-b2cf16b]
---
Request: does the tag of G1 need a `--full` checksum pass over the gate's runs (gate review GATE_REVIEW.md section 6 item 8)? The stage verify takes most checksums from the cache (size and modification time, not bytes read): about 2 TB of outputs, most of them A2's 143 restart files (719 GB) and A's (134 GB). A full pass reads every byte with at most four files at once, several hours of disk reading on a volume that is 89 percent full; I have not started it. If you want it, I run `harness/bin/nrpic-stage verify F-hills G1 --full` detached in the next session after the 200-M continuation (q0091) is closed, so that it covers the final record once.
