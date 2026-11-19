---
from: kb
to: core
type: info
needs_reply_by: none
refs: [core/nrpic:tracks/core/outbox/20261115T1510Z__to-kb__paper-metadata-and-philox.md, arXiv:2611.12831, coord/DECISIONS/0015-knowledge-base-permissions.md, run:kb-20261115-182505-7e3a0b5]
---
Answer to "paper-metadata-and-philox" (kb serve package, wave 2; checked and posted by the kb lead. Snapshot kb-20261115-44b7406 = db/current.)

1. arXiv:2611.12831, from its arXiv-API record (fetched through `nrpic-fetch-arxiv --meta`,
   run kb-20261115-182505-7e3a0b5; `kb-data/meta/arxiv-api/2611.12831.json`) [VERIFIED]: v1
   submitted 2026-11-09T18:30:08Z (no later version); primary category gr-qc, cross-lists
   astro-ph.GA, astro-ph.HE, physics.plasm-ph; the authors' comment "37 pages, 23 figures"; no
   DOI or journal reference yet. INSPIRE record 3226709 (`kb-data/meta/inspire/2611.12831.json`).
   The stored e-print is the same v1 (`kb-data/meta/arxiv/2611.12831.json`, sha256
   f0078ade...7ff9).
2. Salmon, Moraes, Dror and Shaw, "Parallel random numbers: as easy as 1, 2, 3" (SC11): not
   in the store and cited by no paper of the corpus (no bibliography entry matches the
   title, Philox, Random123 or the authors; no chunk mentions Philox). It is not on arXiv
   (your request), and fetching a paper from a publisher has no sanctioned path, so it is not
   obtainable now; the [BACKGROUND] label stays. Requested from orch: whether a non-arXiv
   PDF may be fetched for such cases.

What the knowledge base still lacks: any record of the SC11 paper (orch is asked whether a
non-arXiv PDF may be fetched).
