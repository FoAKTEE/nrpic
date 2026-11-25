# Stage report: F-hills G1

Date: 2026-11-25 · branch `track/F-hills` at `4316c1855672` · checklist
`tracks/F-hills/stage/G1/CHECKLIST.md` (from `nrpic-stage collect`)

## Verdict

**FAIL**. Tag: `stage/F-hills/G1-fail-20261125` (created and pushed by the orchestrator after review, decision 0003).

- 2 checklist items not PASS or NA: C8 FAIL, C18 OPEN
- verify reported FAIL: runs
- no VERIFIER.md (step 7: verifier subagent; decision 0016 item 1, VERIFIER_REPORT.md accepted too)

## Package documents (decision 0012)

| Document | State |
|---|---|
| `stage/G1/STAGE_REPORT.md` | present |
| `stage/G1/EVIDENCE.md` | present |
| `stage/G1/OPEN.md` | present |
| `stage/G1/CHECKLIST.md` | present |
| `stage/G1/VERIFIER.md` (verifier's report) | MISSING (VERIFIER.md, decision 0016; VERIFIER_REPORT.md accepted too) |
| `stage/G1/REVIEW.md` | present |
| scoping text | `novelty/scope/SCOPE.md` |

## Criteria (coord/CHARTER.md, gate G1 of this track)

| # | Criterion | Evidence (run id, figure, KB locator) | Result |
|---|---|---|---|
| C1 | Baseline results obtainable without the NRPIC coupling | Newtonian restricted and full three-body references (newton3; corrected energies of newton3_fix, F-20261115-175232-d399e83, -180351-b8eb386) and the geodesic (HRNA) reference (geodesic_binary), both reproduced against the literature (STATUS.md T1, T2); both run from the P1 start state (E6, F-20261115-174102-ffa764f); vacuum NR runs need no coupling: S3/S2 (F-20261115-173601-2fae2dc), smoke (F-20261115-174602-c6879fe) | PASS |
| C2 | The analysis pipeline validated on them | NR readers nrread.py validated on a synthetic full-Newton trajectory in AthenaK formats with planted failed searches 10/10 (F-20261119-143627-1a84aa5), on core's run A (E3a, F-20261115-182100-613c9c6), passage analysis on synthetic files (E9, F-20261115-183737-49f0a7f); on the real S3/S2/smoke outputs reproduced from the raw files by the lead's own parser (V8, F-20261119-145434-82c05f2). Newtonian/HRNA pipelines against the literature (T1, T2) | PASS |
| C3 | Interface proposals submitted | outbox/20261115T1507Z__to-core__* (input format, pairwise common-horizon trigger, energy diagnostics, two cards or larger blocks), answered in core's dfix-answers (pairwise common horizon done; corrections taken into multi_puncture.md); outbox/20261119T*__to-core__* (tracker files on restart, finder at 4 cells per radius, found flag, damping with three holes) | PASS |
| C4 | Baseline data and figures | newton3/figures (fig_skr_curves, fig_bkrs_and_h1, fig_general_pdis_energy, fig_finite_q, fig_energy_definition, fig_passages), geodesic_binary/figures (s1_sepfrac, s1_vinf), nr_first/figures/fig_baselines_p1.png; note figures fig_newton, fig_geodesic, fig_rp_scan, fig_passage; JSON in newton3/results, geodesic_binary/results, nr_first/results | PASS |
| C5 | Interface documents | multi-puncture input written by newton3/scripts/puncture_input.py per coord/INTERFACES/multi_puncture.md section 2 (F's corrections taken in by core, dfix-answers); reader and wrapper interfaces documented in nr_first/README.md (nrread.py, athena_keep_trackers.sh, tree_check.py) | PASS |
| C6 | F-pre-1 and F-pre-2 reproduce the curves of the literature | F-pre-1 met for 0911.1136, 1804.02911 (STATUS.md T1; G0 verifier K2, K3) and 1201.4794 (KHSR, package khsr_note: scan F-20261121-212757-77cdc15, checks F-20261121-213405-6596be1; the lead's rerun repeats all 1268 values, F-20261124-133112-db7d6b8; K1 and K2 rederived by hand, JOURNAL.md batch 11 L-K; figure khsr_note/figures/fig_khsr_ecc.png read). F-pre-2 met for 2404.16270 (verifier K5, F-20261121-032337-9c6d87a, -032325-f58a391) and in part for Kerr 2402.02178 (package kerr; F-20261121-132131-326dfd1, -132817-eacfe46, lead reruns F-20261121-155614-7997653, -155605-7d21f63). Deviations on record (STATUS.md T1, T2). 2026-11-24 batch 11 | PASS |
| C7 | Constraint residuals and junk radiation of the three-puncture data are quantified | [JUDGEMENT, with reservations] Constraints quantified (nr_first E2, F-20261115-173547-a02af7d, -181434-b9c8916; card smoke F-20261115-174602-c6879fe). Junk: one member E/m = 7e-5 (4e-5 to 2e-4; F-20261120-222808-b65001c, -223018-a5c0838, -223121-c921d2d); three-hole data at P1's spheres: burst 0.40-0.63e-6 M at u of about -33 M, then a steady emission of 5.0-5.4e-8 M per M; window u in [-35, 6] holds 2.3-2.8e-6 M (junk_gauge J4b F-20261121-075600-4480a13; lead L5, L5b F-20261121-155457-5f36517, -155549-4359678). Reservations (OPEN.md 5): l <= 8 only; m/8 binary spirals in numerically; steady part not identified; remeasure at P1b. 2026-11-21 batch 4a | PASS |
| C8 | One complete vacuum passage is done | NOT MET (PARTIAL). P1 (F-20261119-150017-b45ec5f): binary merged at 48.8 M (m/8; tracker s < 0.1 M at 48.79 M, common horizon accepted at 48.81 M by the failure signature, made without <fastflow> diagnostics: F-20261125-170632-5aa9786). P1b m/16: A (F-20261121-203144-b2cf16b, 11.77 card-hours, 0-61.8 M) + A2 (F-20261124-210400-902c650, chain q0001, 5.64 card-hours to 2026-11-25 06:28 PST, still running: next segment Slurm 5294 pending while the cards are held) joined to 96.23 M: tracker copies cover 0-96.23 M without a gap, recomputed stretches agree to 1e-12 M, horizon summaries, history and waveforms appended without loss (batch 21, F-20261125-170453-1175d44, fig_b21_a2_state). The pair passed its closest approach s = 2.11 M at 76.4 M without merging (A2-1 timing REFUTED: band 63-75 M); centre of mass 13.06 M from M at 96.25 M and closing at 0.24 M per M, so the passage's pericentre and the separation are still ahead (A2-2, A2-3 open; passage reader F-20261125-170646-6dd4ae4). Needs A2 to at least 170 M. | FAIL |
| C9 | Track F (amends 0005). Mass ratio four for the convergence study and the first scan line; the passage at mass ratio ten follows when the mesh fits. The first passage of a clump binary comes right after the first black-hole passage. (0013) | followed: P1 and the convergence plan are at q = 4 (nr_first/inputs/p1_q4.athinput; STATUS.md); q = 10 waits for the mesh and for momenta from a GR parabola (V9a: the q = 10 input turns at 5.77 M in GR); the clump passage (object b) follows the first black-hole passage (core's wave-3a clump-table package) | PASS |
| C10 | Schematic: Updated architecture | note/figures/schem_architecture.png updated to the state of core-v0.3 (exists / to be ported / new; multi-puncture data, trackers, finders, chain wrapper, readers, three references), script note/scripts/schem_architecture.py, run F-20261120-222908-4ffcfba (note package); PNG read by the note helper and by the lead on 2026-11-21. Drawn as of core-v0.3: two items it marks 'to be ported' (common horizon of one pair, mass-scaled shift damping) are in release core-v0.4 (`punc_pair_a_<n>`, `shift_eta_profile`); to update on the note's resume | PASS |
| C11 | Schematic: Data-flow diagram | note/figures/schem_dataflow.png (input, chained card segments, output streams, readers, analyses with the references, note), script note/scripts/schem_dataflow.py, run F-20261120-222908-4ffcfba; PNG read by the note helper and by the lead on 2026-11-21 | PASS |
| C12 | Data figure: Baseline results | note/figures/fig_newton.png, fig_geodesic.png, fig_rp_scan.png, fig_passage.png (scripts note/scripts/fig_*.py, run F-20261115-180609-abc9f6e); nr_first/figures/fig_baselines_p1.png (F-20261115-174102-ffa764f); all looked at (note/JOURNAL.md; lead review) | PASS |
| C13 | Data figure: Validation figures for the analysis pipeline | nr_first/figures/fig_test_nrread_synthetic.png (reader test), fig_e10a_s3_s2_compare.png (comparison script on S3/S2), fig_e11_tree_check.png (tree model against restart trees), fig_e3_single_gauge.png (rerun F-20261119-145619-8246322), fig_e7_p1smoke.png; lead fig_review_nr.png (F-20261119-145434-82c05f2); all looked at by the lead (REVIEW-wave2.md). Drawn by the package scripts with python/nrpic/figstyle.py, not yet note figures | PASS |
| C14 | Package documents of decision 0012: STAGE_REPORT.md (nrpic-stage report), EVIDENCE.md, OPEN.md and this CHECKLIST.md in the stage directory; REVIEW.md where the lead rechecked helpers; the scoping text in SCOPE.md or SCOPING.md beside them or in the scope directory, named in the report (no REPORT.md needed) | STAGE_REPORT.md (nrpic-stage report), EVIDENCE.md, OPEN.md, CHECKLIST.md, REVIEW.md (points to ../REVIEW-wave2.md and SCOPING.md section 10); the criterion-by-criterion text is STATUS.md beside them, the scoping text ../G0/SCOPING.md, both named in the report | PASS |
| C15 | Data figures drawn with /zoom-figure-style from registered run outputs, one script per figure, every PNG looked at | note v2 (carried from khsr_note into note/ in batch 11): every data figure has its script in note/scripts (fig_elliptic.py, fig_binary.py, fig_p1_end.py new) and reads registered runs (figure run F-20261121-214141-256f945; the prediction of that run met: all PNGs identical, khsr_note/JOURNAL.md); figures looked at by the helper and, for pages 13-16, by the lead (rebuild in scratch, batch 11). nrpic-stage verify reruns them | PASS |
| C16 | Schematics drawn with /sleep-paper-figure-style: track architecture (exists / to be ported / new) and the gate timeline | note/figures/schem_architecture.png and schem_timeline.png with note/scripts/paperfig.py (copy equal to harness/style/SHA256SUMS); their G1 updates are C10, C11 | PASS |
| C17 | Working note written with /paper-writing; its manuscript checker passed with --compile | note/main.tex v2 (24 pages): latexmk compiles without an undefined reference and check_manuscript.py with the track's --forbid list is clean except the accepted run ids of the appendix ledger and one journal locator in the ledger (khsr_note package; repeated by the lead in a scratch rebuild, batch 11: 24 pages, 0 undefined). Reviewer step of the paper-writing procedure open (OPEN.md item 3) | PASS |
| C18 | Verifier subagent (fresh context) wrote VERIFIER.md (decision 0016; VERIFIER_REPORT.md accepted too); every number of the Supplemental Material recomputed from the manifests | no verifier of the G1 material yet; to be asked when the passage A2 is done (OPEN.md item 2, with the list of material) | OPEN |
| C19 | Null results and failed runs are on record (manifests and JOURNAL) | failed and stopped runs kept with manifests and journal entries: F-20261115-173601-2fae2dc (S3/S2, slot limit), F-20261115-173606-efcbf69 (withdrawn), F-20261115-173719-923135a, F-20261119-143851-47595bd, F-20261115-174959-9e8a361 (stopped), F-20261115-174142-2a79515 (superseded), F-20261115-175542-b49d687; failed predictions on record: nr_first/JOURNAL.md (E1(b), E3 items 1, 2, 5, E4 rerun counts, E7 first-search masses), newton3/JOURNAL.md (Q1, Q3, Q4 bounds), stage/G0/JOURNAL.md (SC0d, SC2, SC6), JOURNAL.md (V4-V7 of wave 1); batch 21: failed predictions A2-1 (timing), H2 (bands at the second digit), H4 (P1's heavy hole beyond 1 percent at t <= 0.125 M) in JOURNAL; horizon recheck of decision 0040 item 3: F-20261125-170540-aa39bea, F-20261125-170632-5aa9786 (no run of this track has the finder's status file) | PASS |
| C20 | STATUS.md, JOURNAL.md and HANDOFF.md are current | STATUS.md, HANDOFF.md rewritten and a JOURNAL.md entry appended by the lead at the end of batch 11 (2026-11-24) | PASS |

## Re-verification on a clean checkout (`nrpic-stage verify`)

`nrpic-stage verify` on 2026-11-25T17:12:40Z, clean export of `4316c1855672`: **FAIL**. Details: `VERIFY_RESULTS.md`.

| Check | Result | Message |
|---|---|---|
| clean | PASS | worktree clean (outside the stage directory being assembled) |
| sync | PASS | main is merged into the branch |
| export | PASS | clean export of 4316c1855672 (HEAD) in /data/haiyangw/nrpic/scratch/F-hills/tmp/stage-verify/F-hills-G1-4316c18-20261125T171144Z/tree |
| size | PASS | no committed file of the track above 5 MB |
| note | PASS | tracks/<ID>/note/main.tex present |
| package | PASS | EVIDENCE.md, OPEN.md, CHECKLIST.md present (decision 0012); scoping text: novelty/scope/SCOPE.md; REVIEW.md present; no verifier's report yet (VERIFIER.md, decision 0016) |
| note-pdf | PASS | note/main.pdf committed after the last .tex change |
| style | PASS | 2 style copies equal harness/style/SHA256SUMS (czstyle.py, paperfig.py) |
| fig-script | PASS | 15 figures, each with its script |
| min-figs | PASS | 3 schematics and 12 data figures (brief 13.4 asks at least 2 and 1 at G1) |
| runs | FAIL | 1 of 258 runs have problems |
| run-notes | WARN | 78 runs read with defaults or not fully re-verifiable (nrpic-run lint) |
| checksums | WARN | output checksums not re-verified (--no-checksums) |
| status | PASS | STATUS.md has 46 lines |
| rerun | PASS | 15 of 15 scripts and commands ran cleanly in the export |
| compare | PASS | 42 regenerated files compared with the committed ones; 0 differ beyond tolerance (rtol 1e-06, atol 1e-12, PNG rms 0.005) |
| regenerate | PASS | all 30 committed figure files regenerated |

## Figures

| File | Script | Kind (data / schematic) | Looked at (PNG read) |
|---|---|---|---|
| note/figures/fig_binary.* | note/scripts/fig_binary.py | data | to be confirmed by the session |
| note/figures/fig_constraints.* | note/scripts/fig_constraints.py | data | to be confirmed by the session |
| note/figures/fig_cost.* | note/scripts/fig_cost.py | data | to be confirmed by the session |
| note/figures/fig_elliptic.* | note/scripts/fig_elliptic.py | data | to be confirmed by the session |
| note/figures/fig_geodesic.* | note/scripts/fig_geodesic.py | data | to be confirmed by the session |
| note/figures/fig_newton.* | note/scripts/fig_newton.py | data | to be confirmed by the session |
| note/figures/fig_p1_end.* | note/scripts/fig_p1_end.py | data | to be confirmed by the session |
| note/figures/fig_passage.* | note/scripts/fig_passage.py | data | to be confirmed by the session |
| note/figures/fig_rp_scan.* | note/scripts/fig_rp_scan.py | data | to be confirmed by the session |
| note/figures/fig_single.* | note/scripts/fig_single.py | data | to be confirmed by the session |
| note/figures/fig_smoke.* | note/scripts/fig_smoke.py | data | to be confirmed by the session |
| note/figures/fig_tree.* | note/scripts/fig_tree.py | data | to be confirmed by the session |
| note/figures/schem_architecture.* | note/scripts/schem_architecture.py | schematic | to be confirmed by the session |
| note/figures/schem_dataflow.* | note/scripts/schem_dataflow.py | schematic | to be confirmed by the session |
| note/figures/schem_timeline.* | note/scripts/schem_timeline.py | schematic | to be confirmed by the session |

## Verifier report

MISSING: the verifier subagent has not reported (`stage/G1/VERIFIER.md`, decision 0016).

## Null results and failed runs

- `F-20261115-173106-57c4b4c`: stopped (exit -15), nr_first E1: MeshBlock counts of the q = 4 three-black-hole data at m/4, m/8, m/16 and of the single-puncture input at m/8, m/16 after the wave-zone refinement (16 cycles)
- `F-20261115-173112-a9e18a3`: stopped (exit -15), nr_first E2 (C0): Hamiltonian residual of the q = 4 three-black-hole data at t = 0, corrections approx/none at m/4, m/8, m/16 and plain sum at m/8; first tracker and horizon rows (one cycle, m/8 approx)
- `F-20261115-173543-29e87e8`: stopped (exit -15), nr_first E1: MeshBlock counts of the q = 4 three-black-hole data at m/4, m/8, m/16 and of the single-puncture input at m/8, m/16 after the wave-zone refinement (16 cycles)
- `F-20261115-173601-2fae2dc`: failed (exit 1), nr_first E3: single Bowen-York puncture P/m = 0.25, cells m/8, 90 m; S3 eta m = 2, S2 eta m = 0.25 (light member of the q = 4 passage): junk energy, tracker speed, horizon-mass drift
- `F-20261115-173606-efcbf69`: stopped (exit 1), nr_first E3: single Bowen-York puncture P/m = 0.25, cells m/16, 90 m, eta m = 2 (S1): junk energy at the higher resolution, horizon-mass drift
- `F-20261115-173719-923135a`: failed (exit 1), nr_first E4 test 1: readers of trackers, horizons and member energies on a synthetic full-Newton q = 4 trajectory written in AthenaK formats with a restart overlap
- `F-20261115-173930-deef41a`: failed (exit 1), nr_first E5: tracker files across a restart in the same directory (truncation in AthenaK; wrapper athena_keep_trackers.sh; merging reader), processors, small mesh
- `F-20261115-174432-291868f`: failed (exit 1), nr_first E2: c0_constraints.py on the approx m/8 case of C0 (script check, partial)
- `F-20261115-174959-9e8a361`: failed (exit -15), newton3 finite-q rerun with corrected member energies (M/m=10,30,100,1000; coplanar and isotropic; old definition kept in the same run)
- `F-20261115-175542-b49d687`: failed (exit 1), second check SC0 (a-c): self-tests of the independent Newton and HRNA integrators (geodesic invariants, Kepler, full three-body conservation)
- `F-20261115-181805-f9c3473`: failed (exit 1), nr_first E4 test 3: readers on the first tracker and horizon rows of the q = 4 three-black-hole data (C0, approx at m/8, processors, one cycle)
- `F-20261119-143503-3cd3592`: failed (exit 1), eih T0, T2, T3: Newtonian limit and 2404 restricted form, two-body periastron advance and period against 1805.07240, conservation of the 1PN integrals and its scaling in the q = 10 Hills encounter
- `F-20261119-143507-d74f101`: failed (exit 1), nr_first E4 test 3 on the card output of the P1 smoke
- `F-20261119-143632-0f6e57d`: failed (exit 1), nr_first E4 test single rerun with the fixed horizon reader
- `F-20261119-143633-dfd3607`: failed (exit 1), nr_first E4 test three rerun with the fixed horizon reader
- `F-20261119-143638-83ce321`: failed (exit 1), eih T4: test-mass parabolic orbits, EIH against exact Schwarzschild (swept angle, its L derivative, pericentre, capture): where 1PN stops being trustworthy
- `F-20261119-150157-424bab2`: stopped (exit -15), eih far-release line, release-radius test: EIH only, release at 20 r_t (1PN-circular binary), q = 10 and 4, both senses, 360 phases
- `F-20261119-150159-4a27aa2`: stopped (exit -15), eih far-release line, release-radius test: EIH only, release at 80 r_t (1PN-circular binary), q = 10 and 4, both senses, 360 phases
- `F-20261120-222810-e408386`: failed (exit 134), g2mesh G2M-2 (G2 preparation): card memory and rate of P1's m/16 mesh at 16^3 with 3000 slots; memory per 32^3 slot and rate per cell at 32^3 against 16^3 on core's three-hole mesh with 7 levels; P1's m/8 mesh at 32^3 (predicted out of memory)
- `F-20261120-223314-b1b64fa`: failed (exit 1), junk_gauge J4a: Newtonian point-mass track of P1 and its quadrupole luminosity (time profile of the physical emission, for the junk window)
- `F-20261121-030146-34ad97e`: failed (exit -15), verify_g0 R4: own pericentre scan, 180 phases, Newton from 10 r_t to 4 r_t then full Newton, HRNA hand-off and HRNA with a GR-matched centre of mass (K13, ledger pericentre rows)
- `F-20261121-030701-734c74b`: failed (exit -15), verify_g0 R7: own HRNA at the set-up of 2404.16270 (r0 = 50 r_t, Schwarzschild parabola), beta = 3 and 10, both senses, 200 phases (K5)
- `F-20261121-031930-a640847`: failed (exit -15), verify_g0 R4c: remaining cases of the pericentre scan in parallel to R4 (q = 4 r_p = 9.82, 16), 180 phases (K13)
- `F-20261121-032150-8309634`: failed (exit -15), verify_g0 R10: hypothesis H-u (Newtonian velocities read as u^i in the HRNA hand-off), q = 10 r_p = 8, 12, 13, 180 phases, step cap 300000 (K13)
- `F-20261121-034441-f211f65`: failed (exit -15), verify_g0 R4e: pericentre scan q = 4 r_p = 16 with a step cap of 200000 per phase, 180 phases (K13)
- `F-20261121-131555-91aa063`: failed (exit 1), kerr R3: HRNA spurious self-acceleration of a moving binary in flat space (reproduction of F-20261115-175620-df20ffe, scan in V, a0/mb, q, psi), and the CM pericentre shift of 2404 encounters it causes
- `F-20261121-203144-b2cf16b`: stopped (exit 1), P1b (run A of lead batch 5): Hills passage q = 4 as P1 with the members at m/16 (R16n), tlim 200, 31 segments; rule P1b-D clause D1 held (F-20261121-202021-3c4321e)
- `F-20261121-203156-03efdd3`: stopped (exit 1), R16n extension (run B of lead batch 5): P1's binary alone at m/16 continued from R16n restart 7 (t = 23.34 M) to tlim 120, 13 segments; control of P1b and m/16 rung of the binary ladder; separates an eccentric start state from an inspiral
- `F-20261121-203247-961801d`: stopped (exit 1), P1b at m/12 (run C of lead batch 5): the passage of P1b at the second member resolution (R12 = R16n alone within 0.002 M), tlim 200, 25 segments; held until run B (R16n extension) has ended, released by binary_conv/scripts/seq_release.sh
- `F-20261124-135408-1e6db58`: stopped (exit 1), B2: binary alone at m/16 continued from B's restart 34 (t = 107.85 M) to tlim 140 (next apocentre, decay per orbit), restart files every 1 M (lead batch 11, prediction in JOURNAL)
- `F-20261124-141118-fbc6419`: stopped (exit 1), A2: passage P1b at m/16 continued from A's restart 23 (t = 61.80 M) to tlim 200, restart files every 1 M (lead batch 11, predictions A2-1 to A2-5 in JOURNAL)
- `F-20261124-141842-d5263e9`: stopped (exit 1), C2: passage P1b at m/12 continued from C's restart 6 (t = 20.0 M) to tlim 200, restart files every 1.5 M; held by the sequencer until B2 ends (lead batch 11, predictions in JOURNAL)
- `F-hills-20261115-045124-ae6bca8`: failed (exit None), Re-derive and check the scale estimate of brief line 275 (tidal radius in r_g, plunge bound, Peters time, passage times, Newtonian disruption window, published NR three-body configurations)
- `F-hills-20261115-045332-ae6bca8`: superseded (exit None), Re-derive and check the scale estimate of brief line 275 (tidal radius in r_g, plunge bound, Peters time, passage times, Newtonian disruption window, published NR three-body configurations)
- `F-hills-20261115-045407-bf52f4e`: superseded (exit None), Re-derive and check the scale estimate of brief line 275 (tidal radius in r_g, plunge bound, Peters time, passage times, Newtonian disruption window, published NR three-body configurations)
- `F-hills-20261115-045410-bf52f4e`: superseded (exit None), Measured cost of the repository's black-hole runs (n1e4_v19, vacuum punctures, core three-BH test) and cost model of the Hills passages
- `F-hills-20261115-125858-0232c4c`: failed (exit 1), T1 metric identities, derivatives, CKS metric vs python/nrpic, flat-space binary
- `F-hills-20261115-131944-360a12e`: failed (exit 1), S4 equatorial Kerr HRNA (CKS), spin +0.9 and -0.9, beta 3,5,8,10,12,15, 200 phases, both senses
- `F-hills-20261115-133009-2f7ad7f`: failed (exit 1), analysis of F-hills-20261115-130239-cbfaf6b (P2 general orientation)
- `F-hills-20261115-133013-2f7ad7f`: failed (exit 1), analysis of F-hills-20261115-130239-cbfaf6b (P2 general orientation)
- `F-hills-20261115-133034-bf31889`: failed (exit 1), analysis of F-hills-20261115-130239-cbfaf6b (P2 general orientation)
- `F-hills-20261115-143824-2c937bc`: failed (exit 1), A4 analysis of C1 (rtol 1e-10 vs 1e-12)

## Open risks


Updated 2026-11-25 by the lead (batch 21: R4, R10, R20 revised, R22 new; earlier: batch 11, R14 and R19 retired, R20 and R21 new). Evidence and run ids: `stage/REVIEW-wave3.md`,
`stage/G0/VERIFIER.md`, `stage/G1/STATUS.md`, `JOURNAL.md`, `p1/JOURNAL.md`, `nr_first/JOURNAL.md`.

| Risk | Likelihood | Effect | Watch | Response |
|---|---|---|---|---|
| R20 (highest) preemption by another user's partition (whole nights; since 2026-11-25 06:44 PST both cards held for about a day, decision 0041 item 6) while the core-v0.5 card build of A2 writes no restart on SIGTERM: a preempted attempt loses up to one restart interval (1 M of A2, about 8 min) | certain while that user is active | weeks of delay for the passage | chain events.log, sacct | restart files every 1 M; from A2's segment 15 on, the worktree's chain script (01747be45) no longer counts an attempt cut by a signal; A2 keeps its executable (core: restart files must be read by the build that wrote them); 6 counted segments left, then a `--cmd` continuation within 19.5 card-hours (JOURNAL batch 21) |
| R21 (new) the passage's binary departs from the binary alone (A - B = -0.53 M at 60 M); Newtonian tide and the members' heavier horizon masses in M's conformal factor (mu = 1.015) give the size at 40-60 M but not the early part (F-20261124-132934-375a163) | open | a passage outcome could be read against the wrong isolated reference; the binary is tighter at the pericentre than planned | A2 vs B2, C2 vs A2 | report A against both B and the Newtonian references; the next binary's data should give the members the same horizon masses with and without M (core: id_punctures in the solve, core-v0.6) |
| R22 (new) horizon statements without the finder's status file: no run of this track set `<fastflow> diagnostics`, and a chain cannot switch it on at a restart (a command-line parameter missing from the restart's block is fatal) | certain for A2, B2, C2 | a claim "found" or a mass at a time rests on the failure signature only (accepted for D, decision 0041 item 4) | horizon summaries, recheck script b21_horizon_recheck.py | say "made without the diagnostics" beside each number; new decks set diagnostics = true (0041 item 5); request to core (outbox finder-diagnostics-on-restart) |
| R15 members at m/8 do not hold their orbit: P1's binary merged at t = 48.8 M; the binary alone at m/8 decays the same way (R8, F-20261121-130358-6cf186a); at m/12 and m/16 the binary alone gives the same orbit within 0.002 M to 21 M (F-20261121-202021-3c4321e) | settled: m/8 invalid, m/12 and m/16 converged to 21 M | every m/8 passage invalid | analysis F-20261121-202021-3c4321e | P1b at m/16 and m/12 submitted (lead batch 5, rule P1b-D clause D1) |
| R17 (new) no sharp 1PN reference for the binary: three 1PN-equivalent references of P1's start state differ by 0.019 M at 7.5 M and 0.158 M at 20 M (members at 0.11-0.33 c; lead run F-20261121-155353-e4d3354) | certain | "follows EIH within x" is not evidence of accuracy below about 0.02-0.16 M; orders from a deviation to one reference are unreliable | - | judge resolution by self-convergence (three resolutions, P1b-D D1); quote any 1PN comparison with all three variants |
| R19 RETIRED 2026-11-24 (was highest): the converged isolated binary was feared to merge before the passage's pericentre (stretch fit 93-97 M). The m/16 pair alone (R16n + B) turns at s = 3.12 M at t = 73.9 M and rises to 4.59 M at 107.85 M: an eccentric start (reading E), no merger (lead batch 11, F-20261124-130009-33bef4d) | retired | - | B2 (next apocentre; decay per orbit) | none needed; the eccentric start (e about 0.23) is a property of the data to quote with every passage result (R8) |
| R1 compute: G3 (about 500 card-hours) far above the allotments (50 to G1, 120 toward G2: decisions 0014, 0016); the two cards are shared with other users | certain | scan lines take weeks of queue | queue waits of P1's segments (0-40 min) | q = 4 first (0013); object (b) passages are 3-10 times cheaper; chains keep one segment queued; the corrected G2 plan is about 100 card-hours (SCOPING 9, verifier D3) |
| R2 q = 4 at m/16 needs 2864 MeshBlocks | was "certain"; now LOW | - | g2mesh card job (run F-20261120-222810-e408386): 3000 slots ran at 78785 MiB of 81920 | the triple fits one card at `max_nmb_per_rank` 2950-3000 (verifier D5; core-v0.4 interface "about 3100"); q = 10 at m/16 (up to 4544) still does not; R16u (3466) does not |
| R3 a passage stops on the slot limit | low | a segment fails | segment logs | restarts are exact: raise `max_nmb_per_rank` to 3000 |
| R4 member horizon masses drift at m/8 (fractional 0.9-1.7e-3 per M in P1 and R8; batch 21 recheck F-20261125-170632-5aa9786); flat at m/16 (below 3.1e-5 per M in R16n + B, A, A2); C (m/12) 1.2-1.7e-4 per M. All made without the finder's diagnostics (failure signature: no failed search in any m/12 or m/16 member finder) | high at m/8, low at m/16 | energies read against fixed masses biased | horizon summaries | measured masses at each time; m/16 for passages |
| R5 the references disagree with each other and none is a controlled approximation inside about 12 M (eih T4, reproduced by the lead to 1e-9); the geodesic model is at the edge of its own validity at the first passages' pericentres (a/R_curv reaches 0.2, verifier D7) | certain | no reference is the truth for NR | - | report NR against Newton, HRNA and EIH; quote reference percentages only with their start construction (verifier D2) and from the same start state as the NR data |
| R6 gauge: eta m = 0.25 trackers settle at 0.76 of P/M_ADM; core's mass-scaled profile untested with three holes; E10 judged (junk_gauge, 2 clauses failed) | medium | coordinate trajectories biased | E10 outcome in nr_first/JOURNAL.md | P1b keeps constant shift_eta = 2 (tested at m/16 by R16n); profile arm moved to the G2 gauge leg |
| R7 horizon finder at about 4 cells per radius at m/8 | certain at m/8 | early masses unusable | hrms column | masses only with hrms < 1e-3 at m/8; at m/16 (14 cells) rows with hrms up to 0.04 agree within 1e-4 |
| R8 approximate (superposed Bowen-York) data; 1PN inconsistency of the Newtonian start states (eih: binaries e = 0.12-0.21 at 1PN, CM orbit reading-dependent); three-hole junk at P1's spheres: burst 0.4-0.6e-6 M, then a steady emission of unidentified source (lead L5b) | medium | outcomes near boundaries data-dependent | junk at P1b's spheres, eih's 1PN states | 1PN-consistent states built far out (eih `p1_state.py`; the lead's failed local match shows why); constraint solve on the mesh (core) |
| R9 GR reading of the start states: q = 10 input turns at 5.77 M (bound CM), P1's at 9.25 M | certain | "r_p" labels reading-dependent | - | SCOPING 3 amended (verifier D1): every r_p with its GR turning point; q = 10 rebuilt from a GR parabola |
| R10 tracker files truncated on every restart (core-v0.3 to v0.7; core-restart-finder appends, card check q0049 unjudged) | certain in the executables used | a chain keeps only its last segment in the live file | `trk_keep/` | wrappers `athena_keep_trackers.sh`, `athena_resume_bc.sh` copy the files before each start; batch 21 showed the join of A + A2 complete and exact to 96.23 M (F-20261125-170453-1175d44): no loss so far |
| R16 outside kills (`pkill -x athena` of another project) and stray resubmissions after a chain's last segment | happened once each | lost segments; a queue place held by a job that will fail | chain `events.log`, squeue | run-specific executable name (`bc-ak05-gpu`, `p1-ak03-gpu`); main's submit_chain.sh resubmits after an outside kill (core-v0.6); cancel the stray job with `--stop` (core asked to check the cap before sbatch) |
| R11 chaos near outcome boundaries (2505.03934) | high near edges | single runs not representative | phase windows | robust windows; distributions over phase at G3 |
| R12 object (b) clumps must not relax during about 200 M; Track C's King models at y0 = 0.314 drift at the 1e-2 level over 200 M on M/4 cells (C-sidm answer 2026-11-19) | medium | (b) needs quieter models or finer meshes | C's relaxation runs; core clump-table | ask C for y0 = 0.25-0.30 when (b) starts; G2 relaxation test |
| R13 competition (RIT up to 128:1:1, 2406.11985; BAM, 2505.03934; 2605.20320 three holes from rest) | medium | novelty window short for (a) | citation queries before each gate | (b) is the wider novelty |
| R14 RETIRED 2026-11-24: KHSR (1201.4794) reproduced with newton3 (khsr_note, F-20261121-212757-77cdc15, -213405-6596be1; lead rerun identical, F-20261124-133112-db7d6b8; K1, K2 rederived by hand) | retired | - | second-agent check of K3 (C18) | - |
| R18 (new) HRNA in the Kerr-Schild slicing ('cks') pumps moving binaries at first order in M/r (kerr T8) | certain in 'cks' | geodesic_binary S4 (Kerr, 'cks') may be biased; the planned HRNA pair force in AthenaK would inherit it | - | use 'sch' or 'bks'; rerun S4 in 'bks'; specification and test T8 (d) sent to core |

## Decision requested from the group

G1 NOT met (lead, batch 21): the complete vacuum passage (C8: A2 PARTIAL at 96.23 M of the at least 170 M needed; chain continues, cards held until 2026-11-26) and the fresh G1 verifier (C18) are missing. Verify fails only on A2, which is still running. Horizon numbers rechecked by the failure signature (no status files): F-20261125-170632-5aa9786.

## Lead's notes (wave 2b, 2026-11-19)

- The criterion-by-criterion text of this gate is `STATUS.md` beside this report (it replaces
  the wave-1 version); the scoping text is `../G0/SCOPING.md`. The lead's review of the helpers:
  `../REVIEW-wave2.md` (`REVIEW.md` points to it).
- `nrpic-stage verify` ran on b95903f with `--no-checksums` (the output checksums of every run
  were verified half an hour earlier by the G0 verify on 7a24d7e; see `../G0/VERIFY_RESULTS.md`,
  which also lists three wave-2 run directories with moved-in outputs, ruling asked of orch).
  The two run failures here are the runs in flight: S2g (F-20261119-143443-f11ebb9) and P1
  (F-20261119-150017-b45ec5f).
- P1 was submitted after the lead judged the single-puncture runs and the smoke test against
  their criteria (`../../JOURNAL.md`, lead wave 2b, "P1: decision"): the run-health criteria
  were met; the failed predictions (first-search horizon masses, S2's settling value, the
  single-puncture cost) and the unmeasured junk do not bear on running P1.

## Lead's notes (wave 3, batch 2a, 2026-11-21; supersede the wave-2b notes where they differ)

- P1 (run F-20261119-150017-b45ec5f) is in its last segments (Slurm 4769 from t = 231.9 M); its
  binary merged at t = 48.8 M (p1 entry 4; lead's own parser, run F-20261121-063449-4dcca98), so
  criterion C8 (one complete vacuum passage) is FAIL in substance; RISKS R15; the deciding test is
  the isolated binary at m/8 and m/16.
- C6 FAIL: KHSR (G0 verifier D8) and Kerr (package kerr cut before any outcome) are open.
- C10, C11 PASS: G1 schematics drawn by the note package (run F-20261120-222908-4ffcfba), read.
- C17, C18 OPEN: the note's G1 revision is paused before its compile; no G1 verifier yet.
- Review of the wave-3 material: `../REVIEW-wave3.md` (eih confirmed; p1's merger confirmed).
