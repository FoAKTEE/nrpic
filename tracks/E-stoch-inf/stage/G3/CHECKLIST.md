# Checklist: E-stoch-inf G3

Collected by `harness/bin/nrpic-stage collect E-stoch-inf G3` on 2026-11-26T02:39:19Z from `coord/CHARTER.md` (last changed in a61186835) and the brief (sections 13.3 and 13.4).
For each item set `status:` to PASS, FAIL or NA (OPEN until judged) and give the evidence: run ids,
figure files, KB locators, commits. `nrpic-stage report` reads this file; the automated checks are
in VERIFY_RESULTS.md (`nrpic-stage verify`), not here.

## Evidence required at every track's G3 (Science runs; charter 9.2)

- [ ] **C1** The pre-registered scan is complete
  - status: OPEN
  - evidence: not complete: pilot q0050 ran (E-20261126-002413-65295f3: ten baseline members ok, k000/k001/l000/l001 stopped at start-up on deck lines the deck lacks); G3C q0051 submitted (job 5348, E-20261126-030044-6933f21); G3R q0052, baseline G3B00-G3B06 (q0053, q0054, q0061-q0065: pairs 0-73) and level 2 G3L00 (q0066, pairs 0-4 + kdriver record) waiting; pairs 74-127 and level-2 pairs 5-15 not yet queued; zeta of the 128^3 dumps not readable at present cost (R41, g3/JOURNAL.md entry 8)
- [ ] **C2** Robustness checks
  - status: OPEN
  - evidence: planned: G3-C (4d.4 with A6), G3-R (4d.5 with A7), level 2 (4d.7 with A11); gauge leg withdrawn as a criterion, stated as a limitation (A8, decision 0040 item 1)
- [ ] **C3** Comparison with the literature
  - status: OPEN
  - evidence: reference: corrected one-patch delta N of the 128 band (A1; pilot E-20261125-151340-743c38c passes the variance gate 0.9993 +- 0.0032); 4e6 direct E-20261125-152832-c301e92 (gate 0.99865 +- 0.00058, skewness 0.0199 +- 0.0012); importance-sampled nu = 4 E-20261125-160658-855db8c (g3/amend entry 10); sigma = 0.1 lattice E-20261125-160722-a6d1f26 (gate failed, bound of A10 not reached; entry 9); model and landmarks of the reference = the deck (TO VERIFY of 4d.3 settled, E-20261125-161456-8d3f43c)
- [ ] **C4** Null results and failed runs are on record
  - status: OPEN
  - evidence: on record: batch 19-21 items as before (amend entries 4-9, zeta entries 6-7); batch 23: pilot members k/l failed at start-up (entry 5, R42); three reading runs stopped (E-20261126-022447-40a80b4, -022448-9510ee9, -024953-ed2d15f: map too slow, entries 7-8); G3P-3 sd clause failed by 0.3 per cent (entry 9); Z1 as run stays failed as written (zeta entry 9, decision 0042 item 1); Z2(iii) failed as written

## Main products of G3 (charter 9.2)

- [ ] **C5** Result figures and tables
  - status: OPEN
  - evidence: 
- [ ] **C6** The numerical ledger in the Supplemental Material
  - status: OPEN
  - evidence: 

## Track-specific criteria of E-stoch-inf for G3 (9.8 Track E: stochastic inflation (S11, if possible))

- [ ] **C7** Tail statistics, compared with E-pre-3
  - status: OPEN
  - evidence: the criterion of the track sheet; its statistic, estimator and criteria are SCOPE 4d + 4d.9 (A2 judges variance and tail shape apart)

## Rulings of the orchestrator on the criteria (coord/DECISIONS; check that they apply to G3)

- [x] **C8** Track E. Decision of the feasibility gate, pending the group: continue to G1 and G2 (about two card-hours); the scope of G3 is decided at G2. The lead's choices of `spec/scope/SCOPE.md` section 4 are accepted. (0013)
  - status: NA
  - evidence: decision 0013 concerned G0-G2; the scope of G3 was decided by decisions 0038 item 2 and 0040 item 1 and is written in SCOPE 4d with 4d.9

## Minimum figures at G3 (brief 13.4)

- [ ] **C9** Schematic: Sketch of the parameter space
  - status: OPEN
  - evidence: 
- [ ] **C10** Data figure: Main results
  - status: OPEN
  - evidence: 
- [ ] **C11** Data figure: Robustness
  - status: OPEN
  - evidence: 
- [ ] **C12** Data figure: Comparison with the literature
  - status: OPEN
  - evidence: 

## Package (brief 13.3, decision 0012; judged by the session)

- [ ] **C13** Package documents of decision 0012: STAGE_REPORT.md (nrpic-stage report), EVIDENCE.md, OPEN.md and this CHECKLIST.md in the stage directory; REVIEW.md where the lead rechecked helpers; the scoping text in SCOPE.md or SCOPING.md beside them or in the scope directory, named in the report (no REPORT.md needed)
  - status: OPEN
  - evidence: 
- [ ] **C14** Data figures drawn with /zoom-figure-style from registered run outputs, one script per figure, every PNG looked at
  - status: OPEN
  - evidence: 
- [ ] **C15** Schematics drawn with /sleep-paper-figure-style: track architecture (exists / to be ported / new) and the gate timeline
  - status: OPEN
  - evidence: 
- [ ] **C16** Working note written with /paper-writing; its manuscript checker passed with --compile
  - status: OPEN
  - evidence: 
- [ ] **C17** Verifier subagent (fresh context) wrote VERIFIER.md (decision 0016; VERIFIER_REPORT.md accepted too); every number of the Supplemental Material recomputed from the manifests
  - status: OPEN
  - evidence: 
- [ ] **C18** Null results and failed runs are on record (manifests and JOURNAL)
  - status: OPEN
  - evidence: manifests of every run above (status failed or stopped where so) and the journal entries g3 5-9, zeta 8-9
- [ ] **C19** STATUS.md, JOURNAL.md and HANDOFF.md are current
  - status: OPEN
  - evidence: current at the end of batch 23 (STATUS.md, JOURNAL.md, HANDOFF.md)
