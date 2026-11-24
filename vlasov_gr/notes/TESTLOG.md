# GR-LBV Development & Benchmark Test Log

Prediction-first verification log for extending Hopkins (2026) 6+1D Lagrangian-basis Vlasov/Boltzmann method to the 3+1 Einstein-Vlasov equations in `athenak-nr-nrpic` on `gb204` (NVIDIA B200 183 GiB, 15 CPUs, branch `feat/gr-lagrangian-vlasov`).

---

## Verified Baseline Stages (Stages 1–3)

### Stage 1 — Python 1D/3D GR-LBV Prototype (`e7ea72a3`)
- **Verified**: `pytest -v tests/test_vlasov_gr.py` (9/9 passed); Newtonian Hopkins limit exact to machine precision (`< 1e-13`); curved-metric flux vs 3D numerical integral `< 1e-12`; Kerr `a=0.9M` 27-point cubature kick & stress-energy parity; Anderson-Witting relativistic BGK exact $(D, P_i, E_{\rm lab})$ conservation and Synge equation-of-state recovery; 1D two-stream + second-order spatial convergence; exact Taub shock match (`< 1%` at `N=200`); 1D empty-slot injection (`N_b=4`); 3D periodic two-stream.
- **Diagnostic**: `vlasov_gr/notes/figs/diag_stage1_python_1d.png` (inspected).

### Stage 2 — Standalone C++/CUDA Kernels (`93f8eb3e`, re-verified after `FaceTriad` update)
- **Verified (`g++` & `nvcc -arch=sm_100`)**: Standalone C++ self-tests and Python parity across all 10 kernel families:
  - $K_2(z)e^z$: `3.458e-15`, $K_3(z)e^z$: `6.191e-15`, Synge $c_s^2$: `3.219e-12`, $\langle v_{\rm Mol}\rangle$: `6.607e-15`
  - Curved-metric Top-Hat flux across $\beta_F \in [-1.2, 1.2]$: `7.975e-15`
  - $\beta_F$ Brent root-finder: `1.110e-16`, Covariant pairing $C^{\rm eb}$: `1.110e-16`
  - Kerr $a=0.9M$ cubature kick (`u`, `Sigma`): `4.484e-16 / 5.472e-17`
  - Anderson-Witting BGK: `1.554e-15`, Relativistic HLLC flux: `5.407e-14`
- **Diagnostic**: `vlasov_gr/notes/figs/diag_stage2_kernel_parity.png` (inspected).

### Stage 3 — AthenaK GPU/OpenMP Solver Parity & Kerr Regression (`051db59f`)
- **Verified (`$SCRATCH_ROOT/build_gpu` & `$SCRATCH_ROOT/build_omp`, `5^3 = 125` elements, $N_b = 2$, $t = 0.10$)**:
  - AthenaK B200 GPU vs Python 3D MFM max abs errors: $x$: `2.220e-16`, $m$: `3.469e-18`, $\bar{u}$: `3.109e-15`, $\Sigma$: `1.166e-15`.
  - AthenaK OpenMP CPU (4 threads) vs B200 GPU max abs diffs: $x$: `1.110e-16`, $m$: `3.903e-18`, $\bar{u}$: `2.776e-15`, $\Sigma$: `9.010e-16`.
  - OpenMP 4-thread determinism (`OMP4a vs OMP4b`): $x$: `1.110e-16`, $m$: `2.168e-18`, $\bar{u}$: `2.109e-15`, $\Sigma$: `8.591e-16`.
  - Existing NRPIC Kerr $a=0.9M$ geodesic regression (`time/tlim=20.0`): `2000` cycles, `push_unconverged = 0`, `push_maxit = 4`.
- **Diagnostic**: `vlasov_gr/notes/figs/diag_stage3_athenak_parity.png` (inspected).

---

## Stage 4a Predictions & Results (Suites 1, 2, 3)

### Suite 1 — 3D Flat Periodic Relativistic Vlasov-Boltzmann (B200 GPU)

