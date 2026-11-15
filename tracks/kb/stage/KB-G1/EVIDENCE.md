# KB-G1 evidence (owner kb)

Gate definition: brief 12.10 (line 1458) and 14.2 (lines 1673-1675). Package files:
`FIRST_QUESTIONS.md` (answers with locators), this file (criteria, artefacts, run ids),
`OPEN.md` (what the gate still lacks, stages that remain), `priority3_ingestion.tsv`.
Database for every number: snapshot `kb-data/db/kb-20261115-f2fcda5.sqlite` (`db/current`,
run kb-20261115-141500-b2e57be), schema version 5. Run manifests:
`tracks/kb/runs/<run_id>/manifest.json`; outputs `scratch/kb/<run_id>/`.

## Criteria and their state

| Criterion | State | Evidence |
|---|---|---|
| KB-G0: tools chosen, directories in place | met | tool choices with reasons in `kb/JOURNAL.md` (K0 helper); `kb/.venv` frozen in `kb/requirements-k0.lock`, `kb/requirements-k6.lock`; layout of brief 12.2 by `kb init` |
| `kb verify-downloads` report | met | `kb/reports/verify-downloads.md`, run kb-20261115-140336-29f15a1: 684 manifest ids, ok 683, problem 1 (gr-qc/9412071, gzipped PostScript), incomplete 0, failed 0, missing 0, extras 18; 63 of 63 repositories ok. Figure `kb/reports/fig_inventory.png` (run kb-20261115-140851-29f15a1) |
| all priority-3 papers ingested | met | `priority3_ingestion.tsv` (run kb-20261115-141457-b2e57be): 47 of 47; 45 ok, 2 review (gr-qc/9906015 plain TeX, no sections or bibliography found; 2009.08715 no \title, no abstract environment) |
| code and parameter index of AthenaK | met | upstream IAS-Astrophysics/athenak c5a0d7f9155a and this tree (local/nrpic, main a1c2237): `kb/reports/code_index.md`, `kb/reports/code_params.md`, `kb/reports/code_params_*.tsv`; 64 repositories, 68037 files, 305733 symbols, 157184 code chunks, 3454 parameter rows |
| answers to the first questions of 12.9 | met, open sub-points in `OPEN.md` | `FIRST_QUESTIONS.md`, nine answers with file:line locators |

## Runs of the helpers (registered by them; rechecked by the lead)

