# Independent verification of the G0 plan of F-hills (S12, the Hills mechanism)

Verifier package `tracks/F-hills/verify_g0/` (wave 3, round 1), 2026-11-20/21, given the
artefacts and not the conclusions of anyone who checked them before. Evidence labels:
[VERIFIED] recomputed here (run id) or read at the source (file:line); [BACKGROUND] standard, not
checked; [JUDGEMENT] mine; [TO VERIFY] open. Predictions and outcomes of every check:
`verify_g0/JOURNAL.md` (entries 1-8). Paper sources under
`kb-data/raw/arxiv/<id>/<version>/src/` (read as data).

**Read before sections 1-3 were written and committed:** `CLAUDE.md`, `harness/RULES.md`
(nrpic-run), brief lines 466-492, 674-686, 804-822, decisions 0005, 0010, 0013, 0014, 0016,
0017, the F-hills rows of `coord/BRIEF_ERRATA.md`; `stage/G0/{SCOPING.md, README.md,
EVIDENCE.md, CHECKLIST.md}`; `note/main.tex`, `note/tables/{ledger.tex, parameters.tex}`,
`note/scripts/{ledger.py, common.py}`; `novelty/NOVELTY.md`; `newton3/README.md` and the
scripts `newton3/scripts/{digitize_skr.py, digitize_bkrs.py}` (to mirror the comparisons with
digitised curves), `geodesic_binary/{README.md, analysis_s1.py, hrna.py}` (definitions of the
S1 diagnostics), the two passage inputs, `coord/INTERFACES/multi_puncture.md` lines 220-236,
`nr_first/JOURNAL.md` lines 620-630 (card memory of the smoke); run outputs under
`scratch/F-hills/`. CHECKLIST.md and the G0 README (allowed) carry one-line summaries of the
earlier second check (C18 evidence, README Requests R1-R3); I saw those lines.
**Not read before sections 1-3 were committed:** `stage/G0/{REVIEW.md, SECOND_CHECK.md,
second_check/, checks/, VERIFY_RESULTS.*, STAGE_REPORT.md, OPEN.md, JOURNAL.md}`,
`stage/REVIEW-wave2.md`, `stage/review_wave2/`, `stage/G1/`, the owner's
`JOURNAL/STATUS/HANDOFF/RISKS/PLAN-wave3`, `scratch/orch/`, `outbox/`. In particular I did not
read the lead's check script `stage/G0/checks/lead_checks.py` (V4-V7), so my own codes are
independent of it.

Scope. The G0 plan is `stage/G0/SCOPING.md` with the working note. The note's ledger has three
tables today; tables 1 and 2 (`tab:ledger1`, `tab:ledger2`, 57 rows) are byte-identical to the
ledger of the G0 state (a717db0d); table 3 (37 rows) was added by the note's G1 revision on
2026-11-20 14:29 PST, after the planner's brief, and belongs to G1 (decision 0016 item 4). C18
below recomputes every row of tables 1-2; of table 3 only the rows my G0 checks give for free.

## Runs

All local, registered with `harness/bin/nrpic-run` (kind scouting, gate G0, package
`tracks/F-hills/verify_g0`), one core each unless stated, no card time; outputs under
`scratch/F-hills/<run id>/`, figures copied to `verify_g0/figures/`, summaries to
`verify_g0/results/`. My codes (`verify_g0/scripts/`) share nothing with the track's: own
Dormand-Prince 5(4) integrator (`vint.py`), own restricted problem from prp.tex:224-259
(`restricted.py`), own Newton three-body and own HRNA in Cartesian Schwarzschild form from
article.tex:246-261 (`threebody.py`), own closed forms (`closed_forms.py`), own ledger
recomputation (`ledger_check.py`), own kb searches (`kb_novelty.py`).

| Run | Script, what | Claims |
|---|---|---|
| F-20261121-030100-b88c2d3 | `closed_forms.py`: plunge bound, marginally bound orbit, Peters time, scales, start states of the two inputs and their GR readings, cost from the mesh trees, 2406.11985 table | K6-K9, K12, K14, K15, K19 |
| F-20261121-030102-acb4dbd | `threebody.py --mode selftest`: my HRNA against exact geodesics (E, L, pericentre advance, circular orbit, static release, flat limit) | (my tool) |
| F-20261121-030138-8d3ca16 | `threebody.py --mode passages`: Newton, fixed-hole Newton and HRNA from the two input files, to t = 1500 M | K10, K11, C18 |
| F-20261121-030146-34ad97e | `threebody.py --mode scan`, 180 phases: Newton 10 r_t -> 4 r_t, then Newton, HRNA hand-off (the state relative to M, Newtonian velocities as dx/dt), HRNA with the CM put on the Schwarzschild parabola of pericentre r_p ("GR-matched", 2404's CM construction, appendix.tex:173-179); cases q = 10 r_p = 7, 8 done, then hung on r_p = 12; stopped after 20 min (record: failed), its two finished cases are used | K13 |
| F-20261121-031920-5e6425e | the same scan, q = 10 r_p = 13 | K13 |
| F-20261121-031930-a640847 | the same scan, q = 4 r_p = 9.82 done; stopped on r_p = 16 (record: failed) | K13 |
| F-20261121-034434-0113a18 | the same scan with a cap of 200000 steps per phase, q = 10 r_p = 12 | K13 |
| F-20261121-034441-f211f65 | the same, q = 4 r_p = 16: still running when sections 1-3 were committed (pending) | (K13) |
| F-20261121-030155-1061bcb | `restricted.py`, 3000 phases at 14 (sense, D) against `coplanar.npz` | K2, C18 |
| F-20261121-030205-c4d2894 | `kb_novelty.py`, first run: BM25 answered, every hybrid query FAILED (torch not found under nrpic-run); kept on record | K1 |
| F-20261121-030306-e8533e8 | `kb_novelty.py` rerun with the kb worktree's interpreter: 12 queries x 2 modes, citation graph, INSPIRE metadata of nine papers | K1 |
| F-20261121-030701-734c74b | `threebody.py --mode s1`, beta = 3 and 10 uncapped: no case finished in 37 min (a few phases need very many steps); stopped, record kept | (K5) |
| F-20261121-032337-9c6d87a, F-20261121-032325-f58a391 | `threebody.py --mode s1` with a cap of 400000 steps per phase: my HRNA at the set-up of 2404.16270 (r0 = 50 r_t, Schwarzschild parabola, M/m_b = 1e6), beta = 3 (R7c) and 10 (R7b), both senses, 200 phases | K5 |
| F-20261121-031300-a59f41f | `threebody.py --mode scan --mu-conv M`: hypothesis H-mu about the V7 scan (refuted) | K13 |
| F-20261121-032150-8309634 | `threebody.py --mode scan --with-u`: hypothesis H-u (velocities read as u^i); no case finished in 35 min, stopped (record: failed); H-u NOT TESTED | (K13) |
| F-20261121-035817-0aca1c5 | `ledger_check.py` (R9): every row of ledger tables 1-2, extras for K8, K14, K18 | C18, K8, K14, K18 |
| F-20261121-035825-975e07b | `fig_scan.py` (R11): my scans and 2404 runs against V7 and S1 (`figures/fig_scan.png`, read) | K5, K13 |

Self-test of my HRNA (F-20261121-030102-acb4dbd): E and L of a free geodesic (E = 0.97,
L = 3.9) conserved to 4e-13 and 6e-12; pericentre advance equal to the elliptic integral to
4e-9; circular orbit at r = 10 M kept to 5e-8; static release gives -(1 - 2/r)/r^2 exactly;
the flat limit equals Newton with each member's pair force times Gamma^-2 to 1e-6 (plain Newton
differs by O(v^2), 0.156 after one period at v = 0.09, by construction of the model).
[VERIFIED]

## 1. Verdicts

