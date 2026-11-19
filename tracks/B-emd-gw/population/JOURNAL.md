# JOURNAL of the population package (B-emd-gw, wave 3a, 2026-11-19)

Helper package: design of the G3 science run of Track B (the stochastic GW background of a
halo population in a small box) and a Newtonian-mode scouting run. Predictions are written
here before the runs, outcomes after them (including failed predictions). Units G = c = 1,
H = 1 and a = 1 at the start, lengths in initial Hubble radii, conformal time t with
a = (1 + t/2)^2.

## Entry 1 (06:33 PST): set-up and predictions, before any run

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

## Entry 2 (06:38 PST): first fiducial run stopped, resubmitted cheaper

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

## Entry 3 (07:43 PST): runs finished so far; the per-halo quadrupole reworked

Finished: fiducial B-20261119-143828-0ef9b5b (577 cycles, 3396 s on one core), seed 2
B-20261119-143832-85cbe25 (3425 s), 32 cells B-20261119-145324-525e4fd (227 s). Running:
amplitude doubled B-20261119-145328-4b3663f, nc = 4 B-20261119-145715-b18561e.

The first analysis of the 32-cell run (B-20261119-153509-02a921f) gave a per-halo
quadrupole-formula energy (halos of the last snapshot tracked back) of Omega = 1.9e-4,
four orders above the box TT measure: an artefact. Cause, found by printing the particle
extent and Q(t) (not a registered run): the Lagrangian regions of the a = 100 halos span up
to half the box (the largest holds 6.6 per cent of the mass), so unwrapping about one
particle fails, and the constant anisotropy of a Lagrangian region in the Hubble flow
alone contributes -Qc(t0) a^(-5/2) to d^3Q/dT^3 (derived: for Q = a^2 Qc, a = s^2,
s = 1 + t/2, d^3Q/dT^3 = -Qc/s^5). The analysis now takes the halos of a = 20 (compact
regions), follows them to a = 30, unwraps about the periodic centre of mass, removes the
constant term (Q = a^2 (Qc(t) - Qc(t0))) and differentiates in conformal time with the
chain rule. The fiducial analysis started with the old code (B-20261119-153724-a6f1ab5)
was stopped and is resubmitted with the new one. A check of the new code on the 32-cell
outputs (not registered, scratch/B-emd-gw/tmp/analyze) matched the seven halos of a = 20
to maxima of the initial field within 0.02 to 0.16 (comoving) and gave energies 1.3 to
240 times the baseline of the matched maximum; the registered numbers follow.

## Entry 4 (07:57 PST): outcomes of P1-P9

Runs: Newtonian fid B-20261119-143828-0ef9b5b, seed 2 B-20261119-143832-85cbe25, 32 cells
B-20261119-145324-525e4fd, amplitude doubled B-20261119-145328-4b3663f (stopped by me at
a = 57, past the a = 50 that P4 and P9 need), nc = 4 B-20261119-145715-b18561e. Analyses:
A-fid B-20261119-154315-c55b30f (fid, seed2, n32; GW of fid at 64^3), A-amp2
B-20261119-154447-99fa502, A-nc4 B-20261119-155537-d49f8f1, comparison
B-20261119-155621-68170ca (`results/compare.json`, `figs/pop_compare.png`). Figures
`figs/pop_halos_fid.png`, `pop_density_fid.png`, `pop_gw_fid.png`, `pop_compare.png`
looked at (the a = 5 density panel shows a moire of the particle lattice against the
128-bin projection, cosmetic).

- P1 HOLDS (at the upper edge): first halo (>= 100 particles) at a = 9.0; 25 halos at
  a = 30.1 (predicted 6 to 25).
- P2 REFUTED as written, by one halo: 21 halos at a = 100 (predicted 3 to 20); the largest
  holds 0.4705 of 7.639, 6.2 per cent (predicted 2 to 25). The count plateaus at 18 to 28
  from a = 25 on: new halos keep forming while others merge; my mass-function argument
  (M_* ~ a^(3/2)) did not account for the continued formation of cut-scale halos.
- P3 HOLDS: seed 2 has 25 halos at a = 30 as seed 1 (identical count, by chance).
- P4 HOLDS except at one epoch: amp2 at a against fid at 2a: counts 1/1, 9/14 (ratio 1.56,
  outside the 1.5 predicted), 14/14, 25/25, 26/25, 21/22, 19/18, 23/23, 26/28, 21/21; the
  largest mass and the collapsed fraction agree to 1 to 4 per cent from a_fid = 20 on
  (`compare.json` P4). The Newtonian evolution depends on sigma1 a only, to the halo-count
  noise.
- P5 REFUTED as written: 11 of the 16 halos with >= 300 particles at a = 30 (69 per cent,
  predicted >= 70) have a 32-cell halo within one 32-cell spacing; the 5 without are the
  smallest (M = 0.009 to 0.020), below the 32-cell detection limit of 100 particles
  (M = 0.023) that I did not account for. Every 64-cell halo above that limit is matched,
  masses within -24 to +12 per cent.
- P6 HOLDS (at the edge): 35 halos at a = 30 with nc = 4 against 25 (ratio 1.4, predicted
  1.4 to 3). The BBKS ratio of the maxima is 1.95; mergers and the 100-particle limit
  (cut-scale halos of nc = 4 are half as massive) reduce it [JUDGEMENT].
