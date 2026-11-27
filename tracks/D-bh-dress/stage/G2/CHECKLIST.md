# Checklist: D-bh-dress G2

Collected by `harness/bin/nrpic-stage collect D-bh-dress G2` on 2026-11-26T05:56:37Z from `coord/CHARTER.md` (last changed in a61186835) and the brief (sections 13.3 and 13.4).
For each item set `status:` to PASS, FAIL or NA (OPEN until judged) and give the evidence: run ids,
figure files, KB locators, commits. `nrpic-stage report` reads this file; the automated checks are
in VERIFY_RESULTS.md (`nrpic-stage verify`), not here.

## Evidence required at every track's G2 (Verified capability; charter 9.2)

- [x] **C1** The code paths used by the track pass their tests of §10
  - status: PASS
  - evidence: Ladder table stage/G2/LADDER.md (rows D owns: Einstein-Straus null test N at M/8 and M/16, converged-finder re-search FP; self-similar infall Q16/Q16-256; D's growth criterion G) and schematic D-20261124-175505-a1053fa. Null test N holds at M/8 (judge_long D-20261123-020550-f9a3482: 2.28e-4 against 2.51e-4) and M/16 (1.99e-4, D-20261124-131138-0b8ffc5); converged finder <= 7.3e-5 (fp_analyse D-20261124-172508-c847ee4). Growth criterion G holds at N/4, N, 4N (D-20261126-054616-a13a888, D-20261125-115647-fd2f3f7, D-20261125-122827-c5735f8) and at M/8, M/16 with own-mesh controls (D-20261123-020614-7ba5874, D-20261126-055158-30ae09c). On record as failed with its ruling: P5 (M/4 null test fails by a factor 20, judge_conv D-20261125-122227-3eb563a; decision 0039 item 4: M/4 outside the convergent regime, labelled so). every horizon number made without `<fastflow> diagnostics` (decision 0041 item 4) and rechecked by the failure signature (hz_check D-20261125-160142-b1c51b5, D-20261126-055208-4e0fd0e). All G2 runs slice with plain 1+log (decision 0025 item 3; OPEN.md section 2). The fresh G2 verifier is item C17.
- [x] **C2** Three-way convergence in particle number, mesh spacing, and gauge or boundary
  - status: PASS
  - evidence: Particle number, three members, read whole (g2long entries 26-27): N/4 FNQ D-20261124-172725-2f426b6, N FK D-20261123-022725-a553496, 4N FN4 D-20261124-134157-b17938b; |M_4N - M_N| <= |M_N - M_N/4| at all four named times, window-rms ratio 1.9-3.1 against 2 for N^-1/2 noise (conv3 D-20261126-055249-505b079, conv3.png looked at); removed m E_K of N/4 within 0.86 per cent of N (np_partial D-20261126-054636-93618ee). Mesh of the growth: M/8 ES-FL D-20261121-203150-15f2bad and M/16 FL16 D-20261124-172745-72472ed agree in Delta M from 20 M to 4.4e-4, 1.2e-4, 8.6e-5 at 100, 200, 300 (299) M (bound 3e-3; 3.6e-4 to 1.3e-5 with own controls); these samples understate the difference: its envelope is 1.0e-3 at most, with a systematic part of +5.8e-4 (mean of M/16 - M/8 over 250-299 M), not removed by the own controls (R5; GATE_REVIEW section 5 item 1; VERIFIER section 9) [correction d of the gate review, 2026-11-27]; M/4 FF4 D-20261123-022727-1c17e73 drawn and labelled outside the convergent regime (decision 0039 item 4); two members in the regime, NO order claimed (L3 held as written only against the out-of-regime M/4). Mesh of the null test: M/8 and M/16 at the floor, two members and no order (decision 0041 item 4). Boundary: faces +-192/384/768 M (boundary_gauge D-20261124-131657-89cd963). Gauge: plain 1+log only; the relaxed lapse cannot serve (OPEN.md section 2) - stated as the gap of the gauge leg. every horizon number made without `<fastflow> diagnostics` (decision 0041 item 4) and rechecked by the failure signature (hz_check D-20261125-160142-b1c51b5, D-20261126-055208-4e0fd0e).
- [x] **C3** Constraints behave
  - status: PASS
  - evidence: Volume norms bounded in all long runs (D-20261123-021027-e3af9b8); exterior plane norms bounded to 500 M (XC1, D-20261124-134211-c6fce88). Particle noise of the deposit shown three ways: XN 4N/N = 0.43-0.49 (D-20261125-122849-43db157), XQ N/4 over N = 1.65-1.89 on A1/A2 at 100 and 200 M (D-20261126-054718-afa783e, looked at), region shells FNQ/FN4 = 3.2-5.2 from 20 to 400 M (region_norms D-20261126-054736-10c837a, looked at). Mesh: L5 M/16 over M/8 on A1 2.11 at 100 M, 1.08 at 200 M, 1.00 at 300 M (D-20261126-055159-6c40115, looked at). On record: XC2's expected fall failed (factor 1.05), R1's 'every column finite' failed on the NaN of the empty horizon sphere at t = 0 (g2long entries 12, 24).
- [x] **C4** A first minimal full-GR kinetic run
  - status: PASS
  - evidence: ES-F (D-20261121-144631-aa7ce9b) and ES-FL (D-20261121-203150-15f2bad, 850724 particles, 500 M): kinetic matter falling into an evolved puncture in full GR; analyses D-20261123-020606-fa0046c, -020614-7ba5874.

## Main products of G2 (charter 9.2)

- [x] **C5** Verification report (decision 0012: STAGE_REPORT.md with EVIDENCE.md and OPEN.md; no REPORT.md)
  - status: PASS
  - evidence: STAGE_REPORT.md (nrpic-stage report, batch 25), EVIDENCE.md, OPEN.md, this CHECKLIST, LADDER.md, REVIEW.md; working note v3 (note/main.pdf, section V and ledger part 11). What stays open is listed in OPEN.md: failures on record with their rulings and the fresh-context verifier (C17).
- [x] **C6** Reproducibility package
  - status: PASS
  - evidence: stage/G2/rerun_g2.py: every run id cited in CHECKLIST, EVIDENCE, LADDER, OPEN and STAGE_REPORT looked up in its manifest; 35 analyses rerun as new registered runs from the registered card outputs (5 that name no output directory of their own are listed and not rerun), 6 processor simulations with --include-sims, 14 card runs listed with input and card-hours for the queue only. Tested: rerun of xc_plane D-20261125-122849-43db157 as D-20261125-160651-29a730e gives a byte-identical xc_plane.json.

## Track-specific criteria of D-bh-dress for G2 (9.7 Track D: black-hole growth and dark-matter dress (S4))

- [x] **C7** In the vacuum-bubble case the drift of the horizon mass does not exceed the noise floor
  - status: PASS
  - evidence: Criterion N of g2long entry 1 (fixed before the runs): max |D_ES1L - D_V1L| on 100-500 M = 2.28e-4 against 2.51e-4 = 2 F_V(500) (judge_long D-20261123-020550-f9a3482); M/16 1.99e-4 on 100-300 M (H3, D-20261124-131138-0b8ffc5). Since batch 11b the floor's cause is found: the production finder's stopping rule (FP2, FP3: converged-finder vacuum drift 1.8e-5 at M/8 over 100-500 M, 3.9e-6 at M/16); with the converged finder the bubble-minus-vacuum difference is at most 7.3e-5 (M/8, 100-500 M) and 5.5e-5 (M/16, 100-300 M), without a trend in time; the bubble's horizon mass dips by 4-6e-5 at 100 M at both meshes (FP5, FP-ext, FE; D-20261124-172508-c847ee4, D-20261124-175356-0f40f1a; fp_analyse.png and fe_analyse.png looked at). Reservation: at M/4 the criterion FAILS (FE4: 4.6e-3 at 300 M, P5 refuted, judge_conv D-20261125-122227-3eb563a, g2long entry 21): N holds at M/8 and M/16 only; M/4 is outside the convergent regime. Horizon searches rechecked (decision 0040 item 3; no D run has a status file, every one was made without `<fastflow> diagnostics`): by the source-fixed signature of a failed search (NaN or bit-identical repeat), none after 20 M in any of 13 summaries, the plateaus are found surfaces, no removal reads a failed line, N unchanged; four V-1L dumps also by core's status files (hz_check D-20261125-160142-b1c51b5, D-20261125-160241-2b7ba3b; g2long entry 24).
- [x] **C8** With matter filled in, the mass growth agrees with the integrated particle flux through the horizon
  - status: PASS
  - evidence: Criterion G of g2long entry 1 holds at every member: (iii) every 10 M bin within +-1 per cent (+-2 per cent for N/4) and D2 at every sample: ES-FL M/8 61 bins, max 0.620 per cent (D-20261123-020614-7ba5874); FL16 M/16 38 bins, 0.485 (D-20261126-055158-30ae09c, own control V-1L16); FK N 50 bins, 0.249 (D-20261125-115647-fd2f3f7); FN4 4N 0.239 (D-20261125-122827-c5735f8); FNQ N/4 0.290 (D-20261126-054616-a13a888); FF4 M/4 0.685 with its own control, outside the regime (D-20261125-121123-143a007). The (iii) step at tau_rem ~285 M is the end of horizon excision at 4 x initial_radius (FK, P9). On record: D3 fails at M/4 and at N/4 (8352 of 29984 removals after ~220 M, g2long entry 26); early removals before the exact crossing (FK, FN4, FNQ): decided by the fresh verifier (VERIFIER.md section 4.1, run D-20261126-062436-72c04d3) as early arrivals, not early excision - the numerical shells run ahead of the exact LTB solution by about 0.2 per cent of their proper time at R0 = 28 M (0.78 M at M/8 and N, 0.55 M at 4N, 0.40 M at M/16), converging with cell size and particle number [VERIFIED for the tracers, JUDGEMENT for the dust]; D4 has no bound. D3 of FK: no violation; the smallest value of M_AH - [M_ctrl - 1] - m_disc over FK's removals is -1.4e-4, inside the criterion's allowance of -3e-4 (the earlier wording 'min margin -1.4e-4' read as a violation; VERIFIER section 9). FF4's D2 '480 samples with its own control' holds with V-1L4 held at its last value after 299 M; 280 samples lie within the control's range (VERIFIER section 4.2) [corrections g, h, c of the gate review, 2026-11-27]. every horizon number made without `<fastflow> diagnostics` (decision 0041 item 4) and rechecked by the failure signature (hz_check D-20261125-160142-b1c51b5, D-20261126-055208-4e0fd0e).

## Minimum figures at G2 (brief 13.4)

- [x] **C9** Schematic: Verification ladder
  - status: PASS
  - evidence: Verification-ladder schematic schem_ladder.png, registered D-20261124-172838-3a30e48 and, redrawn after test FE, D-20261124-175505-a1053fa (paperfig style, g2long/tools/schem_ladder.py), both looked at by the lead on 2026-11-24; it will be redrawn as the queued runs end.
- [x] **C10** Data figure: Convergence figures (one each for particle number, mesh, gauge)
  - status: PASS
  - evidence: Particle number and mesh of the growth: conv3.png (D-20261126-055249-505b079) and in the note fig_g2conv (note build D-20261126-055502-fbb1bec), looked at; mesh of the null test: judge_conv.png (D-20261125-122227-3eb563a) and fp_analyse.png panel (d) (D-20261124-172508-c847ee4); boundary/gauge: boundary_gauge.png (D-20261124-131657-89cd963).
- [x] **C11** Data figure: Constraint norms against time
  - status: PASS
  - evidence: constraints_long.png (D-20261123-021027-e3af9b8), xc_plane.png (D-20261124-134211-c6fce88, D-20261125-122849-43db157, D-20261126-054718-afa783e, D-20261126-055159-6c40115) and region_norms.png (D-20261126-054736-10c837a, FN4 and FNQ to 400 M), each looked at by the lead.
- [x] **C12** Data figure: At least one multi-scale slice mosaic with zoom boxes
  - status: PASS
  - evidence: Slice mosaic with zoom boxes D-20261124-134644-2389227 (g2long/tools/slice_mosaic.py), looked at by the lead of batch 11.

## Package (brief 13.3, decision 0012; judged by the session)

- [x] **C13** Package documents of decision 0012: STAGE_REPORT.md (nrpic-stage report), EVIDENCE.md, OPEN.md and this CHECKLIST.md in the stage directory; REVIEW.md where the lead rechecked helpers; the scoping text in SCOPE.md or SCOPING.md beside them or in the scope directory, named in the report (no REPORT.md needed)
  - status: PASS
  - evidence: CHECKLIST, EVIDENCE, OPEN, LADDER, STAGE_REPORT present; stage/G2/REVIEW.md points to the lead reviews in stage/REVIEW-wave3.md (sections 13-23); scope text scope/SCOPE.md; rerun plan stage/G2/rerun_plan.json (rerun_g2.py --json).
- [x] **C14** Data figures drawn with /zoom-figure-style from registered run outputs, one script per figure, every PNG looked at
  - status: PASS
  - evidence: Note v3 data figures drawn by one script each from registered run outputs (note/scripts/fig_*.py; new fig_g2conv.py), all regenerated by the registered build D-20261126-055502-fbb1bec (run_all 15 of 15); figure pages of the compiled note looked at by the lead (pages 11-14). The other G2 figures (judge_long, esf_criteria, xc_plane, region_norms, hz_check, conv3) are drawn with figstyle by their registered readers and were looked at.
- [x] **C15** Schematics drawn with /sleep-paper-figure-style: track architecture (exists / to be ported / new) and the gate timeline
  - status: PASS
  - evidence: note/figures/schem_architecture.png (on release core-v0.7: released capabilities as exists, the excision guard as provided by core on a tested branch) and schem_timeline.png (G2 package assembled), paperfig style, drawn by the registered build D-20261126-055502-fbb1bec and looked at by the lead.
- [x] **C16** Working note written with /paper-writing; its manuscript checker passed with --compile
  - status: PASS
  - evidence: Note v3 (note/main.tex, 24 pages): section V 'Verified capability' (null test to 500 M, growth at three particle numbers and two cell sizes, what stays open), ledger part 11 with every G2 number and its run id; compiled; check_manuscript.py --compile: 0 undefined references, 0 undefined citations, 0 overfull boxes; remaining candidates are run ids in the ledger (by design) and four contrastive phrasings kept where the contrast carries the content.
- [x] **C17** Verifier subagent (fresh context) wrote VERIFIER.md (decision 0016; VERIFIER_REPORT.md accepted too); every number of the Supplemental Material recomputed from the manifests
  - status: PASS
  - evidence: stage/G2/VERIFIER.md (fresh context, own exact LTB reference and own readers, predictions committed first; every checked number reproduced to three digits; one open point decided: the early removals, section 4.1; one ledger reservation, FF4's D2, section 4.2; two wording corrections, section 9). Gate review stage/G2/GATE_REVIEW.md (own reader of the raw finder summaries, nine predictions, all held): PASS WITH RESERVATIONS; gate G2 signed 2026-11-26 (coord/GATES.md, decision 0045). The eight corrections of its section 6 applied 2026-11-27 (stage/REVIEW-wave3.md, section of batch 34).
- [x] **C18** Null results and failed runs are on record (manifests and JOURNAL)
  - status: PASS
  - evidence: Failed predictions on record in g2long/JOURNAL.md: entry 5 (V3, E2 sharper bounds, E3, F2 at 400/500 M, F3 median and D1, F4 reason 3, H1, H2), entry 11 (P2), entry 12 (XC2 expected factor), entry 14 (FP4 refuted, FP-ext (ii) missed its bound); QR3/QR4 in secondary_infall/JOURNAL.md; cut chains closed as failed and resumed (entry 10). Batch 17-20: P5 refuted, P6, P11, P13 failed (entries 19-21); entry 24: R1 failed as written (NaN Hmax of the empty horizon sphere at t = 0), T1 failed for FN4 as an extension (3.4 per cent before 219 M); hz_check run D-20261125-160123-f86d73c failed (parser), on record. Batch 25: D3 fails at N/4 (FNQ, entry 26); conv3's first reading dropped the 300 M mesh time (D-20261126-055207-0137c53, reader changed after it and rerun, entry 27); np_partial's 'partial' label on a whole reading (entry 26).
- [x] **C19** STATUS.md, JOURNAL.md and HANDOFF.md are current
  - status: PASS
  - evidence: STATUS.md, JOURNAL.md and HANDOFF.md rewritten at the end of batch 25 (2026-11-25).
