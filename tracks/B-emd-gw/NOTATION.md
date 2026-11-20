# Notation: working note of Track B (S2)

The notation dictionary of `note/main.tex` (3.6, 3.7). Use only macros defined in its
preamble, and add no new packages. Units G = c = 1 unless stated; time unit the initial
Hubble time of the box runs.

## Symbols

| Symbol | Macro | Definition | First defined |
|---|---|---|---|
| a | | scale factor of the background, a = 1 at the initial slice | Sec. II |
| tau | `\tau` | conformal time, a = (1 + tau/2)^2 in code units | Sec. II |
| \mathcal{H}_c | `\Hc` | conformal Hubble rate a'/a = 1/(1 + tau/2) | Sec. II |
| H | | Hubble rate at the initial slice (box unit: initial Hubble radius 1/H) | Sec. II |
| L | | box side, in initial Hubble radii | Sec. II |
| k | | wave number of the box's fundamental mode, 2 pi/L | Sec. II |
| K | `\mathbf K` | wave vector (k, k, 0) of the first radiating mode | Sec. II |
| delta | | amplitude of the linear density contrast at a = 1 | Sec. II |
| r_i, epsilon | `\epsilon` | amplitude ratios (1, epsilon, 0) of the crossed waves | Sec. II |
| Phi | `\Phi` | Newtonian (Bardeen) potential, Phi = sum phi_i sin(k x_i) | Sec. II |
| phi_i | | amplitude of the i-th sine wave of Phi, -(3/2)(H/k)^2 delta r_i | Sec. II |
| psi_N | | depth of the potential, (3/2)(H/k)^2 delta | Sec. II |
| h_ij | | metric perturbation, conformal metric minus delta_ij | Sec. II |
| h^TT_ij, h_+, h_x | | flat TT part and its two polarizations | Sec. II |
| \Lambda | `\TT` | flat TT projector in Fourier space | Sec. III |
| K_ij, K^TT_ij | | extrinsic curvature and its TT part | Sec. III |
| rho_K | | energy density of the TT part, (M_pl^2/2) K^TT_ij K_TT^ij | Sec. III |
| E_ij, B_ij | | electric and magnetic parts of the Weyl tensor | Sec. III |
| Psi_4 | `\Psi_4` | Weyl scalar on a fixed null tetrad along the wave direction | Sec. III |
| alpha | `\alpha` | lapse | Sec. III |
| \mathcal H, \mathcal M | `\Ham`, `\Mom` | Hamiltonian and momentum constraints, relative to the energy density | Sec. III |
| N | | cells per box side (cells per wavelength for the vacuum wave) | Sec. IV |
| delta_L, sigma | | linear contrast of the ellipsoid and the rms of the initial field | Sec. IV |
| E_GW | | radiated energy of the ellipsoid | Sec. IV |
| S | | shape factor of the ellipsoid, sum over (3 lambda_i^2 - sum lambda^2)^2/6 | Sec. IV |
| g(tau) | | growth function of the quasi-static strain from conformally flat data | Sec. II |
| s | | static amplitude of the crossed-wave strain, s = -(5/6) phi_x phi_y (replaces h_s) | Sec. II B |
| c_+ | | cosine part of the + amplitude of the flat TT strain at K = (k, k, 0), basis of Sec. II B | Sec. V |
| x, x_T | `\mathbf x`, `\mathbf x_{\rm T}` | code coordinates on a slice; coordinates in which the conformal metric has no traceless scalar or vector part | Sec. III B |
| xi | `\xi` | displacement x_T - x | Sec. III B |
| D, J | | displacement gradient D_ki = d_i xi_k; J = 1 + D | Sec. III B |
| h^R | `h^{\rm R}` | part of the metric no periodic displacement removes: TT part plus homogeneous traceless part | Sec. III B |
| h^L | `h^{\rm L}` | traceless non-TT part of the measured metric, d_i xi_j + d_j xi_i - (2/3) delta_ij div xi | Sec. III B |
| G_tot | `G_{\rm tot}` | the spatial-gauge piece of the flat projection at second order | Sec. III B |
| F | | the force factor of the seven-point stencil, [(k Delta x/2)/sin(k Delta x/2)]^2 | Sec. IV F |
| Delta x | `\Delta x` | mesh spacing (h stays the metric perturbation) | Sec. IV F |
| alpha_e | `\alpha_{\rm e}` | deformation of the ellipsoid (alpha stays the lapse) | Sec. IV F |
| t_k | | time unit of the ellipsoid runs (the time at which linear theory sets the scale) | ledger |
| M | | mass of a patch (only) | Sec. IV E |
| tilde gamma_T | `\tilde\gamma_{\rm T}` | conformal metric in the transverse coordinates | Sec. III B |