- P7 HOLDS: Layzer-Irvine constant within 4.7e-4 to 8.4e-4 of max a|W| in all five runs.
- P8 SPLIT. The box measure (TT stress, junk and near field removed) against the baseline
  sum of design.json: 2.2, 10, 5 and 12 times above it at a = 10, 15, 20, 30 (inside the
  predicted window), then 206 and 775 times at a = 50 and 100 (outside: the baseline stops
  at each first crossing and decays as 1/a; the box keeps radiating after collapse:
  Omega_rad 1.2e-7 at a = 50, 3.0e-7 at a = 70, 2.3e-7 at a = 100). The per-halo
  quadrupole formula during formation (the ten largest halos of a = 20, followed to
  a = 30) is 3.4 to 2760 times the baseline energy of the matched maximum (median of the
  eight matched within 0.1: about 300); refuted for six of them. Sum over those halos
  Omega = 2.3e-7 at a = 30, 19 times the box measure at that time. [JUDGEMENT on the
  cause, not tested: at a >= 30 the halo dynamical wave number 9.4/sqrt(a) (design.json
  k_dyn) approaches the box fundamental 2 pi/L = 1.57; the box holds no mode at the
  frequency of most of the halo emission, which the isolated-source formula counts.]
- P9 HOLDS: at equal stage (amp2 at a against fid at 2a) the radiated box measure is 8.0
  to 18.7 times larger for a_fid = 10 to 100 (predicted 2^(7/2) = 11.3 within a factor
  2), the near field 6.1 to 11.1 times (predicted 8); `figs/pop_compare.png` middle panel:
  the rescaled curves lie on each other after a = 10. The sigma^(7/2) law of the emitted
  energy holds in the Newtonian box with the post-collapse emission included.
- Near field: Omega_qs = 1.17e-8 at the first snapshot (design formula: 1.18e-8, the
  (20/3) source at a = 1), 4.95e-7 at a = 20 (twice the linear 1.18e-8 a), then 3.6 to
  3.8e-7 to a = 100 (a third of the linear extrapolation).

## Entry 5 (07:58 PST): prediction P10 before the box-scaling analysis

The Newtonian problem is invariant under x -> lambda x, p -> lambda p, m -> lambda^3 m at
fixed t, so the fiducial run also stands for the boxes L = 8 (lambda = 2) and L = 2
(lambda = 1/2); `scripts/analyze.py --lscale` applies the scaling to the snapshots. Only
the GW wave equation (light speed, the box modes k = 2 pi n/L) breaks it.

- P10a (exact): the per-halo quadrupole sum scales by lambda^7 (2.3e-7 -> 3.0e-5 at
  lambda = 2) and the near field by lambda^6 (3.65e-7 -> 2.34e-5 at a = 100) to rounding.
- P10b: at lambda = 2 the radiated box measure grows by MORE than 2^7 = 128 at a >= 30
  (the halo wave number 9.4/sqrt(a) stays above the fundamental 0.785 to a = 143, so more
  of the emission lands on box modes), at most by 128 x 19 (the per-halo/box ratio at
  L = 4, a = 30). Refuted if the ratio is at or below 128 at a >= 30.
- P10c: at lambda = 1/2 (fundamental 3.14, above 9.4/sqrt(a) from a = 9) the radiated
  measure falls by more than 2^7 for a >= 15. Refuted if it falls by 128 or less.

Note (07:59 PST): the clock times in the headers of entries 1 to 5 were first written
wrong (estimated, not read); corrected to the commit times of each entry (`git log`).
The order of predictions and runs is unchanged and is the commit order.

## Entry 6 (08:06 PST): outcomes of P10 and I1

P10 (analyses A-fid-L8 B-20261119-155808-0942d44 and A-fid-L2 B-20261119-155838-4f1954f
against A-fid):
- P10a HOLDS: per-halo quadrupole sum 2.342e-7 (L = 4) -> 2.998e-5 (L = 8, ratio 128.0)
  and 1.830e-9 (L = 2, ratio 1/128); near field 3.651e-7 -> 2.337e-5 at a = 100, ratio 64.00
  at every a (printed digits).
- P10b REFUTED in part: the radiated measure grows by 221, 200, 137 at a = 30, 40, 50
  (more than 128, as predicted) but by 113 and 124 at a = 70 and 100 (less than 128); at
  a = 15 and 20 by 243 and 270. The box-fundamental argument accounts for the excess
  before a ~ 50 at most; the late emission scales like the quadrupole law. The per-halo
  sum is 11 times the box measure at a = 30 for L = 8 (19 for L = 4), so the gap between
  the isolated-source formula and the box is not mainly the box fundamental.
- P10c HOLDS: from L = 4 to L = 2 the radiated measure falls by 292, 275, 171, 177, 185,
  177, 166 at a = 15, 20, 30, 40, 50, 70, 100 (more than 128 everywhere).

I1 (relativistic initial data, run I-gr B-20261119-154528-9306cb1, stopped by me during
L = 16): L = 4 HOLDS (outer change 5.5e-10 < 1e-9, Hamiltonian residual 5.1e-11, momentum
4.3e-6, max|psi_N| 0.0221, 209 s); L = 8 REFUTED (18 outer iterations, the limit of
make_field.build, ended at a change of 1.8e-6 with contraction 0.81 per iteration;
Hamiltonian residual 1.1e-11, momentum 5.1e-5; max|psi_N| 0.0883 = 4.0 times L = 4, the L^2
scaling holds); L = 16 REFUTED (overflow in the conformal-factor powers of cosmo_id.py
lines 192-233 in the first outer iteration, NaN; stopped after 2 outer iterations, each
running its 60 inner iterations on NaN). The predicted |psi_N| ~ 0.35 at L = 16 is where
the tool fails.

DESIGN.md rewritten with these results: the recommendation moved from a scan in L to a
scan in amplitude at L = 8 (section 3), because the Newtonian problem depends on sigma1 a
only (P4) and the radiated box signal follows sigma^(7/2) (P9), while a smaller box loses
part of the radiation (P10b, P10c) and a larger one fails at the initial data (I1).
