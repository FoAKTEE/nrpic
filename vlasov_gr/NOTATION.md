# Notation: PRX general-relativistic kinetic methodology paper

Consistent mathematical dictionary across `main.tex`, all section files in `paper/sections/`, `appendix_sampling.tex`, `appendix_parameters.tex`, and `supplement.tex`. Every differential uses `\dd`; no symbol carries conflicting definitions within an equation or subsection.

Units: geometrized $G = c = 1$, signature $(-,+,+,+)$. Greek indices $\mu, \nu, \rho, \sigma$ run over spacetime coordinates; Latin indices $i, j, k, l$ run over spatial coordinates; parenthesized indices $(m), (n), (k)$ label orthonormal normal-observer tetrad components.

## Symbols

| Symbol | Macro | Definition | First defined |
|---|---|---|---|
| $g_{\mu\nu}, g^{\mu\nu}$ | | spacetime metric and inverse | system |
| $\alpha, \beta^i$ | | ADM lapse function and shift vector | system |
| $\gamma_{ij}, \gamma^{ij}, \gamma$ | | spatial three-metric, inverse, and determinant $\det(\gamma_{ij})$ | system |
| $n^\mu, n_\mu$ | | future-directed unit normal to constant-$t$ hypersurfaces | system |
| $K_{ij}, K$ | | extrinsic curvature and trace $\gamma^{ij} K_{ij}$ | system |
| $\chi, \tilde{\gamma}_{ij}, \tilde{A}_{ij}, \hat{K}, \tilde{\Gamma}^i, \Theta$ | | Z4c conformal variables and constraint scalar | system |
| $\kappa_1, \kappa_2, \mu_S, \eta, c_H$ | | Z4c constraint-damping, gauge, and relaxation parameters | system |
| $\mathcal{H}, \mathcal{M}_i$ | `\Ham`, `\Mom` | ADM Hamiltonian and momentum constraint residuals | system |
| $\varepsilon$ | | mass-shell indicator ($\varepsilon = 1$ massive, $\varepsilon = 0$ null) | system |
| $u_\mu, u^i$ | | covariant four-velocity per unit mass (or affine null covector) | system |
| $W$ | | normal-observer Lorentz factor or dimensionless energy $\sqrt{\varepsilon + \gamma^{ij} u_i u_j}$ | system |
| $H(x^i, u_i)$ | | canonical Darboux Hamiltonian $-u_0 = \alpha W - \beta^i u_i$ | system |
| $\mathcal{F}, f$ | | invariant phase-space distribution and Darboux density $\sqrt{\gamma} W \mathcal{F}$ | system |
| $E, S_i, S_{ij}, D$ | | normal-observer energy density, momentum density, spatial stress, and $\sqrt{\gamma}\rho_0$ | system |
| $\mu_p, m_p$ | | microscopic constituent mass and finite macroparticle rest mass | system |
| $\mathcal{E}_{\rm geo}, L_z, Q, K_{\rm C}$ | `\Egeo`, `L_z`, `Q`, `\KC` | Kerr Killing energy, axial angular momentum, and Carter constants (distinct from $K$) | system |
| $\sigma/\mu_p, \theta, h_{\rm rel}, \bar{W}_{\rm com}, \Gamma_{\rm ad}$ | | reduced cross section, dimensionless temperature, Synge enthalpy, mean Lorentz factor, adiabatic index | system |
| $c_{1,2}, b_{1,2}, a_{rs}$ | | two-stage fourth-order Gauss--Legendre Butcher coefficients | method (pushers) |
| $e^{(m)}_i, u_{(m)}, \tilde{E}_{(m)}, \tilde{B}_{(k)}$ | `\Et`, `\Bt` | normal-observer spatial triad, tetrad momentum, gravito-electric and gravito-magnetic fields | method (pushers) |
| $r, w_{-1}, w_0, w_1$ | | step ratio $\Delta t_n/\Delta t_{n-1}$ and three-level quadratic Lagrange time weights | method (pushers) |
| $h, \Delta x, s$ | | cell spacing and normalized subcell offset $s \in [0, 1)$ | method (reconstruction) |
| $H_{ab}(s), w_{-2}\dots w_3$ | | quintic Hermite polynomial basis and six-node $C^2$ stencil weights | method (reconstruction) |
| $B_1, B_2, B_3, \omega_{Cp}, \ell_p, \ell_{\rm cap}$ | `\lcap` | B-spline shape functions, AMR leaf weights, representation level, and cap | method (deposition) |
| $\sigma_{c+1/2}, F_{c+1/2}, \kappa, w_1$ | | harmonic face metric conductance, intercell flux, and filter coupling | method (filter) |
| $d_0, d_1, \theta_{\rm lim}, s_{\rm m}, \nu_{\rm CFL}$ | | causal stage base, rate/increment, causality limiter, multi-rate stride, Courant factor | method (coupling) |
| $\psi, \psi_s, u, W_i, \bar{A}_{ij}$ | | York--Lichnerowicz conformal factor, analytical puncture piece, potential, and vector potential | method (ID & AMR) |
| $q_{\rm AMR}, \varepsilon_i$ | | L\"ohner refinement monitor $\alpha\chi^{-7/4}$ and normalized second-difference indicator | method (ID & AMR) |
| $\alpha_{\rm exc}, M_{\rm AH}, \chi_{\rm AH}, M_{\rm MS}, I$ | `\aexc` | lapse excision threshold, horizon mass, horizon dimensionless spin, Misner--Sharp mass, Kretschmann scalar | method (diagnostics) |
| $N_{\rm ppc}, \bar{r}, y_c, q = m_p / M_0$ | `\Nppc`, `\rbar` | mean particle count per cell, isotropic radius, cluster central redshift, mass ratio | results & appendices |

