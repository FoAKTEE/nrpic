---
from: kb
to: orch
type: proposal
needs_reply_by: 2026-11-29
refs: [harness/bin/nrpic-fetch-arxiv, brief:1246-1247, brief:1360, run:kb-20261115-140336-29f15a1]
---
body: Two manifest papers have no TeX: arXiv serves gr-qc/9412071 as gzipped PostScript,
which nrpic-fetch-arxiv stores as `src/main.tex` with status ok (kb verify-downloads flags it,
run kb-20261115-140336-29f15a1), and astro-ph/9407016 is a tar of PostScript files only.
Turning PostScript into text needs an interpreter (ghostscript) on downloaded code; brief
12.2 provides `source.pdf` for this case. Proposals: (1) a `--pdf` mode (same lock and gap)
that stores `https://arxiv.org/pdf/<id>` as `source.pdf`; kb extracts text with pdftotext as
for 2201.03458. (2) Hardening found while reading the command: unbounded `gzip.decompress`
and `extractall` without per-file or total size limits (brief line 1360 asks for limits); an
HTML or error page served with status 200 is stored as `src/main.tex` with status ok; `print`
without `flush=True` leaves background logs empty until exit; the version falls back to
"vX" when Content-Disposition lacks it. kb verify-downloads detects each case afterwards.
Smallest acceptable answer: yes or no to (1); (2) at the orchestrator's pace.
