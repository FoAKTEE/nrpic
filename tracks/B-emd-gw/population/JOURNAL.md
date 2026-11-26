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

## Entry 7 (08:12 PST): reruns for the figures; state at the end of the package

The design rerun B-20261119-160611-3ef806d and the L = 8 analysis rerun
B-20261119-160632-e1a1d05 rewrote `results/design.json` and `results/analysis_fidL8.json`
byte for byte (git shows no change); only the figures changed (box ticks; data-driven
limits, the first L = 8 figure had cut the curves above 1e-5). Figures looked at.

Not done (also in README.md and DESIGN.md section 10): card timing at 128^3 and 256^3
(owner at its two card jobs), a full-GR run of this box, relativistic data at L = 8 with
more outer iterations or lower amplitudes, Newtonian runs at 128 and 256 cells.

## 2026-11-21 12:52 PST (lead of batch 5): first full-relativity run of the box; predictions

Written before either run. Aim (decision 0025 item 4): the first full-GR population run of
DESIGN.md section 8 ("scouting of the scan"), sigma1 = 0.028 at L = 8, nc = 3.2, seed 1,
128^3, one particle per cell, to a = 143. sigma1 = 0.028 first because the 64^3 data at
sigma1 = 0.056, L = 8 did not reach the outer tolerance (I1 above) and section 10 expects
0.028 to converge.

Step 1, initial data (processors, `scripts/run_gr_ic.sh 128 "8" "--nc 3.2 --sigma1 0.028
--seed 1 --ppc 1"`, one thread). Predictions: outer change of psi below 1e-9 within the 18
outer iterations of make_field.build; Hamiltonian residual below 1e-10; max|psi_N| about
0.044 (0.0883 of I1 at sigma1 = 0.056 times 1/2, linear in the amplitude; the 128^3 field
shares every mode below the cut with 64^3, so the mesh changes it little); wall time 30-90
min (209 s at 64^3, L = 4, times about 10 for 8x the cells, more outer iterations at L = 8)
[JUDGEMENT]. Refuted if the outer iteration stalls above 1e-7 or gives NaN; then the GR run
is not submitted and the amplitude is halved again.

Step 2, GR run (card, chain, release core-v0.6 executable, deck `inputs/pop_gr_run.athinput`,
submitted by the sequencer of `../cards/` once step 1 has converged and a card slot of the
owner is free). Predictions [JUDGEMENT]:
- G1. The run reaches a = 143 (t = 21.916) without a guard stop; card time 0.2-0.6 h (model
  0.18 card-h of DESIGN.md section 7 plus the dumps: 88 double-precision Z4c dumps of about
  0.35 GB and 22 particle snapshots).
- G2. Mean relative Hamiltonian violation (cstat Hr_mean) below 1e-2 to a = 30 and below 5e-2
  to a = 143 (one particle per cell; the pancake reached 0.0075 at its five dumps after
  crossing with one per cell, ledger row 59); refuted above 0.1 or if it grows without bound.
- G3. Halos: by the sigma1 a scaling (P4), the GR box at a = 2 a_N resembles the Newtonian
  L = 8 run at a_N (fidL8, analysis_fidL8.json): halo counts at a = 60 within the count noise
  of those at a_N = 30, the largest mass within 10 per cent. Relativistic corrections at
  Phi_vir ~ 0.03 are of that order or smaller.
- G4. The TT strain at the box modes is dominated by the near field until a ~ 100 (section
  6 at L = 8), and its rms grows at least as fast as a over 30 <= a <= 143.

Queued behind it (same entry, written before any run): the second amplitude of the scan,
sigma1 = 0.014 (initial data started by the sequencer when the first data are done; GR run
when they have converged). Predictions: data converge faster than at 0.028 (max|psi_N| about
0.022); the GR run behaves as G1-G2 with smaller violations; by the sigma1 a scaling its box
at a = 143 resembles the 0.028 box at a = 71.5 and the Newtonian fidL8 box at a_N = 36
(halo counts within the count noise); G4 with the strain smaller by roughly the square of the
amplitude ratio at equal stage [JUDGEMENT].

## 2026-11-22 17:48 PST (lead of batch 10a): outcome of step 1; why no GR run went to the cards

Outcome of step 1 (initial data, runs B-20261121-202946-ec4a156 for sigma1 = 0.028 and
B-20261121-211707-d795743 for sigma1 = 0.014; numbers from `gr_L8_n128/id.json` and
`make_ic.log` of each):
- sigma1 = 0.028: outer change of psi 3.25e-7 after the 18 outer iterations of
  make_field.build (contraction about 0.66 per iteration from outer 8 to 17, still falling,
  no floor); Hamiltonian residual 2.4e-11; momentum residual 5.6e-6; max|psi_N| 0.0440; wall
  2665 s. Prediction "outer change below 1e-9" REFUTED; "Hamiltonian residual below 1e-10"
  HOLDS; "max|psi_N| about 0.044" HOLDS; wall time within 30-90 min HOLDS. By the rule written
  before the run (change above 1e-7), its GR run was not submitted and the amplitude halved.
- sigma1 = 0.014: outer change 7.3e-8 (below the sequencer's 1e-7, above the 1e-9 I had
  expected), Hamiltonian residual 6.1e-12, momentum 6.7e-7, max|psi_N| 0.0220 (prediction
  "about 0.022" HOLDS; "converges faster" HOLDS: 7.3e-8 against 3.25e-7 after 18 iterations).

Why no card job of this owner since 2026-11-21 22:23 (found from `cards/queue.json`,
`cards/sequencer.py` and `scratch/B-emd-gw/sequencer/state.json`): the sequencer is alive
(pid 2548041) and was doing what the queue says. Entry `pop_s028_gr` needs
outer_last_change_of_psi < 1e-7 and never got it (3.25e-7); card entries are submitted in the
order of the file, so `pop_s014_gr`, whose data meet every condition, waits behind it for
ever; a blocked condition writes nothing to the log. Not the allotment (B had about 3.5 of the
6 card-hours asked left) and not the card queue (no job of B queued).

Correction (this session, before the queue edit): `pop_s014_gr` moves to the front, and a
re-solve of the sigma1 = 0.028 data with 36 outer iterations (`make_ic.py --outer 36`, new
option, same seed) goes behind it, with `pop_s028_gr` reading the re-solved data. The
0.028 data of the first run stay on disk unused.

Predictions for the re-solve, written before it runs [JUDGEMENT]:
- R1. Outer iterations 0-17 print the same digits as the first run (one thread, same input).
- R2. The change falls below 1e-7 by outer 21 and to between 1e-11 and 1e-8 at outer 35
  (contraction 0.6-0.8); Hamiltonian residual below 1e-10 at every outer iteration.
- R3. Wall time 60-100 min on one thread.
Refuted if R1 differs (the solve is not repeatable), if the change stalls above 1e-7 (a floor:
then the sequencer leaves `pop_s028_gr` unsubmitted and the scan continues at 0.014 and
0.007), or on NaN.
The GR-run predictions G1-G4 of the entry of 2026-11-21 12:52 stand for both amplitudes, and
for 0.014 the companion paragraph under them; card time 0.2-0.6 h each (unchanged step count:
same mesh and cfl_number = 0.25, zero shift, no lapse_leak, decisions 0025 item 3, 0027 item 2).

## 2026-11-24 05:15 PST (lead of batch 11): outcomes known before any analysis; predictions for it

Runs read (closed by the sequencer, which then found its queue empty and exited on 2026-11-23
06:55): pop_s014_gr = B-20261123-014847-f295ab4 (Slurm 4921, one segment, 11:12, DONE at
t = 21.916, a = 143.0, cycle 1421); pop_s028_ic2 = B-20261123-014850-7b7d986 (processors);
pop_s028_gr = B-20261123-035002-bcc82bd (Slurm 4941 preempted after 3:10 and resubmitted by the
chain as 4961, which restarted from rst t = 4 and stopped after 2:57 with exit status 3).

Outcomes read from logs and history files (no analysis code yet):
- Re-solve R1 HOLDS (outer iterations 0-17 print the same digits as the first run: `diff` of
  the 18 lines empty). R2 HOLDS: change 7.03e-8 at outer 21; the solve reached its 1e-9
  tolerance at outer 33 (9.1e-10) and stopped there; Hamiltonian residual at most 5.2e-11.
  R3 HOLDS: 4005 s (67 min). max|psi_N| 0.0440 as before.
- G1 for sigma1 = 0.014 HOLDS for the end point (a = 143 without a guard stop); its cost
  prediction 0.2-0.6 card-h FAILS on the low side (0.19 card-h by Slurm accounting).
- G1 for sigma1 = 0.028 FAILS: the guard stopped the run at t = 9.086 (a = 30.7, cycle 599):
  11 non-finite values in one cell (MeshBlock 5, cell (63, 0, 19), position (7.969, 0.031,
  5.219), next to the periodic faces x = 8 and y = 0), with chi = -20.4 and alpha = -230 there,
  6036 particles excised (lapse and horizon excision are off in the deck: alpha_exc = -1,
  ah_exc_factor = -1). `pop.cstat.hst`: K_max turned positive at a = 24.9 and rose to +0.198 at
  a = 30.1; alpha_min fell from 18.5 (a = 22.5) to 14.0 (a = 30.1) while alpha_max = a;
  Hr_max reached 1.6 at a = 19 and stays at 1.7. In the 0.014 run K_max stays negative to the end
  (-9.2e-4 at a = 140.7), and alpha_min/alpha_max is 0.80 at a = 61.8, the same stage by the
  sigma1 a scaling. No cause is named here.
