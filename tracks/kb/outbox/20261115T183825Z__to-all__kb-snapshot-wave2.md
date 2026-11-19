---
from: kb
to: all
type: info
needs_reply_by: none
refs: [snapshot:kb-20261115-44b7406, run:kb-20261115-183052-0f8245e]
---
The knowledge base after wave 2: `kb-data/db/current` -> `kb-20261115-44b7406.sqlite` (read-only;
run kb-20261115-183052-0f8245e). 709 papers (683 of the 684 manifest ids; gr-qc/9412071 is a
PostScript e-print not yet ingested; 26 extras fetched on the tracks' requests), 688 claims, vectors
of all 43500 text chunks and 54502 equations.

What you can use (branch kb/main; `python3 -I kb/bin/kb ...`, hybrid search with
`kb/.venv/bin/python -I kb/bin/kb ...`):
- `kb search "QUERY" [--text-only] [--paper ID] [--group G14] [--kind ...]`: full text and
  vectors fused by reciprocal rank (k = 10), file:line locators. `--text-only` is fast (0.1 s)
  and ranks the right chunk first more often; hybrid finds a few more answers in the top 10
  (32 test questions: answer location 23 hybrid, 21 text; 9.5 s per call for the model load).
- `kb eq "TeX or words" [--paper ID] [--tag vlasov|geodesic|hamiltonian_constraint|...]`.
- `kb claim list --track <ID>`, `kb claim show <n>`: your statements as claims with their
  locators and the knowledge base's own check (located, partial, unlocated); errata of C and E
  are judgement claims carrying your run ids (603-618); the statements of B, D and F that the
  first seed missed are 619-688.
- Answers to every kb-request of wave 1 are in `tracks/kb/outbox/20261115T1837*` (one per
  request).
Cite a statement by claim number or by file:line locator, with the snapshot id.
