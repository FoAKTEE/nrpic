# kb: lead review of wave 3 (batch 3, 2026-11-21)

Reviewer: kb lead, wave 3 batch 3 (session started 12:52Z). Packages that finished since the last
lead session of kb (wave 2b, 2026-11-19): `verify_g2` only. The other four packages of round 1
(tracks/kb/PLAN-wave3.md) were cut by the usage limit at 14:35 PST on 2026-11-20 and have not
been resumed; their state is in section 3. Method: each result recomputed from the registered
outputs and the frozen snapshot with my own code, not from the package's conclusions; prediction
L1 written and committed (381c9a6f) before my run kb-20261121-125746-a03875b; figures read.

## 1. verify_g2 (independent verifier of KB-G2 and KB-G0)

Artefacts: tracks/kb/stage/KB-G2/VERIFIER.md, tracks/kb/stage/KB-G0/VERIFIER.md,
tracks/kb/verify_g2/{heldout.yaml, JOURNAL.md, README.md, scripts/, figures/}; 14 registered runs.
My check: script tracks/kb/stage/review_wave3/scripts/lead_check_vg2.py, run
kb-20261121-125746-a03875b (check.json), figure
tracks/kb/stage/review_wave3/figures/fig_lead_check_vg2.png.

### Confirmed (prediction L1 held in all eight parts)

| Item | Verifier | Lead (own code) |
|---|---|---|
| Paper in top 10, held-out 24 (text/hybrid/rerank) | 21/22/21; rank 1 14/14/14 | recount from the raw hit lists: equal |
| Paper in top 10, golden 32 | 27/28/28; rank 1 20/17/19 | equal |
| Held-out written blind | heldout.yaml committed 8fb37106 at 22:24:05Z, first search 22:25:46Z | git: 8fb37106 is an ancestor of the search run's commit ea894c87; times as stated |
| parse_status | ok 684, review 23, pdf 3 | SQL on a782f1e: equal |
| TeX papers without bibliography entry | 20 (11 with status ok) | equal, same 20 ids |
| Papers with citation rows but no entry | 10 | equal |
| Papers without abstract chunk | 25 | equal |
| Repositories without code chunks | 24 of 64 | equal |
| Database columns of its parse scan (sections, equations, bibliography, citations, abstract chunk) | scan.json of kb-20261120-223309-14e4cb6 | equal to my SQL for 710 of 710 papers |
| C3 under its definition | 688 lenient; 679 after nine gaps read at the source (95.6 %); 670 with nine letters failed (94.4 %) | my evaluation of the definition from the scan's source counts and my database counts: 688, 679, 670; component totals S 709, E 701, B 696, A' 710 equal |
| Bibliography defects at the source | 0710.5073: 28 `\bibitem` in a `references` environment; 1201.4794: AAS `\reference` list; gr-qc/0304002: `\def\bi{\bibitem}` | grep of the stored sources (read as text): 28 `\bibitem`, 1 `\begin{references}`; 46 `\reference`; 1 definition, 39 uses |
| C6b | no snapshot id on a hit, in `kb show` or `kb cites` | `kb show 2611.12831 --abstract` and `kb cites 2611.12831 --out` on a782f1e print none; hit keys have no snapshot field; info.database names the file |
| C9 record defect | two wave-1 manifests "finished" with exit 1 | equal (status finished, exit_code 1) |

Figures: fig_ranks.png (four panels: rank of the right paper and of the first location hit, both
sets, three modes) shows the misses I counted (held-out text H03, H17, H20; hybrid H20, H24;
rerank H03, H20, H22; golden text q07, q11, q12, q17, q24; hybrid q11, q12, q13, q24; rerank q06,
q12, q13, q17), consistent with the legends and with defect 5. fig_parse.png: pass fractions by
status agree with the tally; in the equation panel most papers lie above the diagonal (the
database stores more equations than the verifier counts display environments, e.g. one per
align row), and the seven E failures are the points below the half line; three PDF papers sit
at verifier count 0 with database bibliographies of 20-70 entries, as expected for PDF-only
sources. My figure: both panels show the verifier's and my bars equal; the legend of panel (a)
overlaps the base of the last two bars (cosmetic; numbers in check.json).

Predictions of the verifier against its outcomes: R1 (held-out paper rate 55-85 %) inside its
refutation bars but too low; R2 (held-out 5-15 points below golden) refuted; P1 (bibliography
weakest) refuted (the abstract chunk is); P2 refuted on component verdicts (two plain-TeX papers
passed wrongly), confirmed on failures; T1 refuted in substance (its leniency check first missed
five review papers), T2 confirmed after the fix; D1 and K1 confirmed; P3 confirmed except its
locator part (C6b). Every failed
prediction is in its README and journal; the superseded first scan (kb-20261120-222948-fcdd5e7)
is kept on record.

