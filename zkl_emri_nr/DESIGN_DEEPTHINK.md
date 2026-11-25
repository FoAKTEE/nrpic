# AGN Binary-EMRI Zeipel–Kozai–Lidov (ZKL) Oscillations in Full 3+1 Numerical Relativity: Deep-Think Architecture & Production Plan

> **Important Clarifications**
> 1. **Production Solver Requirement**: **All production ZKL runs use full 3+1 Numerical Relativity** (`Z4c` moving-puncture spacetime evolution coupled to self-gravitating relativistic particles in AthenaK/NRPIC). The pure-CPU 1PN+1.5PN EIH/Lense–Thirring scout (`tools/pn_zkl_scout.py`) is strictly a pre-flight parameter-selection tool and secular baseline reference.
> 2. **Tooling Availability**: No `"neon"` CLI, MCP tool, plugin, or environment skill is installed or configured on this system. This design synthesis was performed directly from first-principles triple-GR analysis, source verification against `athenak/src/`, and the verified 1PN+1.5PN scout matrix (`data/zkl_scout_matrix.json`).
> 3. **GPU Scheduling**: All GPU evolutions run exclusively on `gb204` (`NVIDIA B200`, Slurm job `1964821`, never using external B200 queues). Following Phase 0 calibration (`m16_64_L5`), late-time `t=200–300 M` artificial inspiral/resolution loss diagnosis (`G1..G5` gauge/stride ablation), and compact dynamic-AMR verification (`AMR_close`, `P0_compact_s1`), the flagship full-NR evolution **`GR_low_a082_amr`** (`amr_dyn`, `L5->L8`) is now running all the way toward ZKL-driven particle merger before launching the remaining 6 Phase 1 runs.

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

## 2. Validated Zero-Drag Dynamic-AMR Full-NR Architecture (AthenaK + NRPIC on `gb204`)

Earlier static circular-ring runs (`m16_64_L5`, `3,480` blocks, $\Delta x_{\rm bin} = M/16$, `matter_stride = 4`, `shift_eta = 2.0`, `damp_kappa1 = 0.02`) showed two late-time ($t \approx 200\text{–}300\,M$) bottlenecks: (i) spurious secular outer orbital inspiral caused by Z4c constraint/gauge drag (`matter_stride > 1` + standard $\eta = 2.0$, $\kappa_1 = 0.02$), and (ii) insufficient static resolution ($\Delta x_{\rm bin} = M/16$) during high-eccentricity ZKL pericenter passages ($r_{\min} \sim 0.11\,M$) and merger. Our production **`amr_dyn`** architecture resolves both simultaneously on `gb204`.

### 2.1 Zero-Drag Gauge/Stride Calibration & `amr_dyn` Moving Hierarchy
1. **Self-Force Elimination & Conformal Initial Data**: Using **`deposit_shape = pcs`**, **`interp = quintic`**, split metric-conservative filtering (`filter_metric_conservative = true`, `filter_mcons_unsplit = false`), **`source_stage_extrap = true`**, **`rk3 cfl_number = 0.35, diss = 0.20`** with **`nfilter = 6`** ($\sigma_{\rm eff} = \sqrt{4/12 + 6/2}\,\Delta x = 1.826\,\Delta x = 0.1141\,M$ at $L_5 = M/16$), plus `<problem> ncomp = 3` conformal Gaussian wells and bare-mass compensation `m_bare = m_i (1 + m_i / (\sqrt{2\pi}\,\sigma_{\rm eff}))`, eliminates grid-aliasing self-force and matches ADM mass/momentum ($|\mathbf{P}_{\rm ADM}| \le 1.3\times 10^{-9}$).
2. **Gauge & Matter-Stride Drag Fix (`G1..G5` Ablation on `gb204`)**: Ablating `matter_stride`, `nfilter`, `damp_kappa1`, and `shift_eta` at `L4–L5` established that **`matter_stride = 1`**, **`damp_kappa1 = 0.50`**, and tracker-following Gamma-driver shift damping (`shift_eta_profile = true`, `shift_eta = 0.07`, `shift_eta_mref = 2.0 / shift_eta = 28.5714`, `shift_eta_width = 2.0`) suppress specific orbital angular-momentum drift down to `|d ln L_z / dt| = 3.887e-5 M^-1` (`g_uy ~ -1.3e-5 to -3.7e-5 M^-1`, `H2(15) = 5.7e-5 to 1.83e-4`), whereas `matter_stride = 2` degraded drift to `-1.441e-4 M^-1`.
3. **Separation-Adaptive `NRPICCFRefinement` (`amr_dyn`)**: Combining `z4c_amr/method = tracker` (`radius_0_rad = 24.0`, `radius_0_reflevel = 1`) with custom `NrpicCFRefinement` (`athenak/src/pgen/nrpic/nrpic_cf.cpp`, `<amr_criterion0> method = user`, `ncycle_check = refinement_interval = 16`, `max_nmb_per_rank = 2400`) maintains a compact wave-zone + SMBH puncture hierarchy while dynamically nesting `16^3` blocks around the comoving binary from `L5` ($\Delta x = M/16$) down to `L8` ($\Delta x = M/128$ = `0.0078125 M`) as separation $d_{\min}$ shrinks (`track_cells_between = 8.0`, `track_buffer_cells = 14.0`, `track_min_radius = 1.0`, `track_hysteresis = 2.50`, `track_spatial_hysteresis = 1.12`).

