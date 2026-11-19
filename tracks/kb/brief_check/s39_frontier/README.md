# Work package s39_frontier: check of brief lines 239-256 and the frontier after the survey

Owner kb (helper), wave 3a, 2026-11-19. Branch `kb/brief-check`, worktree `wt/kb-brief`.
Scope: brief §3.9 "Developments in 2025-2026 and active groups" (lines 239-256: a heading and
a table of 13 rows naming 32 arXiv ids). Every claim about a paper is checked at the TeX
source in the knowledge-base store; then, for each group and line of work, INSPIRE searches
(forward citations, topics, authors) for papers the brief does not cite, sorted by track.

## What is here

| Path | What |
|---|---|
| `CHECK.md` | one row per checked statement (44): brief line, quotation, label, verdict, locator, note; and the 13 judgements without a verdict |
| `ERRATA_ROWS.md` | 14 rows for `coord/BRIEF_ERRATA.md` in its format (4 wrong or incomplete, 8 imprecise, 2 superseded by a decision) |
| `FRONTIER.md` | what is new for tracks A to F and core since the survey, one line each on whether it changes a plan or overlaps |
| `JOURNAL.md` | predictions (entries 1, 3) and outcomes (entries 2, 4), including the failed ones (P9; the track ordering of entry 3) |
| `scripts/locate.py` | regex search of the TeX sources in `kb-data/raw/arxiv/`, printing file:line locators (read-only; fields of the spec separated by " \| " so the regex may use "\|") |
| `scripts/meta_dump.py` | titles, authors, dates, abstracts from `kb-data/meta/arxiv-api/` (read-only) |
| `scripts/run_inspire.py` | runs the INSPIRE queries of a spec file one after the other through `harness/bin/nrpic-fetch-arxiv --inspire-query` |
| `scripts/frontier_scan.py` | merges query results: distinct papers, whether the brief cites them, whether the store has them, abstracts, forward-citation counts |
| `scripts/fig_frontier.py`, `scripts/figstyle.py` | tally of CHECK.md and the figure (vendored copy of `harness/style/figstyle.py`) |
| `specs/r*.txt` | the locator searches behind CHECK.md |
| `specs/inspire_queries.txt`, `specs/inspire_queries2.txt` | the 74 INSPIRE queries |
| `specs/nov2026_ids.txt` | the ids whose arXiv records were fetched for exact dates |
| `figures/fig_frontier.png` | figure of run kb-20261119-153319-ad2a3a7: (a) verdicts per brief line, (b) forward citations of the 32 ids, split by whether the brief cites the citing paper, (c) papers not cited in the brief per arXiv month, by track (grey line: month of the survey) |

## Results in one paragraph

Of 44 checked statements, 37 are confirmed at the source (16 with a precision) and 7
corrected. Wrong about papers: 2605.04487 is not by "the same authors" (Terada added) and is
Newtonian-gravity N-body, not full NR; 2610.23218 has no finished gauge scheme to borrow (its
own conclusion: further gauge work is needed for stability); 2610.13294 treats the Hills
encounter in Newtonian dynamics; 2506.17641 computes no relativistic collapse; three ids of a
"2025-2026" table are from 2024. Superseded: "potential collaborators" (decision 0017) and
the use of gevolution and GRTresna as codes (decision 0010). Frontier: 284 papers found, 226
not cited in the brief; only one is dated after the survey (2611.23627, an AthenaK refinement
criterion, 2026-11-17); none is a 3D Einstein-Vlasov cosmology run, a full-GR Hills
disruption, a 3D kinetic GR SIDM collapse or full NR with particle dark matter.
2611.12831 has no citing paper in INSPIRE yet. Plan-relevant: for C, a recalibration of the
gravothermal conductivity interpolation (2610.28890) and a Newtonian collapse time against
Knudsen number (2610.28745); for D, a general-relativistic Eddington inversion (2610.33150)
and closed-form GR spikes (2611.08145); for F, the first full-NR three-hole runs with a
Hills-criterion check, in the non-disruptive regime (2605.20320).

## How to rerun

