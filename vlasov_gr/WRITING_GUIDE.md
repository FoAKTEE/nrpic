# Writing guide: Hybrid symplectic-cubature and moving-finite-volume solver for general-relativistic kinetic matter

The per-paper layer of the paper-writing principles (Sec. 0). Sits one level above `paper/` (7.1).

## Journal and tone (2.8)

- Target journal: *Physical Review D* (`revtex4-2`, `aps,prd,twocolumn`).
- Venue role: methods paper in `aps,prd`; the formulation and algorithm live in the main text, scenario parameters live in the Appendix table, and detailed error, convergence, and timing ledgers live in the Supplemental Material.
- Tone: letter-like concision in American English, physical subjects and active verbs, zero hype, zero contrastive negations, zero trailing participial tails.

## Readers (1.2)

| Community | Minimum background the paper supplies |
|---|---|
| Numerical relativists (fluid or spacetime) | Lagrangian moving-finite-volume basis discretization of phase space, Maxwell-J{\"u}ttner relaxation, and deterministic cubature packets |
| Plasma particle-in-cell practitioners | 3+1 ADM split ($\alpha$, $\beta^i$, $\gamma_{ij}$), canonical $(x^i, u_i)$ Darboux phase space, Z4c evolution, and moving-puncture gauge |
| Astroparticle and collisional-kinetic readers | why collisionless Liouville transport admits exact symplectic packets while arbitrary mean free path needs a finite-volume Riemann solver and asymptotic-preserving HLLC blend |

## Outline (2.1)

| Level | Axis it splits along | Headings |
|---|---|---|
| Section | Steps of the argument | Introduction; Relativistic kinetic system in 3+1 form; Hybrid phase-space algorithm; Kinetic-to-hydrodynamic transition in flat spacetime; Tidal shearing around a spinning black hole; Self-gravitating dust collapse and throughput scaling; Conclusions |
| Subsection of Method | Regimes and kernels | Canonical basis discretization and moving finite volumes; Collisionless symplectic cubature packets; Collisional relaxation and asymptotic-preserving Riemann blend; Mesh coupling and GPU kernel structure |
| Subsection of Results | Physical scenario | Special-relativistic convergence and advection; Collisional-to-collisionless shock transition; Warm sheared cloud on a Kerr background; Full-GR Oppenheimer-Snyder collapse; Strong throughput scaling |

Special cases entered as limits (2.2): non-relativistic Newtonian transport enters as the low-velocity weak-field limit; cold dust collapse enters as the zero-dispersion limit of warm phase-space packets; the fluid limit enters as the zero-mean-free-path asymptote of the Maxwell-J{\"u}ttner relaxation and HLLC Riemann flux blend.

## Allowed numbers (4.1)

- Exact analytic factors and powers: $1/2$, $1/3$, $\sqrt{3}$, $8\pi$, $4\pi$, $\sqrt{\gamma}$, adiabatic index bounds $4/3$ and $5/3$, fifth-order degree-$5$ cubature precision.
- Structural integers: $6$ phase-space coordinates, $10$ covariant moments per velocity basis, $3$ spatial dimensions, $8$, $14$, and $27$ cubature nodes per packet expansion, $2$-stage second-order Runge-Kutta splitting, $4$-point cubic Hermite stencil.
- Labels of cases: Kerr spin $a = 0.9 M$, Oppenheimer-Snyder initial areal radius $R_0 = 5 M$, collisionality parameter $\sigma / \mu_p$, and figure curve labels ($\sigma / \mu_p \in \{0, 2, 15, 10^4\}$ and reference packet counts $10^4$, $10^5$).
- Speedup ratios between solver configurations and strong-scaling slopes may appear; wall times of individual runs, hardware model names, tolerances, and raw decimal error tables live only in the Supplemental Material.

## Expert dictionary (Sec. 6)

| Use | Instead of | Field |
|---|---|---|
| black hole | hole | any |
| numerical methods | pipeline, solver infrastructure | any |
| numerical-relativity particle-in-cell (NRPIC) method | NRPIC code, PIC reproduction | kinetic GR |
| moving-finite-volume (MFM) basis solver | meshless SPH kinetic code | computational astrophysics |
| symplectic cubature packet (SCP) | deterministic PIC blob, macro-dot | kinetic theory |
| asymptotic-preserving (AP) kinetic-fluid blend | shock fix, fluid patch | kinetic theory |
| Einstein-Vlasov system | Vlasov-Einstein system | kinetic GR |
| normal observer | Eulerian grid observer | 3+1 relativity |
| apparent horizon | coordinate horizon | numerical relativity |
| lapse excision | particle deletion, culling | numerical relativity |
| sampling noise | shot noise, Monte Carlo jitter | particle-in-cell |
| mean free path | collision length | kinetic theory |

## Project names (7.7)

Internal development names, cluster names, and code identifiers that never appear in the manuscript (including comments and scripts):

- `B200`
- `gb204`
- `login05`
- `Slurm`
- `srun`
- `nsys`
- `cuobjdump`
- `nrpic_vlasov`
- `vlasov_mfm`
- `vlasov_hybrid`
- `vlasov_scp`
- `GRLBV001`
- `athinput`
- `run_hybrid_benchmark`
- `plot_stage`
- `run_stage`
- `s1d_`
- `s2_grlbv`
- `s3_grlbv`
- `s3_nrpic`
- `nrpic_cf`
- `nrpic_geodesic`
- `Opt MFM`
- `Tier-1`
- `Step B`
- `Part A`
- `Part B`
- `NVTX`
- `cudaEventSynchronize`
- `ConstantMemory`

## Figures (Sec. 9)

| Figure | What the reader should see | Defining parameters |
|---|---|---|
| `fig_sr_regimes` | Second-order MFM convergence in 1D and smooth shock transition across four decades of collisionality to the Taub relativistic fluid limit | $\sigma / \mu_p \in \{0, 2, 15, 10^4\}$ |
| `fig_kerr_pareto_arc` | Hybrid cubature packets populate the dominant cost-accuracy corner and match a hundred-thousand-particle Monte Carlo reference with lower azimuthal roughness | Kerr $a = 0.9 M$, $t = 30 M$ |
| `fig_os_and_scaling` | Cold cubature-packet collapse matches Z4c metric, horizon mass, and constraint evolution while eliminating neighbor-search quadratic growth at large element counts | $R_0 = 5 M$, $a = 0.9 M$ |
