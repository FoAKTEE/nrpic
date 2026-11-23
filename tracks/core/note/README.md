# note: working note of core for gate G2

The REVTeX working note of the shared implementation (`main.tex`, `main.pdf`, 8 pages):
what the base coupling is, what releases core-v0.3 to core-v0.6 added, the verification
ladder of the brief (section 10, rows marked CORE) row by row with its evidence and what
is partial, the known limits scheduled for core-v0.7, and the numerical ledger (every
number with its registered run or source locator, and the claim of the fresh verifier,
`../stage/G2/VERIFIER.md`, that recomputed it). Guide and notation (paper-writing skill,
one level above the manuscript): `../WRITING_GUIDE.md`, `../NOTATION.md`. Written in
batch 8 (2026-11-21, session core-lead-8); predictions and outcomes in
`../JOURNAL.md` (entry of 23:16Z, Q2).

## What is here

| Path | Content |
|---|---|
| `main.tex`, `references.bib`, `main.pdf` | the note (REVTeX 4.2, `aps,prd,twocolumn`) |
| `figures/schem_architecture.{png,svg}` | architecture by release (base, v0.3, v0.4, v0.5-v0.6, open for v0.7) and the gate timeline, `paperfig.py` |
| `figures/fig_geodesic.*` | ladder row 1: invariants along the Kerr passage, order in dt (regression G, core-20261115-065452-3629622) |
| `figures/fig_collapse.*` | rows 2 and 3: horizon mass of the dust collapse (pre-program reference `runs/os/nocap_sc`; regression O, core-20261115-065901-3629622) and of the prolate collapse (`runs/prolate/e09_v8`; core-20261115-152845-5728b1d) |
| `figures/fig_clusters.*` | row 4: central lapse of the five models (pre-program `runs/st/*`) and of the M/4 bisection (core-20261115-152842/-152843-5728b1d, -154726-37450f2, -155617-06f844b) |
| `tables/ledger.tex`, `tables/ledger.json` | the ledger of Appendix A (103 rows, 70 recomputed by the fresh verifier) |
| `tables/runinfo.tex` | the id of the run that made figures and tables |
| `scripts/common.py` | run ids, readers; every input checked against the sha256 its run recorded (registered runs with `sha256sums.txt`; pre-program files against the inventory core-20261121-231825-135474c) |
| `scripts/fig_*.py`, `scripts/schem_architecture.py`, `scripts/ledger.py`, `scripts/run_all.py` | one script per figure, the ledger, the driver |
| `scripts/figstyle.py`, `scripts/paperfig.py` | unchanged copies of `harness/style/` |

`fig_geodesic.py` imports `analysis/geodesic/geo_common.py`; `common.py` imports
`cosmo/ic/nrp_io.py` (both of this repository, unchanged).

## Registered runs of this package

| Run | What | Outcome |
|---|---|---|
| core-20261121-231825-135474c | inventory of the pre-program run directories of ladder rows 2-4 (`../verify/preprogram/`) | completed; Q1 held for inputs, executables, logs, histories; failed as written for horizon summaries where no finder ran |
| core-20261121-232757-f86d965 | figures, schematic, ledger (`scripts/run_all.py`) | completed; Q2 (a)-(c) held; 11 inputs sha256 ok, 31 without a recorded checksum (wave-1 runs whose manifests list no outputs) |
| core-20261121-232936-d979f1c | the same after the ledger escapes `<` and `>` (read on page 8) | completed; the three numbers files byte-identical to the run before; only two ledger lines differ; **these outputs are in `figures/` and `tables/`** |

## How to rerun

From the worktree root, with the worktree environment, after committing:

    harness/bin/nrpic-run submit --kind scouting --gate G2 --launcher local --cores 1 \
        --purpose "core working note G2: figures and ledger" -- \
        python3 tracks/core/note/scripts/run_all.py '$NRPIC_RUN_DIR'
    # copy <run dir>/figures/* to note/figures/ and <run dir>/tables/* to note/tables/
    cd tracks/core/note && latexmk -pdf main.tex
    python3 ~/.claude/skills/synced/<id>/paper-writing/scripts/check_manuscript.py --main main.tex \
        --forbid 'NRPIC|nrpic|wt/core|scratch|Track [A-F]|batch [0-9]' --compile

## Checker (paper-writing Sec. 8), last run batch 8

0 undefined references, 0 undefined citations, 0 overfull boxes. Remaining candidates
are accepted exceptions of `../WRITING_GUIDE.md`: run ids, locators and paths in the
ledger appendix and in `scripts/` (5.5, 5.8; program rule 4); the y_c labels of the
cluster models (4.3, labels); one negation and one "defects" heading in the ledger
appendix. All 8 pages read. Step 4 of the story-first procedure (reviewer subagents)
was not run (no subagent tool in the session).
