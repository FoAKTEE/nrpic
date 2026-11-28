# Checklist: E-stoch-inf G3

Collected by `harness/bin/nrpic-stage collect E-stoch-inf G3` on 2026-11-28T00:20:33Z from `coord/CHARTER.md` (last changed in a61186835) and the brief (sections 13.3 and 13.4).
For each item set `status:` to PASS, FAIL or NA (OPEN until judged) and give the evidence: run ids,
figure files, KB locators, commits. `nrpic-stage report` reads this file; the automated checks are
in VERIFY_RESULTS.md (`nrpic-stage verify`), not here.

## Evidence required at every track's G3 (Science runs; charter 9.2)

- [ ] **C1** The pre-registered scan is complete
  - status: OPEN
  - evidence: not complete (batch 34): 71 of 128 mirrored pairs read (pairs 0-70; runs G3B00-G3B06, readings listed in g3/JOURNAL.md entry 17); pairs 71-127 re-queued after preemptions (q0079-q0083: G3B07b running as job 5537, others pending); level 2 (16 pairs) not run, re-queued (q0084, q0087, q0088)
- [ ] **C2** Robustness checks
  - status: OPEN
  - evidence: G3-C PASSES (E-20261126-115943-32970f2); G3-R PASSES (E-20261126-120438-9d48377); level 2 (4d.7, reported) not run (preempted three times, re-queued); gauge leg withdrawn, slicing limitation stated (A8); mirroring gain 40 on the skewness error (E-20261128-000627-00ed437)
- [ ] **C3** Comparison with the literature
  - status: OPEN
  - evidence: comparison with one-patch delta N of the same band stated with errors on 71 pairs (E-20261128-000627-00ed437; g3 entry 17): tail shape (T) agrees on every item (skewness -0.15, kurtosis -0.03, F_pm(3) -1.5/+1.35, F_pm(4) +1.1/+1.8, A(3) -2.1, A(4) -2.1 combined s.e.); variance (V) differs, +0.28 +- 0.07 per cent (4.1 s.e.); reference: pooled direct E-20261125-152832-c301e92 + E-20261125-163825-ca2ebaa, sampler E-20261125-160658-855db8c; A4 not yet computed; sigma = 0.1 bound open (R39)
- [x] **C4** Null results and failed runs are on record
  - status: PASS
  - evidence: on record: batch 19-27 items as before; batch 34: preemption of G3B06 (17 of 22 members) and G3L00 (none), six re-queued jobs preempted within seconds and G3L01/G3L02 after 68 s (g3 entries 14, 16, 18; runs closed as stopped); (V) of entry 4 FAILED as written (entry 17); P5-3 would fail again on every box (round-off, entry 17)

## Main products of G3 (charter 9.2)

- [ ] **C5** Result figures and tables
  - status: OPEN
  - evidence: fig_g3_onepoint, fig_g3_tails, fig_g3_pairs (E-20261128-000627-00ed437); fig_g3_mosaic (E-20261128-001644-500a097); interim on 71 pairs
- [ ] **C6** The numerical ledger in the Supplemental Material
  - status: OPEN
  - evidence: ledger section 'Tail statistics' of the working note (17 rows, repro/note/manuscript/tables/ledger.tex, run E-20261128-001644-500a097); no independent check yet

## Track-specific criteria of E-stoch-inf for G3 (9.8 Track E: stochastic inflation (S11, if possible))

- [ ] **C7** Tail statistics, compared with E-pre-3
  - status: OPEN
  - evidence: SCOPE 4d + 4d.9 judged on 71 pairs (g3 entry 17): (T) agrees, (V) failed as written; the statement on 128 pairs and level 2 wait for their runs

## Rulings of the orchestrator on the criteria (coord/DECISIONS; check that they apply to G3)

- [x] **C8** Track E. Decision of the feasibility gate, pending the group: continue to G1 and G2 (about two card-hours); the scope of G3 is decided at G2. The lead's choices of `spec/scope/SCOPE.md` section 4 are accepted. (0013)
  - status: NA
  - evidence: decision 0013 concerned G0-G2; the scope of G3 was decided by decisions 0038 item 2 and 0040 item 1 and is written in SCOPE 4d with 4d.9

## Minimum figures at G3 (brief 13.4)

- [ ] **C9** Schematic: Sketch of the parameter space
  - status: OPEN
  - evidence: schematic of the verification ladder at G3 (schem_ladder_g3.py; Fig. 16 of the note); parameter-space sketch not drawn (one scenario, one band)
- [ ] **C10** Data figure: Main results
  - status: OPEN
  - evidence: Figs. 18-19 of the note (one-point density with tail, tail fractions against threshold), interim
- [ ] **C11** Data figure: Robustness
  - status: OPEN
  - evidence: Fig. 20 (mirrored pairs, even-part coefficient); G3-C and G3-R figures of batch 27 (fig_g3c.png, fig_g3r.png); level 2 missing
- [ ] **C12** Data figure: Comparison with the literature
  - status: OPEN
  - evidence: Figs. 18-19 compare with one-patch delta N of the same band (the literature comparison of S11)

## Package (brief 13.3, decision 0012; judged by the session)

- [ ] **C13** Package documents of decision 0012: STAGE_REPORT.md (nrpic-stage report), EVIDENCE.md, OPEN.md and this CHECKLIST.md in the stage directory; REVIEW.md where the lead rechecked helpers; the scoping text in SCOPE.md or SCOPING.md beside them or in the scope directory, named in the report (no REPORT.md needed)
  - status: OPEN
  - evidence: STAGE_REPORT.md (nrpic-stage report), OPEN.md, CHECKLIST.md, review in stage/REVIEW-wave3.md part L; scope in spec/scope/SCOPE.md 4d; EVIDENCE.md not yet written
- [x] **C14** Data figures drawn with /zoom-figure-style from registered run outputs, one script per figure, every PNG looked at
  - status: PASS
  - evidence: every G3 data figure from a registered script (g3/pairs_g3.py, note scripts fig_g3_mosaic.py) in the figstyle library, each PNG looked at (REVIEW-wave3 L.2)
- [ ] **C15** Schematics drawn with /sleep-paper-figure-style: track architecture (exists / to be ported / new) and the gate timeline
  - status: OPEN
  - evidence: ladder schematic at G3 drawn (paperfig); architecture and timeline schematics of the note not updated for G3
- [ ] **C16** Working note written with /paper-writing; its manuscript checker passed with --compile
  - status: OPEN
  - evidence: G3 section V of repro/note/manuscript/main.tex written with the paper-writing guide; checker run with --compile: 0 undefined references, 0 overfull boxes, only earlier hits in scripts; pages 12-15 read; interim text on 71 pairs
- [ ] **C17** Verifier subagent (fresh context) wrote VERIFIER.md (decision 0016; VERIFIER_REPORT.md accepted too); every number of the Supplemental Material recomputed from the manifests
  - status: OPEN
  - evidence: fresh verifier not yet sent (after the remaining pairs and level 2)
- [x] **C18** Null results and failed runs are on record (manifests and JOURNAL)
  - status: PASS
  - evidence: manifests of every run above (status stopped where preempted) and journal entries g3 5-18, zeta 8-9
- [x] **C19** STATUS.md, JOURNAL.md and HANDOFF.md are current
  - status: PASS
  - evidence: STATUS.md, JOURNAL.md, HANDOFF.md current at the end of batch 34
