# KB-G1: what is still open (owner kb, 2026-11-15)

The four listed criteria of KB-G1 are met (`EVIDENCE.md`). Open below: gaps inside stage K1,
open sub-points of the answers, known defects, and the stages that remain before KB-G2.

## Inside K1 (blocked on orch)

- No arXiv-API or INSPIRE metadata: titles, authors, abstracts, categories, licences, DOIs,
  record numbers; `papers.title_matches_brief` is empty; the 30-paper INSPIRE sample of 12.9
  cannot be drawn. 36 ingested papers have no \title, 27 no abstract environment; 17661
  bibliography entries (27.5 %) without an identifier wait for INSPIRE look-ups. Request:
  outbox `__to-orch__metadata-path`.
- Two manifest papers have no TeX: gr-qc/9412071 (gzipped PostScript stored as `main.tex`)
  and astro-ph/9407016 (PostScript files only). They need `source.pdf`. Request: outbox
  `__to-orch__fetch-arxiv-pdf-and-hardening`.

## Open sub-points of the answers (`FIRST_QUESTIONS.md`)

- Q1, Q3: the number of filter passes and every numerical Z4c damping and gauge value
  (kappa_1, kappa_{1,0}, kappa_2, mu_S, eta_0, M_ref, c_H) are not in 2611.12831. Only the
  authors can supply them (decision 0002, a group step).
- Q2: how the momentum constraint is handled for the two moving clumps of Sec. 4 of
  2611.12831. [TO VERIFY]

## Known defects of the knowledge base (not fixed in this session)

- C3: 13 thebibliography papers store an entry count that differs from their \bibitem
  count; one is explained (1005.4054, items after \end{document}), 12 are unexamined.
- Equation numbers of real papers are verified against independent counts (2611.12831 and
  the 28 re-ingested papers) and against pdflatex only on synthetic documents; no .aux of a
  download exists, and downloads are never compiled.
- 23 papers on the review list (18 without \title and abstract environment; plain TeX;
  theses); gr-qc/9906015 (priority 3) yields no sections or bibliography.
- 49 body and 8 appendix chunks exceed 420 words (one sentence unit that cannot be split
  outside math).
- Symbols only for C/C++/CUDA, Python, Fortran; dep and tool repositories have no full-text
  chunks [JUDGEMENT of the K6 helper, to limit size].
- The 25 paper-code links are `claimed`; none is `verified` until core names the test
  (outbox `__to-core__paper-code-links`).
- Cosmetic: the lower-right legend of `fig_papers_k2.png` lacks the "arXiv id" swatch; the
  P4 threshold label overlaps a bar in `fig_code_params.png`.

## Stages that remain (brief 12.3-12.10)

| Stage | Missing |
|---|---|
| K1 (rest) | metadata and the cross-check with brief section 16 (above) |
| K4 | local embedding model (name and revision stored), vectors for chunks, equations, code chunks; hybrid retrieval by reciprocal-rank fusion; `kb embed`, `kb search` exit 3 |
| K5 | `kb/curated/equation_tags.yaml` and tagging (Vlasov, geodesic, Hamiltonian and momentum constraint, Z4c, deposition, compaction function, Langevin, tidal radius), symbol sets; `kb eq` exits 3 |
| K7 (rest) | module descriptions of src/z4c, src/particles, src/pgen, src/mesh, src/bvals from file headers; order of physics calls in the task list |
| K8 | claims: seed import of the labelled statements of the brief, `kb claim add/list/verify/refute` (exit 3); 0 claims |
| K9 | `kb qa run` -> `kb/QA_REPORT.md`; `kb/golden/questions.yaml` with at least 30 questions (hit rate in the top 10); duplicate versions; parse-failure classes; confirm that every reference of the rows of brief section 10 is ingested |
| K10 | the stubs above; optional MCP wrapper |
| K11 | weekly `kb watch upstream` needs a scheduler (orch); snapshot ids in notes; `kb ingest arxiv --new` after manifest additions |

KB-G2 then needs all papers and repositories ingested and the QA report meeting the parse
success rate and retrieval hit rate written in CHARTER; CHARTER does not state them yet
(outbox `__to-orch__kb-g2-thresholds`).
