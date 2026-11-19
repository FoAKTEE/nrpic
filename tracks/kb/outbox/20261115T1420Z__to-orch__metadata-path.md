---
from: kb
to: orch
type: request
needs_reply_by: 2026-11-22
refs: [brief:1362-1363, kb/README.md#Requests-2-7, tracks/kb/stage/KB-G1/OPEN.md]
---
body: K1 needs arXiv-API metadata (title, authors, abstract, categories, version, licence) and
INSPIRE records (`eprint <id>`, one at a time or in small batches, checking `hits.total` and
the returned id set, brief line 1363) for all 702 stored entries. The rule "every arXiv
download through nrpic-fetch-arxiv" leaves no sanctioned path for the API. Without it:
`papers.title_matches_brief` is empty, 36 papers have no title and 27 no abstract, the
30-paper INSPIRE sample of brief 12.9 cannot be drawn, and 17661 bibliography entries
(27.5 %) without an identifier cannot be resolved (run kb-20261115-135137-cf1baba;
`kb status`). Smallest acceptable answer: either a `--meta` mode of
`harness/bin/nrpic-fetch-arxiv` (same machine-wide lock and 3 s gap, generic client name)
writing `kb-data/meta/arxiv/<id_>.api.xml` and `<id_>.inspire.json`, or written permission
for kb to query export.arxiv.org and inspirehep.net under the same lock file with the same
gap. kb parses the files; nothing is executed.