#### 1A: Boosted Relativistic Two-Stream ($|u| \in \{0.8, 1.5, 3.0\}$, $C^{\rm eb}$ vs `v_only`)
- **Prediction**:
  - Covariant pairing (`vlasov_pair_mode = covariant`, $C^{\rm eb}$) preserves distinct crossing stream identities cleanly across $t \in [0, 0.4]$ even at ultrarelativistic boost $|u| = 3.0$ where 3-velocities saturate near $c$, keeping total mass error $|\Delta M/M_0| < 10^{-13}$, momentum error $|\Delta P|/P_0 < 10^{-12}$, and maintaining crisp stream separation (no artificial mid-velocity collapse).
  - Naive Euclidean 4-velocity pairing (`v_only`) without frame-velocity matching or donor-occupancy weighting mis-pairs inhomogeneous / near-empty stream intersections at high $|u|$ where $\Delta u^i$ along the boost direction mixes unequally boosted components, yielding elevated spurious stream broadening / energy drift compared to `covariant`.

#### 1B: Warm Relativistic Density Wave ($8^3, 12^3, 16^3, 24^3$, Brent vs `analytic_vf`)
- **Prediction**:
  - Comparing $N_{\rm lat} \in \{8, 12, 16\}$ against $24^3$ reference at $t = 0.08$ in the smooth warm regime ($\sigma_u = 0.25$), spatial $L_1(D)$ and $L_1(E)$ errors decrease with empirical convergence order $p \in [1.8, 2.2]$ (second-order MFM reconstruction with smooth TVD/BJ limiting).
  - Exact Brent $\beta_F$ solve agrees closely with `vlasov_analytic_vf = true` at $\sigma_u = 0.25$ (relative difference $< 5 \times 10^{-3}$ in density, larger under strong relativistic bulk boost), with $|\Delta M/M_0| < 10^{-13}$ in both modes.

#### 1C: Empty-Slot Injection ($N_b = 4$, half-empty initial basis)
- **Prediction**:
  - Left-half ($x < 0.5$) streams in bases `0, 1` and right-half ($x \ge 0.5$) streams in bases `2, 3` stream across $x=0.5$ and $x=0$ without NaNs, negative masses, or non-SPD $\Sigma$.
  - Populated slot count ($m_{a,\alpha} > 10^{-8}$) grows monotonically from initial $2N$ toward $\ge 3N$ as crossing elements populate previously empty basis slots, with $|\Delta M/M_0| < 10^{-13}$ and $|\Delta \mathbf{P}| < 10^{-12}$.

#### 1D: 3D Relativistic Colliding Beams / Taub Double Shock ($\sigma/\mu \in \{0, 2, 10^4\}$, $64 \times 5 \times 5$)
- **Prediction**:
  - $\sigma/\mu = 0$: free collisionless interpenetration with overlapping central plateau $D \approx 2 D_0$ and zero shock jump.
  - $\sigma/\mu = 2$: finite mean free path relaxation zone bridging collisionless overlap and fluid shock.
  - $\sigma/\mu = 10^4$: instantaneous Maxwell-Juttner thermalization + HLLC flux produces symmetric outward-propagating shocks whose post-shock state $(D_{\rm post}, e_{\rm post}, p_{\rm post}, v_{\rm shock})$ matches the exact analytic Taub shock (`exact_taub_shock`) within $2\%$.

### Suite 2 — Kerr $a = 0.9 M$ Warm Sheared Inclined Cloud (`kerr_schild`)
- **Prediction**:
  - Starting at $\mathbf{x}_0 = (6.0, 0.0, 1.5)\,M$ ($r \approx 6.18\,M$, radius $R_{\rm cl} = 1.0\,M$, warm isotropic $\sigma_u = 0.06$, prograde inclined orbit, $t \in [0, 30]\,M$), GR-LBV ($N \in \{512, 1412, 3052\}$ elements) tracks the bulk trajectory, tidal shearing, and spin-$a = 0.9M$ frame dragging cleanly in agreement with $10^4$ NRPIC `midpoint` tracers.
  - Total Killing energy $\sum E_\infty$ and axial angular momentum $\sum L_z$ remain bounded to $< 10^{-3}$ relative drift (arising purely from warm stress-gradient work across finite cloud width + second-order time splitting), while density reconstruction on the orbital plane is smooth with orders-of-magnitude lower point-to-point Poisson scatter than the $10^4$-particle NRPIC Monte Carlo cloud.

