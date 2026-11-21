# note: working note v1 of Track D (gates G0 and G1)

Helper package of D-bh-dress. The REVTeX working note of S4 (black-hole growth in an
expanding collisionless medium, the dark-matter dress, the null test of cosmological
coupling), its figures and schematics, the numerical ledger, and a check of the lead's
documents against the run outputs. Predictions and outcomes: `JOURNAL.md` (P1-P6 wave 2,
P7-P15 wave 3). Guide and notation (paper-writing skill, one level above the manuscript):
`../WRITING_GUIDE.md`, `../NOTATION.md`. No simulation is run here: every script reads
outputs of registered runs (`scripts/common.py` lists them).

## What is here

| Path | Content |
|---|---|
| `main.tex`, `references.bib`, `main.pdf` | the note v1 (REVTeX 4.2, two columns, 18 pages, state of 2026-11-21) and its compiled pages |
| `figures/fig_*.{pdf,png}` | data figures, each made by `scripts/<same name>.py` from registered run outputs (table below) |
| `figures/fig_*_numbers.json` | the numbers each figure script derived (read by `ledger.py`) |
| `figures/schem_*.{png,svg}` | architecture schematic (G1 item C9) and stage timeline, `paperfig.py` |
| `tables/ledger.tex` | the ledger appendix: every number of the note with its run id (six tables) |
| `tables/parameters.tex` | the parameter table of the note |
| `tables/claims.md`, `tables/claims.json` | 76 statements of the lead's and the packages' documents checked against the run outputs (66 agree, 10 remarks) |
| `scripts/common.py` | the run ids the note reads; inputs checked against each run's `sha256sums.txt` where it has one |
| `scripts/run_all.py` | runs every `fig_*`, `schem_*` and `ledger.py` into one directory (the registered run) |
| `scripts/handreg.py` | registers a run by hand when `nrpic-run` refuses (wave 2 only) |
| `scripts/czstyle.py`, `scripts/paperfig.py` | unchanged copies of `harness/style/` |

Figures and the runs they read (all drawn by the run of every script
D-20261121-130510-7e14c5f, whose outputs are the committed ones):

| Figure | Reads |
|---|---|
| `schem_architecture` (C9: exists / provided by core / new; run chain) | nothing (sources named in its docstring) |
| `schem_timeline` (G0 passed; G1 open for the infall criterion and this note) | nothing |
| `fig_es`, `fig_constraints`, `fig_floor`, `fig_spike`, `fig_infall` | wave-1 runs of `common.py` (unchanged since v0) |
| `fig_kerr` (Kerr spike against FdRW; AthenaK stationarity) | D-bh-dress-20261115-171615-8adbbdd, -172611-1e40191, -172646-ed6a510, -174954-786ddcc |
| `fig_newton` (Newtonian-mode growth and profile) | D-20261115-171503-4262f03, -171505-62940f4, -171507-d1058a9; analysis -190541-e27453d; self-similar -123813-97afeea |
| `fig_esrun` (wall, crossings, horizon-mass drift against the control, 1+log lapse) | D-20261115-172726-60ba4c2, -172730-c6d151b; analyses D-20261119-141839-8686bd7, -142929-bb375ff; data D-20261115-170213-d2c2131 |

The ledger also reads the fresh-context verifier's infall run D-20261121-031711-0d79cb3
(profile deviation with r_ta moved by 3 per cent), labelled "second agent" in its row.

Registered runs of this package (manifests under `../runs/`, outputs under
`/data/haiyangw/nrpic/scratch/D-bh-dress/<run_id>/`): wave 2 D-bh-dress-20261115-171128-38634d6,
-171627-18706fb (by hand); wave 3 D-20261120-222413-4a67fa2, -222422-983f3f6, -222424-d7cd958,
-222429-026731f, -222430-452c907 (single figures), -223535-24f7f90 (all; outputs not copied, the
session was cut); batch 3 D-20261121-130021-e7a9166, -130215-83e6c7b, -130347-5b37c59
(superseded intermediate passes), -130510-7e14c5f (final).

