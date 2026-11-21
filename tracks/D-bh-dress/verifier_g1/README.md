# verifier_g1: fresh-context verifier of Track D's G1 material (checklist item C17)

Helper package of D-bh-dress, wave 3 (2026-11-20). Independent recomputation of the numbers
gate G1 rests on (decision 0016 item 4). The report is `VERIFIER.md` (the lead copies it into
`stage/G1/`); predictions and outcomes, in the order they were made, are in `JOURNAL.md`.

## What is here

| File | What it is |
|---|---|
| `VERIFIER.md` | the verdicts V1-V5 with evidence and run ids |
| `JOURNAL.md` | predictions (written before each run) and outcomes |
| `vreaders.py` | my readers of AthenaK output (`traj.bin`, `trajmet.bin`, `part.*.bin`, particle files, horizon summary, history) and of the format-2 table, from `athenak/src/particles/nrpic_io.cpp` |
| `v1_es.py` | V1: ES-1 / V-1 wall tracers, inner tracer crossings, horizon-mass drift, dust against the wall |
| `v2_infall.py`, `v2_selfsim.py` | V2: turnaround mass, dress and profile of the Newtonian-mode runs from the snapshots; my spherical shell reference (several force laws); my self-similar solution |
| `v3_kerr.py` | V3: my Kerr spike in the equatorial plane (constant f, Hernquist adiabatic growth) and my digitiser of the FdRW pgf figures; local-frame check of the measure |
| `zamo_test.py`, `jac_test.py` | development checks of V3 (local-frame quadrature, finite-difference Jacobian) |
| `v4_kerr_stat.py`, `v4b_refconv.py` | V4: Kerr a = 0.8 stationarity from the snapshots (counts, E, Lz, Q) and my off-equator reference counts; their convergence |
| `v5_ledger.py` | V5: the note's numerical ledger at commit 78d470ca, row by row |
| `figstyle.py` | copy of `harness/style/figstyle.py` |

Outputs (figures, JSON) are in the run directories `scratch/D-bh-dress/<run id>/`, listed below;
nothing large is committed.

## Runs (all processor, 0 card-hours, registered with `harness/bin/nrpic-run`)

| Run id | Script | What |
|---|---|---|
| D-20261120-222209-871e07f | `v1_es.py` | V1 |
| D-20261121-031031-e23da04 | `v2_infall.py` | V2, first run |
| D-20261121-031711-0d79cb3 | `v2_infall.py` | V2, with step checks and the growth figures against the converged shells |
| D-20261121-033209-9c0bd44 | `v3_kerr.py --procs 4` | V3 |
| D-20261121-034048-17427b0 | `v4_kerr_stat.py --procs 4` | V4 |
| see `VERIFIER.md` | `v4b_refconv.py --procs 4` | V4b, convergence of the V4 reference |
| see `VERIFIER.md` | `v5_ledger.py` | V5 |

## How to rerun

From the worktree root, package committed, Python environment present
(`harness/bin/nrpic-env create --no-kokkos` if `.venv` is missing):

    V=tracks/D-bh-dress/verifier_g1
    run() { harness/bin/nrpic-run submit --kind scouting --gate G1 --package $V --cores "$1" --purpose "$2" -- "${@:3}"; }
    run 2 "V1" python3 $V/v1_es.py                     # 15 s
    run 2 "V2" python3 $V/v2_infall.py                 # 5 min (reads 3 x 36 snapshots of 520k particles)
    run 4 "V3" python3 $V/v3_kerr.py --procs 4         # 9 min
    run 4 "V4" python3 $V/v4_kerr_stat.py --procs 4    # 8 min
    run 4 "V4b" python3 $V/v4b_refconv.py --procs 4    # 15 min
    run 2 "V5" python3 $V/v5_ledger.py                 # 5-10 min; V5 reads the V2 and V3 run directories (--v2run, --v3run)

Inputs are the raw outputs of the track's runs under `scratch/D-bh-dress/` (named in each
script) and, for V3, the paper source `kb-data/raw/arxiv/1707.06302/v2/src` (pgf figures read
as text). Scripts write into `$NRPIC_RUN_DIR`.

## Requests

See the last section of `VERIFIER.md` (to the lead of D-bh-dress; none to other owners).
