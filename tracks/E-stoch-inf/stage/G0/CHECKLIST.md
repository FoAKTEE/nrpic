# Checklist: E-stoch-inf G0

Collected by `harness/bin/nrpic-stage collect E-stoch-inf G0` on 2026-11-15T14:00:42Z from `coord/CHARTER.md` (last changed in b7b431d) and the brief (sections 13.3 and 13.4).
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
  - evidence: SCOPE.md section 8 (codebase/figs/cost.json, run E-stoch-inf-20261115-123936-b2ec5c7, rerun identical in E-20261115-140116-87c1cc5; GPU throughput docs/TESTLOG.md:46; processor throughput runs E-stoch-inf-20261115-122727-a1c2237 and E-20261115-135218-bdf4710); card overhead assumed, not measured (OPEN.md item 7)

## Main products of G0 (charter 9.2)

- [ ] **C5** Working note v0
  - status: OPEN
  - evidence: not started: OPEN.md item 2
- [ ] **C6** Architecture schematic
  - status: OPEN
  - evidence: not drawn: OPEN.md item 3
- [x] **C7** Stage timeline
  - status: PASS
  - evidence: table in SCOPE.md section 10 (schematic still to draw, C10)

## Track-specific criteria of E-stoch-inf for G0 (9.8 Track E: stochastic inflation (S11, if possible))

- [ ] **C8** Reproduction specification, code-base assessment and compute estimate are complete, and the group decides to continue, to shrink or to downgrade
  - status: OPEN
  - evidence: specification (spec/SPEC.md), code-base assessment (codebase/DESIGN_REVIEW.md; decision 0010) and compute estimate (SCOPE.md 8) complete and checked by the lead (EVIDENCE.md 2); the group's decision is pending: outbox 20261115T1410Z__to-orch__g0-decision-requested.md; recommendation SCOPE.md 9 (continue)

## Minimum figures at G0 (brief 13.4)

- [ ] **C9** Schematic: Track architecture (three states: exists, to be ported, new)
  - status: OPEN
  - evidence: not drawn: OPEN.md item 3
- [ ] **C10** Schematic: Stage timeline
  - status: OPEN
  - evidence: not drawn; timeline table SCOPE.md 10
- [x] **C11** Data figure: None required
  - status: NA
  - evidence: none required at G0
- [x] **C12** Data figure: Data from the literature may be redrawn
  - status: PASS
  - evidence: P1 Fig. 1 values redrawn against the reference: spec/fig/fig_background.png (run E-stoch-inf-20261115-123236-2e87364)

## Package (brief 13.3; judged by the session)

- [x] **C13** Data figures drawn with /zoom-figure-style from registered run outputs, one script per figure, every PNG looked at
  - status: PASS
  - evidence: figures of the packages (spec/fig, codebase/figs, langevin/fig, noise/fig) and the lead's (bg/fig_lead_bg.png, bg/fig_lead_ms.png, dn/fig_lead_dn.png of E-20261115-135532-3f958a1; fig_lu_diag.png of E-20261115-140553-0b75e1e; val_*/fig_val_*.png of E-20261115-140502-2957846) drawn with python/nrpic/figstyle.py from registered runs, one script each, every PNG looked at by the lead; scripts live in the packages, not under note/scripts (OPEN.md item 5)
- [ ] **C14** Schematics drawn with /sleep-paper-figure-style: track architecture (exists / to be ported / new) and the gate timeline
  - status: OPEN
  - evidence: OPEN.md item 3
- [ ] **C15** Working note written with /paper-writing; its manuscript checker passed with --compile
  - status: OPEN
  - evidence: OPEN.md item 2
- [ ] **C16** Verifier subagent (fresh context) wrote VERIFIER_REPORT.md; every number of the Supplemental Material recomputed from the manifests
  - status: OPEN
  - evidence: OPEN.md item 4; the lead's independent checks are in EVIDENCE.md section 2
- [x] **C17** Null results and failed runs are on record (manifests and JOURNAL)
  - status: PASS
  - evidence: EVIDENCE.md section 4; failed runs E-stoch-inf-20261115-125316-dafadc4, -131526-629fed8, E-20261115-135532-5ec2b09 (library-log leaf), E-20261115-140116-87c1cc5 (timing leaves), E-20261115-140502-2957846 (diagnostic syntax error) kept with manifests; refuted predictions in the package journals and the owner JOURNAL
- [x] **C18** STATUS.md, JOURNAL.md and HANDOFF.md are current
  - status: PASS
  - evidence: rewritten at the end of the lead session of 2026-11-15
