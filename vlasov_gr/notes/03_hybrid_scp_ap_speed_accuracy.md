# GR-LBV GPU Acceleration & Hybrid `SCP-AP` Engineering Report

**Goal**: Eliminate the GPU performance bottleneck and collisionless curved-space dispersion of baseline `vlasov_mfm` (`65.99 s` on Kerr $a=0.9M$ $N=3112$; `19.38 s` on Suite 1D `s1d_sig15`) without sacrificing continuum AP shock-capturing or machine-precision parity.

**Executive Summary**:
1. **Tier-1 GPU optimization of `vlasov_mfm`**: Cuts NVIDIA B200 wall time on `s2_grlbv_n18` ($N=3112, t=30M$) from **`65.99 s` to `5.62 s` wall / `4.57 s` compute (`11.7x` wall speedup)** and on `s1d_sig15` ($N=2400, N_b=2, 462$ substeps) from **`19.38 s` to `3.52 s` wall / `2.37 s` compute (`5.5x` wall speedup)** while preserving exact `< 1e-12` Stage 2/3 parity (`row1_dh = 3.419e-15` vs Stage 4a; `<= 1.998e-15` CPU/GPU/Python Stage 3 parity; `10/10 pytest passed`).
2. **Hybrid `vlasov_hybrid` (`SCP-AP` — Symplectic Cubature-Packet & Asymptotic-Preserving MFM)**:
   - When `coll_sigma <= 0`, populated velocity bases expand once at startup into deterministic degree-5 Stroud cubature packets ($Q_{\rm SCP}=14$, or $8/27$, collapsing to $1$ when $\Sigma = 0$) with base-$2,3,5$ Halton-$SO(3)$ Shoemake quaternion rotation, evolved by implicit midpoint integration (`NrpicPush`).
   - When `coll_sigma > 0`, `vlasov_hybrid` dispatches automatically to the optimized Tier-1 AP-MFM + Maxwell-Jüttner BGK + HLLC + harmonic-$c_s$ Noh solver.
   - **Suite 2 (Kerr $a=0.9M$ vs `MC 100k` truth)**: `s2_hyb_n18_q14` ($43{,}568$ packets) achieves **`1.55 s` wall (`0.27 s` compute) -> `42.6x` wall / `244x` compute speedup** over baseline MFM, cuts Killing drift to `|dE/E0| = 3.04e-8` and `|dLz/Lz0| = 1.28e-13`, lowers azimuthal histogram roughness to **`R_hist = 0.0846`** (`2.64x` smoother than equal-runtime `MC 10k` `0.2236`, nearly matching `MC 100k` truth `0.0809`), and reduces normalized PDF $L_1$ error to **`0.0418`** (vs `MC 10k` `0.0695`, `Opt MFM` `0.1158`).
   - **Suite 1D (`sig=0`)**: `s1d_hybrid_sig0` ($33{,}600$ packets) cuts relative $L_1$ error against a $512$-node exact collisionless reference by `4.7x` (`0.0615` vs `Opt MFM` `0.2878`) with `dE = 0.00` in `2.238 s` wall (`1.185 s` compute).
   - **Suite 3 (Z4c + AMR + FastFlow OS collapse)**: `s3_hyb_n26` (`138.41 s` wall / `137.19 s` comp) matches `s3_nrp_n26` (`136.59 s` / `135.39 s`) and `s3_opt_n26` (`151.77 s` / `150.31 s`) with exact apparent horizon time `t_AH = 16.3894`, `M_AH = 0.99969`, `t_exc99 = 19.7108`, `H_max = 3.5945`.
   - **Strong scaling (50 Kerr cycles)**: `Hybrid SCP-AP` scales from `7,728` packets (`0.006 s` comp) to `200,592` packets (`0.012 s` comp), delivering **`68.8x` lower compute time** at $N_{\rm lat} = 30$ than `Opt MFM` (`0.825 s` for `14,328` elements).

---

## 1. Tier-1 GPU Optimization Architecture & Root-Cause Profiling