- G2 for 0.014: Hr_mean 1.6e-4 at a = 28.8 (below 1e-2) and 2.85e-2 at a = 140.7 (below 5e-2):
  HOLDS, growing monotonically (1.2e-4 at a = 26, 2.0e-3 at a = 51, 1.8e-2 at a = 97) but slower
  at the end. For 0.028 Hr_mean 4.75e-3 at a = 30.1: the first half HOLDS. Not predicted, on
  record: the mean relative momentum violation Mr_mean grows to 0.20 at a = 143 (0.014) and
  0.053 at a = 30 (0.028).
- The history files of the 0.028 run hold the rows of the preempted segment twice (restart at
  t = 4): any reader keeps the last row of each time.
- Seen during a timing test of the reader (t = 10, a = 36, 0.014): flat TT strain of the
  conformal metric, rms over the box 1.81e-4 raw, gauge piece G_tot 2.5e-5, corrected 1.81e-4.

Predictions for the analysis `scripts/analyze_gr.py` (written before it runs) [JUDGEMENT]:
- A1 (design, near field). The near-field energy of the metric's TT strain,
  Omega_qs = (a/(32 pi rho_c)) sum_k k^2 |h^TT_k|^2 (the measure of analyze.py applied to the
  metric), follows the design's linear value scaled to this box, 1.18e-8 a x 2^6 x
  (0.014/0.0562)^4 = 2.9e-9 a, within a factor 1.5 for 5 <= a <= 40 (junk below 10 per cent of it
  after a = 5, DESIGN.md 5(d)), on the corrected and the raw strain alike. Refuted outside.
- A2 (near-field dominance, G4 made quantitative). Mode by mode over |k| <= 8 k_f, the metric's
  corrected TT strain and the weak-field quasi-static strain S^TT/k^2 computed from the GR run's
  own particles (S = 16 pi rho_c v v/a + 4 dPhi_N dPhi_N, analyze.py) correlate with
  coefficient above 0.9 for 5 <= a <= 100, and their rms agree within 30 per cent. Refuted if
  the coefficient falls below 0.7 before a = 100.
- A3 (G4 growth). The rms of the corrected TT strain grows at least as fast as a^1/2 (the
  strain itself, h ~ Phi^2 is constant in linear theory, rising once halos form) and
  Omega_qs at least as fast as a over 30 <= a <= 143. [G4's "rms grows at least as fast as a"
  read as the energy measure, which is what DESIGN.md section 6 tabulates.]
- H1 (halos, G3). With a common mass limit (100 particles of the Newtonian fidL8 run = 800 of
  this run), the count of FoF halos at a matches fidL8 at a_N = a x 0.014/0.0562 within
  2 sqrt(N) + 2 for a = 49, 64, 81, 100, 121, and the largest mass within 25 per cent
  (resolution: 32 against 64 cells gave -24 to +12 per cent, P5); the five largest fidL8
  halos at a_N = 30 have a GR counterpart within 0.25 (two fidL8 spacings) at a = 121.
- H2. The first FoF group of 100 or more particles of this run appears at 25 <= a <= 45
  (first halo at a = 36 by the scaling with a mass limit eight times higher; here earlier).
