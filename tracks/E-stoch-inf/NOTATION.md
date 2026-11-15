# Notation: working note of Track E (stochastic inflation in numerical relativity)

The notation dictionary of the note `note/main.tex` (3.6, 3.7). Use only the macros of the
manuscript preamble; add no packages. Conventions follow arXiv:2512.14649 (the target of
the reproduction) except where stated.

## Symbols

| Symbol | Macro | Definition | First defined |
|---|---|---|---|
| M_Pl | `\Mpl` | reduced Planck mass | Sec. II A |
| N | | number of e-folds; N_0 Bunch-Davies start, N_* start of the simulation, N_f end, N_k crossing of mode k, N_e end surface of delta N | Sec. II A |
| H | | Hubble rate; K = -3H on the background | Sec. II A |
| eps1, eps2 | `\epsilon_1`, `\epsilon_2` | slow-roll parameters, eps1 = -d ln H/dN, eps2 = -d ln eps1/dN (sign of the source papers: eps2 = +6 in USR) | Sec. II A |
| R, R_k | `\mathcal{R}` | comoving curvature perturbation and its mode function | Sec. II A |
| Delta_R | `\Delta_\mathcal{R}` | dimensionless power, k^3 abs(R_k)^2/(2 pi^2) | Sec. II A |
| W_k(t) | | coarse-graining window, (1/2){1 + tanh[s ln(k_sigma/k)]} | Sec. II A |
| k_sigma, sigma, s | `k_\sigma` | window scale sigma a H; its parameter; the steepness of the tanh | Sec. II A |
| alpha_k | `\alpha_{\bm k}` | complex unit Gaussian of wave vector k, drawn once | Sec. II A |
| S_R | `S_\mathcal{R}` | stochastic source built from R_k and the window derivatives | Sec. II A |
| phi, Pi | | scalar field and its momentum along the normal observers | Sec. II A |
| K, A_ij | | trace of the extrinsic curvature and its conformal trace-free part | Sec. II A |
| dk | `\Delta k` | lattice wave-number spacing 2 pi/L | Sec. II B |
| L | | box size, L k_sigma* = 2 pi | Sec. II B |
| k_max | | noise cutoff 64 dk (N/4 cells per shortest wavelength) | Sec. II B |
| H, M (constraints) | `\mathcal{H}`, `\mathcal{M}` | Hamiltonian and momentum constraint; [H], [M] their term magnitudes | Sec. II C |
| sigma_lin | `\sigma_\mathrm{lin}` | standard deviation of linear delta N over the band | Sec. IV B |
| theta | `\theta` | Courant factor dt/dx | Sec. III D |

## Named results

| Name | What it is | Where |
|---|---|---|
| the stochastic sources | S_Pi, S_K, S_A of S_R, all from one draw | Sec. II A |
| the freezing criterion | per-mode power ratio between N_k + 4 and N_f against the full Mukhanov-Sasaki ratio | Sec. II C |
| the deformed equation | Mukhanov-Sasaki equation without metric perturbations (arXiv:2606.14853) | Sec. II C |
| the corrected momentum of the initial slice | delta Pi with -sqrt(2 eps1) Mpl H Psi_B | Sec. III C |

## Preamble macros

| Macro | Meaning |
|---|---|
| `\dd` | the differential |
| `\Mpl` | reduced Planck mass |
| `\Ham`, `\Mom` | Hamiltonian and momentum constraints |

## Overlaps kept on purpose

| Symbol | Meanings | Why they stay apart in the text |
|---|---|---|
| N | e-folds; cells per side of the lattice | the lattice size is written "256 cells per side" or N^3 only in the parameter table and figure axes; e-folds always carry a subscript or appear in N - N_* |
| sigma | window parameter; standard deviation (sigma_lin) | the standard deviation always carries the subscript lin |
| H | Hubble rate; Hamiltonian constraint | the constraint is `\Ham` (calligraphic) |
