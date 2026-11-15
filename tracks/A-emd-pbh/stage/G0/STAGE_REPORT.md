# Stage report: A-emd-pbh G0

Date: 2026-11-15 · branch `track/A-emd-pbh` at `5aad6dca517e` · checklist
`tracks/A-emd-pbh/stage/G0/CHECKLIST.md` (from `nrpic-stage collect`)

## Verdict

**FAIL**. Tag: `stage/A-emd-pbh/G0-fail-20261115` (created and pushed by the orchestrator after review, decision 0003).

- 2 checklist items not PASS or NA: C2 FAIL, C18 OPEN
- verify ran on fe07201; files changed since: tracks/A-emd-pbh/criteria/check_criteria2.py, tracks/A-emd-pbh/criteria/predict.py, tracks/A-emd-pbh/criteria/scouting_table.py, tracks/A-emd-pbh/newton/analyze_newton.py, tracks/A-emd-pbh/periodic_threshold/DESIGN.md, tracks/A-emd-pbh/periodic_threshold/JOURNAL.md (run verify again)
- verify reported FAIL: clean, runs
- no VERIFIER_REPORT.md (step 7: verifier subagent)

## Package documents (decision 0012)

| Document | State |
|---|---|
| `stage/G0/STAGE_REPORT.md` | written by this command |
| `stage/G0/EVIDENCE.md` | present |
| `stage/G0/OPEN.md` | present |
| `stage/G0/CHECKLIST.md` | present |
| `stage/G0/REVIEW.md` | none (needed where the lead rechecked helpers) |
| scoping text | `scope/SCOPE.md` |

## Criteria (coord/CHARTER.md, gate G0 of this track)

