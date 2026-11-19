# STATUS of kb

gate:        KB-G1 package complete for review (tracks/kb/stage/KB-G1/, all 10 items PASS with the
             verifier's VERIFIER.md); KB-G2 thresholds met on kb-20261119-a782f1e but package
             incomplete (no verifier, C8 FAIL); no gate passed yet (orch reviews)
headline:    710 papers (684 + 26 additions) all ingested, arXiv/INSPIRE metadata in the papers
             table, parameter index at main, 700 claims; parse ok 96.3 %, golden paper hits
             28/32 (87.5 %), answer location 25/32 with `kb search --rerank`; db/current
             kb-20261119-a782f1e
last-result: - lead review of pdf_meta, retrieval and the KB-G1 verifier (stage/REVIEW-wave2.md,
               wave 2b; fig note/figures/fig_w2b_review.png): helper numbers reproduced exactly
               (B1 kb-20261119-155134-17d6704, B2 kb-20261119-155310-e600e38); every verifier
               WRONG item confirmed (B3 kb-20261119-155315-b2c7420)
             - wrong/new: PDF Greek mapping 17/20 (cmsy/cmex symbols read as Greek); 2602.00155 a
               7th cause of lost bibliographies; claim 25 defect caused by my wave-2 verify
             - fixed: claim locator rows (`kb claim relocate`, verify --locator), parameter index
               re-indexed at main 5deee18 (kb-20261119-161451-e15d1b8, 1242 rows, links 25/25),
               `kb ingest pdf`, `kb meta`, ingest reads metadata back, `kb search --rerank`, QA
               C1/C2/C4; 220 tests pass
             - KB-G2 QA on a782f1e (kb-20261119-161633-1d05960): 710/710 ingested, ok 684/710,
               paper 28/32 hybrid and rerank, location 25/32 rerank; fig note/figures/fig_kbg2.png
             - verifier scripts rerun registered on a782f1e: identical (kb-20261119-161909-08df7ea)
             - claims 689-700 (B 7, C 1 verified by reading; D 4 annotations) (kb-20261119-161413-31e6b85)
next:        1. bibliography parser for REVTeX-3 references, AASTeX \reference, \bi/\bib macros,
                \harvarditem, unreached .tex; status review when \cite but no entry; claim
                chunk remap before re-ingesting the 20 papers
             2. KB-G2 verifier (orch) and a held-out golden set; then the R4b remedies
             3. KB-G3: seed the brief's labelled statements; work the 117 to_verify, 43
                unlocated, 34 partial claims; `kb claim` command to attach evidence (D 682/683)
blockers:    KB-G2 package needs a verifier (orch); held-out questions need a writer (orch)
needs:       orch: kb-gates-wave2b (KB-G1 review; accept the registered rerun of the
             verifier's runs), kb-g2-verifier, heldout-golden-questions,
             additions-groups-and-0608095, arxiv-licences, brief16-titles-authors (pdf_meta);
             still open from waves 1-2: brief-corrections, paper-code-links (core)
offers:      db/current kb-20261119-a782f1e (read-only); `kb search --rerank`, `kb show` with
             DOI/journal/INSPIRE, `kb code <opt> --kind param --repo local/nrpic` (core-v0.3
             options), `kb claim show`; kb/QA_REPORT.md; kb/golden/questions.yaml
budget:      0 card-hours used of 0 allotted; lead runs at most 6 threads
