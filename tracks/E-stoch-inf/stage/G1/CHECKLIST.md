# Checklist: E-stoch-inf G1

Collected by `harness/bin/nrpic-stage collect E-stoch-inf G1` on 2026-11-21T13:08:35Z from `coord/CHARTER.md` (last changed in a6118683) and the brief (sections 13.3 and 13.4).
For each item set `status:` to PASS, FAIL or NA (OPEN until judged) and give the evidence: run ids,
figure files, KB locators, commits. `nrpic-stage report` reads this file; the automated checks are
in VERIFY_RESULTS.md (`nrpic-stage verify`), not here.

## Evidence required at every track's G1 (Pre-core baseline; charter 9.2)

- [x] **C1** Baseline results obtainable without the NRPIC coupling
  - status: PASS
  - evidence: linear Mukhanov-Sasaki references of both cases (spec/ref/ms_reference.py; runs E-stoch-inf-20261115-122806-ef0d039, E-20261115-135532-3f958a1, verifier E-20261115-174606-3c67607, rerun identical E-20261119-150346-a513bc8); stochastic delta-N references (langevin/, runs E-stoch-inf-20261115-130137-176cdd6, -130139-176cdd6); the SR ladder itself needs no particle coupling (scalar field and Z4c only): STATUS.md, EVIDENCE.md 1
- [x] **C2** The analysis pipeline validated on them
  - status: PASS
  - evidence: analysis/sfa.py synthetic tests T1-T5, 15/15 (E-20261115-171445-36152c4, rerun identical E-20261119-150346-a513bc8); estimators against the code's own history on a plane perturbation (E-20261115-171859-0b34449); ladder reader bitwise equal to core's and R^NR at t = 0 within 7.5e-10 (E-20261115-172935-ddfade0); extraction factor E6 (E-20261115-174214-74becdd); lead's independent extraction on L32p agreeing to three digits (E-20261119-150238-b81e33f)
- [x] **C3** Interface proposals submitted
  - status: PASS
  - evidence: noise/NOISE_SPEC.md, noise/RNG_REQUIREMENTS.md, codebase/DESIGN_REVIEW.md 9 and 11, spec/SPEC.md 10; outbox 20261115T1410Z to core (initial slice, diagnostics, card build, noise results), answered by core (message scalar2-ready; interface proposal tracks/core/interfaces/scalar_field_2.md on core/scalar-2); outbox of 2026-11-19 (release request, A4 proposal)

## Main products of G1 (charter 9.2)

- [x] **C4** Baseline data and figures
  - status: PASS
  - evidence: ladder/results/final, final2 (time-matched pairing), floor, a6, a6_64, l5, seed2, a12 and ladder/fig/ (runs EVIDENCE.md 1 and 7); analysis/fig; g1verify/fig (verifier); stage/G1/fig/fig_lead_check.png; stage/review3/fig (leads of batches 2a and 3); note/figures/fig_sr_*.png (G1 data figures)
- [x] **C5** Interface documents
  - status: PASS
  - evidence: noise/NOISE_SPEC.md and RNG_REQUIREMENTS.md (track); coord/INTERFACES/ scalar field of core-v0.3; coord/INTERFACES/scalar_field_2.md and scalar_field_3.md (released in core-v0.4 and core-v0.5)

## Track-specific criteria of E-stoch-inf for G1 (9.8 Track E: stochastic inflation (S11, if possible))

