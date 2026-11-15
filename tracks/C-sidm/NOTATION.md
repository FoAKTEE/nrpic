# Notation: working note of C-sidm

The notation dictionary of the note (3.6, 3.7). Units G = c = k_B = 1; the ADM mass M of
the cluster sets lengths and times unless a unit is given.

## Symbols

| Symbol | Macro | Definition | First defined |
|---|---|---|---|
| f | | one-particle distribution function | Sec. II B |
| E | | Killing energy per unit rest mass, E = -u_t | Sec. II B |
| E_c | | cutoff energy of the truncated families | Sec. II B |
| b | | k_B T(R)/m, temperature at the edge in units of the particle mass | Sec. II B |
| w_0 | | central cutoff kinetic energy over the local temperature (thermal core) | Sec. II B |
| y_0 | | central value of the potential variable of the King sequence (Ref. 2009.08163) | Sec. II B |
| y_c | | central value of e^{2(Phi - Phi_s)} (monoenergetic family) | Sec. II B |
| Z(0), z_c | | central redshift to infinity (all three families; Ref. 2009.08163 quotes e^{y_0} - 1, the redshift to the edge) | Sec. II B |
| epsilon | | binding-energy fraction (M_0 - M)/M_0 | Sec. II B |
| M, M_0 | | ADM mass; rest mass | Sec. II B |
| R | | areal radius of the edge | Tab. I |
| rho_0, p, p_T | | rest-mass density, radial and tangential pressure | Sec. II C |
| v_1 | | one-dimensional velocity dispersion, v_1^2 = (p + 2 p_T)/(3 rho_0) | Sec. II C |
| sigma_m | `\sigmam` | cross-section per unit mass | Sec. II C |
| lambda | | mean free path 1/(rho_0 sigma_m) | Sec. II C |
| H | | gravitational scale height (v_1^2/(4 pi rho_0))^{1/2} | Sec. II C |
| Kn, Kn_c | `\Kn` | Knudsen number lambda/H; at the centre | Sec. II C |
| sigma~ | `\sigt` | sigma_m in code units (inverse surface density, units of 1/M) | Sec. II C |
| K | | conversion constant sigma~ Kn_c = 1/(rho_0c H_c) | Sec. II C |
| f_BH | | collapsed mass fraction M_BH/M | Sec. II D |
| theta, zeta | | temperature T/m; zeta = 1/theta | Sec. III B |
| u_a, W_a | | spatial four-velocity of particle a; W = (1 + u^2)^{1/2} | Sec. III B |
| gamma_rel | | -u_a . u_b, relative Lorentz factor of a pair | Sec. III B |
| v_Mol | `\vM` | Moller speed (gamma_rel^2 - 1)^{1/2}/(W_a W_b) | Sec. III B |
| K_nu | | modified Bessel functions of the second kind | Sec. III B |
| P_ij | | collision probability of a tested pair in one step | Sec. III B |
| alpha, gamma_ij | | lapse; spatial metric (determinant gamma) | Sec. III B |
| omega_0^2 | | lowest squared radial-pulsation frequency | Sec. IV A |
| Gamma, Gamma_1 | | adiabatic index of the perturbation; of a Juttner gas | Sec. IV A |
| L | | box length | Sec. IV C |
| varepsilon | | unit roundoff of double precision | Sec. IV B |

## Named results

| Name | What it is | Where |
|---|---|---|
| the Moller-averaged rate | Gamma = rho_0 sigma_m <v_Mol>, <v_Mol> = 4 K_3(2 zeta)/(zeta K_2(zeta)^2) | Sec. III B |
| the pair probability | P_ij = (N - 1) sigma_m M v_Mol alpha Delta t/(sqrt(gamma) Delta V) | Sec. III B |
| the conversion constant | K = sigma~ Kn_c = 1/(rho_0c H_c) | Sec. II C |
| the thermal kernel | f = A[exp((1 - E/E_c)/b) - 1] for E < E_c | Sec. II B |

## Preamble macros

| Macro | Meaning |
|---|---|
| `\dd` | the differential |
| `\Kn` | Knudsen number, roman Kn |
| `\vM` | Moller speed, v with subscript M\o l |
| `\sigmam` | cross-section per unit mass sigma_m |
| `\sigt` | sigma tilde |

## Renames

| Old | New | Reason |
|---|---|---|
| epsilon (binding fraction) vs varepsilon (roundoff) | kept apart by the two glyphs | both appear in the note |
| gamma (metric determinant) vs Gamma (adiabatic index) vs gamma_rel | kept as written | never in one formula |

## Overlaps kept on purpose

| Symbol | Meanings | Why they stay apart in the text |
|---|---|---|
| K | conversion constant; K_nu Bessel functions | the Bessel functions always carry an index |
| M | ADM mass of the cluster; macroparticle mass in the pair probability (equal masses: M_i) | the pair probability writes M_i |
| Z(0), z_c | central redshift to infinity, written Z(0) for the thermal core and z_c for the King and monoenergetic families as in their sources | same quantity; the note keeps the sources' letters |
