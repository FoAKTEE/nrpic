# Checklist: E-stoch-inf G2

Collected by `harness/bin/nrpic-stage collect E-stoch-inf G2` on 2026-11-25T04:00:19Z from `coord/CHARTER.md` (last changed in a61186835) and the brief (sections 13.3 and 13.4).
For each item set `status:` to PASS, FAIL or NA (OPEN until judged) and give the evidence: run ids,
figure files, KB locators, commits. `nrpic-stage report` reads this file; the automated checks are
in VERIFY_RESULTS.md (`nrpic-stage verify`), not here.

## Evidence required at every track's G2 (Verified capability; charter 9.2)

- [x] **C1** The code paths used by the track pass their tests of §10
  - status: PASS
  - evidence: Release card build core-v0.6: SR P256v6 (E-20261121-202935-31520bc) records identical to the tested-branch G1 run, A2 1.2078e-4 (analysis E-20261123-015014-b4ecd4e); USR seed A identical per mode to the scouting pair, U-A0..U-A3 and U-A2' pass on all eight release USR runs (E-20261123-014858-8e72d4c, -021730-a421438, -020751-0baf597; judge E-20261123-024359-5dc3213). g2prod/JOURNAL.md entry 2.
- [x] **C2** Three-way convergence in particle number, mesh spacing, and gauge or boundary
  - status: PASS
  - evidence: Ruling 0030 item 2: a gauge variant is not required of Track E at G2 (the reproduced paper runs geodesic slicing only); C2 stands on mesh convergence in the periodic box, another gauge is a G3 item. Mesh: U-R 256 vs 320 PASS (factor 2.10 on the odd-part maximum, shell power 1.2e-4; fig_g2_resolution.png of E-20261123-024359-5dc3213); SR spectral convergence 32-256 (repro/figs Fig. 7, pass E-20261124-213029-e937f69; floor at the lowest shells, test FL128h/FL256h queued q0037/q0038, floor/JOURNAL.md entry 1). Particle number: NA (no particles before the hand-over).
