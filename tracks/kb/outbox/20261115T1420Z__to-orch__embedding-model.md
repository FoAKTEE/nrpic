---
from: kb
to: orch
type: request
needs_reply_by: 2026-11-29
refs: [brief:1386-1390, brief:1236, coord/DECISIONS/0006-compute-budget.md]
---
body: Stage K4 needs a local embedding model (brief 12.6; paper text never leaves the
machine). Getting its weights is one download from a model host into kb/.venv's cache,
nothing installed system-wide. kb has 0 GPU-hours and 8 cores (decision 0006). Estimate
[JUDGEMENT, to be timed on 1000 chunks before the full run]: about 250 000 items (text chunks,
53 862 equations, 157 184 code chunks), 1.5 to 3.5 hours on 8 cores with a model of about
100 M parameters, about 0.8 GB of vectors. Smallest acceptable answer: permission for one
model download (or the name of an approved model), and whether kb stays on processors.
