# note_v2: working note v2 of Track D (after gate G1) and the second Kerr sampler seed

Helper package of D-bh-dress, batch 6 (2026-11-21 afternoon; processors only, 0 card-hours).
Two deliverables:

1. **Working note v2** (REVTeX, `main.tex`, `main.pdf`): note v1 (`../note/`) brought to the
   state after gate G1 (signed 2026-11-21 with reservations, `coord/GATES.md` line 20), with
   every change that `../stage/G1/GATE_REVIEW.md` sections 5-6 asks of the note, the first G2
   result ES-F, and the relaxed-lapse finding (decisions 0022 item 3, 0025 item 3). Guide and
   notation one level above: `../WRITING_GUIDE.md`, `../NOTATION.md` (unchanged).
2. **Second sampler seed of the Kerr spike stationarity test** (gate review section 5 item 3:
   inner-range deficits 3.1, 1.8, 0.9 per cent of seed 1), prediction first (`JOURNAL.md` N1),
   outcome in `JOURNAL.md` N3 and in the note (ledger part 10, `fig_kerr_seeds`).

Predictions and outcomes: `JOURNAL.md` (N0-N4). v1's history: `../note/JOURNAL.md`.

## Where v2 lives

The package may write only here, so v2 is a full copy of the note directory: `note_v2/` has
the same layout as `../note/` (scripts, figures, tables, main.tex). `../note/` is v1 and is
untouched. **Request to the lead**: replace `../note/` by this directory (or point the stage
package at it); `nrpic-stage verify` looks for `tracks/D-bh-dress/note/`.

## What is here

| Path | Content |
|---|---|
| `main.tex`, `references.bib`, `main.pdf` | note v2 (REVTeX 4.2, PRD two-column) and its compiled pages |
| `figures/fig_*.{pdf,png}`, `fig_*_numbers.json` | data figures, each from `scripts/<same name>.py` and registered run outputs |
| `figures/schem_*.{png,svg}` | architecture (post-G1 chain) and stage timeline (G0 and G1 passed), `paperfig.py` |
| `tables/ledger.tex` | ten ledger tables: every number of the note with its run id (parts 7-10 new) |
| `tables/parameters.tex` | parameter table (Q16 and ES-F added) |
| `tables/claims.{md,json}` | v1's check of the lead's documents against the run outputs (unchanged inputs) |
| `scripts/common.py` | run ids the note reads (new: q16, q16_ana, q16_lost, v1b, hor_cmp, lead_y1, gate_review, v1gb, es1g, esf_data, esf, esf_ana, esf_crit, kerr2_*, kerr_seeds) |
| `scripts/fig_esf.py` | new: ES-F growth against the removed energy, closure, M_AH over the exact LTB mass |
| `scripts/fig_q16.py` | new: Newtonian-mode infall to a/a_i = 16 against matched shells and the self-similar profile |
| `scripts/fig_kerr_seeds.py` | new: the two Kerr seeds, time-averaged deficits and running means |
| `scripts/ledger.py` | v1's ledger plus parts 7-10 and the parameter rows |
| `scripts/schem_*.py` | schematics updated to the post-G1 state |
| `kerr_seed2/compare_seeds.py` | the pre-registered seed comparison of N1 (figure `fig_kerr_seeds` of its run) |
| `JOURNAL.md` | predictions and outcomes N0-N4 |

## Runs of this package (manifests under `../runs/`, outputs under `scratch/D-bh-dress/<id>/`)

| Run | What |
|---|---|
| D-20261121-211717-7b6374b | Kerr initial data, seed 20261121 (48000 particles, 6 files), `spike/sample_kerr.py` |
| D-20261121-212016-7e090f9 | AthenaK release core-v0.3 processor build on analytic Kerr-Schild a = 0.8, 20000 M, 6 cores |
| (filled at close) | analysis of seed 2 (`spike/analyze_kerr.py`), seed comparison, note build (`run_all.py`) |

## How to rerun (from the worktree root, worktree venv)

    # Kerr seed 2
    harness/bin/nrpic-run submit --kind scouting --gate G2 --package tracks/D-bh-dress/note_v2 --cores 4 -- \
      bash -c 'cd tracks/D-bh-dress/spike && python sample_kerr.py --out "$NRPIC_RUN_DIR" --n 48000 --nfiles 6 --a 0.8 --ecut 0.99 --slice ks --seed 20261121'
    harness/bin/nrpic-run submit ... --cores 6 -- bash -c 'cd tracks/D-bh-dress/spike && python3 drive_runs.py --ic <IC> --out "$NRPIC_RUN_DIR" \
      --exe /data/haiyangw/nrpic/.work/build_cpu_v03/src/athena --athinput kerr_geodesic.athinput --files kerr_0.nrp ... kerr_5.nrp \
      -- time/tlim=20000 particles/snap_dt=100 particles/dt=0.05'          # 40 min on 6 cores
    harness/bin/nrpic-run submit ... -- bash -c 'cd tracks/D-bh-dress/spike && python analyze_kerr.py --ic <IC> \
      --ref /data/haiyangw/nrpic/scratch/D-bh-dress/D-bh-dress-20261115-172646-ed6a510 --runs <RUN>/kerr_* --out "$NRPIC_RUN_DIR" --tag kerr_seed2'
    harness/bin/nrpic-run submit ... -- python tracks/D-bh-dress/note_v2/kerr_seed2/compare_seeds.py \
      --a <seed-1 analysis json> --b <seed-2 analysis json> --out '$NRPIC_RUN_DIR'
    # note: figures, schematics, ledger, then copy into figures/ and tables/, compile, check
    harness/bin/nrpic-run submit --kind scouting --gate G2 --package tracks/D-bh-dress/note_v2 --cores 2 -- \
      python tracks/D-bh-dress/note_v2/scripts/run_all.py
    cd tracks/D-bh-dress/note_v2 && latexmk -pdf main.tex
    python3 <paper-writing skill>/scripts/check_manuscript.py --main main.tex --compile --forbid '<list of ../WRITING_GUIDE.md>'

## State

(filled at close; see JOURNAL.md)

## Requests

(filled at close)
