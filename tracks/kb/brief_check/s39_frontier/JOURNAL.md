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

## Entry 2, 2026-11-19T15:32Z: outcomes of entry 1 (source check and query runs)

Runs: kb-20261119-152359-851b963 (59 INSPIRE queries: forward citations of the 32 ids and
topic/author queries per row; completed, 0 failed, none truncated at 25 hits),
kb-20261119-152939-22939e5 (15 queries: Track D topics, extra topics, last weeks; completed),
kb-20261119-153125-0836e49 (arXiv API metadata of 15 of the newest candidates; completed).

- P1 held: all 32 ids match the subject of their row (CHECK.md rows 2-36).
- P2 held: authors of 2609.14218 exact (`MDPBH.tex:131-134`); 2605.04487 has five authors,
  Terada added (`main_v3.tex:144-148`).
- P3 held (`2610.23218 main.tex:21`).
- P4 held, more than predicted: of the six ids under "Macpherson et al." and "Adamek et al.",
  two are not first-authored by the named person (2606.18437, 2603.24179) and one is
  single-author (2603.24838).
- P5 held: the scaled Gamma-driver is in 2608.13206 (GRChombo, radiation fluid), the
  multi-peak diagnostic in 2609.03051 (COSMOS, radiation); both 3+1.
- P6 held: none of the three Hills papers is full GR (HRNA, freely falling tidal frame,
  Newtonian three-body in a population model).
- P7 held: Wu and Most on all three.
- P8 held: 2610.32592 is Launay's thesis, single author (`preword.tex:18, 107`).
- P9 FAILED: 7 rows are CORRECTED, not at most 3 (5 about papers, 2 about the project
  relation). I had underestimated how often the table's one-word subject labels ("relativistic
  Hills mechanism", "relativistic SIDM collapse", "by the same authors") misdescribe a paper.
- Frontier prediction, partial outcome (final numbers in entry 3): 284 distinct papers in
  all query results, 226 not cited anywhere in the brief, 11 of them from 2026-11 and only
  one (2611.23627, 2026-11-17) dated after the brief's newest id (2611.15050); the other ten
  (2026-11-02 to 11-11) were missed by the survey. Forward citations total far fewer than
  "tens to low hundreds" for the newest ids (2611.12831 has none in INSPIRE). No
  three-dimensional Einstein-Vlasov particle calculation in cosmology was found among the
  titles and abstracts: that part of the prediction held. Caveat: INSPIRE indexes with a lag
  of days, so the window 2026-11-12 to 11-19 is covered only as far as INSPIRE had it at
  15:24-15:31Z.

## Entry 3, 2026-11-19T15:33Z: prediction for the tally and figure run

Command: `scripts/fig_frontier.py` on the two queries.tsv files (registered run, README).
Prediction: the tally of CHECK.md gives 44 rows, 21 CONFIRMED, 16 CONFIRMED (precision),
7 CORRECTED, 0 NOT FOUND, 0 unclassified; the scan reproduces 284 / 226 / 11 of entry 2.
Among papers not cited in the brief and dated 2025-01 or later, Track C (SIDM: a large
astrophysics community) has the most, then D, B and E; A and F the fewest. Refuted if the
counts differ from these numbers, or if A or F is not among the two smallest.
