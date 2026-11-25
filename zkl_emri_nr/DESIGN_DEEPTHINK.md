# AGN Binary-EMRI Zeipel–Kozai–Lidov (ZKL) Oscillations in Full 3+1 Numerical Relativity: Deep-Think Architecture & Production Plan

> **Important Clarifications**
> 1. **Production Solver Requirement**: **All production ZKL runs use full 3+1 Numerical Relativity** (`Z4c` moving-puncture spacetime evolution coupled to self-gravitating relativistic particles in AthenaK/NRPIC). The pure-CPU 1PN+1.5PN EIH/Lense–Thirring scout (`tools/pn_zkl_scout.py`) is strictly a pre-flight parameter-selection tool and secular baseline reference.
> 2. **Tooling Availability**: No `"neon"` CLI, MCP tool, plugin, or environment skill is installed or configured on this system. This design synthesis was performed directly from first-principles triple-GR analysis, source verification against `athenak/src/`, and the verified 1PN+1.5PN scout matrix (`data/zkl_scout_matrix.json`).
> 3. **GPU Scheduling**: No GPU jobs will be launched until `gb204` is free from the currently active 24h `64^3` 1M-particle Kerr `0.90` disruption run (`PID 3917314`), or unless explicitly halted earlier by the user.

---

## 1. Relativistic Binary-EMRI Physics & Verified Scout Baseline

Consider an inclined stellar-mass compact binary of individual masses $m_1, m_2$ ($m_{\rm bin} = m_1 + m_2 \ll M_0$) orbiting a supermassive black hole (SMBH) of mass $M_0 = 1.0$ and dimensionless Kerr spin $\bm{\chi}_0 = (0, 0, \chi_0)$ at outer semimajor axis $a_{\rm out}$, with inner semimajor axis $a_{\rm in}$, initial inner eccentricity $e_0$, and mutual orbital inclination $I_0$.

### 1.1 Fundamental Scales & Regimes
- **Hill Stability Boundary**:
  $$R_{\rm H} = a_{\rm out}\left(\frac{m_{\rm bin}}{3 M_0}\right)^{1/3}, \qquad f_{\rm H} \equiv \frac{a_{\rm in}}{R_{\rm H}} \lesssim 0.40.$$
  Keeping $f_{\rm H} \in [0.26, 0.39]$ prevents dynamical three-body Hill ionization while keeping the outer tidal lever arm strong enough that full ZKL cycles complete within practical full-NR wall-clock horizons ($t_{\rm ZKL} \sim 1.3\text{–}1.9 \times 10^3\,M$).
- **Quadrupole ZKL Timescale**:
  $$t_{\rm ZKL} \approx \frac{1}{2}\frac{P_{\rm out}^2}{P_{\rm in}}\frac{M_0 + m_{\rm bin}}{M_0} = \frac{2\pi}{\sqrt{3}}\left(\frac{a_{\rm out}^3}{M_0}\right)^{1/2} f_{\rm H}^{-3/2}.$$
  At fixed Hill fraction $f_{\rm H}$ and outer separation $a_{\rm out}$, $t_{\rm ZKL}$ is independent of $m_{\rm bin}$.
- **1PN Pericenter Precession Quenching Parameter**:
  $$\epsilon_{\rm GR} \equiv \frac{\dot{\omega}_{\rm 1PN}}{t_{\rm ZKL}^{-1}} = \frac{3\, m_{\rm bin}^2\, a_{\rm out}^3}{M_0\, a_{\rm in}^4}.$$
  Unlike $t_{\rm ZKL}$, $\epsilon_{\rm GR}$ scales steeply as $m_{\rm bin}^2 / a_{\rm in}^4$. Varying $a_{\rm in}$ at fixed $m_{\rm bin} = 0.008\,M_0$ and $a_{\rm out} = 15\,M$ isolates pure 1PN quenching from mass-ratio recoil effects.
