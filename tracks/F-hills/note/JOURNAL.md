# JOURNAL of the package note (F-hills, wave 2): working note v0, schematics, stage report

Helper of owner F-hills. Units G = c = 1, M = 1 (heavy black hole). Labels: [VERIFIED]
measured in a registered run named here or read at a locator; [BACKGROUND]; [JUDGEMENT];
[TO VERIFY]. Run ids as `harness/bin/nrpic-run` writes them; manifests under
`tracks/F-hills/runs/<run_id>/`, outputs under `scratch/F-hills/<run_id>/`. Every entry:
prediction (before the run), then the outcome, also when the prediction failed.

## 2026-11-15 N1. Time series of the two baselines for the first passages (prediction)

What: `scripts/passage_curves.py` as a registered analysis run (processor, one core, python
of `scratch/F-hills/venv-gb` for numba). From the start states of the q = 4 input of wave 2
(`nr_first/inputs/p1_q4.athinput`) and the q = 10 input of wave 1
(`three_punctures/inputs/hills_q10_m8.athinput`): full Newton, Newton with the black hole
fixed, HRNA with the black hole fixed; distances of the members from M against time and the
member energies (two-body with M; against the barycentre of M and the other member). The
figure script `fig_passage.py` reads its output.

Prediction [the functions are the lead's and nr_first's, read only; the numbers they printed
are VERIFIED in their runs]: every number agrees in its fourth significant digit with the
earlier runs.
- q = 4 (E6, run F-20261115-174102-ffa764f; V5b, F-hills-20261115-145559-a314517): full
  Newton ejects m1 with +1.3119 units against the barycentre, the captured m2 has two-body
  energy -1.627 units and closest approach 5.777 M; HRNA ejects m2 with +0.9703 units and
  binds m1 (-0.49995 units, first pericentre 7.262 M); hole-fixed Newton ejects m1 with
  +1.835 units, m2 bound with closest approach 6.107 M.
- q = 10 (V5, V5b, V6, runs F-hills-20261115-145251-090f5dc, -145559-a314517): full Newton
  ejects m1 with +1.6127 units against the barycentre, its two-body energy with M swings
  between 1.474 and 1.845 units after t = 300, m2 bound with closest approach 5.641 M; HRNA
  plunges m1 (r < 2.5 M, closest 2.472 M) and ejects m2 with +1.159 units; hole-fixed Newton
  ejects m1 with +1.887 units, m2 closest 5.862 M.
Refuted if any of these differs in the fourth significant digit (then the functions or the
inputs changed since those runs).

## 2026-11-15 N2. Figures, ledger and claims check (prediction)

What: `scripts/run_all.py` as a registered analysis run: the data figures (restricted
Newtonian scan, geodesic scan of 2404, pericentre scan of the two baselines, passage time
series, MeshBlock counts and cost), the two schematics, the ledger and parameter tables, and
`scripts/ledger.py`'s check of numbers in the lead's documents against the files.

Predictions [JUDGEMENT]:
1. Every input file matches the sha256 its run recorded (sha256sums.txt, or the manifest);
   wave-1 runs without a record are reported as such.
2. The numbers the figure scripts recompute equal those of the analysis runs they come from:
   restricted coplanar scan (runs F-hills-20261115-130237-cbfaf6b with the deep supplement
   -132156-efddfc0; analysis -133222-9cb10db): last disrupting D 2.085 (prograde) and 0.405
   (retrograde), deep-limit P_dis 0.8075 and 0.8014, max |E| 27.15 at D = 0.1; geodesic scan
   (S1 summary of -142554-c10b371): separated fraction at beta = 3 of 0.98, 0.295, 0.985, 0.51
   (prograde Newton, retrograde Newton, prograde HRNA, retrograde HRNA); pericentre scan (V7,
   -145915-71abf93) as tabulated in `JOURNAL.md` of the track.
