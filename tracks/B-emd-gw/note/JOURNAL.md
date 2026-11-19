# JOURNAL of note (helper package of B-emd-gw, wave 2)

Package: the working note v0 of Track B (REVTeX), its figures from registered runs, the two
schematics of the G0 stage check, the numerical ledger, a check of the numbers stated in the
lead's documents against the run outputs, and `stage/G0/STAGE_REPORT.md`. Predictions are
written before the run they concern; outcomes are appended below, also when a prediction
fails. Run ids are under `tracks/B-emd-gw/runs/`.

## Set-up (2026-11-15, before any run of this package)

Sources of every number of the note: the output directories of registered runs under
`/data/haiyangw/nrpic/scratch/B-emd-gw/<run_id>/`, checked against the sha256 the run recorded
(its `sha256sums.txt` or the manifest field `outputs_sha256`); wave-1 runs that recorded no
checksum are read as they are and listed so in the ledger, and for them the lead's re-check
L1 (run B-emd-gw-20261115-131016-03b1119) regenerated the same file bit for bit
(`stage/G0/REVIEW.md`), which the claims script tests where L1 holds a copy.

Runs the note reads (one per figure or table):
- periodic Z4c linear wave, convergence table: L1 export, regenerated
  `periodic_z4c/tables/lw_x.json` (B-emd-gw-20261115-131016-03b1119);
- diagnostics on AthenaK output: B-emd-gw-20261115-120128-7dfaa38 (`results_athenak.json`),
  analytic TT validation in L1 (`gw_tt/results_tt.json`);
- crossed-wave strain and plane-symmetric null: B-emd-gw-20261115-113148-4e5c33b;
- regime estimates (junk decay, virial frequency, cost): B-emd-gw-20261115-113632-2960145;
- symbolic checks: B-emd-gw-20261115-113102-bc5e082, lead checks B-emd-gw-20261115-131027-03b1119;
- pancake through shell crossing (analysis of the GR card runs -115217-69ab1db,
  -115902-a3207d7 and the Newtonian runs -115239-69ab1db, -122451-01801f6):
  B-emd-gw-20261115-123852-ea4475c;
- FLRW background: B-emd-gw-20261115-115414-7ffbde1;
- semi-analytic baseline T1-T8: B-emd-gw-20261115-115752-840e994.

## Predictions (written before the first run of the note scripts)

N1 (figures and ledger from registered outputs). Every data-figure script and `ledger.py`
runs to the end reading only the files above; every file with a recorded checksum matches
it. Refuted by a checksum mismatch or by a script that needs a file outside a registered
run directory.

N2 (agreement with the committed package results). Each file read from a run directory is
byte-identical to the copy committed in the helper package (`*/results/*.json`,
`periodic_z4c/tables/lw_x.json`), because L1 found every leaf bit-identical. Refuted by any
differing byte (other than the figure paths and wall times L1 named for
`baseline_results.json`).

