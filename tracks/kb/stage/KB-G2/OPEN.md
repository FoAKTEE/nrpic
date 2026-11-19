# KB-G2: what is open (owner kb; lead, wave 2b, 2026-11-19)

The two thresholds of decision 0016 item 6 are met on snapshot kb-20261119-a782f1e
(`EVIDENCE.md`). The package is not complete for the orchestrator's review: it has no verifier
report (CHECKLIST C8, FAIL); requested from orch.

## Defects that bear on the thresholds

- Bibliographies lost for unusual reference-list formats (KB-G1 verifier defect 1, rechecked by
  the lead, run kb-20261119-155315-b2c7420): 20 of 707 TeX papers have no bibliography entry,
  11 of them with status ok. Causes: `\bibitem` in a REVTeX-3 `references` environment (0710.5073,
  1109.2484, 1302.5308, 1304.7791, gr-qc/0107076, gr-qc/9402041, hep-ph/0011159, astro-ph/0003278),
  AASTeX `\reference` (1201.4794), a macro for `\bibitem` (gr-qc/0304002, gr-qc/9703066),
  `\harvarditem` in the .bbl (2507.01095), plain-TeX `\ref` paragraphs (gr-qc/9906015,
  astro-ph/9510056), a bibliography file the main file does not reach (2602.00155), none found
  (2403.15126, astro-ph/0306304, astro-ph/9306009, astro-ph/9607124, gr-qc/9604001). Counting the
  11 as failures puts parse success at 94.8 % (95.2 % with the PDF papers). Fix: the parser reads
  these formats and a paper with `\cite` but no entry gets status review; then re-ingest, which
  needs a remap of claim chunk ids first (re-ingest renumbers chunks).
- Plain-TeX papers (gr-qc/9906015 priority 3, astro-ph/9510056, astro-ph/9306009, gr-qc/9604001):
  no `\eqno` numbers, no headings.
- astro-ph/0003278: sections present in flat.tex, none extracted (wave 2; unchanged).
- PDF text of the 1994-95 papers: characters of cmsy/cmex mapped as Greek letters (3 of 20 in the
  lead's sample, B1); affiliation words with OT1 accents turned Greek.

## Retrieval

- The re-ranking (w2-noexpand) was chosen in-sample; held-out set requested.
- Still missed at the answer location by rerank: q06, q07 (the conclusion chunk of 2611.12831 never
  enters the pool), q12, q13 (paper not in the top ten), q16 (abstract found; narrow location),
  q17, q20 (outranked through window BM25). Remedies of R4b (paper expansion by chunk count, less
  weight on window BM25) wait for the held-out set.
- 23 % of chunks exceed the embedding model's 512 pieces; smaller chunks or stored window vectors
  would make rerank cheaper (about 10 s per query now).
- Code chunks (about 160000) have no vectors; `kb search --kind code` is full-text only.

## Other open items of the knowledge base (not KB-G2 criteria)

- Licences: empty for all 710 papers (arXiv API carries none; request to orch, arxiv-licences).
- 26 additions: groups to be confirmed by orch; gr-qc/0608095 keep or drop.
- The brief's own labelled statements are not seeded as claims (brief 12.8, first item; KB-G3).
- K7 module descriptions of src/z4c, src/particles, src/pgen, src/mesh, src/bvals.
- Upstream watch not run in wave 2b (last kb-20261115-154646-234060c).