- **1.5PN Kerr Spin–Orbit Coupling & Octupole Channel**:
  Frame dragging from the central SMBH spin $\bm{S}_0 = M_0^2 \bm{\chi}_0$ drives outer nodal/apsidal precession, shifting the ZKL secular resonance. Across our scout suite at $\epsilon_{\rm GR} = 2.411$, **prograde** SMBH spin ($\chi_0 = +0.7, +0.9$) quenches eccentricity growth ($e_{\max} \approx 0.11$), whereas **retrograde** SMBH spin ($\chi_0 = -0.7$) resonantly amplifies excitation up to $e_{\max} = 0.948$ ($r_{\min} = 0.074\,M$). Breaking inner mass symmetry ($q = m_2/m_1 = 1/3$) activates octupole-order terms that re-excite eccentricity ($e_{\max} = 0.412$) even in the prograde spin-quenched regime.

### 1.2 Local Fermi-Normal $\leftrightarrow$ Global Conformal/Harmonic IC Map
Initializing a bound binary inside the SMBH potential $\Phi_0 = M_0/a_{\rm out}$ requires transforming the binary's local proper rest-frame elements $(\bm{R}_{\rm loc}, \bm{U}_{\rm loc})$ into global harmonic/isotropic NRPIC coordinates $(\bm{r}_{\rm harm}, \bm{u}_{\rm harm})$, accounting for isotropic conformal contraction ($1 - \Phi_0$), special-relativistic Lorentz contraction along the binary COM velocity $\bm{V}_{\rm com}$, and gravitational/kinematic clock rate matching the 1PN two-body force balance:
$$\bm{r}_{\rm harm} = (1 - \Phi_0)\bm{R}_{\rm loc} - \frac{1}{2}(\bm{R}_{\rm loc}\cdot\bm{V}_{\rm com})\bm{V}_{\rm com},$$
$$\bm{u}_{\rm harm} = \left(1 - \frac{5}{2}\Phi_0 - \frac{1}{2}V_{\rm com}^2\right)\bm{U}_{\rm loc} - \frac{1}{2}(\bm{U}_{\rm loc}\cdot\bm{V}_{\rm com})\bm{V}_{\rm com}.$$
Exact algebraic inversion of this map recovers instantaneous local Fermi-frame $(a_{\rm in}, e_{\rm in}, I)$ during post-processing without artificial coordinate-$P_{\rm out}$ eccentricity spikes. Notice that in naive Newtonian initial coordinates at $a_{\rm out}=15\,M$, $e_{\rm in}$ spuriously spikes above $0.35\text{–}0.99$ within one inner orbit, whereas the Fermi-harmonic transform preserves $e_{\rm in}(t=0)=0.050$ smoothly (`unbound = False` across all 11 scout cases).

### 1.3 Verified 1PN+1.5PN Scout Matrix (`data/zkl_scout_matrix.json`, $M_0 = 1.0$, $a_{\rm out} = 15\,M$, $e_0 = 0.05$)

| Run ID | Suite | $m_1, m_2$ [$M_0$] | $a_{\rm in}$ [$M$] | $I_0$ [deg] | $\chi_0$ | $f_{\rm H}$ | $\epsilon_{\rm GR}$ | $t_{\rm ZKL}$ [$M$] | $a_{\rm in}/\Delta x_{24}$ | $e_{\max}^{\rm 1PN}$ | $r_{\min}$ [$M$] |
|---|---|---|---|---|---|---|---|---|---|---|---|
| `I20_subcrit` | Inclination | `0.004, 0.004` | `0.72` | `20` | `0.0` | `0.346` | `2.411` | `1552.3` | `17.3` | `0.128` | `0.703` |
| `I60_mild` | Inclination | `0.004, 0.004` | `0.72` | `60` | `0.0` | `0.346` | `2.411` | `1552.3` | `17.3` | `0.158` | `0.670` |
| `FID_I82_chi0` | Fiducial | `0.004, 0.004` | `0.72` | `82` | `0.0` | `0.346` | `2.411` | `1552.3` | `17.3` | `0.394` | `0.467` |
| `I86_high` | Inclination | `0.004, 0.004` | `0.72` | `86` | `0.0` | `0.346` | `2.411` | `1552.3` | `17.3` | `0.687` | `0.253` |
| `GR_low_a082` | GR quench | `0.004, 0.004` | `0.82` | `82` | `0.0` | `0.394` | `1.433` | `1277.2` | `19.7` | `0.868` | `0.113` |
| `GR_mid_a062` | GR quench | `0.004, 0.004` | `0.62` | `82` | `0.0` | `0.298` | `4.385` | `1942.6` | `14.9` | `0.254` | `0.515` |
| `GR_high_a055` | GR quench | `0.004, 0.004` | `0.55` | `82` | `0.0` | `0.264` | `7.081` | `2325.0` | `13.2` | `0.130` | `0.559` |
| `SPIN_p07` | Kerr spin | `0.004, 0.004` | `0.72` | `82` | `+0.7` | `0.346` | `2.411` | `1552.3` | `17.3` | `0.109` | `0.714` |
| `SPIN_m07` | Kerr spin | `0.004, 0.004` | `0.72` | `82` | `-0.7` | `0.346` | `2.411` | `1552.3` | `17.3` | `0.948` | `0.074` |
| `SPIN_p09` | Kerr spin | `0.004, 0.004` | `0.72` | `82` | `+0.9` | `0.346` | `2.411` | `1552.3` | `17.3` | `0.109` | `0.716` |
| `OCT_q3_I80` | Octupole | `0.006, 0.002` | `0.72` | `80` | `+0.7` | `0.346` | `2.411` | `1552.3` | `17.3` | `0.412` | `0.460` |

