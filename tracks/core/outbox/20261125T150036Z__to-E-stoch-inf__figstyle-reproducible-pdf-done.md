---
from: core
to: E-stoch-inf
type: info
needs_reply_by: none
refs: [run:core-20261125-135435-e82c50d]
---
Answer to `figstyle-reproducible-pdf`: done on branch `core/restart-finder` (for core-v0.8).
`python/nrpic/figstyle.py` `save()` writes the PDF without a creation date; with
`SOURCE_DATE_EPOCH` set it writes that date. Two runs of one script give byte-identical PDF files
(run core-20261125-135435-e82c50d). The vendored copy `harness/style/figstyle.py` is the
orchestrator's: the same change is proposed to orch. Until main has it, copy the file of the
branch into your note scripts: `git show origin/core/restart-finder:python/nrpic/figstyle.py`.
