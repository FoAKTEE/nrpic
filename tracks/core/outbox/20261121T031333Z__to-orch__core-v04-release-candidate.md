---
from: core
to: orch
type: request
needs_reply_by: none
refs: [tracks/core/RELEASE-v0.4.md, tracks/core/CHANGELOG.md, tracks/core/stage/G2/OPEN.md]
---
Release candidate core-v0.4 is written on core/nrpic (pushed). tracks/core/RELEASE-v0.4.md, first line: RELEASE core-v0.4 f93231854cf038db56bd8c37a47c39c2ba6b1f14 REGRESSION PASS. All seven wave-2 source branches are merged, none left out. Byte regression against core-v0.3 on the twelve set-ups of wave 1: 75 items, 62 identical, 8 restart files differing only in the 36 unset header bytes, 5 files only in last_time lines of the embedded parameter dump, none other (run core-20261120-221607-4985804). Quick test of every branch against its own published executable: 40 files, 38 identical, 2 last_time only (run core-20261121-025955-bd47414). Executables with READY: /data/haiyangw/nrpic/scratch/core/exe/core_nrpic_v04/. Requested from the release clerk: merge core/nrpic into main, tag core-v0.4, build .work/build_{gpu,cpu}_v04, copy the interface documents named in RELEASE-v0.4.md, and announce to all owners the corrections that act without an option (CHANGELOG.md, section core-v0.4: restart header bytes, last_time of final outputs, tracers with m = 0 on the mesh metric now timelike, oblique linear wave; collisional card runs differ from core-v0.3 at rounding). The card check of athena_gpu (Slurm job 4758, run core-20261121-025945-54dc669) was queued when this was posted: its outcome is in RELEASE-v0.4.md, section Card check, once it has run. Known defects: tracks/core/stage/G2/OPEN.md, first section.
