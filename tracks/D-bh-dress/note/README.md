# note: working note v0 of Track D (gate G0)

Helper package of D-bh-dress, wave 2 (2026-11-15). The REVTeX working note of S4 (black-hole
growth in an expanding collisionless medium, the dark-matter dress, the null test of
cosmological coupling), its figures and schematics, the numerical ledger, and a check of the
lead's documents against the run outputs. Predictions and outcomes: `JOURNAL.md`. Guide and
notation (paper-writing skill, one level above the manuscript): `../WRITING_GUIDE.md`,
`../NOTATION.md`. No simulation was run: every script reads outputs of runs registered in
wave 1 (`scripts/common.py` lists them).

## What is here

| Path | Content |
|---|---|
| `main.tex`, `references.bib`, `main.pdf` | the note (REVTeX 4.2, two columns, 10 pages) and its compiled pages |
| `figures/fig_*.{pdf,png}` | five data figures, each made by `scripts/<same name>.py` from registered run outputs: `fig_es` (bubble slice and exact shell motion), `fig_constraints` (constraint convergence offline and in AthenaK at t = 0), `fig_floor` (horizon-mass floor of a vacuum black hole), `fig_spike` (probe-limit spike and its stationarity in AthenaK), `fig_infall` (self-similar infall, growth, capture) |
| `figures/fig_*_numbers.json` | the numbers each figure script derived (read by `ledger.py`) |
| `figures/schem_*.{png,svg}` | the two schematics of the stage check (architecture, timeline), `paperfig.py` |
| `tables/ledger.tex` | the ledger appendix: every number of the note with its run id |
| `tables/parameters.tex` | the parameter table of the note |
| `tables/claims.md`, `tables/claims.json` | 36 numbers of `stage/G0/REPORT.md`, `stage/G1/STATUS.md`, `STATUS.md` checked against the run outputs (31 agree; five remarks) |
| `scripts/common.py` | the run ids the note reads; inputs checked against each run's `sha256sums.txt` where it has one |
| `scripts/run_all.py` | runs every `fig_*`, `schem_*` and `ledger.py` into one directory (the registered run) |
| `scripts/handreg.py` | registers and runs a local run by hand when `nrpic-run` refuses (adapted from Track A's note package) |
| `scripts/czstyle.py`, `scripts/paperfig.py` | unchanged copies of `harness/style/` |

Registered runs of this package (manifests under `../runs/`, outputs under
`/data/haiyangw/nrpic/scratch/D-bh-dress/<run_id>/`): D-bh-dress-20261115-171128-38634d6
(first pass, superseded) and D-bh-dress-20261115-171627-18706fb (the committed figures and
tables). Both registered by hand: `harness/bin/nrpic-run submit --package tracks/D-bh-dress/note`
refused because of an untracked `es.horizon_summary_0.txt` in the worktree root.

## How to rerun

From the worktree root, with the worktree environment (`harness/bin/nrpic-env create --no-kokkos`):

    harness/bin/nrpic-run submit --kind scouting --gate G0 --package tracks/D-bh-dress/note \
        --purpose "note v0: figures, schematics, ledger" -- \
        .venv/bin/python tracks/D-bh-dress/note/scripts/run_all.py
    # if nrpic-run refuses (an untracked file outside tracks/), the same by hand:
    .venv/bin/python tracks/D-bh-dress/note/scripts/handreg.py --gate G0 --purpose "..." \
        --refusal "<message>" -- .venv/bin/python tracks/D-bh-dress/note/scripts/run_all.py
    # copy <run dir>/figures/* to note/figures/ and <run dir>/tables/* to note/tables/, then
    cd tracks/D-bh-dress/note && latexmk -pdf main.tex
    python3 <paper-writing skill>/scripts/check_manuscript.py --main main.tex --compile \
        --forbid 'ES-1|V-1|D-pre|nrpic_cf|nrpic_geodesic|make_es|athinput|nrpic-run|puncture_drift|secondary_infall|einstein_straus|anta|A100|Slurm'

Each figure script also runs alone (`python scripts/fig_es.py`, output to `figures/`);
`ledger.py` without `--out` reads `figures/*_numbers.json` and writes `tables/`.

## State (2026-11-15)

Done: guide and notation; five data figures and two schematics, each looked at; ledger,
parameter table and claims check from registered runs; note v0 compiled and read;
`../stage/G0/STAGE_REPORT.md` from `nrpic-stage report` with the helper's sections
(proposed statuses, the five remarks of the claims check, a draft decision paragraph).
Predictions P1-P6 and outcomes in `JOURNAL.md` (P4 and P5 partly refuted, causes found by
runs in which they could have failed; P6 refuted only by one data key).
Not done: the paper-writing reviewers of step 4 (no subagent tool in this session);
`nrpic-stage verify` (it writes into the stage directory); a fresh-context verifier of the
note's ledger; journal data of the references (the bibliography has arXiv eprints, titles and
authors read from the sources).

## Requests

- To the lead of D-bh-dress: (1) carry the proposed statuses of `stage/G0/STAGE_REPORT.md`
  ("Products of the note package") into `stage/G0/CHECKLIST.md`, rerun
  `harness/bin/nrpic-stage report D-bh-dress G0`, and write "Decision requested" (draft in the
  report); (2) correct `stage/G1/STATUS.md:13` (0.625 is run -125613-248fdaf; -123813-97afeea
  prints m(lambda_1) = 0.654), `:11` (5.8-5.9 is the box "mid transition"; 5.3 and 4.7 over
  the region), `:12` (0.02 per cent holds for the peak only), `:52` and REPORT.md section 3
  (exact arrival times 14.83 M and 34.44 M), `REPORT.md:101` (analysis run -125739-a18d74d);
  (3) compute the cost of the vacuum control V-1 with the model before submitting it;
  (4) add `cd tracks/D-bh-dress/note/scripts && python ledger.py` to a `stage/G0/VERIFY`
  command list so that `nrpic-stage verify` regenerates the ledger and the claims check, and
  run `nrpic-stage verify D-bh-dress G0`; (5) rewrite STATUS.md and HANDOFF.md (C18): the note
  and the schematics exist now; (6) when ES-1 and V-1 have run, rerun `scripts/run_all.py`
  and extend Sec. IV of the note.
- To orch: `harness/bin/nrpic-run submit --package DIR` refuses when any untracked file sits
  outside `tracks/` (here `es.horizon_summary_0.txt` in the worktree root, written by another
  helper's AthenaK run whose working directory is the worktree root). Same request as Track
  A's note helper: ignore untracked files outside the package and the shared code, or have
  runs never write into the worktree root.
- To the helper whose AthenaK run writes `es.*` into the worktree root (through the lead): set
  the run's working directory under `scratch/`.
- To kb: journal data (or confirmation that none exists) for the eleven references of
  `references.bib`; the Bertschinger 1985 and Fillmore-Goldreich 1984 sources (already
  requested in `../outbox/20261115T1510Z__to-kb__dress-and-coupling-sources.md`).
