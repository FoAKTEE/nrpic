# Journal of the verify package (core, wave 1)

Predictions are written before the runs; outcomes are appended below them and never
edited away. Times are local (PST), 2026-11-15.

## 03:40 Setting, before any run

Executables (no build): card `/data/haiyangw/nrpic/.work/build_gpu_c3/src/athena`
(mtime 2026-11-14 08:31:30), processor `/data/haiyangw/nrpic/.work/build_cpu_c1/src/athena`
(mtime 2026-11-14 06:03:37). Neither records the source commit (`git-state.txt` holds the
Kokkos submodule commit 6739bc623). What I checked [VERIFIED, grep of the binaries]: the
card executable contains the option names `damp_kappa_gam` (added in 0c06525, 08:35:50,
the last commit touching `athenak/src`) and `damp_ch_chipow` (631cfe3); the processor
executable contains neither but does contain `cons_dcycle` and `bspline` (f219ade,
06:09:43). [JUDGEMENT] The card executable is built from the source of 0c06525 (the
current `athenak/src`), the processor executable from a state between f219ade and
631cfe3; for the geodesic test (no Z4c) the difference does not enter.

Defaults of the cosmology-era options are off (`athenak/src/particles/nrpic.cpp` lines
100-188: `source_density`, `source_extrap` false, `deposit_shape` cic, `interp` hermite,
`deposit_comp_*` 0, `dt_expansion` 0), so an asymptotically flat input runs the path of
core-v0.1 unless it asks otherwise.

## 03:45 Predictions of the four regression tests

**G, Kerr passage on processors** (11 runs, dt = 0.02, 0.01, 0.005 M for three pushers on
the analytic metric; midpoint and Boris-Cholesky on the Hermite lattice at 0.01 M).
Prediction: the largest relative errors of E, L_z, Q equal the earlier ones
(`problems/kerr/results/kerr_summary.json`; for dt = 0.01: 2.781e-8, 0, 1.254e-7;
9.046e-8, 1.136e-8, 7.825e-7; 2.162e-6, 5.304e-6, 5.060e-5; 2.046e-6, 3.788e-6, 5.289e-5)
to at least four digits; the pairwise orders in dt of the final position error equal
the earlier ones (1.9989 to 2.0003) to 1e-3; the two runs that exist from the earlier
processor build (`runs/geodesic/kerr_passage_cpu/`) are reproduced bitwise.
Refuted if any error moves by more than 1e-3 relative (a change in a pusher, the
analytic metric or the lattice reconstruction), or if the processor trajectories
differ by more than the earlier processor-card difference (1.8e-8).

