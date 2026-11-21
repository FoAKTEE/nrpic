# JOURNAL of the package g1close (helper of A-emd-pbh, wave 3 round 1)

Package: close gate G1 of A-emd-pbh. Apply or rebut the corrections of the wave-2b verifier
(`stage/G1/VERIFIER.md`, run A-20261119-142905-c813c01), put its data-flow schematic
(run A-20261119-143347-37240f3) into the note, record checksums of the wave-1 outputs behind
the ledger, regenerate the note and the G1 stage package, judge C11 and C18. No card time.
Evidence labels as in the brief: [VERIFIED], [BACKGROUND], [JUDGEMENT], [TO VERIFY].

## 2026-11-20T22:22Z, entry 1: corrections planned and predictions (before any run of this package)

Read: CLAUDE.md; coord/CHARTER.md to "Owners" and 9.4; decisions 0010, 0012, 0013, 0016,
0019; harness/RULES.md; `stage/G1/{VERIFIER,README,CHECKLIST,OPEN,STATUS,EVIDENCE,
STAGE_REPORT,VERIFY,REVIEW}.md`; `stage/G0/OPEN.md`; the A-emd-pbh rows of coord/GATES.md and
coord/REQUESTS.md; `note/{README.md,main.tex}`, `note/scripts/{ledger,common,run_all,
schem_dataflow}.py`; `WRITING_GUIDE.md`, `NOTATION.md`; `PLAN-wave3.md`; the paper-writing
skill (SKILL.md of the synced copy). For the wave-2 state: `criteria/README.md` (wave 2),
`newton/SCAN.md` sections 7-8, `runs_ball/README.md` ("Wave 2 results", "Wave 2b"),
`szekeres/README.md`, the manifests of the wave-2b runs.

Exploration done while reading, before this entry (so two of the predictions below are not
blind, and I say which): I opened `results.json` of the two wave-2 criteria runs
(A-emd-pbh-20261115-161813-6c820fb, -163358-9b2d048) and `newton_results.json` of the
Newtonian analysis A-emd-pbh-20261115-164420-4528861 with one-line Python, to know what the
ledger can read. What I saw is recorded under P4 and P5.

### Corrections (verifier locator -> what I will change, where)

