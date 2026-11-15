# note: working note v0 of Track B (gate G0)

Helper package of B-emd-gw, wave 2 (2026-11-15). The REVTeX working note of S2
(gravitational waves from structure formation in an early matter era), its data figures and
the two schematics of the G0 stage check, the numerical ledger, a check of the numbers in the
lead's stage documents against the run outputs, and `stage/G0/STAGE_REPORT.md`. Predictions
and outcomes: `JOURNAL.md`. Guide and notation of the note (paper-writing skill, one level
above the manuscript): `../WRITING_GUIDE.md`, `../NOTATION.md`.

## What is here

| Path | Content |
|---|---|
| `main.tex`, `references.bib`, `main.pdf` | the note (REVTeX 4.2, two columns) and its compiled pages |
| `figures/fig_*.{pdf,png}` | data figures, each made by `scripts/<same name>.py` from registered run outputs |
| `figures/schem_*.{png,svg}` | the two schematics of the stage check (architecture, timeline), `paperfig.py` |
| `tables/ledger.tex` | the ledger appendix: every number of the note with its run id |
| `tables/parameters.tex` | the parameter table of the scenarios |
| `tables/claims.md`, `tables/claims.json`, `tables/claims_summary.tex` | numbers of the lead's documents checked against the files; the sentence the note prints |
| `tables/checked.md` | every file the scripts read, its run, its checksum check, and whether it equals the copy committed by its package |
| `scripts/common.py` | the run ids the note reads; checksum checks against `sha256sums.txt` or the manifest's `outputs_sha256` |
| `scripts/run_all.py` | runs every `fig_*`, `schem_*` and `ledger.py` into one directory (the registered run) |
| `scripts/czstyle.py`, `scripts/paperfig.py` | unchanged copies of `harness/style/` |

## How to rerun

From the worktree root, with the worktree environment (`harness/bin/nrpic-env create --no-kokkos`):

    harness/bin/nrpic-run submit --kind scouting --gate G0 --package tracks/B-emd-gw/note \
        --purpose "note v0: figures, schematics, ledger, claims check" -- \
        .venv/bin/python tracks/B-emd-gw/note/scripts/run_all.py
    harness/bin/nrpic-run finish <run_id>
    # copy <run dir>/figures/* to note/figures/ and <run dir>/tables/* to note/tables/, then
    cd tracks/B-emd-gw/note && latexmk -pdf main.tex
    python3 <paper-writing skill>/scripts/check_manuscript.py --main main.tex --compile \
        --forbid 'gw_diag|gwdiag|periodic_z4c|verify_cosmo|first_source|make_east|nrpic_cosmo|z4c_linear_wave|athinput|pm\.py|nrpic-run|anta|A100|Slurm'

If `nrpic-run` refuses, `python scripts/run_all.py <dir>` writes the same outputs and a
`sha256sums.txt` into `<dir>` for a manifest written by hand. Each figure script also runs
alone (`python scripts/fig_pancake.py`, output to `figures/`), which is what
`harness/bin/nrpic-stage verify` does.

## State (2026-11-15)

See the end of `JOURNAL.md` for the outcomes and the registered run. Not done in this
package: the reviewer subagents of step 4 of the paper-writing procedure for a new paper
(no subagent tool in this session), an independent verifier's recomputation of the ledger
(`stage/G0/VERIFIER_REPORT.md`, owed by a fresh agent).

## Requests

See the end of `JOURNAL.md` (section "Requests"), repeated here when the package closes.
