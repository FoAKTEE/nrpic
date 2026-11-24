# Checklist: F-hills G1

Collected by `harness/bin/nrpic-stage collect F-hills G1` on 2026-11-24T14:20:05Z from `coord/CHARTER.md` (last changed in a6118683) and the brief (sections 13.3 and 13.4).
For each item set `status:` to PASS, FAIL or NA (OPEN until judged) and give the evidence: run ids,
figure files, KB locators, commits. `nrpic-stage report` reads this file; the automated checks are
in VERIFY_RESULTS.md (`nrpic-stage verify`), not here.

## Evidence required at every track's G1 (Pre-core baseline; charter 9.2)

- [x] **C1** Baseline results obtainable without the NRPIC coupling
  - status: PASS
  - evidence: Newtonian restricted and full three-body references (newton3; corrected energies of newton3_fix, F-20261115-175232-d399e83, -180351-b8eb386) and the geodesic (HRNA) reference (geodesic_binary), both reproduced against the literature (STATUS.md T1, T2); both run from the P1 start state (E6, F-20261115-174102-ffa764f); vacuum NR runs need no coupling: S3/S2 (F-20261115-173601-2fae2dc), smoke (F-20261115-174602-c6879fe)
- [x] **C2** The analysis pipeline validated on them
  - status: PASS
  - evidence: NR readers nrread.py validated on a synthetic full-Newton trajectory in AthenaK formats with planted failed searches 10/10 (F-20261119-143627-1a84aa5), on core's run A (E3a, F-20261115-182100-613c9c6), passage analysis on synthetic files (E9, F-20261115-183737-49f0a7f); on the real S3/S2/smoke outputs reproduced from the raw files by the lead's own parser (V8, F-20261119-145434-82c05f2). Newtonian/HRNA pipelines against the literature (T1, T2)
- [x] **C3** Interface proposals submitted
  - status: PASS
  - evidence: outbox/20261115T1507Z__to-core__* (input format, pairwise common-horizon trigger, energy diagnostics, two cards or larger blocks), answered in core's dfix-answers (pairwise common horizon done; corrections taken into multi_puncture.md); outbox/20261119T*__to-core__* (tracker files on restart, finder at 4 cells per radius, found flag, damping with three holes)

## Main products of G1 (charter 9.2)

- [x] **C4** Baseline data and figures
  - status: PASS
  - evidence: newton3/figures (fig_skr_curves, fig_bkrs_and_h1, fig_general_pdis_energy, fig_finite_q, fig_energy_definition, fig_passages), geodesic_binary/figures (s1_sepfrac, s1_vinf), nr_first/figures/fig_baselines_p1.png; note figures fig_newton, fig_geodesic, fig_rp_scan, fig_passage; JSON in newton3/results, geodesic_binary/results, nr_first/results
