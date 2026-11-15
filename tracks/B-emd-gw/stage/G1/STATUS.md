# G1 status of B-emd-gw (pre-core baseline)

State 2026-11-15, end of wave 2 (lead). Verdict of the lead: **G1 not met**. Of the three
criteria of the track sheet (`coord/CHARTER.md` 9.5) as ruled by decision 0013, one is met
(2), one is struck (3), one is met only in part (1); the G1 schematics, the note's G1
sections and an independent verifier of the wave-2 runs are owed (`CHECKLIST.md`,
`OPEN.md`). Run ids are under `tracks/B-emd-gw/runs/`. Corrections of the wave-1 version of
this file (found by the note helper, `note/tables/claims.md`) are marked "corrected".

## Criterion 1. "The two diagnostics agree on analytic linear waves": met for waves along an axis in a flat box; oblique and expanding cases open

- Analytic fields: 48 random TT waves recovered to 2.6e-12; Psi_4 = hddot_+ - i hddot_x
  (runs B-emd-gw-20261115-115206-2e6c497, -115637-175cbca); independently by the verifier
  on its own plane waves in four directions and three polarizations: TT read-back to 1e-10 A,
  Psi_4 to 8.7e-7 (run B-20261115-170546-4507b05).
- AthenaK output (z4c_linear_wave along x): TT amplitude within 3e-7, phase 1.2e-6 rad,
  energy 6e-7 at 32^3 (runs -113218-0ea0f74, -120128-7dfaa38); the verifier: TT projection
  and Psi_4 agree mutually to 1.8e-7 A at 64^3, t = 10. The wave errors follow the Fourier
  symbol of the scheme to 1 percent except the production phase error at 64 cells, which
  departs by 9.5 percent (corrected; `periodic_z4c/tables/lw_x.md`).
- Oblique wave: the upstream generator gives non-TT data off the axes (track, wave 1;
  verifier C6, run B-20261115-165056-835fddf). Core flipped the two signs on branch
  `core/requests-b` (not on main) and ran k = (1, 1, 1) on a card with gw_diag's Psi_4
  (errors 9.2e-5, 3.2e-6, 3.3e-7, 8.1e-7 at N = 16-128; core message 20261115T1850Z,
  `tracks/core/interfaces/REQUESTS_B.md` on that branch). That is core's evidence; the
  track's own oblique run with both diagnostics is owed.
- Expanding box: the 1/a reference is ready (scope run -113632-2960145; verifier C3, run
  B-20261115-165123-9cb1745); no run yet. The crossed-wave scan (below) shows the junk
  oscillation of the box mode decaying as predicted in a particle-filled box, which is a
  related but not the same test (strain only, not both diagnostics on a free wave).

## Criterion 2. "The Newtonian baseline reproduces the scaling of the literature": met (lead's judgement)

- Semi-analytic (wave 1, run -115752-840e994): the Zel'dovich spectrum of 2403.15126 and
  2605.04487, slopes 3.5 (energy, peak) and 1.5 (peak frequency) for delta_L <= 1e-2;
  rechecked at emission by the verifier (run B-20261115-170518-c1b61a3: 3.495 and 1.500 at
  small alpha). Not confirmed: the paper's Omega today ~ sigma^(7/2) (2403.15126:1074); with
  its own eq. (result_OmZ), z_e at t_col (line 1061), it is sigma^(5/2) [TO VERIFY].
- N-body in AthenaK's Newtonian mode (decision 0013; newton_tests, lead recheck run
  B-20261115-190015-4dd3416): the isolated Zel'dovich ellipsoid of the 2605.04487
  benchmark crosses at t_x = 24.066, 23.895, 23.860 (N = 32, 64, 128; ODE 23.852; Richardson
  23.851, second order); its quadrupole energy to the first crossing approaches the ODE at
  first order (-34, -18, -10 percent); four exact rescalings give E/(M c^2 (2 alpha)^(7/2))
  the same to 3e-14, so the 7/2 law of the single patch holds in the code; the plane-wave
  pancake follows the exact Zel'dovich solution with the error of the seven-point Laplacian,
  (kh)^2/12 in the force (H1, confirmed at n = 16, 32, 64; runs B-20261115-163556-ad5637f,
  -165349-81a17bc, -163653-f6324ea). The Newtonian mode has been on main since core-v0.3
  (corrected; the wave-1 text said it was not).
- Open: N2 (a patch embedded in a periodic box) needs core's per-species history.

## Criterion 3. "Background error and constraint convergence with the stand-in matter": struck by decision 0013

The particle FLRW background measured directly (`cosmo/`): lapse = scale factor to 1.9e-7
at a = 4 and 7.0e-8 at a = 36 (run B-emd-gw-20261115-115414-7ffbde1); the error of chi
converges at fourth order; the relative Hamiltonian constraint is 1.6e-9, 1.1e-10, 3.2e-11 at
8, 16, 32 cells at t = 100 Mpc/h and 3.1e-8, 2.5e-9, 3.0e-9 at t = 3000 Mpc/h, where it no
longer falls from 16 to 32 cells (corrected; `cosmo/analysis/daverio_a.json`, keys `Hr`).
Particle-number convergence of the background: not shown (G2).

## The first source in full GR (beyond G1; counts toward G2 and G3)

Crossed waves (1, eps, 0), delta = 0.01, box 4, two particles per cell and direction, to
a = 140 (first_source; card runs B-20261115-164059-d802e82, -165353-b592d43; processor runs
B-20261115-165525-f7c2004; rechecked by the lead, run B-20261115-190007-e09a0d2): the
(k, k, 0) strain follows the second-order value with its junk oscillation to 0.22-0.44
percent for 2 <= a <= 10, linear in eps to 0.05 percent; the plane-symmetric null holds at
rounding (<= 4e-16) through shell crossing; 32^3 and 64^3 agree to 0.09 percent for a <= 40;
a second spatial gauge (Gamma driver) differs by the computed gauge piece G_tot (raw
difference reduced twelvefold); after shell crossing the strain grows to 2.5 times the
static value, quasi-static (not radiation). Particle-number convergence and the jittered null
are not run.
