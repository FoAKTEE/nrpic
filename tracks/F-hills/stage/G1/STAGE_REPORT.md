# Stage report: F-hills G1

Date: 2026-11-19 · branch `track/F-hills` at `b95903f4e876` · checklist
`tracks/F-hills/stage/G1/CHECKLIST.md` (from `nrpic-stage collect`)

## Verdict

**FAIL**. Tag: `stage/F-hills/G1-fail-20261119` (created and pushed by the orchestrator after review, decision 0003).

- 8 checklist items not PASS or NA: C6 FAIL, C7 OPEN, C8 OPEN, C10 OPEN, C11 FAIL, C15 OPEN, C17 OPEN, C18 OPEN
- verify reported FAIL: runs
- no VERIFIER.md (step 7: verifier subagent; decision 0016 item 1, VERIFIER_REPORT.md accepted too)

## Package documents (decision 0012)

| Document | State |
|---|---|
| `stage/G1/STAGE_REPORT.md` | written by this command |
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
| C6 | F-pre-1 and F-pre-2 reproduce the curves of the literature | F-pre-1 met (STATUS.md T1; independent check at seven points within 0.002/0.4 %, two retrograde points within 0.0063/1.2 %). F-pre-2 met for Schwarzschild (2404.16270: separation fraction within 0.0225, v_inf within 0.7 %), NOT for Kerr: 2402.02178's inclined-binary statement not reproduced (OPEN.md item 3) | FAIL |
| C7 | Constraint residuals and junk radiation of the three-puncture data are quantified | constraints quantified (E2: t = 0 norm 4.7e-5 at m/8 is truncation; corrected data 4.9e-7 = 1/33 of uncorrected; order 7.6-8; F-20261115-173547-a02af7d, -181434-b9c8916; nr_first/figures/fig_c0_constraints.png; card smoke equal, F-20261115-174602-c6879fe). Junk radiation NOT measured: S3/S2 stopped at the slot limit before the pulse reached 30 m; pending P1's spheres (F-20261119-150017-b45ec5f) and S2g (F-20261119-143443-f11ebb9) | OPEN |
| C8 | One complete vacuum passage is done | P1 at q = 4 (decision 0013) submitted 2026-11-19 as a chain, run F-20261119-150017-b45ec5f, Slurm 4650 (pending), 17-20 card-hours expected; smoke passed its run-health criteria (E7, V8d); predictions in JOURNAL.md (lead wave 2b) and STATUS.md here | OPEN |
| C9 | Track F (amends 0005). Mass ratio four for the convergence study and the first scan line; the passage at mass ratio ten follows when the mesh fits. The first passage of a clump binary comes right after the first black-hole passage. (0013) | followed: P1 and the convergence plan are at q = 4 (nr_first/inputs/p1_q4.athinput; STATUS.md); q = 10 waits for the mesh and for momenta from a GR parabola (V9a: the q = 10 input turns at 5.77 M in GR); the clump passage (object b) follows the first black-hole passage (core's wave-3a clump-table package) | PASS |
| C10 | Schematic: Updated architecture | not drawn: the G0 architecture schematic (note/figures/schem_architecture.png) predates core-v0.3 and the NR runs of waves 2 and 2b | OPEN |
| C11 | Schematic: Data-flow diagram | no data-flow diagram exists yet (OPEN.md item 4) | FAIL |
| C12 | Data figure: Baseline results | note/figures/fig_newton.png, fig_geodesic.png, fig_rp_scan.png, fig_passage.png (scripts note/scripts/fig_*.py, run F-20261115-180609-abc9f6e); nr_first/figures/fig_baselines_p1.png (F-20261115-174102-ffa764f); all looked at (note/JOURNAL.md; lead review) | PASS |
| C13 | Data figure: Validation figures for the analysis pipeline | nr_first/figures/fig_test_nrread_synthetic.png (reader test), fig_e10a_s3_s2_compare.png (comparison script on S3/S2), fig_e11_tree_check.png (tree model against restart trees), fig_e3_single_gauge.png (rerun F-20261119-145619-8246322), fig_e7_p1smoke.png; lead fig_review_nr.png (F-20261119-145434-82c05f2); all looked at by the lead (REVIEW-wave2.md). Drawn by the package scripts with python/nrpic/figstyle.py, not yet note figures | PASS |
| C14 | Package documents of decision 0012: STAGE_REPORT.md (nrpic-stage report), EVIDENCE.md, OPEN.md and this CHECKLIST.md in the stage directory; REVIEW.md where the lead rechecked helpers; the scoping text in SCOPE.md or SCOPING.md beside them or in the scope directory, named in the report (no REPORT.md needed) | STAGE_REPORT.md (nrpic-stage report), EVIDENCE.md, OPEN.md, CHECKLIST.md, REVIEW.md (points to ../REVIEW-wave2.md and SCOPING.md section 10); the criterion-by-criterion text is STATUS.md beside them, the scoping text ../G0/SCOPING.md, both named in the report | PASS |
| C15 | Data figures drawn with /zoom-figure-style from registered run outputs, one script per figure, every PNG looked at | the G0 data figures of the note pass (zoom style, one script each, registered inputs, looked at); the G1 NR figures exist in nr_first/figures with their scripts and runs and were looked at, but are not yet note figures with scripts under note/scripts (OPEN.md item 4) | OPEN |
| C16 | Schematics drawn with /sleep-paper-figure-style: track architecture (exists / to be ported / new) and the gate timeline | note/figures/schem_architecture.png and schem_timeline.png with note/scripts/paperfig.py (copy equal to harness/style/SHA256SUMS); their G1 updates are C10, C11 | PASS |
| C17 | Working note written with /paper-writing; its manuscript checker passed with --compile | note v0 (11 pages, checker clean with --compile) covers G0 and the baselines; its G1 sections on the NR runs are not written | OPEN |
| C18 | Verifier subagent (fresh context) wrote VERIFIER.md (decision 0016; VERIFIER_REPORT.md accepted too); every number of the Supplemental Material recomputed from the manifests | no VERIFIER.md (no subagent tool in this session; the lead does not verify its own package); asked of orch (outbox 20261119T*). Second agent so far: ../G0/SECOND_CHECK.md (plan and baselines) | OPEN |
| C19 | Null results and failed runs are on record (manifests and JOURNAL) | failed and stopped runs kept with manifests and journal entries: F-20261115-173601-2fae2dc (S3/S2, slot limit), F-20261115-173606-efcbf69 (withdrawn), F-20261115-173719-923135a, F-20261119-143851-47595bd, F-20261115-174959-9e8a361 (stopped), F-20261115-174142-2a79515 (superseded), F-20261115-175542-b49d687; failed predictions on record: nr_first/JOURNAL.md (E1(b), E3 items 1, 2, 5, E4 rerun counts, E7 first-search masses), newton3/JOURNAL.md (Q1, Q3, Q4 bounds), stage/G0/JOURNAL.md (SC0d, SC2, SC6), JOURNAL.md (V4-V7 of wave 1) | PASS |
| C20 | STATUS.md, JOURNAL.md and HANDOFF.md are current | STATUS.md, HANDOFF.md rewritten and a JOURNAL.md entry appended by the lead at the end of wave 2b (2026-11-19); P1 announced in STATUS before submission | PASS |

## Re-verification on a clean checkout (`nrpic-stage verify`)

`nrpic-stage verify` on 2026-11-19T15:22:08Z, clean export of `b95903f4e876`: **FAIL**. Details: `VERIFY_RESULTS.md`.

| Check | Result | Message |
|---|---|---|
| clean | PASS | worktree clean (outside the stage directory being assembled) |
| sync | PASS | main is merged into the branch |
| export | PASS | clean export of b95903f4e876 (HEAD) in /data/haiyangw/nrpic/scratch/F-hills/tmp/stage-verify/F-hills-G1-b95903f-20261119T152147Z/tree |
| size | PASS | no committed file of the track above 5 MB |
| note | PASS | tracks/<ID>/note/main.tex present |
| package | PASS | EVIDENCE.md, OPEN.md, CHECKLIST.md present (decision 0012); scoping text: novelty/scope/SCOPE.md; REVIEW.md present; no verifier's report yet (VERIFIER.md, decision 0016) |
| note-pdf | PASS | note/main.pdf committed after the last .tex change |
| style | PASS | 2 style copies equal harness/style/SHA256SUMS (czstyle.py, paperfig.py) |
| fig-script | PASS | 7 figures, each with its script |
| min-figs | PASS | 2 schematics and 5 data figures (brief 13.4 asks at least 2 and 1 at G1) |
| runs | FAIL | 2 of 158 runs have problems |
| run-notes | WARN | 78 runs read with defaults or not fully re-verifiable (nrpic-run lint) |
| status | PASS | STATUS.md has 49 lines |
| rerun | PASS | 7 of 7 scripts and commands ran cleanly in the export |
| compare | PASS | 19 regenerated files compared with the committed ones; 0 differ beyond tolerance (rtol 1e-06, atol 1e-12, PNG rms 0.005) |
| regenerate | PASS | all 14 committed figure files regenerated |

## Figures

| File | Script | Kind (data / schematic) | Looked at (PNG read) |
|---|---|---|---|
| note/figures/fig_cost.* | note/scripts/fig_cost.py | data | yes (lead, 2026-11-19; also note/JOURNAL.md N1-N4) |
| note/figures/fig_geodesic.* | note/scripts/fig_geodesic.py | data | yes (lead, 2026-11-19; also note/JOURNAL.md N1-N4) |
| note/figures/fig_newton.* | note/scripts/fig_newton.py | data | yes (lead, 2026-11-19; also note/JOURNAL.md N1-N4) |
| note/figures/fig_passage.* | note/scripts/fig_passage.py | data | yes (lead, 2026-11-19; also note/JOURNAL.md N1-N4) |
| note/figures/fig_rp_scan.* | note/scripts/fig_rp_scan.py | data | yes (lead, 2026-11-19; also note/JOURNAL.md N1-N4) |
| note/figures/schem_architecture.* | note/scripts/schem_architecture.py | schematic | yes (lead, 2026-11-19; also note/JOURNAL.md N1-N4) |
| note/figures/schem_timeline.* | note/scripts/schem_timeline.py | schematic | yes (lead, 2026-11-19; also note/JOURNAL.md N1-N4) |

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


Updated 2026-11-19 by the lead (wave 2b). Evidence and run ids: `stage/G1/STATUS.md`,
`stage/REVIEW-wave2.md`, `JOURNAL.md`, `nr_first/JOURNAL.md`.

| Risk | Likelihood | Effect | Watch | Response |
|---|---|---|---|---|
| R1 compute: G3 (about 500 card-hours) far above the allotments (50 to G1, 120 toward G2: decisions 0014, 0016); the two cards are shared with other users | certain | scan lines take weeks of queue | queue waits of P1's segments | q = 4 first (0013); object (b) passages are 3-10 times cheaper; chains keep one segment queued |
| R2 q = 4 at m/16 needs 2864 MeshBlocks, above the 2700 slots of one card (69.2 GiB at 2700, 26.2 MiB per slot; smoke F-20261115-174602-c6879fe); q = 10 at m/16 needs 2654-4544 | certain on the present build | the G2 resolution triple does not fit | core's answer on 32^3 blocks (no source change; benchmark bench16/bench32 not run) | run the 32^3 benchmark with the release; two cards (core/mpi, wave 3a) |
| R3 the passage P1 stops on the slot limit, as S3/S2 did (1632 > 1600: wave-zone radius plus the 2:1 rule, nr_first E11) | low (P1's tree 1716-1744 measured, wave-1 maximum 2080 along the Newtonian track, limit 2700) | a segment fails; restart with a higher limit costs memory | `slurm-*.out` and `athena.*.log` of each segment | restarts are exact: resume with `mesh_refinement/max_nmb_per_rank` raised up to about 3000 |
| R4 member horizon masses drift at m/8: 0.6-1.1e-4 per member mass per unit time in single punctures (S3, S2), +1.3-1.5 % in 16 M in core's three-hole run | high | members 10-18 % heavier by t = 200 M if the rate persists; energies read against fixed masses biased | P1's horizon summaries | read member energies with the measured masses at each time; G2 resolution triple decides whether the drift converges away |
| R5 the two baselines disagree on the outcome of P1 (Newton ejects m1, HRNA ejects m2; E6) and at q = 10 in kind; HRNA carries a spurious self-acceleration of a moving binary (second check) | certain | neither is the truth for NR | P1 | report NR against both, plus the 1PN (EIH) reference of wave 3a after review |
| R6 gauge: with eta m = 0.25 the members' trackers settle at 0.76 of P/M_ADM in 4 m; with eta m = 2 still rising at 22 m; core's mass-scaled profile untested with three holes | medium | coordinate trajectories biased; q = 10 cannot use one constant eta | S2g (run F-20261119-143443-f11ebb9); core's answer | gauge-free observables (asymptotic speeds, horizon masses); profile only after a three-hole test |
| R7 horizon finder at about 4 cells per radius: m2 not found at t = 0, heavy hole fails 17/25 early searches, "converged" poor surfaces (hrms 1e-2) | certain at m/8 | early masses unusable; a member merger may be missed | hrms column | read masses only with hrms < 1e-3, members from t = 0.5 M, heavy from about 4 M; request to core |
| R8 approximate (superposed Bowen-York) data: corrected data's own residual 1/33 of uncorrected (E2); junk not measured yet | medium | outcomes near boundaries data-dependent | P1's spheres, S2g | junk from P1; constraint solve on the mesh (core id-solver-2) before G3 |
| R9 GR reading of the start states: the q = 10 input turns at 5.77 M, not 8 M (second check, lead V9a); P1's at 9.25 M in the hole frame and at the capture boundary in other readings (V9b) | certain | the "r_p" label of an NR passage is reading-dependent | - | label passages by their GR turning point; build q = 10 momenta from a GR parabola |
| R10 tracker files truncated on every restart (compact_object_tracker.cpp line 77) | certain until core fixes it | a chain keeps only its last segment's trajectory | `trk_keep/` in P1's run directory | wrapper `nr_first/scripts/athena_keep_trackers.sh`; request to core |
| R11 chaos near outcome boundaries (2505.03934) | high near edges | single runs not representative | phase windows of newton3_fix (q = 4: 109-144 deg contain 127) | robust windows; distributions over phase at G3 |
| R12 object (b) clumps must be mildly relativistic and must not relax during about 200 M | medium | (b) needs larger a_b or more particles | core clump-table (wave 3a), Track C models | G2 relaxation test |
| R13 competition (RIT plans up to 128:1:1, 2406.11985; BAM scatters N black holes, 2505.03934) | medium | novelty window short for (a) | citation queries before each gate (second check: verdict holds on 2026-11-15) | (b) is the wider novelty |
| R14 no fresh verifier for G0/G1 | - | gate review may be delayed | orch's answer (outbox 20261119T151429Z__to-orch__verifier-g0-g1) | SECOND_CHECK.md as the second agent's check of the plan |

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

## Decision requested from the group

Not complete for the orchestrator's review: G1 of F-hills is not met. Met: F-pre-1, the baselines, the validated analysis pipeline, interface proposals. Open: the complete vacuum passage P1 (run F-20261119-150017-b45ec5f, submitted 2026-11-19, 17-20 card-hours in the shared queue), the junk radiation of the three-hole data (from P1's spheres), F-pre-2 for Kerr (2402.02178), the G1 schematics and note sections, and a verifier. No decision is requested now; the package is resubmitted when P1 has been analysed.
