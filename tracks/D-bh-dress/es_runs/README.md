# es_runs: first full-relativity runs of Track D (ES-1, its vacuum control V-1, ES-1G)

Helper package of owner D-bh-dress, waves 2 and 2b. The black hole in a vacuum bubble inside
an expanding dust ball (Einstein-Straus type, D-pre-1), evolved in this repository's AthenaK
(release `core-v0.3`, card executable `/data/haiyangw/nrpic/.work/build_gpu_v03/src/athena`),
with its matched vacuum control V-1, and ES-1G, the same data with core's relaxed lapse
(`lapse_leak`, card executable `scratch/core/exe/core_gauge/athena_gpu`). Specification and
pass criteria: `stage/G1/STATUS.md`, section "The first full-relativity run"; predictions in
`JOURNAL.md` before each run, never changed afterwards; outcomes, also of failed
predictions, appended there.

## Results (JOURNAL entries 4 and 6; numbers with run ids there)

| Question | ES-1 (1+log) | V-1 (control) | Verdict |
|---|---|---|---|
| horizon-mass drift from t = 100 M, max over 100-200 M | 3.40e-4 | 1.37e-4 | predicted <= 3e-5: FAILED; refutation (ES-1 above V-1 by > 3x V-1's floor) not met: 1.49x |
| same, over 100-165 M (before the common late drift) | -5.0e-5 .. +9.3e-5 | -4.2e-5 .. +2.1e-5 | |
| M_AH(100 M) - M | +9.55e-4 | +9.37e-4 | predicted +1.5e-3 +- 3e-4: FAILED |
| wall tracers, max relative error for tau <= 200 M | 2.20e-3 | 1.59e-3 | predicted 3e-3: HELD |
| R0 = 6 M group reaches R = 2M (exact 14.827 M) | 14.826 M | 14.826 M | HELD (to 6e-4 M) |
| R0 = 10 M group reaches R = 2M (exact 34.442 M) | 34.437 M | 34.437 M | HELD (to 6e-3 M) |
| R0 = 20 M group (exact 244.74 M) | 244.09-244.51 M at t = 177 M | not by t = 200 M | inside A1's 0.5 M |
| dust inside the wall (by direction) | none; margin >= 0.136 M | - | HELD |
| plateau lapse, 1+log model 1 + 6 ln a | 1.3-1.7, K -> ~0 by t ~ 40 M | - | REFUTED (gauge drifts to K ~ 0) |
| dust proper time at t = 200 M (R0 = 48 M) | 279.7 M (model 1251 M) | - | |
| card-hours | 0.769 | 0.672 | below the predicted 1.0 and 0.9 |

Gauge pathologies of the 1+log runs (entries 4, 6, 7): (i) the slicing leaves the dust
within 30 M (K at the plateau tracer 0.1-0.2 of -3H at t = 30-40 M, positive at t = 40-90 M),
the lapse settles at 1.3-1.4 out to the boundary instead of 1 + 6 ln a; (ii) a lapse pulse
from the dust reaches the hole at t ~ 20-23 M and moves the horizon mass by -2.3e-4 to
+3.2e-4 against V-1 during t = 25-50 M; (iii) the mesh minimum of the lapse swings between
0.004 and 0.23 in the first 45 M (above alpha_exc = 0.05 for several M near t = 6 and
15 M: lapse excision then acts on nothing); (iv) a step of the horizon mass at t ~ 30 M
in both runs; (v) after t ~ 165 M a common downward drift of the horizon mass, and after
tau ~ 130 M an axis/diagonal split of the tracer errors (cause open: no inward signal
from the boundary in the probe lapse, entry 7); (vi) outgoing gauge waves at speed ~1.5
during t = 30-100 M.

Open: the cause of (v). ES-1G (entry 5: the same data with `lapse_leak`, T = 2 M) is
submitted and was still queued at the end of this session; see the run table.

## Runs

Manifests in `tracks/D-bh-dress/runs/<id>/`, outputs in `/data/haiyangw/nrpic/scratch/D-bh-dress/<id>/`.

| Run id | What | State |
|---|---|---|
| D-20261115-170213-d2c2131 | data: ES (dust 36-60 M, 696688 particles + 140 tracers) and V-1 tables, references, prediction numbers | done |
| D-20261115-170234-f9b7f03 | offline constraint check of both tables | done: fourth order |
| D-20261115-170326-dfb2a02 | processor smoke run, 16^3 blocks (1280 blocks) | superseded |
| D-20261115-172413-6412daf | processor smoke run of the ES-1 input as submitted (344 blocks) | done |
| D-20261115-172821-f800e34 | m = 0 against m = 1e-30 on a Kerr geodesic (entry 3) | done: m = 0 is a null particle |
| D-20261115-172726-60ba4c2 | ES-1 on the card (chain, Slurm 4472) | done: 200 M in one segment, 0.769 card-hours |
| D-20261115-172730-c6d151b | V-1 on the card (chain, Slurm 4473) | done: 200 M in one segment, 0.672 card-hours |
| D-20261119-141839-8686bd7 | `analyse.py` on ES-1 and V-1 (entry 4) | done |
| D-20261119-142334-4f2bffe | `tools/es1g_model.py`: homogeneous lapse models for ES-1G (entry 5) | done |
| D-20261119-142929-bb375ff | `tools/es_extra.py` on ES-1 and V-1 (entry 6) | done |
| D-20261119-143659-7adcad7 | `tools/es_extra.py` version 2 on ES-1 and V-1 (adds crossings, Khat, windows against V-1); `results/es_extra.json` | done |
| D-20261119-143413-bce5e71 | `tools/probe_fronts.py`, t = 50-200 M (entry 7) | done: features move outward |
| D-20261119-143444-8a9949c | `tools/probe_fronts.py`, t = 100-200 M (entry 7) | done: no coherent inward signal |
| D-20261119-143623-8576a6e | pre-flight of the ES-1G input, 2 cycles, gauge processor executable (entry 8) | see JOURNAL |
| D-20261119-143626-7d1fa75 | the same with the release processor executable (entry 8) | see JOURNAL |
| D-20261119-142633-6f72922 | ES-1G on the card (chain, Slurm 4636, one segment, <= 1 card-hour) | see JOURNAL; close and analyse with `tools/finish_es1g.sh` |

## Contents

| Path | What |
|---|---|
| `make_data.py` | data sets: ES with the outer dust edge at 60 M (through `einstein_straus/make_es.py`, whose figures it redirects into the run directory), V-1 (`VacuumBubble`: the same f(R), rho = 0), exact references, numbers for the predictions (`predictions.json`), the homogeneous 1+log lapse model of the plateau |
| `tools/offline_check_es.py` | offline constraint check of both tables (`einstein_straus/offline_check.py`, figures redirected) |
| `tools/tracer_mass_check.py` | entry 3: the Kerr geodesic of `problems/kerr/geodesic_mesh.athinput` with p0_m = 0 and 1e-30 |
| `inputs/es1_dx8.athinput`, `inputs/v1_dx8.athinput` | the two runs (identical apart from basename, table and particle file; 24^3 MeshBlocks, 344 blocks; 1+log + Gamma-driver; D-pre-4 finder; massive tracers m = 1e-30; probes at x = 46, 1, 4, 20, 36, 56, 80, 152 M; z = 0 slices of z4c every 10 M, of con and tmunu_E every 25 M) |
| `tools/finish.sh` | closes both card runs (`nrpic-run finish`), registers `analyse.py` on them and copies its JSON and figures here (`--partial`: analyse what exists) |
| `inputs/es1g_dx8.athinput` | ES-1 with core's `lapse_leak = 0.5`, `lapse_leak_alpha = 1` (T = 2 M; option 1 of `scratch/core/exe/core_gauge/READY`); run as D-20261119-142633-6f72922 with `scratch/core/exe/core_gauge/athena_gpu` |
| `tools/es1g_model.py` | homogeneous plateau lapse and dust proper time under 1+log and under `lapse_leak` (numbers of entry 5) |
| `tools/es_extra.py` | second look at any set of ES runs (entry 6): wall per class (axis, diagonal), onset of the tracer errors, crossings of R = 2M, turnaround, lapse and K at the plateau tracers against the models, dust against the wall by direction, space-time diagrams on the x axis, horizon mass against V-1 |
| `tools/probe_fronts.py` | moving features in the lapse at the probes: detrended d alpha/dt, lag of the best cross-correlation between neighbouring probes (entry 7) |
| `tools/preflight_compare.py` | compares the two-cycle processor runs of the ES-1G input with the gauge and the release executables (entry 8) |
| `tools/finish_es1g.sh` | closes ES-1G and runs `es_extra.py` on ES-1, V-1, ES-1G; JSON to `results/es_extra_es1g.json`, figures to `figs/es1g/` |
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
    harness/bin/nrpic-run submit --kind scouting --gate G1 --launcher chain --gpu-hours 1.0 --athena-wall 00:56:00 \
      --package tracks/D-bh-dress/es_runs --exe /data/haiyangw/nrpic/scratch/core/exe/core_gauge/athena_gpu \
      --purpose "..." -- tracks/D-bh-dress/es_runs/inputs/es1g_dx8.athinput   # ES-1G
    # analysis once the card runs are DONE (each closes its runs and copies JSON and figures):
    tracks/D-bh-dress/es_runs/tools/finish.sh          # ES-1 and V-1 with analyse.py (entry 4)
    tracks/D-bh-dress/es_runs/tools/finish_es1g.sh     # ES-1G beside ES-1 and V-1 with es_extra.py
    # the second look of entry 6 and the model of entry 5:
    S=/data/haiyangw/nrpic/scratch/D-bh-dress
    harness/bin/nrpic-run submit --kind scouting --gate G1 --package tracks/D-bh-dress/es_runs --cores 4 \
      --purpose "..." -- python3 tracks/D-bh-dress/es_runs/tools/es_extra.py \
      --run ES-1:$S/D-20261115-172726-60ba4c2:es:es --run V-1:$S/D-20261115-172730-c6d151b:v1:v1 \
      --data $S/D-20261115-170213-d2c2131
    harness/bin/nrpic-run submit ... -- python3 tracks/D-bh-dress/es_runs/tools/es1g_model.py --T 2.0 --t_end 200

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
   else differs between the builds. (The card pushes massive tracers correctly: ES-1's
   wall and crossings, entries 4 and 6.)
2. `docs/FORMATS.md` says `<base>.trajmet.bin` has records of 12 doubles; the code writes 17
   (`nrpic_io.cpp:811-814`: + proper time, E, S_i).
3. The horizon finder writes `<base>.horizon_summary_0.txt` relative to the working
   directory and ignores `-d` (smoke run D-20261115-170326-dfb2a02); the shape file goes to
   `-d`. Write both into the output directory.
4. Gauge: under 1+log with the Gamma-driver the slicing of ES-1 leaves the dust within
   30 M (K at the plateau tracer 0.1-0.2 of -3H by t = 30-40 M, positive between 40 and
   90 M; lapse 1.3-1.7 instead of 1 + 6 ln a), and a lapse pulse from the dust moves the
   horizon mass by up to 3e-4 during t = 25-50 M (entries 4, 6). ES-1G tests `lapse_leak`
   on these data at M/8 for 200 M; please put the outcome of your own ES test
   (core-20261115-202901-b4430da, still "pending" in READY) into READY so that the two can
   be compared.

To the lead of D-bh-dress:
5. The mesh of the specification is built on 24^3 MeshBlocks (16^3 blocks snap the refined
   regions out to +-128 and +-64 M: 1280 blocks, 3.7 times the cells). The near-hole nest is
   therefore wider than in D-pre-4 (M/8 on +-6 M instead of +-4 M); V-1 has the same mesh.
6. Under 1+log, 200 M of coordinate time gave 280 M of dust proper time (not the 1250 M of
   the homogeneous model, entry 4); the wall criterion is judged for tau <= 200 M.
7. The vacuum floor of this mesh is not the D-pre-4 floor: V-1 drifts within 4.2e-5 over
   100-165 M and then, together with ES-1, falls by 1.4e-4 by t = 200 M. Before the null
   test is stated with a floor, decide the cause of the late drift: a rerun of V-1 (no
   dust, 0.67 card-hours) with the outflow boundary at 384 M instead of 192 M (one more
   root level, same inner mesh) tests the boundary hypothesis of entry 6 (E2); not run
   here (outside this package's card-hours).
8. The horizon mass has a step at t ~ 30 M in both runs (+1.05e-3 to +0.92e-3 in V-1):
   take the reference time of any drift after it (t0 = 100 M is).
