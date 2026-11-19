# Checklist: C-sidm G0

Collected by `harness/bin/nrpic-stage collect C-sidm G0` on 2026-11-19T15:11:16Z from `coord/CHARTER.md` (last changed in a6118683) and the brief (sections 13.3 and 13.4).
For each item set `status:` to PASS, FAIL or NA (OPEN until judged) and give the evidence: run ids,
figure files, KB locators, commits. `nrpic-stage report` reads this file; the automated checks are
in VERIFY_RESULTS.md (`nrpic-stage verify`), not here.

## Evidence required at every track's G0 (Scoping; charter 9.2)

- [x] **C1** Problem statement, parameter ranges, exit criteria, test plan
  - status: PASS
  - evidence: REPORT.md sections 1 (problem), 3 (parameter ranges), 4 (exit criteria), 5 (test plan against brief rows 843, 844, 852, 853)
- [x] **C2** The statements of the key references verified in the knowledge base
  - status: PASS
  - evidence: REPORT.md section 6: 27 statements re-read by the lead at file:line in kb-data/raw/arxiv sources; in the knowledge base as claims 229-303 (scope/REFERENCES.md) and 304-331 (REPORT section 6), errata 610-618, snapshot kb-20261115-44b7406, with kb's own located/partial check (run kb-20261115-154906-f19880f; kb message 20261115T183741Z index-locators-typos). kb's open point (file name of the astro-ph/0111176 locator) answered: SMBH_SIDM_Xiv2.tex:289-291 of v3 (outbox 2026-11-19 to kb)
- [x] **C3** Risk list
  - status: PASS
  - evidence: tracks/C-sidm/RISKS.md (13 risks), REPORT.md section 7
- [x] **C4** Compute estimate
  - status: PASS
  - evidence: REPORT.md section 8: unit costs from run C-sidm-20261115-115400-eb8b752 (reproduced in -131135-3077a99); wave 2 16-20 card-h, G2 ~45, G3 80-160. Collision cost measured in wave 2: 3.4-3.9e-9 s per tested pair on one A100, 3.3-6.7e-7 s on one core (runs C-20261115-180525-94ddd22, C-20261115-165500-c67e036); coll_energy = particle costs 1.68 times cell mode per tested pair on a processor (run C-20261119-143146-226b0e0); cluster runs at N = 1e5 on the M/4 mesh 3.42-3.46 s per M on a card (threshold_scan, 1.73 card-h for six 300 M runs); SCAN.md 26-28 card-h for the G2 scan

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
  - evidence: STAGE_REPORT.md (nrpic-stage report, wave 2), EVIDENCE.md (wave-2 section added), OPEN.md (rewritten for wave 2), CHECKLIST.md, REVIEW.md (wave 1) and ../REVIEW-wave2.md (lead's recheck of the wave-2 helpers, runs C-20261115-193332-48771b4, C-20261115-193751-d3872ff); scoping text tracks/C-sidm/scope/SCOPE.md (verifier findings V4b, V8 corrected in wave 2) with REPORT.md of wave 1 (accepted by decision 0012; numbers corrected in wave 2)
- [x] **C15** Data figures drawn with /zoom-figure-style from registered run outputs, one script per figure, every PNG looked at
  - status: PASS
  - evidence: the stage package figures are the note figures: four data figures, one script each (note/scripts/fig_*.py, czstyle.py), all inputs read from registered runs with their recorded sha256 (63 files), every PNG opened (note/JOURNAL.md N1, N2); nrpic-stage verify: fig-script, rerun, compare, regenerate PASS. The wave-1 package figures (several per script, figstyle) stay as package records
- [x] **C16** Schematics drawn with /sleep-paper-figure-style: track architecture (exists / to be ported / new) and the gate timeline
  - status: PASS
  - evidence: note/figures/schem_architecture.png and schem_timeline.png with note/scripts/paperfig.py (copy equal to harness/style/SHA256SUMS; verify style PASS)
- [x] **C17** Working note written with /paper-writing; its manuscript checker passed with --compile
  - status: PASS
  - evidence: paper-writing checker with --compile (note/README.md): 0 undefined references and citations; main text clean in all 16 checks; remaining hits are run ids and file names in the ledger appendix and data keys in the scripts, accepted by exception 1 of WRITING_GUIDE.md; one overfull box of 1 pt (parameter table). Not done: the reviewer step of a new paper (skill Sec. 10)
- [x] **C18** Verifier subagent (fresh context) wrote VERIFIER.md (decision 0016; VERIFIER_REPORT.md accepted too); every number of the Supplemental Material recomputed from the manifests
  - status: PASS
  - evidence: decision 0016 item 4: G0 is judged with a verifier's report on the plan. The wave-2 verifier (fresh context, own code) wrote stage/G0/VERIFIER.md: claims V1-V8 of the scoping text recomputed (runs C-20261115-170630-1037f6a, C-20261115-170716-e81ba08); its suite reruns byte-identically (lead's run C-20261115-193332-48771b4); its WRONG and NOT CONFIRMED items are fixed (../REVIEW-wave2.md section 5). The note v0 has no Supplemental Material; its ledger appendix (39 rows) is regenerated from the registered JSON by note/scripts/ledger.py, which nrpic-stage verify reruns and compares; the three rows that differed were recomputed by the lead (L11). A fresh verifier of the ledger was not run (stated in OPEN.md)
- [x] **C19** Null results and failed runs are on record (manifests and JOURNAL)
  - status: PASS
  - evidence: failed runs kept with their manifests: wave 1 C-sidm-20261115-120801-38ab057, -121400-d463e1a, superseded -121536, -121811; wave 2 C-20261115-165742-2c645f8 (driver), C-20261115-170221-b1a491c and C-20261115-171137-9e3c807 (exit 1: three TOV-residual checks), C-20261115-170231-4e68455 (KeyError); failed predictions in the helpers' journals (box_tests T4 seed 2, models G2/G4/G5/A1, threshold_scan P3.4, P3.7, P3.8, P3.10, P3.11, Test 4) and in JOURNAL.md
- [x] **C20** STATUS.md, JOURNAL.md and HANDOFF.md are current
  - status: PASS
  - evidence: the wave-2 lead was cut off before rewriting them (its checklist claimed PASS too early); STATUS.md, HANDOFF.md and RISKS.md rewritten and JOURNAL.md appended (entries of 2026-11-19, predictions and outcomes L12-L15) by the wave-2b lead session, in the same commit series as this checklist