- Z (the 0.028 stop, a diagnosis from the run's own dumps, no cause named): the NaN cell lies
  within 0.5 of the densest particle concentration of the last snapshot (a halo at the
  corner of the box), and the largest K of the last dumps sits there. Refuted if the stop
  occurs away from every halo (then a boundary or block-face defect becomes the first
  candidate to test).

## 2026-11-24 05:48 PST (lead of batch 11): Newtonian reference at the same resolution; predictions

The comparison of H1 maps a 128^3 GR box onto the 64^3 Newtonian fidL8 box by two scalings
(box and amplitude); a reference with the GR runs' own Newtonian particles removes both. Card
batch `inputs/batch_newton128.list`: deck `inputs/pop_newton128.athinput` (release core-v0.6 card
build, Fourier Poisson solver, spectral symbol, step 1/64, snapshots every 1/16), particles
`particles_newton.nrp` of the GR initial-data runs (same delta0 and modes as the GR runs),
sigma1 = 0.014 and 0.028, L = 8, 128^3, one per cell, to a = 143. Analysis afterwards with
`analyze.py` (halos, box GW measure at ng = 64) and a halo-by-halo comparison with the GR runs.

Predictions [JUDGEMENT], written before the job is queued:
- N1. Both cases reach t = 21.916 with exit 0; the job uses below 0.5 card-h (about 1400 Fourier
  steps of 0.05-0.1 s with 2.1e6 particles, newtonian_mode.md 7.11, plus 351 snapshots of 126 MB).
- N2 (GR against Newton, same particles and mesh, sigma1 = 0.014). FoF halo counts (>= 100
  particles) at a = 49, 64, 81, 100, 121 equal within 2 sqrt(N) + 2; the ten largest Newtonian
  halos at a = 121 have a GR halo within 0.1 (1.6 cells), with |M_GR/M_N - 1| below 5 per cent
  in the median (relativistic corrections of order Phi ~ 0.01 at this amplitude, plus the
  different force: Z4c fourth-order differences against the spectral Poisson solve). Refuted if
  the median exceeds 10 per cent or a count differs by more than the band.
- N3 (amplitude scaling at 128^3). Newtonian 0.028 at a against Newtonian 0.014 at 2a: halo
  counts within 2 sqrt(N) + 2, largest mass within 5 per cent, for a = 25 to 71.
- N4 (signal). The quasi-static measure Omega_qs of the Newtonian particles equals that of the GR
  particles (analyze_gr.py) within 10 per cent at every common snapshot; the radiated box measure
  of the Newtonian 0.014 run at a = 120 equals the fidL8 value at a_N = 30 times 4.014^(-7/2)
  within a factor 2 (P9's sigma^(7/2) at equal stage; 64^3 against 128^3 particles).

## 2026-11-24 05:58 PST (lead of batch 11): outcomes of the full-GR analysis; the 0.028 stop

Analysis run B-20261124-131918-e71996f (`analyze_gr.py`, both GR runs; JSON complete, figure step
failed on a keyword clash) and its figure/summary run B-20261124-133150-e9ef701 (`--from-json`).
The first attempt B-20261124-130512-d39dae4 failed on the 0.028 run's last dump (written at the
guard stop, its blocks do not tile the box); now skipped. Figures `figs/pop_gr_constraints.png`,
`pop_gr_halos.png`, `pop_gr_gw.png`, `pop_gr_stop.png` looked at; numbers `results/analysis_gr.json`.
[VERIFIED by these runs]

sigma1 = 0.014 (to a = 143):
- A1 HOLDS for 5 <= a <= 30, FAILS from a = 36: Omega_qs of the gauge-corrected metric strain over
  the design's 2.9e-9 a is 1.00 (a = 4.0), 1.09, 1.13, 1.12, 1.11, 1.13 (a = 20.3), 1.21 (25.0),
  1.37 (30.3), then 1.68 (36.1; raw 2.0) and 3.3 (42.3). The departure starts when the first halo
  forms (H2). The design's linear near-field estimate is confirmed in full GR to 9-13 per cent for
  6 <= a <= 20.
- A2 FAILS in part: the corrected strain and the particles' S^TT/k^2 over |k| <= 8 k_f correlate
  at 0.961 (a = 6.3) to 0.998 (a = 25-42), 0.978 (64), 0.946 (72), then 0.899 (81), 0.818 (90),
  0.707 (100); rms ratio (metric/particles) 0.63 (a = 6.3), 0.77 (9.0), 0.83-0.90 (12-42),
  0.95-1.19 (49-100). Above 0.9 only to a = 72 (predicted to 100), and the rms is outside 30 per
  cent at a = 6.3 (the strain is still building up from zero, conformally flat start). Its stated
  refutation (below 0.7 before a = 100) is not reached: 0.707 at a = 100.1.
- A3: Omega_qs grows by 2640 from a = 30.3 to 132.3 (a by 4.4): HOLDS. The rms of the corrected
  strain grows by 1.97 (a^(1/2) would give 2.09): FAILS, narrowly. G4 read as the strain rms: fails;
  as the energy: holds; "near field dominates until a ~ 100": holds to a ~ 80 by the correlation.
- Not predicted, on record: after the halos form the corrected metric energy leaves the particles'
  near field far behind (Omega 3.2e-4 against 5.7e-7 at a = 132), while the strain over
  |k| <= 8 k_f stays within 1.4 of it: the excess sits at high k. The spatial-gauge piece G_tot
  becomes as large as the raw strain (rms 1.21e-3 against 1.09e-3 at a = 132). Whether the high-k
  excess is radiation, a gauge remainder or mesh-scale error (Mr_mean reaches 0.20) is not
  established [TO VERIFY]; no radiated-energy number of the GR box is claimed.
- H1 HOLDS: halos above 100 fidL8 particle masses, GR (a) against fidL8 (a_N): 3/3 (49.1/12.5),
  11/14 (64.1/15.0; stage 6 per cent apart), 16/14 (81.1/20.0), 24/25 (100.1/25.2), 29/25
  (121.1/30.1), all inside 2 sqrt(N) + 2; largest mass +2.8, +13, -5.4, -7.1, -5.6 per cent; the
  five largest fidL8 halos at a_N = 30.1 have GR counterparts at 0.012-0.071 with masses 0.94-1.05
  of theirs.
- H2 HOLDS: no group of 100 particles at a = 30.3, one (M = 0.074) at a = 36.1.
- G2 (Hr_mean 1.6e-4 at a = 29, 2.85e-2 at a = 141) and G3 (counts inside the band at stages
  25-33) hold, as recorded in the 05:15 entry and in H1.
- Companion paragraph: corrected strain rms of 0.028 at a over 0.014 at about 2a: 4.1 (a = 9.0),
  4.2 (12.3), 3.8 (25.0): the square of the amplitude ratio at equal stage HOLDS.

sigma1 = 0.028 (stopped at a = 30.7):
- A1-type check: corrected Omega_qs over its design value (2.9e-9 a x 16) 1.03 (a = 4.0), 1.14,
  1.21, 1.25, 1.36 (16.0), 1.89 (20.3). At equal stage it departs earlier than 0.014 (1.37 at a = 30
  is stage 7.6; 0.028 reaches 1.36 at stage 4.0).
- Halos at a = 30.3 (stage 15.1): 6 against fidL8's 14 at 15.0 (inside the band), largest mass
  0.6565 against 0.6558.
- Z HOLDS: the stop cell lies 0.088 from the densest cloud-in-cell cell of the box at t = 9.0
  (rho/rho_bar = 1583 at 128^3) and next to the largest K of the last good dump (K = 0.265 at
  (0.031, 0.094, 5.281), across the face x = 8|0). K_max of the box: 0.0027 (t = 8.0), 0.012,
  0.025, 0.057, 0.265 (t = 9.0); the smallest lapse within two cells of the stop cell fell from
  18.5 (t = 7.5) to 13.5 (t = 9.0) while the box mean is about a = 30. In the 0.014 run at the same
  stage (a = 50-62) K stays negative everywhere and (K - K_bar)/|K_bar| stays below 0.4.
  [BACKGROUND] the cosmology extension's large-amplitude run (delta = 0.05) failed in the same way
  at a = 17.2 (`cosmo/TESTLOG.md` lines 1844-1852: non-finite metric determinant around the
  overdensity), and in conformal-time slicing a homogeneous collapsing region reaches its crunch
  in finite coordinate time [JUDGEMENT, arithmetic: alpha = a_local, dt = dtau/a_local, a_local ~
  (tau_c - tau)^(2/3) makes the integral finite]. No cause is named.

What would tell the candidates apart, and what is queued (card list `inputs/batch_stop028.list`,
four restarts from the run's restart file at t = 8 to t = 10, the release v0.6 card executable):
the stop is a property of the continuum slice in the collapsing core (then a smaller step does
not move it), of the time step (the 0.014 run has sqrt(2) more steps per halo dynamical time at
equal stage), or of the slicing condition (then a slicing that collapses the lapse faster where
K > 0 passes). Predictions [JUDGEMENT], written before the job is queued:
- X0 (same parameters): the stop recurs at t = 9.09 +- 0.05. Refuted if X0 passes t = 9.3 (then the
  stop depends on round-off, card runs with deposit are not byte-reproducible).
- X1 (cfl 0.125): stops within 0.1 of X0. Refuted if it passes t = 9.3 (then the step is implicated).
- X2 (Gamma-driver shift from t = 8): stops within 0.2 of X0 (the shift does not change the slicing).
  Refuted if it passes t = 9.5.
- X3 (f = 1, step by the light speed): passes t = 9.3 and reaches t = 10 (in a contracting region
  this slicing collapses the lapse with the volume); the background lapse grows as a^3 there, so
  the mean scale factor at t = 10 is about 46 rather than 36 [arithmetic]. Refuted if it stops
  before t = 9.3.
- Card time below 0.3 h for the four (130 to 400 steps each at 0.47 s).

## 2026-11-24 06:10 PST (lead of batch 11): mesh and particle legs of the GR box; predictions

The 0.014 box is the first population run in full GR; G2 item C2 asks for convergence in mesh and
particle number of what the track uses, and the late-time growth of the metric's high-k TT energy
and of the constraint means (05:58 entry) needs a run in which a numerical origin could show.
Queued through `../cards/queue.json` (sequencer): initial data at 128^3 with 8 particles per cell
(`--ppc 2`) and at 256^3 with one per cell (both `--outer 36`, same seed and modes), then their GR
chains with the release v0.6 card executable, deck `inputs/pop_gr_run.athinput` (cfl 0.25, zero
shift, no lapse_leak), the 256^3 chain with Z4c dumps every 0.5. Then the analysis with
`analyze_gr.py` against the 128^3, one-per-cell run B-20261123-014847-f295ab4 (base). Also queued:
`analyze.py` on the Newtonian reference when its card job ends (N1-N4 of the 05:48 entry).

Predictions [JUDGEMENT], written before anything is queued:
- I3. Both initial-data solves reach an outer change below 1e-7 with a Hamiltonian residual below
  1e-9 (the 128^3 solve reached 7.3e-8 in 18 outer iterations); the 256^3 solve takes 3 to 8 hours
  on one thread.
- M1 (256^3). The run reaches a = 143 without a guard stop. Refuted by a stop; then it is compared
  with the 0.028 stop (same halo, stage, K_max history).
- M2. Halo counts above 100 masses of the 128^3 particles (800 of the 256^3 particles) equal the
  base's within 2 sqrt(N) + 2 at a = 64-132, the largest mass within 10 per cent.
- M3. The corrected TT strain over |k| <= 8 k_f stays within 5 per cent of the base's rms to
  a = 50 and within 20 per cent to a = 132; the high-k excess of Omega_qs after a = 50 changes by
  more than a factor 2 with the mesh (a mesh-scale numerical origin). Refuted for the second part
  if Omega_qs at a = 132 agrees with the base within 30 per cent.
- M4. Hr_mean at a = 141 is at least two times smaller than the base's 2.85e-2.
- Q1 (8 per cell). The run reaches a = 143; Mr_mean at a = 141 is at least two times smaller than
  the base's 0.20 (particle noise feeds the momentum constraint) and the high-k excess of
  Omega_qs after a = 50 is at least two times smaller. Refuted if either ratio is below 2.
- Q2. Halo counts and largest masses as in M2, the masses within 5 per cent.
- Card time: 8 per cell 0.3-0.8 card-h; 256^3 2.5-4 card-h (DESIGN.md section 7: 2.9 by the
  rate model).

## 2026-11-24 06:25 PST (lead of batch 11): shell spectra of the GR box's TT energy; prediction

`scripts/fig_gr_spectra.py` plots the per-shell Omega_qs of the corrected metric strain and of the
particles' S^TT/k^2 (both already in `results/analysis_gr.json`) at a = 9, 25, 49, 81, 121.
Prediction [JUDGEMENT]: at a >= 81 the excess (ratio metric/particles above 3) begins above
|k| = 16 k_f, and more than half of the corrected Omega_qs sits above shell 16 (the mesh-scale
half of the spectrum, Nyquist at 64 k_f). Refuted if the ratio exceeds 3 at |k| <= 8 k_f, or if
less than half of Omega sits above shell 16 at a = 121.

Outcome (run B-20261124-134953-18618df, `figs/pop_gr_spectra.png` looked at) [VERIFIED by it]:
- REFUTED in its first part: at a = 81 and 121 the per-shell ratio metric/particles passes 3 at
  |k| = 5 and 4 k_f (12 at a = 49), not above 16; it rises to about 1e3 near 30-40 k_f. HOLDS in
  its second part: 82 and 87 per cent of the corrected Omega_qs lie above shell 16 at a = 81 and
  121 (60 per cent at a = 49, none at a <= 25).
- At a = 9 and 25 the metric follows the particles to |k| = 10-30 k_f; above that the particles'
  spectrum flattens (shot noise of one particle per cell in the cloud-in-cell estimate) while the
  metric falls by orders of magnitude: the early rms ratio 0.63 (A2) is the particles' noise, not
  the metric.
- [JUDGEMENT, not tested] the excess after halo formation, 1e3-1e4 times any Newtonian box
  measure scaled to this amplitude, is more likely the coordinates of the zero-shift slice
  following the normal observers into the halos (a gauge effect beyond the second-order G_tot)
  than radiation. A run in which it could fail: the same box with a Gamma-driver shift (queued
  below).

## 2026-11-24 06:30 PST (lead of batch 11): gauge leg of the GR box; prediction

`pop_s014_gr_gd` (sequencer, card chain, release v0.6): the 0.014 box from the same initial data
to a = 143 with the Gamma-driver shift of first_source's second-gauge run (shift_Gamma 0.75,
shift_eta 1, shift and lapse advection 1; cfl 0.25 <= 0.6, decision 0027 item 2), same slicing.
It is also the gauge leg of G2 item C2 for the population box. Predictions [JUDGEMENT]:
- GD1: reaches a = 143 without a guard stop; card time 0.2-0.5 h.
- GD2: halo counts and largest masses as in the zero-shift run (counts within 2 sqrt(N) + 2, the
  largest mass within 5 per cent at a = 64-132): the shift changes coordinates, not physics.
- GD3: the corrected TT strain over |k| <= 8 k_f within 20 per cent of the zero-shift run's to
  a = 100; above 16 k_f the corrected Omega_qs at a = 121 at least ten times smaller than the
  zero-shift run's 2.3e-4 (the excess is coordinate motion). Refuted if it agrees within a factor
  3 there (then the excess is not a spatial-gauge effect: mesh or physics, for the legs to decide).

Figures redrawn (06:55): `pop_gr_halos`, `pop_gr_stop` with shorter labels and wider spacing from
the same JSON (run B-20261124-135404-ca06d42; looked at, labels no longer cut). The mosaic with the
full colour range of K (B-20261124-135412-ab31dae) washes the plane out, so the package keeps the
first drawing (B-20261124-133709-85c4be7, 99.5 per cent range, saturated in the core) and the
script returns to that range.

## 2026-11-24 09:29 PST (resumed lead session, batch 11b): Newtonian reference moved to processors; prediction

The cards are held by another user's priority job until about the morning of 2026-11-25
(decision 0032 item 2), so card job 5167 (B-20261124-131438-5d7e049) would wait about a day. The
Newtonian reference needs no card: the release core-v0.6 processor build
(`.work/build_cpu_v06/src/athena`, one thread; the Fourier solver is not tested with the threaded
build, READY of core_nrpic_v06) runs the same deck `inputs/pop_newton128.athinput` with the same
particle files, one registered local run per amplitude (`newton_s014`, `newton_s028`), one core
each. When both have started cleanly, card job 5167 is stopped and the sequencer's analysis entry
points at the two processor runs. Nothing else changes; N2-N4 (05:48 entry) stand as written.

Prediction [JUDGEMENT], before the runs: N1p. Both reach t = 21.916 (a = 143) with exit 0; each
takes 0.5 to 3 hours on one core (about 1400 steps; a 128^3 Fourier solve and 2.1e6 particles
per step at 1-6 s) plus 351 snapshots of 126 MB. Refuted by a non-zero exit or more than 5 hours.

09:37 (same session): both processor runs started cleanly (2097152 particles read, snapshots
00000-00002 written). Measured rate: one snapshot (four steps) every 132 s, 33 s per step on one
core, so about 13 h per run for 1400 steps: the time part of N1p ("0.5 to 3 hours", refuted above
5 hours) will FAIL; the cause of the slow step (the Fourier solve on one core of the -O2 -g
reference build, or the particles) is not tested. Kept anyway: the cards are held until about the
morning of 2026-11-25 and the result arrives before that. Card job 5167 was cancelled before it
started (`nrpic-run stop`, then `finish`, which records it as failed with exit 1: it never ran);
its slot goes to the gauge leg pop_s014_gr_gd through the sequencer.

## 2026-11-25 04:00 PST (lead of batch 17): outcomes of X0-X3 and GD1; predictions for two continuations

Queue entries q0004 (gauge leg, run B-20261124-210431-6bf48af, Slurm 5208), q0005 (X0-X3,
B-20261124-210432-6c4d005, Slurm 5209) and q0006 (particle leg, B-20261124-223926-33194d9, Slurm
5222, 5231, 5238) ended overnight. `nrpic-run finish` of the three was started before any analysis;
the hashing of 45-62 GB per run takes longer than this session, so the analyses below were started
while it ran (they only read the run directories). [VERIFIED by the runs named]

X0-X3 (analysis run B-20261125-115619-ad8b3f4, `scripts/analyze_stop028.py`, figure
`figs/pop_stop028.png`, looked at):
- X0 HOLDS: the guard stop recurs at t = 9.08646 (cycle 599), the base run's time and cycle to
  every printed digit; K_max, chi_min, Hr_mean of X0 equal the base's at every history row
  (K_max 0.1984 at t = 8.977). The restart repeats the run here, although card runs with deposit
  are not promised to repeat.
- X1 HOLDS: half the step stops at t = 9.07865 (cycle 667), 0.008 before X0; K_max 0.227 at
  t = 8.993. The step is not what stops the run.
- X2 REFUTED (predicted: stops within 0.2 of X0, refuted if it passes 9.5): with the Gamma-driver
  shift (0.75, eta 1, advection 1) from t = 8 the run reaches t = 10 (a = 36) with exit 0; the
  largest K of the box turns negative within 0.25 of the restart (-0.011 at t = 8.48) and stays
  negative (-0.0032 at t = 9.98) where the zero-shift run climbed to +0.2; the smallest lapse rises
  (22.1 at t = 9.98) where it fell to 14. The price: Hr_mean 1.0e-2 at t = 8.98 against 4.7e-3 of
  X0 at the same time, 2.1e-2 at t = 9.98, Mr_mean 0.21. With a run in which it could have failed:
  the zero shift is implicated in the stop of the 0.028 core at t = 9.09 (its coordinates follow
  the collapse); whether the shifted run lasts to a = 143 is not known.
- X3 NOT RUN (exit 1 at start): `Parameter 'dt_lightspeed' in block 'z4c' on command line not
  found`: a restart accepts on the command line only parameters its stored input has, and the base
  deck had no `dt_lightspeed`. A setup error of this lead (batch 11), on record. Not retried: the
  slicing leg needs a fresh start with `dt_lightspeed` in the deck, and X2 already separates the
  candidates the restarts were for.
- Card time of the batch: 13:45:41-13:48:31 PST, 0.05 card-h (predicted below 0.3: holds).

GD1 (gauge leg) HOLDS in its first part: t = 21.916 (a = 143) at cycle 1421, exit 0, no guard file
(chain events of the run; `chain/seg001.job5208.a1.log`). Its time part FAILS narrowly: one segment
of 11.1 min (13:45:41-13:56:47), 0.185 card-h against the predicted 0.2-0.5.

Particle leg (q0006): cut, not finished. Two segments, each ended by SIGTERM (preemption at
15:42 and 17:08 PST); the chain script of release v0.6 counted both against MAX_SEGMENTS = 2 and
ended the chain FAILED when job 5238 started at 20:16. Last history row t = 17.477 (a = 94.8,
cycle 1136); newest restart rst/pop.00008.rst (t = 16.0, with .prt). Q1 (judged at a = 141)
cannot be judged from this run; Q2 and the part of Q1 at a <= 95 are judged from analysis
B-20261125-115657-91b61ec below.

Two continuations, both card batches restarting a closed run's restart file into a new run
directory (release v0.6 card executable, the runs' own; `dt_gauge` cannot be added at a restart
of a v0.6 file for the reason X3 shows; the step stays 0.25 cells, below the bounds of decisions
0027 and 0035). Predictions [JUDGEMENT], written before they are queued:
- P8C (`inputs/batch_p8cont.list`, rst/pop.00008.rst of B-20261124-223926-33194d9 to
  t = 21.916). P8C1: exit 0 at t = 21.916 without a guard stop, below 0.4 card-h. Refuted by a
  stop or a non-zero exit. P8C2: the history rows at t = 16.0-17.48 equal the cut run's (Hr_mean
  and K_max within 1e-6 relative; X0 repeated to every digit). Refuted above 1e-3. Q1 is judged
  with the union of both directories.