N3 (claims of the lead's documents). Of the numbers stated in `stage/G0/REPORT.md`,
`stage/G1/STATUS.md` and `STATUS.md` that the claims script checks (about 40), all agree
with the files at the precision they are stated, except at most a few wordings that
round or drop a qualifier (one already seen while reading: G1/STATUS.md says the
linear-wave errors match the Fourier-symbol prediction "to 1 % up to 64 cells", while
`periodic_z4c/README.md` and `tables/lw_x.json` give 9.5 percent for the production phase
error at 64 cells). Refuted if more than five checked numbers disagree beyond their stated
precision, or if any disagreement changes a conclusion of the G0 report.

N4 (the note compiles). `latexmk -pdf` on `main.tex` gives no undefined reference or
citation; the paper-writing checker reports no hit in the main text outside the accepted
ledger exception of the writing guide. Refuted by an undefined reference, a figure caption
longer than five lines on the rendered page, or a project name in the main text.

N5 (figures). Each figure shows what `WRITING_GUIDE.md` (Figures) says the reader should
see; I look at every PNG with Read before citing it. Refuted, for example, if the pancake
departures at the two box sizes do not collapse onto each other after division by the
ratio of their (H/k)^2 at a = 10.

## Development runs (not cited)

Before the registered runs the scripts were run into `scratch/B-emd-gw/tmp/note/` while
the figures and the LaTeX were drafted (figure labels, legend frames, caption length,
ledger split into two tables, a bibliography style that needs `@misc` for preprints). One
finding there changed the text before any registered run: the claims check shows that the
Hamiltonian-constraint numbers that `stage/G1/STATUS.md` quotes for a thousandfold
expansion are the values of the first record (t = 100 Mpc/h) of `cosmo/analysis/daverio_a.json`.

## Registered runs

- B-20261115-165138-cb53c14 (nrpic-run, 1 core, 8 s): first full run; superseded because the
  first-source helper published the outcome of its late-rise analysis (run
  B-20261115-164616-a6d9477, commit 9719b17) while this package was being written, and the
  note's text on that rise had to follow it.
- B-20261115-165231-9e29328 (nrpic-run, 1 core): second full run, superseded by the next (nrpic-stage verify flagged the y label of fig_baseline cut at the figure edge; margin widened, commit 91026b8). `note/figures/` and
  `note/tables/` are copies of its `figures/` and `tables/`. A first submit at 16:51Z was
  refused (16 cores busy in other helpers' local runs, decision 0006); retried a minute later.

## Outcomes of N1-N5 (2026-11-15T17:00Z)

N1: HOLDS. Every script ran to exit 0 reading only registered run directories (14 files
from 13 runs, `tables/checked.md`); the 7 files whose runs recorded checksums match them;
7 files of wave-1 runs that recorded none were read as they are. Beyond N1 as written, the
claims check also reads the lead's stage documents (to locate the stated numbers) and one
committed file of the cosmology extension, `cosmo/analysis/daverio_a.json`.

N2: HOLDS. All 9 run outputs that have a committed copy in a helper package are
byte-identical to it (`tables/checked.md`).

N3: HOLDS (4 of 28 differ, none changes a G0 conclusion). `tables/claims.md`:
1. `stage/G0/REPORT.md:88`: "lapse = scale factor to 1e-7 at a = 4 and 36"; the files give
   1.9e-7 at a = 4 and 7.0e-8 at a = 36 (order of magnitude only).
2. `stage/G1/STATUS.md:22`: errors "matching the Fourier symbol of the scheme to 1 % up to
   64 cells"; the production phase error at 64 cells departs by 9.5 % (the package README
   says so; the others are within 1 %).
3. `stage/G1/STATUS.md:56`: "Hamiltonian constraint 1.6e-9, 1.1e-10, 3.2e-11 at 8, 16, 32
   cells over a thousandfold expansion"; these are the values at t = 100 Mpc/h, the first
   record; at t = 3000 Mpc/h (end) the values are 3.1e-8, 2.5e-9, 3.0e-9 and do not fall
   from 16 to 32 cells. The fourth-order convergence holds for the error of chi.
4. `stage/G1/STATUS.md:47`: the Newtonian mode and its quadrupole history "exist on
   `core/newton` (tip ce329f5, not on main)"; since the merge of release core-v0.3 they are
   on main (`coord/INTERFACES/newtonian_mode.md`, CLAUDE.md).
Two wordings agree in number but not in words: `REPORT.md:50` calls the box means of the
constraints (1.3e-3, 0.21 at a = 15) "pancake void" values (the dumps place most of the
violation in the void, but the numbers are box means); `REPORT.md:91` "plane symmetry to
1e-12" (largest transverse velocity 1.25e-12).
New since the G0 report, from another helper: the late TT rise in the wave-1 cosmology
dumps, flagged in REVIEW.md as a possible second-order gauge piece, is not that piece
(run B-20261115-164616-a6d9477, `first_source/JOURNAL.md` lines 158-193); the note follows
it. OPEN.md item 9 and RISKS.md R4 still carry the old reading (lead's files).

N4: HOLDS. `latexmk -pdf`: 0 undefined references and citations, 0 overfull hboxes (one
overfull vbox of 7 pt in the output routine, ledger page). Checker (paper-writing
`check_manuscript.py --compile` with the guide's forbid list): every principle clean in the
main text; the remaining hits are run ids and file names in the ledger appendix, its
generated tables and the scripts (exception 1 of WRITING_GUIDE.md). All ten pages read at
90 dpi: every caption within five lines, figures legible, ledger tables fit the page.

N5: HOLDS. Figures looked at (Read): fig_source, fig_waves, fig_pancake, fig_baseline,
schem_architecture, schem_timeline. In fig_pancake (a) the four-Hubble-radii curve divided by
16 lies on the one-Hubble-radius curves from a = 5 on (16.1 at a = 10); at a = 2 it lies
lower by a factor of two, the early transient the verify_cosmo journal reports (P2).

Not done: step 4 of the paper-writing procedure for a new paper (reviewer subagents with
the 1000-word version; no subagent tool in this session); `nrpic-stage verify` (see below).

## Registered run used by the note (17:00Z)

B-20261115-165556-a399d4e (nrpic-run, 1 core; one refusal for busy cores before it): the run
the note uses; `note/figures/` and `note/tables/` are copies of its outputs. Numbers and the
claims check are those of the previous run (only the margin of one figure changed).

## nrpic-stage verify and report (17:00Z)

First verify (tip 78bb928): FAIL on `clean` (another helper's uncommitted journal), `runs`
(other helpers' runs in flight, wave-1 manifests) and `rerun` (fig_baseline printed a
czstyle warning, y label cut by 0.05 in at the left edge). The last one was mine: margin
widened (commit 91026b8), note rerun as B-20261115-165556-a399d4e. Second verify (tip
0fee5b6): every check PASS except `runs` (17 of 108: 8 runs of other helpers in flight,
8 wave-1 manifests of the scope and baseline packages without `code`, `env`, `input`, and
one first-source run with moved outputs outside its `sha256sums.txt`; none of the note's).
`nrpic-stage report` wrote `stage/G0/STAGE_REPORT.md` (verdict FAIL: C2, C18 open, verify
`runs`, no VERIFIER_REPORT.md); I added two sections of my own (scoping text and note;
disagreements between the stage documents and the files) and a draft "Decision requested"
for the lead to rewrite. Commit c382abd.

# Wave 2b (2026-11-19): note v1, the G1 products on paper (package note2)

Task: the two G1 schematics (updated architecture, data flow) and the G1 sections of the note
(the first source against the second-order strain; the spatial-gauge check; the Newtonian-mode
baseline), from the registered runs of wave 2 that `stage/REVIEW-wave2.md` lists. Where the
review and a file disagree, the file wins. No run of wave 2b enters the note (none had finished
at the start of this package; sibling helpers' runs are in flight).

State found at the start (06:02 PST): worktree clean after `git merge main` (d058b72); no
partial work of this package (the last commit touching `note/` is 2f8806a, the lead's
one-sentence fix of the late-rise wording). The note is v0 (10 pages), its figures from run
B-20261115-165556-a399d4e.

Sources the new sections read (run outputs, checksums in each run's `sha256sums.txt`):
- per-dump diagnostics of the scan, 64^3: B-20261115-174722-ba1048d (eps = 0, 0.1, 0.3),
  B-20261115-180834-c77a132 (eps = 1, zero shift and Gamma driver); 32^3:
  B-20261115-184650-2d155b6 (all five cases); card runs B-20261115-164059-d802e82,
  -165353-b592d43; processor runs -165525-f7c2004;
- gauge piece on exact pure-gauge data (T0): B-20261115-164221-6a6b779 (`t0_gauge.json`);
- Newtonian mode: B-20261115-173904-a7297e3 (`pancake.json`), B-20261115-174405-af11300
  (`ellipsoid.json`);
- the lead's rechecks: B-20261115-190007-e09a0d2, -190015-4dd3416 (cited only as the second
  reading of a number, never as the source of a printed value).

Found while reading, before any run: the claims check of `ledger.py` locates its phrases in the
lead's stage documents at the working tree; the lead rewrote `stage/G1/STATUS.md` after the
check (review, section note), so a rerun now finds 13 of 28 (15 phrases no longer found: a
development run into `scratch/B-emd-gw/tmp/note2/tables`). The claims check is a record of
those documents as they stood at G0: I pin it to the revision at which run
B-20261115-165556-a399d4e checked them (its manifest `git.sha`) so that it reproduces.

## Predictions (written before the first run of the new scripts)

N6 (first source from the per-dump files, my own reduction in `fig_scan.py`). From the
columns `h_K1_plus`, `h_K2_plus` (cosine part) of the 64^3 files and my own s g(tau):
max |c_+/(s eps g) - 1| over 2 <= a <= 10 is 0.22 percent (eps = 0.1, 0.3) and 0.44 percent
(eps = 1), the same at K2 with the opposite sign (helper P2, lead R2: 0.224, 0.222, 0.435
percent); c_+/eps for 0.3 against 0.1 within 0.05 percent for 2 <= a <= 10; largest c_+/s
of eps = 1 is 2.55 near a = 123 (lead R6; the helper wrote 2.5 near 95). Null (eps = 0): the
largest TT amplitude of h over all dumps <= 3e-16 (lead: 1.9e-16 at every tenth dump; helper:
2.8e-16 over all single-precision dumps). Refuted if any of these differs by more than 2 in
the last printed digit, or if the null exceeds 1e-15.

N7 (resolution, same script). max |c_+(32^3)/c_+(64^3) - 1| over the common dumps with
5 <= a <= 40 is below 0.1 percent in every case (lead R5: 0.091 percent for eps = 0.1; the
helper's 0.06 percent was read at five values of a only). Refuted above 0.1 percent.

N8 (gauge, `fig_gauge.py`). eps = 1, raw zero-shift minus Gamma-driver c_+ over |s|: 0.13,
0.36, 1.45 percent at a = 5, 10, 20; after G_tot in each run 0.005, 0.008, 0.03 percent;
median |corrected/raw| over the dumps where |raw| > 1e-3 |s|: 0.084 (64^3), 0.093 (32^3).
With G alone (no cross terms) the median ratio is about 5. The G_tot-corrected strain departs
from s g more than the raw one at a = 10 and 20 for eps = 1 (0.69 against 0.44 percent, 3.5
against 2.3 percent; lead's point 3). T0: slopes 2.000 (Lambda h) and 3.000 (after G) for the
two seeds without slicing; 2.000 for both with slicing. Refuted by a difference beyond the
printed digits, or if the corrected strain lies closer to s g than the raw one at a = 20.

N9 (Newtonian mode, `fig_newton.py`, values read from the helper's analysis files). Measured
over H1-predicted sheet error at a = 2 and 5 within 2 percent for n = 16, 32, 64; the error
at n = 32 over n = 64 near 4 at a <= 5; crossing time of the ellipsoid 24.0659, 23.8955,
23.8604 against the ODE's 23.8524, Richardson 23.8513 (order 2.3); energy to the crossing
-34, -18, -9.7 percent (raw), order 0.88; N3 constants identical over the four alpha to
< 1e-13. The review gives N3 constants 0.0620684, 0.0772146 (R9), which match neither the
helper's averaged (0.061787, 0.076375) nor raw (0.062059, 0.077205) values: the note prints
the helper's file values (the file wins) and the journal records the review's. Refuted if a
value read differs from the README of `newton_tests` beyond its digits.

N10 (schematics). The architecture of v0 classified by "exists / to be ported / new"; for G1 I
classify by evidence: verified by the track in a registered run (green), on a tested branch
of the code but not yet run by the track (slate), to be written (red). Prediction: about half
of the twenty-one boxes change colour or text (Newtonian mode with history, Gamma driver,
gauge piece, second-order strain, Zel'dovich ellipsoid become verified; oblique wave,
double-precision dumps, jitter and thin boxes sit on core/requests-b). The data-flow diagram
has five stages (initial data, evolution, outputs, analysis, comparison with references) and
the ledger. Refuted if a box claims "verified" without a run id in `common.py` or a run
manifest of this track.

N11 (pages). After the new sections the note compiles with no undefined reference or
citation and no overfull hbox; every caption stays within five lines; the checker finds no
project name in the main text. The note grows from 10 to about 14 pages. Refuted otherwise.

## Development runs (wave 2b, not cited)

The scripts were run into `scratch/B-emd-gw/tmp/note2/` while the figures and the text were
drafted. Findings there that changed the scripts before the registered run:
- Dump times of different runs differ by up to one coarse step (32^3 against 64^3: up to
  0.025 in tau late; the eps cases among themselves by ~1e-6), so matching dumps by time
  with a tight tolerance silently dropped most of them (my first gauge numbers came out
  five times too large from a sparse match). The two gauges share their step sequence to
  2e-9 and are matched dump by dump; every other pair is compared by a cubic spline in tau
  of one series at the dump times of the other (`g1data.py`).
- `ledger.py` compared every file named `pancake.json` with the wave-1 copy; the
  Newtonian-mode `pancake.json` has its own committed copy. The committed-copy check is now
  per run (14 of 14 identical).
- The departure from second order looked like a power law; its local slope is 2.3-2.4 between
  a = 10 and 60, so the text says "slightly faster than the square of the scale factor" and
  shows no guide line.

## Registered run (wave 2b)

B-20261119-142525-2a55af7 (nrpic-run, local, 1 core, exit 0; commit 2a55af7): all figure,
schematic and table scripts; `note/figures/` and `note/tables/` are copies of its outputs.
Its `log.txt`: every script exit 0; committed copies identical 14 of 14; claims 24 of 28 (the
G0 record, now reproduced from the documents at a399d4e). Text edits after the run
(wording, symbol renames in the gauge-piece paragraph, one qualification in Sec. IV G) touch
no script and no number.

## Outcomes of N6-N11 (2026-11-19, from run B-20261119-142525-2a55af7)

N6 HOLDS. Departure for 2 <= a <= 10: 0.224, 0.222, 0.435 percent (eps = 0.1, 0.3, 1) at K1,
the same at K2 with the opposite sign; 32^3: 0.195, 0.190, 0.379 percent. Linearity 0.3 vs
0.1: 0.0497 percent (1 vs 0.1: 0.213). Largest c_+/s of eps = 1: 2.547 at a = 123.3 (the
review's correction of the helper's "2.5 near 95" stands). Null: largest TT amplitude of h
2.77e-16 (single precision, 218 dumps) and 2.05e-16 (double, 23 dumps); of tilde A 1.08e-16
(double), 6.5e-15 (single); z dependence <= 2.0e-14.

N7 HOLDS. max |c_+(32^3)/c_+(64^3) - 1| for 5 <= a <= 40: 0.086, 0.032, 0.023, 0.022 percent
(eps = 0.1, 0.3, 1, driven shift); 40 < a <= 80: up to 1.6 percent; a = 100: up to 3.2
percent. The lead's 0.091 percent (eps = 0.1) used another matching of the dumps; the
helper's 0.06 percent was read at five values of a only.

N8 PARTLY REFUTED (the predicted numbers, not the physics). I took the raw and corrected gauge
differences from the review (0.13, 0.36, 1.45 percent; 0.005, 0.008, 0.03 percent at a = 5,
10, 20). From the files: raw 0.121, 0.360, 1.468 percent; corrected 0.002, 0.0076, 0.030
percent, equal to the helper's own summary (`first_source/results/scan_summary_64.json`, P6),
so the review's values at a = 5 and 20 differ from the files in the second digit (the review
interpolated in its own scale factor). The file wins. The rest holds: median corrected/raw
0.0840 (64^3), 0.0928 (32^3) over the 89 percent of dumps where |raw| > 1e-3 |s|; quadratic
piece alone 5.24, 5.32; the corrected strain departs more from s g than the raw one (a = 10:
0.69 against 0.44 percent; a = 20: 3.45 against 2.31 percent); T0 slopes 2.000 (Lambda h),
3.000 (after G), 2.000 with a slicing change.

N9 HOLDS. Measured over predicted sheet error at a = 2, 5: 0.984, 0.982 (n = 16), 0.989, 1.019
(32), 1.000, 1.012 (64); error ratio 32/64: 3.96, 4.03. Ellipsoid t_x 24.0659, 23.8955,
23.8604; ODE 23.8524; Richardson 23.8513, order 2.28. Energy -34.4, -18.4, -9.71 percent,
Richardson +0.74 percent, order 0.876. N3: E/(M (2 alpha)^(7/2)) = 0.0618 (N = 32), 0.0764
(N = 64), averaged d3I, spread 1.9e-14. The review's 0.0620684 and 0.0772146 are raw-d3I
values with its own quadrature (rv_newton.json, R9); the helper's raw values are 0.062059 and
0.077205; the difference (1.5e-4 relative) is the quadrature rule. The note prints the
helper's averaged values, from the file.

N10 HOLDS. The G1 architecture has 24 boxes: 14 verified (each with run ids in the docstring
of `schem_architecture.py`), 3 on the tested branch core/requests-b (jitter, thin boxes,
oblique wave with double-precision dumps), 7 to be written; relative to v0, 13 boxes changed
state or text. The data-flow diagram has five stages, the record band and the ledger.
Both looked at (Read) in the run output.

N11 HOLDS except the page count: 17 pages (predicted about 14; four ledger tables now). latexmk
and the checker: 0 undefined references and citations, 0 overfull hboxes; every caption
within five lines on the rendered page (the two longest shortened before the registered run);
no project name in the main text (the 41 hits of 5.8 are in the scripts, the 5.5 hits in the
ledger appendix, exception 1 of the guide). All 17 pages read at 80-90 dpi.

## Found while writing (not predicted; post hoc, labelled so)

[JUDGEMENT, post hoc] The departure of c_+ from s g divided by (1 + eps^2) is the same for the
three ratios: relative to eps = 0.1, 1.01 and 1.02 (eps = 0.3, 1) at a = 20, 0.998 and 1.01
at a = 40, 0.996 and 1.05 at a = 60 (ledger row fs_scaled). This is the pattern of the
fourth-order terms phi_x^3 phi_y and phi_x phi_y^3 (relative size phi_x^2 + phi_y^2), and it
agrees with the order counting of the verifier's C5 and with the review's point 3 (the
G_tot-corrected strain departs more). I formed the (1 + eps^2) reading after seeing the
departures at a = 20; it has not survived a test written in advance. Test proposed to the
lead: at delta = 0.0025 (same box, same eps) the departure at fixed a is 1/16 of that at
delta = 0.01 if it is of relative order phi^2 (refuted if the ratio is outside 1/12-1/20 at
a = 20-60).

Not used in the note: rho_GW/rho_bar. My reduction (rho_kin + rho_grad)/rho_bar over the
double-precision dumps gives a largest value 4.2e-6 (eps = 1) and 1.2e-8 (eps = 0.1); the
helper's README states 3.5e-6 and 8.8e-9; the review did not confirm these. The definition
behind the helper's number is not in its summary; the note states only the ratio of kinetic
to gradient energy, which is normalization-free.
