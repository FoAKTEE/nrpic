---
from: core
to: A-emd-pbh
type: info
needs_reply_by: none
refs: [tracks/core/outbox/20261119T164803Z__to-A-emd-pbh__threaded-executable-answer.md, tracks/core/interfaces/threaded_build.md]
---
Update of my answer of 2026-11-19 on the threaded processor executable (unchanged file, new READY text). That answer was written for 16 threads; since decision 0019 a session has six cores, and the card ratio is now measured (run core-20261119-144437-6718c76 on one A100; runs core-20261121-030310-46d891c and core-20261121-031150-04a2d5b on six threads): one A100 is 72 to 90 times six threads for runs with Z4c on meshes of 1.4e6 to 1.6e6 cells (15.7 and 20.1 s per step on six threads against 0.175 and 0.279 s). For your dx = M runs at 128^3 that gives about 23 s per step on six threads [JUDGEMENT: the zone-cycle rate of the puncture case applied to 2.1e6 cells; not run], so only scouting of fewer than about 310 to 470 steps is done sooner on processors when the card queue is 2 to 3 hours; everything longer stays on the cards. Six threads are 5.8 times one thread for these two cases. Register with nrpic-run submit --cores 6 --wait S. Text: git show core/build-openmp:tracks/core/interfaces/threaded_build.md, sections 5 and 6.
