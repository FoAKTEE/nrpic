# Checklist: kb KB-G1

Collected by `harness/bin/nrpic-stage collect kb KB-G1` on 2026-11-19T16:19:43Z from the brief (sections 12.10, 13.3), `coord/CHARTER.md` (9.10).
For each item set `status:` to PASS, FAIL or NA (OPEN until judged) and give the evidence: run ids,
figure files, KB locators, commits. `nrpic-stage report` reads this file; the automated checks are
in VERIFY_RESULTS.md (`nrpic-stage verify`), not here.

## Criteria of the knowledge base for KB-G1 (brief 12.10; charter 9.10)

- [x] **C1** The inventory report
  - status: PASS
  - evidence: Download inventory: kb/reports/verify-downloads.md (wave 1, run kb-20261115-140336-29f15a1) and reruns kb-20261115-154547-12ef9f0, kb-20261115-182907-3f69615 (manifest 684: ok 683, problem 1 = gr-qc/9412071 PostScript; 63/63 repositories; 26 extras). Metadata part of K1 fetched in wave 2 (run kb-20261115-182505-7e3a0b5: arXiv-API records 708/708, INSPIRE 704/708). Wave 2b: metadata read into the papers table and compared with brief section 16 (pdf_meta, run kb-20261119-143702-aa436e7: 710 papers with arXiv title/authors/abstract, INSPIRE 706, title_matches_brief 680 agree, 4 differ, 26 additions without a section-16 entry; table tracks/kb/pdf_meta/BRIEF16_ERRATA.md); recounted by the lead (run kb-20261119-155134-17d6704). gr-qc/9412071 ingested from its PDF (run kb-20261119-142651-7318d01): 684 of 684 manifest ids ingested.
- [x] **C2** All priority-3 papers ingested
  - status: PASS
  - evidence: 47 of 47 priority-3 papers ingested (45 ok, 2 review): priority3_ingestion.tsv (run kb-20261115-141457-b2e57be); unchanged in waves 2 and 2b. The verifier found gr-qc/9906015 (priority 3, status review) a shell: no equation numbers, sections or bibliography (WRONG in VERIFIER.md test P); it is ingested and flagged, the plain-TeX reader is open (../KB-G2/OPEN.md).
- [x] **C3** Code index and parameter index of AthenaK
  - status: PASS
  - evidence: Upstream AthenaK c5a0d7f and this tree: kb/reports/code_index.md, code_params.md, code_params_*.tsv (64 repositories, 3454 parameter rows; wave 1); upstream unchanged at the wave-2 watch (run kb-20261115-154646-234060c). Verifier test K (VERIFIER.md): 10 of 10 parameter rows CONFIRMED, recall 83/83 in particles/ and pgen/nrpic/, but the index of this repository was stale (a1c2237; 101 pairs of core-v0.3 missing). Wave 2b: re-indexed at main 5deee18 (run kb-20261119-161451-e15d1b8: 1242 parameter rows, 25/25 curated links OK); the verifier's scripts rerun on the new snapshot give 0 stale pairs and 10/10 rows (run kb-20261119-161909-08df7ea).
- [x] **C4** The answers to the first questions
  - status: PASS
  - evidence: FIRST_QUESTIONS.md: nine answers with file:line locators (snapshot kb-20261115-f2fcda5); open sub-points in OPEN.md. Wave 2 adds the metadata core asked for (2611.12831: submitted 2026-11-09, gr-qc with astro-ph.GA, astro-ph.HE, physics.plasm-ph, '37 pages, 23 figures'; run kb-20261115-182505-7e3a0b5). Verifier test Q (VERIFIER.md, fresh reader, own answers first): 9 of 9 CONFIRMED, 185/185 equation numbers, 73/73 paper and 18/18 code locators; rerun registered on a782f1e: same (run kb-20261119-161909-08df7ea).

## Rules of brief 12.10 that hold at every stage of the knowledge base

- [x] **C5** Tracks read the knowledge base read-only: `kb` opens db/current by default (brief 12.10)
  - status: PASS
  - evidence: kb opens db/current by default; snapshots are mode 0444; harness doctor row kb PASS in wt/kb.
- [x] **C6** `kb snapshot` run at the end of the stage; its identifier recorded in the package, and every locator cited from the knowledge base carries it (brief 12.10)
  - status: PASS
  - evidence: Snapshot of this update: kb-20261119-a782f1e (run kb-20261119-161451-e15d1b8, db/current; 710 papers, 700 claims, local/nrpic at 5deee18); wave 2: kb-20261115-a848a06 (run kb-20261115-183921-31d5b77), on which the verifier worked; the posted answers name the snapshot they cite.

## Package (brief 13.3, decision 0012; judged by the session)

- [x] **C7** Package documents of decision 0012: STAGE_REPORT.md (nrpic-stage report), EVIDENCE.md, OPEN.md and this CHECKLIST.md in the stage directory; REVIEW.md where the lead rechecked helpers; the scoping text in SCOPE.md or SCOPING.md beside them or in the scope directory, named in the report (no REPORT.md needed)
  - status: PASS
  - evidence: STAGE_REPORT.md (nrpic-stage report), EVIDENCE.md, OPEN.md, this CHECKLIST.md, REVIEW.md (wave-1 checks L0-L11 in tracks/kb/JOURNAL.md; waves 2 and 2b in ../REVIEW-wave2.md, which answers every WRONG item of VERIFIER.md); scope: ../KB-G0/SCOPE.md (brief section 12, charter 9.10).
- [x] **C8** Verifier subagent (fresh context) wrote VERIFIER.md (decision 0016; VERIFIER_REPORT.md accepted too): the package's numbers recomputed from the run manifests and the snapshot
  - status: PASS
  - evidence: VERIFIER.md (wave-2b verifier, fresh reader, own code in verifier/): P 18/20 CONFIRMED, 2 WRONG (1201.4794 and gr-qc/9906015 bibliographies); C 10/10; K 10/10 (index stale against main); Q 9/9. Runs kb-20261119-142015-7620bd4, -142303-f38a48c, -142448-3ea268d (hand-written manifests, the shared worktree was dirty); the same scripts rerun unchanged and registered by the lead on kb-20261119-a782f1e: run kb-20261119-161909-08df7ea (papers.tsv identical, zero-bibliography list identical, 0 stale pairs, 0 claims with string and rows disagreeing). Lead's recheck of the WRONG items and the track's action for each: ../REVIEW-wave2.md (wave 2b) and run kb-20261119-155315-b2c7420.
- [x] **C9** Null results and failed runs are on record (manifests and JOURNAL)
  - status: PASS
  - evidence: Failed runs on record: kb-20261115-154858-b0d8c8f, kb-20261115-164121-5aca10c, kb-20261115-181519-d78b8d4, kb-20261115-182907-3f69615 (manifests kept); refuted predictions in tracks/kb/JOURNAL.md (L2, L11, W2; wave 2b: B2 C4 ratio, see JOURNAL) and the package journals (E3 truncation, E4, E5 v1, E6; P5, P6; wave 2b: pdf_meta P1 rare tokens, P3 TeX titles, P4 concentration; retrieval R3, R4; verifier P 'no lost content'). Wave-2b failed run: kb-20261119-143242-737909d (an option kb embed does not have; nothing written).
- [x] **C10** STATUS.md, JOURNAL.md and HANDOFF.md are current
  - status: PASS
  - evidence: STATUS.md, HANDOFF.md rewritten and JOURNAL.md appended in this session (kb lead, wave 2b, 2026-11-19).
