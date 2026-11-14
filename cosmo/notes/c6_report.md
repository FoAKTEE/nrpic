# C6: initial conditions of GRAMSES Part II (arXiv:2001.07968), reproduced without radiation

Specification: `cosmo/notes/spec_2001.07968.md` ("notes:L" = its line L; "II:L" = line L of
the paper's `main.tex`). Code: `cosmo/ic/gramses_ic.py` (generator, closed forms, checks),
`cosmo/analysis/gramses_tests.py` (tests, figures). Numbers: `cosmo/analysis/gramses_tests.json`.
Figures: `cosmo/analysis/figs/gramses_*.png` (and `.pdf`). Scratch: `.work/c6/`.

Every test is on initial-condition data at z_ini; nothing is evolved (notes:43-45).

## 1. What was built

`gramses_ic.py`:

- Background and growth for matter + Λ from `spectrum.py` (GRAMSES parameters: Ω_m = 0.3072,
  Ω_Λ = 0.6928, h = 0.68, n_s = 0.9649, σ8 = 0.83, Eisenstein-Hu transfer function with
  baryon wiggles). ℋ/c = aE(a)/(c/H0) in h/Mpc, H in km s⁻¹ (h⁻¹Mpc)⁻¹, m² = (9/2)Ω_m(a)ℋ².
- The closed forms of notes §5.3 as transfer ratios to δ^S at the same k and a (each function's
  docstring gives the formula and the notes line), the spectra of δ^S, δ^p, δ^N, δ^C, η and the
  δ^S–η cross spectrum, the linear P_θθ in the paper's units, the CMC lower-index P_θθ, and the
  finite-difference growth rate II:349.
- `closed_form_checks()`: 20 implementation checks (relations between the closed forms through
  the gauge transformations and constraint equations, numerical time derivatives, small- and
  large-k limits) and 12 comparisons with values printed in the notes.
- `make_ic(n, L, z_ini, setting, velocity, dz, sigma8, ...)`: particles on the n³ lattice of cell
  centres, displaced by the Zel'dovich displacement of a Gaussian field realised with
  `random_field.gaussian_field` (fixed seed, resolution-independent modes, Nyquist planes left
  empty so that −∇·χ = δ exactly);
  - setting "newtonian": δ^S; setting "gramses": δ^p = δ^S[1 + (3f + 9Ω_m/2)/x] (CMC-MD);
  - velocity "fd": II:341 with χ(z±) realised with the same seed from P(z±), the z± spectra
    built with η frozen (II:372) or taken from the closed forms directly, and optionally
    renormalised to σ8 targets like 2LPTic: "linear" (II:378, 384, 388), "scaled" (σ8 ∝ D_1 for
    the setting's own spectrum, i.e. II:384 skipped), "none"; a growth function other than D_1
    can be passed to model a code with different growth; `fd_dtype=np.float32` stores χ(z±) in
    single precision before differencing;
  - velocity "two-step": u^i = Hfχ_S (also in the gramses setting, II:333-334); "naive": Hfχ of
    the setting's own density;
  - `lower=True`: GRAMSES's one-time shift solve (notes §3.7) spectrally on the mesh,
    β_∥ = −m²/(k²+m²)u_∥, β_⊥ = −(4m²/3)/(k² + 4m²/3)u_⊥, and u_i/a² = u^i + β^i;
  - returns positions, velocities u = a^{1/2}dx/dt (km/s, the Gadget/2LPTic convention the
    paper plots, notes:347-350, 578-582) and dx/dt, the mesh fields (δ, χ, χ(z±), u, β, u_lower)
    and the metadata (σ8 targets, renormalisation factors). Command line writes an `.npz`.

`gramses_tests.py`: stages `expect`, `closed` (Fig. 1 analogue), `estimator`, `ics` (per box
and z_ini: T0, Figs. 2 and 3), `fig4`, `report`.

## 2. Formulas used, with sources

| quantity | formula | source |
|---|---|---|
| x | (k/ℋ)² | notes:554 |
| φ = ψ | −(3/2)Ω_m(a)δ^S/x | notes:558 |
| η (constant) | −(f + 3Ω_m/2)δ^S/x | notes:558 |
| δ^N | δ^S(1 + 3f/x) | notes:559 |
| δ^p | δ^N − 3φ = δ^S[1 + (3f + 9Ω_m/2)/x] = δ^S − 3η | notes:560, II:308 |
| P_pp/P_SS | [1 + (3f + 9Ω_m/2)ℋ²/k²]² | notes:561 |
| f_p | f/[1 + (3f + 9Ω_m/2)/x] | notes:562 |
| Hξ_0 | −3fφ/(x + 9Ω_m/2) | notes:563 |
| β_∥/u_∥ | −m²/(k² + m²) | notes:564 |
| θ_C^lower/θ_N | k²/(k² + m²) | notes:565-567 |
| Ψ_C | φ(x + 3f + 9Ω_m/2)/(x + 9Ω_m/2) | notes:568 |
| δ^C, Φ_C | δ^p k²/(k²+m²); −(3/2)Ω_m δ^C/(x + 9Ω_m/2) | notes:569-570, II:476 |
| FD velocity | dx/dt = (H/a)[χ(z−) − χ(z+)]/(2Δz) | notes:245, II:341 |
| two-step velocity | dx/dt = Hfχ_S | notes:253, II:333 |
| frozen-η spectra | δ^p(z±) = [D_1(z±)/D_1(z_ini)]δ^S(z_ini) − 3η(z_ini) | notes:261, II:372 |
| σ8 targets | II:378, II:384, II:388 | notes:270-272 |
| FD truncation | ΔP/P = 2Δz²/(1+z)² + O(Δz⁴) | notes:586-588 |
| plotted velocity | θ = ∇·(a^{1/2}dx/dt), P_θθ = aH²f²P_SS | notes:580-582 |
| FD growth rate | [√P(z−) − √P(z+)]/[2aΔz√P(z)] | notes:368, II:349 |
| shift solve | (Δ_Lβ)^i = 16πGρ̄a²(u^i + β^i), u_i = a²(u^i + β^i) | notes:285-293, II:322 |

## 3. Expectations, written before the tests were run

Seed 2001 for every realisation; 256³ particles in both boxes (4 h⁻¹Gpc: k_f = 1.571e-3,
k_Ny = 0.201 h/Mpc; 256 h⁻¹Mpc: k_f = 0.0245, k_Ny = 3.14 h/Mpc); z_ini = 99 and 49 (the notes list
no other redshift for Figs. 2-3; Fig. 1 adds z = 19). Bins of width k_f with edges at integer
multiples of k_f, as the paper's DTFE bins (first bin [k_f, 2k_f), centre 1.4165 k_f).

### 3.0 Closed forms (`gramses_ic.py --check`, `closed` stage)

All relations among the closed forms hold to rounding or to the O(ε²) error of the numerical
time derivatives (ε = 1e-4); limits: x → ∞ gives δ^p/δ^S, f_p/f, θ_C/θ_N, Ψ_C/φ, δ^C/δ^p → 1 and
β → 0; x → 0 gives δ^p → −3η, f_p → fx/(3f + 9Ω_m/2), θ ratio → k²/m², β → −u,
Ψ_C/φ = δ^C/δ^S → (3f + 9Ω_m/2)/(9Ω_m/2) (= 5/3 in matter domination); f_p = f/2 at
k = √(3f + 9Ω_m/2) ℋ = 3.580e-3 (z = 49), 5.063e-3 (z = 99). From the notes: f_p(z=49, k=3e-3) =
0.408, f_p(z=99, k=5e-3) = 0.484 (notes:395-396), P_pp/P_SS(0.002225) = 38.2 (z=99), 12.9 (z=49)
(notes:574), [k²/(k²+m²)]²(0.002225) = 0.0593, 0.153 (notes:472), ℋ/c and m/c of notes:19, 623.

### 3.1 Fig. 1 analogue (closed forms; no particles)

- f_S = f = 0.999999 (z=99), 0.999990 (z=49), 0.99985 (z=19) at all k. The paper's synchronous
  curves (with radiation) are 1.053/1.028 at k = 1e-4 and 0.9805/0.9903 at k ≥ 0.3 (z = 99/49):
  expect ours to be 5.3%/2.8% low on large scales and 2.0%/1.0% high on small scales. A
  Mészáros sub-horizon growth rate with photons and three massless neutrinos (a_eq = Ω_r/Ω_m,
  1 + z_eq = 3396) gives f = 0.98074 (z=99), 0.99028 (z=49): expected to match the paper's
  small-scale values to ~3e-4 if the small-scale deficit is radiation.
- f_p from the closed form: 0.0375, 0.1350, 0.2598, 0.4937, 0.7960, 0.9398, 0.9974 (z = 99) and
  0.0724, 0.2378, 0.4125, 0.6611, 0.8864, 0.9689, 0.9987 (z = 49) at k = 1e-3, 2e-3, 3e-3, 5e-3,
  1e-2, 2e-2, 0.1. The FD growth rate II:349 with Δz = 0.5 equals it to O((Δz/(1+z))²) ≲ 1e-4.
- P_pp(1e-4) = 4.707e5, 4.711e5, 4.722e5 (z = 99, 49, 19), i.e. 9P_η = 4.703e5 plus a 0.4%
  synchronous part at z = 19; paper 4.67e5, 4.68e5, 4.69e5 (our σ8 = 0.83 and n_s are the notes'
  inferences, so agreement at the few-% level is all that is expected).
- P_SS(0.1) = 0.957, 3.83, 23.9 (z = 99, 49, 19) against the paper's 0.958, 3.78, 23.2; on
  super-horizon scales ours is higher than the paper's (radiation suppresses the early
  synchronous growth): P_SS(1e-4) = 0.0716, 0.286, 1.79 against 0.0636, 0.268, 1.74.

### 3.2 T0 and the Fig. 3 subpanel: FD against two-step, Newtonian setting

With the same seed, χ(z±) = [D(z±)/D(z_ini)]χ(z_ini) mode by mode, so u_FD = c u_two-step per
particle with c = (1+z)[D(z−) − D(z+)]/(2Δz f D(z)); ΔP_N/P_N = c² − 1 in every bin, both boxes,
any estimator, to double-precision rounding:

| Δz | z=99: c²−1 | 2Δz²/(1+z)² | z=49: c²−1 | 2Δz²/(1+z)² | paper z=99 / z=49 |
|---|---|---|---|---|---|
| 1 | 2.0003e-4 | 2.0000e-4 | 8.0044e-4 | 8.0000e-4 | 2.0e-4 / 8.0e-4 |
| 0.5 | 5.0002e-5 | 5.0000e-5 | 2.0002e-4 | 2.0000e-4 | 5.0e-5 / 2.0e-4 |
| 0.25 | 1.2500e-5 | 1.2500e-5 | 4.9999e-5 | 5.0000e-5 | 1.1e-5 / 5.1e-5 |
| 0.05 | 5.0000e-7 | 5.0000e-7 | 1.9999e-6 | 2.0000e-6 | ~0 ± 2-5e-4 / ~0 ± 1e-4 |

(the differences between c² − 1 and the approximation are the O(Δz⁴) term and the deviation of
D from a). The default 2LPTic growth rate f = Ω_m(a)^0.6 differs from the exact one by
(f_0.6/f)² − 1 = −2.5e-7 (z=99), −2.0e-6 (z=49): invisible except at Δz = 0.05 and z = 49, where it
equals the truncation offset. Single precision (χ(z±) stored as float32): per-particle relative
error of the velocity ≈ 6e-8 (1+z)/(2Δz), i.e. 5.6e-5 (z=99) and 2.8e-5 (z=49) at Δz = 0.05 (and
proportionally less at larger Δz); in P_θθ this is a white-noise term whose relative size grows
towards high k, plus random scatter of order 1e-5-1e-4 per bin; the paper's Δz = 0.05 scatter
(±2-5e-4, ±1e-4) is expected to be of this origin (notes:468-469, [inferred]).
In the gramses setting u^i_C = u^i_N exactly (the η part of χ_p cancels in χ_p(z−) − χ_p(z+)),
so FD (CMC) against two-step (CMC) also gives c² − 1 (paper: "well below 0.1%").

### 3.3 Fig. 2 analogue (P_δδ of the ICs)

Same-seed ratio P^CMC/P^S per bin equals the mode average of the closed-form ratio over the
realised modes (the mesh-field ratio). Ensemble mode averages (and closed form at the bin centre):

| box, z | bin [j, j+1)k_f | ensemble | centre | paper measured / paper linear at centre |
|---|---|---|---|---|
| 4 Gpc, 99 | 1, 2, 3, 6 | 47.16, 8.141, 3.643, 1.566 | 38.18, 7.862, 3.578, 1.563 | 46.7/41.4, 8.89/7.85, 4.07/3.67, 1.69/1.58 |
| 4 Gpc, 49 | 1, 2, 3, 6 | 15.26, 3.700, 2.112, 1.267 | 12.88, 3.617, 2.090, 1.266 | 13.7/13.3, 3.57/3.53, 2.17/2.10, 1.29/1.27 |
| 256 Mpc, 99 | 1, 2, 4 | 1.0522, 1.0155, 1.0044 | 1.0429, 1.0148, 1.0043 | 1.049/1.043, 1.016/1.014, 1.005/1.004 |
| 256 Mpc, 49 | 1, 2, 4 | 1.0259, 1.0077, 1.0022 | 1.0213, 1.0074, 1.0022 | 1.024/1.021, 1.007/1.007, 1.0025/1.002 |

The first bin holds 26 modes (13 independent amplitudes), so the realised ratio depends on the
seed: 16-84% range over realisations 38.3-56.9 (4 Gpc, z=99), 12.8-18.0 (z=49), 1.045-1.058
(256 Mpc, z=99), 1.0226-1.0290 (z=49). The paper's own linear curves are 8% (z=99) and 3% (z=49)
above our closed form at the first bin centre (radiation, notes:574-576); this is smaller than the
realisation spread, so the first-bin comparison with the paper can only be at the ±20% level in
the 4 Gpc box, and at the 0.5% level in the 256 Mpc box. In the last bins the ratio is 1.0013
(4 Gpc, z=99), 1.0006 (z=49), 1.00001 (256 Mpc).

Estimator (Eulerian deposit, `estimator` stage): for particles on a lattice the B-spline
deconvolution is not the right correction, because the cloud is sampled at fixed offsets from
the lattice sites. At first order in the displacement the deposited density is
δ_dep(k) = −Σ_i χ_i(k) S′(k_i) Π_{j≠i} S(k_j), with S(k) = Σ_d W(d)e^{−ikhd} the kernel sampled
at the lattice offsets d and S′ its derivative sum; the deposited momentum is Π_j S(k_j)u(k).
Predicted (deconvolved deposit)/(mesh field) at k_Ny/2 and k_Ny, flat mode weights:

| cloud, mesh | density k_Ny/2 | density k_Ny | velocity k_Ny/2 | velocity k_Ny | 1% reached at k/k_Ny (dens., vel.) |
|---|---|---|---|---|---|
| TSC, n³ | 0.861 | 0.454 | 1.036 | 1.98 | 0.17, 0.39 |
| TSC, (2n)³ | 1.067 | 1.267 | 0.998 | 0.968 | 0.20, 0.77 |
| PCS, n³ | 0.976 | 0.623 | 1.018 | 1.84 | 0.42, 0.48 |
| PCS, (2n)³ | 1.0012 | 1.018 | 0.9993 | 0.987 | 0.89, 0.95 |

CIC on the n³ mesh is not differentiable at the lattice sites (no linear response). Expected
choice: PCS on (2n)³, reliable to 1% up to ~0.9 k_Ny at linear order; at the actual amplitude the
Zel'dovich particle density has second-order terms the linear mesh field lacks (largest in the
256 Mpc box at z = 49, where the rms displacement is the largest fraction of the lattice
spacing), expected to add a few per cent near k_Ny there and to be negligible in the 4 Gpc box.
Absolute spectra: the mesh-field spectra scatter around the ensemble linear spectra with the
sample variance of each bin (reduced χ² ~ 1).

