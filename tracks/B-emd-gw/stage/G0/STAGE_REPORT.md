# Stage report: B-emd-gw G0

Date: 2026-11-15 · branch `track/B-emd-gw` at `0fee5b605028` · checklist
`tracks/B-emd-gw/stage/G0/CHECKLIST.md` (from `nrpic-stage collect`)

## Verdict

**FAIL**. Tag: `stage/B-emd-gw/G0-fail-20261115` (created and pushed by the orchestrator after review, decision 0003).

- 2 checklist items not PASS or NA: C2 OPEN, C18 OPEN
- verify reported FAIL: runs
- no VERIFIER_REPORT.md (step 7: verifier subagent)

## Package documents (decision 0012)

| Document | State |
|---|---|
| `stage/G0/STAGE_REPORT.md` | written by this command |
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
| C2 | The statements of the key references verified in the knowledge base | statements verified at the source in kb-data/raw with file:line (REPORT.md section 5, scope/REFERENCES.md; lead re-read 5 locators); not yet in an indexed KB snapshot (outbox to kb); 2212.00425, 2312.12499 unread | OPEN |
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
| C18 | Verifier subagent (fresh context) wrote VERIFIER_REPORT.md; every number of the Supplemental Material recomputed from the manifests | the lead's re-check REVIEW.md (runs -131016-03b1119, -131027-03b1119) is the owner's; a fresh verifier's VERIFIER_REPORT.md is owed (OPEN.md item 3) | OPEN |
| C19 | Null results and failed runs are on record (manifests and JOURNAL) | failed predictions in the helper journals and JOURNAL.md; failed run B-emd-gw-20261115-120531-40a3597 and stopped run -130926-a1c2237 kept with manifests | PASS |
| C20 | STATUS.md, JOURNAL.md and HANDOFF.md are current | STATUS.md, JOURNAL.md, HANDOFF.md, RISKS.md rewritten 2026-11-15 | PASS |

## Re-verification on a clean checkout (`nrpic-stage verify`)

`nrpic-stage verify` on 2026-11-15T16:57:42Z, clean export of `0fee5b605028`: **FAIL**. Details: `VERIFY_RESULTS.md`.

| Check | Result | Message |
|---|---|---|
| clean | PASS | worktree clean (outside the stage directory being assembled) |
| sync | PASS | main is merged into the branch |
| export | PASS | clean export of 0fee5b605028 (HEAD) in /data/haiyangw/nrpic/scratch/B-emd-gw/tmp/stage-verify/B-emd-gw-G0-0fee5b6-20261115T165645Z/tree |
| size | PASS | no committed file of the track above 5 MB |
| note | PASS | tracks/<ID>/note/main.tex present |
| package | PASS | EVIDENCE.md, OPEN.md, CHECKLIST.md present (decision 0012); scoping text: scope/SCOPE.md; REPORT.md of wave 1 accepted as it is; REVIEW.md present |
| note-pdf | PASS | note/main.pdf committed after the last .tex change |
| style | PASS | 2 style copies equal harness/style/SHA256SUMS (czstyle.py, paperfig.py) |
| fig-script | PASS | 6 figures, each with its script |
| min-figs | PASS | 2 schematics and 4 data figures (brief 13.4 asks at least 2 and 0 at G0) |
| runs | FAIL | 17 of 108 runs have problems |
| run-notes | WARN | 70 runs read with defaults or not fully re-verifiable (nrpic-run lint) |
| status | PASS | STATUS.md has 35 lines |
| rerun | PASS | 6 of 6 scripts and commands ran cleanly in the export |
| compare | PASS | 12 regenerated files compared with the committed ones; 0 differ beyond tolerance (rtol 1e-06, atol 1e-12, PNG rms 0.005) |
| regenerate | PASS | all 12 committed figure files regenerated |

## Figures

| File | Script | Kind (data / schematic) | Looked at (PNG read) |
|---|---|---|---|
| note/figures/fig_baseline.* | note/scripts/fig_baseline.py | data | yes, PNG read (note/JOURNAL.md, N5) |
| note/figures/fig_pancake.* | note/scripts/fig_pancake.py | data | yes, PNG read (note/JOURNAL.md, N5) |
| note/figures/fig_source.* | note/scripts/fig_source.py | data | yes, PNG read (note/JOURNAL.md, N5) |
| note/figures/fig_waves.* | note/scripts/fig_waves.py | data | yes, PNG read (note/JOURNAL.md, N5) |
| note/figures/schem_architecture.* | note/scripts/schem_architecture.py | schematic | yes, PNG read (note/JOURNAL.md, N5) |
| note/figures/schem_timeline.* | note/scripts/schem_timeline.py | schematic | yes, PNG read (note/JOURNAL.md, N5) |

## Verifier report

MISSING: the verifier subagent has not reported.

## Null results and failed runs

