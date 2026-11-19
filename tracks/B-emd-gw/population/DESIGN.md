# Design of Track B's G3 science run: the stochastic GW background of a halo population in a small box

Helper package `population` of B-emd-gw, wave 3a, 2026-11-19. Labels: [VERIFIED] read at
the source (file:line) or measured in a registered run (run id), [BACKGROUND] standard
result not re-derived here, [JUDGEMENT] my design choice or inference, [TO VERIFY] open.
Units G = c = 1; a = 1 and H = 1 at the start of the run; lengths in initial Hubble radii
c/H(a = 1); conformal time t with a = (1 + t/2)^2 and conformal Hubble rate Hc = a^(-1/2)
(`cosmo/README.md`); comoving mean density rho_c = 3/(8 pi). Semi-analytic numbers: run
B-20261119-144134-092e73f (`scripts/design.py`, `results/design.json`,
`figs/design_scales.png`). Newtonian-mode numbers: the runs of section 6. Predictions and
outcomes: `JOURNAL.md` (P1-P10, I1).

## 1. Summary

| Item | Recommendation | Section |
|---|---|---|
| Spectrum | early-matter-era growing mode of a scale-invariant curvature spectrum, P_delta(k, a = 1) = 2 pi^2 (4/25) A_s k (Delta^2 ~ k^4), sharp cut at k_c = nc 2 pi/L | 2, 3 |
| Cut | nc = 3.2 (twenty cells per cut wavelength at 64 cells): 16.5 maxima per box expected, 15 in the seed-1 field; measured 25 halos at a = 30 and 21 at a = 100 in the 64-cell Newtonian run | 4, 6 |
| Box | L = 8 initial Hubble radii: the halo emission wave number 9.4/sqrt(a) stays above the box fundamental 2 pi/L until a = 143 (L = 4: a = 36; L = 2: a = 9) | 3, 6 |
| Relativistic knob | the amplitude at fixed L: rms delta_N at a = 1 sigma1 = 0.014, 0.028, 0.056 gives a virial potential of 2 sigma halos of 0.017, 0.033, 0.067 (v = 0.13, 0.18, 0.26 c); the Newtonian problem depends on sigma1 a only (P4 measured), so one Newtonian reference serves all three, and the sigma^(7/2) law it obeys (P9 measured) is the baseline the full-GR runs depart from | 3, 6 |
| Mesh, particles | 256^3, one particle per cell (16.8M): virial radius of cut-scale halos 3.4 cells (0.85 at 64, 1.7 at 128); refinement when core/cosmo-amr is released | 3, 7 |
| Duration | to a = 143 (t = 21.9) | 3 |
| Expected signal (Newtonian box, L = 8, sigma1 = 0.056) | radiated rho_GW/rho_bar 1.2e-6 at a = 15, 2.7e-6 at a = 30, 2.9e-5 at a = 100; quasi-static near field 2.3e-5 at a = 30 to 100 | 5, 6 |
| Cost, full relativity | 2.9 card-h per 256^3 run to a = 143 at L = 8 (extrapolated rate); about 15 card-h for the run list of section 8 | 7, 8 |
| Blocking gaps | in-situ Fourier output of the metric; initial data at the top amplitude (the outer loop of the constraint solve did not converge at L = 8, sigma1 = 0.056, and failed with NaN at L = 16); the covariant TT part; halo refinement | 9 |

## 2. What the references give (read at the source)

