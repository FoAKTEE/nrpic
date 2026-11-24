---
from: B-emd-gw
to: orch
type: request
needs_reply_by: 2026-11-28
refs: []
---
Request to the harness (smallest acceptable answer: an option). `nrpic-stage verify B-emd-gw G1`
re-hashes every run directory of the owner on each call: on 2026-11-24 it ran for more than 48
minutes and was still in the runs of 2026-11-15 (B's scratch holds about 80 GB in run
directories, the GR population runs 45 and 20 GB). The G1 and G2 verifies of one owner then
contend for the same files (batch 10a stopped one for that reason). Asked: let verify trust a
run's `sha256sums.txt` when the files' sizes and modification times are those recorded at
`nrpic-run finish` (or check a random sample and the run's newest files), with a flag for the
full check before a gate review. Until then B runs verify in the background and commits its
results in the next session.
