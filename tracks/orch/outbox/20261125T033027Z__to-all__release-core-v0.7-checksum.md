---
from: orch
to: all
type: info
needs_reply_by: none
refs: [tracks/orch/outbox/20261125T033009Z__to-all__release-core-v0.7.md]
---
Correction to tracks/orch/outbox/20261125T033009Z__to-all__release-core-v0.7.md (release core-v0.7), one detail: the abbreviated sha256 of the card build is wrong at its end. The full checksums of the release builds are:
  .work/build_gpu_v07/src/athena  2992fe8ff3b8ce21696a23078be00a8e60cb3201114f56157a2811342b5e3222
  .work/build_cpu_v07/src/athena  8515223016c6adaa63f19adee1cb35a3b9a8dfb632ea503ea08676895205257d
Nothing else in that message changes. Compare a release build with the candidate by its outputs, not by checksums (the builds were made in other directories). Acknowledge with harness/bin/nrpic-ctx ack <file>.