### 3.4 Fig. 3 analogue (P_θθ of the ICs)

- FD (N) against two-step (N): the T0 table above, in every bin.
- Lower-index CMC divergence: exact per mode θ_C^lower/θ_N = k²/(k²+m²) (Lagrangian estimator);
  per bin the realised mode average of [k²/(k²+m²)]². First 4 Gpc bin, ensemble: 0.0693 (z=99),
  0.169 (z=49), 16-84% over realisations 0.061-0.077 and 0.152-0.185; at the bin centre 0.0593,
  0.153. Paper: 0.0754, 0.191 measured, 0.0611, 0.155 its linear curves at the centre. 256 Mpc
  first bin: 0.970 (z=99), 0.985 (z=49).
- Mean of (lower/N − 1) over our bins with k > 0.01: −1.50% (z=99), −0.78% (z=49) in the 4 Gpc
  box (k ≤ 0.2); over the paper's bins to k = 0.804 the closed form gives −0.37% and −0.19%,
  against the paper's −0.5% and −0.3%.
- Eulerian estimator for θ: response 0.9993 at k_Ny/2 and 0.987 at k_Ny (PCS, (2n)³); no
  resolution deficit comparable to the paper's DTFE one (0.92 at k = 0.2, 0.20 at k_Ny in the
  4 Gpc box) is expected, because the DTFE deficit is a property of that estimator.

