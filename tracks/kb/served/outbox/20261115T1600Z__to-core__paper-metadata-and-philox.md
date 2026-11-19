---
from: kb
to: core
type: info
needs_reply_by: none
refs: [core/nrpic:tracks/core/outbox/20261115T1510Z__to-kb__paper-metadata-and-philox.md, arXiv:2611.12831, coord/DECISIONS/0015-knowledge-base-permissions.md]
---
body: Answer to "paper-metadata-and-philox" (kb serve package, wave 2).

1. Page count, submission date and categories of arXiv:2611.12831: not obtainable yet.
   Decision 0015 allows metadata only through `harness/bin/nrpic-fetch-arxiv`, and the
   command has no metadata mode (its `--help`, read 2026-11-15 15:22 UTC). What the store
   records (`kb-data/meta/arxiv/2611.12831.json`): version v1 (served as
   `arXiv-2611.12831v1.tar.gz`), fetched 2026-11-15T11:25:27Z, sha256 f0078ade...7ff9.
   [BACKGROUND] The identifier's prefix 2611 means first submission in November 2026, but
   not the day. The source names no category, and no page count exists without compiling,
   which is never done to downloads. Requested from orch again (metadata mode).
2. Salmon, Moraes, Dror and Shaw, "Parallel random numbers: as easy as 1, 2, 3" (SC11): not
   in the store and cited by no paper of the corpus (no bibliography entry matches the
   title, Philox, Random123 or the authors; no chunk mentions Philox). It is not on arXiv
   (your request), and fetching a paper from a publisher has no sanctioned path, so it is not
   obtainable now; the [BACKGROUND] label stays. Requested from orch: whether a non-arXiv
   PDF may be fetched for such cases.

What the knowledge base lacked: the metadata path; any record of the SC11 paper.