**O, dust collapse on a card** (9328 lattice particles, surface-corrected masses, cloud
at the finest level, to t = 25 M; earlier run `runs/os/nocap_sc`, made on 2026-11-13 with
an executable of 07:06). Initial data regenerated with the current `make_ic.py`:
prediction bitwise identical to the earlier files (sha256 c6b2753b... and f2b5e5bf...).
Run: first apparent horizon at 16.39 M (within one search, 0.15 M), mass 1.0004; the
horizon mass within 3e-4 of the earlier run at every comparison and within 1e-3 of the
total mass throughout (the paper's order, main.tex line 945); all particles removed near
19.74 M; deposition identity at 1e-15; largest Hamiltonian-constraint norm 1.90 near
17.3 M. I expect the central lapse to agree with the earlier run to better than 1e-6
before the horizon forms, perhaps bitwise, because the defaults keep the old path; the
pass criterion is looser (1e-3, the size of a change of deposition rule). Refuted if the
horizon mass moves by more than 3e-4 or the lapse by more than 1e-3: that would mean a
later change (cosmology work) altered the asymptotically flat path.

**F, homogeneous universe on a card** (32^3, to a = 4; earlier `runs/cosmo/flrw_n32_cpu_sd`
on processors). Particles regenerated with the current `make_lattice.py`; I do not know
whether the default lattice placement is the one of the earlier file (the generator
gained a `--centred` switch); either placement deposits a uniform density. Prediction:
relative errors against the exact solution of the lapse 1.9e-7, density 1.1e-6, mean K
3.8e-7, proper volume 1.1e-6, each within a factor 1.1 of the earlier values (the same
Runge-Kutta errors; card against processor only changes round-off); the probe proper
time is now third order (cosmo/TESTLOG.md line 127), so its error drops from 4.0e-5 to
below 1e-6; history column H-norm2 below 3.7e-10 and Theta below 1.1e-11 as before;
all 32768 particles kept, the deposit exactly uniform. Refuted if any of the four
background errors grows by more than a factor two.

**L, linear growth on a card** (amplitude 1e-4, 32^3, to t = 9, a = 30.25; earlier
`runs/cosmo/east_d1e-4_n32_cpu` on processors). Initial data regenerated with the
current `make_east.py`; the solver gained an accelerated outer iteration and a
rounding-aware tolerance since the earlier run (commit 56ac61d), so I expect the files
to differ, by at most 1e-12 in the fields and particle data. Prediction: the observer
contrast is within 0.5 percent of linear theory at both probes to a_p = 30 (earlier
0.45 and 0.31 percent at most), and differs from the earlier run by less than 1e-4 of
the contrast; constraint norms at t = 0 of 6.0e-10 (Hamiltonian) and 7.6e-10
(momentum), within a factor 1.5. Refuted if the contrast departs from linear theory by
more than 0.5 percent or from the earlier run by more than 1e-3 of the contrast.

Card time: the earlier collapse reached t = 22 M in 251 s of a 1100 s run to 60 M
(`runs/os/nocap_sc/athena.20261113-070659.log`); the two cosmology runs are 32^3. Expected
total under 0.25 card-hours, against the 2 card-hours of the package.

Correction (03:55): the clock times of the two entries above are wrong; both were
written before any run and committed in 45e1779 at 03:26, before job 4342 was
submitted (03:26) and before the geodesic runs (03:26).

## 03:55 Outcomes of the first regression pass

**G** (`core-20261115-032625-45e1779`, processors, 11 runs, 13 s): 104 of 104 checks pass.
Invariant errors equal the earlier card values to 2e-5 relative or better (round-off of
processor against card), the published values to the paper's two digits; pairwise
orders 1.9989 to 2.0003, equal to the earlier ones to 6e-7; the two passage runs of the
earlier processor build are reproduced bitwise (largest difference 0). Prediction
confirmed. Figure `figs/regress_geodesic_core-20261115-032625-45e1779.png` (inspected:
the maxima of the four error histories sit on the dashed earlier maxima; the order panel
puts today's points on the earlier circles).

**O** (`core-20261115-032614-45e1779`, card, 317 s = 0.088 card-hours): 13 of 13 checks
pass. Initial data regenerated bitwise identical (sha256 of .nrp and .tab equal). First
horizon at 16.3894 M as before, mass 1.000352575670864 against 1.000352575670862
(2e-15); central lapse equal to the earlier run to 2.4e-15 before the horizon; largest
Hamiltonian-constraint norm equal to the printed digits; all particles removed at
19.739 M as before; deposition identity 1.0e-15. Prediction confirmed, closer than I
wrote (agreement to round-off, not bitwise). The asymptotically flat path of the current
source is the path of the earlier run. Figure `figs/regress_os_core-20261115-032614-45e1779.png`
(inspected; the spike of the lapse difference at t = 25 M is the last, shortened step
compared with an interpolated earlier record, not a difference of the runs).

**F** (`core-20261115-032615-45e1779`, card, 1 s): 12 of 12 checks of the criteria as
written pass; errors of lapse, density, mean K, volume, H-norm2 and Theta equal the
earlier ones to four digits (1.914e-7, 1.119e-6, 3.793e-7, 1.119e-6, 3.696e-10,
1.106e-11), the particle file differs from the earlier one (sha256) but deposits the same
uniform density. One prediction refuted: I wrote that the largest proper-time error
drops from 4.0e-5 to below 1e-6; it is 4.005e-5 in both runs. Reading, with a check that
could have failed: the largest error sits at the first record, where the code uses the
trapezoidal rule (no earlier lapse yet, `athenak/src/particles/nrpic_io.cpp` lines
142-156), whose relative error is dt^2 a''/(12 a) = 4.07e-5 at dt = 1/32; the first
record of both runs is 4.005e-5. At t = 2 the earlier (second-order) run is off by
1.73e-5, this run by 1.0e-7: the third-order integration is in effect. Change made after
seeing the run: the judge now also checks the error at t = 2 against 1e-6 (criteria.json
F.tau_probe_end_max, with its reason); with it 13 of 13 pass. Figure
`figs/regress_flrw_core-20261115-032615-45e1779.png` (inspected).

**L** (`core-20261115-032617-45e1779`, card, 4 s): FAILED, 4 of 10 checks. The observer
contrast is 0.6 to 1.0 percent below linear theory at both probes (criterion 0.5) and
0.46 and 0.82 percent of the contrast below the earlier run (criterion 0.1). The offset
is there at a_p = 1 and stays (figure `figs/regress_growth_core-20261115-032617-45e1779.png`,
inspected), so it comes from the initial data, not from the evolution. The regenerated
data are not those of the earlier run: `id.json` shows displacement_factor 1.0 and
particle masses varying by 9e-4, against 4.0396 and 3e-6 in the earlier run. The
generator's default changed from the relativistic ("number") displacement to the
Newtonian one in commit 2a19963 (`cosmo/ic/make_east.py` lines 84-95); my run script
used the default. This is a defect of my regression set-up, and the second variant of
the data is not the one the earlier result was obtained with. Constraint norms at t = 0
(6.0e-10, 7.6e-10) equal the earlier ones.

## 03:58 Predictions for the second linear-growth pass (written before the runs)

Two runs on one card job: (a) `growth/run.py --variant number`, the data regenerated
with `--displacement number`; (b) `--variant copy`, the earlier files themselves.
(a) The regenerated fields agree with the earlier `fields.bin` to below 1e-12 and the
particle records, sorted by position, to below 1e-12 (the generator's solver changed
only its iteration and stopping rule since, commit 56ac61d); the run then reproduces
the earlier contrast to below 1e-4 of the contrast and stays within 0.5 percent of
linear theory (earlier 0.45 and 0.31 percent). (b) The same to below 1e-5 of the
contrast (round-off of card against processor only). If (b) passes and (a) fails, the
generator has changed beyond the displacement; if both fail, the evolution has changed.
The first pass (Newtonian displacement) stays on record as variant "newtonian"; its
0.6 to 1.0 percent offset from linear theory at 32 cells is not explained here.

## 04:02 Outcomes of the second linear-growth pass (job 4346, 7 s of card time)

(b) `core-20261115-033410-bac7416`, earlier files copied: 10 of 10 checks pass; the
contrast equals the earlier processor run to 2.5e-12 and 4.8e-12 of the contrast at the
two probes; constraint norms at t = 0 equal. Prediction confirmed. The evolution of the
card release executable is the earlier one to round-off.
(a) `core-20261115-033408-bac7416`, data regenerated with `--displacement number`: 10 of
10 checks pass; 0.47 and 0.33 percent from linear theory (earlier 0.45 and 0.31); the
contrast differs from the earlier run by 1.9e-4 of the contrast at both probes.
Prediction partly refuted: I wrote that the regenerated files agree with the earlier
ones to 1e-12 and the contrast to 1e-4. The particle records agree to 6.3e-11 and the
traceless curvature to 1.3e-11, but the conformal factor differs by 2.9e-8, 3.2e-4 of
its perturbation (9.0e-5), which matches the 1.9e-4 difference of the contrast. Cause
not determined; the solver of `cosmo/ic/cosmo_id.py` changed its outer iteration and
stopping rule after the earlier run (commit 56ac61d; the new `id.json` records
outer_last_change_of_psi = 5.4e-10), which is a candidate that no run here isolates.
Figures `figs/regress_growth_core-20261115-033408-bac7416.png` and
`..._033410-bac7416.png` (inspected: the regenerated run lies on the earlier curve within
the line width; the copy is indistinguishable).
Variant "newtonian" (pass 1, `core-20261115-032617-45e1779`) stays on record: with the
generator's current default the 32^3 run is 0.6 to 1.0 percent below linear theory,
outside the 0.5 percent the C1 entry reports for the relativistic displacement. Whether
that default is the better one at 64 cells (where the cosmology production runs use it)
is not tested here.

Card time used by the package: jobs 4342 (5 min 23 s) and 4346 (7 s), 0.092
card-hours in all, of the 2 allowed.

# Wave 2 (2026-11-15, UTC from here on)

Package: ladder rows 3 and 4 on release core-v0.3 with the release executables
(`/data/haiyangw/nrpic/.work/build_gpu_v03/src/athena`, sha256 f9f2dc12...;
`.work/build_cpu_v03/src/athena`), the open analysis of the initial data with extrinsic
curvature (T2d, T3), the figures of the stage check. Card time allowed: 2.5 card-hours.

## 15:26Z Setting, before any run

- Initial data regenerate bitwise: `make_ic.py prolate --e 0.9 --b 10 --N 10000 --seed 1`
  gives the particle file of `runs/prolate/e09_v8` (sha256 dcc80b8d...), and
  `make_ic.py st --yc 0.605 --N 10000 --sampler stratified --seed 1 --vpert 0.01
  --no-consistent-table` gives the table and particles of `runs/st/yc0605_v5` (b76213c9...,
  81fa1c2d...) [VERIFIED, trial in scratch/core/tmp/verify2/, not a registered run]. The
  earlier sequence runs therefore used the equilibrium table with kicked particles; the
  bisection keeps that protocol (`--no-consistent-table`; the consistent table differs in
  psi_c by 1.1e-6, generator output).
- Inputs `problems/st/st_cluster_amr.athinput` and `problems/prolate/prolate_amr.athinput`
  equal the copies in the earlier run directories (diff).
- Oblate collapse: the `spheroid` component of `nrpic_cf` refuses a > b
  (`athenak/src/pgen/nrpic/nrpic_cf.cpp` line 485, "needs 0 < a < b (prolate ...)"), and
  the sampler has `ProlateSpheroid` only (`python/nrpic/spheroid.py`). An oblate run needs
  source work in `athenak/src` (core lead), which this package may not write: BLOCKED,
  request in README.md.
- First maximum of E_b/M_0 along the monoenergetic sequence (turning-point criterion,
  `python/nrpic/st_cluster.binding_energy_maximum`): y_c* = 0.6796, z_c = 0.4553,
  E_b/M_0 = 0.036058, R/M = 6.552 (recomputed in the registered IC run below).

## 15:30Z Predictions, prolate collapse at a second resolution (written before the run)

Run: the input of `runs/prolate/e09_v8` with one level fewer, finest cells M/8 instead of
M/16 (`mesh_refinement/num_levels=6`; everything else as e09_v8: 10^4 particles of the
same file, four binomial passes with compensation, block limit 2000), to t = 45 M, card
release executable. The horizon finder searches every 16 cycles, every 0.5 M at
dt = M/32.
Predictions: (i) first apparent horizon at 31.5 to 33.0 M (e09_v8: 32.00 M; the paper's
detection times vary by less than 0.1 M between M/32 and M/128, main.tex line 975);
(ii) the largest Kretschmann scalar is below the 1203 of e09_v8 (the peak grows with
resolution, main.tex line 975) and lies on the axis within |z| < 3 M between 25 and 30 M;
(iii) if the mass deficit of e09_v8 is a mesh effect, the largest horizon mass at M/8 is
below e09_v8's 0.9666 (I expect 0.92 to 0.96); if it is equal within 0.005 or larger,
the deficit is not set by the finest cell size between M/8 and M/16; (iv) all 10^4
particles are removed by 45 M; (v) under 0.25 card-hours.
Refuted: (i) by a first horizon outside 31.5-33.0 M or none by 45 M.

## 15:30Z Predictions, bisection of the stability threshold, round 1 (written before the runs)

Protocol of the earlier sequence (`runs/st/yc0605_v5`): 10^4 stratified particles, seed 1,
one-percent uniform inward kick, equilibrium table, input `st_cluster_amr.athinput`; one
change to make four runs fit the card time: `mesh_refinement/num_levels=7`, so the mesh
never refines beyond the initial nest of M/4 (the earlier compact runs refined to M/8
early and to M/16 at collapse; 7.9 s of card time per M before collapse, too dear for a
bisection). To t = 300 M. Models y_c = 0.72, 0.70 (stable side of y_c*) and 0.66, 0.64
(unstable side).
Fate rule, fixed now: COLLAPSE if an apparent horizon is found or the central lapse
(probe at the origin) falls below 0.3; STABLE if neither happens by 300 M and the mean
central lapse over 200-300 M is within 0.03 of the equilibrium alpha_c; otherwise
UNDECIDED (drift without collapse).
Predictions: 0.72 STABLE; 0.70 STABLE (less sure: 0.02 from y_c*); 0.66 COLLAPSE or
UNDECIDED (growth time near the threshold may exceed 300 M); 0.64 COLLAPSE with a first
horizon between 150 and 300 M (0.605 collapsed at 191 M on the finer AMR mesh).
Refuted (turning point is not the threshold at this resolution and noise): 0.72 or 0.70
collapsing, or 0.64 and 0.66 both STABLE. If 0.64 does not collapse, the coarse mesh
is suspect and the control 0.605 on the same mesh runs next.
Card time: about 0.25 card-hours per run (0.2 s per cycle at about 450 blocks, 4800
cycles); four runs and the prolate run about 1.3 card-hours; round 2 (two models inside
the bracket) about 0.5.

## 15:40Z Open id analysis (T2d, T3): what I expect, written before my analysis run

Not blind: before writing this I read the region numbers that the lead's analysis run
`core-20261115-145804-3629622` left in `analysis/id/test2_numbers.json.gz` (interior rms
of H for `ct-edge2-prod-n128/-n256`: 2.54e-5, 5.51e-6 at t = 8 M; 2.62e-5, 1.24e-5 at
10 M) and the history files of the t3 runs (`t3-bound-ct-n320`,
`core-20261115-042001-abc5fe2`: central lapse 1.249 at t = 7.97 M, then 1e71 and all
211062 particles removed between 8.4 and 9.4 M, exit status 0; `t3-bound-gs0-n160`,
`core-20261115-055107-6fa6472`: particles lost from 4.56 M, as the processor run
core-20261115-044359-aef2f7b). The test of the predictions is therefore the one written
in `JOURNAL-id.md` before those runs (T2d; T3 (i)-(iv)); my run re-derives the numbers
with a script that does not crash on these runs (`idcheck/t2d_t3.py`).
Expectations: (a) T2d: interior rms of H of the production deposit at dx = 1/4 M below
5e-5 at t = 8 and 10 M and not above the dx = 1/2 M value: CONFIRMED by the lead's
numbers; my run reproduces them to the printed digits (same code, same files) or I have
a reading error. (b) The rms of H in the boundary layer (r > 0.7 of the half-width) is
the same in every smooth-edge run (3.7e-4 at 10 M), i.e. the mesh mean of |H| quoted in
the lead entry is the boundary layer, not the ball. (c) T3: at dx = 1/8 M the run breaks
down when the lapse front reaches the centre (t near 8.4 M), so T3 (iii) and the
"run ends before t = 12 M" refutation clause hold at the finest mesh: T3 REFUTED at
dx = 1/8 M; the turnaround numbers at 1/8 M exist only up to the breakdown (tau of the
shells about 8 M, before the turnaround at 9.54 M). (d) `bound-mp-n160` (1+log): the
lapse front reaches the centre near t = 3 M (central lapse 0.72 at 4 M after 1.71 at
2 M): T3 (iv) confirmed in timing; its core errors at least twice those of
`bound-ct-n160` (prediction (iv)).

Correction: the heading time of the previous entry ("15:40Z") is wrong; it was written at
15:30Z, before the analysis run below.

## 15:37Z Outcomes of the T2d/T3 re-analysis

Runs: `core-20261115-153052-b17f40d` (first pass), `core-20261115-153429-cdc0f54`
(figure layout), `core-20261115-153539-9702c09` (final figures; numbers identical in all
three), script `idcheck/t2d_t3.py`, numbers `scratch/core/<run>/t2d_t3_numbers.json`.
Figures `figs/id_t2d_interior.png`, `figs/id_t3_bound.png` (both looked at; the first
version of each had legends over the data and an unframed |H| panel, corrected in the
later runs).

(a) T2d CONFIRMED. Interior rms of H (cells further than four cells plus two edge widths
inside the outermost ball particle), dx = 1, 1/2, 1/4 M:
- ct-edge2 (CIC, Hermite): t = 8 M 3.94e-4, 7.53e-5, 2.14e-4; t = 10 M 3.61e-4,
  1.77e-4, 3.20e-4 (not converging, larger at 1/4 than at 1/2 M);
- ct-edge2-ext (CIC, sources extrapolated): 4.00e-4, 5.30e-5, 2.20e-4; 3.62e-4, 1.86e-4,
  3.27e-4 (the extrapolation does not change the late residual);
- ct-edge2-prod (cubic cloud, compensation, spline metric, sources extrapolated):
  dx = 1/2, 1/4 M: 2.54e-5, 5.51e-6 at 8 M; 2.62e-5, 1.24e-5 at 10 M.
At dx = 1/4 M the production deposit is 39 and 26 times below ct-edge2 at 8 and 10 M,
below the 5e-5 bound, and below its own dx = 1/2 M value (ratio 4.6 at 8 M, 2.1 at
10 M). The late interior residual of ct-edge2 is therefore the deposit (cloud-in-cell
of a lattice that has drifted against the mesh), as hypothesized. Equal to the lead's
numbers to the printed digits (same code).
(b) CONFIRMED: the boundary layer (r > 0.7 of the half-width) carries rms H 3.71e-4 to
3.74e-4 at 10 M in every smooth-edge run, whatever the deposit; it, not the ball,
dominates the mesh mean of |H| quoted in the lead entry (2.3e-4). Item 4 of
JOURNAL-id.md entry 8 (outer boundary condition for K_ij ~ r^(-3/2)) stays open.
(c) T3 at dx = 1/8 M (`t3-bound-ct-n320`, core-20261115-042001-abc5fe2): the run BREAKS
DOWN when the lapse front reaches the centre. Central lapse a(tau_c) to 1.25 until
t = 8 M, 1.462 at 8.78 M, 0.551 at 8.875 M, non-finite from 8.906 M; all 211062
particles removed as non-finite by 9.4 M; the code goes on to t = 12 M and exits with
status 0 (OPEN.md item 11). The largest |H| on the mesh at the front grows with
resolution: 0.135 (dx = 1/2 M), 6.44 (1/4 M), 184 at 8.75 M and infinite at 9 M (1/8 M)
(cstat history). A front that steepens without bound as the mesh is refined is the
signature of a gauge shock [JUDGEMENT; no run here separates it from an instability of
the formulation]. Before the breakdown the finest run is the most accurate: shells turn
around at a_max 1.2472 (core), 1.2485, 1.2509, 1.2505 (exact 1.2500) at tau 9.40, 9.50,
9.56, 9.59 M (exact 9.542 M); largest |eps| at tau = 2 M 4.4e-4 against 3.5e-3 at
dx = 1/4 M. T3 as predicted (run reaching t = 12 M with |eps| < 1e-2) is REFUTED at
dx = 1/8 M; at dx = 1/2 and 1/4 M the earlier outcome stands (turnaround within 0.5
per cent at 1/4 M, errors 0.11 (core) over the whole run, no convergence after the front).
(d) T3 (iv) CONFIRMED: with 1+log (`t3-bound-mp-n160`) the central lapse peaks at 2.08
near t = 3 M and falls to 0.44 at 3.6 M; core |eps| at tau = 8 M 6.5e-2 against 4.85e-3
with the conformal-time lapse (13 times), 0.58 against 0.11 over the run.
(e) `t3-bound-gs0-n160` (lapse 1, shift 0, card, dx = 1/4 M): unstable as on processors,
first particle loss at 4.56 M (processor run at 1/2 M: not-a-number at 4.9 M); the
analysis now records it (3 dumps skipped: no ball particle left) instead of crashing.
The crash of `test2_evolution.py --prefix t3` is thus worked around in
`idcheck/t2d_t3.py`; `analysis/id/test2_evolution.py` itself is unchanged (not this
package's file): request to the lead in README.md.

## 15:47Z Oblate reference (prediction before the check run)

`oblate/oblate_reference.py`: closed form of the potential of a homogeneous oblate
spheroid (atan counterpart of the prolate formulas of `python/nrpic/spheroid.py`),
derived here by the substitution s = sqrt(b^2 + u). Prediction: the closed form equals
adaptive quadrature of the defining integrals to 1e-10 relative; a^2 b (2 J_a + J_b) = 2
inside to 1e-12; the finite-difference Laplacian is 4 pi rho_N inside and 0 outside to
1e-5 (h = 1e-3, second-order truncation); Phi_N is continuous at the surface and tends
to -M/(2r); the same quadrature reproduces the prolate I, J_a, J_b of spheroid.py.
Refuted by any of these failing (a wrong sign or factor in the derivation).

## 15:45Z Outcome: oblate reference

Runs `core-20261115-154359-d74357f` (checks), `-154416-fcec991` and `-154426-8144c9f`
(same checks with the figure; identical numbers). All checks PASS as predicted: closed
form against quadrature 4.1e-12 relative; Poisson identity 1.3e-15; FD Laplacian
1.5e-8 relative (better than the 1e-5 I allowed: the potential is quadratic inside, so
the second difference is exact there up to rounding); surface jump 1.5e-10 at
eps = 1e-9; r Phi_N -> -0.5 to 1e-8 at r = 1e5 M; sphere limit to the 1e-6 offset of
a and b; the quadrature reproduces the prolate I, J_a, J_b of `spheroid.py` to 6e-15.
Figure `figs/oblate_reference.png` (looked at: equatorial and polar profiles join
-M/(2r) beyond 20 M; psibar peaks at 1.093 at the centre, flattened along z; the first
version cut the colorbar label, fixed in the third run). This is the reference the
lead needs for an oblate component of `nrpic_cf` and an oblate sampler; it is not an
oblate collapse.

## 15:48Z First round-1 outcomes (y_c = 0.72, 0.70) and the round-2 prediction

`st_yc0p720` (run core-20261115-152843-5728b1d, 1065 s of card time) and `st_yc0p700`
(core-20261115-152842-5728b1d, 1056 s): both reach 300 M without a horizon and without
the central lapse falling below 0.3; mean central lapse over 200-300 M 0.7079 and 0.6920
against the equilibrium 0.7207 and 0.7039 (offsets -0.013, -0.012: inside the 0.03 of
the rule): STABLE by the rule fixed before the runs, as predicted. Not hidden by the
verdict: in both runs the mean central lapse drifts down in the last 100 M (50 M windows,
y_c = 0.70: 0.7124, 0.7023, 0.6817; y_c = 0.72: 0.7201, 0.7127, 0.7031) and the swing
grows (0.70: 0.701-0.708 in the first 50 M, 0.638-0.727 in the last 50 M), like the
noise-driven growing oscillation of the earlier y_c = 0.819 and 0.756 runs. Whether this
drift would end in collapse after 300 M is not tested (UNDECIDED in a longer run is
possible). Numbers from a quick, unregistered pass of `cluster_fate.py`; the registered
analysis follows when all runs are in.

Round 2, submitted now, before the 0.66 and 0.64 outcomes (to keep the cards busy; risk
written down: if 0.66 does not collapse, the round-2 points lie on the stable side and a
third point below 0.66 is needed): y_c = 0.69 and 0.67, the members 0.01 above and below
y_c* = 0.6796, same protocol, to 300 M.
Prediction: 0.69 STABLE (with the same late drift), 0.67 COLLAPSE or UNDECIDED (its
growth time near the threshold may exceed 300 M); if 0.67 is STABLE by the rule, the
threshold at this resolution and noise lies below y_c* - 0.01, i.e. the cluster is more
stable than the turning point says (which the collapse of 0.605 bounds from below).

## 15:56Z Not predicted: y_c = 0.66 and 0.64 expand instead of collapsing; control run

Partial records (to 150 M) of `st_yc0p660` and `st_yc0p640`: the central lapse RISES,
0.673 -> 0.723 (0.66) and 0.657 -> 0.721 (0.64), means over 25 M windows climbing from
75 M on; no horizon. The models leave their equilibria outward, towards the stable
member of equal binding fraction (migration, paper section "Cluster Migration"):
`st_cluster.migration_target` gives alpha_c = 0.7034 for y_c = 0.66 and 0.7205 for 0.64.
My prediction (0.64 collapses between 150 and 300 M; 0.66 collapses or is undecided) is
REFUTED in its collapse part. The fate rule fixed at 15:30Z has no class for migration:
it will call these runs UNDECIDED (late mean lapse more than 0.03 from alpha_c, no
collapse). I keep the rule and its verdicts, and report the departure and its target
separately as a reading [JUDGEMENT, written after seeing the runs]: a model that leaves
its equilibrium monotonically, inward or outward, is on the unstable side.
Earlier, on the finer AMR mesh (cells M/8 early, M/16 at collapse), the kicked 0.605
model collapsed (horizon 191 M, `runs/st/yc0605_v5`). A difference of mesh could change
the direction of departure (collapse or migration) without moving the threshold.
Control, submitted now: y_c = 0.605, same protocol and mesh as round 1 (finest M/4), to
250 M (0.24 card-hours). Prediction: it leaves its equilibrium within 150 M; collapse
(as on the AMR mesh) or migration towards alpha_c = 0.7519 (its equal-binding member,
y_c = 0.7561). If it migrates, the direction of departure at y_c < y_c* depends on the
mesh at M/4 vs M/8-M/16 [to be stated as such, not as a property of the cluster]; if it
collapses, the 0.64 and 0.66 runs migrate because they are close to y_c*.
Card time after this: about 1.2 (round 1) + 0.25 (prolate) + 0.6 (round 2) + 0.24
(control) = 2.3 of the 2.5 allowed; nothing further will be submitted.

## 16:07Z Outcome of bisection round 1 (registered analysis core-20261115-160501-ee15e0f)

Card jobs 4432 (y_c 0.70, 0.66; run core-20261115-152842-5728b1d, 0.593 card-hours) and
4433 (0.72, 0.64; core-20261115-152843-5728b1d, 0.596). All four reach 300 M with exit
status 0, every particle kept, no apparent horizon, central lapse never below 0.638.
Figure `figs/cluster_threshold.png` (looked at).

By the rule fixed at 15:30Z (mean central lapse over 200-300 M against alpha_c, 0.03):
| y_c | alpha_c (equilibrium) | mean 200-300 M | verdict by the rule | equal-binding target alpha_c |
|---|---|---|---|---|
| 0.72 | 0.7207 | 0.7079 | STABLE | -- |
| 0.70 | 0.7039 | 0.6920 | STABLE | -- |
| 0.66 | 0.6713 | 0.7005 | STABLE (offset +0.029, at the edge of 0.03) | 0.7034 |
| 0.64 | 0.6554 | 0.7221 | UNDECIDED (offset +0.067) | 0.7205 |
No model collapses on this mesh: the collapse part of the prediction is REFUTED (0.64
was to collapse between 150 and 300 M). By the rule the bisection gives no bracket (no
COLLAPSE; the lowest STABLE is 0.66, below y_c* = 0.6796), i.e. the rule as written does
not locate the threshold with these runs.
Reading [JUDGEMENT, after the runs]: the two models below y_c* leave their equilibrium
outward and settle, in the 100 M mean, at the central lapse of the stable member with the
same E_b/M_0 (0.7005 vs 0.7034; 0.7221 vs 0.7205), which is the migration the paper
describes for unstable members (its Sec. "Cluster Migration"; our earlier unperturbed
y_c = 0.5 migration run reached 0.814 against 0.833530 in the paper). The two models
above y_c* stay at their equilibrium in the mean (offsets -0.012, -0.013) and do not move
towards any other member. On that reading the threshold lies between 0.66 and 0.70,
bracketing y_c* = 0.6796. What the rule missed: migration is a departure without
collapse; a criterion "mean central lapse moves to the equal-binding member" would have
to be fixed before round 2's outcome is read, and is written here now: round 2 (0.69,
0.67) and the control are judged by both the 15:30Z rule and this migration criterion
(|mean 200-300 M - alpha_c(target)| < |mean 200-300 M - alpha_c(own)|).
Also seen, and not explained: in all four runs the central lapse oscillates with a
period near 50 M and a swing that grows from +-0.004 in the first 50 M to +-0.05 to
+-0.08 after 200 M (0.72: 0.656-0.742), larger than in the earlier M/2 static runs of
0.819 (half swing up to 0.022) - the growing oscillation of OPEN.md item 3, here at
M/4 and with the stable runs also drifting down by about 0.01 in the last 100 M.
Card time so far 1.19 card-hours (round 1).

## 16:28Z Outcome: prolate collapse at finest cells M/8 (ladder row 3, second resolution)

Card job 4434, run `core-20261115-152845-5728b1d` (exit 0, 1222 s athena cpu time, 0.344
card-hours by sacct; predicted under 0.25: refuted, minor); analysis
`core-20261115-162509-c691fb8` (`ladder2/prolate_compare.py`, M/16 = `runs/prolate/e09_v8`
re-read by the same script: 32.00 M, 0.9291, 0.9666, 0.9489, 1203 at 27.75 M, as in
LADDER.md). Figures `figs/prolate_resolution.png`, `figs/prolate_mosaic.png` (looked at;
the copies of these two files committed in d74357f and a654cd7 were drafts from an
unregistered dry test that compared e09_v8 with itself, now replaced).

| quantity | M/16 (e09_v8) | M/8 (wave 2) |
|---|---|---|
| first apparent horizon (search every 0.25 / 0.5 M) | 32.00 M, M_AH 0.9291 | 32.25 M, M_AH 0.9249 |
| largest M_AH (time) | 0.9666 (33.75 M) | 0.9570 (33.75 M) |
| M_AH at 44.75 M | 0.9489 | 0.9444 |
| largest Kretschmann scalar 20-31 M (time, z) | 1203 (27.75 M, -0.66 M) | 101 (26.25 M, +0.81 M) |
| largest Kretschmann scalar over the run | 1203 (27.75 M) | 110 (37.0 M, near the origin) |
| first particle removal; all removed | 33.78 M; yes | 35.34 M; yes |
| largest sqrt(H-norm2) (time) | 6.31 (27.5 M) | 5.43 (32.0 M) |
| largest MeshBlock count | 1352 | 1128 |

(i) CONFIRMED: first horizon at 32.25 M, within 31.5-33.0 and one search interval (0.5 M
at M/8) of the M/16 run; the paper's statement that detection times vary by less than
0.1 M (main.tex line 975) cannot be tested at the 0.5 M cadence of this run.
(ii) Partly REFUTED: the peak curvature is far below the M/16 value (101 against 1203,
twelve times lower for a factor two in cell size, consistent with an unresolved caustic,
main.tex 975) and on the axis within |z| < 3 M, but its maximum over the run is after the
horizon (110 at 37 M), not in 25-30 M as I wrote; in 20-31 M the peak is at 26.25 M.
(iii) The largest horizon mass is lower at M/8 (0.9570) than at M/16 (0.9666), the end
value too (0.9444 vs 0.9489): the deficit shrinks with resolution (4.3 to 3.3 per cent at
the maximum), so it is at least partly a mesh effect. Two resolutions do not give an
order; a first-order extrapolation would still leave about 2.4 per cent [JUDGEMENT, not
a measurement]. The particle number is the same in both runs, so its share is untested.
(iv) CONFIRMED: all 10^4 particles removed (rest mass 1.0981 removed).
Row 3, prolate part: horizon formation at the paper's time at two resolutions; the
horizon-mass deficit falls with resolution but is 3 per cent at the finer one. Oblate:
not run (source work, README request 2; reference potential ready).
Card time so far: 1.19 + 0.34 = 1.53 card-hours.

## 16:52Z Outcome: control y_c = 0.605 at finest cells M/4

Card job 4447, run `core-20261115-155617-06f844b` (exit 0, 0.248 card-hours), initial
data identical to `runs/st/yc0605_v5` (sha256 81fa1c2d..., b76213c9...). No horizon; the
central lapse rises from 0.631 to 25 M means of 0.754, 0.747, 0.801, 0.784, 0.750 between
125 and 250 M, around its equal-binding partner (y_c = 0.7561, alpha_c = 0.7519): the
model MIGRATES at M/4, where on the finer AMR mesh (M/8 from early on, M/16 near the
centre at collapse) the same data collapsed with a horizon at 191 M. Of the two outcomes
written at 15:56Z this is the first: the direction of departure below y_c* (collapse or
migration after a one-percent inward kick) depends on the mesh between M/4 and M/8-M/16
in these runs; the departure itself does not. So the M/4 bisection says where the
equilibria stop being stable, not whether an unstable member collapses; the latter
needs the finer mesh (and, in the paper, 2e6 particles).
Card time so far: 1.19 + 0.34 + 0.25 = 1.78; job 4439 (round 2) adds about 0.6.

## 17:07Z Outcome: bisection round 2 (y_c = 0.69, 0.67) and the full bisection

Card job 4439, run `core-20261115-154726-37450f2` (both exit 0, 0.594 card-hours);
analysis of all seven M/4 runs `core-20261115-170606-1c69507` (the identical pass
`-170454-5333b49` drew the earlier figure layout); figure `figs/cluster_threshold.png`
(looked at; third panel: late mean central lapse against y_c with the model's own
alpha_c and its equal-binding partner's).

| y_c | alpha_c own / partner | mean 200-300 M | offset from own | rule 15:30Z | migration criterion 16:07Z |
|---|---|---|---|---|---|
| 0.72 | 0.7207 / 0.6552 | 0.7079 | -0.0128 | STABLE | no |
| 0.70 | 0.7039 / 0.6708 | 0.6920 | -0.0119 | STABLE | no |
| 0.69 | 0.6957 / 0.6787 | 0.6864 | -0.0093 | STABLE | yes (towards the compact partner) |
| 0.67 | 0.6793 / 0.6951 | 0.6911 | +0.0118 | STABLE | yes (towards the expanded partner) |
| 0.66 | 0.6713 / 0.7034 | 0.7005 | +0.0292 | STABLE | yes |
| 0.64 | 0.6554 / 0.7205 | 0.7221 | +0.0667 | UNDECIDED | yes |
| 0.605 (to 250 M) | 0.6281 / 0.7519 | 0.7667 (200-250 M) | +0.139 | UNDECIDED | yes |

Prediction of 15:48Z: 0.69 STABLE (confirmed by the rule; with the same late drift,
confirmed: -0.009); 0.67 COLLAPSE or UNDECIDED: REFUTED, it is STABLE by the rule (offset
+0.012). By the migration criterion both "migrate", 0.69 inward: the criterion cannot
separate a member 0.01 from y_c* from the common downward drift of about 0.01 that
every model above y_c* shows, because the partners of 0.69 and 0.67 lie only 0.017 away
in alpha_c. Neither criterion fixed in advance resolves round 2.
What the seven runs establish, stated with its label:
- [VERIFIED, runs above] No member between 0.605 and 0.72 collapses within 250-300 M on
  the M/4 mesh with 10^4 particles; the members 0.605, 0.64, 0.66 leave their equilibrium
  outward and settle, in the 100 M mean, within 0.015, 0.002, 0.003 of their
  equal-binding partner's central lapse; 0.70 and 0.72 stay within 0.013 of their own.
- [JUDGEMENT, read after the runs] The sign of the late offset changes between 0.69
  (-0.009) and 0.67 (+0.012); with the drift of the stable members subtracted the
  threshold of departure lies between 0.67 and 0.69, around y_c* = 0.6796, the
  turning-point value. This is a post-hoc criterion and is not claimed as a measurement
  of the threshold.
- [VERIFIED] The direction of departure depends on the mesh: 0.605 migrates at M/4 and
  collapsed on the finer AMR mesh. So the bisection at M/4 does not test the collapse
  branch of the paper's sequence.
Row 4 verdict: PARTIAL. Threshold bracketed between 0.66 and 0.70 by the migration
criterion (fixed before round 2) applied to round 1, consistent with the turning point;
not located more finely by any criterion fixed in advance; collapse branch untested at
M/4; the growing central-lapse oscillation (OPEN.md item 3) is present in every run.
Card time of the package in wave 2: 0.593 + 0.596 + 0.344 + 0.248 + 0.594 = 2.375
card-hours of the 2.5 allowed (sacct elapsed of jobs 4432, 4433, 4434, 4447, 4439).
