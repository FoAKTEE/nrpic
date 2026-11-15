# three_punctures: plan for three black holes in vacuum (F-pre-3, F-pre-4)

Helper package of F-hills (wave 1, 2026-11-15). The deliverable is `PLAN.md`: the first
configuration of a binary passing a heavier black hole, its mesh and card-hours, the
expected junk radiation and constraint violation and how to measure them, the
diagnostics of F-pre-4 with what exists and what is missing, and the runs named for the
lead. No run of the code of branch `core/multi-puncture` was made here (task rule); all
runs of this package are analyses on processors.

## Contents

| Path | What |
|---|---|
| `PLAN.md` | the plan (start here) |
| `JOURNAL.md` | predictions written before each test, outcomes after, failed ones included |
| `inputs/hills_q10_m8.athinput` | proposed input of the first passage (q = 10, a_b = 3, r_p = 8, phase 130 deg, members at m/8); needs `core/multi-puncture` |
| `inputs/hills_q4_m8.athinput` | the cheaper q = 4 passage (a_b = 5, r_p = 9.82, phase 127 deg) |
| `inputs/junk_single_P028.athinput` | one Bowen-York puncture with P/m = 0.28, spheres at 40-80 m (runs R2, R4 of the plan) |
| `scripts/manifest.py` | runs one analysis command and writes its manifest under `tracks/F-hills/runs/` |
| `scripts/newton_start.py` | T2/T5a: Newtonian phase scan and start state with the newton3 driver |
| `scripts/mesh_count.py`, `scripts/mesh_count_b.py` | T3/T3b/T5b: MeshBlock trees with `athena -m` (processor executable of `main`) emulating `puncture_setup`; card-hours of a passage |
| `scripts/junk_energy.py` | T4: radiated energy and constraint norms of core's single-puncture card runs (read only) |
| `scripts/plan_numbers.py` | closed-form numbers of the plan; writes the three inputs |
| `figures/*.png` | copies of the figures of the runs (all looked at; see the journal) |

## Runs (manifests in `tracks/F-hills/runs/<run_id>/manifest.json`, outputs in `scratch/F-hills/<run_id>/`)

| Run id | What |
|---|---|
| `F-hills-20261115-130342-0471114` | T2 Newtonian scan of three configurations (automatic choice superseded) |
| `F-hills-20261115-130755-982aba0` | T2 rerun with the chosen configuration; start state and Newtonian track |
| `F-hills-20261115-131109-634fb86` | T3 trees: core's by_triple reproduced (1100), m/8-m/32, cube wave zone |
| `F-hills-20261115-131348-634fb86` | T3b trees with the spherical wave zone, two domains, along the passage; card-hours |
| `F-hills-20261115-131605-634fb86` | T4 junk and constraint norms from core's test-1b card runs |
| `F-hills-20261115-131832-907e5fe` | T5a q = 4 Newtonian scan and start state |
| `F-hills-20261115-131933-907e5fe` | T5b q = 4 trees and card-hours |
| `F-hills-20261115-132220-efddfc0`, `-132430-7d0c6dd` | plan numbers and inputs (the second adds static outputs and the single-puncture input; numbers identical) |

## How to rerun (from `/data/haiyangw/nrpic/wt/F-hills`, processors only, about 4 minutes)

    S=tracks/F-hills/three_punctures/scripts; N=/data/haiyangw/nrpic/scratch/F-hills
    python3 $S/manifest.py "T2" scouting $S/newton_start.py -- python3 $S/newton_start.py --choose far 130 OUTDIR
    python3 $S/manifest.py "T3b" scouting $S/mesh_count_b.py -- python3 $S/mesh_count_b.py <T2 outdir>/newton_start.json OUTDIR
    python3 $S/manifest.py "T5a" scouting $S/newton_start.py -- python3 $S/newton_start.py --only q4 --choose q4 auto OUTDIR
    python3 $S/manifest.py "T5b" scouting $S/mesh_count_b.py -- python3 $S/mesh_count_b.py --dom D256q4 256 64 9 2 <T5a outdir>/newton_start.json OUTDIR
    python3 $S/manifest.py "T4" scouting $S/junk_energy.py -- python3 $S/junk_energy.py OUTDIR
    python3 $S/manifest.py "plan" scouting $S/plan_numbers.py -- python3 $S/plan_numbers.py <T2>/newton_start.json <T5a>/newton_start.json OUTDIR

Plain `python3` (numpy, scipy, matplotlib of the user site); not `-I`, which hides them.
The scripts import the sibling package `tracks/F-hills/newton3/hills3` (work in
progress) and `python/nrpic/figstyle.py`; T4 reads `scratch/core/core-20261115-12104*`.

## Requests (details in PLAN.md section 8)

- Lead of F-hills: the runs R0, R2, R4, R1 and then R3 or R3' of PLAN.md section 7
  (they need the executables of `core/multi-puncture`); the budget choice between
  completing q = 10 (40 card-hours in all) and the q = 4 passage (27 in all); replace
  the novelty helper's cost numbers (MeshBlocks 1.5-2.4 times higher when measured;
  m/32 does not fit one card); first configuration r_p = 8 M, not 6 M.
- core: pairwise common-horizon trigger in `fastflow`; optional position-dependent
  shift damping and ADM surface integrals; card memory at `max_nmb_per_rank = 2700`.
- kb: locator of the parabolic-flyby quadrupole energy; gauge literature for punctures
  of mass ratio 10-20; published junk energies of boosted Bowen-York punctures.
- newton3: keep `HillsSetup`, `initial_state`, `scatter`, `trajectory` stable; add
  "state at r0 after integrating from 10 r_t".
- geodesic_binary: run the two chosen configurations in the geodesic-plus-Newtonian
  model (does the captured member plunge?).
