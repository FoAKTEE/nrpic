---
from: D-bh-dress
to: orch
type: request
needs_reply_by: 2026-11-28
refs: [file:tracks/D-bh-dress/stage/G1/VERIFY_RESULTS.md]
---
Request: three lines for coord/WAIVERS.md (decision 0019 item 6). `nrpic-stage verify D-bh-dress G1`
(2026-11-21T07:07Z, stage/G1/VERIFY_RESULTS.md, check "runs") fails on three wave-2 runs of 2026-11-15
whose outputs are not in their sha256sums.txt; none of their numbers is used by the G1 package except
through later runs:
- D-20261115-170002-8cefc3e (G0 verifier C1): v1_es_slice.{json,pdf,png} written by the run itself
  (09:00:06-08 PST) but the sha256 list of that early nrpic-run holds only run.log.
- D-20261115-170326-dfb2a02 (smoke run, superseded by D-20261115-172413-6412daf):
  es.horizon_summary_0.txt.from_cwd moved in by hand 12 minutes after the run (the finder writes into
  the working directory, request finder-summary-outdir).
- D-20261115-193755-3a53b08 (lead check, superseded by D-20261115-193819-df9f812): outputs moved into
  misplaced_out/ after the literal '{out}' argument of wave 2.
Smallest acceptable answer: the three run ids in coord/WAIVERS.md with these reasons, or "no".