| # | Verifier locator | Change | File |
|---|---|---|---|
| a | VERIFIER.md 1.1, 2.1 row "same: median" | ledger row "read-off/top-hat ratio, mu <= 0.15 (range; median)" prints `median_ratio` of `scope_numbers.json`, which is over all six read-offs; print the median over mu <= 0.15 computed from the same arrays, and the all-six median labelled as such | `note/scripts/ledger.py` |
| b | 1.2, 2.1 last row, 2.5 | Sec. III A "a common bang time for every shell": restrict to the core and envelope; say what the surface taper carries | `note/main.tex` |
| c1 | 1.3, 3.4 | Tables V and VI: the values are in units of the nominal mass M_0 = H^2 R_b^3/2 = 1 of the data, the total Misner-Sharp mass is M = 1.0096 M_0: relabel every "/M" of the scouting data as "/M_0", define M_0 in Sec. III A and in Table V | `ledger.py`, `main.tex` |
| c2 | 1.4 | thresholds row: six names for six values, semicolon-separated | `ledger.py` |
| c3 | 1.7, 2.5 "checked against the checksums" | App. B checksum sentence: true for runs with `sha256sums.txt`; for the others, check against the listing of the integrity run of step 3 (`common.py` falls back to it) and say so | `common.py`, `main.tex` |
| d | 1.5, 2.5, 4.4 | criteria state 41 of 41 (4 diagnostics); Newtonian-mode runs (SCAN.md 7-8); SR-1/SR-2 (analyses A-20261115-182657-53da696, A-emd-pbh-20261115-163659-4dbacd0); Sec. V: BH-1, BH-1R, SR-1L, Szekeres named as run, no numbers without a registered analysis | `ledger.py`, `common.py`, `main.tex` |
| e | C11 paragraph | `figures/schem_dataflow.png` as a figure with caption; placed in the ledger appendix (the guide's exception 1 allows file and run names only there) | `main.tex` |
| f | 4.2 | `stage/G1/STATUS.md` T3 and CHECKLIST C8 "14 scan points within 2.2e-4 to 6.3e-4" | `stage/G1/STATUS.md`, `CHECKLIST.md` |
| g1 | 2.1 row "geodesic slicing reaches the step bound" | label the 42.30 as computed with the light speed R_i/R without the conformal factor (the verifier's 42.36 with it) | `ledger.py` |
| g2 | 2.5 row "ball of three r_m ... an order of magnitude is loose" | Sec. III A: "both stay an order of magnitude below the hoop line" -> a statement the numbers support | `main.tex` |
| g3 | 4.5 | SR-1 breakdown: name the criterion (first non-finite record of the line diagnostics) wherever the note or stage/G1 gives a time | `ledger.py`, `stage/G1/STATUS.md` |
| g4 | 1.6, 3.1, 4.1 | SR-2 turnaround: the note quotes it only as the three-point-vertex value and calls it estimator-dependent; no pass/fail. The re-judgement of runs_ball's R2 belongs to the runs_ball helper this round | `ledger.py`, `main.tex` |
| g5 | 3.2 | the M/4 runs have half the box: no order of the core error is quoted in the note; the ledger row says "half the box" | `ledger.py` |
| g6 | 4.4, stage/G1/STATUS.md T2 and section 6 | wave-2 criteria state in T2; SR-2 turnaround per cent figures of section 6 marked estimator-dependent; SR-1 breakdown criterion named | `stage/G1/STATUS.md` |

Not mine (other owners or helpers): finding 6 / weak point 1 / difference 1 (SR-2 turnaround,
runs_ball R2) -> runs_ball helper this round; `docs/FORMATS.md` line 122 -> core (verifier's
request stands); owner's `STATUS.md`, `HANDOFF.md`, `RISKS.md` sentences -> lead (listed in
my README).

### Predictions

- **P1 (a).** From `scope_numbers.json` (run A-20261115-130252-7877b7a): median of
  `ratio_read_to_tc_rm` over mu <= 0.15 = 0.84 at two digits (verifier 0.843), over all six
  = 0.86 (`median_ratio`, verifier 0.8646). The ledger row becomes "0.80--1.01; 0.84 (all six
  read-offs: 0.86)". Refuted if the mu <= 0.15 median does not round to 0.84.
- **P2 (b).** From the shells table of data set 2t (run A-emd-pbh-20261115-130609-947c898,
  `_shells.txt`: R_i, m, E per shell), the time since the bang on the initial slice, from
  the cycloid for E < 0 and t = (2/3) R_i^(3/2) / sqrt(2m) for E = 0: equal to t_i = 10.6667
  within 1e-6 for every shell with R_i < 6.5 (verifier 4.7e-8), and rising to about 13.59
  through the taper (6.5 <= R_i < 9.43; verifier 10.667 to 13.588). Refuted if the spread
  inside R_i < 6.5 exceeds 1e-6 or the taper range differs from the verifier's by more than
  0.01.
- **P3 (c1).** M_0 = H^2 R_b^3/2 = 1 exactly with H = 0.0625, R_b = 8 (data-set JSON), and
  M/M_0 = 1.00959. In units of the total mass: m_AH/M = 0.0797 (first trapped sphere) and
  0.0951 (crunch), tau_ta/M = 16.73 (verifier 1.3). Relabelling changes no printed value of
  the ledger. Refuted by any difference at the printed digits.
- **P4 (d), not blind.** The two wave-2 criteria runs together: 41 checks, all pass, and 4
  diagnostics without a verdict (T1.2b-d, T2.2d-d, T2.4a-d, T2.4c-d), taking T2 from the
  rerun -163358-9b2d048 and the rest from -161813-6c820fb (seen while reading). The ledger row
  changes from "33 of 37; T1.2b, T2.2d, T2.4a, T2.4c" to "41 of 41; 4 diagnostics".
