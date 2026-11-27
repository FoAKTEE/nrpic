# Working Note: 1000:1 Schwarzschild EMRI Full 3+1 NR Campaign & Investigated Bug Report

**Branch:** `feat/gr-lagrangian-vlasov`
**Executable:** `/weka/scratch/schmidt/ssci-anima/ssci-haiyangw/nrpic_grlbv/build_gpu_iter5/src/athena` (`Kokkos_ARCH_BLACKWELL100=ON`, `Athena_ENABLE_MPI=OFF`, single-rank GPU — required because `nrpic_idsolve.cpp` is single-rank only)
**Runs root:** `/weka/scratch/schmidt/ssci-anima/ssci-haiyangw/nrpic_grlbv/runs/emri_1000to1/`
**Tools:** `emri_1000to1/{gen_emri_run.py, pn_2sf_reference.py, analyze_emri_gw.py, render_emri_movie.py, render_emri_2d_fields.py}`

---

## 1. Campaign Summary (Iterations 1–4)

| Run | $R_0\,[M]$ | Grid (`dx_BH`, `dx_p`, wave zone) | Outer BC / Gauge / ID | $t_{\rm end}\,[M]$ | Merger $t_{\rm exc}$ | $|\mathbf{x}_{\rm BH}|_{\rm end}\,[M]$ | $\max|\Delta M_{\rm AH}/M_0|$ | $\|\mathcal{H}\|_2$ / $\|\Theta\|_2$ (end) | $\dot{J}_{\rm orb}/J_{\rm orb}$ vs 1SF $[M^{-1}]$ | $|r\Psi_4^{(2,2)}|$ vs 1SF | Key Finding |
| :--- | :---: | :--- | :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :--- |
| `EMRI_q1e3_R6p5_it1` | `6.50` | `M/16`, `M/8→M/16` (`L7`), `L2` (`2 M`) | `nonwave`, `k1=0.02`, `stencil`, no SSL | `300.0` | — | `0.0088` | `1.92e-4` | `1.92e-3` / `2.06e-3` | `-9.02e-6` vs `-2.95e-6` (`3.1×`) | `1.11e-5` vs `1.33e-5` (`0.84×`) | `dx_p = M/16` at `cfl=0.35` had `-6e-6` excess negative drag; `e_Ω = 0.038` |
| `EMRI_q1e3_R6p5_it2` | `6.50` | `M/16`, `M/8` static slab (`L6`), `L2` | `nonwave`, `k1=0.02`, `stencil`, no SSL | `300.0` | — | `0.0003` | `1.93e-4` | `1.78e-3` / `2.29e-3` | `-1.51e-6` vs `-2.96e-6` (`0.51×`) | `1.70e-5` vs `1.33e-5` (`1.28×`) | Static slab had `N_MB=1464`; `e_Ω = 0.017`; half-1SF inspiral rate |
| `EMRI_q1e3_R6p40_it3` | `6.40` | `M/16`, `M/8` AMR (`L6`), `L2` | `nonwave`, `k1=0.02`, `stencil`, no SSL | `1115.3` | — | **`25.62`** *(runaway)* | `1.49e-3` | `1.38e-1` / **`8.66`** | `+4.97e-6` *(drift-biased)* | `9.95e-6` vs `1.41e-5` (`0.70×`) | Clean to `t≈360 M` (`e_Ω=0.0019`); **Bug 1**: `nonwave` BC reflection at `r=256 M` drove `v_BH = 0.17 c` |
| `EMRI_q1e3_R6p25_it4` | `6.25` | `M/16`, `M/8` AMR (`L6`), `L2` | **stock Sommerfeld**, `k1=0.02`, `stencil`, no SSL | `957.5` | **`732.1 M`** | `0.335` *(post-merger)* (`0.0028` at `400 M`) | `1.38e-3` (`+9.0e-4` step at merger!) | `1.33e-3` / **`9.12e-5`** | `-1.84e-6` vs `-3.55e-6` (`0.52×`) | `1.83e-5` vs `1.56e-5` (`1.17×`); **peak `1.60e-4` at `u=733.2 M`** | **First full 1000:1 inspiral + merger + QNM ringdown!** Merger `ΔM_AH ≈ +9.0e-4 M`, `S_z = +2.17e-3`. Exposed **Bugs 3–6** |
| `EMRI_q1e3_R6p40_it4` | `6.40` | `M/16`, `M/8` AMR (`L6`), `L2` | **stock Sommerfeld**, `k1=0.02`, `stencil`, no SSL | `939.2` | — | **`0.093`** (`0.0027` at `400 M`) | `5.37e-4` | `1.38e-3` / **`7.42e-5`** | `-1.68e-6` vs `-3.27e-6` (`0.51×`) | `1.64e-5` vs `1.41e-5` (`1.16×`) | **Bug 1 verified fixed** (`275×` less BH drift, `117,000×` smaller `||Θ||_2` than It-3!). Exposed **Bugs 3–6** |

