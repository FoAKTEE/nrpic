# note: working note v0 of C-sidm (gate G0)

Helper package of C-sidm, wave 2 (2026-11-15). The REVTeX working note of S3 (relativistic
collapse of a self-interacting dark-matter core), its figures and schematics, the numerical
ledger, and a check of the lead's stage documents against the run outputs. Predictions and
outcomes: `JOURNAL.md`. Guide and notation of the note (paper-writing skill, one level above
the manuscript): `../WRITING_GUIDE.md`, `../NOTATION.md`. The package also wrote
`../stage/G0/STAGE_REPORT.md` and filled the wave-2 items of `../stage/G0/CHECKLIST.md`.

## What is here

| Path | Content |
|---|---|
| `main.tex`, `references.bib`, `main.pdf` | the note (REVTeX 4.2, two columns, 10 pages) and its compiled pages |
| `figures/fig_*.{pdf,png}` | four data figures (Knudsen numbers, equilibrium sequences, collision references and kernel test, AthenaK collisionless box), each made by `scripts/<same name>.py` from registered run outputs |
| `figures/schem_*.{png,svg}` | the two schematics of the stage check (architecture with exists / to be ported / new; stage timeline), `paperfig.py` |
| `tables/ledger.tex` | the two ledger tables of the appendix: every number of the note with its run id |
| `tables/parameters.tex` | the parameter table (models at the instability criteria) |
| `tables/claims.md`, `tables/claims.json`, `tables/claims_summary.tex` | 23 numbers of the lead's stage documents checked against the files: 20 agree, 3 differ (below) |
| `scripts/common.py` | the run ids the note reads; every input checked against the sha256 its run recorded (`sha256sums.txt`, or the output list of a wave-1 manifest) |
| `scripts/fig_*.py`, `scripts/schem_*.py`, `scripts/ledger.py` | one script per figure; the ledger, parameter table and claims check |
| `scripts/run_all.py` | runs all of them into one directory (`$NRPIC_RUN_DIR` of a registered run) and writes its `sha256sums.txt` |
| `scripts/czstyle.py`, `scripts/paperfig.py` | unchanged copies of `harness/style/` (sha256 equal to `harness/style/SHA256SUMS`) |

`fig_box_step.py` imports the track's readers and references from `../collide/analysis/`
(`snap.py`) and `../collide/REFERENCES/` (`mj.py`, `conduction.py`).

## How to rerun

From the worktree root, with the worktree environment (`harness/bin/nrpic-env create --no-kokkos`):

    harness/bin/nrpic-run submit --kind scouting --gate G0 --package tracks/C-sidm/note --cores 1 \
        --purpose "note v0: figures, schematics, ledger" -- \
        .venv/bin/python tracks/C-sidm/note/scripts/run_all.py
    # copy <run dir>/figures/* to note/figures/ and <run dir>/tables/* to note/tables/, then
    cd tracks/C-sidm/note && latexmk -pdf main.tex
    python3 <paper-writing skill>/scripts/check_manuscript.py --main main.tex --compile \
        --forbid 'nrpic_cf|nrpic_geodesic|tmb\.py|evstatic|make_box|an_step|nrpic-run|athinput|F21|G26|core-v0|C-pre|anta|A100'

Each figure script also runs alone (`python scripts/fig_sequences.py`, output to
`figures/`), which is what `harness/bin/nrpic-stage verify` does. About 20 s on one core.

## Registered runs of this package

| Run | What | Outcome |
|---|---|---|
| C-20261115-170415-385069e | N1: figures, schematics, ledger, claims (first layout) | completed; predictions P1-P6 held (`JOURNAL.md`) |
| C-20261115-171741-0e0da67 | N2: the same after layout changes (ledger in two tables, frameless legends, schematic subtitle) | completed; every number identical to N1; these outputs are in `figures/` and `tables/` |

Draft runs of the four data figures went to `scratch/C-sidm/tmp/notefig/` for layout only (not
registered, not used).

## State (2026-11-15)

Done: note v0 (10 pages, compiled with latexmk, every page read), checker clean in the main
text (remaining hits: run ids and file names in the ledger appendix and the scripts, accepted
by exception 1 of the guide; one overfull box of 1 pt in the parameter table); four data
figures and two schematics, each PNG opened; ledger and parameter table from registered runs;
claims check; `stage/G0/STAGE_REPORT.md` from `nrpic-stage report`.

Not done: the reviewer step of the paper-writing procedure for a new paper (300- and 1000-word
versions read by first-year-student reviewers, Sec. 10 of the skill); a fresh-context
verifier of the note's own ledger (the wave-2 G0 verifier works on the scoping claims in
`../stage/G0/verifier/`); the collisional box tests and cluster runs that other helpers are
running now are not in the note (their runs were still running when it was written).

Differences between the lead's documents and the files (the files win; `tables/claims.md`):
1. `stage/G1/STATUS.md` item 2: "Table 1 ... all columns within 1.1e-4 relative except R":
   run C-sidm-20261115-120722-38ab057 has B at 2.43e-4 and eps, ec0 at 1.3e-4 (row
   `main.tex:503`, w0 = 4.5); the bound holds for E and E_rest only.
2. `stage/G0/REPORT.md` section 1: "every phase ... lasts at least 1e5 dynamical times":
   run C-sidm-20261115-121412-d463e1a gives a lower bound of 8.5e4 for the fastest phase.
3. `stage/G0/REPORT.md` section 3: thermal-core models Z(0) = 0.40-0.80 have "R/M = 20-26,
   r_core/M = 1.5-2.1": run C-sidm-20261115-121748-4e8d6b5 gives 19.8-28.1 and 1.27-2.56
   (the quoted ranges fit narrower ranges of Z(0)); the lapse range agrees.
4. Not counted as a difference: `STATUS.md` "three independent solvers agree to 3e-8": the
   King comparison is 3.5e-8 (run C-sidm-20261115-131130-3077a99, X3).
5. Locator: `stage/G0/REPORT.md` section 6 puts the 200 M_sun black hole of arXiv:2601.17117
   at `SIDM_MS.tex:476`; the statement is at line 481 (476 holds the strong-gravity
   discussion), and the 3e-8 fraction at line 68.

## Requests

- To the lead of C-sidm: (1) correct the three numbers above in `stage/G1/STATUS.md` item 2
  and `stage/G0/REPORT.md` sections 1, 3 and the locator of section 6; (2) write the
  "Decision requested" paragraph of `stage/G0/STAGE_REPORT.md` (a draft is there) and decide
  whether the wave-2 verifier's `stage/G0/VERIFIER.md` stands for `VERIFIER_REPORT.md`
  (checklist C18); (3) rewrite STATUS/HANDOFF for wave 2 (checklist C20 is OPEN); (4) once
  the box tests and the first cluster runs finish, rerun `scripts/run_all.py` with new figure
  scripts for them and extend Sec. IV of the note.
- To orch: `nrpic-run submit` refuses while other helpers of the same owner hold the 16
  cores of the allotment, even for a one-core, twenty-second analysis run; N2 waited about
  ten minutes in a retry loop. A small reserve for short analysis runs (or a queue) would help.
- To kb: unchanged from wave 1 (key references are raw-store locators only; checklist C2).
