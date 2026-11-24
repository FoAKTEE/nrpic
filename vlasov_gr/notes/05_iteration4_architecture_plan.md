# Post-Wave-4B/4C Architecture & Iteration 4 Algorithmic Plan

Derived from the byte-level systems, GPU VRAM, MPI communication, and `Z4c` $\leftrightarrow$ particle splitting audit ([architectural report](/home/schmidt/ssci-haiyangw/.gemini/antigravity/brain/9060ae61-bae4-45d3-8b02-aabc18013946/backreaction_gpu_architecture_report.md)). **Execution order:** complete Wave 4B (`M5a–M5c`, Milestone #5) $\to$ Iteration 3 GPU/OMP verification (Milestone #6) $\to$ Wave 4C (`M6` Jeans binary BH merger, Milestone #7) cleanly first, then execute Iteration 4a–4d below after planning-mode sign-off.

---

## 1. Current Bottleneck Diagnosis

1. **Spatial Metric Interpolation Floor (`M2`, `M4`):**
   - `PushGL4` and 3-level quadratic Lagrange time interpolation reach $5.8 \times 10^{-16}$ (M4 analytic) and $1.01 \times 10^{-13}$ (M1 CKS), yet 6-level SMR mesh runs hit a shared floor $|\Delta E/E_0| \approx 1.1 \times 10^{-7}$ because 4-point $C^1$ cubic-Hermite spatial metric interpolation is $\mathcal{O}(\Delta x^3)$ on metric gradients.
2. **Backreaction Time Splitting Limit (`Z4c` $\leftrightarrow$ `Tmunu`):**
   - With `source_density = false` (default), `Tmunu(t^n)` stays frozen across all RK3/RK4 stages of `Z4c::CalcRHS` ($\mathcal{O}(\Delta t)$ Lie–Trotter cap).
   - Enabling `source_density + source_extrap` holds one un-limited midpoint extrapolation (`u_tmunu_step`) across all stages, costing $+20$ full-block Reals/cell and risking $E < 0$ overshoot behind sharp dust/excision fronts.
   - `Z4c::CalcRHS` reads `tmunu` strictly pointwise at interior `(k,j,i)` indices (never spatially differentiated).
3. **VRAM Footprint Before Slimming (`16^3` interior, `ng=4`, $N_{\rm tot}=24^3=13{,}824$):**
   - `Z4c + ADM + Tmunu` core uses `109.11` Reals/cell (`48.26 GB` at 4,000 blocks).
   - Stacking baseline NRPIC + `met_prev` + `bspline` pre-sharpening (`met0s/1s/prevs/work`, `40` Reals) + full-3D `flx_tm` (`31.25` Reals) + `u_tmunu_step`/`tm_prev` (`20` Reals) reaches **`136.21` Reals/cell (`60.26 GB` @ 4k blocks)**, blowing 80 GB GPUs. Actual particles occupy only `80 B/particle` (`8 MB` @ $10^5$).
4. **CPU–GPU Sync & Multi-GPU Stalls (`nrpic_mpi.cpp`, `nrpic.cpp`):**
   - Per-step D2H/H2D staging + CPU `std::sort(tags)` + blocking `MPI_Alltoall`, 8–12 hidden `parallel_reduce` stream syncs, and 5–15 synchronous `pbval_tm` exchanges limit multi-GPU strong scaling.

---

## 2. Sequenced Iteration 4 Action Plan

### Iteration 4a — Memory Slimming (`-76.4` Reals/cell, fitting `< 23 GB` @ 4k blocks)
- Replace 3D `flx_tm.{x1f,x2f,x3f}` (`31.25` Reals/cell) in `NrpicFilterPassMetricConservative` with **register-local interior fluxes + 6-block-boundary face reflux buffers** (`~1.11` Reals/cell-eq, **$28\times$ reduction**).
- Move `tm_prev` / `e_prev` off `ng=4` ghost padding to interior-only `(16^3)` storage and compute `T^{(s)}` in registers inside `Z4c::CalcRHS`, deleting `u_tmunu_step` (`-14.1` Reals/cell).

### Iteration 4b — On-the-Fly Zero-VRAM $C^4$ Quintic B-Spline Mesh Metric (`interp = quintic`)
- Do **not** pre-sharpen or allocate `met0s/met1s/met_prevs/met_work` (`-40.0` Reals/cell saved).
- Evaluate 6-node separable quintic B-spline reconstruction ($\mathcal{O}(\Delta x^6)$ field, $\mathcal{O}(\Delta x^5)$ derivative, $C^4$-smooth) directly on the fly in registers/shared memory from raw `met0/1/prev` (`ng >= 4`).
- Prove broken Hermite floor on `M1` Lattice and `M2`/`M4` 6-level SMR Kerr clusters ($1.1\times 10^{-7} \to 10^{-11}\text{--}10^{-13}$).

### Iteration 4c — Positivity-Preserving High-Order Backreaction (`Scheme A` & `Scheme B+`)
- **Scheme A (fast default, $+0$ extra particle work, $\mathcal{O}(\Delta t^2\text{--}\Delta t^3)$):** Inside `Z4c::CalcRHS`, evaluate stage-accurate metric-rescaled slope-limited extrapolation from interior densitized histories $\tilde{T}^n, \tilde{T}^{n-1}$ at exact stage fraction $c_s$ (`Driver::c_stage`), with local limiting where $\tilde{E}^{(s)} < 0$ or sharp fronts occur.
- **Scheme B+ (strong-collapse/merger reference, $\mathcal{O}(\Delta t^2)$ zero-overshoot):** Predictor half-step particle advance $t^n \to t^{n+1/2}$ + deposit $\tilde{T}^{n+1/2}$, strictly convex interpolation over $[t^n, t^{n+1/2}]$ during Z4c stages, and second half-step advance $t^{n+1/2} \to t^{n+1}$.
- Prove genuine temporal convergence order of coupled collapse/OS backreaction vs Lie–Trotter.

### Iteration 4d — GPU Stream Overlap & Multi-GPU Communication Hiding
- Overlap `Z4c::ADMConstraints_/CalcWeylScalar/FastFlow` (`stream_z4c`) with `NrpicVlasovSyncMetric + PushGL4` (`stream_part`).
- Split Interior (95–99%) vs. Boundary/Migrating (1–5%) particles to overlap GPU-aware `MPI_Ineighbor_alltoallv` on `stream_comm` with interior `CloudDeposit`/`Cell-BGK` on `stream_part`; defer tag-sorting to I/O dumps.
- Use `ng=4` ghost depth for widened-halo communication-avoiding filtering (`4–5x` fewer `pbval_tm` exchanges), fuse scalar diagnostics into 1–2 async `StepStats` reductions, and add periodic `PGID` bucket sorting + warp-aggregated deposit atomics.
