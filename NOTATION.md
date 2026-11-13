# Notation: NRPIC reconstruction paper

The notation dictionary of the paper (3.6, 3.7). It follows the notation of the original
method paper wherever that is unambiguous, so readers can move between the two. Use only
macros already defined in the manuscript preamble, and add no new packages.

Units: geometrized, G = c = 1. Signature (-,+,+,+). Greek indices are spacetime indices,
Latin indices i, j, k are spatial coordinate indices, indices in parentheses (m), (n) are
orthonormal-frame (tetrad) indices.

## Symbols

| Symbol | Macro | Definition | First defined |
|---|---|---|---|
| g_{mu nu} | | spacetime metric | system |
| alpha | `\alpha` | lapse | system |
| beta^i | `\beta^i` | shift | system |
| gamma_{ij}, gamma | `\gamma_{ij}` | spatial metric and its determinant | system |
| n^mu | | future-directed unit normal to the slices | system |
| K_{ij} | | extrinsic curvature | system |
| f(x, u) | | rest-mass-weighted distribution function | system |
| T^{mu nu} | | stress-energy tensor | system |
| E, S_i, S_{ij} | | energy density, momentum density, spatial stress seen by normal observers | system |
| m_p | | rest mass of macroparticle p | system |
| x_p^i | | coordinate position of macroparticle p | system |
| u_i | | covariant spatial components of the four-velocity (momentum per unit rest mass) | system |
| W | | Lorentz factor seen by normal observers, sqrt(1 + gamma^{ij} u_i u_j) | system |
| N | | number of macroparticles | system |
| N_ppc | `\Nppc` | mean number of macroparticles per cell | method |
| Delta t | `\Delta t` | global time step | method |
| h, Delta x | | cell spacing (h in the reconstruction formulas, Delta x elsewhere) | method |
| e^{(m)}_i | | spatial triad (coframe) of the normal observers; gamma_{ij} = delta_{mn} e^{(m)}_i e^{(n)}_j | pushers |
| u_{(m)} | | tetrad components of the momentum, u_{(m)} = e^i_{(m)} u_i | pushers |
| \tilde E_{(m)}, \tilde B_{(m)} | `\Et`, `\Bt` | gravito-electric and gravito-magnetic fields contracted with the momentum | pushers |
| w_a(s) | | cubic Hermite weights, a = -1, 0, 1, 2 | reconstruction |
| B_1 | | first-order (cloud-in-cell) shape function | deposition |
| omega_{Cp} | | weight of particle p on leaf cell C | deposition |
| ell_p, ell_cap | `\ell_p`, `\lcap` | level on which particle p is represented; cap on that level | deposition |
| n_f, c, s | | binomial filter pass count, compensation weight n_f/4, squared half-wavenumber sine | deposition |
| chi, tilde gamma_{ij}, hat K, tilde A_{ij}, tilde Gamma^i, Theta | | Z4c variables | spacetime |
| kappa_1, kappa_2 | | Z4c constraint-damping parameters | spacetime |
| eta | `\eta` | shift damping parameter | spacetime |
| mu_S | | shift speed parameter in the Gamma-driver condition | spacetime |
| c_H | | coefficient of the parabolic Hamiltonian-constraint relaxation | spacetime |
| H, M_i | `\Ham`, `\Mom` | Hamiltonian and momentum constraint residuals | spacetime |
| q | | refinement monitor alpha chi^{-7/4} | adaptive mesh |
| alpha_exc | `\aexc` | lapse threshold of particle excision | numerical methods |
| R | | areal radius | numerical methods |
| K_T | | tangential extrinsic curvature on a coordinate sphere | numerical methods |
| M_MS | | Misner-Sharp mass of the spatial slice | numerical methods |
| M | | ADM mass; sets the unit of length and time | tests |
| a | | Kerr spin parameter (length) | tests |
| E, L_z, Q | `\Egeo`, `L_z`, `Q` | geodesic energy, axial angular momentum, Carter constant | tests |
| R_0 | | initial areal radius of the dust ball | tests |
| \bar r | `\rbar` | isotropic radius | tests |
| psi | `\psi` | conformal factor of the initial slice | tests |
| tau | `\tau` | proper time along a particle worldline | tests |
| M_eff | | enclosed mass implied by a circular tracer orbit | tests |
| tau_c | `\tau_c` | proper time of the central normal observer | numerical methods |
| alpha_c | | central lapse | tests |
| y_c, z_c | | cluster sequence label and central redshift | tests |
| M_0 | | total rest mass | tests |
| alpha_{c,eq} | | central lapse of the cluster equilibrium (isotropic lapse of the model) | tests |
| E_0 | | conserved energy per unit rest mass shared by all particles of a monoenergetic cluster | tests, sampling appendix |
| E_c | | energy density at the centre seen by the normal observer | tests |
| M_AH | `M_{\rm AH}` | apparent-horizon (irreducible) mass | numerical methods |
| h | | spacing of the particle lattice of the dust ball | tests, sampling appendix |
| ell_loc | `\ell_{\rm loc}` | finest mesh level at the position of a particle | deposition |
| E_b | | binding energy M_0 - M | tests |

