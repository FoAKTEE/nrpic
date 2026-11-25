# Checklist: D-bh-dress G2

Collected by `harness/bin/nrpic-stage collect D-bh-dress G2` on 2026-11-25T12:21:07Z from `coord/CHARTER.md` (last changed in a61186835) and the brief (sections 13.3 and 13.4).
For each item set `status:` to PASS, FAIL or NA (OPEN until judged) and give the evidence: run ids,
figure files, KB locators, commits. `nrpic-stage report` reads this file; the automated checks are
in VERIFY_RESULTS.md (`nrpic-stage verify`), not here.

## Evidence required at every track's G2 (Verified capability; charter 9.2)

- [ ] **C1** The code paths used by the track pass their tests of §10
  - status: OPEN
  - evidence: Ladder table stage/G2/LADDER.md (rows D owns: Einstein-Straus null test N at M/8 and M/16 with the converged-finder re-search FP; self-similar infall Q16/Q16-256; D's growth criterion G) and schematic D-20261124-175505-a1053fa. M/4 member of the null test: FE4 D-20261123-022726-1b133af closed; P5 REFUTED (judge_conv D-20261125-122227-3eb563a: at M/4 the bubble-minus-vacuum difference grows to 4.6e-3 by 300 M; M/8 and M/16 at 2e-4): the null test converges from M/8 on. Open: the G2 verifier (C17). All G2 runs slice with plain 1+log (decision 0025 item 3); the relaxed lapse and its mitigation are not used (OPEN.md section 2).
- [ ] **C2** Three-way convergence in particle number, mesh spacing, and gauge or boundary
  - status: OPEN
  - evidence: Particle number: N = FK D-20261123-022725-a553496 (closed; P7-P10 hold, fk_compare D-20261125-115637-7ee26c1, criterion G D-20261125-115647-fd2f3f7), 4N = FN4 D-20261124-134157-b17938b (closed; N1-N4 hold: esf_criteria D-20261125-122827-c5735f8, np_partial D-20261125-115729-011d028), N/4 = FNQ D-20261124-172725-2f426b6 (running, q0010, at 353 M of 400; region shells read to 350 M: FNQ/FN4 = 3.5-3.9 at 100 M, particle noise, region_norms D-20261125-160355-bda7e38). Mesh of the growth: M/4 FF4 D-20261123-022727-1c17e73 (closed; criterion G holds with its own-mesh control, D-20261125-121123-143a007; P13 failed as written), M/8 ES-FL, M/16 FL16 waits (q0011). Mesh of the null test: M/8, M/16 agree at the floor (converged finder fp_analyse D-20261124-172508-c847ee4); M/4 FE4 fails it by a factor 20 (P5 refuted, D-20261125-122227-3eb563a); per ruling 0039 item 4 the mesh leg of the null test is stated with two members (M/8, M/16) and NO order, no M/12 member (g2long entry 23: both sit at the converged-finder floor, nothing above it to give an order). Boundary: faces +-192/384/768 M (boundary_gauge D-20261124-131657-89cd963); the gauge axis cannot use the relaxed lapse (OPEN.md section 2). The horizon mass itself has no mesh order (P2, FP4).
- [ ] **C3** Constraints behave
  - status: OPEN
  - evidence: Volume norms bounded in all long runs (D-20261123-021027-e3af9b8); exterior plane norms on annuli outside 1.2 r_AH bounded to 500 M in eight runs (XC1, xc_plane D-20261124-134211-c6fce88, looked at); with dust the exterior residual is ~100x the vacuum one and falls with more particles per cell. XN HOLDS: the 4N/N ratio of the exterior plane norms is 0.43-0.49 on A1/A2 at 100 and 200 M, the N^-1/2 of particle noise (xc_plane D-20261125-122849-43db157, looked at). Region (sphere) norms READ (region_norms D-20261125-160355-bda7e38, region_norms.png looked at; g2long entry 24): volume identity to 4e-16; FN4's shells [1.2 r_AH, 6 M] and [6, 30] M at 0.52-0.82 of its plane norms (R2); FNQ/FN4 = 3.4-4.4 on both shells at 50-300 M (R3: particle noise, N^-1/2); on [30, 60] M the ratio is 1.1 to 150 M (deterministic), outside 60 M 1.000. Open: XQ (FNQ's end, q0010), L5 (FL16, q0011).
- [x] **C4** A first minimal full-GR kinetic run
  - status: PASS
  - evidence: ES-F (D-20261121-144631-aa7ce9b) and ES-FL (D-20261121-203150-15f2bad, 850724 particles, 500 M): kinetic matter falling into an evolved puncture in full GR; analyses D-20261123-020606-fa0046c, -020614-7ba5874.

## Main products of G2 (charter 9.2)

