# puncture_drift: noise floor of the null test (D-pre-4)

Owner D-bh-dress, helper package. Question: how much does the apparent-horizon mass (and
spin) of a single vacuum puncture drift in this repository's AthenaK, with the
configuration of the horizon-finder check of the first paper, over as long a time as
3 card-hours allow; how does the drift depend on resolution and on the finder settings;
what is the smallest horizon-mass change a matter run of the same length could detect.

Status and numbers: `JOURNAL.md` (predictions before, outcomes after) and the section
"State" below. Run manifests: `tracks/D-bh-dress/runs/<run_id>/manifest.json`.

## Contents

| Path | What |
|---|---|
| `inputs/drift_dx8.athinput` | `problems/puncture/horizon_calib.athinput` (main a1c2237) with `tlim = 500`; dx = M/8 at the puncture (paper Table "setups", row "Vacuum black hole"; finder `metric_drvts = interpolant`, 16 points, l_max 8, tolerance 1e-5, every 16 cycles) |
| `inputs/drift_dx16.athinput` | the same with `refined_region2/level = 6` (dx = M/16 inside abs(x) < 2 M) |
| `tools/manifest.py` | writes and updates the run manifests (by hand; `nrpic-run` refuses a worktree shared by helpers) |
| `tools/probe_finder.py` | re-searches the horizon of restart dumps on the processor executable for one cycle with other finder settings: three horizons at once (production; tolerance 1e-9 with 4000 iterations; start from 2 M) on the 16-point and the 32-point (l_max 16) grid |
| `tools/slice_masses.py` | finder-independent horizon mass of each dump: Misner-Sharp mass of the slice, M_H = R_H/2 at the outermost 2m/R = 1 (imports `analysis/diag/slicemass.py`) |
| `tools/analyse_drift.py` | drift D(T), scatter, slopes, finder-setting spread, smallest detectable change dM_min(T), k_floor for the null-test scenarios, convergence order; figures |
| `tools/finish.sh` | the whole analysis of the two card runs in one command (probes of every dump, slice masses, figures) |
| `results/` | text and JSON output of the analysis runs (copied from scratch) |
| `figs/` | figures (PNG and PDF), looked at before use |

## How to rerun

Card runs (chained, release executable, registered):

    cd /data/haiyangw/nrpic/wt/D-bh-dress
    ATHENA_EXE=/data/haiyangw/nrpic/.work/build_gpu_c3/src/athena MAX_SEGMENTS=1 \
      scripts/submit_chain.sh /data/haiyangw/nrpic/scratch/D-bh-dress/<run_id> \
      tracks/D-bh-dress/puncture_drift/inputs/drift_dx8.athinput
    # dx16: drift_dx16.athinput, MAX_SEGMENTS=2
    scripts/submit_chain.sh --status /data/haiyangw/nrpic/scratch/D-bh-dress/<run_id>

Analysis of the card runs once they exist (processors, 16 threads, about 1 h):

    tracks/D-bh-dress/puncture_drift/tools/finish.sh

Analysis of the dumps that existed before this package (runs/puncture/hcal):

    python3 tracks/D-bh-dress/puncture_drift/tools/probe_finder.py \
      /data/haiyangw/nrpic/runs/puncture/hcal/{dx4,dx8_tight,dx16}/rst/punc.0000[12].rst \
      --out <scratch run dir> --tag hcal --threads 8 --jobs 2
    python3 tracks/D-bh-dress/puncture_drift/tools/slice_masses.py --out <dir>/slices.json <dumps>
    python3 tracks/D-bh-dress/puncture_drift/tools/analyse_drift.py --out <dir> --tag hcal \
      --probes <dir>/hcal/probes.json --slices <dir>/slices.json \
      --res dx4=4 dx8_tight=8 dx16=16

## State

See the end of `JOURNAL.md` (kept current).

## Requests

None yet (filled in at the end of the package).