---

## 2. Detailed Investigated Bug Report

### Bug 1 [RESOLVED in It-4]: Late-Time SMBH Runaway Drift from `sbc_variant = nonwave` Outer Boundary Reflection
- **Symptom:** In `EMRI_q1e3_R6p40_it3`, after ultra-clean circular inspiral on `t ∈ [0, 200] M` (`|x_BH| = 0.0016 M`), `||Z||_2` jumped 8× between `t = 200 M` and `t = 250 M` (`2.6e-3 → 2.0e-2`). Starting at `t ≈ 362 M`, the bound SMBH + particle system accelerated exponentially along `+x` to `|x_BH| = 25.62 M` (`v_x = 0.170 c`) by `t = 1115 M`, destroying fixed-origin GW extraction after `u ≈ 580 M`.
- **Root Cause:** The outgoing 1+log gauge wave ($v_{\rm gauge} = \sqrt{2}\,c$) hits the outer face at $r = 256\,M$ at $t = 256/\sqrt{2} = 181\,M$ and returns to the puncture at $t = 2 \times 181 = 362\,M$. The experimental `sbc_variant = nonwave`, `sbc_speed = metric`, `ghost_falloff = true`, `extrap_order = 4` options (in `athenak/src/z4c/z4c_sbc_ext.hpp`, only validated to $t \le 16\,M$ in `tracks/core/JOURNAL-faces.md`) amplified the reflected $Z_i/\Theta$ constraint mode, and `damp_kappa1 = 0.02` ($\tau \sim 50\,M$) could not damp it.
- **Verification of Fix:** Switching to stock Sommerfeld (`--sbc-mode stock`, omitting those 4 parameters) in `EMRI_q1e3_R6p40_it4` reduced `||Z||_2` at `t = 939 M` from `14.60 → 1.56e-4` (**93,000×**), `||Θ||_2` from `8.66 → 7.42e-5` (**117,000×**), and `|x_BH|` from `25.62 M → 0.093 M` (**275×**).

---

### Bug 2 [AVOIDED in It-4]: Exponential SMBH Horizon Mass Inflation at `damp_kappa1 = 0.50`
- **Symptom:** In the companion `GR_low_a082_amr` run (`damp_kappa1 = 0.50`, stock Sommerfeld), `M_AH` inflated exponentially from `1.0002 M → 2.814 M` by `t = 1103 M`, even after all particles were excised.
- **Root Cause:** Pure-vacuum `VF0`/`VF1` vs `VF2` ablations (`runs/zkl_nr/_mah_fast/`, `task-7692.log`) proved that `damp_kappa1 = 0.50` excites an unstable puncture-region constraint eigenmode ($\lambda_{\Theta} \approx +0.020\,M^{-1}$, inflating $M_{\rm AH}$ by `+3.67%` by `t = 250 M` regardless of BH box size `r_box = 0.85` vs `1.50 M`), whereas `damp_kappa1 = 0.02` (`VF2_k1_002_r150`) kept `max|ΔM_AH/M_0| = 9.39e-4` with `|x_BH| ~ 10⁻¹² M`.
- **Action:** Keep `damp_kappa1` small (`0.02`, or test `0.04`–`0.05` only if checked against pure-vacuum $M_{\rm AH}$ stability). Never raise global `damp_kappa1` to `0.50` around an `M = 1` puncture.

---