- **P5 (f), not blind.** In `newton_results.json` of A-emd-pbh-20261115-164420-4528861 (14 scan
  points, key `t1_vertex_rel`): nine points lie in [+2.2e-4, +6.3e-4] (the four shapes at
  p = 0, the two amplitude copies at e = 0.1, p = +0.2, the rotated lattice, the 2.1e6-particle
  card point, all at 128^3); outside: the spindle +1.5e-3, the 64^3 controls +8.8e-4 and
  +1.5e-3, the 3.4e4-particle controls -2.4e-4 and -4.6e-4. So the STATUS/CHECKLIST sentence is
  wrong as written, and the verifier's replacement ("only the four p = 0 points at 128^3")
  is too narrow: four distinct shapes, but nine points. The registered check reproduces
  these counts; refuted by any other count.
- **P6 (integrity, step 3).** Of the 15 run directories the updated `common.py` names,
  seven have no `sha256sums.txt` (wave-1 runs -120425-80492f8, -130256-a7374a4,
  -130402-f5566fb, -122117-aa1c84d, -130609-947c898; wave-2 hand-run criteria runs
  -161813-6c820fb, -163358-9b2d048), 55 files in all; the run lists the sha256 of each into
  its own directory and changes nothing in theirs (mtimes and a second hash pass unchanged).
  The eight directories with `sha256sums.txt` verify without a mismatch. Refuted by a
  mismatch (that would be a finding against a run, not against this prediction alone), or
  by any write into a listed directory.
- **P7 (ledger and claims).** After the edits `ledger.py` prints the same values as in the
  committed `tables/ledger.tex` for every unchanged row; the claims check keeps its count
  apart from the two claims I re-point at the wave-2 criteria text of `stage/G1/STATUS.md`,
  and finds at most the two differences it found before (an "upper" bound in the third digit
  and the "0.1 H" overshoot of the lead's journal, which the lead's append-only journal
  keeps). Refuted by a changed value in an unchanged row or a new disagreement.
- **P8 (note).** The note compiles with no undefined reference or citation; the checker's
  project-name and file-name hits lie only in the ledger appendix and in the scripts the
  guide's exception 1 names, plus `schem_dataflow.py` and its figure (new: I ask the lead to
  extend the exception to the data-flow schematic). Every page read; captions at most five
  lines.
- **P9 (stage).** `nrpic-stage collect` keeps C1-C10, C12-C20 as they are; C11 becomes PASS
  (schematic drawn, in the note); C18 PASS with the corrections listed (my judgement, the
  reviewer decides). `nrpic-stage verify` passes except possibly (i) `clean`, if other
  helpers of this round leave uncommitted files in the shared worktree at that moment, and
  (ii) `runs`, if the manifests of the card jobs A-20261119-144419-13d5601 and
  -164634-f1fe887 (status "submitted"; the runs_ball helper finishes them this round) or of
  other helpers' runs are not finished when verify runs. Each failure goes into OPEN.md with
  its cause.

## 2026-11-20T22:27Z, entry 2: outcomes of P1-P5 (run A-20261120-222454-d16dbc6)

Run A-20261120-222454-d16dbc6 (`scripts/check_findings.py`, commit d16dbc6, one core, exit 0):
`findings.json`, `fig_g1close_findings.png` (looked at: top left the read-off ratios with the
two medians, top right the age of every shell on the initial slice of data set 2t, bottom left
the 14 Newtonian scan points against the band of the STATUS sentence, bottom right the tallies
of the criteria checks). Inputs checksummed (the wave-1 directories have no `sha256sums.txt`;
see step 3).

- **P1 holds.** median over mu <= 0.15 = 0.84278 (the mu = 0.05 read-off; five values), over
  all six 0.86460 = `median_ratio` (the key is the all-six median, as the verifier said);
  range over mu <= 0.15 0.8017-1.0123. Finding 1 CONFIRMED. Fix: ledger row prints 0.84 and
  the all-six 0.86 with its own label.
- **P2 holds for the finding, refuted at its stated upper end.** The age on the initial slice
  equals t_i = 10.6667 to 1.2e-14 for the 273 shells with R_i < 6.5 (better than the
  verifier's 4.7e-8: I integrate the shells table directly, it rebuilt the slice from the
  radial table). The first shell more than 1e-6 off is at R_i = 6.65; in the taper every
  shell has E = 0 and less mass than the envelope, so its age rises to 13.583 at
  R_i = 9.4287 (the verifier's matter edge 9.43, where m' falls below 1e-6 of its largest
  value) and 13.737 at R_i = 9.5 (the outermost shell of the table, nearly without mass).
  My upper end 13.737 differs from the verifier's 13.588 by more than the 0.01 I allowed:
  the difference is the definition of the matter edge, not a disagreement. Finding 2
  CONFIRMED: the sentence "a common bang time for every shell" is true for the core and the
  envelope, false in the surface taper (earlier bangs: a decaying mode there).