| Level | Cell width $\Delta x$ | Dynamic / Static Zone | Purpose |
|---|---|---|---|
| `L0` | `2.0 M` | `[-64, 64]^3` (`4^3` blocks of `16^3`) | Asymptotic domain, multipole Robin MG boundary & extraction sphere `r = 38 M` (`extraction_nlev = 2`) |
| `L1` | `1.0 M` | `r <= 24.0 M` (`z4c_amr tracker`) | Compact wave zone (`extraction_radius = 22, 30, 38 M`, `waveform_dt = 0.1 M`) |
| `L2–L4` | `0.5 – 0.125 M` | Automatic 2:1 AMR transition shells | Connects `L1` smoothly to central SMBH core and orbital binary patch |
| `L5–L8` | `0.0625 – 0.0078125 M` (`M/16 – M/128`) | Dynamic binary box (`track_cells_between = 8`, `buffer = 14`) | Tracks shrinking pericenter ($r_{\min} \sim 0.11\,M$) toward merger (`596 -> 834` blocks vs `3,480` static) |
| `L6 / L7` | `0.03125 / 0.015625 M` (`M/32 / M/64`) | `[-0.85, 0.85]^3` (`|\chi_0| \le 0.7`) or `[-0.48, 0.48]^3` ($\chi_0 = +0.9$) | Central SMBH puncture core (`D_AH = 32.0 -> 64.2` cells at $\chi_0=0$) |

### 2.1.1 Measured Validation, AMR Close-Encounter & Zero-Drag Benchmarks (`gb204`)
| Calibration / Benchmark Run | Configuration & Mesh | Blocks & Peak VRAM / Speed | Constraint & Horizon | Orbital / Secular Fidelity |
|---|---|---|---|---|
| **`VAL_P0_GR_low_a082`** (`t = 25.0 M`) | Static `m16_64_L5`, `L6` (`M/32`), `ms=4, nf=4` | `3,480` blks, `134.6 GiB`, `77.11 M/hr` | `M_AH: 1.000205 -> 1.000143` (`-6.15e-5`), `32.0 -> 78.9` cells/D | `e_in in [0.0188, 0.1084]`, `r_prop = 0.8609 -> 0.7892 M` |
| **`SPIN_p07` Calib.** (`nlim=1`) | Static `m16_64_L5`, $\chi_0=+0.7$, `comp0_mass=0.7518` | `3,480` blks, `133.8 GiB` | `M_AH(0) = 1.000138`, $S_z = 0.699999$ | `P_ADM = 9.82e-10` |
| **`AMR_close`** (`t = 3.5 M`) | Close encounter, `L5->L8->L6` (`z4c_amr=trivial`) | `344 -> 820 -> 400` blks, `wall = 110.34 s`, `NaN = False` | Dynamic refine `5->6` (`0.5685 M`), `6->7` (`0.2928 M`), `7->8` (`0.1413 M`); derefine `8->7->6` | Tracks pericenter `d: 0.7000 -> 0.0555 -> 0.6486 M` |
| **`P0_compact_s1`** (`t = 15.0 M`, **WINNER**) | `amr_dyn`, `L6` BH + `L5..L8` track, `ms=1, nf=6, k1=0.50, eta=0.07` | **`596 -> 834 -> 778`** blks, **`159.2 M/hr`** (`2.06x` vs static) | `M_AH0 = 1.0002`, `\|dM/M0\| = 7.26e-5`, `D_AH = 32.0 -> 64.2`, `H2(15) = 1.83e-4`, `M2(15) = 5.79e-5` | **`d ln L_z/dt = -3.887e-5 M^-1`**, `r_com = 15.00 -> 15.07`, `e15 = 0.097`, `max\|Psi4\| = 6.53e-4` |
| **`P0_compact_s2`** (`t = 15.0 M`, rejected) | Same as `P0_compact_s1` with `matter_stride = 2` | `596 -> 834 -> 778` blks, `201.2 M/hr` | `H2(15) = 1.94e-4` | `d ln L_z/dt = -1.441e-4 M^-1` (`> 5e-5` cutoff) |