### Suite 3 — Full-GR Oppenheimer-Snyder Dust Collapse ($R_0 = 5 M$, Z4c + AMR + FastFlow)
- **Prediction**:
  - With `vlasov_bnd_detect = true`, `deposit = true`, `nfilter = 1`, `alpha_exc = 0.1`, $N = 9328$ (and $N = 4168$) lattice elements match the exact analytical Oppenheimer-Snyder cycloid $R(\tau)$ and central density $\rho_c(\tau)/\rho_0$ to $< 1\%$ until boundary gauge effects / singularity-avoiding 1+log trumpet freeze around $\tau \sim 3\text{--}3.5\,M$, closely following NRPIC's `9328`-particle evolution.
  - Central lapse $\alpha_c(\tau)$ follows the Staley et al. bound $\alpha_{\rm LL} = 1 + 6\ln(R/R_0)$ until $\tau \approx 2.6\,M$, drops smoothly below $0.1$, and triggers full excision around $t \approx 19\text{--}20\,M$.
  - FastFlow apparent horizon is detected around $t_{\rm AH} \approx 16.0\text{--}16.5\,M$ with $M_{\rm AH}/M$ converging toward $1.00$ (within $\sim 1\text{--}3\%$ mesh/horizon-finder discretization as documented for NRPIC OS AMR), while Hamiltonian and momentum constraint $L_2$ norms $\|\mathcal{H}\|_2, \|\mathcal{M}\|_2$ improve with $N_{\rm elem}$ and track or beat matched-$N$ NRPIC `midpoint`.

### Verified Stage 4a Results & Debug Resolution (`gb204` B200 GPU)

