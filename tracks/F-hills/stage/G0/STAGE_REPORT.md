# Stage report: F-hills G0

Date: 2026-11-19 · branch `track/F-hills` at `e39a9cd23522` · checklist
`tracks/F-hills/stage/G0/CHECKLIST.md` (from `nrpic-stage collect`)

## Verdict

**FAIL**. Tag: `stage/F-hills/G0-fail-20261119` (created and pushed by the orchestrator after review, decision 0003).

- 1 checklist items not PASS or NA: C18 OPEN
- verify ran on 7a24d7e; files changed since: tracks/F-hills/eih/JOURNAL.md, tracks/F-hills/eih/README.md, tracks/F-hills/eih/figures/fig_p1_state_q10.png, tracks/F-hills/eih/figures/fig_p1_state_q4.png, tracks/F-hills/eih/figures/fig_scan_far_k20.png, tracks/F-hills/eih/figures/fig_scan_far_k40.png (run verify again)
- verify reported FAIL: runs
- no VERIFIER.md (step 7: verifier subagent; decision 0016 item 1, VERIFIER_REPORT.md accepted too)

## Package documents (decision 0012)

| Document | State |
|---|---|
| `stage/G0/STAGE_REPORT.md` | present |
| `stage/G0/EVIDENCE.md` | present |
| `stage/G0/OPEN.md` | present |
| `stage/G0/CHECKLIST.md` | present |
| `stage/G0/VERIFIER.md` (verifier's report) | MISSING (VERIFIER.md, decision 0016; VERIFIER_REPORT.md accepted too) |
| `stage/G0/REVIEW.md` | present |
| scoping text | `stage/G0/SCOPING.md`, `novelty/scope/SCOPE.md` |

## Criteria (coord/CHARTER.md, gate G0 of this track)

| # | Criterion | Evidence (run id, figure, KB locator) | Result |
|---|---|---|---|
| C1 | Problem statement, parameter ranges, exit criteria, test plan | SCOPING.md sections 1 (problem), 3 (parameter ranges), 5 (exit criteria G0-G3), 7 (test plan against brief rows 857-859); restated with figures in note/main.pdf Secs. II-IV (note package, wave 2) | PASS |
| C2 | The statements of the key references verified in the knowledge base | SCOPING.md section 8: 15 statements re-read by the lead at file:line in kb-data/raw/arxiv sources (0911.1136, 1804.02911, 2404.16270, 2402.02178, 2406.11985, 0710.0879, 1004.1353); the note package re-read prp.tex:735-738, 846-854, 345-357 and mnras.tex:368-379, 433-441 and article.tex:244-275 (note/JOURNAL.md, ledger appendix). Not through a kb index (outbox 20261115T1507Z__to-kb__*). Helper locators beyond these are not re-read (OPEN.md item 8) | PASS |
| C3 | Risk list | tracks/F-hills/RISKS.md (rewritten 2026-11-19: allotments of decisions 0014/0016, core-v0.3 released, wave-2b risks of the passage), SCOPING.md section 11 | PASS |
| C4 | Compute estimate | SCOPING.md section 9 from runs F-hills-20261115-131109-634fb86, -131348-634fb86, -131933-907e5fe, -045438-f62d553; recomputed in note figure fig_cost (runs F-20261115-180609-abc9f6e, F-20261115-173543-29e87e8). Correction: the q = 4 m/16 row uses puncture radius 1.2; the inputs use 1.8 (2514/2864/2568 MeshBlocks, 44.8 card-hours; note/tables/claims.md item 14), corrected in SCOPING.md section 9 on 2026-11-19 (lead V11) | PASS |
| C5 | Working note v0 | tracks/F-hills/note/main.tex and main.pdf (REVTeX 4.2, 11 pages, latexmk, every page read); guide and notation tracks/F-hills/WRITING_GUIDE.md, NOTATION.md; problem, set-up, tests with five data figures and the ledger from runs F-20261115-174648-25514db (N1) and F-20261115-180609-abc9f6e (N4); note/README.md | PASS |
| C6 | Architecture schematic | note/figures/schem_architecture.png (paperfig.py; exists / to be ported / new), Fig. 1 of the note; run F-20261115-180609-abc9f6e; PNG looked at | PASS |
| C7 | Stage timeline | note/figures/schem_timeline.png (paperfig.py), Fig. 7 of the note; run F-20261115-180609-abc9f6e; PNG looked at | PASS |
| C8 | (no track-specific criterion for G0 in the sheet: write the ones agreed with the orchestrator here, or mark NA) | the sheet (charter 9.9) has no G0-specific criterion; the track exit criteria per gate are in SCOPING.md section 5 | NA |
| C9 | Track F (amends 0005). Mass ratio four for the convergence study and the first scan line; the passage at mass ratio ten follows when the mesh fits. The first passage of a clump binary comes right after the first black-hole passage. (0013) | the ruling concerns G1-G3 (mass ratio of the convergence study and scan lines, timing of object (b)); followed already: the P1 input of wave 2 is at q = 4 (nr_first/inputs/p1_q4.athinput), the note plan (Sec. V, Fig. 7) and Sec. II C use it | NA |
| C10 | Schematic: Track architecture (three states: exists, to be ported, new) | note/figures/schem_architecture.png, three states (green exists, slate to be ported, red new); script note/scripts/schem_architecture.py; run F-20261115-180609-abc9f6e | PASS |
| C11 | Schematic: Stage timeline | note/figures/schem_timeline.png; script note/scripts/schem_timeline.py; run F-20261115-180609-abc9f6e | PASS |
| C12 | Data figure: None required | none required at G0; five data figures exist anyway (C15) | NA |
| C13 | Data figure: Data from the literature may be redrawn | optional; the note marks only values printed in the papers' text (with locators) and keeps digitised third-party curves out of committed figures | NA |
| C14 | Package documents of decision 0012: STAGE_REPORT.md (nrpic-stage report), EVIDENCE.md, OPEN.md and this CHECKLIST.md in the stage directory; REVIEW.md where the lead rechecked helpers; the scoping text in SCOPE.md or SCOPING.md beside them or in the scope directory, named in the report (no REPORT.md needed) | STAGE_REPORT.md (nrpic-stage report, rerun 2026-11-19), EVIDENCE.md and OPEN.md (updated by the lead in wave 2b), CHECKLIST.md (collect 2026-11-19), REVIEW.md (points to SCOPING.md section 10 for wave 1 and to ../REVIEW-wave2.md for waves 2 and 2b); scoping text SCOPING.md beside them, named in the report | PASS |
| C15 | Data figures drawn with /zoom-figure-style from registered run outputs, one script per figure, every PNG looked at | five data figures of the note, one script each (note/scripts/fig_*.py, czstyle.py copy equal to harness/style/SHA256SUMS), inputs read from registered run outputs with their recorded sha256 (26 files; one wave-1 run without checksums, said so), every PNG opened (note/JOURNAL.md N1-N4). The wave-1 package figures (newton3, geodesic_binary, three_punctures, checks) stay as package records | PASS |
| C16 | Schematics drawn with /sleep-paper-figure-style: track architecture (exists / to be ported / new) and the gate timeline | note/figures/schem_architecture.png and schem_timeline.png with note/scripts/paperfig.py (copy equal to harness/style/SHA256SUMS) | PASS |
| C17 | Working note written with /paper-writing; its manuscript checker passed with --compile | paper-writing checker with --compile (note/README.md): 0 undefined references and citations, 0 overfull boxes; main text clean in all 16 checks; remaining hits are run ids in the ledger appendix and data keys in the scripts, accepted by exception 1 of WRITING_GUIDE.md. Not done: the reviewer step of a new paper (skill Sec. 10) | PASS |
| C18 | Verifier subagent (fresh context) wrote VERIFIER.md (decision 0016; VERIFIER_REPORT.md accepted too); every number of the Supplemental Material recomputed from the manifests | no VERIFIER.md: this session has no subagent tool and the lead may not verify its own package. What exists: SECOND_CHECK.md, a check of the plan's two load-bearing claims by a second agent of wave 2 with its own code (novelty verdict holds; the q = 10 baseline disagreement is physical, HRNA's size of it inflated by two artefacts; the q = 10 start state turns at 5.77 M in GR), confirmed in part by the lead (V9a, run F-20261119-145449-245e984); it did not recompute the note's ledger. Requested of orch: a fresh verifier for G0 (on the plan, decision 0016 item 4), or a ruling that SECOND_CHECK.md is the verifier's report on the plan (outbox 20261119T*) | OPEN |
| C19 | Null results and failed runs are on record (manifests and JOURNAL) | failed and stopped runs kept: wave 1 in EVIDENCE.md (F-hills-20261115-045124-ae6bca8, -125858-0232c4c, -131944-360a12e, -143824-2c937bc, -133009-2f7ad7f, -133013-2f7ad7f, -133034-bf31889); wave 2 F-20261115-173719-923135a (failed), F-20261115-173106-57c4b4c, -173112-a9e18a3, -173543-29e87e8 (stopped, nr_first/JOURNAL.md); failed predictions on record in JOURNAL.md (V4, V5, V6, V7, V5b), nr_first/JOURNAL.md (E4, E6) and note/JOURNAL.md (N2 item 3) | PASS |
| C20 | STATUS.md, JOURNAL.md and HANDOFF.md are current | STATUS.md, HANDOFF.md rewritten and a JOURNAL.md entry appended by the lead at the end of wave 2b (2026-11-19), with P1 announced in STATUS before its submission | PASS |

