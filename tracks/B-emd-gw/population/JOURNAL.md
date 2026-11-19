# JOURNAL of the population package (B-emd-gw, wave 3a, 2026-11-19)

Helper package: design of the G3 science run of Track B (the stochastic GW background of a
halo population in a small box) and a Newtonian-mode scouting run. Predictions are written
here before the runs, outcomes after them (including failed predictions). Units G = c = 1,
H = 1 and a = 1 at the start, lengths in initial Hubble radii, conformal time t with
a = (1 + t/2)^2.

## Entry 1 (07:05 PST): set-up and predictions, before any run

Sources read for the design (locators in `README.md` and `DESIGN.md`): arXiv:2312.12499
(main.tex: spectrum 581-594, Press-Schechter 595-613, A_s^(7/4) 621-639, k_NL and
k_cross 643-673, resolution and box table 176-203, fit 237-242, caution above the
light-crossing frequency 235, 251), arXiv:2212.00425 (main.tex: S_k method 219-288,
box 213, threshold Delta^2 = 0.1 at 319, rho_GW ~ a^3.78 at 314), arXiv:2403.15126
(sigma range 276, monochromatic peaks 295, sigma^(7/2) 1031), arXiv:2605.04487 (sigma at
the reference epoch 1126-1136), the wave-1 baseline (`../baseline/BASELINE.md`), the
wave-2 review (`../stage/REVIEW-wave2.md`), `coord/INTERFACES/newtonian_mode.md`,
`cosmo/ic/random_field.py`, `cosmo/ic/make_field.py`.

Fiducial field (scripts/make_ic.py): early-matter-era growing mode of a scale-invariant
curvature spectrum, P_delta(k, a = 1) = 2 pi^2 (4/25) A_s k (Delta^2 ~ k^4), sharp cut at
k_c = nc 2 pi/L with nc = 3.2 (twenty cells per cut wavelength at 64 cells, the rule of
`cosmo/README.md`), L = 4, rms delta_N at a = 1 sigma1 = 0.0562 (spherical collapse of a
1 sigma peak at a = 1.686/0.0562 = 30), end a = 100 (t = 18). For this band-limited
spectrum gamma = sigma1^2/(sigma0 sigma2) = sqrt(32)/6 = 0.943 and R_* = 2/k_c [JUDGEMENT,
arithmetic]; the BBKS peak density (BBKS eq. 4.3 with the function f of eq. A15, computed
in this session, not a registered run) gives 16.5 maxima in the box for nc = 3.2 (16.0
above nu = 1, 9.8 above nu = 2, 1.9 above nu = 3) and 32 for nc = 4.

Smoke tests of my scripts (not results, outputs in `scratch/B-emd-gw/tmp/pop_smoke16`):
make_ic.py at 16 cells with --gr ran (constraint solve converged); the Newtonian input ran
16 steps at 16 cells.

Predictions for the Newtonian runs (release core-v0.3 processor build, 64 cells, one
particle per cell unless said; halos = friends-of-friends groups with linking length 0.2
of the mean particle spacing and at least 100 particles):

- P1 (fiducial, seed 1). The first halo forms between a = 8 and a = 20; at a = 30 there
  are between 6 and 25 halos. Refuted if no halo exists at a = 20 or more than 40 at a = 30.
- P2. At a = 100 there are between 3 and 20 halos and the largest holds between 2 and 25
  per cent of the box mass (mergers along the k^4 spectrum: M_* grows as a^(3/2) once
  the cut scale is nonlinear [JUDGEMENT]). Refuted outside these ranges.
- P3. Seeds 2 and 3 give halo counts at a = 30 within a factor 2 of seed 1 (the expected
  number of maxima is 16.5; Poisson scatter about 4).
- P4. Amplitude doubled (sigma1 = 0.1124): the halo count against a follows that of the
  fiducial run at a/2 within a factor 1.5 (collapse time scales as 1/sigma1 in linear
  theory [BACKGROUND]).
- P5. 32 cells, same modes (the cut lies below the 32-cell Nyquist frequency): the halos
  above 300 particles of the 64-cell run at a = 30 have a counterpart (centre within one
  32-cell spacing) in the 32-cell run, at least 70 per cent of them. Masses of matched
  halos agree to 30 per cent.
- P6. nc = 4 (16 cells per cut wavelength): about twice as many halos at a = 30 as the
  fiducial (ratio between 1.4 and 3).
- P7. Layzer-Irvine constant (history column 8 against a |W|) holds to 1e-2 of max a|W| to
  a = 100 in every run. Refuted above 1e-2.
- P8 (signal). The quadrupole-formula (TT-stress) GW energy of the box, computed from the
  snapshots with the method of arXiv:2212.00425 (S_k, kinetic plus gravitational stress),
  rises steeply while halos form and is within a factor 30 of the semi-analytic estimate
  sum over halos of F M R_L^7 (2 alpha)^(7/2) (baseline model A, F about 0.1, per halo
  from its Lagrangian patch) times the redshift factor; I expect it ABOVE that estimate
  (the baseline stops at the first axis crossing; violent relaxation adds up to ten,
  2403.15126 line 312). Refuted if below the estimate by more than 3 or above by more
  than 30.
- P9 (scaling of the signal with amplitude). Between sigma1 = 0.0562 and 0.1124, the
  emitted energy at equal number of collapsed halos scales as sigma1^(7/2) within a
  factor 2 (single-patch law, `../baseline/BASELINE.md` section 2, T6).

Predictions for the relativistic initial data (make_ic.py --gr, 128 cells): the constraint
solve converges (outer change of psi below 1e-9) for L = 4 and L = 16; max|psi_N| grows as
L^2 at fixed nc (0.02 at L = 4, about 0.35 at L = 16 [JUDGEMENT, the potential of the
growing mode is (3/2) delta/k^2]).

Predictions for the card timing runs (relativistic, production configuration, release
card build): 128^3, one particle per cell: 4.5e6 zone-cycles per second within 30 per cent
(SCOPE.md section 9: 4.47e6 to 5.7e6 measured for the cosmo/ problems); 256^3, one particle
per cell: between 3e6 and 6e6 zone-cycles per second and below 60 GB of card memory.
Refuted outside these ranges.

## Entry 2 (07:12 PST): first fiducial run stopped, resubmitted cheaper

Run B-20261119-143348-728c0e5 (fiducial, step 1/64, Poisson solve to rounding) was stopped
by me after 32 cycles: 6 s per cycle on the loaded machine (load average 148 on 144
cores), 1.9 h projected for the 1152 steps. Resubmitted with the solver tolerance
`newton_mg_tol = 1e-6` (core measured positions within 3.4e-9 and an unchanged energy
error at a third of the V cycles, coord/INTERFACES/newtonian_mode.md section 5.8), the
step 1/32 (still below a tenth of the halo dynamical time 0.1 sqrt(a) [JUDGEMENT]) and
`newton_cfl = 0.25` as an additional limit inside halos. The predictions of entry 1 stand
unchanged for the new runs. The owner's processor allotment (16 cores, 13 busy with the
other helpers) and the two queued card jobs of B-emd-gw (Slurm 4635, 4637) limit this
package to processors and to a few cores at a time: no card job is submitted by me.