- [x] **C5** Interface documents
  - status: PASS
  - evidence: multi-puncture input written by newton3/scripts/puncture_input.py per coord/INTERFACES/multi_puncture.md section 2 (F's corrections taken in by core, dfix-answers); reader and wrapper interfaces documented in nr_first/README.md (nrread.py, athena_keep_trackers.sh, tree_check.py)

## Track-specific criteria of F-hills for G1 (9.9 Track F: Hills mechanism (S12))

- [x] **C6** F-pre-1 and F-pre-2 reproduce the curves of the literature
  - status: PASS
  - evidence: F-pre-1 met for 0911.1136, 1804.02911 (STATUS.md T1; G0 verifier K2, K3) and 1201.4794 (KHSR, package khsr_note: scan F-20261121-212757-77cdc15, checks F-20261121-213405-6596be1; the lead's rerun repeats all 1268 values, F-20261124-133112-db7d6b8; K1 and K2 rederived by hand, JOURNAL.md batch 11 L-K; figure khsr_note/figures/fig_khsr_ecc.png read). F-pre-2 met for 2404.16270 (verifier K5, F-20261121-032337-9c6d87a, -032325-f58a391) and in part for Kerr 2402.02178 (package kerr; F-20261121-132131-326dfd1, -132817-eacfe46, lead reruns F-20261121-155614-7997653, -155605-7d21f63). Deviations on record (STATUS.md T1, T2). 2026-11-24 batch 11
- [x] **C7** Constraint residuals and junk radiation of the three-puncture data are quantified
  - status: PASS
  - evidence: [JUDGEMENT, with reservations] Constraints quantified (nr_first E2, F-20261115-173547-a02af7d, -181434-b9c8916; card smoke F-20261115-174602-c6879fe). Junk: one member E/m = 7e-5 (4e-5 to 2e-4; F-20261120-222808-b65001c, -223018-a5c0838, -223121-c921d2d); three-hole data at P1's spheres: burst 0.40-0.63e-6 M at u of about -33 M, then a steady emission of 5.0-5.4e-8 M per M; window u in [-35, 6] holds 2.3-2.8e-6 M (junk_gauge J4b F-20261121-075600-4480a13; lead L5, L5b F-20261121-155457-5f36517, -155549-4359678). Reservations (OPEN.md 5): l <= 8 only; m/8 binary spirals in numerically; steady part not identified; remeasure at P1b. 2026-11-21 batch 4a
- [ ] **C8** One complete vacuum passage is done
  - status: FAIL
  - evidence: P1 (F-20261119-150017-b45ec5f): binary merged at 48.8 M (m/8). P1b m/16 (run A, F-20261121-203144-b2cf16b, 11.77 card-hours): reached 61.8 M, members unmerged (s = 2.74 M), A1, A2, A4, A5 met; cut by preemption and closed as stopped. Isolated m/16 pair (R16n + B) turns at 3.12 M at 73.9 M (no merger to 107.85 M; F-20261124-130009-33bef4d), so the passage can be tested: continuation A2 on the cards (JOURNAL.md batch 11, predictions A2-1 to A2-5). 2026-11-24 batch 11

## Rulings of the orchestrator on the criteria (coord/DECISIONS; check that they apply to G1)

- [x] **C9** Track F (amends 0005). Mass ratio four for the convergence study and the first scan line; the passage at mass ratio ten follows when the mesh fits. The first passage of a clump binary comes right after the first black-hole passage. (0013)
  - status: PASS
  - evidence: followed: P1 and the convergence plan are at q = 4 (nr_first/inputs/p1_q4.athinput; STATUS.md); q = 10 waits for the mesh and for momenta from a GR parabola (V9a: the q = 10 input turns at 5.77 M in GR); the clump passage (object b) follows the first black-hole passage (core's wave-3a clump-table package)

## Minimum figures at G1 (brief 13.4)

- [x] **C10** Schematic: Updated architecture
  - status: PASS
  - evidence: note/figures/schem_architecture.png updated to the state of core-v0.3 (exists / to be ported / new; multi-puncture data, trackers, finders, chain wrapper, readers, three references), script note/scripts/schem_architecture.py, run F-20261120-222908-4ffcfba (note package); PNG read by the note helper and by the lead on 2026-11-21. Drawn as of core-v0.3: two items it marks 'to be ported' (common horizon of one pair, mass-scaled shift damping) are in release core-v0.4 (`punc_pair_a_<n>`, `shift_eta_profile`); to update on the note's resume
- [x] **C11** Schematic: Data-flow diagram
  - status: PASS
  - evidence: note/figures/schem_dataflow.png (input, chained card segments, output streams, readers, analyses with the references, note), script note/scripts/schem_dataflow.py, run F-20261120-222908-4ffcfba; PNG read by the note helper and by the lead on 2026-11-21
- [x] **C12** Data figure: Baseline results
  - status: PASS
  - evidence: note/figures/fig_newton.png, fig_geodesic.png, fig_rp_scan.png, fig_passage.png (scripts note/scripts/fig_*.py, run F-20261115-180609-abc9f6e); nr_first/figures/fig_baselines_p1.png (F-20261115-174102-ffa764f); all looked at (note/JOURNAL.md; lead review)
- [x] **C13** Data figure: Validation figures for the analysis pipeline
  - status: PASS
  - evidence: nr_first/figures/fig_test_nrread_synthetic.png (reader test), fig_e10a_s3_s2_compare.png (comparison script on S3/S2), fig_e11_tree_check.png (tree model against restart trees), fig_e3_single_gauge.png (rerun F-20261119-145619-8246322), fig_e7_p1smoke.png; lead fig_review_nr.png (F-20261119-145434-82c05f2); all looked at by the lead (REVIEW-wave2.md). Drawn by the package scripts with python/nrpic/figstyle.py, not yet note figures

## Package (brief 13.3, decision 0012; judged by the session)

- [x] **C14** Package documents of decision 0012: STAGE_REPORT.md (nrpic-stage report), EVIDENCE.md, OPEN.md and this CHECKLIST.md in the stage directory; REVIEW.md where the lead rechecked helpers; the scoping text in SCOPE.md or SCOPING.md beside them or in the scope directory, named in the report (no REPORT.md needed)
  - status: PASS
  - evidence: STAGE_REPORT.md (nrpic-stage report), EVIDENCE.md, OPEN.md, CHECKLIST.md, REVIEW.md (points to ../REVIEW-wave2.md and SCOPING.md section 10); the criterion-by-criterion text is STATUS.md beside them, the scoping text ../G0/SCOPING.md, both named in the report
- [x] **C15** Data figures drawn with /zoom-figure-style from registered run outputs, one script per figure, every PNG looked at
  - status: PASS
  - evidence: note v2 (carried from khsr_note into note/ in batch 11): every data figure has its script in note/scripts (fig_elliptic.py, fig_binary.py, fig_p1_end.py new) and reads registered runs (figure run F-20261121-214141-256f945; the prediction of that run met: all PNGs identical, khsr_note/JOURNAL.md); figures looked at by the helper and, for pages 13-16, by the lead (rebuild in scratch, batch 11). nrpic-stage verify reruns them
- [x] **C16** Schematics drawn with /sleep-paper-figure-style: track architecture (exists / to be ported / new) and the gate timeline
  - status: PASS
  - evidence: note/figures/schem_architecture.png and schem_timeline.png with note/scripts/paperfig.py (copy equal to harness/style/SHA256SUMS); their G1 updates are C10, C11
- [x] **C17** Working note written with /paper-writing; its manuscript checker passed with --compile
  - status: PASS
  - evidence: note/main.tex v2 (24 pages): latexmk compiles without an undefined reference and check_manuscript.py with the track's --forbid list is clean except the accepted run ids of the appendix ledger and one journal locator in the ledger (khsr_note package; repeated by the lead in a scratch rebuild, batch 11: 24 pages, 0 undefined). Reviewer step of the paper-writing procedure open (OPEN.md item 3)
- [ ] **C18** Verifier subagent (fresh context) wrote VERIFIER.md (decision 0016; VERIFIER_REPORT.md accepted too); every number of the Supplemental Material recomputed from the manifests
  - status: OPEN
  - evidence: no verifier of the G1 material yet; to be asked when the passage A2 is done (OPEN.md item 2, with the list of material)
- [x] **C19** Null results and failed runs are on record (manifests and JOURNAL)
  - status: PASS
  - evidence: failed and stopped runs kept with manifests and journal entries: F-20261115-173601-2fae2dc (S3/S2, slot limit), F-20261115-173606-efcbf69 (withdrawn), F-20261115-173719-923135a, F-20261119-143851-47595bd, F-20261115-174959-9e8a361 (stopped), F-20261115-174142-2a79515 (superseded), F-20261115-175542-b49d687; failed predictions on record: nr_first/JOURNAL.md (E1(b), E3 items 1, 2, 5, E4 rerun counts, E7 first-search masses), newton3/JOURNAL.md (Q1, Q3, Q4 bounds), stage/G0/JOURNAL.md (SC0d, SC2, SC6), JOURNAL.md (V4-V7 of wave 1)
- [x] **C20** STATUS.md, JOURNAL.md and HANDOFF.md are current
  - status: PASS
  - evidence: STATUS.md, HANDOFF.md rewritten and a JOURNAL.md entry appended by the lead at the end of batch 11 (2026-11-24)
