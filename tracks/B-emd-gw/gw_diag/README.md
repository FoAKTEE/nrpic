# gw_diag — gravitational-wave diagnostics for a periodic domain (B-pre-3)

Helper package of B-emd-gw. Analysis of AthenaK output only (decision 0010): no simulation
code here. Status: deliverables exist and are tested (see "Validation"); open items at the end.

## Contents

| Path | What |
|---|---|
| `gwdiag/grid.py` | periodic cell-centred mesh `Grid`, array layout, wavevectors, rfft weights, shells |
| `gwdiag/tt.py` | TT projection (Lambda projector) in Fourier space; h^TT and d_tau h^TT from (gamma, K) or from the Z4c variables; energy densities and spectrum; +/x and helicity amplitudes |
| `gwdiag/weyl.py` | Ricci tensor, E_ij, B_ij from (gamma_ij, K_ij) with FD order 2/4/6 or spectral derivatives; triad for a fixed direction or AthenaK's radial triad; Psi_4 |
| `gwdiag/analytic.py` | reference fields written as arrays: superpositions of linear plane waves (TT gauge), exact pure-gauge Minkowski (random spatial coordinates and slicing), scalar (longitudinal) data |
| `gwdiag/readers.py` | readers of AthenaK restart (`.rst`, double), binary mesh output (`.bin`, float32) and NRFIELD dumps; Z4c -> ADM |
| `tests/` | pytest unit tests (14; two of them need real files, see below) |
| `scripts/validate_tt.py`, `validate_weyl.py`, `validate_athenak.py` | validation runs with figures and JSON |
| `scripts/registered.py` | runs a command as a registered run (manifest in `../runs/<run_id>/`) |
| `figs/` | PNG copies of the validation figures (PDFs in the run directories) |
| `JOURNAL.md` | predictions and outcomes, including the failed ones |

## Array layout

* scalar field `f[k, j, i]`, shape `(nz, ny, nx)`; `i` along x and fastest (AthenaK's
  Kokkos LayoutRight and the NRFIELD order);
* vector `v[a, k, j, i]`, `a = 0, 1, 2` for x, y, z;
* symmetric tensor stored in full, `T[a, b, k, j, i]`, shape `(3, 3, nz, ny, nx)`;
* cell centres `x_i = xmin + (i + 1/2) dx`; direction `a` lives on array axis `-1 - a`.
`Grid((nx, ny, nz), (Lx, Ly, Lz), xmin)`; the readers return a `Grid` with the dump.

## Conventions and gauge assumptions

* Sign of the extrinsic curvature as in AthenaK: `K_ij = -(1/2 alpha)(d_t - L_beta) gamma_ij`.
* **TT projection** `Lambda_ij,lm = P_il P_jm - P_ij P_lm / 2`, `P = delta - k k / k^2`, applied
  mode by mode with `numpy.fft.rfftn`. The k = 0 mode is set to zero by default
  (`k0="traceless"` keeps its traceless part); the Nyquist planes are set to zero by default
  (k and -k coincide there). For any sampled field the projection is exact to round-off; it
  has no truncation error.
* **Metric perturbation** `h_ij = tilde gamma_ij - delta_ij`, `tilde gamma = det(gamma)^(-1/3) gamma`
  (the Z4c conformal metric). The conformal factor removes the homogeneous expansion, so no
  scale factor is needed. **Time derivative** along the normal (proper time of the Eulerian
  observers): `d_tau h^TT = -2 Lambda(tilde A)`, `tilde A = chi (K - gamma K/3)`. The trace is
  removed with the full metric before projecting; projecting `K_ij` itself would add a spurious
  `a adot h^TT` term (JOURNAL.md, D1).
* Gauge assumptions [JUDGEMENT, checked by the tests]: the background is Minkowski or a
  spatially flat FLRW slice whose spatial metric is conformally `delta_ij` in the simulation
  coordinates, and perturbations are small. Then (i) Lambda of the conformal metric equals the
  TT tensor mode to first order, and spatial and slicing gauge changes enter only at second
  order (pure-gauge data: h^TT, d_tau h^TT ~ eps^2, `figs/tt_gauge_scalar.png`); (ii) the O(h^2)
  correction of the conformal decomposition is a pure trace, so the error on a TT wave is
  O(A^2) relative, not O(A) (JOURNAL.md, P1 outcome); (iii) on a flat torus Lambda equals York's
  covariant TT decomposition with respect to delta [VERIFIED definitions: arXiv:2111.09163 v2,
  `prd_v1.tex` lines 163-175]; with respect to the actual gamma the two differ at O(eps^2).
  Beyond linear order the flat projection is a convention, not the covariant one.
