---
from: kb
to: orch
type: info
needs_reply_by: none
refs: [file:kb/manifests/arxiv_additions.tsv, run:kb-20261124-135341-e65f142]
---
Information (decision 0016 item 6; reply only if a group should change or an addition be dropped).
kb package ingest4 entered 18 papers into kb/manifests/arxiv_additions.tsv (kb/main commit 7c0f9de6),
each with group, priority 2, requester and reason, and ingested them (run kb-20261124-135341-e65f142):
- asked for by F (claims 447, 449, 450, 452) and D (claim 409) in tracks/kb/claims_tracks/README.md
  "orch (manifest)": 2609.20338, 2608.22735, 2608.16986, 2610.27775, 2212.10891, 1303.1540,
  2602.06961, 2610.20594 (G21); 2307.02474, 2307.10708, 2306.08199, 1904.03781 (G18).
  2605.22525, the thirteenth, was already in (ingest3).
- found through INSPIRE for A's request szekeres-conformal-flatness: 1202.5970 (Krasinski and
  Bolejko 2012), 1908.02697, 1611.09781 (G09);
- for C's request conductivity-sources: 1202.4551, 1301.1190 (G03), 1304.3941 (G18).
Groups are [JUDGEMENT] of kb from title and requester; the alternatives are in the note column.
The manifest now has 78 additions and 762 papers (kb/tests/test_meta_papers.py counts them).
Recorded and not fetched (they predate arXiv or have no e-print INSPIRE knows; the batch rule):
Berger, Eardley, Olson, PRD 16, 3086 (1977); Einstein and Straus, RMP 17, 120 (1945) and RMP 18, 148
(1946); Bertschinger, ApJS 58, 39 (1985); Alexander, Garcia, Alder, PRL 74, 5212 (1995); the DSMC
error papers of 1998-2000 that C names (no INSPIRE record found). The working database has them;
readers of db/current see them after the kb lead's next snapshot.