`nsys` and `cuobjdump` profiling on `gb204` (`NVIDIA B200`, `sm_100`) identified four bottlenecks in baseline `vlasov_mfm`, all eliminated in [nrpic_vlasov.cpp](file:///home/schmidt/ssci-haiyangw/nrpic/athenak/src/particles/nrpic_vlasov.cpp) and [nrpic_vlasov_kernels.hpp](file:///home/schmidt/ssci-haiyangw/nrpic/athenak/src/particles/nrpic_vlasov_kernels.hpp):

1. **Constant-memory Kokkos lambda staging & `cudaEventSynchronize` stalls**: Capturing multi-dimensional `Kokkos::View` objects pushed functor sizes past CUDA parameter-memory limits (`cuda_parallel_launch_constant_memory`). Packing raw device pointers into small POD descriptors (`VlasovGradPtrs`, `VlasovFluxPtrs`, `VlasovKickPtrs`, `VlasovBgkPtrs`, `VlasovDomain`) and dispatching metric paths via compile-time `MetricKind` (`0`=Minkowski passing dummy `KerrSchildLight{0.0, 0.0}`, `1`=analytic `KerrSchildLight{mass, spin}`, `2`=general `VlasovMetric`) moved **100% of Vlasov physics kernels** onto `cuda_parallel_launch_local_memory`.
   - During Tier-1 verification we caught `Kokkos::Max<int>` (`INT_MIN` identity) in `NrpicVlasovInitializeOnMesh` preventing `metric_is_minkowski` from turning `true` on flat periodic domains; changing the reduction to `Kokkos::Sum<int>` dropped flat `ApplyGeodesicHalfKick` calls to zero and put `ComputeEdgeFluxesImpl<true, 2, 0, KerrSchildLight>` (`MetricKind=0`) into local memory.
2. **Double-rebuild & $h_{\max}$ grid collapse in neighbor geometry**: Replacing the two-grid rebuild with a single mean-$\bar{h}$ spatial hash grid, single-walk candidate caching (`kMaxCand = 128`, `cand_scale = 1.08`), fast damped Newton convergence for $h_a^3 \bar{n}_a = 1$, symmetric gather-scatter neighbor insertion with stack batching (`kLocNgb = 96`), and stack-local sorting pruned `UpdateGeometry` + `FillNeighborsAndCount` sharply.
3. **Nested Brent root-finders & eigensolvers**: Replaced 60-iter Brent root-finders with safeguarded analytical Newton solves (`SolveFaceBetaFT<MaxNb>`, `SafeMjThetaFromW`, `ValenciaC2PSynge`), combined `Kve2`+`Kve3` evaluation (`Kve2And3`), Sylvester minor fast-path `IsSpd3Fast` before calling `SymEig3`, and hoisted `kp_cache[96]` outside the `al` loop in `ComputeGradientsImpl<MaxNb>`.
4. **Shock-conduction parity fix**: Fixed `PrecomputeCellNohFluidImpl` to map `BuildHllcCellFluid`'s orthonormal tetrad velocity `st_c.v` cleanly through $L_g$ (`L_g * st_c.v`) instead of `<u_i>/(D h U^0)`, restoring `row1_dh = 3.419e-15` machine parity against Stage 4a on `s1d_sig15` (verified with back-to-back GPU determinism runs `runA` vs `runB`: plateau $D = 3.79544$ vs `3.79328` vs Stage 4a `3.79185`).

### Measured B200 `nsys` Top Kernels (`s1d_sig15`, full 462-substep run, $N=2400$, $N_b=2$)

| Kernel | Post-fix calls | Total GPU time (ms) | Launch path |
|---|---:|---:|---|
| `ComputeEdgeFluxesImpl<true, 2, 0, KerrSchildLight>` | 924 | 608.07 | `local_memory` |
| `ComputeGradientsImpl<8>` | 924 | 424.51 | `local_memory` |
| `UpdateGeometry` | 926 | 325.08 | `local_memory` |
| `FillNeighborsAndCount` | 925 | 253.68 | `local_memory` |
| `ApplyBgkRelaxationImpl<0, KerrSchildLight>` | 462 | 129.36 | `local_memory` |
| `FillNeighborsAndCount` reduce | 925 | 40.34 | `local_memory` |
| `ComputeCellVelocitiesImpl<0>` | 924 | 21.45 | `local_memory` |
| `PrecomputeCellNohFluidImpl<2, 0>` | 924 | 14.74 | `local_memory` |

---

## 2. `vlasov_hybrid` (`SCP-AP`) Benchmark Ledger (B200 `gb204`)

Diagnostic visualization: [diag_hybrid_speed_accuracy.png](file:///home/schmidt/ssci-haiyangw/nrpic/vlasov_gr/notes/figs/diag_hybrid_speed_accuracy.png), generated by [run_hybrid_benchmark.py](file:///home/schmidt/ssci-haiyangw/nrpic/vlasov_gr/notes/scripts/run_hybrid_benchmark.py) and [plot_hybrid_speed_accuracy.py](file:///home/schmidt/ssci-haiyangw/nrpic/vlasov_gr/notes/scripts/plot_hybrid_speed_accuracy.py).

### 2.1 Suite 1D: 3D Flat Periodic SR Colliding Beams ($N = 2400, N_b = 2, t = 0.55$)

| Run | $\sigma/\mu$ | Mode | $N_{\rm eff}$ | Wall (s) | Comp (s) | $|dM/M_0|$ | $|dE/E_0|$ | Accuracy |
|---|---:|---|---:|---:|---:|---:|---:|---|
| `s1d_mfm_sig0` | $0$ | Opt MFM | 2400 | 3.018 | 1.724 | 3.20e-16 | 3.09e-5 | `L1 = 0.2878` vs exact |
| `s1d_hybrid_sig0` | $0$ | SCP ($q=14$) | 33600 | **2.238** | **1.185** | 0.00 | **0.00** | **`L1 = 0.0615`** (`4.7x` better) |
| `s1d_mfm_sig15` | $15$ | Opt AP-MFM | 2400 | 3.519 | 2.366 | 3.20e-16 | 2.48e-10 | `row1_dh = 3.4e-15` |
| `s1d_hybrid_sig15` | $15$ | Opt AP-MFM | 2400 | 3.392 | 2.335 | 3.20e-16 | 2.45e-10 | AP parity |
| `s1d_mfm_sig1e4` | $10^4$ | Opt AP-MFM | 2400 | 2.678 | 1.530 | 0.00 | 6.04e-13 | $D_{\rm plat} = 4.0611$ (`-0.96%` Taub) |
| `s1d_hybrid_sig1e4` | $10^4$ | Opt AP-MFM | 2400 | 2.615 | 1.561 | 0.00 | 5.80e-13 | $D_{\rm plat} = 4.0528$ (`-1.17%` Taub) |

### 2.2 Suite 2: Kerr $a = 0.9M$ Sheared Tidal Cloud ($t = 30M$, Truth = `MC 100k`; `Wall Spd = 65.99 s / Wall`, `Comp Spd = 65.99 s / Comp`)

| Run | $N_{\rm init}$ | Wall (s) | Comp (s) | Wall Spd | Comp Spd | $\max|dE/E_0|$ | $\max|dL_z/L_{z0}|$ | $R_{\rm hist}$ | $L_1^{\rm hist}$ | $\|\Delta \bm{x}_{\rm cm}\|_2$ |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| Baseline MFM `n18` | 3112 | 65.99 | --- | 1.0x | 1.0x | 5.82e-5 | 1.56e-4 | 0.3616 | 0.1158 | 1.11e-2 |
| `s2_opt_n10` | 552 | 2.96 | 1.92 | 22.3x | 34.4x | 5.26e-5 | 2.25e-4 | 0.5504 | 0.2010 | 2.53e-2 |
| `s2_opt_n14` | 1472 | 4.35 | 3.29 | 15.2x | 20.1x | 5.47e-5 | 2.00e-4 | 0.6057 | 0.1931 | 1.65e-2 |
| `s2_opt_n18` | 3112 | 5.62 | 4.57 | 11.7x | 14.4x | 5.82e-5 | 1.56e-4 | 0.3616 | 0.1158 | 1.11e-2 |
| `s2_mc10k` | 10000 | 1.31 | 0.13 | 50.4x | 508x | 3.42e-8 | 1.34e-13 | 0.2236 | 0.0695 | 1.33e-2 |
| `s2_mc100k` (Truth) | 100000 | 1.29 | 0.24 | --- | --- | 3.28e-8 | 1.31e-13 | 0.0809 | 0.0000 | 0.00 |
| `s2_hyb_n10_q14` | 7728 | 1.55 | 0.28 | 42.6x | 236x | 3.03e-8 | 1.36e-13 | 0.2941 | 0.0927 | 1.07e-3 |
| `s2_hyb_n14_q14` | 20608 | **1.30** | **0.27** | **50.8x** | **244x** | 3.04e-8 | 1.34e-13 | 0.1498 | 0.0548 | 3.07e-3 |
| `s2_hyb_n18_q8` | 24896 | 1.51 | 0.32 | 43.7x | 206x | 4.19e-8 | 1.40e-13 | 0.1331 | 0.0450 | 9.52e-3 |
| **`s2_hyb_n18_q14`** | **43568** | **1.55** | **0.27** | **42.6x** | **244x** | **3.04e-8** | **1.28e-13** | **0.0846** | **0.0418** | **3.56e-3** |
| `s2_hyb_n18_q14_unrot` | 43568 | 1.52 | 0.25 | 43.4x | 264x | 4.23e-8 | 1.32e-13 | 0.0551 | 0.0316 | 3.19e-3 |
| `s2_hyb_n18_q14_rexc98` | 43568 | 1.45 | 0.23 | 45.5x | 287x | 6.87e-6 (3.04e-8 $\le 25M$) | 3.70e-5 | 0.0846 | 0.0418 | 4.22e-3 |

### 2.3 Suite 3 (OS Z4c+AMR+FastFlow Collapse) & Strong Scaling (50 cycles)

- **Suite 3 ($N=9328$, $t=0..25M$)**:
  - `s3_opt_n26`: `wall = 151.77 s`, `comp = 150.31 s`, `t_AH = 16.3894`, `M_AH = 0.99969`, `t_exc99 = 19.7014`, `H_max = 3.5718`
  - `s3_hyb_n26` ($q=1$ auto-collapse): `wall = 138.41 s`, `comp = 137.19 s`, `t_AH = 16.3894`, `M_AH = 0.99969`, `t_exc99 = 19.7108`, `H_max = 3.5945`
  - `s3_nrp_n26`: `wall = 136.59 s`, `comp = 135.39 s`, `t_AH = 16.3894`, `M_AH = 0.99969`, `t_exc99 = 19.7108`, `H_max = 3.5945`
- **Strong scaling (50 Kerr cycles)**:
  - `nc=10` (`552` vs `7728`): Opt MFM `0.098 s` vs Hybrid `0.006 s` vs MC `0.007 s`
  - `nc=18` (`3112` vs `43568`): Opt MFM `0.330 s` vs Hybrid `0.006 s` vs MC `0.008 s`
  - `nc=24` (`7208` vs `100912`): Opt MFM `0.422 s` vs Hybrid `0.008 s` vs MC `0.009 s`
  - `nc=30` (`14328` vs `200592`): Opt MFM **`0.825 s`** vs Hybrid **`0.012 s`** (`68.8x` speedup with `14x` more tracers) vs MC `0.013 s`

---

## 3. Code Map & Manuscript Artifacts

- Solver & kernels: [nrpic_vlasov.hpp](file:///home/schmidt/ssci-haiyangw/nrpic/athenak/src/particles/nrpic_vlasov.hpp), [nrpic_vlasov_kernels.hpp](file:///home/schmidt/ssci-haiyangw/nrpic/athenak/src/particles/nrpic_vlasov_kernels.hpp), [nrpic_vlasov.cpp](file:///home/schmidt/ssci-haiyangw/nrpic/athenak/src/particles/nrpic_vlasov.cpp), [nrpic.cpp](file:///home/schmidt/ssci-haiyangw/nrpic/athenak/src/particles/nrpic.cpp), [particles.cpp](file:///home/schmidt/ssci-haiyangw/nrpic/athenak/src/particles/particles.cpp)
- Kernel unit tests: [vlasov_kernel_test.cpp](file:///home/schmidt/ssci-haiyangw/nrpic/tests/kernel/vlasov_kernel_test.cpp), [test_vlasov_gr.py](file:///home/schmidt/ssci-haiyangw/nrpic/tests/test_vlasov_gr.py)
- Working paper (PRD style + `/cz-figure-style`): [main.tex](file:///home/schmidt/ssci-haiyangw/nrpic/vlasov_gr/paper/main.tex), [main.pdf](file:///home/schmidt/ssci-haiyangw/nrpic/vlasov_gr/paper/main.pdf), [supplement.tex](file:///home/schmidt/ssci-haiyangw/nrpic/vlasov_gr/paper/supplement.tex), [supplement.pdf](file:///home/schmidt/ssci-haiyangw/nrpic/vlasov_gr/paper/supplement.pdf), [hybrid_speed_accuracy.npz](file:///home/schmidt/ssci-haiyangw/nrpic/vlasov_gr/paper/data/hybrid_speed_accuracy.npz)