### Bug 3 [ACTIVE — PRIORITY 1]: Central-BH Wormhole→Trumpet $v = \sqrt{2}\,c$ Gauge Shock Polluting Full-Domain GW Signal
- **Symptom:** Observed directly in the 2D `xy` movie (`emri_R6p40_it4_xy_alpha_H_movie.gif`, frames `00000 → 00005`, `t = 0 → 100 M`) and final It-4 waveforms (`fig_emri_R6p25_it4_final_gw_pn_2sf.png`, `fig_emri_R6p40_it4_final_gw_pn_2sf.png`):
  1. At `t = 20 M` and `t = 40 M`, a bright spherical `|H| ~ 10⁻⁵–10⁻⁴` shell expands from the central BH to $r \approx 28\,M$ (`= 20√2`) and $r \approx 56\,M$ (`= 40√2`), sweeping across all 5 GW extraction spheres (`r = 20..58 M`) and creating a `~4 × 10⁻⁵` $\Psi_4^{(2,2)}$ junk burst (`3×` larger than the physical $1.4\times 10^{-5}$ EMRI signal) plus a persistent `|H| ~ 10⁻⁶` wave-zone bath.
  2. **Cubic outer-boundary $\ell = m = 4$ reflection spikes:** In BOTH `R6p25_it4` and `R6p40_it4`, huge `|rΨ4_44| ~ 10⁻⁴` spikes hit the extraction spheres at identical retarded times **`u ≈ 330 M`** (`= 2 × 256/√2 + 41 - 68 M`, first $\sqrt{2}\,c$ gauge round-trip off the cubic $\pm 256\,M$ outer faces!) and **`u ≈ 610 M`** (second / $c$-speed round-trip), corrupting higher modes and `F_E(u)`.
- **Root Cause:** Initializing the central SMBH as a time-symmetric Brill–Lindquist wormhole ($r_{\rm AH} = 0.50\,M$, $K_{ij} = 0$, $\beta^i = 0$, `lapse = precollapsed`) with `slow_start_lapse = false` causes violent collapse to a moving-puncture trumpet ($r_{\rm AH}: 0.50 \to 0.934\,M$ in `t < 15 M`). The resulting $O(1)$ radial gauge shock scatters off Cartesian AMR boundaries (`±1.95..±60 M`) and the cubic `±256 M` outer boundary into $\ell = 4$ and $\ell = 2$ Weyl/constraint noise at `O(10⁻⁵)` — the exact scale of our $q = 10^{-3}$ EMRI waveform.
- **Fix Recipe:**
  1. Enable **Slow-Start Lapse** (`slow_start_lapse = true`, `ssl_damping_amp = 0.6`, `ssl_damping_time = 20.0`, `ssl_damping_index = 1` — built into `athenak/src/z4c/z4c_calcrhs.cpp:813-820`, Etienne et al. 2024).
  2. Push the outer boundary from `±256 M` → **`±512 M`** (1 extra coarse root level, negligible MeshBlock overhead) so any residual outer-face gauge reflection cannot return until `u ≈ 695 M` (well after `R6p25` merger!).
  3. Run a **matched `q = 0` pure-vacuum central-BH twin** on the exact same mesh/gauge and subtract $\Psi_4^{\rm clean}(u) = \Psi_4^{\rm EMRI}(u) - \Psi_4^{\rm vac}(u)$ to cancel remaining $M = 1$ background grid/gauge artifacts to $O(q)$.

---

### Bug 4 [ACTIVE — PRIORITY 1]: Initial-Data Solver Operator Mismatch & Missing Analytic Particle Momentum
- **Symptom:** Right at `t = 0` (`frame_00000.png` of `EMRI_q1e3_R6p40_it4`), the 2D Hamiltonian map shows:
  - A strong **4-lobe `|H| ~ 10⁻³` quadrupole flower** centered on the particle at `(x, y) = (5.35, 0) M`.
  - Bright `|H| ~ 10⁻⁴` square rings along every AMR refinement boundary (`±2, ±4, ±15.5, ±30.5 M`).
  - An 8-petal `|H| ~ 10⁻³` Cartesian rosette around the central BH (`r ≈ 0.5..1.5 M`).
  - In `EMRI_q1e3_R6p40_it4.idsolve.txt`, while the 7-point residual `max|F7|` dropped `7.86e-4 → 1.02e-8`, **Z4c's 6th-order monitor `max|H|` actually increased from `2.21e-3 → 3.41e-3`**, and the vector residual stopped at `max|M| = 8.61e-4`.
