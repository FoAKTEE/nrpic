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