- [x] **C6** The power spectrum of the slow-roll case agrees with the analytic result, super-horizon modes freeze by the criterion of arXiv:2606.14853, the constraints converge
  - status: PASS
  - evidence: met as ruled by decision 0021 item 1 (A4'): spectrum A2 1.21e-4 at 256^3 (second seed 2.12e-4), verified; freezing A3 within 2.4e-6 to 4.6e-6 of the full MS, FLRW lattice excluded by 1e4-1e5, verified; constraints converge (odd part order 5.5-5.96, halving 1.9989-2.0000; even part halving 3.986-4.000 and N-independent), verified; A4' (d) on the maxima over the entry 1709-1874; the strict A4 FAILS in P1's set-up and stays on record (odd/even 745, 655, 869, 25 at N = 32-256). STATUS.md, VERIFIER.md V2-V5, ../REVIEW-wave3.md

## Rulings of the orchestrator on the criteria (coord/DECISIONS; check that they apply to G1)

- [x] **C7** Track E. Decision of the feasibility gate, pending the group: continue to G1 and G2 (about two card-hours); the scope of G3 is decided at G2. The lead's choices of `spec/scope/SCOPE.md` section 4 are accepted. (0013)
  - status: PASS
  - evidence: applied: continue to G1 and G2; SCOPE 4 choices used (Courant 0.25, now justified by A6; level 0; thresholds A1-A7 as written, A4 failure kept on record); downgrade (SCOPE 4 item 5) not triggered: A3 passes, 0.503 card-hours per 256^3 SR realisation against 5

## Minimum figures at G1 (brief 13.4)

- [x] **C8** Schematic: Updated architecture
  - status: PASS
  - evidence: note/figures/schem_architecture.png (script note/scripts/schem_architecture.py; four states core-v0.3, core-v0.4/v0.5, track analysis, new or under way), drawn by registered run E-20261121-080840-6112292, reproduced by the lead's rerun E-20261121-130021-0140e4e; looked at by the note helper and by the lead of batch 3
- [x] **C9** Schematic: Data-flow diagram
  - status: PASS
  - evidence: note/figures/schem_dataflow.png (script note/scripts/schem_dataflow.py: mode tables -> AthenaK run -> analysis -> ledger and note), run E-20261121-080840-6112292, reproduced by E-20261121-130021-0140e4e; looked at by the lead of batch 3
- [x] **C10** Data figure: Baseline results
  - status: PASS
  - evidence: ladder/fig/final/fig_spectrum.png, fig_a2_modes.png, fig_a3_freezing.png; wave 3: ladder/fig/final2/fig_a4_paper.png, fig/a6_64/fig_a6.png, fig/l5/fig_l5.png, fig/seed2/fig_seed2.png; all looked at by the lead (2026-11-19, 2026-11-21)
- [x] **C11** Data figure: Validation figures for the analysis pipeline
  - status: PASS
  - evidence: analysis/fig/fig_t2_extraction.png, fig_plane_constraint_ratios.png; stage/G1/fig/fig_lead_check.png (script stage/G1/scripts/lead_check.py, run E-20261119-150238-b81e33f); all looked at

## Package (brief 13.3, decision 0012; judged by the session)

- [x] **C12** Package documents of decision 0012: STAGE_REPORT.md (nrpic-stage report), EVIDENCE.md, OPEN.md and this CHECKLIST.md in the stage directory; REVIEW.md where the lead rechecked helpers; the scoping text in SCOPE.md or SCOPING.md beside them or in the scope directory, named in the report (no REPORT.md needed)
  - status: PASS
  - evidence: STAGE_REPORT.md (nrpic-stage report), EVIDENCE.md, OPEN.md, CHECKLIST.md, VERIFIER.md, REVIEW.md (pointer to ../REVIEW-wave2.md and ../REVIEW-wave3.md), STATUS.md (criteria table); scoping text spec/scope/SCOPE.md
- [x] **C13** Data figures drawn with /zoom-figure-style from registered run outputs, one script per figure, every PNG looked at
  - status: PASS
  - evidence: one script per G1 data figure from registered outputs: note/scripts/fig_sr_modes.py, fig_sr_freezing.py, fig_sr_constraints.py, fig_sr_order.py (+ fig_background.py redrawn), figstyle copy; registered run E-20261121-080840-6112292 (every figure repeats with pixel rms 0), reproduced by the lead (E-20261121-130021-0140e4e, ../REVIEW-wave3.md B2); every PNG looked at (note helper; lead of batch 3)
- [x] **C14** Schematics drawn with /sleep-paper-figure-style: track architecture (exists / to be ported / new) and the gate timeline
  - status: PASS
  - evidence: schematics with paperfig: updated architecture (C8), data flow (C9) and the redrawn gate timeline note/figures/schem_timeline.png (G0 passed, G1 in progress, G2 USR); run E-20261121-080840-6112292; looked at
- [x] **C15** Working note written with /paper-writing; its manuscript checker passed with --compile
  - status: PASS
  - evidence: note/main.tex working note v1 (16 pages; Secs. VI-VIII: slow-roll reproduction, constraints with strict A4 failed on record and A4' as ruled, validation/reproducibility/cost), G1 ledger note/tables/ledger_g1.{md,tex}; check_manuscript.py --main main.tex --compile: 0 undefined references or citations, 0 overfull boxes, all pages read (note/JOURNAL.md 08:12 UTC); three \pending{} markers for a4res/usr/window (G2 material)
- [x] **C16** Verifier subagent (fresh context) wrote VERIFIER.md (decision 0016; VERIFIER_REPORT.md accepted too); every number of the Supplemental Material recomputed from the manifests
  - status: PASS
  - evidence: VERIFIER.md (fresh-context helper g1verify, own code from the raw dumps, V1-V7 committed db88f631 before it read the track's numbers). Ledger part: the G1 ledger (45 rows) compared row by row with the verifier's independent values and the leads' own-code runs (../REVIEW-wave3.md B4): of 40 track rows 27 agree with an independent value, 13 are the track's alone (listed there; reproduced by reruns), core's 3 rows are labelled [TO VERIFY]; no disagreement beyond a stated difference of definition. Reservation: the ledger was checked by the lead of batch 3 (who did not produce it), not by the fresh verifier
- [x] **C17** Null results and failed runs are on record (manifests and JOURNAL)
  - status: PASS
  - evidence: failed and stopped runs kept with manifests: E-20261115-172521-e098160, -170651-885fc6e, -171628-1737ebe, -171633-f574079, E-20261119-145853-ef835c2; wave 3: E-20261121-030415-22d518b, -031936-16d6ae5, -034609-f573ddc, -063758-d643396 (lead); superseded note runs E-20261121-075717-1849987, -080526-7fbe919; refuted predictions of batch 3: note N8, lead LU2 (dump 4, transcription) and LU3 (late value) (../REVIEW-wave3.md B1, B2); refuted predictions on record: ladder P5, entry 6, entries 16, 19-22 (eight in wave 3), g1verify entries 4-6, owner A4 strict (ladder/JOURNAL.md, g1verify/JOURNAL.md, JOURNAL.md); REVIEW-wave3.md section 1 lists them
- [x] **C18** STATUS.md, JOURNAL.md and HANDOFF.md are current
  - status: PASS
  - evidence: STATUS.md, HANDOFF.md rewritten, JOURNAL.md appended, RISKS.md updated by the lead of batch 3 on 2026-11-21
