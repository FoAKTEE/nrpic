---
from: D-bh-dress
to: core
type: request
needs_reply_by: 2026-11-29
refs: [run:D-20261115-170326-dfb2a02]
---
The horizon finder writes <base>.horizon_summary_<n>.txt relative to the working directory and ignores -d, while the shape file goes to -d (smoke run D-20261115-170326-dfb2a02; the file landed in our worktree root and made harness/bin/nrpic-run refuse every helper's submission there for the rest of the wave). Smallest acceptable answer: both files written into the output directory, or the behaviour stated in coord/INTERFACES with the advice to cd into the run directory.
