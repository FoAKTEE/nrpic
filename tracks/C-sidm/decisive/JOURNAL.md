# JOURNAL of C-sidm/decisive (wave 3, round 1, helper of C-sidm)

Package: the decisive collisional cluster runs D1 (energy defect of the release operator,
seed scatter) and D3 (a King model on the stable side of the fluid onset) designed in
`../stage/REVIEW-wave2.md` section 7, card runs with predictions first. Card cap of the
package: 3.0 card-hours of allocation, no job above one hour, at most one job of this
package in the queue (package `drift` holds the owner's other slot). Run ids:
`tracks/C-sidm/runs/<run_id>/manifest.json`; outputs `scratch/C-sidm/<run_id>/`.

## 2026-11-20 22:15 UTC Entry 1: go/no-go for card runs with the collisions-2 executable

Pause flag absent (22:13 and 22:15 UTC). Queue at 22:14 UTC (`squeue -u haiyangw`): one job
of the user, 4733 `core-mpi-cards` (core), pending; no job named C-*. Budget (`nrpic-run
budget`, 22:15 UTC): G2 used 1.73, reserved 1.84, left 41.43 card-hours.

Executable: `/data/haiyangw/nrpic/scratch/core/exe/core_collisions-2/athena_gpu`, built from
f46f159 (`COMMIT` there), sha256 82a05ada... (`CARD_TESTS.log` lines "exe sha256
82a05adae8f65304").

Condition 1, core's entry D stands [VERIFIED by reading, locators below]:
- `git show core/collisions-2:tracks/core/JOURNAL-coll2.md`, entry "2026-11-19 14:30 UTC",
  section "D: card differences, run core-20261119-141059-f3ccf56" (journal lines 829-855 at
  branch head 4c798e7): (a) every integer column of every differing `coll.hst` identical in
  every row of all five tests, "the two executables test and accept the same pairs in every
  step; no acceptance flipped"; (b) momenta |du|/max(1,|u|) at most 2.1e-14; positions
  2.6e-12 at x = 100 (2.6e-14 of the coordinate; the clause "below 1e-12 absolute" failed as
  written, read by core as rounding of the coordinates); (c) first differing snapshot is the
  first after a collision step; with sigma = 0 the snapshots are identical. Core's reading:
  card code generation of the changed collision kernel [JUDGEMENT of core, not tested].
- Later entries do not withdraw it; they extend it. Entry "2026-11-20 22:05 UTC", section
  "R150" (journal lines 1026-1037): over 1200 collision steps of a self-gravitating cluster
  in Z4c (150 M), `coll_energy = cell` of this executable and the release card executable
  agree in every integer column of all 1200 rows of `st.coll.hst`, 5001 collisions each,
  central lapse within 7.8e-15 (collisionless pair: 5.8e-15); comparison run
  core-20261120-220420-63419ab.

Condition 2, nothing declares the executable unfit for collisional cluster runs
[VERIFIED by reading]:
- `READY` (rewritten 2026-11-20 14:07 local), section "Card": all card items PASSED or
  explained; no pending section. "Not tested: adaptive refinement, more than one rank, heat
  conduction (Track C's T6-T8), coll_energy with removal or excision of colliding
  particles." Neither of the first three applies to D1/D3 (static mesh, one rank); the last
  applies to the phase after the first excision (alpha < 0.1), which comes after the
  collapse criterion alpha_min < 0.3 that D1 measures (wave 2: excision 8.5-11 M after it,
  `../threshold_scan/JOURNAL.md` entry 6 table).
- `CARD_TESTS.log` last line (note 2026-11-20, core coll2-close): the five FAIL lines of job
  4484 mean "not byte-identical to the release card executable"; "Usable for runs".
- Core's outbox `tracks/core/outbox/20261120T220741Z__to-C-sidm__collisions-2-card-closed.md`
  on core/collisions-2: "tested on the card and usable for your runs, including D1 (Kn = 10
  with `coll_energy = particle`)".

What core's wave-3 entries say about the 150 M cluster test (job 4639, card run
core-20261119-143232-4d1e995, analysis core-20261120-220159-7418482; journal entry
2026-11-20 22:05 UTC, section "C") [VERIFIED by reading core's journal; numbers are core's]:
cluster y_c = 0.819, Kn = 3, 1e4 particles, collision cells of 2 M, 150 M, 1200 collision
steps; `particle` changes sum M H_p in the collision steps by 6.3e-17 of its value over 5104
collisions, `cell` by +6.49e-5 over 5001; 0 pairs without a root; 5 of 5109 proposals
rejected by the balance step; particle against cell: collisions z = +1.02, central lapse at
most 2.80e-3 apart, mass radii at most 2.97 percent apart; collisions lower the central
lapse from 0.809 to 0.791 (cell) and 0.789 (particle) while the collisionless run stays
between 0.810 and 0.816. Core's own caution: "there is no second seed per mode to separate
the mode from the realisation". Card cost 0.219 s per step with `particle`, 0.218 s with
`cell`.

Decision: GO for D1 and D3 with this executable, scouting, gate G2 [JUDGEMENT on the two
conditions above, both of which hold as written in the task].

## 2026-11-20 22:18 UTC Entry 2: D1 decks and prediction D1 (written before submission)

Decks (`scripts/decks.py d1`, `inputs/`): the wave-2 decks `threshold_scan/inputs/cc{1,2}_kn10.athinput`
with only `<job> rng_seed` and `<particles> coll_energy` changed (diff checked: header,
problem name, rng_seed, one added line; `coll_budget = true` was already there). Same
particle files (IC run C-20261115-165832-fccee3a), mesh (static, M/4 cells inside
|x|_inf < 8 M), sigma~ (18.608 CC2, 16.890 CC1), 300 M. Card executable of core/collisions-2
(Entry 1). Jobs: `inputs/d1_job1.list` (cc2_kn10_part_s1, cc2_kn10_part_s2),
`inputs/d1_job2.list` (cc1_kn10_part_s1, cc1_kn10_part_s2); cc2_kn10_cell_s2 goes into a
later job with a D3 run. Each list starts with a smoke run of its first deck to t = 0.5 M.

References from wave 2 (release core-v0.3, cell mode, seed 1; `../stage/REVIEW-wave2.md`
section 7 and `../threshold_scan/JOURNAL.md` entry 6, runs C-20261115-171058-c26cfad,
C-20261115-171059-4b70228, C-20261115-171059-35441e3, analyses C-20261115-191420-8538aa4,
C-20261119-151944-08f3220): alpha_min < 0.3 at 206.75 M (cc2_kn10) and 184.25 M (cc1_kn10);
collisions per particle before that 2.88 and 2.48; the central lapse relative to the
control falls by 0.01 at 44-46 M (L16); summed dE_particles (energy at the particles'
metric, cell mode) to the collapse 2.2e-4 and 1.8e-4 of sum M W, 1.9 and 2.3 binding
margins (L14); cost 3.42-3.46 s per M.

Definitions used by the analysis (`scripts/analyze_decisive.py`, to be written and tested
on the wave-2 runs before the D1 outputs exist):
- dalpha(t) = alpha_c(control) - alpha_c(run), alpha_c = `alpha_probe` of `cc.nrpic.hst`,
  control = the wave-2 Kn = inf run of the same model (the seed does not enter it);
  D100 = mean of dalpha over 95 <= t <= 105 M.
- t_c = first time with alpha_min < 0.3 (`alpha_min` of `cc.nrpic.hst`, every 4 cycles).
- Seed scatter: s_X = |X(s1) - X(s2)| for a pair of one model and mode; the scatter of one
  run sigma_X ~ s_X/sqrt(2) (one degree of freedom: a factor-of-several uncertainty).

Prediction D1 [JUDGEMENT throughout; bases given]:

(a) Early contraction unchanged. D100 of the particle-mode runs equals D100 of the
    cell-mode runs (wave-2 seed 1 and cc2_kn10_cell_s2) within the seed scatter:
    |mean(part) - mean(cell)| <= 3 sigma_pooled, sigma_pooled^2 = (s_part^2 + s_cell^2)/4,
    or <= 2e-3, whichever is larger. Expected sign: particle mode contracts slightly more
    (the cell-mode defect heats), by 0 to 2e-3 at 100 M. Basis: before 100 M the summed
    defect is about 0.02-0.05 of the binding margin (L14: 0.013-0.016 at 44-46 M, growing),
    against the 0.0148 in alpha_c that one whole margin separates CC1 from CC2.
    Refuted if the difference exceeds both bounds; a larger contraction in particle mode
    would mean the defect slowed the early phase, a smaller one that it drove it.
(b) Seed scatter of the early drop: s(D100) about 1e-3 (band 2e-4 to 4e-3). Basis: core's
    150 M cluster at N = 1e4 moved the central lapse by 2.8e-3 between two collision
    sequences (Entry 1); scaled by (1e4/1e5)^(1/2) to 9e-4.
(c) Collapse in particle mode: both CC2 particle runs and both CC1 particle runs reach
    alpha_min < 0.3 before 300 M (90 percent confidence). Refuted by a particle run that
    does not: the release defect would then be a cause of the collapse itself.
(d) Seed scatter of the collapse time: s(t_c) about 4 M (2 percent of 200 M), band 1 to
    12 M, for each pair (cc2 part, cc1 part, cc2 cell s1/s2). Basis: a lapse scatter of
    about 1e-3 (b) divided by the early contraction rate relative to the control,
    0.01/45 M = 2.2e-4 per M, gives 4.5 M; the late runaway does not add to a time shift
    fixed earlier. A scatter above 12 M means every later collisional comparison needs
    more than two seeds.
(e) Effect of the defect on the late phase: t_c(particle) - t_c(cell) between -15 and
    +3 M for CC2 (central -5 M: removing the heating makes the collapse earlier), the same
    for CC1. The defect is a cause of the late phase if |mean t_c(part) - mean t_c(cell)|
    exceeds 3 sigma_pooled of (d) (or 6 M if the measured scatter is smaller than 2 M); a
    shift of the opposite sign (particle later by more than that) would refute the heating
    reading of the defect.
(f) Energy budget (history columns 32-36 of `cc.coll.hst`, particle mode): the summed
    collision-step change of sum M H_p (column 33, dH_particles) stays below 1e-13 of
    sum_MH_particles at every record before the first excision, one-signed and positive
    at about 2e-21 M per collision (box_rerun R6: +1.5-1.9e-21 M per collision, run
    C-20261119-141431-a351ac7); n_noroot = 0; n_balance at most 1e-3 of the collisions
    (R6: <= 2.7e-4); max_dlam below 0.05. sum_MH_particles itself (column 32) is not
    conserved by the push in an evolving metric: it moves like the controls' sum M E_K
    (up to 1e-2 M by 200 M, threshold_scan P3.9). In cell mode (cc2_kn10_cell_s2) column 33
    is positive, about 1-2.4e-10 M per collision in the first 25 M (R6: +1.11(0.47)e-10 M at
    Kn = 0.01; wave-2 step-1 prediction 1.74e-10 M of E_K for CC2), and the summed
    dE_particles to t_c is 1-4e-4 of sum M W (wave 2: 2.2e-4). Refuted by any of these
    failing before the first excision; after excision `coll_energy` with removal is
    untested by core (READY), and only rest-mass bookkeeping is predicted there.
(g) Collision statistics: collisions per particle before t_c within 15 percent of the
    wave-2 value scaled by t_c (2.88 x t_c/206.75 for CC2, 2.48 x t_c/184.25 for CC1);
    |collisions - sum of sum_P|/sqrt(sum of sum_P) < 4; first-step sum_P of part_s1 within
    2e-3 relative of the wave-2 seed-1 value (23.69597, 24.41630; the particle mode takes
    the Moller speed of the transferred momenta, a first-order change in the metric
    difference across a cell that averages out to second order), of part_s2 within 3
    pairing sd (0.050, 0.054) of the expectation 23.692 and 24.412. n_trunc = 0.
(h) Rest mass bit-identical before the first excision; deposit identity int_E = sum_mW to
    1e-14; cost 3.4-3.7 s per M (particle costs as cell on the card, 0.219 against
    0.218 s per step in core's cluster), so 1030-1110 s per run and about 0.63 card-hours
    of allocation per job with the smoke run.

## 2026-11-20 22:29 UTC Entry 3: D1 job 1 submitted; D3 initial data (outcome); test of the analysis

D1 job 1 (cc2_kn10_part_s1, cc2_kn10_part_s2 after a smoke run) is run
C-20261120-221846-797bdbe, Slurm job 4737, submitted 22:18 UTC with --gpu-hours 0.65; pending
at 22:29 UTC. The package `drift` submitted the owner's second card job (4741) at 22:25 UTC,
so this package submits nothing more until 4737 has run (queue rule).

D3 initial data, run C-20261120-222427-6b27eea (`scripts/make_d3_ic.py`, 2 cores, 3.5 min).
I did not write a prediction for this run before starting it; its pass criteria are the
offline checks of `equilibria/check_equilibria.py` (unchanged thresholds of the equilibria
package) and the rule of the task (distance from the onset above the drift). Outcome
[VERIFIED from `d3_ic.json`, `checks.json` of the run]:
- Model King b = 1, y0 = 0.26: alpha_c = 0.71884 (Z_c = 0.39113), E_b/M0 = 0.034169,
  R = 15.286 M, rbar_s = 14.268 M, M0 = 1.035378.
- Distance from the Juttner-Gamma_1 fluid onset of the King family (alpha_c = 0.67067,
  y0 = 0.321433, run C-20261119-151502-cb831a8 `rv_king_onset.json`, J_E_N1200): +0.04817 in
  alpha_c, 1.44 times the largest drift of the collisionless controls (cc1_kninf 0.03342,
  cc2_kninf 0.01853: `alpha_c_max_dev_from_start` of run C-20261115-191420-8538aa4) and 8.7
  times CC2's distance (+0.00556). y0 = 0.27 would give about 0.039 (1.2 times the drift)
  and 0.28 about 0.03 (below it), from the sequence in the same JSON [JUDGEMENT: 0.26 is the
  most compact model of the range that clears the larger drift with a margin].
- Particle file: 1e5 equal masses M0/N, net momentum below 7e-18, largest E/E0 = 0.99994,
  sum m W/psi - 1 = -2.8e-5, particles out to rbar = 13.82 M. All 18 pass/fail checks of
  `check_model` pass (matching, TOV 2.0e-7, Hamiltonian constraint of the table 3.6e-8,
  round trip, ECDF deviations exactly 1/N, equal-mass shells, shell moments max z 2.14 and
  1.18 for the two samplers).
- K = 1/(rho0_c H_c) = 251.509 (the decks' definition, `threshold_scan/common.kn_constant`);
  `equilibria/knudsen.model_conversion` gives (Kn sigma~)_l/(l/lambda) = 190.654/0.75804 =
  the same K to 1.1e-13. sigma~ = 25.1509 (Kn = 10) and 251.509 (Kn = 1).
- Expected collisions per particle in 300 M at the initial rate (knudsen.py nu_bar): 2.06
  (Kn = 10) and 20.6 (Kn = 1); for CC2 by the same code 2.28 and 22.8 (wave-2 prediction of
  `threshold_scan` entry 2: 2.27 and 22.7). t_d (coordinate, centre) 7.92 M against 6.91 M.
- Figure `fig_d3_model.png` of the run: looked at; the inset hid the peak of the energy
  histogram and is moved in `make_d3_ic.py` (mode `--from`, which also writes the fraction
  of particles inside the M/4 region); rerun registered below.

Decks `inputs/d3_kninf.athinput`, `d3_kn10_part_s1`, `d3_kn1_part_s1` (from the CC2 decks:
only the header, problem name, particle and table files, sigma~, coll_energy differ; diff
checked) and lists `inputs/d3_job3.list` (d3_kninf, d3_kn1_part_s1) and `d3_job4.list`
(d3_kn10_part_s1, cc2_kn10_cell_s2).

Prediction for the analysis script on the wave-2 runs (`scripts/analyze_decisive.py`, no
D1 output yet): it reproduces the reviewed numbers, t_c = 206.75 and 184.25 M (cc2_kn10,
cc1_kn10), 77.75 and 72.5 M (Kn = 1); t(dalpha >= 0.01) = 44-46 M at Kn = 10 and 20-21 M at
Kn = 1 (L16); collisions per particle before t_c 2.88, 2.48, 15.3, 13.4; summed
dE_particles to t_c 2.2e-4 and 1.8e-4 of sum M W at Kn = 10 (threshold_scan entry 6, P3.4);
first-step sum_P 23.69597, 24.41630. Refuted by any difference beyond the rounding of the
quoted digits: then the script misreads the histories.

## 2026-11-20 22:30 UTC Entry 4: outcome of the analysis test; D3 geometry; prediction D3

Analysis test, run C-20261120-222941-595c263 (`analyze_decisive.py` on the six wave-2 runs;
figures `fig_d1_lapse.png`, `fig_d1_budget.png`, `fig_controls.png` looked at): PASS. t_c =
206.75, 184.25, 77.75, 72.5 M; t(dalpha >= 0.01) = 46.0 and 44.25 M (Kn = 10), 21.25 and
20.25 M (Kn = 1); collisions per particle before t_c 2.882, 2.483, 15.26, 13.44; summed
dE_particles to t_c 2.16e-4 and 1.77e-4 (Kn = 10), 1.75e-3 and 1.57e-3 (Kn = 1); first-step
sum_P 23.695968, 24.416303; per collision in the first 25 M 0.22e-10, 0.88e-10, 1.24e-10,
1.22e-10 (threshold_scan entry 6: 0.22, 0.88, 1.24, 1.22): all as quoted. New numbers of the
wave-2 cell-mode seed-1 runs, the D1 reference: D50 = 0.0118 and 0.0131, D100 = 0.0426 and
0.0507 (CC2, CC1 at Kn = 10), early slope of dalpha over 0-100 M 4.43e-4 and 5.12e-4 per M;
at Kn = 1 D25 = 0.0170 and 0.0185, D50 = 0.0991 and 0.1134. The controls' alpha_c at 100 M
lies 0.0108 (CC2) and 0.0163 (CC1) above its start (part of every dalpha).

D3 geometry, run C-20261120-222949-2712568 (figure `fig_d3_model.png` looked at: the file's
energy distribution and mass profile follow the model; D3 sits above the band onset +
largest drift): fraction of particles inside the M/4 region |x|_inf < 8 M is 0.9737 for D3
and 0.9891 for CC2; D3 particles reach rbar = 13.8 M (cells of M/2 beyond 8 M, as for CC2's
outer 1 percent).

Prediction D3 (runs d3_kninf, d3_kn10_part_s1, d3_kn1_part_s1; written before submission).
The hypothesis under test (REVIEW-wave2 section 7, [JUDGEMENT]): collisions carry heat out of
the King core and the core contracts (gravothermal); a model on the stable side contracts
relative to its control at a rate comparable to CC2's and collapses later in proportion to
its distance from the onset.
(D3a) Control d3_kninf: every particle kept, no collapse; outward excursion of alpha_c smaller
    than CC2's: largest |alpha_c - alpha_c(0)| between 0.003 and 0.018 [JUDGEMENT: the drift
    grew from 0.0185 to 0.0334 between CC2 and CC1, towards the threshold]. If it exceeds
    0.048 (D3's distance from the onset) the model is not cleanly on the stable side of the
    numerical equilibrium either.
(D3b) Kn = 10: dalpha > 0 from the first tens of M; D100 between 0.015 and 0.09 (CC2 cell
    0.043; "comparable" read as within a factor 3; D3's initial collision rate is 0.9 times
    CC2's and its t_d 1.15 times longer, so the expected value is 0.03); t(dalpha >= 0.01)
    between 30 and 110 M (CC2 46 M).
(D3c) Kn = 1: D25 between 0.006 and 0.05, D50 between 0.03 and 0.25 (CC2 cell 0.017, 0.099);
    t(dalpha >= 0.01) between 12 and 45 M (CC2 21 M).
(D3d) Collapse. The proportional form gives t_c = 8.7 x CC2's: 1800 M at Kn = 10 and 680 M
    at Kn = 1, so no collapse within 300 M in either run. My own expectation differs at Kn = 1
    [JUDGEMENT, 50 percent]: CC2's relative contraction at Kn = 1 grew by a factor three in
    10 M (dalpha 0.01 at 21 M, 0.03 at 31 M), a runaway; D3 then needs only a few more
    e-folds, and alpha_min < 0.3 before 300 M is as likely as not. At Kn = 10 I expect no
    collapse within 300 M (80 percent).
(D3e) Budget and statistics as D1 (f), (g), (h): particle-mode collision-step change of sum
    M H_p below 1e-13 before excision, n_noroot = 0, n_balance below 1e-3 of the collisions;
    first-step sum_P within 3 pairing sd of the expectation (to be computed from the file
    at the time of the analysis; not predicted numerically here); collisions per particle
    in the first 25 M within 10 percent of the initial-rate value (2.06 and 20.6 per 300 M:
    0.172 and 1.72 in 25 M).
Refutation of the hypothesis: no relative contraction, i.e. dalpha at 100 M below 0.005 at
Kn = 10 (an order of magnitude below CC2) and D50 below 0.005 at Kn = 1, or dalpha of either
sign that stays within the scatter of D1 (b). A relative contraction with a collapse within
300 M at Kn = 10 would refute the "later in proportion" clause and mean that the collisional
runs collapse whatever the King model on this mesh, which would point at the method
(collision cells of M/4 with 2.3 particles, heat transport at the cell size) rather than at
the onset [JUDGEMENT].

## 2026-11-20 22:34 UTC Entry 5: paused (locks/PAUSE present since about 22:33 UTC)

The pause flag appeared while I waited for D1 job 1 (`locks/PAUSE`: five-hour window at 97
percent). Per decision 0019 nothing new is submitted; job 4737 (run
C-20261120-221846-797bdbe) stays queued and may run on its own.

Where this package stands:
- Done: go/no-go (GO, entry 1); D1 decks and lists; predictions D1 (entry 2) and D3 (entry 4);
  D3 model built and checked (run C-20261120-222427-6b27eea), its figure and geometry (run
  C-20261120-222949-2712568); D3 decks and lists; analysis script tested on the wave-2 runs
  (run C-20261120-222941-595c263, PASS).
- Queued: D1 job 1, Slurm 4737, pending at 22:34 UTC behind core's two-card job 4733.
- Not submitted: D1 job 2 (`inputs/d1_job2.list`), D3 job 3 (`inputs/d3_job3.list`), D3 job 4
  (`inputs/d3_job4.list`, which also holds cc2_kn10_cell_s2 of D1). Commands in README
  "Pending". No D1 or D3 outcome exists yet; every prediction clause is open.
- On resuming: if 4737 has finished, close it (`harness/bin/nrpic-run finish
  C-20261120-221846-797bdbe`), run the analysis with `--batch C-20261120-221846-797bdbe`,
  record the outcomes of D1 (a), (b), (f), (g), (h) for CC2 particle mode and the cell s1
  reference, size the next job from the measured s per M, and submit the next list when
  fewer than two C-* jobs are queued (order: d1_job2, d3_job3, d3_job4). Card time so far:
  none used by this package (4737 not started); reserved 0.65.

## 2026-11-21 02:56 UTC Entry 6: resumed (batch of 2026-11-20 evening); D1 job 1 has run; job 2 sized and submitted

Pause flag absent (02:54, 02:56 UTC). D1 job 1 (run C-20261120-221846-797bdbe, Slurm 4737) ran
14:59:06-15:34:07 PST, 35.0 min, exit 0 for the smoke run and both 300 M runs
(`batch.list.status` of the run); closed with `nrpic-run finish` (commit 150872b5). Measured
cost [VERIFIED, `batch.list.status` times]: cc2_kn10_part_s1 1046 s, cc2_kn10_part_s2 1037 s
for 300 M (3.49 and 3.46 s per M; prediction (h): 3.4-3.7 s per M, holds), smoke 18 s; job
0.584 card-hours. The next jobs hold the same two 300 M runs, so --gpu-hours 0.65 and --wall
00:55:00 stay (a third run would need 52 min plus start-up, too close to the limit). Queue at
02:56 UTC: one job of the user (4754, F), no C-* job; drift's job 4741 completed at 16:30 PST.
Submitting D1 job 2 (CC1 pair) now; the analysis of job 1 follows while it waits.

## 2026-11-21 03:00 UTC Entry 7: outcome of D1 for CC2 (job 1, particle mode, seeds 1 and 2)

Runs: card run C-20261120-221846-797bdbe (cc2_kn10_part_s1, cc2_kn10_part_s2); analyses
C-20261121-025642-fb29332 (script as committed in entry 3/4) and C-20261121-025928-94def70
(script extended before it ran, commit "analysis adds sub-cadence crossing times ...": linear
crossing time of alpha_min between the 0.25 M records, budget columns up to t_c, the
instantaneous seed difference of dalpha(t), figure `fig_d1_diff.png`). The extensions were
made after I had seen the first output, because all three CC2 runs hit alpha_min < 0.3 in the
same 0.25 M record and the "before excision" budget of seed 2 contained the blow-up steps
(below). Figures looked at: `fig_d1_lapse.png`, `fig_d1_diff.png`, `fig_d1_budget.png` of
run C-20261121-025928-94def70. Reference: wave-2 cc2_kn10 (cell, seed 1, release
executable, run C-20261115-171059-35441e3). Numbers below [VERIFIED] from `summary.json` of
C-20261121-025928-94def70 unless stated.

| quantity | cell s1 (wave 2) | part s1 | part s2 |
|---|---|---|---|
| t_c, record of alpha_min < 0.3 (M) | 206.75 | 206.75 | 206.75 |
| t_c, linear crossing (M) | 206.663 | 206.556 | 206.728 |
| alpha_min = 0.5 / 0.4 crossing (M) | 188.48 / 200.18 | 188.06 / 200.07 | 188.53 / 200.32 |
| D25 / D50 / D100 / D150 | 0.00226 / 0.01184 / 0.04264 / 0.09139 | 0.00236 / 0.01155 / 0.04231 / 0.09057 | 0.00196 / 0.01193 / 0.04235 / 0.09212 |
| t(dalpha >= 0.01), t(dalpha >= 0.03) (M) | 46.0, 81.75 | 46.5, 82.25 | 45.75, 80.75 |
| collisions per particle before t_c | 2.8816 | 2.8917 | 2.8931 |
| count z before t_c | -2.82 | -1.95 | -1.46 |
| first-step sum_P (n_coll) | 23.69597 (28) | 23.69485 (28) | 23.76635 (14) |
| first excision (M) | 216.5 | 216.0 | 216.25 |
| cost (s per M) | 3.45 | 3.48 | 3.45 |

Instantaneous difference of dalpha(t) (`curve_scatter`): part s2 - part s1 rms 6.3e-4 over
0-100 M and 1.7e-3 over 100-196 M, largest |.| 3.4e-3; part - cell s1: rms 3.3e-4 and 5.2e-4
(0-100 M), 1.2e-3 and 1.4e-3 (100-196 M); mean over 0-196 M -6.5e-5 and +4.8e-4. The
differences oscillate on a time scale of about 10 M (figure `fig_d1_diff.png`) and do not
accumulate: the three alpha_min curves lie on top of each other through 195-211 M.

Against prediction D1 (entry 2):
- (a) Early contraction unchanged: HOLDS. D100 part mean 0.04233 against cell 0.04264,
  difference -3.1e-4, below the bound 2e-3. The expected sign (particle contracts more)
  FAILED as a sign: the difference is negative at 100 M, positive in the 0-196 M mean of
  part s2 and negative in that of part s1; with the measured curve scatter (rms 0.6-1.7e-3)
  the sign is not resolved. The analysis' z = -9 of D100 uses the one-draw D100 difference of
  the two seeds (4.9e-5) as sigma, which the curve scatter shows to be a chance small value
  [JUDGEMENT]; it is not evidence of a mode effect.
- (b) Seed scatter of the early drop about 1e-3 (band 2e-4 to 4e-3): FAILED as written for
  the window mean, |D100(s1) - D100(s2)| = 4.9e-5 (|D50| difference 3.8e-4, |D25| 3.9e-4);
  the instantaneous seed difference has rms 6.3e-4 over 0-100 M and 1.7e-3 over 100-196 M,
  inside the band. The window mean of one pair is a single draw of a quantity that
  oscillates about zero on 10 M; the rms is the usable scatter.
- (c) Collapse in particle mode before 300 M: HOLDS for CC2 (both seeds).
- (d) Seed scatter of the collapse time about 4 M (band 1-12 M): FAILED, smaller than the
  band: |t_c(s1) - t_c(s2)| = 0.17 M from the linear crossing (0 at the record cadence of
  0.25 M); 0.47 M and 0.25 M at alpha_min = 0.5 and 0.4. My basis (a lapse scatter of 1e-3
  divided by the early contraction rate) assumed that a lapse offset persists; it does not:
  the offsets oscillate and average out, and the time of the runaway is set by the
  collision-averaged heat flow, whose relative noise with about 1.4e5 collisions is small
  [JUDGEMENT]. Consequence: at N = 1e5 and Kn = 10 one seed gives the collapse time of CC2
  to about 0.2 M (0.1 percent); later collisional comparisons need no second seed for t_c.
- (e) Effect of the defect on the late phase: t_c(part) - t_c(cell) = -0.02 M (linear
  crossing, means of the two seeds against cell s1), inside the predicted -15 to +3 M; the
  central value -5 M FAILED (no shift). Far below the criterion of a cause (6 M): the energy
  defect of the release operator is NOT a cause of the collapse of CC2 at Kn = 10, and does
  not move its time. Pending: cell-mode seed 2 (job 4) for the cell scatter.
- (f) Budget, particle mode, judged to t_c (the excision record of `cc.nrpic.hst` comes every
  4 cycles; in seed 2 the two collision steps before the excision record, 216.06 and
  216.125 M, are those of the blow-up, sum_MH_particles 57 and 200 times its start): summed
  dH_particles at most 3.1e-16 and 3.2e-16 of sum_MH_particles(0) = 0.87405 to t_c (4.1e-16
  and 4.3e-16 to the excision): HOLDS (bound 1e-13). Per collision +1.88e-21 and +1.91e-21 M
  (predicted about 2e-21): HOLDS. "One-signed": FAILED as written: 17 and 20 of the steps
  before t_c have a negative change, at most -7.3e-21 and -1.7e-20 M against positive steps
  up to 5e-19 M; the cumulative sum stays positive throughout (smallest 4.5e-20 and
  1.6e-20 M). n_noroot = 0 to t_c: HOLDS; the first pairs without a root come at 209.0 and
  209.3 M, after t_c, and 2046 and 2068 by the excision: FAILED for the clause "before the
  first excision". n_balance at most 1e-3 of the collisions: holds to 150 M (3.6e-4 and
  3.1e-4 to 100 M, 5.1e-4 and 4.3e-4 to 150 M), FAILED to t_c (2.9e-3 and 3.0e-3) and to the
  excision (2.6e-2); core's tests reach 2.3e-2 at theta = 0.2-0.3 (interface section 11.5),
  so the rise as the core heats is the operator's design, not a fault [JUDGEMENT].
  max_dlam below 0.05: holds to 150 M (1.0e-2 and 5.4e-3), FAILED to t_c (0.197, 0.209) and
  to the excision (23, 26). sum_MH_particles itself: -0.99 and -1.02 percent at 100 M
  (-0.0087 M), -20 percent at t_c; the predicted magnitude "up to 1e-2 M by 200 M" FAILED
  (-0.11 M at 200 M): in the runaway the potential deepens and H = alpha W - beta.u of the
  particles falls with it; the collision steps' own change stays at 3e-16. Cell part of (f):
  pending (job 4).
- (g) Collision statistics: collisions per particle before t_c 2.892 and 2.893 against the
  scaled wave-2 value 2.88: HOLDS (0.4 percent). |z| = 1.95 and 1.46 < 4: HOLDS. First-step
  sum_P of part s1 23.69485, 4.7e-5 relative from the wave-2 seed-1 value: HOLDS (bound
  2e-3); part s2 23.76635, 1.5 pairing sd from 23.692: HOLDS. n_trunc = 0: HOLDS. Not
  predicted: particle mode collides 0.37 percent more than cell s1 before t_c (2.892 against
  2.882); one cell seed only, so the cell scatter is not known yet (job 4).
- (h) Rest mass bit-identical before the first excision: HOLDS (both). Deposit identity
  2.1e-15 and 4.0e-15 < 1e-14: HOLDS. Cost 3.48 and 3.45 s per M: HOLDS. Card-hours 0.584
  per job against 0.63: HOLDS.

Not predicted, after the criterion: seed 2 became non-finite at 216.5 M (alpha_min -2.7e8 at
the record after the first excision, every particle excised by 220 M), seed 1 ran to 300 M
with 96 percent of the mass excised and alpha_min 0.050; wave-2 cc2_kn10 ran to 300 M, cc1_kn10
became non-finite at 289.5 M. The phase after the first excision is fragile in both modes
(RISKS item on excision; core READY: coll_energy with excision untested); D1 measures nothing
there.

## 2026-11-21 03:00 UTC Entry 8: sharpened predictions for jobs 2-4 (written before they run)

Entry 2 and entry 4 stay the predictions of record; these add sharper clauses from the CC2
outcome (entry 7) [JUDGEMENT throughout]. References (analysis C-20261121-025928-94def70):
wave-2 cc1_kn10 (cell s1) has linear crossings alpha_min = 0.5, 0.4, 0.3 at 166.22, 177.81,
184.02 M, D100 = 0.0507, 2.483 collisions per particle before t_c; cc2_kn10 cell s1 206.66 M.

- (D1-CC1, job 2) Both CC1 particle runs: t_c (linear crossing) within 1.0 M of 184.02 M, and
  |t_c(s1) - t_c(s2)| < 1.0 M; the instantaneous seed difference of dalpha has rms below
  2e-3 over 0-100 M; collisions per particle before t_c within 1 percent of
  2.483 x t_c/184.25 (CC2: +0.4 percent); summed dH to t_c below 1e-15 of sum_MH_particles,
  n_noroot = 0 to t_c. Refuted by a shift of the CC1 collapse beyond 1 M, which would make
  the threshold model, unlike CC2, sensitive to the operator or to the realisation.
- (D1-cell, job 4) cc2_kn10_cell_s2: t_c within 0.5 M of cell s1 (206.66 M) and of the
  particle mean (206.64 M); the cell seed difference of collisions per particle before t_c
  below 0.2 percent, which would make the particle-cell difference of +0.37 percent (entry 7)
  a mode effect. Summed dE_particles to t_c within a factor 2 of seed 1 (2.16e-4).
- (D3) With the seed scatter of entry 7, one seed resolves dalpha to about 1e-3 (rms of the
  instantaneous seed difference) and a collapse time to about 0.5 M; the clauses of entry 4
  are judged against these. d3_kninf also gives drift's third period point (drift JOURNAL
  entry 6, its prediction, judged by drift or the lead).

## 2026-11-21 03:23 UTC Entry 9: job 2 running; a cosine fit of the controls (prediction)

D1 job 2 (run C-20261121-025633-bb8dac4, Slurm 4756) started 03:22 UTC; smoke run rc = 0.
While it runs: `analyze_decisive.py` gets the cosine form A (1 - cos 2 pi t/P) + c of
`drift/scripts/controls.py` (copied, not imported) for every Kn = inf control, so that the
d3_kninf control yields the third point of the excursion period that drift asked for (drift
JOURNAL entry 6; drift's own prediction for it is drift's to judge).
Prediction for the test on the wave-2 controls: the fit to alpha_c(t) - alpha_c(0) over
0-300 M reproduces drift's values (run C-20261120-222211-aa1be86, drift's report): P = 399 M
and A = 0.0154 (CC1), P = 355 M and A = 0.0086 (CC2), to the quoted digits. Refuted by any
difference beyond them: then the fitted series differs from drift's.
Outcome (development run of the script in `scratch/C-sidm/tmp/decisive_test/`, unregistered;
the registered analysis after job 2 repeats it): CC1 P = 399.24(31) M, A = 0.015409(35); CC2
P = 355.44(41) M, A = 0.008586(35); rms of the residual 8e-4. HOLDS: drift's values to the
quoted digits. Figure `fig_controls.png` looked at: the dashed fits follow both controls; the
largest rise of alpha_c is 0.0334 at 201.5 M (CC1) and 0.0185 at 206.75 M (CC2).

## 2026-11-21 03:59 UTC Entry 10: outcome of D1 for CC1 (job 2); job 3 submitted; job 5 added

D1 job 2 (run C-20261121-025633-bb8dac4, Slurm 4756) ran 03:22:34-03:57:15 UTC, exit 0 for the
smoke run and both runs (1039 and 1036 s for 300 M); closed with `nrpic-run finish`. D3 job 3
(d3_kninf, d3_kn1_part_s1) submitted at 03:57 UTC as run C-20261121-035737-295e5c3, Slurm
4764 (no other C-* job in the queue). Analysis C-20261121-035741-b3595d4 (jobs 1 and 2, the
wave-2 runs; figures `fig_d1_lapse.png`, `fig_d1_diff.png`, `fig_d1_budget.png`,
`fig_controls.png` looked at). Numbers [VERIFIED] from its `summary.json`.

| quantity | cell s1 (wave 2) | part s1 | part s2 |
|---|---|---|---|
| t_c record / linear crossing (M) | 184.25 / 184.018 | 185.0 / 184.928 | 186.0 / 185.847 |
| alpha_min = 0.5 / 0.4 crossing (M) | 166.22 / 177.81 | 166.90 / 178.54 | 167.79 / 179.51 |
| D25 / D50 / D100 / D150 | 0.00259 / 0.01311 / 0.05069 / 0.1288 | 0.00260 / 0.01334 / 0.04917 / 0.1253 | 0.00281 / 0.01388 / 0.04878 / 0.1244 |
| t(dalpha >= 0.01), t(dalpha >= 0.03) (M) | 44.25, 76.5 | 45.0, 77.75 | 43.25, 76.5 |
| collisions per particle before t_c (count z) | 2.4828 (-0.30) | 2.4888 (-0.75) | 2.4956 (-1.83) |
| first-step sum_P (n_coll) | 24.41630 (31) | 24.41389 (31) | 24.39603 (27) |
| first excision; non-finite (M) | 193.75; 289.5 | 194.5; none to 300 | 195.25; 249.75 |

Curve scatter: part s2 - part s1 rms 5.9e-4 (0-100 M), 2.8e-3 (100-175 M); part - cell s1
mean over 100-174 M -2.0e-3 and -3.6e-3 (both particle seeds below the cell run from about 95 M,
figure `fig_d1_diff.png`, right).

Against entry 2 and entry 8 (CC1):
- (a) D100 part mean 0.04898 against cell 0.05069: -1.7e-3, inside the bound 2e-3: HOLDS,
  narrowly; sign "particle contracts more": FAILED (it contracts less, as in CC2).
- (b) |D100(s1) - D100(s2)| = 3.9e-4, inside 2e-4 to 4e-3: HOLDS for CC1; curve rms 5.9e-4.
- (c) both CC1 particle runs reach alpha_min < 0.3 before 300 M: HOLDS.
- (d) seed scatter of t_c about 4 M (band 1-12 M): 0.92 M: FAILED, just below the band. The
  scatter is five times that of CC2 (0.17 M).
- (e) t_c(part mean) - t_c(cell s1) = +1.37 M: inside -15 to +3 M: HOLDS; central value -5 M
  FAILED (sign opposite: particle later). Below the cause criterion (6 M, the measured scatter
  being below 2 M): the defect is not a cause of the CC1 collapse. The shift is 2.1 times the
  sigma from the particle seeds alone (0.65 M); one cell seed, so a mode effect of about 1 M
  (0.7 percent of t_c) is neither shown nor excluded.
- (f) particle budget to t_c: summed dH at most 2.8e-16 and 2.85e-16 of sum M H (HOLDS), +1.96e-21
  and +1.98e-21 M per collision (HOLDS), one-signed FAILED (14 and 12 negative steps, at most
  -3.1e-20 M; cumulative sum positive throughout), n_noroot = 0 to t_c (HOLDS; first at 188.5
  and 188.75 M, 1787 and 1783 by the excision: FAILED for "to the first excision"), n_balance
  6.0e-4 and 5.4e-4 to 150 M (HOLDS), 2.9e-3 and 3.2e-3 to t_c (FAILED), max_dlam 8.6e-3 and
  7.6e-3 to 150 M (HOLDS), 0.22 and 0.19 to t_c (FAILED); sum M H -1.07 percent at 100 M, -20
  percent at t_c (magnitude clause FAILED as for CC2).
- (g) collisions per particle before t_c 2.489 and 2.496 against the scaled 2.493 and 2.507:
  HOLDS (-0.2, -0.4 percent; entry 8: within 1 percent, HOLDS); |z| < 4: HOLDS; first-step
  sum_P of s1 9.9e-5 relative from wave 2 (HOLDS), s2 0.3 pairing sd (HOLDS); n_trunc = 0.
- (h) rest mass bit-identical before excision, deposit identity 2.4e-15 and 2.7e-15, cost 3.45
  and 3.44 s per M: HOLD.
- Entry 8 (D1-CC1): both t_c within 1.0 M of 184.02 M: FAILED for s2 (+1.83 M; s1 +0.91 M);
  |t_c(s1) - t_c(s2)| < 1.0 M: HOLDS (0.92); rms of the seed difference over 0-100 M below
  2e-3: HOLDS (5.9e-4); dH and n_noroot clauses: HOLD. Its refutation clause is met: the mean
  particle-mode collapse moved by more than 1 M, so the threshold model is more sensitive than
  CC2 to the realisation or to the operator (seed scatter 0.92 against 0.17 M) [VERIFIED for the
  realisation; the operator part needs the cell scatter].

Reading [JUDGEMENT]: near the collisionless threshold a fixed perturbation shifts the collapse
time more, so the realisation matters more for CC1 than for CC2; the systematic offset of both
particle seeds from the one cell run (from 95 M on) is what a mode effect would look like, but
one cell seed cannot tell it from that run's own realisation.

Job 5 (added; within the cap): `inputs/d1_job5.list` = cc1_kn10_cell_s2, cc1_kn10_cell_s3 (decks
from `scripts/decks.py d1`, the wave-2 CC1 deck with rng_seed 2 and 3 and `coll_energy = cell`,
which leaves the particles' evolution that of the release operator; card executable of
collisions-2 as for every run here). Package total with it: 5 jobs x 0.58 = 2.9 card-hours of
allocation (cap 3.0). Submitted after job 4, one job at a time.
Prediction for job 5 [JUDGEMENT]: the two cell seeds have t_c (linear crossing) within 1.5 M of
each other and of 184.02 M; their mean lies 0.5-2 M before the particle mean 185.39 M if the
offset is a mode effect. Decision rule: with the three cell values, the mode effect is
|mean(part) - mean(cell)| against sigma = sqrt(s_cell^2/3 + s_part^2/2), s the sample
standard deviations; a mode effect is shown if the ratio exceeds 3, excluded at the 1 M level
if the difference is below 0.5 M.
Processor work while job 3 waits (04:05 UTC): the D3 branch of `analyze_decisive.py` (never
run on D3 output) tested on a mock, CC2 histories linked under D3 names in
`scratch/C-sidm/tmp/d3mock/` (unregistered development run): it reads the runs, takes the
`d3_kninf` control, writes `fig_d3_contraction.png` (now three panels: dalpha against t and
against collisions per particle, alpha_min against t); looked at; the D3 numbers it printed are
the CC2 numbers, as they must be. Queue rule kept: one job of this package at a time.

## 2026-11-21 05:28 UTC Entry 11: outcome of D3 job 3 (control and Kn = 1); job 4 submitted

D3 job 3 (run C-20261121-035737-295e5c3, Slurm 4764) ran 04:49:44-05:25:35 UTC, exit 0 for the
smoke run, d3_kninf (1054 s) and d3_kn1_part_s1 (1079 s); closed with `nrpic-run finish`. D3 job
4 (d3_kn10_part_s1, cc2_kn10_cell_s2) submitted at 05:27 UTC as run C-20261121-052716-6b64f97,
Slurm 4767. Analysis C-20261121-052720-75f3fff (jobs 1-3 and the wave-2 runs; figures
`fig_d3_contraction.png`, `fig_controls.png` looked at). Numbers [VERIFIED] from its
`summary.json`, except the lines marked (arithmetic), computed in this session from the same
histories by the reader of `threshold_scan/common.py` (corrected count z, dalpha at fixed
collisions per particle; not a registered run, repeated by the final analysis only in part).

Control d3_kninf: alpha_c(0) = 0.71927; largest |alpha_c - alpha_c(0)| = 0.00529 (at 152 M),
+0.0026 at 100 M; cosine fit P = 282.3(1.2) M, A = 0.00221 (rms of the residual 7.5e-4); every
particle kept; rest mass bit-identical; deposit identity 1.0e-15; 3.50 s per M.
- (D3a) largest excursion between 0.003 and 0.018: HOLDS (0.0053); far below D3's distance from
  the onset (0.048): D3 is cleanly on the stable side of the numerical equilibrium too.
- For drift (its JOURNAL entry 6, its prediction, its verdict): the third period point is
  P(y0 = 0.26) = 282 M with A = 0.0022 (CC2 355 M, A = 0.0086; CC1 399 M, A = 0.0154), in the
  cosine form of `drift/scripts/controls.py` on 0-300 M; with less than one period in 300 M and
  A only three times the residual rms, the period carries the fit-form error drift found (4-10
  percent) or more [JUDGEMENT].

d3_kn1_part_s1 (K = 251.509, sigma~ = 251.509):

| quantity | D3 Kn = 1 (particle) | CC2 Kn = 1 (cell, wave 2) | CC1 Kn = 1 (cell, wave 2) |
|---|---|---|---|
| t_c record / linear crossing (M) | 100.5 / 100.46 | 77.75 / 77.75 | 72.5 / 72.43 |
| alpha_min = 0.5 / 0.4 crossing (M) | 83.29 / 92.82 | 62.52 / 71.30 | 57.43 / 66.10 |
| D25 / D50 | 0.0094 / 0.0613 | 0.0170 / 0.0991 | 0.0185 / 0.1134 |
| t(dalpha >= 0.01), t(dalpha >= 0.03) (M) | 26.0, 38.5 | 21.25, 31.25 | 20.25, 30.75 |
| slope of dalpha over 0-100 M (per M) | 3.57e-3 | 6.36e-3 | 6.49e-3 |
| collisions per particle to t_c | 23.86 | 15.26 | 13.44 |
| dalpha at 2 / 3 / 5 collisions per particle (arithmetic) | 0.0136 / 0.0356 / 0.0844 | 0.0177 / 0.0424 / 0.1036 | 0.0181 / 0.0444 / 0.1097 |
| first excision; non-finite (M) | 115.5; 153.5 | 88.75; 162.25 | 83.25; 204.25 |

Against prediction D3 (entry 4) and entry 8:
- (D3c) D25 between 0.006 and 0.05: HOLDS (0.0094); D50 between 0.03 and 0.25: HOLDS (0.0613);
  t(dalpha >= 0.01) between 12 and 45 M: HOLDS (26.0 M). D3 contracts relative to its control
  at 0.56 of CC2's early rate: "comparable" (within a factor 3) HOLDS.
- (D3d) Collapse at Kn = 1: the proportional form (t_c = 8.7 x CC2's = 680 M, no collapse in
  300 M) FAILED: t_c = 100.46 M, 1.29 times CC2's 77.75 M (in collisions per particle 23.6
  against 15.1, 1.56 times). My own 50 percent expectation of a collapse before 300 M came true.
