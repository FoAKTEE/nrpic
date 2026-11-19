# Design of Track B's G3 science run: the stochastic GW background of a halo population in a small box

Helper package `population` of B-emd-gw, wave 3a, 2026-11-19. Labels: [VERIFIED] read at
the source (file:line) or measured in a registered run (run id), [BACKGROUND] standard
result not re-derived here, [JUDGEMENT] my design choice or inference, [TO VERIFY] open.
Units G = c = 1; a = 1 and H = 1 at the start of the run; lengths in initial Hubble radii
c/H(a = 1); conformal time t with a = (1 + t/2)^2 and conformal Hubble rate Hc = a^(-1/2)
(`cosmo/README.md`); comoving mean density rho_c = 3/(8 pi). Numbers of the semi-analytic
design come from run B-20261119-144134-092e73f (`scripts/design.py`,
`results/design.json`, figure `figs/design_scales.png`); numbers of the Newtonian scouting
run from the runs listed in section 6.

## 1. Summary

| Item | Choice | Section |
|---|---|---|
| Spectrum | early-matter-era growing mode of a scale-invariant curvature spectrum, P_delta(k, a=1) = 2 pi^2 (4/25) A_s k (Delta^2 ~ k^4), sharp cut at k_c | 2, 3 |
| Cut and halo number | k_c = 3.2 x 2 pi/L (twenty cells per cut wavelength at 64 cells): 16.5 maxima per box expected (BBKS), 15 in the seed-1 field; nc = 4: 32; nc = 6.4 (128 cells): 132 | 4 |
| Amplitude | rms delta_N = 0.0562 at a = 1: spherical collapse of 1, 2, 3 sigma peaks at a = 30, 15, 10; first axis crossings of the 15 maxima at a = 9.6 to 29.7 (baseline model A) | 4 |
| Duration | to a = 100 (t = 18), in the run that is about 3.3 to 10 collapse times of the first halos; to a = 200 for the late signal | 4, 5 |
| Box (the physics knob) | L = 2, 4, 8 initial Hubble radii at fixed nc and amplitude: the Newtonian problem is identical up to scaling, the virial potential of a 2 sigma halo is 0.004, 0.017, 0.067 (v = 0.06, 0.13, 0.26 c); L = 16 reaches 0.27 (black-hole formation: Track A's gauge first) | 3 |
| Mesh | 256^3 for the science run (virial radius 3.4 cells; 0.85 at 64, 1.7 at 128, the same at every L); 128^3 for the scan; AMR when core/cosmo-amr is released | 3, 7 |
| Particles | one per cell (2.1M at 128^3, 16.8M at 256^3); eight per cell does not fit one card at 256^3 [JUDGEMENT, section 7] | 7 |
| Signal at L = 4 | radiated (baseline model A, first axis crossings only): rho_GW/rho_bar up to 1.7e-9 near a = 16; quasi-static second-order TT near field 1.18e-8 a (1.2e-6 at a = 100), i.e. the near field dominates the box energy by about 10^3; radiated/near-field scales as L at fixed nc and amplitude | 5 |
| Cost, full relativity | to a = 100: 0.30 card-h (128^3, L = 4), 4.8 card-h (256^3, L = 4), 2.4 (256^3, L = 8), 9.6 (256^3, L = 2); about 25 to 35 card-h for the scan of section 8 | 7, 8 |

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
the factor does not enter the runs, only the translation to A_s.

Scales and durations of interest:
- The signal of a scale-invariant spectrum is dominated by the largest, latest-forming halos;
  it scales as A_s^(7/4) (2312.12499 main.tex:221, 637, observed in its runs) and the
  emitted spectrum of one patch as sigma^(7/2) with omega_peak ~ sigma^(3/2) (2403.15126
  pII_GW_Vir_C2_Arx.tex:1031) [VERIFIED reading]. The Newtonian single-patch origin of the
  7/2 law is exact self-similarity (`../baseline/BASELINE.md` section 2, T6).
- Typical collapsing scale at reheating k_NL = 1.7 Hc_eq/A_s^(1/4) (2312.12499:645); the
  EMDE must last a_eq/a_i > 3/A_s^(1/2) (654); the box runs of 2312.12499 have
  k_nyq/k_NL = 11 to 44 and boxes of 0.88 to 3.84 tau_eq (table at 182-188); the Newtonian
  spectrum is to be read with care above the light-crossing wave number of the largest
  halos, k_cross = 14 Hc_eq/A_s^(1/4) (235, 672), and a fully relativistic simulation is
  named as what resolves it (251) [VERIFIED reading].
- arXiv:2212.00425 runs 256^3 particles from 14 to 23 e-folds (a x 8100) in a box of 1200
  l_u (main.tex:204, 213), computes S_k with the TT stress rho v_i v_j along six directions
  with a time step 500 times finer than the N-body step (285-287), finds rho_GW ~ a^3.78
  (314) and halos forming where Delta^2 crosses 0.1 (319); the spherical-collapse estimate
  falls short at high frequency, a post-collapse term with p = 1.84, xi = 0.4 fits (337)
  [VERIFIED reading].
- Patches near horizon size: sigma = 0.005 to 0.2 at horizon entry (2403.15126:276),
  monochromatic peaks (295); 2605.04487 defines sigma and nu at the reference epoch
  (main_v3.tex:1126-1136), finds the dominant contribution from nu ~ 3 (abstract, 171), and
  mean speeds 0.4 to 0.5 c at sigma = 0.1 (2395-2405, quoted in `../scope/REFERENCES.md`)
  [VERIFIED reading].

What follows for a full-GR box [JUDGEMENT]: the relativistic content of the problem is set
by the rms contrast of the collapsing band at its horizon entry, sigma_H, i.e. by how soon
after horizon entry the halos form; the literature range sigma_H = 0.005 to 0.1 is what the
box must span. In the code's units sigma_H = sigma1 a_k with a_k = 1/k_c^2.

## 3. The box and its parameters

Field: `scripts/make_ic.py` (cosmo/ic/random_field.py `gaussian_field` with the spectrum of
section 2, sharp cut at k_c = nc 2 pi/L, Nyquist planes zeroed; Newtonian particles with
`make_field.newtonian_particles`, masses scaled to rho_c L^3; relativistic data with
`make_field.build`, production deposit of `cosmo/README.md`). The noise is drawn shell by
shell, so 32, 64, 128 and 256 cells share every mode below the cut.

The Newtonian problem in comoving coordinates is invariant under x -> lambda x, p ->
lambda p, Phi -> lambda^2 Phi at fixed t (G, H fixed) [BACKGROUND; exact for the code's
scheme with a fixed step, as N3 of `../newton_tests/README.md` shows for the ellipsoid]. At
fixed nc, field and amplitude, the box size L therefore changes only the relativistic
content: velocities ~ L, potentials ~ L^2, quadrupole-formula energies E/M ~ L^7. One
Newtonian run serves every L, and the full-GR runs at several L measure the departure.

Scales against L (nc = 3.2, sigma1 = 0.0562; `results/design.json` key `scales`; R_L =
1.5/k_c the Lagrangian radius of a peak core [JUDGEMENT], virial radius R_L/(18 pi^2)^(1/3)
[BACKGROUND]):

| L | k_c | a_k (cut mode enters) | sigma_H | rms Phi (linear) | Phi_vir, v_vir/c (nu = 2, a_c = 15) | Phi_vir (nu = 3, a_c = 10) |
|---|---|---|---|---|---|---|
| 2 | 10.05 | 0.0099 | 0.0006 | 0.0019 | 0.0042, 0.06 | 0.0063 |
| 4 | 5.03 | 0.040 | 0.0022 | 0.0078 | 0.017, 0.13 | 0.025 |
| 8 | 2.51 | 0.158 | 0.0089 | 0.031 | 0.067, 0.26 | 0.10 |
| 16 | 1.26 | 0.63 | 0.036 | 0.12 | 0.27, 0.52 | 0.40 |

Reading [JUDGEMENT]: L = 2 is weak field (relativistic corrections expected at the 0.5 per
cent level, order Phi); L = 4 is moderately relativistic (2 per cent); L = 8 is the regime
of 2605.04487's sigma = 0.1 case (v up to 0.3 c), where that paper expects order-one
corrections; L = 16 puts the 3 sigma peaks at 2GM/(r c^2) ~ 0.8, i.e. black-hole formation,
which the cosmological gauge cannot pass yet (risk 5 of `../scope/SCOPE.md`: delta = 0.05
fails at a = 17.2). The G3 scan is L = 2, 4, 8; L = 16 waits for Track A's gauge and core's
horizon finder in periodic runs.

The virial radius of a cut-scale halo is 0.85, 1.7 and 3.4 cells at 64, 128 and 256 cells,
independent of L (the box and the halo scale with L together). So the 64-cell runs (this
package) do not resolve halo interiors: their GW signal at high k and the virial
compactness are set by the mesh (the force is softened at the cell, `coord/INTERFACES/
newtonian_mode.md` section 6). The science run needs 256^3, or refinement.

## 4. How many halos, and when

Expected maxima of the band-limited field (BBKS eq. 4.3 with f of A15; gamma = sqrt(32)/6,
R_* = 2/k_c; `results/design.json` key `bbks`):

| nc | cells per cut wavelength at 64 / 128 / 256 cells | maxima per box | above nu = 2 | above 3 |
|---|---|---|---|---|
| 2.0 | 32 / 64 / 128 | (not tabulated) | | |
| 3.2 | 20 / 40 / 80 | 16.5 | 9.8 | 1.9 |
| 4.0 | 16 / 32 / 64 | 32.2 | 19.2 | 3.8 |
| 6.4 | 10 / 20 / 40 | 131.7 | 78.6 | 15.4 |

The seed-1 field (64 cells) has 15 maxima with delta > 0, nu = 1.07 to 3.94; the wave-1
baseline (homogeneous ellipsoid, model A, from each maximum's deformation eigenvalues at
a = 1) puts their first axis crossings at a = 9.6 to 29.7 (`results/design.json` key
`peaks_seed1`). Press-Schechter with the sharp-k filter (mass 6 pi^2 rho_c/k^3, 2312.12499
main.tex:600) gives 26 halos of at least the cut mass at a = 30 and 30 at a = 100 (crude for
a band-limited spectrum: it puts the whole collapsed fraction below the cut mass into halos
of exactly that mass). "A handful to a few tens of halos" is met by nc = 3.2 to 4 in the
256-cell box; nc = 6.4 at 256 cells gives about 130 at 40 cells per cut wavelength.
Measured counts: section 6.

## 5. Signal estimates

(a) Radiated, from the wave-1 baseline. Each maximum radiates, from its first-axis
turnaround to its first crossing, E = [E_lib/(M_lib c^2)] M R_L^7 c^2 (the library's
horizon-sized patch scaled to a patch of Lagrangian radius R_L in units of the Hubble radius
at a = 1; E/M ~ x^7 from the Newtonian self-similarity, `../baseline/BASELINE.md` section 2)
[JUDGEMENT on the scaling; the library numbers VERIFIED in wave 1]. Over the 15 maxima,
2.6e-11 to 8.8e-9 in code units (L = 4); emitted at a_x and redshifting as radiation,
rho_GW/rho_bar = sum E a_x/(a L^3 rho_c) peaks at 1.7e-9 near a = 16 and falls as 1/a
afterwards (right panel of `figs/design_scales.png`). This is a lower bound: the baseline
stops at the first crossing, and violent relaxation adds up to ten times (2403.15126:312) or
more (2605.04487 finds the numerical spectra above the Zel'dovich ones by up to three orders
at the peak for BBKS weighting, main_v3.tex:2625).

(b) Quasi-static near field, from the measured second-order signal of the first source. In
the matter era (Phi constant, growing-mode velocities) the TT source is (20/3) [d_i Phi d_j
Phi]^TT and the sub-horizon TT field follows it, h = (20/3) [d_i Phi d_j Phi]^TT/k^2. For
two crossed waves this gives |h_+| = (5/12) phi_x phi_y (checked numerically in the design
run, key `crossed_wave_check`: equal to rounding), the second-order value the first source
measured in the code to 0.2-0.4 per cent for 2 <= a <= 10 and exceeding by up to 2.5 times
after shell crossing (`../stage/REVIEW-wave2.md`, first_source) [VERIFIED by the lead's
review]. For the seed-1 field at L = 4: h_rms = 1.6e-4 and a gradient energy
Omega_qs = 1.18e-8 a (1.2e-6 at a = 100) (`results/design.json` key `quasi_static`).

(c) Scaling with L at fixed nc and amplitude: Omega_rad ~ L^7 (Newtonian quadrupole),
Omega_qs ~ L^6 (h ~ Phi^2 ~ L^4, k ~ 1/L); radiated/near field ~ L [JUDGEMENT, arithmetic].
At L = 8 the radiated estimate is 128 times larger (2e-7 at a = 16), the near field 64
times (8e-7 a).

(d) Junk radiation. The relativistic initial data are conformally flat (cosmo_id.py), so
the TT field starts at zero instead of at h_qs (risk 2 of `../scope/SCOPE.md`). The
difference propagates as free waves with the energy of the near field at the start,
redshifting as 1/a: Omega_junk ~ 1.2e-8/a at L = 4 [JUDGEMENT], about 7e-10 at a = 16,
comparable to the radiated estimate (a). The science run must either start from initial
data with the second-order TT part (request below) or subtract the computed junk (the first
source did, with its g(tau)). The Newtonian analysis of this package removes it by
construction (section 6, "radiated" measure).

## 6. Newtonian-mode scouting run (64 cells, processors)

Runs (release core-v0.3 processor build, `inputs/pop_newton.athinput`, cubic cloud with
compensation, cubic-spline force, step 1/32 with `newton_cfl = 0.25`, solver tolerance
1e-6): see `README.md` (run ids) and `JOURNAL.md` (predictions P1-P9 and outcomes).

RESULTS: to be filled from the analysis runs (section kept as the place of the numbers).

## 7. Cost of the full-relativity run on this machine

Steps: dt = min(0.25 dx, 0.01 sqrt(a)) in conformal time (Courant 0.25 of the deck,
`dt_expansion = 0.01` of the production configuration), a = (1 + t/2)^2. Throughput (one
A100, one particle per cell): 5.77e6 zone-cycles/s at 64^3 and 4.47e6 at 128^3 (logs quoted
in `../scope/SCOPE.md` section 9; 5.6e6 to 5.7e6 for the production configuration at
128^3); 256^3 assumed at the 128^3 rate [JUDGEMENT; not measured: the card timing runs of
section 9 are pending]. Memory linear in the cells between 1.65 GiB (64^3) and 4.96 GiB
(128^3) (`results/design.json` key `gr_cost`):

| cells | L | steps to a = 100 | card-h to a = 100 | to a = 200 | memory |
|---|---|---|---|---|---|
| 128^3 | 2 | 4608 | 0.60 | 0.88 | 5.0 GiB |
| 128^3 | 4 | 2304 | 0.30 | 0.44 | 5.0 GiB |
| 128^3 | 8 | 1170 | 0.15 | 0.22 | 5.0 GiB |
| 256^3 | 2 | 9216 | 9.6 | 14.0 | 31.5 GiB |
| 256^3 | 4 | 4608 | 4.8 | 7.0 | 31.5 GiB |
| 256^3 | 8 | 2304 | 2.4 | 3.5 | 31.5 GiB |

Add for each run: restart dumps of the particles (about 180 bytes per particle, from 380 MB
per dump at 2.1M particles in `../first_source/README.md` line 123: 3 GB per dump at 256^3);
a 256^3 run is a chain of 5 to 10 one-hour segments (`scripts/submit_chain.sh`, restarts
exact). Output for the GW analysis: a double-precision Z4c dump of 20 variables is 2.7 GB at
256^3 [JUDGEMENT, arithmetic]; 100 dumps would be 270 GB, so the science run needs in-situ
output of the low-k Fourier modes of gamma_ij and K_ij (request below) or sparse dumps.
Eight particles per cell at 256^3 (134M particles) adds about 24 GB of particle storage at
180 bytes each [JUDGEMENT; the in-memory size per particle is not measured] and would not
leave room for the Z4c state on one 80 GB card: one per cell, or several cards (core/mpi).
The Newtonian reference of the same particles costs little on a card (core measured 0.65 s
per step at 128^3 with 1.4e5 particles, `coord/INTERFACES/newtonian_mode.md` 5.8); on the
serial processor build it took about 6 s per step at 64^3 here (section 6), so its 128^3 and
256^3 versions go to the cards.

## 8. Proposed G3 run list (draft for the pre-registration)

[JUDGEMENT] Three box sizes, the three legs of the gate, two seeds:

| Set | Runs | Cells | Card-h (to a = 100) |
|---|---|---|---|
| L scan, full GR | L = 2, 4, 8, seed 1 | 256^3 | 9.6 + 4.8 + 2.4 = 16.8 |
| Newtonian reference | one run (scales to every L), seed 1 | 256^3 | about 1 [JUDGEMENT] |
| Mesh leg | L = 4, seed 1 | 128^3 (and the 256^3 above) | 0.3 |
| Particle leg | L = 4, 8 per cell | 128^3 | about 0.6 [JUDGEMENT: twice the 1-per-cell cost] |
| Gauge leg | L = 4, Gamma-driver shift (passed in an expanding box, `../first_source/README.md` request 4) | 128^3 | 0.3 |
| Seed | L = 4, seed 2 | 256^3 | 4.8 |
| Total | | | about 24, inside the 40 GPU-hours of the track |

## 9. What the code still lacks for the science run

1. Resolution of halo interiors: uniform 256^3 gives 3.4 cells per virial radius; refinement
   in periodic cosmology runs is core/cosmo-amr (wave 3a, `coord/digests/wave-3a-plan.md`
   on main), not released.
2. GW output: double-precision mesh dumps exist on core/requests-b (scouting executable,
   not on main); in-situ Fourier output of gamma_ij and K_ij at |k| <= k_max is not
   implemented (request of risk 7 of `../scope/SCOPE.md`, repeated below); without it a
   256^3 run cannot keep the cadence the radiated measure needs (dynamical frequency of
   the halos about 2.4/sqrt(a/15) in conformal time, `results/design.json`).
3. Initial data with the second-order TT field (or a computed junk to subtract): section
   5(d). Not in cosmo_id.py; core/id-solver solves the constraints on the mesh but starts
   from a given conformal metric.
4. The covariant (York) TT part and rho_K on the code's slicing: not implemented (gw_diag
   has the flat Fourier TT and Psi_4; `../stage/REVIEW-wave2.md` "large items left open").
5. Gauge and horizons for L >= 8: the virial potentials reach 0.07 to 0.1; for L = 16 black
   holes form. A slicing that passes collapse in the periodic box, a horizon finder and
   excision in periodic runs (core/cosmo-amr; Track A's requests). Until then the scan
   stops at L = 8 and runs end at the first non-finite field.
6. Several cards (core/mpi, wave 3a) for 8 particles per cell at 256^3 or for 512^3.
7. A threaded processor build (core/build-openmp, wave 3a) for the Newtonian references on
   processors; the serial build took about 6 s per step at 64^3 with 2.6e5 particles on the
   loaded machine.
8. Not needed from core: a halo finder (friends-of-friends on the snapshots, here) and the
   per-species history of the Newtonian mode (N2 of `../newton_tests/`) for this problem.

## 10. Not done here

- The full-GR card timing at 128^3 and 256^3 with this problem (pending: the owner had two
  card jobs queued, the limit of `CLAUDE.md`); the 256^3 rate and memory are extrapolated.
- The relativistic initial data were built only at 16 cells (smoke test); 64 and 128 cells
  at L = 4, 8, 16 are pending (processors were at the owner's allotment).
- The factor 3 between the delta-R relations (section 2).
