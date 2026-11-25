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


### Verified Phase 4 Wave 4A — M1–M4 NRPIC Benchmarks at $N = 10^4, 10^5$ (`gb204` B200 GPU, Milestone #4)

All reduced diagnostics stored in [`repro_wave4a.npz`](file:///home/schmidt/ssci-haiyangw/nrpic/vlasov_gr/paper/data/repro_wave4a.npz) via [`run_repro_wave4a.py`](file:///home/schmidt/ssci-haiyangw/nrpic/vlasov_gr/notes/scripts/run_repro_wave4a.py).

- **M1–M2 (`e = 0.99` Kerr $a=0.9M$, $t=230M, \Delta t=0.01M$; `geodesic_mesh` $dx=0.25M, t=600M, \Delta t=0.005M$)**:
  - `ks` (`kerr_schild_sph`): `midpoint` (`7.73s`): $\max|\Delta E/E_0|=2.781\times 10^{-8}$, $\max|\Delta Q/Q_0|=1.254\times 10^{-7}$, `pos_err = 4.487e-4`; `vlasov_hybrid + gl4` (`8.40s`): $\max|\Delta E/E_0|=3.451\times 10^{-15}$, $\max|\Delta Q/Q_0|=5.770\times 10^{-14}$, `pos_err = 2.609e-11` (**$8.06\times 10^6\times$ better $E$, $1.72\times 10^7\times$ better position**).
  - `cks` (`kerr_schild`): `midpoint` (`7.85s`): `dE=6.154e-7`, `dQ=1.226e-6`, `pos_err=1.728e-2`; `vlasov_hybrid + gl4` (`6.90s`): `dE=1.014e-13`, `dQ=3.011e-13`, `pos_err=2.529e-9` (**$6.07\times 10^6\times$ better $E$, $6.83\times 10^6\times$ better position**, faster GPU runtime).
  - `lattice` (`dx=0.025M`): `midpoint` (`11.23s`): `dE=1.983e-6`, `dLz=5.220e-6`, `dQ=4.758e-5`, `pos_err=1.594e-2`; `vlasov_hybrid + gl4` (`12.79s`): `dE=9.791e-7`, `dLz=4.112e-6`, `dQ=4.815e-5`, `pos_err=6.778e-5` (**$235\times$** better position).
  - `geodesic_mesh` (`600M`): `midpoint` (`18.63s`, `dE=7.122e-7`, `dLz=7.595e-6`, `dQ=5.775e-5`) and `gl4` (`23.17s`, `7.131e-7 / 7.601e-6 / 5.773e-5`) match at the 3rd-order Hermite mesh floor. Also identified I/O optimization: `traj_dcycle=1` vs `25` cut $20M$ geodesic runtime from `13.016s` to `0.941s` ($13.8\times$ wall speedup).
- **M3 (Dynamic Z4c Puncture Tracers & Binary Head-On Merger, `metric_drvts = interpolant`)**:
  - `tracers_single` (`250M`): `midpoint` (`484.87s`) and `gl4` (`492.40s`) both yield `M_AH = 1.00147`, `||H||_max = 1.006`, circular $|dL/L| = [1.09\times 10^{-4}, 2.37\times 10^{-4}, 3.87\times 10^{-4}, 2.31\times 10^{-4}]$, plunge excision $t=(126.25, 54.12)M$, `max|dx|` between solvers $\le 8.30\times 10^{-4}M$.
  - `tracers_headon` (`100M`): `midpoint` (`945.58s`) and `gl4` (`968.30s`) both form common horizon at $t = 49.5M$ with $M_{\rm AH} = 1.00210$, `||H||_max = 1.632`, reflection `|x_tag2| <= 4.19e-14`, axisymmetry $|dL_x| \le 9.79\times 10^{-4}$, trajectory agreement `max|dx| <= 2.4e-6`.
- **M4 (6-Level SMR Kerr $a=0.9M$ Bound Clusters at $N=10^4$ & $N=10^5$, $t=200M$, $100\%$ survival)**:
  - Analytic `10k`: `midpoint` (`1.78s`, `dE med/p99/max = 8.22e-9/3.31e-8/9.29e-8`, `dQ/K_med = 5.72e-11`) vs `gl4` (`2.10s`, **`5.81e-16/3.52e-15/3.71e-14`**, **`dQ/K_med = 7.22e-17`**); analytic `100k`: `midpoint` (`1.90s`, `dE = 8.47e-9/3.36e-8/7.22e-7`) vs `gl4` (**`2.00s`, `dE = 5.82e-16/3.63e-15/6.65e-13`, `dQ/K_med = 7.23e-17`**).
  - 6-level SMR mesh `10k`: `midpoint (filter_densitized=false)` (`66.85s`, `dE_med=1.11e-7`, `filt(t0/max) = -2.25e-6 / 8.91e-4`) vs `gl4 (filter_densitized=true)` (`75.71s`, `dE_med=1.05e-7`, **`filt_t0 = 0.00e+00`**; SMR boundary crossing still yields `filt_max = 8.64e-4` -> Iteration 3 candidate).
  - 6-level SMR mesh `100k`: `midpoint` (`77.62s`, `dE_med=1.10e-7`, `filt(t0/max) = -2.25e-6 / 5.29e-4`, `|<e^{iphi}>|=0.1623`) vs `gl4` (`91.70s`, `dE_med=1.06e-7`, **`filt_t0 = 0.00e+00`**, `filt_max = 5.03e-4`, `|<e^{iphi}>|=0.1623`).


### Verified Phase 4 Wave 4B — M5a–M5c Self-Gravitating Relativistic Collapse & Equilibria at $N = 10^4, 10^5$ (`gb204` B200 GPU, Milestone #5)

All reduced diagnostics stored in [`repro_wave4b.npz`](file:///home/schmidt/ssci-haiyangw/nrpic/vlasov_gr/paper/data/repro_wave4b.npz) (`151 KB`) via [`run_repro_wave4b.py`](file:///home/schmidt/ssci-haiyangw/nrpic/vlasov_gr/notes/scripts/run_repro_wave4b.py) (pre-Iteration-3 baseline with `filter_densitized = true` on `hyb`).

- **M5a Oppenheimer-Snyder $R_0 = 5M$ Collapse (7-level AMR, Z4c + FastFlow)**:
  - `os_10k_lat_mid` ($N=9{,}328$): `wall = 130.9s` (`129.0s` comp), `rho_err = 4.18e-4`, `t_AH = 16.39M`, `M_AH = 0.99969M`, `t_exc99 = 19.72M`, `||H||_(0/max) = (0.322 / 1.896)`, `filt(t0/max) = (-2.49e-3 / 2.20e-2)`.
  - `os_10k_lat_hyb` ($N=9{,}328$): `wall = 132.2s` (`130.5s` comp), `rho_err = 3.35e-3`, `t_AH = 16.39M`, `M_AH = 1.00272M`, `t_exc99 = 19.72M`, `||H||_(0/max) = (0.323 / 1.912)`, `filt(t0/max) = (0.00e+00 / 2.38e-2)`.
  - `os_10k_qmc_hyb` ($N=10{,}000$, unstratified Sobol): `wall = 262.5s` (`260.5s` comp), `rho_err = 6.91e-1`, `t_AH = 16.31M`, `M_AH = 1.00070M`, `t_exc99 = 19.72M`, `||H||_(0/max) = (0.414 / 5.057)`, `filt(t0/max) = (0.00e+00 / 7.24e-3)`.
  - `os_100k_lat_mid` ($N=102{,}208$): `wall = 152.0s` (`150.2s` comp), `rho_err = 7.60e-2`, `t_AH = 16.20M`, `M_AH = 0.99995M`, `t_exc99 = 19.68M`, `||H||_(0/max) = (0.346 / 1.139)`, `filt(t0/max) = (-2.47e-3 / 1.33e-2)`.
  - `os_100k_qmc_hyb` ($N=100{,}000$): `wall = 158.1s` (`156.3s` comp), `rho_err = 5.30e-2`, `t_AH = 16.35M`, `M_AH = 1.00307M`, `t_exc99 = 19.68M`, `||H||_(0/max) = (0.347 / 1.536)`, `filt(t0/max) = (0.00e+00 / 4.94e-3)`.
- **M5b Prolate Spheroid $e = 0.9, b = 10M$ Collapse (7-level AMR, `nfilter = 4, filter_compensate = true`)**:
  - `prol_10k_mc_mid` ($N=10^4$): `wall = 818.5s` (`814.7s` comp), `|COM0| = 2.18e-17`, `q_asym0 = 6.38e-3`, `t_AH = 32.25M`, `M_AH = 0.94694M`, `t_exc99 = 38.06M`, `||H||_(0/max) = (0.543 / 6.312)`, `filt(t0/max) = (-5.73e-5 / 9.77e-1)`.
  - `prol_10k_qmc_hyb` ($N=10^4$, `qmc_octant`): `wall = 790.6s` (`786.9s` comp), `|COM0| = 4.44e-19`, `q_asym0 = 0.00e+00`, `t_AH = 32.31M`, `M_AH = 1.02552M`, `t_exc99 = 36.56M`, `||H||_(0/max) = (0.348 / 6.538)`, `filt(t0/max) = (0.00e+00 / 1.26e-3)`.
  - `prol_100k_mc_mid` ($N=10^5$): `wall = 785.6s` (`782.0s` comp), `|COM0| = 1.15e-16`, `q_asym0 = 2.73e-3`, `t_AH = 32.13M`, `M_AH = 0.97783M`, `t_exc99 = 36.94M`, `||H||_(0/max) = (0.274 / 6.725)`, `filt(t0/max) = (-5.80e-5 / 1.155)`.
  - `prol_100k_qmc_hyb` ($N=10^5$, `qmc_octant`): `wall = 789.8s` (`786.2s` comp), `|COM0| = 1.91e-19`, `q_asym0 = 0.00e+00`, `t_AH = 32.00M`, `M_AH = 1.02772M`, `t_exc99 = 36.00M`, `||H||_(0/max) = (0.217 / 5.733)`, `filt(t0/max) = (0.00e+00 / 6.00e-4)`.
- **M5c Shapiro-Teukolsky Relativistic Polytrope Sequence ($N = 10^4$ & $N = 10^5$, 5/7-level AMR)**:
  - $y_c = 0.900$ (stable, `vp01`, $N=10^4$): `mid` (`201.5s`, `alp = 0.886->0.886`, `r50 = 10.42->10.30`, `|COM| = 3.12e-2->2.64e-2`) vs `hyb` (`205.6s`, `alp = 0.873->0.890`, `r50 = 10.42->10.26`, `|COM| = 5.94e-17->1.40e-3`).
  - $y_c = 0.819$ (marginal, `vp01`):
    - $N=10^4$: `mid` (`199.0s`, `alp_min=0.788`, `r50 = 5.88->5.65`, `|COM| = 1.79e-2->6.82e-3`, `filt_t0=-3.95e-5`), `anti` (`205.4s`, `alp_min=0.799`, `r50 = 5.88->5.87`, `|COM| = 9.57e-18->3.66e-14`, `filt_max=1.03e-15`), `hyb` (`204.8s`, `alp_min=0.797`, `r50 = 5.88->6.06`, `|COM| = 1.02e-16->1.13e-3`, `filt_max=1.03e-15`).
    - $N=10^5$: `mid` (`204.0s`, `alp_min=0.801`, `r50 = 5.88->5.81`, `|COM| = 6.61e-3->4.14e-3`, `||H||_0=0.066`) vs `hyb` (`215.5s`, `alp_min=0.798`, `r50 = 5.88->5.79`, `|COM| = 7.77e-18->1.69e-4`, `||H||_0=0.118`, `filt_max=1.03e-15`).
  - $y_c = 0.756$ (`dp10`, $N=10^4$ collapse): `mid` (`671.7s`, `t_AH = 147.44M`, `M_AH = 0.9975M`, `filt_max = 4.33e-1`) vs `hyb` (`980.7s`, `t_AH = 113.88M`, `M_AH = 0.9957M`, `filt_max = 2.16e-3`).
  - $y_c = 0.605$ (`vp01`, $N=10^4$ unstable collapse): `mid` (`1578.8s`, `t_AH = 191.00M`, `M_AH = 0.9988M`, `r50 = 2.84->10.42`, `|COM| = 9.01e-3->4.44`) vs `hyb` (`1616.6s`, `t_AH = 118.44M`, `M_AH = 0.9996M`, `filt_max = 1.46e-3`).
  - $y_c = 0.500$ (`vp01` collapse):
    - $N=10^4$: `mid` (`1219.5s`, `t_AH = 104.31M`, `M_AH = 1.0003M`, `filt_max = 1.90e-1`) vs `hyb` (`1050.1s`, `t_AH = 76.06M`, `M_AH = 1.0005M`, `filt_max = 2.22e-3`).
    - $N=10^5$: `mid` (`1009.1s`, `t_AH = 68.81M`, `M_AH = 1.0018M`, `filt_max = 4.47e-1`) vs `hyb` (`1016.0s`, `t_AH = 70.81M`, `M_AH = 1.0011M`, `filt_max = 7.49e-4`).
  - $y_c = 0.283$ (`vp01` dispersive outer-branch dispersal):
    - $N=10^4$: `mid` (`199.8s`, `alp = 0.422->0.984`, `r50 = 1.68->80.69`, `|COM| = 6.04e-3->1.08e-1`, `filt_max=1.73e-2`) vs `hyb` (`207.5s`, `alp = 0.422->0.981`, `r50 = 1.68->77.13`, `|COM| = 1.91e-18->1.78e-13`, `filt_max=3.25e-3`).
    - $N=10^5$: `mid` (`206.0s`, `alp = 0.422->0.982`, `r50 = 1.68->79.05`, `|COM| = 3.00e-3->5.59e-2`, `filt_max=1.73e-2`) vs `hyb` (`225.8s`, `alp = 0.422->0.981`, `r50 = 1.68->76.91`, `|COM| = 1.11e-17->1.57e-2`, `filt_max=1.97e-3`).
  - $y_c = 0.500$ (`mig`, $N=10^4$ outward migration): `mid` (`201.8s`, `alp = 0.557->0.889`, `r50 = 2.29->10.68`, `|COM| = 7.49e-3->2.89e-2`) vs `hyb` (`206.5s`, `alp = 0.557->0.898`, `r50 = 2.29->9.78`, `|COM| = 1.86e-18->1.22e-13`).


### Verified Iteration 3 — Self-Adjoint Metric-Weighted Flux-Conservative AMR Filter (`gb204` B200 GPU, Milestone #6)

Full derivation and summary: [04_iterative_algorithmic_proofs.md](file:///home/schmidt/ssci-haiyangw/nrpic/vlasov_gr/notes/04_iterative_algorithmic_proofs.md), verification data [`iter3_filter_verify.npz`](file:///home/schmidt/ssci-haiyangw/nrpic/vlasov_gr/paper/data/iter3_filter_verify.npz) via [`run_iter3_filter_verify.py`](file:///home/schmidt/ssci-haiyangw/nrpic/vlasov_gr/notes/scripts/run_iter3_filter_verify.py).

- **Standalone Tests 1–10 (`g++` & `nvcc -arch=sm_100`)**: **PASSED** (`Test 10 mcons`: `const_err = 0.00e+00` vs naive `4.80e-01`, `sa = 0.00e+00`, `cons_1d = 2.30e-16`, `amr_const = 0.00e+00`, `amr_cons = 3.77e-16`).
- **M5a OS $R_0=5M$ (`os_10k_lat`, 7-level dynamic AMR, $t=25M$)**: `plain` (`151.2s`, `rho_err=4.178e-4`, `||H||_max=1.896`, `filt=-2.49e-3/2.20e-2`), `dens` (`150.4s`, `rho_err=3.354e-3`, `||H||_max=1.912`, `filt=0.00e+00/2.38e-2`) vs **`mcons`** (`160.5s`, **`rho_err = 4.183e-4`**, `||H||_max = 1.893`, **`filt(t0/max) = 0.00e+00 / 8.76e-16`**).
- **M4 6-Level SMR Kerr $a=0.9M$ (`mesh 10k`, $t=200M$)**: `plain` (`76.02s`, `filt=-2.25e-6/8.91e-4`), `dens` (`75.44s`, `filt=0.00e+00/8.64e-4`) vs **`mcons`** (`189.85s`, `|<e^{iphi}>|=0.1577`, **`filt(t0/max) = 0.00e+00 / 9.93e-16`**). *(Full-3D `flx_tm` + `pbval_tm` overhead here directly motivates Iteration 4a boundary-only refluxing + 4d widened-halo filter.)*
- **M5b Prolate Compensated Pass (`nfilter=4, filter_compensate=true`, 7-level AMR, $t=5M$)**: `mcons` (`59.3s`, `||H||_max = 0.3475`, `filt = 0.00e+00 / 1.01e-15`).
- **GPU vs OpenMP (4 threads) 10-step OS AMR Determinism**: `max|dx| = 8.882e-16`, `max|du| = 6.453e-16`, `rel|d_int_E_filt| = 4.229e-15`.

### Verified Iteration 4 — VRAM Slimming (`bflx`), $C^2$ Quintic Hermite, and Scheme A Stage-Accurate RK Backreaction (`gb204` B200 GPU, Milestone #7)

Worktree `feat/iter4-vram-quintic-backreaction`, proof script [`run_iter4_verify.py`](file:///home/schmidt/ssci-haiyangw/nrpic/vlasov_gr/notes/scripts/run_iter4_verify.py), data [`iter4_verify.npz`](file:///home/schmidt/ssci-haiyangw/nrpic/vlasov_gr/paper/data/iter4_verify.npz).

- **Standalone Kernel Checks 1–12 (`g++` & `nvcc -arch=sm_100`)**: **PASSED** (`Test 11 quintic`: `sym = 2.97e-15, pou = 2.22e-16, p4 = (3.55e-15, 3.20e-14), C2 = (0.00e+00, 0.00e+00, 5.00e-16), orders = (5.30, 4.13)`; `Test 12 stageA`: `p_frozen = 1.00, p_rk2 = 1.99, p_rk3 = 1.99, p_rk4 = 1.99, th = (1.00, 0.125, 0.062)`).
- **Iter 4a (Boundary-Only `bflx` Refluxing + Interior `e_prev`/`tm_prev`)**:
  - 10-step OS AMR Determinism: `GPU4 vs GPU3` `max|dx| = 4.441e-16, max|du| = 4.247e-16, rel|d_intE_filt| = 0.000e+00`; `GPU4 vs OMP4 (4 threads)` `max|dx| = 8.882e-16, max|du| = 6.313e-16, rel|d_intE_filt| = 4.229e-15, filt4_max = 9.611e-16`.
  - Full `t=25M` 7-level OS AMR (`mcons`): `build_gpu` (`wall = 161.1s, peak_VRAM = 73,174 MiB, rho_err = 4.183e-4, t_AH = 16.39M, M_AH = 1.00158M, ||H||_max = 1.893`) vs **`build_gpu_iter4`** (**`wall = 160.8s, peak_VRAM = 67,110 MiB` (`-6,064 MiB`), `rho_err = 4.183e-4, t_AH = 16.39M, M_AH = 1.00158M, ||H||_max = 1.893, filt_max = 9.29e-16`**).
- **Iter 4b ($C^2$ 6-Node `quintic` Hermite, Zero Extra `met*s` VRAM) on M4 6-Level SMR Kerr $a=0.9M$ ($N=10^4, t=200M$, `gl4 + mcons`)**:
  - `hermite_ng2`: `wall = 192.8s, VRAM = 6,746 MiB, dE(med/p99/max) = (1.05e-7/4.44e-6/3.27e-5), dL_med = 3.31e-6, dQ/K_med = 5.26e-7`.
  - `hermite_ng4`: `wall = 205.4s, VRAM = 11,880 MiB, dE(med/p99/max) = (1.05e-7/4.44e-6/3.27e-5), dL_med = 3.31e-6, dQ/K_med = 5.26e-7`.
  - `bspline_ng4`: `wall = 205.3s, VRAM = 14,260 MiB (+2,380 MiB), dE(med/p99/max) = (1.65e-9/5.30e-7/1.94e-6), dL_med = 2.50e-8, dQ/K_med = 2.01e-8`.
  - **`quintic_ng4`**: **`wall = 209.3s, VRAM = 11,880 MiB` (`0` extra VRAM vs `hermite_ng4`, `-2,380 MiB` vs `bspline_ng4`), `dE(med/p99/max) = (3.38e-10 / 7.31e-8 / 3.27e-7)` (`311x` vs `hermite`, `4.9x` vs `bspline`), `dL_med = 8.53e-9` (`388x`), `dQ/K_med = 2.36e-9` (`223x`), `|<e^{iphi}>| = 0.1577`, `filt_max = 9.93e-16`**.
- **Iter 4b/4c M5a OS $R_0=5M$ Variants ($t=25M$, `mcons`)**:
  - `quintic + frozen`: `wall = 163.5s, peak_VRAM = 67,160 MiB, rho_err = 4.183e-4, t_AH = 16.39M, M_AH = 1.00161M, ||H||_max = 1.895, filt_max = 9.61e-16`.
  - `hermite + stageA`: `wall = 161.4s (+0.4%), peak_VRAM = 68,394 MiB (-4,780 MiB vs Iter 3), rho_err = 4.223e-4, t_AH = 16.20M, M_AH = 1.00074M (2x cleaner), ||H||_max = 1.881, filt_max = 9.48e-16`.
  - `quintic + stageA`: `wall = 165.5s, peak_VRAM = 68,444 MiB, rho_err = 4.223e-4, t_AH = 16.20M, M_AH = 1.00077M, ||H||_max = 1.883, filt_max = 9.61e-16`.
- **Iter 4c OS CFL Convergence (`t=10.0M`, `cfl = 0.25, 0.125, 0.0625`, `hermite + mcons`)**:
  - `frozen` $\alpha_c(10)$: `rel(0.25) = 5.192e-4, rel(0.125) = 2.841e-4, p_emp = 0.87` (`rho_err = 4.201e-4, 4.225e-4, 4.227e-4`).
  - **`stageA`** $\alpha_c(10)$: **`rel(0.25) = 3.463e-5` (`15.0x` smaller), `rel(0.125) = 1.248e-5` (`22.8x` smaller), `p_emp = 1.47` (`rho_err = 4.227e-4` converged at `cfl=0.25`)**.
- **Iter 4c Nonlinear ST Collapse ($y_c=0.500, N=10^4$, `qmc_antipodal`, 9-level AMR, `tlim=90M`, `mcons`)**:
  - `st_herm_froz`: `wall = 742.3s, peak_VRAM = 99,160 MiB, t_AH = 75.56M, M_AH = 1.00080M, ||H||_max = 1.566, |P|_max/M0 = 8.06e-15, filt_max = 9.24e-16`.
  - `st_quin_stgA`: `wall = 754.5s, peak_VRAM = 101,084 MiB, t_AH = 76.06M, M_AH = 1.00060M, ||H||_max = 1.572, |P|_max/M0 = 1.43e-14, filt_max = 9.25e-16`.
- **Wave 4C Partial Harvest (`jeans_10k_strat_mid`, stopped on user directive after binary BH inspiral)**: reached `t = 56.73M` (`part.00000..00011.bin`, `t_l=55.0M`), both clumps formed AH at `t_AH ~ 10.5M`, final `M_AH,0 = 0.1865M, M_AH,1 = 0.1844M`, separation shrunk `d_AB = 6.09M -> 0.55M`, MC vertical kick reached `z_BH,0 = +0.65M` (`t=55M`, peak `+0.71M`).

### Iteration 5 (`filter_mcons_unsplit` + `matter_stride` + `rk3` High-CFL Speed-Accuracy Pareto, `gb204` B200)
- **Standalone CUDA/C++ Kernel Proofs (`Tests 13–14`, both `g++` & `nvcc -arch=sm_100` PASS)**:
  - `[TEST13 UNSPLIT_MCONS]`: `const=0.00e+00`, single-pass 3D self-adjointness `sa=1.43e-16` (`10^6` metric contrast), unconditional positivity for `kappa=1/12` `minE=1.01e-03 >= 0`, octahedral symmetry `iso=2.22e-16`, 2-level 3D AMR reflux conservation `amr_cons=5.11e-16`.
  - `[TEST14 MULTIRATE]`: `matter_stride=4` continuous Scheme A (`dt_stage = stage_tau + c_s * dt_z4c`) with non-uniform substeps recovers `p_frozen=0.99`, `p_mr_rk3=1.98`, `p_mr_rk4=1.98`, `th_mr=0.500`.
- **Full-System Parity (`os10k`, `nlim=20`, `unsplit=false, stride=1`)**: `max|dE|/E0=0.000e+00`, `max|dH|=0.000e+00` vs Iteration 4 binary.
- **Suite 5.1 (M4 6-Level SMR Kerr, `a=0.9M, 10k, quintic_ng4, t=200M`)**:
  - Baseline directional `mcons` (`209.3s`): directional filter overhead measured at `58.6%` of Kerr cycle (`52.42 vs 21.69 ms/cyc`).
  - `m4_uns_nf1` (`filter_mcons_unsplit=true, nfilter=1`): **`65.6s` (`3.19x` speedup)**, `VRAM=11,894 MiB`, `dE_med=3.38e-10`, `dL=8.53e-09`, `dQ=2.36e-09`, `filt_max=9.81e-16`.
  - `m4_uns_nf2` (`filter_mcons_unsplit=true, nfilter=2`): **`98.9s` (`2.12x` speedup)**, identical invariants, `filt_max=9.81e-16`.
- **Suite 5.2 (OS `R0=5M` 8-Level AMR `t=25M`, `quintic+stageA`)**:
  - **CFL/`rk3` sweep (`10k`)**: `rk4 cfl=0.25` `164.7s (1.00x, M_AH=1.00077M, H2max=3.547)` -> `rk3 cfl=0.25` `131.4s (1.25x)` -> `rk3 cfl=0.40 dir1_s1` `72.6s (2.27x)` -> `rk3 cfl=0.40 dir1_s2` **`66.2s (2.49x, rho_early=4.944e-4, t_AH=16.35M)`** -> `rk3 cfl=0.45 dir1_s2` **`59.9s (2.75x)`** (`rk3 cfl=0.50` unstable). Note single-pass 7-pt unsplit `k=1/12` (`nf=1`) damps $(\pi,0,0)$ modes weaker (`H2max~56`), cured by matching 2nd moment (`uns3` `nf=3, k=1/12`).
  - **`100k` collapse (`t=25M, nlim=-1`)**: `rk4 cfl=0.25 dir1` **`180.2s`** (`M_AH=1.00104M, H2max=2.268`) -> `rk3 cfl=0.40 uns3_s2` **`80.4s` (`2.24x`, `t_AH=16.17M`, `M_AH=1.00075M`, `H2max=2.244`)**, `dir1_s2` **`80.3s` (`2.24x`, `M_AH=1.00112M`, `H2max=1.949`)**, `dir1_s4` **`74.0s` (`2.43x`, `H2max=1.847`)**.
- **Suite 5.3 (ST `y_c=0.500 10k` Anti QMC, `tlim=90M`, 9-level AMR)**:
  - `st10k_rk3_040_dir4c_s2` (`rk3 cfl=0.40, dir nfilter=4+comp, matter_stride=2`): **`314.7s` (`2.40x` speedup vs Iter 4 `754.5s`)**, `cyc=2836`, `t_AH=76.70M` (vs `76.06M`), `M_AH=1.00051M` (vs `1.00060M`), `|P|/M0=3.93e-15` (**`3.6x` cleaner than `1.43e-14`**), `filt_max=9.25e-16`. (Uncompensated `uns4_k16_s2` softens central gravity enough to stabilize `y_c=0.500` past `90M`, confirming `filter_compensate=true` is essential near the critical threshold.)
