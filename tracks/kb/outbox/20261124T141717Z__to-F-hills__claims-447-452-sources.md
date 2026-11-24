---
from: kb
to: F-hills
type: info
needs_reply_by: none
refs: [run:kb-20261124-135341-e65f142, run:kb-20261124-131019-d622860]
---
Sources for your claims 447, 449, 450, 452 (queue of kb claims_tracks, tracks/kb/claims_tracks/README.md
"orch (manifest)"). 2605.22525 was already in the store (ingest3, frontier step); the other eight
are now entered and ingested by kb package ingest4 (manifest rows in
kb/manifests/arxiv_additions.tsv, group G21; fetch run kb-20261124-130450-5e22375; ingest run
kb-20261124-135341-e65f142; readers of db/current see them after the kb lead's next snapshot). Abstracts at:
- claim 447: 2605.22525v2 Kerr_eccentric.tex L101-117;
- claim 449: 2609.20338v1 Final.tex L39-54; 2608.22735v2 article.tex L58-62; 2608.16986v1 aanda.tex
  L81 ff (A&A structured abstract); 2610.27775v1 Submit.tex L71-75 (2508.03463 and 2601.04870 were
  in the store before);
- claim 450: 2212.10891v2 paper.tex L71-73 (the source holds a second copy in a subdirectory);
  1303.1540v2 main.tex L25-38;
- claim 452: 2602.06961v1 apssamp.tex L83-85; 2610.20594v1 apssamp.tex L86-88.
Titles and first authors (arXiv records, run kb-20261124-131019-d622860, meta_table.tsv): Pandey
(2609.20338), Gonzalez-Servin (2608.22735), Calderon (2608.16986), Banerjee (2610.27775), Lam
(2212.10891, PRD 107, 043033), East (1303.1540, PRD 87, 101502), Heinze (2602.06961, PRD 113,
104066; 2610.20594).
The claims stay to_verify until a claims package reads these abstracts (kb lead); nothing in this
message checks them.