### 3.5 Fig. 4 analogue (σ8 at z_ini ± Δz; 4 Gpc, z = 49, Δz = 0.5)

ΔP_θθ/P^N_θθ against the two-step reference, ensemble mode averages at the first three bins
(k = 0.00222, 0.00377, 0.00536) and the mean over k > 0.05:

| variant | prediction | paper |
|---|---|---|
| FD (N), σ8 corrected (II:378) | +2.0e-4 everywhere (truncation) | (Fig. 3 circles) |
| FD (CMC), σ8 corrected (II:384, 388) | +2.0e-4 everywhere | — |
| FD (CMC), no renormalisation | +2.0e-4 everywhere (σ8 targets are the spectra's own) | — |
| FD (CMC), σ^p_8 ∝ D_1 (II:384 skipped) | +1.59%, +0.82%, +0.63%; +0.44% | — |
| FD (N), σ8(z±) from radiation growth (Mészáros model of "def σ8") | −1.91% everywhere | −1.92% (cyan) |
| FD (CMC), same model with II:384 | −7.05%, −3.66%, −2.77%; −1.91% | −8.0%, −4.3%, −3.1%; −1.9% (red) |

The last two rows are a model, not a reproduction: in the paper the σ8 values that CAMB reports at
z± carry the radiation-era growth; here a Mészáros growth factor plays that role. The CMC curve
grows at large scales as (1+G(k)), G = −3η/δ^S, because the misnormalised part of χ_p(z±)
includes the η term, which does not cancel in the difference. The "σ^p_8 ∝ D_1" row is the only
σ8 effect that exists without radiation; it depends on the lower limit of the σ8 integral
(1e-6 h/Mpc here), because P_pp ∝ k^{n_s−4} makes Δ²_pp ∝ k^{n_s−1} at small k.
Positions (P_δδ, the paper's left panel) are identical for all FD variants of a setting
(ΔP_δδ = 0 exactly), and back-scaling the z = 0 spectrum with D_1 is an identity here.

## 4. Results

Runs: `gramses_tests.py expect`, `closed`, `estimator --n 128`, `ics --L {4000,256} --z {99,49}
--n 256`, `fig4 --n 256`, `t0prec --n 256`, `report --n 256` (about 35 min on 4 processes).
Every number below is in `cosmo/analysis/gramses_tests.json`.

### 4.0 Closed forms — all 20 implementation checks pass

Largest deviations over 1e-5 < k < 10 h/Mpc and z = 99, 49, 19, 0: η constant 3.6e-12;
δ^p = δ^N − 3φ 1.4e-16; f_p against a numerical d ln δ^p/d ln a 1.7e-9; conjugacy 1.1e-16;
Newtonian continuity (II:232) 5.2e-12; CMC continuity (II:288) 2.6e-7 (the O(ε²) error of the
numerical derivative); Ψ_C by three routes 4.2e-16; δ^C by two routes and the CMC Hamiltonian
constraint 1.0e-11 (cancellation of 1/x terms at the smallest k); Φ_C from the gauge
transformation II:126 against the lapse equation II:476 4.4e-7; β from II:127 against
−m²/(k²+m²)u 3.3e-16; δK = 0 in CMC 1.2e-9; φ̇ = H(f−1)φ 1.5e-9. Limits: 7.5e-8 at x = 1e8 (the
leading correction 7.5/x), 2.7e-9 at x = 1e-8; f_p = f/2 exactly at k = √(3f + 9Ω_m/2) ℋ;
3f + 9Ω_m/2 = 7.5 in matter domination. Values in the notes: P_pp/P_SS(0.002225) = 38.17, 12.88;
[k²/(k²+m²)]² = 0.0593, 0.1534; ℋ/c and m/c of notes:19, 623 all reproduced.

**Failed expectation 1.** f_p(z=49, k=3e-3) = 0.4125 and f_p(z=99, k=5e-3) = 0.4937, not the
0.408 and 0.484 of notes:395-396. Cause, found before anything was changed: those two numbers
are the paper's Fig. 1 readings, which include radiation. The closed form (the notes' own
formula, with the notes' own ℋ of notes:19) gives 0.4125 and 0.4937. The ratio paper/closed form
across the f_CMC table is 0.990 (z=49) and 0.980 (z=99) for k ≥ 5e-3, i.e. the paper's own
small-scale synchronous growth rate f_rad, and falls further on horizon scales (0.980 and 0.956 at
k = 1e-3), where radiation also changes ℋ and m². The statement of notes:572 ("f_p matches to
±0.001 at the two points checked") holds only after multiplying by f_rad. The formula was not
changed.

### 4.1 Fig. 1 analogue — `figs/gramses_fig1_growth.png`

- Closed-form f_p at the paper's k agrees with the paper's curves only up to the radiation factors
  above (lower-right strip of the figure). f_S = f = 0.999999, 0.999990, 0.99985 against the
  paper's 0.9805 / 0.9903 (small scales) and 1.053 / 1.028 (k = 1e-4). The Mészáros growth rates
  0.98074 (z=99) and 0.99028 (z=49) match the paper's small-scale values (0.9805, 0.9903) to 3e-4,
  as expected if the deficit is radiation.
- FD growth rate II:349 with Δz = 0.5 against the closed form: 2.5e-5 (z=99), 1.0e-4 (z=49),
  6.3e-4 (z=19), i.e. (Δz/(1+z))², as expected.
- P_pp(1e-4) = 4.707e5, 4.711e5, 4.722e5 (z = 99, 49, 19) against 4.67e5, 4.68e5, 4.69e5: our
  values are 0.7-0.8% high and rise by 0.3% from z = 99 to 19, as in the paper (+0.4%).
- P_SS: 0.957, 3.83, 23.9 at k = 0.1 against 0.958, 3.78, 23.2 (paper/ours = 1.002, 0.988, 0.970);
  at k = 1e-4 0.0716, 0.286, 1.79 against 0.0636, 0.268, 1.74 (paper/ours = 0.89, 0.94, 0.97:
  radiation slows the early super-horizon synchronous growth). P_pp: paper/ours = 0.98-1.05 at
  all eight k and all three z (it follows P_S on small scales; on horizon scales it differs by
  the radiation in η and ℋ).

### 4.2 T0: finite difference against two-step, Newtonian setting — `figs/gramses_t0_fd.png`

- In every bin, in both boxes, at both z_ini and for all four Δz, the double-precision
  ΔP_N/P_N equals the exact c² − 1 to ≤ 3.5e-13 (Lagrangian estimator), and to ≤ 3.8e-14 with the
  Eulerian deposit at Δz/z_ini ≈ 1%. Per particle |u_FD − c u_two-step|/max|u| ≤ 7.5e-13.
- Means over k (identical in both boxes): z = 99: 2.0003e-4, 5.0002e-5, 1.2500e-5, 5.0000e-7;
  z = 49: 8.0044e-4, 2.0002e-4, 4.9999e-5, 1.9999e-6 for Δz = 1, 0.5, 0.25, 0.05. Quadratic in
  Δz/(1+z), on the line 2(Δz)²/(1+z)² (right panel), as are the paper's values.
- GRAMSES setting: FD u^i_C against two-step (CMC) also gives c² − 1 to ≤ 1.7e-12. The paper's
  "well below 0.1%" (II:334) is reproduced: the difference is only the truncation term, 2.0e-4 at
  Δz/z_ini ≈ 1%. u^i_C = u^i_N per particle to 7.5e-13.
- **Failed expectation 2.** Storing χ(z±) in float32 does not produce a scatter of 1e-5-1e-4.
  The rms over bins is 1.6e-7 (z=99) and 7.4e-8 (z=49) at Δz = 0.05 (max 6.5e-7), 1000 times
  below the paper's ±2-5e-4 and ±1e-4. My per-bin estimate ignored the averaging over the modes
  of a bin. Investigation (stage `t0prec`, bottom strip of the figure), at Δz = 0.05:
  - a float32 pipeline (field, FFTs and difference in single precision) gives rms 1.3e-5
    (z=99) and 3.9e-6 (z=49), max 1.3e-4 and 2.8e-5: still 10-30 times too small. It would
    shrink further at the paper's 1024³, because the round-off of a white field is spread over
    more modes.
  - double precision, with P(k; z±) read from tables printed with 7 significant digits (CAMB's
    E15.6 format) and interpolated in (ln k, ln P) like 2LPTic (the reference velocity also
    from a table, so that the interpolation error cancels as it does for the paper's default
    run): rms 1.3e-4 (max 6.3e-4) at z = 99 and 5.3e-5 (max 1.6e-4) at z = 49; at Δz = 0.25:
    2.2e-5 (max 9.4e-5) and 1.4e-5. The paper reads ±2-5e-4, ±1e-4 and ±5e-5.
  These rounding errors depend only on |k|, so the modes of a bin do not average them down, and
  they are amplified by (1+z)/(2Δz). They reproduce the size, the 1/Δz scaling and the
  independence of box and particle number of the paper's scatter. The notes' attribution to
  single-precision round-off in χ (notes:468-469) should read "rounding of the tabulated input
  spectra" (still [inferred]: CAMB's output precision and 2LPTic's table handling are not
  stated).
- The 2LPTic default growth rate Ω_m(a)^0.6 instead of the exact f would shift the reference by
  −2.5e-7 (z=99) and −2.0e-6 (z=49); this is negligible except against the Δz = 0.05 truncation
  offset.

### 4.3 Fig. 2 analogue: P_δδ of the ICs — `figs/gramses_fig2_pdd.png`

Estimator (`figs/gramses_estimator.png`, 128³, `estimator` stage): the predicted lattice
response reproduces the 1e-4-amplitude deposits in all six configurations (CIC, TSC, PCS on n³
and (2n)³) to the fourth digit, e.g. TSC on n³: 0.8649 at k_Ny/2 and 0.4446 at k_Ny, both
predicted and measured. Chosen: PCS on (2n)³ = 512³ with the PCS window divided out, momentum
deposit per mean density for velocities. The Eulerian results use this estimator; the
Lagrangian ones are the particles on their lattice.

| quantity | 4 Gpc z=99 | 4 Gpc z=49 | 256 Mpc z=99 | 256 Mpc z=49 |
|---|---|---|---|---|
| first-bin P^CMC/P^S, ICs (deposit) | 52.919 | 16.915 | 1.05533 | 1.02745 |
| same, linear on the realised modes | 52.918 | 16.914 | 1.05533 | 1.02745 |
| same, ensemble linear (expected) | 47.16 | 15.26 | 1.0522 | 1.0259 |
| 16-84% over realisations (expected) | 38.3-56.9 | 12.8-18.0 | 1.045-1.058 | 1.0226-1.0290 |
| paper (measured / linear at centre) | 46.7 / 41.4 | 13.7 / 13.3 | 1.049 / 1.043 | 1.024 / 1.021 |
| bins 2, 3 (4 Gpc: 3, 4; 6), ours | 7.668, 3.638, 1.567 | 3.542, 2.110, 1.268 | 1.0148, 1.0044 | 1.0074, 1.0022 |
| same, paper | 8.89, 4.07, 1.69 | 3.57, 2.17, 1.29 | 1.016, 1.005 | 1.007, 1.0025 |
| max over bins of abs(meas/realised − 1) | 1.1e-4 | 1.1e-4 | 1.2e-4 | 1.0e-4 |
| mean ratio, last quarter of bins | 1.0017 | 1.0008 | 0.99995 | 0.99996 |
| deposit/mesh at k_Ny/2, last bin | 1.0011, 1.0188 | 1.0010, 1.0188 | 1.0013, 1.0163 | 1.0028, 1.0145 |
| predicted lattice response | 1.0011, 1.0188 | 1.0011, 1.0188 | 1.0011, 1.0188 | 1.0011, 1.0188 |
| 1% reached at k/k_Ny (k in h/Mpc) | 0.86 (0.17) | 0.86 (0.17) | 0.89 (2.8) | 0.74 (2.3) |
| χ² per bin, mesh field vs linear | 1.016 | 1.016 | 1.014 | 1.014 |
| rms χ / lattice spacing | 0.008 | 0.016 | 0.115 | 0.230 |

- The same-seed ratio equals the linear ratio on the realised modes to ≤ 1.2e-4 in every bin
  (expected ≲ 1%), and tends to 1 at high k. Our first-bin values lie inside the expected
  realisation ranges, and so do the paper's. The differences from the paper's numbers (+13%
  and +23% in the first 4 Gpc bin, +0.6% and +0.3% in the 256 Mpc box) are realisation, plus
  the 8%/3% radiation term in the 4 Gpc box. In the 256 Mpc box the second and fourth bins
  agree with the paper to 0.1%.
- The estimator is reliable to 1% up to 0.86 k_Ny in the 4 Gpc box, where it is exactly the
  linear lattice response. In the 256 Mpc box second-order Zel'dovich terms take over
  (deposit/mesh at k_Ny/2 = 1.0013 at z = 99 and 1.0028 at z = 49 against the response 1.0011),
  and the 1% point moves to 0.89 and 0.74 k_Ny. This matches the expectation "a few per cent near
  k_Ny, largest in the 256 Mpc box at z = 49". The mesh-field spectra scatter around the
  ensemble linear spectra with χ² ≈ 1 per bin.

### 4.4 Fig. 3 analogue: P_θθ of the ICs — `figs/gramses_fig3_ptt.png`

| quantity | 4 Gpc z=99 | 4 Gpc z=49 | 256 Mpc z=99 | 256 Mpc z=49 |
|---|---|---|---|---|
| first-bin (a^{-2}∂_iu^C_i)/(∂_iu^i_N), deposit | 0.06124 | 0.15320 | 0.96842 | 0.98409 |
| same, Lagrangian = realised expectation | 0.06124 | 0.15321 | 0.96842 | 0.98409 |
| ensemble expectation; 16-84% | 0.0693; 0.061-0.077 | 0.169; 0.152-0.185 | 0.970 | 0.985 |
| paper (triangles/stars; its linear curves) | 0.0754 (0.0611) | 0.191 (0.155) | — | — |
| mean (lower/N − 1), k > 0.01: deposit / expected | −1.483% / −1.483% | −0.763% / −0.762% | −0.042% / −0.025% | −0.037% / −0.003% |
| velocity deposit/Lagrangian at k_Ny/2, last | 0.9993, 0.9869 | 0.9993, 0.9879 | 1.013, 1.048 | 1.056, 1.213 |
| 1% reached at k/k_Ny (k in h/Mpc) | 0.95 (0.19) | 0.96 (0.19) | 0.39 (1.24) | 0.17 (0.53) |

- FD (N) against two-step (N): the T0 numbers, in every bin of the subpanels.
- The lower-index divergence follows k²/(k²+m²) mode by mode to 3e-11 (Lagrangian); per bin it
  equals the realised mode average of [k²/(k²+m²)]² to 1e-13 (Lagrangian) and 3e-4 (deposit,
  k < k_Ny/2; the deposit means in the table include the second-order terms of §4.4 below,
  whereas the Lagrangian means equal the expected ones to 1e-13). The paper's first-bin values
  are at the upper end of, or just above, our
  realisation ranges; its linear curves are 3% (z=99) and 1% (z=49) above our closed form there
  (radiation). The mean deficit for k > 0.01 depends on the k range. Over the paper's bins to
  k = 0.804 the closed form gives −0.37% and −0.19%, against its −0.5% and −0.3%; ours to
  k = 0.2 are −1.48% and −0.76%, as computed beforehand.
- Absolute velocity amplitude: k^{1.5}P_θθ(0.1) = 9.29e5 at both z_ini (independent of z in
  matter domination, as in the paper) against 8.9e5 on the paper's linear curve. That is −4%:
  f_rad² = 0.981 and the paper's 1.2% lower P_SS at z = 49.
- **Failed expectation 3.** I expected the velocity deposit to follow the linear lattice response
  (0.9993 at k_Ny/2, 0.987 at k_Ny). It does in the 4 Gpc box. In the 256 Mpc box it lies above
  linear theory beyond 0.39 k_Ny (z=99) and 0.17 k_Ny = 0.53 h/Mpc (z=49), by 5.6% at k_Ny/2 for
  z = 49. Cause: the excess at k_Ny/2 is 1.3% at z = 99 and 5.6% at z = 49, a ratio of 4.2 ≈
  (D_49/D_99)² = 4, so it is second order in the amplitude, not a window effect. It is the
  difference between the Eulerian momentum field (1+δ)u(q(x)) and the linear Lagrangian field.
  At 128³ the mass-weighted velocity (momentum/mass) deviates by a similar amount with the
  opposite sign (`gramses_estimator.png`, lower right). The particle velocities themselves are
  exact (Lagrangian estimator). In the 256 Mpc box at z = 49 the Eulerian P_θθ is therefore
  usable only below ~0.5 h/Mpc. The paper's DTFE deficit near its Nyquist frequency is a
  different, estimator-specific effect and is not reproduced, as expected.

### 4.5 Fig. 4 analogue: σ8 at z_ini ± Δz — `figs/gramses_fig4_sigma8.png`

4 Gpc, z_ini = 49, Δz = 0.5; ΔP_θθ/P^N_θθ against the two-step reference at k = 0.00222,
0.00377, 0.00536 and the mean for k > 0.05. In every bin the measured value equals the
prediction of §3.5 (evaluated on the realised modes) to ≤ 5e-14.

| variant | ours | paper |
|---|---|---|
| FD (N), σ8 corrected (II:378) | +2.0002e-4 (all bins) | (Fig. 3) |
| FD (CMC), σ8 corrected (II:384, 388) | +2.0002e-4 | — |
| FD (CMC), no renormalisation | +2.0002e-4 | — |
| FD (CMC), σ^p_8 ∝ D_1 (II:384 skipped) | +1.68%, +0.81%, +0.63%; +0.44% | — |
| FD (N), "def σ8" Mészáros model | −1.913% (all bins) | −1.92% (cyan) |
| FD (CMC), "def σ8" Mészáros model | −7.45%, −3.58%, −2.77%; −1.91% | −8.0%, −4.3%, −3.1%; −1.9% (red) |
| FD inc η̇ (N), (CMC); back-scaled | not made (need radiation) | +5.5/+3.6/+2.1%, ...; see §6 |

- The σ8 renormalisation factors for the corrected cases are 1 to 2e-16, i.e. II:378/384/388
  with σ^{Sη}_8 from II:388 (−2.4003e-7, equal to the directly integrated cross term to 13
  digits) are exactly consistent with the frozen-η spectra. Without radiation the correction is
  needed only for the CMC spectrum, and only because δ^p does not grow like D_1 (the
  "σ^p_8 ∝ D_1" row, +0.4-1.7%). That row depends on the lower limit of the σ8 integral
  (1e-6 h/Mpc), because Δ²_pp ∝ k^{n_s−1} at small k.
- The model of the paper's uncorrected curves gives the cyan plateau to 0.01 percentage points.
  It gives the red curve's shape (1 + G(k), G = −3η/δ^S) and plateau, with amplitudes 7-17% of
  the deviation smaller than the paper's at the first bins. The paper's G is larger by
  radiation (P_pp/P_SS 3% larger at z = 49), and its first-bin weights belong to another
  realisation.
- Positions: ΔP_δδ = 0 exactly between all FD variants of a setting. Back-scaling with D_1 is an
  identity here (max |δ_b − δ|/max|δ| = 4e-16; ΔP_δδ = 6e-16).

## 5. Our numbers against the numbers read from the paper's figures (notes §4)

| figure, quantity | paper (notes) | ours | agree? / cause of difference |
|---|---|---|---|
| Fig. 1 f_S, k ≥ 0.3, z = 99 / 49 | 0.9805 / 0.9903 | 1.0000 / 1.0000 | no: radiation (Mészáros 0.9807 / 0.9903) |
| Fig. 1 f_S, k = 1e-4, z = 99 / 49 | 1.053 / 1.028 | 1.0000 / 1.0000 | no: super-horizon radiation, not modelled |
| Fig. 1 f_CMC, k = 3e-3 (z=49) / 5e-3 (z=99) | 0.408 / 0.484 | 0.4125 / 0.4937 | 1-2%: radiation (paper/ours = f_rad) |
| Fig. 1 f_CMC = 0.5 at k, z = 49 / 99 | 3.6e-3 / 5.1e-3 | 3.58e-3 / 5.06e-3 | yes |
| Fig. 1 P_CMC(1e-4), z = 99 / 49 / 19 | 4.67e5 / 4.68e5 / 4.69e5 | 4.707e5 / 4.711e5 / 4.722e5 | yes (0.8%; σ8, n_s inferred) |
| Fig. 1 P_S(0.1), z = 99 / 49 / 19 | 0.958 / 3.78 / 23.2 | 0.957 / 3.83 / 23.9 | yes to 0.1-3% (radiation growth, σ8) |
| Fig. 1 P_S(1e-4), z = 99 / 49 / 19 | 0.0636 / 0.268 / 1.74 | 0.0716 / 0.286 / 1.79 | no: 11/6/3% (radiation) |
| Fig. 2 first-bin ratio, 4 Gpc z = 99 / 49 | 46.7 / 13.7 | 52.9 / 16.9 | within realisation range (38-57 / 13-18) |
| Fig. 2 first-bin ratio, 256 Mpc z = 99 / 49 | 1.049 / 1.024 | 1.0553 / 1.0275 | within realisation range |
| Fig. 2 bins 2 and 4, 256 Mpc z = 99 | 1.016, 1.005 | 1.0148, 1.0044 | yes (0.1%) |
| Fig. 2 bins 2 and 4, 256 Mpc z = 49 | 1.007, 1.0025 | 1.0074, 1.0022 | yes |
| Fig. 2 bins 2, 3, 6, 4 Gpc z = 99 | 8.89, 4.07, 1.69 | 7.67, 3.64, 1.57 | 7-14%: radiation + realisation |
| Fig. 2 bins 2, 3, 6, 4 Gpc z = 49 | 3.57, 2.17, 1.29 | 3.54, 2.11, 1.27 | yes to 3% |
| Fig. 2 ratio at high k | → 1 | 1.0017 (4 Gpc, last quarter), 1.0000 | yes |
| Fig. 3 ΔP_N/P_N, z = 99, Δz = 1 / 0.5 / 0.25 | 2.0e-4 / 5.0e-5 / 1.1e-5 | 2.0003e-4 / 5.0002e-5 / 1.2500e-5 | yes |
| Fig. 3 ΔP_N/P_N, z = 49, Δz = 1 / 0.5 / 0.25 | 8.0e-4 / 2.0e-4 / 5.1e-5 | 8.0044e-4 / 2.0002e-4 / 4.9999e-5 | yes |
| Fig. 3 Δz = 0.05: mean; scatter z = 99 / 49 | ~0; ±2-5e-4 / ±1e-4 | 5e-7, 2e-6 exact; tables-7-digit model 1.3e-4 (max 6.3e-4) / 5.3e-5 (max 1.6e-4) | yes (scatter via the table-rounding model) |
| Fig. 3 T0: two-step vs FD (CMC) | "well below 0.1%" | c² − 1 = 2.0e-4 at 1%, to 1e-12 | yes |
| Fig. 3 lower/N first bin, 4 Gpc z = 99 / 49 | 0.0754 / 0.191 | 0.0612 / 0.1532 | within / just above our realisation range; radiation +3%/+1% |
| Fig. 3 lower/N mean k > 0.01 (4 Gpc) | −0.5% / −0.3% | closed form over the paper's bins −0.37% / −0.19% | yes to its reading precision |
| Fig. 3 linear k^1.5 P_θθ(0.1), z = 49 | 8.9e5 | 9.29e5 | 4%: f_rad², P_S |
| Fig. 4 FD def σ8 (N) | −1.92% | −1.913% (model) | yes (model, not reproduction) |
| Fig. 4 FD def σ8 (CMC), bins 1-3; plateau | −8.0, −4.3, −3.1%; −1.9% | −7.45, −3.58, −2.77%; −1.91% (model) | shape and plateau yes; first bins 7-17% smaller |
| Fig. 4 FD inc η̇ (N), (CMC) | +5.5 ... 0% / +3.7 ... 0% | not made | needs radiation |
| Fig. 4 back-scaled P_δδ, P_θθ | −1.9% ... −2.5%; +1.6 ... −1.85% | 0 (identity) | needs radiation and baryons |
| Fig. 4 ΔP^S/P^S of FD variants | 0 | 0 exactly | yes |

## 6. What could not be reproduced, and why

- **Everything that depends on radiation.** There is no Boltzmann code and no network, so the
  synchronous-gauge spectra are Eisenstein-Hu × the matter + Λ growth factor, and η is exactly
  constant. Not reproducible:
  - Fig. 1, synchronous growth rate: the paper's large-scale boost (+5.3% at z = 99, +2.8% at
    z = 49, k = 1e-4) and small-scale deficit (f = 0.9805, 0.9903). Ours is f = 1.0000 at all k.
    The small-scale deficit is the Mészáros growth rate of CDM with smooth radiation
    (0.98074, 0.99028; agreement with the paper to 3e-4), which supports the radiation explanation
    but is a model, not a reproduction. The large-scale boost needs the super-horizon radiation
    transfer of a Boltzmann code.
  - Fig. 1, CMC growth rate: our closed form is 1-4.4% above the paper's curves (largest on horizon
    scales at z = 99), the sum of the small-scale radiation deficit and of radiation in ℋ and m².
  - Fig. 2 and Fig. 3 linear curves on horizon scales: the paper's Boltzmann ratios P_pp/P_SS are
    8% (z = 99) and 3% (z = 49) above the closed form at k = 0.002225; [k²/(k²+m²)]² is 3% and 1%
    below its curves. Our comparisons are with our own closed forms; the paper's numbers are quoted
    for reference.
  - Fig. 4, the "radiation fix" (II:372 against CAMB's z± spectra): the curves "FD inc η̇ (S/N)"
    (magenta) and "FD inc η̇ (CMC)" (green) need CAMB spectra at z± with radiation-driven η̇ and
    growth; without radiation η̇ = 0 and these variants coincide with the corrected ones.
  - Fig. 4, back-scaling ("2LPTic inc D_1", orange; −1.9% in P_δδ, up to −2.5%): here the z = 0
    spectrum scaled back with D_1 is the z_ini spectrum to rounding, because no radiation or baryon
    growth enters between z_ini and 0. Measured: max |δ_b − δ|/max|δ| ~ 4e-16.
  - Fig. 4, "FD def σ8" (cyan, red): the paper's −1.92% exists only because CAMB's σ8(z±) carry the
    radiation-era growth. It is modelled here with a Mészáros growth factor in II:378/384, not
    reproduced.
- **DTFE and POWMES.** The paper's estimators are not available. The DTFE high-k excess in P_δδ
  (×1.29-×5.1, notes:430-432) and deficit in P_θθ (0.92 → 0.20 at k_Ny, notes:475-477) are
  properties of those estimators and are not reproduced (as the notes advise, notes:441-442,
  485-486). We use mesh deposits with deconvolution, whose behaviour on lattice ICs is
  quantified in §4 and in `gramses_estimator.png`.
- **1024³ particles.** We use 256³: the same k_f, hence the same large-scale bins (where all
  gauge effects are), but k_Ny four times lower (0.201 and 3.14 h/Mpc instead of 0.804 and 12.57).
  The paper's statements near its Nyquist frequency (resolution deficit, POWMES near k_Ny) are
  therefore not tested.
- **The seed.** The paper's seed is not given (notes:320-321), so its realised first-bin modes
  cannot be matched. In the 4 h⁻¹Gpc box the first-bin ratios depend on the realisation by ±20%.
- **GRAMSES's own shift solve.** Our lower-index velocity comes from the physical form of the
  §3.7 equation, solved spectrally on the IC mesh at the lattice sites. The code-unit coefficients
  of II:326 could not be reconciled with Part I's unit table (notes:293-294). GRAMSES solves on its
  own AMR grid from deposited particles; the difference is second order or in the deposit window.

## 7. What a hyperbolic code with our gauge needs in order to start from these ICs

Our gauge: zero shift, ∂_tα = −(1/3)α²K. For a homogeneous universe K = −3(d ln a/dt)/α, so
α ∝ a and t is conformal time. Linearised about α = a(1 + ψ) with K = −(3/a)[ℋ(1 − ψ) − φ′]
(Newtonian-gauge form, prime = d/dτ), the condition gives ψ′ = −φ′. The Newtonian slicing
(ψ = φ without anisotropic stress) is therefore reproduced while φ′ = 0. That holds exactly for the
growing mode in matter domination. With Λ, φ′ = ℋ(f − 1)φ, and the slicing drifts from Newtonian by
δψ = −2∫φ′dτ: relatively 1 − f < 1.5e-4 for z ≥ 19, but O(φ) by z ~ 0. With zero shift and the
shear-free (Newtonian) slicing, the traceless scalar part of the metric does not grow, so h_ij = 0
and the threading is the Newtonian one. At first order this is the minimal-distortion threading of
GRAMSES (ξ_i = 0, notes:192-196). From notes §7b:

1. **Particle positions**: the particle-number contrast of the MD (= Newtonian) threading,
   δ^p = δ^N − 3φ = δ^S − 3η (notes:204-209), i.e. the `setting="gramses"` positions of
   `gramses_ic.py`. These are not the `newtonian` (δ^S) positions of a Newtonian N-body code. δ^p
   depends only on the threading (notes:204-208), so the CMC-MD and the Newtonian-gauge positions
   are the same particles.
2. **Particle velocities**: the coordinate velocity u^i = dx^i/dt is threading-only as well, so
   u^i_N = u^i_C, which is the FD velocity (or the two-step Hfχ_S) of the generator; in the code's
   conformal time dx^i/dτ = a dx^i/dt. The covariant variable the code evolves (the same u_i as
   GRAMSES, notes:684) is, with zero shift and non-relativistic particles, u_i = γ_ij u^j with
   u^j = u^0 dx^j/dt: at first order (φ times a velocity is second order) u_i = a² dx^i/dt =
   a² u^i, or a dx^i/dτ with the code's conformal time τ. The §3.7 shift correction must
   **not** be applied. GRAMSES's
   u_i^C = a²(u^i + β^i) = u_i^N − ∂_iξ_0 belongs to the CMC slicing and differs from ours by the
   factor k²/(k²+m²) (0.14 at z = 99 and 0.24 at z = 49 for k = k_f of the 4 h⁻¹Gpc box).
3. **Energy density**: the code forms E from the deposited particles and √γ. With
   γ_ij = a²(1 − 2φ)δ_ij this is automatically δ^N = δ^p + 3φ; no separate density variable is
   needed. The Newtonian-gauge density is not conjugate to u^i (notes:222), which is why the
   particles must carry δ^p and the metric φ.
4. **Metric data at z_ini**: γ̃_ij = δ_ij, Γ̃^i = 0, Θ = 0, β^i = 0;
   conformal factor ψ_c⁴ = a²(1 − 2φ) with −k²φ = (3/2)Ω_m(a)ℋ²δ^S (Poisson with the comoving
   density; equivalently φ = −(3/2)Ω_m δ^S/x); lapse α = a(1 + φ); K = −3H(1 − fφ) (δK_N = 3Hψ +
   3φ̇ = 3Hfφ); Ã_ij = 0 at first order. The momentum constraint is then satisfied by ∂_iK alone:
   −(2/3)∂_iδK = −2Hf∂_iφ = 8πGρ̄a²u^i. To satisfy the constraints exactly on the code's mesh with
   its own deposit (CIC/TSC, filter), the Hamiltonian and momentum constraints should be re-solved
   with `cosmo_id.solve` for the given K(x), keeping the particles fixed. This gives ψ_c and Ã_ij,
   with Ã_ij of second order. The alternative of notes 7b.2 (CMC-MD data, K = −3H) is the GRAMSES
   gauge, not ours. Started with our lapse condition it would not stay CMC, and the comparison
   would need the gauge map of notes 7b.1.
5. **Comparison curves**: in our gauge the linear spectra are those of δ^p for positions (= GRAMSES's
   Fig. 2 blue curves) and of θ^N = ∂_iu^i (Fig. 3 black curve; the CMC lower-index curve does not
   apply). The energy density follows δ^N = δ^S(1 + 3f/x). For z ≲ 1, where our slicing departs
   from Newtonian, use the gauge-robust map of notes 7b.1 (δ^p and u^i from the threading, δ and u_i
   from K).
6. **Radiation**: the code has none. Start from radiation-free spectra (η frozen, matter + Λ D_1, as
   here) or expect the Fig. 4 offsets.
