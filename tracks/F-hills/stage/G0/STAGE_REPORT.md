# Stage report: F-hills G0

Date: 2026-11-15 · branch `track/F-hills` at `b35169ab73b2` · checklist
`tracks/F-hills/stage/G0/CHECKLIST.md` (from `nrpic-stage collect`)

## Verdict

**FAIL**. Tag: `stage/F-hills/G0-fail-20261115` (created and pushed by the orchestrator after review, decision 0003).

- 3 checklist items not PASS or NA: C14 OPEN, C18 OPEN, C20 OPEN
- no VERIFY_RESULTS.json (run nrpic-stage verify)
- no VERIFIER_REPORT.md (step 7: verifier subagent)

## Package documents (decision 0012)

| Document | State |
|---|---|
| `stage/G0/STAGE_REPORT.md` | written by this command |
| `stage/G0/EVIDENCE.md` | present |
| `stage/G0/OPEN.md` | present |
| `stage/G0/CHECKLIST.md` | present |
| `stage/G0/REVIEW.md` | none (needed where the lead rechecked helpers) |
| scoping text | `stage/G0/SCOPING.md`, `novelty/scope/SCOPE.md` |

## Criteria (coord/CHARTER.md, gate G0 of this track)

| # | Criterion | Evidence (run id, figure, KB locator) | Result |
|---|---|---|---|
| C1 | Problem statement, parameter ranges, exit criteria, test plan | SCOPING.md sections 1 (problem), 3 (parameter ranges), 5 (exit criteria G0-G3), 7 (test plan against brief rows 857-859); restated with figures in note/main.pdf Secs. II-IV (note package, wave 2) | PASS |
| C2 | The statements of the key references verified in the knowledge base | SCOPING.md section 8: 15 statements re-read by the lead at file:line in kb-data/raw/arxiv sources (0911.1136, 1804.02911, 2404.16270, 2402.02178, 2406.11985, 0710.0879, 1004.1353); the note package re-read prp.tex:735-738, 846-854, 345-357 and mnras.tex:368-379, 433-441 and article.tex:244-275 (note/JOURNAL.md, ledger appendix). Not through a kb index (outbox 20261115T1507Z__to-kb__*). Helper locators beyond these are not re-read (OPEN.md item 8) | PASS |
| C3 | Risk list | tracks/F-hills/RISKS.md (13 risks; R3 and the 40-card-hour figure of R1 are superseded by core-v0.3 and decision 0014), SCOPING.md section 11 | PASS |
| C4 | Compute estimate | SCOPING.md section 9 from runs F-hills-20261115-131109-634fb86, -131348-634fb86, -131933-907e5fe, -045438-f62d553; recomputed in note figure fig_cost (runs F-20261115-180609-abc9f6e, F-20261115-173543-29e87e8). Correction: the q = 4 m/16 row uses puncture radius 1.2; the inputs use 1.8 (2514/2864/2568 MeshBlocks, 44.8 card-hours; note/tables/claims.md item 14) | PASS |
| C5 | Working note v0 | tracks/F-hills/note/main.tex and main.pdf (REVTeX 4.2, 11 pages, latexmk, every page read); guide and notation tracks/F-hills/WRITING_GUIDE.md, NOTATION.md; problem, set-up, tests with five data figures and the ledger from runs F-20261115-174648-25514db (N1) and F-20261115-180609-abc9f6e (N4); note/README.md | PASS |
| C6 | Architecture schematic | note/figures/schem_architecture.png (paperfig.py; exists / to be ported / new), Fig. 1 of the note; run F-20261115-180609-abc9f6e; PNG looked at | PASS |
| C7 | Stage timeline | note/figures/schem_timeline.png (paperfig.py), Fig. 7 of the note; run F-20261115-180609-abc9f6e; PNG looked at | PASS |
| C8 | (no track-specific criterion for G0 in the sheet: write the ones agreed with the orchestrator here, or mark NA) | the sheet (charter 9.9) has no G0-specific criterion; the track exit criteria per gate are in SCOPING.md section 5 | NA |
| C9 | Track F (amends 0005). Mass ratio four for the convergence study and the first scan line; the passage at mass ratio ten follows when the mesh fits. The first passage of a clump binary comes right after the first black-hole passage. (0013) | the ruling concerns G1-G3 (mass ratio of the convergence study and scan lines, timing of object (b)); followed already: the P1 input of wave 2 is at q = 4 (nr_first/inputs/p1_q4.athinput), the note plan (Sec. V, Fig. 7) and Sec. II C use it | NA |
| C10 | Schematic: Track architecture (three states: exists, to be ported, new) | note/figures/schem_architecture.png, three states (green exists, slate to be ported, red new); script note/scripts/schem_architecture.py; run F-20261115-180609-abc9f6e | PASS |
| C11 | Schematic: Stage timeline | note/figures/schem_timeline.png; script note/scripts/schem_timeline.py; run F-20261115-180609-abc9f6e | PASS |
| C12 | Data figure: None required | none required at G0; five data figures exist anyway (C15) | NA |
| C13 | Data figure: Data from the literature may be redrawn | optional; the note marks only values printed in the papers' text (with locators) and keeps digitised third-party curves out of committed figures | NA |
| C14 | Package documents of decision 0012: STAGE_REPORT.md (nrpic-stage report), EVIDENCE.md, OPEN.md and this CHECKLIST.md in the stage directory; REVIEW.md where the lead rechecked helpers; the scoping text in SCOPE.md or SCOPING.md beside them or in the scope directory, named in the report (no REPORT.md needed) | STAGE_REPORT.md (nrpic-stage report, wave 2), EVIDENCE.md, OPEN.md, CHECKLIST.md present; scoping text SCOPING.md beside them. No REVIEW.md: the lead rechecked the helpers (SCOPING.md section 10, JOURNAL.md V1-V7) but did not write that file; the lead adds it or points to section 10. EVIDENCE.md and OPEN.md are of wave 1 (OPEN items 1, 6 and the G0 products are now addressed; the lead updates them) | OPEN |
| C15 | Data figures drawn with /zoom-figure-style from registered run outputs, one script per figure, every PNG looked at | five data figures of the note, one script each (note/scripts/fig_*.py, czstyle.py copy equal to harness/style/SHA256SUMS), inputs read from registered run outputs with their recorded sha256 (26 files; one wave-1 run without checksums, said so), every PNG opened (note/JOURNAL.md N1-N4). The wave-1 package figures (newton3, geodesic_binary, three_punctures, checks) stay as package records | PASS |
| C16 | Schematics drawn with /sleep-paper-figure-style: track architecture (exists / to be ported / new) and the gate timeline | note/figures/schem_architecture.png and schem_timeline.png with note/scripts/paperfig.py (copy equal to harness/style/SHA256SUMS) | PASS |
| C17 | Working note written with /paper-writing; its manuscript checker passed with --compile | paper-writing checker with --compile (note/README.md): 0 undefined references and citations, 0 overfull boxes; main text clean in all 16 checks; remaining hits are run ids in the ledger appendix and data keys in the scripts, accepted by exception 1 of WRITING_GUIDE.md. Not done: the reviewer step of a new paper (skill Sec. 10) | PASS |
| C18 | Verifier subagent (fresh context) wrote VERIFIER_REPORT.md; every number of the Supplemental Material recomputed from the manifests | no VERIFIER_REPORT.md. A wave-2 second-check helper (stage/G0/JOURNAL.md, stage/G0/second_check/) checks the novelty verdict and the V6/V7 disagreement with its own code; its outcome was not committed when this checklist was filled. The note ledger was checked against the files by note/scripts/ledger.py (13 of 17 lead numbers agree, 2 differ, 2 superseded: note/tables/claims.md), not by a fresh verifier | OPEN |
| C19 | Null results and failed runs are on record (manifests and JOURNAL) | failed and stopped runs kept: wave 1 in EVIDENCE.md (F-hills-20261115-045124-ae6bca8, -125858-0232c4c, -131944-360a12e, -143824-2c937bc, -133009-2f7ad7f, -133013-2f7ad7f, -133034-bf31889); wave 2 F-20261115-173719-923135a (failed), F-20261115-173106-57c4b4c, -173112-a9e18a3, -173543-29e87e8 (stopped, nr_first/JOURNAL.md); failed predictions on record in JOURNAL.md (V4, V5, V6, V7, V5b), nr_first/JOURNAL.md (E4, E6) and note/JOURNAL.md (N2 item 3) | PASS |
| C20 | STATUS.md, JOURNAL.md and HANDOFF.md are current | STATUS.md, JOURNAL.md, HANDOFF.md describe the end of wave 1 (multi-puncture not released, allotment 40); the wave-2 results are not in them yet; the lead rewrites them at the end of wave 2 (helpers do not edit them) | OPEN |