* **Energy** (G = 1 default, `c = 1`): `rho_kin = <d_tau h^TT_ij d_tau h^TT_ij>/(64 pi G)`, which is
  `rho_K = (M_pl^2/2) K^TT_ab K_TT^ab` of arXiv:2111.09163 (Eq. rhoK, line 260; the paper notes
  `rho_K = rho_Isaacson/2` for linear tensor modes, footnote line 272);
  `rho_grad = chi_bar <d_k h^TT_ij d_k h^TT_ij>/(64 pi G)` (proper gradients, `chi_bar = a^-2`);
  `rho_GW = rho_kin + rho_grad`, which for free waves equals the Isaacson
  `<d_tau h d_tau h>/(32 pi G)` after averaging and is constant in time for a standing wave
  where the two pieces are not. `gw_spectrum` returns shell sums in |k| (they add up to the
  volume averages) and `drho_dlnk`. `helicity_spectrum` splits each mode into the parts
  moving along +k and -k (assumes omega = sqrt(chi_bar)|k|) and returns the energy in
  helicity +2 (pattern turning counterclockwise about the direction of motion) and -2.
* **Polarization basis** for a direction n: `u = theta-hat`, `v = phi-hat` of n (theta from +z,
  phi from +x), `e_+ = u u - v v`, `e_x = u v + v u`. For n = +x: `u = -z`, `v = +y`, so the
  AthenaK `z4c_linear_wave` along x (h = A diag(0, -1, 1) sin) is pure `h_+ = A sin(2 pi (x - t))`.
* **Weyl**: `E_ij = TF[R_ij + K K_ij - K_ik K^k_j] - 4 pi TF[S_ij]` (S optional; in vacuum the
  trace vanishes by the Hamiltonian constraint), `B_ij = sym(eps_i^kl D_k K_lj)`. For a direction
  n: triad (n, theta-hat, phi-hat) orthonormalized with gamma in the order of AthenaK,
  `mbar = (v - i w)/sqrt 2`, `Psi_4 = -(E - iB)_ij mbar^i mbar^j`. For a linear wave moving along
  +n this is `hddot_+ - i hddot_x`; along -n it vanishes. AthenaK's `weyl_rpsi4 + i weyl_ipsi4`
  is `r Psi_4` with the same convention in a radial triad about the origin (`weyl.psi4(...,
  direction=None)` reproduces it to 1e-6, run B-emd-gw-20261115-120128-7dfaa38), which is not
  useful for plane waves on a torus: use a fixed direction.
* **Psi_4 is not a clean wave measure in a box with matter**: a scalar perturbation has a tidal
  field `E_ij = -(d_i d_j - delta lap/3) zeta` whose `mbar mbar` part is nonzero for any direction
  other than its wavevector (validated: run B-emd-gw-20261115-115540-2cb33df, `scalar_psi4`).
  The TT quantities and `Lambda(E)`, `B` vanish for scalar data at first order. Use h^TT /
  rho_GW, or Lambda applied to E - iB, for the radiative part.

## How to use

```python
import sys; sys.path.insert(0, "tracks/B-emd-gw/gw_diag")
from gwdiag import readers, tt, weyl
d = readers.read_rst("rst/lw3.00005.rst")              # Z4c restart, double precision
g = d["grid"]
chi, gt, At, trK, alpha, beta = readers.z4c_tensors(d)
hTT, hdTT = tt.tt_from_conformal(gt, At, g)             # h^TT, d_tau h^TT
sp = tt.gw_spectrum(hTT, hdTT, g, chi_bar=chi.mean())   # rho_kin, rho_grad per |k| shell
hel = tt.helicity_spectrum(hTT, hdTT, g, chi_bar=chi.mean())
gamma, K, alpha, beta = readers.z4c_to_adm(d)
E, B = weyl.electric_magnetic(gamma, K, g, order=6)     # order 6 = AthenaK with nghost = 4
p4 = weyl.psi4(E, B, gamma, g, direction=(1, 0, 0))
```
Which dump: the restart file is the only full-mesh output in double precision. The binary
output (`file_type = bin`) is float32: a diagonal metric component `1 + h` with `h ~ 1e-6` keeps
only ~1 digit of h; use it only for fields that vanish in the background. NRFIELD dumps
(particles module) carry E, chi and constraints, not the conformal metric or A_ij: not enough.
Only uniform meshes are assembled. Memory of `electric_magnetic`: about 60 full arrays
(1 GB at 128^3).

## How to rerun