## Re-verification on a clean checkout (`nrpic-stage verify`)

`nrpic-stage verify` on 2026-11-19T15:20:29Z, clean export of `7a24d7eca748`: **FAIL**. Details: `VERIFY_RESULTS.md`.

| Check | Result | Message |
|---|---|---|
| clean | PASS | worktree clean (outside the stage directory being assembled) |
| sync | PASS | main is merged into the branch |
| export | PASS | clean export of 7a24d7eca748 (HEAD) in /data/haiyangw/nrpic/scratch/F-hills/tmp/stage-verify/F-hills-G0-7a24d7e-20261119T150132Z/tree |
| size | PASS | no committed file of the track above 5 MB |
| note | PASS | tracks/<ID>/note/main.tex present |
| package | PASS | EVIDENCE.md, OPEN.md, CHECKLIST.md present (decision 0012); scoping text: stage/G0/SCOPING.md, novelty/scope/SCOPE.md; REVIEW.md present; no verifier's report yet (VERIFIER.md, decision 0016) |
| note-pdf | PASS | note/main.pdf committed after the last .tex change |
| style | PASS | 2 style copies equal harness/style/SHA256SUMS (czstyle.py, paperfig.py) |
| fig-script | PASS | 7 figures, each with its script |
| min-figs | PASS | 2 schematics and 5 data figures (brief 13.4 asks at least 2 and 0 at G0) |
| runs | FAIL | 6 of 153 runs have problems |
| run-notes | WARN | 78 runs read with defaults or not fully re-verifiable (nrpic-run lint) |
| status | PASS | STATUS.md has 49 lines |
| rerun | PASS | 7 of 7 scripts and commands ran cleanly in the export |
| compare | PASS | 19 regenerated files compared with the committed ones; 0 differ beyond tolerance (rtol 1e-06, atol 1e-12, PNG rms 0.005) |
| regenerate | PASS | all 14 committed figure files regenerated |

