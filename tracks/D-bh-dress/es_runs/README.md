# es_runs: first full-relativity runs of Track D (ES-1, its vacuum control V-1, ES-1G)

Helper package of owner D-bh-dress, waves 2, 2b and 3. The black hole in a vacuum bubble inside
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

Open: the cause of (v) (package `drift_controls`, in parallel).

## ES-1G results (JOURNAL entry 9; predictions of entry 5, J1-J6 and K1-K2 of entry 9)

ES-1G = ES-1 with core's `lapse_leak = 0.5` (T = 2 M), run D-20261119-142633-6f72922
(Slurm 4636, 200 M in one segment, 0.794 card-hours; `nrpic-run verify`: PASS). Analyses:
D-20261120-221754-ae3dafe (`tools/es_extra.py`, `results/es_extra_es1g.json`) and
D-20261120-222424-230f936 (`tools/es1g_judge.py`, `results/es1g_judge.json`; it
supersedes D-20261120-222042-59c7d82 for the figures, same numbers plus W).

| Prediction | ES-1G | Verdict |
|---|---|---|
| G1 dust lapse within 3 % of the lapse_leak model, 10-200 M (R0 = 48 M); mesh max < 1.2 after 10 M; refuted by dust lapse > 1.3 | max deviation 1.31e-2, lapse below the model (R0 = 40 M: 0.80e-2, 56 M: 2.07e-2); mesh max 1.093 after 10 M (1.109 at 5.3 M); dust lapse <= 1.061 | HELD |
| G2 K-hat at the R0 = 48 M tracer within 25 % of -3H at t = 50, 100, 150, 200 M; refuted below 50 % | 0.72, 0.67, 0.64, 0.63 of -3H (ES-1: -0.2 to +0.2) | FAILED, not refuted |
| G3 proper time of R0 = 48 M at t = 200 M: 208 M +- 5 % | 205.3 M (model 207.9 M; ES-1 279.7 M) | HELD |
| G4 wall (tags 56-69) below 3e-3 for the whole run | 1.7e-4 to tau = 206 M, no axis/diagonal split (ES-1 2.2e-3 to tau = 200 M) | HELD |
| G5 R0 = 6, 10 M cross R = 2M within 0.05 M of 14.827, 34.442 M; R0 = 20 M not before t = 200 M | -8.6e-4 M; -5.0e-3 to +0.9e-3 M; 28 removed; R0 = 20 M at tau = 205.2 M, turnaround to 1.8e-4 | HELD |
| G6 M_AH(100 M) - M = 9.5e-4 +- 1e-4; drift from 100 M < 1.4e-4, refuted > 4.1e-4; ES-1's 25-50 M swing against V-1 halved | +1.141e-3; drift [-4.17e-4, +6.96e-3] on 100-199.5 M; swing 0.56 of ES-1's | FAILED, refutation met (its reading "dust coupling" not established) |
| G7 no "not used" warning, finite, no escapes, mass kept, 28 removed, <= 0.85 card-hours | all as predicted; 0.794 card-hours | HELD |
| J1 0-30 M against core's ES test (core-20261115-202901-b4430da) | horizon mass 1.9e-5 apart at 10 M, lapse at the same tracer 1e-5 apart, largest lapse 1.1086 both | HELD |
| J2 no start-up dip > 5 % in the dust lapse | within [-0.95e-2, 0] (R0 = 48 M) | HELD |
| J3 dust lapse never below 1 after 5 M | never below its t = 0 value 1 | HELD |
| J4 near-hole lapse activity (10-40 M) at most 1/3 of ES-1's | 0.089 (x = 4 M), 0.081 (x = 20 M) | HELD |
| J5 mesh minimum of the lapse below alpha_exc = 0.05 after 50 M | above it from t = 108 M on, 0.069 at 200 M | REFUTED |
| J6 dust velocity against the normal observers 0.02-0.1 (R0 = 48 M) | 0.034, 0.052, 0.060, 0.063 at t = 50-200 M (ES-1: up to 0.30) | HELD |
| K1 Misner-Sharp mass in the bubble constant to 1e-3 from 100 to 200 M (refuted > 3e-3) | +6.5e-3 at R ~ 5 M, -5.5e-3 at R ~ 50 M; at 200 M m falls outward from 1.0081 to 0.958 | REFUTED |
| K2 slice horizon mass changes by less than half the finder's +6.97e-3 (100-200 M) | +6.78e-3; finder and slice agree within 2e-4 at every dump | REFUTED: not the finder |

