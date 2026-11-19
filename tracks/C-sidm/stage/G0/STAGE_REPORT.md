# Stage report: C-sidm G0

Date: 2026-11-19 · branch `track/C-sidm` at `476da2886cfd` · checklist
`tracks/C-sidm/stage/G0/CHECKLIST.md` (from `nrpic-stage collect`)

## Verdict

**FAIL**. Tag: `stage/C-sidm/G0-fail-20261119` (created and pushed by the orchestrator after review, decision 0003).

- verify ran on 589237c; files changed since: tracks/C-sidm/stage/G1/STAGE_REPORT.md (run verify again)
- verify reported FAIL: runs

## Package documents (decision 0012)

| Document | State |
|---|---|
| `stage/G0/STAGE_REPORT.md` | present |
| `stage/G0/EVIDENCE.md` | present |
| `stage/G0/OPEN.md` | present |
| `stage/G0/CHECKLIST.md` | present |
| `stage/G0/VERIFIER.md` (verifier's report) | present |
| `stage/G0/REVIEW.md` | present |
| scoping text | `scope/SCOPE.md` |
| `stage/G0/REPORT.md` | written in wave 1, accepted as it is (decision 0012) |

## Criteria (coord/CHARTER.md, gate G0 of this track)

| # | Criterion | Evidence (run id, figure, KB locator) | Result |
|---|---|---|---|
| C1 | Problem statement, parameter ranges, exit criteria, test plan | REPORT.md sections 1 (problem), 3 (parameter ranges), 4 (exit criteria), 5 (test plan against brief rows 843, 844, 852, 853) | PASS |
| C2 | The statements of the key references verified in the knowledge base | REPORT.md section 6: 27 statements re-read by the lead at file:line in kb-data/raw/arxiv sources; in the knowledge base as claims 229-303 (scope/REFERENCES.md) and 304-331 (REPORT section 6), errata 610-618, snapshot kb-20261115-44b7406, with kb's own located/partial check (run kb-20261115-154906-f19880f; kb message 20261115T183741Z index-locators-typos). kb's open point (file name of the astro-ph/0111176 locator) answered: SMBH_SIDM_Xiv2.tex:289-291 of v3 (outbox 2026-11-19 to kb) | PASS |
| C3 | Risk list | tracks/C-sidm/RISKS.md (13 risks), REPORT.md section 7 | PASS |
| C4 | Compute estimate | REPORT.md section 8: unit costs from run C-sidm-20261115-115400-eb8b752 (reproduced in -131135-3077a99); wave 2 16-20 card-h, G2 ~45, G3 80-160. Collision cost measured in wave 2: 3.4-3.9e-9 s per tested pair on one A100, 3.3-6.7e-7 s on one core (runs C-20261115-180525-94ddd22, C-20261115-165500-c67e036); coll_energy = particle costs 1.68 times cell mode per tested pair on a processor (run C-20261119-143146-226b0e0); cluster runs at N = 1e5 on the M/4 mesh 3.42-3.46 s per M on a card (threshold_scan, 1.73 card-h for six 300 M runs); SCAN.md 26-28 card-h for the G2 scan | PASS |
| C5 | Working note v0 | working note v0: tracks/C-sidm/note/main.tex and main.pdf (REVTeX 4.2, 10 pages, compiled with latexmk, every page read), guide and notation tracks/C-sidm/WRITING_GUIDE.md, NOTATION.md; problem, set-up, tests with four data figures and the ledger from runs C-20261115-170415-385069e and C-20261115-171741-0e0da67 (note helper, wave 2); note/README.md | PASS |
| C6 | Architecture schematic | note/figures/schem_architecture.png (paperfig.py; exists / to be ported / new), Fig. 2 of the note; run C-20261115-171741-0e0da67; PNG looked at | PASS |
| C7 | Stage timeline | note/figures/schem_timeline.png (paperfig.py), Fig. 6 of the note; also the table of REPORT.md section 9; run C-20261115-171741-0e0da67; PNG looked at | PASS |
| C8 | (no track-specific criterion for G0 in the sheet: write the ones agreed with the orchestrator here, or mark NA) | the sheet has no G0-specific criterion; the track's exit criteria per gate are in REPORT.md section 4 | NA |
| C9 | Track C. The references and the wording that the lead corrected are taken into `coord/BRIEF_ERRATA.md`; the G2 criterion reads "the collisionless threshold is located with three-way convergence and compared with the turning-point criterion". (0013) | the ruling concerns the G2 wording and the brief errata, not G0: coord/BRIEF_ERRATA.md rows 1.6, 1.8-1.11 carry the corrections of the lead; the note (Sec. II D) and the timeline schematic use the G2 wording of decision 0013 | NA |
| C10 | Schematic: Track architecture (three states: exists, to be ported, new) | note/figures/schem_architecture.png, three states (green exists, slate to be ported, red new); script note/scripts/schem_architecture.py; run C-20261115-171741-0e0da67 | PASS |
| C11 | Schematic: Stage timeline | note/figures/schem_timeline.png; script note/scripts/schem_timeline.py; run C-20261115-171741-0e0da67 | PASS |
| C12 | Data figure: None required | none required | NA |
| C13 | Data figure: Data from the literature may be redrawn | optional; the packages redraw F21 and 2009.08163 values in gravothermal/figs and equilibria/figs | NA |
| C14 | Package documents of decision 0012: STAGE_REPORT.md (nrpic-stage report), EVIDENCE.md, OPEN.md and this CHECKLIST.md in the stage directory; REVIEW.md where the lead rechecked helpers; the scoping text in SCOPE.md or SCOPING.md beside them or in the scope directory, named in the report (no REPORT.md needed) | STAGE_REPORT.md (nrpic-stage report, wave 2), EVIDENCE.md (wave-2 section added), OPEN.md (rewritten for wave 2), CHECKLIST.md, REVIEW.md (wave 1) and ../REVIEW-wave2.md (lead's recheck of the wave-2 helpers, runs C-20261115-193332-48771b4, C-20261115-193751-d3872ff); scoping text tracks/C-sidm/scope/SCOPE.md (verifier findings V4b, V8 corrected in wave 2) with REPORT.md of wave 1 (accepted by decision 0012; numbers corrected in wave 2) | PASS |
| C15 | Data figures drawn with /zoom-figure-style from registered run outputs, one script per figure, every PNG looked at | the stage package figures are the note figures: four data figures, one script each (note/scripts/fig_*.py, czstyle.py), all inputs read from registered runs with their recorded sha256 (63 files), every PNG opened (note/JOURNAL.md N1, N2); nrpic-stage verify: fig-script, rerun, compare, regenerate PASS. The wave-1 package figures (several per script, figstyle) stay as package records | PASS |
| C16 | Schematics drawn with /sleep-paper-figure-style: track architecture (exists / to be ported / new) and the gate timeline | note/figures/schem_architecture.png and schem_timeline.png with note/scripts/paperfig.py (copy equal to harness/style/SHA256SUMS; verify style PASS) | PASS |
| C17 | Working note written with /paper-writing; its manuscript checker passed with --compile | paper-writing checker with --compile (note/README.md): 0 undefined references and citations; main text clean in all 16 checks; remaining hits are run ids and file names in the ledger appendix and data keys in the scripts, accepted by exception 1 of WRITING_GUIDE.md; one overfull box of 1 pt (parameter table). Not done: the reviewer step of a new paper (skill Sec. 10) | PASS |
| C18 | Verifier subagent (fresh context) wrote VERIFIER.md (decision 0016; VERIFIER_REPORT.md accepted too); every number of the Supplemental Material recomputed from the manifests | decision 0016 item 4: G0 is judged with a verifier's report on the plan. The wave-2 verifier (fresh context, own code) wrote stage/G0/VERIFIER.md: claims V1-V8 of the scoping text recomputed (runs C-20261115-170630-1037f6a, C-20261115-170716-e81ba08); its suite reruns byte-identically (lead's run C-20261115-193332-48771b4); its WRONG and NOT CONFIRMED items are fixed (../REVIEW-wave2.md section 5). The note v0 has no Supplemental Material; its ledger appendix (39 rows) is regenerated from the registered JSON by note/scripts/ledger.py, which nrpic-stage verify reruns and compares; the three rows that differed were recomputed by the lead (L11). A fresh verifier of the ledger was not run (stated in OPEN.md) | PASS |
| C19 | Null results and failed runs are on record (manifests and JOURNAL) | failed runs kept with their manifests: wave 1 C-sidm-20261115-120801-38ab057, -121400-d463e1a, superseded -121536, -121811; wave 2 C-20261115-165742-2c645f8 (driver), C-20261115-170221-b1a491c and C-20261115-171137-9e3c807 (exit 1: three TOV-residual checks), C-20261115-170231-4e68455 (KeyError); failed predictions in the helpers' journals (box_tests T4 seed 2, models G2/G4/G5/A1, threshold_scan P3.4, P3.7, P3.8, P3.10, P3.11, Test 4) and in JOURNAL.md | PASS |
| C20 | STATUS.md, JOURNAL.md and HANDOFF.md are current | the wave-2 lead was cut off before rewriting them (its checklist claimed PASS too early); STATUS.md, HANDOFF.md and RISKS.md rewritten and JOURNAL.md appended (entries of 2026-11-19, predictions and outcomes L12-L15) by the wave-2b lead session, in the same commit series as this checklist | PASS |

## Re-verification on a clean checkout (`nrpic-stage verify`)

`nrpic-stage verify` on 2026-11-19T15:45:28Z, clean export of `589237c86781`: **FAIL**. Details: `VERIFY_RESULTS.md`.

| Check | Result | Message |
|---|---|---|
| clean | PASS | worktree clean (outside the stage directory being assembled) |
| sync | PASS | main is merged into the branch |
| export | PASS | clean export of 589237c86781 (HEAD) in /data/haiyangw/nrpic/scratch/C-sidm/tmp/stage-verify/C-sidm-G0-589237c-20261119T154443Z/tree |
| size | PASS | no committed file of the track above 5 MB |
| note | PASS | tracks/<ID>/note/main.tex present |
| package | PASS | EVIDENCE.md, OPEN.md, CHECKLIST.md present (decision 0012); scoping text: scope/SCOPE.md; REPORT.md of wave 1 accepted as it is; REVIEW.md present; verifier's report VERIFIER.md |
| note-pdf | PASS | note/main.pdf committed after the last .tex change |
| style | PASS | 2 style copies equal harness/style/SHA256SUMS (czstyle.py, paperfig.py) |
| fig-script | PASS | 6 figures, each with its script |
| min-figs | PASS | 2 schematics and 4 data figures (brief 13.4 asks at least 2 and 0 at G0) |
| runs | FAIL | 6 of 106 runs have problems |
| run-notes | WARN | 25 runs read with defaults or not fully re-verifiable (nrpic-run lint) |
| status | PASS | STATUS.md has 40 lines |
| rerun | PASS | 6 of 6 scripts and commands ran cleanly in the export |
| compare | PASS | 12 regenerated files compared with the committed ones; 0 differ beyond tolerance (rtol 1e-06, atol 1e-12, PNG rms 0.005) |
| regenerate | PASS | all 12 committed figure files regenerated |

## Figures

| File | Script | Kind (data / schematic) | Looked at (PNG read) |
|---|---|---|---|
| note/figures/fig_box_step.* | note/scripts/fig_box_step.py | data | to be confirmed by the session |
| note/figures/fig_collisions.* | note/scripts/fig_collisions.py | data | to be confirmed by the session |
| note/figures/fig_knudsen.* | note/scripts/fig_knudsen.py | data | to be confirmed by the session |
| note/figures/fig_sequences.* | note/scripts/fig_sequences.py | data | to be confirmed by the session |
| note/figures/schem_architecture.* | note/scripts/schem_architecture.py | schematic | to be confirmed by the session |
| note/figures/schem_timeline.* | note/scripts/schem_timeline.py | schematic | to be confirmed by the session |

## Verifier report

`tracks/C-sidm/stage/G0/VERIFIER.md` present; its first lines:

> # Independent verification of the G0 and G1 material of Track C
> 
> Verifier helper of owner C-sidm, wave 2, 2026-11-15. Fresh reader: I started from the scoping
> text (`tracks/C-sidm/scope/SCOPE.md`), the package derivations and code
> (`gravothermal/`, `equilibria/`, `collide/`, `scope/scripts/`), the raw outputs and the paper
> sources under `kb-data/raw/arxiv/`; the summaries (STATUS, HANDOFF, REVIEW, stage report,
> package journals) were read only after sections 1 and 2 below were written (section 3).
> Predictions: `JOURNAL.md` of this directory (committed in 8e669ce before any of my code ran).
> 
> Runs (processors, 0 card-hours):
> 
> | Run id | What |

## Null results and failed runs

- `C-20261115-165742-2c645f8`: failed (exit 1), box_tests T10 of collide/TESTS.md: bit reproducibility over 1/8/64 MeshBlocks and restarts every 37 cycles, seed control; release CPU executable
- `C-20261115-170221-b1a491c`: failed (exit 1), Offline checks of the N = 10000 models of run C-20261115-170126-b4f74af (M1 King regression at 1e4, M2 F21 solver, M3 per-model checks of equilibria/check_equilibria): tracks/C-sidm/models/JOURNAL.md
- `C-20261115-170231-4e68455`: failed (exit 1), Validation of the growth-rate and collapse-time pipeline (growth.py): synthetic signals and the first paper's cluster runs runs/st/* (read-only), published numbers of tab_outcomes.tex: predictions G1-G6 of tracks/C-sidm/models/JOURNAL.md
- `C-20261115-171137-9e3c807`: failed (exit 1), Offline checks of the N = 100000 models of run C-20261115-170742-84990ed (M1 King regression at 1e4, M2 F21 solver, M3 per-model checks of equilibria/check_equilibria): tracks/C-sidm/models/JOURNAL.md
- `C-20261119-143049-0cf699a`: failed (exit 1), box_rerun R5: T12 collisions in the static homogeneous curved metric (alpha0 0.8, psi0 1.1; static_conformal) against the flat twin and the analytic rate, coll_energy = particle (and cell once), 1e6 particles, 200 steps
- `C-sidm-20261115-120801-38ab057`: failed (exit 1), C-pre-4 Tests 1-2: paper values (2009.08163 table, gr-qc/0601112 Tables 1,2,4), Newtonian limit, King turning point, and the offline checks of the 13 equilibria and their 10^4-particle files

## Open risks


State 2026-11-19 (lead, wave 2b). Numbers carry run ids or locators; see
`stage/G0/REPORT.md` and `stage/REVIEW-wave2.md` for the sources. L = likelihood, E = effect
(high, medium, low).

| Risk | L | E | Watch | Response |
|---|---|---|---|---|
| 1. Stiff collision term at small Kn: N needed grows as Kn^-3 (King threshold: N >= 1.7e3 Kn^-3 for dx <= lambda and 20 per cell); sub-steps ~ dt Gamma/0.1 | high | high | T8 convergence (heat package); max dx/lambda and min N per cell in `coll.hst` | scan stops at Kn_c = 0.3 unless N allows 0.1; the fluid end comes from the exact fluid onset with the Juttner Gamma_1 |
| 2. The collisionless threshold of core-halo families may not sit at the binding-energy maximum (2105.05556 `paper.tex:88-89, 599, 612`) | medium | high | growth rate against Z(0) over 0.4-1.0, both perturbation signs, 1000 M runs | eps_max (Z(0) = 0.5404 at b = 0.1) is a lower bound; G2 wording of decision 0013 |
| 3. The numerical equilibrium drifts more than the stability margin: collisionless King controls on the M/4 mesh move alpha_c by +0.018-0.033 within 200 M (run C-20261115-191420-8538aa4), larger than CC2's distance from the fluid onset (0.0055) and the CC1-CC2 separation (0.0148) (L15) | high (on this mesh) | high | controls of every scan; drift against mesh spacing (run D2) | D2 with one more refinement level and `coll_cell_factor = 2`; read collisional effects relative to a control of the same seed and mesh |
| 4. Physical Kn of relativistic SIDM cores is ~1e-19 (run C-sidm-20261115-115400-eb8b752) against Kn >= 0.3 in the code | certain | high | — | frame the result as the collisionless-to-fluid bridge; physical statements through the Kn -> 0 anchor (Juttner Gamma_1 onset: Z(0) = 0.5331 for F21 b = 0.1, y0 = 0.32143 for King) |
| 5. Card budget: G2 scan 26-28 card-hours (SCAN.md) plus D1-D3 (4-8) against 41.4 left of 45 to the next gate; heat jobs reserve 1.84 | medium | medium | `nrpic-run budget` | D1 first (smallest), scan blocks only after D1-D3 decide the mesh and defect questions |
| 6. Choice of initial model sways the answer: King b = 1 models near the threshold collapse with collisions after 2.5-15 collisions per particle (runs C-20261115-171058-c26cfad ...); F21 b = 0.1 untested in a run | medium | high | relative contraction against the control; distance of each model from both onsets | report every model with its distance from the collisionless and fluid onsets; D3 with a model clearly on the stable side |
| 7. Gravothermal contraction (leading hypothesis for the collisional collapses, JUDGEMENT) makes any King model collapse eventually, so "collapse within 300 M" is no threshold criterion | medium | high | contraction rate per collision against model and Kn | define the collisional threshold by the growth rate of the radial mode or by the time to collapse against the distance from the onset, not by collapse within a fixed time |
| 8. Particle noise and the intrinsic core oscillation near threshold (first paper `tab_outcomes.tex:120`) | high | medium | growth-rate fits over several periods; N = 1e4/1e5/1e6 | three-way convergence of the growth-rate zero, not of a collapse time; growth-rate fit fix still to validate (G1 OPEN item 3) |
| 9. Single seed and non-reproducible card runs: the seed scatter of a collapse time is unmeasured | certain (now) | medium | two seeds in D1 | every collisional comparison with at least two seeds |
| 10. Card executable of core/collisions-2 not shown equivalent to the processor one (CARD_TESTS.log FAIL lines, job 4484) | medium | medium | core's statement (outbox card-tests-collisions-2) | no new collisional card run with it before the statement; the heat card jobs count only after it |
| 11. Equal masses required for exact pairwise conservation and thermalisation (collide `SPEC.md` 4.4) | low | medium | `coll_weights = equal` fatal error | equal-mass sampling for every collisional run |
| 12. Reproducibility with the mesh metric only to rounding between MeshBlock divisions (core `rng.md` 5) | certain | low | T10 with the analytic metric | bitwise claims only for analytic-metric boxes |
| 13. Collapse leaves the static M/4 mesh unable to hold the black hole (non-finite state, exit 0) | certain (static mesh) | medium | constraint norm after collapse | refined mesh with collisions (request to core); excised fraction is a proxy until then |
| 14. Competition: Misner-Sharp group (2601.17117 `SIDM_MS.tex:514`), Gurian and May collisional Boltzmann SIDM (arXiv:2505.15903, fetched, not read) | medium | medium | kb watch | read 2505.15903 before G2; keep the claim to the fully relativistic kinetic 3D calculation |
| 15. One owner allotment of 16 cores shared by two workflows: the lead's analyses wait behind helpers' long runs (wave 2b) | high | low | `nrpic-run` refusals | request to orch (lead core share); run short analyses between helper runs |

## Lead's notes (wave 2b, 2026-11-19)

- The generated verdict FAIL rests on one verify check only: `runs` lists six runs of the
  wave-3a heat helper that were running or queued when verify ran on 589237c
  (C-20261119-144535-2c7b6a4, -144545-c606492, -150335-73fd40f, -150347-e100007,
  -152752-0ffa031, -154032-e450dfc); they are T6-T8 work for G1, not G0 products, and are
  closed by `nrpic-run finish` when they end. All other checks pass (sync, clean, package
  with VERIFIER.md, note-pdf, style, fig-script, min-figs, rerun, compare, regenerate).
  Verify ran with `--no-checksums` (a full checksum pass over the box-test outputs did not
  finish within 20 minutes on the shared machine); the checksums of every run directory are
  in its `sha256sums.txt`, written by `nrpic-run finish`.
- "files changed since" names only the G1 stage report, committed after the verify export.
- C18 is judged PASS under decision 0016 item 4 (verifier's report on the plan); the fresh
  verification of the note's ledger moves to G1 (`OPEN.md` item 1, `../G1/OPEN.md` item 6).
- C20: the wave-2 lead's checklist claimed STATUS, JOURNAL and HANDOFF rewritten before it
  was cut off; they were rewritten in this session.
- G0 is not passed by the track; the decision is the orchestrator's.

## Decision requested from the group

Review the G0 package of C-sidm for a pass under decision 0016 item 4. Every checklist item is PASS or NA. The verifier's report on the plan is VERIFIER.md (fresh context, own code; V1-V8; its WRONG and NOT CONFIRMED items are fixed, REVIEW-wave2.md section 5); a fresh verifier of the note's ledger is moved to G1 (OPEN.md item 1). The three numbers and the locator found by the claims check are corrected in REPORT.md and G1/STATUS.md; STATUS, JOURNAL, HANDOFF and RISKS are of 2026-11-19. The one failed verify check (runs) lists only the six live runs of the wave-3a heat helper (running or queued, closed by nrpic-run finish when they end), none of them a G0 product.

## Notes of the note helper (wave 2)

Written by the helper that made the note package (`tracks/C-sidm/note/`, README there);
kept when `nrpic-stage report` runs again.

- Scoping text: `tracks/C-sidm/scope/SCOPE.md` with `stage/G0/REPORT.md` (wave 1, accepted by
  decision 0012); the working note v0 (`note/main.pdf`) restates the problem, the set-up and
  the tests from registered runs. Where SCOPE.md and the later packages differ, the verifier
  (`VERIFIER.md` V4b, V5) and the lead's REPORT section 2 govern: the fluid window of the
  thermal core is Z(0) = 0.540-0.635 for F21's gas law, and the track's Knudsen number is
  lambda_c/H_c with the rest-mass density (REPORT decision 2).
- Runs of the note package: C-20261115-170415-385069e (N1) and C-20261115-171741-0e0da67 (N2,
  identical numbers; its outputs are committed in `note/figures/`, `note/tables/`). All 63
  input files of the figures and ledger matched the sha256 their runs recorded.
- Differences between the lead's documents and the files (the files win; `note/tables/claims.md`,
  20 of 23 numbers agree): (1) `stage/G1/STATUS.md` item 2 bounds the deviation from F21's
  Table 1 by 1.1e-4 outside R; run C-sidm-20261115-120722-38ab057 has B at 2.43e-4 and eps,
  ec0 at 1.3e-4 at `main.tex:503` (w0 = 4.5). (2) REPORT section 1: "every phase ... at least
  1e5 dynamical times"; run C-sidm-20261115-121412-d463e1a gives a lower bound of 8.5e4 for the
  fastest phase. (3) REPORT section 3: thermal-core models Z(0) = 0.40-0.80 have R/M = 19.8-28.1
  and r_core/M = 1.27-2.56 (run C-sidm-20261115-121748-4e8d6b5), against 20-26 and 1.5-2.1.
  Rounded but counted as agreeing: King solvers agree to 3.5e-8 (STATUS: 3e-8). Locator:
  the 200 M_sun black hole of arXiv:2601.17117 is at `SIDM_MS.tex:481` (REPORT section 6: 476).
- What the failed verify checks are (run on d567429): `clean` failed on files of other helpers
  (threshold_scan) that were uncommitted at that moment; `runs` lists 7 wave-2 runs of other
  helpers that were still running or queued, and the 10 wave-1 manifests of the gravothermal
  package, which declare the schema `nrpic-run-manifest/1` but lack its fields
  `preregistered_in`, `code` and `input`. The warnings (`run-notes`, 25 wave-1 runs) include
  input paths written relative to the main checkout (`wt/C-sidm/...`, `kb-data/...`), which
  verify resolves inside the worktree ("no longer present"), and run
  C-sidm-20261115-120610-b4592be (the 13 particle models), whose recorded inputs
  (`equilibria/check_equilibria.py`, `python/nrpic/io.py`) changed after the run.
  The note's own checks (note, note-pdf, style, fig-script, min-figs, rerun, compare,
  regenerate) passed. Run verify again once the wave-2 runs are finished and committed.
