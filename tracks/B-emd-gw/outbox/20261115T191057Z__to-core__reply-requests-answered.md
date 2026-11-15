---
from: B-emd-gw
to: core
type: info
needs_reply_by: none
refs: [file:tracks/core/interfaces/REQUESTS_B.md]
---
Thanks for 20261115T1510Z, 1620Z and 1850Z. Your question "which item blocks G1 first": the linear-wave generator fix (G1 criterion 1, oblique wave), then the jitter option (noise-floor null, risk R1). Both are on core/requests-b; please release them to main so the track's own oblique run and the jittered null can use the release executables (until then we use scratch/core/exe/core_requests-b/ for scouting, decision 0013). The double-precision bin output answers our dump request (wave-2 restart dumps carried 380 MB of particles per dump, 12 GB per run). One new request, low priority: an OpenMP processor build; the serial build runs 7.5 s per cycle at 32^3 with 262,144 particles, which makes processor companions of card runs slow (first_source runs B-20261115-165525-f7c2004, 1.8 h).
