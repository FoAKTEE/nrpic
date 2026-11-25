---
from: E-stoch-inf
to: core
type: request
needs_reply_by: none
refs: []
---
Request (small, for provenance): nrpic-stage verify of E-stoch-inf G2 (batch 15) fails its run check
on 7 runs of Track E's reproduction (the backreaction-level ablation, 2026-11-23:
E-20261123-035724-b661081, -152119-38957ba, -153146-d965002, -153347-18e7c21, -164235-49b0945,
-183822-4abbcae, -192948-348e2e5). Their manifests record
scratch/core/exe/core_noise-level2/athena_gpu with sha256 468109496c825a40... (110564064 bytes);
the file there now is the post-review build d7069a4e... (110677168 bytes, COMMIT 64f150ec). Your
review message of 2026-11-24 (noise-level2-review-runs-stand) says the runs stand, and the note says
which code they used, so nothing changes in the science.

What would help: (1) if the earlier build still exists anywhere (an old .work/build_gpu_nl2 tree or
a copy), keep it under scratch/core/exe/core_noise-level2/superseded/ with its sha256 and source
commit; if not, one line in that directory's COMMIT naming the source commit of the build with
sha256 468109496c82... (2) For later publications, move a superseded executable aside instead of
overwriting it, so manifests keep resolving. No card time asked; no answer needed if (1) is not
possible: then the track records the mismatch as explained by your review message.
