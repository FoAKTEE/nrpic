# Notation: Hybrid SCP-AP General-Relativistic Kinetic Paper

Follows the conventions of the host NRPIC paper where shared (units $G = c = 1$, signature $(-,+,+,+)$). Greek indices $\mu,\nu$ run over spacetime coordinates, Latin indices $i,j,k$ over spatial coordinate components, and parenthesized indices $(m),(n)$ over orthonormal triad components of normal observers.

## Symbols

| Symbol | Macro | Definition | First defined |
|---|---|---|---|
| $g_{\mu\nu}$ | | spacetime metric | Sec. II |
| $\alpha$, $\beta^i$, $\gamma_{ij}$, $\gamma$ | `\alpha`, `\beta^i`, `\gamma_{ij}` | lapse, shift, spatial three-metric, determinant $\det(\gamma_{ij})$ | Sec. II |
| $n^\mu$, $K_{ij}$ | | normal-observer four-velocity and extrinsic curvature | Sec. II |
| $x^i$, $u_i$, $W$ | | Darboux spatial coordinates, covariant spatial four-velocity, normal Lorentz factor $\sqrt{1+\gamma^{ij}u_i u_j}$ | Sec. II |
| $\mathcal{F}$, $f$ | `\mathcal{F}` | scalar phase-space density and Darboux-weighted rest-mass density $\sqrt{\gamma}\,W\mathcal{F}$ | Sec. II |
| $D$ | | coordinate rest-mass density $\sqrt{\gamma}\,\rho_0 = \int f\,\dd^3 u$ | Sec. II |
| $E$, $S_i$, $S_{ij}$ | | normal-observer energy, momentum, and spatial stress densities | Sec. II |
| $\mathcal{E}$, $\mathcal{S}_{ij}$ | `\mathcal{E}`, `\mathcal{S}` | densitized energy and stress per rest mass integrated on cubature nodes | Sec. III |
| $N$, $N_b$ | | number of spatial elements and number of momentum bases per element | Sec. III |
| $h_a$, $V_a$, $\bm{E}_a$ | | local smoothing length, effective coordinate volume $\bar{n}_a^{-1}$, and gradient moment matrix | Sec. III.A |
| $m_{a,\alpha}$, $P_{a,\alpha,i}$, $\Pi_{a,\alpha,ij}$ | | conserved zeroth, first, and second covariant momentum moments of basis $\alpha$ in element $a$ | Sec. III.A |
| $\bar{u}_{a,\alpha,i}$, $\Sigma_{a,\alpha,ij}$ | | basis mean covariant momentum and symmetric momentum covariance tensor | Sec. III.A |
| $A_{ab,i}$, $\hat{n}_i$, $\beta_F$ | `\beta_F` | effective face area covector, unit face normal, and normal-observer face speed | Sec. III.A |
| $\bm{L}_{a,\alpha}$, $\bm{R}_{a,\alpha}$, $\bm{\xi}_q$, $w_q$ | | Cholesky factor $\bm{L}\bm{L}^T = \Sigma$, Halton $\mathrm{SO}(3)$ frame, Stroud cubature nodes and weights | Sec. III.B |
| $\theta$, $h_{\rm rel}$, $\Gamma_{\rm ad}$, $K_n$ | `\theta`, `h_{\rm rel}`, `\Gamma_{\rm ad}` | dimensionless kinetic temperature $k_B T/\mu_p$, specific enthalpy $K_3/K_2$, Synge adiabatic index, Bessel function | Sec. III.C |
| $\sigma/\mu_p$, $\nu_a$, $w_c$ | | reduced hard-sphere cross section, Maxwell-J{\"u}ttner collision rate, asymptotic Knudsen blend factor | Sec. III.A |
| $(c_r, a_{sr}, b_s)$, $w_{-1,0,1}$ | | two-stage Gauss-Legendre symplectic IRK tableau and non-uniform three-level quadratic Lagrange time weights | Sec. III.B |
| $\bm{q}_p^*$, $s$, $M_{\rm inv}$ | | comoving post-collision momenta, convex projection rescaling factor, cell invariant mass | Sec. III.D |
| $F_{c+1/2}$, $\sigma_{c+1/2}$ | | directional metric-weighted filter flux and harmonic face conductance $2\sqrt{\gamma}_c\sqrt{\gamma}_{c+1}/(\sqrt{\gamma}_c+\sqrt{\gamma}_{c+1})$ | Sec. III.E |
| $\mathcal{H}$, $\mathcal{M}$ | `\Ham`, `\Mom` | $L_2$ norms of the Hamiltonian and momentum constraints | Sec. VI |
| $M_{\rm AH}$, $a_{\rm AH}$, $I$ | `M_{\rm AH}` | apparent-horizon irreducible mass, dimensionless spin $S/M^2$, Kretschmann scalar | Sec. VI |
| $M$, $a$, $\Egeo$, $L_z$, $Q$ | `M`, `a`, `\Egeo`, `L_z` | black hole mass, spin length, geodesic energy $-u_t$, axial angular momentum, Carter constant | Sec. II |
| $R_0$, $y_c$, $\tau$, $\rho_0$ | `R_0`, `\tau` | initial collapse radius, cluster central redshift parameter, central proper time, proper rest-mass density | Sec. VI |

## Named results

Use these fixed descriptive names instead of `Eq.~\eqref{...}` (3.4):

| Name | Relation it names | Section |
|---|---|---|
| the Darboux Vlasov law | conservative 6+1D kinetic equation without $\sqrt{\gamma}$ inside divergences | Sec. II |
| the normal-observer characteristic equations | Hamilton's equations for $(\dd x^i/\dd t, \dd u_i/\dd t)$ | Sec. II |
| the zero-mass-flux root condition | monotonic equation for the face velocity $\beta_F$ | Sec. III.A |
| the sliced flux antiderivatives | analytical 1D parallel moment integrals over $(u_{(1)}/W - \beta_F)$ | Sec. III.A |
| the cubature packet expansion | Halton-rotated fifth-degree Stroud expansion of warm bases into geodesic packets | Sec. III.B |
| the Maxwell-J{\"u}ttner collision rate | M{\o}ller-averaged relativistic hard-sphere rate and Synge closure | Sec. III.C |
| the asymptotic face blend | Knudsen-number exponential blend between kinetic one-sided and HLLC fluxes | Sec. III.C |
| the relativistic Rankine-Hugoniot jump | exact Taub shock density and energy jump for a Synge gas | Sec. IV |

## Preamble macros

| Macro | Meaning |
|---|---|
| `\dd` | `\mathrm{d}` for every differential |
| `\Ham`, `\Mom` | `\mathcal{H}`, `\mathcal{M}` constraint norms |
| `\Egeo` | `\mathcal{E}_{\rm geo}`, geodesic energy per rest mass |
| `\aexc` | `\alpha_{\rm exc}`, lapse excision threshold |