Spectrum in an early matter era. For modes entering during the matter era, Phi = (3/5) R
(arXiv:2312.12499 main.tex:324) and the density contrast grows as a; in the code's units the
Poisson relation of the initial-data tool is k^2 psi_N = (3/2) delta_N at a = 1
(`cosmo/ic/make_field.py:9`), so delta_N(k, a) = (2/5)(k/Hc)^2 R_k = (2/5) k^2 a R_k and
Delta^2_delta = (4/25) A_s k^4 a^2 for a scale-invariant P_R = A_s [VERIFIED as arithmetic
from the two locators]. arXiv:2312.12499 writes delta = (6/5)(a/a_hor) R (main.tex:581), a
factor 3 larger for the same horizon-entry convention; with its normalization the A_s of a
given field is 9 times smaller (`meta.json` key `A_s_2312_normalization`) [TO VERIFY: which
convention for a_hor makes 6/5 right]. The field is normalized here by its rms at a = 1, so
the factor does not enter the runs, only the translation to A_s (A_s = 1.13e-4 for the
fiducial field at L = 4, 1.8e-3 at L = 8 with the same sigma1; design.json `scales`).

Scales and durations of interest:
- The signal of a scale-invariant spectrum is dominated by the largest, latest-forming halos;
  it scales as A_s^(7/4) (2312.12499 main.tex:221, 637, observed in its runs) and the
  emitted spectrum of one patch as sigma^(7/2) with omega_peak ~ sigma^(3/2) (2403.15126
  pII_GW_Vir_C2_Arx.tex:1031) [VERIFIED reading]. The Newtonian single-patch origin of the
  7/2 law is exact self-similarity (`../baseline/BASELINE.md` section 2, T6); the box runs
  here show it for the whole population including the post-collapse emission (P9).
- Typical collapsing scale at reheating k_NL = 1.7 Hc_eq/A_s^(1/4) (2312.12499:645); the
  EMDE must last a_eq/a_i > 3/A_s^(1/2) (654); its box runs have k_nyq/k_NL = 11 to 44 and
  boxes of 0.88 to 3.84 tau_eq (table at 182-188); the Newtonian spectrum is to be read
  with care above the light-crossing wave number of the largest halos, k_cross =
  14 Hc_eq/A_s^(1/4) (235, 672), and a fully relativistic simulation is named as what
  resolves it (251) [VERIFIED reading].
- arXiv:2212.00425 runs 256^3 particles from 14 to 23 e-folds (a x 8100) in a box of 1200
  l_u (main.tex:204, 213), computes S_k with the TT stress rho v_i v_j along six directions
  with a time step 500 times finer than the N-body step (285-287), finds rho_GW ~ a^3.78
  (314) and halos forming where Delta^2 crosses 0.1 (319); the spherical-collapse estimate
  falls short at high frequency, a post-collapse term with p = 1.84, xi = 0.4 fits (337)
  [VERIFIED reading].
- Patches near horizon size: sigma = 0.005 to 0.2 at horizon entry (2403.15126:276),
  monochromatic peaks (295); 2605.04487 defines sigma and nu at the reference epoch
  (main_v3.tex:1126-1136), finds the dominant contribution from nu ~ 3 (abstract, 171),
  numerical spectra above the Zel'dovich ones by up to three orders at the peak for the
  BBKS weighting (2625), and mean speeds 0.4 to 0.5 c at sigma = 0.1 (2395-2405), all as
  quoted in `../scope/REFERENCES.md` [VERIFIED reading].

What follows for a full-GR box [JUDGEMENT]: the relativistic content is set by the rms
contrast of the collapsing band at its horizon entry, sigma_H = sigma1 a_k (a_k = 1/k_c^2),
equivalently by the virial potential of the halos; the literature range sigma_H = 0.005 to
0.1 is what the box should span.

## 3. The box and its parameters

Field: `scripts/make_ic.py` (cosmo/ic/random_field.py `gaussian_field` with the spectrum of
section 2, sharp cut at k_c, Nyquist planes zeroed; Newtonian particles with
`make_field.newtonian_particles`, masses scaled to rho_c L^3; relativistic data with
`make_field.build`, production deposit of `cosmo/README.md`). The noise is drawn shell by
shell, so 32, 64, 128 and 256 cells share every mode below the cut.

