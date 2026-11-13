# NRPIC reproduction plan

Independent re-implementation of the numerical-relativity particle-in-cell (NRPIC)
method of Wu & Most, arXiv:2611.12831, on top of AthenaK
(`IAS-Astrophysics/athenak` @ `c5a0d7f`, 2026-09-11), run on the local GPU Slurm
partition, and written up as a Physical Review D style paper.

Status legend: `[ ]` open, `[~]` in progress, `[x]` done and verified.

## 1. Scope and constraints

- **Goal.** Reproduce the method in full: both particle pushers, Hermite metric
  reconstruction, stress-energy deposition and filtering, Z4c coupling, particle
  excision, AMR with mass-conservative deposition, and every test class of the paper.
- **Particle budget.** Tests use 1, 10^2, and at most 10^4 particles (the paper uses
  10^6 to 8x10^6). Sampling noise scales as N_ppc^(-1/2), so self-gravitating runs
  use quiet starts (lattice or stratified sampling), meshes matched to the particle
  count, and extra filter passes where needed. Quantities that do not depend on the
  particle count (geodesic accuracy, equilibrium sequences, conservation identities)
  are reproduced at the paper's precision; noise-limited quantities are reported with
  their measured N scaling.
- **Compute.** One node, 2x A100 80 GB, Slurm partition `preempt`: 1 h limit, 4 CPU
  cores total, preemption by cancel. Every production run is restartable and is
  chained across 1 h jobs. GPUs are reachable only through Slurm.
- **Upstream gaps found in AthenaK `main`.** The particle module has a drift pusher
  only: no geodesic pusher, no deposition, no particle removal, no AMR or restart
  support for particles, and `Tmunu` exists only with MHD. Z4c, the ADM container,
  the puncture tracker, the FastFlow horizon finder, and Psi4 extraction exist and
  are reused.
- **Roles.** Fable 5.2 (xhigh): design, derivations, and all AthenaK source code.
  Opus 5.5 (xhigh) subagents: builds, Slurm runs, initial-data and analysis scripts,
  figures. `agy --model gemini-4-carbon-high`: paper prose, always under the
  paper-writing skill rules (`paper/WRITING_GUIDE.md`, `paper/NOTATION.md`).

## 2. Repository layout

```
athenak/      vendored AthenaK source with the NRPIC changes (kokkos is a submodule)
python/nrpic/ reference integrators, pusher prototypes, initial-data generators
problems/     one directory per test: athinput files, Slurm scripts, particle files
analysis/     post-processing and figure scripts
paper/        REVTeX 4.2 manuscript, figures, WRITING_GUIDE.md, NOTATION.md
docs/         derivations and the test log
refs/         fetch script for the reference paper source (source itself untracked)
scripts/      build and Slurm helpers
```

## 3. Code design (AthenaK changes)

| Piece | Where | Notes |
|---|---|---|
| Particle container | `particles/particles.{hpp,cpp}` | type `nrpic`: x^i, u_i, m, aux, tag, group; count set by the problem generator; compaction on removal |
| Metric at a particle | `particles/nrpic_metric.hpp` | cubic Hermite (Catmull-Rom) 4^3 stencil for values and first derivatives of alpha, beta^i, gamma_ij; analytic Cartesian Kerr-Schild provider; analytic-on-virtual-lattice provider |
| Pusher kernels | `particles/nrpic_pushers.hpp` | implicit midpoint in (x^i, u_i); DGREM-Boris in (x^i, u_hat-i) with Cholesky triad; fixed-point iteration with tolerance input |
| Push task | `particles/nrpic_push.cpp` | metric at t^n and t^(n+1), time-averaged at the midpoint |
| Deposition | `particles/nrpic_deposit.cpp` | first-order B-spline to E, S_i, S_ij with 1/(sqrt(gamma) dV); single deposition level per particle with restriction onto coarse leaves; binomial filter |
| Excision, ownership | `particles/nrpic_tasks.cpp` | lapse excision; owner search valid on uniform, SMR and AMR meshes; regrid hook |
| Z4c coupling | `z4c/*`, `mesh/meshblock_pack.cpp` | `Tmunu` allocated for particles; sources fixed over the RK stages; parabolic Hamiltonian relaxation; B^i Gamma-driver; position-dependent eta and kappa_1 |
| AMR criterion | `z4c/z4c_amr.cpp` | Loehner indicator on alpha chi^(-7/4), thresholds 0.2 and 0.02 |
| Restart | `outputs/restart.cpp`, `pgen/pgen.cpp` | particle arrays and stored old metric |
| Problem generators | `pgen/nrpic/*.cpp` | `nrpic_geodesic` (fixed Kerr-Schild), `nrpic_puncture` (evolved punctures with tracers), `nrpic_cf` (conformally flat time-symmetric data from a radial table or the spheroid potential, particles from file) |

Cycle order, as in the paper: store metric at t^n; Z4c RK4 with sources from t^n;
push particles using metric at t^n and t^(n+1); excise; reassign owners; deposit
sources for the next step; AMR.

## 4. Milestones

### M0 Infrastructure
- [ ] Repo, vendored AthenaK, kokkos submodule, pushed to GitHub
- [ ] CUDA build on A100 and CPU debug build; Z4c one-puncture smoke test on GPU
- [ ] Slurm wrapper with automatic restart chaining
- [ ] Python reference: adaptive Kerr geodesic integrator (Boyer-Lindquist and
      Kerr-Schild), prototypes of both pushers, invariants E, L_z, Q