## Figures

| File | Script | Kind (data / schematic) | Looked at (PNG read) |
|---|---|---|---|
| note/figures/fig_cost.* | note/scripts/fig_cost.py | data | to be confirmed by the session |
| note/figures/fig_geodesic.* | note/scripts/fig_geodesic.py | data | to be confirmed by the session |
| note/figures/fig_newton.* | note/scripts/fig_newton.py | data | to be confirmed by the session |
| note/figures/fig_passage.* | note/scripts/fig_passage.py | data | to be confirmed by the session |
| note/figures/fig_rp_scan.* | note/scripts/fig_rp_scan.py | data | to be confirmed by the session |
| note/figures/schem_architecture.* | note/scripts/schem_architecture.py | schematic | to be confirmed by the session |
| note/figures/schem_timeline.* | note/scripts/schem_timeline.py | schematic | to be confirmed by the session |

## Verifier report

MISSING: the verifier subagent has not reported (`stage/G0/VERIFIER.md`, decision 0016).

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

## Decision requested from the group

Complete for the orchestrator's review except the verifier's report: accept G0 of F-hills when a fresh verifier has reported on the plan (decision 0016 item 4), or rule that SECOND_CHECK.md (a second agent's independent check of the novelty verdict, both baselines and the start state, wave 2) serves as that report; and rule on the three wave-2 run directories whose moved-in outputs are not checksummed. Scope, exit criteria, test plan, references, risks, compute estimate, working note v0 and both schematics are complete; the corrections found by the note helper and the second check are made; the first passage runs at q = 4 under decision 0013.

## Notes of the note helper (wave 2)

Written by the helper that made the note package (`tracks/F-hills/note/`, README there); kept
when `nrpic-stage report` runs again.

- Scoping text: `tracks/F-hills/stage/G0/SCOPING.md` (wave 1, the lead's; decision 0012
  accepts it under that name), with the novelty helper's draft `novelty/scope/SCOPE.md` and
  verdict `novelty/NOVELTY.md`. The working note v0 (`note/main.pdf`, 11 pages) restates the
  problem, the set-up and the tests from registered runs and adds the plunge-bound argument,
  the pericentre scan of both references and the first passages at q = 4 and 10 as figures.
- Runs of the note package: F-20261115-174648-25514db (N1, time series of both references
  from the two passage inputs; reproduces E6, V5, V5b, V6 in every printed digit) and
  F-20261115-180609-abc9f6e (N4, the figures and tables now committed; N2
  F-20261115-175639-ce844e5 and N3 F-20261115-180428-fc8172f gave byte-identical PNGs).
  All 26 input files of the figures and ledger matched the sha256 their runs recorded, except
  the scale run F-hills-20261115-045435-f62d553, whose manifest records no checksums.
- Differences between the lead's documents and the files (the files win;
  `note/tables/claims.md`: 13 of 17 agree, 2 differ, 2 superseded):
  1. `stage/G1/STATUS.md` T1, `EVIDENCE.md` V4b and `STATUS.md` say the independent code
     agrees with newton3 at nine (sense, D) points within 0.002 in P_dis and 0.4 percent in
     energy (V4b), "all nine agree". V4b (F-hills-20261115-145544-a314517) reran only
     retrograde D = 0.3 and 0.38 (|dP| <= 0.0013, |dE|/E <= 0.0035); retrograde D = 0.1 and
     0.2 come from V4 (F-hills-20261115-145246-090f5dc) with |dP| = 0.0023 and 0.0063 and
     |dE|/E = 0.0038 and 0.0116, and 8 and 14 wide bound samples that V4b did not follow on.
  2. `SCOPING.md` section 9, row "q = 4, m/16: 2416 / 2654 / 2348, 41 card-hours" is the tree
     with puncture radius 1.2; the inputs use 1.8: 2514 / 2864 / 2568 and 44.8 card-hours
     (F-hills-20261115-131933-907e5fe; E1 measured 2514 at the start with the release
     executable, F-20261115-173543-29e87e8). 2864 exceeds the inputs' max_nmb_per_rank 2700.
  3. Superseded: allotment 40 card-hours (STATUS, RISKS R1; decision 0014 gives 50) and
     "core/multi-puncture not released" (HANDOFF, OPEN item 6, RISKS R3; in core-v0.3 now).
  4. Wording: the STATUS headline's "captures a member in 69-96 percent of phases" is a
     plunge (r < 2.5 M) in the files; "Newton in none" holds for plunges, but full Newton brings
     a member inside 4 M in 62 percent of the phases at r_p = 7 M (V7).
