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
