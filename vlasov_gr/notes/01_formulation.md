# Mathematical Formulation: General-Relativistic Lagrangian-Basis Vlasov (GR-LBV) Method for the Full 3+1 Einstein-Vlasov System

## 1. Conventions and 3+1 Einstein-Vlasov Equations

We adopt geometrized units $G = c = 1$ and metric signature $(-, +, +, +)$, matching the Z4c and NRPIC modules of AthenaK. Greek indices $\mu, \nu, \dots \in \{0,1,2,3\}$ denote spacetime components, Latin indices $i, j, k, l \in \{1,2,3\}$ denote spatial coordinate components, and parenthesized indices $(m), (n), \dots \in \{1,2,3\}$ denote orthonormal spatial triad components of the normal Eulerian observers.

On spacelike hypersurfaces $\Sigma_t$ with ADM variables $(\alpha, \beta^i, \gamma_{ij}, K_{ij})$, the spacetime line element is
$$
\mathrm{d}s^2 = -\alpha^2\,\mathrm{d}t^2 + \gamma_{ij}(\mathrm{d}x^i + \beta^i\,\mathrm{d}t)(\mathrm{d}x^j + \beta^j\,\mathrm{d}t).
$$
The future-directed unit normal covector is $n_\mu = (-\alpha, 0, 0, 0)$ and vector is $n^\mu = (\alpha^{-1}, -\alpha^{-1}\beta^i)$.

### 1.1 Canonical Phase-Space Coordinates and Exact Conservation Form

Consider massive particles of unit physical mass scale evolving on the future mass shell $g^{\mu\nu} u_\mu u_\nu = -1$ ($u^\mu$ is four-velocity, momentum per unit rest mass). We parameterize phase space by canonical Darboux coordinates $(x^i, u_j)$, where $u_j = g_{j\mu} u^\mu$ are the covariant spatial components of $u_\mu$. The Lorentz factor measured by normal observers is
$$
W = \alpha u^0 = -n^\mu u_\mu = \sqrt{1 + \gamma^{ij} u_i u_j},
$$
and the raised spatial components are $u^i = \gamma^{ij} u_j$. The time component of $u_\mu$ is $-u_0 = H(t, x^i, u_j) = \alpha W - \beta^i u_i$.

In $(x^i, u_j)$, the Lorentz-invariant mass-shell momentum volume element is $\mathrm{d}\Pi_u = \frac{\mathrm{d}^3 u}{\sqrt{\gamma}\,W}$ and the spatial proper volume element on $\Sigma_t$ is $\mathrm{d}V_{\rm prop} = \sqrt{\gamma}\,\mathrm{d}^3 x$, so the invariant 6D phase-space measure is simply $\mathrm{d}\Omega_{\rm ps} = \mathrm{d}^3 x\,\mathrm{d}^3 u$. Defining the coordinate-weighted rest-mass distribution function
$$
f(t, x^i, u_j) \equiv \frac{\mathrm{d}M_0}{\mathrm{d}^3 x\,\mathrm{d}^3 u} = \sqrt{\gamma}\,W\,\mathcal{F}(x^\mu, u_j),
$$
where $\mathcal{F}$ is the covariant scalar phase-space density, the coordinate rest-mass density is
$$
D(t, \bm{x}) \equiv \sqrt{\gamma}\,\rho_0 = \int_{\mathbb{R}^3} f(t, \bm{x}, \bm{u})\,\mathrm{d}^3 u.
$$
Along timelike geodesics, $(x^i, u_j)$ obey Hamilton's canonical equations:
$$
\dot{x}^i \equiv \frac{\mathrm{d}x^i}{\mathrm{d}t} = \frac{\partial H}{\partial u_i} = \frac{\alpha \gamma^{ij} u_j}{W} - \beta^i,
$$
$$
\dot{u}_i \equiv \frac{\mathrm{d}u_i}{\mathrm{d}t} = -\frac{\partial H}{\partial x^i} = -W \partial_i \alpha + u_j \partial_i \beta^j + \frac{\alpha}{2W} u^l u^m \partial_i \gamma_{lm}.
$$
Because $(\dot{x}^i, \dot{u}_i)$ is Hamiltonian, the 6D phase-space flow is identically divergence-free:
$$
\frac{\partial \dot{x}^i}{\partial x^i} + \frac{\partial \dot{u}_i}{\partial u_i} = 0.
$$
Consequently, the relativistic Boltzmann/Vlasov equation $\mathcal{L}_{\rm geo}\mathcal{F} = C[\mathcal{F}]$ takes the exact coordinate conservative form
$$
\frac{\partial f}{\partial t} + \frac{\partial}{\partial x^i}\!\left(\dot{x}^i f\right) + \frac{\partial}{\partial u_i}\!\left(\dot{u}_i f\right) = \left(\frac{\partial f}{\partial t}\right)_{\rm coll}.
$$
Notice that no factor of $\sqrt{\gamma}$ enters the spatial or momentum divergence! Furthermore, because $\bm{u} \in \mathbb{R}^3$ is unconstrained, any finite linear combination of realizable bases $\tilde{g}_\alpha(\bm{u}) \ge 0$ guarantees strict subluminality $|\bm{v}_{\rm phys}| < 1$ everywhere without velocity-horizon clamping.

