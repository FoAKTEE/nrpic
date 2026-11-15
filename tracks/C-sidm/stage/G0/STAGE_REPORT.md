# Stage report: C-sidm G0

Date: 2026-11-15 · branch `track/C-sidm` at `41dd4a719ba1` · checklist
`tracks/C-sidm/stage/G0/CHECKLIST.md` (from `nrpic-stage collect`)

## Verdict

**FAIL**. Tag: `stage/C-sidm/G0-fail-20261115` (created and pushed by the orchestrator after review, decision 0003).

- 2 checklist items not PASS or NA: C18 OPEN, C20 OPEN
- verify ran on d567429; files changed since: tracks/C-sidm/models/figures.py, tracks/C-sidm/runs/C-20261115-172003-6422b6a/manifest.json, tracks/C-sidm/threshold_scan/SCAN.md, tracks/C-sidm/threshold_scan/analyze.py (run verify again)
- verify reported FAIL: clean, runs
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
| C1 | Problem statement, parameter ranges, exit criteria, test plan | REPORT.md sections 1 (problem), 3 (parameter ranges), 4 (exit criteria), 5 (test plan against brief rows 843, 844, 852, 853) | PASS |
| C2 | The statements of the key references verified in the knowledge base | REPORT.md section 6: 27 statements re-read by the lead at file:line in kb-data/raw/arxiv sources; not yet through a kb index (OPEN.md item 5, outbox to kb) | PASS |
| C3 | Risk list | tracks/C-sidm/RISKS.md (13 risks), REPORT.md section 7 | PASS |
| C4 | Compute estimate | REPORT.md section 8: unit costs from run C-sidm-20261115-115400-eb8b752 (reproduced in -131135-3077a99); wave 2 16-20 card-h, G2 ~45, G3 80-160; collision cost unmeasured | PASS |
| C5 | Working note v0 | working note v0: tracks/C-sidm/note/main.tex and main.pdf (REVTeX 4.2, 10 pages, compiled with latexmk, every page read), guide and notation tracks/C-sidm/WRITING_GUIDE.md, NOTATION.md; problem, set-up, tests with four data figures and the ledger from runs C-20261115-170415-385069e and C-20261115-171741-0e0da67 (note helper, wave 2); note/README.md | PASS |
| C6 | Architecture schematic | note/figures/schem_architecture.png (paperfig.py; exists / to be ported / new), Fig. 2 of the note; run C-20261115-171741-0e0da67; PNG looked at | PASS |
| C7 | Stage timeline | note/figures/schem_timeline.png (paperfig.py), Fig. 6 of the note; also the table of REPORT.md section 9; run C-20261115-171741-0e0da67; PNG looked at | PASS |
| C8 | (no track-specific criterion for G0 in the sheet: write the ones agreed with the orchestrator here, or mark NA) | the sheet has no G0-specific criterion; the track's exit criteria per gate are in REPORT.md section 4 | NA |
| C9 | Track C. The references and the wording that the lead corrected are taken into `coord/BRIEF_ERRATA.md`; the G2 criterion reads "the collisionless threshold is located with three-way convergence and compared with the turning-point criterion". (0013) | the ruling concerns the G2 wording and the brief errata, not G0: coord/BRIEF_ERRATA.md rows 1.6, 1.8-1.11 carry the corrections of the lead; the note (Sec. II D) and the timeline schematic use the G2 wording of decision 0013 | NA |
| C10 | Schematic: Track architecture (three states: exists, to be ported, new) | note/figures/schem_architecture.png, three states (green exists, slate to be ported, red new); script note/scripts/schem_architecture.py; run C-20261115-171741-0e0da67 | PASS |
| C11 | Schematic: Stage timeline | note/figures/schem_timeline.png; script note/scripts/schem_timeline.py; run C-20261115-171741-0e0da67 | PASS |
| C12 | Data figure: None required | none required | NA |
| C13 | Data figure: Data from the literature may be redrawn | optional; the packages redraw F21 and 2009.08163 values in gravothermal/figs and equilibria/figs | NA |
| C14 | Package documents of decision 0012: STAGE_REPORT.md (nrpic-stage report), EVIDENCE.md, OPEN.md and this CHECKLIST.md in the stage directory; REVIEW.md where the lead rechecked helpers; the scoping text in SCOPE.md or SCOPING.md beside them or in the scope directory, named in the report (no REPORT.md needed) | STAGE_REPORT.md (nrpic-stage report, this wave), EVIDENCE.md, OPEN.md, CHECKLIST.md, REVIEW.md present; scoping text tracks/C-sidm/scope/SCOPE.md with REPORT.md of wave 1 (accepted by decision 0012); EVIDENCE.md and OPEN.md are of wave 1 (OPEN items 1, 2, 4 are now closed by the note package; the lead updates them) | PASS |
| C15 | Data figures drawn with /zoom-figure-style from registered run outputs, one script per figure, every PNG looked at | the stage package figures are the note figures: four data figures, one script each (note/scripts/fig_*.py, czstyle.py), all inputs read from registered runs with their recorded sha256 (63 files), every PNG opened (note/JOURNAL.md N1, N2); nrpic-stage verify: fig-script, rerun, compare, regenerate PASS. The wave-1 package figures (several per script, figstyle) stay as package records | PASS |
| C16 | Schematics drawn with /sleep-paper-figure-style: track architecture (exists / to be ported / new) and the gate timeline | note/figures/schem_architecture.png and schem_timeline.png with note/scripts/paperfig.py (copy equal to harness/style/SHA256SUMS; verify style PASS) | PASS |
| C17 | Working note written with /paper-writing; its manuscript checker passed with --compile | paper-writing checker with --compile (note/README.md): 0 undefined references and citations; main text clean in all 16 checks; remaining hits are run ids and file names in the ledger appendix and data keys in the scripts, accepted by exception 1 of WRITING_GUIDE.md; one overfull box of 1 pt (parameter table). Not done: the reviewer step of a new paper (skill Sec. 10) | PASS |
| C18 | Verifier subagent (fresh context) wrote VERIFIER_REPORT.md; every number of the Supplemental Material recomputed from the manifests | the wave-2 verifier (fresh context) wrote stage/G0/VERIFIER.md, not VERIFIER_REPORT.md: claims V1-V8 of the scoping text recomputed with its own code (runs C-20261115-170630-1037f6a, C-20261115-170716-e81ba08); V4b (fluid window of SCOPE.md section 1) and V5 (three Knudsen conventions) found wrong or open. The numbers of the note ledger were checked against the files by note/scripts/ledger.py (20 of 23 lead numbers agree; three differ, note/tables/claims.md) but not by a fresh verifier. The lead decides whether VERIFIER.md stands for VERIFIER_REPORT.md | OPEN |
| C19 | Null results and failed runs are on record (manifests and JOURNAL) | failed runs kept: C-sidm-20261115-120801-38ab057 (failed check), -121400-d463e1a (defect), superseded -121536, -121811; failed predictions in the helpers' journals and lead outcome L1 in JOURNAL.md | PASS |
| C20 | STATUS.md, JOURNAL.md and HANDOFF.md are current | STATUS.md, JOURNAL.md, HANDOFF.md describe the end of wave 1 (lead session); the wave-2 results (note, verifier, box tests, threshold scan) are not in them yet; the lead rewrites them at the end of wave 2 (helpers do not edit them) | OPEN |

