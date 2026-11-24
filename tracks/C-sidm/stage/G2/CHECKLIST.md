# Checklist: C-sidm G2

Collected by `harness/bin/nrpic-stage collect C-sidm G2` on 2026-11-24T13:20:14Z from `coord/CHARTER.md` (last changed in a6118683) and the brief (sections 13.3 and 13.4).
For each item set `status:` to PASS, FAIL or NA (OPEN until judged) and give the evidence: run ids,
figure files, KB locators, commits. `nrpic-stage report` reads this file; the automated checks are
in VERIFY_RESULTS.md (`nrpic-stage verify`), not here.

## Evidence required at every track's G2 (Verified capability; charter 9.2)

- [ ] **C1** The code paths used by the track pass their tests of §10
  - status: FAIL
  - evidence: Collision operator rows of brief section 10 pass (G1, signed; box tests, heat T6-T8; conductivity series of batch 11 closes G1 reservation 1: kappa/kappa_1 = 1.020 +- 0.004 at zero cell and k lambda, run C-20261124-131012-f920f45). The row "Einstein-Vlasov steady states and their stability threshold" does NOT pass: on M/8 at N = 1e5 the collisionless controls of y0 = 0.334032 and 0.344 collapse on their own at 534.8 and 549.3 M (C-20261124-130634-3338d9b; JOURNAL 2026-11-24T13:12Z, A.3 and A.4 failed). Reproducible random numbers: rng.md of core (G1).
- [ ] **C2** Three-way convergence in particle number, mesh spacing, and gauge or boundary
  - status: FAIL
  - evidence: Particle number: on M/4 the energy diffusion scales as 1/N (D ratio 11.07, run C-20261124-130222-6a4924d) and the constraint floor as 1/N (9.95, C-20261124-130021-5c9c207); on M/8 the N-series (N = 1e4, 1e6 controls) is queued (JOURNAL 13:14Z). Mesh: M/4 -> M/8 changes the control drift sign (drift runs i, iii, vi) and the collisional t_c by 21 per cent (206.64 -> 163.41 M, C-20261124-130442-0819c88); M/16 member queued. Gauge or boundary: no run.
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
  - evidence: No threshold located yet: block A on M/8 at N = 1e5 is unfit by its own refutation rule (A.4 failed: two controls collapse within 600 M); kicked runs collapse 240 M (y0 = 0.334032) and 320 M (0.344) before their controls (C-20261124-130634-3338d9b). Decides next: N-series (N = 1e6 control) and M/16.
- [x] **C8** Once the collision module is in core, the budgets of conserved quantities close in curved spacetime
  - status: PASS
  - evidence: Collision budget in curved spacetime, coll_energy = particle, D2 on M/8: summed dH_particles / sum MH below 3.2e-16 up to the first excision for f = 1, 2, 4; rest-mass budget 2.7e-14; deposit identity 1e-15 (C-20261124-130442-0819c88, d2.json). Open item for the verifier: the collision-count test before t_c gives z = -3.39 at f = 4 (REVIEW-wave3 section 14).

## Rulings of the orchestrator on the criteria (coord/DECISIONS; check that they apply to G2)

- [ ] **C9** Track C. The references and the wording that the lead corrected are taken into `coord/BRIEF_ERRATA.md`; the G2 criterion reads "the collisionless threshold is located with three-way convergence and compared with the turning-point criterion". (0013)
  - status: FAIL
  - evidence: Same as C7: the threshold is not located; the comparison with the turning point y_max = 0.334032 waits for a mesh and N on which the controls hold.

## Minimum figures at G2 (brief 13.4)

- [ ] **C10** Schematic: Verification ladder
  - status: OPEN
  - evidence: No verification-ladder schematic for G2 yet (G1 schematics in tracks/C-sidm/note/).
- [ ] **C11** Data figure: Convergence figures (one each for particle number, mesh, gauge)
  - status: OPEN
  - evidence: Particle number: fig_cc2_N.png and fig_diffusion.png (runs C-20261124-130021-5c9c207, -130222-6a4924d); mesh: fig_d2.png (C-20261124-130442-0819c88) with M/16 pending; gauge: none.
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
  - evidence: Failed predictions and runs of this round on record: JOURNAL 2026-11-24T13:12Z (N.3, D2.2, A.1 kout part, A.3, A.4) and the failed analysis runs C-20261124-130433-e84cb43, -130951-36beb5c, -131113-b196c0e, -131221-49d5fcc (own script bugs, rerun); the ten preempted chains keep their manifests with continuations entries.
- [x] **C20** STATUS.md, JOURNAL.md and HANDOFF.md are current
  - status: PASS
  - evidence: Rewritten at the end of the batch-11 session.
