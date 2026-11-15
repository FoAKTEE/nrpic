# Checklist: C-sidm G0

Collected by `harness/bin/nrpic-stage collect C-sidm G0` on 2026-11-15T13:15:10Z from `coord/CHARTER.md` (last changed in b7b431d) and the brief (sections 13.3 and 13.4).
For each item set `status:` to PASS, FAIL or NA (OPEN until judged) and give the evidence: run ids,
figure files, KB locators, commits. `nrpic-stage report` reads this file; the automated checks are
in VERIFY_RESULTS.md (`nrpic-stage verify`), not here.

## Evidence required at every track's G0 (Scoping; charter 9.2)

- [x] **C1** Problem statement, parameter ranges, exit criteria, test plan
  - status: PASS
  - evidence: REPORT.md sections 1 (problem), 3 (parameter ranges), 4 (exit criteria), 5 (test plan against brief rows 843, 844, 852, 853)
- [x] **C2** The statements of the key references verified in the knowledge base
  - status: PASS
  - evidence: REPORT.md section 6: 27 statements re-read by the lead at file:line in kb-data/raw/arxiv sources; not yet through a kb index (OPEN.md item 5, outbox to kb)
- [x] **C3** Risk list
  - status: PASS
  - evidence: tracks/C-sidm/RISKS.md (13 risks), REPORT.md section 7
- [x] **C4** Compute estimate
  - status: PASS
  - evidence: REPORT.md section 8: unit costs from run C-sidm-20261115-115400-eb8b752 (reproduced in -131135-3077a99); wave 2 16-20 card-h, G2 ~45, G3 80-160; collision cost unmeasured

## Main products of G0 (charter 9.2)

- [ ] **C5** Working note v0
  - status: FAIL
  - evidence: working note v0 (REVTeX, tracks/C-sidm/note/) not written; OPEN.md item 1
- [ ] **C6** Architecture schematic
  - status: FAIL
  - evidence: architecture schematic not drawn; OPEN.md item 2
- [x] **C7** Stage timeline
  - status: PASS
  - evidence: stage timeline as a table, REPORT.md section 9 (the schematic is C10)

## Track-specific criteria of C-sidm for G0 (9.6 Track C: relativistic collapse of an SIDM core (S3))

- [x] **C8** (no track-specific criterion for G0 in the sheet: write the ones agreed with the orchestrator here, or mark NA)
  - status: NA
  - evidence: the sheet has no G0-specific criterion; the track's exit criteria per gate are in REPORT.md section 4

## Minimum figures at G0 (brief 13.4)

- [ ] **C9** Schematic: Track architecture (three states: exists, to be ported, new)
  - status: FAIL
  - evidence: not drawn; OPEN.md item 2
- [ ] **C10** Schematic: Stage timeline
  - status: FAIL
  - evidence: not drawn (table only, REPORT.md section 9); OPEN.md item 2
- [x] **C11** Data figure: None required
  - status: NA
  - evidence: none required
- [x] **C12** Data figure: Data from the literature may be redrawn
  - status: NA
  - evidence: optional; the packages redraw F21 and 2009.08163 values in gravothermal/figs and equilibria/figs

## Package (brief 13.3; judged by the session)

- [ ] **C13** Data figures drawn with /zoom-figure-style from registered run outputs, one script per figure, every PNG looked at
  - status: FAIL
  - evidence: all data figures come from registered runs in the figstyle of python/nrpic/figstyle.py, but several packages draw many figures per script (make_figures.py, figures.py) and the lead opened 29 of 35 PNGs (REVIEW.md lists the unopened ones)
- [ ] **C14** Schematics drawn with /sleep-paper-figure-style: track architecture (exists / to be ported / new) and the gate timeline
  - status: FAIL
  - evidence: no schematics yet
- [ ] **C15** Working note written with /paper-writing; its manuscript checker passed with --compile
  - status: FAIL
  - evidence: no working note yet
- [ ] **C16** Verifier subagent (fresh context) wrote VERIFIER_REPORT.md; every number of the Supplemental Material recomputed from the manifests
  - status: FAIL
  - evidence: no fresh-context verifier; the lead's review (REVIEW.md, runs -131130, -131135, -132327) is not independent of the conclusions
- [x] **C17** Null results and failed runs are on record (manifests and JOURNAL)
  - status: PASS
  - evidence: failed runs kept: C-sidm-20261115-120801-38ab057 (failed check), -121400-d463e1a (defect), superseded -121536, -121811; failed predictions in the helpers' journals and lead outcome L1 in JOURNAL.md
- [x] **C18** STATUS.md, JOURNAL.md and HANDOFF.md are current
  - status: PASS
  - evidence: rewritten in the lead session of 2026-11-15
