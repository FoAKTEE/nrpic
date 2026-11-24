# Iterative Algorithmic Proofs: Mathematical Derivations and Numerical Verification

This working note documents each iterative algorithmic improvement built on top of the modular `athenak/src/particles/vlasov/` TaskList architecture and proves both analytical invariants and numerical speed/accuracy gains.

---

## Iteration 1 — High-Order Geodesic Integration, Symplectic $S^2$/QMC Initialization, Tier-2 MFM, and Densitized Filtering

### 1.1 Tier-2 MFM Gradient Specialization (`vlasov_mfm.cpp`)
- **Mathematical formulation**: In the relativistic meshless-finite-mass (MFM) kernel, per-element weighted least-squares gradient solves for $N_b$ velocity bases require only the first $N_b$ active basis slots. Previously, `ComputeGradients` looped statically over `MAX_BASIS = 8` on every element, incurring dead register pressure and unused shared/local-memory traffic for $N_b \in \{1, 2, 4\}$.
- **Implementation**: Specialized `ComputeGradients<NB_MAX>` for `<1>`, `<2>`, `<4>`, and `<MAX_BASIS>` alongside explicit TaskList decomposition (`NrpicVlasovPrepareStep` $\to$ `NrpicVlasovSyncMetric` $\to$ `NrpicVlasovAdvanceTask` $\to$ `NrpicVlasovExciseTask`).
- **Measured verification**:
  - **Stage 3 3D parity** (`dt=0.02`, 5 steps, $N=125$, $N_b=2$):
    - B200 GPU vs Python 3D reference: $\max|\Delta x| = 2.22\times 10^{-16}$, $\max|\Delta m| = 3.81\times 10^{-16}$, $\max|\Delta\bar{u}| = 1.22\times 10^{-15}$, $\max|\Delta\Sigma| = 8.33\times 10^{-16}$.
    - OpenMP CPU (`4` threads) vs B200 GPU: $\max|\Delta x| = 1.11\times 10^{-16}$, $\max|\Delta m| = 3.47\times 10^{-18}$, $\max|\Delta\bar{u}| = 2.11\times 10^{-15}$, $\max|\Delta\Sigma| = 7.91\times 10^{-16}$.
    - OpenMP determinism (`OMP4a` vs `OMP4b`): $\le 1.89\times 10^{-15}$.
  - **Suite 1D Tier-2 GPU benchmark (`s1d_sig15`, `vlasov_mfm`)**:
    - Baseline wall/compute time: `3.52 s` / `2.37 s`.
    - Iteration 1 wall/compute time: `3.286 s` / `2.222 s` (`3.168e4` zone-cycles/cpu_second, $\Delta M/M_0 = 3.197\times 10^{-16}$, $\Delta E/E_0 = 2.650\times 10^{-10}$).

### 1.2 4th-Order Symplectic 2-Stage Gauss-Legendre IRK Pusher (`PushGL4`)
- **Mathematical formulation**: In coordinate Hamiltonian variables $(x^i, u_i)$ with Hamiltonian $H(t, x, u) = \alpha W - \beta^i u_i$ ($W = \sqrt{\epsilon + \gamma^{ij} u_i u_j}$), the 2-stage Gauss-Legendre implicit Runge-Kutta tableau
  $$c = \left[\frac{1}{2} - \frac{\sqrt{3}}{6},\; \frac{1}{2} + \frac{\sqrt{3}}{6}\right], \qquad b = \left[\frac{1}{2},\; \frac{1}{2}\right], \qquad A = \begin{pmatrix} \frac{1}{4} & \frac{1}{4} - \frac{\sqrt{3}}{6} \\ \frac{1}{4} + \frac{1}{4}\frac{2\sqrt{3}}{3} & \frac{1}{4} \end{pmatrix}$$
  (with $A_{10} = \frac{1}{4} + \frac{\sqrt{3}}{6}$) satisfies $b_i A_{ij} + b_j A_{ji} - b_i b_j = 0$, making `PushGL4` **exactly symplectic** ($O(\Delta t^4)$ global phase-space and modified-Hamiltonian accuracy, $A$-stable for stiff near-horizon trajectories).