## Named equations and results

| Name | Meaning | Section |
|---|---|---|
| the Einstein--Vlasov system | coupled characteristic Vlasov equation and Einstein field equations | Sec.~\ref{sec:system} |
| the ADM constraints | Hamiltonian $\Ham$ and momentum $\Mom_i$ constraint equations | Sec.~\ref{sec:system} |
| the moving-puncture gauge | $1+\log$ lapse and Gamma-driver shift equations | Sec.~\ref{sec:system} |
| the characteristic equations | Hamilton's equations for $(\dd x^i/\dd t, \dd u_i/\dd t)$ with metric parameter $\varepsilon$ | Sec.~\ref{sec:system} |
| the Darboux Vlasov law | flux-conservative phase-space transport equation | Sec.~\ref{sec:system} |
| the particle sources | normal-observer projections $(E, S_i, S_{ij})$ summed over packets | Sec.~\ref{sec:system} |
| the Gauss--Legendre tableau | two-stage fourth-order symplectic implicit Runge--Kutta scheme | Sec.~\ref{sec:method_gl4} |
| the tetrad equation of motion | gravito-electromagnetic Lorentz form in the normal-observer triad | Sec.~\ref{sec:method_gl4} |
| the Boris rotation | kick--rotate--kick update in the orthonormal triad | Sec.~\ref{sec:method_gl4} |
| the three-level time weights | quadratic Lagrange metric interpolation across $(t^{n-1}, t^n, t^{n+1})$ | Sec.~\ref{sec:method_gl4} |
| the quintic Hermite basis | $C^2$ six-node spatial metric interpolation weights and derivatives | Sec.~\ref{sec:method_quintic} |
| the conservation identity | proper-volume leaf integral of $(E, S_i, S_{ij})$ equals particle sums | Sec.~\ref{sec:method_dep} |
| the harmonic face conductance | $\sigma_{c+1/2} = 2\sqrt{\gamma}_c\sqrt{\gamma}_{c+1}/(\sqrt{\gamma}_c+\sqrt{\gamma}_{c+1})$ | Sec.~\ref{sec:method_filter} |
| the harmonic conservative filter | directional and unsplit seven-point self-adjoint flux filters | Sec.~\ref{sec:method_filter} |
| the causal stage limiter | local positivity and subluminality limiter $\theta_{\rm lim} \in [0, 1]$ | Sec.~\ref{sec:method_coupling} |
| the one-sided kinetic flux | MFM boosted normal-observer Riemann moment flux | Sec.~\ref{sec:method_closures} |
| the Maxwell--J\"uttner majorant | globally dominating three-component Gamma-mixture envelope | Sec.~\ref{sec:method_closures} |
| the convex momentum projection | exact four-momentum restoration for unequal packet weights | Sec.~\ref{sec:method_closures} |
| the puncture-split constraint system | coupled Hamiltonian and Bowen--York vector momentum PDEs | Sec.~\ref{sec:method_numerical} |
| the refinement indicator | L\"ohner second-difference ratio of $q_{\rm AMR} = \alpha\chi^{-7/4}$ | Sec.~\ref{sec:method_numerical} |
| the Misner--Sharp mass | quasilocal spherical mass functional | Sec.~\ref{sec:method_numerical} |
| the Kretschmann decomposition | Gauss--Codazzi--Ricci contraction of the Riemann tensor | Sec.~\ref{sec:method_numerical} |

## Preamble macros

`\dd`, `\aexc`, `\Ham`, `\Mom`, `\Egeo`, `\KC`, `\Et`, `\Bt`, `\Nppc`, `\lcap`, `\rbar`

## Renames

| Old | New | Reason |
|---|---|---|
| $K$ (Carter constant) | `\KC` ($K_{\rm C}$) | avoid collision with extrinsic curvature trace $K$ |
| $q$ (AMR monitor) | $q_{\rm AMR}$ | avoid collision with back-reaction mass ratio $q = m_p/M_0$ and filter field $q_c$ |
| $\chi$ (BH spin) | $\chi_{\rm AH}$ | avoid collision with Z4c conformal factor $\chi$ |
| `\eqref` / `Eq.~(\ref{...})` | named equation reference | PRX / Physical Review house style |
| `\texttt{rk3}` | SSP-RK3 | human prose naming rather than raw input keyword |
| `\texttt{matter\_stride}` | multi-rate stride $s_{\rm m}$ | symbolic notation instead of config key |
