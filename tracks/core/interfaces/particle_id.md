# Interface: particle initial data (proposal for `coord/INTERFACES/particle_id.md`)

Status: PROPOSAL (core, 2026-11-15), written from the code at commit b7b431d:
`athenak/src/particles/nrpic_io.cpp` (particle files), `athenak/src/pgen/nrpic/*.cpp`
(problem generators), `problems/ic/make_ic.py`, `python/nrpic/*.py`, `cosmo/ic/*.py`,
`docs/FORMATS.md`. Tests: `docs/TESTLOG.md` (DT), `cosmo/TESTLOG.md` (CT), test D1 of
this package. Units G = c = 1 everywhere.

## 1. Division of responsibility

A run starts from (a) a slice (gamma_ij, K_ij, alpha, beta^i) set by a problem
generator, and (b) a particle file. The code does not solve the constraints: whoever
writes the data guarantees them for the matter it ships (as `coord/INTERFACES/
spherical_id_format2.md` states for the new table format). The code deposits the
particles at start-up (`NrpicStartup`, `nrpic_io.cpp` lines 1231-1271) and records the
constraint residuals of the deposited sources from the first record on, which is the
check every generator should pass.

## 2. Particle file (`*.nrp`) [VERIFIED by test D1]

Little-endian (native order of the machine; `docs/FORMATS.md`):

| bytes | content |
|---|---|
| 8 | ASCII `NRPIC001` |
| 8 | int64 N |
| 56 N | N records of 7 float64: `x y z u_x u_y u_z m` |
| 4 N | int32 species |

Read only for a new run (`<particles> particle_file`, `NrpicLoadParticleFile`, lines
989-1026); tags are the positions in the file; the MeshBlock is found at start-up.
Alternative for a few particles: `nparticles` and `pN_x1 .. pN_u3, pN_m` in the input
(lines 1034-1057; species 0, m defaults to 0, i.e. a null particle).
`x` are the coordinates of the run; `u_i` the covariant spatial four-velocity per unit
rest mass in the same coordinates (for matter at rest with respect to the normal
observers, `u_i = 0`); `m` the rest mass (`m = 0` null particle, `m = -t_e` light ray,
see `pusher.md`). Writers: `python/nrpic/io.py`, `cosmo/ic/nrp_io.py`.

## 3. Problem generators

### 3.1 `nrpic_cf`: conformally flat, time-symmetric data (`pgen/nrpic/nrpic_cf.cpp`)

`gamma_ij = psi^4 delta_ij`, `K_ij = 0`, `beta^i = 0`, `psi = 1 + sum_c u_c(x - x_c)`,
each `u_c` a solution of `lap u_c = -2 pi rho~_c` (flat Laplacian). The sum solves the
Hamiltonian constraint `lap psi = -2 pi psi^5 E` for `E = psi^-5 sum_c rho~_c`. Set on
all cells including ghost cells, then converted to Z4c variables.

| `<problem>` option | Default | Meaning |
|---|---|---|
| `ncomp` | required, 1 to 8 | number of components |
| `compN_type` | required | `table`, `puncture`, `gaussian`, `spheroid` |
| `compN_x1, _x2, _x3` | 0 | centre |
| `compN_file` | (table) | radial table, format 1 below |
| `compN_mass` | (puncture, gaussian, spheroid) | puncture: bare mass m, `u = m/(2r)`; gaussian: conformal mass m, `u = (m/2) erf(r/(sqrt 2 sigma))/r`; spheroid: ADM mass M, `u = -Phi_N` of a homogeneous prolate spheroid of Newtonian mass M/2 |
| `compN_sigma` | (gaussian) | width |
| `compN_a, compN_b` | (spheroid) | equatorial and polar semi-axes, `0 < a < b`, polar axis z |
| `lapse` | `one` | `one`; `table` (column 3 of component `lapse_comp`, Schwarzschild isotropic lapse outside); `isotropic` `(2 - psi)/psi`; `precollapsed` `psi^-2` |
| `lapse_comp` | 0 | component whose table gives the lapse |

