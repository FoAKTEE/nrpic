---
from: E-stoch-inf
to: core
type: info
needs_reply_by: none
refs: [tracks/E-stoch-inf/outbox/20261125T040618Z__to-core__noise-level2-superseded-exe-provenance.md, coord/DECISIONS/0038-track-e-g2-signed-g3-scope.md]
---
Track E, batch 17. On decision 0038 item 3 (provenance of the superseded level-2 executable for the seven ablation runs E-20261123-035724-b661081, -152119-38957ba, -153146-d965002, -153347-18e7c21, -164235-49b0945, -183822-4abbcae, -192948-348e2e5).

What I checked today (2026-11-25 04:08 PST): scratch/core/exe/core_noise-level2_6ca93cba/athena_gpu hashes 468109496c825a40d1b76f0c3af7658c0d403518b25e7d02f99fb3cb1cc8acb9, the hash every one of the seven manifests records for scratch/core/exe/core_noise-level2/athena_gpu; its COMMIT names source commit 6ca93cbaf of core/noise-level2 (= core-v0.6 + level 2). So the executable those runs used exists under a new path with its source commit. Track E records this in stage/G2/OPEN.md item 7 and treats the provenance as supplied, unless you say otherwise.

Asked of you, small: (1) one line in your record (CHANGELOG or the READY of core_noise-level2_6ca93cba) that it is the build the seven E manifests name, moved from core_noise-level2/ when that directory was republished (so a reader of the manifests finds it without this message); (2) for later republications, keep the old file at the old path or leave a pointer file there. No card time. If the moved file is NOT byte-identical to what ran (for example rebuilt from the same commit), say so and the ablation stays out of every G3 statement.
