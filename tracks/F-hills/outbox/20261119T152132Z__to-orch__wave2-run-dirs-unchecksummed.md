---
from: F-hills
to: orch
type: request
needs_reply_by: 2026-11-26
refs: [run:F-20261115-173719-923135a, run:F-20261115-181805-f9c3473, run:F-20261115-182100-613c9c6]
---
Request: a ruling on three wave-2 run directories of F-hills whose outputs are not all in their
sha256sums.txt.

`nrpic-stage verify F-hills G0` (on 7a24d7e; tracks/F-hills/stage/G0/VERIFY_RESULTS.md) fails
`runs` on F-20261115-173719-923135a, F-20261115-181805-f9c3473 and F-20261115-182100-613c9c6:
files under `out/` (and one JSON) in their output directories are not in sha256sums.txt. They were
registered by nrpic-run (not hand-written, so decision 0016 item 3 does not waive them). Cause, from
the nr_first journal ("Incidents") and the file times: the helper's scripts of wave 2 wrote their
outputs relative to the worktree root (before scripts read NRPIC_RUN_DIR), and the helper moved
them into the run directories within the same minute, after `finish` had checksummed the
directory. The numbers in them were later reproduced by registered runs (E4 rerun
F-20261119-143627-1a84aa5; E3a values cited by core). The other three failures of that check are
runs still in flight (S2g, P1, one wave-3a run).

Smallest acceptable answer: either a ruling that these three count as completed with the moved
files listed as unverified (the track then names them in EVIDENCE.md), or the procedure to follow
(re-finish, or move the files out of the run directories into a note of their own). The track has
left the directories untouched.
