# verify_g0 journal: independent verifier of the G0 plan of F-hills

Helper package of F-hills, wave 3 round 1. Predictions are written before each check,
outcomes after. Labels: [VERIFIED] recomputed here or read at the source; [BACKGROUND];
[JUDGEMENT]; [TO VERIFY].

## Entry 1 (2026-11-20 14:35 PST): what I read, and the claims list with predictions

Read before writing this entry: `CLAUDE.md`, `harness/RULES.md` section nrpic-run, brief lines
466-492, 674-686, 804-822, decisions 0005, 0010, 0013, 0014, 0016, 0017, the F-hills rows of
`coord/BRIEF_ERRATA.md`, `stage/G0/{SCOPING.md, README.md, EVIDENCE.md, CHECKLIST.md}`,
`note/main.tex`, `note/tables/{ledger.tex, parameters.tex}`, `note/scripts/{ledger.py,
common.py}`, `novelty/NOVELTY.md`, `newton3/README.md`, `geodesic_binary/README.md`, the two
passage inputs, `coord/INTERFACES/multi_puncture.md` lines 220-236. Not read (forbidden until
sections 1-3 of VERIFIER.md are committed): REVIEW.md, SECOND_CHECK.md, second_check/,
checks/, VERIFY_RESULTS.*, STAGE_REPORT.md, OPEN.md, stage/G0/JOURNAL.md, REVIEW-wave2.md,
review_wave2/, G1/, the owner's JOURNAL/STATUS/HANDOFF/RISKS/PLAN-wave3, scratch/orch/,
outbox/. Note: CHECKLIST.md and the G0 README (both allowed) summarise conclusions of the
earlier second check in one line each (C18 evidence; README "Requests" R1-R3); I saw those
lines.

The claims on which the G0 plan rests (K1-K20), where the track states each, how I check it,
and what would make it WRONG.

