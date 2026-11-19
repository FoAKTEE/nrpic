# JOURNAL of the heat package (C-sidm, wave 3a): tests T6-T8 of collide/TESTS.md

Predictions are written here before the run they concern; outcomes after, failed ones
included. Times are UTC (the machine's clock shows PST; `date -u`).

## 2026-11-19 14:35 Set-up

Executable: core's branch core/collisions-2, `scratch/core/exe/core_collisions-2/athena_cpu`
(commit f46f159 in its COMMIT file; READY says: options absent = release core-v0.3 byte for
byte; `coll_energy = particle` conserves each pair's canonical energy with the metric at
the particle). Deck `inputs/heat.athinput` (flat Kerr-Schild functor, periodic box at
x0 = 10, `coll_energy = particle`). Particle files from `collide/analysis/make_box.py`
(the track's generator, wave 1). References: `collide/REFERENCES/` (wave 1) and
`scripts/isobaric.py` (this package, nonlinear isobaric conduction).

Cost basis from wave 2 (`../box_tests/README.md`, run C-20261115-165500-c67e036): one core,
5.7-6.7e-7 s per tested pair in one sub-step, 3.3-3.7e-7 s per tested pair sub-cycled,
3.0e-7 s per particle and step. Owner allotment at the start: 16 cores at a time, 8 busy
(`nrpic-run budget`, 14:30 UTC).

## 2026-11-19 14:40 Prediction S0 (smoke and cost)

Mode box theta = 0.003, k lambda = 0.2, 2e5 particles, 128 x 4 x 4 cells, dt = 0.1 t_coll,
60 steps, `coll_energy = particle` and `cell` side by side (`scripts/smoke.py`).
Predicted: both exit 0; n_trunc = 0, n_noroot = 0, n_balance = 0 (flat metric: the
canonical energy is W, the root exists, no detailed-balance rejection); about 0.5 tested
pairs per particle and sub-step and 2 to 4 sub-steps per step (P_bound/pmax with
v_bound/<v_Mol> ~ 2.5 and 0.1 t_coll per step gives P_bound ~ 0.25); cost
1.5-3e-6 s per particle and collision time (12-25 tested pairs per particle per t_coll at
3.5e-7 s each, plus the push); `particle` and `cell` give the same final momenta to
1e-12 (equal to rounding in a flat metric) and differ in cost by less than a factor 2.
Refuted by: a non-zero exit, truncated pairs, any root failure or balance rejection in a
flat box, a particle/cell difference above 1e-12, or a cost outside 0.5-10e-6 s.
