# Checklist: C-sidm G2

Collected by `harness/bin/nrpic-stage collect C-sidm G2` on 2026-11-25T12:21:54Z from `coord/CHARTER.md` (last changed in a61186835) and the brief (sections 13.3 and 13.4).
For each item set `status:` to PASS, FAIL or NA (OPEN until judged) and give the evidence: run ids,
figure files, KB locators, commits. `nrpic-stage report` reads this file; the automated checks are
in VERIFY_RESULTS.md (`nrpic-stage verify`), not here.

## Evidence required at every track's G2 (Verified capability; charter 9.2)

- [ ] **C1** The code paths used by the track pass their tests of §10
  - status: FAIL
  - evidence: Collision operator rows of brief section 10 pass (G1, signed; heat series: kappa/kappa_1 = 1.020 +- 0.004, run C-20261124-131012-f920f45). Row 'Einstein-Vlasov steady states and their stability threshold': the steady state FAILED at N = 1e5 on M/8 (controls of y0 = 0.334032, 0.344 collapse at 534.8, 549.3 M; C-20261124-130634-3338d9b, on record) and HOLDS at N = 1e6 (control N6c C-20261124-221122-928c9eb: no collapse in 600 M, alpha_c within [-0.0022, +0.0115]; analysis C-20261125-122010-fb3cc08, fig_nseries.png read; NS.1 held, NS.2 failed, JOURNAL 2026-11-25T12:21Z). The threshold part is not located: bracket at N = 1e6 queued (q0046 N6b344, q0047 N6b324). Stays FAIL until the bracket is read. Batch 20: block A closed (C-20261125-160056-a5b7282): the y0 = 0.324 control at N = 1e5 also crosses alpha_min 0.3 (599.99 M), so all three N = 1e5 controls fail; collapse times are lapse markers, no run had the horizon finder (C-20261125-160207-05b6db1, decision 0040 item 3).
- [ ] **C2** Three-way convergence in particle number, mesh spacing, and gauge or boundary
  - status: FAIL
  - evidence: Particle number on M/8: N = 1e5 control collapses at 534.8 M, N = 1e6 holds 600 M (C-20261125-122010-fb3cc08); H-norm2 floor ratio 9.95 for N ratio 10; third point N4c queued (q0018); seed scatter at 1e5 from q0022, q0023. Mesh (collisional t_c, collision cells M/4): 206.64 (M/4), 163.41 (M/8), 158.42 M (M/16), differences 43.23 and 4.99 M (C-20261125-122020-031b67e, fig_d2.png read; M16.1, M16.2 held); the seed scatter at M/8 that judges the 3.1 per cent M/8->M/16 shift waits for q0024 (D2f2s2+). Gauge or boundary: no run yet; D2 with shift_eta 1.0 queued (q0048, B17.4). Collisionless mesh leg of the threshold (M/16 at N = 1e6) and its gauge leg (shift_eta 1.0): queued in batch 20 under ruling 0039 item 3 (A16b344, A16b324, N6b344e1, N6b324e1; predictions B20.1-B20.3, JOURNAL 2026-11-25T16:02Z; decks smoke-tested, C-20261125-155959-866b049).
- [x] **C3** Constraints behave
  - status: PASS
  - evidence: H-norm2 of the controls flat after 50 M at a floor set by the deposit noise: 8.6e-4 (N = 1e5) and 8.5e-3 (N = 1e4) on M/4, ratio 9.97 = the N ratio (C-20261124-130021-5c9c207, fig_cc2_N.png, panel 3); on M/8 the floor is 9.3 times that of M/4 at equal N (drift entry 12), close to the factor 8 of the particles per cell. No growth before collapse in any run read; after collapse the guard or the excision ends the record. [JUDGEMENT: "behave" read as bounded and scaling with the particle noise; convergence of the floor with the mesh is not expected at fixed N.]
- [x] **C4** A first minimal full-GR kinetic run
  - status: PASS
  - evidence: Full-GR kinetic runs with and without collisions to 300-600 M on M/8 (release core-v0.6): D2 (C-20261122-103854-4670b59, -144455-6e0992e, -141414-399ad97, -181011-60baef9) and block A (15 chains, e.g. C-20261121-214601-40dc927).

## Main products of G2 (charter 9.2)

- [ ] **C5** Verification report (decision 0012: STAGE_REPORT.md with EVIDENCE.md and OPEN.md; no REPORT.md)
  - status: OPEN
  - evidence: STAGE_REPORT.md written by nrpic-stage report in this session with EVIDENCE.md and OPEN.md; the verification it reports is incomplete (C1, C2, C7).
- [ ] **C6** Reproducibility package
  - status: OPEN
  - evidence: Every run registered (tracks/C-sidm/runs/); decks and readers in tracks/C-sidm/longruns/ (README "How to rerun the analyses"); not yet a package that verifies the capability (C7 open).

## Track-specific criteria of C-sidm for G2 (9.6 Track C: relativistic collapse of an SIDM core (S3))

