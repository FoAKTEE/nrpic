# JOURNAL of the kb serve package (wave 2, helper of kb)

Predictions are written before the run; outcomes after it, also when the prediction failed.
Times UTC, 2026-11-15.

## S0 15:25 Inventory of the requested ids (no prediction: read-only query run before this
journal existed)

`scripts/presence.py` against `db/current` = `kb-20261115-f2fcda5.sqlite`: of the 77
(request, id) pairs named in the nine kb-requests, 76 are in the raw store and ingested;
2605.30145 (A) is absent. Eight requested papers are extras without a group (F's seven
fetched by F's helpers, D's 1707.06302). Thin parses among them: 1901.04498 (1 section,
0 equations), 1505.04756 (0 sections), 2506.17641 (1 section), 0710.0879 (0 sections,
0 equations, review), 2403.15126 (review, 0 bibliography entries), gr-qc/0107076 and
1201.4794 (0 bibliography entries).

## S1 15:35 Fetch of 2605.30145 (prediction)

Prediction: arXiv serves a TeX source for 2605.30145 (A names it "spherical CDM-peak
collapse"); `nrpic-fetch-arxiv` stores it with status ok and kind tar or gzip-tex.
Refuted if the endpoint answers "not found" (identifier does not exist) or the record is
not ok.

Outcome S1 (run kb-20261115-152541-e02d870, registered by hand with
`kb/scripts/registered_run.py`: `nrpic-run submit` refused because another helper's
untracked `tracks/kb/embed/` makes the worktree dirty): prediction held. 2605.30145 v1,
status ok, kind tar (13.7 MB; `main.tex`, `references.bib`), fetched 15:25:52Z.

## S2 15:40 verify-downloads and ingest of the new entry (prediction)

Prediction: `kb verify-downloads` lists 2605.30145 among the extras with status ok and 0
missing; `kb ingest arxiv --new --extras` ingests exactly one paper, 2605.30145, with
parse_status ok, at least 5 sections, 10 equations and 20 bibliography entries
(gr-qc/9412071, PostScript only, is skipped as before). Refuted if any other paper is
(re)ingested, or the new paper parses as review/failed or below those counts.