Two exact properties of the Newtonian problem [BACKGROUND; both measured here]:
1. Box scaling: x -> lambda x, p -> lambda p, m -> lambda^3 m at fixed t (G, H fixed)
   leaves it invariant (Phi -> lambda^2 Phi). The analyses at lambda = 2 and 1/2
   (B-20261119-155808-0942d44, -155838-4f1954f) reproduce the per-halo quadrupole sum times
   2^7 and the near field times 2^6 to the printed digits (P10a).
2. Amplitude scaling: with growing-mode initial data in the matter era the evolution
   depends on sigma1 a only; doubling sigma1 reproduces the halo counts at half the scale
   factor within the count noise and the largest mass and collapsed fraction to 1 to 4 per
   cent (P4, B-20261119-155621-68170ca).

Scales (design.json `scales`, nc = 3.2, sigma1 = 0.0562; R_L = 1.5/k_c the Lagrangian
radius of a peak core [JUDGEMENT]; virial radius R_L/(18 pi^2)^(1/3) [BACKGROUND]; Phi_vir
and v scale as sigma1 L^2 and its square root):

| L | k_c | a_k | sigma_H | rms Phi (linear) | Phi_vir, v_vir/c (nu = 2, a_c = 15) | Phi_vir (nu = 3, a_c = 10) |
|---|---|---|---|---|---|---|
| 2 | 10.05 | 0.0099 | 0.0006 | 0.0019 | 0.0042, 0.06 | 0.0063 |
| 4 | 5.03 | 0.040 | 0.0022 | 0.0078 | 0.017, 0.13 | 0.025 |
| 8 | 2.51 | 0.158 | 0.0089 | 0.031 | 0.067, 0.26 | 0.10 |
| 16 | 1.26 | 0.63 | 0.036 | 0.12 | 0.27, 0.52 | 0.40 |

Measured in the 64-cell Newtonian run at L = 4 (A-fid B-20261119-154315-c55b30f):
G M/r_half (physical) of the halos 0.003 to 0.12, median 0.010 at a = 30 and 0.025 at
a = 100; velocity dispersion 0.06 to 0.25, median 0.11. These are set partly by the mesh
(r_half 0.025 to 0.09 comoving, 0.4 to 1.5 cells): at 256 cells the halos will be more
compact and their potentials deeper.

Constraints on L [JUDGEMENT, with the measurements of section 6]:
- Radiation must land on box modes. Halos have the density 18 pi^2 rho_bar at any epoch, so
  their dynamical wave number in conformal time is sqrt(9 pi^2) Hc = 9.4/sqrt(a)
  (design.json `k_dyn`), independent of their mass; the box fundamental 2 pi/L lies below
  it only for a <= (1.5 L)^2: 9, 36, 143 for L = 2, 4, 8.
- Relativity: Phi_vir ~ sigma1 L^2/nc^2; at L = 16 the 3 sigma peaks reach
  2GM/(r c^2) ~ 0.8 (black-hole formation, the end that the cosmological gauge cannot pass
  yet, risk 5 of `../scope/SCOPE.md`), and the initial-data tool fails there (section 9).
- Resolution: the virial radius in cells is 0.043 N/nc, independent of L and sigma1.
Hence L = 8 with the amplitude as the relativistic knob, rather than a scan in L: at fixed L
the box holds the halo frequencies over the whole run for every amplitude, the mesh
resolves the halos equally, and the Newtonian reference is one run rescaled. The box
modes below Hc at the start (k_f = 0.785 < 1 at L = 8) carry about 1 per cent of the
variance; they are evolved correctly only in GR (2312.12499 main.tex:349-359 on
back-scaling) [JUDGEMENT: a small, known part of the GR-Newton difference].

## 4. How many halos, and when

