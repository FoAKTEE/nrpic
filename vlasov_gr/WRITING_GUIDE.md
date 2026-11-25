# Writing guide: PRX methodology paper on general-relativistic kinetic theory

The per-paper layer of the paper-writing principles. This file and `NOTATION.md` sit one level above the manuscript directory `paper/`. Where this guide is more specific than the general principles, it governs this paper.

## Journal and tone

- Target journal: Physical Review X (REVTeX 4.2, `aps,prx,twocolumn,10pt`).
- Role of the paper: A comprehensive, self-contained methodology and validation paper written for numerical relativists, plasma and kinetic theorists, and computational astrophysicists. Every algorithmic stage carries its discrete equations, analytical conservation or regularity proofs, and domain of validity inside the main text (`system.tex` and `method.tex`).
- Where raw numbers go: Scenario parameters, numerical discretization ledgers, and quantitative comparison metrics (runtimes, memory footprints, exact error exponents, horizon masses and spins) live cleanly in tables in the Appendices and the Supplemental Material. Main-text prose highlights physical mechanisms, scaling behavior, order-of-magnitude gains, and qualitative milestones without dense strings of inline decimals or percentages.
- Tone: Authoritative, lucid Physical Review prose in American English. Zero hype, zero promotional adjectives, zero contrastive negation tics.

## Readers across PRX communities

| Community | Minimum context the paper supplies |
|---|---|
| Numerical relativists | why collisionless and collisional kinetic closures supplement fluid GRMHD; how particle clouds, B-spline weights, QMC initialization, and Cell-BGK operate on Z4c adaptive meshes |
| Plasma and kinetic-theory practitioners | how 3+1 ADM foliations, Z4c constraint damping, moving-puncture gauges, Darboux canonical momenta, and harmonic metric-weighted refluxing generalize flat-space PIC |
| Relativistic astrophysicists | how fourth-order symplectic integration, $C^2$ quintic metric reconstruction, and causality-limited stage coupling enable accurate strong-field photon/particle dynamics and black hole back-reaction |

## Outline

| Level | Axis | Sections / Subsections |
|---|---|---|
| Main sections | Argument structure | Introduction; General-relativistic kinetic system in 3+1 form; High-order symplectic, metric-conservative, and collisional algorithm; Special-relativistic convergence and optical-depth transition; Strong-field Kerr orbits, photon spheres, and static-mesh clusters; Dynamical three-plus-one collapse, massive-particle back-reaction, and end-to-end validation; Conclusions |
| Method subsections | Cycle stage & closure | Symplectic geodesic pushers and metric time interpolation; Zero-overhead $C^2$ quintic Hermite spatial metric reconstruction; Conservative adaptive-mesh stress-energy deposition; Self-adjoint metric-weighted flux-conservative filtering; Causal stage-accurate spacetime coupling and multi-rate subcycling; Deterministic phase-space sampling and collisional closures; Initial-data constraint solvers, adaptive mesh refinement, and horizon diagnostics |

## Allowed main-text numbers

- Exact analytical constants and exponents: $8\pi$, $4\pi$, $1/2$, $1/3$, $1/4$, $1/12$, $1/6$, $\sqrt{3}/6$, $\psi^4$, $\psi^6$, $\chi^{-7/4}$, $\Nppc^{-1/2}$, four-tuple and $14$-point rules, fourth-order accuracy, $C^2$ regularity, two-stage Gauss--Legendre, three-stage SSP-RK3.
- Defining physical labels and canonical testbed parameters: mass-shell parameter $\varepsilon \in \{0, 1\}$, black hole spins $a = 0.9\,M$, $0.95\,M$, and $0.999\,M$, eccentricities $e = 0.99$ and $0.999$, prograde light-ring radius $r_{\rm ph}^+$, photon-shell radius $r_{\rm sph} = 2.2\,M$, dust radius $R_0 = 5\,M$, spheroid eccentricity $e = 0.9$, equilibrium sequence labels $y_c \in \{0.900, 0.819, 0.756, 0.605, 0.500, 0.283\}$, back-reaction mass ratios $q \in \{0, 0.02, 0.05, 0.10\}$, particle budgets $N \sim 10^4\text{--}10^5$, and collisional couplings $\sigma/\mu_p \in \{0, 2, 15, 10^4\}$.
- Detailed convergence tables, exact digit counts, hardware-timed runtimes, and memory savings reside in Appendix B tables (`appendix_parameters.tex`) and `supplement.tex`.

## Expert dictionary

| Use | Instead of |
|---|---|
| black hole | hole (bare) |
| macroparticle; phase-space packet | superparticle; marker (unclear); particle-in-cell test weight |
| graphics accelerator | B200; A100; H100; GPU model name |
| device memory | VRAM |
| baseline second-order NRPIC method | NRPIC Original; baseline code |
| high-order metric-conservative solver | Our Best; Iter 3; Iter 4; Iter 5; Iteration 3/4/5 |
| SSP-RK3; three-stage strong-stability-preserving Runge--Kutta | `\texttt{rk3}` |
| multi-rate stride $s_{\rm m}$ | `\texttt{matter\_stride}` |
| eighth-order Dormand--Prince reference | `\texttt{DOP853}` (prose) |
| four-stage fourth-order Runge--Kutta | `\texttt{rk4}` |
| causal stage-accurate source extrapolation | `\texttt{Scheme A}` without mathematical definition; raw parameter names |
| apparent horizon | horizon alone (when the finder surface is meant) |
| moving-puncture gauge | puncture gauge without first naming $1+\log$ slicing and Gamma-driver shift |
| monoenergetic cluster | ST model |
| binary black hole formation in a relativistic cluster | Jeans run |

## Forbidden project names

- Iter 3
- Iter 4
- Iter 5
- Iteration 3
- Iteration 4
- Iteration 5
- B200
- A100
- H100
- VRAM
- build_gpu
- nrpic_cf
- nrpic_geodesic
- nrpic_grlbv
- kernel_test
- gb204
- login05
- DOP853
- matter_stride
- filter_mcons