- [ ] **C7** The collisionless threshold reproduces the literature value with three-way convergence
  - status: FAIL
  - evidence: Not located. At N = 1e5 on M/8 block A is unfit by its own refutation rule (A.4 failed; C-20261124-130634-3338d9b, on record). N6c shows the cause is particle noise (NS.1 held), so the reading moves to N = 1e6: bracket y0 = 0.324 / 0.344 kicked inward at N = 1e6 queued (q0046, q0047; predictions B17.5, B17.6, JOURNAL 2026-11-25T12:01Z). Three-way convergence of the threshold: mesh (M/16) and gauge (shift_eta 1.0) members queued in batch 20 (B20.1-B20.3); the particle-number leg of the bracket has the N = 1e5 kin members of block A (0.344 kin collapses at 229.79 M, 0.324 kin holds 600 M; C-20261125-160056-a5b7282), whose controls fail.
- [x] **C8** Once the collision module is in core, the budgets of conserved quantities close in curved spacetime
  - status: PASS
  - evidence: Collision budget in curved spacetime, coll_energy = particle, D2 on M/8: summed dH_particles / sum MH below 3.2e-16 up to the first excision for f = 1, 2, 4; rest-mass budget 2.7e-14; deposit identity 1e-15 (C-20261124-130442-0819c88, d2.json). Open item for the verifier: the collision-count test before t_c gives z = -3.39 at f = 4 (REVIEW-wave3 section 14).

## Rulings of the orchestrator on the criteria (coord/DECISIONS; check that they apply to G2)

- [ ] **C9** Track C. The references and the wording that the lead corrected are taken into `coord/BRIEF_ERRATA.md`; the G2 criterion reads "the collisionless threshold is located with three-way convergence and compared with the turning-point criterion". (0013)
  - status: FAIL
  - evidence: As C7: the threshold is not yet located; comparison with the turning point y_max = 0.334032 follows from the N = 1e6 bracket (q0046, q0047) at one mesh and one N; mesh and gauge legs of the bracket queued in batch 20 (ruling 0039 item 3; B20.1-B20.3).

## Minimum figures at G2 (brief 13.4)

- [ ] **C10** Schematic: Verification ladder
  - status: OPEN
  - evidence: No verification-ladder schematic for G2 yet (G1 schematics in tracks/C-sidm/note/).
- [ ] **C11** Data figure: Convergence figures (one each for particle number, mesh, gauge)
  - status: OPEN
  - evidence: Particle number: fig_nseries.png (C-20261125-122010-fb3cc08, N = 1e5 vs 1e6 on M/8; read) and fig_cc2_N.png, fig_diffusion.png (M/4; C-20261124-130021-5c9c207, -130222-6a4924d); mesh: fig_d2.png with M/16 (C-20261125-122020-031b67e; read); gauge: none until q0048. Note figures not drawn.
- [x] **C12** Data figure: Constraint norms against time
  - status: PASS
  - evidence: Constraint norms against time: fig_cc2_N.png panel 3 (C-20261124-130021-5c9c207), looked at.
- [ ] **C13** Data figure: At least one multi-scale slice mosaic with zoom boxes
  - status: OPEN
  - evidence: No slice mosaic yet.

## Package (brief 13.3, decision 0012; judged by the session)

- [x] **C14** Package documents of decision 0012: STAGE_REPORT.md (nrpic-stage report), EVIDENCE.md, OPEN.md and this CHECKLIST.md in the stage directory; REVIEW.md where the lead rechecked helpers; the scoping text in SCOPE.md or SCOPING.md beside them or in the scope directory, named in the report (no REPORT.md needed)
  - status: PASS
  - evidence: STAGE_REPORT.md, EVIDENCE.md, OPEN.md, CHECKLIST.md in stage/G2/; REVIEW is stage/REVIEW-wave3.md section 14; scoping text tracks/C-sidm/scope/.
- [ ] **C15** Data figures drawn with /zoom-figure-style from registered run outputs, one script per figure, every PNG looked at
  - status: OPEN
  - evidence: Analysis figures exist in the run directories (each looked at); the note figures of G2 are not drawn.
- [ ] **C16** Schematics drawn with /sleep-paper-figure-style: track architecture (exists / to be ported / new) and the gate timeline
  - status: OPEN
  - evidence: G2 schematics not drawn.
- [ ] **C17** Working note written with /paper-writing; its manuscript checker passed with --compile
  - status: OPEN
  - evidence: The working note has its G1 sections only.
- [ ] **C18** Verifier subagent (fresh context) wrote VERIFIER.md (decision 0016; VERIFIER_REPORT.md accepted too); every number of the Supplemental Material recomputed from the manifests
  - status: OPEN
  - evidence: No G2 verifier yet; what it must cover: OPEN.md section "What a G2 verifier must cover".
- [x] **C19** Null results and failed runs are on record (manifests and JOURNAL)
  - status: PASS
  - evidence: Failed predictions and runs on record: JOURNAL 2026-11-24T13:12Z (N.3, D2.2, A.1 kout part, A.3, A.4) and 2026-11-25T12:21Z (NS.2); withdrawn unqueued predictions B17.1-B17.3 (2026-11-25T12:01Z); failed analysis runs of batch 11 (own script bugs, rerun); preempted chains keep their manifests; six N = 1e5 continuations removed from the queue with the reason (stage/G2/OPEN.md).
- [x] **C20** STATUS.md, JOURNAL.md and HANDOFF.md are current
  - status: PASS
  - evidence: Rewritten at the end of the batch-20 lead session (2026-11-25).