*Note*: Diagnostic plot saved at `zkl_emri_nr/paper/figures/fig_zkl_scout.{pdf,png}`.

---

## 2. Cheaper, Stable Full-NR Architecture (AthenaK + High-Order NRPIC)

To make a systematic multi-run suite affordable on a single `gb204` GPU while preserving central puncture stability over $t \gtrsim 1800\,M$ and clean gravitational waveforms, we combine **`32^3` MeshBlocks**, **static hollow-ring orbital refinement**, **2 gravitating particles**, and **central puncture initial data solved by `id_solve`**.

### 2.1 Why Static `32^3` Hollow-Ring Refinement?
1. **Zero AMR Regridding Noise in Waveforms**: Using `<mesh_refinement> refinement = static` with stacked `<refined_regionK>` boxes avoids dynamic block creation/destruction boundary reflections when extracting subtle ZKL waveform modulations at **`waveform_dt = 0.1`** ($5\times$ higher cadence than `0.5` in `kerr09_tde_1m.athinput`).
2. **Symmetric Cell-Corner Puncture Placement**: Per `nrpic_idsolve.cpp`, a puncture cannot sit on a cell center (`IdFatal("<particles> id_solve: a puncture sits on a cell centre")`). A root domain `[-128.0, 128.0]^3` with `nx1=nx2=nx3=128` (`dx_0 = 2.0 M`, `4 x 4 x 4` blocks of `32^3`) places `(0,0,0)` strictly on a cell corner/face at all levels.
3. **Hollow Orbital Slab Optimization**: Four non-overlapping static `<refined_region>` boxes forming a square annulus `max(|x|,|y|) in [12, 18] M`, `z in [-2, 2] M` cover the entire outer orbital belt $r_{\rm out} = 15 \pm 2.1\,M$ and inner tilted plane ($|z| \le a_{\rm in} \le 0.86\,M$) at fine orbital resolution while leaving the empty `|x|,|y| < 12` annular interior coarser (`dx = M/8`), cutting fine orbital blocks by ~44% relative to a solid slab:

| Level | Cell width $\Delta x$ | Static Region Box(es) | Purpose |
|---|---|---|---|
| `L0` | `2.0 M` | `[-128, 128]^3` (`4^3` blocks of `32^3`) | Outer asymptotic domain, Robin MG boundary |
| `L1` | `1.0 M` | `[-64, 64]^3` | Buffer to wave zone |
| `L2` | `0.5 M` | `[-48, 48]^3` | GW extraction spheres (`r = 22, 30, 38 M`, `extraction_nlev = 2`) |
| `L3` | `0.25 M` | `[-24, 24]^3` | Near-field tidal zone |
| `L4` | `0.125 M` (`M/8`) | `[-20, 20]^2 x [-4, 4]` | Outer orbital envelope & central BH skirt |
| `L5` | `0.0625 M` (`M/16`) | 4 ring boxes: `x in [12,18]`, `x in [-18,-12]`, `y in [12,18]`, `y in [-18,-12]` (`z in [-2,2]`); plus `[-4,4]^3` around SMBH | Inner-binary orbit (`11.5–13.1` cells per $a_{\rm in}$, `m_i/dx = 0.064 << 1`) & central puncture L5 buffer |
| `L6` | `0.03125 M` (`M/32`) | `[-2, 2]^3` around SMBH origin (`4^3 = 64` blocks) | Nonspinning SMBH ($\chi_0 = 0$) core (`32.0` cells/diameter at $t=0$, `~53` evolved); nested buffer for spinning runs |
| `L7` | `0.015625 M` (`M/64`) | `[-1, 1]^3` around SMBH origin (`+64` blocks; spinning runs only) | Spinning Kerr SMBH ($|\chi_0| \in \{0.7, 0.9\}$) core (`>= 32` cells across evolved polar/mean horizon diameter) |