3. Claims check: the numbers of `STATUS.md`, `stage/G0/SCOPING.md` sections 3, 4, 6, 9 and
   `stage/G1/STATUS.md` agree with the files, except where the record already shows a change:
   the card-hour allotment (40 in the lead's text; 50 since decision 0014), the release state
   of the multi-puncture capability (now in core-v0.3, CLAUDE.md), the "captures" wording of
   the headline for what the files call a plunge (r < 2.5 M), and the m/16 count at q = 4 at
   t = 0 (2416 in SCOPING section 9 with puncture radius 1.2; 2514 in E1 with the input's
   radius). Refuted if a number of the lead's text has no source in the files or differs
   from it beyond rounding.

## 2026-11-15 N1, outcome (run F-20261115-174648-25514db, 66 s on one core)

Prediction met in every number [VERIFIED, `passage_summary.json` of the run]:
- q = 4: full Newton ejects m1 with +1.31187 units against the barycentre (spread 1.54e-4
  after t = 300), m2 captured with two-body energy -1.6265 units and closest approach
  5.7771 M (pericentres at t = 122.1 and 250.9); HRNA ejects m2 with +0.97030 units, m1 bound
  (-0.49995) with first pericentre 7.2616 M at t = 121.0; hole-fixed Newton ejects m1 with
  +1.8348 units, m2 closest 6.1067 M. Same digits as E6.
- q = 10: full Newton ejects m1 with +1.61267 units (spread 3.2e-5 after t = 300), its
  two-body energy with M swings between 1.4745 and 1.8453 units; m2 bound, closest
  5.64124 M (the lead's V5 printed 5.641254 from output every 0.1 M; this run samples every
  0.05 M, so the minimum moved in the sixth digit); HRNA: m1 reaches 2.4719 M at t = 97.12
  and is stopped there (plunge), m2 ejected with +1.15885 units; hole-fixed Newton ejects m1
  with +1.88742 units, m2 closest 5.86240 M. Same digits as V5, V5b, V6.
Figure `fig_passage` (draft, read): in the planned run windows (280 M at q = 4, 250 M at
q = 10) the two baselines differ in kind from t of about 100 M on: at q = 4 Newton sends m1
out and keeps m2 between 5.8 and 9.7 M, the geodesic baseline sends m2 out and keeps m1 on a
wide orbit; at q = 10 the geodesic m1 plunges at t = 97 M while Newton's m1 leaves.

## 2026-11-15 N2, outcome (run F-20261115-175639-ce844e5)

1. Inputs: 26 files checked; all match the sha256 their runs recorded except the scale run
   F-hills-20261115-045435-f62d553 (wave 1, novelty helper), whose manifest lists its outputs
   without checksums; read as it is and said so in the ledger appendix. Prediction met.
2. The recomputed numbers equal those of the source analyses to the precision checked in the
   scripts (`common.close`, relative 1e-12): last disrupting D 2.085 / 0.405, deep-limit
   P_dis 0.8075 / 0.8014, max |E| 27.146 at D = 0.1 (prograde); geodesic fractions at
   beta = 3, 5, 8, 10 and mean speeds equal the run's printed values. Prediction met.
3. Claims check (`tables/claims.md`): 13 of 17 agree, 2 superseded (allotment 40 -> 50 by
   decision 0014; multi-puncture released in core-v0.3), 2 differ. The four changes I
   predicted were found (two as "superseded", the q = 4 m/16 tree as "differs
   (definition)", the "captures" wording as "agrees, wording differs"). Prediction REFUTED
   in one point I did not foresee: the lead's "independent code agrees at nine (sense, D)
   points within 0.002 in P_dis and 0.4 percent in energy (V4b)" (G1/STATUS.md T1,
   EVIDENCE.md "all nine agree") is not what the files show: V4b reran only retrograde
   D = 0.3 and 0.38 (|dP| <= 0.0013, |dE|/E <= 0.0035); retrograde D = 0.1 and 0.2 come from
   V4 with |dP| = 0.0023 and 0.0063 and |dE|/E = 0.0038 and 0.0116, and they have 8 and 14
   wide bound samples that were not followed on. Plausibly the same classification effect;
   not shown.
4. Figures: all seven PNGs byte-identical to the drafts I opened and read
   (`scratch/F-hills/tmp/note/figures/`).
New finding while checking claim 14: the q = 4 input has puncture_radius = 1.8 and
max_nmb_per_rank = 2700; its m/16 tree reaches 2864 MeshBlocks along the passage (run
F-hills-20261115-131933-907e5fe), above that limit and close to the card's ~3000 slots.

## 2026-11-15 N3. Rerun of the figures and tables after the text pass (prediction)

Changes since N2: two ledger rows added (survival criterion H1 of run
F-hills-20261115-132942-2f7ad7f; recoil of the heavy black hole in E6), the isotropic fit
row, narrower table columns, explicit frameon=False in the legends (the style already set
it), comments of the generated tables.
Prediction: every PNG byte-identical to N2 (the legend change is a no-op under czstyle);
ledger.tex differs from N2 only in the added rows and the column widths; claims.md
identical. Refuted if a PNG changes.

## 2026-11-15 N3, outcome (run F-20261115-180428-fc8172f)

Prediction met: all seven PNGs byte-identical to N2; `claims.md` identical; `ledger.tex`
differs only in the comment line, the column widths and the four added rows (H1: largest
|dP| 0.0088 against SKR's retrograde curve and last disrupting D 0.445 when bound binaries
wider than 3.5 a_b count as disrupted; isotropic fit deviations 0.015 and 0.017 for D <= 1
against the stated one percent; the printed plateau and accuracy; recoil 13.3 M by t = 280 M).
Note compiled (11 pages, latexmk), checker clean in the main text, every page read.

## 2026-11-15 N4. Final rerun after the last ledger format change (prediction)

Only change: penetration factors below 1e-3 printed as powers of ten in `ledger.tex`
(retrograde maximum energy at D = 10^-5). Prediction: PNGs and `claims.md` byte-identical to
N3; `ledger.tex` differs in that one cell. Refuted otherwise.

## 2026-11-15 N4, outcome (run F-20261115-180609-abc9f6e)

Prediction met: PNGs and `claims.md` byte-identical to N3; `ledger.tex` differs in the one
cell (D = 10^-5). These outputs are the ones in `figures/` and `tables/`; appendix B of the
note names this run. Note recompiled (11 pages), checker with --compile: 0 undefined
references or citations, 0 overfull boxes; candidates only in the ledger appendix (run ids)
and in the scripts (data keys), accepted by exception 1 of `../WRITING_GUIDE.md`.
Pages 1-11 read after N3, pages 2 and 10 again after N4.

## 2026-11-20 Wave 3, round 1: note brought to G1 state (helper "note"; plan and predictions)

Restart check: the note's last commits are cc8e31f7 / b35169ab (v0, wave 2); no stranded file in
`note/`; deliverables of this package do not exist yet, so the revision starts from v0.
Main merged by the planner at ea569de3 (not merged again here). Sources read: `CLAUDE.md`,
`harness/RULES.md` "nrpic-run", the paper-writing skill (on disk, Skill tool unavailable),
`../WRITING_GUIDE.md`, `../NOTATION.md`, this directory, `stage/G1/STATUS.md`, `nr_first/README.md`
and `JOURNAL.md` (E1-E11, E10a), `newton3/README.md` (Jacobi split, newton3_fix), and
`stage/REVIEW-wave2.md`.

### Plan of the revision (skill: an existing draft is edited in place; Sec. 10 does not apply)

Sections:
- Title, date, abstract, Introduction (results list): G1 state, v1 of 20 November 2026.
- Sec. III (set-up): architecture figure replaced by the state as of release core-v0.3; the
  data-flow schematic of a passage in "Numerical methods" (chain of segments, tracker-keeping
  wrapper, readers); the 1PN reference named as the third reference with a "(round 2)" slot.
- Sec. IV becomes "Reference solutions: tests and predictions" (Newton, geodesic, the two
  references at q = 4 and 10, the first passages in the references); corrections of
  `stage/REVIEW-wave2.md` carried: the geodesic fractions at q = 10 from four tidal radii are
  model outputs inflated by the start convention and a spurious self-acceleration of a moving
  binary (second check, F-20261115-175620-df20ffe); the q = 10 start state turns at 5.77 M in the
  GR test-mass reading (V9, F-20261119-145449-245e984), so it is rebuilt before any q = 10
  passage; the independent restricted code agrees at seven points and differs slightly at
  retrograde D = 0.1 and 0.2 (already in v0's text). Kerr slot "(round 2)".
- New Sec. V "Full relativity: data, members, mesh and the first passage":
  V.A constraints of the three-black-hole data (E2; junk slot "(round 2)");
  V.B a single member: gauge settling and horizon drift (E3; S2g slot "(round 2)");
  V.C mesh and tree, cost (E11 + the v0 cost subsection, label sec:t-cost kept);
  V.D the first passage: set-up, start-state reading (V9), cost (E7), prediction, and the
  baselines' disagreement on its outcome; outcome slot "(round 2)"; 1PN prediction slot.
- Sec. VI plan: gates updated (G1 state); Sec. VII summary; appendix A parameters unchanged;
  appendix B ledger with a third table (full relativity).
Figures: schem_architecture (rewritten), schem_dataflow (new), fig_constraints (E2),
fig_single (E3), fig_tree (E11), fig_smoke (E7); the v0 figures unchanged.
Numbers and their runs (ledger rows):
- E2: C0 run F-20261115-173547-a02af7d, analysis F-20261115-181434-b9c8916 (`c0_constraints.json`,
  byte-identical to the first analysis F-20261115-181053-d52f22d).
- E3: raw S3/S2 of F-20261115-173601-2fae2dc (trackers, horizons, history), summary of the
  lead's rerun F-20261119-145619-8246322 (`single_analysis.json`), windows of E10a
  F-20261119-144351-b448f38 (`s2g_compare.json`).
- E11: F-20261119-144425-10a94b7 (`tree_check.json`, same numbers as F-20261119-143931-4fbf2d0)
  and F-20261119-144024-988d5c9 (`tree_path.json`); stop positions from E3.
- E7: F-20261115-174602-c6879fe (log, card-memory file, trackers, history of `P1smoke/`),
  analysis F-20261119-144544-d9c8542 (`p1_analysis.json`); cost arithmetic from these with the
  largest wave-1 tree (F-hills-20261115-131933-907e5fe).
- Start state: V9 F-20261119-145449-245e984 (`review_gr.json`). P1 itself
  (F-20261119-150017-b45ec5f): set-up and prediction only (lead's prediction, `JOURNAL.md`
  "P1: decision (lead) and prediction"), no outcome.
Not used (other packages or not reviewed): `eih/`, S2g (F-20261119-143443-f11ebb9), the Kerr work.

### Predictions [JUDGEMENT] for the figure run (run_all with the four new figures)

1. fig_constraints reproduces `c0_constraints.json`: code norm with the correction 1.191e-2,
   4.713e-5, 5.514e-7 at m/4, m/8, m/16; closed forms 4.9e-7 (corrected) and 1.63e-5
   (uncorrected), ratio about 33; truncation orders 7.96/7.62 and 7.98/7.68. Refuted if a plotted
   value differs from the JSON.
2. fig_single, from the raw tracker, horizon and history files read with the package readers
   (`nrread.py`, read only): window means of f equal `single_analysis.json` of
   F-20261119-145619-8246322 to 1e-9 relative (S3 0.4825 over 10-20 m, S2 0.7574), the
   horizon drifts from the median of t = 4-6 to that of 12-14 equal E10a (+5.11e-4 S3,
   +8.49e-4 S2) to 1e-9, the first good search (hrms < 1e-3) at t = 3.5 (S3) and 2.5 (S2).
   Refuted if any differs (then the raw files or the readers changed since).
3. fig_tree: restart trees equal the model level by level (400 at t = 0; 1576 at t = 10; 1548
   at t = 20 for S3); the model along x = 0-20 m has maximum 1632 and exceeds the 1600 slots
   from x = 2.25 m; the runs stopped at x = 2.203 (S3) and 2.217 m (S2).
4. fig_smoke: 1716 -> 1744 MeshBlocks, 689088 MeshBlock-cycles in 334.9 s (2057 per second),
   peak card memory 70847 MiB, trackers within 4.1e-9 of the input at t = 0, horizon medians of
   the good searches 0.12952, 0.12949, 1.00271; cost of P1 16.9 (N = 1744) to 20.1 (N = 2080)
   card-hours for 71680 cycles.
5. The v0 figures (fig_newton, fig_geodesic, fig_rp_scan, fig_passage, fig_cost) are
   byte-identical to the committed PNGs of N4 if the environment (matplotlib 3.10.8) is the
   one of N4; the ledger rows of v0 unchanged (new rows added in a third table).
Refuted as a whole if a script needs a number it cannot locate in a registered run.

## 2026-11-20 Figure run of the G1 revision, outcome (run F-20261120-222908-4ffcfba, about 40 s, one core)

`scripts/run_all.py` at commit 4ffcfba through `nrpic-run submit --kind scouting --gate G1
--package tracks/F-hills/note --cores 1`; completed, 39 files checksummed. Outputs copied into
`figures/` and `tables/`. Every input checked against the sha256 its run recorded (the
wave-1 scale run as before, without a record). [VERIFIED, `fig_*_numbers.json`, `log.txt` of
the run]
1. fig_constraints: met. Code norm with the correction 1.19e-2, 4.71e-5, 5.51e-7; closed forms
   4.91e-7 (corrected), 1.64e-5 (uncorrected), 3.02e-6 (plain sum, m/8); ratio of the closed
   forms 33.3; orders 7.98/7.68 (corrected) and 7.96/7.62 (uncorrected), equal to the JSON.
2. fig_single: met. From the raw files: f over 10-20 m 0.4825 (eta m = 2) and 0.7574
   (eta m = 0.25), equal to `single_analysis.json` to 1e-9; drifts +5.11e-4 and +8.49e-4
   (ratio 1.66), first good search t = 3.5 and 2.5 m, equal to E10a. New in the figure: the
   searches at t = 0.5 m of both runs (mass 2.2 percent low, residual 0.019) are off its scale
   and are named on it.
3. fig_tree: met. Restart trees 400, 1576, 1548 equal to the model level by level (asserted);
   model along x: 1548, 1576, 1604, 1632, first above 1600 at x = 2.25 m; stops at
   x = 2.203 and 2.217 m.
4. fig_smoke: met. 1716 -> 1744 MeshBlocks (70 created, 42 removed), 689088 MeshBlock-cycles
   in 334.9 s = 2057 per second, peak 70847 MiB, trackers within 4.1e-9 of the input, horizon
   medians 0.12952 / 0.12949 / 1.0027 with 1 / 2 / 17 missed of 25, cost 16.9 and 20.1
   card-hours for 71680 cycles. Not predicted, read from the files: none of the heavy black
   hole's eight found searches in the smoke has a residual below 1e-3; the members' trackers
   move at 0.59 and 0.62 of |P|/m (bare mass) at t = 1.56 M (12.5 member masses), below the
   0.76 of P/M_ADM of the single member with the same damping (eta m = 0.25) at that time; the
   normalisations differ by a few percent; no cause named (one reading, no test).
5. Met: fig_newton, fig_geodesic, fig_rp_scan, fig_passage, fig_cost PNGs byte-identical to the
   committed N4 PNGs (their PDFs differ only in the embedded date); the v0 rows of
   `tables/ledger.tex` unchanged (a third table added); `claims.md` identical (13 of 17 agree).
   schem_architecture and schem_timeline changed as intended. Every new PNG byte-identical to
   the draft I opened and read (`scratch/F-hills/tmp/note/figs/`).

## 2026-11-20 Rerun after three ledger rows (prediction)

Changes since F-20261120-222908-4ffcfba: `common.py` (run key of the second check's flat-space
run F-20261115-175620-df20ffe), `ledger.py` (rows: the geodesic model's sideways acceleration of
a binary moving through flat space, 1.065e-4 against 0 for the Newtonian law; the single-member
set-up m = 1, P = 0.25, eta = 2 and 0.25, 1600 slots, read from the run's input and batch list;
the first good horizon searches of the smoke, 0.5 M for both members and none of the heavy
black hole's eight found searches). Prediction: every PNG byte-identical to the previous run;
`ledger.tex` differs by exactly these three rows; `claims.md` identical. Refuted otherwise.
Amendment before the run: the full-relativity ledger table was too tall for a page (LaTeX:
"Float too large for page by 52 pt"), so `ledger.py` now writes it as two tables
(tab:ledger3: data, single member, tree; tab:ledger4: first passage). Prediction amended:
`ledger.tex` differs from F-20261120-222908-4ffcfba by the three rows and this split only.

## 2026-11-20 22:34 UTC PAUSED (locks/PAUSE appeared: five-hour window at 97 percent)

Where I stopped (everything below is committed):
- Done: plan and predictions; schematics `schem_architecture` (state as of core-v0.3) and
  `schem_dataflow` (new), timeline state updated; data figures `fig_constraints` (E2),
  `fig_single` (E3), `fig_tree` (E11), `fig_smoke` (E7), each PNG read; registered figure run
  F-20261120-222908-4ffcfba (outcome above, all predictions met) and its outputs in
  `figures/`, `tables/`; ledger rows of the four G1 groups; `main.tex` rewritten for G1
  (commit d746da26): new Sec. V (data at the start, single member, mesh and cost, first
  passage set-up / start state / cost / prediction), corrections of `stage/REVIEW-wave2.md`
  (geodesic fractions as model outputs with the flat-space self-acceleration; q = 10 start
  state turns at 5.77 M; seven-point agreement of the independent restricted code), round-2
  slots in the text.
- Not done: the rerun of `run_all.py` after the three added ledger rows and the split of the
  full-relativity ledger into tab:ledger3 / tab:ledger4 (prediction written above; nrpic-run
  refused once because a draft main.pdf was uncommitted, then the pause came). So
  `tables/ledger.tex` in the note is still the one of F-20261120-222908-4ffcfba (three tables),
  while `main.tex` cites four: the committed `main.pdf` is the v0 PDF, not rebuilt.
  A draft compile with the new ledger (not committed) gave 16 pages, no undefined reference;
  LaTeX reported a stuck float at the start of Sec. V.A (to look at on the pages).
- Next steps on resume: (1) `harness/bin/nrpic-run submit --kind scouting --gate G1 --package
  tracks/F-hills/note --cores 1 --purpose "..." -- .venv/bin/python
  tracks/F-hills/note/scripts/run_all.py`; check the prediction (PNGs byte-identical to
  F-20261120-222908-4ffcfba, ledger differs by three rows and the split); copy figures/ and
  tables/; put the new run id into appendix B of main.tex; (2) latexmk; check_manuscript.py
  with the guide's forbid list; read every page; fix the stuck float; (3) README: contents,
  rerun commands, the round-2 slots (P1 outcome and energies, horizons, burst; post-Newtonian
  reference and its P1 prediction; junk energy of the three-black-hole data; S2g mass-scaled
  damping and single-member junk; Kerr comparison) and Requests (guide: allowed numbers
  eta m = 2 and 0.25, P = m/4, cells m/4; outline: Sec. IV split into reference solutions and
  full relativity); (4) commit main.pdf and push.

## 2026-11-21 Lead (batch 2a): corrections from the G0 verifier (stage/G0/VERIFIER.md)

Applied by the lead to `main.tex` (text only; nothing rerun, the PDF is not rebuilt):
- Sec. IV A (old l. 129): the BKRS fits are followed "to about one and a half times their stated
  accuracy" (VERIFIER K3, D10: 0.015 and 0.017 against one percent); the inner retrograde
  difference is closed at the innermost point by the verifier's run F-20261121-030155-1061bcb
  (wide pairs followed), the second inner point is not rerun (N2).
- Sec. IV B (old l. 140): "stays small ... throughout" was wrong (VERIFIER N1, D7; lead's run
  F-20261121-063504-00f0743: a/R_curv at any time 0.199 prograde at beta = 10, 0.0056 while
  bound); the sentence now says so.

To apply on resume (in `scripts/ledger.py`, then the registered rerun of `run_all.py`; they
change the predicted "ledger rows unchanged" of the pending rerun, so predict them first):
1. Row "largest a_b/R_curv of a bound binary at beta = 10" (0.0056): add the any-time value
   0.199 (s1.npz `alpha_all`, run F-hills-20261115-130405-ce17dcf) as a second number (D7).
2. q = 4 geodesic ejected energy 0.9703: three digits and the time of evaluation; it drifts
   0.9777 (t = 600 M) to 0.9650 (1500 M) (D9, verifier run F-20261121-030138-8d3ca16).
3. q = 10 geodesic "plunges at t = 97.1 M": the crossing of 2.5 M is at 96.9 M; 97.1 is the first
   sample inside (D9).
4. Row "card memory, MeshBlock slots: about 3000" with locator `multi_puncture.md` lines 229-230:
   release core-v0.4 rewrote the paragraph; now lines 235-247, "about 3100 slots with three
   finders" (the lead's rerun of the verifier's ledger check, run F-20261121-063712-25981e0, fails
   this row only).
5. Every r_p of the first passages with the GR turning point beside it (D1): q = 4 9.81 M
   (turning 9.25 M), q = 10 8.00 M (5.77 M) - table 3 has them; the text of Sec. II should say so.
6. V7 percentages at r_p = 12-13 M (table 2) only with their construction (circular binary
   released at 4 r_t); the plan's start rule (state integrated from 10 r_t) gives other numbers
   (D2, verifier runs F-20261121-031920-5e6425e, F-20261121-034434-0113a18, F-20261121-040103-6b9074c).