### 2.2 Verified AthenaK Solver & Initial-Data Configuration
All keys below are verified against `athenak/src/` and `P0_compact_s1` on `gb204` (`gen_zkl_run.py --mesh-preset amr_dyn`):
- **Mesh & Refinement (`<mesh_refinement>`, `<z4c_amr>`, `<amr_criterion0>`, `<particles_amr>`)**: `refinement = adaptive`, `max_nmb_per_rank = 2400`, `num_levels = 10`, `ncycle_check = 16`, `refinement_interval = 16`, `<z4c_amr> method = tracker, radius_0_rad = 24.0, radius_0_reflevel = 1`, `<amr_criterion0> method = user`, `<particles_amr> track_particles = true, track_min_level = 5, track_max_level = 8, track_cells_between = 8.00, track_buffer_cells = 14.00, track_min_radius = 1.00, track_hysteresis = 2.50, track_spatial_hysteresis = 1.12`.
- **Time Integration & Spacetime (`<time>`, `<z4c>`)**: `integrator = rk3`, `cfl_number = 0.35`, `lapse_oplog = 2.0`, `lapse_harmonicf = 1.0`, `lapse_harmonic = 0.0`, `lapse_advect = 1.0`, `shift_Gamma = 0.75`, `shift_eta = 0.07`, `shift_eta_profile = true`, `shift_eta_mref = 28.5714285714`, `shift_eta_width = 2.0`, `shift_advect = 1.0`, `diss = 0.20`, `chi_div_floor = 1.0e-5`, `damp_kappa1 = 0.50`, `damp_kappa2 = 0.0`, `tracker_mode = ode`, `nrad_wave_extraction = 3`, `extraction_radius_{0,1,2} = 22.0, 30.0, 38.0`, `extraction_nlev = 2`, **`waveform_dt = 0.1`**.
- **Particles (`<particles>`)**:
  `particle_type = nrpic`, `pusher = vlasov_hybrid`, `vlasov_mode = hybrid`, **`vlasov_pusher = gl4`**, **`vlasov_time_interp = quadratic`**, **`interp = quintic`**, `metric = mesh`, `tolerance = 2.0e-14`, `max_iterations = 200`, `deposit = true`, **`deposit_shape = pcs`**, `deposit_comp_c = 0.0`, **`nfilter = 6`**, **`filter_compensate = false`**, **`filter_metric_conservative = true`**, **`filter_mcons_unsplit = false`**, **`source_stage_extrap = true`**, **`matter_stride = 1`**, `traj_ntrack = 2`, `traj_dcycle = 4`, `snap_dt = 5.0`.
- **Constraint Initial-Data Solver (`<particles>` + `<gravity>`)**:
  `id_solve = true`, `id_vector = true`, `id_residual = stencil`, `id_vector_residual = stencil`, `id_psi_init = trial`, `id_puncture_radius = 1.0`, `id_far = multipole`, `id_tol = 1.0e-7`, `id_vector_tol = 1.0e-4`, `id_maxit = 25`, `<gravity> four_pi_G = 1.0`, `threshold = 0.0`, `mg_bc = robin`.
- **Three-Component Conformally Flat IC (`<problem>`)**:
  `pgen_name = nrpic_cf`, `ncomp = 3`, `comp0_type = puncture` (`comp0_mass` calibrated: `1.0000` for $\chi_0=0$, `0.7518` for $|\chi_0|=0.7$, `0.4535` for $\chi_0=0.9$, `comp0_p{1,2,3}` balancing particle ADM momenta, `comp0_s3 = \chi_0 M_0^2`), `comp1, comp2` stationary `gaussian` wells (`comp_mass = m_{1,2}`, `comp_sigma = sigma_eff`), `lapse = precollapsed`, `puncture_setup = false`.
