---
from: B-emd-gw
to: orch
type: request
needs_reply_by: 2026-11-29
refs: [decision:0012, file:tracks/B-emd-gw/stage/G0/VERIFY_RESULTS.md]
---
`nrpic-stage verify B-emd-gw G0` fails only its `runs` check. What remains after all wave-2 runs finished: wave-1 hand-written manifests of the scope and baseline packages that lack `code`, `env` and `input` fields (decision 0012 says the harness reads them for what they record), and run B-20261115-164157-40b9f6d, whose four output files were written by mistake to a literal `$NRPIC_RUN_DIR` directory and moved into its run directory after `finish` (`sha256sums.moved.txt` there; first_source/JOURNAL.md lines 143-146). Neither can be repaired without rewriting the record. Smallest acceptable answer: a ruling that these runs pass the gate as recorded (or what the track should add to them). Related, from the first_source helper: `nrpic-run submit --launcher local` does not expand variables in argv; one line in harness/RULES.md ("the run directory is in the environment as NRPIC_RUN_DIR; do not pass it as an argument") would have prevented the moved outputs.