| id | claim | where stated | check | WRONG if |
|---|---|---|---|---|
| K1 | No Hills-type full-NR calculation published (binary separated by a heavier hole, q > 1, near-parabolic, r_p <~ r_t); no full-GR matter binary passing a hole | SCOPING 1 l.29-34; note Intro l.35; novelty/NOVELTY.md Verdict | own kb searches (8+ queries), kb citation graph of the closest papers; the closest papers' set-ups at the source (2406.11985 massratio_table, 2505.03934, 0710.0879) | a kb hit (or a paper the closest ones cite or are cited by) reports such a full-NR calculation |
| K2 | Restricted coplanar problem reproduces SKR (0911.1136): last disrupting D 2.085 (2.1 printed) prograde, 0.405 retrograde (0.44 printed; differs, reproduced only with a wide-binary criterion), deep-limit P 0.807/0.801 (about 0.8), max E 27.15 at D = 0.1 (27.3) and 1.838 (1.8), best D 0.16 (0.15) | SCOPING 7 row 1, 8; note IV A, ledger 1; newton3/README P1, P7, P8 | printed values at prp.tex; own restricted integrator (prp.tex:224-259, energy 353-357), 3000 phases at 11 D values | my P_dis differs from the track's by more than 0.02 at a D away from an edge, my prograde edge is outside 2.06-2.11, or max E at D = 0.1 differs by more than 2 percent |
| K3 | Isotropic scan follows the BKRS (1804.02911) fits within 0.015 (P) and 0.017 (E) fractional for D <= 1; plateau about 0.88 | ledger 1; note IV A; newton3 P2 | printed fit coefficients mnras.tex:372-379, 433-441; own evaluation of the fits against the run's P(D), E(D) | the fit I evaluate differs from the run's `P_fit_BKRS` column, or the deviation exceeds the stated numbers |
| K4 | 1201.4794 (KHSR) is covered by the Newtonian baseline ("and 1201.4794") | SCOPING 7 row 1; brief l.476 asks for it | read KHSR at the locators newton3 uses; list which KHSR results were reproduced | (PARTLY expected) no KHSR result itself reproduced |
| K5 | The geodesic-plus-Newton model (HRNA) reproduces 2404.16270: separated fraction within 0.0225 of its figure, mean v_inf within 0.73 percent, retrograde onsets beta = 1.9 (HRNA) and 2.5 (Newton) | SCOPING 7 row 2; note IV B, ledger 1 | equation at article.tex:246-261; own HRNA (Schwarzschild, Cartesian form) at 2404's set-up, beta = 3 and 10, both senses, 120 phases | my separated fractions differ from the ledger's (0.98, 0.295, 0.985, 0.51 at beta 3; 0.985, 0.58, 0.993, 0.91 at 10) by more than 3 binomial sigma |
| K6 | Plunge bound a_b/r_gb > 4 q^(2/3) = 18.57, 86.18, 400.0 (q = 10, 100, 1000); r_mb = 4 M, L_mb = 4 M; correction of brief l.275: needs a_b >= 29.5 r_gb at q = 20, >= 38.6 at q = 30 | SCOPING 4; note II B eq. (4); errata row 1.5 | closed form; marginally bound orbit from the effective potential numerically; logic of "needs" | numbers differ in the third digit; or the bound is not a necessary condition for separation before a plunge |
| K7 | Peters time (5/64)(a_b/r_gb)^4 m_b = 6328 M at a_b = 30 r_gb, q = 10, against a passage of 160-290 M | SCOPING 4; ledger 1 | closed form from the Peters formula for an equal-mass circular binary | 6328 not reproduced |
| K8 | Scales of the first passages: q = 10, a_b = 3 M = 30 r_gb, r_t = 6.46 M; q = 4, a_b = 5 M = 20 r_gb, r_t = 7.94; member speed 0.09 c; HRNA consistency a_b/R_curv = 0.13 at 8 M, 0.06 at 13 M; tidal over binding 0.031 at 4 r_t; D ranges 1.08-2.01 (q = 10), 9.8-16 M (q = 4) | SCOPING 3, 4; note II B; parameters.tex | closed forms; article.tex:272-279 and appendix.tex:6-12 | any of these differ beyond rounding |
| K9 | Start states of the passages (input files): q = 10: a_b 3.036, e_b 0.029, CM conic r_p 7.9965, e 1.00006, start 25.85 M (4 r_t); q = 4: 5.111, 0.033, 9.8087, 1.00023, 31.75; total momentum zero | SCOPING 6; parameters.tex | own computation from the puncture positions and momenta of `hills_q10_m8.athinput`, `p1_q4.athinput` (= hills_q4_m8 problem block) | any value differs beyond the printed digits |
| K10 | Newtonian outcome of those states: q = 10 m1 ejected +1.6127 units (barycentric; 2.90e-3 M), m2 captured -1.845, closest 5.641 M, captured orbit a 7.55, e 0.247, r_p 5.68; q = 4 m1 ejected +1.3119, m2 -1.627, closest 5.777 M; heavy hole moves 13.3 M by t = 280; two-body energy with M oscillates (1.474-1.845, 0.989-1.723) | SCOPING 6, 10; note IV D; ledger 2 | own Newtonian three-body integration (SciPy DOP853, my own right-hand side and energies) from the input states | outcome class differs, or energies differ by more than 0.5 percent |
| K11 | HRNA outcome of the same states (relative to M): q = 10 m1 crosses r = 2.5 M at t = 97.1 M, m2 ejected with +1.159 units; q = 4 m2 ejected +0.9703, m1 bound (-0.5), first pericentre 7.262 M | SCOPING 6; note IV D; ledger 2 | own HRNA integrator from the same states | outcome class differs, plunge time off by more than 1 M, or energies off by more than 2 percent |
| K12 | Reading of the start states in GR: r_p is the Newtonian conic pericentre "reported together with the Schwarzschild pericentre of the same E and L"; the first passage at q = 10 is at r_p = 8 M (D = 1.24) | SCOPING 3 (definition), 6; note II, IV | own E, L of the CM state in Schwarzschild and in isotropic reading; turning point | (prediction) the GR turning point of the CM is well inside 8 M (my estimate before computing: about 5.7-5.8 M, since L_N = (2 (M+m_b) r_p)^(1/2) = 4.20 M is close to 4 M); claim WRONG in effect if SCOPING gives no GR pericentre while the plan reads "r_p = 8 M" as the encounter depth |
| K13 | Pericentre scan (V7): q = 10 r_p = 8: Newton sep. 0.88, a member inside 4 M 0.056; HRNA sep. 1.0, plunge 0.94; r_p = 12: HRNA plunge 0.69; r_p = 13: Newton sep. 0.22, HRNA sep. 0.98, plunge 0.30; q = 4 r_p = 9.82: 0.84, 0.30; 0.99, 0.94; r_p = 16: 0.54, 0.011; 0.94, 0.67. "The two references disagree in kind" | SCOPING 4; note IV C, Fig. 5, abstract, summary; ledger 2 | own scans (Newton 10 -> 4 r_t then each model), 180 phases at q = 10 r_p = 8, 13 and q = 4 r_p = 9.82; and a GR-matched CM start (E = 1, L of a Schwarzschild parabola with pericentre r_p) for HRNA at q = 10 r_p = 8, 13 | my fractions differ by more than 3 binomial sigma (about 0.06 at p = 0.5, 180 phases) with the same construction; (prediction for the GR-matched start: the HRNA plunge fraction at r_p = 8 falls well below 0.94, so part of the "disagreement in kind" comes from feeding Newtonian parabola velocities to the geodesic model) |
| K14 | Mesh and cost: MeshBlocks start/max/mean and card-hours: q = 10 m/8 1800/2332/2006, 38.9 (37.0-42.3) for 240 M; m/16 99-156; q = 4 m/8 1716/2080/1744, 15.2 for 270 M; m/16 2514/2864/2568, 44.8; rate 2022/2201/2310 MeshBlock-cycles per second; one global step dt = 0.25 h_min; about 3000 slots per card ("2864 above the 2700 slots of one card") | SCOPING 9; note IV E; ledger 2 | arithmetic from the trees n(t) in the run outputs (my own sum), dt from the AthenaK source, rates from the novelty run output, `athena -m` rerun of the t = 0 trees of both inputs with the release processor executable | card-hours differ by more than 1 percent from my recomputation; t = 0 tree differs from 1716 / 1800 |
| K15 | Programme compute: G1 36-40 card-hours; G2 about 120 (15 + 28 + 41 + 30 + 12 + 5 + contingency); G3 about 500; allotment 50 (0014) then 120 (0016) | SCOPING 9 last paragraph | arithmetic; decisions 0014, 0016 | (prediction) the G2 items sum to 131 before contingency, so "about 120" is low |
| K16 | Parameter ranges and first values are consistent with decision 0013 (q = 4 for the convergence study and the first scan line; q = 10 when the mesh fits) | SCOPING 3 ("10 for the first passage"), 6 (q = 10 passage named for G1), 9; note II B, V | compare with decision 0013 and with the note | (prediction) SCOPING 3 and 6 still name q = 10 for the first passage, against 0013 and the note |
| K17 | Exit-criteria numbers: 3BH1 of 0710.0879 E_rad = (6.06 +- 0.02)e-3 M (first.tex:291), 11 levels, h = M/80, boundary 640 M (first.tex:141-146); 1004.1353 statements (Punc_N.tex:185-194, 1238-1261); 2402.02178 "intractable" (main.tex:224-225) | SCOPING 5, 8 | read at the source | the source does not say it |
| K18 | Start radius: a start at 10 r_t keeps 95/97 percent (M/m = 1e6 / 10) of the outcomes of a 40 r_t start, 5 r_t only 92/90 percent; SKR's 10 r_t "sufficient for convergency" (prp.tex:597-599) | SCOPING 3 row "start"; newton3 P4 | recompute the fractions from the per-phase outcomes of `p4.npz` (run F-hills-20261115-131801-907e5fe) | my fractions differ |
| K19 | 2406.11985 configurations: q = 4.0, 9.0, a_b = 9.9 r_gb, D/r_t = 4.1, 5.8; below the plunge bound (10.1, 17.3); "could be continued ... until 128:1:1" | SCOPING 8; NOVELTY | arithmetic on massratio_table.tex; TBH3.tex:708-712 | numbers differ |
| K20 | Every number of the note's ledger (appendix app:ledger) comes from the named run | note app:ledger; CHECKLIST C18 | own script reads each run output (sha256 checked) and recomputes each row; selected rows also from raw arrays (coplanar.npz, p4.npz, mesh trees, passage_curves.npz) and from my own integrations | a row's value differs from my recomputation |

