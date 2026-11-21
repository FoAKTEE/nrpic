# Checklist: kb KB-G2

Collected by `harness/bin/nrpic-stage collect kb KB-G2` on 2026-11-21T13:00:45Z from the brief (sections 12.10, 13.3), `coord/CHARTER.md` (9.10).
For each item set `status:` to PASS, FAIL or NA (OPEN until judged) and give the evidence: run ids,
figure files, KB locators, commits. `nrpic-stage report` reads this file; the automated checks are
in VERIFY_RESULTS.md (`nrpic-stage verify`), not here.

## Criteria of the knowledge base for KB-G2 (brief 12.10; charter 9.10)

- [x] **C1** All papers and repositories ingested
  - status: PASS
  - evidence: Papers: 710 of 710 manifest ids ingested (684 of brief section 17, gr-qc/9412071 from its PDF since wave 2b, run kb-20261119-142651-7318d01; 26 additions of decision 0016 item 6), QA C1 of run kb-20261119-161633-1d05960 on snapshot kb-20261119-a782f1e (kb/QA_REPORT.md). Repositories: 63 of 63 of the manifest and this repository (re-indexed at main 5deee18, run kb-20261119-161451-e15d1b8). Quality caveat, not an ingestion gap: 20 TeX papers have no bibliography entry (OPEN.md). Verifier: CONFIRMED (710/710 ids, none extra, group and priority equal; 64/64 repositories with commit and files; run kb-20261121-080038-306bcdd); lead recount by SQL equal (run kb-20261121-125746-a03875b).
- [x] **C2** The QA report meets the parse success rate and retrieval hit rate written in CHARTER (thresholds: coord/CHARTER.md, "Gates of the knowledge base"; items below)
  - status: PASS
  - evidence: kb/QA_REPORT.md (run kb-20261119-161633-1d05960, snapshot kb-20261119-a782f1e) meets both thresholds of the charter: C3 and C4 below. Figure tracks/kb/note/figures/fig_kbg2.png (run kb-20261119-162642-25012f7), inspected. Verifier: CONFIRMED with a remark (the report gives the same retrieval numbers and 26 papers not ok, but states no parse rate against the 95 % bar; to be added at the next `kb qa run`, OPEN.md).

## Thresholds of KB-G2 (coord/CHARTER.md, "Gates of the knowledge base"; decision 0016 item 6)

- [x] **C3** Parse success rate: at least 95 per cent of the ingested papers are parsed successfully.
  - status: PASS
  - evidence: Parse status ok for 684 of 710 ingested papers = 96.3 % (23 review, 3 pdf); 96.8 % if a paper read from its PDF counts. Caveat of the KB-G1 verifier: 11 papers with status ok have no bibliography entry; counted as failures the rate is 673/710 = 94.8 % (676/710 = 95.2 % with the PDF papers). So the bar is met on the status the knowledge base records and is borderline under the strictest reading; the bibliography-parser fix (OPEN.md) removes the doubt. fig_kbg2.png panel (a). Verifier (VERIFIER.md, Test 3; runs kb-20261120-223309-14e4cb6, kb-20261121-080834-6c50215, kb-20261121-080843-98907be): CONFIRMED narrowly under an explicit definition (sections, equations, bibliography, abstract available to a reader; gaps read at the source subtracted): 679/710 = 95.6 %, 4.5 papers above the bar; 670/710 = 94.4 % if nine letters with run-in headings count as failures; 658/710 = 92.7 % if an extracted abstract chunk is required. Lead recount from the snapshot by own SQL and own evaluation of that definition: 688 lenient, 679 after the nine gaps, 670 with the letters failed; database columns of the verifier's scan equal to my SQL for 710 of 710 papers (run kb-20261121-125746-a03875b, figure ../review_wave3/figures/fig_lead_check_vg2.png). The margin is thin; the remedy is package ingest3 (bibliography formats, old-style headings).
- [x] **C4** Retrieval hit rate: at least 80 per cent of the golden questions are answered with the right paper among the top ten results; the hit at the answer location is reported, not gating.
  - status: PASS
  - evidence: Right paper in the top ten for 28 of 32 golden questions = 87.5 % with hybrid search and with rerank (text only: 27 = 84.4 %); answer location in the top ten (reported, not gating): rerank 25 = 78.1 %, hybrid 23 = 71.9 %, text 21 = 65.6 %. Run kb-20261119-161633-1d05960 on kb-20261119-a782f1e; equal question by question to the retrieval helper's run on a848a06 except q01 hybrid location rank 7 -> 6; the helper's ranked lists rescored by the lead with own code (run kb-20261119-155310-e600e38). Caveat: the re-ranking was chosen on these 32 questions (in-sample). Verifier: CONFIRMED (golden 27/28/28 of 32, text/hybrid/rerank; runs kb-20261121-074940-08426cc, kb-20261121-080557-06d44ba) and, on its blind held-out set of 24 questions (tracks/kb/verify_g2/heldout.yaml, committed 8fb37106 before the first search), 21/22/21 = 87.5/91.7/87.5 %, at or above the golden rates: no sign of tuning on the golden set (runs kb-20261120-222546-ea894c8, kb-20261121-075156-b84a189). Lead recount of the paper hits and rank-1 counts from the raw hit lists: equal in all six set-mode pairs (run kb-20261121-125746-a03875b).