## Re-verification on a clean checkout (`nrpic-stage verify`)

`nrpic-stage verify` on 2026-11-15T17:21:41Z, clean export of `d567429c4283`: **FAIL**. Details: `VERIFY_RESULTS.md`.

| Check | Result | Message |
|---|---|---|
| clean | FAIL | 2 uncommitted paths: commit them first (tracks/C-sidm/threshold_scan/analyze.py, tracks/C-sidm/threshold_scan/SCAN.md) |
| sync | PASS | main is merged into the branch |
| export | PASS | clean export of d567429c4283 (HEAD) in /data/haiyangw/nrpic/scratch/C-sidm/tmp/stage-verify/C-sidm-G0-d567429-20261115T171935Z/tree |
| size | PASS | no committed file of the track above 5 MB |
| note | PASS | tracks/<ID>/note/main.tex present |
| package | PASS | EVIDENCE.md, OPEN.md, CHECKLIST.md present (decision 0012); scoping text: scope/SCOPE.md; REPORT.md of wave 1 accepted as it is; REVIEW.md present |
| note-pdf | PASS | note/main.pdf committed after the last .tex change |
| style | PASS | 2 style copies equal harness/style/SHA256SUMS (czstyle.py, paperfig.py) |
| fig-script | PASS | 6 figures, each with its script |
| min-figs | PASS | 2 schematics and 4 data figures (brief 13.4 asks at least 2 and 0 at G0) |
| runs | FAIL | 17 of 57 runs have problems |
| run-notes | WARN | 25 runs read with defaults or not fully re-verifiable (nrpic-run lint) |
| status | PASS | STATUS.md has 40 lines |
| rerun | PASS | 6 of 6 scripts and commands ran cleanly in the export |
| compare | PASS | 12 regenerated files compared with the committed ones; 0 differ beyond tolerance (rtol 1e-06, atol 1e-12, PNG rms 0.005) |
| regenerate | PASS | all 12 committed figure files regenerated |