### 1.2 ADM Stress-Energy Sources

The stress-energy tensor $T^{\mu\nu} = \int u^\mu u^\nu \mathcal{F}\,\frac{\mathrm{d}^3 u}{\sqrt{\gamma}\,W}$ projects onto normal observers via $E = n_\mu n_\nu T^{\mu\nu}$, $S_i = -g_{i\mu} n_\nu T^{\mu\nu}$, $S_{ij} = g_{i\mu} g_{j\nu} T^{\mu\nu}$. In terms of $f$:
$$
\sqrt{\gamma}\,E = \int W(\bm{x}, \bm{u})\,f\,\mathrm{d}^3 u, \qquad
\sqrt{\gamma}\,S_i = \int u_i\,f\,\mathrm{d}^3 u, \qquad
\sqrt{\gamma}\,S_{ij} = \int \frac{u_i u_j}{W(\bm{x}, \bm{u})}\,f\,\mathrm{d}^3 u.
$$
These densitized fields $(\sqrt{\gamma}E, \sqrt{\gamma}S_i, \sqrt{\gamma}S_{ij})$ match AthenaK's `Tmunu` convention (`I_Tmunu_E`, `I_Tmunu_Sx..Sz`, `I_Tmunu_Sxx..Szz` after dividing by $\sqrt{\gamma}$). When $\sqrt{\gamma} S_{ij}$ is evaluated from positive-weight moments or cubatures on the mass shell, the Weak, Dominant, and Strong Energy Conditions ($E \ge 0$, $\gamma^{ij} S_i S_j < E^2$, $0 \le \gamma^{ij} S_{ij} < E$) hold identically.

---

## 2. Operator Splitting and Dual-Lagrangian Phase-Space Discretization

Following Hopkins (2026, arXiv:2611.23084), we Strang-split the three operators over a step $\Delta t$:
1. **Geodesic momentum kick $\mathcal{K}(\Delta t/2)$**: $\partial_t f + \partial_{u_i}(\dot{u}_i f) = 0$ at fixed $\bm{x}_a$, using the metric at $t^n$ for the first half-kick and $t^{n+1}$ for the second half-kick.
2. **Phase-space spatial transport $\mathcal{A}(\Delta t)$**: $\partial_t f + \partial_i (\dot{x}^i f) = 0$ on the moving MFM partition using the time-centered midpoint metric $(\text{met}_0 + \text{met}_1)/2$.
3. **Intra-cell relativistic collision operator $\mathcal{C}(\Delta t)$**: $\partial_t f = (\partial_t f)_{\rm coll}$ solved locally within each element $\Omega_a$.

### 2.1 Configuration-Space Meshless Finite-Mass (MFM) Partition

