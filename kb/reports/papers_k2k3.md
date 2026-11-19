# Papers, stages K2-K3: state of the store and the database (2026-11-15, 14:00 UTC)

Counts only; no paper text. Snapshot `kb-data/db/kb-20261115-5ba1ab3.sqlite` (run
`kb-20261115-135747-5505dbe`) is `db/current`. Runs are registered under `tracks/kb/runs/`; predictions and
outcomes in `kb/JOURNAL.md` (D2, K2-P1 to K2-P8).

## Downloads (brief section 17 manifest, 684 arXiv ids)

| | |
|---|---|
| download run | `kb-20261115-124340-9048b83`: one process (`kb fetch-missing --priority 3 2 1`, exec of `harness/bin/nrpic-fetch-arxiv`), 599 ids, 12:43-13:27 UTC, 599 store paths printed, stderr empty |
| verify run | `kb-20261115-132730-a51e26e` (`reports/verify-downloads.md`) |
| manifest entries in the store and verified | 683 of 684 (priority 3: 47 of 47, priority 2: 160 of 160, priority 1: 476 of 477) |
| failed downloads | 0 |
| problem | 1: gr-qc/9412071, arXiv serves only a gzipped PostScript file, stored by the fetch command as `src/main.tex` |
| extras added by other sessions | 18 |

## Ingestion (`kb ingest arxiv --all --extras --jobs 8`, run `kb-20261115-135137-cf1baba`, 237 s)

| | manifest (684) | extras (18) |
|---|---|---|
| ok (parse score >= 0.75) | 658 | 18 |
| review (score < 0.75; 18 of 23 have neither \\title nor an abstract environment) | 23 | 0 |
| pdf only (pdftotext, no equations): 2201.03458 | 1 | 0 |
| failed: astro-ph/9407016 (PostScript files only, no TeX) | 1 | 0 |
| not ingested: gr-qc/9412071 (download problem) | 1 | 0 |

Priority 3: 47 of 47 ingested (45 ok, 2 review: gr-qc/9906015 plain TeX, 2009.08715 no \\title).

Rows: papers 701, sections 13186, chunks 71069 (body 29712, appendix 2219, caption 6584,
footnote 3914, abstract 674, comment 27966), equations 52755 (25595 labelled), figures and
tables 6655. Mean parse score 0.963. Titles from \\title: 665 of 701; abstracts: 674.

## Bibliography and citation graph

| | |
|---|---|
| bibliography entries | 64248 (source: .bbl 400 papers, .bib 49, thebibliography 230) |
| with an arXiv id | 38636 = 60.1 % (written id 38343, corpus title match 293) |
| DOI only | 7951; no identifier 17661 (27.5 %; need INSPIRE, Request 2) |
| citations (key occurrences) | 103808; 910 keys without an entry (0.88 %) |
| distinct citation edges with an arXiv id | 38268, of which inside the corpus 5653 = 14.8 % |
| in-corpus edges inside one group of brief section 16 | 53.2 % (6.4 % expected at random) |

## Independent checks (run `kb-20261115-135554-d405f64`, `scripts/papers_checks.py`)

| check | result |
|---|---|
| C1 main file by the heuristics alone vs 00README.json | 115 of 115 agree |
| C2 .bib parser vs bibtexparser 2.1 | key sets equal in 50 of 52 files; 8 of 17101 eprint/doi values differ (duplicate keys, an empty key, a block bibtexparser rejects) |
| C3 stored entries vs \\bibitem count | 621 of 634 papers agree (the one examined disagreement is \\bibitem text after \\end{document}) |
| C4 labels in display environments stored | 25654 labels; 14 not in rows, all examined: 12 after \\end{document}, 2 figure labels the checker's regex swept in |
| C5 citation keys without an entry | 910 of 103808 |
| C6 blind fuzzy title matching vs the written arXiv id | 1482 of 1697 matched at ratio >= 0.93, all correct (precision 1.0, recall 0.873) |
| numbering vs LaTeX (synthetic documents, pdflatex .aux; article, \\numberwithin, revtex4-2) | all labels equal (tests/test_tex_numbering.py) |

Figures: `fig_papers_k2.png` (top left: parse scores; top right: equations against sections per
paper; bottom left: words per chunk by kind, target band grey; bottom right: fraction of
bibliography entries with an arXiv id, blue, or a DOI only, yellow, per paper);
`fig_citations_k3.png` (left: in-corpus citation edges by group of the citing and the cited
paper; right: the 25 works cited by most corpus papers but absent from the corpus).

## Frontier (`kb frontier -n 50`; arXiv id and number of corpus papers citing it)

1807.06209 (81), gr-qc/9810065 (66), astro-ph/0411220 (55), 1807.06211 (53), astro-ph/9507001 (43), 1104.2933 (42), 1602.03837 (42), 1801.05235 (38), 1502.01589 (36), 2006.02838 (36), 2007.10722 (36), 0809.4944 (35), gr-qc/9801017 (35), 1603.08338 (34), 1702.00786 (34), 1110.3193 (33), 1603.00464 (33), astro-ph/0505010 (32), 1811.12907 (31), 0912.5297 (30), astro-ph/0210603 (29), 0912.0201 (27), 1804.07124 (27), astro-ph/9605094 (27), 1702.03901 (26), astro-ph/9506072 (26), gr-qc/0405109 (26), 1805.03946 (25), 1908.11357 (25), astro-ph/0504045 (25), astro-ph/9707278 (25), 1607.06077 (24), 1611.00036 (24), 1811.11158 (24), 2007.05564 (24), 2011.03014 (24), 2211.13932 (24), gr-qc/0102049 (24), 1004.2488 (23), 1805.04087 (23), 1810.11000 (23), 1905.13202 (23), 1703.00447 (22), astro-ph/0111367 (22), astro-ph/9805201 (22), gr-qc/9412071 (22), 1805.06731 (21), 1811.02175 (21), 1904.00984 (21), 2109.00791 (21)

All are outside the manifest except gr-qc/9412071 (in the manifest, PostScript only).
