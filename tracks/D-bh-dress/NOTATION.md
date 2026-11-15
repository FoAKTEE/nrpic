# Notation of the working note of Track D (3.7)

Units G = c = 1 throughout; lengths and times in units of the initial black-hole mass M.

| Symbol | Meaning | Where defined |
|---|---|---|
| M | mass of the black hole at the start (bubble interior: Misner-Sharp mass inside the wall) | Sec. II |
| M_AH | apparent-horizon (area, irreducible) mass, sqrt(A/16 pi) | Sec. II |
| bar M_AH | running mean of M_AH over a window (20 M unless stated) | Sec. IV B |
| Delta M_in | energy that crossed the horizon (two definitions) | Sec. II C |
| a, a_i | scale factor measured by distant comoving dust; its initial value | Sec. II |
| H, H_i | Hubble rate of the dust plateau; initial value | Sec. III A |
| eps | H_i M, the initial Hubble rate in units of the black hole | Sec. II |
| k | coupling exponent, M proportional to a^k | Sec. II C |
| k_eff | Delta ln(M_AH - Delta M_in) / Delta ln a over a run | Sec. II C |
| R | areal radius | Sec. III A |
| rbar | isotropic (conformal) radius of the slice | Sec. III A |
| psi | conformal factor, psi = 1 + u + m_p/(2 rbar) | Sec. III A |
| u | regular part of psi (table column) | Sec. III A |
| m_p | bare mass of the puncture | Sec. III A |
| K^r_r, K^theta_theta | mixed components of the extrinsic curvature (KL, KT in the files) | Sec. III A |
| rho, rho_0 | rest-mass density of the dust; its plateau value | Sec. III A |
| f | slicing function of the vacuum transition, K^theta_theta = -f (2M/R^3)^(1/2) | Sec. III A |
| R_w, R_in, R_out | Schuecking radius, wall (innermost dust), outer dust edge | Sec. III A |
| tau | proper time of a dust particle or tracer | Sec. III A |
| E | specific energy of a shell or tracer (LTB energy function) | Sec. IV A |
| H, M_r (in figures) | Hamiltonian and momentum constraint residuals | Sec. IV A |
| h, Delta x | grid spacing; finest cell at the puncture | Sec. III C |
| r_ta, M_ta | turnaround radius; mass inside it, black hole included | Sec. IV D |
| lambda | r / r_ta, self-similar radius | Sec. IV D |
| lambda_1 | outermost caustic of the self-similar solution | Sec. IV D |
| rho_b | background (Einstein-de Sitter) density | Sec. IV D |
| sigma_i | initial velocity dispersion of warm dust (units of c) | Sec. IV D |
| L | specific angular momentum of a particle | Sec. II B |
| Gm | gravitational radius of the black hole in the spike calculation (m its mass) | Sec. IV C |
| f (spike) | phase-space distribution function; written f_DM to avoid the clash with the slicing function | Sec. IV C |

## Names that replace equation numbers (3.4)

| Name | Relation |
|---|---|
| the wall law | R_w(tau) = (R_in^(3/2) + (3/2)(2M)^(1/2) tau)^(2/3), marginally bound comoving shell |
| the infall law | proper time of a radial fall from R0 with energy E to R = 2M (cycloid) |
| the Hamiltonian constraint on the table | 16 pi rho = -8 psi^(-5) lap psi + 4 K^r_r K^theta_theta + 2 (K^theta_theta)^2 |
| the floor | smallest detectable change, max|D| + D_fs + 2 sqrt(2) sigma |
| the coupling estimator | k_eff above |
| the capture condition | L < 4M for a particle falling from rest at infinity |

## Kept overlaps and renames

- f is the slicing function; the spike's distribution function is f_DM.
- H in the constraint figure is the Hamiltonian residual; H elsewhere is the Hubble rate.
  The figure labels say "Hamiltonian", the text writes the residual as \mathcal H.
- m (lower case) is the black-hole mass of the spike calculation in its own units (Gm);
  m(lambda) is the self-similar mass profile in units of M_ta. Both follow their sources.

## Preamble macros

`\dd` (differential), `\Ham` (\mathcal H), `\Mom` (\mathcal M), `\MAH` (M_{\rm AH}).
