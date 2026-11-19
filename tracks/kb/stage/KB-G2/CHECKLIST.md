# Checklist: kb KB-G2

Collected by `harness/bin/nrpic-stage collect kb KB-G2` on 2026-11-19T16:21:41Z from the brief (sections 12.10, 13.3), `coord/CHARTER.md` (9.10).
For each item set `status:` to PASS, FAIL or NA (OPEN until judged) and give the evidence: run ids,
figure files, KB locators, commits. `nrpic-stage report` reads this file; the automated checks are
in VERIFY_RESULTS.md (`nrpic-stage verify`), not here.

## Criteria of the knowledge base for KB-G2 (brief 12.10; charter 9.10)

- [x] **C1** All papers and repositories ingested
  - status: PASS
  - evidence: Papers: 710 of 710 manifest ids ingested (684 of brief section 17, gr-qc/9412071 from its PDF since wave 2b, run kb-20261119-142651-7318d01; 26 additions of decision 0016 item 6), QA C1 of run kb-20261119-161633-1d05960 on snapshot kb-20261119-a782f1e (kb/QA_REPORT.md). Repositories: 63 of 63 of the manifest and this repository (re-indexed at main 5deee18, run kb-20261119-161451-e15d1b8). Quality caveat, not an ingestion gap: 20 TeX papers have no bibliography entry (OPEN.md).
- [x] **C2** The QA report meets the parse success rate and retrieval hit rate written in CHARTER (thresholds: coord/CHARTER.md, "Gates of the knowledge base"; items below)
  - status: PASS
  - evidence: kb/QA_REPORT.md (run kb-20261119-161633-1d05960, snapshot kb-20261119-a782f1e) meets both thresholds of the charter: C3 and C4 below. Figure tracks/kb/note/figures/fig_kbg2.png (run kb-20261119-162642-25012f7), inspected.

## Thresholds of KB-G2 (coord/CHARTER.md, "Gates of the knowledge base"; decision 0016 item 6)

- [x] **C3** Parse success rate: at least 95 per cent of the ingested papers are parsed successfully.
  - status: PASS
  - evidence: Parse status ok for 684 of 710 ingested papers = 96.3 % (23 review, 3 pdf); 96.8 % if a paper read from its PDF counts. Caveat of the KB-G1 verifier: 11 papers with status ok have no bibliography entry; counted as failures the rate is 673/710 = 94.8 % (676/710 = 95.2 % with the PDF papers). So the bar is met on the status the knowledge base records and is borderline under the strictest reading; the bibliography-parser fix (OPEN.md) removes the doubt. fig_kbg2.png panel (a).
- [x] **C4** Retrieval hit rate: at least 80 per cent of the golden questions are answered with the right paper among the top ten results; the hit at the answer location is reported, not gating.
  - status: PASS
  - evidence: Right paper in the top ten for 28 of 32 golden questions = 87.5 % with hybrid search and with rerank (text only: 27 = 84.4 %); answer location in the top ten (reported, not gating): rerank 25 = 78.1 %, hybrid 23 = 71.9 %, text 21 = 65.6 %. Run kb-20261119-161633-1d05960 on kb-20261119-a782f1e; equal question by question to the retrieval helper's run on a848a06 except q01 hybrid location rank 7 -> 6; the helper's ranked lists rescored by the lead with own code (run kb-20261119-155310-e600e38). Caveat: the re-ranking was chosen on these 32 questions (in-sample); a held-out set is requested from orch.

## Rules of brief 12.10 that hold at every stage of the knowledge base

- [x] **C5** Tracks read the knowledge base read-only: `kb` opens db/current by default (brief 12.10)
  - status: PASS
  - evidence: kb opens db/current by default; snapshots are mode 0444 (kb-20261119-a782f1e: -r--r--r--).
- [x] **C6** `kb snapshot` run at the end of the stage; its identifier recorded in the package, and every locator cited from the knowledge base carries it (brief 12.10)
  - status: PASS
  - evidence: Snapshot kb-20261119-a782f1e (run kb-20261119-161451-e15d1b8; sha256 a782f1ee...), db/current; every number of this package is on it except the retrieval helper's R4 (a848a06), named as such.

## Package (brief 13.3, decision 0012; judged by the session)

- [x] **C7** Package documents of decision 0012: STAGE_REPORT.md (nrpic-stage report), EVIDENCE.md, OPEN.md and this CHECKLIST.md in the stage directory; REVIEW.md where the lead rechecked helpers; the scoping text in SCOPE.md or SCOPING.md beside them or in the scope directory, named in the report (no REPORT.md needed)
  - status: PASS
  - evidence: STAGE_REPORT.md (nrpic-stage report), EVIDENCE.md, OPEN.md, this CHECKLIST.md, REVIEW.md (and ../REVIEW-wave2.md, section wave 2b); scope SCOPE.md (as ../KB-G0/SCOPE.md).
- [ ] **C8** Verifier subagent (fresh context) wrote VERIFIER.md (decision 0016; VERIFIER_REPORT.md accepted too): the package's numbers recomputed from the run manifests and the snapshot
  - status: FAIL
  - evidence: No verifier report for KB-G2. The KB-G1 verifier of wave 2b did not check retrieval, embeddings, metadata or parse rates (VERIFIER.md of KB-G1, 'Not checked'). The second checks so far are the lead's own (B1, B2: helper numbers reproduced exactly). Requested from orch (outbox, kb-g2-verifier).
- [x] **C9** Null results and failed runs are on record (manifests and JOURNAL)
  - status: PASS
  - evidence: Failed predictions on record: tracks/kb/JOURNAL.md B2 (C4 ratio of my own instrument), tracks/kb/retrieval/JOURNAL.md R3 (refuted), R4 (25 instead of >= 26), tracks/kb/pdf_meta/JOURNAL.md P1, P3, P4 parts; failed run kb-20261119-143242-737909d (an option kb embed does not have).
- [x] **C10** STATUS.md, JOURNAL.md and HANDOFF.md are current
  - status: PASS
  - evidence: STATUS.md, HANDOFF.md rewritten and JOURNAL.md appended in this session (kb lead, wave 2b, 2026-11-19).
