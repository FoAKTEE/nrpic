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
