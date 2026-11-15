# Stage report: A-emd-pbh G0

Date: 2026-11-15 · branch `track/A-emd-pbh` at `2b756f503362` · checklist
`tracks/A-emd-pbh/stage/G0/CHECKLIST.md` (from `nrpic-stage collect`)

## Verdict

**FAIL**. Tag: `stage/A-emd-pbh/G0-fail-20261115` (created and pushed by the orchestrator after review, decision 0003).

- 1 checklist items not PASS or NA: C18 FAIL
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

## Criteria (coord/CHARTER.md, gate G0 of this track)

| # | Criterion | Evidence (run id, figure, KB locator) | Result |
|---|---|---|---|
| C1 | Problem statement, parameter ranges, exit criteria, test plan | scope/SCOPE.md sections 1, 3, 5, 7 and the lead's section 10 (amplitude convention 10.1, set-up order 10.2); stage/G0/EVIDENCE.md | PASS |
| C2 | The statements of the key references verified in the knowledge base | knowledge-base snapshots kb-20261115-3826a68 (read by the lead, read-only) and kb-20261115-44b7406 (db/current; kb's answer tracks/kb/outbox/20261115T183737Z__to-A-emd-pbh__ingest-s1-references.md on kb/main, independent locator check run kb-20261115-154906-f19880f: all 166 locator groups resolve; 48 of 53 numeric statements have every number in the cited lines): all twelve S1 key references ingested (parse ok: 2609.14218 v1, 2610.23218 v1, 1609.01588 v2, 1707.03595 v4, 2211.13950 v3, 2507.18312 v3, 2508.10070 v1, 2109.04896 v3, 2306.11810 v2, 2605.04487 v2, 1611.07906 v2, 1901.04498 v2); 170 claims tagged A-emd-pbh with resolved file:line locators, 152 verified by the kb claims check, among them mu_c in (0.32, 0.33] (claim 21, MDPBH.tex:L766-768) and the constraint caveat (claim 30). Qualification: the particle bracket (claim 25, MDPBH.tex:L1101-1103) and 17 others are still 'to_verify' in the kb (seeded without a [VERIFIED] label); the lead read claim 25 at the source in this session (stage/REVIEW-wave2.md, criteria2) and asked kb to update its status (outbox) | PASS |
| C3 | Risk list | RISKS.md (22 rows, rewritten after wave 2: rows 1, 2, 18-20 realized by the scouting runs); SCOPE.md section 8 | PASS |
| C4 | Compute estimate | SCOPE.md section 9 (T5, run A-emd-pbh-20261115-112625-e854f12, rerun A-20261115-130252-7877b7a identical) and 10.7 (unit cost from core run core-20261115-040406-1311b8e; scouting runs A-20261115-130948-5a2b58a) | PASS |
| C5 | Working note v0 | note/main.tex, note/main.pdf (REVTeX, 9 pages; problem, threshold definition, set-ups, tests with four data figures, plan, open items, parameter table, ledger); figures and tables from run A-20261115-161947-09324e1 (registered by hand, nrpic-run refused; same scripts as A-20261115-161054-50848b1 and A-20261115-161720-6ae975e); note/JOURNAL.md N1-N5 | PASS |
| C6 | Architecture schematic | note/figures/schem_architecture.png (script note/scripts/schem_architecture.py), Fig. 3 of the note; run A-20261115-161947-09324e1; PNG looked at | PASS |
| C7 | Stage timeline | table in SCOPE.md 10.8; schematic note/figures/schem_timeline.png (Fig. 6 of the note), run A-20261115-161947-09324e1 | PASS |
| C8 | (no track-specific criterion for G0 in the sheet: write the ones agreed with the orchestrator here, or mark NA) | no track-specific G0 criterion in the sheet | NA |
| C9 | Track A. The threshold line is built in the periodic box (the expanding ball holds only amplitudes below the comparison amplitudes of arXiv:2609.14218; lead's evidence in `scope/SCOPE.md`); the expanding ball stays the spherical verification case and the set-up for isolated collapses. The G1 scan-design criterion is met on the reference-based design; the Newtonian-mode runs are G2 work. (0013) | applied: the threshold line is built in the periodic box, the ball stays the verification case (note Sec. III A, B; SCOPE.md 10.2). The ruling's stated reason is partly wrong (verifier C1c, confirmed by the lead's run A-20261115-182314-bebd0cf: a q = 2 ball holds the particle bracket (0.045, 0.05], not the hoop or fluid amplitudes); SCOPE.md 4, 8, 10.9(a) and RISKS row 4 corrected; correction proposed to orch (outbox). The ruling stands on the source's own data in the box | PASS |
| C10 | Schematic: Track architecture (three states: exists, to be ported, new) | note/figures/schem_architecture.png: exists (green), to be ported (slate), new (red); PNG looked at | PASS |
| C11 | Schematic: Stage timeline | note/figures/schem_timeline.png: gates G0-G4 at the charter's target times, requirements, needs between gates; PNG looked at | PASS |
| C12 | Data figure: None required | none required | NA |
| C13 | Data figure: Data from the literature may be redrawn | scope figures fig_hoop (2609.14218 hoop line by eye against the reproduction), fig_timing; rerun A-20261115-130252-7877b7a, looked at | PASS |
| C14 | Package documents of decision 0012: STAGE_REPORT.md (nrpic-stage report), EVIDENCE.md, OPEN.md and this CHECKLIST.md in the stage directory; REVIEW.md where the lead rechecked helpers; the scoping text in SCOPE.md or SCOPING.md beside them or in the scope directory, named in the report (no REPORT.md needed) | STAGE_REPORT.md (nrpic-stage report), EVIDENCE.md, OPEN.md, CHECKLIST.md in stage/G0; the lead's re-check of the helpers is ../REVIEW-wave2.md (wave 2) and JOURNAL.md entry 2026-11-15T12:57Z (wave 1); scoping text scope/SCOPE.md (named in the report) | PASS |
| C15 | Data figures drawn with /zoom-figure-style from registered run outputs, one script per figure, every PNG looked at | figstyle (python/nrpic/figstyle.py), one script per figure set (scope_calc.py, lead_crosscheck.py, scouting_predictions.py, helper scripts); PNGs looked at: stage/G0/EVIDENCE.md 'Figures looked at' | PASS |
| C16 | Schematics drawn with /sleep-paper-figure-style: track architecture (exists / to be ported / new) and the gate timeline | note/scripts/schem_architecture.py and schem_timeline.py with the vendored paperfig.py (unchanged copy of harness/style/); PNGs looked at | PASS |
| C17 | Working note written with /paper-writing; its manuscript checker passed with --compile | check_manuscript.py --compile on note/main.tex: 0 undefined references, 0 undefined citations, 0 overfull boxes; candidates only in 5.5/5.8 for run ids in the ledger appendix and harness names in the ledger scripts, accepted by the note's guide (../WRITING_GUIDE.md, exception 1); captions within five lines on the rendered pages (looked at) | PASS |
| C18 | Verifier subagent (fresh context) wrote VERIFIER_REPORT.md; every number of the Supplemental Material recomputed from the manifests | a fresh verifier wrote stage/G0/VERIFIER.md (taken as VERIFIER_REPORT.md under decision 0012; sections 1-3 committed in 0ac9951 before the track's summaries were read; runs A-20261115-160935-41f721d, -161239-1c41333, -161253-e506d90; reproduced exactly by the lead, A-20261115-182514-3bb6846): C1a/b, C2, C3, C4a, C5, C6, C7 confirmed, C1c and C4b wrong (corrected, ../REVIEW-wave2.md section 3), C8 now confirmed by the measured cost. Not met: the note's ledger appendix (every number with its run id) was recomputed from the manifests by note/scripts/ledger.py with checksum checks (run A-20261115-161947-09324e1), but not by a verifier; closing it needs a fresh verifier to rerun ledger.py and check the rows | FAIL |
| C19 | Null results and failed runs are on record (manifests and JOURNAL) | failed and superseded runs kept with manifests (stage/G0/EVIDENCE.md, status failed/stopped); failed predictions in the helpers' journals and JOURNAL.md | PASS |
| C20 | STATUS.md, JOURNAL.md and HANDOFF.md are current | rewritten in the lead session of wave 2 (STATUS.md, JOURNAL.md entry, HANDOFF.md, RISKS.md) | PASS |

## Re-verification on a clean checkout (`nrpic-stage verify`)

`nrpic-stage verify` on 2026-11-15T18:55:32Z, clean export of `2b756f503362`: **PASS**. Details: `VERIFY_RESULTS.md`.

| Check | Result | Message |
|---|---|---|
| clean | PASS | worktree clean (outside the stage directory being assembled) |
| sync | PASS | main is merged into the branch |
| export | PASS | clean export of 2b756f503362 (HEAD) in /data/haiyangw/nrpic/scratch/A-emd-pbh/tmp/stage-verify/A-emd-pbh-G0-2b756f5-20261115T185412Z/tree |
| size | PASS | no committed file of the track above 5 MB |
| note | PASS | tracks/<ID>/note/main.tex present |
| package | PASS | EVIDENCE.md, OPEN.md, CHECKLIST.md present (decision 0012); scoping text: scope/SCOPE.md |
| note-pdf | PASS | note/main.pdf committed after the last .tex change |
| style | PASS | 2 style copies equal harness/style/SHA256SUMS (czstyle.py, paperfig.py) |
| fig-script | PASS | 6 figures, each with its script |
| min-figs | PASS | 2 schematics and 4 data figures (brief 13.4 asks at least 2 and 0 at G0) |
| runs | PASS | 130 run manifests finished (102 hand-written, read as decision 0012 allows), output checksums verified where recorded |
| run-notes | WARN | 78 runs read with defaults or not fully re-verifiable (nrpic-run lint) |
| status | PASS | STATUS.md has 35 lines |
| rerun | PASS | 6 of 6 scripts and commands ran cleanly in the export |
| compare | PASS | 12 regenerated files compared with the committed ones; 0 differ beyond tolerance (rtol 1e-06, atol 1e-12, PNG rms 0.005) |
| regenerate | PASS | all 12 committed figure files regenerated |

## Figures

| File | Script | Kind (data / schematic) | Looked at (PNG read) |
|---|---|---|---|
| note/figures/fig_ball_exact.* | note/scripts/fig_ball_exact.py | data | to be confirmed by the session |
| note/figures/fig_constraints.* | note/scripts/fig_constraints.py | data | to be confirmed by the session |
| note/figures/fig_criteria.* | note/scripts/fig_criteria.py | data | to be confirmed by the session |
| note/figures/fig_landscape.* | note/scripts/fig_landscape.py | data | to be confirmed by the session |
| note/figures/schem_architecture.* | note/scripts/schem_architecture.py | schematic | to be confirmed by the session |
| note/figures/schem_timeline.* | note/scripts/schem_timeline.py | schematic | to be confirmed by the session |

## Verifier report

MISSING: the verifier subagent has not reported.

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


State 2026-11-15 (lead, end of wave 2). Likelihood and effect: H high, M medium, L low
[JUDGEMENT]. Sources: `scope/SCOPE.md` sections 8 and 10.9, `gauge/GAUGE.md`,
`stage/REVIEW-wave2.md`, the helpers' journals. "Realized" means a wave-2 run showed it.

| # | Risk | Likelihood | Effect | Watch | Response |
|---|---|---|---|---|---|
| 1 | Lapse fronts: the conformal-time lapse sends a pulse from the edge of the bound core to the centre (central lapse 1.80-1.87 against 1.34 at dx = M, M/2, M/4; runs_ball, A-20261115-182314-bebd0cf) | realized | H: the core runs through its proper time too fast, no horizon | central lapse against a(tau_c) | lapse towards dust proper time, K_ref lapse (outbox gauge-expanding-ball) |
| 2 | Geodesic slicing with frozen shift unstable: SR-1 non-finite at t = 30.8 (dx = M), 33.1 (M/2), grid-scale growth at the core edge | realized | H for SR-1 | largest |H| (0.24 / 0.051 / 0.040 at t = 20) | not the slicing for collapse; keep for the expansion phase only |
| 3 | Time step ignores the coordinate light speed (v = R_i/R reaches 17 at the first trapped sphere in comoving coordinates) | H in SR-1 | M | staged cfl plan | step limit asked of core (outbox) |
| 4 | The ball holds the particle bracket of arXiv:2609.14218 only at q = 2 with the mean-contrast cap, not the hoop or fluid amplitudes (corrected after verifier C1c) | certain | M for the comparison | | threshold line in the periodic box (decision 0013; reason corrected, outbox decision-0013-reason) |
| 5 | Phase-1 capability missing: generator for the source data at its start epoch and mu >= 0.5, a slicing that survives collapse in a box, the finder in a box | H | H: G3 waits | core replies | requests sent; S1/S2 now show where it fails (rows 20-22) |
| 6 | Constraint violation at particle crossings (arXiv:2609.14218 MDPBH.tex:1148-1186) | H | H: spurious black holes below the hoop line (H2) | Hamiltonian norm outside the horizon | Z4c damping; two mesh spacings with damping on and off |
| 7 | Curvature at caustics does not converge (arXiv:1611.07906) | H | M | | outcomes from horizons and constraints |
| 8 | Particle noise halts or seeds collapse near threshold; lattice law N^(-4/9) has no fitted coefficient (verifier C6) | M | H | b_min against N | N convergence of every bracket |
| 9 | Threshold depends on the run length (H1); the comparison bracket at e = 0.2 sits on the cutoff mu_fd(250 t_H) = 0.048 (top-hat form; verifier weak point 2) | H | H | t_AH of every BH run | runs near the bracket to 400 t_H; A_c(t_end) with the cutoff stated |
| 10 | Two amplitude conventions (central 12 mu/5, mean in r_m 0.883 mu); linear measures poor for mu >~ 0.1 (crunch carries e^(3 mu)) | M | M | every table names its measure | criteria/predict.py amplitude_measures |
| 11 | Sharp ball edges: table interpolation deviates by up to 1.37 H at the jump (A-20261115-130257-a7374a4); constraints do not converge | M | M | | C^4 taper for all evolution data |
| 12 | Outflow boundary: a Theta signal enters from 32 M (seen at |x| = 20 at t = 16.9 in the dx = M/4 run) | certain | L-M | Theta near the matter edge | boundary beyond the light-travel distance |
| 13 | Finder spin biased in an expanding region | M | M for spin | test G-R4 | projected rotation vectors (request to core, wave 1) |
| 14 | Budget: first scan ~155 card-hours (band 50-470) against 60 to the next gate | H | M | nrpic-run budget | ask for the raise at G2 |
| 15 | Overlap with the authors of arXiv:2609.14218 | M | M | arXiv | H1 and the converged line first |
| 16 | Newtonian mode lacks the SR push and the deformed-ball generator in make_ic.py (core deferred); energy off by 1e-3 to 3e-2 at sub-cell crossings, cause unknown | M | L-M | newton/JOURNAL.md entry 8 | own generator meanwhile; question to core (newton-mode-followup) |
| 17 | G2 asks convergence of the horizon-formation time and a horizon-mass error ~1e-3; the source's OS test saw no monotonic convergence of the horizon mass (main.tex:1484-1485, verifier C7) | M | M: G2 criterion may be unreachable as written | | report the measured mass error with its N and dx dependence; ask orch if it stalls |
| 18 | First horizon of data set 2t (areal radius 0.161 M) is below one cell in non-comoving gauges (SR-2: largest 2m/R 0.34) | realized | H for the G2 horizon test | | data set with a horizon of several M; central refinement (outbox amr-for-first-horizon) |
| 19 | Non-finite runs keep going with exit 0 (S1 spent a third of its card time on non-finite fields) | realized | M: card time, misread outcomes | first non-finite record | stop option asked of core; every analysis checks finiteness |
| 20 | Periodic constraint control on refined levels: H_r max above 0.1 before collapse (S2 from 36 t_H; S1 0.16 at the first pancake) | realized | H: threshold definition's bound fails | L2 norms (not available on multilevel meshes) | refined-level solve, nested lattice, diagnostics (outbox) |
| 21 | Adaptive refinement crashes with nrpic_cosmo (user_ref_func never set) | certain until fixed | H for the scan cost | | one-line fix asked of core |
| 22 | Periodic generator: make_field has a first-order super-horizon error and fails for mu >= 0.5; the CMC route diverges at mu = 0.5 | certain | H | | Newton step in core's id-solver (outbox phase1-generator-cmc) |

## Decision requested from the group

Lead of A-emd-pbh (wave 2): G0 is complete except C18. The problem statement, ranges, exit criteria and test plan (scope/SCOPE.md, corrected in 10.9 after the verifier), the key references in the knowledge base (all twelve ingested, 152 of 170 claims verified), the risk list, the compute estimate (now confirmed by measured cost), the working note v0 and both schematics are in place, and the automated re-verification passes. A fresh verifier wrote VERIFIER.md and the lead reproduced it exactly, but no verifier has recomputed the note's ledger. Request: accept G0 with C18 carried to G1 (a verifier session for the ledger, newton/ and criteria/ is asked in outbox gate-review-g0-g1), or name what else is missing; the lead does not pass the gate.

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

## Why the computed verdict is FAIL, and what closes it (lead, end of wave 2)

The note helper's version of this section (commit 088a387) listed C2, C18 and the verify failures `clean` and `runs`; state after the lead's session:
- C2 is now PASS: the knowledge base holds all twelve key references with 152 of 170
  Track-A claims verified (snapshot kb-20261115-44b7406); claim 25 (the particle bracket)
  awaits a kb status update (outbox claim-status-s1), read at the source by the lead.
- verify: PASS on commit 2b756f5 (all checks; the earlier `clean` and `runs` failures came
  from helpers' work in flight and from the lead's misplaced output, both resolved).
- Disagreements 1-6 above are resolved: 1-2 corrected (SCOPE.md 10.3, RISKS row 11, the
  lead's journal entry of wave 2), 3 and 5 by the rewritten STATUS/HANDOFF, 4 noted (both
  values agree to the printed digits), 6 corrected in SCOPE.md 10.9 and proposed to orch
  (outbox decision-0013-reason).
- The only item left: C18, a verifier's recomputation of the note's ledger (OPEN.md item 1).
