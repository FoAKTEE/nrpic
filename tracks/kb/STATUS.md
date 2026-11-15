# STATUS of kb

gate:        KB-G1 package updated 2026-11-15 (tracks/kb/stage/KB-G1/); KB-G0 package written
             (stage/KB-G0/); both complete except VERIFIER_REPORT.md (no verifier assigned to kb);
             KB-G2 not met
headline:    709 papers, 688 claims, vectors of all text chunks and equations, equation tags,
             first QA report; every kb-request of waves 1-2 answered; db/current
             kb-20261115-a848a06
last-result: - lead review of the three wave-2 helpers from their outputs (stage/REVIEW-wave2.md):
               serve locators 372/372, reading 12/12; QA counts recounted exactly (W4); retrieval
               rescored identically (ten: hybrid 5, K9: 23/32); vectors complete; tags 16/18
             - wrong and fixed: F answer (0.07 is at mnras.tex:762), claim-parser table-row
               defect (claim 193), 17 failing tests (fixture), kb claim/qa not wired, lead
               equation counter (trailing row, multline); 173 tests pass
             - 70 served statements loaded as claims 619-688 (kb-20261115-182425-edbae8b);
               claims 25, 674 verified by reading (kb-20261115-183921-31d5b77)
             - metadata: arXiv API 708/708, INSPIRE 704/708 (kb-20261115-182505-7e3a0b5);
               2201.09277 (C) and 2107.06643 (D) found by DOI, fetched, ingested, embedded
             - snapshot kb-20261115-a848a06 = db/current
next:        1. KB-G2 path: ingest gr-qc/9412071 from its stored PDF (reader for source.pdf);
                read meta/arxiv-api and meta/inspire into the papers table, compare with brief 16
             2. K9 rerun: qa_report reads meta/inspire/<key>.json for C4; `kb qa run --hybrid`
                with all vectors; kb/QA_REPORT.md, kb/golden/questions.yaml
             3. retrieval at the answer location (72 % on 32 questions): finer chunks or windowed
                vectors, chosen on one set, checked on the other; seed the brief's own statements
blockers:    KB-G2 thresholds not in CHARTER (orch); verifier for kb packages (orch)
needs:       orch: verifier-for-kb, kb-g2-hit-level, non-arxiv-pdf,
             extras-as-manifest-additions, nrpic-run-literal-run-dir (outbox 20261115T1838Z__*);
             still open from wave 1: kb-g2-thresholds, brief-corrections, paper-code-links (core)
offers:      db/current kb-20261115-a848a06 (read-only); `kb search` (hybrid or --text-only),
             `kb eq --tag`, `kb claim list/show`, `kb qa` on branch kb/main; AthenaK parameter
             tables kb/reports/code_params_*.tsv; answers in tracks/kb/outbox/20261115T18*
budget:      0 card-hours used of 0 allotted (decision 0014); lead runs at most 8 cores; two
             helper embedding runs used 12 and 16 threads (recorded in REVIEW-wave2.md)
