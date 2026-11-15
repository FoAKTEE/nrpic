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
