# tracks/kb/served: answers of the knowledge base to the kb-requests of wave 1

Helper package "serve" of owner kb, wave 2 (2026-11-15, 15:22-17:30 UTC). Predictions and
outcomes: `JOURNAL.md` (S0-S8). Nothing here contains paper text: ids, locators, counts,
our wording and the tracks' wording only.

## What is here

| Path | What |
|---|---|
| `outbox/20261115T1600Z__to-<ID>__<slug>.md` | the nine answers, one per kb-request (A, B, C x2, D, E, F x2, core), in the format of `harness/templates/outbox_message.md`; drafts for the lead to post into `tracks/kb/outbox/` (this helper writes only `served/`) |
| `claims/served_claims.tsv` | one row per served statement (330): track locator, knowledge-base locator (version, section, chunk ids, equation and figure numbers, flat.tex range), number check (found in the cited lines / within 3 lines / quoted), numbers not found, K8 claim ids, labels, statuses and seed keys, or the label the K8 rules would give where no K8 claim exists |
| `claims/uncovered_seed.jsonl` | the 70 checked statements with a paper locator that no K8 claim of the same note covers (F 56: SCOPING section 8, `newton3/hills3/reference.py`, `geodesic_binary/README.md`; D 7: its request's annotations; B 7: "Abstract NN-..." locators), for the K8 owner |
| `claims/manual.jsonl` | 27 statements written by hand from the requests of C, D, E and F's README (errata and notes), each with paper, file, lines, our wording, label, evidence, expected tokens or values |
| `claims/summary.json` | counts of the last run |
| `fig_locator_check.{png,pdf}` | (a) served statements per track: K8 claim exists / not yet a claim (by label) / no paper locator; (b) statements quoting numbers: all in the cited lines, all within 3 lines, some not found |
| `watch/code_watch_upstream.md`, `watch/fig_code_watch.{png,pdf}` | weekly upstream watch of IAS-Astrophysics/athenak (run kb-20261115-154646-234060c) |
| `scripts/requested_ids.py`, `presence.py` | the ids named in the requests and where each stands (store, ingest, group) |
| `scripts/extract_track_locators.py` | statements with paper locators from A's and B's `scope/REFERENCES.md`, C's `stage/G0/REPORT.md` section 6, F's `stage/G0/SCOPING.md` section 8 and `newton3/hills3/reference.py` (read with `ast`, never imported) |
| `scripts/map_to_k8.py` | served statement -> K8 claims of the same note with overlapping lines |
| `scripts/run_serve.py`, `fig_serve.py`, `figstyle.py` | the pipeline (extract, check, map, dry-run sync, tables, figure); figure style copied from `harness/style/` |
| `scripts/kbq.py` | read-only queries used for the literature answers: equation by number, BM25 over chunks, regex over flat.tex, bibliography entries, citers, titles; every hit with file:line |
| `../../../kb/serve_locate.py` | track `file:line` -> knowledge-base locator by inverting `build/tex/<id_>/sourcemap.json`; number and token check at the source; `sync-k8` (adds uncovered statements with the K8 side tables; used only as a dry run here); `load` (superseded, see JOURNAL S3) |
| `../../../kb/serve_tests.py` | 6 tests of serve_locate.py on synthetic inputs |

## How to rerun

```bash
cd /data/haiyangw/nrpic/wt/kb
python3 -I kb/serve_tests.py                                    # 6 tests
python3 -I tracks/kb/served/scripts/presence.py /data/haiyangw/nrpic/kb-data/db/kb.sqlite \
    /data/haiyangw/nrpic/scratch/kb/tmp/presence.tsv            # where the requested ids stand
python3 -I kb/scripts/registered_run.py --purpose "kb serve: ..." -- \
    python3 -I tracks/kb/served/scripts/run_serve.py '{run_dir}' --publish
                    # read-only on kb.sqlite (the sync step rolls back); --write-claims adds the
                    # uncovered statements to the K8 layer (only after a snapshot froze the ids)
python3 -I tracks/kb/served/scripts/kbq.py bib 'Eggleton.{0,80}1983'   # example query
python3 -I kb/bin/kb watch upstream --report tracks/kb/served/watch/code_watch_upstream.md
kb/.venv/bin/python -I kb/scripts/fig_code_watch.py \
    /data/haiyangw/nrpic/kb-data/meta/github/watch/IAS-Astrophysics__athenak/<stamp>.json \
    tracks/kb/served/watch/fig_code_watch
```

## Results (runs registered under `tracks/kb/runs/`)

- Store: 2605.30145 fetched for A (kb-20261115-152541-e02d870); 2505.15903 (C), 0707.1350
  and astro-ph/0608642 (D), gr-qc/0305023 (B), 1003.4681 (F) fetched
  (kb-20261115-154525-248806f); all six ingested ok (kb-20261115-152647-ca81acd,
  kb-20261115-154612-4703404); verify-downloads after each (kb-20261115-152614-8a93349,
  kb-20261115-154547-12ef9f0): manifest 683 ok + 1 problem (gr-qc/9412071), 24 extras.
- Locators (kb-20261115-154906-f19880f): 330 statements, 372 paper locators, all resolve to
  lines inside the stored sources and into flat.tex; 132 statements quote numbers, 117 with
  all numbers in the cited lines, 2 within three lines, 13 with numbers not found (listed in
  the answers). 258 statements have a claim of the K8 layer from the same note; 70 do not
  (`claims/uncovered_seed.jsonl`); 2 rows have no paper locator.
- Upstream watch (kb-20261115-154646-234060c): AthenaK main still c5a0d7f, 124 branches
  unchanged since 13:27:54Z, no branch hands particle stress-energy to Z4c; nothing for core.
- Literature answers: in the nine drafts (identifiers found in corpus bibliographies, with
  the entry as locator; "not found" where the corpus has nothing).

## Not done

- No claims written by this package: the K8 helper owns the claims layer; my first load
  (330 rows, run kb-20261115-153751-e164901, with the literal run id RUNID_PLACEHOLDER in
  verified_by) duplicated it and was removed by its `--rebuild` (JOURNAL S3).
- No snapshot taken (a snapshot that holds claims blocks the K8 helper's rebuild); answers
  cite claim ids in `kb-data/db/kb.sqlite` and seed keys.
- Not posted: the nine answers are drafts in `outbox/`; the requests are not acknowledged in
  `inbox_acks.txt` (lead's files).
- Wording of the reference.py entries with text values and of every fulltext-ready
  statement was not compared with the passage by a person (only locators, numbers, tokens).

## Requests

1. **kb lead: post and acknowledge.** Move `outbox/*.md` into `tracks/kb/outbox/` (or post
   them with `nrpic-ctx post`) and acknowledge the nine requests (`nrpic-ctx ack`).
2. **kb lead / K8 owner: seed sources.** Add F's `stage/G0/SCOPING.md` section 8,
   `newton3/hills3/reference.py` and `geodesic_binary/README.md`, D's request
   `outbox/20261115T1510Z__to-kb__dress-and-coupling-sources.md`, and B's "Abstract NN-..."
   locator style to the K8 seed; the 70 statements, already checked, are in
   `claims/uncovered_seed.jsonl`. Alternative once a snapshot froze the ids:
   `run_serve.py <dir> --write-claims` (seed keys `served:<key>`).
3. **kb lead: snapshot.** `db/current` (kb-20261115-f2fcda5) has neither the claims nor the six
   papers fetched here; the answers to A, B, C, E, F name claim ids of kb.sqlite.
4. **kb lead: groups of extras.** F asks for G21 on 2406.11985, 2308.07365, 2505.03934,
   2605.20320, 2108.01392, 2604.27429, 2610.09336; ingest takes `papers.grp` from the
   manifest only, so a curated group list for extras is needed (an update by hand would be
   lost at the next re-ingest).
5. **orch: nrpic-run in a shared worktree.** `nrpic-run submit` refuses while any helper has
   untracked files in the worktree ("the worktree is not clean"), which is the normal state
   when several helpers share `wt/kb`; every run of this package was therefore registered by
   hand (`kb/scripts/registered_run.py`). Some manifests record `worktree_dirty_kb: true`
   from another helper's uncommitted `kb/` files. Proposal: check only tracked files and the
   run's inputs, or accept `--allow-untracked`.
6. **orch: metadata mode** of `nrpic-fetch-arxiv` (decision 0015). Waiting on it: core item 1
   (date, categories, pages of 2611.12831), C item 5 (Ambrus 2022 arXiv id from DOI), D item 3
   (Croker and Weiner 2019 arXiv id from DOI).
7. **orch: non-arXiv papers.** Core asks for the SC11 Philox paper (not on arXiv); decide
   whether a publisher PDF may be fetched for such cases.
8. **orch: additions outside the manifest.** Six papers were fetched on the tracks' explicit
   requests (2605.30145, 2505.15903, 0707.1350, astro-ph/0608642, gr-qc/0305023, 1003.4681);
   record or reject them as manifest additions.
9. **E-stoch-inf, D-bh-dress, C-sidm** (in their answers): E, the equation number at
   `main_V2PRD.tex:320` ((17) in the request, (23) by the knowledge base); D, run ids for the
   measured values (9.2 per cent, 2.59, +45/+14 per cent); C, the file of the
   astro-ph/0111176 locator.