- S28GD (`inputs/batch_s028gd.list`, rst/pop.00004.rst of B-20261123-035002-bcc82bd, the X2
  gauge from t = 8 to t = 21.916). S1: reaches t = 21.916 without a guard stop and with Hr_mean
  below 0.2 at the end. Refuted by a stop or a larger Hr_mean (then the shifted gauge only delays
  the failure). S2: halo counts above the common mass limit at a (0.028) equal those of the
  0.014 gauge leg at the same stage (a' = 4a, 0.014 at a' = 64-143 against 0.028 at a = 16-36)
  within 2 sqrt(N) + 2, largest mass within 10 per cent. S3: raw TT strain rms of 0.028 at a over
  0.014 (gauge leg) at the same stage between 3 and 5.5 (square of the amplitude ratio, 4, as the
  zero-shift companion paragraph found 3.8-4.2). Card time below 0.3 h.

## 2026-11-25 04:10 PST (lead of batch 17): outcomes of GD2-GD3 (gauge leg)

Analysis B-20261125-115558-2ab4161 (`analyze_gr.py` on B-20261124-210431-6bf48af, closed) and the
comparison with the zero-shift base B-20261124-131918-e71996f, run B-20261125-120818-1dfae55
(`scripts/compare_legs.py`, figure `figs/pop_legs.png`, four panels looked at). [VERIFIED by them]
- GD2 HOLDS for the counts, FAILS for the masses: halo counts above the common mass limit agree
  within 2 sqrt(N) + 2 at every snapshot (11/11 at a = 64, 13/16 at 81, 25/24 at 100, 31/29 at
  121, 30/28 at 132), but the largest halo of the shifted run is 10-16 per cent heavier at
  a = 64-132 (ratios 1.13, 1.12, 1.16, 1.12, 1.12, 1.14, 1.13, 1.10), predicted within 5. Against
  the Newtonian fidL8 box at equal stage the shifted run's largest mass is +3.8 per cent (a = 100)
  and +6.6 (a = 121), the zero-shift run's -7.1 and -5.6: the two gauges bracket the Newtonian
  value. [JUDGEMENT, not tested] friends-of-friends links in coordinate distance, and the two
  spatial gauges place the particles of a collapsed halo differently; the count, which needs only
  the mass limit, does not see it.
- GD3 HOLDS in both parts. Corrected strain over |k| <= 8 k_f, shifted over zero-shift: 1.000 to
  a = 36, 0.984 (49), 0.950 (64), 0.905 (81), 0.865 (90), 0.803 (100), then 0.68 (121): within 20
  per cent to a = 100, just. Omega_qs above 16 k_f at a = 121: 2.08e-7 against 1.97e-4, 950 times
  smaller (predicted at least ten). The high-k excess of the zero-shift run after halo formation is
  therefore the zero-shift coordinates following the infall, not radiation and not mesh error: a
  run in which it could have failed (refuted had the shifted run kept it within a factor 3).
- Not predicted, on record: in the shifted gauge the spatial-gauge piece stays small (rms_G
  1.0e-6 against an rms strain 9.9e-5 at a = 132; zero-shift 1.2e-3 against 1.1e-3), the metric
  strain keeps its correlation with the particles' S^TT/k^2 over |k| <= 8 k_f above 0.93 to
  a = 132 (0.971 at a = 100, where the zero-shift run had 0.707) with an rms ratio 0.95-1.08 from
  a = 56 on, and the total corrected Omega_qs (5.4e-7 at a = 121) stays below the particles'
  quasi-static estimate (8.3e-7). Hr_mean is 4.8 times smaller than zero-shift at a = 141
  (5.98e-3 against 2.85e-2); Mr_mean is the same in both gauges (0.203): the momentum-constraint
  growth does not depend on the spatial gauge (Q1 and M4 test particle noise and mesh).