## How to rerun

From the worktree root, with the worktree environment (`harness/bin/nrpic-env create --no-kokkos`),
on a committed state of `note/` (nrpic-run refuses uncommitted changes in the package):

    harness/bin/nrpic-run submit --kind scouting --gate G1 --package tracks/D-bh-dress/note \
        --cores 2 --purpose "note: figures, schematics, ledger" -- \
        .venv/bin/python tracks/D-bh-dress/note/scripts/run_all.py
    # copy <run dir>/figures/* to note/figures/ and <run dir>/tables/* to note/tables/, then
    cd tracks/D-bh-dress/note && latexmk -pdf main.tex
    python3 <paper-writing skill>/scripts/check_manuscript.py --main main.tex --compile \
        --forbid 'ES-1|V-1|D-pre|nrpic_cf|nrpic_geodesic|make_es|athinput|nrpic-run|puncture_drift|secondary_infall|einstein_straus|anta|A100|Slurm'

Each figure script also runs alone (`python scripts/fig_es.py`, output to `figures/`);
`ledger.py` without `--out` reads `figures/*_numbers.json` and writes `tables/`.

## State (2026-11-21, batch 3)

Done: C9 schematic (redrawn in wave 3, looked at again this round); timeline at the gate state
(G0 passed, coord/GATES.md line 11); data figures of the Kerr spike, the Newtonian-mode infall
and the first bubble run with its control, each from registered runs and looked at; sections
"Tests so far" and "Plan and open items" with the failed predictions of the first run (level,
drift, 1+log model) stated as refuted, the late common drift after about 165 M open, the infall
criterion open at the orchestrator; the verifier's wording corrections (dress at a/a_i = 2,
profile sensitive to r_ta, Hernquist gap judged to lie in FdRW's curve, black-hole mass a
choice, wall column, upper bounds, self-similar model); ledger extended (94 rows, all old values
reproduced) and claims check (76 statements); checker with `--compile`: 0 undefined references
or citations, 0 overfull boxes, remaining hits only in the ledger appendix, the registration
scripts and three data keys (JOURNAL entry of 2026-11-21T13:06Z); every page of `main.pdf` read.

Not in this version, by the package brief (results of parallel packages, named as pending
work only, with no numbers): the relaxed-lapse run, the late-drift controls (the
distant-boundary control has run; its reading is the lead's), the first run with dust at the
black hole, the Newtonian-mode run to a/a_i = 30. The verifier's corrections are taken in,
because the lead's HANDOFF and REVIEW-wave3 section 2 ask for them after the brief was written.

Not done: paper-writing reviewers of step 4 (no subagent tool); a second-agent check of the
eight ledger rows the verifier left NOT CONFIRMED; the axis curve of the Kerr Hernquist spike by
a second agent; journal data of the references.

## Requests

- To the lead of D-bh-dress: (1) mark G1 item C16 PASS with evidence: `main.pdf` of
  2026-11-21 from run D-20261121-130510-7e14c5f, checker `--compile` 0/0/0 (JOURNAL entry
  2026-11-21T13:06Z); (2) `stage/G1/STATUS.md:22` "0.5-3.3 per cent at a/a_i = 2": the note's
  numbers give 3.43 for N128Lc (the 3.31 is from the cell-centre table): say "0.5-3.4" or name
  the table; (3) extend exception 1 of `../WRITING_GUIDE.md` to data keys of registered outputs
  read by the figure scripts (`"ES-1"` in fig_esrun.py, `pass_e0.1_s0.5_a100` in fig_infall.py),
  the only 5.8 hits left outside the exception; (4) when the relaxed-lapse run, the drift
  controls, the matter run and the late Newtonian-mode run are judged, add them to the note
  (next version) with their run ids.
- To orch: the ruling `d-pre-3-criterion` (the note states the question as open at the program
  level: r^(-9/4) is only the asymptote of the self-similar solution).
- To kb: journal data of the eleven references (still open from wave 2).
