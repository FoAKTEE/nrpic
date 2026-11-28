# Checklist: F-hills G1

Collected by `harness/bin/nrpic-stage collect F-hills G1` on 2026-11-28T02:09:15Z from `coord/CHARTER.md` (last changed in a61186835) and the brief (sections 13.3 and 13.4).
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
  - evidence: [JUDGEMENT, with reservations] Constraints quantified (nr_first E2, F-20261115-173547-a02af7d, -181434-b9c8916; card smoke F-20261115-174602-c6879fe). Junk: one member E/m = 7e-5 (4e-5 to 2e-4; F-20261120-222808-b65001c, -223018-a5c0838, -223121-c921d2d); three-hole data at P1's spheres: burst 0.40-0.63e-6 M at u of about -33 M, then a steady emission of 5.0-5.4e-8 M per M; window u in [-35, 6] holds 2.3-2.8e-6 M (junk_gauge J4b F-20261121-075600-4480a13; lead L5, L5b F-20261121-155457-5f36517, -155549-4359678). Reservations (OPEN.md 5): l <= 8 only; m/8 binary spirals in numerically; steady part not identified; remeasure at P1b. 2026-11-21 batch 4a. G1 verifier (VERIFIER.md 3.4, F4; run F-20261125-175931-32701e4): window energies 2.73, 2.50, 2.28, 2.36e-6 M at r = 40, 48, 70, 90 M reproduced within 3-9 percent; the four radii agree within 19.8 percent, so criterion (iii)'s "two radii within 20 percent" is MET AT ITS EDGE (batch 25).
