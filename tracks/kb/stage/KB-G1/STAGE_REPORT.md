# Stage report: kb KB-G1

Date: 2026-11-19 · branch `kb/main` at `78282d393e8d` · checklist
`tracks/kb/stage/KB-G1/CHECKLIST.md` (from `nrpic-stage collect`)

## Verdict

**PASS**. Tag: `stage/kb/KB-G1-pass-20261119` (created and pushed by the orchestrator after review, decision 0003).

## Package documents (decision 0012)

| Document | State |
|---|---|
| `stage/KB-G1/STAGE_REPORT.md` | present |
| `stage/KB-G1/EVIDENCE.md` | present |
| `stage/KB-G1/OPEN.md` | present |
| `stage/KB-G1/CHECKLIST.md` | present |
| `stage/KB-G1/VERIFIER.md` (verifier's report) | present |
| `stage/KB-G1/REVIEW.md` | present |
| scoping text | `stage/KB-G1/SCOPE.md` |

## Criteria (coord/CHARTER.md, gate KB-G1 of this track)

| # | Criterion | Evidence (run id, figure, KB locator) | Result |
|---|---|---|---|
| C1 | The inventory report | Download inventory: kb/reports/verify-downloads.md (wave 1, run kb-20261115-140336-29f15a1) and reruns kb-20261115-154547-12ef9f0, kb-20261115-182907-3f69615 (manifest 684: ok 683, problem 1 = gr-qc/9412071 PostScript; 63/63 repositories; 26 extras). Metadata part of K1 fetched in wave 2 (run kb-20261115-182505-7e3a0b5: arXiv-API records 708/708, INSPIRE 704/708). Wave 2b: metadata read into the papers table and compared with brief section 16 (pdf_meta, run kb-20261119-143702-aa436e7: 710 papers with arXiv title/authors/abstract, INSPIRE 706, title_matches_brief 680 agree, 4 differ, 26 additions without a section-16 entry; table tracks/kb/pdf_meta/BRIEF16_ERRATA.md); recounted by the lead (run kb-20261119-155134-17d6704). gr-qc/9412071 ingested from its PDF (run kb-20261119-142651-7318d01): 684 of 684 manifest ids ingested. | PASS |
| C2 | All priority-3 papers ingested | 47 of 47 priority-3 papers ingested (45 ok, 2 review): priority3_ingestion.tsv (run kb-20261115-141457-b2e57be); unchanged in waves 2 and 2b. The verifier found gr-qc/9906015 (priority 3, status review) a shell: no equation numbers, sections or bibliography (WRONG in VERIFIER.md test P); it is ingested and flagged, the plain-TeX reader is open (../KB-G2/OPEN.md). | PASS |
| C3 | Code index and parameter index of AthenaK | Upstream AthenaK c5a0d7f and this tree: kb/reports/code_index.md, code_params.md, code_params_*.tsv (64 repositories, 3454 parameter rows; wave 1); upstream unchanged at the wave-2 watch (run kb-20261115-154646-234060c). Verifier test K (VERIFIER.md): 10 of 10 parameter rows CONFIRMED, recall 83/83 in particles/ and pgen/nrpic/, but the index of this repository was stale (a1c2237; 101 pairs of core-v0.3 missing). Wave 2b: re-indexed at main 5deee18 (run kb-20261119-161451-e15d1b8: 1242 parameter rows, 25/25 curated links OK); the verifier's scripts rerun on the new snapshot give 0 stale pairs and 10/10 rows (run kb-20261119-161909-08df7ea). | PASS |
| C4 | The answers to the first questions | FIRST_QUESTIONS.md: nine answers with file:line locators (snapshot kb-20261115-f2fcda5); open sub-points in OPEN.md. Wave 2 adds the metadata core asked for (2611.12831: submitted 2026-11-09, gr-qc with astro-ph.GA, astro-ph.HE, physics.plasm-ph, '37 pages, 23 figures'; run kb-20261115-182505-7e3a0b5). Verifier test Q (VERIFIER.md, fresh reader, own answers first): 9 of 9 CONFIRMED, 185/185 equation numbers, 73/73 paper and 18/18 code locators; rerun registered on a782f1e: same (run kb-20261119-161909-08df7ea). | PASS |
| C5 | Tracks read the knowledge base read-only: `kb` opens db/current by default (brief 12.10) | kb opens db/current by default; snapshots are mode 0444; harness doctor row kb PASS in wt/kb. | PASS |
| C6 | `kb snapshot` run at the end of the stage; its identifier recorded in the package, and every locator cited from the knowledge base carries it (brief 12.10) | Snapshot of this update: kb-20261119-a782f1e (run kb-20261119-161451-e15d1b8, db/current; 710 papers, 700 claims, local/nrpic at 5deee18); wave 2: kb-20261115-a848a06 (run kb-20261115-183921-31d5b77), on which the verifier worked; the posted answers name the snapshot they cite. | PASS |
| C7 | Package documents of decision 0012: STAGE_REPORT.md (nrpic-stage report), EVIDENCE.md, OPEN.md and this CHECKLIST.md in the stage directory; REVIEW.md where the lead rechecked helpers; the scoping text in SCOPE.md or SCOPING.md beside them or in the scope directory, named in the report (no REPORT.md needed) | STAGE_REPORT.md (nrpic-stage report), EVIDENCE.md, OPEN.md, this CHECKLIST.md, REVIEW.md (wave-1 checks L0-L11 in tracks/kb/JOURNAL.md; waves 2 and 2b in ../REVIEW-wave2.md, which answers every WRONG item of VERIFIER.md); scope: ../KB-G0/SCOPE.md (brief section 12, charter 9.10). | PASS |
| C8 | Verifier subagent (fresh context) wrote VERIFIER.md (decision 0016; VERIFIER_REPORT.md accepted too): the package's numbers recomputed from the run manifests and the snapshot | VERIFIER.md (wave-2b verifier, fresh reader, own code in verifier/): P 18/20 CONFIRMED, 2 WRONG (1201.4794 and gr-qc/9906015 bibliographies); C 10/10; K 10/10 (index stale against main); Q 9/9. Runs kb-20261119-142015-7620bd4, -142303-f38a48c, -142448-3ea268d (hand-written manifests, the shared worktree was dirty); the same scripts rerun unchanged and registered by the lead on kb-20261119-a782f1e: run kb-20261119-161909-08df7ea (papers.tsv identical, zero-bibliography list identical, 0 stale pairs, 0 claims with string and rows disagreeing). Lead's recheck of the WRONG items and the track's action for each: ../REVIEW-wave2.md (wave 2b) and run kb-20261119-155315-b2c7420. | PASS |
| C9 | Null results and failed runs are on record (manifests and JOURNAL) | Failed runs on record: kb-20261115-154858-b0d8c8f, kb-20261115-164121-5aca10c, kb-20261115-181519-d78b8d4, kb-20261115-182907-3f69615 (manifests kept); refuted predictions in tracks/kb/JOURNAL.md (L2, L11, W2; wave 2b: B2 C4 ratio, see JOURNAL) and the package journals (E3 truncation, E4, E5 v1, E6; P5, P6; wave 2b: pdf_meta P1 rare tokens, P3 TeX titles, P4 concentration; retrieval R3, R4; verifier P 'no lost content'). Wave-2b failed run: kb-20261119-143242-737909d (an option kb embed does not have; nothing written). | PASS |
| C10 | STATUS.md, JOURNAL.md and HANDOFF.md are current | STATUS.md, HANDOFF.md rewritten and JOURNAL.md appended in this session (kb lead, wave 2b, 2026-11-19). | PASS |

## Re-verification on a clean checkout (`nrpic-stage verify`)

`nrpic-stage verify` on 2026-11-19T16:33:14Z, clean export of `78282d393e8d`: **PASS**. Details: `VERIFY_RESULTS.md`.

| Check | Result | Message |
|---|---|---|
| clean | PASS | worktree clean (outside the stage directory being assembled) |
| sync | PASS | main is merged into the branch |
| export | PASS | clean export of 78282d393e8d (HEAD) in /data/haiyangw/nrpic/scratch/kb/tmp/stage-verify/kb-KB-G1-78282d3-20261119T163032Z/tree |
| size | PASS | no committed file of the track above 5 MB |
| note | WARN | no tracks/<ID>/note/main.tex (working note) |
| package | PASS | EVIDENCE.md, OPEN.md, CHECKLIST.md present (decision 0012); scoping text: stage/KB-G1/SCOPE.md; REVIEW.md present; verifier's report VERIFIER.md |
| style | PASS | 1 style copies equal harness/style/SHA256SUMS (figstyle.py) |
| fig-script | PASS | 3 figures, each with its script |
| min-figs | PASS | 0 schematics and 3 data figures (brief 13.4 asks at least 0 and 0 at KB-G1) |
| runs | PASS | 117 run manifests finished (77 hand-written, read as decision 0012 allows), output checksums verified where recorded |
| run-notes | WARN | 76 runs read with defaults or not fully re-verifiable (nrpic-run lint) |
| status | PASS | STATUS.md has 38 lines |
| rerun | PASS | 5 of 5 scripts and commands ran cleanly in the export |
| compare | PASS | 6 regenerated files compared with the committed ones; 0 differ beyond tolerance (rtol 1e-06, atol 1e-12, PNG rms 0.005) |
| regenerate | PASS | all 6 committed figure files regenerated |

## Figures

| File | Script | Kind (data / schematic) | Looked at (PNG read) |
|---|---|---|---|
| note/figures/fig_kbg2.* | note/scripts/fig_kbg2.py | data | to be confirmed by the session |
| note/figures/fig_w2_review.* | note/scripts/fig_w2_review.py | data | to be confirmed by the session |
| note/figures/fig_w2b_review.* | note/scripts/fig_w2b_review.py | data | to be confirmed by the session |

## Verifier report

`tracks/kb/stage/KB-G1/VERIFIER.md` present; its first lines:

> # VERIFIER report: gate KB-G1 of the knowledge base
> 
> Verifier: helper of kb, wave 2b, 2026-11-19 (Opus). Fresh reader: I did not read `REVIEW.md`,
> `../REVIEW-wave2.md`, `VERIFY_RESULTS.*` or `STAGE_REPORT.md` of this package, and I read the
> answers in `FIRST_QUESTIONS.md` only after writing my own answers from the sources (journal
> entry 14:05 UTC and the section Q below). My code (`verifier/`) is my own and does not import
> `kb/kbtool`; it opens the snapshot `kb-data/db/current -> kb-20261115-a848a06.sqlite`
> (sha256 `a848a06b...`) read-only and reads the raw sources as data.
> 
> Runs (hand-written manifests, because `nrpic-run submit` refused the shared worktree while other
> kb helpers had uncommitted code in `kb/kbtool/`; the manifests say so):
> 

## Null results and failed runs

- `kb-20261115-182907-3f69615`: failed (exit 1), kb lead W9: fetch 2201.09277 and 2107.06643 (DOIs of C and D), verify-downloads, ingest, tags, embed, check, snapshot
- `kb-20261119-143242-737909d`: failed (exit 2), pdf_meta P6: vectors for the chunks of the three PDF papers (orphans of the old 2201.03458 chunks removed), coverage check, citation edges resolved

## Open risks


Updated 2026-11-19 (kb lead, wave 2b). Likelihood and effect: low / medium / high.

| Risk | Likelihood | Effect | Watch | Response |
|---|---|---|---|---|
| Parse errors hidden behind a good quality score give tracks wrong equation numbers, locators or missing citation edges (wave 1: 28 papers; wave 2: astro-ph/0003278; wave 2b verifier: 11 papers with status ok and no bibliography entry, 502 reference items lost) | high | high | three independent counters agree on equations (W4, verifier P); the verifier's zero-bibliography scan (run kb-20261119-161909-08df7ea) | parser fix for REVTeX-3 `references`, AASTeX `\reference`, `\bi` macros, `\harvarditem`; status review when `\cite` is present and no entry; re-ingest after a chunk remap of the claims |
| Re-ingesting a paper renumbers its chunks and equations, so claims (chunk_id), vectors and tags point at nothing | high (any re-ingest) | medium | `kb embed --check --work`; claims with_chunk count in `kb claim stats` | remap claim chunk ids from their flat ranges after an ingest (to build); until then re-ingest only papers without claims, and run tags, embed, check after it |
| A track takes a `located` claim for a checked one | medium | high | `kb claim show` gives status and checked_by; audits 29/30, 9/10, verifier C 10/10 | only `checked` claims count as read by a person (39 now) |
| Retrieval generalizes worse than the golden numbers say: the re-ranking was chosen on the 32 questions the helper inspected; the ten held-out share passages with them | medium | medium | paper hit 28/32, answer location 25/32 (rerank) on a782f1e (Q1) | a held-out set of 20 or more questions by someone who has not seen R3/R4 (requested from orch) before any further tuning |
| KB-G2 judged on the lead's own QA run without a second agent | medium | medium | CHECKLIST C8 of KB-G2 | verifier for KB-G2 requested from orch |
| The parameter index goes stale again as core releases change options (wave 2b: 101 pairs missing at a1c2237) | high | medium | `kb code ... --repo local/nrpic`; repos.commit_sha | `kb ingest repo --this --ref main` after each core release merged into main, then `kb link load`, `kb link check`, `kb snapshot` |
| Paper text or third-party figures leave the machine through commits | low | high | `git status` and sizes before each commit; reading samples stay in scratch | scripts write only ids, counts and our wording; pre-commit hook dry run on main (wave 3a) |
| Two writers of kb.sqlite undo each other (wave 2: a `--rebuild` deleted 330 rows; wave 2b: three helpers and wt/kb-brief beside the lead) | low | medium | ingest_log; locks/kb-writer.lock held by every `kb` write | one writer at a time under the lock; snapshots taken by the lead only |
| A download escapes its directory or is executed | low | high | `kb verify-downloads`; the fetch command's limits (decision 0015) | never run code from kb-data/raw; read with python3 -I code outside it |
| PDF text of the 1994-95 papers carries wrong symbols (cmsy/cmex characters mapped as Greek; 3 of 20 sampled) | medium | low | the lead's reading sample (B1) | equations of PDF papers are not indexed; quote PDF papers only after reading the PDF itself |
| Upstream AthenaK publishes a particle-spacetime coupling and nobody notices | medium | medium | `kb watch upstream` each wave; last run kb-20261115-154646-234060c | run it at the start of the next kb session (not run in wave 2b) |
| Tracks treat `claimed` paper-code links as verified | medium | medium | `kb link list`; 25/25 resolve at 5deee18 (run kb-20261119-161451-e15d1b8) | core names tests (outbox paper-code-links, open since wave 1) |
| Snapshots fill the disk (about 1 GB each, nine now) | medium | low | `du -sh kb-data/db` | keep the ones cited in notes (f2fcda5, 621430e, 44b7406, a848a06, a782f1e); prune others by name |

## Decision requested from the group

Review of KB-G1 by the orchestrator (decision 0016 item 4): all ten checklist items PASS with the wave-2b verifier's VERIFIER.md; accept the registered rerun kb-20261119-161909-08df7ea as evidence for the verifier's three hand-written runs of 2026-11-19. The lead does not pass the gate.

## Gate status in plain words (kb lead, wave 2b, 2026-11-19)

- KB-G1: the four criteria are met and the package is complete for the orchestrator's review
  (decision 0016 item 4): every checklist item PASS, `nrpic-stage verify` PASS on a clean export,
  verifier's report `VERIFIER.md` (P 18/20 with 2 WRONG bibliographies, C 10/10, K 10/10, Q 9/9).
  Every WRONG item and defect has the track's action in `../REVIEW-wave2.md` (wave 2b); two are
  fixed (stale parameter index, claim 25), the bibliography parser is open (`OPEN.md`). The verdict
  line above is the harness's reading of the checklist; the lead does not pass the gate.
- KB-G2: the two thresholds of decision 0016 item 6 are met on snapshot kb-20261119-a782f1e
  (parse ok 684/710 = 96.3 %; right paper in the top ten 28/32 = 87.5 %), with the caveat that
  the 11 status-ok papers without bibliography bring the strict rate to 94.8 %; the package
  (`../KB-G2/`) lacks a verifier report and is not complete for review.
- Review of the helpers of waves 2 and 2b: `../REVIEW-wave2.md`.