Radial table, format 1 (`docs/FORMATS.md`): text, `#` comments, rows `r u alpha` on a
uniform grid starting at r = 0, at least 8 rows; four-point Lagrange interpolation
inside; `u = u_N r_N / r` outside (mass `M = 2 r_N u_N`).
Format 2 (`r u KL KT alpha betar`, extrinsic curvature and shift) is specified in
`coord/INTERFACES/spherical_id_format2.md` (PROVISIONAL) and is implemented on branch
`core/id-extrinsic`, not in this source.

Tests by component: `table` with `lapse = one` DT "Dust collapse, R_0 = 5 M, 9328
lattice particles"; `table` with `lapse = table` DT "Stable cluster y_c = 0.819, 10^4
stratified particles", DT "Consistent initial data for perturbed clusters";
`puncture` with `lapse = precollapsed` DT "Test particles around an evolved puncture",
"Horizon mass of a vacuum puncture: calibration", "Test particles around a head-on
collision of two black holes"; `spheroid` DT "Prolate collapse, complete to 45 M";
`gaussian` with `table` and `lapse = isotropic` DT "Cluster with two overdensities ..."
entries (`problems/jeans/jeans.athinput` lines 205-216).

What the generator guarantees: the Hamiltonian constraint in the continuum for the
conformal sources it is given. What it does not check: that the particles carry those
sources. The particle generator must place equal-mass particles with coordinate density
of `m W` equal to `rho~ psi` (since the deposit divides by `psi^6`), and must make the
momentum density vanish (particles at rest, or isotropic momenta whose mean is removed);
otherwise the momentum constraint of `K_ij = 0` is violated.

### 3.2 `nrpic_cosmo`: periodic cosmological data (`pgen/nrpic/nrpic_cosmo.cpp`)

`gamma_ij = psi^4 delta_ij`, `K_ij = psi^-2 Ahat_ij + (1/3) psi^4 delta_ij K`,
`beta^i = 0`, lapse given.

| `<problem>` option | Default | Meaning |
|---|---|---|
| `id` | `flrw` | `flrw`: psi = 1, Ahat = 0, K = -3 `hubble`, alpha = 1; `file`: fields from `id_file` |
| `hubble` | 1.0 | initial Hubble rate of `flrw` |
| `id_file` | (file) | `NRCOSMO1`, 3 int64 (n1 n2 n3) equal to the root mesh, then 9 float64 arrays of n3 n2 n1 values, first index fastest: psi, K, alpha, Ahat_xx, Ahat_xy, Ahat_xz, Ahat_yy, Ahat_yz, Ahat_zz at the root cell centres; refined blocks get periodic cubic Lagrange interpolation |
| `noise_amp`, `noise_atilde`, `noise_theta`, `noise_gamma`, `noise_seed` | 0, `noise_amp`, `noise_amp`, `noise_amp`, 1 | white noise on the evolved fields (robustness test of arXiv:1904.07841): a counter-based generator (splitmix64 of the global cell index, the field component and the seed), the same in a ghost cell and in its periodic image, so the noise does not depend on the MeshBlock layout |

Tests: `id = flrw` CT "C0, first test: homogeneous dust universe" and test D1 of this
package; `id = file` CT "C1: constraint-solved initial data ..."; interpolation onto
refined blocks CT "E1, third step: static refinement around the overdensity" (initial
relative Hamiltonian constraint 4e-5 on refined blocks against 2e-11 on the uniform
mesh); noise CT "C5, tests A0 and A of paper 2" and its follow-up.

What the file generator guarantees (`cosmo/ic/cosmo_id.py`, lines 1-20 and 219-243): the
Hamiltonian and momentum constraints on the torus, solved spectrally with the particles
held fixed and with E and S_i formed exactly as the code forms them (same cloud shape,
`deposit_comp_c`, filter passes, division by `psi^6`). The mean of the momentum source
must vanish on a torus; the solver removes it and reports it (`rmean`). The box length of
the run must equal the generator's to all digits (CT "C5, test C: the
Hamiltonian-constraint level was a rounded box size": a six-digit box gave a uniform
density error of 3.8e-7 that grew like spatial curvature).