- **Measured verification** (Test 7, Kerr $a=0.9M, e=0.99$ orbit over $t \in [0, 230M]$, tolerance $2\times 10^{-14}$):
  - Observed convergence slope across $\Delta t \in \{0.16, 0.08, 0.04, 0.02\}$: $p_E^{\rm GL4} = 4.003$, $p_Q^{\rm GL4} = 3.980$ (vs $p_E^{\rm Mid} = 2.000$).
  - At Wu & Most canonical $\Delta t = 0.01M$:
    - `PushGL4`: $\max|\Delta E| = 3.775\times 10^{-15}$, $\max|\Delta Q| = 7.416\times 10^{-14}$.
    - `PushMidpoint`: $\max|\Delta E| = 2.773\times 10^{-8}$, $\max|\Delta Q| = 2.476\times 10^{-7}$.
    - Accuracy gain: **$7.3\times 10^6\times$** in $E$ and **$3.3\times 10^6\times$** in Carter constant $Q$. Even at $8\times$ larger step ($\Delta t = 0.08M$), `PushGL4` achieves $\max|\Delta E| = 1.096\times 10^{-11}$, $2500\times$ more accurate than `PushMidpoint` at $\Delta t = 0.01M$.

### 1.3 3-Level Quadratic Lagrange Metric Time Interpolation (`EvalFrac`)
- **Mathematical formulation**: A 4th-order stage pusher evaluates the spacetime metric at fractional stage times $c \in \{c_1, c_2\} \subset (0, 1)$. Standard 2-level linear blending `[met0, met1]` has $O(\Delta t^2)$ time truncation error, capping global accuracy at $O(\Delta t^2)$. Retaining a zero-copy swapped third time slice `met_prev` ($t^{n-1} = t^n - \Delta t_{\rm prev}$) and step ratio $r = \Delta t_n / \Delta t_{\rm prev}$ gives exact degree-2 Lagrange interpolation at $c = (t - t^n)/\Delta t_n$:
  $$w_{-1}(c) = \frac{r^2 c(c-1)}{1+r}, \qquad w_0(c) = (1-c)(1+rc), \qquad w_1(c) = \frac{c(1+rc)}{1+r},$$
  reducing metric time error to $O(\Delta t^3)$ with zero extra Z4c RHS evaluations. Regridding or startup cleanly resets `met_prev_valid = false`, falling back smoothly to 2-level linear weights for the first step.
- **Measured verification** (Test 8, non-uniform time steps with alternating ratio $r = 1.27$ and $1/1.27$ on an analytic oscillatory 3+1 metric, $T=1.6$, $n \in \{16, 32, 64, 128\}$):
  - Linear `BlendAdm2`: observed convergence order $p_{\rm lin} = 2.003$, error at $h = 0.0125$: $1.396\times 10^{-5}$.
  - 3-level quadratic `BlendAdm3`: observed convergence order $p_{\rm quad} = 2.977$, error at $h = 0.0125$: $5.221\times 10^{-8}$ (**$267\times$ accuracy improvement**).

### 1.4 $S^2$ Lebedev/Icosahedral Cubature & Quasi-Monte Carlo Phase-Space Samplers
- **Mathematical formulation**: For isotropic spherical equilibria (Shapiro-Teukolsky clusters) or ellipsoidal collapse (Oppenheimer-Snyder, prolate spheroids), Monte Carlo sampling introduces $O(N^{-1/2})$ Poisson dipole/quadrupole/stress-anisotropy fluctuations that seed spurious constraint violations and artificial triaxiality.
  - **C++ SCP $S^2$ shells (`SphericalCubatureRule`)**: Octahedral ($Q=6$, degree 3), icosahedral ($Q=12$, equal weights, degree 5), Lebedev-14 ($w_1 = 1/15, w_2 = 3/40$, degree 5), and Lebedev-26 ($w_1 = 1/21, w_2 = 4/105, w_3 = 9/280$, exact for all spherical harmonics $Y_{\ell m}$ up to $\ell = 7$) shells rotated by `HaltonSO3` and scaled by $\sqrt{3}$ so $\sum w_q (\sqrt{3}\hat{n}_q)(\sqrt{3}\hat{n}_q)^T = I_3$ and $\boldsymbol{\Sigma}$ is preserved to machine precision.
  - **Python QMC samplers (`python/nrpic/qmc_sampling.py`)**:
    - `qmc_antipodal`: 4-tuple phase-space pairing $\{(+\mathbf{x},+\mathbf{u}), (-\mathbf{x},-\mathbf{u}), (+\mathbf{x},-\mathbf{u}), (-\mathbf{x},+\mathbf{u})\}$ over radially rank-stratified 5D scrambled Sobol points, zeroing center of mass $\mathbf{COM}$, momentum $\mathbf{P}$, angular momentum $\mathbf{J}$, and local grid momentum density $S_i(\mathbf{x})$ identically.
    - `qmc_lebedev`: Halton-$SO(3)$ rotated $S^2$ Lebedev shells ($Q=6,12,14,26$) centered on radially rank-stratified Sobol spatial sites, achieving machine-precision local velocity stress-tensor isotropy at every site.
    - `qmc_octant`: $O_h$ 24-fold reflection (8 octants $\times$ 3 cyclic permutations) for spherical OS data (guaranteeing exact $Q_{xx}=Q_{yy}=Q_{zz}$) and 16-fold $x\leftrightarrow y$ octant reflection for axisymmetric Prolate spheroids ($Q_{xx}=Q_{yy}$, $Q_{ij}=0$ for $i\ne j$).