Around $N$ moving mesh-generating points $\bm{x}_a(t)$, define the MFM partition of unity using the 3D cubic spline kernel $W(\bm{r}, h_a)$ with compact support $H_a = 2 h_a$:
$$
\bar{n}_a \equiv \sum_c W(\bm{x}_{ca}, h_a) = V_a^{-1}, \qquad h_a^D \bar{n}_a = 1 \quad (\text{target } N_{\rm ngb} = 32 \text{ in 3D, } 4 \text{ in 1D}),
$$
where $\bm{x}_{ca} = \bm{x}_c - \bm{x}_a$ (with periodic wrapping when periodic BCs are active). Define the coordinate kernel-moment matrix
$$
\bm{E}_a = \sum_c (\bm{x}_{ca} \otimes \bm{x}_{ca})\,W(\bm{x}_{ca}, h_a).
$$
For isolated systems with free vacuum boundaries or interior excision surfaces, one-sided neighbor stencils can make $\bm{E}_a$ ill-conditioned. We normalize $\tilde{\bm{E}}_a = \bm{E}_a / (\sum_c \|\bm{x}_{ca}\|^2 W(\bm{x}_{ca}, h_a))$ and, whenever $\lambda_{\min}(\tilde{\bm{E}}_a)/\lambda_{\max}(\tilde{\bm{E}}_a) < \epsilon_{\rm cond}$ (default $10^{-3}$), apply regularized ridge stabilization $\bm{E}_a \to \bm{E}_a + \lambda_{\rm reg} \mathrm{Tr}(\bm{E}_a) \bm{I}$ (or fall back to zero gradients on exterior boundary elements) while preserving exact antisymmetry of the effective face area covectors:
$$
A_{ab,i} = V_a (\bm{E}_a^{-1} \bm{x}_{ba})_i W(\bm{x}_{ba}, h_a) + V_b (\bm{E}_b^{-1} \bm{x}_{ba})_i W(\bm{x}_{ba}, h_b), \qquad A_{ab,i} = -A_{ba,i}.
$$

### 2.2 Multi-Basis Moment Expansion in Canonical Momentum Space

Inside $\Omega_a$, approximate the domain-averaged distribution function by a mixture of $N_{\rm basis}$ momentum-Lagrangian basis functions $\tilde{g}_{a,\alpha}(\bm{u})$ normalized to $\int \tilde{g}_{a,\alpha}(\bm{u})\,\mathrm{d}^3 u = 1$:
$$
f_a(\bm{u}) \equiv \frac{1}{V_a}\int_{\Omega_a} f(\bm{x}, \bm{u})\,\mathrm{d}^3 x = D_a \sum_{\alpha=1}^{N_{\rm basis}} \varpi_{a,\alpha}\,\tilde{g}_{a,\alpha}(\bm{u}), \qquad \sum_{\alpha=1}^{N_{\rm basis}} \varpi_{a,\alpha} = 1.
$$
The 10 canonical conserved variables per basis are:
$$
m_{a,\alpha} = \varpi_{a,\alpha} D_a V_a, \qquad
P_{a,\alpha,i} = m_{a,\alpha} \bar{u}_{a,\alpha,i}, \qquad
\Pi_{a,\alpha,ij} = m_{a,\alpha}\left(\Sigma_{a,\alpha,ij} + \bar{u}_{a,\alpha,i}\bar{u}_{a,\alpha,j}\right).
$$
The primitive variables are $D_{a,\alpha} = m_{a,\alpha}/V_a$, $\bar{u}_{a,\alpha,i} = P_{a,\alpha,i}/m_{a,\alpha}$, and symmetric positive semi-definite covariance $\Sigma_{a,\alpha,ij} = \Pi_{a,\alpha,ij}/m_{a,\alpha} - \bar{u}_{a,\alpha,i}\bar{u}_{a,\alpha,j}$.

The mesh-generating point moves at the center-of-rest-mass coordinate velocity,
$$
\dot{x}_a^i = \frac{1}{m_a} \sum_\alpha m_{a,\alpha} \langle \dot{x}^i(\bm{x}_a, \bm{u}) \rangle_{a,\alpha},
$$
evaluated with the same symmetric positive-weight cubature used for kicks and stress-energy.

---

## 3. Relativistic One-Sided Vacuum Riemann Solver

Consider a face $ab$ with face center $\bm{x}_{f,ab} = \bm{x}_a + \psi_{ab}(\bm{x}_b - \bm{x}_a)$, $\psi_{ab} = \frac{h_b}{h_a+h_b}$, and interpolated midpoint ADM metric $(\alpha_f, \beta_f^i, \gamma_{ij,f})$.

### 3.1 Face-Aligned Orthonormal Triad and Causal Face Velocity