- Refutation clause of the hypothesis (no relative contraction, D50 < 0.005 at Kn = 1): not met;
  the relative contraction is there and large (D50 = 0.061, 12 times the bound).
- So: the gravothermal clause "contracts relative to its control at a rate comparable to CC2's"
  HOLDS; the clause "collapses later in proportion to its distance from the onset" is REFUTED at
  Kn = 1 (8.7 times the distance, 1.29 times the time).
- (D3e) particle budget to t_c: summed dH 2.5e-15 of sum M H (HOLDS, bound 1e-13), +1.87e-21 M
  per collision; no negative step before t_c (one-signed HOLDS here); n_noroot = 1 before t_c
  (at 98.3 M, alpha_min about 0.33; 24372 by the excision at 115.5 M): FAILED by one pair;
  n_balance 6.5e-3 of the collisions to 100 M and 7.1e-3 to t_c: FAILED (bound 1e-3; core's
  tests reach 2.3e-2 at theta 0.2-0.3); max_dlam 0.77 before t_c: FAILED. Collisions per
  particle in the first 25 M 1.7185 against the initial-rate value 1.72: HOLDS (0.1 percent).
  First-step sum_P 214.00 against 214.6 from knudsen's initial rate (20.6 per particle per
  300 M x 0.0625 M x 1e5/2; arithmetic): 0.3 percent. Count z before t_c -9.88 (FAILED as a
  "|z| < 4" clause of D1 (g)); with the 8309 balance rejections and the one pair without root
  added back to the collisions (arithmetic) z = -2.29: the deficit is the operator's
  detailed-balance rejection, by design (n_coll counts accepted collisions, sum_P the
  proposals). The same correction moves the Kn = 10 particle runs from z = -1.8..-0.75 to
  -0.8..+0.3 (arithmetic).
