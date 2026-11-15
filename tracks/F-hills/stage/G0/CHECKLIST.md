# Checklist: F-hills G0

Collected by `harness/bin/nrpic-stage collect F-hills G0` on 2026-11-15T18:06:46Z from `coord/CHARTER.md` (last changed in b7b431dd) and the brief (sections 13.3 and 13.4).
For each item set `status:` to PASS, FAIL or NA (OPEN until judged) and give the evidence: run ids,
figure files, KB locators, commits. `nrpic-stage report` reads this file; the automated checks are
in VERIFY_RESULTS.md (`nrpic-stage verify`), not here.

## Evidence required at every track's G0 (Scoping; charter 9.2)

- [x] **C1** Problem statement, parameter ranges, exit criteria, test plan
  - status: PASS
  - evidence: SCOPING.md sections 1 (problem), 3 (parameter ranges), 5 (exit criteria G0-G3), 7 (test plan against brief rows 857-859); restated with figures in note/main.pdf Secs. II-IV (note package, wave 2)
- [x] **C2** The statements of the key references verified in the knowledge base
  - status: PASS
  - evidence: SCOPING.md section 8: 15 statements re-read by the lead at file:line in kb-data/raw/arxiv sources (0911.1136, 1804.02911, 2404.16270, 2402.02178, 2406.11985, 0710.0879, 1004.1353); the note package re-read prp.tex:735-738, 846-854, 345-357 and mnras.tex:368-379, 433-441 and article.tex:244-275 (note/JOURNAL.md, ledger appendix). Not through a kb index (outbox 20261115T1507Z__to-kb__*). Helper locators beyond these are not re-read (OPEN.md item 8)
- [x] **C3** Risk list
  - status: PASS
  - evidence: tracks/F-hills/RISKS.md (13 risks; R3 and the 40-card-hour figure of R1 are superseded by core-v0.3 and decision 0014), SCOPING.md section 11
- [x] **C4** Compute estimate
  - status: PASS
  - evidence: SCOPING.md section 9 from runs F-hills-20261115-131109-634fb86, -131348-634fb86, -131933-907e5fe, -045438-f62d553; recomputed in note figure fig_cost (runs F-20261115-180609-abc9f6e, F-20261115-173543-29e87e8). Correction: the q = 4 m/16 row uses puncture radius 1.2; the inputs use 1.8 (2514/2864/2568 MeshBlocks, 44.8 card-hours; note/tables/claims.md item 14)

## Main products of G0 (charter 9.2)

- [x] **C5** Working note v0
  - status: PASS
  - evidence: tracks/F-hills/note/main.tex and main.pdf (REVTeX 4.2, 11 pages, latexmk, every page read); guide and notation tracks/F-hills/WRITING_GUIDE.md, NOTATION.md; problem, set-up, tests with five data figures and the ledger from runs F-20261115-174648-25514db (N1) and F-20261115-180609-abc9f6e (N4); note/README.md
- [x] **C6** Architecture schematic
  - status: PASS
  - evidence: note/figures/schem_architecture.png (paperfig.py; exists / to be ported / new), Fig. 1 of the note; run F-20261115-180609-abc9f6e; PNG looked at
- [x] **C7** Stage timeline
  - status: PASS
  - evidence: note/figures/schem_timeline.png (paperfig.py), Fig. 7 of the note; run F-20261115-180609-abc9f6e; PNG looked at

## Track-specific criteria of F-hills for G0 (9.9 Track F: Hills mechanism (S12))

- [x] **C8** (no track-specific criterion for G0 in the sheet: write the ones agreed with the orchestrator here, or mark NA)
  - status: NA
  - evidence: the sheet (charter 9.9) has no G0-specific criterion; the track exit criteria per gate are in SCOPING.md section 5

## Rulings of the orchestrator on the criteria (coord/DECISIONS; check that they apply to G0)

- [x] **C9** Track F (amends 0005). Mass ratio four for the convergence study and the first scan line; the passage at mass ratio ten follows when the mesh fits. The first passage of a clump binary comes right after the first black-hole passage. (0013)
  - status: NA
  - evidence: the ruling concerns G1-G3 (mass ratio of the convergence study and scan lines, timing of object (b)); followed already: the P1 input of wave 2 is at q = 4 (nr_first/inputs/p1_q4.athinput), the note plan (Sec. V, Fig. 7) and Sec. II C use it

## Minimum figures at G0 (brief 13.4)

- [x] **C10** Schematic: Track architecture (three states: exists, to be ported, new)
  - status: PASS
  - evidence: note/figures/schem_architecture.png, three states (green exists, slate to be ported, red new); script note/scripts/schem_architecture.py; run F-20261115-180609-abc9f6e
