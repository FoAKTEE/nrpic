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
| `tools/finish.sh` | the whole analysis of the two card runs in one command (probes of every dump, slice masses, figures); `FINISH_RUN_ID=<id>` continues an analysis run |
| `tools/tracer_check.py` | side check: radius of the six massless tracers, release card executable against `runs/puncture/single_v3` |
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

## State (2026-11-15, 14:50Z): done

Runs (manifests in `tracks/D-bh-dress/runs/`): D-bh-dress-20261115-121313-284ec4f (M/8,
500 M, 0.654 card-hours), D-bh-dress-20261115-121314-284ec4f (M/16, 500 M, two segments,
1.523 card-hours), D-bh-dress-20261115-121427-284ec4f (finder re-search of the earlier
calibration dumps), D-bh-dress-20261115-130954-49ed46f (analysis of the card runs),
D-bh-dress-20261115-143918-a5c125a (tracer side check). Card total 2.18 of 3.

Results (numbers with their sources in `JOURNAL.md`, tables in `results/drift_drift.txt`,
figures `figs/drift_history.png`, `figs/drift_floor.png`, `figs/drift_finder.png`,
`figs/hcal_finder.png`, `figs/tracer_check.png`):
- Drift of the apparent-horizon mass, production finder, 50 -> 500 M: +3.0e-4 at M/8
  (end of the gauge transient +1.6e-4 by 100 M, plateau, then +7e-7 per M), +3.7e-5 at
  M/16 (9e-8 per M). Spin |S|/M^2 below 3.3e-7 (M/8) and 5.7e-9 (M/16) after 5 M.
- Excursions of the same size and timing at both resolutions at 220-255 M (1e-4 peak to
  peak) and 300-340 M (1.5e-4): from the outer region (boundary at 128 M), not the hole.
- Finder settings (tolerance 1e-9, start from outside, 32 points) shift the mass by
  6e-5 to 3.1e-4, constant in time: they change the drift by at most 1.0e-5.
- Smallest detectable mass change Delta M_min/M at M/16: 2.0e-5 to 2.5e-5 for windows from
  t0 = 50 M of 41-156 M that end before 210 M; 5e-5 to 9e-5 for windows that cross the
  excursions (up to 440 M); 8e-5 when the gauge transient is included (t0 = 20 M). At M/8:
  1.6e-4 to 3.5e-4 (2.8e-5 from t0 = 100 M before 210 M). k_floor = Delta M_min /
  ln(a_f/a_i) at M/16: 1.8e-5 to 3.3e-5 before 210 M, 4.3e-5 to 8.3e-5 across.
- Not done: M/32 (outside the budget; judged not to lower the floor in this
  configuration, JOURNAL.md); a run with the boundary at 256 M (would test the attribution
  of the excursions); the cause of the tracer behaviour.

## Requests

1. core: the release card executable `.work/build_gpu_c3/src/athena` does not push the
   six massless tracers of `problems/puncture/horizon_calib.athinput` along geodesics: one
   is excised at t = 0.31 M, the other five move outward together near light speed and
   leave the mesh by 182 M; the earlier executable of `runs/puncture/single_v3` kept the
   circular orbits at r = 6-11 for 250 M (run D-bh-dress-20261115-143918-a5c125a,
   `figs/tracer_check.png`, both runs' `punc.traj.bin` and `punc.nrpic.hst`). The
   spacetime is unaffected (massless, not deposited), but every Track D matter run pushes
   its particles with this executable: please check the release build's push (or the
   problem generator's reading of `p<n>_u<i>`) on this input before Track D's matter runs.
2. core (minor): a chained restart loses one periodic dump: the wall-clock stop writes
   its restart through the ordinary writer, which advances `last_time` by dt
   (athenak/src/outputs/restart.cpp:193-201), so the next scheduled dump is skipped (here
   t = 300 M of the M/16 run). Writing the final restart without advancing `last_time`
   would keep the schedule.
3. lead (D-bh-dress), for the null-test design (not another owner, recorded here): measure
   from t0 >= 50 M at M/16 or finer (M/8 still has +1.6e-4 of transient between 50 and
   100 M); keep the measurement window before the outer-boundary signal reaches the hole
   (about 215 M for a boundary at 128 M), or move the boundary out; a control run with the
   boundary at 256 M at M/16 (about 1.8 card-hours for 500 M) would test the attribution.