- Consequence for the track: the population's GW measure is read in the Gamma-driver gauge from
  now on; the zero-shift strain after a = 36 is a coordinate artefact at high k. A1-A3 (05:58
  entry) were judged on the zero-shift run: A2's late failure (correlation below 0.9 after a = 72)
  is a failure of that gauge (above 0.9 to a = 132 in the shifted run); A1's departure from the
  linear design value is not (shifted run: Omega_cor over the design 1.36 at a = 30, 1.56 at
  a = 36, 1.95 at a = 42; zero-shift 1.37, 1.68, 3.3): it is the growth of the halos, which the
  linear design does not hold. Not yet done: the same comparison with the GW measure of the
  Newtonian reference at the same particles (N4).

## 2026-11-25 04:20 PST (lead of batch 17): Q1-Q2 to a = 94.8 (particle leg, cut)

Analysis B-20261125-115657-91b61ec (`analyze_gr.py` on B-20261124-223926-33194d9, 8 per cell, to
t = 17.477) and the comparison of both legs with the base, B-20261125-121830-9ecb59c (figure
`figs/pop_legs.png`, now with the gauge and particle legs, looked at). [VERIFIED by them]
- Q1 (judged at a = 141 as written; this is its part up to a = 94.8). First part on course:
  Mr_mean 8 per cell over one per cell 0.43 (a = 25), 0.21 (49), 0.26 (81): the momentum
  constraint falls 2.3-4.7 times with eight times the particles, more than the square root of 8.
  Second part FAILS already: Omega_qs above 16 k_f is the base's to three digits after a = 36
  (2.035e-6 against 2.033e-6 at a = 56, 5.193e-5 against 5.192e-5 at a = 90; predicted at least two
  times smaller). The high-k excess does not depend on particle number, consistent with GD3 (it is
  the zero-shift coordinates). Hr_mean 1.5 times smaller (7.6e-3 against 1.17e-2 at a = 81).
- Q2 to a = 90: counts HOLD (9/11 at a = 64, 11/15, 14/16, 19/22 at a = 90, inside 2 sqrt(N) + 2);
  largest masses within 5 per cent FAIL at a = 64 (1.41: a merger counted at a different moment
  or linked differently; the linking length is b = 0.2 of the own mean spacing, half as long here)
  and hold at a = 72-90 (1.048, 1.014, 1.016).
- Not predicted: the metric strain of the eight-per-cell run equals the one-per-cell strain over
  |k| <= 8 k_f to 1e-3 at every dump to a = 90 (band ratios 1.000), and K_min, K_max of the box agree
  to 1e-7 relative early and 1e-2 at a = 81: at this mesh the metric is set by the mesh-deposited
  density, which one particle per cell with the PCS cloud already samples; particle number moves the
  constraints and the halo catalogue, not the strain.
- Q1 is judged in full when the continuation q0042 (P8C) has run; the leg is merged with the cut
  run's directory in the analysis (snapshots to t = 17 from the cut run, from t = 18 from the
  continuation).

## 2026-11-25 08:58 PST (lead of batch 21): N2-N4 against both gauges; predictions

The Newtonian analysis B-20261125-122434-060d53d (`analyze.py`, cases newton_s014, newton_s028 at
128^3 with the GR runs' own particles, GW box at ng = 64) ended 12:49Z with exit 0 and is closed
(`nrpic-run finish`, 8 files hashed). Its figures and `results/analysis_n128.json` were copied into
the package by the script; committed now. Next: `scripts/compare_newton.py` twice, once with the
zero-shift run's JSON (B-20261124-131918-e71996f/analysis_gr_s014.json), once with the
Gamma-driver leg's (B-20261125-115558-2ab4161/analysis_gr_gd.json). N2-N4 (05:48 entry of
2026-11-24) are judged as written, on each gauge separately.

Disclosure before the predictions: while checking the JSON layouts I saw the largest masses at
a = 132 (Newton 1.794, zero shift 1.743, Gamma driver 1.912) and the log's halo counts of the
Newtonian runs; nothing else of the comparison.

Added prediction [JUDGEMENT], before the runs:
- GN1 (which gauge is closer to Newton). The Gamma driver drives the conformal connection to zero,
  the transverse condition of the conformal metric, which is the spatial part of the Poisson
  gauge, in which particle positions are the Newtonian ones to first order; zero shift lets the
  metric take a longitudinal part, which displaces the coordinates of a collapsed halo. So the
  median |M_GR/M_N - 1| over the matched ten largest halos, averaged over a = 81-132, is smaller in
  the Gamma-driver leg than in the zero-shift leg. Refuted if it is larger (then the 10-16 per cent
  gauge spread, R23, is not ordered by this argument).