## Figures

| File | Script | Kind (data / schematic) | Looked at (PNG read) |
|---|---|---|---|
| note/figures/fig_box_step.* | note/scripts/fig_box_step.py | data | yes (note/JOURNAL.md N1, N2) |
| note/figures/fig_collisions.* | note/scripts/fig_collisions.py | data | yes (note/JOURNAL.md N1, N2) |
| note/figures/fig_knudsen.* | note/scripts/fig_knudsen.py | data | yes (note/JOURNAL.md N1, N2) |
| note/figures/fig_sequences.* | note/scripts/fig_sequences.py | data | yes (note/JOURNAL.md N1, N2) |
| note/figures/schem_architecture.* | note/scripts/schem_architecture.py | schematic | yes (note/JOURNAL.md N1, N2) |
| note/figures/schem_timeline.* | note/scripts/schem_timeline.py | schematic | yes (note/JOURNAL.md N1, N2) |

## Verifier report

No file of that name. The wave-2 verifier of C-sidm (fresh context) wrote `stage/G0/VERIFIER.md` (runs C-20261115-170630-1037f6a and C-20261115-170716-e81ba08): claims V1-V8 of the scoping text recomputed with independent code; V1-V4, V6-V8 confirmed, V4b (the fluid window of `scope/SCOPE.md` section 1) wrong at its upper end, V5 (one Knudsen number) not confirmed. Whether it stands for `VERIFIER_REPORT.md` is the lead's decision (checklist C18).

## Null results and failed runs

- `C-20261115-165742-2c645f8`: failed (exit 1), box_tests T10 of collide/TESTS.md: bit reproducibility over 1/8/64 MeshBlocks and restarts every 37 cycles, seed control; release CPU executable
- `C-20261115-170221-b1a491c`: failed (exit 1), Offline checks of the N = 10000 models of run C-20261115-170126-b4f74af (M1 King regression at 1e4, M2 F21 solver, M3 per-model checks of equilibria/check_equilibria): tracks/C-sidm/models/JOURNAL.md
- `C-20261115-170231-4e68455`: failed (exit 1), Validation of the growth-rate and collapse-time pipeline (growth.py): synthetic signals and the first paper's cluster runs runs/st/* (read-only), published numbers of tab_outcomes.tex: predictions G1-G6 of tracks/C-sidm/models/JOURNAL.md
- `C-20261115-171137-9e3c807`: failed (exit 1), Offline checks of the N = 100000 models of run C-20261115-170742-84990ed (M1 King regression at 1e4, M2 F21 solver, M3 per-model checks of equilibria/check_equilibria): tracks/C-sidm/models/JOURNAL.md
- `C-sidm-20261115-120801-38ab057`: failed (exit 1), C-pre-4 Tests 1-2: paper values (2009.08163 table, gr-qc/0601112 Tables 1,2,4), Newtonian limit, King turning point, and the offline checks of the 13 equilibria and their 10^4-particle files

## Open risks


State 2026-11-15 (lead, wave 1). Numbers carry run ids or locators; see
`stage/G0/REPORT.md` for the sources. L = likelihood, E = effect (high, medium, low).

