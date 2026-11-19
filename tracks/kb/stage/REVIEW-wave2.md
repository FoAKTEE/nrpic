# Review of the wave-2 helper packages of kb (lead, 2026-11-15, 18:10-19:00Z)

Three helpers worked in `wt/kb` in wave 2: serve (`tracks/kb/served/`), claims (K8, K9;
`tracks/kb/claims/`) and embed (K4, K5; `tracks/kb/embed/`). I rechecked each from its registered
outputs and the store with my own code (`tracks/kb/analysis/lead_checks/w2_*.py`, which imports
neither kbtool nor the helpers' scripts), read every figure of the three packages with the Read
tool, and compared each result with the prediction the helper wrote before the run. Predictions
and outcomes of my checks: `tracks/kb/JOURNAL.md`, entries W1-W7 of this session. Figure:
`tracks/kb/note/figures/fig_w2_review.png` (script `note/scripts/fig_w2_review.py`), inspected.

No verifier was assigned to kb in wave 2 (`coord/digests/wave-2-plan.md`: kb has the helpers
serve, claims, embed and no verifier). There are therefore no verifier items marked WRONG or NOT
CONFIRMED to answer; this review is the second check, and the items below that I found wrong or
could not confirm each carry the track's action (table at the end).

| Check | Run | Prediction | Outcome |
|---|---|---|---|
| W1 kb test suite without NRPIC_HOME after the fixture fix | (pytest, no run dir) | 174 pass | held, 174 pass |
| W2 serve locators, numbers, reading sample | kb-20261115-181544-94f68f2 (first try kb-20261115-181519-d78b8d4 misplaced its output, see JOURNAL) | 372/372 in file; at most 5 helper-exact statements fail my check; reading >= 10/12 | locators held; number part refuted by my own instrument (all 16 disputes read: helper right); reading 12/12 |
| W3 lead equation counter vs pdflatex | kb-20261115-182232-85883d1 | 16 and 6 | held |
| W4 claims QA recount, third equation count, audit | kb-20261115-181916-08ebad9 | exact counts; equal on shorthand-free single-file papers; audit >= 9/10 | held; audit 9/10 (one parser fragment) |
| W5 embed rescoring, vectors, model hash, tags | kb-20261115-182238-b86d2b5 | identical hits; complete vectors; tags >= 14/18 | held; tags 16/18 |
| W6 load of the 70 uncovered served statements into K8 | kb-20261115-182414-e13b30c (dry), kb-20261115-182425-edbae8b | +70 ids 619-688, 1-618 unchanged | held |
| W7 arXiv-API and INSPIRE metadata of 708 ids | kb-20261115-182505-7e3a0b5 | see JOURNAL W7 | outcome in JOURNAL W7 |

## serve (tracks/kb/served)

Confirmed.
- The six fetched papers (2605.30145, 2505.15903, 0707.1350, astro-ph/0608642, gr-qc/0305023,
  1003.4681) have status ok in `kb-data/meta/arxiv/`, their `source.bin` hashes equal the records,
  and all six are papers-table rows with parse_status ok in db/current (kb-20261115-621430e).
- All 372 locators of the 330 served statements lie inside their stored files (my own line count,
  W2). The claim id ranges named in the nine draft answers equal db/current (A 1-170, B 171-228,
  C 229-303 and 304-331, D 332-420, F 421-452, core 453-602, E 603-609, C errata 610-618; label
  counts as stated for A, B, C).
- Reading sample of 12 statements (seed 20261116): 12 supported by the cited lines as worded.
- Upstream watch: the snapshots 20261115T132754Z and 20261115T154646Z of
  `kb-data/meta/github/watch/IAS-Astrophysics__athenak/` have the same 124 tips; main c5a0d7f.
- E's equation number: by my own count of numbered environments in 2502.06783 `main_V2PRD.tex`,
  line 320 lies in equation 23 (eq:eqInitialConditions, from line 317); equation 17 is
  eq:Bardeen (line 248), which defines Psi_G. The discrepancy stands; E may have meant the
  definition. [TO VERIFY against the PDF]
- Figures `fig_locator_check.png` and `watch/fig_code_watch.png` agree with summary.json and the
  watch snapshot.

Wrong (fixed by the lead before posting).
- F answer, newton3 entry BKRS collision_deep: the draft says 1804.02911 `mnras.tex:757-763`
  "has 0.05 but not 0.07". Line 762 prints "about 5-7 %", so both values are at the locator.
  The posted answer says so. (The helper's matcher reads "5-7" as a range, not as two values.)
- The drafts say "db/current is still kb-20261115-f2fcda5" and "no metadata path yet". Both were
  overtaken during the wave: db/current is kb-20261115-621430e (with the 618 claims and the six
  papers), and `nrpic-fetch-arxiv --meta` exists (harness f9ab6c7). The posted answers carry the
  new snapshot, the claim ids 619-688 of the statements the K8 seed had not covered, and the
  metadata the W7 run fetched.
- The journal times of S3-S8 (16:05-17:30) do not match the commits (15:37-15:53Z); the run ids
  carry the true times. Left as written; noted here.

Not confirmed.
- The wording of the served statements beyond my 12-statement sample (the helper says so
  itself). Listed.
- The 13 "number not found" cases as a class: 12 confirmed by reading (track-derived or
  eye-read values, a truncation 0.98 of the printed 0.988, a range read as numbers), 1 wrong
  (above).

## claims (tracks/kb/claims)

Confirmed.
- QA counts recounted with my own SQL on db/current (W4): 25 papers not ok (23 review, 1 pdf,
  1 failed); 38775 of 64712 bibliography entries with an arXiv id (59.9 %); 5700 of 38406
  distinct citation edges inside the corpus (14.8 %, K3's definition); claims by label and status
  exactly as in `QA_REPORT.md`; no id stored in two versions.
- C8 equation count: a third, independent count (the lead's corrected counter) equals the
  database on all 26 shorthand-free single-file papers of the 41-paper sample (30 of 36
  single-file papers in all; the 6 differences are papers with shorthand macros that my counter
  does not expand). The helper's finding that pdflatex numbers an empty last row after a trailing
  `\\` (run kb-20261115-155344-596b4ce) is confirmed by a second synthetic probe (W3), and the
  lead's own checker had the wrong rule: fixed (`analysis/lead_checks/eqcount.py`; it also
  counted multline rows separately, fixed).
- Audit: 9 of 10 freshly drawn fulltext claims are supported by their cited lines (P2 of the
  helper: 29 of 30).
- The incident (the helper's `--rebuild` deleted the serve helper's 330 rows) is recorded in its
  journal; the guard commit daa0aa2 has a test; I loaded the 70 statements the K8 seed does not
  cover through `sync-k8` (W6), with claims 1-618 unchanged (digest before and after).
- Figures `fig_qa_claims.png`, `fig_qa_eqcount.png`, `fig_qa_retrieval.png` agree with qa.json.

Wrong (fixed by the lead).
- Claim 193 is a fragment (`purely by shot noise" (2234-2238)`): B's bullet wraps onto a line
  starting with `|Q_ij|`, which the parser took for a table row. Fixed in
  `kb/kbtool/claims_parse.py` with a test that fails without the fix. Claim 193 stays until the
  next seed (ids are frozen); listed.
- `kb claim` and `kb qa` were not reachable from `kb/bin/kb` (the helper could not edit cli.py).
  Wired in; the stub test replaced by `test_no_stub_left`.
- 17 tests failed without NRPIC_HOME (fixture loaded `unpack` from the main checkout's fetch
  command, which main's f9ab6c7 removed). Fixed: the fixture loads the worktree's command and
  mirrors its layout; 174 tests pass.

Not confirmed or open (large; listed in `stage/KB-G1/OPEN.md`).
- C4 (30 papers against INSPIRE): blocked in the helper's run; the INSPIRE records exist since
  W7 (`kb-data/meta/inspire/`), but `qa_report` reads `meta/arxiv/<id_>.inspire.json`, not the
  layout the fetch command writes. Needs a reader change and a rerun of `kb qa run`.
- The hybrid retrieval figures and numbers of `QA_REPORT.md` were made with 21760-29184 of 43398
  chunks embedded; they are stale for hybrid (the embed helper's runs with all vectors supersede
  them: 23 of 32).
- astro-ph/0003278: flat.tex has `\section` and an abstract environment, the database has no
  section, no abstract and one equation (status review). Cause in the K2 extractor not
  established.
- 39 unlocated, 73 to_verify, 33 partial and 1 unresolved claims are not worked through; the
  brief's own labelled statements (brief 12.8) are not seeded.

## embed (tracks/kb/embed)

Confirmed.
- My rescoring of the helper's registered top-10 lists (chunk -> paper and flat range from the
  database, -> source lines by my own bisection of `sourcemap.json`) gives exactly the helper's
  hits in every mode, with no disagreement on any question: ten questions text 4, vector 4,
  hybrid 5; K9 set text 21, vector 17, hybrid 23 (W5).
- Vectors: one model `bge-small-en-v1.5@5c38ec7`, dimension 384, 43398 chunk and 54259 equation
  vectors, no owner without a vector, no vector without an owner, norms 1 within 1.3e-7. The
  weights' sha256 equals `kb/EMBEDDING.md` (3c9f3166...21ad).
- Tags: 1140 equations carry 1147 tags; my reading of 18 sampled tagged equations (2 per tag):
  16 correct, 2 wrong (2110.11720 eq. 3, a total-Hamiltonian functional, as
  hamiltonian_constraint; 2009.08715 eq. 31, a noise correlator, as langevin).
- The failed predictions are on record as the helper wrote them: hybrid 5 of 10 (predicted 8 or
  more), equation truncation 14.3 % (predicted below 5 %), the E6 prediction (which misread the
  K9 helper's paper-level 27/32 as a locator rate).
- Figures `fig_e1e2_bench.png`, `fig_e4_retrieval.png`, `fig_e6_retrieval_k9.png`,
  `fig_e7_fusion.png` agree with the run outputs.

Wrong (procedural, recorded).
- Two runs used more threads than kb's allotment of 8 cores at a time (decision 0006, as
  `nrpic-run` enforces it): the benchmark kb-20261115-152906-ca81acd (16 threads) and the full
  embedding kb-20261115-153805-e164901 (12 threads, 60 min). Both were registered by hand, so no
  tool refused them. Nothing to undo; later embedding runs go through `nrpic-run` with at most
  8 cores (the W9b run did).

Caveats (not defects).
- The fusion constant k = 10 was chosen on the K9 set, so 23/32 on K9 is in-sample; the held-out
  gain is one question of ten (4 -> 5).
- Retrieval at the locator level is 23 of 32 (72 %) on K9 and 5 of 10 on the ten; at the paper
  level 28 of 32. Whether the proposed KB-G2 threshold (80 % in the top 10) is met depends on
  which level CHARTER names; at the locator level it is not.

Open (listed).
- Code chunks have no vectors; papers ingested later need `kb eq --apply-tags` and `kb embed`
  (ingest does not call them); hybrid search costs 9.5 s per call (model load).

## What the track does about each wrong or unconfirmed item

| Item | Action | Where |
|---|---|---|
| F answer: 0.07 "not found" | corrected in the posted answer | outbox `__to-F-hills__index-hills-sources` |
| outdated snapshot and metadata statements in the drafts | answers posted with snapshot kb-20261115-<new>, claim ids 619-688 and W7 metadata | `tracks/kb/outbox/` |
| claim 193 fragment | parser fixed and tested; the claim is superseded at the next seed | `kb/kbtool/claims_parse.py`; OPEN.md |
| kb claim / kb qa not wired | wired, tested | `kb/kbtool/cli.py`, `kb/tests/test_cli.py` |
| 17 failing tests | fixture fixed, 174 pass | `kb/tests/conftest.py` |
| lead counter rules (trailing row, multline) | fixed, confirmed by pdflatex | `analysis/lead_checks/eqcount.py`, run kb-20261115-182232-85883d1 |
| C4 INSPIRE sample | metadata fetched (W7); reader change and QA rerun are next | OPEN.md, HANDOFF.md |
| stale hybrid numbers in QA_REPORT.md | superseded by the embed runs; rerun `kb qa run --hybrid` next | OPEN.md |
| astro-ph/0003278 sections | K2 extractor investigation | OPEN.md |
| two wrong tag rules | regression cases and rule change next (hamiltonian functional, correlator form) | OPEN.md |
| wording beyond the samples | no automatic check can do it; claims stay `located`, not `checked` | OPEN.md |
| E's equation number | asked of E in the posted answer [TO VERIFY] | outbox `__to-E-stoch-inf__errata-s11-references` |
| embedding runs above 8 cores | recorded; later runs through nrpic-run with at most 8 | this file; JOURNAL |

---

# Wave 2b: review of the helper packages pdf_meta, retrieval and the KB-G1 verifier (lead, 2026-11-19, 15:45-16:45Z)

Three helpers worked in `wt/kb` in wave 2b: pdf_meta (`tracks/kb/pdf_meta/`), retrieval
(`tracks/kb/retrieval/`) and a fresh verifier of KB-G1 (`tracks/kb/stage/KB-G1/VERIFIER.md`,
`verifier/`). I rechecked each from its registered outputs and the databases with my own code
(`tracks/kb/analysis/lead_checks/w2b_*.py`, which imports neither kbtool nor the helpers'
scripts), read every figure of the three packages with the Read tool, and compared each result
with the prediction the helper wrote before the run. My predictions and outcomes: `tracks/kb/JOURNAL.md`,
entries B1-B3, D1, D2, Q1 of this session. Figure: `tracks/kb/note/figures/fig_w2b_review.png`
(script `note/scripts/fig_w2b_review.py`, run kb-20261119-161744-2d5ecc8), inspected.

| Check | Run | Prediction | Outcome |
|---|---|---|---|
| B1 pdf_meta: PDF papers, metadata columns, additions, vectors; reading of 20 word and 20 Greek repairs; the brief-16 errata | kb-20261119-155134-17d6704 | counts as reported; word repairs >= 18/20; Greek >= 15/20 | held; 20/20 and 17/20 |
| B2 retrieval: rescoring of R4's ranked lists, final run against R4, C4 | kb-20261119-155310-e600e38 | identical hits in all modes; C4 below a bar exactly 2103.01183, gr-qc/9905058 | held, except my word-level C4 ratio also flags gr-qc/0312117 (a misspelling in both records) |
| B3 verifier: zero bibliographies, plain TeX, claim 25, parameter index | kb-20261119-155315-b2c7420 | 20 papers, 11 ok; causes found in the 14; claim 25 one row | held; a seventh cause found (2602.00155) |
| D1 claims updates (claim 25, C 249/313, B x7, C x1, D x4) | kb-20261119-161413-31e6b85 | 700 claims, checked 39 | held |
| D2 re-index of this repository at main, curated links, snapshot | kb-20261119-161451-e15d1b8 | params +101 or more; links >= 20/25 OK | held: 1115 -> 1242 rows, 25/25 links OK; snapshot kb-20261119-a782f1e |
| Q1 `kb qa run --hybrid` on kb-20261119-a782f1e | kb-20261119-161633-1d05960 | see JOURNAL Q1 | see JOURNAL Q1 and `stage/KB-G2/` |

## pdf_meta (tracks/kb/pdf_meta)

Confirmed (my own SQL on kb.sqlite, B1).
- gr-qc/9412071 is in the base from its stored PDF: parse_status pdf, 6 sections, 16 chunks (1
  abstract, 14 body, 1 caption), 19 bibliography entries, 32 outgoing citation rows, 36 incoming;
  astro-ph/9407016 (before: failed) 12 sections, 45 chunks, 22 entries; 2201.03458 5 sections,
  70 entries. Every one of the 74 chunks has a vector; 43560 chunks = 43560 vectors, 0 orphans.
- Abstract of gr-qc/9412071 against the arXiv-API abstract: 0.994 by my word-sequence measure.
- Metadata: 710 papers, arXiv-API title, authors, abstract, class and dates for 710, INSPIRE 706,
  DOI 651, journal reference 648, licence 0, stored version = API latest for 710; papers.title
  equals the API title for 25 of 25 random papers; title_matches_brief 680/4/26.
- Additions: `kb/manifests/arxiv_additions.tsv` holds exactly the 26 ids outside arxiv.tsv, with
  the groups the papers table carries; no paper without a group.
- The four section-16 rows I read (2310.00776, 2107.06306, 2204.13098, 1203.6185) say what the
  helper says, from the brief line its table names and both metadata records.
- Word repairs of the PDF reader: 20 of 20 right in a fresh sample (seed 20261120) beside the
  helper's 30 of 30.
- Figures fig_pdf_reader, fig_brief16, fig_metadata agree with the numbers.

Wrong or not as reported.
- "gr-qc/9412071 ... 32 citation keys": 32 citation rows, 19 distinct keys. Wording only.
- The Greek mapping ('cmmi-greek', 545 edits, not in the helper's audit) is right for letters in
  formulas but maps characters of other TeX fonts as math italic: 3 of my 20 are wrong (an
  equivalence sign and an approximation sign of cmsy, a parenthesis of cmex), and an
  affiliation word ("Física", OT1 accent and dotless i) became Greek. Affects the text of the two
  1994-95 PDFs only; equations of PDF papers are not indexed anyway. Listed, not fixed.
- fig_pdf_reader draws the abstract bar at 0.6 where the prediction said 0.8; fig_brief16's
  right panel starts at 0.6. Cosmetic; left as committed.

Not confirmed.
- The comparison of all 684 section-16 entries beyond the four rows I read (I did not read the
  brief's section 16, which is outside the lines my task names).

## retrieval (tracks/kb/retrieval)

Confirmed (B2).
- My rescoring of R4's top-10 chunk lists (run kb-20261119-142613-942f713) with my own source-map
  bisection gives the helper's counts in all six modes on both sets, with no question that
  disagrees: golden 32 (5-line slack) text 27/21, hybrid 28/23, w2 27/22, w3 28/22, w2+stage1
  29/23, w2-noexpand 28/25 (paper / answer location); ten held out 9/4, 9/5, 7/6, 7/6, 8/6, 8/6.
- The final QA run (kb-20261119-151500-2721f64) equals R4 on all 96 (mode, question) pairs.
- The predictions were committed before the runs (6b0e3a4 at 06:17 PST before run 142613 at
  06:26 PST); the failed ones are on record (R3 refuted, R4 25 instead of >= 26).
- C4: 30 of 30 sampled papers have an INSPIRE record file; the two the helper lists are parse
  defects of the TeX title (2103.01183, gr-qc/9905058).
- Figures fig_r4_rerank and fig_r5_c4 agree with rerank_eval.json and qa.json.

Wrong.
- Nothing in the numbers. The commit message of fdb7c90 miscounts the tests (helper said so).

Not confirmed / open.
- Whether w2-noexpand generalizes: chosen on the 32 questions the helper inspected; the ten are
  not independent (shared passages). A held-out set written by someone who has not seen R3/R4 is
  needed (request recorded in OPEN.md of KB-G2).

## KB-G1 verifier (tracks/kb/stage/KB-G1/VERIFIER.md)

Confirmed (B3). Every WRONG item and defect the verifier lists holds on my own count:
- 20 of 707 TeX papers have no bibliography entry, 11 with status ok; my patterns find the
  verifier's cause in all 14 it named; 1201.4794 has 46 `\reference` lines; gr-qc/9906015 58 live
  `\eqno`, no sections, 21 plain `\ref` items.
- Claim 25 had one locator row for a two-part locator string.
- The parameter index of this repository was built at a1c2237 and lacked every option of the
  files I checked on main (12/12 nrpic_collide, 13/14 scalar_field, 5/5 nrpic_kick, 2/5 nrpic_cf).
- Its figures fig_papers, fig_summary, fig_zero_bib agree with papers.tsv and zero_bib.tsv.
- Additional finding: 2602.00155 keeps 28 `\bibitem` in paper.tex, which its main file does not
  reach; the verifier counted it as "no list recognized".

Not rechecked: tests C (ten claims) and Q (nine first questions), 10/10 and 9/9 CONFIRMED; I read
the cited lines of claim 25 (L1084, the e = 0.2 case) only.

## What the track does about each WRONG or NOT CONFIRMED item (verifier and helpers)

| Item | Verdict | Action | Where |
|---|---|---|---|
| Verifier P: 1201.4794 bibliography lost (AASTeX `\reference`), status ok | WRONG | large: bibliography parser must read REVTeX-3 `references`, `\reference`, `\bi`/`\bib` macros, `\harvarditem`; re-ingest of 14 papers changes their chunk ids, which claims reference, so it needs the claim-chunk remap; next session | KB-G2/OPEN.md; RISKS.md |
| Verifier P: gr-qc/9906015 plain TeX shell (no numbers, sections, bibliography) | WRONG (flagged review) | stays on the review list; plain-TeX `\eqno`, headings and `\ref` items need a plain-TeX reader; next session | KB-G2/OPEN.md |
| Verifier defect 1: 11 papers ok with zero entries | defect | quality score must drop to review when `\cite` is present and entries are 0 (with the parser fix) | KB-G2/OPEN.md |
| Verifier defect 2: parameter index stale | defect | fixed: `kb ingest repo --this --ref main` (5deee18), 1242 rows, 25/25 curated links OK, snapshot a782f1e | run kb-20261119-161451-e15d1b8 |
| Verifier defect 4: claim 25 lost L1084 | defect | fixed: cause was my wave-2 `kb claim verify --locator`, which changed claims.locator but not the rows; verify now rewrites the rows, `kb claim relocate` added; claim 25 has 2 resolved rows | kb/kbtool/claims_db.py, test_lead_w2b.py; run kb-20261119-161413-31e6b85 |
| Verifier defect 5: claim 254 and Q8 locator offsets | minor | left; content right | - |
| Verifier request 4 / helpers: runs refused in the shared worktree | process | from wave 2b `--package DIR` exists (decision 0016 item 3); the verifier's three hand-written manifests are listed in KB-G1 EVIDENCE | KB-G1/EVIDENCE.md |
| pdf_meta: Greek mapping wrong for cmsy/cmex characters | defect (mine, B1) | listed; low effect | KB-G2/OPEN.md |
| pdf_meta: no snapshot; modules not wired; QA C2/C4 semantics | open | fixed: `kb ingest pdf`, `kb meta`, ingest reads metadata back, C1/C2/C4 changed; snapshot kb-20261119-a782f1e | commit 31e6b855 |
| retrieval: `--rerank` not in `kb search`; kb/QA_REPORT.md stale | open | fixed: `kb search --rerank`; kb/QA_REPORT.md and kb/golden/questions.yaml from Q1 | commit 31e6b855; Q1 |
| retrieval: no independent held-out set | NOT CONFIRMED (generalization) | request: 20 or more questions written by someone who has not seen R3/R4 (orch to assign) | outbox to orch |
| retrieval: q16 location arguably too narrow | open | left as written (changing the golden set after seeing the results would bias it) | - |
| pdf_meta: section-16 rows beyond the four I read | NOT CONFIRMED | proposal to orch stands as the helper's; orch decides | outbox 20261119T143821Z |
