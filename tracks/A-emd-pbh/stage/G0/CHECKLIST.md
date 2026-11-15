# Checklist: A-emd-pbh G0

Collected by `harness/bin/nrpic-stage collect A-emd-pbh G0` on 2026-11-15T16:21:05Z from `coord/CHARTER.md` (last changed in b7b431d) and the brief (sections 13.3 and 13.4).
For each item set `status:` to PASS, FAIL or NA (OPEN until judged) and give the evidence: run ids,
figure files, KB locators, commits. `nrpic-stage report` reads this file; the automated checks are
in VERIFY_RESULTS.md (`nrpic-stage verify`), not here.

## Evidence required at every track's G0 (Scoping; charter 9.2)

- [x] **C1** Problem statement, parameter ranges, exit criteria, test plan
  - status: PASS
  - evidence: scope/SCOPE.md sections 1, 3, 5, 7 and the lead's section 10 (amplitude convention 10.1, set-up order 10.2); stage/G0/EVIDENCE.md
- [ ] **C2** The statements of the key references verified in the knowledge base
  - status: FAIL
  - evidence: verified at the raw store with file:line locators (scope/REFERENCES.md; seven locators re-read by the lead, SCOPE.md 10.5), not yet knowledge-base entries: outbox 20261115T1320Z__to-kb__ingest-s1-references.md
- [x] **C3** Risk list
  - status: PASS
  - evidence: RISKS.md (16 rows); SCOPE.md section 8
- [x] **C4** Compute estimate
  - status: PASS
  - evidence: SCOPE.md section 9 (T5, run A-emd-pbh-20261115-112625-e854f12, rerun A-20261115-130252-7877b7a identical) and 10.7 (unit cost from core run core-20261115-040406-1311b8e; scouting runs A-20261115-130948-5a2b58a)

## Main products of G0 (charter 9.2)

- [x] **C5** Working note v0
  - status: PASS
  - evidence: note/main.tex, note/main.pdf (REVTeX, 9 pages; problem, threshold definition, set-ups, tests with four data figures, plan, open items, parameter table, ledger); figures and tables from run A-20261115-161947-09324e1 (registered by hand, nrpic-run refused; same scripts as A-20261115-161054-50848b1 and A-20261115-161720-6ae975e); note/JOURNAL.md N1-N5
- [x] **C6** Architecture schematic
  - status: PASS
  - evidence: note/figures/schem_architecture.png (script note/scripts/schem_architecture.py), Fig. 3 of the note; run A-20261115-161947-09324e1; PNG looked at
- [x] **C7** Stage timeline
  - status: PASS
  - evidence: table in SCOPE.md 10.8; schematic note/figures/schem_timeline.png (Fig. 6 of the note), run A-20261115-161947-09324e1

## Track-specific criteria of A-emd-pbh for G0 (9.4 Track A: EMD primordial-black-hole formation (S1))

- [x] **C8** (no track-specific criterion for G0 in the sheet: write the ones agreed with the orchestrator here, or mark NA)
  - status: NA
  - evidence: no track-specific G0 criterion in the sheet

## Rulings of the orchestrator on the criteria (coord/DECISIONS; check that they apply to G0)