| # | Criterion | Evidence (run id, figure, KB locator) | Result |
|---|---|---|---|
| C1 | Problem statement, parameter ranges, exit criteria, test plan | scope/SCOPE.md sections 1, 3, 5, 7 and the lead's section 10 (amplitude convention 10.1, set-up order 10.2); stage/G0/EVIDENCE.md | PASS |
| C2 | The statements of the key references verified in the knowledge base | verified at the raw store with file:line locators (scope/REFERENCES.md; seven locators re-read by the lead, SCOPE.md 10.5), not yet knowledge-base entries: outbox 20261115T1320Z__to-kb__ingest-s1-references.md | FAIL |
| C3 | Risk list | RISKS.md (16 rows); SCOPE.md section 8 | PASS |
| C4 | Compute estimate | SCOPE.md section 9 (T5, run A-emd-pbh-20261115-112625-e854f12, rerun A-20261115-130252-7877b7a identical) and 10.7 (unit cost from core run core-20261115-040406-1311b8e; scouting runs A-20261115-130948-5a2b58a) | PASS |
| C5 | Working note v0 | note/main.tex, note/main.pdf (REVTeX, 9 pages; problem, threshold definition, set-ups, tests with four data figures, plan, open items, parameter table, ledger); figures and tables from run A-20261115-161947-09324e1 (registered by hand, nrpic-run refused; same scripts as A-20261115-161054-50848b1 and A-20261115-161720-6ae975e); note/JOURNAL.md N1-N5 | PASS |
| C6 | Architecture schematic | note/figures/schem_architecture.png (script note/scripts/schem_architecture.py), Fig. 3 of the note; run A-20261115-161947-09324e1; PNG looked at | PASS |
| C7 | Stage timeline | table in SCOPE.md 10.8; schematic note/figures/schem_timeline.png (Fig. 6 of the note), run A-20261115-161947-09324e1 | PASS |
| C8 | (no track-specific criterion for G0 in the sheet: write the ones agreed with the orchestrator here, or mark NA) | no track-specific G0 criterion in the sheet | NA |
| C9 | Track A. The threshold line is built in the periodic box (the expanding ball holds only amplitudes below the comparison amplitudes of arXiv:2609.14218; lead's evidence in `scope/SCOPE.md`); the expanding ball stays the spherical verification case and the set-up for isolated collapses. The G1 scan-design criterion is met on the reference-based design; the Newtonian-mode runs are G2 work. (0013) | applied: the note builds the threshold line in the periodic box and keeps the ball for verification (note Sec. III A, B). Qualification from the verifier (stage/G0/VERIFIER.md C1c) and the note's Fig. 1: a ball of two compaction radii reaches the particle bracket of arXiv:2609.14218 at R_b H_i = 0.9; both ball sizes stay far below the hoop line | PASS |
| C10 | Schematic: Track architecture (three states: exists, to be ported, new) | note/figures/schem_architecture.png: exists (green), to be ported (slate), new (red); PNG looked at | PASS |
| C11 | Schematic: Stage timeline | note/figures/schem_timeline.png: gates G0-G4 at the charter's target times, requirements, needs between gates; PNG looked at | PASS |
| C12 | Data figure: None required | none required | NA |
| C13 | Data figure: Data from the literature may be redrawn | scope figures fig_hoop (2609.14218 hoop line by eye against the reproduction), fig_timing; rerun A-20261115-130252-7877b7a, looked at | PASS |
| C14 | Package documents of decision 0012: STAGE_REPORT.md (nrpic-stage report), EVIDENCE.md, OPEN.md and this CHECKLIST.md in the stage directory; REVIEW.md where the lead rechecked helpers; the scoping text in SCOPE.md or SCOPING.md beside them or in the scope directory, named in the report (no REPORT.md needed) | STAGE_REPORT.md (nrpic-stage report), EVIDENCE.md, OPEN.md, CHECKLIST.md in stage/G0; scoping text scope/SCOPE.md (named in the report); no REVIEW.md: the lead's re-check of the helpers is JOURNAL.md entry 2026-11-15T12:57Z (L1-L8) | PASS |
| C15 | Data figures drawn with /zoom-figure-style from registered run outputs, one script per figure, every PNG looked at | figstyle (python/nrpic/figstyle.py), one script per figure set (scope_calc.py, lead_crosscheck.py, scouting_predictions.py, helper scripts); PNGs looked at: stage/G0/EVIDENCE.md 'Figures looked at' | PASS |
| C16 | Schematics drawn with /sleep-paper-figure-style: track architecture (exists / to be ported / new) and the gate timeline | note/scripts/schem_architecture.py and schem_timeline.py with the vendored paperfig.py (unchanged copy of harness/style/); PNGs looked at | PASS |
| C17 | Working note written with /paper-writing; its manuscript checker passed with --compile | check_manuscript.py --compile on note/main.tex: 0 undefined references, 0 undefined citations, 0 overfull boxes; candidates only in 5.5/5.8 for run ids in the ledger appendix and harness names in the ledger scripts, accepted by the note's guide (../WRITING_GUIDE.md, exception 1); captions within five lines on the rendered pages (looked at) | PASS |
| C18 | Verifier subagent (fresh context) wrote VERIFIER_REPORT.md; every number of the Supplemental Material recomputed from the manifests | a fresh verifier (wave 2) is writing stage/G0/VERIFIER.md (runs A-20261115-160935-41f721d, -161239-1c41333, -161253-e506d90): C1a/b, C2, C3, C4a, C5, C6, C7 confirmed, C1c and C4b wrong, C8 model not confirmed; the ledger of the note is recomputed from the run outputs by note/scripts/ledger.py (claims check: 68 numbers of the lead's documents, 66 agree, note/tables/claims.md); a verifier's recomputation of the note's ledger is not done | OPEN |
| C19 | Null results and failed runs are on record (manifests and JOURNAL) | failed and superseded runs kept with manifests (stage/G0/EVIDENCE.md, status failed/stopped); failed predictions in the helpers' journals and JOURNAL.md | PASS |
| C20 | STATUS.md, JOURNAL.md and HANDOFF.md are current | rewritten in this session (commit of the lead session) | PASS |

## Re-verification on a clean checkout (`nrpic-stage verify`)

`nrpic-stage verify` on 2026-11-15T16:30:01Z, clean export of `fe07201c5770`: **FAIL**. Details: `VERIFY_RESULTS.md`.

| Check | Result | Message |
|---|---|---|
| clean | FAIL | 5 uncommitted paths: commit them first (tracks/A-emd-pbh/periodic_threshold/JOURNAL.md, tracks/A-emd-pbh/runs/A-emd-pbh-20261115-153843-7172b66/manifest.json, peak.horizon_summary_0.txt, tracks/A-emd-pbh/criteria/scouting_table.py, tracks/A-emd-pbh/runs/A-emd-pbh-20261115-161829-dba94f6/) |
| sync | PASS | main is merged into the branch |
| export | PASS | clean export of fe07201c5770 (HEAD) in /data/haiyangw/nrpic/scratch/A-emd-pbh/tmp/stage-verify/A-emd-pbh-G0-fe07201-20261115T162124Z/tree |
| size | PASS | no committed file of the track above 5 MB |
| note | PASS | tracks/<ID>/note/main.tex present |
| package | PASS | EVIDENCE.md, OPEN.md, CHECKLIST.md present (decision 0012); scoping text: scope/SCOPE.md |
| note-pdf | PASS | note/main.pdf committed after the last .tex change |
| style | PASS | 2 style copies equal harness/style/SHA256SUMS (czstyle.py, paperfig.py) |
| fig-script | PASS | 6 figures, each with its script |
| min-figs | PASS | 2 schematics and 4 data figures (brief 13.4 asks at least 2 and 0 at G0) |
| runs | FAIL | 6 of 96 runs have problems |
| run-notes | WARN | 65 runs read with defaults or not fully re-verifiable (nrpic-run lint) |
| status | PASS | STATUS.md has 32 lines |
| rerun | PASS | 6 of 6 scripts and commands ran cleanly in the export |
| compare | PASS | 12 regenerated files compared with the committed ones; 0 differ beyond tolerance (rtol 1e-06, atol 1e-12, PNG rms 0.005) |
| regenerate | PASS | all 12 committed figure files regenerated |

## Figures

| File | Script | Kind (data / schematic) | Looked at (PNG read) |
|---|---|---|---|
| note/figures/fig_ball_exact.* | note/scripts/fig_ball_exact.py | data | yes (helper note, 2026-11-15) |
| note/figures/fig_constraints.* | note/scripts/fig_constraints.py | data | yes (helper note, 2026-11-15) |
| note/figures/fig_criteria.* | note/scripts/fig_criteria.py | data | yes (helper note, 2026-11-15) |
| note/figures/fig_landscape.* | note/scripts/fig_landscape.py | data | yes (helper note, 2026-11-15) |
| note/figures/schem_architecture.* | note/scripts/schem_architecture.py | schematic | yes (helper note, 2026-11-15) |
| note/figures/schem_timeline.* | note/scripts/schem_timeline.py | schematic | yes (helper note, 2026-11-15) |

## Verifier report

MISSING as `VERIFIER_REPORT.md`. A fresh verifier of wave 2 (a helper given the artefacts, not
the conclusions) is writing `stage/G0/VERIFIER.md` with its own runs (A-20261115-160935-41f721d,
A-20261115-161239-1c41333, A-20261115-161253-e506d90; journal `stage/G0/JOURNAL.md`). Its
section 1 at commit 0e0e224 confirms C1a/b, C2, C3, C4a, C5, C6, C7 of its list, finds C1c
(the ball's amplitude window) and C4b (the predicted horizon time of mu = 0.045 under H1)
wrong, and leaves the compute model (C8) unconfirmed. The note v0 already states C1c as the
verifier does (Sec. III A, Fig. 1) and quotes no horizon time for H1.

## Null results and failed runs

- `A-20261115-125927-6d2c1e6`: failed (exit 1), lead rerun of the scope package T1-T5 (L1)
- `A-20261115-125932-574c747`: failed (exit 1), lead rerun of the gauge package (L1)
- `A-20261115-125932-5a90432`: failed (exit 0), lead rerun of the newton package (L1)
- `A-20261115-125932-b90223c`: failed (exit 1), lead rerun of the criteria package (L1)
- `A-20261115-125932-f221206`: failed (exit 1), lead rerun of the expball package (L1)
- `A-emd-pbh-20261115-112500-61acbec`: failed (exit None), G0 scoping: semi-analytic tests T1-T5 of tracks/A-emd-pbh/scope/JOURNAL.md (hoop criterion of 2609.14218, collapse times against top-hat shells, ball geometry, velocity-dispersion axis and particle floor, compute estimate from measured costs)
- `A-emd-pbh-20261115-115339-044312f`: stopped (exit None), G1 of A-pre-1: FD constraint residuals vs resolution (orders (2, 4), N = [32, 64, 128, 256]) and table interpolation error vs spacing
- `A-emd-pbh-20261115-115559-c4a583e`: stopped (exit None), A-pre-1: Hamiltonian-constraint noise of CIC-deposited particles vs N (N = [10000, 30000, 100000, 300000, 1000000], mesh 64^3)
- `A-emd-pbh-20261115-125932-574c747`: failed (recorded as 'failed (exit 1)') (exit None), lead rerun of P1-P7 (L1)
- `A-emd-pbh-20261115-125932-779f753`: failed (recorded as 'failed (exit 1)') (exit None), lead rerun of the snapshot self-test (L1)
- `A-emd-pbh-20261115-153856-9d731b1`: stopped (exit 143), SR-1 (geodesic slicing) of data set 2t on processors, dx = M (128^3 over [-64,64]^3), three segments with restarts (cfl 0.25 to 42.0, 0.03125 to 44.3568, 0.0078125 to 44.4472); release core-v0.3 processor executable
- `A-emd-pbh-20261115-153903-9d731b1`: stopped (exit 143), SR-2 (conformal-time lapse + Gamma-driver) of data set 2t on processors, dx = M (128^3 over [-64,64]^3), t = 0 -> 53; release core-v0.3 processor executable
- `A-emd-pbh-20261115-154356-527a6d1`: stopped (exit None), S1 initial data: peak mu = 0.5, e = 0.2, eps_i = 1, 64^3, one particle per cell (make_peak_ic.py)
- `A-emd-pbh-20261115-161253-b8c1dc9`: failed (exit 2), Analysis of the top-hat campaign A-emd-pbh-20261115-153409-dc27b98 against the cycloid (P9)
- `A-emd-pbh-20261115-161542-36e461d`: failed (exit None), A-pre-2: check the analytic criteria against numbers printed in 1609.01588, 1707.03595, 2211.13950, 2507.18312, 2508.10070
- `A-emd-pbh-20261115-162133-208f933`: failed (exit 1), analysis of SR-1 dx = M/2 segment 1 (run A-emd-pbh-20261115-153843-7172b66): comparison with the exact solution in invariants, field slices
- `A-emd-pbh-20261115-162237-a614467`: failed (exit 1), analysis of SR-1 dx = M/2 segment 1 (run A-emd-pbh-20261115-153843-7172b66): comparison with the exact solution in invariants, field slices (second attempt)
- `A-emd-pbh-20261115-162505-d32d331`: failed (exit 1), Test of analyse_scouting.py on the dry run S0

## Open risks


State 2026-11-15 (lead, wave 1). Likelihood and effect: H high, M medium, L low
[JUDGEMENT]. Sources: `scope/SCOPE.md` section 8, `gauge/GAUGE.md`, `expball/DERIVATION.md`,
core's `tracks/core/JOURNAL-id.md` on branch `core/id-extrinsic`.

| # | Risk | Likelihood | Effect | Watch | Response |
|---|---|---|---|---|---|
| 1 | Lapse fronts: every condition d_t alpha = -f(alpha) alpha K reacts to K gradients at the ball edge; core saw 1+log fronts reach the centre at t = 5.5 M (R_b = 10 M) and conformal-time fronts at speed 0.58 (bound ball, sharp edge) [VERIFIED by core's runs] | H | H: core shells lose accuracy before turnaround | central lapse against R/R_i of the core in SR-2 | geodesic slicing for the spherical tests (SR-1); K_ref lapse (request to core); taper |
| 2 | Geodesic slicing with frozen shift not well posed in Z4c [BACKGROUND, unchecked] | M | M: SR-1 fails, spherical tests need a dynamical gauge | core's T2e outcome; SR-1 constraint norms | fall back to SR-2 at dx = M/4 |
| 3 | Time step: fixed dt = cfl dx is unstable once C v > 0.618 (gauge T2); in comoving coordinates v = R_i/R grows to 17 at the first trapped sphere | H in SR-1 | M | staged cfl plan (G1 STATUS section 3) | restart with smaller cfl; conformal-time lapse keeps v ~ 1 |
| 4 | The ball holds only mu <~ 0.03-0.07 (scope T3) | certain | H for the comparison with arXiv:2609.14218 | | threshold line in the periodic box (proposal to orch) |
| 5 | Phase-1 capability missing: generator for the data of arXiv:2609.14218, a slicing that survives collapse in a box, the finder in a box | H | H: G3 waits | core and B replies | requests sent; ball work meanwhile |
| 6 | Constraint violation at particle crossings (arXiv:2609.14218 MDPBH.tex:1148-1186) | H | H: spurious black holes below the hoop line (hypothesis H2) | Hamiltonian norm outside the horizon (outcome bound of SCOPE.md section 3) | Z4c damping; two mesh spacings with damping on and off |
| 7 | Curvature at caustics does not converge (arXiv:1611.07906) | H | M: diagnostics | | outcomes from horizons and constraints, not from peak curvature |
| 8 | Particle noise halts or seeds collapse near threshold | M | H | b_min against N (A6) | lattice loads aligned with the mesh; N from scope T4b; N convergence of every bracket |
| 9 | Threshold depends on the run length (hypothesis H1) | H | H: misread threshold | t_AH of every BH run | A_c(t_end) with delta_fd stated (SCOPE.md section 3) |
| 10 | Two amplitude conventions in use (central contrast 12 mu/5, mean in r_m 0.883 mu) | M | M: factor e errors in comparisons | every table names its measure | SCOPE.md 10.1; conversion row in predict.py (open) |
| 11 | Sharp ball edges in evolution data: constraint residual does not converge; expball sharp tables carry no `breaks` line (cubic overshoot ~10 % over two rows) | M | M | | C^4 taper for all evolution data (data set 2t) |
| 12 | Outflow boundary inconsistent with the r^(-3/2) fall-off of K_ij (core) | certain | L-M | tracers near the boundary | boundary beyond the light-travel distance (half-width 64 M for SR runs) |
| 13 | Finder spin biased in an expanding region (flat rotation vectors with the full K_ij; derived, not measured) | M | M for the spin deliverable | test G-R4 | projected rotation vectors (request to core) |
| 14 | Budget: first scan ~155 card-hours (band 50-470) against 60 to the next gate | H | M | `nrpic-run budget` | G2 needs 25-50; raise asked at G2 |
| 15 | Overlap with the authors of arXiv:2609.14218 (high-density regime announced, MDPBH.tex:1218) | M | M | arXiv | H1 and the converged line first |
| 16 | Newtonian precursor waits for core/newton (decision 0010) | H | L | core/newton branch | references meanwhile (newton/), A6 as acceptance tests |

## Decision requested from the group

One paragraph: accept G0 of A-emd-pbh, or what is missing.

TO WRITE by the track before the package is submitted (`nrpic-stage report ... --decision "..."`).

## What the note package of wave 2 closed (helper `note`, 2026-11-15)

Written by the helper of the package `note/` (journal `note/JOURNAL.md`, predictions N1-N5
before the runs, outcomes after). Items of `OPEN.md`:

| OPEN.md item | State | Evidence |
|---|---|---|
| 1 REPORT.md | closed by decision 0012: this STAGE_REPORT.md from `nrpic-stage report` | this file; `CHECKLIST.md` recollected |
| 2 working note v0 | closed | `note/main.tex`, `note/main.pdf` (9 pages); guide and notation `../../WRITING_GUIDE.md`, `../../NOTATION.md`; paper-writing checker with `--compile`: no undefined reference or citation, no overfull box |
| 3 two schematics | closed | `note/figures/schem_architecture.png`, `schem_timeline.png` (paperfig) |
| 4 verifier | in progress (another helper) | `VERIFIER.md` above |
| 8 `nrpic-stage verify` | ran on fe07201: every check of the note passes (note, note-pdf, style, fig-script, min-figs, rerun, compare, regenerate); FAIL only on `clean` and `runs`, both from other helpers' work in flight (uncommitted files, among them `peak.horizon_summary_0.txt` at the worktree root; six runs still `submitted` or `running`) | `VERIFY_RESULTS.md` |
| 2, 3 runs | the figures and tables come from run A-20261115-161947-09324e1 (registered by hand: `nrpic-run` refused while the untracked file above exists); identical PNGs from the registered runs A-20261115-161054-50848b1 and A-20261115-161720-6ae975e | `runs/<id>/manifest.json` |

Scoping text: `scope/SCOPE.md` (sections 1-9 helper, section 10 lead). The note's numbers
come only from registered runs; each input file is checked against its run's
`sha256sums.txt` where the run wrote one (`note/tables/claims.md`, "Inputs read").

## Disagreements between the leads' reports and the files (the files win)

`note/scripts/ledger.py` checked 68 numbers stated in `STATUS.md`, `stage/G1/STATUS.md`,
`scope/SCOPE.md`, `JOURNAL.md` and `runs_ball/JOURNAL.md` against the run outputs
(`note/tables/claims.md`): 66 agree to the printed digits, two differ.

1. `JOURNAL.md:94` (lead's L3 outcome): "the cubic smears the KL jump over two rows with an
   overshoot of about 0.1 H"; `SCOPE.md` 10.3 and `RISKS.md` row 11: "~10 % overshoot". The
   cross-check run A-20261115-130257-a7374a4 records `L3.KL_overshoot_near_edge` = 0.0855
   (M = 1 units) = 1.37 H, the largest deviation from the exact step within 0.01 M of the
   edge; it contains the smeared jump itself (the jump of KL is 1.5 H). The overshoot beyond
   the step values is not recorded by any run [TO VERIFY]. The conclusion (sharp tables for
   offline tests only, taper for evolution) is unaffected.
2. `JOURNAL.md:101` (L6 outcome): "below 4.3e-15"; the same run records 4.33e-15. A rounding
   of the bound; the conclusion (rounding error) is unaffected.

Further differences found while writing the note, not counted above:

3. `STATUS.md` `budget:` says 0 GPU-hours used; `harness/bin/nrpic-run budget` now reports
   0.10 card-hours used toward G2 and 0.17 on hand-written manifests without a gate (wave-2
   runs). A difference of date, not of fact; the lead rewrites STATUS at the end of wave 2.
4. Two exact references of data set 2t give the first trapped sphere at R_i = 2.74183,
   m = 0.080513 (lead, A-20261115-130948-5a2b58a) and R_i = 2.74175, m = 0.080505 (runs_ball,
   A-emd-pbh-20261115-153719-91b03d1); they agree to the printed digits of both documents
   (2.742, 0.0805), the difference is the shell-grid spacing 1.25e-4 of the second run. The
   note takes the second (the one with the m_AH(tau) curve). The data-set run
   A-emd-pbh-20261115-130609-947c898 itself prints a coarser first-horizon estimate
   (R_i = 2.731, m = 0.0796, 400 shells), superseded by both.
5. `stage/G0/OPEN.md` item 1 and `HANDOFF.md` ask for `REPORT.md`; decision 0012 replaces it
   by this file. `CHECKLIST.md` item C20 ("STATUS, JOURNAL, HANDOFF current") is kept PASS
   from wave 1 but those files describe the state before wave 2.
6. The verifier's C1c and C4b (above) correct `SCOPE.md` sections 2 and 4 and the wording of
   decision 0013 ("the expanding ball holds only amplitudes below the comparison amplitudes"):
   at R_b H_i = 0.9 a ball of two compaction radii holds mu up to 0.069 (run
   A-20261115-130252-7877b7a), above the particle bracket (0.045, 0.05] of arXiv:2609.14218.

## Why the computed verdict is FAIL, and what closes it

- C2 (key statements as knowledge-base entries): needs the kb ingest requested in
  `outbox/20261115T1320Z__to-kb__ingest-s1-references.md`.
- C18 / verifier report: the wave-2 verifier finishes `VERIFIER.md`; the lead decides whether
  it stands for `VERIFIER_REPORT.md` and whether a verifier recomputes the note's ledger.
- verify `clean` and `runs`: rerun `harness/bin/nrpic-stage verify A-emd-pbh G0` once the
  helpers of wave 2 have committed and finished their runs.

Draft for "Decision requested" (the lead's to write with `--decision`): accept G0 of
A-emd-pbh with C2 carried to G1 (knowledge-base entries), once the verifier's report is in
and a clean `verify` has run.