Compute the proper area element $\|A\|_\gamma = \sqrt{\gamma_f^{ij} A_{ab,i} A_{ab,j}}$ and unit normal covector $\hat{n}_i = A_{ab,i}/\|A\|_\gamma$. Construct a right-handed orthonormal triad $\{\hat{e}_{(1)}^i, \hat{e}_{(2)}^i, \hat{e}_{(3)}^i\}$ with $\hat{e}_{(1)}^i = \gamma_f^{ij}\hat{n}_j$ and $\gamma_{f,ij}\hat{e}_{(a)}^i\hat{e}_{(b)}^j = \delta_{ab}$ via Gram-Schmidt on coordinate axes (selecting the coordinate axis least aligned with $\hat{e}_{(1)}$). Denote coframe covectors $e^{(a)}_i = \gamma_{f,ij}\hat{e}_{(a)}^j$.

Define the normal-observer dimensionless face velocity:
$$
\beta_F \equiv \frac{(\beta_f^i + v_{F,ab}^i)\,\hat{n}_i}{\alpha_f}.
$$
Then the relative coordinate advection flux normal to the face simplifies identically to:
$$
(\dot{x}^i - v_{F,ab}^i)\,A_{ab,i} = \alpha_f\,\|A\|_\gamma \left(\frac{u_{(1)}}{W} - \beta_F\right),
$$
where $u_{(a)} = \hat{e}_{(a)}^i u_i$ and $W = \sqrt{1 + u_{(1)}^2 + u_{(2)}^2 + u_{(3)}^2}$. Notice that $|\beta_F| \ge 1$ occurs automatically inside horizons or rapidly shifting gauges:
- If $\beta_F \le -1$, $u_{(1)}/W - \beta_F > 0$ for all $\bm{u} \in \mathbb{R}^3$ (all characteristics flow $a \to b$).
- If $\beta_F \ge +1$, $u_{(1)}/W - \beta_F < 0$ for all $\bm{u} \in \mathbb{R}^3$ (zero outgoing flux from $a \to b$).
- If $|\beta_F| < 1$, particles leave $a \to b$ iff $u_{(1)} > u_{(1)}^\star(\bm{u}_\perp)$, where
  $$
  u_{(1)}^\star(\bm{u}_\perp) = \Gamma_F \beta_F m_\perp, \qquad \Gamma_F = \frac{1}{\sqrt{1 - \beta_F^2}}, \qquad m_\perp = \sqrt{1 + u_{(2)}^2 + u_{(3)}^2}.
  $$

### 3.2 Exact 1D-Sliced + 2D-Cubature Flux Integrals

Transform the reconstructed state $(D^*_{ab,\alpha}, \bar{u}^*_i, \Sigma^*_{ij})$ from side $a$ into the face triad:
$$
\bar{u}_{(a)} = \hat{e}_{(a)}^i \bar{u}^*_i, \qquad \Sigma_{\rm tet,(ab)} = \hat{e}_{(a)}^i \hat{e}_{(b)}^j \Sigma^*_{ij} = \begin{pmatrix} \sigma_\parallel^2 & \bm{c}^T \\ \bm{c} & \bm{\Sigma}_{\perp\perp} \end{pmatrix}.
$$
Factor $\bm{\Sigma}_{\perp\perp} = \bm{L}_\perp \bm{L}_\perp^T$ via 2D Cholesky with zero-variance guard; compute $\bm{g} = \bm{L}_\perp^{-1}\bm{c}$ (with $g_k = 0$ where $L_{\perp,kk} = 0$) and conditional parallel variance
$$
s_\parallel^2 = \max\!\left(\sigma_\parallel^2 - \|\bm{g}\|^2,\, 0\right).
$$
Writing $\bm{u}_\perp = \bar{\bm{u}}_\perp + \bm{L}_\perp \bm{\eta}$ for standardized transverse variables $\bm{\eta} = (\eta_2, \eta_3)$, the conditional mean along $u_{(1)}$ is $\mu_\parallel(\bm{\eta}) = \bar{u}_{(1)} + \bm{g}^T\bm{\eta}$.

