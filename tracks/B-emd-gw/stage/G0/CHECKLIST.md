# Checklist: B-emd-gw G0

Collected by `harness/bin/nrpic-stage collect B-emd-gw G0` on 2026-11-15T13:13:12Z from `coord/CHARTER.md` (last changed in b7b431d) and the brief (sections 13.3 and 13.4).
For each item set `status:` to PASS, FAIL or NA (OPEN until judged) and give the evidence: run ids,
figure files, KB locators, commits. `nrpic-stage report` reads this file; the automated checks are
in VERIFY_RESULTS.md (`nrpic-stage verify`), not here.

## Evidence required at every track's G0 (Scoping; charter 9.2)

- [x] **C1** Problem statement, parameter ranges, exit criteria, test plan
  - status: PASS
  - evidence: REPORT.md sections 1-4 (problem, ranges, exit criteria, test plan mapped to brief lines 845-851); scope/SCOPE.md; item 3 checked twice (runs B-emd-gw-20261115-113102-bc5e082, -131027-03b1119)
- [ ] **C2** The statements of the key references verified in the knowledge base
  - status: OPEN
  - evidence: statements verified at the source in kb-data/raw with file:line (REPORT.md section 5, scope/REFERENCES.md; lead re-read 5 locators); not yet in an indexed KB snapshot (outbox to kb); 2212.00425, 2312.12499 unread
- [x] **C3** Risk list
  - status: PASS
  - evidence: tracks/B-emd-gw/RISKS.md (R1-R11); REPORT.md section 6
- [x] **C4** Compute estimate
  - status: PASS
  - evidence: REPORT.md section 7: measured throughput from runs/cosmo logs (read by the lead), per-run table from run B-emd-gw-20261115-113632-2960145, plan 13-31 card-h of 40; used 0.48

## Main products of G0 (charter 9.2)

- [ ] **C5** Working note v0
  - status: OPEN
  - evidence: working note v0 not written (OPEN.md item 1); REPORT.md holds its content
- [ ] **C6** Architecture schematic
  - status: OPEN
  - evidence: architecture schematic not drawn (OPEN.md item 2)
- [ ] **C7** Stage timeline
  - status: OPEN
  - evidence: timeline as a table in REPORT.md section 8; schematic not drawn

## Track-specific criteria of B-emd-gw for G0 (9.5 Track B: gravitational waves from EMD structure formation (S2))

- [x] **C8** (no track-specific criterion for G0 in the sheet: write the ones agreed with the orchestrator here, or mark NA)
  - status: NA
  - evidence: the sheet has no G0-specific criterion; the agreed criteria are the charter's gate items

## Minimum figures at G0 (brief 13.4)

- [ ] **C9** Schematic: Track architecture (three states: exists, to be ported, new)
  - status: OPEN
  - evidence: not drawn (OPEN.md item 2)
- [ ] **C10** Schematic: Stage timeline
  - status: OPEN
  - evidence: not drawn (OPEN.md item 2)
- [x] **C11** Data figure: None required
  - status: NA
  - evidence: none required
- [x] **C12** Data figure: Data from the literature may be redrawn
  - status: NA
  - evidence: optional; not used

## Package (brief 13.3; judged by the session)

- [x] **C13** Data figures drawn with /zoom-figure-style from registered run outputs, one script per figure, every PNG looked at
  - status: PASS
  - evidence: all data figures from registered runs with one script each, project figstyle; looked at by the helpers and by the lead (list in JOURNAL.md entry 2026-11-15T13:05Z and REVIEW.md)
- [ ] **C14** Schematics drawn with /sleep-paper-figure-style: track architecture (exists / to be ported / new) and the gate timeline
  - status: OPEN
  - evidence: schematics not drawn
- [ ] **C15** Working note written with /paper-writing; its manuscript checker passed with --compile
  - status: OPEN
  - evidence: no working note yet
- [ ] **C16** Verifier subagent (fresh context) wrote VERIFIER_REPORT.md; every number of the Supplemental Material recomputed from the manifests
  - status: OPEN
  - evidence: the lead's re-check REVIEW.md (runs -131016-03b1119, -131027-03b1119) is the owner's; a fresh verifier's VERIFIER_REPORT.md is owed (OPEN.md item 3)
- [x] **C17** Null results and failed runs are on record (manifests and JOURNAL)
  - status: PASS
  - evidence: failed predictions in the helper journals and JOURNAL.md; failed run B-emd-gw-20261115-120531-40a3597 and stopped run -130926-a1c2237 kept with manifests
- [x] **C18** STATUS.md, JOURNAL.md and HANDOFF.md are current
  - status: PASS
  - evidence: STATUS.md, JOURNAL.md, HANDOFF.md, RISKS.md rewritten 2026-11-15