Late horizon drift from t0 = 100 M (measured, no prediction): ES-1G [-4.17e-4, +9.46e-4]
on 100-165 M and up to +6.96e-3 on 100-199.5 M (minimum at 126 M, zero at 149 M); ES-1
[-5.0e-5, +9.3e-5] and down to -3.40e-4; V-1 [-4.2e-5, +2.1e-5] and down to -1.37e-4. The
common downward drift of ES-1 and V-1 does not appear in ES-1G as such: ES-1G moves the
other way, 20-50 times more. Meanwhile its horizon shrinks in coordinates, 1.40 M
(t = 25 M) to 0.78 M (199.5 M; 6.2 cells of M/8), where ES-1 and V-1 grow to 2.56 and
2.25 M, and the puncture lapse rises (mesh minimum 0.039 at 50 M, 0.069 at 200 M). The
slice-mass analysis D-20261120-222956-6abf860 (K1-K2) shows that the growth is in the
slice, not in the finder (slice horizon mass +6.78e-3 against the finder's +6.97e-3), and
that the exterior mass (2.7397 = M plus the dust) is lost from the outer boundary inward,
beyond coordinate r ~ 105 M at t = 100 M, r ~ 62 M at 150 M and everywhere, the bubble
included, at 200 M; the bubble's mass stayed within 1.0005-1.0020 up to t = 150 M.
[JUDGEMENT] This points at the outflow boundary at +-192 M (core READY: outflow is not
transparent for the Painleve-Gullstrand exterior); not tested. Slicing at the puncture
and the dust are not excluded.

Gauge pathologies of ES-1G (entry 5's list): no start-up pulse beyond a 1-2 % lag behind
the homogeneous model; no lapse below 1 in the dust; no front from the dust edges at the
hole; the mesh minimum of the lapse above alpha_exc = 0.05 on 2.8-13.1 M and from 108 M to
the end (lapse excision then acts on no cell, risk R14; no particle was near the hole).

Figures (`figs/es1g/`, each looked at, described in entry 9): `judge_horizon.png`
(horizon mass, drift, coordinate radius of ES-1G, ES-1, V-1, core-ES), `judge_hole.png`
(mesh minimum of the lapse against 0.05, probe lapses and rates near the hole),
`judge_lapse.png` (dust lapse against the models, largest lapse), `judge_core30.png`
(0-30 M against core's run), `judge_wall.png` (wall by class), `extra_horizon.png`,
`extra_plateau.png`, `extra_tracers_vs_t.png`, `extra_dust_wall.png`,
`extra_spacetime_ES-1G.png`, `extra_spacetime_ES-1.png`, `extra_spacetime_V-1.png`,
`slicemass_ES-1G.png` (Misner-Sharp mass m(R) and 2m/R of the dumps at t = 0-200 M, finder
horizons on the slice's crossing).

Particle energy: no number of this package (entries 4, 6, 7, 9) depends on the code's
particle energy E = alpha W - beta^i u_i (entry 9, "Particle energy E"): `analyse.py` reads
it (trajmet index 13) and never uses it; the "E" of the exact groups is the LTB shell
energy of the model; proper time is the pusher's (index 12).

## Gauge for the null test with matter

The evidence (run ids above and in entries 4, 6, 9):
- In the matter, lapse_leak (ES-1G) against plain 1+log (ES-1): largest lapse 1.11
  against 2.13; dust lapse within 2.1 % of the homogeneous model against a slicing that
  leaves the dust (K ~ 0 in the dust from t ~ 40 M); dust speed against the normal
  observers at most 0.064 against 0.30; wall within 1.7e-4 to tau = 206 M against 2.2e-3
  (tau <= 200 M) and 1.7e-2 (tau = 283 M); every tracer group within about 3.6e-3 at
  t = 200 M against more than 2e-2 (read from `figs/es1g/extra_tracers_vs_t.png`); no lapse pulse from the dust at the hole (activity at
  x = 4 M 0.09 of ES-1's; ES-1's pulse moved the horizon mass by up to 3.2e-4 during
  25-50 M).
- At the hole, the other way round: ES-1G's horizon mass drifts by up to 6.96e-3 over
  100-200 M against 3.4e-4 (ES-1) and 1.4e-4 (V-1); its horizon shrinks to 6.2 cells of
  M/8 and the puncture lapse rises above alpha_exc from t = 108 M on. Over 30-100 M its
  horizon mass stays 1.0-1.25e-3 above M with oscillations of about 1e-4, like ES-1's,
  and the slice's mass in the bubble stays within 1.0005-1.0020 up to t = 150 M. The late
  growth is in the slice, not the finder, and arrives with a loss of the exterior mass
  that enters from the outer boundary (K1-K2); ES-1G's boundary at 192 M is closer than
  the light travel distance of the 200 M run, which core's READY asks to avoid.
- On 0-30 M ES-1G and core's ES test agree to 2e-5, so the near-hole behaviour is not a
  matter of the particle lattice, the outer boundary or the extent of the M/8 nest at
  early times; core's L3 test also found the hole much smaller in coordinates under
  lapse_leak (horizon radius 0.73 against 2.34 M with plain 1+log) and asks for M/16 at
  the centre.

[JUDGEMENT] The G2 vacuum-bubble (null) and matter runs should use lapse_leak (T = 2 M),
because it removes the gauge pathologies of the matter that dominate ES-1 (a slicing
that leaves the dust, a lapse pulse into the hole, wall and shell errors ten times
larger), and the null test compares the hole against matter that must be on its exact
curve. But not on the ES-1 mesh as it stands: (o) the outer boundary must lie beyond the
light travel distance of the run (or hold the Painleve-Gullstrand exterior), since in
ES-1G the exterior mass is lost from the boundary inward and the late horizon growth
arrives with it; (i) the near-hole nest must be M/16 (or the
hole must stay above about 8 cells of radius for the whole window; at M/8 ES-1G left that
at t ~ 100 M); (ii) every matter run needs a vacuum control with the same gauge and mesh
(a V-1G), because ES-1G minus V-1 mixes gauge and dust (the two horizon masses split at
t = 8 M, before any dust signal); (iii) lapse excision must not rest on alpha_exc = 0.05
alone (rely on ah_exc_factor, or a threshold below the measured puncture lapse); (iv) the
reference time t0 lies after the start-up (finder spikes to t ~ 15 M, mesh minimum of
the lapse above 0.05 to 13 M). With plain 1+log the late horizon drift is 10-50 times
smaller, but the matter is not on its exact curve after t ~ 100 M and the dust drives a
gauge pulse into the hole; I would use 1+log only as the second gauge of a pair, to show
that a null result does not depend on the slicing.

Still missing for the null-test floor (the floor itself is not stated here; the late-drift
controls of ES-1 and V-1 run in package `drift_controls`):
1. V-1G: V-1 with lapse_leak on the same mesh (card run, about 0.7 card-hours like V-1),
   the matched control of ES-1G; it decides whether ES-1G's drift needs the dust.
2. ES-1G and V-1G with an M/16 nest near the hole (card runs; cost not estimated here):
   they decide whether the drift is resolution of the horizon (finder or slice) or the
   slicing.
3. A boundary test for ES-1G: the same run (or V-1G) with the outflow boundary at 384 M,
   or with a boundary condition that holds the exterior; the slice-mass profile of
   ES-1G (D-20261120-222956-6abf860) favours the boundary but does not test it.
4. The cause of the common late drift of ES-1 and V-1 (`drift_controls`, whose step-1
   slice-mass test on ES-1 and V-1 is the direct comparison with K1-K2 here).
5. For a flux comparison, the particle energy per tag from the initial data, not the
   code's E (`flux_tools`).

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
| D-20261119-143623-8576a6e | pre-flight of the ES-1G input, 2 cycles, gauge processor executable (entry 8) | done: option read, acts only where alpha > 1 |
| D-20261119-143626-7d1fa75 | the same with the release processor executable (entry 8) | done: warns lapse_leak not used |
| D-20261119-150329-d1d8f03 | `tools/preflight_compare.py` on the two pre-flights | done |
| D-20261119-142633-6f72922 | ES-1G on the card (chain, Slurm 4636, one segment; ran 2026-11-19 07:36-08:24 PST) | done: 200 M, 0.794 card-hours; closed 2026-11-20, `nrpic-run verify` PASS; judged in entry 9 |
| D-20261120-221754-ae3dafe | `tools/es_extra.py` on ES-1, V-1, ES-1G (`results/es_extra_es1g.json`, `figs/es1g/extra_*`) | done |
| D-20261120-222042-59c7d82 | `tools/es1g_judge.py`, first version (no W; two figures with clipped labels) | done, superseded for figures by the next |
| D-20261120-222424-230f936 | `tools/es1g_judge.py` on ES-1G, ES-1, V-1, core-ES (`results/es1g_judge.json`, `figs/es1g/judge_*`) | done |
| D-20261120-222956-6abf860 | `analysis/diag/slicemass.py` on the five ES-1G restart dumps (Misner-Sharp mass against the finder; log `results/slicemass_es1g.txt`, `figs/es1g/slicemass_ES-1G.png`) | done: K1, K2 refuted (growth in the slice; exterior mass lost from the boundary inward) |

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
| `tools/finish_es1g.sh` | closes ES-1G and runs `es_extra.py` on ES-1, V-1, ES-1G; JSON to `results/es_extra_es1g.json`, figures to `figs/es1g/` (entry 9: its `tee` no longer truncates a redirected log) |
| `tools/es1g_judge.py` | entry 9: dust-tracer lapse against the lapse_leak model over whole intervals, the tracers' Lorentz factor W against the normal observers, largest and smallest lapse on the mesh (intervals above alpha_exc), probe lapses and detrended rates near the hole, departure from V-1, horizon mass, drift windows and coordinate radius, wall by class; any set of runs named ES-1G, ES-1, V-1, core-ES; `es1g_judge.json` and `figs/judge_*` |
| `figs/es1g/`, `results/es_extra_es1g.json`, `results/es1g_judge.json` | outputs of the entry-9 analyses (copied from the run directories) |
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
    # entry 9: ES-1G judged beside ES-1, V-1 and core's 30 M run
    harness/bin/nrpic-run submit --kind scouting --gate G1 --package tracks/D-bh-dress/es_runs --cores 2 \
      --purpose "..." -- python3 tracks/D-bh-dress/es_runs/tools/es1g_judge.py \
      --run ES-1G:$S/D-20261119-142633-6f72922:es --run ES-1:$S/D-20261115-172726-60ba4c2:es \
      --run V-1:$S/D-20261115-172730-c6d151b:v1 \
      --run core-ES:/data/haiyangw/nrpic/scratch/core/core-20261115-202901-b4430da:es \
      --data $S/D-20261115-170213-d2c2131 --t0 100
    # entry 9 (K1-K2): Misner-Sharp mass of the ES-1G restart dumps against the finder
    harness/bin/nrpic-run submit --kind scouting --gate G1 --package tracks/D-bh-dress/es_runs --cores 2 \
      --purpose "..." -- python3 analysis/diag/slicemass.py ES-1G=$S/D-20261119-142633-6f72922 \
      --base es --out '$NRPIC_RUN_DIR/slicemass_ES-1G'

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
4. Gauge (updated in wave 3, entry 9). ES-1G (D-20261119-142633-6f72922) is the
   "Einstein-Straus run longer than 30 M" that `scratch/core/exe/core_gauge/READY` lists
   as not tested. On 0-30 M it reproduces your ES test (core-20261115-202901-b4430da) to
   2e-5 in the horizon mass and 1e-5 in the lapse. Over 200 M at M/8: the dust side is
   ten times better than plain 1+log (wall 1.7e-4, dust lapse within 2.1 % of exp(6TH),
   dust speed against the slices <= 0.064), but the hole shrinks in coordinates (horizon
   mean radius 1.40 M at t = 25 M to 0.78 M at 199.5 M), the mesh minimum of the lapse
   rises from 0.039 (50 M) to 0.069 (200 M), and the finder's mass grows by 6.96e-3 over
   100-200 M. Please (a) add this outcome to READY; (b) say whether the shrinking hole is
   expected of lapse_leak with the Gamma-driver (the condition is plain 1+log where
   alpha < 1, so the change must come through the slicing of the bubble or the shift),
   and whether another shift_eta or lapse_leak_alpha keeps the hole's coordinate size;
   (c) consider a lapse-excision criterion that does not depend on a fixed value: with
   alpha_exc = 0.05 lapse excision acted on no cell from t = 108 M on (risk R14);
   (d) the Misner-Sharp mass of ES-1G's dumps (D-20261120-222956-6abf860) shows the
   exterior mass (2.7397) lost from the outflow faces at +-192 M inward, reaching the hole
   at t ~ 150-200 M, as your READY warns for the Painleve-Gullstrand exterior: Track D's
   200 M runs need the boundary further out or a boundary condition that holds that
   exterior; please say which you will provide and with which executable.

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
9. (wave 3, entry 9) Card runs that decide the gauge of the G2 null test (section "Gauge
   for the null test with matter"): V-1G, the input `inputs/v1_dx8.athinput` with the two
   `<z4c>` lines of `inputs/es1g_dx8.athinput` (lapse_leak = 0.5, lapse_leak_alpha = 1),
   run with `scratch/core/exe/core_gauge/athena_gpu` (about 0.7 card-hours, like V-1); then
   ES-1G and V-1G with an M/16 nest near the hole (cost not estimated here). Not run in
   this package (card time 0).
10. (wave 3, to the lead and package `drift_controls`) The finder re-search on restart
   dumps that `drift_controls` prepares for ES-1 and V-1 (its test C: finer angular grid,
   tighter stopping) applies unchanged to ES-1G's dumps at t = 100, 150, 200 M
   (`scratch/D-bh-dress/D-20261119-142633-6f72922/rst/es.0000{2,3,4}.rst`); it tests
   directly whether the finder loses accuracy as the horizon shrinks to 6 cells.
