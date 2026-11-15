# note: working note v0 of Track A (gate G0)

Helper package of A-emd-pbh, wave 2 (2026-11-15). The REVTeX working note of S1 (primordial
black holes from collisionless collapse in an early matter era), its figures and schematics,
the numerical ledger, and a check of the lead's documents against the run outputs.
Predictions and outcomes: `JOURNAL.md`. Guide and notation of the note (paper-writing
skill, one level above the manuscript): `../WRITING_GUIDE.md`, `../NOTATION.md`.

## What is here

| Path | Content |
|---|---|
| `main.tex`, `references.bib`, `main.pdf` | the note (REVTeX 4.2, two columns) and its compiled pages |
| `figures/fig_*.{pdf,png}` | data figures, each made by `scripts/<same name>.py` from registered run outputs |
| `figures/schem_*.{png,svg}` | the two schematics of the stage check (architecture, timeline), `paperfig.py` |
| `tables/ledger.tex` | the ledger appendix: every number of the note with its run id (written by `scripts/ledger.py`) |
| `tables/claims.md`, `tables/claims.json` | numbers stated in the lead's documents checked against the files (written by `scripts/ledger.py`) |
| `scripts/common.py` | the run ids the note reads; every input checked against its run's `sha256sums.txt` |
| `scripts/run_all.py` | runs every `fig_*`, `schem_*` and `ledger.py` into one directory (the registered run) |
| `scripts/czstyle.py`, `scripts/paperfig.py` | unchanged copies of `harness/style/` |

## How to rerun

From the worktree root, with the worktree environment (`harness/bin/nrpic-env create --no-kokkos`):

    harness/bin/nrpic-run submit --kind scouting --gate G0 --package tracks/A-emd-pbh/note \
        --purpose "note v0: figures, schematics, ledger" -- \
        .venv/bin/python tracks/A-emd-pbh/note/scripts/run_all.py
    # copy <run dir>/figures/* to note/figures/ and <run dir>/tables/* to note/tables/, then
    cd tracks/A-emd-pbh/note && latexmk -pdf main.tex

Each figure script also runs alone (`python scripts/fig_landscape.py`, output to
`figures/`), which is what `harness/bin/nrpic-stage verify` does.

## Requests

(filled in at the end of the session)