- [ ] **C5** Verification report (decision 0012: STAGE_REPORT.md with EVIDENCE.md and OPEN.md; no REPORT.md)
  - status: OPEN
  - evidence: STAGE_REPORT.md (nrpic-stage report), EVIDENCE.md and OPEN.md written in this session; the package is not complete (C1-C3, C9-C12, C16, C17 open).
- [x] **C6** Reproducibility package
  - status: PASS
  - evidence: stage/G2/rerun_g2.py: every run id cited in CHECKLIST, EVIDENCE, LADDER, OPEN and STAGE_REPORT looked up in its manifest; 35 analyses rerun as new registered runs from the registered card outputs (5 that name no output directory of their own are listed and not rerun), 6 processor simulations with --include-sims, 14 card runs listed with input and card-hours for the queue only. Tested: rerun of xc_plane D-20261125-122849-43db157 as D-20261125-160651-29a730e gives a byte-identical xc_plane.json.

## Track-specific criteria of D-bh-dress for G2 (9.7 Track D: black-hole growth and dark-matter dress (S4))

- [x] **C7** In the vacuum-bubble case the drift of the horizon mass does not exceed the noise floor
  - status: PASS
  - evidence: Criterion N of g2long entry 1 (fixed before the runs): max |D_ES1L - D_V1L| on 100-500 M = 2.28e-4 against 2.51e-4 = 2 F_V(500) (judge_long D-20261123-020550-f9a3482); M/16 1.99e-4 on 100-300 M (H3, D-20261124-131138-0b8ffc5). Since batch 11b the floor's cause is found: the production finder's stopping rule (FP2, FP3: converged-finder vacuum drift 1.8e-5 at M/8 over 100-500 M, 3.9e-6 at M/16); with the converged finder the bubble-minus-vacuum difference is at most 7.3e-5 (M/8, 100-500 M) and 5.5e-5 (M/16, 100-300 M), without a trend in time; the bubble's horizon mass dips by 4-6e-5 at 100 M at both meshes (FP5, FP-ext, FE; D-20261124-172508-c847ee4, D-20261124-175356-0f40f1a; fp_analyse.png and fe_analyse.png looked at). Reservation: at M/4 the criterion FAILS (FE4: 4.6e-3 at 300 M, P5 refuted, judge_conv D-20261125-122227-3eb563a, g2long entry 21): N holds at M/8 and M/16 only; M/4 is outside the convergent regime. Horizon searches rechecked (decision 0040 item 3; no D run has a status file, every one was made without `<fastflow> diagnostics`): by the source-fixed signature of a failed search (NaN or bit-identical repeat), none after 20 M in any of 13 summaries, the plateaus are found surfaces, no removal reads a failed line, N unchanged; four V-1L dumps also by core's status files (hz_check D-20261125-160142-b1c51b5, D-20261125-160241-2b7ba3b; g2long entry 24).
- [x] **C8** With matter filled in, the mass growth agrees with the integrated particle flux through the horizon
  - status: PASS
  - evidence: Criterion G of g2long entry 1: (iii) every 10 M bin of tau_rem <= 650 M within +-0.62 per cent of the exact LTB mass (61 bins), D2 at all 960 samples (esf_criteria D-20261123-020614-7ba5874, esf_criteria.png L; esf_bracket.png L). Batch 17: G holds for FK (50 bins to tau_rem 500 M, max 0.249 per cent; D-20261125-115647-fd2f3f7), for FF4 at M/4 with the M/4 control (60 bins, max 0.685 per cent; D-20261125-121123-143a007; with the M/8 control D2 fails, D-20261125-121034-8f82998) and, partially, for FN4/FNQ (np_partial D-20261125-115729-011d028). The (iii) step at tau_rem ~285 M of ES-FL is the end of horizon excision at 4 x initial_radius: absent in FK (P9, g2long entry 19). Reservations: FNQ and FL16 pending; D3 fails at M/4 (1704 early removals); FK's D4 split at 219 M (d4_timing D-20261125-160450-9326390, entry 24): before 219 M FK and ES-FL are identical (0 of 63344 removals before the exact crossing, min +0.0715 M in both); FK's 29.5 per cent come after 235 M, where it keeps horizon excision and ES-FL removes by the lapse rule; why excision then removes up to 0.36 M (FN4: 0.66 M, from 170 M) of proper time before the exact crossing stays [TO VERIFY] (D4 has no bound). Horizon searches rechecked (decision 0040 item 3; no D run has a status file, every one was made without `<fastflow> diagnostics`): by the source-fixed signature of a failed search (NaN or bit-identical repeat), none after 20 M in any of 13 summaries, the plateaus are found surfaces, no removal reads a failed line, N unchanged; four V-1L dumps also by core's status files (hz_check D-20261125-160142-b1c51b5, D-20261125-160241-2b7ba3b; g2long entry 24).

