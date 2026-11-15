# STATUS of kb

gate:        KB-G1 package submitted 2026-11-15 (tracks/kb/stage/KB-G1/); KB-G0 met
headline:    683 of 684 manifest papers verified, 701 ingested, 64 repositories indexed
             with AthenaK parameter tables; the nine first questions answered with locators;
             two equation-extraction defects found and fixed (28 papers re-ingested)
last-result: - verify-downloads rerun kb-20261115-140336-29f15a1: ok 683, problem 1
               (gr-qc/9412071 PostScript), missing 0, extra 18; 63/63 repositories
             - priority 3: 47/47 ingested, 45 ok, 2 review (stage/KB-G1/priority3_ingestion.tsv)
             - lead checks L1-L11 of the helpers' artefacts held (L2, L11 as worded refuted by
               my own instruments; journal); 110 tests pass
             - fixes: \nc-aliased definitions (8 papers), \bea = equation+aligned (20 papers),
               kb export headings; runs kb-20261115-141159-bf9c30f, kb-20261115-141358-9043e03
             - snapshot kb-data/db/kb-20261115-f2fcda5.sqlite = db/current
next:        1. Serve the five kb-requests (A, B, C x2, E; tracks/kb/inbox_acks.txt):
                ingest their locators as claims once K8 exists; fetch B's and A's extra ids
             2. K8 claims layer (seed from the brief's labelled statements) and K9 QA report
                with golden questions and a sampled independent equation count
             3. K4-K5 embeddings and equation tags once orch answers the model request
blockers:    metadata path for arXiv API / INSPIRE (orch); PDF path for 2 PostScript-only
             papers (orch); embedding model download (orch)
needs:       orch: metadata-path, fetch-arxiv-pdf-and-hardening, gitignore-runs,
             brief-corrections, watch-scheduler, kb-g2-thresholds, embedding-model;
             core: paper-code-links (all as tracks/kb/outbox/20261115T1420Z__*)
offers:      read-only snapshot kb-data/db/kb-20261115-f2fcda5.sqlite; `kb show/export/cites/
             frontier/code/link` (kb/bin/kb, branch kb/main); AthenaK parameter tables
             kb/reports/code_params_*.tsv; answers stage/KB-G1/FIRST_QUESTIONS.md
budget:      0 GPU-hours used of 0 allotted (decision 0006); at most 8 cores used