| Run | What | Result |
|---|---|---|
| kb-20261115-112414-6bb2b7d | first inventory | 24 of 684 ok, 660 missing |
| kb-20261115-112522-3ac74c2 | priority-3 download (33 ids) | 33 of 33 stored |
| kb-20261115-112823-3ac74c2 | inventory | priority 3: 47 of 47 ok |
| kb-20261115-124340-9048b83 | download of 599 ids (priorities 2, 1) | 599 store paths printed, stderr empty, 2606 s |
| kb-20261115-132730-a51e26e | inventory | 683 of 684 ok, 1 problem |
| kb-20261115-135137-cf1baba | full paper ingestion | 701 papers, 240 s on 8 processes |
| kb-20261115-135554-d405f64 | checks C1-C6 | `kb/reports/papers_k2k3.md` |
| kb-20261115-130232-ac33aa1 | 63 shallow clones | 63 of 63, 157 s |
| kb-20261115-133232-3f7f25a, kb-20261115-134736-0e94ee2 | code index | 64 repositories |
| kb-20261115-130931-c0e0ec8, -131150-, -131158-, -131207-7350d70 | P2/P3 extractor cross-checks | all calls agree |
| kb-20261115-135337-45ab9d0, -135445-dfc83c9, -135545-d405f64 | inputs against code (P4, P4') | P4 refuted (85.0 %), P4' held (99.3 %) |
| kb-20261115-132754-bb3da03 | upstream watch baseline | `kb/reports/code_watch_upstream.md`, `fig_code_watch.png` |
| kb-20261115-135323-534eb86 | paper-code link check | 25 of 25 |

## Runs and checks of the lead (this session)

| Run or check | What | Result |
|---|---|---|
| L0 | `cd kb && .venv/bin/python -m pytest` | 107 of 107 on 29f15a1; 110 of 110 after the lead's fixes |
| L1 | awk extraction of brief lines 2543-3226, 3234-3296 | 684 rows (47/160/477), 63 repositories, id sets equal `kb/manifests` |
| L2 | own scan of the store bytes (`scratch/kb/lead/store_scan.py`) | 684 of 684 present, 684 sha256 equal the records; 654 gzip-tar, 28 gzip single file, 1 PDF (2201.03458), 1 PostScript (gr-qc/9412071) |
| kb-20261115-140336-29f15a1 | verify-downloads rerun (L3) | as above |
| L4 | database counts, db/current contents | 701 papers; 64 repos, 3454 params in the current snapshot |
| L5 | numbered lines of 2611.12831 counted independently | 139 = 139; ordinals 1, 10, 40 carry the same labels |
| L6 | bibliography counts of 2611.12831 and 5 drawn papers | 6 of 6 equal |
| L7 | grep of ParameterInput calls in upstream AthenaK; 3 defaults by hand | 1172 call sites against 1165 (0.6 %); defaults and lines equal |
| L8 | git grep over the 124 tips of the stored watch mirror | no tmunu/deposit in any src/particles; no nrpic/vlasov under src/; ADM read in particles_gr |
| L9 | `kb link check` | 25 links, 0 problems |
| kb-20261115-140838-29f15a1 | inventory figure, wrong output name | stray files removed by name |
| kb-20261115-140851-29f15a1 | inventory figure | `kb/reports/fig_inventory.{png,pdf}` |
| kb-20261115-141159-bf9c30f | re-ingestion of 8 papers after the \nc fix (L10) | 7 of 7 compared papers equal the independent count |
| kb-20261115-141358-9043e03 | re-ingestion of 20 papers after the composite-shorthand fix (L11) | gain equals use count in 20 of 20 (after correcting my count) |
| kb-20261115-141457-b2e57be | priority-3 table | `priority3_ingestion.tsv` |
| kb-20261115-141500-b2e57be | snapshot | `kb-data/db/kb-20261115-f2fcda5.sqlite`, db/current |
| kb-20261115-141630-b2e57be | figure of L10/L11 | `kb/reports/fig_lead_equations.png` (inspected) |

## Commits of this owner (branch kb/main)

Helpers: 6bb2b7d, 3ac74c2, d939d5d (K0-K1); 9048b83 to 29f15a1 (K2-K3); ac33aa1 to 5505dbe
(K6-K7). Lead: bf9c30f (checks, export and alias fixes), 9043e03 (composite shorthands),
b2e57be (outcome L11), and the package commit that adds this file.

## Figures (each inspected with the Read tool)

`kb/reports/fig_inventory.png`, `fig_papers_k2.png`, `fig_citations_k3.png`,
`fig_code_repos.png`, `fig_code_params.png`, `fig_code_watch.png`, `fig_lead_equations.png`.

## Compute used and estimated (kb: 0 GPU-hours, 8 cores, decision 0006)

No card time used. Largest runs: download 2606 s (network, 3 s rule), code index 474 s +
328 s, full ingestion 240 s on 8 processes. Data: 6.8 GB raw, 0.5 GB build, 0.81 GB per
snapshot. K4 estimate [JUDGEMENT, TO VERIFY with a timed scouting run on 1000 chunks]: about
250 000 items to embed (about 43 000 retrievable text chunks, 53 862 equations, 157 184 code
chunks); a local model of about 100 M parameters on 8 cores at an assumed 20-50 items per
second takes 1.5 to 3.5 hours; 768-dimensional float32 vectors take about 0.8 GB.

## Wave 2 update (kb lead, 2026-11-15T18:10-19:10Z)

KB-G2 is not met (OPEN.md, section "KB-G2"), so this package is KB-G1 brought up to date. The
four KB-G1 criteria stay met; what wave 2 added to each:

| Criterion | Wave-2 evidence |
|---|---|
| inventory report | verify-downloads reruns kb-20261115-154547-12ef9f0 and kb-20261115-182907-3f69615: manifest 683 ok + 1 problem, 26 extras (8 fetched on the tracks' requests in wave 2). K1 metadata: run kb-20261115-182505-7e3a0b5, arXiv-API records 708 of 708 and INSPIRE records 704 of 708 in `kb-data/meta/arxiv-api/`, `kb-data/meta/inspire/` (decision 0015); not yet compared with brief 16 |
| priority-3 papers | unchanged (47 of 47) |
| code and parameter index | unchanged; upstream watch kb-20261115-154646-234060c: main c5a0d7f, 124 branches, none moved |
| first questions | unchanged; core's metadata question answered from the arXiv-API record (outbox `__to-core__paper-metadata-and-philox`) |

Stages that wave 2 built (not KB-G1 criteria; they prepare KB-G2 and KB-G3):

| Stage | State | Evidence |
|---|---|---|
| K4 embeddings | built | 43398 chunk and 54259 equation vectors at the W5 check (then +102 chunks, +243 equations for the two new papers, run kb-20261115-183052-0f8245e); model and hashes `kb/EMBEDDING.md`; rechecked W5 (kb-20261115-182238-b86d2b5) |
| K5 equation tags | built, version 3 | 1140 equations tagged; precision 7/10 or better per tag on the helper's sample; lead's sample 16/18 (W5) |
| K8 claims | built | 618 claims seeded (kb-20261115-154020-7b80ccc) + 70 served statements (W6, kb-20261115-182425-edbae8b) = 688; audit 29/30 (helper) and 9/10 (lead) |
| K9 QA report | first version | `tracks/kb/claims/QA_REPORT.md` (kb-20261115-155508-2e00432); counts recounted exactly by the lead (W4, kb-20261115-181916-08ebad9); C4 (INSPIRE sample) and the hybrid retrieval part to rerun |
| K10 commands | built | `kb embed`, `kb search`, `kb eq`, `kb claim`, `kb qa` reachable from `kb/bin/kb` (no stub left but `ingest`'s dispatcher); 173 tests pass |
| K11 snapshots, watch | done this wave | snapshots kb-20261115-621430e, kb-20261115-3826a68, kb-20261115-44b7406, kb-20261115-a848a06; weekly watch run by the kb session (decision 0015) |

Database for the wave-2 numbers: snapshot `kb-data/db/kb-20261115-44b7406.sqlite` (run
kb-20261115-183052-0f8245e): 709 papers, 688 claims, 98002 vectors, schema 6. The last snapshot of
the session, `kb-20261115-a848a06.sqlite` (= db/current, run kb-20261115-183921-31d5b77), differs
from it only by claims 25 and 674, verified by the lead's reading (checked 31).

Runs of the lead in wave 2: kb-20261115-181519-d78b8d4 (output misplaced, superseded),
kb-20261115-181544-94f68f2 (W2), kb-20261115-181916-08ebad9 (W4), kb-20261115-182232-85883d1 (W3),
kb-20261115-182238-b86d2b5 (W5), kb-20261115-182414-e13b30c (W6 dry), kb-20261115-182425-edbae8b
(W6), kb-20261115-182505-7e3a0b5 (W7), kb-20261115-182741-7dafdf9 (W8),
kb-20261115-182907-3f69615 (W9, failed at the tag step), kb-20261115-183052-0f8245e (W9b), kb-20261115-183921-31d5b77 (W10). All
registered with `harness/bin/nrpic-run submit` (the helpers' runs by hand with
`kb/scripts/registered_run.py`, because submit refused the shared worktree before `--package`
existed).

Compute in wave 2: 0 card-hours. Cores: the lead's runs at most 8 at a time; two runs of the embed
helper exceeded kb's allotment of 8 (kb-20261115-152906-ca81acd 16 threads, kb-20261115-153805-e164901
12 threads for 60 min; `../REVIEW-wave2.md`).
