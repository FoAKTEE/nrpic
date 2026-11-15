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

Outcome S2 (runs kb-20261115-152614-8a93349 verify-downloads, kb-20261115-152647-ca81acd
ingest): prediction held. verify-downloads: 684 manifest rows ok 683, problem 1
(gr-qc/9412071, as before), missing 0, extras 19 (2605.30145 ok, gzip-tar, tex; exit code
1 is the known PostScript problem). Ingest `--new --extras`: 2 candidates, gr-qc/9412071
download-problem (skipped), 2605.30145 ok, score 0.9995, 36 sections, 185 equations, 107
chunks, 162 bibliography entries.

## S3 16:05 Locator check and claims load (tool built here; prediction for the registered run)

Built `kb/serve_locate.py` (track `file:line` -> flat.tex range, section, chunks,
equations, figures by inverting `build/tex/<id_>/sourcemap.json`; number check at the
source; claims load under the writer lock, origin `served:<key>`, idempotent),
`kb/serve_tests.py` (6 tests, synthetic inputs, pass), the extractor
`scripts/extract_track_locators.py` (A, B reference files; C report section 6; F scoping
section 8 and `newton3/hills3/reference.py`), 27 hand-written entries
`claims/manual.jsonl` (C, D, E errata and notes; F README locators), the driver
`scripts/run_serve.py` and `scripts/fig_serve.py`.