```bash
cd /data/haiyangw/nrpic/wt/kb-brief
P=tracks/kb/brief_check/s39_frontier
python3 -I $P/scripts/locate.py $P/specs/r243_245.txt          # locators (also r246_249, r250_255, r253_255, r_extra)
python3 -I $P/scripts/meta_dump.py 2609.14218 2605.04487         # metadata
# INSPIRE queries (network, machine-wide lock; registered):
harness/bin/nrpic-run submit --kind scouting --gate G2 --package $P --launcher local --background --cores 1 \
  --purpose "..." -- python3 -I $P/scripts/run_inspire.py $P/specs/inspire_queries.txt '$NRPIC_RUN_DIR/queries.tsv'
# tally, scan and figure (registered):
harness/bin/nrpic-run submit --kind scouting --gate G2 --package $P --launcher local --cores 1 \
  --purpose "..." -- python $P/scripts/fig_frontier.py <run1>/queries.tsv <run2>/queries.tsv
```

A rerun of the INSPIRE queries returns today's index, so counts grow with time; the stored
results of the runs below are what this package used.

## Runs

| Run id | What | State |
|---|---|---|
| kb-20261119-152359-851b963 | 59 INSPIRE queries (forward citations of the 32 ids; topic and author queries per row) | completed |
| kb-20261119-152939-22939e5 | 15 INSPIRE queries (Track D, extra topics, the last weeks) | completed |
| kb-20261119-153125-0836e49 | arXiv API metadata of 15 of the newest candidates (exact dates) | completed |
| kb-20261119-153240-15320f5 | tally, scan and first figure | completed; figure superseded by the next run (layout only, numbers identical) |
| kb-20261119-153319-ad2a3a7 | tally, scan and figure (the one used) | completed |

All on processors, one core, under a minute each; no card time. Output under
`scratch/kb/<run_id>/`.

## Not done

- Frontier papers are summarized from their INSPIRE abstracts; full texts were read only
  for the three already in the store (2605.20320, 2609.14755, 2604.27429). No new source was
  fetched.
- The week 2026-11-12 to 11-19 is covered only as far as INSPIRE had indexed it (it lags
  arXiv by days); the arXiv listing cannot be searched with the fetch tool.
- Topic searches were limited to the directions of lines 243-255 plus Track D; e.g. Track B's
  plane-symmetric pancake literature was not searched here.
- The kb database was not written (helper rule): the new papers are not ingested.

## Requests

- To kb (lead): ingest into the knowledge base the papers FRONTIER.md marks as plan-relevant:
  2610.28890, 2610.28745 (C); 2610.33150, 2611.08145, 2611.13170 (D; 2609.14755 is already in
  the store); 2610.01964 (A); 2610.26669, 2602.11652, 2606.28005 (E); 2605.22525 (F;
  2605.20320 and 2604.27429 are in the store); 2611.23627 (core). Then forward
  `ERRATA_ROWS.md` to the orchestrator for `coord/BRIEF_ERRATA.md`.
- To C-sidm: check whether the gravothermal fluid reference of Track C interpolates the long-
  and short-mean-free-path conductivities harmonically; 2610.28890 finds that inaccurate and
  gives a gentler transition calibrated on a softening-free spherical DSMC code; take the
  Newtonian collapse time against Knudsen number of 2610.28745 as the Newtonian baseline of
  the Kn scan (FRONTIER.md, Track C).
- To D-bh-dress: consider 2610.33150 (general-relativistic Eddington inversion), 2611.08145
  (Einstein-cluster spike with closed-form metrics) and 2609.14755 (self-consistent static
  Einstein-Vlasov environments) as reference solutions for the strong-field spike, and
  2611.13170 (spike depletion by mergers) for the motivation of dressed binaries.
- To F-hills: cite 2605.20320 (full-NR triples, non-disruptive by construction) as the
  nearest full-NR work, and compare the regime boundaries of 2605.22525 with the pericentre
  scan line.
- To E-stoch-inf: check the inflection-point test potential for the hidden higher-derivative
  spikes of 2606.28005, and add the UV sensitivity of 2610.26669 to the acceptance discussion.
- To core: 2611.23627 (2026-11-17) implements a five-point smoothness indicator as a
  refinement criterion in AthenaK, tested in Newtonian, SR and GR MHD; a candidate for the
  refinement criteria of the periodic-mesh work (information, no change asked).
- To A-emd-pbh: 2610.01964 locates a line of critical solutions with 35 runs against 270 for
  bisection (automatic differentiation); a benchmark for the threshold-line budget only.
- To orch: rows s39.1-s39.14 of `ERRATA_ROWS.md`; row s39.13 also reflects decision 0017 on
  the brief's "potential collaborators".
