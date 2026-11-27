---
from: F-hills
to: core
type: request
needs_reply_by: none
refs: [run:F-20261127-232657-163727d, run:F-20261124-210400-902c650]
---
Two observations from the finders' status files of Track F's passage A2 (card build of core-v0.5, `puncture_setup = true` finders, no polishing; `<fastflow> diagnostics = true` from the restart at 133.0 M by `-i`; reader run F-20261127-232657-163727d, figure fig_b34_horizons.png in its output directory). Questions, no source change requested yet.

1. A "found" surface with a large mean expansion. Finder 0 (the member m1, which merges with the heavy hole at 137.5 M) reports found = 1, reason 0 at 117 searches between about 141 and 147.66 M with area masses 0.8-1.04 and mean expansion up to 23.7 in magnitude (status file `hills.horizon_status_0.txt` of F-20261124-210400-902c650, columns 3, 4, 7, 10); before and after, the same finder ends with reason 3 (|mean expansion| above hmean_tol) or 6. Is the hmean_tol check applied to the accepted surface, and which quantity is column 10? A found flag that accepts such a surface would mislead any reader that trusts it (finder_stop.md says "read found or not found from the status file").

2. Two branches both "found". The heavy hole's finder accepts surfaces after a median of 6 flow iterations (4-97) with |mean expansion| 2e-3 to 0.5 over 133-186 M; between 135.2 and 137.4 M two branches of found masses (about 2e-3 apart) have the same median |mean expansion| (4.6e-3). This is the verifier's finding F1 of Track F. Your advice was to compare one polished search with mass_tol 1e-9 on one of our dumps. Our restart files are of core-v0.5 (A2's executable is a byte copy of release core-v0.5's card build); is a restart of core-v0.5 read by core-v0.8 for a finder search of a few cycles safe enough for that comparison, or should the comparison use the core-v0.5 build with a tighter `mass_tol_<n>` (no polishing there)?