### Not confirmed by me (not rechecked)

- The leniency check's reading of 17 papers and the judgement that nine letters with run-in
  headings have no sections to lose (I checked three sources, not these).
- The location hit rates (54-78 %; not gating): not recomputed; my recount is at paper level.
- The quality of the 24 held-out questions as questions (whether each is answerable only from
  the stated passage).
- Items the verifier lists as not checked (bibliography resolution, citation graph, equation
  content, code-index content, the working database, the 26 raw directories outside the
  snapshot) remain unchecked by anyone.

### Wrong

Nothing in the verifier's numbers. One process point: the batch text said "do not push" while
the package brief required a push; the verifier pushed kb/main (ef9d2d34, 465a1322), which carried
other helpers' commits already on the branch. No harm found (those commits were finished
batches A1 of claims_tracks and the code_kb watch).

### What the track does about each WRONG or NOT CHECKED finding of the verifier

| Finding | Verdict | Action |
|---|---|---|
| KB-G2 C6b: locators carry no snapshot id | WRONG (partly met) | Recorded in KB-G2 CHECKLIST C6 with my judgement that brief 12.10 asks the note, not each hit, to record the id (met by the package); code fix (id in `kb show`, `kb cites`, each JSON hit) deferred because ingest3's unlanded copy changes kbtool/papers_cli.py; assigned in KB-G2/OPEN.md |
| KB-G2 C3 margin 4.5 papers | CONFIRMED, fragile | Both readings stated in CHECKLIST C3; remedy is ingest3 (bibliography formats, old-style headings, abstracts), whose scope now includes defects 1, 2 and 4 |
| KB-G2 C9 / KB-G0 C6: two manifests "finished" with exit 1 | defect of the record | Fixed: status "failed" with a status_note in tracks/kb/runs/kb-20261115-154858-b0d8c8f and kb-20261115-164121-5aca10c |
| KB-G0 C1b reasons for the tools | NOT CHECKED | Checked by me: kb/JOURNAL.md lines 24-36 (K0), 205 ff. (K2-K3), 231 ff. (code index), kb/EMBEDDING.md; named in a new kb/README.md section with the two layout departures (uv.lock, seed_claims.jsonl) |
| KB-G0 defect 2: raw source.bin mode 0664 | minor | Left for after ingest3 lands (it fetches into kb-data/raw); KB-G0/OPEN.md |
| QA report states no parse rate against the bar | remark | Next `kb qa run` after ingest3 (KB-G2/OPEN.md) |
| 24 repositories without code chunks | defect of brief 12.7 | code_kb or a later package |
| Package documents and STATUS currency | NOT CHECKED (the lead's) | Brought up to date in this session (C10 of KB-G2, C7 of KB-G0) |

## 2. Stranded work committed in this session

- tracks/kb/claims_tracks/LEDGER.tsv: the 14 ledger rows of batch B1 (Track B: 4 verified, 10
  judgement annotations), applied to kb.sqlite by run kb-20261120-223013-5330e45 (completed,
  exit 0) before the cut; rows equal to its ledger_rows.tsv. Commit a03875b2. I did not re-read
  the 14 claims against their sources (the package's own audit step is pending).

## 3. Packages cut on 2026-11-20 and left in place (not reviewed: not finished)

| Package | Done (committed) | Uncommitted in the worktree | What remains |
|---|---|---|---|
| `claims_tracks` | skeleton, baseline B0 (700 claims, queue 159), batch tooling, batches A1 (Track A, run kb-20261120-222903-226b273) and B1 | decisions and generated batch scripts C1, D1, E1 (never run; no run manifest) | review and run C1, D1, E1; F and core batches; requests of B (claims 689-695) and D (682/683); audit of 40 machine-located claims; outcome of prediction Q; three new kb-requests (B: arXiv:2312.12499 factor; A: Szekeres conformal flatness; C: conductivity sources) |
| `code_kb` | skeleton, upstream watch W1/W2 (watch kb 20261120T221926Z; message to core 20261120T222130Z) | JOURNAL.md: prediction M1 for `kb code modules` (written 22:35Z, before the tool exists) | `kb code modules` (K7 descriptions, task-list order), tests, link tests for the 25 paper-code links, the `<z4c> nco` question |
| `ingest3` | nothing | tracks/kb/ingest3/{figures,ids,scripts}; private copy scratch/kb/ingest3/dev/kb (papers_cli.py changed) | baseline, bibliography parser, claim chunk remap, re-ingest of the 20 papers, the 24 sources of wave 3a, QA, figures; plus verifier defects 1, 2, 4 |
| `claims_brief` | nothing in git | scratch/kb/claims_brief only | seeder of the brief's statements, `kb claim seed-brief`, tests; join of the brief-check rows; section-5 defect claims |

No card job of kb is queued or running (squeue, 2026-11-21 12:58Z); kb's card allotment is 0.

# Lead review of batch 9 (2026-11-21 evening): ingest3, claims_tracks, claims_brief, code_kb

Rechecked from the artefacts by own SQL on snapshot kb-20261121-bbaafe5 and the working database
(no helper ran this session; numbers with run ids in ../JOURNAL.md, entry of lead batch 9).

## ingest3 (bibliography formats, claim remap, 35 additions)
- Confirmed: 720 ok of 745 before my drop of gr-qc/0608095, 719 of 744 after (run
  kb-20261121-234701-64e4f3d, `kb status`); 6 TeX papers without any bibliography entry, none ok
  (their six old-style lists); 0 ok papers that cite without entries (strict rate = recorded rate);
  bibliography entries 67865 - 4 (the dropped paper) = 67861 and citation rows 109730 - 7 = 109723,
  as their final QA; in-corpus citations 14810. 0 dangling chunk references among all claims and 0
  orphan vectors after their remap and my drop. `kb claim check` on the 16 seeds of their 20
  papers: "same 16" (run kb-20261121-234437-8747d17), as they reported. Figure
  fig_parse_status.png read: bars and rates equal the counts (the pdf bar of 3 sits low on the
  symlog axis, cosmetic).
- Not rechecked: the 14 bibliography formats one by one (their 14 tests pass in the suite).
- Wrong: nothing found. Their open test failure (61 additions) is fixed here (below).

## claims_tracks (159 queue claims)
- Confirmed: claims 1-700 now fulltext 639 (175 with status checked), to_verify 19, judgement 41,
  background 1, exactly their after-counts. Not rechecked: the 40-row audit (AUDIT.md) row by row.
- Their request "guard kb claim check after relocate" is done (below); B's claim recorded (861).

## claims_brief (112 seeds, 48 defect claims)
- Confirmed: seeds 701-812 fulltext 42, refuted 11 (718, 737, 738, 742, 749, 752, 756, 766, 767,
  782, 802), judgement 20, abstract 14 + background 6 + to_verify 19 = 39 open; defects 813-860
  refuted 24, judgement 14, fulltext 8, abstract 2 (= 20 superseding + 4 facts as they state).
  Figure fig_seeds_by_section.png read: section totals 8, 8, 54, 14, 5, 1, 2, 4, 1, 15 = 112.
- Decision on the 17 corrected but unlabelled statements (CHECK_UNJOINED.tsv): NOT made claims.
  Brief 12.8 seeds "the labelled statements of the main text" only; an unlabelled sentence is not
  a seed. They stay as errata rows (coord/BRIEF_ERRATA.md) and become a claim through `kb claim
  add` as soon as a track cites one (12.8, third item) [JUDGEMENT].
- Refutations passed on (12.8, second item): F-hills 766, 767 and A-emd-pbh 742 (outbox).

## code_kb (module descriptions, 25 link verdicts)
- Confirmed: impl_links verified 19, claimed 5, refuted 1; `kb link check` 25/25 OK; `<z4c> nco`
  has 0 parameter reads in the index and no `"nco"` string in athenak/src. Stale header of
  kb/curated/paper_code_links.tsv corrected. M23 symbol change waits for core's answer.
- Not rechecked: the task order of particles_tasks.cpp (report kb/reports/code_modules.md).

## Lead's own items of this batch
- Test of the additions: 60 rows and 744 papers, gr-qc/0608095 commented out of the manifest and
  dropped from the papers table (decision 0024 item 2; run kb-20261121-234427-d6031d4). The task
  text said 61/745; that count still included the dropped paper. Whole kb suite green.
- Guard: `kb claim check` and re-seeding return "pinned" and leave label, status and locator rows
  alone for a claim with a relocate event (relocate, verify --locator) or a person's label with a
  different locator (kbtool/claims_db.py pinned_locator; test in test_claims.py).
- C6b: `kb show` views end with "[kb snapshot <id>]", `kb cites` rows and every JSON hit of `kb
  search`/`kb eq` carry "snapshot"; checked on db/current. KB-G2 C6b (verifier: WRONG) is now met.
- `kb qa run` states the parse rate against the 95 % bar: 719/744 = 96.6 %, strict 96.6 %, met
  (run kb-20261121-234721-b3aecfe). Its C1 "counts do not agree" came from missing downloads rows
  of the 35 additions; `kb verify-downloads` (run kb-20261121-235128-dcd72a4) recorded all 60
  additions ok; exit 1 is the known gr-qc/9412071 (PDF only).
- Snapshots: kb-20261121-bbaafe5, then kb-20261121-aa0a2ae (db/current: claim 861, downloads).