## Re-verification on a clean checkout (`nrpic-stage verify`)

Not run: `harness/bin/nrpic-stage verify F-hills G0`.

## Figures

| File | Script | Kind (data / schematic) | Looked at (PNG read) |
|---|---|---|---|
| note/figures/fig_cost.* | note/scripts/fig_cost.py | data | yes (note/JOURNAL.md N1-N4; committed PNG byte-identical to the draft opened) |
| note/figures/fig_geodesic.* | note/scripts/fig_geodesic.py | data | yes (note/JOURNAL.md N1-N4; committed PNG byte-identical to the draft opened) |
| note/figures/fig_newton.* | note/scripts/fig_newton.py | data | yes (note/JOURNAL.md N1-N4; committed PNG byte-identical to the draft opened) |
| note/figures/fig_passage.* | note/scripts/fig_passage.py | data | yes (note/JOURNAL.md N1-N4; committed PNG byte-identical to the draft opened) |
| note/figures/fig_rp_scan.* | note/scripts/fig_rp_scan.py | data | yes (note/JOURNAL.md N1-N4; committed PNG byte-identical to the draft opened) |
| note/figures/schem_architecture.* | note/scripts/schem_architecture.py | schematic | yes (note/JOURNAL.md N1-N4; committed PNG byte-identical to the draft opened) |
| note/figures/schem_timeline.* | note/scripts/schem_timeline.py | schematic | yes (note/JOURNAL.md N1-N4; committed PNG byte-identical to the draft opened) |