- [x] **C3** Constraints behave
  - status: FAIL
  - evidence: U-A4'(a) as written FAILS at one dump of M (3.9245 at cN 6.52, bar 3.95-4.05; H within at all 9 judged dumps), on record without rewording (rulings 0030 item 2, 0036 item 2); confirmed by the fresh verifier (stage/G2/VERIFIER.md table, run E-20261125-022309-d346f12). U-A4'(b) reported; (c) PASS on the proper runs (H' <= 3.03e-12, M <= 0.0252); (d) control ratio 1.19e5 / 2.38e5 PASS (E-20261123-024359-5dc3213). Quarter pair (g2prod/JOURNAL.md entry 4, judge E-20261125-033450-4c4a31c on analysis E-20261124-233223-51b52c0): Q-a REFUTED (4.1275), Q-b and Q-c hold; no s^4 cause. The three-amplitude reading (verifier run E-20261125-023427-6fb6400: every judged factor within 4 +- 0.005) stands beside the failure as a finding after the data (entry 4.2; note Sec. IV C).
- [x] **C4** A first minimal full-GR kinetic run
  - status: NA
  - evidence: Decision 0026 item 3: does not apply to Track E before the hand-over from field to particles.

## Main products of G2 (charter 9.2)

- [x] **C5** Verification report (decision 0012: STAGE_REPORT.md with EVIDENCE.md and OPEN.md; no REPORT.md)
  - status: PASS
  - evidence: STAGE_REPORT.md (nrpic-stage report), EVIDENCE.md, OPEN.md, this CHECKLIST; verification of the SCOPE 4c numbers by a fresh verifier: stage/G2/VERIFIER.md (every recomputed number CONFIRMED, the one failure confirmed, nothing WRONG); its two open points answered in g2prod/JOURNAL.md entry 4 (quarter pair) and stage/REVIEW-wave3.md Part F. Verification of the reproduction: repro/verify/VERIFIER.md.
- [x] **C6** Reproducibility package
  - status: PASS
  - evidence: Every run registered with manifests and checksums; decks, queue, scripts committed (g2prod/, repro/*); restart byte-exact (R0); g2prod/README.md: run ids, the analyses with their manifests and the rerun command (batch 15); note: run_all.py registered (R16 E-20261125-035757-340bd1e), repro/note/README.md 'How to rerun and rebuild'.
## Track-specific criteria of E-stoch-inf for G2 (9.8 Track E: stochastic inflation (S11, if possible))

- [x] **C7** The USR case is reproduced
  - status: FAIL
  - evidence: SCOPE 4c as written: U-A0, U-A1, U-A2', U-A3 (seeds A and B), U-R, U-W, U-A4'(b)-(d), U-S PASS; U-A4'(a) FAILS at one dump of M, so 'the USR case is reproduced' is NOT met as written (rulings 0030 item 2 and 0036 item 2: stays FAILED, the three-amplitude reading beside it, labelled as after the data). Confirmed criterion by criterion by stage/G2/VERIFIER.md section 2. Quarter pair g2prod/JOURNAL.md entry 4. Note: repro/note/manuscript/main.pdf Sec. IV.
- [x] **C8** Sensitivity to window-function parameters and resolution
  - status: PASS
  - evidence: Window: U-W met by the scan (E-20261121-154733-0d1fbda, rerun E-20261121-203008-f104a3e). Resolution: U-R PASS (E-20261123-020751-0baf597 with E-20261123-014858-8e72d4c, judge E-20261123-024359-5dc3213).

## Rulings of the orchestrator on the criteria (coord/DECISIONS; check that they apply to G2)

- [x] **C9** Track E. Decision of the feasibility gate, pending the group: continue to G1 and G2 (about two card-hours); the scope of G3 is decided at G2. The lead's choices of `spec/scope/SCOPE.md` section 4 are accepted. (0013)
  - status: PASS
  - evidence: G0 decision: continue (coord/GATES.md 2026-11-20); G1 signed 2026-11-21; G2 within the scope of SCOPE section 4 and 4c.

## Minimum figures at G2 (brief 13.4)

- [x] **C10** Schematic: Verification ladder
  - status: PASS
  - evidence: Verification-ladder schematic fig_ladder (repro/note/manuscript/figures/fig_ladder.pdf, script scripts/schem_ladder.py, registered run_all R16 E-20261125-035757-340bd1e; looked at), note Fig. 12.
- [x] **C11** Data figure: Convergence figures (one each for particle number, mesh, gauge)
  - status: PASS
  - evidence: Mesh: note Fig. 14 fig_g2_resolution (USR 256^3 vs 320^3, script fig_g2_resolution.py from judge E-20261123-024359-5dc3213, R16) and Fig. 7 fig_specconv (SR spectral convergence 32-256); particle number NA (no particles before the hand-over); gauge NA by ruling 0030 item 2.
- [x] **C12** Data figure: Constraint norms against time
  - status: PASS
  - evidence: Note figure fig_constraints (repro/note/manuscript: constraint records against e-folds, both scenarios, rungs 32-256, from registered runs; ledger with verifier verdicts) and fig_g2_records.png (every release USR run, E-20261123-024359-5dc3213).
- [x] **C13** Data figure: At least one multi-scale slice mosaic with zoom boxes
  - status: PASS
  - evidence: Note Fig. 13 fig_g2_mosaic: R^NR at N_f of the release run E-20261121-211214-0377aab on the slice through its maximum, box / quarter / sixteen cells with zoom boxes (script fig_g2_mosaic.py, R16; looked at).
## Package (brief 13.3, decision 0012; judged by the session)

- [x] **C14** Package documents of decision 0012: STAGE_REPORT.md (nrpic-stage report), EVIDENCE.md, OPEN.md and this CHECKLIST.md in the stage directory; REVIEW.md where the lead rechecked helpers; the scoping text in SCOPE.md or SCOPING.md beside them or in the scope directory, named in the report (no REPORT.md needed)
  - status: PASS
  - evidence: CHECKLIST, EVIDENCE, OPEN, STAGE_REPORT (nrpic-stage report of batch 15) and VERIFIER.md in stage/G2/; scoping text spec/scope/SCOPE.md section 4c; REVIEW: stage/REVIEW-wave3.md Part F (the lead's recheck of the verifier and the quarter pair, batch 15).
- [x] **C15** Data figures drawn with /zoom-figure-style from registered run outputs, one script per figure, every PNG looked at
  - status: PASS
  - evidence: Each note figure has one script in repro/note/manuscript/scripts/ run by the registered run_all (R16 E-20261125-035757-340bd1e) from registered run outputs (json checked against sha256sums); every PNG looked at (repro/note/JOURNAL.md entries 19-26); figstyle.py (Cyclic Zoom).
- [x] **C16** Schematics drawn with /sleep-paper-figure-style: track architecture (exists / to be ported / new) and the gate timeline
  - status: PASS
  - evidence: G2 state of the architecture schematic (fig_architecture: first release / later releases / track analysis / ahead) and of the gate timeline (fig_timeline: G0, G1 passed, G2 ready for review), paperfig.py, scripts schem_architecture.py and schem_timeline.py, R16; note Appendix F, Figs. 20-21; looked at.
- [x] **C17** Working note written with /paper-writing; its manuscript checker passed with --compile
  - status: PASS
  - evidence: repro/note/manuscript/main.pdf (32 pages): Sec. IV 'The ultra-slow-roll lattice against criteria fixed in advance' (criteria, runs at three amplitudes, resolution pair, window, the failure on record and the three-amplitude reading, independent check), abstract, introduction item (iv), discussion, summary rule 5, ledger Table XVI, Appendix F; written with /paper-writing (guide and notation one level above); check_manuscript.py --compile: no undefined references, no overfull boxes, accepted hits only (repro/note/JOURNAL.md entry 24); pages read. The G1 note (note/) points to it.
- [x] **C18** Verifier subagent (fresh context) wrote VERIFIER.md (decision 0016; VERIFIER_REPORT.md accepted too); every number of the Supplemental Material recomputed from the manifests
  - status: PASS
  - evidence: stage/G2/VERIFIER.md: fresh verifier of the SCOPE 4c numbers (own reader, own R^NR extraction, own background and MS reference, own Philox; tools tested on planted data; runs E-20261125-022126-26671c3 ... -023609-01d8feb, verifier/JOURNAL.md with predictions): every recomputed number CONFIRMED, the U-A4'(a) failure confirmed, Q-a refuted, no claim WRONG. The note's ledger Table XVI cites its lines for each G2 row (ledger.py stops if a string moves).
- [x] **C19** Null results and failed runs are on record (manifests and JOURNAL)
  - status: PASS
  - evidence: Failed predictions and failed runs on record: g2prod entry 2 (T memory band, U320 band, U-A2' at s = 1/2, U-A4'(a) halving of M; failed analysis E-20261123-015650-493cff5; invalid pass E-20261123-014905-2bf3570).
- [x] **C20** STATUS.md, JOURNAL.md and HANDOFF.md are current
  - status: PASS
  - evidence: STATUS.md, JOURNAL.md, HANDOFF.md rewritten by the lead of batch 15 (2026-11-24).