### 2.1.1 Enforcing $\ge 32$ Cells Across the Central Horizon Diameter
Measurements from our active $\chi_0 = 0.90$ run (`kerr09_tde_1m.horizon_summary_0.txt`, `comp0_mass = 0.4535`, `M_AH ≈ 1.00–1.01 M`) show why `M/32` alone falls short at high spin:
- At $t = 0$ (Bowen–York slice): `meanradius = 0.2283 M`, `minradius = 0.2280 M` $\implies D_0 = 0.456\,M$ (`14.6` cells at `M/32`, contributing to the initial relaxation drift from `M_AH = 1.0003` to `1.0110 M`).
- After trumpet relaxation ($t = 57.6\,M$): `meanradius = 0.5467 M`, `minradius = 0.4637 M` $\implies$ polar diameter $D_{\min} = 0.9275\,M$ (`29.7` cells at `M/32` — **below the 32-cell threshold**) and mean diameter $D_{\rm mean} = 1.0935\,M$ (`35.0` cells at `M/32`).

To guarantee $\ge 32$ cells across the central black hole horizon for every spin without inflating the outer orbital slab or wave zone:

| Configuration | Core Level & $\Delta x_{\rm BH}$ | Total `32^3` Blocks (Cells) | Initial Diameter $D_0 / \Delta x_{\rm BH}$ | Evolved Diameter $D_{\min} / \Delta x_{\rm BH}$ ($D_{\rm mean}/\Delta x_{\rm BH}$) | RK3 CFL $\Delta t$ (`cfl=0.40`) | Cycles to `t=1800 M` |
|---|---|---|---|---|---|---|
| **$\chi_0 = 0$ (Suites 1 & 2, 7 runs)** | `L6`: `M/32` (`[-2, 2]^3`) | `~600` (`~19.7M`) | `32.0` ($D_0 \approx 1.00\,M$) | `~53` ($D_{\rm AH} \approx 1.66\,M$) | `0.0125 M` | `144,000` |
| **$|\chi_0| = 0.7$ (Suites 3 & 4, 3 runs)** | `L7`: `M/64` (`[-1, 1]^3`) | `~664` (`~21.8M`) | `~45` ($D_0 \approx 0.70\,M$) | `~83` ($D_{\min} \approx 1.30\,M$) | `0.00625 M` | `288,000` |
| **$\chi_0 = +0.9$ (`SPIN_p09`, 1 run)** | `L7`: `M/64` (`[-1, 1]^3`) | `~664` (`~21.8M`) | `29.2` (`>32` by $t=0.8\,M$) | `59.4` polar (`70.0` mean) | `0.00625 M` | `288,000` |
| **Alt. Phase-0 Benchmark (`VAL_BH_42`)** | `L7`: `M/42.7` (`[-1.5, 1.5]^3` on `[-96,96]^3, nx=64`) | `~950` (`~31.1M`) | `19.5` ($\chi_0=0.9$) / `~30` ($0.7$) | `39.6` polar / `46.7` mean ($\chi_0=0.9$) | `0.00938 M` | `192,000` |

Note the practical cost split: adding `L7` (`[-1, 1]^3`) adds only `+64` blocks (`+2.1M` cells, keeping all runs far smaller than the active `48M`-cell 1M cloud grid), while cutting the CFL timestep by $2\times$ (`0.00625 M` vs `0.0125 M`) exclusively for the 4 spinning runs (`SPIN_p07`, `SPIN_m07`, `SPIN_p09`, `OCT_q3_I80`), leaving all 7 Schwarzschild runs at `0.0125 M`. Tightening `a_out` (e.g., to `13 M`) remains a backup lever in Phase 0 if cycle throughput needs shorter `t_ZKL \propto a_{\rm out}^{3/2}`.