## Named results

The names that replace equation numbers (3.4). Use each name consistently.

| Name | What it is | Where |
|---|---|---|
| the characteristic equations | dx^i/dt and du_i/dt of a geodesic in 3+1 form | system |
| the particle sources | E, S_i, S_ij as sums over macroparticles | system |
| the midpoint update | implicit midpoint discretization of the characteristic equations | pushers |
| the tetrad equation of motion | du_(m)/dt in Lorentz-force form with the contracted gravito-electric and gravito-magnetic fields | pushers |
| the Boris rotation | kick, rotation, kick sequence in the tetrad frame | pushers |
| the Hermite weights | the four cubic weights and their derivatives | reconstruction |
| the conservation identity | sum over leaf cells of (E, S_i, S_ij) sqrt(gamma) Delta V equals the particle sums | deposition |
| the level cap | representation level ell_p = min(finest local level, ell_cap) | deposition |
| the refinement indicator | the Loehner-type ratio of second to first differences of q | adaptive mesh |
| the lapse bound | central lapse 1 + 6 ln(R/R_0) of collapsing dust in 1+log slicing | tests |
| the cycloid | R(eta), tau(eta), rho(eta) of the collapsing dust ball | tests |
| the structure equations | the dimensionless equilibrium equations of the monoenergetic cluster | tests |

## Preamble macros

| Macro | Meaning |
|---|---|
| `\dd` | the differential, for every differential |
| `\Nppc` | N_{\rm ppc} |
| `\lcap` | \ell_{\rm cap} |
| `\aexc` | \alpha_{\rm exc} |
| `\Ham`, `\Mom` | \mathcal{H}, \mathcal{M} |
| `\Egeo` | \mathcal{E}, the geodesic energy |
| `\Et`, `\Bt` | \tilde E, \tilde B |
| `\rbar` | \bar r |

## Renames

| Old | New | Reason |
|---|---|---|
| E (geodesic energy, original paper) | \mathcal{E} (`\Egeo`) | collision with the energy density E |
| S_{ijk} (assignment weight, original paper) | omega_{Cp} only | collision with the stress S_{ij} |
| E_i (refinement indicator, original paper) | varepsilon_i | collision with the energy density E |
| hatted tetrad indices | parenthesized indices | hats are used for the Z4c variable \hat K |
| mu (shift speed parameter) | mu_S | collision with spacetime index mu |

## Overlaps kept on purpose

| Symbol | Meanings | Why they stay apart in the text |
|---|---|---|
| M | ADM mass; (calligraphic) momentum constraint | different typeface, never in one formula |
| a | Kerr spin parameter; spheroid semi-axis (prolate collapse) | different sections; the spheroid axes are always written a_eq and b |
| h | cell spacing in the reconstruction formulas; particle-lattice spacing | equal by construction in the dust-collapse setup, stated there |
