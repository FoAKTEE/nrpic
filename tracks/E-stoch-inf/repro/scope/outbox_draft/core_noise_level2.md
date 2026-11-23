# Draft request to core: stochastic backreaction of level 2 (`<scalar_field> noise_level = 2`)

From: E-stoch-inf, package repro/scope (2026-11-22). For the lead of E to post (outbox), not posted.

## Why

arXiv:2512.14649 (P1, `kb-data/raw/arxiv/2512.14649/v2/src/PRD_v2.tex`) runs its validation with
"level 2" backreaction (P1:487, 520) and shows an ablation of levels 0, 1, 2 at 256^3 with one seed
(Fig. 9, P1:777-790). Our code has levels 0 and 1 (`scalar_field_noise.cpp:162-166` refuses 2). Every
other figure of P1 is reproduced with level 0 within P1's own bound (about 1e-4 in the spectrum,
P1:520); Fig. 9 and the statement P1:520 need level 2. Track E's map: `repro/scope/REPRO_MAP.md` rows
Fig. 9 and S3.

## What level 2 is in P1 (P1:312-323, 783-788)

The mode equation of the noise, P1 eq. (ReqISTORIZ1), in real space:

    Pi_R = 9 phidot_b^2/(alpha_b K_b^2) (d_0 R + beta^i d_i R)
    d_0 Pi_R - alpha_b K_b Pi_R + beta_b^i d_i Pi_R - 9 phidot_b^2 alpha_b/K_b^2 d_i d^i R = 0

with the background coefficients replaced by their local values: phi_b -> phi(t, x) (so phidot_b ->
alpha Pi), K_b -> K(t, x), alpha_b -> alpha, beta_b -> beta. The field R(t, x) starts from the draw
R*(x) = L^(-3/2) sum_n R_n(t*) alpha_n e^(i k.x) (and its time derivative), and the noise of each step
is S_R(k) built from the Fourier coefficients of R and dR/dt on the mode set, as now.

## Smallest option that would serve

`<scalar_field> noise_level = 2` (default unchanged), only with `noise = mukhanov_sasaki`:

1. Two mesh fields R, Pi_R (or R, dR/dt), initialised at t* by the existing synthesis from the mode
   file (W = 1), evolved with the stage coefficients of the driver by the equation above with the
   local alpha, K = Khat + 2 Theta, Pi and the stencils of the field (sixth order at nghost = 4).
2. At each stage: the coefficients R_n, dR_n/dt on the mode set by projection of the two fields onto
   e^(-i k.x) (the adjoint of the existing synthesis, same mode order and normalisation L^(-3/2)),
   then S_R exactly as now (window and its derivatives from the box means of level 1, or the
   lockstep background of level 0: say which; P1 does not state it [TO VERIFY with P1's authors' text
   only, no contact]).
3. Everything else unchanged: kick coefficients, projector, keys of the draw.

No FFT library is needed (the projection costs what the synthesis costs, 10-19 percent of a step at
256^3, SF2 cost row). A cheaper variant, if (1)-(2) is too large for one release: local coefficients
only in the kick amplitudes (Pi_b/H -> Pi/H_local, eps1 -> local), mode functions unchanged; it is not
P1's level 2 and would be labelled as such.

## Tests Track E would supply and run

- Homogeneous slice (no perturbation): level 2 equals level 1 to rounding (the local values are the
  means).
- 32^3, nmax2 = 64: R^NR against the linear reference as in A2 (threshold 0.02 per mode) and the
  odd/even split under s -> -s (level 2 adds an even part only).
- The ablation of P1 Fig. 9 at 256^3, seed A, both scenarios: |Delta_L2/Delta_L0 - 1| per shell at N_f,
  expected below about 1e-4 (P1:520); level 1 from runs RL1, UL1 of repro/scope.

Card cost at 256^3: one run per scenario, 0.6-0.8 card-hours each (U256ap, P256v6 plus the
projection).

## Optional, low priority

`noise_k_sign`, `noise_a_sign` (signs of the K and At_ij kicks beside `noise_pi_sign`), if the group
wants P1:541 "switching any sign" for each source separately; the Pi flip already shows the first-order
violation (ladder NC64/NC128, U256nc).