## Rules of brief 12.10 that hold at every stage of the knowledge base

- [x] **C5** Tracks read the knowledge base read-only: `kb` opens db/current by default (brief 12.10)
  - status: PASS
  - evidence: kb opens db/current by default; snapshots are mode 0444 (kb-20261119-a782f1e: -r--r--r--). Verifier: CONFIRMED, statically and by a dynamic test in a fake data root (run kb-20261121-080038-306bcdd).
- [x] **C6** `kb snapshot` run at the end of the stage; its identifier recorded in the package, and every locator cited from the knowledge base carries it (brief 12.10)
  - status: PASS
  - evidence: Snapshot kb-20261119-a782f1e (run kb-20261119-161451-e15d1b8; sha256 a782f1ee...), db/current; every number of this package is on it except the retrieval helper's R4 (a848a06), named as such. Verifier: C6a (snapshot, id recorded) CONFIRMED; C6b WRONG (partly met) on the stricter reading that the tool's locators carry the id: `kb search`, `eq`, `code` name the database file once per answer (footer, JSON info.database), no single hit carries it, `kb show` and `kb cites` print none (lead's check, run kb-20261121-125746-a03875b: confirmed). Lead's judgement [JUDGEMENT]: brief 12.10 asks that a note citing the knowledge base record the snapshot id, which this package and the answers to the tracks do, so C6 as written is met; the tool should still print the id with every locator. The fix (snapshot id in `kb show`, `kb cites` and in each JSON hit) touches kbtool/papers_cli.py, which the unfinished package ingest3 has changed in its private copy; it lands with or after ingest3 (OPEN.md).

## Package (brief 13.3, decision 0012; judged by the session)

- [x] **C7** Package documents of decision 0012: STAGE_REPORT.md (nrpic-stage report), EVIDENCE.md, OPEN.md and this CHECKLIST.md in the stage directory; REVIEW.md where the lead rechecked helpers; the scoping text in SCOPE.md or SCOPING.md beside them or in the scope directory, named in the report (no REPORT.md needed)
  - status: PASS
  - evidence: STAGE_REPORT.md (nrpic-stage report), EVIDENCE.md, OPEN.md, this CHECKLIST.md, REVIEW.md (and ../REVIEW-wave2.md, section wave 2b; ../REVIEW-wave3.md), VERIFIER.md; scope SCOPE.md (as ../KB-G0/SCOPE.md).
- [x] **C8** Verifier subagent (fresh context) wrote VERIFIER.md (decision 0016; VERIFIER_REPORT.md accepted too): the package's numbers recomputed from the run manifests and the snapshot
  - status: PASS
  - evidence: VERIFIER.md (helper verify_g2, wave 3, batches 1 and 2b; fresh context, given artefacts and criteria, not conclusions; own scripts in tracks/kb/verify_g2/scripts, 14 registered runs, two figures): C1, C2, C3, C4, C5, C6a, C9 CONFIRMED; C6b WRONG (partly met); package documents NOT CHECKED (the lead's). Rechecked by the lead from the artefacts (../REVIEW-wave3.md; run kb-20261121-125746-a03875b): every number recomputed held.
- [x] **C9** Null results and failed runs are on record (manifests and JOURNAL)
  - status: PASS
  - evidence: Failed predictions on record: tracks/kb/JOURNAL.md B2 (C4 ratio of my own instrument), tracks/kb/retrieval/JOURNAL.md R3 (refuted), R4 (25 instead of >= 26), tracks/kb/pdf_meta/JOURNAL.md P1, P3, P4 parts; failed run kb-20261119-143242-737909d (an option kb embed does not have). Verifier: CONFIRMED; defect of the record: two wave-1 manifests (kb-20261115-154858-b0d8c8f, kb-20261115-164121-5aca10c) said 'finished' with exit code 1; corrected to 'failed' with a status_note on 2026-11-21. Failed predictions of the verifier itself on record (tracks/kb/verify_g2/README.md: R1, R2, P1, P2, T1).
- [x] **C10** STATUS.md, JOURNAL.md and HANDOFF.md are current
  - status: PASS
  - evidence: STATUS.md, HANDOFF.md rewritten and JOURNAL.md appended by the kb lead, wave 3 batch 3 (2026-11-21), the session that brought this package up to date.