Expected maxima of the band-limited field (BBKS eq. 4.3 with f of A15; gamma = sqrt(32)/6,
R_* = 2/k_c; design.json `bbks`): nc = 3.2: 16.5 per box (9.8 above nu = 2, 1.9 above 3);
nc = 4: 32.2; nc = 6.4: 131.7. The seed-1 field (64 cells) has 15 maxima with delta > 0,
nu = 1.07 to 3.94; the baseline model A puts their first axis crossings at a = 9.6 to 29.7
(design.json `peaks_seed1`). Press-Schechter (sharp-k filter, mass 6 pi^2 rho_c/k^3,
2312.12499 main.tex:600): 26 at a = 30, 30 at a = 100 (crude for a band-limited spectrum).

Measured (friends-of-friends, b = 0.2, >= 100 particles; section 6): first halo at a = 9.0;
25 halos at a = 30 in seeds 1 and 2; 18 to 28 between a = 25 and 100 (formation and merging
balance); 21 at a = 100 holding 49 per cent of the mass, the largest 6.2 per cent; nc = 4:
35 at a = 30. For sigma1 = 0.014, 0.028, 0.056 at L = 8 the same counts occur at 4, 2, 1
times these scale factors (P4): first halos at a = 36, 18, 9; 25 halos at a = 120, 60, 30.
So all three amplitudes form 20 or more halos before a = 143.

## 5. Signal estimates

(a) Wave-1 baseline (homogeneous ellipsoid, model A, first-axis turnaround to first
crossing) per maximum of the seed-1 field: E = [E_lib/(M_lib c^2)] M R_L^7 c^2 (the
library's horizon-sized patch scaled to a patch of Lagrangian radius R_L in units of the
Hubble radius at a = 1; E/M ~ x^7 by the Newtonian scaling [JUDGEMENT; the library numbers
VERIFIED in wave 1]): 2.6e-11 to 8.8e-9 (L = 4); the box sum rho_GW/rho_bar = sum E a_x/(a
L^3 rho_c) peaks at 1.7e-9 near a = 16 and decays as 1/a.

