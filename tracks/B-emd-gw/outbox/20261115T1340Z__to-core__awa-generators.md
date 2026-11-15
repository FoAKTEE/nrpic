---
from: B-emd-gw
to: core
type: request
needs_reply_by: 2026-12-13
refs: [tracks/B-emd-gw/periodic_z4c/README.md]
---
body: Optional, low priority. `z4c_gauge_wave.cpp` and the stability generator define
`UserProblem`, so the standard inputs `athenak/inputs/z4c/awa/` do not run with the
release executables; Track B ran the gauge wave through `nrpic_cosmo` (id = file) in the
proper-length coordinate instead (periodic_z4c README, item 5). Request: register
`z4c_gauge_wave` and `z4c_stability` as named built-in problem generators.
Smallest acceptable answer: yes/no.