- [x] **C9** Track A. The threshold line is built in the periodic box (the expanding ball holds only amplitudes below the comparison amplitudes of arXiv:2609.14218; lead's evidence in `scope/SCOPE.md`); the expanding ball stays the spherical verification case and the set-up for isolated collapses. The G1 scan-design criterion is met on the reference-based design; the Newtonian-mode runs are G2 work. (0013)
  - status: PASS
  - evidence: applied: the note builds the threshold line in the periodic box and keeps the ball for verification (note Sec. III A, B). Qualification from the verifier (stage/G0/VERIFIER.md C1c) and the note's Fig. 1: a ball of two compaction radii reaches the particle bracket of arXiv:2609.14218 at R_b H_i = 0.9; both ball sizes stay far below the hoop line

## Minimum figures at G0 (brief 13.4)

- [x] **C10** Schematic: Track architecture (three states: exists, to be ported, new)
  - status: PASS
  - evidence: note/figures/schem_architecture.png: exists (green), to be ported (slate), new (red); PNG looked at
- [x] **C11** Schematic: Stage timeline
  - status: PASS
  - evidence: note/figures/schem_timeline.png: gates G0-G4 at the charter's target times, requirements, needs between gates; PNG looked at
- [x] **C12** Data figure: None required
  - status: NA
  - evidence: none required
- [x] **C13** Data figure: Data from the literature may be redrawn
  - status: PASS
  - evidence: scope figures fig_hoop (2609.14218 hoop line by eye against the reproduction), fig_timing; rerun A-20261115-130252-7877b7a, looked at

## Package (brief 13.3, decision 0012; judged by the session)

- [x] **C14** Package documents of decision 0012: STAGE_REPORT.md (nrpic-stage report), EVIDENCE.md, OPEN.md and this CHECKLIST.md in the stage directory; REVIEW.md where the lead rechecked helpers; the scoping text in SCOPE.md or SCOPING.md beside them or in the scope directory, named in the report (no REPORT.md needed)
  - status: PASS
  - evidence: STAGE_REPORT.md (nrpic-stage report), EVIDENCE.md, OPEN.md, CHECKLIST.md in stage/G0; scoping text scope/SCOPE.md (named in the report); no REVIEW.md: the lead's re-check of the helpers is JOURNAL.md entry 2026-11-15T12:57Z (L1-L8)
- [x] **C15** Data figures drawn with /zoom-figure-style from registered run outputs, one script per figure, every PNG looked at
  - status: PASS
  - evidence: figstyle (python/nrpic/figstyle.py), one script per figure set (scope_calc.py, lead_crosscheck.py, scouting_predictions.py, helper scripts); PNGs looked at: stage/G0/EVIDENCE.md 'Figures looked at'
- [x] **C16** Schematics drawn with /sleep-paper-figure-style: track architecture (exists / to be ported / new) and the gate timeline
  - status: PASS
  - evidence: note/scripts/schem_architecture.py and schem_timeline.py with the vendored paperfig.py (unchanged copy of harness/style/); PNGs looked at
- [x] **C17** Working note written with /paper-writing; its manuscript checker passed with --compile
  - status: PASS
  - evidence: check_manuscript.py --compile on note/main.tex: 0 undefined references, 0 undefined citations, 0 overfull boxes; candidates only in 5.5/5.8 for run ids in the ledger appendix and harness names in the ledger scripts, accepted by the note's guide (../WRITING_GUIDE.md, exception 1); captions within five lines on the rendered pages (looked at)
- [ ] **C18** Verifier subagent (fresh context) wrote VERIFIER_REPORT.md; every number of the Supplemental Material recomputed from the manifests
  - status: OPEN
  - evidence: a fresh verifier (wave 2) is writing stage/G0/VERIFIER.md (runs A-20261115-160935-41f721d, -161239-1c41333, -161253-e506d90): C1a/b, C2, C3, C4a, C5, C6, C7 confirmed, C1c and C4b wrong, C8 model not confirmed; the ledger of the note is recomputed from the run outputs by note/scripts/ledger.py (claims check: 68 numbers of the lead's documents, 66 agree, note/tables/claims.md); a verifier's recomputation of the note's ledger is not done
- [x] **C19** Null results and failed runs are on record (manifests and JOURNAL)
  - status: PASS
  - evidence: failed and superseded runs kept with manifests (stage/G0/EVIDENCE.md, status failed/stopped); failed predictions in the helpers' journals and JOURNAL.md
- [x] **C20** STATUS.md, JOURNAL.md and HANDOFF.md are current
  - status: PASS
  - evidence: rewritten in this session (commit of the lead session)