- (h) rest mass bit-identical before the first excision, deposit identity 2.0e-15: HOLD; cost 3.59
  s per M (3.4-3.7: HOLDS).

Reading [JUDGEMENT]: at Kn = 1 the relative contraction per collision is nearly the same for
D3, CC2 and CC1 (dalpha at 3 collisions per particle 0.036, 0.042, 0.044; the curves against
collisions per particle lie on top of each other, `fig_d3_contraction.png`, middle), and the
collapse follows after 13-24 collisions per particle whatever the model's distance from the
relativistic onset (8.7 times larger for D3 than for CC2). The collapse of these collisional
runs is therefore set by the collisional (gravothermal) contraction, the relativistic onset
deciding at most the last few percent of it; the wave-2 reading "CC2 collapses because it lies
near the onset" is not supported. Whether the contraction rate itself is physical or set by the
method (collision cells of M/4, heat transport at the cell size) is D2's question.

## 2026-11-21 05:49 UTC Entry 12: sharpened prediction for d3_kn10_part_s1 (job 4 running, output not looked at)

Job 4 (run C-20261121-052716-6b64f97, Slurm 4767) started at 05:48 UTC. Entry 4 (D3b, D3d) stays
the prediction of record; from the Kn = 1 outcome (entry 11) I add [JUDGEMENT]: D3 contracted at
0.56 of CC2's early rate at Kn = 1; at Kn = 10 the same ratio gives D100 = 0.024 (band
0.012-0.040; CC2 0.0426) and t(dalpha >= 0.01) in 50-90 M (CC2 46 M). The collapse time scales
either with time (1.29 x CC2's 206.6 M = 267 M) or with collisions per particle (1.56 x 2.88 =
4.5 per particle, more than D3 collects in 300 M at Kn = 10); I give 50 percent to a collapse
before 300 M, and if it comes, after 240 M. A collapse before 240 M, or D100 above 0.040, would
mean that at Kn = 10 the model's distance from the onset matters even less than at Kn = 1.

