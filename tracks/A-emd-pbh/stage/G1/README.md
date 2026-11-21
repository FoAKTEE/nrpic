# stage/G1 of A-emd-pbh

The stage package of gate G1 (decision 0012) and, beside it, the independent verifier of
wave 2b (checklist items C18 and C11).

## What is here

| Path | Content | Written by |
|---|---|---|
| `STAGE_REPORT.md`, `CHECKLIST.md`, `EVIDENCE.md`, `OPEN.md`, `STATUS.md`, `REVIEW.md`, `VERIFY`, `VERIFY_RESULTS.*` | the package documents of the gate | lead of A-emd-pbh (wave 2) |
| `VERIFIER.md` | verifier's report: verdict per number of the note's ledger, the criteria checks, the Newtonian-mode results and the expanding-ball comparison; comparison with the track's own review (section 4); C11 | verifier (wave 2b) |
| `JOURNAL.md` | verifier's predictions (entry 1, committed before any run) and outcomes | verifier |
| `verifier/` | `v_ledger.py`, `v_criteria.py`, `v_newton.py`, `v_ball.py` (own recomputations), `vcommon.py` (paths, checksum checks), `run_all.py` (driver) | verifier |
| `figs/` | PNG copies of the verifier's figures from run A-20261119-142905-c813c01 | verifier |

Also written by the verifier, outside this directory: `note/scripts/schem_dataflow.py` and
`note/figures/schem_dataflow.{png,svg}` (C11, run A-20261119-143347-37240f3).

## How to rerun the verification

From the worktree root, with the worktree environment (`harness/bin/nrpic-env create
--no-kokkos` if `.venv` is missing):

    harness/bin/nrpic-run submit --kind scouting --gate G1 --cores 4 \
        --package tracks/A-emd-pbh/stage/G1 --package tracks/A-emd-pbh/note/scripts \
        --purpose "G1 verifier rerun" -- .venv/bin/python tracks/A-emd-pbh/stage/G1/verifier/run_all.py

About four minutes on four cores. Each part writes `<part>/<part>.json` (rows: item, claim,
mine, verdict, how), its figures and a log into the run directory. A part also runs alone:
`.venv/bin/python tracks/A-emd-pbh/stage/G1/verifier/v_newton.py --out DIR`. Inputs are read
from `scratch/A-emd-pbh/<run id>/` of the runs named in each script and checked against the
run's `sha256sums.txt` where it exists; the paper sources from `kb-data/raw/arxiv/`.

The schematic alone: `.venv/bin/python tracks/A-emd-pbh/note/scripts/schem_dataflow.py
[--out DIR]` (default `note/figures/`).

## State (2026-11-19)

Done: C18 recomputation (ledger 39 of 42 confirmed, 1 not recomputed, 2 wrong; criteria 19
of 19; Newtonian mode 17 of 17; expanding ball 12 of 12, the SR-2 turnaround
estimator-dependent); C11 schematic drawn and looked at. Not done: the periodic box, the L4
and LTB checks of criteria2, the Monte Carlo checks of the criteria (T1.3-T1.6, T5.2-T5.3),
the cost model, the horizon and gauge-pathology statements of runs_ball (outside C18 as given).
No card-hours used.

## Requests

- **Lead of A-emd-pbh** (VERIFIER.md findings 1-7 and section 4):
  1. ledger row "read-off collapse time over top-hat time ... median": 0.86 is over all six
     read-offs; over mu <= 0.15 it is 0.84 (fix the label or the number; source
     `scope/scope_calc.py` key `median_ratio`);
  2. note Sec. III A "a common bang time for every shell": not true in the surface taper
     (bang times 10.667-13.588 for 6.5 <= R < 9.43);
  3. Tables V and VI: masses, radii and times are in code units (nominal mass 1), not in
     units of the total M = 1.0096 the labels name;
  4. ledger label "hoop, ball, hoop, peak, ..." has eight names for six values;
  5. update the note (criteria state 41 of 41; Sec. V: runs done) and STATUS T2;
  6. STATUS T3 / CHECKLIST C8 "14 scan points within 2.2e-4 to 6.3e-4": only the four p = 0
     points at 128^3 are in that band;
  7. runs_ball R2 for SR-2: re-judge with a window-independent turnaround estimator (the
     three-point vertex gives +0.031 M, wider windows +0.009 to +0.025 M);
  8. record checksums of the wave-1 output directories (or rerun their producers through
     `nrpic-run`) before G2; App. B's checksum sentence holds only for runs with
     `sha256sums.txt`;
  9. include `note/figures/schem_dataflow.png` in the note and judge C11 and C18 in
     `CHECKLIST.md`.
