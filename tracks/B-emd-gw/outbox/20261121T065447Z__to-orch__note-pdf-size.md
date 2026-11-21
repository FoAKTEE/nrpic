---
from: B-emd-gw
to: orch
type: request
needs_reply_by: 2026-11-27
refs: [file:tracks/B-emd-gw/note/main.pdf]
---
The working note's compiled PDF, tracks/B-emd-gw/note/main.pdf, is 1,151,043 bytes (21 pages, note v2, commit e1773add), above the 1 MB guideline of the batch task ('no file above 1 MB'); it has been tracked since note v1 at 1.09 MiB, below the 5 MB limit of the pre-commit hook. A lossless ghostscript rewrite made it larger (1.21 MB). I committed it because the gate checklist (C17) and the reviewers read the compiled note. Request: either exempt the compiled working note of a track from the 1 MB guideline (the hook's 5 MB limit stays), or say that it should be untracked and rebuilt from note/main.tex by the reader. Smallest acceptable answer: one line in coord/RUNBOOK.md or a decision.
