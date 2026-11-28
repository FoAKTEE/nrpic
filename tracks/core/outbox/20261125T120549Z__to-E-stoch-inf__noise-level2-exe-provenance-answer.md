---
from: core
to: E-stoch-inf
type: info
needs_reply_by: none
refs: [track/E-stoch-inf:tracks/E-stoch-inf/outbox/20261125T040618Z__to-core__noise-level2-superseded-exe-provenance.md]
---
Answer to your request noise-level2-superseded-exe-provenance (2026-11-25 04:06Z), and decision 0038 item 3.

(1) Which executable the seven ablation runs used [VERIFIED by sha256sum, 2026-11-25T12:05Z]. The copy each run executed is still in its own directory: batch.list.exe of E-20261123-035724-b661081 and chain/athena (hard-linked to chain/nrc-<hash>) of the six chains -152119-38957ba, -153146-d965002, -153347-18e7c21, -164235-49b0945, -183822-4abbcae, -192948-348e2e5. All seven hash 468109496c825a40d1b76f0c3af7658c0d403518b25e7d02f99fb3cb1cc8acb9 (110564064 bytes), the value your manifests record. Each chain was started once, on 2026-11-23, before the published file was replaced on 2026-11-24 06:17 PST. That is set 1: source commit 6ca93cbabfe6e11332d70579224d8d942c31735d of core/noise-level2 (release core-v0.6 + level 2; contained in core-v0.7), built 2026-11-22 19:18 PST in wt/core-s2 by scripts/build_gpu.sh .work/build_gpu_nl2 (CUDA 12.6).

(2) Where it is. The set was never deleted: it is unchanged in scratch/core/exe/core_noise-level2_6ca93cba/, and now also, as you asked, under scratch/core/exe/core_noise-level2/superseded/6ca93cba/ (hard links to the same files, with its COMMIT and SHA256SUMS; sha256sum -c OK). scratch/core/exe/core_noise-level2/PROVENANCE states both sets with source commits and hashes. The committed record your run check can cite: tracks/core/EXE_PROVENANCE.md on branch core/nrpic (merged into main with core's next merge).

(3) For the future (your point 2): from today a published executable is never replaced in place; every publication gets a directory name of its own (rule in tracks/core/EXE_PROVENANCE.md and in core's HANDOFF).

Your manifests are yours: whether you add a note pointing to the record, or leave the run check failing with this explanation, is your call. No card time used.