- **Checkpoints (`<output*>`)**:
  `.hst` (`dt = 0.5`), `.rst` checkpoints (`dt = 100.0`, wall-limit `-t 23:00:00`), 2D slices `alpha_xy`, `alpha_xz`, and `conH_xy` at `dt = 5.0`.

---

## 3. Live Movie & High-Cadence GW Diagnostic Pipeline

Following the pure-CPU movie workflow used for `kerr09_cloud_1m_24h` (`render_kerr09_tde_movie.py`, always with `CUDA_VISIBLE_DEVICES=""`), build `render_zkl_movie.py` producing synchronized multi-panel frames every `dt = 2.5 M`:
1. **Top-Left (Global Outer Orbit $x\text{–}y$ Slice)**: `z4c_alpha` heatmap (`|x|,|y| <= 18 M`) with SMBH apparent horizon (`horizon_summary_0.txt`), binary COM orbital trail from `.traj.bin`, and both gravitating BH particle markers.
2. **Top-Right (Comoving Inner-Binary Frame)**: Recentered zoom (`|\Delta x|,|\Delta y|,|\Delta z| <= 1.5 M`) showing both BH trajectories projected on local inner orbital plane + $\text{x–z}$ side projection tracking ZKL spin-inclination nutation and pericenter bursts.
3. **Bottom-Left (Secular Dynamics vs 1PN)**: Full-NR Fermi-inverted $e_{\rm in}(t)$ and $I(t)$ overlaid against the 1PN+1.5PN secular scout baseline (`pn_zkl_scout.py`).
4. **Bottom-Right (High-Cadence $r\Psi_4$ Waveform, `dt = 0.1 M`)**: Mode $(2,2)$ real/amplitude strain/Weyl scalar zoomed across recent pericenter passages alongside Constraint $\|\mathcal{H}\|_2(t)$ and $M_{\rm AH}(t)$ diagnostics.

Outputs: Incremental `frame_NNNNN.png`, animated `*.webp` and `*.gif` (and `.mp4` if `ffmpeg` available).

---

## 4. Phased Full-NR Production Schedule (`gb204`, Slurm Job `1964821`)

All production ZKL runs listed below use **full 3+1 Numerical Relativity** exclusively on `gb204` (`NVIDIA B200`, Slurm job `1964821`):
1. **Phase 0 & Zero-Drag `amr_dyn` Calibration (COMPLETED)**:
   - Static calibration (`VAL_P0_GR_low_a082`, `SPIN_p07` `comp0_mass = 0.7518`) verified `M_AH` accuracy (`|dM/M| < 1e-4`), horizon cell coverage (`>= 32`), and Fermi-harmonic IC (`|P_ADM| < 1e-9`).
   - Gauge/stride ablation (`G1..G5`), isolated close-encounter tracking (`AMR_close`, `L5->L8->L6` down to `d = 0.0555 M`), and compact full-3+1 benchmark (`P0_compact_s1`, `amr_dyn`, `matter_stride = 1`, `nfilter = 6`, `damp_kappa1 = 0.50`, `shift_eta = 0.07`, `159.2 M/hr`, `|d ln L_z / dt| = 3.887e-5 M^-1`) resolved the `t = 200–300 M` artificial drag and pericenter resolution issues.
2. **Phase 1A (Flagship Long Merger Run — ACTIVE on `gb204`)**:
   - **`GR_low_a082_amr`** (`amr_dyn`, `L5->L8`, `tlim = 3000.0 M`, `rst_dt = 100.0 M`, `waveform_dt = 0.1 M`) running all the way through ZKL eccentricity growth toward particle merger (`t_merge ~ 2200 M` in 1PN+2.5PN scout) to verify merger waveforms and late-time AMR scaling before queueing the remaining suite.
3. **Phase 1B (Remaining Core Physics Matrix — 6 Full-NR Runs on `amr_dyn`)**:
   - `FID_I82_chi0`, `I20_subcrit`, `GR_high_a055`, `I86_high`, `SPIN_p07`, `SPIN_m07`.
4. **Phase 2 (Extended Spin & Octupole Completion — 4 Full-NR Runs on `amr_dyn`)**:
   - `I60_mild`, `GR_mid_a062`, `SPIN_p09`, `OCT_q3_I80`.
5. **Phase 3 (Paper Completion)**: Populate `[PENDING FULL-NR RUNS]` placeholders in `zkl_emri_nr/paper/main.tex` with full-NR ZKL orbital cycles, $r\Psi_4$ waveform modulation analysis at `0.1 M` cadence, constraint convergence figures, and finalize PRL submission.
