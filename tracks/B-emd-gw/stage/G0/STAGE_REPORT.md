# Stage report: B-emd-gw G0

Date: 2026-11-15 · branch `track/B-emd-gw` at `26cbf6b699f5` · checklist
`tracks/B-emd-gw/stage/G0/CHECKLIST.md` (from `nrpic-stage collect`)

## Verdict

**FAIL**. Tag: `stage/B-emd-gw/G0-fail-20261115` (created and pushed by the orchestrator after review, decision 0003).

- verify reported FAIL: runs
- no VERIFIER_REPORT.md (step 7: verifier subagent)

## Package documents (decision 0012)

| Document | State |
|---|---|
| `stage/G0/STAGE_REPORT.md` | present |
| `stage/G0/EVIDENCE.md` | present |
| `stage/G0/OPEN.md` | present |
| `stage/G0/CHECKLIST.md` | present |
| `stage/G0/REVIEW.md` | present |
| scoping text | `scope/SCOPE.md` |
| `stage/G0/REPORT.md` | written in wave 1, accepted as it is (decision 0012) |

## Criteria (coord/CHARTER.md, gate G0 of this track)

| # | Criterion | Evidence (run id, figure, KB locator) | Result |
|---|---|---|---|
| C1 | Problem statement, parameter ranges, exit criteria, test plan | REPORT.md sections 1-4 (problem, ranges, exit criteria, test plan mapped to brief lines 845-851); scope/SCOPE.md; item 3 checked twice (runs B-emd-gw-20261115-113102-bc5e082, -131027-03b1119) | PASS |
| C2 | The statements of the key references verified in the knowledge base | statements of the key references read at the source with file:line (REPORT.md section 5, scope/REFERENCES.md); the knowledge base holds them as claims 171-228 and 619-625 of snapshot kb-20261115-44b7406, all 55 locator groups resolved by kb's own check (run kb-20261115-154906-f19880f; kb message 20261115T183741Z); the seven S2 key references the scope had not read (1002.3278, 2212.00425, 2312.12499, 1704.03500, 2012.14016, 2610.08045, 2109.01398) read by the lead at abstract level with locators in EVIDENCE.md (wave-2 section); not yet entered as claims (kb request in the outbox) | PASS |
| C3 | Risk list | tracks/B-emd-gw/RISKS.md (R1-R11); REPORT.md section 6 | PASS |
| C4 | Compute estimate | REPORT.md section 7: measured throughput from runs/cosmo logs (read by the lead), per-run table from run B-emd-gw-20261115-113632-2960145, plan 13-31 card-h of 40; used 0.48 | PASS |
| C5 | Working note v0 | tracks/B-emd-gw/note/main.pdf (10 pages; REVTeX 4.2), sources tracks/B-emd-gw/note/main.tex; figures and tables from registered run B-20261115-165556-a399d4e (supersedes B-20261115-165138-cb53c14 and -165231-9e29328); guide and notation tracks/B-emd-gw/WRITING_GUIDE.md, NOTATION.md; pages read (note JOURNAL.md, outcomes) | PASS |
| C6 | Architecture schematic | tracks/B-emd-gw/note/figures/schem_architecture.png (script tracks/B-emd-gw/note/scripts/schem_architecture.py, run B-20261115-165556-a399d4e); Fig. 2 of the note; looked at | PASS |
| C7 | Stage timeline | tracks/B-emd-gw/note/figures/schem_timeline.png (script tracks/B-emd-gw/note/scripts/schem_timeline.py, run B-20261115-165556-a399d4e); Fig. 6 of the note; REPORT.md section 8 is the table it draws; looked at | PASS |
| C8 | (no track-specific criterion for G0 in the sheet: write the ones agreed with the orchestrator here, or mark NA) | the sheet has no G0-specific criterion; the agreed criteria are the charter's gate items | NA |
| C9 | Track B. The stand-in-matter item is struck (particles do it directly). The multi-code row is covered by the shearing-dust comparison of arXiv:2003.08014 and by full relativity against the Newtonian mode of the code; the N-body baseline runs in that mode. Item 3 of `coord/notes/derivations_to_check.md` is amended as Track B found. (0013) | the ruling of decision 0013 changes the G1 item (stand-in matter struck) and the G2 multi-code row; it adds nothing to G0. The note (Sec. V) and REPORT.md section 3 already state the reworded criteria | NA |
| C10 | Schematic: Track architecture (three states: exists, to be ported, new) | tracks/B-emd-gw/note/figures/schem_architecture.png: exists (green), to be ported (slate), new (red), in three columns (initial data, evolution, analysis); run B-20261115-165556-a399d4e | PASS |
| C11 | Schematic: Stage timeline | tracks/B-emd-gw/note/figures/schem_timeline.png: gates G0-G4 with targets and the needs between gates; run B-20261115-165556-a399d4e | PASS |
| C12 | Data figure: None required | none required | NA |
| C13 | Data figure: Data from the literature may be redrawn | optional; not used | NA |
| C14 | Package documents of decision 0012: STAGE_REPORT.md (nrpic-stage report), EVIDENCE.md, OPEN.md and this CHECKLIST.md in the stage directory; REVIEW.md where the lead rechecked helpers; the scoping text in SCOPE.md or SCOPING.md beside them or in the scope directory, named in the report (no REPORT.md needed) | STAGE_REPORT.md (nrpic-stage report, this wave), EVIDENCE.md, OPEN.md, CHECKLIST.md, REVIEW.md in stage/G0/; scoping text tracks/B-emd-gw/scope/SCOPE.md (named in STAGE_REPORT.md); the wave-1 REPORT.md stays (decision 0012) | PASS |
| C15 | Data figures drawn with /zoom-figure-style from registered run outputs, one script per figure, every PNG looked at | all data figures from registered runs with one script each, project figstyle; looked at by the helpers and by the lead (list in JOURNAL.md entry 2026-11-15T13:05Z and REVIEW.md) | PASS |
| C16 | Schematics drawn with /sleep-paper-figure-style: track architecture (exists / to be ported / new) and the gate timeline | both schematics with harness/style/paperfig.py (unchanged copy in tracks/B-emd-gw/note/scripts/, sha256 as harness/style/SHA256SUMS), sleep-paper style; run B-20261115-165556-a399d4e | PASS |
| C17 | Working note written with /paper-writing; its manuscript checker passed with --compile | written with /paper-writing (guide and notation one level above tracks/B-emd-gw/note); checker check_manuscript.py --compile: 0 undefined references or citations, 0 overfull boxes, every principle clean in the main text; remaining hits are run ids and file names in the ledger appendix and the scripts, accepted by exception 1 of WRITING_GUIDE.md; step 4 of the new-paper procedure (reviewer subagents) not run | PASS |
| C18 | Verifier subagent (fresh context) wrote VERIFIER_REPORT.md; every number of the Supplemental Material recomputed from the manifests | fresh-context verifier helper of wave 2: stage/G0/VERIFIER.md (eight claims C1-C8 recomputed from the artefacts before reading the track's review, commit ad7f707; 7 confirmed, C8 confirmed at emission and not for Omega today, two WRONG side items); its scripts rerun bit for bit by the lead (run B-20261115-190323-2f8806a); every number of the note's ledger regenerated from the manifests by nrpic-stage verify (rerun, compare, regenerate PASS) and checked against the files (note/tables/claims.md). Name: VERIFIER.md as the verifier's brief said, not VERIFIER_REPORT.md (request to orch to accept it) | PASS |
| C19 | Null results and failed runs are on record (manifests and JOURNAL) | failed predictions in the helper journals (first_source P1 as worded, P4, P6 with G; newton_tests P1a, P1b, P2a, H1a, H1c, H1d-3, N1d, N1e) and in the lead's review journal (R5, R6 partly refuted); failed or stopped runs kept with manifests: B-emd-gw-20261115-120531-40a3597, -130926-a1c2237, B-20261115-161656-03d75e1, -164104-886798f, -170149-75036cf, -165526-23d8541, -170526-a53d364; superseded runs kept | PASS |
| C20 | STATUS.md, JOURNAL.md and HANDOFF.md are current | STATUS.md, JOURNAL.md (entry of the lead session 2026-11-15, wave 2), HANDOFF.md and RISKS.md rewritten by the lead at the end of wave 2 | PASS |

## Re-verification on a clean checkout (`nrpic-stage verify`)

`nrpic-stage verify` on 2026-11-15T19:24:43Z, clean export of `20350efd1394`: **FAIL**. Details: `VERIFY_RESULTS.md`.

| Check | Result | Message |
|---|---|---|
| clean | PASS | worktree clean (outside the stage directory being assembled) |
| sync | PASS | main is merged into the branch |
| export | PASS | clean export of 20350efd1394 (HEAD) in /data/haiyangw/nrpic/scratch/B-emd-gw/tmp/stage-verify/B-emd-gw-G0-20350ef-20261115T191231Z/tree |
| size | PASS | no committed file of the track above 5 MB |
| note | PASS | tracks/<ID>/note/main.tex present |
| package | PASS | EVIDENCE.md, OPEN.md, CHECKLIST.md present (decision 0012); scoping text: scope/SCOPE.md; REPORT.md of wave 1 accepted as it is; REVIEW.md present |
| note-pdf | PASS | note/main.pdf committed after the last .tex change |
| style | PASS | 2 style copies equal harness/style/SHA256SUMS (czstyle.py, paperfig.py) |
| fig-script | PASS | 6 figures, each with its script |
| min-figs | PASS | 2 schematics and 4 data figures (brief 13.4 asks at least 2 and 0 at G0) |
| runs | FAIL | 9 of 132 runs have problems |
| run-notes | WARN | 70 runs read with defaults or not fully re-verifiable (nrpic-run lint) |
| status | PASS | STATUS.md has 34 lines |
| rerun | PASS | 6 of 6 scripts and commands ran cleanly in the export |
| compare | PASS | 12 regenerated files compared with the committed ones; 0 differ beyond tolerance (rtol 1e-06, atol 1e-12, PNG rms 0.005) |
| regenerate | PASS | all 12 committed figure files regenerated |

## Figures

| File | Script | Kind (data / schematic) | Looked at (PNG read) |
|---|---|---|---|
| note/figures/fig_baseline.* | note/scripts/fig_baseline.py | data | to be confirmed by the session |
| note/figures/fig_pancake.* | note/scripts/fig_pancake.py | data | to be confirmed by the session |
| note/figures/fig_source.* | note/scripts/fig_source.py | data | to be confirmed by the session |
| note/figures/fig_waves.* | note/scripts/fig_waves.py | data | to be confirmed by the session |
| note/figures/schem_architecture.* | note/scripts/schem_architecture.py | schematic | to be confirmed by the session |
| note/figures/schem_timeline.* | note/scripts/schem_timeline.py | schematic | to be confirmed by the session |

## Verifier report

MISSING: the verifier subagent has not reported.

## Null results and failed runs

- `B-20261115-161656-03d75e1`: failed (exit -15), first_source: initial data of the crossed-wave scan (1, eps, 0), eps = 0, 0.1, 0.3, 1, delta = 0.01, box 4, 64^3, two particles per cell and direction (make_east.py, production deposit settings)
- `B-20261115-164104-886798f`: failed (exit 2), first_source: initial data of the crossed waves eps = 1 (rebuild; the case was cut off in B-20261115-161656-03d75e1), delta = 0.01, box 4, 64^3, two particles per cell and direction
- `B-20261115-170149-75036cf`: failed (exit 1), newton_tests analysis of P1, P2, H1 (pancakes n=16, 32 against Zel'dovich, pm.py, and the discrete-Laplacian growth law)
- `B-emd-gw-20261115-120531-40a3597`: failed (exit 1), scouting: TT energy spectrum, TT/non-TT ratio and Weyl parts on the restart dumps of the full-GR cosmology runs dav_c256_n128_t and dav_c256_n128_pcs4bt
- `B-emd-gw-20261115-130926-a1c2237`: stopped (exit None), Lead re-check L1 of the five wave-1 packages: clean git-archive export of commit 2fb3dbff41a1dcba59577c9f8410ff4501f06f2c; all analysis scripts and tests rerun, results compared leaf by leaf with the committed/original results (compare_results.py); four periodic_z4c AthenaK cases re-executed with the release processor executable and compared byte by byte with the original runs

## Open risks


State 2026-11-15, end of wave 2 (lead). Likelihood and effect are JUDGEMENT; the watch
column names the measurement that decides. Sources: `scope/SCOPE.md` section 8,
`stage/G0/REVIEW.md`, `stage/G0/VERIFIER.md`, `stage/REVIEW-wave2.md`, the helper journals.

| Risk | Likelihood | Effect | Watch | Response |
|---|---|---|---|---|
| R1 Spurious TT power from particle noise after shell crossing (brief line 745). In `cosmo/` the relative momentum-constraint violation is 2.9e-2 at a = 40 and 0.17 at a = 100 (`cosmo/TESTLOG.md` 1404-1415, 1674-1676). The crossed-wave scan on an aligned lattice has no noise to show (null at rounding, run B-20261115-190007-e09a0d2); the floor is unmeasured (verifier weakest point 2) | high | the post-crossing science claim | jittered-lattice null (eps = 0, 1 and 8 per cell) against the eps = 0.3 signal; the jitter option exists on core/requests-b | two particles per cell and direction; eps >= 0.032 (a = 40) to 0.19 (a = 100) [JUDGEMENT bound, corrected crossover 0.289]; descope to the pancake phase if the floor exceeds the eps = 1 signal at 128 cells |
| R2 Junk TT of conformally flat initial data | certain | biases the pre-crossing comparison | now modelled: the box-mode strain follows s g(tau) with the junk to 0.22-0.44 percent for 2 <= a <= 10 (first_source P2, rechecked) | keep the full second-order solution s g(tau) as the reference; initial data with a TT part deferred by core |
| R3 Near field against radiation in a box | measured: high | the box-mode signal before and after shell crossing is a quasi-static spin-2 field, not radiation: rho_kin/rho_grad <= 0.04 (first_source; K1 mode <= 0.013 for a >= 12, lead) | rho_kin against rho_grad per band; virial frequency against c k_1 | report rho_K (propagating) and the strain (static) separately; the radiated signal needs larger boxes (L = 8) or later times; L = 4 stays the first box |
| R4 Gauge and hypersurface dependence of h^TT (2111.09163 `prd_v1.tex:369-426`; 1704.03500 `GW2nd_ApJ.tex:245`) | medium (was high) | a gauge piece mistaken for a signal | spatial-gauge piece G_tot measured: < 1.1 percent of c_+ for a <= 20, ~10 percent near shell crossing; a second spatial gauge agrees after G_tot (difference reduced twelvefold); the wave-1 late rise is not gauge (runs -164616-a6d9477, -171804-42e975b) | report raw and G_tot-corrected strain (adopt gauge_piece_total into gw_diag); slicing piece only bounded (P10); York projection; lapse as third convergence leg |
| R5 Gauge shocks of the production lapse (conformal time): in vacuum K/k ~ 0.24 makes a shock within two crossings | medium in collapse | non-convergent metric near caustics | Theta and lapse gradients against resolution | harmonic and 1+log as alternatives; joint gauge work with Track A (shared test accepted) |
| R6 Black-hole end: delta = 0.05 fails at a = 17.2 (`cosmo/TESTLOG.md` 1842-1852) | certain at large delta | caps the amplitude range | any slicing that passes collapse (Track A: none yet, its message 18:37Z) | range to 0.02 until then (stop rule) |
| R7 Output volume: restart dumps carry the particles (380 MB per dump at 2.1M particles, 12 GB per run) | medium (was high) | limits cadence and resolution | dump size per run | double-precision bin output for z4c exists on core/requests-b; single-precision bin is adequate for the box modes (4e-5 relative) but not for the null of tilde A |
| R8 Dependence on core: generator fix and jitter (on core/requests-b, not on main), species history (N2), OpenMP processor build | medium | delays G1 criterion 1 and the noise null | release of core/requests-b to main | scouting with core's published executables (decision 0013) |
| R9 Literature comparison: 2212.00425, 2312.12499 read at abstract level only; the Omega-today scaling of 2403.15126 is sigma^(5/2) with its own eq. (result_OmZ), not the stated 7/2 (verifier C8); the 144-392 prefactor gap varies as theta^(2/3) | medium | the "when does GR matter" comparison has no quantitative anchor | reading of the papers' spectra; kb claims | compare emitted energies (7/2 holds at emission), not Omega today, until settled |
| R10 Particle-number convergence of the background, growth and first-source rows not shown | medium | G2 criterion | FLRW and test B at 1, 8, 27 per cell; first source at 1, 8, 27 per cell and 128^3 | card package of about 1 card-h |
| R11 Overlap: 2605.04487 names a fully relativistic treatment as future work (`main_v3.tex:2630`); 2312.12499 says the same (`main.tex:115`) | medium | novelty | arXiv listings | keep the plane-symmetric null, the gauge-controlled box-mode strain and the GR-minus-Newton statement per k as the distinct contribution |
| R12 Short second-order comparison window: at delta = 0.01 the strain departs from s g by 1-2 percent at a = 20 and 6-11 percent at a = 40, growing with eps (beyond second order; 2610.08045 `main.tex:40-49`: secular growth of higher orders in matter domination) | certain | pre-crossing accuracy claims limited to a <= 10 | the same scan at delta = 0.0025 | quote the window; extend it with smaller delta; the higher-order departure is itself a result to explain |
| R13 Newtonian reference force error (kh)^2/12 of the seven-point Laplacian (3.2e-3 at kh = 2 pi/32) | certain | biases GR-minus-Newton per mode at the 1e-3 level | core's answer on a fourth-order option | quote it with every comparison or use the spectral pm.py as a second Newtonian reference |

## Decision requested from the group

Accept the G0 scope of Track B (scoping text scope/SCOPE.md as amended in wave 2, with stage/G0/REPORT.md of wave 1), with the products delivered in wave 2: working note v0 and the two schematics (tracks/B-emd-gw/note/, run B-20261115-165556-a399d4e), the fresh verifier's report stage/G0/VERIFIER.md, the key references at the source and in kb snapshot kb-20261115-44b7406, the lead's recheck stage/REVIEW-wave2.md. Every checklist item is PASS or NA in the lead's judgement; the harness verdict is FAIL on two formal points for which rulings are requested in the outbox: the verifier file name (VERIFIER.md, not VERIFIER_REPORT.md) and the runs check (8 wave-1 hand-written manifests without code/env/input fields, 1 run whose outputs were moved into its directory after finish). The lead does not pass the gate; the group decides.

## Scoping text and working note (note helper, wave 2)

- Scoping text: `stage/G0/REPORT.md` sections 1-8 (wave 1, written through the shell and
  accepted by decision 0012) and the detailed scope `tracks/B-emd-gw/scope/SCOPE.md`; risks
  `tracks/B-emd-gw/RISKS.md`; evidence `EVIDENCE.md`; what G0 still lacks `OPEN.md`.
- Working note v0: `tracks/B-emd-gw/note/main.pdf` (10 pages), REVTeX 4.2, written with
  /paper-writing (guide `tracks/B-emd-gw/WRITING_GUIDE.md`, notation
  `tracks/B-emd-gw/NOTATION.md`). It states the problem (the plane-symmetric null, the
  crossed-wave source with its second-order strain, the radiation band, the relativistic
  depth), the set-up and methods, the tests so far with four data figures, and the plan and
  open questions with the timeline. Every number is in its ledger appendix with the run
  that produced it. Figures, schematics and tables: registered run
  B-20261115-165556-a399d4e (earlier runs B-20261115-165138-cb53c14 and
  -165231-9e29328 superseded, kept on record). Package journal with predictions N1-N5 and
  outcomes: `tracks/B-emd-gw/note/JOURNAL.md`.
- Re-verification of this package: `nrpic-stage verify` passes every check of the note
  (rerun of the six scripts in a clean export, regenerated figures equal to the committed
  ones, style copies, PDF newer than the sources). Its `runs` check fails on runs of other
  helpers in flight (8), on eight wave-1 hand-written manifests of the scope and baseline
  packages that lack `code`, `env` and `input` fields, and on one first-source run whose
  moved outputs are outside its `sha256sums.txt`; none of these is a run of the note.

## Where the stage documents and the files disagree (files win)

The note's claims check (`tracks/B-emd-gw/note/tables/claims.md`, run
B-20261115-165556-a399d4e) compared 28 numbers and statements of `REPORT.md`,
`stage/G1/STATUS.md`, `REVIEW.md`, `STATUS.md` and one helper journal with the run outputs:
24 agree at the precision stated, 4 differ.

| Document:line | Stated | Files |
|---|---|---|
| `REPORT.md:88` | lapse = scale factor "to 1e-7 at a = 4 and 36" | 1.9e-7 at a = 4, 7.0e-8 at a = 36 (run B-emd-gw-20261115-115414-7ffbde1) |
| `stage/G1/STATUS.md:22` | errors match the Fourier symbol "to 1 % up to 64 cells" | 9.5 % for the production phase error at 64 cells, the others within 1 % (L1 export of `periodic_z4c/tables/lw_x.json`) |
| `stage/G1/STATUS.md:56` | Hamiltonian constraint "1.6e-9, 1.1e-10, 3.2e-11 at 8, 16, 32 cells over a thousandfold expansion" | those are the values of the first record (t = 100 Mpc/h); at the end (t = 3000 Mpc/h) 3.1e-8, 2.5e-9, 3.0e-9, not falling from 16 to 32 cells; the fourth-order convergence holds for the error of chi (`cosmo/analysis/daverio_a.json`) |
| `stage/G1/STATUS.md:47` | Newtonian mode with quadrupole history "on `core/newton` (tip ce329f5, not on main)" | on main since release core-v0.3 (`coord/INTERFACES/newtonian_mode.md`) |

Wording only: `REPORT.md:50` gives box means as "pancake void" values; `REPORT.md:91`
"plane symmetry to 1e-12" for a largest transverse velocity of 1.25e-12. Superseded
reading: OPEN.md item 9 and RISKS.md R4 describe the late TT rise in the wave-1 cosmology
dumps as a possible second-order gauge piece; run B-20261115-164616-a6d9477 of the
first-source helper finds that piece an order of magnitude below the rise, which sits near
the grid scale (`first_source/JOURNAL.md` lines 158-193).

State after the lead's session of wave 2: `stage/G1/STATUS.md` is rewritten with the
corrected values (lines 22, 47, 56 above); `REPORT.md` (wave 1, accepted as it is by
decision 0012) is left unedited, and this table is its erratum: the lapse equals the scale
factor to 1.9e-7 at a = 4 and 7.0e-8 at a = 36, the box means of line 50 are box means, and
line 91 means a largest transverse velocity of 1.3e-12. OPEN.md item 9 and RISKS.md R4 now
carry the late-rise outcome (rechecked by the lead, run B-20261115-190019-b5f5eb6).

## Lead's assessment (wave 2)

- The verifier's report is `stage/G0/VERIFIER.md` (fresh context, eight claims recomputed
  from the artefacts, written before it read the track's review; its scripts reproduce bit
  for bit in the lead's run B-20261115-190323-2f8806a). The harness looks for the name
  `VERIFIER_REPORT.md`; request `outbox/20261115T191031Z__to-orch__verifier-report-name.md`.
- The `runs` check fails on 9 of 132 runs: 8 wave-1 hand-written manifests without code,
  env and input fields and run B-20261115-164157-40b9f6d, whose outputs were moved into its
  directory after `finish` (the move is recorded in `sha256sums.moved.txt` and in
  `first_source/JOURNAL.md` lines 143-146). Request
  `outbox/20261115T191032Z__to-orch__stage-verify-runs-check.md`. Every other check passes
  on 20350ef, including the rerun of the note's six scripts and the comparison of all twelve
  regenerated figure files.
- The verifier's WRONG and NOT CONFIRMED items and what the track did: `stage/REVIEW-wave2.md`,
  section "verifier" (crossover 0.289 corrected in SCOPE.md; oblique generator fixed by core
  on a branch; Omega-today scaling marked TO VERIFY after reading 2403.15126:1061).
- In the lead's judgement every G0 item is met (CHECKLIST.md: 16 PASS, 4 NA). The lead does
  not pass the gate.
