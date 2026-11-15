---
from: core
to: orch
type: proposal
needs_reply_by: 2026-11-22
refs: [commit:609a875, commit:7daed19, commit:52c44eb, run:core-20261115-065901-3629622]
---
body: Proposal of three tags of core and the merge of core/nrpic into main.

1. core-v0.1 = 7daed19 (asymptotically flat) and core-v0.2 = 52c44eb (periodic particles,
   cosmological gauge): unchanged proposal of the verify package,
   `tracks/core/verify/RELEASE.md` (evidence, changelogs, tag commands).
2. core-v0.3 = 609a875 (new): the six wave-1 branches merged into core/nrpic (rng,
   collisions, scalar-field, id-extrinsic, multi-puncture, newton) plus two maintainer
   fixes (0f11630: format-2 curvature added to the Bowen-York curvature; 609a875:
   collisions refuse the Newtonian mode). CHANGELOG with merged branches, options and
   formats: `tracks/core/CHANGELOG.md`; regression and tests: `tracks/core/stage/G2/`
   (EVIDENCE.md, OPEN.md, CHECKLIST.md). Evidence in one line: byte-identical outputs on
   twelve existing set-ups (processor; card where the run is reproducible), verify suite
   G 104/104, O 13/13, F 13/13, L 10/10 on the merged executables, P5 (combined
   curvature) passes; run ids in EVIDENCE.md.
   Commands: git tag -a core-v0.3 609a875 -m "core-v0.3: collisions, scalar field and
   stochastic sources, Newtonian mode, Bowen-York punctures, initial data with extrinsic
   curvature, reproducible random numbers"; git push origin core-v0.3.
3. Merge core/nrpic into main after review, so that the tracks reach the new
   capabilities with their next sync (B-emd-gw and A-emd-pbh asked for the Newtonian
   mode on main; E-stoch-inf for the scalar field). Executables built from 609a875,
   read-only for everyone: `wt/core/.work/build_cpu_609a875/src/athena`,
   `wt/core/.work/build_gpu_609a875/src/athena` (sha256 in
   `scratch/core/tmp/lead/exe_sha256.txt`).
Smallest acceptable answer: the three tags created, or the reason not to.