- `nrpic-stage verify` was not run by this package: other helpers of F-hills had uncommitted
  files in the worktree (newton3) while this package finished, so its `clean` check would
  fail on their work, and its results file is the lead's to write. The figure scripts of the
  note each run alone from a clean checkout of the scripts and the registered outputs.
- Draft of the decision paragraph (for the lead to edit and pass with `--decision`): "Accept
  G0 of F-hills once the second check of the novelty verdict and of the V6/V7 disagreement
  (stage/G0/second_check, wave 2) is in, REVIEW.md points to the lead's check of the helpers
  (SCOPING.md section 10), STATUS/HANDOFF are rewritten for wave 2, and the two corrections
  above (V4b wording, q = 4 m/16 row) are made. The scope, the two reference solutions, the
  compute estimate, the working note and the two schematics are complete; the first passage
  runs at q = 4 under decision 0013 within the 50 card-hours of decision 0014."

## Lead's state of the package (wave 2b, 2026-11-19)

- The note helper's four differences are settled: (1) V4b wording corrected in EVIDENCE.md and
  the G1 package (seven points; retrograde D = 0.1, 0.2 rest on V4); (2) SCOPING.md section 9's
  q = 4 m/16 row corrected with a dated note; (3) STATUS, HANDOFF, RISKS and OPEN rewritten
  for core-v0.3 and decisions 0014/0016; (4) the headline no longer quotes HRNA percentages.
  Lead's checks V8-V11 and the review of every helper: `../REVIEW-wave2.md`, `REVIEW.md`.
- `nrpic-stage verify` on 7a24d7e (VERIFY_RESULTS.md): every check PASS except `runs` (6 of
  153): three runs of F-hills's own wave 2 are still in flight (S2g F-20261119-143443-f11ebb9,
  P1 F-20261119-150017-b45ec5f; and F-20261119-145920-d7af935 of the wave-3a eih package), and
  three wave-2 runs registered by nrpic-run have files in their output directories that are not
  in their sha256sums.txt (F-20261115-173719-923135a, F-20261115-181805-f9c3473,
  F-20261115-182100-613c9c6): outputs the helper's scripts wrote relative to the worktree root
  and that were moved into the run directories after `finish` (nr_first/JOURNAL.md,
  "Incidents"). Not waivable under decision 0016 item 3 (not hand-written); the run
  directories are left as they are and a ruling is asked of orch.
- The verifier's report (C18) is missing; SECOND_CHECK.md is a second agent's check of the
  plan. Asked of orch (outbox `20261119T151429Z__to-orch__verifier-g0-g1.md`).