- GN2. N4's ratio Omega_qs(GR particles)/Omega_qs(Newton particles) is the same in both gauges to
  10 per cent (the particles' estimate depends on the gauge only through the positions); the two
  measures use different grids (the GR dumps' own mesh against ng = 64), so a departure of N4 that
  grows with a in both gauges alike is first read as the grid, not as relativity.

## 2026-11-25 09:00 PST (lead of batch 21): N2-N4 outcomes; a band test of N4 predicted

Comparisons B-20261125-165836-70b17b6 (zero shift) and B-20261125-165845-0621554 (Gamma driver),
`compare_newton.py`, numbers recomputed by the lead from their `compare_newton.json`. [VERIFIED by
these runs]
- N2 HOLDS in both gauges. Counts of halos >= 100 particles inside 2 sqrt(N) + 2 at every common
  catalogue a = 49-132 (zero shift 16/20, 44/46, 53/49, 75/88, 83/90, 93/90, 108/106, 104/101;
  Gamma driver 15/20, 47/46, 48/49, 73/88, 75/90, 92/90, 98/106, 108/101, GR/Newton). At a = 121
  all ten largest Newtonian halos have a GR halo within 0.1 in both gauges; median |M_GR/M_N - 1|
  2.5 per cent (zero shift) and 2.8 per cent (Gamma driver), predicted below 5. Earlier the median
  is larger (a = 49: 22 and 14 per cent with 5 of 10 matched; the catalogues differ by 1.6 per
  cent in a there, while the halos are forming).
- N3 HOLDS. Newtonian 0.028 at a against 0.014 at 2a, a = 25-60: counts 20/20, 27/28, 46/49,
  87/90, 94/106 inside the band; largest-mass ratio 0.962, 0.964, 0.981, 0.982, 0.996 (within 5
  per cent).
- N4 FAILS as written in both gauges. Omega_qs of the GR particles over that of the Newtonian
  particles is 11.7 at a = 2.3, 4.3 at 4.0, 1.94 at 9.0, 1.35 at 20, 1.17 at 36 (zero shift; the
  Gamma driver agrees to 2 per cent to a = 30), then 1.15-1.55 (zero shift) and 1.3-2.2 (Gamma
  driver) to a = 132; predicted within 10 per cent at every snapshot. Not predicted: the GR
  metric's corrected strain over the Newtonian particles' estimate is 1.01, 1.09, 1.11, 1.08,
  1.03, 0.99, 0.99, 1.00, 1.03 at a = 4-36 in both gauges (0.50 at a = 2.3), so the metric agrees
  with the Newtonian particles and the GR particles' own estimate is the outlier early on; after
  a = 42 the zero-shift metric departs by factors 1.8 to 860 (the coordinate effect of GD3), the
  Gamma-driver metric stays at 1.04-1.47.
- GN1 REFUTED. Mean over a = 81-132 of the median |M_GR/M_N - 1|: zero shift 2.9 per cent, Gamma
  driver 6.0 per cent; the largest halo is 1.6-5 per cent lighter than Newton's at a = 81-132
  with zero shift and 6.6-10 per cent heavier with the Gamma driver. With the same particles the
  zero-shift masses are the closer ones; the earlier statement that the gauges "bracket" the
  Newtonian mass (batch 17, against the fidL8 box with other particles) does not survive the
  same-particle reference. The Poisson-gauge argument does not order the spread. [JUDGEMENT, not
  tested] candidates: friends-of-friends links in coordinate distance, and the shifted
  coordinates of a collapsed halo are more compact; a mass by proper distance at the particles
  would test it.
- GN2: the N4 ratio is the same in both gauges to 2 per cent up to a = 30 and departs after
  (1.17 against 1.22 at a = 36, 1.55 against 2.19 at a = 132): HOLDS to a = 36, FAILS after.

Prediction [JUDGEMENT] for the band test `scripts/n4_band.py` (same two JSONs and the Newtonian
spectra at a = 9.8, 19.4, 39.1, 68.1, 97.5; GR spectra interpolated per shell in log a), before
the run: NB1. The early excess of N4 is the grid: the GR particles' estimate on the 128^3 dump
mesh holds shells 33-64 k_f that ng = 64 does not; restricted to |k| <= 32 k_f the ratio is
within 10 per cent of 1 at a = 9.8-39 in both gauges, and more than half of the GR estimate at
a = 9.8 lies above 32 k_f. Refuted if the ratio over |k| <= 32 k_f exceeds 1.3 at a = 9.8 (then
the two estimates differ in the source itself: normalisation, velocities or potential).

## 2026-11-25 09:02 PST (lead of batch 21): NB1 outcome

First band run B-20261125-170051-49ada01 compared unlike units (the Newtonian shell spectra of
`analyze.py` are a^4 rho_qs, not Omega); fixed in `n4_band.py` (divided by a rho_c), kept on record
as a defective analysis. Rerun B-20261125-170116-0b635a0, figure `fig_n4_band.png` in its run
directory looked at (left: shell spectra at a = 19.4 and 97.5; right: band ratios). [VERIFIED by
it]
- NB1 REFUTED. The GR particles' quasi-static measure holds nothing above 8 k_f before a = 40 (the
  band sums over |k| <= 8, 16, 32 and over all shells agree to 1e-3; fraction above 32 k_f 0.000 to
  a = 39), so the early N4 excess is not the grid. Over |k| <= 32 k_f the ratio GR/Newton is 3.38
  (a = 4.9), 1.85 (9.8), 1.37 (19.4), 1.16 (39.1) in the zero-shift gauge, the Gamma driver within
  1 per cent of it to a = 19 (predicted within 10 per cent of 1; refuted above 1.3 at a = 9.8).
  The left panel shows the two spectra with the same shape at a = 19.4, the GR one higher by a
  factor uniform in k: a time-dependent normalisation of one estimator, not a difference of
  physics, since the GR metric itself agrees with the Newtonian particles' estimate to 1-11 per
  cent at a = 4-36 (N4 entry above). After a = 60 the Gamma-driver ratio grows in the high shells
  (1.48 over |k| <= 32 at a = 68, 1.71 at 97.5) and the zero-shift one less (1.15, 1.23).
- [TO VERIFY] cause: one snapshot through both estimators (`hqs_particles` of `analyze_gr.py` and
  `TTBox.source` of `analyze.py`) on the same GR particle file at a = 5 and 20 decides between the
  velocity convention of the GR snapshot (u, W, factors of a) and the potential term. Until then
  the GR-particle Omega_qs of analyze_gr.py (A1-A3, GD3 "particles' estimate") is not used as a
  reference; the metric's corrected Omega_qs and the Newtonian particles' estimate are.

## 2026-11-25 09:03 PST (lead of batch 21): same particles through one estimator; prediction

`scripts/vel_check.py`: GR particle snapshots of B-20261123-014847-f295ab4 (pop.part.00001, 4, 7,
10: a = 2.3, 9.0, 20.3, 36) and the Newtonian snapshots of B-20261124-172958-fc4a2cf at the same t
(within 0.01), matched by tag: rms of the velocity v (GR u/(a W), Newton p/a) and their
correlation, the rms position difference in cells, and Omega_qs of both particle sets through the
SAME estimator (`analyze.TTBox`, ng = 64).

Prediction [JUDGEMENT], before the run: VC1. The particle data agree (rms velocities within 5 per
cent, correlation above 0.99, positions within 0.1 cell at a <= 20), and through one estimator the
two Omega_qs agree within 10 per cent at every epoch: the N4 excess is in the GR path
(`hqs_particles` on the 128^3 dump mesh). Refuted if the one-estimator ratio reproduces N4's
(about 11.7, 1.9, 1.35, 1.17): then the GR particles' velocities or positions differ from the
Newtonian ones, and the velocity ratio says which.

## 2026-11-25 09:05 PST (lead of batch 21): VC1 outcome; VC2 predicted

Run B-20261125-170321-cd30c0b (`vel_check.py`, 4 epochs). [VERIFIED by it]
- VC1 REFUTED in its second part. The particle data agree: rms velocity ratio GR/Newton 1.006,
  1.005, 1.006, 1.003 at a = 2.3, 9.0, 20.3, 36 (correlation above 0.9997, least-squares factor
  1.003-1.006), positions within 0.0016, 0.010, 0.031, 0.079 cells rms (largest 0.73 cells at
  a = 36), total masses equal to 4.4e-4. But through one estimator the GR set gives 11.6, 1.92,
  1.33, 1.14 times the Newtonian Omega_qs (N4's numbers), and the potential term alone 26.1, 2.70,
  1.55, 1.21 times: the excess is in the potential term, with positions that agree to 0.002 cells.
- VC2 [JUDGEMENT], before the run: the GR particles carry unequal masses (the initial data weight
  each particle by the local metric), the Newtonian ones equal masses; a mass weight constant in
  time adds a density term that does not grow, so its share of the potential term falls with a.
  With the GR positions and the Newtonian masses the ratio of the potential term is within 10 per
  cent of 1 at every epoch, and the relative spread of the GR masses is of the order of the
  density contrast at a = 2.3 (1e-3 to 1e-2) while the Newtonian masses are equal to round-off.
  Refuted if the ratio stays above 1.3 at a = 9 with the masses exchanged.

## 2026-11-25 09:07 PST (lead of batch 21): VC2 outcome; the cause of the N4 failure

Run B-20261125-170535-84c9ba5 (`vel_check.py` with the masses exchanged; figure
`fig_vel_check.png` in its run directory looked at: the right panel's y label is cut at the top, a
cosmetic defect). [VERIFIED by it]
- VC2 HOLDS in its main part: with the GR positions and the Newtonian masses the potential term of
  the GR set over the Newtonian one is 1.004, 0.988, 0.965, 0.906 and the full source 1.010, 1.000,
  0.989, 0.944 at a = 2.3, 9.0, 20.3, 36 (within 10 per cent; refuted above 1.3 at a = 9). Its side
  statements FAIL: the relative spread of the GR masses is 0.0283 (predicted 1e-3 to 1e-2) and of
  the Newtonian masses 2e-4 (predicted round-off; they come from the target density and the
  Jacobian, `make_ic.py` line 23).
- Cause of the N4 failure, named after a run in which it could have failed (VC2): the GR particle
  file carries the rest-mass weight of the initial data, m W psi^6 (1 + dN - 2 psiN)/(1 + dN)
  (`make_ic.py` line 133), a weight that is constant along each particle; `hqs_particles` of
  `analyze_gr.py` deposits it as if it were the Newtonian mass, which adds a density term of the
  size of the potential (2.8 per cent rms) that does not grow and dominates the lowest k early on.
  It is an error of that estimator, not of the run: the GR metric and the Newtonian particles agree
  (N4 entry above), and the GR particles move as the Newtonian ones do (VC1: velocities 0.3-0.6 per
  cent, positions 0.002-0.08 cells to a = 36).
- Consequences [JUDGEMENT]: every use of `Omega_qs_part`, `spec_qs` and `cmp_*_qs` of
  analyze_gr.py is biased high at early times (A1-A3 of 2026-11-24 05:58 and GD3's "particles'
  estimate" of 2026-11-25 04:10: the ratio "corrected 5.4e-7 against particles 8.3e-7 at a = 121"
  is not a reference until redone). The fix is one line (deposit m / (W psi^6 ...) or equal
  masses, as `vel_check.py` does); the rerun of analyze_gr.py over the two GR runs takes about an
  hour of processors and is the next session's (not done here; prediction first). N4 stays FAILED
  as written, on record, with this cause; after a = 36 the same-particle ratio with equal masses is
  not yet measured.

## 2026-11-25 09:24 PST (lead of batch 21): second part of N4

The radiated part of N4 (the Newtonian 0.014 run's radiated box measure at a = 120 against fidL8
at a_N = 30 times 4.014^(-7/2), within a factor 2; written 2026-11-24 05:48) was not yet judged.
Script `scripts/n4_rad.py` reads the two committed analyses. No new prediction: N4's own bound
applies; the side columns (rad1, switch-off) are reported without a bound.

Outcome (run B-20261125-172136-3e920ab, `n4_rad.json`). [VERIFIED by it] The radiated part of N4
FAILS: Omega_rad of the Newtonian 0.014 run at a = 120.3 is 6.10e-9 against 2.10e-8 predicted
from fidL8 (2.72e-6 at a_N = 30.07, times 4.014^(-7/2)), a ratio 0.29, outside the factor 2. The
measure with one boundary term removed gives 0.28; the switch-off measure (both terms kept)
gives 1.56, inside. [JUDGEMENT, not tested] the radiated measure subtracts the quasi-static
boundary terms, whose size depends on the snapshot cadence and on the particle number (eight
times more particles per mode volume here than in fidL8), so the sigma^(7/2) map between the two
boxes holds for the switch-off measure and not for the remainder; a run in which this could fail
is the fidL8 box re-analysed at the 128^3 cadence, or the 128^3 box at fidL8's. N4 is FAILED as
written in both parts; the GR question it was meant to serve (the GR metric against the
Newtonian particles) is answered by the metric ratio above (within 11 per cent to a = 36).

## 2026-11-25 18:35 PST (lead of batch 23): the three ended entries; what is judged and how

q0007 (mesh leg B-20261125-093500-242d3a3, seven chain segments, Slurm 5278-5326), q0042 (P8C,
B-20261125-221742-5100a22, job 5333) and q0044 (S28GD, B-20261126-011415-449c8ce, job 5342) have
ended. `nrpic-run finish` started on all three before any analysis (q0042, q0044 closed
completed; q0007 closed as failed, its hashing of 272 GB runs in the background).

Disclosure before the analyses (seen while locating outputs; nothing else read): the mesh leg
ended with a guard stop (`pop.guard.txt`: non-finite fields at t = 18.2109, cycle 2332, a = 102;
chain FAILED, athena exit 3); its history shows K_max of the box above zero from t = 17 (0.0015)
rising to 0.022 at t = 18.12, Hr_mean 0.0151 against the base's 0.0186 and Mr_mean 0.154 against
0.168 at t = 18 (one-line history print, not a registered analysis). Both batch continuations
end "Terminating on time limit" at t = 21.916 with exit 0 (P8C 13 min 25 s, S28GD 7 min 39 s).

Method change, decided before the runs (risk R25, VC2 of batch 21): `analyze_gr.py` gets
`--equal-mass` (every particle the mean mass in the halo finder's masses and in S^TT of the
particles), the dump time read from the file header (the 256^3 chain wrote dumps every 0.5 with
extra ones at segment ends, so index x 0.25 is wrong there), `--times`/`--halo-times` to restrict
the 256^3 analysis to the snapshot times, and DIR1+DIR2 for a run and its continuation (later
directory wins at equal t). Every halo number of this session is with equal masses, the base and
the gauge leg recounted the same way (halos only), so the comparisons do not mix weights.

How each prediction is judged (written before the analyses run):
- M1 as written: refuted by the stop (judged from the guard file and history; compared with the
  0.028 stop: K_max > 0, the zero shift, X2).
- M2 at the snapshots a = 64, 72, 81, 90, 100 (the run ends at a = 102; a = 121, 132 do not
  exist); M3 first part to a = 50 as written, second part at a = 81-100 instead of 132 (the
  written refutation at a = 132 cannot be reached); M4 at a = 141 cannot be judged: reported at
  equal a to 100 and marked not judgeable as written.
- P8C1 (exit 0 at t = 21.916, below 0.4 card-h, no guard), P8C2 (history rows t = 16.0-17.48 of
  the continuation against the cut run, relative 1e-6 holds, 1e-3 refutes).
- Q1 at a = 141 over both directories (Mr_mean from the history row t = 21.727; the high-k
  excess of the corrected strain above 16 k_f at every common gauge-corrected dump after a = 50).
- S1 as written. S2 and S3 say "at the same stage" and then write a' = 4a; the stage is sigma1 a
  (P4, analyze_gr.py), so the same stage of 0.028 at a is 0.014 at a' = 2a, as N3 and the
  zero-shift companion paragraph used. The parenthesis is an error of the batch-17 prediction.
  Judged at the same stage (a' = 2a, 0.028 at a = 32-72 against the 0.014 gauge leg at
  a' = 64-143), the bounds as written; the as-written pairing a' = 4a reported beside it.

## 2026-11-25 18:50 PST (lead of batch 23): the gauge at a second mesh; decision and predictions

Decision: a run is needed. The track reads the population's GW measure in the Gamma-driver gauge
since GD3 (04:10 entry); the only second mesh, the zero-shift 256^3 leg, stopped at a = 102 with
K_max of the box above zero before the stop (history, 18:35 entry), as the zero-shift 0.028 box
did at 128^3 (Z, X2). So neither the mesh convergence of the measure the track uses nor any mesh
convergence past a = 100 exists, and C2 (three-way convergence) and C11 (its figures) need the
Gamma-driver box at 256^3. One queue entry, priority 2: `pop_s014_gr256_gd`, the q0007 command
with the gauge-leg shift flags (shift_Gamma 0.75, shift_eta 1, shift and lapse advection 1), the
256^3 initial data B-20261124-135030-b54972f, dumps every 1.0 (at the snapshot times, where the
gauge-corrected strain is measured; halves the 120 GB of dumps of q0007), restart every 1.0
(about 10 min of card time), the release core-v0.7 card executable and chain (writes a restart
file on SIGTERM; a run without the signal writes the bytes of v0.6, CHANGELOG core-v0.7 item 1),
ceiling 6 card-h, no dt_gauge (the gauge leg had none; cfl 0.25 is below the printed bounds).

Predictions [JUDGEMENT], written before it is queued (GM = 256^3 Gamma driver, GD = the 128^3
gauge leg B-20261124-210431-6bf48af, analyses with --equal-mass):
- GM1. Reaches t = 21.916 (a = 143) without a guard stop; K_max of the box stays below zero after
  t = 9 as in GD. Refuted by a stop or by K_max > 0 after t = 9.
- GM2. Corrected TT strain over |k| <= 8 k_f within 5 per cent of GD's to a = 64 and within 20
  per cent to a = 132. Omega_cor (all shells) at a = 121 is 1.0 to 2.0 times GD's (finer halo
  cores add k^2-weighted power). Refuted if the band ratio leaves 0.8-1.2 before a = 100, or the
  Omega ratio leaves 0.8-3.
- GM3. Halo counts above the common mass limit within 2 sqrt(N) + 2 of GD's at a = 64-132, the
  largest mass within 10 per cent (FoF in the same gauge at both meshes).
- GM4. Hr_mean at a = 141 at least 1.5 times smaller than GD's 5.98e-3 (truncation error of the
  shifted gauge); Mr_mean within 20 per cent of GD's 0.203 (particle noise, Q1). Refuted if the
  Hr ratio is below 1.2.
- Card time 3.5-5 card-h (q0007: 2332 cycles in 3.2 card-h including the cut attempts; this run
  about 2840 cycles).

## 2026-11-25 18:30 PST (lead of batch 23): equal-mass catalogues of base and gauge leg; N2, GN1 redone, predicted

Correction of the two previous headers: "18:35" and "18:50" were not read from the clock; `date`
gave 18:22-18:25 PST when they were committed (52c2460e7, e6d4d20bc). The labels stay, because
the manifests of this session and queue entry q0060 cite them.

Run B-20261126-022407-87e8803 (closed) recounted the halos of the base and of the gauge leg with
equal masses at t = 12-21. Seen in its log (disclosure): the largest halo with equal masses is
1.250, 1.492, 1.660 (zero shift) and 1.399, 1.689, 1.824 (Gamma driver) at a = 100, 121, 132,
against 1.476, 1.774, 1.912 (Gamma driver) with the file's weights in B-20261125-115558-2ab4161:
the rest-mass weight made the largest halos about 5 per cent heavier. The Newtonian largest mass
at a = 132, 1.794, was seen in batch 21. N2 and GN1 of batch 21 were judged with the weighted GR
masses, so both are redone with `compare_newton.py` on the equal-mass catalogues (the GR JSON
without dumps; N4 is not touched). Predictions [JUDGEMENT], written after seeing the largest
masses above and before the medians:
- N2e. Counts as in batch 21 (inside 2 sqrt(N) + 2 at every common catalogue a = 49-132), the
  median |M_GR/M_N - 1| of the ten largest at a = 121 below 5 per cent in both gauges.
- GN1e (GN1 as written, with the masses the Newtonian run uses): the mean over a = 81-132 of the
  median |M_GR/M_N - 1| is smaller with the Gamma driver than with zero shift. Refuted if larger.
  Batch 21's refutation of GN1 stands on record as a judgement made with biased masses.

## 2026-11-25 18:51 PST (lead of batch 23): outcomes M1, M4, P8C1-2, Q1 (constraints), S1, N2e, GN1e

Runs: histories B-20261126-024849-87e72b7 (`fig_leg_histories.py`, figure `pop_leg_histories.png`
in its run directory, looked at: K_max, Hr_mean, Mr_mean against a for six legs; cosmetic: the
legend of the left panel lies over the early curves); equal-mass comparisons with the Newtonian
mode B-20261126-024936-1ee0a16 (zero shift) and B-20261126-024941-647553b (Gamma driver), figure
`fig_gr_newton.png` looked at (its third panel is empty: N4 needs dumps, not rerun). Card time
from sacct: q0007 seven jobs 193.9 min = 3.23 card-h; q0042 13 min 25 s = 0.22; q0044 7 min 39 s
= 0.13. [VERIFIED by these runs]
- M1 REFUTED: guard stop at t = 18.2109 (a = 102.1), non-finite fields in 10.4 million values,
  2.25 million of 16.8 million particles excised in the last step; the history's largest K of
  the box turns positive at t = 15.875 (a = 79.9) and reaches 0.022 at t = 18.125, where the
  128^3 zero-shift base stays below -7e-4 after t = 9 and the 128^3 gauge leg below -1.4e-3. The
  same signature as the 0.028 stop (Z, X2): the zero-shift slice fails in the densest core once
  the mesh resolves it. M2 and M3 wait for the analysis B-20261126-022356-52c2460 (running).
- M4 NOT JUDGEABLE as written (a = 141 not reached); in its reachable part it FAILS: Hr_mean base
  over 256^3 is 1.11, 1.35, 1.36, 1.29, 1.26, 1.23 at a = 36, 49, 64, 81, 90, 100 (bound 2).
  Mr_mean base over 256^3 1.09-1.15: one particle per cell at either mesh carries the same
  momentum-constraint level.
- P8C1 HOLDS: exit 0 at t = 21.916 ("Terminating on time limit"), no guard file, 0.22 card-h
  (bound 0.4). P8C2 HOLDS: at the six common history rows t = 16.23-17.48 the continuation's
  Hr_mean, K_max and Mr_mean equal the cut run's within 4.2e-12 relative (bound 1e-6).
- Q1, constraint part, HOLDS: Mr_mean one per cell over eight per cell at a = 141 (row t = 21.727)
  is 0.2026/0.0691 = 2.93 (bound 2); 2.35, 4.71, 3.79, 3.43, 3.23 at a = 25, 49, 81, 100, 121.
  Hr_mean falls 1.55-1.67 times at every a. The high-k part waits for B-20261126-022838-27fab1b.
- S1 HOLDS: t = 21.916 without a guard file; Hr_mean 1.06e-2 at the last row (a = 140.7), largest
  2.2e-2 after t = 8 (bound 0.2). Not predicted: K_max of the box turns positive in short episodes
  (largest 6.7e-3 after t = 8.5, near a = 80 and 120 in the figure) and returns below zero; Mr_mean
  peaks at 0.25 near a = 40 and falls to 0.061 at the end.
- N2e HOLDS: counts inside 2 sqrt(N) + 2 at every common catalogue a = 49-132 in both gauges; the
  median |M_GR/M_N - 1| of the ten largest at a = 121 is 0.026 (zero shift) and 0.012 (Gamma
  driver).
- GN1e HOLDS: mean over a = 81-132 of that median, 0.057 (zero shift) against 0.038 (Gamma
  driver). The largest halo is 6.9-10.9 per cent lighter than Newton's with zero shift and 1.7-5.5
  per cent heavier with the Gamma driver at a = 72-132. Batch 21's refutation of GN1 came from the
  rest-mass weight, which made GR halo masses about 5 per cent heavier; it is withdrawn here as a
  judgement made with biased masses (on record, not erased). R23 stays: the two gauges' largest
  masses differ by 10-17 per cent with equal masses too (1.399/1.250 at a = 100, 1.689/1.492 at
  121, 1.824/1.660 at 132).
- Cores: the two comparisons ran for a few seconds each while three analyses held six cores (seven
  processes for about ten seconds).

## 2026-11-26 13:22 PST (lead of batch 28): q0060 ended; how GM1-GM4 are judged, before any analysis

q0060 (`pop_s014_gr256_gd`, run B-20261126-105021-6343c13, Slurm 5377, 5383, 5388, 5394, 5399)
ended: chain STATUS DONE (tlim), last segment "finished: time=21.916 cycle=2806", no
`pop.guard.txt` (seen while locating outputs; nothing else read). `nrpic-run finish` started
before any analysis (261 GB to hash, in the background). The three detached analyses of batch 23
(B-20261126-022356-52c2460, -022403-82f6e69, -022838-27fab1b) ended with exit 0 and are closed.

How each waiting prediction is judged (written before the analyses run; times t -> a by
a = 143 ((t + 2)/23.916)^2 of the box, so t = 14, 16, 18, 20, 21 are a = 64, 81, 100, 121, 132):
- GM1 from `pop.cstat.hst` and the chain record: K_max of the box after t = 9, guard file, end time.
- GM2 with `analyze_gr.py --equal-mass --times 4,8,12,14,16,18,20,21` on q0060 and
  `compare_legs.py --base <gauge leg B-20261125-115558-2ab4161/analysis_gr_gd.json>` (the
  metric strain carries no particle weight, so that weighted-era file is a valid base for the
  strain); the band ratio |k| <= 8 k_f at a <= 64 against 5 per cent, before a = 100 against
  0.8-1.2, to a = 132 against 20 per cent; Omega_cor (all shells) at a = 121 against 1.0-2.0
  (refuted outside 0.8-3). Fewer dumps than the 18:50 entry listed (t = 2, 6, 10 dropped): the
  bounds are read at the dumps listed only, to fit the session.
- GM3 with the halos of the same analysis at t = 14, 16, 18, 20, 21 (equal masses) against the
  equal-mass catalogue of the gauge leg in B-20261126-022407-87e8803/analysis_gr_gd.json.
- GM4 from the histories: Hr_mean, Mr_mean at the row nearest t = 21.727 (a = 141) of q0060
  against GD's B-20261124-210431-6bf48af.
- M2 and M3 (second part at a = 81-100, the 18:35 entry) from B-20261126-022356-52c2460 with
  `compare_legs.py` against the base B-20261124-131918-e71996f (strain) and the base's equal-mass
  catalogue in B-20261126-022407-87e8803 (halos).
- Q1 high-k part from B-20261126-022838-27fab1b against the base after a = 50.
- S2, S3 with `judge_s028gd.py` on B-20261126-022403-82f6e69 at a' = 2a (as-written a' = 4a
  beside).