- **Root Cause:**
  1. `gen_emri_run.py` set `id_residual = stencil` and `id_vector_residual = stencil` (2nd-order 7-point operator) instead of `id_residual = code` (Z4c's own 6th-order `NGHOST = 4` monitor including Z4c AMR prolongation/restriction; `athenak/src/particles/nrpic_idsolve.cpp:26,50`, `tracks/core/interfaces/id_solver2.md:268-272`).
  2. `gen_emri_run.py` set `comp0_p1..3 = -m_bare * u_cov` on the central puncture **but omitted `comp1_p1..3 = +m_bare * u_cov`** on the moving Gaussian particle, ignoring AthenaK's built-in analytic smeared Bowen-York clump curvature (`athenak/src/pgen/nrpic/nrpic_clump_curvature.hpp:39-41`). Consequently, the coarse 2nd-order vector solver (`id_vector_tol = 2e-3`) had to reconstruct the entire $1/r^2$ extrinsic curvature field from scratch across AMR boundaries.
- **Fix Recipe:**
  1. Add `comp1_p1, comp1_p2, comp1_p3 = +m_bare * u_cov` in `gen_emri_run.py`.
  2. Switch to `id_residual = code`, `id_puncture_radius = 1.5`, tighten `id_tol = 1e-8`, `id_vector_tol = 1e-5`, `id_lin_tol = 1e-4`, `id_mg_tol = 1e-4`, and benchmark `id_vector_residual = code` vs `stencil` on top of analytic `comp1_p`.

---

### Bug 5 [ACTIVE — PRIORITY 2]: Under-Resolved Wave Zone (`dx = 2.0 M`) & BH Core (`dx_BH = M/16`)
- **Symptom:** In `R6p25_it4` and `R6p40_it4`, `r = 30.5..60 M` lies on `level = 2` (`dx = 2.0 M`). At `dx = 2.0 M`:
  - `(4,4)` GW wavelength ($\lambda_{44} \approx 24.5\,M$) has only `~12` cells/wavelength.
  - Schwarzschild `l=m=2, n=0` QNM ringdown ($\omega_{220} = 0.3737\,M^{-1}$, $\lambda_{\rm QNM} = 16.8\,M$) has only **`8.4` cells/wavelength** at `r = 38, 48, 58 M`!
  - At the BH core, `dx_BH = M/16` (`bh_level = 7`) puts only `16` cells across the initial `D_AH = 1.0 M`, producing the `t = 0` 8-petal rosette.
- **Fix Recipe:** Raise the wave zone by +1 level (`dx = 1.0 M` out to `r = 62 M`, `dx = 0.5 M` out to `r = 32 M`), and test `dx_BH = M/32` (`bh_level = 8` with `L7` buffer out to `±3.5 M`) vs `dx_BH = M/16` in the parallel full-node ablation.

---

### Bug 6 [ACTIVE — UNDER INVESTIGATION]: Half-Rate Inspiral (`d ln J_orb / dt ≈ 51%` of 1SF) Despite Full 1SF GW Flux
- **Symptom:** Every `dx_p = M/8, nfilter = 8` run (`It-2`, `R6p40_it4`, `R6p25_it4`) shows:
  - Radiated GW flux `F_E_NR ≈ 1.16–1.28 × F_E_1SF` and `|rΨ4_22|` within `10–17%` of 1SF,
  - **Yet** orbital angular momentum decays at only **~51–52% of the 1SF GW rate**:
    - `R6p5_it2`: `-1.51e-6` vs `-2.96e-6 M⁻¹` (`51%`)
    - `R6p40_it4`: `-1.68e-6` vs `-3.27e-6 M⁻¹` (`51%`)
    - `R6p25_it4`: `-1.84e-6` vs `-3.55e-6 M⁻¹` (`52%`), delaying plunge/merger from `t_ISCO(1SF) = 225 M` (+ ~110 M plunge ≈ `335 M`) out to `t_merger_exc = 732.1 M`!
  - Conversely, `It-1` (`dx_p = M/16`) had `-9.02e-6` vs `-2.95e-6 M⁻¹` (`306%`, excess negative drag).
- **Hypotheses to Test Directly in the Full-Node 8-GPU Ablation:**
  1. **Residual self-force/drag offset** (`~ +1.6e-6 M⁻¹` at `dx_p = M/8, nfilter = 8, cfl = 0.35`, vs negative drag at `dx_p = M/16`; note `E1_dx8_nf8` measured `g_vy = +6.85e-6`, `g_uy = -2.52e-6`, `dln(mW)/dt = -2.26e-7` in flat space).
  2. **Initial data / orbital circularity coupling:** The `t = 0` `id_residual = stencil` 4-lobe `|H| ~ 10⁻³` error around the particle + omitted `comp1_p` + `omega_scale = 0.998` caused an initial outward radial drift (`6.40 → 6.44 M` over `t = 0..200 M`, one half near-ISCO radial epicycle $T_r \approx 400\,M$).
  3. **Finite Gaussian cloud size** ($\sigma_{\rm eff} = 0.2602\,M$ at `dx_p = M/8, nfilter = 8` vs `0.1301 M` at `dx_p = M/16`) and `cfl_number` (`0.35` vs `0.25`) / `source_stage_extrap` / `shift_eta_far` sensitivity.

---

## 3. Iteration 5 Verification & Production Recipe (Single Full B200 Node)

Because `nrpic_idsolve.cpp` requires single-rank execution (`Athena_ENABLE_MPI=OFF`, 1 GPU per simulation), we exploit a **full single B200 node** (7–8 B200 GPUs + 100+ host CPUs) in two tightly monitored phases:

### Phase A — Fast Parallel Ablation (`t = 80 M`, ~10–15 min wall-time across all GPUs simultaneously)
Verify every single fix quantitatively (`idsolve.txt` `max|H|`/`max|M|`, `t = 0` 2D `|H|` map, `t = 20..80 M` wave-zone `|H|`, `|rΨ4_22|` junk peak, vacuum-subtracted `|rΨ4_22|`, `d ln J_orb / dt`, and wall rate `s/M`):
1. `A0_baseline`: It-4 baseline (`R0=6.25 M`, `±256 M`, `stencil`, no `comp1_p`, no SSL, `L2` wave zone)
2. `A1_ssl_only`: + `slow_start_lapse = true` (`amp=0.6, time=20, index=1`)
3. `A2_id_code_comp1p`: + `id_residual = code`, `comp1_p` smeared BY, `id_tol = 1e-8`, `id_vector_tol = 1e-5` (no SSL)
4. `A3_ssl_id_l512_wz`: **Full Fix Recipe** (`±512 M` domain, `SSL`, `id_residual = code` + `comp1_p`, `L3`/`L4` wave zone `dx = 1.0 M` to `62 M`, `dx_BH = M/16`, `dx_p = M/8`)
5. `A4_full_bh32`: Same as `A3` with `dx_BH = M/32` (`bh_level = 8`)
6. `A5_full_dxp16`: Same as `A3` with `dx_p = M/16` (`p_level = 7`, `cfl = 0.25`) — directly tests Bug 6 (`d ln J_orb / dt` vs 1SF!)
7. `A6_vac_twin_A3`: Pure-vacuum `q = 0` twin of `A3` (for exact $\Psi_4^{\rm EMRI} - \Psi_4^{\rm vac}$ background subtraction test!)
8. *(if 8th GPU available)* `A7_vac_twin_A4`: Pure-vacuum `q = 0` twin of `A4` (`dx_BH = M/32`)

### Phase B — Full Iteration 5 Production Suite to Merger & Ringdown (Same Full Node)
Using the winning verified configuration from Phase A:
- Launch **`EMRI_q1e3_R6p25_it5`** (inspiral → ISCO plunge → merger → QNM ringdown) + its **exact matched `q = 0` pure-vacuum twin** (`VAC_ref_it5`) + **`EMRI_q1e3_R6p40_it5`** + a resolution-convergence run in parallel on the full node's GPUs.
- Continuously monitor from `t = 0` (`idsolve.txt` + `frame_00000` check) → `t = 40..100 M` (gauge shock / junk check) → `t = 200..400 M` (`d ln J_orb / dt` vs 1SF + vacuum-subtracted waveforms + `xy`/`xz` slices) → **plunge, merger (`t_merger_exc`, `ΔM_AH`, `S_z`), and QNM ringdown** using idle host CPUs on the same node (`CUDA_VISIBLE_DEVICES=""`).

---

## 4. Iteration 5 Results & Post-Fix Audit
*(To be updated live as Phase A ablation and Phase B production to merger complete.)*