- [x] **C11** Schematic: Stage timeline
  - status: PASS
  - evidence: note/figures/schem_timeline.png; script note/scripts/schem_timeline.py; run F-20261115-180609-abc9f6e
- [x] **C12** Data figure: None required
  - status: NA
  - evidence: none required at G0; five data figures exist anyway (C15)
- [x] **C13** Data figure: Data from the literature may be redrawn
  - status: NA
  - evidence: optional; the note marks only values printed in the papers' text (with locators) and keeps digitised third-party curves out of committed figures

## Package (brief 13.3, decision 0012; judged by the session)

- [ ] **C14** Package documents of decision 0012: STAGE_REPORT.md (nrpic-stage report), EVIDENCE.md, OPEN.md and this CHECKLIST.md in the stage directory; REVIEW.md where the lead rechecked helpers; the scoping text in SCOPE.md or SCOPING.md beside them or in the scope directory, named in the report (no REPORT.md needed)
  - status: OPEN
  - evidence: STAGE_REPORT.md (nrpic-stage report, wave 2), EVIDENCE.md, OPEN.md, CHECKLIST.md present; scoping text SCOPING.md beside them. No REVIEW.md: the lead rechecked the helpers (SCOPING.md section 10, JOURNAL.md V1-V7) but did not write that file; the lead adds it or points to section 10. EVIDENCE.md and OPEN.md are of wave 1 (OPEN items 1, 6 and the G0 products are now addressed; the lead updates them)
- [x] **C15** Data figures drawn with /zoom-figure-style from registered run outputs, one script per figure, every PNG looked at
  - status: PASS
  - evidence: five data figures of the note, one script each (note/scripts/fig_*.py, czstyle.py copy equal to harness/style/SHA256SUMS), inputs read from registered run outputs with their recorded sha256 (26 files; one wave-1 run without checksums, said so), every PNG opened (note/JOURNAL.md N1-N4). The wave-1 package figures (newton3, geodesic_binary, three_punctures, checks) stay as package records
- [x] **C16** Schematics drawn with /sleep-paper-figure-style: track architecture (exists / to be ported / new) and the gate timeline
  - status: PASS
  - evidence: note/figures/schem_architecture.png and schem_timeline.png with note/scripts/paperfig.py (copy equal to harness/style/SHA256SUMS)
- [x] **C17** Working note written with /paper-writing; its manuscript checker passed with --compile
  - status: PASS
  - evidence: paper-writing checker with --compile (note/README.md): 0 undefined references and citations, 0 overfull boxes; main text clean in all 16 checks; remaining hits are run ids in the ledger appendix and data keys in the scripts, accepted by exception 1 of WRITING_GUIDE.md. Not done: the reviewer step of a new paper (skill Sec. 10)
- [ ] **C18** Verifier subagent (fresh context) wrote VERIFIER_REPORT.md; every number of the Supplemental Material recomputed from the manifests
  - status: OPEN
  - evidence: no VERIFIER_REPORT.md. A wave-2 second-check helper (stage/G0/JOURNAL.md, stage/G0/second_check/) checks the novelty verdict and the V6/V7 disagreement with its own code; its outcome was not committed when this checklist was filled. The note ledger was checked against the files by note/scripts/ledger.py (13 of 17 lead numbers agree, 2 differ, 2 superseded: note/tables/claims.md), not by a fresh verifier
- [x] **C19** Null results and failed runs are on record (manifests and JOURNAL)
  - status: PASS
  - evidence: failed and stopped runs kept: wave 1 in EVIDENCE.md (F-hills-20261115-045124-ae6bca8, -125858-0232c4c, -131944-360a12e, -143824-2c937bc, -133009-2f7ad7f, -133013-2f7ad7f, -133034-bf31889); wave 2 F-20261115-173719-923135a (failed), F-20261115-173106-57c4b4c, -173112-a9e18a3, -173543-29e87e8 (stopped, nr_first/JOURNAL.md); failed predictions on record in JOURNAL.md (V4, V5, V6, V7, V5b), nr_first/JOURNAL.md (E4, E6) and note/JOURNAL.md (N2 item 3)
- [ ] **C20** STATUS.md, JOURNAL.md and HANDOFF.md are current
  - status: OPEN
  - evidence: STATUS.md, JOURNAL.md, HANDOFF.md describe the end of wave 1 (multi-puncture not released, allotment 40); the wave-2 results are not in them yet; the lead rewrites them at the end of wave 2 (helpers do not edit them)