Debugging used unregistered dry runs in `scratch/kb/tmp/serve/` (nothing written to the
database). Two parser defects found that way and fixed before the registered run: numbers
written as percentages (`19\%` for F's fraction 0.19) and numbers glued to a TeX command
(`\mu\geq0.05`) were not counted, so 15 correct locators looked wrong. One locator of D
(1805.09034 `main.tex:195`) holds the citation but the slope r^{-3/2} is in the equation at
lines 197-200; the entry now spans 195-200. The last dry run gave: 330 statements, 372
locators, all 372 resolve to lines inside the stored source and into flat.tex (370 exact,
2 partial); 2 rows carry no paper locator (C row astro-ph/0111176 without a file; F row on
`athenak/src`); 132 statements quote numbers: 117 all found in the located lines, 2 all
within three lines, 13 with numbers not found.

Prediction for the registered run (same inputs, deterministic code): the same counts; 330
claims loaded with consecutive new ids, because the claims table was empty at 15:23
(`kb status`). Refuted if any count differs, or the ids are not consecutive (another writer
of claims at the same time).

Outcome S3 (run kb-20261115-153751-e164901; the `--run-id` argument was passed as the
literal RUNID_PLACEHOLDER by my mistake, so the loaded rows named that instead of the run
id). Counts held exactly (330 statements, 372 locators all resolved, numbers 117/2/13);
330 claims loaded with consecutive ids, but 623-952, not from 1: the premise of the
prediction was false. A second helper of kb (K8 claims layer, commit 595d313,
`tracks/kb/claims/`) had seeded 622 claims from the same track notes at 15:37:15Z, 36 s
before my load. At 15:39:43Z its `kb claim seed --rebuild` emptied all claim tables
(ingest_log) and re-seeded 618 claims with ids 1-618; my 330 rows are gone (checked:
0 rows with origin `served:%`).

Decision [JUDGEMENT]: the K8 layer (`kbtool/claims_*.py`, `kb claim`) owns the claims; my
rows duplicated 265 of its claims and bypassed its side tables (claim_meta,
claim_locators, claim_events). This package therefore writes no claims. It maps each
served statement to the K8 claims that cover it (`scripts/map_to_k8.py`: same track, paper
and file, overlapping lines) and hands the statements the K8 seed does not cover to the
K8 owner (`claims/uncovered_seed.jsonl`). `kb/serve_locate.py sync-k8` (adds uncovered
statements with the K8 side tables, idempotent on seed_key `served:<key>`) is tested only
as a dry run (rolled back); it is for the lead once K8 claim ids are frozen by a snapshot
(K8 refuses `--rebuild` once `db/current` holds claims, so a snapshot by this package
would block the K8 helper; none taken).

## S4 16:25 Registered locator check and mapping to the K8 claims (prediction)

Inputs: track notes at their branch tips, `claims/manual.jsonl`, kb.sqlite read-only.
Prediction: identical check counts to S3 (330 statements, 372 locators resolved, numbers
117 exact / 2 near / 13 missing); 266 statements covered by K8 claims as in the last dry
run (fewer or more only if the K8 helper re-seeds in between); 62 uncovered with a
locator (F 53, B 7, D 2-3, E 1), 2 without a paper locator; nothing written to the
database (the sync step rolls back). Refuted if a check count differs or any claims row
changes because of this run.

Outcome S4 (run kb-20261115-154254-b4a4d3d): prediction held. 330 statements, 372 locators
all resolved inside the stored sources; numbers 117 exact / 2 near / 13 missing; 266
statements covered by K8 claims, 62 not (with a locator), 2 without a paper locator; the
claim tables are unchanged by the run (618 claims, 618 claim_meta, 647 claim_events before
and after). Figure `fig_locator_check.png` read: panel (a) shows A, C and E fully covered by
the K8 seed, F mostly not (its SCOPING section 8 and `reference.py` are not K8 sources);
panel (b) shows numbers found at the locator for 117 of 132 statements. Published:
`claims/served_claims.tsv` (one row per statement: track locator, kb locator with section,
chunk, equation numbers, number check, K8 claim ids, labels, statuses, seed keys),
`claims/uncovered_seed.jsonl`, `claims/summary.json`.

## S5 16:50 Literature searches; fetch of five identifiers found (prediction)

Searches (read-only, `scripts/kbq.py` on kb.sqlite; results go into the answers) found
arXiv ids in the corpus bibliographies for sources the tracks asked for and the store
lacks: 2505.15903 (Gurian and May, "Gurian:2025zpc", C item 1; bib entry of 2601.17117),
0707.1350 (Faraoni and Jacques 2007, D item 3; bib entries of 2504.01669, 2206.08466),
astro-ph/0608642 (Mack, Ostriker, Ricotti 2007, D item 3; bib entry of 2505.21885),
gr-qc/0305023 (Alcubierre et al., "Toward standard testbeds", B item 3; bib entry of
1904.07841), 1003.4681 (Muller and Brugmann, cited for the spatially dependent shift
damping at high mass ratio in 2505.01495 `apssamp.tex:440-446`, F item 2).

Prediction: `nrpic-fetch-arxiv` stores all five with status ok and a TeX source; after
verify-downloads, `kb ingest arxiv --new --extras` ingests exactly these five, at least
four with parse_status ok (the 2003 and 2006 sources may land on the review list).
Refuted if a fetch fails, an id is not a TeX e-print, or two or more parse as
review/failed.

Outcome S5 (runs kb-20261115-154525-248806f fetch, kb-20261115-154547-12ef9f0
verify-downloads, kb-20261115-154612-4703404 ingest): prediction held. All five stored
ok with TeX (2505.15903 v2 tar; 0707.1350 v1 single gzip-tex; astro-ph/0608642 v1 tar;
gr-qc/0305023 v1 tar; 1003.4681 v1 tar); manifest still 683 ok + 1 problem, 24 extras;
ingest: all five ok (scores 0.93-1.00; sections 5-21, equations 6-102, bibliography
33-86), gr-qc/9412071 skipped as before.

## S6 17:00 Weekly upstream watch of AthenaK (prediction)

Previous watch: run kb-20261115-132754-bb3da03 at 13:27:54Z (main c5a0d7f, 124 branches,
none named pic/vlasov/nrpic/deposit, no `src/particles` line with tmunu or deposit on any
branch). Prediction for `kb watch upstream` now (3.5 h later): main still c5a0d7f; 124
branches with at most two moved, none new with a flagged name; still no branch hands
particle stress-energy to Z4c; hence no message to core is needed. Refuted if main moved,
a flagged branch appeared, or any branch's `src/particles` gained a tmunu/deposit line.

Outcome S6 (run kb-20261115-154646-234060c): prediction held. Main still c5a0d7f9155a; 124
branches, 0 new, 0 removed, 0 moved since 13:27:54Z; no flagged branch name; 0 branches
whose `src/particles` mentions tmunu or deposit, 7 that read the metric (z4c/adm) as
before; the report's message for core: nothing to report. Report
`watch/code_watch_upstream.md`; figure `watch/fig_code_watch.png` (made afterwards from the
run's snapshot JSON with `kb/scripts/fig_code_watch.py`, read: 117 stock branches, 7 that
read the metric, none red).

## S7 17:15 Coverage criterion of the K8 mapping corrected

While writing the answers I found that S4's criterion (same track, paper, file and
overlapping lines) counts a K8 claim from a different note about the same passage as
covering a served statement: D's request annotations were "covered" by claims of D's
`scope/REFERENCES.md` (for example claim 332, a general statement on 1305.2619), and F's
SCOPING rows by claims of F's `novelty/NOVELTY.md`. `scripts/map_to_k8.py` now also requires
the same note (claim_meta.origin_path equals the statement's document). A dry check with
the new criterion on S4's checked.jsonl was run before this entry (so this is not a
prediction made blind): 258 of 330 covered; not covered: F 57, D 7, B 7, C 1.
Prediction for the registered rerun: the same 258 / 72 split (the check counts as in S4);
refuted if it differs, which would mean the K8 claims changed between the two runs.
