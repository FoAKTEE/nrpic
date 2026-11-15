# Checklist: A-emd-pbh G0

Collected by `harness/bin/nrpic-stage collect A-emd-pbh G0` on 2026-11-15T13:12:42Z from `coord/CHARTER.md` (last changed in b7b431d) and the brief (sections 13.3 and 13.4).
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

- [ ] **C5** Working note v0
  - status: OPEN
  - evidence: not started: stage/G0/OPEN.md item 2
- [ ] **C6** Architecture schematic
  - status: OPEN
  - evidence: not drawn: stage/G0/OPEN.md item 3
- [x] **C7** Stage timeline
  - status: PASS
  - evidence: table in SCOPE.md 10.8 (schematic still to draw, C10)

## Track-specific criteria of A-emd-pbh for G0 (9.4 Track A: EMD primordial-black-hole formation (S1))

- [ ] **C8** (no track-specific criterion for G0 in the sheet: write the ones agreed with the orchestrator here, or mark NA)
  - status: NA
  - evidence: no track-specific G0 criterion in the sheet

## Minimum figures at G0 (brief 13.4)

- [ ] **C9** Schematic: Track architecture (three states: exists, to be ported, new)
  - status: OPEN
  - evidence: stage/G0/OPEN.md item 3
- [ ] **C10** Schematic: Stage timeline
  - status: OPEN
  - evidence: stage/G0/OPEN.md item 3
- [ ] **C11** Data figure: None required
  - status: NA
  - evidence: none required
- [x] **C12** Data figure: Data from the literature may be redrawn
  - status: PASS
  - evidence: scope figures fig_hoop (2609.14218 hoop line by eye against the reproduction), fig_timing; rerun A-20261115-130252-7877b7a, looked at

## Package (brief 13.3; judged by the session)

- [x] **C13** Data figures drawn with /zoom-figure-style from registered run outputs, one script per figure, every PNG looked at
  - status: PASS
  - evidence: figstyle (python/nrpic/figstyle.py), one script per figure set (scope_calc.py, lead_crosscheck.py, scouting_predictions.py, helper scripts); PNGs looked at: stage/G0/EVIDENCE.md 'Figures looked at'
- [ ] **C14** Schematics drawn with /sleep-paper-figure-style: track architecture (exists / to be ported / new) and the gate timeline
  - status: OPEN
  - evidence: stage/G0/OPEN.md item 3
- [ ] **C15** Working note written with /paper-writing; its manuscript checker passed with --compile
  - status: OPEN
  - evidence: stage/G0/OPEN.md item 2
- [ ] **C16** Verifier subagent (fresh context) wrote VERIFIER_REPORT.md; every number of the Supplemental Material recomputed from the manifests
  - status: OPEN
  - evidence: lead's re-check of the helpers (JOURNAL.md L1-L8) is a second agent for their numbers; no fresh verifier yet: stage/G0/OPEN.md item 4
- [x] **C17** Null results and failed runs are on record (manifests and JOURNAL)
  - status: PASS
  - evidence: failed and superseded runs kept with manifests (stage/G0/EVIDENCE.md, status failed/stopped); failed predictions in the helpers' journals and JOURNAL.md
- [x] **C18** STATUS.md, JOURNAL.md and HANDOFF.md are current
  - status: PASS
  - evidence: rewritten in this session (commit of the lead session)
