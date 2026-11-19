# Checklist: E-stoch-inf G1

Collected by `harness/bin/nrpic-stage collect E-stoch-inf G1` on 2026-11-19T15:09:46Z from `coord/CHARTER.md` (last changed in a6118683) and the brief (sections 13.3 and 13.4).
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
  - evidence: ladder/results/final, floor, a6, a12 and ladder/fig/ (runs EVIDENCE.md 1); analysis/fig; stage/G1/fig/fig_lead_check.png
- [x] **C5** Interface documents
  - status: PASS
  - evidence: noise/NOISE_SPEC.md and RNG_REQUIREMENTS.md (track); coord/INTERFACES/ scalar field of core-v0.3; core's tracks/core/interfaces/scalar_field_2.md (branch core/scalar-2, written to SPEC 5.3 and 10; not yet released)

## Track-specific criteria of E-stoch-inf for G1 (9.8 Track E: stochastic inflation (S11, if possible))

- [ ] **C6** The power spectrum of the slow-roll case agrees with the analytic result, super-horizon modes freeze by the criterion of arXiv:2606.14853, the constraints converge
  - status: OPEN
  - evidence: spectrum MET (A2: 1.21e-4 at 256^3 for |n| <= 32, E-20261115-172618-f948386; lead 8.76e-5 on L32p); freezing MET (A3: drift 1.4e-4 per e-fold against 2.5e-3, FLRW lattice excluded by 350); constraints converge in the sheet's sense (odd part order 4.2-5.9, H0 order 4, second-order part independent of N within 2.2 percent; E-20261115-194633-9e04ed8, E-20261119-142713-32c883a), but the owner's accepted A4 fails in its strict form in P1's set-up at every N (odd part up to 385-870 x even part from ln(N/8) e-folds) and A5's floor was defined after the data: ruling on A4'/A5' asked of orch (outbox 20261119). STATUS.md

## Rulings of the orchestrator on the criteria (coord/DECISIONS; check that they apply to G1)

- [x] **C7** Track E. Decision of the feasibility gate, pending the group: continue to G1 and G2 (about two card-hours); the scope of G3 is decided at G2. The lead's choices of `spec/scope/SCOPE.md` section 4 are accepted. (0013)
  - status: PASS
  - evidence: applied: continue to G1 and G2; SCOPE 4 choices used (Courant 0.25, now justified by A6; level 0; thresholds A1-A7 as written, A4 failure kept on record); downgrade (SCOPE 4 item 5) not triggered: A3 passes, 0.503 card-hours per 256^3 SR realisation against 5

## Minimum figures at G1 (brief 13.4)

- [ ] **C8** Schematic: Updated architecture
  - status: OPEN
  - evidence: not drawn: note/figures/schem_architecture.png shows the G0 state (836ac86); the initial slice, mode tables, constraint record, R^NR, per-mode and freezing analysis now exist (core/scalar-2, ladder/, analysis/)
- [ ] **C9** Schematic: Data-flow diagram
  - status: OPEN
  - evidence: not drawn
- [x] **C10** Data figure: Baseline results
  - status: PASS
  - evidence: ladder/fig/final/fig_spectrum.png, fig_a2_modes.png, fig_a3_freezing.png (looked at by the lead 2026-11-19; regenerated pixel-identically in run E-20261119-150842-ca70d37)
- [x] **C11** Data figure: Validation figures for the analysis pipeline
  - status: PASS
  - evidence: analysis/fig/fig_t2_extraction.png, fig_plane_constraint_ratios.png; stage/G1/fig/fig_lead_check.png (script stage/G1/scripts/lead_check.py, run E-20261119-150238-b81e33f); all looked at

## Package (brief 13.3, decision 0012; judged by the session)

- [x] **C12** Package documents of decision 0012: STAGE_REPORT.md (nrpic-stage report), EVIDENCE.md, OPEN.md and this CHECKLIST.md in the stage directory; REVIEW.md where the lead rechecked helpers; the scoping text in SCOPE.md or SCOPING.md beside them or in the scope directory, named in the report (no REPORT.md needed)
  - status: PASS
  - evidence: STAGE_REPORT.md (nrpic-stage report), EVIDENCE.md, OPEN.md, CHECKLIST.md, REVIEW.md (pointer to ../REVIEW-wave2.md), STATUS.md (criteria table); scoping text spec/scope/SCOPE.md
- [ ] **C13** Data figures drawn with /zoom-figure-style from registered run outputs, one script per figure, every PNG looked at
  - status: OPEN
  - evidence: style: ladder and lead figures use a copy of harness/style/figstyle.py; every PNG looked at; but the ladder's six final figures come from one script (ladder/scripts/make_figures.py), not one script per figure, and no G1 note figure exists yet
- [ ] **C14** Schematics drawn with /sleep-paper-figure-style: track architecture (exists / to be ported / new) and the gate timeline
  - status: OPEN
  - evidence: the G0 schematics (note/scripts/schem_*.py, paperfig.py) exist; updated G1 versions not drawn (C8, C9)
- [ ] **C15** Working note written with /paper-writing; its manuscript checker passed with --compile
  - status: OPEN
  - evidence: note/main.tex is the G0 note v0; G1 sections not written
- [ ] **C16** Verifier subagent (fresh context) wrote VERIFIER.md (decision 0016; VERIFIER_REPORT.md accepted too); every number of the Supplemental Material recomputed from the manifests
  - status: OPEN
  - evidence: no fresh-context verifier of the G1 material (decision 0016 item 4); stage/G0/VERIFIER.md covered the plan; the lead's re-check (../REVIEW-wave2.md) is not a verifier
- [x] **C17** Null results and failed runs are on record (manifests and JOURNAL)
  - status: PASS
  - evidence: failed and stopped runs kept with manifests: E-20261115-172521-e098160, -170651-885fc6e (literal run directory), -171628-1737ebe (failed |M| prediction), -171633-f574079 (final tail), E-20261119-145853-ef835c2 (lead's rerun, I/O bound); refuted predictions on record: ladder P5 and entry 6's attribution, analysis PS5 and T2a, verifier V6/V7/V2b items, owner A4 strict (ladder/JOURNAL.md, analysis/JOURNAL.md, stage/G0/JOURNAL.md, JOURNAL.md)
- [x] **C18** STATUS.md, JOURNAL.md and HANDOFF.md are current
  - status: PASS
  - evidence: STATUS.md, HANDOFF.md rewritten and JOURNAL.md appended by the lead on 2026-11-19
