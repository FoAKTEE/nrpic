# Checklist: E-stoch-inf G0

Collected by `harness/bin/nrpic-stage collect E-stoch-inf G0` on 2026-11-15T17:35:18Z from `coord/CHARTER.md` (last changed in b7b431d) and the brief (sections 13.3 and 13.4).
For each item set `status:` to PASS, FAIL or NA (OPEN until judged) and give the evidence: run ids,
figure files, KB locators, commits. `nrpic-stage report` reads this file; the automated checks are
in VERIFY_RESULTS.md (`nrpic-stage verify`), not here.

## Evidence required at every track's G0 (Scoping; charter 9.2)

- [x] **C1** Problem statement, parameter ranges, exit criteria, test plan
  - status: PASS
  - evidence: spec/scope/SCOPE.md (owner's version 1): problem statement section 1, parameter ranges 2, exit criteria and the owner's decisions 4, test plan by row of brief 10 section 5; stage/G0/EVIDENCE.md
- [ ] **C2** The statements of the key references verified in the knowledge base
  - status: FAIL
  - evidence: verified at the raw store (kb-data/raw/arxiv, all eight references ingested by kb, inventory status ok) with file:line locators, SCOPE.md section 3; key P1, P2, BZ lines re-read by the lead; errata not yet knowledge-base claims: outbox 20261115T1410Z__to-kb__errata-s11-references.md
- [x] **C3** Risk list
  - status: PASS
  - evidence: RISKS.md (R1-R14); SCOPE.md section 7
- [x] **C4** Compute estimate
  - status: PASS
  - evidence: SCOPE.md section 8 (codebase/figs/cost.json, run E-stoch-inf-20261115-123936-b2ec5c7, rerun identical in E-20261115-140116-87c1cc5; GPU throughput docs/TESTLOG.md:46; processor throughput runs E-stoch-inf-20261115-122727-a1c2237 and E-20261115-135218-bdf4710). Card overhead now measured by core (run core-20261115-143907-cea4c86: 65 percent instead of the assumed 15); recomputed with it, one 256^3 realisation costs 0.57-0.71 (SR) and 0.71-0.88 (USR) card-hours, an extrapolation from 128^3 (note Sec. V, Fig. 6, note/scripts/costmodel.py, run E-20261115-173402-641b6e2); the conclusion of SCOPE.md 9 holds

## Main products of G0 (charter 9.2)

- [x] **C5** Working note v0
  - status: PASS
  - evidence: note/main.tex, note/main.pdf (REVTeX, 9 pages: problem and acceptance criteria, set-up and corrected initial slice, freezing and delta-N references, noise validation, cost and decision, open items; appendices parameters, errata, ledger); figures and tables from run E-20261115-173402-641b6e2; predictions and outcomes note/JOURNAL.md N1-N3; claims check note/tables/claims.md (59 numbers of the lead's documents, 54 agree, 5 differ, listed in note/README.md)
- [x] **C6** Architecture schematic
  - status: PASS
  - evidence: note/figures/schem_architecture.png (Fig. 2 of the note; script note/scripts/schem_architecture.py, run E-20261115-173402-641b6e2; PNG looked at)
- [x] **C7** Stage timeline
  - status: PASS
  - evidence: table in SCOPE.md section 10; schematic note/figures/schem_timeline.png (Fig. 7 of the note; run E-20261115-173402-641b6e2)

## Track-specific criteria of E-stoch-inf for G0 (9.8 Track E: stochastic inflation (S11, if possible))

- [ ] **C8** Reproduction specification, code-base assessment and compute estimate are complete, and the group decides to continue, to shrink or to downgrade
  - status: OPEN
  - evidence: specification (spec/SPEC.md), code-base assessment (codebase/DESIGN_REVIEW.md; decision 0010) and compute estimate (SCOPE.md 8) complete and checked by the lead (EVIDENCE.md 2); the group's decision is pending: outbox 20261115T1410Z__to-orch__g0-decision-requested.md; recommendation SCOPE.md 9 (continue)

## Rulings of the orchestrator on the criteria (coord/DECISIONS; check that they apply to G0)

- [x] **C9** Track E. Decision of the feasibility gate, pending the group: continue to G1 and G2 (about two card-hours); the scope of G3 is decided at G2. The lead's choices of `spec/scope/SCOPE.md` section 4 are accepted. (0013)
  - status: PASS
  - evidence: applied: the note's recommendation and timeline follow the ruling (continue to G1 and G2, scope of G3 decided at G2; note Sec. V, Fig. 7); the acceptance criteria of SCOPE.md section 4 are those of the note (Sec. II C). The group's decision itself is item C8

## Minimum figures at G0 (brief 13.4)

- [x] **C10** Schematic: Track architecture (three states: exists, to be ported, new)
  - status: PASS
  - evidence: note/figures/schem_architecture.png: exists (green), to be ported (slate), new (red), deliverables (plum); PNG looked at
- [x] **C11** Schematic: Stage timeline
  - status: PASS
  - evidence: note/figures/schem_timeline.png: gates G0-G4 at the indicative times of SCOPE.md 10, requirements, needs between gates; PNG looked at
- [x] **C12** Data figure: None required
  - status: NA
  - evidence: none required at G0
- [x] **C13** Data figure: Data from the literature may be redrawn
  - status: PASS
  - evidence: P1 Fig. 1 values redrawn against the reference: spec/fig/fig_background.png (run E-stoch-inf-20261115-123236-2e87364)

## Package (brief 13.3, decision 0012; judged by the session)

- [x] **C14** Package documents of decision 0012: STAGE_REPORT.md (nrpic-stage report), EVIDENCE.md, OPEN.md and this CHECKLIST.md in the stage directory; REVIEW.md where the lead rechecked helpers; the scoping text in SCOPE.md or SCOPING.md beside them or in the scope directory, named in the report (no REPORT.md needed)
  - status: PASS
  - evidence: STAGE_REPORT.md (nrpic-stage report), EVIDENCE.md, OPEN.md, CHECKLIST.md in stage/G0; scoping text spec/scope/SCOPE.md (named in the report); no separate REVIEW.md: the lead's re-check of the helpers is EVIDENCE.md section 2 (for the lead to confirm)
- [x] **C15** Data figures drawn with /zoom-figure-style from registered run outputs, one script per figure, every PNG looked at
  - status: PASS
  - evidence: package figures (spec/fig, codebase/figs, langevin/fig, noise/fig) and the lead's (E-20261115-135532-3f958a1, E-20261115-140553-0b75e1e, E-20261115-140502-2957846) with python/nrpic/figstyle.py; the note's five data figures note/figures/fig_{background,freezing,deltan,noise,cost}.png with note/scripts/czstyle.py (unchanged copy), one script each, from checksum-verified outputs of registered runs (run E-20261115-173402-641b6e2), every PNG looked at
- [x] **C16** Schematics drawn with /sleep-paper-figure-style: track architecture (exists / to be ported / new) and the gate timeline
  - status: PASS
  - evidence: note/scripts/schem_architecture.py and schem_timeline.py with note/scripts/paperfig.py (unchanged copy of harness/style/paperfig.py); both PNGs looked at
- [x] **C17** Working note written with /paper-writing; its manuscript checker passed with --compile
  - status: PASS
  - evidence: paper-writing guide and notation ../WRITING_GUIDE.md, ../NOTATION.md; check_manuscript.py --compile on note/main.tex: 0 undefined references, 0 undefined citations, 0 overfull boxes; remaining candidates are the run ids of the ledger appendix and the document names in the scripts, accepted by exception 1 of the guide; captions within five lines on the rendered pages (looked at). Reviewer subagents of the skill's step 4 not run
- [ ] **C18** Verifier subagent (fresh context) wrote VERIFIER_REPORT.md; every number of the Supplemental Material recomputed from the manifests
  - status: OPEN
  - evidence: no VERIFIER_REPORT.md (OPEN.md item 4); the lead's independent checks are in EVIDENCE.md section 2; the note's ledger and the lead's numbers are recomputed from the run outputs by note/scripts/ledger.py (run E-20261115-173402-641b6e2), which is not a fresh-context verifier
- [x] **C19** Null results and failed runs are on record (manifests and JOURNAL)
  - status: PASS
  - evidence: EVIDENCE.md section 4; failed runs E-stoch-inf-20261115-125316-dafadc4, -131526-629fed8, E-20261115-135532-5ec2b09 (library-log leaf), E-20261115-140116-87c1cc5 (timing leaves), E-20261115-140502-2957846 (diagnostic syntax error) kept with manifests; refuted predictions in the package journals and the owner JOURNAL
- [ ] **C20** STATUS.md, JOURNAL.md and HANDOFF.md are current
  - status: OPEN
  - evidence: STATUS.md and HANDOFF.md describe the state before the merge of release core-v0.3 (scalar field on the unmerged branch, no card build; HANDOFF names wt/core-scalar executables); to be rewritten for wave 2 by the lead (note/README.md, Requests)
