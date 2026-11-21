# Checklist: F-hills G0

Collected by `harness/bin/nrpic-stage collect F-hills G0` on 2026-11-21T06:42:08Z from `coord/CHARTER.md` (last changed in a6118683) and the brief (sections 13.3 and 13.4).
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
  - evidence: tracks/F-hills/RISKS.md (rewritten 2026-11-19: allotments of decisions 0014/0016, core-v0.3 released, wave-2b risks of the passage), SCOPING.md section 11
- [x] **C4** Compute estimate
  - status: PASS
  - evidence: SCOPING.md section 9 from runs F-hills-20261115-131109-634fb86, -131348-634fb86, -131933-907e5fe, -045438-f62d553; recomputed in note figure fig_cost (runs F-20261115-180609-abc9f6e, F-20261115-173543-29e87e8); verifier K14 recount within 0.4 percent (run F-20261121-035817-0aca1c5). Corrections: q = 4 m/16 row (radius 1.8; lead V11, 2026-11-19); slot limit against card capacity and the G2 sum 131-135 (verifier D3, D5; amended 2026-11-21, lead run F-20261121-063504-00f0743); P1's measured cost row (about 13 card-hours to 280 M)

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
  - status: PASS
  - evidence: the ruling concerns G1-G3 and is followed: P1 (the first passage) is at q = 4 (nr_first/inputs/p1_q4.athinput, run F-20261119-150017-b45ec5f); SCOPING.md sections 3, 6 and 9 named q = 10 until the verifier's D4 and were amended on 2026-11-21 (../REVIEW-wave3.md); the note follows 0013

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

- [x] **C14** Package documents of decision 0012: STAGE_REPORT.md (nrpic-stage report), EVIDENCE.md, OPEN.md and this CHECKLIST.md in the stage directory; REVIEW.md where the lead rechecked helpers; the scoping text in SCOPE.md or SCOPING.md beside them or in the scope directory, named in the report (no REPORT.md needed)
  - status: PASS
  - evidence: STAGE_REPORT.md (nrpic-stage report, rerun 2026-11-21), EVIDENCE.md and OPEN.md (updated by the lead in batch 2a), CHECKLIST.md (collect 2026-11-21), REVIEW.md (points to SCOPING.md section 10 for wave 1, ../REVIEW-wave2.md for waves 2 and 2b, ../REVIEW-wave3.md for wave 3); scoping text SCOPING.md beside them, named in the report; VERIFIER.md
- [x] **C15** Data figures drawn with /zoom-figure-style from registered run outputs, one script per figure, every PNG looked at
  - status: PASS
  - evidence: five data figures of the note, one script each (note/scripts/fig_*.py, czstyle.py copy equal to harness/style/SHA256SUMS), inputs read from registered run outputs with their recorded sha256 (26 files; one wave-1 run without checksums, said so), every PNG opened (note/JOURNAL.md N1-N4). The wave-1 package figures (newton3, geodesic_binary, three_punctures, checks) stay as package records
- [x] **C16** Schematics drawn with /sleep-paper-figure-style: track architecture (exists / to be ported / new) and the gate timeline
  - status: PASS
  - evidence: note/figures/schem_architecture.png and schem_timeline.png with note/scripts/paperfig.py (copy equal to harness/style/SHA256SUMS)
- [x] **C17** Working note written with /paper-writing; its manuscript checker passed with --compile
  - status: PASS
  - evidence: paper-writing checker with --compile (note/README.md): 0 undefined references and citations, 0 overfull boxes; main text clean in all 16 checks; remaining hits are run ids in the ledger appendix and data keys in the scripts, accepted by exception 1 of WRITING_GUIDE.md. Not done: the reviewer step of a new paper (skill Sec. 10)
- [x] **C18** Verifier subagent (fresh context) wrote VERIFIER.md (decision 0016; VERIFIER_REPORT.md accepted too); every number of the Supplemental Material recomputed from the manifests
  - status: PASS
  - evidence: VERIFIER.md (fresh verifier, package verify_g0, batch 1 of 2026-11-20; artefacts only; sections 1-3 committed fecdec04 before reading the earlier checks): 20 claims of the plan with verdicts (14 CONFIRMED, K4 NOT DONE, K6/K13 PARTLY, K12/K14/K15/K16 WRONG as worded) and ledger tables 1-2 of the note recomputed row by row, 57 of 57 (run F-20261121-035817-0aca1c5). The lead reran that recomputation from its registered outputs (run F-20261121-063712-25981e0: 56 rows identical, row 57 a stale locator after core-v0.4 rewrote multi_puncture.md) and checked every WRONG item at the source (run F-20261121-063504-00f0743); each is corrected in SCOPING.md (marked [amended: D1-D8]), in note/main.tex (D7, D10) or listed for the note's ledger rerun (D9, row 57): ../REVIEW-wave3.md. Table 3 of the ledger (G1 material) is for the G1 verifier (decision 0016 item 4)
- [x] **C19** Null results and failed runs are on record (manifests and JOURNAL)
  - status: PASS
  - evidence: failed and stopped runs kept: wave 1 in EVIDENCE.md (F-hills-20261115-045124-ae6bca8, -125858-0232c4c, -131944-360a12e, -143824-2c937bc, -133009-2f7ad7f, -133013-2f7ad7f, -133034-bf31889); wave 2 F-20261115-173719-923135a (failed), F-20261115-173106-57c4b4c, -173112-a9e18a3, -173543-29e87e8 (stopped, nr_first/JOURNAL.md); failed predictions on record in JOURNAL.md (V4, V5, V6, V7, V5b), nr_first/JOURNAL.md (E4, E6) and note/JOURNAL.md (N2 item 3)
- [x] **C20** STATUS.md, JOURNAL.md and HANDOFF.md are current
  - status: PASS
  - evidence: STATUS.md, HANDOFF.md rewritten and a JOURNAL.md entry appended by the lead at the end of batch 2a (2026-11-21)
