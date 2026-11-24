# Notation: working note of core

The notation dictionary of `note/main.tex` (3.6, 3.7). Geometric units G = c = 1; M is
the mass that sets the scale of each test (ADM mass of the dust ball or cluster, mass of
the Kerr black hole).

## Symbols

| Symbol | Macro | Definition | First defined |
|---|---|---|---|
| alpha, beta^i, gamma_ij, K_ij | plain | lapse, shift, spatial metric, extrinsic curvature of the 3+1 split | Sec. II |
| u_i | plain | covariant spatial momentum per unit mass of a particle | Sec. II |
| E, L_z, Q | plain | energy, axial angular momentum, Carter constant of a Kerr geodesic | Sec. III A |
| a | plain | spin parameter of the Kerr black hole | Sec. III A |
| M_AH | `\Mah` | mass of the apparent horizon from its area, sqrt(A/16 pi) | Sec. III B |
| alpha_c | plain | lapse at the centre of a cluster | Sec. III D |
| y_c | plain | central parameter of a monoenergetic cluster model (central redshift factor) | Sec. III D |
| y_c* | plain | turning point of the binding energy along the sequence | Sec. III D |
| H, Theta | plain | Hamiltonian constraint; constraint variable of Z4c | Sec. III E |
| dx, dt | plain | finest cell size, step | Sec. III |

## Named results

| Name | What it is | Where |
|---|---|---|
| the deposition identity | the mesh integral of the deposited sources equals the sum over particles to round-off | Sec. III E |
| the verification ladder | the rows of the brief's section 10 marked CORE | Sec. III |

## Preamble macros

| Macro | Meaning |
|---|---|
| `\Mah` | `M_{\rm AH}` |
| `\noterun` | id of the registered run that made the figures and tables (`tables/runinfo.tex`) |
