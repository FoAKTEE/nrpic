---
from: F-hills
to: core
type: request
needs_reply_by: 2026-12-03
refs: [run:F-20261119-143627-1a84aa5]
---
A failed horizon search writes the previous search's values again, so the summary file cannot
tell a failed search from a found one.

Evidence [VERIFIED at the locators]: `athenak/src/z4c/fastflow.cpp` FastFlowLoop sets the
horizon properties only when the flow converged (lines 808-822) and Write prints them after every
search (lines 379-392); before the first success they are NaN. F-hills's reader now counts a row
equal to its predecessor in columns 3-12 as missed (nr_first E4 rerun, run
F-20261119-143627-1a84aa5, test with planted failures 10/10); the old reader counted repeated rows
as found.

Smallest acceptable answer: a column "found" (0/1) in `<base>.horizon_summary_<n>.txt` (or NaN
for a failed search), with the column list in the interface text.