### 3.3 `nrpic_geodesic`: test particles in Kerr (`pgen/nrpic/nrpic_geodesic.cpp`)

No `<z4c>`; with an `<adm>` block and `metric = mesh` the mesh holds Cartesian
Kerr-Schild data from `bh_mass`, `bh_spin`, reset also on restart. The particles are test
particles. Tests: DT "Pusher kernels" (analytic and lattice metrics), "Mesh path (CPU)"
(mesh metric), "Test-particle clusters in Schwarzschild and Kerr".

## 4. Particle generators and what each guarantees

| Generator | Data | Guarantee | Test |
|---|---|---|---|
| `make_ic.py os --sampler lattice` | dust ball at rest (paper L888-917) | `m_p = rho_0 psi^6 h^3` (the published rule) on lattice sites inside the surface; at 10^4 particles the total is 1.2 % above the continuum rest mass; `--lattice-surface-correction` rescales the outer layer to the continuum total | DT "Dust collapse: the published lattice rule at 10^4 particles carries 1.2 percent too much mass" |
| `make_ic.py os --sampler mc` | dust ball, Monte Carlo | acceptance `psi^6/psi^6(0)`, equal masses | DT "Monte Carlo dust ball ..." entries |
| `make_ic.py st` | monoenergetic cluster, stratified or Monte Carlo sampler | equilibrium table (format 1) and particles; mass-weighted mean of `u_i` removed unless `--keep-net-momentum` | DT "Stable cluster: block size, perturbation, net momentum" |
| `make_ic.py st --dpert/--vpert` | perturbed cluster | by default the table solves the Hamiltonian constraint for the perturbed particles (`PerturbedST`, residual 1e-9); the velocity kick with `K_ij = 0` violates the momentum constraint at first order in the kick (not addressed) | DT "Consistent initial data for perturbed clusters (10:35)" |
| `make_ic.py prolate` | cold spheroid (Yoo et al. 1611.07906; paper L961-967) | spheroid component of `nrpic_cf`; reflection and half-turn symmetric sample unless `--no-symmetrize` | DT "Prolate collapse, complete to 45 M" |
| `make_ic.py jeans` | cluster with two Gaussian clumps (`python/nrpic/clumps.py`) | Hamiltonian constraint by superposition of conformal sources; the clumps' bulk momentum with `K_ij = 0` violates the momentum constraint at first order (`paper/sections/method.tex` line 217) | DT "Two overdensities ..." entries |
| `cosmo/ic/make_lattice.py` | homogeneous lattice, optional noise, light rays | exactly uniform deposit without noise (lattice centred in the cells) | CT "C0, first test"; test D1 |
| `cosmo/ic/make_east.py` | single-wavelength data of 1908.05683 | constraints solved by `cosmo_id.py`; code's own norms at t = 0: 6e-10 (Hamiltonian), 8e-10 (momentum) | CT "C1: constraint-solved initial data ..." |
| `cosmo/ic/make_daverio_c.py` | Gaussian random field of 1904.07841 | as above | CT "C5, test C ..." entries |
| `cosmo/ic/gramses_ic.py` | initial conditions of 2001.07968 | see the entry | CT "C6: initial conditions of paper 3 (GRAMSES), outcome" |

## 5. Proposed interface rules (JUDGEMENT)

1. Every generator writes, next to the particle file, a JSON with the continuum masses
   (ADM, rest), the table or field files, and the `<problem>` block it expects
   (`make_ic.py` does this already), and an offline check of the constraint residuals
   against resolution.
2. Data with net motion (kicks, moving clumps, expanding balls) must carry `K_ij` that
   solves the momentum constraint; format 2 is the first such route for spherical data,
   `coord/notes/design_wave2_initial_data.md` the plan beyond spherical symmetry.
3. The particle file format `NRPIC001` is frozen for core-v0.1; added per-particle data
   go into a new magic (`NRPIC002`) read alongside the old one.
