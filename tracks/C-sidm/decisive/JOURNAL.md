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
