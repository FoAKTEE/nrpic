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
