# Checklist: kb KB-G1

Collected by `harness/bin/nrpic-stage collect kb KB-G1` on 2026-11-15T18:29:11Z from the brief (sections 12.10, 13.3), `coord/CHARTER.md` (9.10).
For each item set `status:` to PASS, FAIL or NA (OPEN until judged) and give the evidence: run ids,
figure files, KB locators, commits. `nrpic-stage report` reads this file; the automated checks are
in VERIFY_RESULTS.md (`nrpic-stage verify`), not here.

## Criteria of the knowledge base for KB-G1 (brief 12.10; charter 9.10)

- [x] **C1** The inventory report
  - status: PASS
  - evidence: Download inventory: kb/reports/verify-downloads.md (wave 1, run kb-20261115-140336-29f15a1) and reruns kb-20261115-154547-12ef9f0, kb-20261115-182907-3f69615 (manifest 684: ok 683, problem 1 = gr-qc/9412071 PostScript; 63/63 repositories; 26 extras). Metadata part of K1 fetched in wave 2 (run kb-20261115-182505-7e3a0b5: arXiv-API records 708/708, INSPIRE 704/708); the title and author comparison with brief section 16 is not done yet (OPEN.md).
- [x] **C2** All priority-3 papers ingested
  - status: PASS
  - evidence: 47 of 47 priority-3 papers ingested (45 ok, 2 review): priority3_ingestion.tsv (run kb-20261115-141457-b2e57be); unchanged in wave 2.
- [x] **C3** Code index and parameter index of AthenaK
  - status: PASS
  - evidence: Upstream AthenaK c5a0d7f and this tree: kb/reports/code_index.md, code_params.md, code_params_*.tsv (64 repositories, 3454 parameter rows; wave 1); upstream unchanged at the wave-2 watch (run kb-20261115-154646-234060c).
- [x] **C4** The answers to the first questions
  - status: PASS
  - evidence: FIRST_QUESTIONS.md: nine answers with file:line locators (snapshot kb-20261115-f2fcda5); open sub-points in OPEN.md. Wave 2 adds the metadata core asked for (2611.12831: submitted 2026-11-09, gr-qc with astro-ph.GA, astro-ph.HE, physics.plasm-ph, '37 pages, 23 figures'; run kb-20261115-182505-7e3a0b5).

## Rules of brief 12.10 that hold at every stage of the knowledge base

- [x] **C5** Tracks read the knowledge base read-only: `kb` opens db/current by default (brief 12.10)
  - status: PASS
  - evidence: kb opens db/current by default; snapshots are mode 0444; harness doctor row kb PASS in wt/kb.
- [x] **C6** `kb snapshot` run at the end of the stage; its identifier recorded in the package, and every locator cited from the knowledge base carries it (brief 12.10)
  - status: PASS
  - evidence: Snapshot of this update: kb-20261115-44b7406 (run kb-20261115-183052-0f8245e, db/current); the posted answers name it.

## Package (brief 13.3, decision 0012; judged by the session)

- [x] **C7** Package documents of decision 0012: STAGE_REPORT.md (nrpic-stage report), EVIDENCE.md, OPEN.md and this CHECKLIST.md in the stage directory; REVIEW.md where the lead rechecked helpers; the scoping text in SCOPE.md or SCOPING.md beside them or in the scope directory, named in the report (no REPORT.md needed)
  - status: PASS
  - evidence: STAGE_REPORT.md (nrpic-stage report), EVIDENCE.md, OPEN.md, this CHECKLIST.md, REVIEW.md (wave-1 checks L0-L11 in tracks/kb/JOURNAL.md; wave 2 in ../REVIEW-wave2.md); scope: ../KB-G0/SCOPE.md (brief section 12, charter 9.10).
- [ ] **C8** Verifier subagent (fresh context) wrote VERIFIER_REPORT.md: the package's numbers recomputed from the run manifests and the snapshot
  - status: FAIL
  - evidence: No VERIFIER_REPORT.md: no verifier was assigned to kb in waves 1 and 2 (coord/digests/wave-1-plan.md, wave-2-plan.md); the lead's rechecks (JOURNAL L0-L11, W1-W9; ../REVIEW-wave2.md) are the only second check. Requested from orch.
- [x] **C9** Null results and failed runs are on record (manifests and JOURNAL)
  - status: PASS
  - evidence: Failed runs on record: kb-20261115-154858-b0d8c8f, kb-20261115-164121-5aca10c, kb-20261115-181519-d78b8d4, kb-20261115-182907-3f69615 (manifests kept); refuted predictions in tracks/kb/JOURNAL.md (L2, L11, W2) and the package journals (E3 truncation, E4, E5 v1, E6; P5, P6).
- [x] **C10** STATUS.md, JOURNAL.md and HANDOFF.md are current
  - status: PASS
  - evidence: STATUS.md, HANDOFF.md rewritten and JOURNAL.md appended in this session (kb lead, wave 2).