(b) Quasi-static near field from the measured second-order signal of the first source: in
the matter era the TT source is (20/3)[d_i Phi d_j Phi]^TT and the sub-horizon TT field
follows it, h = (20/3)[d_i Phi d_j Phi]^TT/k^2; for two crossed waves this gives (5/12)
phi_x phi_y (design run, key `crossed_wave_check`, equal to rounding), the value the first
source measured in the code to 0.2-0.4 per cent for 2 <= a <= 10 (`../stage/REVIEW-wave2.md`)
[VERIFIED by the lead's review]. Seed-1 field at L = 4: Omega_qs = 1.18e-8 a in linear
theory (design.json `quasi_static`); measured from the particles 1.17e-8 at a = 1, twice
the linear value at a = 20 (4.95e-7), then 3.6e-7 to 3.8e-7 up to a = 100 (a third of the
linear extrapolation) (A-fid).

(c) The radiated part measured in the Newtonian box (section 6): at L = 4 it exceeds the
baseline sum by 2 to 12 times up to a = 30 and by 200 to 800 times at a = 50 to 100 (the
emission after collapse dominates, as 2605.04487 and 2212.00425 found); per halo during
formation the quadrupole formula gives 3 to 2760 times the baseline energy of the matched
maximum (median about 300).

(d) Junk radiation of the conformally flat relativistic data (risk 2 of
`../scope/SCOPE.md`): free waves with the energy of the near field at the start,
Omega_junk ~ Omega_qs(a = 1)/a [JUDGEMENT]: 1.2e-8/a at L = 4, 7.5e-7/a at L = 8 and
sigma1 = 0.056. Against the measured radiated part this is 30 times below at L = 4, a = 30
and 100 times below at L = 8, a = 30: the junk matters before the first halos (a < 10),
not after. Subtracting it (the first source did, with its g(tau)) or second-order TT
initial data remove it.

## 6. Newtonian-mode scouting run (64 cells, processors)

Runs (release core-v0.3 processor build, `inputs/pop_newton.athinput`: cubic cloud with
compensation 1/6, 7/15, cubic-spline force, step 1/32 with `newton_cfl = 0.25`, solver
tolerance 1e-6; L = 4, nc = 3.2, sigma1 = 0.0562 unless said; one particle per cell,
262,144 particles; about 6 s per step on one core of the loaded machine):

| Run | Case | Analysis |
|---|---|---|
| B-20261119-143828-0ef9b5b | fiducial, seed 1, to a = 100 (577 steps, 3396 s) | A-fid B-20261119-154315-c55b30f (GW at 64^3), box-scaled A-fid-L8 B-20261119-155808-0942d44, A-fid-L2 B-20261119-155838-4f1954f |
| B-20261119-143832-85cbe25 | seed 2 | A-fid |
| B-20261119-145324-525e4fd | 32 cells, same modes | A-n32 B-20261119-153509-02a921f, A-fid |
| B-20261119-145328-4b3663f | sigma1 doubled, stopped at a = 57 | A-amp2 B-20261119-154447-99fa502 |
| B-20261119-145715-b18561e | nc = 4 | A-nc4 B-20261119-155537-d49f8f1 |
| B-20261119-155621-68170ca | comparison of P3-P7, P9 | `results/compare.json`, `figs/pop_compare.png` |

Halos (`figs/pop_halos_fid.png`, `figs/pop_density_fid.png`): numbers in section 4. The
32-cell run (same modes) finds every 64-cell halo above its 100-particle limit
(M >= 0.023) within one 32-cell spacing, masses within -24 to +12 per cent (P5). The
Layzer-Irvine constant holds to 4.7e-4 to 8.4e-4 of max a|W| in all runs (P7).

GW of the box (`figs/pop_gw_fid.png`; method: `scripts/analyze.py` docstring, the
linearized Einstein equation with the Newtonian stress 16 pi rho_c v_i v_j/a +
4 d_i Phi_N d_j Phi_N, time integrals exact for a source linear between snapshots, the
start term (junk) and the end term (near field) removed to second order):

| a | radiated, L = 2 | radiated, L = 4 | radiated, L = 8 | near field, L = 4 (x 64 for L = 8, / 64 for L = 2) | baseline (a), L = 4 |
|---|---|---|---|---|---|
| 10 | 9.5e-13 | 4.7e-10 | 2.4e-7 | 2.1e-7 | 2.2e-10 |
| 15 | 1.8e-11 | 5.1e-9 | 1.2e-6 | 4.3e-7 | 5.1e-10 |
| 20 | 2.7e-11 | 7.3e-9 | 2.0e-6 | 5.0e-7 | 1.5e-9 |
| 30 | 7.2e-11 | 1.2e-8 | 2.7e-6 | 3.6e-7 | 9.9e-10 |
| 50 | 6.6e-10 | 1.2e-7 | 1.7e-5 | 3.8e-7 | 5.9e-10 |
| 100 | 1.4e-9 | 2.3e-7 | 2.9e-5 | 3.7e-7 | 3.0e-10 |

- The radiated part rises steeply from a = 8 (first halos) and grows through a = 70: the
  post-collapse stage dominates the box signal.
- sigma^(7/2) holds at equal stage: doubling sigma1 raises the radiated part 8.0 to 18.7
  times (2^(7/2) = 11.3) and the near field 6.1 to 11.1 times (8 expected) (P9).
- Box size at fixed field: the radiated part grows by 200 to 270 between L = 4 and 8 for
  a = 15 to 40 and by 113 to 137 at a = 50 to 100 (2^7 = 128 is the quadrupole-formula
  scaling); between L = 2 and 4 by 165 to 290 for a >= 15. So a box too small for the halo
  frequencies loses up to about half of the radiated signal before a = 40; later the loss is
  small (P10b refuted at a = 70 and 100: the argument of section 3 accounts for part of the
  difference only).
- The per-halo quadrupole formula of the ten largest halos of a = 20 (followed to a = 30)
  sums to Omega = 2.3e-7 at L = 4, 19 times the box measure at a = 30; at L = 8 11 times.
  The isolated-source formula and the box measure differ in what they count (a periodic box
  of interacting halos, the near zone, the lowest frequencies) [JUDGEMENT]; the GR run is
  compared with the box measure computed from its own particles, not with the formula.

## 7. Cost of the full-relativity run on this machine

Steps: dt = min(0.25 dx, 0.01 sqrt(a)) in conformal time (Courant 0.25 of the deck,
`dt_expansion = 0.01` of the production configuration). Throughput (one A100, one particle
per cell): 5.77e6 zone-cycles/s at 64^3, 4.47e6 at 128^3 (logs quoted in
`../scope/SCOPE.md` section 9; 5.6e6 to 5.7e6 for the production configuration at 128^3);
256^3 assumed at the 128^3 rate [JUDGEMENT; not measured, the card timing is pending,
section 10]. Memory linear in the cells between 1.65 and 4.96 GiB (design.json `gr_cost`):

| cells | L | steps to a = 100 | card-h to a = 100 | to a = 143 | to a = 200 | memory |
|---|---|---|---|---|---|---|
| 128^3 | 4 | 2304 | 0.30 | (0.36) | 0.44 | 5.0 GiB |
| 128^3 | 8 | 1170 | 0.15 | (0.18) | 0.22 | 5.0 GiB |
| 256^3 | 4 | 4608 | 4.8 | (5.8) | 7.0 | 31.5 GiB |
| 256^3 | 8 | 2304 | 2.4 | (2.9) | 3.5 | 31.5 GiB |

(The a = 143 column is the same model, 2(sqrt(a) - 1)/(0.25 dx) light-limited steps,
evaluated by hand [JUDGEMENT, arithmetic].) Add: particle restart dumps of about 180 bytes
per particle (380 MB per dump at 2.1M particles, `../first_source/README.md` line 123):
3 GB per dump at 256^3; a 256^3 run is a chain of three to four one-hour segments
(`scripts/submit_chain.sh`, restarts exact). A double-precision Z4c dump of 20 variables is
2.7 GB at 256^3 [JUDGEMENT, arithmetic]; the GW analysis needs the metric at a cadence
finer than the halo dynamical time (0.1 sqrt(a) in conformal time: about 100 samples to
a = 143), 270 GB in full dumps, so the science run needs the in-situ Fourier output of
section 9. Eight particles per cell at 256^3 (134M particles) adds about 24 GB at 180 bytes
each [JUDGEMENT; in-memory size per particle not measured] and does not fit next to the Z4c
state on one 80 GB card: one per cell, or several cards (core/mpi). The Newtonian reference
of the same particles goes to a card (core measured 0.65 s per step at 128^3 with 1.4e5
particles, `coord/INTERFACES/newtonian_mode.md` 5.8); the serial processor build took 6 s
per step at 64^3 with 2.6e5 particles here.

## 8. Proposed G3 run list (draft for the pre-registration)

[JUDGEMENT] L = 8, nc = 3.2, to a = 143, one particle per cell, the legs of the gate at
128^3:

| Set | Runs | Cells | Card-h |
|---|---|---|---|
| Amplitude scan, full GR | sigma1 = 0.014, 0.028, 0.056, seed 1 | 256^3 | 3 x 2.9 = 8.8 |
| Newtonian reference | sigma1 = 0.056, seed 1 (the others by the sigma1 a scaling, P4) | 256^3 | about 1 |
| Scouting of the scan | the three amplitudes | 128^3 | 0.55 |
| Particle leg | sigma1 = 0.028, eight per cell | 128^3 | about 0.4 [JUDGEMENT: twice the 1-per-cell cost] |
| Gauge leg | sigma1 = 0.028, Gamma-driver shift (passed in an expanding box, `../first_source/README.md` request 4) | 128^3 | 0.18 |
| Seed | sigma1 = 0.028, seed 2 | 256^3 | 2.9 |
| Total | | | about 14, inside the 40 GPU-hours of the track |

Quantities: the TT strain and K^TT at the box modes from the in-situ output; the same
radiated / near-field split as `scripts/analyze.py`, with the GR stress of the particles;
the departure of the radiated energy from sigma1^(7/2) and from the Newtonian reference at
equal stage, per amplitude, against the convergence error of the legs.

## 9. What the code still lacks for the science run

1. Initial data at the top amplitude. `make_field.build` (cosmo/ic) at 64 cells, seed 1
   (run I-gr B-20261119-154528-9306cb1): L = 4 converged (outer change 5.5e-10, Hamiltonian
   residual 5e-11, momentum 4e-6, max|psi_N| = 0.022); L = 8 did NOT reach the stopping
   tolerance within its 18 outer iterations (last change 1.8e-6, contraction 0.81 per
   iteration, Hamiltonian residual 1.1e-11, momentum 5e-5, max|psi_N| = 0.088); L = 16
   gave NaN in the first outer iteration. So sigma1 = 0.056 at L = 8 needs more outer
   iterations (about 36 more at that contraction [JUDGEMENT]) and L = 16 needs a
   nonlinear initial-data method (core/id-solver, in-code elliptic solve; core/id-solver-2
   in wave 3a).
2. GW output: double-precision mesh dumps exist on core/requests-b (scouting executable,
   not on main); in-situ output of the low-k Fourier modes of gamma_ij and K_ij is not
   implemented (risk 7 of `../scope/SCOPE.md`; request in `README.md`).
3. The covariant (York) TT part and rho_K on the code's slicing: not implemented (gw_diag
   has the flat Fourier TT and Psi_4; `../stage/REVIEW-wave2.md`, large items left open).
   The near field dominates the TT energy until a ~ 100 at L = 8 (section 6), so the
   split into radiated and quasi-static parts must be done on the GR data too.