- **Convergence & Horizon Calibration Check (Phase 0)**: Run `VAL_CONV_24` (`dx_0 = 1.5 M` on `[-144, 144]^3`, `nx = 192` $\implies$ `dx_bin = M/21.3`, `dx_BH = M/42.7`) and `VAL_BH_RES` (`\chi_0 = +0.9` comparing `M/32`, `M/42.7`, and `M/64` cores) over $t \le 300\,M$ to verify irreducible SMBH horizon mass $M_{\rm AH}$ and spin $\chi_{\rm AH}$ drift remain $< 10^{-3}$, confirm $\ge 32$ cells across evolved $D_{\min}$, and ensure two-particle binding holds without self-trapping (`m_i/\Delta x_{\rm bin} \le 0.1`).
- **Projected Memory Footprint (scaling estimate, not yet benchmarked)**: Whereas the active 1M-particle `64^3` cloud mesh (`183` blocks $\approx 48.0\text{M}$ cells + $10^6$ particle buffers) occupies `122.8 GiB` on `gb204`, this `32^3` hollow-ring + core grid uses $\sim 600\text{–}664$ blocks ($\sim 19.7\text{–}21.8\text{M}$ cells) with only $N = 2$ particles (negligible particle push/deposit cost), fitting comfortably inside $\sim 35\text{–}45\text{ GiB}$ VRAM with substantially higher evolution speed ($M/\text{hr}$).

### 2.2 Verified AthenaK Solver & Initial-Data Configuration
All keys below are verified against `athenak/src/` and `kerr09_tde_1m.athinput` / `tracers_single.athinput`:
- **Spacetime (`<z4c>`)**: `lapse_oplog = 2.0`, `lapse_harmonicf = 1.0`, `lapse_harmonic = 0.0`, `lapse_advect = 1.0`, `shift_Gamma = 0.75`, `shift_eta = 2.0`, `shift_advect = 1.0`, `diss = 0.5`, `chi_div_floor = 1.0e-5`, `damp_kappa1 = 0.02`, `damp_kappa2 = 0.0`, `tracker_mode = ode`, `nrad_wave_extraction = 3`, `extraction_radius_0 = 22.0`, `extraction_radius_1 = 30.0`, `extraction_radius_2 = 38.0`, `extraction_nlev = 2`, **`waveform_dt = 0.1`** ($5\times$ higher cadence than `0.5`).
- **Particles (`<particles>`)**:
  `particle_type = nrpic`, `pusher = vlasov_hybrid`, `vlasov_mode = hybrid`, **`vlasov_pusher = gl4`**, **`vlasov_time_interp = quadratic`**, **`interp = quintic`**, `metric = mesh`, `tolerance = 2.0e-14`, `max_iterations = 200`, `deposit = true`, `deposit_shape = tsc`, `deposit_comp_c = 0.0`, `nfilter = 2`, **`filter_metric_conservative = true`**, **`filter_mcons_unsplit = true`**, **`source_stage_extrap = true`**, `matter_stride = 1` (update full particle self-gravity every metric step cleanly since $N=2$), `traj_ntrack = 2`, `traj_dcycle = 4`, `snap_dt = 2.5`.
- **Constraint Initial-Data Solver (`<particles>` + `<gravity>`)**:
  `id_solve = true`, `id_vector = true`, `id_residual = stencil`, `id_vector_residual = stencil`, `id_psi_init = trial`, `id_puncture_radius = 1.0`, `id_far = multipole`, `id_tol = 1.0e-8`, `<gravity> four_pi_G = 1.0`, `threshold = 0.0`, `mg_bc = robin`, `robin_x1 = 0.0`, `robin_x2 = 0.0`, `robin_x3 = 0.0`.
