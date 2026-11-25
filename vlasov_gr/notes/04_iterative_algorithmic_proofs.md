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


---

## Iteration 2 — Asymptotic-Preserving Conservative Relativistic Cell-BGK Operator (`vlasov_pbgk`)

### 2.1 Motivation & Regime Complementarity
At intermediate and large collisionality ($\sigma/\mu \gg 1$), pure Monte Carlo binary pairing (`nrpic` collisions) requires subcycling with $\mathcal{O}(\tau_{\rm coll})$ cost per step ($\tau_{\rm coll} = n_{\rm com}\sigma v_{\rm M\o l}\Delta\tau$), becoming $50\times$ slower than collisionless integration at $\sigma/\mu = 10^4$, while low-basis fluid MFM (`vlasov_mfm`, $N_b = 2$) cannot represent multi-stream crossing in the collisionless limit ($\sigma/\mu = 0$) and loses conservation ($\Delta E/E_0 \sim 6\times 10^{-3}$) in transitional relaxation ($\sigma/\mu = 15$). Iteration 2 equips the GPU-fast Lagrangian packet ensemble (`vlasov_hybrid`) with an asymptotic-preserving, exactly 4-momentum-conserving relativistic Cell-BGK collision operator ([`vlasov_pbgk_kernels.hpp`](file:///home/schmidt/ssci-haiyangw/nrpic/athenak/src/particles/vlasov/vlasov_pbgk_kernels.hpp), [`vlasov_pbgk.cpp`](file:///home/schmidt/ssci-haiyangw/nrpic/athenak/src/particles/vlasov/vlasov_pbgk.cpp)).

### 2.2 Global Gamma-Mixture Rejection Proof (`SampleMaxwellJuttner`)
Let $x = W - 1 \ge 0$ be the dimensionless kinetic energy in the cell center-of-momentum frame with dimensionless temperature $\Theta = k_B T / m c^2 > 0$. The isotropic Maxwell-J\"uttner marginal distribution is proportional to
$$f(x) = x^{1/2}(1+x)\sqrt{2+x}\,e^{-x/\Theta}.$$
We construct the global polynomial-exponential majorant
$$h(x) = \left(\sqrt{2}\,x^{1/2} + 2\,x^{3/2} + x^2\right)e^{-x/\Theta}.$$
**Proof of global domination**: Setting $t = \sqrt{x} \ge 0$, direct expansion of the squared radial prefactors yields
$$\left(\sqrt{2} + 2t^2 + t^3\right)^2 - (1+t^2)^2(2+t^2) = (4\sqrt{2} - 5)\,t^2 + 2\sqrt{2}\,t^3 + 4\,t^5 > 0 \qquad \forall\, t > 0,$$
since $4\sqrt{2} - 5 \approx 0.65685 > 0$. Thus $h(x) \ge f(x)$ **identically for all $x \ge 0$ and all $\Theta > 0$** (nonrelativistic $\Theta \ll 1$ through ultra-relativistic $\Theta \gg 1$) using exact $\mathrm{Gamma}(3/2,\Theta)$, $\mathrm{Gamma}(5/2,\Theta)$, and $\mathrm{Gamma}(3,\Theta)$ mixture weights $1 : \frac{3}{\sqrt{2}}\Theta : \sqrt{\frac{8}{\pi}}\Theta^{3/2}$, driven deterministically across CPU OpenMP and NVIDIA B200 GPU by `utils/rng.hpp` Philox-4x32 keys.

### 2.3 Exact Per-Cell 4-Momentum Projection (`ProjectCellFourMomentumT`)
Given cell invariant 4-momentum $(E_c, \mathbf{P}_c)$ evaluated in the local ADM triad and $M_{\rm inv} = \sqrt{E_c^2 - |\mathbf{P}_c|^2}$, colliding packets interact with the asymptotic-preserving exponential relaxation probability $p_{\rm coll} = 1 - e^{-\tau_{\rm coll}}$ ($\tau_{\rm coll} = M_c \sigma_0 v_{\rm M\o l} \alpha \Delta t / (V_c U_0^2)$). Any finite sample of $n$ unequal-weight packets $(m_p, \mathbf{q}_p)$ after stochastic Maxwell-J\"uttner draws exhibits $O(N_c^{-1/2})$ momentum and energy fluctuation. `ProjectCellFourMomentumT` enforces **exact** cell conservation in $O(n)$ memory and work:
1. Boost post-draw orthonormal-frame momenta $\mathbf{q}_p$ into their own COM frame $(\sum_p m_p \mathbf{q}_p^* = \mathbf{0})$ and remove roundoff COM residual ($\mathbf{q}_p^* \leftarrow \mathbf{q}_p^* - \mathbf{P}_{\rm com}/M_c$).
2. Rescale $\mathbf{q}_p^* \leftarrow s\,\mathbf{q}_p^*$ where $s > 0$ is the unique root of the strictly increasing convex scalar equation
   $$F(s) = \sum_{p=1}^{n} m_p \sqrt{1 + s^2 |\mathbf{q}_p^*|^2} = M_{\rm inv}$$
   ($F(0) = M_c < M_{\rm inv}$, $F'(s) > 0$ for any non-cold cell), solved to $|F(s) - M_{\rm inv}| \le 10^{-15} M_{\rm inv}$ via safeguarded Newton-Raphson + bisection.
3. Boost $s\,\mathbf{q}_p^*$ back into the Eulerian triad frame by $U_{\rm cm}^\mu = (E_c, \mathbf{P}_c)/M_{\rm inv}$ (`LorentzBoostMom`), guaranteeing $E_{\rm after} = E_c$ and $\mathbf{P}_{\rm after} = \mathbf{P}_c$ to machine precision for arbitrary unequal particle weights.

### 2.4 Measured Verification
- **Kernel Self-Tests ([`vlasov_kernel_test.cpp`](file:///home/schmidt/ssci-haiyangw/nrpic/tests/kernel/vlasov_kernel_test.cpp) Test 9, $40{,}000$ draws per $\Theta$)**:
  - $\Theta = 10^{-4}$: $\langle W\rangle = 1.000150$ ($\mathrm{rel} = 5.29\times 10^{-8}$), $\langle q^2/W\rangle = 0.000300$ ($3\Theta$, $\mathrm{rel} = 3.53\times 10^{-4}$).
  - $\Theta = 0.1$: $\langle W\rangle = 1.166131$ ($\mathrm{rel} = 7.35\times 10^{-4}$), $\langle q^2/W\rangle = 0.298649$ ($\mathrm{rel} = 4.50\times 10^{-3}$).
  - $\Theta = 1.0$: $\langle W\rangle = 3.355416$ ($\mathrm{rel} = 4.46\times 10^{-3}$), $\langle q^2/W\rangle = 2.983524$ ($\mathrm{rel} = 5.49\times 10^{-3}$).
  - $\Theta = 5.0$: $\langle W\rangle = 15.028034$ ($\mathrm{rel} = 4.53\times 10^{-3}$), $\langle q^2/W\rangle = 14.931012$ ($\mathrm{rel} = 4.60\times 10^{-3}$).
  - Unequal-mass `ProjectCellFourMomentumT` ($n = 32$): `rel_dE = 2.347e-16`, `rel_dP = 6.062e-17`.
- **Suite 1D Optical-Depth Crossover ([`run_pbgk_crossover.py`](file:///home/schmidt/ssci-haiyangw/nrpic/vlasov_gr/notes/scripts/run_pbgk_crossover.py), B200 GPU, `nx1=256`, $t=0.65$, $49{,}152$ $S^2$ packets for P-BGK/NRPIC vs $128\times 4\times 4$ for AP-MFM)**:
  Exact warm beam inflow Rankine-Hugoniot jump (`sig_v=0.03`, $u_0 = \pm 0.60$): $D_2^{\rm warm} = 4.075414$, $e_2^{\rm warm} = 4.758756$, $\theta_2 = 0.100376$, $V_s = 0.167061$ (cold inflow reference: $D_2^{\rm cold} = 4.100558$, $e_2^{\rm cold} = 4.782032$).

| Method | $\sigma/\mu$ | Wall [s] | Comp [s] | $\max\|\Delta M/M_0\|$ | $\max\|\Delta E/E_0\|$ | $D_2$ | Warm $D_2$ err | $e_2$ | Warm $e_2$ err |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `vlasov_pbgk` | $0$ | `2.670` | `1.366` | `0.00e+00` | `0.00e+00` | `2.0004` | — | `2.3349` | — |
| `vlasov_pbgk` | $2$ | `2.659` | `1.556` | `0.00e+00` | `3.61e-15` | `2.5888` | — | `3.0065` | — |
| `vlasov_pbgk` | $15$ | `2.870` | `1.758` | `0.00e+00` | `1.10e-14` | `3.8678` | `5.09%` | `4.5293` | `4.82%` |
| `vlasov_pbgk` | $10^4$ | `3.589` | `2.476` | `0.00e+00` | `1.83e-14` | `3.9991` | `1.87%` | `4.6787` | `1.68%` |
| `vlasov_mfm` | $0$ | `3.759` | `2.686` | `4.44e-16` | `1.08e-03` | `2.0000` | — | `2.3345` | — |
| `vlasov_mfm` | $2$ | `4.506` | `3.389` | `0.00e+00` | `1.74e-09` | `2.9792` | — | `3.4412` | — |
| `vlasov_mfm` | $15$ | `4.862` | `3.736` | `4.44e-16` | `6.19e-03` | `3.6406` | `10.67%` | `4.3141` | `9.34%` |
| `vlasov_mfm` | $10^4$ | `3.320` | `2.268` | `0.00e+00` | `3.97e-12` | `4.0677` | `0.19%` | `4.7493` | `0.20%` |
| `nrpic` (MC) | $0$ | `2.056` | `1.017` | `0.00e+00` | `0.00e+00` | `2.0004` | — | `2.3349` | — |
| `nrpic` (MC) | $2$ | `2.566` | `1.534` | `0.00e+00` | `1.90e-16` | `2.4399` | — | `2.8459` | — |
| `nrpic` (MC) | $15$ | `3.217` | `2.190` | `0.00e+00` | `1.90e-16` | `3.7072` | `9.03%` | `4.3200` | `9.22%` |
| `nrpic` (MC) | $10^4$ | `179.5`* | `161.6`* | — | — | — | — | — | — |

\* `nrpic_sig1e4` exceeded `180 s` timeout; projected from 20-step measurement (`wall = 11.048 s`, `comp = 9.942 s` across 20 of 325 steps): **`vlasov_pbgk` achieves a `50.0x` wall-clock (`65.3x` compute) speedup** over subcycled MC collisions while maintaining **$O(1)$ runtime** (`2.67 s` to `3.59 s` from $\sigma/\mu=0$ to $10^4$), exact free streaming at $\sigma=0$, $\le 1.83\times 10^{-14}$ energy conservation across all $\sigma/\mu$, and $< 1.9\%$ Taub double-shock accuracy at $\sigma/\mu = 10^4$.
- **GPU vs OpenMP (4 threads) Determinism** (5 steps at $\sigma/\mu=15$): `max|dx| = 4.441e-16`, `max|du| = 9.812e-14`.


---

## Iteration 3 — Self-Adjoint Metric-Weighted Flux-Conservative AMR Source Filter (`filter_metric_conservative`)

### 3.1 Root Cause of Prior Tradeoff
- **Plain un-densitized source filtering (`plain`)**: Applies the binomial stencil directly to physical coordinate densities $(E, S_i, S_{ij}) = \mathcal{O}(1)$ in curved spacetime. On uniform central boxes, this preserves constant rest density ($\rho_{\rm err} = 4.18\times 10^{-4}$ in OS $R_0=5M$), **but** violates proper-volume conservation $\int \sqrt{\gamma}\,E\,d^3x$ ($\sim 2.49\times 10^{-3}$ bias at $t=0$, growing to $2.20\times 10^{-2}$ under dynamic AMR).
- **Pre-$\sqrt{\gamma}$ densitized filtering (`dens`)**: Filters $\sqrt{\gamma}\,E$ at each refinement level and divides back by $\sqrt{\gamma}$. Across curved interiors ($\partial_i\sqrt{\gamma}\ne 0$), dividing the average of $\sqrt{\gamma}\,c$ by local $\sqrt{\gamma}$ bends even a spatially uniform dust density, introducing a central OS curvature bias (`rho_err = 3.35e-3`, $8\times$ worse than `plain`). Moreover, without flux refluxing across AMR coarse-fine interfaces (`FilterPass` uses ghost prolongation without fine-to-coarse flux replacement), conservation drifts by $5.03\times 10^{-4}$ (M4 SMR) to $2.38\times 10^{-2}$ (OS AMR).

### 3.2 Self-Adjoint Discrete Formulation & AMR Refluxing
In [`vlasov_math.hpp`](file:///home/schmidt/ssci-haiyangw/nrpic/athenak/src/particles/vlasov/vlasov_math.hpp) (`HarmonicFaceWeight`, `MetricFlux1D`) and [`nrpic.cpp`](file:///home/schmidt/ssci-haiyangw/nrpic/athenak/src/particles/nrpic.cpp) (`NrpicFilterPassMetricConservative`), each directional sweep $d \in \{x^1, x^2, x^3\}$ (alternating forward/backward order across odd/even passes) updates the cell-centered source array $u_c$ weighted by $\sigma_c = \sqrt{\gamma_c}$ (or $\sigma_c=1$ in Newtonian runs, zeroed inside invalid/excised $\det\gamma \le 0$ cells) using discrete divergence:
$$u_c^{\rm new} = u_c + \frac{\mathcal{F}_{c+1/2} - \mathcal{F}_{c-1/2}}{\sigma_c\,\Delta x}, \qquad \mathcal{F}_{c+1/2} = \kappa\,\Delta x\,\sigma_{c+1/2}\,(u_{c+1} - u_c),$$
where the face conductance is the harmonic mean (zeroed if either neighbor has $\sigma \le 0$ or at non-block non-periodic domain boundaries):
$$\sigma_{c+1/2} = \frac{2\,\sigma_L\,\sigma_R}{\sigma_L + \sigma_R} \qquad (\sigma_L, \sigma_R > 0).$$

**Proven Mathematical Properties:**
1. **Exact Flat-Space Equivalence**: When $\sigma_c \equiv \sigma_0 > 0$, $\sigma_{c+1/2} = \sigma_0$, so $\kappa = 1/4$ reduces algebraically to $(1/4, 1/2, 1/4)$ and $\kappa = -c$ reduces to $(-c, 1+2c, -c)$.
2. **Exact Constant Preservation ($\rho_{\rm const} \to \rho_{\rm const}$)**: If $u_c \equiv C$ everywhere (for arbitrary smooth or discontinuous $\sqrt{\gamma_c} > 0$), then $\mathcal{F}_{c+1/2} = 0$ identically at every cell face and every AMR interface, eliminating the $O(\Delta x^2 \nabla^2\sqrt{\gamma})$ curved-center density bias.
3. **Self-Adjointness and $L^2(\sigma)$ Contraction**: Under the curved proper-volume inner product $\langle u, v\rangle_\sigma = \sum_c \sigma_c \Delta x\, u_c v_c$, summation by parts yields:
   $$\langle u, \mathcal{L}v\rangle_\sigma = -\kappa\Delta x \sum_{c+1/2} \sigma_{c+1/2}(u_{c+1}-u_c)(v_{c+1}-v_c) = \langle \mathcal{L}u, v\rangle_\sigma,$$
   with unconditional $L^2(\sigma)$ energy stability $\langle u, (I+\mathcal{L})u\rangle_\sigma \le \langle u,u\rangle_\sigma$ when $\kappa\,\max_c\frac{\sigma_{c+1/2}+\sigma_{c-1/2}}{\sigma_c} \le \frac{1}{2}$ (note $\sigma_{c+1/2} < 2\min(\sigma_L,\sigma_R)$, which also bounds harmonic face conductances near strong curvature gradients).
4. **Exact Conservation Across Multi-Level AMR Interfaces**: At every coarse-fine interface, ghost filling precedes face flux computation, and `pbval_tm->PackAndSendFluxCC` / `RecvAndUnpackFluxCC` overwrites the coarse face flux with the sum of fine-child face fluxes so $\sum_c \sigma_c \Delta x_c \Delta u_c = 0$ telescopically across all refinement jumps.

### 3.3 Measured Verification (`Tests 1–10`, `M5a`, `M4`, `M5b`, GPU/OMP)
- **Standalone Kernel Test 10 ([`vlasov_kernel_test.cpp`](file:///home/schmidt/ssci-haiyangw/nrpic/tests/kernel/vlasov_kernel_test.cpp), verified identically on `g++` and `nvcc -arch=sm_100`)**:
  - Constant preservation (`err_const = 0.00e+00` vs naive pre-densitized `4.80e-01`), self-adjointness `sa = 0.00e+00`, 1D proper-volume conservation `cons_1d = 2.30e-16`, and curved 2-level coarse-fine AMR constant & conservation tests (both $\kappa=+0.25$ and $\kappa=-1$): `amr_const = 0.00e+00`, `amr_cons = 3.77e-16`.
- **Full AthenaK Benchmarks ([`run_iter3_filter_verify.py`](file:///home/schmidt/ssci-haiyangw/nrpic/vlasov_gr/notes/scripts/run_iter3_filter_verify.py), [`iter3_filter_verify.npz`](file:///home/schmidt/ssci-haiyangw/nrpic/vlasov_gr/paper/data/iter3_filter_verify.npz), B200 GPU)**:
  - **M5a Oppenheimer-Snyder $R_0=5M$ (`os_10k_lat`, $N=9{,}328$, 7-level dynamic AMR, $t=25M$)**:
    - `plain`: `rho_err = 4.178e-4`, `||H||_max = 1.896`, `filt(t0/max) = (-2.49e-3 / 2.20e-2)`.
    - `dens`: `rho_err = 3.354e-3`, `||H||_max = 1.912`, `filt(t0/max) = (0.00e+00 / 2.38e-2)`.
    - **`mcons` (Iteration 3)**: **`rho_err = 4.183e-4`** ($8.02\times$ cleaner than `dens`), `||H||_max = 1.893`, **`filt(t0/max) = (0.00e+00 / 8.76e-16)`** (**$2.72\times 10^{13}\times$** tighter proper-volume conservation).
  - **M4 6-Level SMR Kerr $a=0.9M$ (`mesh 10k`, $t=200M$)**: `plain` `(-2.25e-6 / 8.91e-4)` and `dens` `(0.00e+00 / 8.64e-4)` vs **`mcons` `(0.00e+00 / 9.93e-16)`** (**$8.70\times 10^{11}\times$** reduction; identical cluster order parameter `|<e^{iphi}>| = 0.1577`).
  - **M5b Prolate $e=0.9$ Compensated Pass (`nfilter=4, filter_compensate=true`, 7-level AMR, $t=5M$)**: `||H||_max = 0.3475`, **`filt(t0/max) = (0.00e+00 / 1.01e-15)`**.
  - **GPU vs OpenMP (4 threads) 10-step OS AMR Determinism (`mcons`)**: `max|dx| = 8.882e-16`, `max|du| = 6.453e-16`, `rel|d_int_E_filt| = 4.229e-15`.

---

## Iteration 4 — Boundary-Only AMR Refluxing (`bflx`), $C^2$ Quintic Hermite, and Scheme A Stage-Accurate Backreaction

### 4.1 Mathematical Formulations
1. **Iter 4a — Boundary-Only `bflx` Refluxing + Interior `e_prev`/`tm_prev`**:
   Since `mcons` refluxing only replaces coarse-fine boundary face fluxes (never interior cell fluxes), `flx_tm` $(nmb \times 10 \times 3 \times n_{\rm all}^3)$ is replaced by three face slabs `bflx_x{1,2,3}` $(nmb \times 10 \times 2 \times nx^2)$ and `PackAndSendBndryFluxCC` / `RecvAndUnpackBndryFluxCC` in `flux_correct_cc.cpp`, alongside interior-only $(nx_3,nx_2,nx_1)$ allocation for `e_prev` and `tm_prev` (`242` fewer `Real`/cell on $16^3$ blocks at `nghost=4`).
2. **Iter 4b — $C^2$ 6-Node Quintic Hermite (`interp = quintic`, Zero Extra `met*s` VRAM)**:
   On uniform stencils $\{-2,-1,0,1,2,3\}$ with $\alpha \in [0,1)$, 1D endpoint quintic Hermite interpolation using 4th-order centered derivatives $D_1 = (-f_{+2}+8f_{+1}-8f_{-1}+f_{-2})/(12h)$ and $D_2 = (-f_{+2}+16f_{+1}-30f_0+16f_{-1}-f_{-2})/(12h^2)$ produces six $C^2(\mathbb{R})$ weights (`QuinticHermiteWeights` in `nrpic_kernels.hpp`) exact for polynomials through degree 4 (`O(h^5)` value, `O(h^4)` first derivative), requiring zero `met1s`/`met0s` shadow arrays (`46 * 8 bytes/cell` saved vs `bspline`).
3. **Iter 4c — Scheme A Stage-Accurate RK Backreaction (`source_stage_extrap`)**:
   Storing interior $(U_0, \Delta U) = (\text{tm\_prev}, \text{tm\_cur} - \text{tm\_prev})$ in `u_tmunu_{d0,d1}`, `Z4c::CalcRHS` evaluates at RK stage fraction $c_s = \text{Driver::c\_stage}[s-1]$ the pointwise admissibility-limited state $U(t^n + c_s\Delta t) = U_0 + c_s \theta(U_0, \Delta U)\,\Delta U$, where $\theta \in [0,1]$ (`StageSourceLimiter`) enforces positivity $E \ge \varepsilon E_0$ and causal flux $|S|_{\gamma^{-1}} \le (1-\varepsilon) E$, eliminating the first-order frozen-$T_{\mu\nu}$ RK splitting error without additional particle pushes.

### 4.2 Measured GPU Proofs (`run_iter4_verify.py`, `iter4_verify.npz`, `tests/kernel/vlasov_kernel_test.cpp`)
- **Tests 1–12 (`g++` & `nvcc -arch=sm_100`)**: `Test 11 quintic` (`C2=(0,0,5.00e-16), orders=(5.30, 4.13)`); `Test 12 stageA` (`p_frozen=1.00 -> p_rk4=1.99, th=(1.00, 0.125, 0.062)`).
- **Iter 4a**: `GPU4 vs GPU3` 10-step OS parity `max|dx|=4.441e-16, rel|d_intE_filt|=0.000e+00`; `GPU4 vs OMP4` `max|dx|=8.882e-16, rel|d_intE_filt|=4.229e-15`. Full `t=25M` OS AMR: **`73,174 MiB -> 67,110 MiB` (`-6,064 MiB`), `161.1s -> 160.8s`**, identical physics (`rho_err=4.183e-4, M_AH=1.00158M`).
- **Iter 4b**: M4 6-level SMR Kerr ($a=0.9M, t=200M, ng=4, \text{gl4}+\text{mcons}$): **`quintic_ng4` (`11,880 MiB, 209.3s`) improves median $|\Delta E/E_0|$ by `311x` over `hermite_ng4` (`3.38e-10` vs `1.05e-7`) and `4.9x` over `bspline_ng4` (`1.65e-9`) with zero extra `met*s` VRAM (`-2,380 MiB` vs `bspline`)** and `dL_med=8.53e-9, dQ/K_med=2.36e-9, filt_max=9.93e-16`.
- **Iter 4c**: OS `t=10M` CFL convergence (`0.25, 0.125, 0.0625`) cuts $\alpha_c(10)$ error by **`15–23x`** (`3.463e-5, 1.248e-5`, `p=1.47` vs frozen `5.192e-4, 2.841e-4`, `p=0.87`), halves OS $t=25M$ $M_{\rm AH}$ error (`1.00074M` vs `1.00158M` at `+0.4%` cost), and holds ST $y_c=0.500$ 9-level AMR (`tlim=90M`) at `M_AH=1.00060M`, `|P|_max/M0=1.43e-14`, and `filt_max=9.25e-16` (`754.5s`). *(754s ST wall time + 209s M4 Kerr time motivate Iteration 5: Speed is King!)*
