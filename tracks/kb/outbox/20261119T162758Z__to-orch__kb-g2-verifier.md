---
from: kb
to: orch
type: request
needs_reply_by: 2026-12-03
refs: [snapshot:kb-20261119-a782f1e, run:kb-20261119-161633-1d05960]
---
Request: a verifier (fresh agent, given the artefacts, not the conclusions) for KB-G2.

What it should recompute from the snapshot kb-data/db/kb-20261119-a782f1e.sqlite and the run
manifests, with its own code: (1) papers and repositories ingested against kb/manifests (arxiv.tsv
plus arxiv_additions.tsv, github.tsv); (2) the parse success rate, and whether status ok means
parsed (sample of papers against their TeX source, as the KB-G1 verifier did for bibliographies);
(3) the golden-question hits of kb/QA_REPORT.md (run kb-20261119-161633-1d05960) by rerunning
kb search in the three modes on the 32 questions of kb/golden/questions.yaml and scoring them
independently; (4) a reading sample of ten golden hits at the answer location (does the chunk
answer the question?).

Why: CHECKLIST item C8 of tracks/kb/stage/KB-G2 is FAIL without it; the KB-G1 verifier explicitly
did not check retrieval or parse rates. kb uses no card time; the QA run takes about 10 minutes on
6 threads.

Smallest acceptable answer: a verifier package assigned in the next wave (tracks/kb/stage/KB-G2/VERIFIER.md).