- **Central SMBH Puncture (`<problem>`)**:
  `pgen_name = nrpic_cf`, `ncomp = 1`, `comp0_type = puncture`, `comp0_mass` calibrated so initial AH mass equals $1.000\,M$ (`~0.5000` for $\chi_0=0$, `~0.4535` for $\chi_0=0.9$), `comp0_p{1,2,3}` equal and opposite to the total particle ADM linear momentum (zero net triple momentum), `comp0_s3 = \chi_0 M_0^2`, `lapse = precollapsed`, `puncture_setup = false`.
- **Checkpoints (`<output*>`)**:
  `.hst` (`dt = 0.1`), `.rst` checkpoints (`dt = 100.0`, enabling safe resume/extend for each sweep run), 2D slices `z4c_alpha` and `con_H` in both `x-y` (`slice_x3 = 0.001`) and `x-z` (`slice_x2 = 0.001`) at `dt = 2.5`.

---

## 3. Live Movie & High-Cadence GW Diagnostic Pipeline

Following the pure-CPU movie workflow used for `kerr09_cloud_1m_24h` (`render_kerr09_tde_movie.py`, always with `CUDA_VISIBLE_DEVICES=""`), build `render_zkl_movie.py` producing synchronized multi-panel frames every `dt = 2.5 M`:
1. **Top-Left (Global Outer Orbit $x\text{–}y$ Slice)**: `z4c_alpha` heatmap (`|x|,|y| <= 18 M`) with SMBH apparent horizon (`horizon_summary_0.txt`), binary COM orbital trail from `.traj.bin`, and both gravitating BH particle markers.
2. **Top-Right (Comoving Inner-Binary Frame)**: Recentered zoom (`|\Delta x|,|\Delta y|,|\Delta z| <= 1.5 M`) showing both BH trajectories projected on local inner orbital plane + $\text{x–z}$ side projection tracking ZKL spin-inclination nutation and pericenter bursts.
3. **Bottom-Left (Secular Dynamics vs 1PN)**: Full-NR Fermi-inverted $e_{\rm in}(t)$ and $I(t)$ overlaid against the 1PN+1.5PN secular scout baseline (`pn_zkl_scout.py`).
4. **Bottom-Right (High-Cadence $r\Psi_4$ Waveform, `dt = 0.1 M`)**: Mode $(2,2)$ real/amplitude strain/Weyl scalar zoomed across recent pericenter passages alongside Constraint $\|\mathcal{H}\|_2(t)$ and $M_{\rm AH}(t)$ diagnostics.

Outputs: Incremental `frame_NNNNN.png`, animated `*.webp` and `*.gif` (and `.mp4` if `ffmpeg` available).

---

## 4. Phased Full-NR Production Schedule (Pending `gb204` Availability)

All production ZKL runs listed below are **full 3+1 Numerical Relativity simulations** and remain **queued (NOT started)** until the active 1M Kerr disruption run completes:
1. **Phase 0 (Validation & Calibration, $t_{\rm max} = 300\,M$)**: Calibrate $\chi_0 \in \{0, \pm 0.7, +0.9\}$ bare masses and run `VAL_CONV_24` ($M/16$ vs $M/21.3$ orbital convergence) plus `VAL_BH_RES` (`M/32` vs `M/42.7` vs `M/64` central core benchmark) to confirm $\ge 32$ cells across evolved horizon diameter, horizon $M_{\rm AH}/\chi_{\rm AH}$ stability, and zero spurious Fermi IC eccentricity drift.
2. **Phase 1 (Core Physics Matrix — 7 Key Full-NR Runs, $t_{\rm max} = 1800\,M$ each)**:
   - Suite 1 (Inclination threshold): `I20_subcrit`, `FID_I82_chi0`, `I86_high`
   - Suite 2 (GR quenching): `GR_low_a082`, `GR_high_a055`
   - Suite 3 (Kerr spin): `SPIN_p07`, `SPIN_m07`
3. **Phase 2 (Extended Spin & Octupole Completion — 4 Full-NR Runs)**:
   - `I60_mild`, `GR_mid_a062`, `SPIN_p09`, `OCT_q3_I80`
4. **Phase 3 (Paper Completion)**: Populate `[PENDING FULL-NR RUNS]` placeholders in `zkl_emri_nr/paper/main.tex` with full-NR ZKL orbital cycles, $r\Psi_4$ waveform modulation analysis at `0.1 M` cadence, constraint convergence figures, and finalize PRL submission.