- `B-20261115-161656-03d75e1`: failed (exit -15), first_source: initial data of the crossed-wave scan (1, eps, 0), eps = 0, 0.1, 0.3, 1, delta = 0.01, box 4, 64^3, two particles per cell and direction (make_east.py, production deposit settings)
- `B-20261115-164104-886798f`: failed (exit 2), first_source: initial data of the crossed waves eps = 1 (rebuild; the case was cut off in B-20261115-161656-03d75e1), delta = 0.01, box 4, 64^3, two particles per cell and direction
- `B-emd-gw-20261115-120531-40a3597`: failed (exit 1), scouting: TT energy spectrum, TT/non-TT ratio and Weyl parts on the restart dumps of the full-GR cosmology runs dav_c256_n128_t and dav_c256_n128_pcs4bt
- `B-emd-gw-20261115-130926-a1c2237`: stopped (exit None), Lead re-check L1 of the five wave-1 packages: clean git-archive export of commit 2fb3dbff41a1dcba59577c9f8410ff4501f06f2c; all analysis scripts and tests rerun, results compared leaf by leaf with the committed/original results (compare_results.py); four periodic_z4c AthenaK cases re-executed with the release processor executable and compared byte by byte with the original runs

## Open risks


State 2026-11-15 (lead, after wave 1). Likelihood and effect are JUDGEMENT; the watch
column names the measurement that decides. Sources: `scope/SCOPE.md` section 8,
`stage/G0/REVIEW.md`, the helper journals.

| Risk | Likelihood | Effect | Watch | Response |
|---|---|---|---|---|
| R1 Spurious TT power from particle noise after shell crossing (brief line 745). In `cosmo/` the relative momentum-constraint violation is 2.9e-2 at a = 40 and 0.17 at a = 100 and is not shot noise alone (`cosmo/TESTLOG.md` 1404-1415, 1674-1676); one particle per cell leaves the pancake void at M_r 0.21 by a = 15 (run -123852-ea4475c) | high | the post-crossing science claim | jittered-lattice null run (eps = 0, 1 and 8 per cell) against the eps = 0.3 signal; deposit dependence of high-k TT power (56-1100x in gw_diag scouting) | two particles per cell and direction in every production run; eps >= 0.03 (a = 40) to 0.3 (a = 100) [JUDGEMENT bound]; descope to the pancake phase if the floor exceeds the eps = 1 signal at 128 cells |
| R2 Junk TT of conformally flat initial data | certain | biases the pre-crossing comparison | oscillation decays as 1/a (scope run -113632-2960145: 1.8 % of the static value at a = 60) | subtract the computed junk; or initial data with the TT part (request to core) |
| R3 Near field against radiation in a box: box modes may sit below the collapse frequency | medium | the "radiated" signal is a static spin-2 field | virial frequency against c k_1 (0.81-3.57 at L = 4; near field at L = 2 below delta = 0.016) | report rho_K (propagating) and the strain (static) separately; L = 4 first |
| R4 Gauge and hypersurface dependence of h^TT and rho_K (2111.09163 `prd_v1.tex:369-426`); flat Lambda projection exact only at first order | high after shell crossing | a gauge piece mistaken for a signal | late rise of h^TT in the cosmology dumps (a > 600) matches (rms non-TT)^2 (`stage/G0/REVIEW.md`); slicing leg of the convergence test | compare with the second-order gauge estimate; covariant (York) projection; lapse as third convergence leg |
| R5 Gauge shocks of the production lapse (conformal time): in vacuum K/k ~ 0.24 makes a shock within two crossings (runs -114004-0ea0f74, -115139/-115140-42096b9) | medium in collapse | non-convergent metric near caustics | Theta and lapse gradients against resolution | harmonic slicing and 1+log as alternatives; joint gauge work with Track A |
| R6 Black-hole end: delta = 0.05 fails at a = 17.2 (`cosmo/TESTLOG.md` 1842-1852) | certain at large delta | caps the amplitude range | any slicing that passes collapse (Track A) | range to 0.02 until then (stop rule) |
| R7 Output volume and precision: float32 bin loses h ~ 1e-6; rst only double output; 8-67 GB of dumps per run | high | limits cadence and resolution | dump size per run | request to core (double output or in-situ Fourier modes); rst at the GW cadence meanwhile |
| R8 Dependence on core: generator fix (blocks G1 criterion 1), Newtonian mode on main (blocks G1 criterion 2), jitter option, thin boxes, GW output | medium | delays G1 | replies to the outbox of 2026-11-15 | Track B can add the jitter option on a proposal branch; semi-analytic baselines stand meanwhile |
| R9 Literature comparison: the Newtonian box results named by S2 (2212.00425, 2312.12499) not read; 2403.15126 Omega prefactor missed by 144-392 | medium | the "when does GR matter" comparison has no anchor | kb fetch; baseline T7b | kb request; compare with 2605.04487 (consistent) first |
| R10 Particle-number convergence of the background and growth rows not shown in the production configuration (VERIFY.md 1, 2) | medium | G2 criterion | FLRW and test B at 1, 8, 27 per cell | card package of about 0.5 card-h |
| R11 Overlap: 2605.04487 names a fully relativistic treatment as future work (`main_v3.tex:2630`) | medium | novelty of the result | arXiv listings of its authors | keep the plane-symmetric-family null and the GR-minus-weak-field statement as the distinct contribution |

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

## Decision requested from the group

DRAFT by the note helper, for the lead to rewrite: accept sections 1-7 of the scoping text (stage/G0/REPORT.md, scope/SCOPE.md) as the G0 scope of Track B, with the working note v0 and the two schematics now delivered (tracks/B-emd-gw/note/, run B-20261115-165556-a399d4e); still owed before the gate is tagged: the independent verifier's VERIFIER_REPORT.md (C18), the knowledge-base snapshot of the key references (C2), and a verify run of nrpic-stage that passes its run-manifest check (it fails on other helpers' runs in flight and on eight wave-1 manifests without code/env/input fields).