Full root-cause debugging of Stage 1 Panel (d) and Stage 4a Panels (b, d) is documented in [02_debug_report_stage1_stage4a.md](file:///home/schmidt/ssci-haiyangw/nrpic/vlasov_gr/notes/02_debug_report_stage1_stage4a.md), and all four diagnostics are rendered in `/cz-figure-style`:
- [diag_stage1_python_1d.png](file:///home/schmidt/ssci-haiyangw/nrpic/vlasov_gr/notes/figs/diag_stage1_python_1d.png): Stage 1 Panel (d) Taub double shock ($\sigma/\mu = 500$, $u_0 = \pm 1$) central dip resolved (`D_mid`: `3.4212` [$-17.39\%$] $\to$ **`4.1142` [$-0.66\%$]** vs exact `4.1414`, symmetric `D31=4.1145, D32=4.1139`, plateau std `0.2968 -> 0.0436`, `dM=0`, `dE=7.85e-16`) via exact Valencia Synge C2P, symmetric HLLC contact branch, `lim_eps_v=0` in shocks, and harmonic-$c_s$ Noh thermal conduction (`noh_kappa = 0.5`).
- [diag_stage2_kernel_parity.png](file:///home/schmidt/ssci-haiyangw/nrpic/vlasov_gr/notes/figs/diag_stage2_kernel_parity.png): C++/CUDA (`sm_100`) vs Python 10-kernel parity (`cs2 = 3.219e-12`, `MJ BGK = 1.221e-15`, `Rel. HLLC = 2.824e-14`); `pytest -v tests/test_vlasov_gr.py` 10/10 PASSED.
- [diag_stage3_athenak_parity.png](file:///home/schmidt/ssci-haiyangw/nrpic/vlasov_gr/notes/figs/diag_stage3_athenak_parity.png): AthenaK GPU/OpenMP vs Python parity (`~3e-15`) and NRPIC Kerr regression.
- [diag_stage4a_suites123.png](file:///home/schmidt/ssci-haiyangw/nrpic/vlasov_gr/notes/figs/diag_stage4a_suites123.png):
  - **Suite 1A** (`|u| = 0.8, 1.5, 3.0`, `cpu ~2.38-2.50 s`): `covariant` $C^{\rm eb}$ achieves `sep/sep0 = [1.031, 1.028, 1.004]`, `dM = 0`, `dE = [1.74e-7, 2.37e-5, 1.83e-5]`, whereas `v_only` degrades separation to `[0.921, 0.903, 0.889]`.
  - **Suite 1B** (`8^3..24^3`): `L1(D) = [5.348e-5, 2.713e-5, 1.713e-5]`, empirical order `p_fit = 1.64`; Brent vs `analytic_vf` max diff `5.47e-4` (`16^3`), `6.69e-4` (boosted $u_x=1.5$).
  - **Suite 1C** (`Nb = 4, 12^3`, `cpu = 3.53 s`): populated slots grow `3456 -> 6912 / 6912`, `min Sig eig = 9.58e-15`, `dM = 0`, `dP = 1.01e-15`.
  - **Suite 1D** (`96x5x5`): `sig=15` (`cpu = 18.08 s`) dispersion eliminated via unconditional `use_contact_beta_F = true`: `m/m0 = 1.000000` (`std = 7.68e-13`), central $D$ std `1.216 -> 0.0522` ($23.3\times$); `sig=1e4` (`cpu = 11.45 s`) gives `D_cent = 4.0671` vs exact `4.1006` (`-0.82%`), `e_cent = 4.7509` vs `4.7820` (`-0.65%`); `sig=0`: `5.72 s`, `sig=2`: `12.08 s`.
  - **Suite 2** (Kerr $a=0.9M$, grazing orbit $r_{\rm min}=1.702M > r_+ = 1.436M$, $t=30M$):
    - `N=552`: `dE=5.264e-5`, `dLz=2.252e-4`, `dM=2.22e-16`, `cpu = 9.41 s`
    - `N=1472`: `dE=5.475e-5`, `dLz=2.001e-4`, `dM=2.22e-16`, `cpu = 28.69 s`
    - `N=3112`: `dE=5.824e-5`, `dLz=1.561e-4`, `dM=1.11e-16`, `cm_diff=7.93e-3`, azimuthal arc roughness `0.0211` vs NRPIC MC10k `0.2319` (`cpu = 64.93 s` vs NRPIC `N=10^4` `~1.37 s`, `dE=3.421e-8`, `dLz=1.326e-13`).
  - **Suite 3** (Full-GR OS collapse $R_0=5M$, Z4c + AMR + FastFlow):
    - `s3_grlbv_n20` (`cpu = 183.83 s`): `t_AH = 16.35M`, `M_AH_fin = 0.9942M`, `t_exc99 = 19.71M`, `||H||_max = 4.464`, `||M||_max = 1.948`.
    - `s3_grlbv_n26` (`cpu = 198.58 s`): `t_AH = 16.39M`, `M_AH_fin = 0.9997M`, `t_exc99 = 19.70M`, `||H||_max = 1.857`, `||M||_max = 0.834` (matching `s3_nrpic_n26` `cpu = 135.86 s`, `M_AH_fin = 0.9997M`, `||H||_max = 1.896`, `||M||_max = 0.878`).


### Verified Tier-1 GPU Optimization & Hybrid `SCP-AP` Results (`gb204` B200 GPU)

Full engineering report: [03_hybrid_scp_ap_speed_accuracy.md](file:///home/schmidt/ssci-haiyangw/nrpic/vlasov_gr/notes/03_hybrid_scp_ap_speed_accuracy.md) and summary diagnostic [diag_hybrid_speed_accuracy.png](file:///home/schmidt/ssci-haiyangw/nrpic/vlasov_gr/notes/figs/diag_hybrid_speed_accuracy.png).

- **Parity & Unit Verification (post-Step-1 fixes)**:
  - Standalone `vlasov_kernel_test.cpp` (`g++` + `nvcc -arch=sm_100`), Stage 2 kernel parity (`<= 3.22e-12`), Stage 3 AthenaK GPU/OMP/Python parity (`dx <= 1.110e-16, du <= 1.998e-15, dS <= 8.604e-16`), `pytest -v tests/test_vlasov_gr.py` **10/10 passed in 183.60 s**.
  - Back-to-back B200 determinism & parity on `s1d_sig15`: `row1_dh = 3.419e-15` vs Stage 4a baseline; `nsys` confirms 100% of kernels run on `MetricKind = 0` (flat Minkowski via `KerrSchildLight{0.0, 0.0}`) and `cuda_parallel_launch_local_memory` with `0` geodesic kick calls.
- **Tier-1 Opt MFM Speedups**:
  - `s2_grlbv_n18` ($N=3112, t=30M$): `65.99 s -> 5.62 s` wall (`4.57 s` compute) = **`11.7x` wall speedup**, `dx = 7.122e-7, dm = 3.250e-15` vs Stage 4a.
  - `s1d_sig15` ($N=2400, N_b=2, 462$ substeps): `19.38 s -> 3.52 s` wall (`2.37 s` compute) = **`5.5x` wall speedup**.
- **Hybrid `vlasov_hybrid` (`SCP-AP`) Benchmark Suite**:
  - **Suite 1D `sig=0`**: `s1d_hybrid_sig0` ($33{,}600$ SCP packets) `wall = 2.238 s` (`1.185 s` comp), `dM = 0.00`, `dE = 0.00`, relative $L_1$ vs 512-node exact = **`0.0615`** (`4.7x` better than `Opt MFM` `0.2878`); `sig = 2, 15, 1e4` auto-dispatch to Opt AP-MFM (`D_plat = 4.0528` vs Taub `4.1006`).
  - **Suite 2 Kerr $a=0.9M$ ($t=30M$, vs `MC 100k` truth)**: `s2_hyb_n18_q14` ($43{,}568$ packets) runs in **`1.55 s` wall (`0.27 s` comp; `42.6x` wall / `244x` comp speedup vs baseline MFM)** with `|dE/E0| = 3.04e-8`, `|dLz/Lz0| = 1.28e-13`, `R_hist = 0.0846` (vs `MC 10k` `0.2236`, `Opt MFM` `0.3616`, Truth `0.0809`), `L1_hist = 0.0418` (vs `MC 10k` `0.0695`), `cm_err = 3.56e-3` (vs `MC 10k` `1.33e-2`).
  - **Suite 3 OS Collapse**: `s3_hyb_n26` (`138.41 s` wall / `137.19 s` comp) matches `s3_nrp_n26` (`136.59 s` / `135.39 s`) and `s3_opt_n26` (`151.77 s` / `150.31 s`) identically at `t_AH = 16.3894`, `M_AH = 0.99969`, `t_exc99 = 19.7108`.
  - **Strong Scaling (`50` cycles)**: `Hybrid SCP-AP` scales from `7,728` (`0.006 s`) to `200,592` packets (`0.012 s`), achieving **`68.8x`** lower compute time at `N_lat = 30` than `Opt MFM` (`0.825 s` for `14,328` elements).


### Verified Iteration 2 — Conservative Relativistic Cell-BGK Crossover (`gb204` B200 GPU, Milestone #3)

- Implemented `vlasov_pbgk_kernels.hpp` (`LorentzBoostMom`, unified Gamma-mixture `SampleMaxwellJuttner`, scalar Newton+bisection `ProjectCellFourMomentumT`) and `vlasov_pbgk.cpp` (`CollideScpPbgk`) wired as `vlv_coll` in `Particles::AssembleTasks`.
- Kernel self-tests (`vlasov_kernel_test.cpp`, Tests 1–9) **PASSED**: Test 9 `SampleMaxwellJuttner` moments across $\Theta \in \{10^{-4}, 0.1, 1, 5\}$ agree within $\le 5.5\times 10^{-3}$; unequal-weight `ProjectCellFourMomentumT` yields `rel_dE = 2.347e-16`, `rel_dP = 6.062e-17`.
- **Suite 1D Optical-Depth Crossover (`run_pbgk_crossover.py`, `pbgk_crossover.npz`, `u_0 = \pm 0.60`, `sig_v = 0.03`)**:
  - `vlasov_pbgk` (`256x4x4`, `49,152` $S^2$ packets, `cell_factor = 2`): `dM/M = 0.00`, `dE/E <= 1.83e-14` across ALL $\sigma/\mu \in \{0, 2, 15, 10^4\}$, near-constant wall time (`2.670s, 2.659s, 2.870s, 3.589s`), and Taub double-shock jump errors `1.87%` ($D_2$) and `1.68%` ($e_2$) at $\sigma/\mu = 10^4$ vs exact warm Rankine-Hugoniot (`D2_w = 4.0754, e2_w = 4.7588`).
  - `nrpic` Monte Carlo collisions (`sig = 1e4`): timed out $> 180\text{ s}$ (projected `179.5 s` wall / `161.6 s` compute from 20-step measurement `11.048 s / 9.942 s`), giving `vlasov_pbgk` **`50.0x` wall (`65.3x` compute) speedup** at $\sigma/\mu = 10^4$.
  - `vlasov_mfm`: `dE/E = 1.08e-3` ($\sigma=0$) and `6.19e-3` ($\sigma=15$), whereas `vlasov_pbgk` holds `<= 1.83e-14` across every optical depth.
  - GPU vs OpenMP (`4` threads) determinism at $\sigma/\mu = 15$: `max|dx| = 4.441e-16`, `max|du| = 9.812e-14`.
