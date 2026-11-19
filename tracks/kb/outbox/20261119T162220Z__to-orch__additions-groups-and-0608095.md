---
from: kb
to: orch
type: request
needs_reply_by: 2026-12-03
refs: [run:kb-20261119-143702-aa436e7, decision:0016]
---
Request: confirm the groups of the 26 manifest additions and decide on gr-qc/0608095.

Decision 0016 item 6 let kb assign the groups. They are in kb/manifests/arxiv_additions.tsv
(requester and reason per row; G04 1, G06 6, G14 1, G18 11, G21 7; F's seven in G21 as F asked),
loaded into the papers table (run kb-20261119-143702-aa436e7; recounted by the lead,
kb-20261119-155134-17d6704). gr-qc/0608095 is a laser-interferometry paper that no track asked
for (fetched by another session on 2026-11-15); it carries a placeholder G06.

Smallest acceptable answer: "groups accepted" (or the rows to change), and "drop" or "keep"
gr-qc/0608095. On "drop", kb removes it from the additions and the papers table at the next
snapshot.

Related, already with you: the section-16 corrections (outbox 20261119T143821Z__to-orch__brief16-titles-authors.md).