## Named results

| Name | What it is | Where |
|---|---|---|
| the plane-symmetric null | an exactly plane-symmetric pancake has no TT part at nonzero wave number | Sec. II A |
| the crossed-wave strain | h_+ = -(5/6) phi_x phi_y cos(K.x) at K = (k, k, 0) before shell crossing | Sec. II B |
| the junk equation | g'' + 2 Hc g' + K^2 (g - 1) = 0, g(0) = g'(0) = 0 | Sec. II B |
| the relativistic depth | psi_N = (3/2)(H/k)^2 delta | Sec. II C |
| the conformal-time slicing | d_t alpha = -(1/3) alpha^2 K | Sec. III A |
| the Zel'dovich energy | E_GW = (8/15) M S [t2^(1/3) - t1^(1/3)] | Sec. IV E |
| the spatial-gauge piece | G_tot (equation in Sec. III B) | Sec. III B |
| the force factor | F = 1 + (k Delta x)^2/12 + ... | Sec. IV F |
| the free tensor equation | the tensor equation of Sec. II B with zero source, h'' + 2 Hc h' + k^2 h = 0; in the matter era its standing solution is a combination of spherical Bessel functions of order one divided by their argument | Sec. IV A |
| the departure from second order | c_+/(s g) - 1 (words in the text; dev in the scripts) | Sec. V A |

## Preamble macros

| Macro | Meaning |
|---|---|
| `\dd` | differential d |
| `\Ham`, `\Mom` | Hamiltonian, momentum constraint |
| `\TT` | the flat TT projector Lambda |
| `\Hc` | conformal Hubble rate |

## Renames

| Old | New | Reason |
|---|---|---|
| K (wave vector) | \mathbf K (bold) | collision with the trace K of the extrinsic curvature |
| H (Hamiltonian constraint) | \mathcal H | collision with the Hubble rate H |
| h_s (static strain) | s | the static amplitude is not a metric component |
| x' (code coordinates) | x (and x_T for the transverse ones) | the prime is the conformal-time derivative |
| M (displacement gradient) | D | M is the mass |
| A (residual metric) | h^R | A is the linear-wave amplitude |
| h (mesh spacing) | Delta x | h is the metric perturbation |
| alpha (deformation of the ellipsoid) | alpha_e | alpha is the lapse |
| jitter amplitude A (scripts) | "a jitter of 0.3 cells" in words | A is the linear-wave amplitude |
| K1, K2 (scripts) | \mathbf K = (k, k, 0) and its mirror (k, -k, 0) | K is the trace of the extrinsic curvature |

## Overlaps kept on purpose

| Symbol | Meanings | Why they stay apart in the text |
|---|---|---|
| k | box wave number; index k of a tensor | indices are i, j, l in the note |
| N | cells per side; cells per wavelength | the vacuum wave fills the box with one wavelength, so they coincide; for the oblique and expanding-box waves N is the cells per side (stated in the text) |
| k | box wave number; magnitude of the wave vector of a test wave | the test wave's vector is named by its direction in the text |
