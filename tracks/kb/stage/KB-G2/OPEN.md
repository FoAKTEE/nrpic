# KB-G2: what is open (owner kb; lead, wave 3 batch 3, 2026-11-21)

Every item of CHECKLIST.md is PASS on snapshot kb-20261119-a782f1e, with the independent
verifier's report (VERIFIER.md) and the lead's check of it (../REVIEW-wave3.md). Two
reservations for the gate review:

1. **Parse success has a thin margin.** 96.3 % on the recorded status; 95.6 % (679/710, 4.5
   papers above the bar) under the verifier's definition; 94.4 % if nine letters with run-in
   headings count as failures; 92.7 % if an extracted abstract chunk is required.
2. **C6 on the stricter reading (verifier: WRONG, partly met).** The package and every answer
   to a track name the snapshot; the tool does not put the id on each locator: `kb show` and
   `kb cites` print none, a JSON search hit carries none (the answer names the database once).

## Defects and who removes them

| Defect (verifier's numbering) | Action | Who |
|---|---|---|
| 1. 21 papers with status ok fail the definition: 13 bibliographies lost or under half (REVTeX-3 `references`, `\def\bi{\bibitem}`, `\sortbibitem`, AAS `\reference`, `\harvarditem`, unreached .bbl), 7 with under half of the display equations, 1 without its numbered headings; 10 papers with citation rows but no entry | parser for the bibliography formats; "bibliography missing or under half" and "citation rows without entries" as parse-failure causes in the QA report; re-ingest after the claim chunk remap | package `ingest3` (cut 2026-11-20; dev copy in scratch/kb/ingest3/dev) |
| 2. Old styles: five plain-TeX or old-macro review papers without sections and references (astro-ph/0306304, astro-ph/9306009, astro-ph/9510056, gr-qc/9604001, gr-qc/9906015; also astro-ph/9607124) | recognise `{\bf I. ...}`, A&A `\titlea`/`\titleb`, `\rma` headings and numbered reference lists without `\cite` | `ingest3` (added to its scope) |
| 3. C6b snapshot id not on each locator | print the snapshot id in `kb show`, `kb cites`, and add it to every JSON hit; test | the package that next edits `kbtool/papers_cli.py` and `embed_search.py` (ingest3 changes papers_cli.py in its dev copy, so after it lands) |
| 4. 25 papers without an abstract chunk (21 of 23 review papers) | abstract from `{\bf Abstract}` and `\section*{Abstract}`; the metadata abstract is served meanwhile | `ingest3` |
| 5. Retrieval misses: golden q12, held-out H20 in all modes | reported, not gating; held-out set never used for tuning | retrieval work after KB-G2 |
| 6. 24 of 64 repositories without code chunks (kokkos, amrex, rebound, ...) | chunk the code of these repositories (brief 12.7) | package `code_kb` (cut) or a later one |
| QA report states no parse rate against the 95 % bar | add the rate and its definition to `kb qa run` | next QA run after ingest3 |
| C9: two wave-1 manifests said "finished" with exit 1 | corrected to "failed" with a status_note (2026-11-21) | done |

## Other open items of the knowledge base (not KB-G2 criteria)

- Licences: empty for all 710 papers (arXiv API carries none; request to orch, arxiv-licences).
- 26 additions: groups to be confirmed by orch; gr-qc/0608095 keep or drop.
- KB-G3: the brief's own labelled statements are not seeded as claims (package `claims_brief`,
  cut); the tracks' queue is partly processed (package `claims_tracks`, batches A1 and B1 of
  seven done).
- K7 module descriptions of src/z4c, src/particles, src/pgen, src/mesh, src/bvals (package
  `code_kb`, cut; upstream watch of 2026-11-20 done, message to core sent).
- 24 sources fetched in wave 3a (brief check) not yet ingested (`ingest3`).

## Closed after the signature (lead batch 9, 2026-11-21)
- C6b: snapshot id in `kb show`, `kb cites` and every JSON hit (commit e4ad423a).
- C2 remark: `kb qa run` states the parse rate against the bar: 719/744 = 96.6 %, strict 96.6 %
  (run kb-20261121-234721-b3aecfe, snapshot kb-20261121-bbaafe5). The thin strict margin of the
  signature (94.4-94.8 %) is gone with ingest3's parser.
