# Stage report: F-hills G0

Date: 2026-11-21 · branch `track/F-hills` at `f4dfb4d94cc0` · checklist
`tracks/F-hills/stage/G0/CHECKLIST.md` (from `nrpic-stage collect`)

## Verdict

**FAIL**. Tag: `stage/F-hills/G0-fail-20261121` (created and pushed by the orchestrator after review, decision 0003).

- verify ran on 7bf8f9d; files changed since: coord/DECISIONS/0020-size-batches-to-the-five-hour-window.md, harness/workflows/batch-2a.json, harness/workflows/batch-2b.json, harness/workflows/make_batch.py, tracks/F-hills/HANDOFF.md, tracks/F-hills/JOURNAL.md (run verify again)
- verify reported FAIL: clean, sync, runs

## Package documents (decision 0012)

| Document | State |
|---|---|
| `stage/G0/STAGE_REPORT.md` | present |
| `stage/G0/EVIDENCE.md` | present |
| `stage/G0/OPEN.md` | present |
| `stage/G0/CHECKLIST.md` | present |
| `stage/G0/VERIFIER.md` (verifier's report) | present |
| `stage/G0/REVIEW.md` | present |
| scoping text | `stage/G0/SCOPING.md`, `novelty/scope/SCOPE.md` |

## Criteria (coord/CHARTER.md, gate G0 of this track)

| # | Criterion | Evidence (run id, figure, KB locator) | Result |
|---|---|---|---|
| C1 | Problem statement, parameter ranges, exit criteria, test plan | SCOPING.md sections 1 (problem), 3 (parameter ranges), 5 (exit criteria G0-G3), 7 (test plan against brief rows 857-859); restated with figures in note/main.pdf Secs. II-IV (note package, wave 2) | PASS |
| C2 | The statements of the key references verified in the knowledge base | SCOPING.md section 8: 15 statements re-read by the lead at file:line in kb-data/raw/arxiv sources (0911.1136, 1804.02911, 2404.16270, 2402.02178, 2406.11985, 0710.0879, 1004.1353); the note package re-read prp.tex:735-738, 846-854, 345-357 and mnras.tex:368-379, 433-441 and article.tex:244-275 (note/JOURNAL.md, ledger appendix). Not through a kb index (outbox 20261115T1507Z__to-kb__*). Helper locators beyond these are not re-read (OPEN.md item 8) | PASS |
| C3 | Risk list | tracks/F-hills/RISKS.md (rewritten 2026-11-19: allotments of decisions 0014/0016, core-v0.3 released, wave-2b risks of the passage), SCOPING.md section 11 | PASS |
| C4 | Compute estimate | SCOPING.md section 9 from runs F-hills-20261115-131109-634fb86, -131348-634fb86, -131933-907e5fe, -045438-f62d553; recomputed in note figure fig_cost (runs F-20261115-180609-abc9f6e, F-20261115-173543-29e87e8); verifier K14 recount within 0.4 percent (run F-20261121-035817-0aca1c5). Corrections: q = 4 m/16 row (radius 1.8; lead V11, 2026-11-19); slot limit against card capacity and the G2 sum 131-135 (verifier D3, D5; amended 2026-11-21, lead run F-20261121-063504-00f0743); P1's measured cost row (about 13 card-hours to 280 M) | PASS |
| C5 | Working note v0 | tracks/F-hills/note/main.tex and main.pdf (REVTeX 4.2, 11 pages, latexmk, every page read); guide and notation tracks/F-hills/WRITING_GUIDE.md, NOTATION.md; problem, set-up, tests with five data figures and the ledger from runs F-20261115-174648-25514db (N1) and F-20261115-180609-abc9f6e (N4); note/README.md | PASS |
| C6 | Architecture schematic | note/figures/schem_architecture.png (paperfig.py; exists / to be ported / new), Fig. 1 of the note; run F-20261115-180609-abc9f6e; PNG looked at | PASS |
| C7 | Stage timeline | note/figures/schem_timeline.png (paperfig.py), Fig. 7 of the note; run F-20261115-180609-abc9f6e; PNG looked at | PASS |
| C8 | (no track-specific criterion for G0 in the sheet: write the ones agreed with the orchestrator here, or mark NA) | the sheet (charter 9.9) has no G0-specific criterion; the track exit criteria per gate are in SCOPING.md section 5 | NA |
| C9 | Track F (amends 0005). Mass ratio four for the convergence study and the first scan line; the passage at mass ratio ten follows when the mesh fits. The first passage of a clump binary comes right after the first black-hole passage. (0013) | the ruling concerns G1-G3 and is followed: P1 (the first passage) is at q = 4 (nr_first/inputs/p1_q4.athinput, run F-20261119-150017-b45ec5f); SCOPING.md sections 3, 6 and 9 named q = 10 until the verifier's D4 and were amended on 2026-11-21 (../REVIEW-wave3.md); the note follows 0013 | PASS |
| C10 | Schematic: Track architecture (three states: exists, to be ported, new) | note/figures/schem_architecture.png, three states (green exists, slate to be ported, red new); script note/scripts/schem_architecture.py; run F-20261115-180609-abc9f6e | PASS |
| C11 | Schematic: Stage timeline | note/figures/schem_timeline.png; script note/scripts/schem_timeline.py; run F-20261115-180609-abc9f6e | PASS |
| C12 | Data figure: None required | none required at G0; five data figures exist anyway (C15) | NA |
| C13 | Data figure: Data from the literature may be redrawn | optional; the note marks only values printed in the papers' text (with locators) and keeps digitised third-party curves out of committed figures | NA |
| C14 | Package documents of decision 0012: STAGE_REPORT.md (nrpic-stage report), EVIDENCE.md, OPEN.md and this CHECKLIST.md in the stage directory; REVIEW.md where the lead rechecked helpers; the scoping text in SCOPE.md or SCOPING.md beside them or in the scope directory, named in the report (no REPORT.md needed) | STAGE_REPORT.md (nrpic-stage report, rerun 2026-11-21), EVIDENCE.md and OPEN.md (updated by the lead in batch 2a), CHECKLIST.md (collect 2026-11-21), REVIEW.md (points to SCOPING.md section 10 for wave 1, ../REVIEW-wave2.md for waves 2 and 2b, ../REVIEW-wave3.md for wave 3); scoping text SCOPING.md beside them, named in the report; VERIFIER.md | PASS |
| C15 | Data figures drawn with /zoom-figure-style from registered run outputs, one script per figure, every PNG looked at | five data figures of the note, one script each (note/scripts/fig_*.py, czstyle.py copy equal to harness/style/SHA256SUMS), inputs read from registered run outputs with their recorded sha256 (26 files; one wave-1 run without checksums, said so), every PNG opened (note/JOURNAL.md N1-N4). The wave-1 package figures (newton3, geodesic_binary, three_punctures, checks) stay as package records | PASS |
| C16 | Schematics drawn with /sleep-paper-figure-style: track architecture (exists / to be ported / new) and the gate timeline | note/figures/schem_architecture.png and schem_timeline.png with note/scripts/paperfig.py (copy equal to harness/style/SHA256SUMS) | PASS |
| C17 | Working note written with /paper-writing; its manuscript checker passed with --compile | paper-writing checker with --compile (note/README.md): 0 undefined references and citations, 0 overfull boxes; main text clean in all 16 checks; remaining hits are run ids in the ledger appendix and data keys in the scripts, accepted by exception 1 of WRITING_GUIDE.md. Not done: the reviewer step of a new paper (skill Sec. 10) | PASS |
| C18 | Verifier subagent (fresh context) wrote VERIFIER.md (decision 0016; VERIFIER_REPORT.md accepted too); every number of the Supplemental Material recomputed from the manifests | VERIFIER.md (fresh verifier, package verify_g0, batch 1 of 2026-11-20; artefacts only; sections 1-3 committed fecdec04 before reading the earlier checks): 20 claims of the plan with verdicts (14 CONFIRMED, K4 NOT DONE, K6/K13 PARTLY, K12/K14/K15/K16 WRONG as worded) and ledger tables 1-2 of the note recomputed row by row, 57 of 57 (run F-20261121-035817-0aca1c5). The lead reran that recomputation from its registered outputs (run F-20261121-063712-25981e0: 56 rows identical, row 57 a stale locator after core-v0.4 rewrote multi_puncture.md) and checked every WRONG item at the source (run F-20261121-063504-00f0743); each is corrected in SCOPING.md (marked [amended: D1-D8]), in note/main.tex (D7, D10) or listed for the note's ledger rerun (D9, row 57): ../REVIEW-wave3.md. Table 3 of the ledger (G1 material) is for the G1 verifier (decision 0016 item 4) | PASS |
| C19 | Null results and failed runs are on record (manifests and JOURNAL) | failed and stopped runs kept: wave 1 in EVIDENCE.md (F-hills-20261115-045124-ae6bca8, -125858-0232c4c, -131944-360a12e, -143824-2c937bc, -133009-2f7ad7f, -133013-2f7ad7f, -133034-bf31889); wave 2 F-20261115-173719-923135a (failed), F-20261115-173106-57c4b4c, -173112-a9e18a3, -173543-29e87e8 (stopped, nr_first/JOURNAL.md); failed predictions on record in JOURNAL.md (V4, V5, V6, V7, V5b), nr_first/JOURNAL.md (E4, E6) and note/JOURNAL.md (N2 item 3) | PASS |
| C20 | STATUS.md, JOURNAL.md and HANDOFF.md are current | STATUS.md, HANDOFF.md rewritten and a JOURNAL.md entry appended by the lead at the end of batch 2a (2026-11-21) | PASS |

## Re-verification on a clean checkout (`nrpic-stage verify`)

`nrpic-stage verify` on 2026-11-21T07:05:39Z, clean export of `7bf8f9da55ee`: **FAIL**. Details: `VERIFY_RESULTS.md`.

| Check | Result | Message |
|---|---|---|
| clean | FAIL | 2 uncommitted paths: commit them first (tracks/F-hills/g2mesh/scripts/card_analysis.py, tracks/F-hills/kerr/) |
| sync | FAIL | main has commits not merged: run nrpic-ctx sync |
| export | PASS | clean export of 7bf8f9da55ee (HEAD) in /data/haiyangw/nrpic/scratch/F-hills/tmp/stage-verify/F-hills-G0-7bf8f9d-20261121T064300Z/tree |
| size | PASS | no committed file of the track above 5 MB |
| note | PASS | tracks/<ID>/note/main.tex present |
| package | PASS | EVIDENCE.md, OPEN.md, CHECKLIST.md present (decision 0012); scoping text: stage/G0/SCOPING.md, novelty/scope/SCOPE.md; REVIEW.md present; verifier's report VERIFIER.md |
| note-pdf | WARN | note/main.pdf is older than the last change of its .tex files |
| style | PASS | 2 style copies equal harness/style/SHA256SUMS (czstyle.py, paperfig.py) |
| fig-script | PASS | 12 figures, each with its script |
| min-figs | PASS | 3 schematics and 9 data figures (brief 13.4 asks at least 2 and 0 at G0) |
| runs | FAIL | 4 of 201 runs have problems |
| run-notes | WARN | 78 runs read with defaults or not fully re-verifiable (nrpic-run lint) |
| status | PASS | STATUS.md has 51 lines |
| rerun | PASS | 12 of 12 scripts and commands ran cleanly in the export |
| compare | PASS | 33 regenerated files compared with the committed ones; 0 differ beyond tolerance (rtol 1e-06, atol 1e-12, PNG rms 0.005) |
| regenerate | PASS | all 24 committed figure files regenerated |

## Figures

| File | Script | Kind (data / schematic) | Looked at (PNG read) |
|---|---|---|---|
| note/figures/fig_constraints.* | note/scripts/fig_constraints.py | data | to be confirmed by the session |
| note/figures/fig_cost.* | note/scripts/fig_cost.py | data | to be confirmed by the session |
| note/figures/fig_geodesic.* | note/scripts/fig_geodesic.py | data | to be confirmed by the session |
| note/figures/fig_newton.* | note/scripts/fig_newton.py | data | to be confirmed by the session |
| note/figures/fig_passage.* | note/scripts/fig_passage.py | data | to be confirmed by the session |
| note/figures/fig_rp_scan.* | note/scripts/fig_rp_scan.py | data | to be confirmed by the session |
| note/figures/fig_single.* | note/scripts/fig_single.py | data | to be confirmed by the session |
| note/figures/fig_smoke.* | note/scripts/fig_smoke.py | data | to be confirmed by the session |
| note/figures/fig_tree.* | note/scripts/fig_tree.py | data | to be confirmed by the session |
| note/figures/schem_architecture.* | note/scripts/schem_architecture.py | schematic | to be confirmed by the session |
| note/figures/schem_dataflow.* | note/scripts/schem_dataflow.py | schematic | to be confirmed by the session |
| note/figures/schem_timeline.* | note/scripts/schem_timeline.py | schematic | to be confirmed by the session |

## Verifier report

`tracks/F-hills/stage/G0/VERIFIER.md` present; its first lines:

> # Independent verification of the G0 plan of F-hills (S12, the Hills mechanism)
> 
> Verifier package `tracks/F-hills/verify_g0/` (wave 3, round 1), 2026-11-20/21, given the
> artefacts and not the conclusions of anyone who checked them before. Evidence labels:
> [VERIFIED] recomputed here (run id) or read at the source (file:line); [BACKGROUND] standard, not
> checked; [JUDGEMENT] mine; [TO VERIFY] open. Predictions and outcomes of every check:
> `verify_g0/JOURNAL.md` (entries 1-8). Paper sources under
> `kb-data/raw/arxiv/<id>/<version>/src/` (read as data).
> 
> **Read before sections 1-3 were written and committed:** `CLAUDE.md`, `harness/RULES.md`
> (nrpic-run), brief lines 466-492, 674-686, 804-822, decisions 0005, 0010, 0013, 0014, 0016,
> 0017, the F-hills rows of `coord/BRIEF_ERRATA.md`; `stage/G0/{SCOPING.md, README.md,

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


Updated 2026-11-21 by the lead (wave 3, batch 2a). Evidence and run ids: `stage/REVIEW-wave3.md`,
`stage/G0/VERIFIER.md`, `stage/G1/STATUS.md`, `JOURNAL.md`, `p1/JOURNAL.md`, `nr_first/JOURNAL.md`.

| Risk | Likelihood | Effect | Watch | Response |
|---|---|---|---|---|
| R15 (new, highest) the members of a binary at m/8 do not hold their orbit: P1's binary (a_b = 5.1 M, members 0.125) merged at t = 48.8 M, before the passage (common horizon 0.268; p1 entry 4, lead run F-20261121-063449-4dcca98); no reference merges (inspiral time about 3400 M) | happened once; cause unknown | P1 is not a Hills passage; every m/8 passage may be invalid; the G2 ladder (m/8, m/12, m/16) may need finer members | the isolated binary at m/8 and m/16 for about 60 M | run that test before any further passage; gauge (eta, mass-scaled damping) and data (`corr`) as the other suspects; re-cost G2 after it |
| R1 compute: G3 (about 500 card-hours) far above the allotments (50 to G1, 120 toward G2: decisions 0014, 0016); the two cards are shared with other users | certain | scan lines take weeks of queue | queue waits of P1's segments (0-40 min) | q = 4 first (0013); object (b) passages are 3-10 times cheaper; chains keep one segment queued; the corrected G2 plan is about 100 card-hours (SCOPING 9, verifier D3) |
| R2 q = 4 at m/16 needs 2864 MeshBlocks | was "certain"; now LOW | - | g2mesh card job (run F-20261120-222810-e408386): 3000 slots ran at 78785 MiB of 81920 | the triple fits one card at `max_nmb_per_rank` 2950-3000 (verifier D5; core-v0.4 interface "about 3100"); q = 10 at m/16 (up to 4544) still does not; R16u (3466) does not |
| R3 a passage stops on the slot limit | low | a segment fails | segment logs | restarts are exact: raise `max_nmb_per_rank` to 3000 |
| R4 member horizon masses drift at m/8: 1.6-2.0e-4 per member mass per unit time in P1 before the merger (1.5-1.9 times the single-puncture rate) | high | energies read against fixed masses biased | horizon summaries | measured masses at each time; resolution decides |
| R5 the references disagree with each other and none is a controlled approximation inside about 12 M (eih T4, reproduced by the lead to 1e-9); the geodesic model is at the edge of its own validity at the first passages' pericentres (a/R_curv reaches 0.2, verifier D7) | certain | no reference is the truth for NR | - | report NR against Newton, HRNA and EIH; quote reference percentages only with their start construction (verifier D2) and from the same start state as the NR data |
| R6 gauge: eta m = 0.25 trackers settle at 0.76 of P/M_ADM; core's mass-scaled profile untested with three holes; E10 outcome not yet recorded | medium | coordinate trajectories biased; may contribute to R15 | E10 (junk_gauge) | gauge-free observables; decide E10 before the next passage |
| R7 horizon finder at about 4 cells per radius at m/8 | certain at m/8 | early masses unusable | hrms column | masses only with hrms < 1e-3 |
| R8 approximate (superposed Bowen-York) data; 1PN inconsistency of the Newtonian start states (eih: binaries e = 0.12-0.21 at 1PN, CM orbit reading-dependent) | medium | outcomes near boundaries data-dependent | junk (J4), eih's 1PN states | 1PN-consistent states built far out (eih `p1_state.py`; the lead's failed local match shows why); constraint solve on the mesh (core) |
| R9 GR reading of the start states: q = 10 input turns at 5.77 M (bound CM), P1's at 9.25 M | certain | "r_p" labels reading-dependent | - | SCOPING 3 amended (verifier D1): every r_p with its GR turning point; q = 10 rebuilt from a GR parabola |
| R10 tracker files truncated on every restart | certain until core fixes it | a chain keeps only its last segment | `trk_keep/` | wrapper `nr_first/scripts/athena_keep_trackers.sh`; reminder to core (2026-11-21) |
| R16 (new) outside kills: segment 7 of P1 was killed by `pkill -x athena` from a session of another project of the account; the chain treated exit 143 as failure and stopped | happened once | lost segments, idle card time | chain `events.log` | run under a run-specific process name (P1 does: `p1-ak03-gpu`); proposal to orch (2026-11-21) |
| R11 chaos near outcome boundaries (2505.03934) | high near edges | single runs not representative | phase windows | robust windows; distributions over phase at G3 |
| R12 object (b) clumps must not relax during about 200 M; Track C's King models at y0 = 0.314 drift at the 1e-2 level over 200 M on M/4 cells (C-sidm answer 2026-11-19) | medium | (b) needs quieter models or finer meshes | C's relaxation runs; core clump-table | ask C for y0 = 0.25-0.30 when (b) starts; G2 relaxation test |
| R13 competition (RIT up to 128:1:1, 2406.11985; BAM, 2505.03934; 2605.20320 three holes from rest) | medium | novelty window short for (a) | citation queries before each gate | (b) is the wider novelty |
| R14 KHSR (1201.4794) not reproduced (verifier D8) | certain until done | F-pre-1 incomplete against the track sheet | - | one KHSR result at G1 with newton3 (processor minutes) |

## Decision requested from the group

Lead's judgement: package complete for an independent review (decision 0016 item 4); harness FAILs are outside the plan (two cut packages' uncommitted files, three wave-2 run directories awaiting a waiver, P1 in flight); the lead does not pass the gate

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
