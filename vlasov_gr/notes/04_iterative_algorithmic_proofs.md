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