## Verifier report

MISSING: the verifier subagent has not reported.

## Null results and failed runs

- `F-20261115-173106-57c4b4c`: stopped (exit -15), nr_first E1: MeshBlock counts of the q = 4 three-black-hole data at m/4, m/8, m/16 and of the single-puncture input at m/8, m/16 after the wave-zone refinement (16 cycles)
- `F-20261115-173112-a9e18a3`: stopped (exit -15), nr_first E2 (C0): Hamiltonian residual of the q = 4 three-black-hole data at t = 0, corrections approx/none at m/4, m/8, m/16 and plain sum at m/8; first tracker and horizon rows (one cycle, m/8 approx)
- `F-20261115-173543-29e87e8`: stopped (exit -15), nr_first E1: MeshBlock counts of the q = 4 three-black-hole data at m/4, m/8, m/16 and of the single-puncture input at m/8, m/16 after the wave-zone refinement (16 cycles)
- `F-20261115-173719-923135a`: failed (exit 1), nr_first E4 test 1: readers of trackers, horizons and member energies on a synthetic full-Newton q = 4 trajectory written in AthenaK formats with a restart overlap
- `F-20261115-174432-291868f`: failed (exit 1), nr_first E2: c0_constraints.py on the approx m/8 case of C0 (script check, partial)
- `F-20261115-174959-9e8a361`: failed (exit -15), newton3 finite-q rerun with corrected member energies (M/m=10,30,100,1000; coplanar and isotropic; old definition kept in the same run)
- `F-20261115-175542-b49d687`: failed (exit 1), second check SC0 (a-c): self-tests of the independent Newton and HRNA integrators (geodesic invariants, Kepler, full three-body conservation)
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