## 2026-11-21 06:25 UTC Entry 13: outcome of job 4 (D3 at Kn = 10, CC2 cell seed 2); job 5 submitted

Job 4 (run C-20261121-052716-6b64f97, Slurm 4767) ran 05:48:36-06:23:47 UTC (35.2 min), exit 0
for the smoke run, d3_kn10_part_s1 (1065 s) and cc2_kn10_cell_s2 (1040 s); closed with
`nrpic-run finish`. Job 5 (cc1_kn10_cell_s2, cc1_kn10_cell_s3) submitted at 06:24 UTC as run
C-20261121-062408-49fa14a, Slurm 4770, pending behind two jobs that hold both cards (one of them
another user's) until about 07:15-07:25 UTC. Analysis C-20261121-062412-7473ef1 (jobs 1-4 and the
wave-2 runs; figures `fig_d3_contraction.png`, `fig_d1_diff.png`, `fig_d1_lapse.png`,
`fig_d1_budget.png`, `fig_controls.png` looked at). Numbers [VERIFIED] from its `summary.json`
unless marked (arithmetic).

d3_kn10_part_s1 (sigma~ = 25.1509): no collapse in 300 M (alpha_min 0.656 at 300 M, alpha_c
0.719 -> 0.656); D25 / D50 / D100 / D150 = 0.00145 / 0.00783 / 0.0258 / 0.0393; dalpha 0.046 at
200 M, 0.051 at 250 M, 0.063 at 290-300 M; t(dalpha >= 0.01) = 57.0 M, t(dalpha >= 0.03) = 118 M;
2.875 collisions per particle in 300 M (CC2 collapsed after 2.88), 0.1719 in the first 25 M;
first-step sum_P 21.402 (knudsen's initial rate gives 21.46, arithmetic: 0.3 percent); every
particle kept; summed dH 1.9e-16 of sum M H, +1.2e-21 M per collision, 80 negative steps;
n_noroot 0, n_balance 3.8e-4, max_dlam 3.4e-3 over the whole run; 3.54 s per M.
- (D3b) dalpha > 0 from the first tens of M: HOLDS; D100 in 0.015-0.09: HOLDS (0.0258); t(dalpha
  >= 0.01) in 30-110 M: HOLDS (57 M). Entry 12: D100 0.024 (0.012-0.040): HOLDS; t(0.01) in
  50-90 M: HOLDS.
- (D3d) no collapse within 300 M at Kn = 10 (80 percent): HOLDS. Entry 12 gave a collapse 50
  percent; none came, which favours the scaling of the collapse with collisions per particle
  (D3 would need about 4.5, it collected 2.9) over the scaling with time (267 M) [JUDGEMENT].
- (D3e) budget and statistics: dH below 1e-13: HOLDS; n_noroot = 0 and n_balance below 1e-3: HOLD
  (to 300 M; D3 never got hot); one-signed: FAILED (80 negative steps of rounding); collisions in
  the first 25 M 0.1719 against 0.172: HOLDS; count z -0.72: HOLDS.
- The relative contraction of D3 at Kn = 10 is 0.61 of CC2's at 100 M and grows slower after
  150 M (part of the plateau at 170-250 M is the fall of the control's own excursion after its
  maximum at 152 M, which dalpha = alpha_c(control) - alpha_c contains) [JUDGEMENT from
  `fig_d3_contraction.png` and `fig_controls.png`].

cc2_kn10_cell_s2 (release operator, seed 2): t_c 206.5 M record, 206.258 M linear crossing
(cell s1 206.663; particle mean 206.642); D100 0.04397 (cell s1 0.04264); collisions per particle
before t_c 2.9178 (cell s1 2.8816); count z -0.50; first-step sum_P 23.76774 with 14 collisions
(particle s2, same seed: 23.76635 and 14); summed dE_particles to t_c 2.27e-4 of sum M W
(seed 1: 2.16e-4); with `coll_energy = cell` present the H budget is written as well: summed
dH_particles 1.58e-4 of sum M H to t_c, +9.1e-10 M per collision (+2.9e-10 M in the first 25 M),
against 3e-16 and 2e-21 M in particle mode.
- Entry 8 (D1-cell): t_c within 0.5 M of cell s1 and of the particle mean: HOLDS (0.40 and 0.38
  M). Cell seed difference of collisions per particle below 0.2 percent: FAILED (1.25 percent):
  the particle-cell difference of +0.37 percent (entry 7) lies inside the cell seed scatter and
  is not a mode effect. dE_particles to t_c within a factor 2 of seed 1: HOLDS (2.27e-4).
- Entry 2 (f), cell part: column 33 positive at 1-2.4e-10 M per collision in the first 25 M:
  FAILED narrowly (2.9e-10 M); summed dE_particles to t_c 1-4e-4 of sum M W: HOLDS.
- Entry 2 (a), (e) with both cell seeds (analysis `mode_comparison`): D100 part - cell
  -9.7e-4 with sigma_pooled 6.7e-4 (z = -1.5; bound 2e-3: HOLDS); t_c part - cell +0.18 M with
  sigma_pooled 0.22 M (z = 0.8): the defect does not move CC2's collapse (HOLDS). Cell-mode seed
  scatter of t_c 0.40 M (particle 0.17 M); instantaneous dalpha difference of the two cell seeds
  rms 9.1e-4 (0-100 M) and 2.4e-3 (100-196 M), as for the particle seeds.

## 2026-11-21 06:28 UTC Entry 14: package closed with job 5 pending

D1 and D3 as designed (REVIEW-wave2 section 7, the brief's runs) have run and are analysed
(entries 7, 10, 11, 13); README.md has the results table, the requests and the pending job.
Card time used: 2.34 card-hours of allocation (jobs 1-4, sacct elapsed 35:01, 34:41, 35:38,
35:11); job 5 (run C-20261121-062408-49fa14a, Slurm 4770) adds about 0.58 when it runs, 2.93 in
all, within the cap of 3.0. At 06:28 UTC both cards are held by other jobs until about
07:15-07:25 UTC, so job 5 will end after this session; its finish and analysis commands and the
decision rule for entry 10's prediction are in README "Pending". Nothing else of this package is
open on the cards. The pause flag was absent at every check of this session.