```
cd tracks/B-emd-gw/gw_diag
python3 -m pytest -q -p no:cacheprovider tests/          # 12 pass, 2 skip without real files
GWDIAG_RST=<a .rst> GWDIAG_NRFIELD=<a .field.NNNNN.bin> python3 -m pytest -q tests/test_readers.py
python3 scripts/registered.py --purpose "..." --kind scouting -- python3 scripts/validate_tt.py
python3 scripts/registered.py --purpose "..." -- python3 scripts/validate_weyl.py
python3 scripts/registered.py --purpose "..." -- python3 scripts/validate_athenak.py <run dir with rst/ and bin/>
```
Each validation takes 7-40 s on 4-8 cores. Outputs land in
`/data/haiyangw/nrpic/scratch/B-emd-gw/<run_id>/`, PNG copies in `figs/`.

## Validation (details and numbers in JOURNAL.md)

| Check | Result | Run id |
|---|---|---|
| Lambda idempotent, traceless, transverse; plane waves on a non-cubic box exact; circular waves to the right helicity | < 1e-12 | unit tests |
| 48 random waves (64^3): shell spectrum, helicity split 70/30, energy constant in time; standing wave rho_kin 0..2, total constant | 2.6e-12, 1.7e-11 | B-emd-gw-20261115-115206-2e6c497 (also -115001-e9262bd) |
| from (gamma, K): error of h^TT, d_tau h^TT, rho ~ A^2 | slopes 2.00, 1.99, 2.00 | same |
| pure gauge and scalar data: h^TT, d_tau h^TT ~ eps^2, rho ~ eps^4 | slopes 2.00-2.01, 4.00 | same |
| E, B convergence (waves, pure gauge, scalar), FD orders 2/4/6 | fitted 1.9-2.0, 3.9-4.0, 5.8-5.9 | B-emd-gw-20261115-115637-175cbca (also -115540-2cb33df) |
| Psi_4 = hddot_+ - i hddot_x; error ~ A; reverse direction at round-off | slope 1.001 | same |
| scalar mode: B, Lambda E ~ eps^2; Psi_4 off the wavevector = -E_lin mbar mbar | 3e-6 at eps = 1e-6 | same |
| AthenaK z4c_linear_wave (32^3, two periods): amplitude, phase, rho, h_x, non-TT part | 3e-7, 1.2e-6 rad, 6e-7, 1e-24, 2.7e-5 | B-emd-gw-20261115-120128-7dfaa38 (input run B-emd-gw-20261115-113218-0ea0f74) |
| d_tau h^TT from tilde A against time differences of the dumps | equals the truncation of the differences (2.55e-2 vs 2.57e-2; 7.8e-4 vs 7.9e-4) | same |
| AthenaK weyl output vs gwdiag radial-triad Psi_4 | 3e-7..1.8e-6 at t_n - 7 dt; output lags by waveform_dt - dt | same |
| readers: own vs periodic_z4c reader bit-identical; synthetic multi-block rst with trackers; real cosmology rst (8 blocks) and NRFIELD | pass | unit tests |

## Not done / open

* Covariant (York) TT decomposition with respect to the actual gamma (vector elliptic solve):
  not implemented; the flat Lambda is exact at first order only. Needed if rho_K is to be
  evaluated beyond the perturbative regime (pancake after shell crossing).
* The helicity split assumes free waves (omega = sqrt(chi_bar)|k|); in a matter era on
  super-horizon scales it is not meaningful.
* Psi_4 / E with matter: the `S_ij` term is supported but no reader supplies `S_ij` (AthenaK's
  `tmunu` is not in the restart file).
* Not tested on a refined mesh (readers refuse it).

## Requests

* **core**: (1) AthenaK's `weyl` mesh output at an output time holds the Weyl scalar of one step
  after the previous waveform time (lag `waveform_dt - dt`, measured as exactly 7 steps of 1/128
  with `waveform_dt = 1/16`, run B-emd-gw-20261115-120128-7dfaa38); please confirm in
  `z4c_tasks.cpp` (InitRecvWeyl / CalcWeylScalar) and fix or document it. (2) For periodic runs,
  an optional double-precision binary output of the Z4c variables (the restart file is the only
  double full-mesh output and carries ghost zones and the whole state), or confirmation that
  restart files at the wave-output cadence are the intended route. (3) Optional: `S_ij` (and
  `E`, `S_i`) in a double-precision dump, so that E_ij can include the matter term.
* **B-emd-gw lead**: the periodic_z4c dumps should keep `file_type = rst` at the cadence of the
  GW analysis; the `weyl` output of AthenaK is radial and lagged, gwdiag's fixed-direction
  Psi_4 replaces it.