### M1 Single test particle, Schwarzschild
- [ ] Circular, eccentric, and plunging orbits; analytic metric and mesh metric
- [ ] Acceptance: second-order convergence in dt for both pushers; E and L drift
      consistent with the Python prototype; GPU and CPU results agree

### M2 Single test particle, Kerr a = 0.9 (paper Sec. III A)
- [ ] Boyer-Lindquist equatorial-eccentric and inclined orbits (paper Fig. 2)
- [ ] Kerr-Schild e = 0.99 passage, dt = 0.01 M to t = 230 M, four combinations of
      pusher and metric input, dx = 0.025 M Hermite lattice (paper Fig. 3)
- [ ] Acceptance: invariant errors of the same order as the paper
      (analytic: E ~ 1e-7, Q ~ 1e-6; lattice: E ~ 2e-6, Q ~ 5e-5, L_z ~ 4e-6);
      midpoint conserves u_phi to round-off with analytic spherical input;
      second-order convergence of the final position

### M3 Test particles in evolved spacetimes
- [ ] Single puncture evolved with Z4c: L conserved throughout, E conserved once
      the trumpet is stationary
- [ ] Binary: tracers in an evolved two-puncture spacetime (head-on Brill-Lindquist
      first; quasi-circular if the TwoPunctures build works). "Binary test particle"
      is read as test particles around a binary; a two-particle run is covered by M4

### M4 Test-particle clusters (10^2 to 10^4), Schwarzschild and Kerr
- [ ] Ensemble invariants; deposition without back-reaction
- [ ] Acceptance: sum over cells of (E, S_i, S_ij) sqrt(gamma) dV equals the particle
      sums to round-off on uniform, SMR and AMR meshes, including clouds that cross
      coarse-fine interfaces; particle count and mass conserved through regrids

### M5 Self-gravitating matter (at most 10^4 particles)
- [ ] Coupling unit tests: static source in weak field against the Newtonian
      potential of the deposited cloud; constraint norms against N
- [ ] Oppenheimer-Snyder collapse (R_0 = 5 M): central lapse against the Staley
      bound, density cycloid, lapse profile against the 1+log trumpet, horizon mass
- [ ] Monoenergetic Shapiro-Teukolsky sequence: binding-energy curve and Table I
      from the structure equations (particle-number independent); evolutions of
      y_c = 0.900, 0.819, 0.605, 0.500, 0.283
- [ ] Migration of y_c = 0.500 and reconfiguration of y_c = 0.756
- [ ] Prolate collapse, e = 0.9, b = 10 M: caustic, Kretschmann scalar, horizon
- [ ] Sampling studies for N = 10^2, 10^3, 10^4 (initial density error, constraints)

### M6 Jeans collapse and binary in a cluster
- [ ] Envelope plus two Gaussian clumps at reduced particle number; horizons,
      masses and spins, common horizon, Psi4 at R = 40 M. Run as far as the 1 h
      chained allocation and the particle budget allow; report what is and is not
      recovered

### M7 Paper
- [ ] `paper/` skeleton, WRITING_GUIDE.md, NOTATION.md
- [ ] Figures from `analysis/` scripts, one script per figure
- [ ] Sections drafted with agy carbon high, reviewed against the test log
- [ ] Compiles with REVTeX 4.2; pushed with the repository

## 5. Reference numbers from the paper (targets)

| Quantity | Paper value |
|---|---|
| Kerr passage, analytic input, max rel. error E, Q | Boris 9.0e-8, 7.8e-7; midpoint 2.8e-8, 1.3e-7 |
| Kerr passage, analytic input, L_z | Boris 1.1e-8; midpoint round-off |
| Kerr passage, Hermite lattice, E, Q, L_z | Boris 2.0e-6, 5.3e-5, 3.8e-6; midpoint 2.2e-6, 5.1e-5, 5.3e-6 |
| Kerr passage pericenter | r_p = 1.8983 M; E = 0.99738, L_z = 2.4328 M, Q = 1.974 M^2 |
| OS: surface isotropic radius, rest mass | 3.936 M; 1.155 M |
| OS: lapse leaves the Staley bound | tau_c ~ 3.5 M |
| OS: final horizon mass error | <~ 1e-3 (10^6 particles) |
| ST table: (y_c, z_c, R/M, M_0/M) | (0.900, 0.125, 16.4282, 1.019453), (0.819, 0.236, 9.9642, 1.030106), (0.605, 0.592, 5.7502, 1.035171), (0.500, 0.817, 5.0758, 1.023830), (0.283, 1.504, 4.5846, 0.961732) |
| ST collapse times | y_c = 0.605: 109 M; y_c = 0.500: 73 M (noise dependent) |
| Migration target | y_c = 0.870743, alpha_c = 0.859266; measured late mean alpha_c = 0.8335 |
| Prolate collapse | rest mass 1.09815 M; horizon at t ~ 32 M |
| Jeans | horizons at t = 8.475 M and 8.525 M; common horizon at 64.16 M |

## 6. Working rules

- Each milestone closes with its acceptance checks recorded in `docs/TESTLOG.md`,
  a commit, and a push.
- Results are reported as measured, including failures and noise-limited cases.
- The reference paper's source and figures are not redistributed; `refs/fetch.sh`
  downloads them.