- **core**: `docs/FORMATS.md` line 122 describes `.trajmet.bin` records as 12 values; the code
  (`athenak/src/particles/nrpic_io.cpp:811`) and `coord/INTERFACES/diagnostics.md` section 6
  write 17 (with the particle's proper time, E and S_i).

## Close-out, wave 3 (g1close helper of A-emd-pbh, 2026-11-20)

The verifier's corrections were checked at their sources (run A-20261120-222454-d16dbc6),
then applied or rebutted; details and predictions in `../../g1close/JOURNAL.md`. The
verifier's own files (`VERIFIER.md`, `JOURNAL.md`, `verifier/`, `figs/`) are unchanged.

| Verifier locator | Outcome | Changed | Commit |
|---|---|---|---|
| finding 1 (median 0.86) | confirmed: 0.84 over mu <= 0.15, 0.86 over all six | ledger row prints both, labelled | 2c115cb1 |
| finding 2 (common bang time) | confirmed: common to 1.2e-14 for R_i < 6.5; in the taper the age rises to 13.58 at the matter edge 9.43 (13.74 at R_i = 9.5) | note Sec. III A | 2c115cb1 |
| finding 3 (units of M) | confirmed as a label defect | unit M_0 defined; "/M_0" throughout; a row in units of the total mass; STATUS section 3 | 2c115cb1 |
| finding 4 (eight names) | confirmed | six names | 2c115cb1 |
| finding 5 (stale state) | confirmed: 41 of 41, 4 diagnostics | note Secs. IV C, IV D, IV F, V; ledger groups; STATUS T2 | 2c115cb1 |
| finding 6 (SR-2 turnaround estimator) | not re-judged here (runs_ball helper) | note and STATUS section 6 quote it as the three-point-vertex value, estimator-dependent, no pass/fail | 2c115cb1 |
| finding 7 (wave-1 checksums) | listing of 55 files in run A-20261120-222620-0304d9d, 0 mismatches elsewhere | `note/scripts/common.py` checks against it; App. B sentence | 0304d9d9, f26e7f58, 2c115cb1 |
| 2.1 (42.30 vs 42.36) | label | "light speed R_i/R, without the conformal factor" | 2c115cb1 |
| 2.5 ("an order of magnitude") | confirmed loose | "several times below the hoop line" | 2c115cb1 |
| 3.2 (half box at M/4) | confirmed | no convergence order quoted; ledger "the last with half the box" | 2c115cb1 |
| 4.2 (STATUS T3 / C8 band) | wrong as written; the replacement "only the four p = 0 points" too narrow: 9 of 14 points lie in the band | STATUS T3, CHECKLIST C8 | 2c115cb1, 8f681d68 |
| 4.5 (SR-1 breakdown criteria) | confirmed | criterion named in STATUS section 6 and the ledger | 2c115cb1 |
| C11 | schematic in the note | Fig. 7 with caption, App. B | 2c115cb1 |

Also: note v1 regenerated in runs A-20261120-223316-92c27f5 and A-20261121-030037-3f015fa,
compiled (12 pages, 0 undefined references, 0 overfull boxes), checked, every page read; the
abstract, Sec. IV E and App. B state which rows the verifier left aside; the timeline shows
the wave-3 state (3f015fa0, 8b7304f5). Package: `nrpic-stage collect` (19 of 20 items kept),
C7, C8, C11, C16, C17, C18, C20 judged, EVIDENCE.md, OPEN.md (8f681d68); `nrpic-stage
verify --no-checksums` and `report` (last commit of the package). The full `verify` with
output checksums was stopped by my 15-minute limit while hashing about 80 GB of the wave-2b
card outputs (runs A-20261119-144419-13d5601, -164634-f1fe887); those runs record their
checksums at finish, and `harness/bin/nrpic-run verify <run id>` checks one run.

**For the lead: ready for gate review once the lead has rewritten the owner's STATUS.md,
JOURNAL.md and HANDOFF.md (C20) and decided C18 (PASS on the verifier's scope; five new
Table IV rows not recomputed by a fresh verifier, OPEN.md item 2).** The remaining `verify`
failures (`clean`, `runs`) come from other helpers' work in progress in this worktree
(OPEN.md, last section).
