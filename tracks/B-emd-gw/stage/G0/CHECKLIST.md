# Checklist: B-emd-gw G0

Collected by `harness/bin/nrpic-stage collect B-emd-gw G0` on 2026-11-15T16:51:33Z from `coord/CHARTER.md` (last changed in b7b431d) and the brief (sections 13.3 and 13.4).
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

- [x] **C5** Working note v0
  - status: PASS
  - evidence: tracks/B-emd-gw/note/main.pdf (10 pages; REVTeX 4.2), sources tracks/B-emd-gw/note/main.tex; figures and tables from registered run B-20261115-165556-a399d4e (supersedes B-20261115-165138-cb53c14 and -165231-9e29328); guide and notation tracks/B-emd-gw/WRITING_GUIDE.md, NOTATION.md; pages read (note JOURNAL.md, outcomes)
- [x] **C6** Architecture schematic
  - status: PASS
  - evidence: tracks/B-emd-gw/note/figures/schem_architecture.png (script tracks/B-emd-gw/note/scripts/schem_architecture.py, run B-20261115-165556-a399d4e); Fig. 2 of the note; looked at
- [x] **C7** Stage timeline
  - status: PASS
  - evidence: tracks/B-emd-gw/note/figures/schem_timeline.png (script tracks/B-emd-gw/note/scripts/schem_timeline.py, run B-20261115-165556-a399d4e); Fig. 6 of the note; REPORT.md section 8 is the table it draws; looked at

## Track-specific criteria of B-emd-gw for G0 (9.5 Track B: gravitational waves from EMD structure formation (S2))

- [x] **C8** (no track-specific criterion for G0 in the sheet: write the ones agreed with the orchestrator here, or mark NA)
  - status: NA
  - evidence: the sheet has no G0-specific criterion; the agreed criteria are the charter's gate items

## Rulings of the orchestrator on the criteria (coord/DECISIONS; check that they apply to G0)

- [x] **C9** Track B. The stand-in-matter item is struck (particles do it directly). The multi-code row is covered by the shearing-dust comparison of arXiv:2003.08014 and by full relativity against the Newtonian mode of the code; the N-body baseline runs in that mode. Item 3 of `coord/notes/derivations_to_check.md` is amended as Track B found. (0013)
  - status: NA
  - evidence: the ruling of decision 0013 changes the G1 item (stand-in matter struck) and the G2 multi-code row; it adds nothing to G0. The note (Sec. V) and REPORT.md section 3 already state the reworded criteria

## Minimum figures at G0 (brief 13.4)

- [x] **C10** Schematic: Track architecture (three states: exists, to be ported, new)
  - status: PASS
  - evidence: tracks/B-emd-gw/note/figures/schem_architecture.png: exists (green), to be ported (slate), new (red), in three columns (initial data, evolution, analysis); run B-20261115-165556-a399d4e
- [x] **C11** Schematic: Stage timeline
  - status: PASS
  - evidence: tracks/B-emd-gw/note/figures/schem_timeline.png: gates G0-G4 with targets and the needs between gates; run B-20261115-165556-a399d4e
- [x] **C12** Data figure: None required
  - status: NA
  - evidence: none required
- [x] **C13** Data figure: Data from the literature may be redrawn
  - status: NA
  - evidence: optional; not used

## Package (brief 13.3, decision 0012; judged by the session)

- [x] **C14** Package documents of decision 0012: STAGE_REPORT.md (nrpic-stage report), EVIDENCE.md, OPEN.md and this CHECKLIST.md in the stage directory; REVIEW.md where the lead rechecked helpers; the scoping text in SCOPE.md or SCOPING.md beside them or in the scope directory, named in the report (no REPORT.md needed)
  - status: PASS
  - evidence: STAGE_REPORT.md (nrpic-stage report, this wave), EVIDENCE.md, OPEN.md, CHECKLIST.md, REVIEW.md in stage/G0/; scoping text tracks/B-emd-gw/scope/SCOPE.md (named in STAGE_REPORT.md); the wave-1 REPORT.md stays (decision 0012)
- [x] **C15** Data figures drawn with /zoom-figure-style from registered run outputs, one script per figure, every PNG looked at
  - status: PASS
  - evidence: all data figures from registered runs with one script each, project figstyle; looked at by the helpers and by the lead (list in JOURNAL.md entry 2026-11-15T13:05Z and REVIEW.md)
- [x] **C16** Schematics drawn with /sleep-paper-figure-style: track architecture (exists / to be ported / new) and the gate timeline
  - status: PASS
  - evidence: both schematics with harness/style/paperfig.py (unchanged copy in tracks/B-emd-gw/note/scripts/, sha256 as harness/style/SHA256SUMS), sleep-paper style; run B-20261115-165556-a399d4e
- [x] **C17** Working note written with /paper-writing; its manuscript checker passed with --compile
  - status: PASS
  - evidence: written with /paper-writing (guide and notation one level above tracks/B-emd-gw/note); checker check_manuscript.py --compile: 0 undefined references or citations, 0 overfull boxes, every principle clean in the main text; remaining hits are run ids and file names in the ledger appendix and the scripts, accepted by exception 1 of WRITING_GUIDE.md; step 4 of the new-paper procedure (reviewer subagents) not run
- [ ] **C18** Verifier subagent (fresh context) wrote VERIFIER_REPORT.md; every number of the Supplemental Material recomputed from the manifests
  - status: OPEN
  - evidence: the lead's re-check REVIEW.md (runs -131016-03b1119, -131027-03b1119) is the owner's; a fresh verifier's VERIFIER_REPORT.md is owed (OPEN.md item 3)
- [x] **C19** Null results and failed runs are on record (manifests and JOURNAL)
  - status: PASS
  - evidence: failed predictions in the helper journals and JOURNAL.md; failed run B-emd-gw-20261115-120531-40a3597 and stopped run -130926-a1c2237 kept with manifests
- [x] **C20** STATUS.md, JOURNAL.md and HANDOFF.md are current
  - status: PASS
  - evidence: STATUS.md, JOURNAL.md, HANDOFF.md, RISKS.md rewritten 2026-11-15