- **P3 holds.** M_0 = H^2 R_b^3/2 = 1.0 exactly, M/M_0 = 1.009588. In units of the total
  mass: tau_ta = 16.733, m_AH = 0.07974 (first trapped sphere) and 0.09511 (crunch),
  tau_AH = 43.928, R_b = 7.924, t_i = 10.565. Finding 3 CONFIRMED as a label defect; I relabel
  (the values stay in units of M_0, which is what the code and every journal use).
- **P4 holds (not blind).** wave 1 (-130256-a7374a4): 37 checks, failing T1.2b, T2.2d, T2.4a,
  T2.4c. Wave-2 full run (-161813-6c820fb): 40 checks, failing T2.6a-c (fixed in the T2
  rerun). State (T1, T3-T5 from the full run, T2 from -163358-9b2d048): 41 checks, 41 pass,
  diagnostics T1.2b-d, T2.2d-d, T2.4a-d, T2.4c-d. Finding 5 CONFIRMED.
- **P5 holds (not blind).** 9 of 14 scan points in [+2.2e-4, +6.3e-4]; outside: e0p1_h050
  -2.4e-4, e0p2_h050 -4.6e-4 (3.4e4 particles), e0p1_n064 +8.8e-4, e0p2_n064 +1.5e-3 (64^3),
  e0p2_pm +1.5e-3 (spindle). Section 4 item 2 of VERIFIER.md: the sentence is wrong as
  written (CONFIRMED), but the verifier's "only the four p = 0 points at 128^3" is too narrow
  (REBUTTED in part): the band holds every 128^3 point with >= 2.7e5 particles except the
  spindle, i.e. the four shapes at p = 0, the two amplitude copies, p = +0.2, the rotated
  lattice and the 2.1e6-particle point. Correct sentence for STATUS T3 / C8: "the 9 points at
  128^3 with >= 2.7e5 particles other than the spindle within +2.2e-4 to +6.3e-4; the spindle
  +1.5e-3; the 64^3 controls +8.8e-4, +1.5e-3; the 3.4e4-particle controls -2.4e-4, -4.6e-4".

## 2026-11-20T22:30Z, entry 3: outcome of P6, the integrity listing (run A-20261120-222620-0304d9d)

Run A-20261120-222620-0304d9d (`scripts/wave1_sha256.py`, commit 0304d9d, one core, exit 0),
over the 15 run directories of the note's run table (`note/scripts/common.py` RUNS, with the
wave-2 runs added for this package): **P6 holds.** Seven directories recorded no
`sha256sums.txt` (A-emd-pbh-20261115-120425-80492f8, -122117-aa1c84d, -130256-a7374a4,
-130402-f5566fb, -130609-947c898, -161813-6c820fb, -163358-9b2d048); their 55 files are
listed in `<run id>.sha256` in the run's directory, each hashed twice with equal results.
The eight directories with `sha256sums.txt` verify without a mismatch and list every file
they hold. Size and modification time of every file in all 15 directories are unchanged
before and after, and no file appeared or vanished. Figure `fig_integrity.png` looked at
(files per directory, blue verified, red listed now, no black bar); its legend text
overlaps the longest bar, which leaves the bar lengths readable, so the run is not
repeated for it.

What this does and does not establish [JUDGEMENT]: from 2026-11-20 on, any change of these
55 files is detected (the note's `common.py` now checks every input of a run without its
own record against this listing, `INTEGRITY_RUN`). It cannot show that the files are the
ones the wave-1 runs wrote on 2026-11-15; for that the verifier's mitigation stands (its own
reconstruction of data set 2t and its closed forms of the criteria agree with them).

## 2026-11-20T22:55Z, entry 4: corrections applied in the sources; prediction for the note's run

