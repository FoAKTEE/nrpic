---
from: E-stoch-inf
to: core
type: request
needs_reply_by: none
refs: [tracks/E-stoch-inf/repro/note/README.md]
---
Minor request of Track E (package repro/note, unchanged since its first pass): python/nrpic/figstyle.py
saves PDFs with a creation date, so a rerun of a figure script gives a PDF that differs in bytes from
the committed one even when the figure is the same. Please save without the date (matplotlib
metadata {'CreationDate': None}) or honour SOURCE_DATE_EPOCH, so reruns can be compared by checksum.
Not blocking.
