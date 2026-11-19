# Journal of work package s39_frontier (brief lines 239-256, §3.9)

Owner kb (helper), wave 3a, branch `kb/brief-check`. Entries are appended; predictions are
written before the check they concern and are not edited afterwards.

## Entry 1, 2026-11-19T15:21Z: scope and predictions before reading any source

Scope. Brief lines 239-256 are the table "Developments in 2025-2026 and active groups"
(13 rows, 32 arXiv ids). No cell carries an explicit label; every cell of the second column
is a specific claim about a paper (authors, subject), and the third column is mostly the
author's [JUDGEMENT] with some claims about paper content inside ("Cosmological
Gamma-driver, multi-peak diagnostics"; "The gauge scheme can be borrowed directly"). I check
every second-column claim and every content claim in the third column at the source; pure
judgements are listed and not given a verdict. All 32 ids are already in the store
(`kb-data/raw/arxiv/<id>/<v>/src`, metadata in `kb-data/meta/arxiv-api/` and
`kb-data/meta/inspire/`), checked with `ls` at 15:20Z; no fetch is needed for the check.

Predictions (what would refute each is in brackets):

- P1. Every id's title and abstract match the direction of its row [refuted if any id is
  about a different subject].
- P2. The author list "Yoo, Escrivà, Harada, Kohri" is exact for 2609.14218, and
  2605.04487 has a different author set (the brief says "by the same authors") [refuted if
  2605.04487 has exactly the same four].
- P3. "Munoz, Byrnes, Bruni, Hawke" is the author list of 2610.23218 [refuted otherwise].
- P4. Under "Macpherson et al." and "Adamek et al." at least one of the three ids each is
  not first-authored by the named person [refuted if all six are].
- P5. The Gamma-driver and multi-peak diagnostics appear in at least one of 2608.13206,
  2609.03051, and these are 3+1 simulations in a radiation-dominated universe [refuted if
  either paper is spherically symmetric or matter-era only].
- P6. Among the three "relativistic Hills mechanism" ids at least one is not a
  full-relativity calculation (post-Newtonian or Newtonian three-body, or a test-particle
  calculation in a fixed spacetime) [refuted if all three evolve full GR].
- P7. 2504.15978 and 2509.19769 share at least one author with 2611.12831 [refuted if not].
- P8. 2610.32592 is a thesis by Launay alone; the table attributes all three ids to
  "Launay, Rigopoulos, Shellard" which is a group label, not an author list [refuted if
  2610.32592 has three authors].
- P9. At most 3 of the roughly 40 checked statements are CORRECTED [refuted if 4 or more].

Frontier search (FRONTIER.md), prediction. The brief's survey reaches 2611.15050, so papers
"after the survey" are those of the last days (2611.15xxx onward) plus earlier papers the
survey missed. Expected: forward citations of the cited ids number in the tens to low
hundreds in all; fewer than 10 papers dated after 2026-11-14 across all directions; most new
items are inflation and PBH papers, and none of them is a three-dimensional Einstein-Vlasov
particle calculation in cosmology [refuted if one exists: that would change the novelty of
tracks A or B].
