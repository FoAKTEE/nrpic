# Checklist: C-sidm G0

Collected by `harness/bin/nrpic-stage collect C-sidm G0` on 2026-11-15T17:13:07Z from `coord/CHARTER.md` (last changed in b7b431d) and the brief (sections 13.3 and 13.4).
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

- [x] **C5** Working note v0
  - status: PASS
  - evidence: working note v0: tracks/C-sidm/note/main.tex and main.pdf (REVTeX 4.2, 10 pages, compiled with latexmk, every page read), guide and notation tracks/C-sidm/WRITING_GUIDE.md, NOTATION.md; problem, set-up, tests with four data figures and the ledger from runs C-20261115-170415-385069e and C-20261115-171741-0e0da67 (note helper, wave 2); note/README.md
- [x] **C6** Architecture schematic
  - status: PASS
  - evidence: note/figures/schem_architecture.png (paperfig.py; exists / to be ported / new), Fig. 2 of the note; run C-20261115-171741-0e0da67; PNG looked at
- [x] **C7** Stage timeline
  - status: PASS
  - evidence: note/figures/schem_timeline.png (paperfig.py), Fig. 6 of the note; also the table of REPORT.md section 9; run C-20261115-171741-0e0da67; PNG looked at

## Track-specific criteria of C-sidm for G0 (9.6 Track C: relativistic collapse of an SIDM core (S3))

- [x] **C8** (no track-specific criterion for G0 in the sheet: write the ones agreed with the orchestrator here, or mark NA)
  - status: NA
  - evidence: the sheet has no G0-specific criterion; the track's exit criteria per gate are in REPORT.md section 4

## Rulings of the orchestrator on the criteria (coord/DECISIONS; check that they apply to G0)

- [x] **C9** Track C. The references and the wording that the lead corrected are taken into `coord/BRIEF_ERRATA.md`; the G2 criterion reads "the collisionless threshold is located with three-way convergence and compared with the turning-point criterion". (0013)
  - status: NA
  - evidence: the ruling concerns the G2 wording and the brief errata, not G0: coord/BRIEF_ERRATA.md rows 1.6, 1.8-1.11 carry the corrections of the lead; the note (Sec. II D) and the timeline schematic use the G2 wording of decision 0013

## Minimum figures at G0 (brief 13.4)

- [x] **C10** Schematic: Track architecture (three states: exists, to be ported, new)
  - status: PASS
  - evidence: note/figures/schem_architecture.png, three states (green exists, slate to be ported, red new); script note/scripts/schem_architecture.py; run C-20261115-171741-0e0da67
- [x] **C11** Schematic: Stage timeline
  - status: PASS
  - evidence: note/figures/schem_timeline.png; script note/scripts/schem_timeline.py; run C-20261115-171741-0e0da67
- [x] **C12** Data figure: None required
  - status: NA
  - evidence: none required
- [x] **C13** Data figure: Data from the literature may be redrawn
  - status: NA
  - evidence: optional; the packages redraw F21 and 2009.08163 values in gravothermal/figs and equilibria/figs

## Package (brief 13.3, decision 0012; judged by the session)

- [x] **C14** Package documents of decision 0012: STAGE_REPORT.md (nrpic-stage report), EVIDENCE.md, OPEN.md and this CHECKLIST.md in the stage directory; REVIEW.md where the lead rechecked helpers; the scoping text in SCOPE.md or SCOPING.md beside them or in the scope directory, named in the report (no REPORT.md needed)
  - status: PASS
  - evidence: STAGE_REPORT.md (nrpic-stage report, this wave), EVIDENCE.md, OPEN.md, CHECKLIST.md, REVIEW.md present; scoping text tracks/C-sidm/scope/SCOPE.md with REPORT.md of wave 1 (accepted by decision 0012); EVIDENCE.md and OPEN.md are of wave 1 (OPEN items 1, 2, 4 are now closed by the note package; the lead updates them)
- [x] **C15** Data figures drawn with /zoom-figure-style from registered run outputs, one script per figure, every PNG looked at
  - status: PASS
  - evidence: the stage package figures are the note figures: four data figures, one script each (note/scripts/fig_*.py, czstyle.py), all inputs read from registered runs with their recorded sha256 (63 files), every PNG opened (note/JOURNAL.md N1, N2); nrpic-stage verify: fig-script, rerun, compare, regenerate PASS. The wave-1 package figures (several per script, figstyle) stay as package records
- [x] **C16** Schematics drawn with /sleep-paper-figure-style: track architecture (exists / to be ported / new) and the gate timeline
  - status: PASS
  - evidence: note/figures/schem_architecture.png and schem_timeline.png with note/scripts/paperfig.py (copy equal to harness/style/SHA256SUMS; verify style PASS)
- [x] **C17** Working note written with /paper-writing; its manuscript checker passed with --compile
  - status: PASS
  - evidence: paper-writing checker with --compile (note/README.md): 0 undefined references and citations; main text clean in all 16 checks; remaining hits are run ids and file names in the ledger appendix and data keys in the scripts, accepted by exception 1 of WRITING_GUIDE.md; one overfull box of 1 pt (parameter table). Not done: the reviewer step of a new paper (skill Sec. 10)
- [ ] **C18** Verifier subagent (fresh context) wrote VERIFIER_REPORT.md; every number of the Supplemental Material recomputed from the manifests
  - status: OPEN
  - evidence: the wave-2 verifier (fresh context) wrote stage/G0/VERIFIER.md, not VERIFIER_REPORT.md: claims V1-V8 of the scoping text recomputed with its own code (runs C-20261115-170630-1037f6a, C-20261115-170716-e81ba08); V4b (fluid window of SCOPE.md section 1) and V5 (three Knudsen conventions) found wrong or open. The numbers of the note ledger were checked against the files by note/scripts/ledger.py (20 of 23 lead numbers agree; three differ, note/tables/claims.md) but not by a fresh verifier. The lead decides whether VERIFIER.md stands for VERIFIER_REPORT.md
- [x] **C19** Null results and failed runs are on record (manifests and JOURNAL)
  - status: PASS
  - evidence: failed runs kept: C-sidm-20261115-120801-38ab057 (failed check), -121400-d463e1a (defect), superseded -121536, -121811; failed predictions in the helpers' journals and lead outcome L1 in JOURNAL.md
- [ ] **C20** STATUS.md, JOURNAL.md and HANDOFF.md are current
  - status: OPEN
  - evidence: STATUS.md, JOURNAL.md, HANDOFF.md describe the end of wave 1 (lead session); the wave-2 results (note, verifier, box tests, threshold scan) are not in them yet; the lead rewrites them at the end of wave 2 (helpers do not edit them)