4. Initial data with the second-order TT field, or the junk subtracted (section 5(d)):
   needed only for a < 10.
5. Resolution of halo interiors: 3.4 cells per virial radius at 256^3 uniform; refinement
   in periodic runs is core/cosmo-amr (wave 3a, `coord/digests/wave-3a-plan.md` on main),
   not released.
6. Gauge and horizons: virial potentials reach 0.07 to 0.1 at the top amplitude; above it
   (or at L = 16) black holes form: a slicing that passes collapse in the periodic box, a
   horizon finder and excision in periodic runs (core/cosmo-amr; Track A's requests).
7. Several cards (core/mpi, wave 3a) for eight particles per cell at 256^3 or for 512^3.
8. A threaded processor build (core/build-openmp, wave 3a) for Newtonian references on
   processors.
9. Not needed from core: a halo finder (friends-of-friends on snapshots, here) and the
   per-species history of the Newtonian mode for this problem.

## 10. Not done here, open

- Card timing of the full-GR box at 128^3 and 256^3 (one batch job, about 0.3 card-h): not
  submitted, the owner had two card jobs queued (the limit of `CLAUDE.md`); the 256^3 rate
  and memory are extrapolated.
- The full-GR scouting run of this box: not run (no card slot; at 64^3 on the serial
  processor build it would take about 1170 steps x 7.5 s x 8 = 20 h, from the 7.5 s per
  cycle at 32^3 in `../first_source/README.md` request 6 [JUDGEMENT]).
- Relativistic initial data at L = 8, sigma1 = 0.028 and 0.014 (expected to converge, as
  their potentials are those of L = 5.7 and L = 4 at sigma1 = 0.056 [JUDGEMENT, not run]).
- The factor 3 between the delta-R relations (section 2).
- The Newtonian runs at 128 and 256 cells (halo compactness and the high-k signal are set
  by the 64-cell mesh here).
