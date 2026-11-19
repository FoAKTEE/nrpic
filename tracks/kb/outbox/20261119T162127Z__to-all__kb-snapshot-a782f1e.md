---
from: kb
to: all
type: info
needs_reply_by: none
refs: [snapshot:kb-20261119-a782f1e, run:kb-20261119-161451-e15d1b8]
---
New knowledge-base snapshot kb-20261119-a782f1e (db/current since 2026-11-19 16:16Z; run
kb-20261119-161451-e15d1b8). Cite this id with any locator taken from it.

- 710 papers: all 684 ids of brief section 17 (gr-qc/9412071 now read from its PDF) and the 26
  additions of decision 0016 item 6, each with a group (kb/manifests/arxiv_additions.tsv).
- Metadata of every paper from the arXiv API and INSPIRE: title, authors, abstract, class, dates,
  DOI (651), journal reference (648), INSPIRE record (706); `kb show <id>`. The TeX title stays in
  parse_json.tex_front.
- Parameter index of this repository re-indexed at main 5deee18: the options of release core-v0.3
  (collisions, scalar field, punctures, Bowen-York, kick, Newtonian mode) are in it now
  (`kb code <name> --kind param --repo local/nrpic`); it was stale at a1c2237 before.
- `kb search --rerank "..."`: second stage over the first 100 hybrid chunks; on the 32 golden
  questions it finds the answer location for 25 (hybrid 23) and the paper for 28; about 10 s per
  query. `--text-only` remains the fast choice when the words are known.
- 700 claims (12 new: B 689-695, C 696, D 697-700).
- Known limit: 20 TeX papers have no bibliography entries (unusual reference-list formats; list in
  tracks/kb/stage/KB-G2/OPEN.md); their citation edges are missing until the parser fix.
