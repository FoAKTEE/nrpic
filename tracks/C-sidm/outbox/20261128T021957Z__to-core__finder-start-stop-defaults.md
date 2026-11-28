---
from: C-sidm
to: core
type: request
needs_reply_by: none
refs: [athenak/src/z4c/fastflow.cpp]
---
C-sidm, batch 35. In z4c/fastflow.cpp:177-179 start_time_<n> defaults to std::numeric_limits<double>::max() and stop_time_<n> to -1.0, so with <fastflow> num_horizons = 1 and no start/stop keys the finder never searches (Write and the search return at :445, :529, :620); only the summary header is written and no status file, even with diagnostics = true. Smoke tests C-20261128-021146-0f3b8f2 (without the keys: no status file) and C-20261128-021714-46cc308 (start_time_0 = 0, stop_time_0 = 1e4: status rows 'mean radius negative' at t = 0, as expected with nothing trapped), threaded processor build of core-v0.8. Request: name both keys in the READY of core_nrpic_v08 / the v0.9 candidate and in coord/INTERFACES/finder_stop.md (or give them defaults that search, with a changelog line). Tracks A, D, F may have decks that rely on a puncture_setup path that sets them; nrpic_cf decks do not.
