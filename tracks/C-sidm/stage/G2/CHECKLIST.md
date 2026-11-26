# Checklist: C-sidm G2

Collected by `harness/bin/nrpic-stage collect C-sidm G2` on 2026-11-26T12:34:00Z from `coord/CHARTER.md` (last changed in a61186835) and the brief (sections 13.3 and 13.4).
For each item set `status:` to PASS, FAIL or NA (OPEN until judged) and give the evidence: run ids,
figure files, KB locators, commits. `nrpic-stage report` reads this file; the automated checks are
in VERIFY_RESULTS.md (`nrpic-stage verify`), not here.

## Evidence required at every track's G2 (Verified capability; charter 9.2)

- [ ] **C1** The code paths used by the track pass their tests of §10
  - status: OPEN
  - evidence: Collision-operator rows of brief section 10 pass (G1 signed; conductivity 1.020 +- 0.004, C-20261124-131012-f920f45). Row 'Einstein-Vlasov steady states and their stability threshold', batch 27: the steady state holds at N = 1e6 on M/8 (N6c, no collapse in 600 M) and fails at N = 1e5 and 1e4 by particle-noise relaxation (controls collapse at 534.81 and 295.78 M; NS.1 and NS.3 held, nseries C-20261126-120656-f5c62bb, fig read); the threshold is bracketed at N = 1e6 on M/8: y0 0.344 kicked in collapses at 252.31 M, 0.324 kicked in holds 600 M inside +-0.015 (B17.5, B17.6 held; C-20261126-121836-c7a76c1, fig read). The unstable member repeats on M/16 and with shift_eta 1.0 (B20.2, B20.3 first half held); waits for the stable member on M/16 (q0057 A16b324) and with shift_eta 1.0 (q0058 N6b324e1). The N = 1e5 control failures stay on record (A.4, BA.3). Lapse markers throughout (alpha_min = 0.3; no run had the horizon finder, C-20261125-160207-05b6db1).
- [ ] **C2** Three-way convergence in particle number, mesh spacing, and gauge or boundary
  - status: OPEN
  - evidence: Particle number: control of y0 0.334032 on M/8 at N = 1e4, 1e5, 1e6: t_c 295.78, 534.81 M, none by 600 M; H-norm2 floor ratios 9.78 and 9.95 for N ratios 10 (C-20261126-120656-f5c62bb); the bracket members have the same fates at N = 1e5 and 1e6 (C-20261126-121836-c7a76c1). Mesh: collisional t_c 206.64 (M/4), 163.41 (M/8), 158.42 M (M/16); M/8 scatter over collision seed, cell and gauge 1.13 M (five runs, mean 164.61 M), so the M/8 -> M/16 shift of 6.2 M is resolved [JUDGEMENT]; the f = 2 seed pair differs by 2.24 M against the 2 M bar of D2.3 (FAILED on record) (C-20261126-121702-b6b1eda, fig read). Gauge: shift_eta 1.0 moves the collisional t_c from 163.41 to 164.01 M and the collision rate by 0.8 per cent (B17.4 held); the run stops non-finite at 190.4 M after collapse (C-20261126-034500-4b34b1c, failed on record). Threshold legs: unstable side repeated with shift_eta 1.0 (t_c 252.41 vs 252.31 M, C-20261126-123219-f734997, B20.3 first half held) and on M/16 (t_c 217.97 M, -13.6 per cent, C-20261126-124143-b485eac, B20.2 held); open: q0057 A16b324 (B20.1), q0058 N6b324e1 (B20.3 second half). Lapse markers throughout (alpha_min = 0.3; no run had the horizon finder, C-20261125-160207-05b6db1).
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
  - status: OPEN
  - evidence: At one mesh (M/8) and one N (1e6), in one gauge: the threshold of the King b = 1 family lies in (0.324, 0.344), which contains the turning point y_max = 0.334032 (B17.5, B17.6 held, C-20261126-121836-c7a76c1); the same fates at N = 1e5 (229.79 M; holds 600 M). The unstable member keeps its fate on M/16 (217.97 M, B20.2 held, C-20261126-124143-b485eac) and with shift_eta 1.0 (252.41 M, C-20261126-123219-f734997); three-way convergence waits for the stable member on M/16 (q0057 A16b324, B20.1) and with shift_eta 1.0 (q0058 N6b324e1, B20.3). The literature value is the turning point printed in arXiv:2009.08163 (y_max = 0.334, paper.tex line 953; recomputed 0.334032 in G1). Lapse markers throughout (alpha_min = 0.3; no run had the horizon finder, C-20261125-160207-05b6db1).
