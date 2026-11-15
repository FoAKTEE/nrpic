# Notation: working note of Track A (S1)

The notation dictionary of `note/main.tex` (3.6, 3.7). Units G = c = 1. Use only the macros of
the manuscript preamble; add no new packages.

## Symbols

| Symbol | Macro | Definition | First defined |
|---|---|---|---|
| tau | `\tau` | proper time of comoving matter (time since the initial slice) | Sec. III |
| t_H | `t_H` | cosmic time at horizon entry of the comoving compaction radius, r_m a H = 1 | Sec. II |
| t_end | `t_{\rm end}` | end time of a run, in t_H; also the end of the matter era in the finite-duration estimate | Sec. II |
| mu | `\mu` | amplitude of the curvature profile of Yoo et al. | Sec. II |
| e, p | `e`, `p` | ellipticity and prolateness of the deformation | Sec. II |
| e_E | `e_{\rm E}` | Euler's number, kept apart from the ellipticity e | Sec. II |
| deltabar_ent | `\bar\delta_{\rm ent}` | linear mean density contrast inside r_m at horizon entry | Sec. II |
| delta_c | `\delta_c` | linear central density contrast at horizon entry | Sec. II |
| delta_fd | `\delta_{\rm fd}` | amplitude that collapses exactly at t_end | Sec. II |
| mu_fd | `\mu_{\rm fd}` | the same in mu | Sec. II |
| h-hat(e, p) | `\hat h` | Zel'dovich-hoop function of Yoo et al. | Sec. II |
| A_c | `A_c` | threshold amplitude in any of the measures | Sec. II |
| r_m | `r_m` | comoving compaction radius of the profile | Sec. II |
| R | `R` | areal radius | Sec. III |
| m(R) | `m` | Misner-Sharp mass inside R | Sec. III |
| E(R) | `E` | binding energy per unit mass of a shell (E < 0 bound) | Sec. III |
| v | `v` | radial velocity of the matter, dR/dtau | Sec. III |
| H | `H` | Hubble rate of the envelope on the initial slice | Sec. III |
| M | `M` | total mass of the ball | Sec. III |
| R_b | `R_b` | radius of the ball | Sec. III |
| R_i | `R_i` | areal radius of a shell on the initial slice | Sec. III |
| Delta(R) | `\Delta` | mean density contrast inside R on the initial slice | Sec. III |
| K_ij, K | `K_{ij}`, `K` | extrinsic curvature and its trace (K < 0 for expansion) | Sec. III |
| H, M (constraints) | `\mathcal H`, `\mathcal M` | Hamiltonian and momentum constraint residuals | Sec. IV |
| h | `h` | cell spacing of the constraint check | Sec. IV |
| m_AH | `m_{\rm AH}` | mass of the outermost trapped sphere on a slice | Sec. IV |
| tau_ta, tau_AH, tau_c | `\tau_{\rm ta}`, ... | turnaround, first trapped sphere, crunch of the core | Sec. IV |
| s | `s` | dispersion measure sigma_v R/(2M) | Sec. II |
| sigma_H | `\sigma_H` | rms density contrast on the scale at horizon entry | Fig. 2 |

## Named results

| Name | What it is | Where |
|---|---|---|
| the ball condition | 2M/R_b = (H R_b)^2 < 1: no anti-trapped sphere on the initial slice | Sec. III A |
| the slice of the matter's proper time | lapse one, flat slice for E = 0, K^R_R = -dv/dR, K^theta_theta = -v/R | Sec. III A |
| the constraint identities | Hamiltonian constraint reduces to m' = 4 pi R^2 rho; momentum constraint holds identically | Sec. III A |
| the amplitude conversion | delta_c = e_E deltabar_ent = 12 mu / 5 | Sec. II A |
| the finite-duration amplitude | delta_fd = (t_H/t_end)^(2/3) | Sec. II B |
| the Zel'dovich-hoop line | mu > h-hat(e, p) at horizon entry | Sec. II C |
| the outcome rule | BH / NO-BH / UNDECIDED and the bracket of A_c | Sec. II B |

## Preamble macros

| Macro | Meaning |
|---|---|
| `\dd` | the differential |
| `\Ham`, `\Mom` | Hamiltonian and momentum constraint residuals |

## Renames

| Old | New | Reason |
|---|---|---|
| e (Euler's number, scope SCOPE.md 10.1) | e_E | collision with the ellipticity e |
| H (Hamiltonian constraint in the journals) | \mathcal H | collision with the Hubble rate H |

## Overlaps kept on purpose

| Symbol | Meanings | Why they stay apart in the text |
|---|---|---|
| M | total mass of the ball; unit of length and time (M = 1) | the unit appears only in axis labels and the ledger |
| h | cell spacing; h-hat is the hoop function | the hoop function always carries its hat |