## 2026-11-26 13:27 PST (lead of batch 28): outcomes GM1, GM4, M2, M3, Q1 (high-k part), S2, S3

Runs (all closed, figures looked at): histories B-20261126-212502-e9e4f4e (`fig_leg_histories.py`
with the 256^3 Gamma-driver leg, `pop_leg_histories.png`: the new purple curve keeps K_max below
zero throughout and lies just under the 128^3 gauge leg in both constraint panels; the legend now
sits below the panels); legs against the base B-20261126-212541-b647c59 (`compare_legs.py
--halo-base`, halos with equal masses, `pop_legs.png` looked at); the 0.028 shifted box
B-20261126-212604-a508e94 (`judge_s028gd.py`, `pop_s028gd.png` looked at; cosmetic defects: the
log-axis tick labels of panels 1-2 overlap and the y label of panel 1 is cut). Card time of
q0060: see the last item. [VERIFIED by these runs]
- GM1 HOLDS: t = 21.916 (a = 143) at cycle 2806, chain DONE (tlim), no guard file; the largest K
  of the box after t = 9 is -8.4e-4 at most, no history row positive (128^3 gauge leg: -1.4e-3).
- GM4 REFUTED in its first part: Hr_mean at a = 141 is 5.41e-3 against GD's 5.98e-3, a ratio of
  1.11 (predicted at least 1.5, refuted below 1.2); 1.17-1.36 at a = 25-100. Second part holds:
  Mr_mean 0.180 against 0.203 (0.88; within 20 per cent). With either shift the mean
  Hamiltonian constraint falls 1.1-1.4 times from 128^3 to 256^3 at one particle per cell
  (M4 with zero shift: 1.11-1.36), while eight particles per cell at 128^3 lower it 1.6 times
  and Mr_mean 2.3-4.7 times (Q1). [JUDGEMENT, not tested by a run that could fail] the late
  constraint level follows particles per cell, not the spacing; a mesh pair at fixed particle
  number per cell larger than one would test it.
