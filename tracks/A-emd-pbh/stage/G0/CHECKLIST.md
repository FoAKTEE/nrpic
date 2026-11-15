# Checklist: A-emd-pbh G0

Collected by `harness/bin/nrpic-stage collect A-emd-pbh G0` on 2026-11-15T18:34:05Z from `coord/CHARTER.md` (last changed in b7b431dd) and the brief (sections 13.3 and 13.4).
For each item set `status:` to PASS, FAIL or NA (OPEN until judged) and give the evidence: run ids,
figure files, KB locators, commits. `nrpic-stage report` reads this file; the automated checks are
in VERIFY_RESULTS.md (`nrpic-stage verify`), not here.

## Evidence required at every track's G0 (Scoping; charter 9.2)

- [x] **C1** Problem statement, parameter ranges, exit criteria, test plan
  - status: PASS
  - evidence: scope/SCOPE.md sections 1, 3, 5, 7 and the lead's section 10 (amplitude convention 10.1, set-up order 10.2); stage/G0/EVIDENCE.md
- [x] **C2** The statements of the key references verified in the knowledge base
  - status: PASS
  - evidence: knowledge-base snapshots kb-20261115-3826a68 (read by the lead, read-only) and kb-20261115-44b7406 (db/current; kb's answer tracks/kb/outbox/20261115T183737Z__to-A-emd-pbh__ingest-s1-references.md on kb/main, independent locator check run kb-20261115-154906-f19880f: all 166 locator groups resolve; 48 of 53 numeric statements have every number in the cited lines): all twelve S1 key references ingested (parse ok: 2609.14218 v1, 2610.23218 v1, 1609.01588 v2, 1707.03595 v4, 2211.13950 v3, 2507.18312 v3, 2508.10070 v1, 2109.04896 v3, 2306.11810 v2, 2605.04487 v2, 1611.07906 v2, 1901.04498 v2); 170 claims tagged A-emd-pbh with resolved file:line locators, 152 verified by the kb claims check, among them mu_c in (0.32, 0.33] (claim 21, MDPBH.tex:L766-768) and the constraint caveat (claim 30). Qualification: the particle bracket (claim 25, MDPBH.tex:L1101-1103) and 17 others are still 'to_verify' in the kb (seeded without a [VERIFIED] label); the lead read claim 25 at the source in this session (stage/REVIEW-wave2.md, criteria2) and asked kb to update its status (outbox)
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
  - evidence: applied: the threshold line is built in the periodic box, the ball stays the verification case (note Sec. III A, B; SCOPE.md 10.2). The ruling's stated reason is partly wrong (verifier C1c, confirmed by the lead's run A-20261115-182314-bebd0cf: a q = 2 ball holds the particle bracket (0.045, 0.05], not the hoop or fluid amplitudes); SCOPE.md 4, 8, 10.9(a) and RISKS row 4 corrected; correction proposed to orch (outbox). The ruling stands on the source's own data in the box

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
  - evidence: STAGE_REPORT.md (nrpic-stage report), EVIDENCE.md, OPEN.md, CHECKLIST.md in stage/G0; the lead's re-check of the helpers is ../REVIEW-wave2.md (wave 2) and JOURNAL.md entry 2026-11-15T12:57Z (wave 1); scoping text scope/SCOPE.md (named in the report)
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
  - status: FAIL
  - evidence: a fresh verifier wrote stage/G0/VERIFIER.md (taken as VERIFIER_REPORT.md under decision 0012; sections 1-3 committed in 0ac9951 before the track's summaries were read; runs A-20261115-160935-41f721d, -161239-1c41333, -161253-e506d90; reproduced exactly by the lead, A-20261115-182514-3bb6846): C1a/b, C2, C3, C4a, C5, C6, C7 confirmed, C1c and C4b wrong (corrected, ../REVIEW-wave2.md section 3), C8 now confirmed by the measured cost. Not met: the note's ledger appendix (every number with its run id) was recomputed from the manifests by note/scripts/ledger.py with checksum checks (run A-20261115-161947-09324e1), but not by a verifier; closing it needs a fresh verifier to rerun ledger.py and check the rows
- [x] **C19** Null results and failed runs are on record (manifests and JOURNAL)
  - status: PASS
  - evidence: failed and superseded runs kept with manifests (stage/G0/EVIDENCE.md, status failed/stopped); failed predictions in the helpers' journals and JOURNAL.md
- [x] **C20** STATUS.md, JOURNAL.md and HANDOFF.md are current
  - status: PASS
  - evidence: rewritten in the lead session of wave 2 (STATUS.md, JOURNAL.md entry, HANDOFF.md, RISKS.md)
