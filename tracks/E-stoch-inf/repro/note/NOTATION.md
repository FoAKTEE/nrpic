# Notation: working note on the reproduction of two papers on stochastic inflation

The notation dictionary of `manuscript/main.tex` (3.6, 3.7). Use only the macros of the
preamble; add no packages. Conventions follow arXiv:2512.14649 (the lattice paper) and
arXiv:2401.08530 (the one-patch paper), which share them, except where stated.

## Symbols

| Symbol | Macro | Definition | First defined |
|---|---|---|---|
| M_Pl | `\Mpl` | reduced Planck mass | Sec. II |
| N, N_b | `\mathcal{N}`, `\mathcal{N}_b` | number of e-folds of a patch; of the background; N_* start of the lattice run, N_f its end | Sec. II |
| H | | Hubble rate; K = -3H on the background | Sec. II |
| eps1, eps2 | `\epsilon_1`, `\epsilon_2` | eps1 = -d ln H/dN, eps2 = -d ln eps1/dN (eps2 = +6 in USR) | Sec. II |
| R, R_k | `\mathcal{R}` | comoving curvature perturbation; its mode function | Sec. II |
| R^NR | `\mathcal{R}^\mathrm{NR}` | curvature perturbation reconstructed from the lattice metric and field | Sec. III |
| Delta | `\Delta` | dimensionless power k^3 abs(R_k)^2/(2 pi^2) | Sec. II |
| W_k | | coarse-graining window (1/2){1 + tanh[s ln(k_sigma/k)]} | Sec. II |
| k_sigma, sigma, s | `k_\sigma` | window scale sigma a H; its parameter; steepness | Sec. II |
| S_R | `S_\mathcal{R}` | source of the coarse-grained R: MS operator acting on W R | Sec. II |
| S_Pi, S_K, S_A | | sources of the momentum, of K and of the trace-free curvature | Sec. II |
| phi, Pi | | scalar field and its momentum along the normal | Sec. II |
| alpha | `\alpha` | lapse | Sec. II |
| K, Kt_ij | `\tilde K_{ij}` | trace and trace-free part of the extrinsic curvature | Sec. II |
| Q | | sqrt(3 Kt_ij Kt^ij / 2), the anisotropic expansion in units of K | Sec. III F |
| H, M (constraints) | `\Ham`, `\Mom` | Hamiltonian and momentum constraints; [H], [M] the sums of the magnitudes of their terms | Sec. III |
| dk, k_max | `\Delta k`, `k_\mathrm{max}` | lattice spacing 2 pi/L of wave numbers; noise cut-off | Sec. III |
| Z | | variable phidot_b/alpha of the one-patch system | Sec. IV |
| h | | step of the stochastic integrator in e-folds | Sec. IV |
| S (one patch) | `S` | noise per e-fold of the one-patch system | Sec. IV |
| kappa3, kappa4 | `\kappa_3`, `\kappa_4` | skewness and excess kurtosis | Sec. IV |

## Named results

| Name | What it is | Where |
|---|---|---|
| the stochastic sources | S_Pi, S_K, S_A of S_R | Sec. II |
| the Langevin pair | the equations for alpha and N of the one-patch system | Sec. IV A |
| the Ito term | the drift alpha^n <S^2> that the chain rule adds | Sec. IV C |
| the plateau stop | the value at which the converged background halts | Sec. IV B |
| the amplitude factor | the ratio of the papers' one-point bands to those its spectra imply | Sec. III D |

## Preamble macros

| Macro | Meaning |
|---|---|
| `\dd` | differential |
| `\Mpl` | reduced Planck mass |
| `\Ham`, `\Mom` | Hamiltonian and momentum constraint |
| `\pending{}` | red marker for a result that waits for a continued run |
| `\Pone`, `\Ptwo` | short names of the two papers in the text (Paper I = arXiv:2401.08530, Paper II = arXiv:2512.14649) |

## Overlaps kept on purpose

| Symbol | Meanings | Why they stay apart |
|---|---|---|
| N | e-folds (calligraphic) and cells per side of the lattice (roman, in N^3) | the lattice size always appears as N^3 or a number cubed |
| alpha | lapse; the Gaussian amplitudes alpha_k of the papers | the note writes the Gaussian amplitudes as "the random numbers" in words |
| sigma | window parameter; standard deviation | the standard deviation is written "width" in the text |
| H | Hubble rate; Hamiltonian constraint | the constraint is calligraphic |

## Section on the criteria (batch 15)

| Symbol | LaTeX | Meaning | First use |
|---|---|---|---|
| lambda | `\lambda` | common amplitude of all stochastic sources and of the initial slice (one in the reproduction) | Sec. IV A |
| X_odd, X_even | `X_\mathrm{odd}`, `X_\mathrm{even}` | odd and even parts of an output from the runs at +lambda and -lambda ("the odd-even split") | Sec. IV A |
| e, o | `e(\lambda)`, `o(\lambda)` | rms over the lattice of the even and the odd part of a constraint | Sec. IV C |
| f | `f` | noise level fixed in advance, f^2 = 4 o(1/2)^2 - o(1)^2 ("the fixed estimator") | Sec. IV C |
| E, A, F_lambda | `E(\lambda)`, `A`, `F_\lambda` | even field of a constraint; its second-order field; the per-run part | Sec. IV C |
| D_1, D_2 | `D_1`, `D_2` | difference fields E(1) - 4E(1/2), E(1/2) - 4E(1/4) ("the difference statistics") | Sec. IV C |

Overlap: s stays the window steepness; the noise amplitude is lambda (the program's records call it s).


## Section on the tail statistics (G3, batch 34)

| Symbol | LaTeX | Meaning | First use |
|---|---|---|---|
| zeta | `\zeta` | delta-N curvature perturbation at N_f: e-folds of each cell, as a homogeneous universe from its field and field velocity, to the uniform-field surface of the reference, plus the local scale factor, box mean removed ("the delta-N curvature perturbation"); zeta = -R^NR at first order | Sec. V A |
| Delta N_bg | `\Delta N_\mathrm{bg}` | e-folds of the homogeneous universe from the cell's state to the end surface | Sec. V A |
| sigma_zeta | `\sigma_\zeta` | the box's own standard deviation of zeta ("the own width") | Sec. V A |
| F_pm(nu) | `F_\pm(\nu)` | fraction of cells above nu sigma_zeta (plus) or below -nu sigma_zeta (minus) ("the tail fractions") | Sec. V A |
| Q(nu) | `Q(\nu)` | the Gaussian tail fraction above nu standard deviations | Sec. V A |
| A(nu) | `\mathcal{A}(\nu)` | tail asymmetry (F_+ - F_-)/(F_+ + F_-) ("the asymmetry") | Sec. V A |
| a | `a` | quadratic coefficient of the even part of a mirrored pair on the square of its odd part | Sec. V C |

Overlap: A(nu) is calligraphic; A without argument stays the second-order constraint field of Sec. IV C.
