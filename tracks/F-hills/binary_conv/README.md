# binary_conv: P1's binary alone at three member resolutions (F-hills, wave 3 batch 3)

Helper package of F-hills. Question: is the merger of P1's binary at t = 48.8 M (run
F-20261119-150017-b45ec5f, members at m/8) caused by resolution, and at which member
resolution does the binary survive the 100 M that the next passage (P1b) needs? Design, cost,
predictions and outcomes: `JOURNAL.md` (BC-0 design and cost, BC-1 prediction, BC-2
references, later entries the card runs).

## State

See the last entries of `JOURNAL.md` and the "Results" section below (filled in as the card
runs land).

## Contents

| Path | What |
|---|---|
| `inputs/bin_m8.athinput`, `bin_m12.athinput`, `bin_m16.athinput` | P1's `<problem>` without the heavy hole (same masses, positions, momenta, gauge); mesh R8 / R12 / R16n on +-128 (JOURNAL BC-0); tlim 100 |
| `inputs/p1b_R16n.athinput`, `p1b_R12.athinput` | P1b candidates: P1's input with the members at m/16 (11 levels) or m/12 (root 96^3), 3000 slots; written by `scripts/make_p1b.py`; not submitted |
| `scripts/athena_keep_trackers_bc.sh` | chain executable: keeps tracker files across restarts, runs `bc-ak05-gpu`, a byte copy of release core-v0.5's card build (`scratch/F-hills/tmp/binary_conv/exe/`, sha256 2512c8d5...61ea4; do not delete it while a chain of this package runs) |
| `scripts/tree_cost.py`, `scripts/mesh_check.sh`, `scripts/p1b_mesh.sh` | MeshBlock trees (g2mesh `tree3.py`) along the Newtonian tracks, card cost; `athena -m` start trees |
| `scripts/refs.py` | references: Newton, EIH (two readings of P), Newton + 2.5PN dissipative Hamiltonian (inspiral time), Peters |
| `scripts/analyze.py` | analysis of the card runs: separation and phase against time with P1 and the references, merger time, horizons, constraint norm, order of convergence, stretch model, segment ledger |
| `scripts/make_p1b.py` | writes the P1b input for a resolution |
| `scripts/figstyle.py` | copy of `harness/style/figstyle.py` |
| `results/`, `figures/` | copies of the JSON summaries and the inspected figures of the runs below |

## Runs

| Run | What | State |
|---|---|---|
| F-20261121-130405-77ad9f6 | mesh check of the three inputs (processors) | completed |
| F-20261121-130646-56612a0 | references (processors; first pass F-20261121-130623-1b35829 had an aliased inspiral panel) | completed |
| F-20261121-131003-75a2b29 | `athena -m` of the P1b candidates | completed |
| F-20261121-130351-04074e1 | R16n card chain, 3 segments (about 19 M) | see JOURNAL |
| F-20261121-130358-6cf186a | R8 card chain, 1 segment (about 17 M) | see JOURNAL |
| (not yet submitted) | R12 card chain, 2 segments (about 16 M): submit when R8's job has ended (two card jobs of the owner at a time) | command below |

## How to rerun (from `/data/haiyangw/nrpic/wt/F-hills`)

Processor parts:

    harness/bin/nrpic-run submit --kind scouting --gate G1 --cores 1 --package tracks/F-hills/binary_conv \
        --purpose "..." -- bash tracks/F-hills/binary_conv/scripts/mesh_check.sh
    harness/bin/nrpic-run submit --kind scouting --gate G1 --cores 1 --package tracks/F-hills/binary_conv \
        --purpose "..." -- python3 tracks/F-hills/binary_conv/scripts/refs.py \
        tracks/F-hills/binary_conv/inputs/bin_m8.athinput '$NRPIC_RUN_DIR' --tend 100 --mass 0.13,0.137

Card chains (one line per resolution; `--gpu-hours` sets the segments, about 0.835 card-hours each):

    harness/bin/nrpic-run submit --kind scouting --gate G1 --launcher chain --gpu-hours 2.0 \
        --package tracks/F-hills/binary_conv \
        --exe tracks/F-hills/binary_conv/scripts/athena_keep_trackers_bc.sh \
        --input /data/haiyangw/nrpic/scratch/F-hills/tmp/binary_conv/exe/bc-ak05-gpu \
        --parent F-20261119-150017-b45ec5f \
        --preregistered 'tracks/F-hills/binary_conv/JOURNAL.md#2026-11-21-bc-1-prediction-for-the-three-runs-written-before-submission' \
        --purpose "binary_conv R12: ..." -- tracks/F-hills/binary_conv/inputs/bin_m12.athinput

Extend a chain that ended at its segment cap (resume from its newest restart; same run
directory; raise MAX_SEGMENTS only within the card-hours granted):

    ATHENA_EXE=tracks/F-hills/binary_conv/scripts/athena_keep_trackers_bc.sh MAX_SEGMENTS=<n> \
    JOB_NAME=<run id> scripts/submit_chain.sh /data/haiyangw/nrpic/scratch/F-hills/<run id> \
        tracks/F-hills/binary_conv/inputs/bin_m<N>.athinput

Analysis (registered; reads whatever the run directories hold, partial runs included):

    harness/bin/nrpic-run submit --kind scouting --gate G1 --cores 1 --package tracks/F-hills/binary_conv \
        --parent F-20261121-130351-04074e1 --parent F-20261121-130358-6cf186a \
        --purpose "binary_conv BC-3: analysis" -- python3 tracks/F-hills/binary_conv/scripts/analyze.py \
        --run R8=/data/haiyangw/nrpic/scratch/F-hills/F-20261121-130358-6cf186a \
        --run R16n=/data/haiyangw/nrpic/scratch/F-hills/F-20261121-130351-04074e1 \
        [--run R12=/data/haiyangw/nrpic/scratch/F-hills/<R12 run id>] \
        --p1 /data/haiyangw/nrpic/scratch/F-hills/F-20261119-150017-b45ec5f \
        --refs /data/haiyangw/nrpic/scratch/F-hills/F-20261121-130646-56612a0/refs.json \
        --g2model /data/haiyangw/nrpic/scratch/F-hills/F-20261120-222426-86392c3/model.json \
        --out '$NRPIC_RUN_DIR'

State of a chain: `scripts/submit_chain.sh --status <run dir>`; close a finished one:
`harness/bin/nrpic-run finish <run id>`.

## Requests

See the end of `JOURNAL.md` (filled in with the verdict).