- M2: counts HOLD (7/11, 10/14, 13/15, 14/22, 14/23 at a = 64, 72, 81, 90, 100 against the
  base's equal-mass catalogue, all inside 2 sqrt(N) + 2, but every one below the base); the
  largest mass FAILS at a = 64 and 72 (ratios 1.37, 1.35) and holds at 81-100 (1.078-1.087).
- M3 first part HOLDS to a = 50 (band ratio 0.993-0.999) and FAILS at a = 100 (1.214 against
  1.2; 0.987-1.082 at a = 64-90). Second part HOLDS where reachable: Omega_cor above 16 k_f
  256^3 over 128^3 is 1.9 (a = 49), 4.4, 6.6, 10.4, 13.5, 23.5 (a = 64-100), more than a factor
  2 after a = 50, growing with the mesh: the zero-shift high-k excess is mesh-dependent, as GD3
  found it gauge-dependent (950 times smaller with the shift).
- Q1 high-k part REFUTED as written in full: Omega_cor above 16 k_f, 8 per cell over one per cell
  0.978-1.007 at a = 56-132 (predicted at least two times smaller); the band strain is equal to
  2e-3. Constraint part held (18:51 entry). Particle number moves the constraints and halos, not
  the metric strain at this mesh.
- S2 HOLDS at the same stage (0.028 at a against 0.014 at a' = 2a, equal masses): counts inside
  the band at all six catalogues a = 30-64, largest mass ratio 0.98-1.09. As written (a' = 4a)
  it fails (7 halos against 31 at a = 30); that pairing is the slip recorded in the 18:35 entry.
- S3 HOLDS at the same stage: raw strain rms ratio 3.84-4.76 at a = 26-70 (bound 3-5.5),
  corrected 3.91-4.71. As written (a' = 4a): 6.8-9.7, outside.
- GM2 and GM3 wait for the analysis B-20261126-212212-c54d979 (registered, running; 5 workers).
- Card time of q0060 HOLDS: five jobs 5377-5399, sacct ElapsedRaw 13486 s = 3.75 card-h
  (predicted 3.5-5).

## 2026-11-26 14:25 PST (lead of batch 29): C3, the 64^3 member at eight particles per cell; predictions

Decision 0046 item 2(b): the mesh pair at eight particles per cell, 64^3 against the existing
128^3 member (runs B-20261124-223926-33194d9 and its continuation B-20261125-221742-5100a22, zero
shift, initial data B-20261124-135029-3fe13f6 with --ppc 2). The predictions that failed at one
particle per cell (M4, GM4) stay on record.

Step 1, initial data (processor, one core, registered now): `run_gr_ic.sh 64 8 "--nc 3.2
--sigma1 0.014 --seed 1 --ppc 2 --outer 36"`, the arguments of the 128^3 data. Expectation: the
same 146 kept modes, sigma1_realized equal to the 128^3 data's 0.012343 within 1e-3 relative (the
modes below k_c are the same draw), Hamiltonian residual below 1e-10, 2^21 particles, wall time
30-60 min (the 128^3 data took 19821 s with eight times the particles). Refuted if the modes or
sigma1 differ: then the pair is not one realization and is not run.

Step 2, the card run (shared queue, priority 2, release core-v0.8 card build; one segment of at
most one card-hour, 64^3 at 2^21 particles costs about one eighth of the 128^3 member's
0.3-0.8 card-h): `pop_gr_run.athinput` with mesh 64^3, meshblock 32^3, the step-1 files, to
a = 143 (tlim of the deck). Predictions [JUDGEMENT]:
- C3a: Hr_mean(64^3)/Hr_mean(128^3) at fixed eight per cell lies between 1.5 and 4 at every common
  history time with a = 25-141 (eight per cell lowers the sampling noise 2.8 times in amplitude
  against one per cell, so the truncation part, which falls with the spacing, carries more of
  the violation than in the one-per-cell pair 128-256, whose ratio was 1.1-1.4).
- C3b: Mr_mean ratio 64/128 at least 1.2 at a = 49-141.
- Refutation of convergence with the mesh at fixed sampling: the Hr_mean ratio below 1.2 at any
  a >= 49 (then the constraints follow the sampling and not the spacing at eight per cell too,
  and the statement of convergence of C3 fails as written).
- The run reaches a = 143 without a guard stop; K_max of the box stays below zero after t = 9
  (as the 128^3 member).