| # | Claim (where the track states it) | Verdict | Evidence |
|---|---|---|---|
| K1 | No Hills-type full-NR calculation published (heavier hole separates a binary on a near-parabolic orbit with r_p <~ r_t), and no full-GR matter binary passing a hole (SCOPING 1; NOVELTY.md Verdict; note Sec. I) | CONFIRMED within the limits below [JUDGEMENT on an absence] | R6b F-20261121-030306-e8533e8: 12 queries, hybrid and BM25, 58 distinct papers hit (`results/kb_hits.md`). No hit reports such a calculation. NR candidates, read at the source: 2505.03934 all holes of equal mass (apssamp.tex:246); 2308.07365 inner binary d = 8 M, third hole at D = 30 M (TBH.tex:66); 2610.09336 head-on collisions from rest (Liu_article_V2.tex:129); 2406.11985 q = 4.0 and 9.0, a_b = 9.90 r_gb, D/r_t = 4.1 and 5.8, bound (massratio_table.tex, my R1); 2604.27429 PN and a scalar perturbation, "would require numerical relativity" (template.tex:45, 80). Every candidate is already in NOVELTY.md. Corpus citation graph: 2406.11985 is cited in the corpus only by 2505.03934, 2605.20320, 2610.09336. Limits: the kb corpus is a curated 710-paper set; INSPIRE metadata carries citation counts (2406.11985: 9 as fetched 2026-11-15) but no citing list; I ran no new INSPIRE query |
| K2 | The restricted coplanar problem reproduces SKR (0911.1136): last disrupting D 2.085 (printed 2.1) and 0.405 (printed 0.44), deep-limit P 0.807 and 0.801 (about 0.8), largest E 27.15 at D = 0.1 (27.3) and 1.838 (1.8), best D 0.16 (0.15) (SCOPING 7, 8; note IV A; ledger 1) | CONFIRMED | R5 F-20261121-030155-1061bcb: my own integrator gives the track's outcome phase by phase at all 14 points (dP = 0.0000, Emax and Emean equal to 1e-8; prograde D = 0.01 ... 2.09, retrograde 0.1 ... 0.41; `figures/fig_restricted.png` read). The retrograde edge stays at 0.405 with wide bound pairs followed to 300 r_t (D = 0.41: P = 0 with 467 pairs followed), so the 0.405 against 0.44 difference is real for this disruption criterion. Printed values read at prp.tex:735-738, 846-849, 854; deep limit and best D from the npz (C18 rows 4-12) |
| K3 | The isotropic scan follows the BKRS fits within 0.015 (P) and 0.017 (mean E) fractional for D <= 1; plateau about 0.88 (ledger 1; note IV A) | CONFIRMED (numbers); the note's "to about their stated accuracy" is generous | My evaluation of the printed polynomials (mnras.tex:372-377, 433-437) against `general.npz` (512 x 64): 0.0152 and 0.0173. BKRS state < 1 percent for D <~ 1 (mnras.tex:377, 440), so the scan deviates 1.5-1.7 times the stated fit accuracy [JUDGEMENT: harmless for a baseline] |
| K4 | 1201.4794 (KHSR) is covered by the Newtonian baseline (SCOPING 7: "(and 1201.4794)"; brief l. 476 and track sheet F-pre-1 name it) | NOT DONE | Only KHSR's energy combination dE = (m1/m)E2 - (m2/m)E1 is used (newton3/README.md:49-50, ms.tex:1103 read). No KHSR result is reproduced; non-parabolic orbits are listed as not done (newton3/README.md:406); the G1 criterion (i) of SCOPING 5 names only 0911.1136 and 1804.02911 |
| K5 | The geodesic-plus-Newton model (HRNA) reproduces 2404.16270: separated fraction within 0.0225 of its figure, mean v_inf within 0.73 percent, retrograde onsets beta = 1.9 (HRNA) and 2.5 (Newton) (SCOPING 7; note IV B; ledger 1) | CONFIRMED (fractions at two beta by an independent code; the comparison with the published figure recomputed; v_inf only transcribed) | My HRNA at the paper's own set-up (article.tex:300-348, appendix.tex:138-179; r0 = 50 r_t, CM on the Schwarzschild parabola, M/m_b = 1e6), 200 phases, runs R7c F-20261121-032337-9c6d87a and R7b F-20261121-032325-f58a391: separated fraction beta = 3 pro 0.990, retro 0.510; beta = 10 pro 1.000, retro 0.915, against the track's 0.985, 0.51, 0.993, 0.91 (s1.npz, 400 phases): all within 3 binomial sigma (5 of 800 phases hit my step cap and are excluded). R9: largest deviation from the digitised 2404 curves 0.0225 (retro HRNA) recomputed from s1.npz; onsets 1.9 and 2.5 recomputed (first beta with fraction > 0.01); mean v_inf deviation 0.0073 only re-read. Note: the paper's separation fraction is an interval length over pi (article.tex:455-458), the track's and mine are counts |
| K6 | Plunge bound a_b/r_gb > 4 q^(2/3) = 18.57, 86.18, 400.0; r_mb = L_mb = 4 M; hence the correction of brief l. 275: "separation before a plunge needs a_b >= 29.5 r_gb at q = 20 and >= 38.6 at q = 30" (SCOPING 4; errata row 1.5) | Numbers CONFIRMED; the "needs" PARTLY WRONG | R1: 4 q^(2/3) = 18.566, 86.177, 400.0, 29.47 (q = 20), 38.62 (q = 30); max of V^2 = 1 at r = 4.0000 M with L = 4.0000. But 4 q^(2/3) is the condition r_t > r_mb, i.e. a penetration D = 1 at the plunge radius. The restricted problem separates binaries out to D = 2.085 (prograde, K2), so a binary whose centre of mass stays outside 4 M can be separated for a_b/r_gb > 4 q^(2/3)/2.085 (8.9 at q = 10, 14.1 at q = 20, 18.5 at q = 30) [JUDGEMENT: in the Newtonian restricted sense; the relativistic edge is unknown]. The bound is a condition for deep encounters (D <= 1), not for separation |
| K7 | Peters time (5/64)(a_b/r_gb)^4 m_b = 6328 M at a_b = 30 r_gb, q = 10, against a passage of 160-290 M (SCOPING 4; ledger 1) | CONFIRMED | R1: (5/256) a^4/(m1 m2 m_b) with m1 = m2 = m_b/2 = 0.05, a = 3 M gives 6328.1 M |
| K8 | Scales: q = 10, a_b = 3 M, r_t = 6.46 M; q = 4, a_b = 5 M, r_t = 7.94 M; member speed 0.09 c; HRNA consistency a_b/R_curv 0.13 at 8 M and 0.06 at 13 M; tidal over binding 0.031 at 4 r_t; D = 1.08-2.01 (q = 10, 7-13 M), 9.8-16 M (q = 4) (SCOPING 3, 4) | CONFIRMED | R1: r_t 6.4633, 7.9370; member speed 0.0913 (q = 10), 0.1118 (q = 4); alpha = 3/8^1.5 = 0.133, 3/13^1.5 = 0.064 (definition article.tex:272-274); tidal/binding = 2q (a_b/4 r_t)^3 = 1/32 for every q; D = 1.083-2.011 and 1.237-2.016. alpha of 0.13 is "as large as in the paper's own examples" (appendix.tex:8, ~0.1) [VERIFIED] |
| K9 | Start states of the passage inputs: q = 10 a_b 3.036, e_b 0.029, CM conic r_p 7.9965, e 1.00006, start 25.85 M (4 r_t); q = 4: 5.111, 0.033, 9.8087, 1.00023, 31.75; total momentum zero (SCOPING 6; parameters.tex) | CONFIRMED | R1 from `three_punctures/inputs/hills_q10_m8.athinput` and `nr_first/inputs/p1_q4.athinput`: 3.0361, 0.0286, 7.99654, 1.000061, 25.853 (= 4.000 nominal r_t); 5.1112, 0.0329, 9.80872, 1.000235, 31.748; P_total 1e-10 and 0; binary prograde in both |
| K10 | Newtonian outcome of those states: q = 10 m1 ejected +1.6127 units (barycentric), m2 captured -1.845, closest 5.641 M, captured orbit a 7.55, e 0.247, r_p 5.68; q = 4 m1 +1.3119, m2 -1.627, closest 5.777 M; heavy hole moves 13.3 M by t = 280 (q = 4); two-body energies with M oscillate 1.474-1.845 and 0.989-1.723 (SCOPING 6, 10; note IV D; ledger 2) | CONFIRMED | R3 F-20261121-030138-8d3ca16, my own integration: 1.61267, -1.84495, 5.6413, a 7.547, e 0.2474, r_p 5.680; 1.31187, -1.62654, 5.7772; 13.256 M; 1.4745-1.8453 and 0.9887-1.7227; all to the printed digits; curves overlay the track's N1 curves (`figures/fig_ledger_passages.png` read) |
| K11 | HRNA outcome of the same states relative to M: q = 10 m1 crosses r = 2.5 M at t = 97 M, m2 ejected with +1.16 units; q = 4 m2 ejected +0.9703, m1 bound (-0.5), first pericentre 7.262 M (SCOPING 6; note IV D; ledger 2) | CONFIRMED, with two precision remarks | R3: q = 10 crossing of 2.5 M at t = 96.90 (the ledger's 97.1 is the first sample inside, N1 `first_pericentre_1` = 97.118 at r = 2.472), m2 +1.1588. q = 4: m2 +0.9777 at t = 600 and +0.9650 at t = 1500 (it keeps drifting under the pair force of the bound member, so the ledger's fourth digit of 0.9703 is not meaningful), m1 -0.5017, first pericentre 7.259 at t = 122.0 |
| K12 | Reading of the start states in GR: r_p is the pericentre of the Newtonian CM conic, "reported together with the Schwarzschild pericentre of the same E and L"; the first q = 10 passage is at r_p = 8 M, D = 1.24 (SCOPING 3 definition, 6; note II, IV) | WRONG in effect | R1: SCOPING 6 and the parameter table give only the Newtonian r_p. In the reading natural for puncture data (isotropic coordinates, u_i = P/m, the heavy hole's static frame) the q = 10 CM has E = 0.99925 (bound to M) and L = 4.194 and turns at areal radius 5.77 M; read as Schwarzschild coordinates with dx/dt it turns at 7.00 M; a GR parabola with pericentre 8 M needs L = 4.618, 10 percent more. The q = 10 encounter is therefore deeper than "8 M" (D_GR = 5.77/6.46 = 0.89 against D = 1.24) and its CM is bound; the q = 4 state turns at 9.25 M (D_GR 1.17 against 1.24). (Table 3 of the note, added for G1, now reports 5.77 and 9.25 from run F-20261119-145449-245e984; my values agree; SCOPING was not updated.) `figures/fig_scales.png` (right) read |
| K13 | Pericentre scan (V7): q = 10 r_p = 8: Newton separated 0.88, a member inside 4 M 0.056; HRNA separated 1.0, plunge 0.94; r_p = 12: HRNA plunge 0.69; r_p = 13: Newton 0.22, HRNA 0.98 and plunge 0.30; q = 4 r_p = 9.82: 0.84, 0.30; 0.99, 0.94; r_p = 16: 0.54, 0.011; 0.94, 0.67. "The two references disagree in kind" (SCOPING 4; note IV C, abstract; ledger 2) | PARTLY: "disagree in kind" CONFIRMED at r_p = 7-8 M (q = 10) and 9.82 M (q = 4); the V7 numbers NOT REPRODUCED at r_p = 12-13 M and in the Newton "inside 4 M" diagnostic | My scans R4, R4b, R4c, R4d (180 phases each; columns: Newton separated, Newton member inside 4 M; HRNA separated, plunge; in brackets V7): q = 10 r_p = 7: 0.878, 0.494 (0.90, 0.62); 1.000, 0.978 (0.99, 0.96). r_p = 8: 0.850, 0.011 (0.88, 0.056); 1.000, 0.944 (1.0, 0.94). r_p = 12: 0.572, 0.000 (0.59, 0.0); 0.944, 0.222 (0.98, 0.69). r_p = 13: 0.422, 0.000 (0.22, 0.0); 0.939, 0.017 (0.98, 0.30). q = 4 r_p = 9.82: 0.800, 0.189 (0.84, 0.30); 0.961, 0.850 (0.99, 0.94). q = 4 r_p = 16: pending (R4e). With the CM on the Schwarzschild parabola of pericentre r_p (2404's construction) the HRNA plunge fraction is 0.944, 0.911, 0.650, 0.161 (q = 10, r_p = 7, 8, 12, 13) and 0.894 (q = 4, 9.82): so at r_p = 12-13 M the plunge fraction of the geodesic reference changes by a factor 3-10 with the translation of the Newtonian start into the Schwarzschild model, and V7's 0.69 and 0.30 lie nearer my GR-matched than my hand-off construction. The Newton "inside 4 M" fractions are lower in my scan at every r_p where they are not zero (2.6-3.5 sigma); H-mu (test-mass parabola speed) refuted by R8 (0.689, 0.417 at r_p = 7, 8), H-u not tested. At r_p = 13 (D = 2.01, the edge of the restricted problem) my Newton fraction is 0.42 against 0.22. `figures/fig_scan.png` read |
| K14 | Mesh and cost: MeshBlocks start/max/mean and card-hours: q = 10 m/8 1800/2332/2006, 38.9 (37.0-42.3) for 240 M; m/16 2654-4544, 99-156; q = 4 m/8 1716/2080/1744, 15.2; m/16 2514/2864/2568, 44.8; rate 2022-2310 MeshBlock-cycles/s; dt = 0.25 h_min; "about 3000 slots per card"; "2864 is above the 2700 slots of one card" (SCOPING 9; note IV E; ledger 2) | Numbers CONFIRMED; the card-capacity statement WRONG as worded | R9: n(t) recounted from the 25 and 28 `athena -m` outputs of the mesh runs (equal to their JSON at every sample, `figures/fig_ledger_mesh.png` read); card-hours from my own sum within 0.4 percent (plain mean against the trapezoid); dt = cfl x min cell (z4c_newdt.cpp:45-58, mesh.cpp:610ff) with cfl_number = 0.25 in both inputs; rates = median, min, max of the five vacuum logs of F-hills-20261115-045438-f62d553. But 2700 is the slot limit `max_nmb_per_rank` of the smoke input, not the card: the smoke F-20261115-174602-c6879fe peaked at 70847 MiB with 2700 slots (26.2 MiB per slot all-in) on an 81920 MiB card, i.e. about 3100 slots if memory is linear in slots, and the interface says "about 3000" (multi_puncture.md:229-230). SCOPING 9 uses both 3000 and 2700. The q = 4 m/16 tree (largest 2864) probably fits one card with a limit near 2950 [JUDGEMENT; TO VERIFY by a card run] |
| K15 | Programme compute: G1 36-40 card-hours (fits the 40 of decision 0006); G2 about 120 (q = 4 triple 15 + 28 + 41, two large-r_p passages 30, 3BH1 rerun 12, clump relaxation 5, contingency); G3 about 500 (SCOPING 9) | WRONG (arithmetic and stale basis) | R1: the listed G2 items sum to 131 before any contingency (135 with the corrected q = 4 m/16 cost of 44.8), against "about 120" and against the 120 card-hours of decision 0016 item 7. The G1 line is for the q = 10 passage and the allotment of decision 0006; decision 0013 moved the first passage to q = 4 (15.2-16.9 card-hours, ledger 2 and 3) and 0014 set 50. G3 "about 500" is an estimate I cannot check [NOT CHECKABLE] |
| K16 | Parameter ranges and first values follow decision 0013 (q = 4 for the convergence study and the first scan line; q = 10 when the mesh fits) (SCOPING 3: "10 for the first passage"; 6: q = 10 passage "named for G1"; note II, V) | WRONG in SCOPING (stale), CONFIRMED in the note | Decision 0013 (ACCEPTED 2026-11-19); the note's plan and the P1 input are at q = 4 (`nr_first/inputs/p1_q4.athinput`), SCOPING 3, 6 and the G1 line of 9 still say q = 10. CHECKLIST C9 marks the ruling NA "followed already", which holds for the note, not for SCOPING |
| K17 | Exit-criteria numbers and statements: 3BH1 of 0710.0879 E_rad = (6.06 +- 0.02)e-3 M, 11 levels, h = M/80, boundary 640 M; 1004.1353 (approximate data do not converge; can change "dramatically"; junk differences ten times larger); 2402.02178 "intractable" (SCOPING 5, 8) | CONFIRMED | first.tex:141-146, 291 (column 3BH1 by the header 288-289); Punc_N.tex:185-194, 1252-1258 ("one order of magnitude bigger"); main.tex:225 |
| K18 | A start at 10 r_t keeps 95-97 percent of the outcomes of a 40 r_t start, 5 r_t only 90 percent; SKR's 10 r_t "sufficient for convergency" (SCOPING 3; newton3 P4) | CONFIRMED (5 r_t: 0.92 and 0.90) | R9 from `p4.npz` of F-hills-20261115-131801-907e5fe: same outcome as 40 r_t in 0.95 (M/m = 1e6) and 0.97 (10) of 200 phases at 10 r_t, 0.92 and 0.90 at 5 r_t, 0.98 and 0.97 at 20 r_t; prp.tex:597-599 read |
| K19 | 2406.11985: q = 4.0, 9.0, a_b = 9.9 r_gb, D/r_t = 4.1, 5.8, below the plunge bound (10.1, 17.3); "could be continued ... until 128:1:1" (SCOPING 8; NOVELTY) | CONFIRMED | R1 from massratio_table.tex: q 3.999, 9.005; a_b 9.899, 9.901 r_gb; D/r_t 4.116, 5.810; bounds 10.08, 17.31; TBH3.tex:710 |
| K20 | Every number of the note's ledger comes from the named run (CHECKLIST C18) | CONFIRMED for tables 1-2 (57 of 57 rows); table 3 not checked (G1) | Section 2 |

Further statements of the note checked on the way (not on the planner's list):

- N1. note main.tex:140, "The binary stays small against the curvature radius of the black hole
  throughout, as the model requires": WRONG. In the track's own S1 scan (s1.npz of
  F-hills-20261115-130405-ce17dcf) alpha = a/R_curv reaches 0.199 at beta = 10 and 0.148 at
  beta = 8.5 at pericentre (`alpha_all`); the ledger's 0.0056 is the largest value while the
  instantaneous pair energy is negative (`alpha_max`, hrna.py:270-271, 399-400). The paper itself
  reports alpha ~ 0.1-0.2 near pericentre (article.tex:279; appendix.tex:8-12). [VERIFIED, R9]
- N2. note main.tex:129, at the two inner retrograde points "a small difference remains, and
  the wide bound binaries there are still to be followed": closed at D = 0.1 by R5 (wide pairs
  followed: P = 0.5923, identical to the scan); D = 0.2 not run here.
- N3. errata row 1.5 says "a member is captured in most phases" where the measured quantity is a
  member crossing r = 2.5 M in the geodesic model (a plunge, not a capture).

## 2. Ledger recomputed (C18)

Run F-20261121-035817-0aca1c5 (R9) (`ledger_check.py`; `results/ledger_check.{md,json}`). Ledger file
`note/tables/ledger.tex` at 70257ac0 (sha256 in the JSON). "Raw" = recomputed by my code from
the arrays or logs of the named run (sha256 checked where the run recorded them; wave-1 runs
without a record read as they are); "own" = my independent integration or closed form; "src" =
read at the paper source; "transcr." = only the summary file's number re-read. Agreement means
equal to the printed digits, except where a tolerance is given.

Columns as written by R9: row number in tables 1-2, ledger table, quantity, ledger value, source the ledger names, my value(s) (the first numbers repeat labels such as q or beta where the ledger string carries them), agreement, route.

| # | table | quantity | ledger value | source | my value | agree | route |
|---|---|---|---|---|---|---|---|
| 1 | 1 | plunge bound $4q^{2/3}$ on $a_b/r_{gb}$, $q=10,100,1000$ | 18.57, 86.18, 400 | F-hills-20261115-045435-f62d553 | 10, 100, 1000, 18.5664, 86.1774, 400 | yes | closed form 4 q^(2/3) (R1) |
| 2 | 1 | marginally bound radius and angular momentum (parabolic) | 4 $M$, 4 $M$ | F-hills-20261115-045435-f62d553 | 4.00003, 4 | yes | max of V^2 = 1 numerically (R1) |
| 3 | 1 | Peters time at $a_b=30\,r_{gb}$, $q=10$ | 6328 $M$ | F-hills-20261115-045435-f62d553 | 30, 10, 6328.12 | yes | closed form (5/256) a^4/(m1 m2 m_b) (R1) |
| 4 | 1 | last disrupting $D$, prograde | 2.085 | F-hills-20261115-133222-9cb10db | 2.085 | yes | largest D with P > 0 in coplanar.npz (main + deep) |
| 5 | 1 | deep-limit disruption probability, prograde | 0.807 | F-hills-20261115-133222-9cb10db | 0.807474 | yes | P at D = 1e-05 (deep supplement npz) |
| 6 | 1 | largest ejection energy, prograde | 27.15 at $D=0.1$ | F-hills-20261115-133222-9cb10db | 27.1457, 0.1 | yes | max |E2| of disrupted samples over D (npz) |
| 7 | 1 | failed integrations, prograde | 127 of 477000 | F-hills-20261115-133222-9cb10db | 127, 477000 | yes | count of ok == False in the combined arrays (deep supplement below D = 1e-3, main run above) NOTE: main run alone: 122 |
| 8 | 1 | last disrupting $D$, retrograde | 0.405 | F-hills-20261115-133222-9cb10db | 0.405 | yes | largest D with P > 0 in coplanar.npz (main + deep) |
| 9 | 1 | deep-limit disruption probability, retrograde | 0.801 | F-hills-20261115-133222-9cb10db | 0.801402 | yes | P at D = 1e-05 (deep supplement npz) |
| 10 | 1 | largest ejection energy, retrograde | 1.838 at $D=10^{-5}$ | F-hills-20261115-133222-9cb10db | 1.83781, 1e-05 | yes | max |E2| of disrupted samples over D (npz) |
| 11 | 1 | failed integrations, retrograde | 92 of 477000 | F-hills-20261115-133222-9cb10db | 92, 477000 | yes | count of ok == False in the combined arrays (deep supplement below D = 1e-3, main run above) NOTE: main run alone: 82 |
| 12 | 1 | largest disruption probability (prograde) | 0.988 at $D=0.16$ | F-hills-20261115-133222-9cb10db | 0.988, 0.16 | yes | max of P(D) (npz) |
| 13 | 1 | printed: last disrupting $D$; largest energy; deep limit; best $D$ | 2.1/0.44; 27.3/1.8; about 0.8; 0.15 | arXiv:0911.1136 prp.tex:735-738, 846-849 | 1, 1, 1, 1, 1, 1 | yes | strings found in prp.tex 735-738, 846-849, 854 NOTE: For $D < 10^{-1}$, the fraction of disrupted cases saturates at a level of $\sim 80\%$. The best chance of disruption is for a binary in prograde orbit, with $D = 0.15$.  | \item The largest $D$ for which there is disruption is  $D=2.1$ for prograde orbits and $D=0.44$ for retrograde orbits. \item T |
| 14 | 1 | against the digitised curve: median, largest $|\Delta P|$, prograde | 0.0014, 0.037 at $D=2.07$ | F-hills-20261115-132703-0bfc352 | 0.00141457, 0.0373454, 2.07447 | yes | my interpolation of P(D) (npz) at the digitised SKR fig. 4 points (track's digitisation, scratch) |
| 15 | 1 | retrograde, bound binaries wider than $3.5\,a_b$ counted as disrupted: largest $|\Delta P| | 0.0088, 0.445 | F-hills-20261115-132942-2f7ad7f | 0.00876888, 0.445 | yes | coplanar.npz with af > 3.5 counted as disrupted, against the digitised SKR retrograde curve |
| 16 | 1 | against the digitised curve: largest $|\Delta P|$, retrograde | 0.21 at $D=0.418$ | F-hills-20261115-132703-0bfc352 | 0.210112, 0.418012 | yes | as the prograde row |
| 17 | 1 | isotropic orientations, $D\le1$: largest fractional deviation from the published fit, prob | 0.015, 0.017 (512 orientations $\times$ 64 phases) | F-hills-20261115-133200-05ee76a | 1, 0.0151896, 0.0172813, 512, 64 | yes | general.npz set A against my evaluation of the BKRS polynomials (mnras.tex:372-377, 433-437) |
| 18 | 1 | printed: plateau of the isotropic probability; accuracy of the fits for $D\lesssim1$ | about 0.88; one percent | arXiv:1804.02911 mnras.tex:368, 377, 440 | 1, 1 | yes | strings at mnras.tex 368, 377, 440 NOTE: disruption rate plateaus with $\sim  88\%$ (the black solid line). Interestingly  The fractional error $\Delta P_{dis}/P_{dis}$ is less than $1\%$ for $D \la 1$.  The fractional error is less than $1\%$ for $D \la 1$, and it is about  |
| 19 | 1 | independent code, nine points: largest $|\Delta P|$, $|\Delta E|/E$ | 0.021, 0.079 (retrograde $D=0.38$) | F-hills-20261115-145246-090f5dc | 0.0210642, 0.0792265, 0.38 | yes | v4_samples.npz (600 phases per point) against coplanar.npz at the same D NOTE: per point dP ['0.0003', '0.0003', '0.0000', '0.0017', '0.0003', '0.0023', '0.0063', '0.0088', '0.0211'], dE/E ['0.0010', '0.0004', '0.0003', '0.0019', '0.0007', '0.0038', '0.0116', '0.0205', '0.0792'] |
| 20 | 1 | the same at retrograde $D=0.3, 0.38$, wide binaries followed on | 0.0013, 0.0035 | F-hills-20261115-145544-a314517 | 0.00133333, 0.00352884 | yes | v4b_summary rows (no sample arrays in that run); my R5 at ret D = 0.3 with wide binaries followed gives P = 0.3720 against the npz 0.3720 NOTE: transcription only for D = 0.38; D = 0.3 also by my own integration |
| 21 | 1 | encounters of the scan | 160000 | F-hills-20261115-142554-c10b371 | 160000 | yes | size of the outcome arrays of s1.npz (F-hills-20261115-130405-ce17dcf) |
| 22 | 1 | retrograde onset of separation in $\beta$ (geodesic, Newton) | 1.9, 2.5 | F-hills-20261115-142554-c10b371 | 1.9, 2.5 | yes | first beta with retro separated fraction > 0.01 (s1.npz) |
| 23 | 1 | separated fraction at $\beta=3$ (N pro, N retro, G pro, G retro) | 0.98, 0.295, 0.985, 0.51 | F-hills-20261115-142554-c10b371 | 3, 0.98, 0.295, 0.985, 0.51 | yes | count fraction of 400 phases (s1.npz) |
| 24 | 1 | separated fraction at $\beta=10$ (N pro, N retro, G pro, G retro) | 0.985, 0.58, 0.993, 0.91 | F-hills-20261115-142554-c10b371 | 10, 0.985, 0.58, 0.9925, 0.91 | yes | count fraction of 400 phases (s1.npz) |
| 25 | 1 | against the figure of arXiv:2404.16270: largest $|\Delta|$ of the fraction | 0.0225 | F-hills-20261115-142554-c10b371 | 0.0225 | yes | my interpolation of the digitised 2404 curves (track's digitisation in scratch; calibration constants of the track, x ticks checked) against s1.npz NOTE: {"dev": {"retro_newton": 0.005, "retro_hrna": 0.0225, "pro_newton": 0.016132804232804165, "pro_hrna": 0.022226554232804285}, "curve_values_at_beta_9_95": {"retro_newton": 0.5784650735294117, "retro_1pn": 0.8254036485890652, "retro_hrna": 0.9072656264172336, "pro_newton": 0.9850911463844796, "pro_1pn |
| 26 | 1 | the same, mean $v_\infty$ (relative) | 0.0073 | F-hills-20261115-142554-c10b371 | 0.00725514 | yes | transcription of s1_summary.json checks only (speed curves not recomputed) NOTE: transcription only |
| 27 | 1 | largest $a_b/R_{\rm curv}$ of a bound binary at $\beta=10$ | 0.0056 | F-hills-20261115-142554-c10b371 | 10, 0.0056358 | yes | max of alpha_max (a/R while the Newtonian pair energy < 0) at beta = 10, HRNA, s1.npz NOTE: the same parameter at any time (alpha_all) reaches 0.199 at beta = 10 (pericentre) |
| 28 | 2 | $q=10$, $r_p=7$: Newton sep., inside $4M$; geodesic sep., plunge | 0.9, 0.62; 0.99, 0.96 | F-hills-20261115-145915-71abf93 | 0.9, 0.622222, 0.988889, 0.955556 | yes | transcription of v7_summary; independent: my scan R4 (180 phases) NOTE: R4: 0.878, 0.494, 1.000, 0.978; within 3 binomial sigma of v7: False |
| 29 | 2 | $q=10$, $r_p=8$: the same | 0.88, 0.056; 1, 0.94 | F-hills-20261115-145915-71abf93 | 0.877778, 0.0555556, 1, 0.944444 | yes | transcription of v7_summary; independent: my scan R4 (180 phases) NOTE: R4: 0.850, 0.011, 1.000, 0.944; within 3 binomial sigma of v7: True |
| 30 | 2 | $q=10$, $r_p=13$: the same | 0.22, 0; 0.98, 0.3 | F-hills-20261115-145915-71abf93 | 0.222222, 0, 0.977778, 0.3 | yes | transcription of v7_summary; independent: my scan R4 (180 phases) NOTE: R4: 0.422, 0.000, 0.939, 0.017; within 3 binomial sigma of v7: False |
| 31 | 2 | $q=4$, $r_p=9.82$: Newton sep., inside $4M$; geodesic sep., plunge | 0.84, 0.3; 0.99, 0.94 | F-hills-20261115-145915-71abf93 | 0.844444, 0.3, 0.988889, 0.944444 | yes | transcription of v7_summary; independent: my scan R4 (180 phases) NOTE: R4: 0.800, 0.189, 0.961, 0.850; within 3 binomial sigma of v7: False |
| 32 | 2 | $q=4$, $r_p=16$: the same | 0.54, 0.011; 0.94, 0.67 | F-hills-20261115-145915-71abf93 | 0.544444, 0.0111111, 0.944444, 0.666667 | yes | transcription of v7_summary; independent: my scan R4 (180 phases) NOTE: no R4 case |
| 33 | 2 | $q=4$: energy unit $(m_1m_2/a_b)q^{1/3}$ | 0.004961 $M$ | F-20261115-174648-25514db | 0.00496063 | yes | closed form (m1 m2/a_b) q^(1/3) at a_b = nominal (R1) |
| 34 | 2 | $q=4$, Newton: ejected member, energy (barycentric), its spread after $t=300M$ | $m_1$, 1.3119, 0.00015 | F-20261115-174648-25514db | 1, 1.31187, 0.000154272 | yes | N1 curves (passage_curves.npz, last sample, ptp after t = 300) ; R3: m1, 1.31187, 0.00015 |
| 35 | 2 | $q=4$, Newton: two-body energy of the same member with $M$, range | 0.9887 to 1.723 | F-20261115-174648-25514db | 0.988721, 1.72273 | yes | N1 curves (t >= 300); R3: 0.9887 to 1.7227 |
| 36 | 2 | $q=4$, Newton: captured member, energy, closest approach | $m_2$, -1.627, 5.777 $M$ | F-20261115-174648-25514db | 2, -1.62654, 5.77715 | yes | R3 (own integration); N1 curve min r of the captured member 5.7771 |
| 37 | 2 | $q=4$, geodesic: ejected member and energy; other member | $m_2$, 0.9703; bound, -0.5, first pericentre 7.262 $M$ | F-20261115-174648-25514db | 2, 0.977673, -0.501661, 7.25919 | yes | R3 (own HRNA) NOTE: ejected energy drifts with time: 0.9777 at t = 600, 0.9650 at t = 1500 (pair force of the bound member) |
| 38 | 2 | $q=4$, Newton with $M$ fixed: ejected energy, closest approach of the other | 1.835, 6.107 $M$ | F-20261115-174648-25514db | 1.8435, 6.10631 | yes | R3 (own integration, energy at t = 600) NOTE: N1 evaluates at t_end = 1309 |
| 39 | 2 | $q=10$: energy unit $(m_1m_2/a_b)q^{1/3}$ | 0.001795 $M$ | F-20261115-174648-25514db | 0.00179536 | yes | closed form (m1 m2/a_b) q^(1/3) at a_b = nominal (R1) |
| 40 | 2 | $q=10$, Newton: ejected member, energy (barycentric), its spread after $t=300M$ | $m_1$, 1.6127, 3.2e-05 | F-20261115-174648-25514db | 1, 1.61267, 3.22758e-05 | yes | N1 curves (passage_curves.npz, last sample, ptp after t = 300) ; R3: m1, 1.61267, 3.2e-05 |
| 41 | 2 | $q=10$, Newton: two-body energy of the same member with $M$, range | 1.474 to 1.845 | F-20261115-174648-25514db | 1.4745, 1.84534 | yes | N1 curves (t >= 300); R3: 1.4745 to 1.8453 |
| 42 | 2 | $q=10$, Newton: captured member, energy, closest approach | $m_2$, -1.845, 5.641 $M$ | F-20261115-174648-25514db | 2, -1.84495, 5.64129 | yes | R3 (own integration); N1 curve min r of the captured member 5.6412 |
| 43 | 2 | $q=10$, geodesic: ejected member and energy; other member | $m_2$, 1.159; plunges at $t=97.1M$ | F-20261115-174648-25514db | 2, 1.1588, 96.8997 | yes | R3 (own HRNA; plunge time = crossing of r = 2.5 M, interpolated) NOTE: ledger 97.1 is the first sample inside 2.5 M (N1 first_pericentre_1 = [97.11800191179567, 2.4719236660023887]) |
| 44 | 2 | $q=10$, Newton with $M$ fixed: ejected energy, closest approach of the other | 1.887, 5.862 $M$ | F-20261115-174648-25514db | 1.89047, 5.86755 | yes | R3 (own integration, energy at t = 600) NOTE: N1 evaluates at t_end = 1078 |
| 45 | 2 | $q=4$: reproduces the earlier run in every printed digit (ejected energy) | 1.31187 | F-20261115-174102-ffa764f | 1.31187 | yes | R3; E6 file 1.311866 |
| 46 | 2 | $q=4$, Newton: displacement of the heavy black hole by the end of the run | 13.3 $M$ at $t=280M$ | F-20261115-174102-ffa764f | 13.2559, 280 | yes | R3 at t = 280; E6 file 13.2559 |
| 47 | 2 | readers on a synthetic three-body run: checks passed | 10 of 10 | F-20261115-173821-b2c969a | 10, 10 | yes | count of ok in test_nrread_synthetic.json (the test itself not rerun) |
| 48 | 2 | $q=10$: captured orbit of Newton ($a$, $e$, pericentre) | 7.55, 0.247, 5.68 $M$ | F-hills-20261115-145251-090f5dc | 10, 7.54749, 0.247422, 5.68007 | yes | R3 osculating orbit at t = 1500 |
| 49 | 2 | $q=10$, $m/8$: MeshBlocks start, largest, mean; card-hours (240 $M$) | 1800, 2332, 2006; 38.9 (37-42.3) | F-hills-20261115-131348-634fb86 | 1800, 2332, 2006.08, 38.8822, 37.0579, 42.329 | yes | n(t) recounted from 25 athena -m stdout files; dt = cfl h_min, cfl 0.25 (input), h_min 0.00625; rates of the novelty run; card-hours plain mean (trapezoid 38.86 |
| 50 | 2 | $q=10$, $m/16$: MeshBlocks start, largest, mean; card-hours (240 $M$) | 3690, 4544, 4019; 156 (149-170) | F-hills-20261115-131348-634fb86 | 3690, 4544, 4018.72, 155.783, 148.474, 169.593 | yes | n(t) recounted from 25 athena -m stdout files; dt = cfl h_min, cfl 0.25 (input), h_min 0.003125; rates of the novelty run; card-hours plain mean (trapezoid 156) |
| 51 | 2 | $q=10$, $m/16$, small radius: MeshBlocks start, largest, mean; card-hours (240 $M$) | 2654, 2934, 2574; 99.4 (94.7-108) | F-hills-20261115-131348-634fb86 | 2654, 2934, 2573.92, 99.7762, 95.095, 108.621 | yes | n(t) recounted from 25 athena -m stdout files; dt = cfl h_min, cfl 0.25 (input), h_min 0.003125; rates of the novelty run; card-hours plain mean (trapezoid 99.4 |
| 52 | 2 | $q=4$, $m/8$: MeshBlocks start, largest, mean; card-hours (270 $M$) | 1716, 2080, 1744; 15.2 (14.5-16.5) | F-hills-20261115-131933-907e5fe | 1716, 2080, 1744, 15.2111, 14.4974, 16.5595 | yes | n(t) recounted from 28 athena -m stdout files; dt = cfl h_min, cfl 0.25 (input), h_min 0.015625; rates of the novelty run; card-hours plain mean (trapezoid 15.1 |
| 53 | 2 | $q=4$, $m/16$: MeshBlocks start, largest, mean; card-hours (270 $M$) | 2514, 2864, 2568; 44.8 (42.7-48.7) | F-hills-20261115-131933-907e5fe | 2514, 2864, 2568.5, 44.8048, 42.7026, 48.7766 | yes | n(t) recounted from 28 athena -m stdout files; dt = cfl h_min, cfl 0.25 (input), h_min 0.0078125; rates of the novelty run; card-hours plain mean (trapezoid 44. |
| 54 | 2 | $q=4$, $m/16$, small radius: MeshBlocks start, largest, mean; card-hours (270 $M$) | 2416, 2654, 2348; 40.9 (39-44.6) | F-hills-20261115-131933-907e5fe | 2416, 2654, 2347.5, 40.9496, 39.0284, 44.5797 | yes | n(t) recounted from 28 athena -m stdout files; dt = cfl h_min, cfl 0.25 (input), h_min 0.0078125; rates of the novelty run; card-hours plain mean (trapezoid 40. |
| 55 | 2 | rate, MeshBlock-cycles per second (median, slow, fast) | 2201, 2022, 2310 | F-hills-20261115-131348-634fb86 | 2201.34, 2022.08, 2309.7 | yes | median, min, max of R_mbcyc_per_s over the novelty run's vacuum logs NOTE: [2022.0842014416185, 2139.7967267979966, 2201.3376739271903, 2233.542131715295, 2309.703355868048] |
| 56 | 2 | $q=4$ input at the start, release executable: $m/4$, $m/8$, $m/16$ | 1128, 1716, 2514 | F-20261115-173543-29e87e8 | 4, 1128, 1716, 2514 | yes | recounted from q4_L9..L11/athena_m.log NOTE: counts.txt {9: 1128, 10: 1716, 11: 2514} |
| 57 | 2 | card memory, MeshBlock slots | about 3000 | multi\_puncture.md lines 229--230 of coo | 3000 | yes | coord/INTERFACES/multi_puncture.md lines 229-230 read NOTE:   three (about 22 MB per block slot plus 2 MB per finder). A card holds a limit of   about 3000. |

Summary: 57 of 57 rows agree with what the named run or source holds. Routes: 31 rows recomputed from raw arrays or logs of the named run (coplanar.npz with the deep supplement, general.npz, v4_samples.npz, s1.npz, passage_curves.npz, the 159 `athena -m` stdout files of the mesh runs, athena_m.log); 14 by my own integrations or closed forms (R1, R3); 3 at the source (prp.tex, mnras.tex, multi_puncture.md:229-230); 5 pericentre rows by transcription of v7_summary.json, with my independent scan alongside, which does NOT reproduce several of their numbers (K13, D2); 4 by transcription only: the v4b row (no sample arrays; its D = 0.3 point confirmed by my R5), the mean-v_inf deviation from the digitised 2404 curves, the count of the readers' self-test (the test not rerun), and the rate row (per-log rates of the novelty run re-read, median, min and max taken by me). The digitised third-party curves (SKR fig. 4, the 2404 separation fraction) are the track's digitisation in scratch; I redid the comparisons with my own interpolation, not the digitisation. Two rows agree only within a tolerance stated in their route: the fixed-hole Newton energies (0.5 percent; evaluation time) and the q = 4 HRNA ejected energy (2 percent; it drifts, D9).

Table 3 (G1, 37 rows): not recomputed, except four rows my G0 runs give: q = 4 start conic
9.809, 1.00023 (R1: 9.8087, 1.000235); heavy-hole-frame reading E 1.0042, L 4.952, turning
9.25 (R1: 1.0042, 4.9522, 9.2507); q = 10 Newtonian r_p 7.997 and turning point 5.77 (R1:
7.9965, 5.775); Newton captured orbit at q = 4 a 7.75, e 0.25, r_p 5.81, first pericentre
122.1 (R3: 7.746, 0.2503, 5.807, 122.0 at 0.25 M sampling). All agree.

## 3. Defects and what each changes in the plan

Ordered by what they change. "Owner" is who can fix it; I changed nothing outside my package.

**D1 (K12) The depth of the first passages is stated in Newtonian terms only.** SCOPING 3
promises the Schwarzschild pericentre next to every r_p; SCOPING 6 and the parameter table give
only the Newtonian conic (7.9965, 9.8087). In the puncture reading the q = 10 CM is bound
(E = 0.99925) and turns at 5.77 M (D_GR = 0.89, not 1.24); the q = 4 state turns at 9.25 M.
What it changes: every "r_p" of the scan lines and of the predictions for the first passages
must carry the GR turning point, and a scan line meant to be equally spaced in depth should be
built from a GR parabola (L = (2 r_p^2/(r_p - 2))^(1/2)) in the reading the code uses for its
data. The prediction "Hills ejection and capture at r_p = 8 M" for the q = 10 passage is a
prediction for a deeper, bound encounter. Owner: lead (SCOPING 3, 6; note Sec. II; the
G1-revision table 3 already has the numbers).

**D2 (K13, D8 of the list in README) The geodesic reference's plunge fraction depends on the
construction of the start state at larger r_p, and the V7 numbers are not reproduced there.**
My independent scans reproduce the HRNA plunge fractions of V7 at r_p = 7 and 8 M (q = 10: 0.978 and 0.944 against 0.96 and 0.94) but not at 12 and 13 M (0.222 and 0.017 against 0.69 and 0.30 with the hand-off of SCOPING 6; 0.650 and 0.161 with the CM on the Schwarzschild parabola of pericentre r_p), nor at q = 4, r_p = 9.82 M (0.850 against 0.94). The Newtonian "member inside 4 M" fractions come out lower than V7's at every r_p where they are not zero, and at r_p = 13 M my Newtonian separated fraction is 0.42 against 0.22 (the encounter sits on the edge D = 2.0 of the restricted problem, where P falls from 0.31 to 0 within 0.09 in D). I did not find the cause before reading the lead's script (H-mu refuted, H-u not finished). [VERIFIED as my runs; the cause TO VERIFY]
What it changes: the statement "the two references disagree in kind" holds at r_p = 7-8 M
(q = 10) and 9.82 M (q = 4) in every construction I tried; the numbers "69 percent at 12 M"
(SCOPING 4, errata row 1.5) and "plunge 0.30 at 13 M" (ledger 2) should not be quoted until
the construction of the V7 hand-off is written down next to them and reproduced. For the scan
lines of G3 the HRNA reference must be started the same way as the NR data (D1).

**D3 (K15) The G2 compute is under-summed.** The items listed add to 131 card-hours (135 with
the corrected q = 4 m/16 cost of 44.8) before any contingency, against "about 120" and against
the 120 card-hours of decision 0016. The G1 line (36-40, q = 10, allotment of 0006) is stale
after decisions 0013 and 0014. What it changes: G2 as planned does not fit the allotment; one
of the large-r_p passages or the 3BH1 rerun must move to G3, or more must be asked for. Owner:
lead (SCOPING 9).

**D4 (K16) SCOPING still names q = 10 as the first passage** (sections 3, 6, 9) against
decision 0013 (accepted 2026-11-19); the note and the P1 input follow 0013. What it changes:
nothing in the work done, but the G0 package contradicts the ruling it claims to follow
(CHECKLIST C9). Owner: lead.

**D5 (K14) "2864 is above the 2700 slots of one card" confuses the input's slot limit with the
card's capacity.** The smoke's measured 70847 MiB at 2700 slots on an 81920 MiB card allows about
3100 slots if memory is linear in slots (the interface says about 3000). What it changes: the
q = 4 m/16 member of the convergence triple (largest tree 2864) may run on one card with
`max_nmb_per_rank` near 2950, without MPI; a short card test at that limit decides it
[TO VERIFY]. Owner: lead (SCOPING 9), with nr_first.

**D6 (K6) The correction of brief l. 275 states a condition for deep encounters, not for
separation.** a_b/r_gb > 4 q^(2/3) is r_t > 4 M (D = 1 at the plunge radius). Newtonian
restricted encounters separate binaries out to D = 2.085 (prograde), so with the CM outside 4 M
separation is possible down to about 4 q^(2/3)/2.085 (14.1 r_gb at q = 20, 18.5 at q = 30):
the whole box q = 10-30, a_b = 20-60 r_gb of l. 275 is above that weaker bound, its corner
(q = 30, a_b = 20) at the edge. What it changes: errata row 1.5 should say "deep (D <= 1)
encounters outside the plunge radius need a_b >= 29.5 r_gb at q = 20 and 38.6 at q = 30"; the
member-plunge argument of the same row (geodesic reference) is the stronger reason why the
shallow part of the box gives few clean separations. Owner: lead (outbox to orch for the
errata row).

**D7 (N1) The note misstates the consistency of the geodesic model.** main.tex:140 says the
binary stays small against the curvature radius "throughout"; in the track's own S1 scan alpha
reaches 0.20 at beta = 10 at pericentre, and the ledger row (0.0056) is the maximum only while
the pair energy is negative. What it changes: the sentence and the ledger label; together with
SCOPING's alpha = 0.13 at 8 M for q = 10 it says that the geodesic reference is at the edge of
its own validity in exactly the regime of the first passages, which belongs in the risk list.
Owner: note.

**D8 (K4) 1201.4794 (KHSR) is not reproduced**, although the track sheet (F-pre-1) and brief
l. 476 name it; only its energy combination is used. What it changes: either one KHSR result
(e.g. the dependence on the CM eccentricity) is reproduced at G1, or the plan says that this
item is dropped and why. Owner: lead / newton3.

**D9 (K11) Two precision remarks on the ledger.** The q = 4 HRNA ejected energy (0.9703) drifts
by 1.3 percent between t = 600 and 1500 M under the pair force of the bound member: three
digits and the evaluation time should be given. The q = 10 "plunges at t = 97.1 M" is the first
sample inside 2.5 M; the crossing is at 96.9 M. Neither changes the plan. Owner: note.

**D10 (N2, N3, K3) Wording.** The note still calls the retrograde difference at D = 0.1 open; R5
closes it (D = 0.2 not run). Errata row 1.5 says "captured" for a plunge. The note's "to about
their stated accuracy" for the BKRS fits hides that the scan deviates 1.5-1.7 times the stated
1 percent. No change to the plan.

Not checked by me: the G3 estimate of about 500 card-hours; the clump-binary cost model (object
b); the junk-energy analysis of core's runs; the 1PN law and the Kerr comparison of
geodesic_binary; table 3 of the ledger beyond four rows; the INSPIRE side of the novelty search.

## 4. Comparison with the earlier checks (read after sections 1-3 were committed, fecdec04)

Read now: `stage/G0/SECOND_CHECK.md` (second agent, wave 2), `stage/G0/REVIEW.md` (an index),
`stage/REVIEW-wave2.md` (lead, wave 2b), and the lead's script `stage/G0/checks/lead_checks.py`
(V7 only, lines 1-20 and 470-530).

**Where we agree.**
- Novelty (K1). SECOND_CHECK repeated the search with 31 INSPIRE queries and the complete
  forward-citation lists of ten papers (2406.11985: 9 citing records, 2505.03934: 8, ...) and
  found 13 papers outside NOVELTY.md, none a full-NR Hills calculation. My kb-corpus search
  (R6b) agrees and is weaker on exactly the point SECOND_CHECK covered (citing lists); together
  the verdict stands with the limits both state (no ADS, no journals outside arXiv, work in
  progress invisible). My request to kb for `refersto` listings is answered by SECOND_CHECK's
  records (`kb-data/meta/inspire/query/`), so I withdraw it.
- GR reading of the q = 10 start state (K12, D1). SECOND_CHECK SC7 (E = 0.99925, L = 4.19 M,
  turning point 5.77 M, CM inside the capture region with the total mass), the lead's V9a
  (5.775 M) and my R1 (5.775 M) agree; the q = 4 reading (9.25 M) agrees with V9b. The track's
  answer (REVIEW-wave2: P1 at q = 4, the q = 10 input rebuilt from a GR parabola before any
  q = 10 passage, RISKS R14) settles the physics; SCOPING 3 and 6 still read as before, which
  is the documentation part of D1.
- The geodesic reference's percentages are not predictions (K13, D2). SECOND_CHECK found the
  HRNA numbers at q = 10 inflated by the 2404 initial-binary convention (a Newtonian-circular
  binary in coordinate time starts too wide under HRNA, SC3) and by a spurious self-acceleration
  of a moving binary (SC0d, SC6); the lead qualified them in G1 and STATUS. My scans reach the
  same conclusion along another axis (the translation of the Newtonian state into the model:
  hand-off against GR-matched CM changes the plunge fraction at r_p = 12-13 M by a factor 3-10).
  Both checks find the qualitative core, a member plunging at r_p = 7-8 M in the geodesic model
  and none in Newton, robust: SECOND_CHECK by the capture plane (SC4), I by four constructions
  that all give 0.91-0.98 at r_p = 7-8 M.
- The wave-2b corrections (REVIEW-wave2 table): the q = 4 m/16 row (2514/2864/2568, 44.8) is the
  one the ledger carries and my recount confirms; V4b's "nine points" was seven. My R5 shows that
  the retrograde D = 0.1 difference of V4 disappears when wide pairs are followed (P identical),
  which closes one of the two points the lead left open.
- P1 cost 16.9-20.1 card-hours (REVIEW-wave2) and the smoke numbers (1716/1744 MeshBlocks,
  2057 MeshBlock-cycles/s, 70847 MiB) are the values I used in K14.

**Where I disagree or add.**
- Construction of the V7 scan. lead_checks.py:486-487 and 520 release a fresh circular binary at
  4 r_t (newton3 `scatter(k0 = 4.0)`; the HRNA with 2404's data released at 4 r_t), while the
  start rule of SCOPING 3 and both passage inputs integrate the Newtonian state from 10 r_t.
  SECOND_CHECK reproduced V7 with V7's own construction ("release at 4 r_t", SC1), so neither
  check tested V7 against the plan's start rule. I tested it after reading the script (journal entries 9-10): my scan with the circular binary released at 4 r_t (runs F-20261121-040103-6b9074c, F-20261121-040112-d429b4c, 180 phases) gives Newton separated / inside 4 M 0.906/0.617, 0.878/0.033, 0.239/0 at r_p = 7, 8, 13 M (V7: 0.90/0.62, 0.88/0.056, 0.22/0) and, with the CM on the Schwarzschild parabola, HRNA plunge 0.928, 0.911, 0.300 (V7: 0.956, 0.944, 0.300), all within 2 sigma (`figures/fig_scan.png` of run F-20261121-040229-dad1b1b, read). So V7 is right for its construction, and the differences of my section 1 (K13, D2) are the start rule: at r_p = 13 M the Newtonian separated fraction is 0.24 (release at 4 r_t) or 0.42 (state integrated from 10 r_t), the HRNA plunge fraction 0.30, 0.16 or 0.02 (release at 4 r_t; from 10 r_t with the CM on the parabola; from 10 r_t with the hand-off). This sharpens D2: the V7 numbers that the plan quotes (and errata row 1.5) do not describe the encounters the NR data set up; near the separation edge they are properties of the construction. A scan line for G3 must use one start rule for NR and both references, and the r_p = 12-13 M numbers should be re-quoted with it. I keep the verdict of K13 (PARTLY) as written; its "not reproduced" now has its cause.
- Errata row 1.5 still quotes "94 percent of phases at r_p = 8 M, 69 percent at 12 M" without
  the qualification the lead applied in G1 and STATUS after SECOND_CHECK R2; and its "needs
  a_b >= 29.5 r_gb at q = 20" is the D <= 1 condition (D6). The lead's table of wrong statements
  (REVIEW-wave2) does not list D3 (G2 sum 131-135 against "about 120"), D4 (SCOPING's q = 10 first
  passage), D5 (2700 slots is the input's limit, not the card's), D7 (the note's "throughout"
  for alpha) or D8 (KHSR not reproduced).
- REVIEW-wave2 says "Not confirmed by me: every number of the ledger" and CHECKLIST C18 is open:
  section 2 closes C18 for ledger tables 1-2 (57 of 57). Table 3, added for G1, remains for the
  G1 verifier.
- SECOND_CHECK's flat-space self-acceleration (1.065e-4 at V = 0.28) is consistent with what my
  self-test shows for a binary at rest (each member's pair force carries its own Gamma^-2, so the
  model is not Newton even in flat space); I did not rerun the moving-binary test.

**What none of us checked.**
- The q = 4 scan at r_p = 16 M with my constructions: run F-20261121-034441-f211f65 found no result in 28 min (a few phases hit the step cap slowly) and was stopped; not done (it does not change the verdicts).
- The HRNA self-force at 2404's own parameters and whether it explains the r0 dependence there
  (SECOND_CHECK R3, still open); a reference that converges in release radius at q = 10 (the
  wave-3a EIH reference exists but none of the G0 checks used it).
- Retrograde and inclined encounters at finite q; the q = 4 scan beyond r_p = 9.82 M with any
  construction other than V7's.
- KHSR (1201.4794): no result of it reproduced by anyone.
- The card capacity near 2950 slots (D5); the G3 estimate of about 500 card-hours; the clump
  binary cost model; the junk-energy analysis of core's runs.
- Whether the q = 10 input rebuilt from a GR parabola (RISKS R14) gives the intended r_p in the
  isotropic reading of the code's data (a statement about future work; nothing to check yet).

Runs added with this section: F-20261121-040103-6b9074c and F-20261121-040112-d429b4c (scan released at 4 r_t, H-k0), F-20261121-040229-dad1b1b (figure). Stopped without result: F-20261121-034441-f211f65 (q = 4, r_p = 16, capped).