| Risk | L | E | Watch | Response |
|---|---|---|---|---|
| 1. Stiff collision term at small Kn: N needed grows as Kn^-3 (King threshold: N >= 1.7e3 Kn^-3 for dx <= lambda and 20 per cell, 2.3e4 Kn^-3 for dx <= lambda/3; Kn = 0.1 needs 1.7e6-2.3e7); sub-steps ~ dt Gamma/0.1 | high | high | T2 cost per pair; T8 convergence in dx, dt, coll_pmax; max dx/lambda and min N per cell in `coll.hst` | scan stops at Kn_c = 0.3 unless N allows 0.1; the fluid end comes from the exact fluid onset (REPORT decision 3); re-scope rule of REPORT section 4 |
| 2. The collisionless threshold of core-halo families may not sit at the binding-energy maximum (2105.05556 `paper.tex:88-89, 612`: two stability changes for some models) | medium | high | growth rate against Z(0) over the whole range 0.4-1.0, both perturbation signs, runs of 1000 M | treat eps_max (Z(0) = 0.5404 at b = 0.1) as a lower bound; G2 wording proposed to orch (outbox brief-corrections item 4) |
| 3. The collision operator is not in the code: `core/collisions` has no commit beyond the rng merge (checked 2026-11-15); G1 is blocked on core | high (now) | high | `git log core/collisions`; `tracks/core/interfaces/collisions.md` | outbox request to core with the smallest acceptable answer (commit + T0); the track's tests and pipelines are ready to run within a day |
| 4. Physical Kn of relativistic SIDM cores is ~1e-19 (200 M_sun, 5 cm^2/g; run C-sidm-20261115-115400-eb8b752) against Kn >= 0.3 in the code: the scan cannot sample the physical parameter | certain | high | — | frame the result as the collisionless-to-fluid bridge; every physical statement through the Kn -> 0 anchor (fluid onset with the Juttner Gamma_1; optional GR-hydro view requested from core) |
| 5. Card budget: G2 ~45 and G3 80-160 card-hours against 20 allotted (decision 0006); the cost of a collision is unmeasured | high | medium | `nrpic-run budget` (once it reads the hand manifests); T2 cost measurement | request to orch (outbox gpu-allotment); minimum G3 version with three Kn values |
| 6. Choice of initial model sways the answer: monoenergetic (no envelope, R/H_c = 3.5) and King b = 1 collapse completely when collisionless (2009.08163 `paper.tex:1190-1193`); whether F21 b = 0.1 (R/H_c = 21-36) leaves an envelope is open | medium | high | mass outside the horizon at the end of collisionless F21 runs | primary family F21 b = 0.1 (REPORT decision 1); report all families; runs long enough for conduction-driven envelope expansion |
| 7. Which fluid onset anchors Kn -> 0: F21's gamma = 1 + p/u gives Z(0) = 0.6348 (b = 0.1), the trial criterion 0.7500, fixed 5/3 0.68-0.78; the Juttner Gamma_1 is lower and not computed | medium | medium | the Gamma_1 onset (OPEN item 6) | compute it before G2; report the spread as a systematic of the Kn -> 0 end |
| 8. Particle noise and the intrinsic core oscillation near threshold: collapse times at 1e4 particles are 1.4-1.8 times those at 2e6 (first paper, `tab_outcomes.tex:120`); the core oscillation (period near the core radial period) overlaps the unstable mode | high | medium | growth-rate fits over several periods; N = 1e4/1e5/1e6 | three-way convergence of the growth-rate zero, not of a collapse time |
| 9. Unequal macroparticle masses cannot be both exactly conserving and correctly thermalising pairwise (collide `SPEC.md` 4.4, [JUDGEMENT]) | low (if equal masses) | medium | `coll_weights = equal` fatal error | equal-mass sampling for every collisional run (equilibria samples are equal-mass) |
| 10. Reproducibility with the mesh metric is only to rounding between MeshBlock divisions (core `rng.md` section 5), so a collision decision can flip | certain | low | T10 with the analytic metric (bitwise); statistical comparisons otherwise | state bitwise claims only for analytic-metric boxes |
| 11. Excision and collisions: particles removed at the lapse threshold must not collide across the excision surface | low | medium | conservation budget of the collision step near horizon formation | operator runs after excision (SPEC 4.7, core draft 3.10) |
| 12. Competition: the Misner-Sharp group announces baryons and accretion next (2601.17117, read by scope at `SIDM_MS.tex:514`); a collisional Boltzmann SIDM treatment exists ("Gurian:2025zpc", not read) | medium | medium | kb watch of new papers by these groups | kb request for the Gurian identifier; keep the claim to the fully relativistic kinetic 3D calculation |
| 13. Harness: `nrpic-run` cannot register runs on this branch (KeyError on the hand manifests), so budgets are not accounted automatically | certain | low | — | hand registration (`review/register.py`); outbox to orch |

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

## Decision requested from the group

Draft by the note helper (wave 2), for the lead to confirm or rewrite: the products of G0 that were missing after wave 1 now exist (working note v0, architecture and timeline schematics, data figures from registered runs, this report); every number of the note is traced to a registered run, and the check of the lead's documents against the files found three numbers to correct (note/tables/claims.md). Accept G0 of C-sidm once the lead (i) decides that the fresh-context verifier's stage/G0/VERIFIER.md stands for VERIFIER_REPORT.md (C18), (ii) rewrites STATUS, JOURNAL and HANDOFF for wave 2 (C20), and (iii) corrects the three numbers and updates OPEN.md; the failed verify checks (uncommitted files of other helpers, unfinished runs of wave 2, wave-1 hand manifests) do not concern the G0 products.