Applied (commit of this entry): `note/scripts/ledger.py` (a: median over mu <= 0.15 plus the
all-six median with its own label; c1: every "/M" of the scouting data now "/M_0", a row in
units of the total mass, the unit row and caption in Table V; c2: six names for six values;
d: wave-1 criteria row kept as "first check run", two wave-2 rows (24 of 24 with 1
diagnostic; T2 17 of 17 with 3), groups "Newtonian limit" (8 rows, analysis
A-emd-pbh-20261115-164420-4528861 and range -164757-b8bc9a3) and "First evolutions of the
scouting data" (10 rows, analyses A-20261115-182657-53da696 and
A-emd-pbh-20261115-163659-4dbacd0); g1: label of the 42.30; g3: breakdown named as the
first non-finite line output; g4: SR-2 turnaround labelled as three-point vertex and
estimator-dependent; g5: "the last with half the box"; three claims added for the wave-2 text
of `stage/G1/STATUS.md`; the ledger split into three table* floats, since one float no longer
fits a page). `note/scripts/common.py` (run table, integrity fallback). `note/scripts/
schem_dataflow.py` (the common.py box names the integrity listing). `note/main.tex` (b, c1
text, e, g2, d: abstract, intro, Sec. III A, III C, new Sec. IV C "Newtonian limit" and IV D
"First evolutions of the scouting data", IV E verifier sentence, IV F criteria state, Sec. V
runs named without numbers, summary, App. B checksum sentence and run list, data-flow
figure in App. B). `stage/G1/STATUS.md` (header, T2 wave-2 state, T3 band, section 3 units
and title, section 6 SR-1 breakdown criteria and SR-2 estimator). A dry compile in
`scratch/A-emd-pbh/tmp/g1close/texdry/` gave 12 pages and no float, reference or box
warning.

Prediction for the registered run of `run_all.py` (next): 7 of 7 scripts run cleanly; the
four data figures and the two older schematics equal the committed ones (same scripts, same
inputs; PNG rms within the stage tolerance); `schem_dataflow` differs only in the common.py
box; ledger 53 rows, 71 claims, 2 disagreements (the same two as before); every input checked
"sha256 ok" either against its run's record or against A-20261120-222620-0304d9d. Refuted by
a script failure, a changed data figure, or any other disagreement or checksum failure.

## 2026-11-21T02:58Z, entry 5: outcome of the note's run (A-20261120-223316-92c27f5); restart after the cut

The session of entry 4 was cut at 14:35 PST by the five-hour usage limit after it had run
the note's registered run, copied its outputs into `note/`, compiled the note, run the
manuscript checker and rendered the pages into `scratch/A-emd-pbh/tmp/g1close/pages/`, but
before it read the pages or committed. This session (restarted 18:54 PST) continues from
there; nothing of entries 1-4 is redone.

Outcome of the entry-4 prediction for run A-20261120-223316-92c27f5 (`run_all.py`, commit
92c27f5, two cores, 11 s, exit 0; `run.log` in its directory):
- Scripts: 8 of 8 ran cleanly. My count "7 of 7" was wrong (four data figures, three
  schematics, the ledger); no script failed, so the substance holds.
- Data figures and the two older schematics: the four `fig_*.png`, `schem_architecture.png`
  and `schem_timeline.png` are byte-identical to the committed ones; the four `fig_*.pdf`
  differ in 7-8 bytes (the creation date), the two `.svg` in their date and clip-path ids.
  Holds.
- `schem_dataflow.png` differs only in the common.py box ("inputs checked against
  sha256sums.txt or the integrity listing"); looked at now (Read): legible, no clipped box,
  the arrows as before. Holds.
- Ledger 53 rows; claims 71, 2 disagreements, the same two as before (JOURNAL.md:101 the
  4.3e-15 bound, JOURNAL.md:94 the 0.1 H overshoot). Holds.
- Every input "sha256 ok", eleven of them against the listing of A-20261120-222620-0304d9d.
  Holds.
- Every file of `note/figures/` and `note/tables/` equals the run's copy (cmp).

One more text change before the compile [JUDGEMENT]: Sec. V said the second ball "was
evolved through trapping"; whether a run reaches trapping is a result that has no registered
analysis in this note, so the sentence now says the runs went past the exact time of the
first trapped sphere (run A-20261119-144419-13d5601 to t = 16 against the exact 9.55 of
data set 3, `runs_ball/README.md` "Wave 2b").

Prediction for the compile and check (P8, made concrete): `latexmk` gives 12 pages, 0
undefined references or citations, 0 overfull boxes; `check_manuscript.py --compile` with the
guide's `--forbid` list has candidates only under 5.5 (run ids in the ledger appendix and its
tables) and 5.8 (scripts the guide's exception names, plus `schem_dataflow.py`, which the
exception does not yet name); every caption within five typeset lines. Refuted by an
undefined reference, an overfull box, a 5.5/5.8 hit in the main text or a caption before
the appendix, or a caption past five lines on the rendered page.