Prediction for the whole: most numbers are transcribed correctly (the ledger is generated by a
script from the run outputs); the defects, if any, are of interpretation: K6 ("needs"), K12/K13
(construction of the geodesic start state), K15 (sum), K16 (stale q = 10 plan).

## Entry 2 (2026-11-21 03:00 UTC, evening batch): restart, scope of C18, plan of the runs

Restart. The burst session of 14:00-14:35 PST committed entry 1 (dc5d3d31) and left four
uncommitted scripts (`closed_forms.py`, `vint.py`, `restricted.py`, `threebody.py`) and no
results. I read them in full, reran each on small cases into `scratch/F-hills/tmp/verify_g0/`
(debugging only, not evidence) and kept them; one change: self-test (e) of `threebody.py` now
compares the model's flat-space limit with Newton whose pair force is scaled by Gamma^-2 = f - v^2
(the model's own prescription, article.tex:246-261 with g^ij -> delta^ij); plain Newton differs
by O(v^2) by construction (0.156 return error after one period at v = 0.09, as found in the
trial). `kb_novelty.py` is new (K1).

Scope of C18. The note's ledger (`note/tables/ledger.tex`) now has three tables. Tables 1 and 2
(`tab:ledger1`, `tab:ledger2`, 63 rows) are byte-identical to the ledger at a717db0d, the state
of the G0 plan; table 3 (`tab:ledger3`, 37 rows of full-relativity runs) was added at 156c8be5
(2026-11-20 14:29 PST) by the G1 revision of the note, after the planner's brief, and is G1
material (decision 0016 item 4: a verifier of later material belongs to G1). I recompute every
row of tables 1 and 2; table 3 rows are recomputed only where my own G0 checks give them for
free (the q = 10 GR turning point) and are otherwise listed as not checked here.

Plan and how each check can fail (predictions of entry 1 stand; additions):
- R1 `closed_forms.py` (K6-K9, K12, K14, K15, K19). WRONG if a closed form differs in the
  third digit, or my sum of the trees n(t) differs from the ledger's card-hours by > 1 percent.
  Addition for K6: I predict that 4 q^(2/3) is the condition r_t >= r_mb (D = 1 at the plunge
  radius), not a necessary condition for separation, since the restricted problem separates up
  to D = 2.085 (prograde): the necessary condition would then be about 4 q^(2/3)/2.085.
- R2 `threebody.py --mode selftest`: WRONG (my HRNA, not the claim) if E, L drift > 1e-8, the
  pericentre advance differs from the elliptic integral by > 1e-6, or the static acceleration
  is not -(1 - 2/r)/r^2.
- R3 `threebody.py --mode passages` (K10, K11, ledger rows of the first passages).
- R4 `threebody.py --mode scan`, 180 phases, q = 10 r_p = 8, 13 and q = 4 r_p = 9.82, 16 (K13).
  Trial at 24 phases (debug): GR-matched plunge 0.96 at q = 10 r_p = 8, so my entry-1 prediction
  "falls well below 0.94" is likely to FAIL; it stands as written and is judged on the 180-phase run.
- R5 `restricted.py`, 3000 phases at 14 (sense, D) (K2, ledger restricted rows).
- R6 `kb_novelty.py` (K1): 12 queries x 2 modes, corpus citation graph and INSPIRE metadata
  of nine closest papers. WRONG (the verdict) if any hit reports a full-NR calculation of a
  binary separated by a heavier hole, or a full-GR matter binary passing a hole.
- R7 `ledger_check.py` (C18): every row of tables 1-2 recomputed from the raw arrays of the
  named run (coplanar.npz, general.npz, v4_samples.npz, passage_curves.npz, the per-time
  `athena -m` stdout of the mesh runs, counts.txt) where they exist, otherwise from the
  summary JSON plus an independent route (my R1-R5) or the paper source. Prediction: all
  transcriptions agree (the ledger is script-generated); at most a few rows whose summary
  number cannot be reached from raw data (digitised third-party curves, the readers' test).

## Entry 3 (2026-11-21 03:10 UTC): K5 by an independent route, prediction

`threebody.py --mode s1` (new): my HRNA at the set-up of 2404.16270 as the paper states it
(article.tex:300-348; appendix.tex:138-179: members at +-a0/2 with the Newtonian circular
velocity, CM at (r0, 0) with r0 = 50 r_t on the Schwarzschild parabola E = 1,
L = (2 rp^2/(rp - 2))^(1/2), rp = r_t/beta, r_t = 101.3 M, M/m_b = 1e6, stop at 150 r_t;
phases k pi/200). Note at the source: the paper's separation fraction is the length of the
phase interval holding all separations over pi (article.tex:455-458), not a count; I count.
Prediction: HRNA separated fraction at beta = 3 (pro, retro) and 10 (pro, retro) within three
binomial sigma (about 0.03 at p = 0.9, 0.1 at p = 0.5 with 200 phases) of the ledger's
0.985, 0.51, 0.993, 0.91 (run F-hills-20261115-142554-c10b371). WRONG if outside. A debug
trial (16 phases, beta = 10) gave 1.0 and 0.875.

## Entry 4 (2026-11-21 03:15 UTC): first outcomes, and a hypothesis about the V7 scan

Outcomes so far (details in VERIFIER.md when written):
- R1 F-20261121-030100-b88c2d3: closed forms reproduce 18.57/86.18/400, r_mb = L_mb = 4, Peters
  6328.1, scales, start states, card-hours (plain mean of my recount within 0.4 percent of the
  ledger's trapezoid). K6 prediction CONFIRMED in substance: 4 q^(2/3) is the condition
  r_t > r_mb; separation needs only D <~ 2.085 at r_p >= 4 M, i.e. a_b/r_gb >~ 4 q^(2/3)/2.085
  (14.1 at q = 20, 18.5 at q = 30). K15 prediction CONFIRMED: G2 items sum to 131 before
  contingency against "about 120". K12: q = 10 start state turns at 5.77 M (isotropic, P/m
  reading) or 7.00 M (Schwarzschild-coordinate reading), not 8 M; the GR parabola with
  pericentre 8 M needs L = 4.618 against L_N = 4.194.
- R2 F-20261121-030102-acb4dbd: my HRNA passes its self-tests (E, L to 4e-13 / 6e-12;
  pericentre advance to 4e-9; static acceleration exact; flat limit 1e-6).
- R3 F-20261121-030138-8d3ca16: every Newtonian passage number of the ledger reproduced; HRNA
  q = 10 plunge crossing at t = 96.90 (ledger 97.1, a sample time); q = 4 HRNA ejected energy
  drifts 0.978 -> 0.965 between t = 600 and 1500 (ledger 0.9703 lies inside).
- R5 F-20261121-030155-1061bcb: sample-by-sample identical to the track's coplanar scan at all
  14 points (same phases, my own integrator): K2 CONFIRMED (edges 2.085 and 0.405 also with wide
  binaries followed to 300 r_t; retrograde D = 0.1 identical, which closes the V4 difference
  the note still calls open at D = 0.1). Figure fig_restricted.png read (legend typo "retgrade"
  in my own figure, cosmetic).
- R6 F-20261121-030205-c4d2894: hybrid mode failed in every query (torch not found under
  nrpic-run); rerun R6b F-20261121-030306-e8533e8 with the fix.
- R4 (running) at q = 10, r_p = 7 and 8: HRNA hand-off plunge 0.978 and 0.944 (track 0.96, 0.94)
  but Newton "member inside 4 M" 0.494 and 0.011 against the track's 0.62 and 0.056 (3.4 and
  2.6 sigma), separated 0.878, 0.850 against 0.90, 0.88. My GR-matched start (the 2404 CM
  construction, appendix.tex:173-179) plunges 0.944 and 0.911: entry-1 prediction for K13
  ("falls well below 0.94") FAILED; the hand-off artefact is small at these r_p.

Hypothesis H-mu (to test before I may read the lead's script): the track's V7 gave the CM the
test-mass parabola speed of M alone (L = (2 M r_p)^(1/2)) instead of the two-body parabola of
M + m_b, so its encounters are slightly bound and deeper. Prediction: with `--mu-conv M`, my
Newton fractions at q = 10, r_p = 7 and 8 move to the track's 0.62 and 0.056 (inside 4 M)
within 3 sigma. Refuted if they stay at 0.49 and 0.01, or overshoot beyond 3 sigma.

## Entry 5 (2026-11-21 03:20 UTC): H-mu outcome, kb searches, sources, extras

- R8 F-20261121-031300-a59f41f (H-mu): with the test-mass parabola speed of M alone, Newton
  "member inside 4 M" becomes 0.689 (r_p = 7) and 0.417 (r_p = 8) against the track's 0.622 and
  0.056: overshoots at r_p = 8 by far. H-mu REFUTED. The separated fractions under H-mu (0.911,
  0.878) do match the track's (0.90, 0.88) better than mine (0.878, 0.850), but the inside-4 M
  fraction does not. The cause of the difference in that diagnostic stays open [TO VERIFY after
  sections 1-3, by reading the lead's script]. The diagnostic is steep in the encounter depth.
- R6b F-20261121-030306-e8533e8: 12 queries x 2 modes, all hybrid queries answered. Union of
  hits: 58 papers. No hit reports a full-NR calculation of a binary separated by a heavier hole
  or a full-GR matter binary passing a hole. The NR candidates (2610.09336 head-on collisions,
  abstract line 129; 2505.03934 equal masses, apssamp.tex:246; 2308.07365 equal masses, d = 8 M,
  D = 30 M, TBH.tex:66; 2406.11985 q = 4, 9 bound, my R1; 2605.20320 head-on, not opened by me
  beyond the novelty file's locator) are all in NOVELTY.md. Corpus citation graph: 2406.11985 is
  cited in the corpus by 2505.03934, 2605.20320, 2610.09336 only. INSPIRE metadata of the
  closest papers carries citation counts (2406.11985: 9 as fetched 2026-11-15) but no citing
  list; I ran no new INSPIRE query (not granted; it would write into kb-data). K1 CONFIRMED
  within these limits.
- Sources read: 0710.0879 first.tex:141-146 (11 levels, h = M/80, boundary 640 M) and :291 with
  the table header 288-289 (6.06 +- 0.02 is the 3BH1 column); 1004.1353 Punc_N.tex:185-194
  ("finite error that does not converge", "change dramatically") and 1252-1258 ("one order of
  magnitude bigger" junk difference); 2402.02178 main.tex:225 ("intractable"); 2406.11985
  TBH3.tex:710 ("at least until 128:1:1"); prp.tex:597-599, 748-749, 784-785; mnras.tex:368,
  375-377, 437, 440; article.tex:246-279, 300-348, 455-458; appendix.tex:6-12, 138-179. All
  as the track quotes them.
- Extras (trial of the ledger check): K18 from p4.npz: 10 r_t keeps 0.95 (M/m = 1e6) and 0.97
  (10) of the 40 r_t outcomes, 5 r_t 0.92 and 0.90 (SCOPING 3 says "5 r_t only 90 percent":
  0.92 at 1e6). K8: in the track's own S1 scan alpha = a/R_curv reaches 0.199 at beta = 10
  and 0.148 at beta = 8.5 at pericentre (alpha_all); the ledger's 0.0056 is the maximum only
  while the instantaneous pair energy is negative. K14: the card smoke F-20261115-174602-c6879fe
  peaked at 70847 MiB with a slot limit of 2700 (26.2 MiB per slot all-in; 81920 MiB card).

## Entry 6 (2026-11-21 03:25 UTC): r_p = 13 disagreement, hypothesis H-u, prediction

R4b F-20261121-031920-5e6425e (q = 10, r_p = 13, 180 phases): Newton separated 0.422 against
the track's 0.22 (about 6 sigma), HRNA hand-off separated 0.939 (0.98) and plunge 0.017 against
0.30; my GR-matched start plunges 0.161. At D = 2.01 the encounter sits on the edge of the
restricted problem (P falls from 0.31 at D = 2.0 to 0 at 2.09, R5), so small differences of
construction move the Newton fraction a lot; the HRNA plunge difference is not explained by
that. Physical estimate [JUDGEMENT]: with the hand-off CM L = 5.86 (E = 1.010) a member loses
about 13 x 0.09 = 1.2 in L at pericentre, so stays above the plunge value 4: plunges should be
rare at 13 M, as I find.

Hypothesis H-u: the track's V7 fed the Newtonian velocities to the HRNA as u^i = dx^i/dtau
(not dx/dt), which lowers the CM's L in the Schwarzschild reading from 5.86 to about 5.3 at
r_p = 13 and deepens the encounter. New construction `hrna_u` in `threebody.py --with-u`
(plus a per-trajectory step cap, `--max-steps`, after R4 spent more than 15 minutes on
r_p = 12). Prediction: with `hrna_u` the HRNA plunge fractions at q = 10, r_p = 8, 12, 13 move
to the track's 0.94, 0.69, 0.30 within 3 sigma (0.05, 0.10, 0.10). Refuted if they stay near
my hand-off values or miss by more than 3 sigma. A 12-phase debug trial at r_p = 13 gave plunge
0.17 (not evidence).

## Entry 7 (2026-11-21 03:50 UTC): K5 outcome; run housekeeping

- R7b F-20261121-032325-f58a391 (beta = 10) and R7c F-20261121-032337-9c6d87a (beta = 3), my
  HRNA at 2404's own set-up, 200 phases, step cap 400000 per phase (5 phases capped of 800,
  excluded): separated fraction beta = 3 pro 0.990, retro 0.510; beta = 10 pro 1.000, retro
  0.915, against the ledger's 0.985, 0.51, 0.993, 0.91 (count fractions of 400 phases, s1.npz).
  All within 3 sigma: prediction of entry 3 MET, K5 CONFIRMED by an independent code at two
  beta. The uncapped R7 F-20261121-030701-734c74b was stopped (no case finished in 37 min;
  record: failed/stopped, kept).
- R4 F-20261121-030146-34ad97e stopped after 20 min on r_p = 12 (its scan.json holds r_p = 7, 8,
  checksummed at finish). Replaced by capped runs R4d (q = 10, r_p = 12) and R4e (q = 4,
  r_p = 16); R4c F-20261121-031930-a640847 (q = 4, r_p = 9.82 done, 16 running, uncapped) and
  R10 (H-u) still running.
- R4c, q = 4, r_p = 9.82: Newton separated 0.800 (track 0.84), inside 4 M 0.189 (0.30, 3.3
  sigma), HRNA hand-off separated 0.961 (0.99), plunge 0.850 (0.94, 4.5 sigma); GR-matched plunge
  0.894. My encounters are again shallower than the track's in every diagnostic.