- **Measured verification** (`tests/test_qmc_sampling.py` 3/3 passed; ST $y_c=0.819$ at $N=8960$):

| Sampler | Radial CDF err | $|\mathrm{COM}|/\bar{r}_s$ | $|\mathbf{P}|/M_0$ | $|\mathbf{J}|/(M_0\bar{r}_s)$ | Stress aniso | 3D $S_{\rm rms}$ ($N=8960$) |
| --- | --- | --- | --- | --- | --- | --- |
| `mc` | $3.243\times 10^{-3}$ | $4.13\times 10^{-3}$ | $5.71\times 10^{-3}$ | $2.61\times 10^{-3}$ | $1.59\times 10^{-2}$ | $9.743\times 10^{-6}$ |
| `stratified` | $7.870\times 10^{-5}$ | $1.88\times 10^{-3}$ | $2.28\times 10^{-3}$ | $2.07\times 10^{-3}$ | $6.01\times 10^{-3}$ | $9.480\times 10^{-6}$ |
| `qmc_antipodal` | $2.131\times 10^{-4}$ | $4.10\times 10^{-19}$ | $3.03\times 10^{-20}$ | $1.09\times 10^{-18}$ | $2.38\times 10^{-3}$ | $9.864\times 10^{-22}$ |
| `qmc_lebedev` ($Q=14$) | $1.492\times 10^{-3}$ | $1.79\times 10^{-17}$ | $9.71\times 10^{-20}$ | $7.00\times 10^{-20}$ | $5.27\times 10^{-16}$ | $4.431\times 10^{-22}$ |

### 1.5 Pre-$\sqrt{\gamma}$ Densitized Binomial Source Filtering (`filter_densitized = true`)
- **Mathematical formulation**: A symmetric normalized convolution filter $(w_1, w_0, w_1)^3$ with $w_0 + 2 w_1 = 1$ preserves the sum over coordinate cells $\sum_c q_c \Delta V_c$ identically. Filtering the physical stress-energy $T^{00} = E$ directly violates proper-volume ADM energy conservation $\int E \sqrt{\gamma}\,d^3x$ wherever $\nabla\sqrt{\gamma} \ne 0$. Accumulating densitized sources $\tilde{T} = \sqrt{\gamma}\,T$ (`NrpicDepositSources` / `NrpicVlasovDepositLoop`), running all binomial/compensated filter passes on $\tilde{T}$, and dividing by $\sqrt{\gamma}$ afterwards (`NrpicNormalizeDensitizedSources`) preserves the proper integral identically (`tm_is_densitized` guard handles dual adaptive deposits cleanly).
- **Measured verification** (Oppenheimer-Snyder $R_0=5M$ Z4c+AMR, `s3_grlbv_n20` to $t=4M$ on B200 GPU):
  - `filter_densitized = false`: `(int_E_filtered - int_E)/int_E = -2.459e-03` at $t=0$ and `-7.432e-04` at $t=4M$.
  - `filter_densitized = true`: `(int_E_filtered - int_E)/int_E = +0.000e+00` at $t=0$ and `+0.000e+00` at $t=4M$ (exact machine conservation).
