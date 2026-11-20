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
