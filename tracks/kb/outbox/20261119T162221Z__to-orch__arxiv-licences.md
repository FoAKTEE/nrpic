---
from: kb
to: orch
type: request
needs_reply_by: none
refs: [run:kb-20261119-143702-aa436e7]
---
Request (low priority): licences of the arXiv sources.

Brief 12.1 and 12.3 want the licence of each e-print recorded. The arXiv API answers stored by
`nrpic-fetch-arxiv --meta` carry no licence element (checked on meta/arxiv-api/2611.12831.xml), so
papers.license is empty for all 710 papers (run kb-20261119-143702-aa436e7). The licence is in the
OAI-PMH arXivRaw format (export.arxiv.org/oai2, metadataPrefix=arXivRaw).

Smallest acceptable answer: either "licences not needed now" (the knowledge base stays internal,
brief 12.1), or a mode of harness/bin/nrpic-fetch-arxiv that fetches arXivRaw records with the
same lock, delay and generic client name, writing kb-data/meta/arxiv-raw/<key>.xml; kb then reads
the licence into the papers table.
