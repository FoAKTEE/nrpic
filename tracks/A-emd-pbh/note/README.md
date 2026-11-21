# note: working note of Track A (v0 at gate G0, v1 at gate G1)

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
| `scripts/handreg.py` | registers and runs a local run by hand when `nrpic-run` refuses (manifest with the template's fields, `sha256sums.txt`) |
| `tables/parameters.tex`, `tables/claims_summary.tex` | the parameter table and the claims sentence of the note (written by `scripts/ledger.py`) |
| `scripts/czstyle.py`, `scripts/paperfig.py` | unchanged copies of `harness/style/` |

## How to rerun

From the worktree root, with the worktree environment (`harness/bin/nrpic-env create --no-kokkos`):

    harness/bin/nrpic-run submit --kind scouting --gate G0 --package tracks/A-emd-pbh/note \
        --purpose "note v0: figures, schematics, ledger" -- \
        .venv/bin/python tracks/A-emd-pbh/note/scripts/run_all.py
    # if nrpic-run refuses (an untracked file elsewhere in the worktree), the same by hand:
    .venv/bin/python tracks/A-emd-pbh/note/scripts/handreg.py --purpose "..." --refusal "<message>" -- \
        .venv/bin/python tracks/A-emd-pbh/note/scripts/run_all.py
    # copy <run dir>/figures/* to note/figures/ and <run dir>/tables/* to note/tables/, then
    cd tracks/A-emd-pbh/note && latexmk -pdf main.tex

Each figure script also runs alone (`python scripts/fig_landscape.py`, output to
`figures/`), which is what `harness/bin/nrpic-stage verify` does.

## State (2026-11-20, working note v1, gate G1)

Note v1 (12 pages): the corrections of the G1 verifier (`../stage/G1/VERIFIER.md`) applied,
the wave-2 state (criteria 41 of 41, Newtonian limit, first evolutions of the scouting data,
the runs made since named in Sec. V without numbers), the data-flow schematic as Fig. 7 in
App. B, the ledger in three tables. Made by the G1 close-out helper (`../g1close/`, journal
entries 4-6). Figures, schematics and tables from run A-20261121-030037-3f015fa (the
previous pass A-20261120-223316-92c27f5 differs only in the timeline); inputs without a
`sha256sums.txt` of their own are checked against the integrity listing of run
A-20261120-222620-0304d9d (`scripts/common.py`, `INTEGRITY_RUN`). Checker
(`check_manuscript.py --compile` with the guide's `--forbid` list): 0 undefined references,
0 overfull boxes, hits only in the ledger appendix and in the scripts; `schem_dataflow.py`
names the track's files, which the guide's exception 1 does not yet list (request to the
lead in `../g1close/README.md`). Every page read.

## State (2026-11-15)

Done: note v0 (9 pages, compiled, checker clean but for the accepted ledger exception), four
data figures and two schematics, each looked at; ledger and parameter table generated from
registered runs; claims check (68 numbers, two differences); `stage/G0/STAGE_REPORT.md`
from `nrpic-stage report`, with the disagreements and what closes G0. Registered runs:
A-20261115-161054-50848b1, A-20261115-161720-6ae975e (nrpic-run), A-20261115-161947-09324e1
(by hand; the committed outputs). Not done: the paper-writing reviewers of a new paper
(step 4), a verifier recomputation of the note's ledger.

## Requests

- To the lead of A-emd-pbh: (1) decide whether `stage/G0/VERIFIER.md` of the wave-2 verifier
  stands for `VERIFIER_REPORT.md` (C18) and write the "Decision requested" paragraph of
  `STAGE_REPORT.md` (a draft is at its end); (2) correct `JOURNAL.md:94` / `SCOPE.md` 10.3 /
  `RISKS.md` row 11 (the edge deviation of the table cubic is 1.37 H as recorded, not an
  overshoot of 0.1 H) and `JOURNAL.md:101` (4.33e-15); (3) rewrite STATUS/HANDOFF for wave 2
  (C20; budget line); (4) add `cd tracks/A-emd-pbh/note/scripts && python ledger.py` to a
  `stage/G0/VERIFY` command list so that `nrpic-stage verify` also regenerates the ledger and
  the claims check; (5) when the wave-2 runs finish (SR-1/SR-2, periodic S1/S2, Newtonian
  campaign), rerun `scripts/run_all.py` and extend the note's Sec. IV.
- To orch: `harness/bin/nrpic-run submit --package DIR` still refuses when any untracked file
  exists outside `tracks/` (here `peak.horizon_summary_0.txt`, written into the worktree root
  by another helper's AthenaK run, whose working directory is the worktree root); either
  ignore untracked files outside the package and the shared code, or have runs never write
  into the worktree root. Run A-20261115-161947-09324e1 was registered by hand for this reason.
- To the helper whose runs write `peak.*` files (by the name, probably `periodic_threshold`; through the lead): the horizon finder's summary file
  `peak.horizon_summary_0.txt` lands in the worktree root; set the run's working or output
  directory under `scratch/`.
- To kb: the key references are still raw-store locators only (C2 of G0 stays FAIL).