Integrating over $\bm{\eta}$ with $Q_\perp$ positive-weight tensor-product nodes $(\bm{\eta}_r, w_r)$ (Gauss-Legendre on $[-\sqrt{3},\sqrt{3}]^2$ for the compactly supported Top-Hat basis, or Gauss-Hermite for the Gaussian basis), each transverse slice $r$ reduces to a 1D integral over $u \equiv u_{(1)}$ with $W(u) = \sqrt{m_\perp^2 + u^2}$. For the Top-Hat basis on $[a_r, b_r] = [\mu_\parallel - \sqrt{3} s_\parallel, \mu_\parallel + \sqrt{3} s_\parallel]$, let $u_{\rm lo} = \max(a_r, u_{(1)}^\star)$. If $u_{\rm lo} < b_r$, we need the moments
$$
I_k(u_{\rm lo}, b_r) \equiv \frac{1}{2\sqrt{3} s_\parallel}\int_{u_{\rm lo}}^{b_r} u^k \left(\frac{u}{W(u)} - \beta_F\right)\mathrm{d}u, \qquad k \in \{0, 1, 2\},
$$
whose exact closed-form antiderivatives are:
$$
\int \frac{u}{W}\,\mathrm{d}u = W, \qquad
\int \frac{u^2}{W}\,\mathrm{d}u = \frac{1}{2}\left[u W - m_\perp^2 \operatorname{arsinh}\!\left(\frac{u}{m_\perp}\right)\right], \qquad
\int \frac{u^3}{W}\,\mathrm{d}u = \frac{1}{3} W (u^2 - 2 m_\perp^2).
$$
When $(b_r - u_{\rm lo}) < 0.25\,m_\perp$ (the cold or near-cutoff limit where difference-of-antiderivatives loses digits), we evaluate $I_k$ via 4-point Gauss-Legendre quadrature on $[u_{\rm lo}, b_r]$, accurate to $< 10^{-15}$ relative error! When $s_\parallel = 0$ (infinitely cold sheet), if $\mu_\parallel > u_{(1)}^\star$ the slice yields $I_k = \mu_\parallel^k (\mu_\parallel/W(\mu_\parallel) - \beta_F)$, else $0$.

The outgoing conserved fluxes in the face triad are:
$$
F^{(m)}_{(a\to b)} = \alpha_f \|A\|_\gamma D^* \sum_r w_r I_0, \qquad
F^{(P)}_{(a\to b),(1)} = \alpha_f \|A\|_\gamma D^* \sum_r w_r I_1, \qquad
F^{(P)}_{(a\to b),(2,3)} = \alpha_f \|A\|_\gamma D^* \sum_r w_r u_{\perp,(2,3)} I_0,
$$
$$
F^{(\Pi)}_{(a\to b),(11)} = \alpha_f \|A\|_\gamma D^* \sum_r w_r I_2, \qquad
F^{(\Pi)}_{(a\to b),(1\perp)} = \alpha_f \|A\|_\gamma D^* \sum_r w_r u_{\perp} I_1, \qquad
F^{(\Pi)}_{(a\to b),(\perp\perp)} = \alpha_f \|A\|_\gamma D^* \sum_r w_r u_{\perp} \otimes u_{\perp} I_0,
$$
which are rotated back to coordinate components via $e^{(a)}_i$: $F^{(P)}_i = e^{(a)}_i F^{(P)}_{(a)}$ and $F^{(\Pi)}_{ij} = e^{(a)}_i e^{(b)}_j F^{(\Pi)}_{(ab)}$.

### 3.3 Exact Mass-Preserving Face Velocity $\beta_F$