## Minimum figures at G2 (brief 13.4)

- [x] **C9** Schematic: Verification ladder
  - status: PASS
  - evidence: Verification-ladder schematic schem_ladder.png, registered D-20261124-172838-3a30e48 and, redrawn after test FE, D-20261124-175505-a1053fa (paperfig style, g2long/tools/schem_ladder.py), both looked at by the lead on 2026-11-24; it will be redrawn as the queued runs end.
- [ ] **C10** Data figure: Convergence figures (one each for particle number, mesh, gauge)
  - status: OPEN
  - evidence: Mesh: judge_conv.png (D-20261124-131149-9f0166d, three vacuum meshes) and fp_analyse.png panel (d) (converged finder, three meshes); boundary/gauge: boundary_gauge.png (D-20261124-131657-89cd963). Particle number: np_partial.png (D-20261125-115729-011d028; FK, FN4 whole, FNQ partial), final when FNQ ends (q0010). Growth mesh figure waits for FL16 (q0011).
- [x] **C11** Data figure: Constraint norms against time
  - status: PASS
  - evidence: constraints_long.png (volume norms, D-20261123-021027-e3af9b8), xc_plane.png (exterior annuli of the z = 0 plane, D-20261124-134211-c6fce88, D-20261125-122849-43db157) and region_norms.png (shell norms of the region spheres against time, FN4 and FNQ, with their ratio; D-20261125-160355-bda7e38), each looked at by the lead. FL16's region norms (q0011) will be added when it runs.
- [x] **C12** Data figure: At least one multi-scale slice mosaic with zoom boxes
  - status: PASS
  - evidence: Slice mosaic with zoom boxes D-20261124-134644-2389227 (g2long/tools/slice_mosaic.py), looked at by the lead of batch 11.

## Package (brief 13.3, decision 0012; judged by the session)

- [ ] **C13** Package documents of decision 0012: STAGE_REPORT.md (nrpic-stage report), EVIDENCE.md, OPEN.md and this CHECKLIST.md in the stage directory; REVIEW.md where the lead rechecked helpers; the scoping text in SCOPE.md or SCOPING.md beside them or in the scope directory, named in the report (no REPORT.md needed)
  - status: OPEN
  - evidence: CHECKLIST, EVIDENCE, OPEN, STAGE_REPORT present; stage/G2/REVIEW.md (batch 20) points to the lead reviews in stage/REVIEW-wave3.md (sections 13-21) and holds this session's recheck; scope text scope/SCOPE.md. Open until the package is complete (C1-C3, C5, C10, C14-C17).
- [ ] **C14** Data figures drawn with /zoom-figure-style from registered run outputs, one script per figure, every PNG looked at
  - status: OPEN
  - evidence: G2 figures so far drawn with figstyle (judge_long, esf_criteria, esf_bracket, esf_growth, constraints_long), each PNG looked at by the lead; not yet in the note.
- [ ] **C15** Schematics drawn with /sleep-paper-figure-style: track architecture (exists / to be ported / new) and the gate timeline
  - status: OPEN
  - evidence: The note schematics are those of G1 (note/figures/schem_*); no G2 update.
- [ ] **C16** Working note written with /paper-writing; its manuscript checker passed with --compile
  - status: OPEN
  - evidence: Note v2 (note/, 22 pages, checker passed --compile per note/README.md) covers ES-F to 200 M; the long runs are not in it.
- [ ] **C17** Verifier subagent (fresh context) wrote VERIFIER.md (decision 0016; VERIFIER_REPORT.md accepted too); every number of the Supplemental Material recomputed from the manifests
  - status: OPEN
  - evidence: No G2 verifier yet.
- [x] **C18** Null results and failed runs are on record (manifests and JOURNAL)
  - status: PASS
  - evidence: Failed predictions on record in g2long/JOURNAL.md: entry 5 (V3, E2 sharper bounds, E3, F2 at 400/500 M, F3 median and D1, F4 reason 3, H1, H2), entry 11 (P2), entry 12 (XC2 expected factor), entry 14 (FP4 refuted, FP-ext (ii) missed its bound); QR3/QR4 in secondary_infall/JOURNAL.md; cut chains closed as failed and resumed (entry 10). Batch 17-20: P5 refuted, P6, P11, P13 failed (entries 19-21); entry 24: R1 failed as written (NaN Hmax of the empty horizon sphere at t = 0), T1 failed for FN4 as an extension (3.4 per cent before 219 M); hz_check run D-20261125-160123-f86d73c failed (parser), on record.
- [x] **C19** STATUS.md, JOURNAL.md and HANDOFF.md are current
  - status: PASS
  - evidence: STATUS.md, JOURNAL.md and HANDOFF.md rewritten at the end of batch 20 (2026-11-25).