## 2026-11-21T03:12Z, entry 6: outcome of the compile and page reading; text fixes; prediction for a second note run

**P8 outcome (compile and check, before the fixes below).** `latexmk`: 12 pages, 0 undefined
references or citations, 0 overfull boxes. `check_manuscript.py --compile` with the guide's
`--forbid` list: candidates only under 5.5 (47, all in the ledger appendix and its tables) and
5.8 (28, all in scripts: `ledger.py` 13, `schem_dataflow.py` 9, `handreg.py` 4,
`run_all.py` 2); no hit in the main text or a caption before the appendix. Captions within
five lines on the rendered pages. P8 holds. Every page read (pages 1-12 at 110 dpi).

Found by reading the pages, and fixed in `main.tex` [JUDGEMENT]:
- Abstract "A verifier ... recomputed every number of the note" and Sec. IV E "every computed
  number of the ledger ... It confirmed every value": too wide. VERIFIER.md section 2 left
  aside the predicted card-hours (2.1, NOT CONFIRMED), the four cross-check differences
  (2.1, "transcription ... not re-run"), and of the wave-2 rows now in Table IV the
  tracked-particle residuals, |H| at t = 20, the two central-lapse rows and the compactness
  on the axes (not in its 2.4; "Not recomputed: the horizon statements"). The abstract and
  Sec. IV E now say so, and App. B names these rows.
- App. B: a run-id suffix ("-155056-ec1b816") broke after its leading hyphen; the six
  suffixes are kept in one box (`\mbox`), two lines of that paragraph are now loose
  (underfull), which reads acceptably.
- Sec. III B "is the set of the threshold line" -> "set-up".
- Fig. 6 (timeline) showed "now: wave 2; G0 and G1 judged together" with the marker before
  G0, stale since G0 passed on 2026-11-19 (`coord/GATES.md` line 8). `schem_timeline.py` now
  marks "now: wave 3 of the program; G0 passed, G1 at its review" just after G1, and the
  bracket G1 -> G2 names what G2 needs after wave 2 (a slicing that reaches trapping, a
  resolved first trapped sphere, convergence runs), as in note Sec. V. Dry render in
  `scratch/A-emd-pbh/tmp/g1close/tl_dry/` looked at.

Prediction for the second registered run of `run_all.py` (P10): 8 of 8 scripts clean; every
output byte-identical to the run A-20261120-223316-92c27f5 except `schem_timeline.{png,svg}`
(the change above) and the PDF/SVG dates; ledger 53 rows, 71 claims, the same 2
disagreements; all inputs "sha256 ok". After the copy the note compiles to 12 pages with 0
undefined references and 0 overfull boxes. Refuted by any other changed output or a new
disagreement.

## 2026-11-21T03:20Z, entry 7: outcome of P10 (run A-20261121-030037-3f015fa)

Run A-20261121-030037-3f015fa (`run_all.py`, commit 3f015fa, two cores, exit 0, finished by
nrpic-run): **P10 holds.** 8 of 8 scripts clean; against the previous run every PNG and
every table is byte-identical except `schem_timeline.png` (the intended change; the
committed PNG looked at in the dry render and again on page 8); PDFs differ in 4-5 bytes
(dates), SVGs in dates and ids; ledger 53 rows, 71 claims, the same 2 disagreements; 23
inputs "sha256 ok". Outputs copied into `note/`; App. B names this run. Compile: 12 pages,
0 undefined references or citations, 0 overfull boxes; checker hits only in the appendix
and the scripts. Pages 1-8 read again after the reflow (9-12 hold Fig. 7, the references and
the unchanged ledger tables, read in entry 6).