Updated 2026-11-15 by the lead. Evidence and run ids: `stage/G0/SCOPING.md`, `JOURNAL.md`.

| Risk | Likelihood | Effect | Watch | Response |
|---|---|---|---|---|
| R1 compute: G2 (about 120 card-hours) and G3 (about 500) exceed the 40 of decision 0006; G1 fits with no margin | certain | scan lines and convergence not done | allotment answer from orch/user | request filed; q = 4 for convergence and the first scan line; object (b) passages are 3-10 times cheaper |
| R2 q = 10 convergence does not fit one card (m/16: 2654-4544 MeshBlocks; about 3000 slots; no MPI) | certain on the present build | G2 at q = 10 impossible | core's answer (two cards or 32^3 blocks) | convergence at q = 4; request to core |
| R3 core capability not released (`core/multi-puncture` not on main, not in CLAUDE.md) | medium | G1 runs cannot start | core and orch replies | runs fully specified (stage/G1/STATUS.md) so they start the day it lands |
| R4 a member plunges into the heavy hole (geodesic reference: 94 percent of phases at r_p = 8 M) | high | a 20:1 merger at m/8 inside the passage; finder and refinement must follow it | P1 trackers and horizons near t = 80-120 | heavy finder follows the merged horizon; request a pairwise common-horizon trigger; restart files every 5 M |
| R5 the two references disagree in kind at q = 10 (HRNA holds the hole fixed; Newton has no plunge) | certain | neither is a truth for the NR comparison | V6/V7 | report NR against both; restart both from the NR state at t = 60; use q -> large limits only as checks |
| R6 member gauge (shift_eta = 2 gives eta m = 0.1) and tracker lag (0.48-0.61 of P/M_ADM over 10-40 M for eta m = 2, core) | medium | coordinate trajectories and binding energies biased for tens of M | R4 run | calibrate f(t); gauge-free observables (asymptotic speeds, horizon masses, energy balance) |
| R7 approximate (superposed Bowen-York) data change the outcome; junk does not converge (1004.1353 Punc_N.tex:185-194, 1238-1261) | medium | outcome near boundaries data-dependent | R0, R2; horizon masses vs closed form | decision rule of three_punctures PLAN section 5; constraint solve on the mesh (decision 0010 item 4) before G3 |
| R8 chaos near outcome boundaries (2505.03934) | high near edges | single runs not representative | phase windows in both references | choose phases inside robust windows; distributions over phase at G3 |
| R9 newton3 energies at finite q not conserved (V5b) | certain until fixed | wrong Newtonian energies at q <= 100 (classes unaffected away from E = 0) | - | barycentric definition; rerun finiteq, P3, three_punctures scans (next wave) |
| R10 m/8 is a scouting resolution (core: horizon masses scatter by 1 percent in the first 2.5 M) | high | outcome near boundaries resolution-dependent | G2 triple at q = 4 | report boundaries as intervals |
| R11 object (b) clumps must be mildly relativistic (m/R > 0.044 at a_b = 30 r_gb; Roche factor unverified) and must not relax during about 200 M | medium | (b) needs larger a_b or more particles | Track C models; G2 relaxation test | request to C-sidm; a_b = 60 r_gb fallback (0.022) |
| R12 competition: RIT plans up to 128:1:1 (2406.11985 TBH3.tex:707-711); BAM scatters N black holes (2505.03934) | medium | novelty window short for (a) | citation queries before each gate | (b) is the wider novelty; move it forward (proposal to orch) |
| R13 novelty verdict and baselines not checked by a second agent | - | gate review may reject | orch | request filed |

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

## Decision requested from the group

One paragraph: accept G0 of F-hills, or what is missing.

TO WRITE by the track before the package is submitted (`nrpic-stage report ... --decision "..."`).