- [x] **C8** One complete vacuum passage is done
  - status: PASS
  - evidence: MET IN SUBSTANCE; ONE CLAUSE NOT YET MET AS WRITTEN (batch 35, 2026-11-27, after the verifier's part 2, VERIFIER.md sections 10-17, and the gate review, GATE_REVIEW.md). Scope criterion (iv) (`../G0/SCOPING.md` l. 139-141) asks for the trackers to t = 200 M; the record ends at 186.0 M because Slurm refused the chain's next submission (I/O error, `chain/slurm-5492.out`). Decision 0048 item 2(a): the criterion is not amended; the passage is continued to 200 M: queue entry **q0091** (label F-A2-to200, priority 2, `continue_chain.sh --reopen F-20261124-210400-902c650 31 --extra-input binary_conv/inputs/fastflow_diag.athinput`; predictions D35-1..9 in JOURNAL batch 35, committed in 72543633f before it was queued). Until it has run and a registered reading shows the record to 200 M, this clause is open. The record to 186.0 M: P1b m/16, A (F-20261121-203144-b2cf16b, 0-61.8 M) + A2 (F-20261124-210400-902c650, 61.8-186.0 M; diagnostics from 133.0 M by q0069) joined without a gap (largest step 2^-9 M; overlaps <= 1.25e-9 M, the largest at 104.0-104.4 M, restart round-off; F-20261127-232849-14345be and, with the corrections below, F-20261128-020208-d7c6f1c, fig_b21_a2_state). Outcome (horizon numbers quoted with the summary's residual hrms; 'found' in a status file means the mass rule held, not a converged surface: finding F5): the binary is disrupted between 120 and 133 M; m1 is captured by M: common horizon from 137.5 M (finder 2 found at all 1697 searches 133-186 M; area mass 1.0053 -> 1.1137; Christodoulou mass 1.12291, S/M^2 = 0.2529 at 186 M with hrms 3.4e-4 and mean expansion -0.040, so not converged to the level of the pre-capture upper branch); m1's own surface is found to about 141 M with small mean expansion but hrms 2e-3 to 7.5e-2 (distorted, VERIFIER 17); m2's horizon is found at every search: converged searches (hrms <= 1e-2) 0.12939-0.12964 over 61.8-186 M, while 160.6-179.2 M finder 1 alternates with an unconverged branch (298 searches, 0.12890-0.12918, hrms 0.15-0.23 after 6 flow iterations) which the earlier "0.12954 within 6.4e-4" included; m2 passes M at 8.733 M (134.3 M, trackers) and recedes (17.53 M at 186 M, relative speed 0.374 against an escape speed of 0.378): m2's fate is undecided in coordinates (two-body energy -0.04 to +0.12 units by mass convention, not conserved). The capture's wave reaches only the 40-M sphere before 186 M, with no ring-down recorded (VERIFIER 12). Newton from the same deck ejects m1 and binds m2 (F-20261127-232940-3f652bf). rms H at most 6.19e-5 (135.5 M), 1.51e-5 at 186 M. MeshBlocks of A2 1968-2514 (start and end counts of its 46 segment logs); the 2584 quoted in batch 34 is A's maximum (0-61.8 M, segments 3-4, jobs 4866 and 4875), which the batch-34 reader joined with A2 (F-20261128-020208-d7c6f1c, S6.mb_and_memory); card memory peak 78789 MiB. Failed predictions on record: A2-1 (timing), A2-2, A2-3, A2-4, A2-5's heavy-hole clause, C25-1's tracker clause, C25-3's rate clause, D34-1, D34-2 in part (JOURNAL batches 21, 25, 34). One resolution only (C2 at m/12 stopped at 106.69 M, G2). Finding F1: decided for 86.6-131 M by the summary's hrms (upper branch 1.00422, hrms 9.4e-9 to 3.6e-8, constant to 6.4e-5 on 618 searches of A2; the 62-86.6 M decline, -1.72e-5 per M, and the lower branches 1.00289-1.00394, hrms 1.4e-4 to 6.5e-4, are unconverged surfaces); open only during m1's approach (131-137.4 M), where both classes' hrms rise. Earlier state (batch 25 and before): `JOURNAL.md` batches 21, 25, 34 and `STATUS.md` T4.

## Rulings of the orchestrator on the criteria (coord/DECISIONS; check that they apply to G1)

- [x] **C9** Track F (amends 0005). Mass ratio four for the convergence study and the first scan line; the passage at mass ratio ten follows when the mesh fits. The first passage of a clump binary comes right after the first black-hole passage. (0013)
  - status: PASS
  - evidence: followed: P1 and the convergence plan are at q = 4 (nr_first/inputs/p1_q4.athinput; STATUS.md); q = 10 waits for the mesh and for momenta from a GR parabola (V9a: the q = 10 input turns at 5.77 M in GR); the clump passage (object b) follows the first black-hole passage (core's wave-3a clump-table package)

## Minimum figures at G1 (brief 13.4)

- [x] **C10** Schematic: Updated architecture
  - status: PASS
  - evidence: note/figures/schem_architecture.png updated to the state of core-v0.3 (exists / to be ported / new; multi-puncture data, trackers, finders, chain wrapper, readers, three references), script note/scripts/schem_architecture.py, run F-20261120-222908-4ffcfba (note package); PNG read by the note helper and by the lead on 2026-11-21. Redrawn in batch 35 to the release core-v0.8 (gate review C10, section 6 item 7): the tracker file kept on a continued run and the status file with the found flag of each search are now 'exists'; run F-20261128-020409-a3edb04 (numbers and ledger of the note unchanged), PNG read by the lead; note v2.1
- [x] **C11** Schematic: Data-flow diagram
  - status: PASS
  - evidence: note/figures/schem_dataflow.png (input, chained card segments, output streams, readers, analyses with the references, note), script note/scripts/schem_dataflow.py, run F-20261120-222908-4ffcfba; PNG read by the note helper and by the lead on 2026-11-21. Redrawn in batch 35 to core-v0.8 (tracker file kept on a continued run, resubmission after a preemption, status file with found flag and residual: all 'exists'), run F-20261128-020409-a3edb04, PNG read by the lead
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
- [x] **C18** Verifier subagent (fresh context) wrote VERIFIER.md (decision 0016; VERIFIER_REPORT.md accepted too); every number of the Supplemental Material recomputed from the manifests
  - status: PASS
  - evidence: MET WITH THE GAPS LISTED (batch 35, set from the two verifier parts and the gate review). Part 1 (batch 22, fresh agent; package verifier/, runs F-20261125-175931-32701e4, -180244-25c98a5): the Newtonian reference, the passage to 96.23 M, the mesh members, P1 to 280 M, H1-H4, criterion (iii), four KHSR points; its requests (a)-(d) applied in batch 25. Part 2 (batch 34, another fresh agent; package verifier-tail/, runs F-20261128-003721-95f3c15, -004301-ce51e1f, -004549-2a094fb, -004718-796bd33, -004800-5f93427, -005105-f29eb5a): the passage to 186.0 M with part 1's readers and new readers of the status files, the hrms column, the segment logs and the waves; findings F1 (decided by hrms for 86.6-131 M) and F5 (found is not converged); its requests 16(a)-(f) and comparison 17 (1)-(5) answered in batch 35 (`../REVIEW-wave3.md`, batch 35; C8 above). The gate review (GATE_REVIEW.md, run F-20261128-013351-b85a9a5) reproduced R1-R7 with a reader of its own. The G0 verifier covered ledger tables 1-2 (57 of 57) and K2, K3, K5. Not verified by anyone (stated, not hidden): the Kerr part of F-pre-2 (2402.02178), the EIH package, ledger tables 3-5 except rows 122, 126 (in part), 128, 168, 194, 200-207, P1's remnant spin and radiated energy, S2g's junk scaling, the junk at P1b's spheres, and the record 186-200 M (to be read when q0091 has run). So "every number of the Supplemental Material" is not literally met.
- [x] **C19** Null results and failed runs are on record (manifests and JOURNAL)
  - status: PASS
  - evidence: failed and stopped runs kept with manifests and journal entries: F-20261115-173601-2fae2dc (S3/S2, slot limit), F-20261115-173606-efcbf69 (withdrawn), F-20261115-173719-923135a, F-20261119-143851-47595bd, F-20261115-174959-9e8a361 (stopped), F-20261115-174142-2a79515 (superseded), F-20261115-175542-b49d687; failed predictions on record: nr_first/JOURNAL.md (E1(b), E3 items 1, 2, 5, E4 rerun counts, E7 first-search masses), newton3/JOURNAL.md (Q1, Q3, Q4 bounds), stage/G0/JOURNAL.md (SC0d, SC2, SC6), JOURNAL.md (V4-V7 of wave 1); batch 21: A2-1 (timing), H2 (bands at the second digit), H4 (P1's heavy hole at t <= 0.125 M); batch 25: A2-2 and B25-2 (centre of mass not turned by 133 M), A2-5's heavy-hole clause (1.55e-3 > 1e-3), the batch-21 forecast of the centre of mass's turn before the cap (F-20261126-054946-a21f229, F-20261126-054957-6cdb7cf); the verifier's own failed predictions (VERIFIER.md section 4); batch 34: A2-3 (no member beyond 30 M at 170 M; m1 captured, not bound at 4-8 M), A2-4 (common horizon of m1 and M from 137.5 M), C25-1's tracker clause (0.5 M at 140.55 M, not by 140), C25-3's rate clause (5.2-5.3 M per segment after the merger), D34-1 (F1: both branches found with equal mean expansion), D34-2's clause on finder 0 (117 spurious found surfaces after the merger) (F-20261127-232657-163727d, -232849-14345be, -232940-3f652bf); failed run F-20261127-232531-8d16e2c (reader parsed no status row); A2 and C2 stopped by a Slurm submission I/O error (chain/slurm-5492.out, slurm-5491.out)
- [x] **C20** STATUS.md, JOURNAL.md and HANDOFF.md are current
  - status: PASS
  - evidence: STATUS.md, HANDOFF.md rewritten and a JOURNAL.md entry appended by the lead at the end of batch 35 (2026-11-27)
