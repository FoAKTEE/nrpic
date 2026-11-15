# es_runs: first full-relativity runs of Track D (ES-1 and its vacuum control V-1)

Helper package of owner D-bh-dress, wave 2. The black hole in a vacuum bubble inside an
expanding dust ball (Einstein-Straus type, D-pre-1), evolved in this repository's AthenaK
(release `core-v0.3`, card executable `/data/haiyangw/nrpic/.work/build_gpu_v03/src/athena`),
with its matched vacuum control V-1. Specification and pass criteria:
`stage/G1/STATUS.md`, section "The first full-relativity run"; predictions restated in
`JOURNAL.md` (entry 2) before submission and not changed afterwards. Outcomes, also of
failed predictions, are appended there.

## State

See the last entries of `JOURNAL.md`. Runs (manifests in `tracks/D-bh-dress/runs/<id>/`,
outputs in `/data/haiyangw/nrpic/scratch/D-bh-dress/<id>/`):

| Run id | What | State |
|---|---|---|
| D-20261115-170213-d2c2131 | data: ES (dust 36-60 M, 696688 particles + 140 tracers) and V-1 tables, references, prediction numbers | done |
| D-20261115-170234-f9b7f03 | offline constraint check of both tables | done: fourth order |
| D-20261115-170326-dfb2a02 | processor smoke run, 16^3 blocks (1280 blocks) | superseded |
| D-20261115-172413-6412daf | processor smoke run of the ES-1 input as submitted (344 blocks) | done |
| D-20261115-172821-f800e34 | m = 0 against m = 1e-30 on a Kerr geodesic (entry 3) | done: m = 0 is a null particle |
| D-20261115-172726-60ba4c2 | ES-1 on the card (chain, Slurm 4472) | see JOURNAL / `harness/bin/nrpic-run status` |
| D-20261115-172730-c6d151b | V-1 on the card (chain, Slurm 4473) | see JOURNAL |

## Contents

| Path | What |
|---|---|
| `make_data.py` | data sets: ES with the outer dust edge at 60 M (through `einstein_straus/make_es.py`, whose figures it redirects into the run directory), V-1 (`VacuumBubble`: the same f(R), rho = 0), exact references, numbers for the predictions (`predictions.json`), the homogeneous 1+log lapse model of the plateau |
| `tools/offline_check_es.py` | offline constraint check of both tables (`einstein_straus/offline_check.py`, figures redirected) |
| `tools/tracer_mass_check.py` | entry 3: the Kerr geodesic of `problems/kerr/geodesic_mesh.athinput` with p0_m = 0 and 1e-30 |
| `inputs/es1_dx8.athinput`, `inputs/v1_dx8.athinput` | the two runs (identical apart from basename, table and particle file; 24^3 MeshBlocks, 344 blocks; 1+log + Gamma-driver; D-pre-4 finder; massive tracers m = 1e-30; probes at x = 46, 1, 4, 20, 36, 56, 80, 152 M; z = 0 slices of z4c every 10 M, of con and tmunu_E every 25 M) |
| `analyse.py` | the analysis of both runs: horizon mass and its drift against the control, every tracer's areal radius (metric at the particle) against its proper time and the exact curve, crossing times of R = 2M, lapse at the probes and along the x axis; `es_analysis.json` and figures |
| `figs/` | figures copied from the registered runs (each looked at before use) |
| `results/` | JSON results copied from the registered runs |
| `JOURNAL.md` | predictions before each test, outcomes after |

## How to rerun

From the worktree root `/data/haiyangw/nrpic/wt/D-bh-dress` (Python of `.venv`):

    harness/bin/nrpic-run submit --kind scouting --gate G1 --package tracks/D-bh-dress/es_runs --cores 8 \
      --purpose "..." -- python3 tracks/D-bh-dress/es_runs/make_data.py --hp 1.0 --tau_max 1500
    harness/bin/nrpic-run submit ... -- python3 tracks/D-bh-dress/es_runs/tools/offline_check_es.py --data <data run dir>
    # card runs (the inputs name the data run directory D-20261115-170213-d2c2131):
    harness/bin/nrpic-run submit --kind scouting --gate G1 --launcher chain --gpu-hours 1.97 \
      --package tracks/D-bh-dress/es_runs --exe /data/haiyangw/nrpic/.work/build_gpu_v03/src/athena \
      --purpose "..." -- tracks/D-bh-dress/es_runs/inputs/es1_dx8.athinput      # and v1_dx8
    # analysis once both have run (partial runs are read as far as they go):
    harness/bin/nrpic-run submit --kind scouting --gate G1 --package tracks/D-bh-dress/es_runs --cores 4 \
      --purpose "..." -- python3 tracks/D-bh-dress/es_runs/analyse.py \
      --es /data/haiyangw/nrpic/scratch/D-bh-dress/D-20261115-172726-60ba4c2 \
      --v1 /data/haiyangw/nrpic/scratch/D-bh-dress/D-20261115-172730-c6d151b \
      --data /data/haiyangw/nrpic/scratch/D-bh-dress/D-20261115-170213-d2c2131 --t0 100

A local AthenaK command must `cd "$NRPIC_RUN_DIR"` first: the horizon finder writes
`<base>.horizon_summary_0.txt` into the working directory, not into `-d`.

## Requests

To core:
1. Tracers (answers our own blocker `outbox/*tracer-push-release-build.md`): in this source
   p<n>_m = 0 makes a null particle (`nrpic.cpp:454-460`); the six tracers of
   `problems/puncture/horizon_calib.athinput` and the geodesic of
   `problems/kerr/geodesic_mesh.athinput` have p<n>_m = 0.0 and are light rays in the
   release executables (run D-20261115-172821-f800e34). Please confirm, give those inputs a
   positive mass (or an explicit null-particle option), and close the blocker or say what
   else differs between the builds.
2. `docs/FORMATS.md` says `<base>.trajmet.bin` has records of 12 doubles; the code writes 17
   (`nrpic_io.cpp:811-814`: + proper time, E, S_i).
3. The horizon finder writes `<base>.horizon_summary_0.txt` relative to the working
   directory and ignores `-d` (smoke run D-20261115-170326-dfb2a02); the shape file goes to
   `-d`. Write both into the output directory.
4. Gauge (as `outbox/*lapse-for-expanding-dust.md`): with 1+log the plateau lapse reaches
   about 10 by t = 200 M in the homogeneous model (`results/predictions.json`); see the
   outcome of entry 2 for what the run did. A lapse option for expanding dust is still
   needed before G2 (`scratch/core/exe/core_gauge/READY` did not exist during this package).

To the lead of D-bh-dress:
5. The mesh of the specification is built on 24^3 MeshBlocks (16^3 blocks snap the refined
   regions out to +-128 and +-64 M: 1280 blocks, 3.7 times the cells). The near-hole nest is
   therefore wider than in D-pre-4 (M/8 on +-6 M instead of +-4 M); V-1 has the same mesh.
6. "200 M of coordinate time" means about 1250 M of dust proper time under 1+log
   (homogeneous model); the wall criterion is stated for tau <= 200 M and judged there.