The MFM zero-net-mass-flux condition is
$$
\Phi(\beta_F) \equiv \sum_\alpha F^{(m)}_{a\to b,\alpha}(\beta_F) + \sum_\beta F^{(m)}_{b\to a,\beta}(\beta_F) = 0,
$$
where $F^{(m)}_{b\to a,\beta}(\beta_F)$ is evaluated with reversed normal $-\hat{n}_i$ and reversed $\beta_F \to -\beta_F$ (subtracting from $b$'s mass). Because $\partial F^{(m)}_{a\to b}/\partial \beta_F \le 0$ and $-\partial F^{(m)}_{b\to a}/\partial \beta_F \le 0$, $\Phi(\beta_F)$ is strictly monotonically decreasing whenever at least one basis has $D^* > 0$, guaranteeing a unique root $\beta_F \in (-1, 1)$ (or a clamped boundary value if all mass is on one side) found to $10^{-13}$ by bracketed Brent's method. Thus cell rest mass $m_a = \sum_\alpha m_{a,\alpha}$ is conserved to machine precision!

---

## 4. Reconstruction, Covariant Basis Pairing, and Realizability Repair

1. **Matched-Basis MLS Gradients and Limiters**: Using the prior-step pairing $\alpha(b)$ on neighbors $b$, compute $\nabla Q_{a,\alpha} = \phi^Q_{a,\alpha} \bm{E}_a^{-1} \sum_b [Q_{b,\alpha(b)} - Q_{a,\alpha}]\bm{x}_{ba} W(\bm{x}_{ba}, h_a)$ for $Q \in \{D_\alpha, \bar{u}_{\alpha,i}, \Sigma_{\alpha,ij}\}$. Apply Barth-Jespersen limiting to $D_\alpha$, Hopkins velocity-crossing Barth-Jespersen limiting ($\epsilon_v = 0.1$, replacing $|\bm{v}|^2$ norms with $\gamma$-norms $\|\bm{u}\|_\gamma^2 = \gamma^{ij} u_i u_j$ and $\mathrm{Tr}_\gamma(\bm{\Sigma}) = \gamma^{ij} \Sigma_{ij}$) to $\bar{u}_{\alpha,i}$, and bisection-SPD Barth-Jespersen limiting (`SymEig3` check on $\Sigma^*$) to $\Sigma_{\alpha,ij}$.
2. **Covariant Face-Rest-Frame Pairing Cost**: When $|\beta_F| < 1$, Lorentz-boost reconstructed tetrad 4-momenta $(W^*_\alpha, \bm{u}^*_\alpha)$ into the face rest frame ($\tilde{u}_{(1)} = \Gamma_F(u_{(1)} - \beta_F W)$, $\tilde{u}_\perp = u_\perp$). Evaluate
   $$
   C^u_{\alpha\beta} = \frac{\|\tilde{\bm{u}}_\alpha - \tilde{\bm{u}}_\beta\|^2}{\|\tilde{\bm{u}}_\alpha\|^2 + \|\tilde{\bm{u}}_\beta\|^2 + 2|\tilde{\bm{u}}_\alpha\cdot\tilde{\bm{u}}_\beta| + \mathrm{Tr}_\gamma(\Sigma^*_\alpha) + \mathrm{Tr}_\gamma(\Sigma^*_\beta)}, \qquad
   C^D_{\alpha\beta} = \frac{|D^*_{a,\alpha} - D^*_{b,\beta}|}{D^*_{a,\alpha} + D^*_{b,\beta} + 10^{-3} D^*_a},
   $$
   and $C_{\alpha\beta} = C^u_{\alpha\beta} + \lambda_D C^D_{\alpha\beta}$ ($\lambda_D = 0.25$), augmented by Hopkins's empty-basis sigmoid reweighting $C^{\rm eb}_{\alpha\beta}$ ($\epsilon_\tau = 0.04$, $\epsilon_{\rm eb} = 0.01$) and one-sided independent pairing $\beta(\alpha) = \arg\min_\beta C^{\rm eb}_{\alpha\beta}$. When $|\beta_F| \ge 1$, evaluate $C^u_{\alpha\beta}$ directly in the unboosted normal-observer orthonormal tetrad.
3. **Realizability Repair $D$**: After every drift or kick update, apply intra-cell conservative mass-floor redistribution ($\epsilon_m = 10^{-12}$), `SymEig3` positive-definite projection ($\epsilon_S = 10^{-12}$), and conservative EQMOM merge/split when near-degenerate bases arise, preserving total $(m_a, P_{a,i}, \Pi_{a,ij})$ to machine precision.

---

## 5. Positive-Weight Cubature Geodesic Kick and Stress-Energy

For each active basis $(a, \alpha)$ with $m_{a,\alpha} > 0$:
1. Factor $\Sigma_{a,\alpha,ij} = L_{ik} L_{jk}$ (`Chol3`, with zero-eigenvalue fallback if cold).
2. Generate $Q$ positive-weight cubature points $\bm{u}_q = \bar{\bm{u}}_{a,\alpha} + \bm{L}\bm{\xi}_q$ with $\sum_q w_q = 1$, $\sum_q w_q \bm{\xi}_q = \bm{0}$, $\sum_q w_q \bm{\xi}_q \otimes \bm{\xi}_q = \bm{I}$ ($2^3=8$ or $3^3=27$ Gauss-Legendre points on $[-\sqrt{3},\sqrt{3}]^3$; 1-point shortcut when $\mathrm{Tr}_\gamma(\Sigma) < 10^{-26}$).
3. **Geodesic Kick $\mathcal{K}(\Delta t)$**: Push each $\bm{u}_q$ at fixed $\bm{x}_a$ over $\Delta t$ by fixed-point implicit midpoint integration of $\dot{u}_i$:
   $$
   u_{q,i}^{n+1} = u_{q,i}^n + \Delta t\left[-W(\bar{\bm{u}}_q)\partial_i\alpha + \bar{u}_{q,j}\partial_i\beta^j + \frac{\alpha}{2 W(\bar{\bm{u}}_q)}\bar{u}_q^l\bar{u}_q^m\partial_i\gamma_{lm}\right], \quad \bar{\bm{u}}_q = \frac{1}{2}(\bm{u}_q^n + \bm{u}_q^{n+1}).
   $$
   Reassemble $\bar{\bm{u}}^{n+1} = \sum_q w_q \bm{u}_q^{n+1}$ and $\Sigma^{n+1} = \sum_q w_q (\bm{u}_q^{n+1}-\bar{\bm{u}}^{n+1})\otimes(\bm{u}_q^{n+1}-\bar{\bm{u}}^{n+1})$ (manifestly SPD!).
4. **Stress-Energy & Drift Velocity**: Evaluate
   $$
   (\mathcal{E}_{a,\alpha}, P_{a,\alpha,i}, \mathcal{S}_{a,\alpha,ij}) = m_{a,\alpha}\sum_q w_q \left(W_q, u_{q,i}, \frac{u_{q,i}u_{q,j}}{W_q}\right), \qquad
   \langle \dot{x}^i \rangle_{a,\alpha} = \sum_q w_q \left(\frac{\alpha\gamma^{ij}u_{q,j}}{W_q} - \beta^i\right),
   $$
   where $W_q = \sqrt{1 + \gamma^{ij}(\bm{x}_a) u_{q,i} u_{q,j}}$. Deposit $(\mathcal{E}_a, P_{a,i}, \mathcal{S}_{a,ij})$ onto AthenaK's `Tmunu` mesh via B-spline clouds (CIC/TSC/PCS) and conservative AMR restriction, filter if requested, and divide by $\sqrt{\gamma}$ to obtain $(E, S_i, S_{ij})$.

---

## 6. Relativistic Maxwell-Jüttner BGK Collision Operator and HLLC Blend

Within cell $a$ (with coordinate volume $V_a$ and metric $\gamma_{ij}(\bm{x}_a)$), form the cell-integrated stress-energy moments $(m_a, P_{a,i}, \mathcal{E}_a)$ using the cubature points of all bases. Transform to the local orthonormal tetrad $\hat{e}_{(m)}^i$: $P_{(0)} = \mathcal{E}_a$, $P_{(m)} = e^i_{(m)} P_{a,i}$.
- Compute invariant mass $M_{\rm inv} = \sqrt{P_{(0)}^2 - \|\bm{P}_{\rm tet}\|^2}$ and fluid 4-velocity $U_{\rm cm}^{(0)} = P_{(0)}/M_{\rm inv}$, $U_{\rm cm}^{(m)} = P_{(m)}/M_{\rm inv}$.
- Lorentz-boost every cubature point to the center-of-momentum (COM) frame: $W' = U_{\rm cm}^{(0)} W - \bm{U}_{\rm cm}\cdot\bm{u}_{\rm tet}$, $\bm{u}' = \bm{u}_{\rm tet} + \left(\frac{\bm{U}_{\rm cm}\cdot\bm{u}_{\rm tet}}{U_{\rm cm}^{(0)}+1} - W\right)\bm{U}_{\rm cm}$. Note $\sum_q w_q W'_q = M_{\rm inv}/m_a \equiv \bar{W}_{\rm com}$ and $\sum_q w_q \bm{u}'_q = \bm{0}$.
- Invert the relativistic Synge-EOS specific energy relation $\bar{W}_{\rm com}(\theta) = \frac{K_3(1/\theta)}{K_2(1/\theta)} - \theta$ (exact scaled Bessel $K_n e^{1/\theta}$ + Newton-Raphson; $\theta = k_B T/\mu_p$, adiabatic index $\Gamma_{\rm ad} \in [4/3, 5/3]$, specific enthalpy $h_{\rm rel} = K_3/K_2$) for dimensionless temperature $\theta$.
- Compute proper rest-mass density $n_a \mu_p = m_a / (V_a \sqrt{\gamma_a} U_{\rm cm}^{(0)})$ and exact hard-sphere Maxwell-Jüttner collision rate (Israel 1963 / Cercignani-Kremer):
  $$
  \nu_a = n_a \sigma \langle v_{\rm rel} \rangle_{\rm MJ} = \frac{m_a}{V_a \sqrt{\gamma_a} U_{\rm cm}^{(0)}} \left(\frac{\sigma}{\mu_p}\right) \frac{4\theta^2 + 2\theta + \cdots}{K_2(1/\theta)^2} \to \frac{m_a}{V_a\sqrt{\gamma_a}U_{\rm cm}^{(0)}}\left(\frac{\sigma}{\mu_p}\right) \mathcal{R}_{\rm MJ}(\theta),
  $$
  where $\mathcal{R}_{\rm MJ}(\theta) = \frac{2\theta e^{-2/\theta}(1 + 2\theta + \dots)}{K_2(1/\theta)^2}$ smoothly bridges $\sqrt{16\theta/\pi}$ (non-relativistic $\theta \ll 1$) to $1$ (ultra-relativistic $\theta \gg 1$) via the exact analytical integral $\int_0^\infty \dots$.
- Apply convex COM-frame BGK relaxation with $\eta_a = 1 - \exp(-\nu_a \Delta\tau_a)$ ($\Delta\tau_a = \alpha_a \Delta t / U_{\rm cm}^{(0)}$), targeting the isotropic Maxwell-Jüttner covariance $\sigma_{\rm eq}^2(\theta)\bm{I}$ with $\sigma_{\rm eq}^2 = \frac{1}{3}(\overline{u'^2})_{\rm MJ} = \theta h_{\rm rel}(\theta)$. To enforce exact conservation of $(m_a, P_{a,i}, \mathcal{E}_a)$ to machine precision ($10^{-15}$), perform a 3-iteration 1D Newton solve on a common dispersion scale $s$ for the COM cubature energy $\sum_{\alpha,q} m_{a,\alpha} w_q \sqrt{1 + \|\bm{u}_{\alpha,q}'(s)\|^2} = \bar{W}_{\rm com} m_a$, then boost back to coordinate momenta $\bm{u}_{a,\alpha}$.
- **Short-mean-free-path HLLC Blend**: When $\Delta x_{ab}/\lambda_{\rm MFP} \sim 1$ or larger, blend the collisionless per-basis face flux with the relativistic HLLC fluid flux (solved in the normal-observer rest frame using the Synge EOS pressure $P_{\rm fluid} = n_{\rm rest}\mu_p\theta$ and sound speed $c_s^2$) via $w_c = \exp(-\Delta x_{ab}/\lambda_{\rm MFP})$, identically conserving $(m_a, P_{a,i}, \mathcal{E}_a)$ across all Knudsen numbers!

---

## 7. Non-Relativistic Limit Verification

In the Newtonian limit ($|\beta^i|, |\alpha - 1|, |\gamma_{ij} - \delta_{ij}| \ll 1$, $|\bm{u}| \ll 1$), $W \to 1 + \frac{1}{2}|\bm{u}|^2$, $\dot{x}^i \to v^i$, $u_{(1)}^\star \to v_{F,n}$, $m_\perp \to 1$, and our exact antiderivatives reduce to:
$$
\int_{v_{\rm lo}}^{b_r} (u - v_{F,n})\,\mathrm{d}u = \frac{1}{2}(b_r - v_{F,n})^2 - \frac{1}{2}(v_{\rm lo} - v_{F,n})^2,
$$
recovering Hopkins (2026) Eq. (44)–(45) identically!