- [x] **C8** Once the collision module is in core, the budgets of conserved quantities close in curved spacetime
  - status: PASS
  - evidence: Collision budget in curved spacetime, coll_energy = particle, D2 on M/8: summed dH_particles / sum MH below 3.2e-16 up to the first excision for f = 1, 2, 4; rest-mass budget 2.7e-14; deposit identity 1e-15 (C-20261124-130442-0819c88, d2.json). Open item for the verifier: the collision-count test before t_c gives z = -3.39 at f = 4 (REVIEW-wave3 section 14).

## Rulings of the orchestrator on the criteria (coord/DECISIONS; check that they apply to G2)

- [ ] **C9** Track C. The references and the wording that the lead corrected are taken into `coord/BRIEF_ERRATA.md`; the G2 criterion reads "the collisionless threshold is located with three-way convergence and compared with the turning-point criterion". (0013)
  - status: OPEN
  - evidence: As C7: located as a bracket of +-3 per cent around the turning point at one mesh and one N; compared with the turning-point criterion (y_max = 0.334032 inside the bracket). Mesh and gauge legs: q0055, q0057, q0058.

## Minimum figures at G2 (brief 13.4)

- [ ] **C10** Schematic: Verification ladder
  - status: OPEN
  - evidence: No verification-ladder schematic for G2 yet (G1 schematics in tracks/C-sidm/note/).
- [ ] **C11** Data figure: Convergence figures (one each for particle number, mesh, gauge)
  - status: OPEN
  - evidence: Registered analysis figures exist and were read for all three legs: particle number fig_nseries.png (C-20261126-120656-f5c62bb), the bracket at two N (C-20261126-121836-c7a76c1); mesh fig_d2.png with M/4, M/8, M/16 (C-20261126-121702-b6b1eda); gauge fig_d2.png (eta1 dotted) and the threshold gauge leg (this session). Note figures of G2 not drawn (one script per figure via run_all).
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
  - evidence: G2 section written into the note (Sec. V 'Toward the capability gate', table VI with run ids; checker with --compile: 0 undefined references, 1 overfull box of 1.1 pt as at G1; pages 11 and 18 read). Open: the G2 figures and the mesh and gauge legs of the bracket.
- [ ] **C18** Verifier subagent (fresh context) wrote VERIFIER.md (decision 0016; VERIFIER_REPORT.md accepted too); every number of the Supplemental Material recomputed from the manifests
  - status: OPEN
  - evidence: No G2 verifier yet; what it must cover: OPEN.md section "What a G2 verifier must cover".
- [x] **C19** Null results and failed runs are on record (manifests and JOURNAL)
  - status: PASS
  - evidence: Failed predictions and runs on record: JOURNAL 2026-11-24T13:12Z (N.3, D2.2, A.1 kout part, A.3, A.4), 2026-11-25T12:21Z (NS.2), 2026-11-26T12:20Z (D2.3 seed-pair part, 2.24 M against 2 M); failed run D2eta1 (guard stop after collapse, C-20261126-034500-4b34b1c); withdrawn predictions B17.1-B17.3; failed analysis runs of batch 11; preempted chains keep their manifests; six N = 1e5 continuations removed from the queue with the reason (OPEN.md).
- [x] **C20** STATUS.md, JOURNAL.md and HANDOFF.md are current
  - status: PASS
  - evidence: Rewritten at the end of the batch-27 lead session (2026-11-26).
