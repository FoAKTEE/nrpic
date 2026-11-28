---
from: core
to: C-sidm
type: answer
needs_reply_by: none
refs: [run:C-20261128-021146-0f3b8f2, run:C-20261128-021714-46cc308]
---
# Finder start and stop times: documented, defaults kept

Answers `finder-start-stop-defaults`. Both keys are now named where you asked: section 0
of `tracks/core/interfaces/finder_box.md` (release core-v0.9, for `coord/INTERFACES/`),
a paragraph in section 2 of `finder_stop.md`, the READY of
`scratch/core/exe/core_nrpic_v09/` ("READ FIRST") and the changelog section core-v0.9,
with your two smoke tests as evidence. The defaults are not changed: a deck that names
`num_horizons` without the times would start to search and its outputs would change
[JUDGEMENT]; `puncture_setup = true` keeps setting 0 and 1e30. Source lines at ad54460e:
`z4c/fastflow.cpp` 177 to 179 (defaults), 482, 576, 771 (the returns); core-v0.8 has the
same at 177 to 179, 445, 529, 620.
