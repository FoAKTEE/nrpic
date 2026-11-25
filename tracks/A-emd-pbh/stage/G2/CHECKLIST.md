# Checklist: A-emd-pbh G2

Collected by `harness/bin/nrpic-stage collect A-emd-pbh G2` on 2026-11-25T15:14:52Z from `coord/CHARTER.md` (last changed in a61186835) and the brief (sections 13.3 and 13.4).
For each item set `status:` to PASS, FAIL or NA (OPEN until judged) and give the evidence: run ids,
figure files, KB locators, commits. `nrpic-stage report` reads this file; the automated checks are
in VERIFY_RESULTS.md (`nrpic-stage verify`), not here.

## Evidence required at every track's G2 (Verified capability; charter 9.2)

- [ ] **C1** The code paths used by the track pass their tests of §10
  - status: OPEN
  - evidence: Rows of brief section 10 that are A's: (i) time-reversed Oppenheimer-Snyder = the expanding ball: horizon formation against the exact solution on three meshes (conv_ball A-20261121-120257-a2eb839) and across eight amplitudes 0.20-1.0 on mesh B (threshold_ball A-20261124-131120-5c974ce: tau_det within 0.03-0.14 M of exact, the code's finite-duration bracket (0.40, 0.42] equals the exact one); (ii) LTB: the periodic spherical peak P0L against its exact LTB reference B (A-20261124-130142-9a2d6a2: shells r0 >= 1.5 within 3 per cent to turnaround; no horizon found, P3 refuted); (iii) Szekeres: round 1 cut (N = 32 non-finite at tau = 26; szekeres/JOURNAL entry 9); card series N = 64, 128, 256 queued in batch 17 (q0040, q0041, predictions P17-P21 of entry 8, v0.7 executable, entry 10). (iv) Oblate and prolate collapse (SCOPE A2): no Track-A run yet; core's prolate test is the only evidence (not A's oblate counterpart). Batch 17: mesh-C member at threshold C-d0.42 (A-20261122-173202-f98c79f, analysis A-20261125-115027-17b419e) forms its horizon by the rule with tau_det 43.705 (exact 43.656), so the upper end of the bracket holds on M/64 too. OPEN until Szekeres runs, P0L's horizon is found (q0013, peak_leak6, in Slurm) and A2 is run or ruled out of A's G2. Batch 19: time measure of the threshold named: t_end = 45 M is the proper time of the core edge (the first trapped shell), equal to the synchronous time of the exact solution (threshold_ball DESIGN section 1); read in the outer comoving layers' proper time on the code's slice (46.5 M at B-d0.42's first detection) the code's bracket would be (0.42, 0.45] (VERIFIER-C18 5g; A-20261125-151126-7f79a83). Persistence and classification of every member rechecked against horizon_status_0.txt (decision 0040 item 3): all stand (same run). (iv) A2: S1L (A-20261123-025907-97bab8d, 20 particle snapshots through the Zel'dovich epoch) serves as A2 against the first-axis time 4.2 t_H (prediction periodic_threshold JOURNAL 2026-11-25 07:15 PST). Outcome (A-20261125-151629-bb77171, A-20261125-151715-66f198f, fig_a2_crossing.png): z crosses first (holds) but at 6.1-6.4 t_H on every clock, outside the band [3.4, 5.0]: A2 FAILED as predicted; cause not named; Newtonian-mode control of the same particles is the next test (processors).
- [x] **C2** Three-way convergence in particle number, mesh spacing, and gauge or boundary
  - status: PASS
  - evidence: conv_ball A-20261121-120257-a2eb839 (README table): mesh M/16, M/32, M/64 (ddet 0.193, 0.068, 0.017 M; orders 1.5, 2.0; horizon-mass error 7.4e-3, 2.1e-3, 2.1e-4), particle number x1, x8, x64 at mesh A and x1, x8 at B (time errors independent of N at B; mass error 2-5e-4 at fixed N on all meshes), boundary 16 M against 32 M (identical to 1e-7 / 1e-11). Gauge leg not run (boundary chosen, charter 9.2 'gauge or boundary'). Ball-radius leg on C added in batch 11 (C-R1.25: ddet +0.040 against +0.017, mass -1.2e-4 against -2.1e-4; T5 partly refuted). Corrected in batch 19 after VERIFIER-C18 (A-20261125-151126-7f79a83): ddet under three interpolations A 0.150-0.193, B 0.056-0.077, C 0.0166-0.0175 M, orders 1.2-1.5 and 1.75-2.1 (not 1.5, 2.0 alone); dtrap orders 2.1, 1.5 unaffected. Mass: the tracked set bounds the median error to [5.1e-3, 7.2e-3] (A), [-2.7e-3, -1.6e-3] (B), [-1.0e-3, +0.5e-3] (C); the A->C fall is mostly the particle number (one per cell) and C lies below the bracket width, so no mass order is claimed. The convergence of the time errors in mesh, N and boundary stands.
- [ ] **C3** Constraints behave
  - status: FAIL
  - evidence: Constraint norms are bounded through each run and jump only at the horizon (A-20261124-132342-d5dc06e, fig_constraint_conv.png), but they do not converge before t ~ 6: ||H||_2 is flat or grows slightly from M/16 to M/64 at t <= 4 (prediction K refuted) and is flat in particle number x1-x64 at fixed mesh (K2 refuted); ||M||_2 at t = 0 grows with the mesh (order -0.8). ||H||/||16 pi E|| on the mesh line outside the horizon is 0.11-0.21 at t = 0 and 0.3-3 later (threshold scan, T6 refuted). The floor is not localized at refinement boundaries or density jumps (K3 refuted, A-20261124-134637-bd0d6eb); step and source-extrapolation test K4 not yet run (batch 17: not started, the session was spent on C-d0.42). C-d0.42 on M/64: constraint ratio up to 1.94 (A-20261125-115027-17b419e), as on M/32. Ruling on the 0.1 bound of SCOPE section 3 still asked of orch. Batch 19: K4 (A-20261125-120525-8fb946e, analysis A-20261125-150851-5545f8e, fig_k4.png): ||H||_2 unchanged to 0.2 per cent with half the step and to 0.8 per cent without source extrapolation, and the processor run equals the card member to 1e-3 (K4a-c hold): the floor is independent of mesh, particle number, location, step and source timing. K4 is not the smoothed-edge test of decision 0039 item 2(c); that test has not run, so C3 stays FAILED as written (bound 0.1 kept). The verifier finds the line ratio at or above 0.1 already at t = 0 on every mesh (0.22 A, 0.11-0.20 B, 0.105 C).
- [x] **C4** A first minimal full-GR kinetic run
  - status: PASS
  - evidence: Full-GR kinetic runs (Z4c + particles, nrpic_cf expanding ball) that form horizons: conv_ball's 14 members (A-20261121-075926-d10c2c1, -083336-6a82131, -091934-ac62f5f, -110017-471b0ae) and the eight mesh-B threshold members (queue lines 3-11, closed with nrpic-run finish in batch 11); periodic P0L to t = 140 (A-20261122-235305-4ea0aa5).

## Main products of G2 (charter 9.2)

- [ ] **C5** Verification report (decision 0012: STAGE_REPORT.md with EVIDENCE.md and OPEN.md; no REPORT.md)
  - status: OPEN
  - evidence: STAGE_REPORT.md written by nrpic-stage report in batch 11 as an interim package; the verification report proper waits for C1, C3, C18.
- [ ] **C6** Reproducibility package
  - status: OPEN
  - evidence: Every run registered (manifests in tracks/A-emd-pbh/runs/, commands, inputs with sha256); scripts in conv_ball/, threshold_ball/, periodic_threshold/ with 'How to rerun' in conv_ball/README.md. threshold_ball/README.md now carries the results table and rerun steps (batch 17). Missing: a single rerun list for G2 (stage/G2/VERIFY).

## Track-specific criteria of A-emd-pbh for G2 (9.4 Track A: EMD primordial-black-hole formation (S1))

- [x] **C7** In the spherical case, the errors of the turnaround time and of the horizon-formation time relative to the exact solution converge in particle number, mesh spacing and ball radius
  - status: PASS
  - evidence: conv_ball (A-20261121-120257-a2eb839): turnaround time error converges B->C at order 2.1 (A->B flat: a flat maximum), horizon-formation time ddet at orders 1.5, 2.0 and trapping time 2.1, 1.5 in mesh spacing; time errors independent of particle number at mesh B; ball radius: dependence 0.09 M at A, 0.04 M at B, 0.024 M at C (C-R1.25, batch 11; T5 refuted at its 0.02 bound). Across amplitude (threshold_ball A-20261124-131120-5c974ce): |ddet| <= 0.14 M for delta_c 0.35-1.0 on mesh B. At threshold on M/64 (C-d0.42, A-20261125-115027-17b419e, entry 11): ddet -0.0135 against +0.0153 on M/32 (both below one search interval; T4's halving refuted as written), core trapping time error -0.096 against -0.209 and turnaround -0.027 against -0.054 (halved); line MOTS mass error on common times 2.1e-3 against 5.2e-3 (A-20261125-115550-fe60ff1). Batch 19: ddet carries an interpolation spread at the core edge (0.001 M on conv_ball C, 0.02-0.08 M on the B threshold members, 0.058 M on C-d0.42; A-20261125-151126-7f79a83); the stated orders become 1.2-1.5 and 1.75-2.1; dtrap (no interpolation) converges at 2.1, 1.5. Turnaround columns not rechecked by the verifier.
- [x] **C8** The horizon-mass error is of the same order as in the Oppenheimer–Snyder test of Wu and Most
  - status: PASS
  - evidence: Horizon-mass error (median over detections) 7.4e-3, 2.1e-3, 2.1e-4 on M/16, M/32, M/64 (conv_ball A-20261121-120257-a2eb839), against the source's fiducial Oppenheimer-Snyder level 1e-3 (main.tex:945) and best AMR particle RMS 7.3e-4 (main.tex:1484); threshold scan on M/32: |dmmed| 3.2e-4 to 9.4e-3 for delta_c 0.35-1.0 (A-20261124-131120-5c974ce). First-detection excess (up to 4-7 per cent at threshold) is carried by the slice, not the finder (threshold_ball entry 4). Corrected in batch 19 (A-20261125-151126-7f79a83, fig_c18_mass_bracket.png): the exact mass on the code's slice is bounded by the tracked particles, and the median error lies in [5.1e-3, 7.2e-3] (M/16), [-2.7e-3, -1.6e-3] (M/32), [-1.0e-3, +0.5e-3] (M/64): of the order of the source's 1e-3. Near threshold on M/32 the brackets are B-d0.42 [-5.6e-3, -0.5e-3], B-d0.40 [-9.6e-3, -3.7e-3], B-d0.35 [-7.7e-3, +0.5e-3]; C-d0.42 [-4.2e-3, +5.9e-3]; the former medians +2.8e-3, +3.2e-4, +2.4e-3, +2.4e-2 lie outside them and are withdrawn, as are the A medians (built on repeated summary rows). The first-detection excess is relative to the shell at the finder's coordinate radius; 'carried by the slice' stands on M/64 only (verifier).

## Rulings of the orchestrator on the criteria (coord/DECISIONS; check that they apply to G2)

- [x] **C9** Track A. The threshold line is built in the periodic box (the expanding ball holds only amplitudes below the comparison amplitudes of arXiv:2609.14218; lead's evidence in `scope/SCOPE.md`); the expanding ball stays the spherical verification case and the set-up for isolated collapses. The G1 scan-design criterion is met on the reference-based design; the Newtonian-mode runs are G2 work. (0013)
  - status: PASS
  - evidence: The expanding ball is the spherical verification case (conv_ball, threshold_ball); the threshold line is built in the periodic box (periodic_threshold): P0L/S1L on the refined periodic mesh run stably at cfl 0.5 (job 2, A-20261124-130507-10510ac); the box's horizon is not yet found (P3 refuted; peak_leak6 queued). Newtonian-mode runs were made at G1 (newton/).

## Minimum figures at G2 (brief 13.4)

- [ ] **C10** Schematic: Verification ladder
  - status: OPEN
  - evidence: Verification-ladder schematic not drawn yet (note/ has the G1 architecture and timeline schematics).
- [ ] **C11** Data figure: Convergence figures (one each for particle number, mesh, gauge)
  - status: OPEN
  - evidence: fig_convergence.png of conv_ball A-20261121-120257-a2eb839 (mesh, particle number, ball radius, boundary legs) and fig_threshold_outcome.png (A-20261124-131120-5c974ce) exist and were looked at; no gauge-leg figure (boundary leg chosen) and not yet drawn into the note with zoom-figure style.
- [x] **C12** Data figure: Constraint norms against time
  - status: PASS
  - evidence: fig_constraint_conv.png of A-20261124-132342-d5dc06e (norms of H and M against time on three meshes, the threshold members, the particle-number leg), looked at; fig_job2_q.png (periodic job 2) and fig_compare_ltb_P0L.png panel f.
- [ ] **C13** Data figure: At least one multi-scale slice mosaic with zoom boxes
  - status: OPEN
  - evidence: No multi-scale slice mosaic yet (the nested runs write line outputs, not field dumps; a mosaic needs 3D outputs of one member).

## Package (brief 13.3, decision 0012; judged by the session)

- [ ] **C14** Package documents of decision 0012: STAGE_REPORT.md (nrpic-stage report), EVIDENCE.md, OPEN.md and this CHECKLIST.md in the stage directory; REVIEW.md where the lead rechecked helpers; the scoping text in SCOPE.md or SCOPING.md beside them or in the scope directory, named in the report (no REPORT.md needed)
  - status: OPEN
  - evidence: CHECKLIST.md, EVIDENCE.md, OPEN.md and STAGE_REPORT.md exist (batch 11); scope text scope/SCOPE.md. Interim package, not for review.
- [x] **C15** Data figures drawn with /zoom-figure-style from registered run outputs, one script per figure, every PNG looked at
  - status: PASS
  - evidence: Every figure of this package is drawn by a registered analysis with the figstyle module (periodic_threshold/scripts/figstyle.py, python/nrpic/figstyle.py): job2_q, compare_ltb, line_trapped, threshold_ball analyse.py, constraint_conv; each PNG looked at by the lead (journals).
- [ ] **C16** Schematics drawn with /sleep-paper-figure-style: track architecture (exists / to be ported / new) and the gate timeline
  - status: OPEN
  - evidence: Schematics of note/ name release core-v0.3 (G1 reservation); not updated to v0.6.
- [ ] **C17** Working note written with /paper-writing; its manuscript checker passed with --compile
  - status: OPEN
  - evidence: The working note has no G2 sections yet.
- [ ] **C18** Verifier subagent (fresh context) wrote VERIFIER.md (decision 0016; VERIFIER_REPORT.md accepted too); every number of the Supplemental Material recomputed from the manifests
  - status: OPEN
  - evidence: verify_bh (independent check of BH-1R) exists; no fresh-context verifier has recomputed conv_ball's or threshold_ball's numbers for G2. Batch 19: the fresh verifier's report stage/G2/VERIFIER-C18.md (package stage/G2/verifier-c18) recomputed conv_ball and threshold_ball: classification, persistence, detection times, the bracket (0.40, 0.42], the constraint ratios and the failures of C3, T4, T5 reproduced; four mass medians and C-d0.42's not reproduced. Every finding answered with a registered analysis (A-20261125-151126-7f79a83; threshold_ball entry 12): the verifier's numbers stand, the READMEs and C2, C7, C8 are corrected to the brackets; A-R1.35's ddet (0.175 against 0.164) and the turnaround columns remain unchecked. OPEN because the G2 numbers still to come (S1L/A2, Szekeres, P0L6, smoothed edge, the note's Supplemental Material) have no verifier yet.
- [x] **C19** Null results and failed runs are on record (manifests and JOURNAL)
  - status: PASS
  - evidence: Failed runs closed as failed: A-20261121-235851-d2200d7 (A-mesh guard stops), A-20261121-131600-02b5d41 (periodic job 1); cut chains continued, not repeated (journals 2026-11-24); refuted predictions on record: T4 reason, T5, T6, P2-P4, Q1b, F1, K, K2, K3 (threshold_ball entries 4-9, periodic_threshold entries 2026-11-24); batch 17: T4 mesh-C half refuted (entry 11), script defect run A-20261125-115530-a4f7dcd kept, q0014 (C-d0.40) withdrawn unrun with T7 untested (entry 8 note); G3 of the A-mesh guard test refuted "stops like G1" (passes to t = 48.5; A-20261125-120158-b76bfe3).
- [x] **C20** STATUS.md, JOURNAL.md and HANDOFF.md are current
  - status: PASS
  - evidence: STATUS.md, JOURNAL.md, HANDOFF.md, RISKS.md rewritten at the end of batch 17 (2026-11-25).
