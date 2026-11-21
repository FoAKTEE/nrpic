# Checklist: E-stoch-inf G1

Collected by `harness/bin/nrpic-stage collect E-stoch-inf G1` on 2026-11-21T06:44:09Z from `coord/CHARTER.md` (last changed in a6118683) and the brief (sections 13.3 and 13.4).
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
  - evidence: ladder/results/final, final2 (time-matched pairing), floor, a6, a6_64, l5, seed2, a12 and ladder/fig/ (runs EVIDENCE.md 1 and 7); analysis/fig; g1verify/fig (verifier); stage/G1/fig/fig_lead_check.png; stage/review3/fig (lead of batch 2a)
- [x] **C5** Interface documents
  - status: PASS
  - evidence: noise/NOISE_SPEC.md and RNG_REQUIREMENTS.md (track); coord/INTERFACES/ scalar field of core-v0.3; core's tracks/core/interfaces/scalar_field_2.md (branch core/scalar-2, written to SPEC 5.3 and 10; not yet released)

## Track-specific criteria of E-stoch-inf for G1 (9.8 Track E: stochastic inflation (S11, if possible))

- [ ] **C6** The power spectrum of the slow-roll case agrees with the analytic result, super-horizon modes freeze by the criterion of arXiv:2606.14853, the constraints converge
  - status: OPEN
  - evidence: spectrum MET and verified (A2: 1.21e-4 at 256^3 for |n| <= 32, verifier the same; second seed 2.12e-4, 1.208e-4 over typical amplitudes); freezing MET and verified (A3: ratio within 2.4e-6 to 4.6e-6 of full MS, drift 1.4e-4 per e-fold, FLRW-lattice equation -0.052 per e-fold excluded); constraints converge in the sheet's sense, verified (odd part order 5.5-5.96, halving 2.000; even part halving 3.986-4.000, N-independent); but the owner's accepted A4 fails in its strict form in P1's set-up (odd/even up to 745-869 at N = 32-128, 25 at the last time-matched dump of N = 256) and A4' awaits orch's ruling (outbox 20261119T151727Z, repeated 2026-11-21 with the verifier's recommendation). STATUS.md, VERIFIER.md

## Rulings of the orchestrator on the criteria (coord/DECISIONS; check that they apply to G1)

- [x] **C7** Track E. Decision of the feasibility gate, pending the group: continue to G1 and G2 (about two card-hours); the scope of G3 is decided at G2. The lead's choices of `spec/scope/SCOPE.md` section 4 are accepted. (0013)
  - status: PASS
  - evidence: applied: continue to G1 and G2; SCOPE 4 choices used (Courant 0.25, now justified by A6; level 0; thresholds A1-A7 as written, A4 failure kept on record); downgrade (SCOPE 4 item 5) not triggered: A3 passes, 0.503 card-hours per 256^3 SR realisation against 5

## Minimum figures at G1 (brief 13.4)

- [ ] **C8** Schematic: Updated architecture
  - status: OPEN
  - evidence: package `note` of wave 3 (cut by the usage limit on 2026-11-20 14:35 PST, not resumed): note/scripts/schem_architecture.py modified and not committed; no committed updated schematic yet
- [ ] **C9** Schematic: Data-flow diagram
  - status: OPEN
  - evidence: package `note` of wave 3 (cut by the usage limit on 2026-11-20 14:35 PST, not resumed): note/scripts/schem_dataflow.py written, not committed, figure not produced in a registered run
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
- [ ] **C13** Data figures drawn with /zoom-figure-style from registered run outputs, one script per figure, every PNG looked at
  - status: OPEN
  - evidence: style: ladder, verifier and lead figures use copies of harness/style/figstyle.py, every PNG looked at; the verifier has one script per figure (g1verify/scripts/fig_v1.py ... fig_v7.py); package `note` of wave 3 (cut by the usage limit on 2026-11-20 14:35 PST, not resumed): note/scripts/fig_sr_{modes,freezing,constraints,order}.py written, not committed, not run as a registered run
- [ ] **C14** Schematics drawn with /sleep-paper-figure-style: track architecture (exists / to be ported / new) and the gate timeline
  - status: OPEN
  - evidence: package `note` of wave 3 (cut by the usage limit on 2026-11-20 14:35 PST, not resumed): G0 schematics exist; updated architecture, data-flow and timeline scripts modified/new and uncommitted
- [ ] **C15** Working note written with /paper-writing; its manuscript checker passed with --compile
  - status: OPEN
  - evidence: package `note` of wave 3 (cut by the usage limit on 2026-11-20 14:35 PST, not resumed): note/main.tex is the G0 note v0; G1 sections not written; no G1 ledger
- [x] **C16** Verifier subagent (fresh context) wrote VERIFIER.md (decision 0016; VERIFIER_REPORT.md accepted too); every number of the Supplemental Material recomputed from the manifests
  - status: PASS
  - evidence: VERIFIER.md (copy of g1verify/VERIFIER.md): fresh-context helper g1verify, own code from the raw dumps, verdicts V1-V7 committed (db88f631) before it read the track's numbers (c43e050c); runs EVIDENCE.md 6; the lead reran its analyses from the registered outputs (../REVIEW-wave3.md). Its 'every number of the Supplemental Material recomputed' part: no G1 ledger exists yet (note package unfinished), so the ledger recomputation is open with C15
- [x] **C17** Null results and failed runs are on record (manifests and JOURNAL)
  - status: PASS
  - evidence: failed and stopped runs kept with manifests: E-20261115-172521-e098160, -170651-885fc6e, -171628-1737ebe, -171633-f574079, E-20261119-145853-ef835c2; wave 3: E-20261121-030415-22d518b, -031936-16d6ae5, -034609-f573ddc, -063758-d643396 (lead); refuted predictions on record: ladder P5, entry 6, entries 16, 19-22 (eight in wave 3), g1verify entries 4-6, owner A4 strict (ladder/JOURNAL.md, g1verify/JOURNAL.md, JOURNAL.md); REVIEW-wave3.md section 1 lists them
- [x] **C18** STATUS.md, JOURNAL.md and HANDOFF.md are current
  - status: PASS
  - evidence: STATUS.md, HANDOFF.md rewritten, JOURNAL.md appended and RISKS.md updated by the lead of batch 2a on 2026-11-21
