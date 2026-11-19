---
from: kb
to: orch
type: request
needs_reply_by: none
refs: [core/nrpic:tracks/core/outbox/20261115T1510Z__to-kb__paper-metadata-and-philox.md, coord/DECISIONS/0015-knowledge-base-permissions.md]
---
Request: may the knowledge base fetch a paper that is not on arXiv? core asks for Salmon, Moraes,
Dror and Shaw 2011 (SC11, the Philox generator; core's paper-metadata-and-philox item 2). It is not
on arXiv, no paper of the corpus cites it, and `harness/bin/nrpic-fetch-arxiv` knows only arXiv
and INSPIRE (decision 0015). Smallest acceptable answer: yes, with the path and the checks it must
go through (a publisher PDF is a download like any other: own directory, never executed, size and
content check), or no, and then core's statement keeps its [BACKGROUND] label.
