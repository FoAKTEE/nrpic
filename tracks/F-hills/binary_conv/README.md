# binary_conv: P1's binary alone at three member resolutions (F-hills, wave 3 batch 3)

Helper package of F-hills. Question: is the merger of P1's binary at t = 48.8 M (run
F-20261119-150017-b45ec5f, members at m/8) caused by resolution, and at which member
resolution does the binary survive the 100 M that the next passage (P1b) needs? Design, cost,
predictions and outcomes: `JOURNAL.md` (BC-0 design and cost, BC-1 prediction, BC-2
references, later entries the card runs).

## State (2026-11-27, lead batch 34; the sections below are of 2026-11-21 and kept as written)

The chains this package prepared have ended (the lead's JOURNAL.md, batches 11-34; stage/G1/STATUS.md
T4): P1b at m/16, A (F-20261121-203144-b2cf16b) + A2 (F-20261124-210400-902c650), reached 186.0 M:
the binary is disrupted between 120 and 133 M, m1 is captured by M (common horizon from 137.5 M),
m2 recedes after an 8.73-M pericentre (readers F-20261127-232657-163727d, -232849-14345be,
-232940-3f652bf). B2, the pair alone at m/16 (F-20261126-052133-10f9a5f), is DONE at 140 M; C2,
P1b at m/12 (F-20261126-131751-89eaff8), stopped at 106.69 M by a Slurm submission I/O error. B2
and C2 are G2 material, not yet analysed. The "Results" table below is of 2026-11-21; its 20-M
m/16 cell "(queued)" is out of date: m/12 and m/16 agree within 2.1e-3 M to 21 M
(stage/G1/VERIFIER.md, finding F2; lead batch 11, F-20261121-202021-3c4321e).

## State (2026-11-21 07:45 PST)

Verdict (JOURNAL BC-4, intermediate): P1's merger is a resolution effect of the m/8 members;
the next passage P1b should resolve the members with m/16 (`inputs/p1b_R16n.athinput`, chain
command in BC-4 item 6, NOT submitted; about 30.6 card-hours to 200 M, 43.8 to 280 M). The
evidence covers 20.9 M at m/8 and 7.7 M at m/16; R16n segments 2-3 and R12 (m/12) are queued
and decide the open checks listed in BC-5.

## Results (runs F-20261121-130358-6cf186a, F-20261121-130351-04074e1; analysis F-20261121-154046-c99ccb9)

| | P1 (m/8, three holes) | alone, m/8 | alone, m/16 | EIH (canonical) | Newton |
|---|---|---|---|---|---|
| separation at 7.5 M | 4.8539 | 4.8863 | 4.9477 | 4.9478 | 4.9430 |
| separation at 20 M | 4.2855 | 4.3753 | (queued) | 4.9302 | 4.9693 |
| merger | 48.8 M | about 53 M (stretch estimate) | none expected before 100 M (extrapolated) | 2600-3400 M (2.5PN, Peters) | - |
| member horizon drift, fraction of the mass per M | 1.4e-3, 1.7e-3 | 1.0e-3, 1.4e-3 | -7e-5, -5e-7 | - | - |
| MeshBlock-cycles/s, advance per 50 min | 1963-2242, 14.3-19.2 M (segments 1-6, `p1/README.md`) | 2241, 20.9 M | 2302, 7.7 M | - | - |

No order of convergence is claimed between the mesh members (G1 verifier F2, request (b),
stage/G1/VERIFIER.md; the earlier two-member ">= 3.3" is withdrawn): with R12 (m/12) the binary's
separation at m/12 and m/16 agrees within 2.1e-3 M to 21 M and their difference changes sign, while
m/8 differs by 0.06-0.38 M, so m/8 lies outside any asymptotic regime and three-member "orders" of
12-14.5 (10-20 M) are not asymptotic. What the data support: m/12 = m/16 within 2.1e-3 M; m/8
differs by 0.06-0.38 M (verifier run F-20261125-175931-32701e4). Figures (read): `figures/fig_orbit_conv_intermediate.png`,
`figures/fig_horizons_H_intermediate.png`, `figures/fig_refs.png`.

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
| F-20261121-130351-04074e1 | R16n card chain, 3 segments (about 23 M) | segment 1 done (0-7.74 M, Slurm 4796); segment 2 queued (Slurm 4807), segment 3 follows |
| F-20261121-130358-6cf186a | R8 card chain, 1 segment | completed (0-20.94 M, Slurm 4797; stray resubmission 4808 cancelled) |
| F-20261121-153759-af77173, F-20261121-153844-fbc75ac, F-20261121-154046-c99ccb9 | intermediate analysis, three passes (the third is the reference) | completed |
| F-20261121-153707-1eaa5d4 | R12 card chain, 2 segments (about 16 M), submitted 07:37 PST | queued (Slurm 4809) |

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
        --parent F-20261121-130351-04074e1 --parent F-20261121-130358-6cf186a --parent F-20261121-153707-1eaa5d4 \
        --purpose "binary_conv BC-3: analysis" -- python3 tracks/F-hills/binary_conv/scripts/analyze.py \
        --run R8=/data/haiyangw/nrpic/scratch/F-hills/F-20261121-130358-6cf186a \
        --run R16n=/data/haiyangw/nrpic/scratch/F-hills/F-20261121-130351-04074e1 \
        --run R12=/data/haiyangw/nrpic/scratch/F-hills/F-20261121-153707-1eaa5d4 \
        --p1 /data/haiyangw/nrpic/scratch/F-hills/F-20261119-150017-b45ec5f \
        --refs /data/haiyangw/nrpic/scratch/F-hills/F-20261121-130646-56612a0/refs.json \
        --g2model /data/haiyangw/nrpic/scratch/F-hills/F-20261120-222426-86392c3/model.json \
        --out '$NRPIC_RUN_DIR'

State of a chain: `scripts/submit_chain.sh --status <run dir>`; close a finished one:
`harness/bin/nrpic-run finish <run id>`.

## Requests

- F-hills lead: decide P1b (input `inputs/p1b_R16n.athinput`, command JOURNAL BC-4 item 6; above
  eight card-hours, so decision 0014's announcement in STATUS.md comes first). Read the queued
  chains when they land (R16n segments 2-3, Slurm 4807 and its successor; R12, Slurm 4809) with
  the analysis command above and judge the checks of JOURNAL BC-5; close both runs with
  `nrpic-run finish`. The same stray resubmission will follow the last segment of R16n
  (segment 3) and of R12 (segment 2): cancel it with `scripts/submit_chain.sh --stop <run dir>`
  once the last segment has ended (see the core request below). A profile arm (junk_gauge's recommendation) was not run: about 0.84
  card-hours for one m/8 segment, if the gauge of P1b is to be chosen with evidence.
- core: (1) `scripts/submit_chain.sh` resubmits a chain after its last allowed segment: R8 (run
  F-20261121-130358-6cf186a, MAX_SEGMENTS = 1) queued job 4808 at the wall-clock stop, which would
  have failed with "MAX_SEGMENTS reached" only when it started, holding one of the owner's two
  queue places meanwhile; I cancelled it with `--stop`. Please check the cap before `sbatch`.
  (2) [TO VERIFY] R8 shows one history sample at t = 0.5 with H-norm2 = 1.83e4 (P1, the same
  members at m/8 with core-v0.3 on +-256: 5.99 at t = 0.5; R8 back to 10.9 at t = 1): is this a
  regrid at an output time in core-v0.5, or a real transient?
