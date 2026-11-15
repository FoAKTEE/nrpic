# Scalar field with stochastic sources in AthenaK: interface

Status: PROPOSAL of core (branch `core/scalar-field`, 2026-11-15) for
`coord/INTERFACES/scalar_field.md`. Clients: Track E (stochastic inflation; requests R1 to
R8 of `tracks/E-stoch-inf/codebase/DESIGN_REVIEW.md` and section 10 of
`tracks/E-stoch-inf/spec/SPEC.md` on `track/E-stoch-inf`), Track B (periodic boxes,
shared diagnostics), any track that needs a scalar matter source. Brief lines 257-266,
445-465, 785-802; decision 0010. Evidence labels as in the brief; every number carries a
run id (`tracks/core/runs/<run_id>/manifest.json`, outputs `scratch/core/<run_id>/`).
Predictions and outcomes, including the failed ones: `tracks/core/JOURNAL-scalar.md`.

## 1. What exists

A minimally coupled real scalar field phi with a potential V(phi), evolved together with
the Z4c spacetime of this repository's AthenaK and sourcing it; a hook for stochastic
sources in a periodic box; initial data for tests; diagnostics in double precision; exact
restart. Off unless the input has a `<scalar_field>` block; runs without that block are
byte-identical to the executable before this work (section 10).

| Where | What |
|---|---|
| `athenak/src/scalar_field/scalar_field.hpp` | class `scalarfield::ScalarField` (pack pointer `pscalar`), options, potential (kernel function) |
| `athenak/src/scalar_field/scalar_field.cpp` | constructor, tasks in the numerical-relativity task list, communication, low-storage update |
| `athenak/src/scalar_field/scalar_field_rhs.cpp` | right-hand side of phi and Pi; E, S_i, S_ij into `Tmunu::tmunu_tot` |
| `athenak/src/scalar_field/scalar_field_noise.cpp` | stochastic sources: modes, amplitudes, lockstep data, synthesis, kicks |
| `athenak/src/scalar_field/scalar_field_io.cpp` | start-up, history, dumps, restart side file |
| `athenak/src/pgen/nrpic/scalar_field_tests.cpp` | `pgen_name = scalar_field`: plane wave on flat space, homogeneous universe, constraint-satisfying plane perturbation |
| `python/nrpic/scalar_field.py` | readers, Friedmann and Klein-Gordon reference, stencil symbols, twin of the stochastic sources (no simulation code) |
| `problems/scalar/*.athinput` | inputs of the tests |
| `tracks/core/analysis/scalar/` | test drivers (`test1_wave.py` to `test4_noise.py`) |

Why a module of its own [JUDGEMENT]: the sources of a field change at every stage of the
integrator, so it belongs in the numerical-relativity task list next to Z4c, like
`dyn_grmhd`, and not behind the step like the particles. Adding phi and Pi to the Z4c
state vector would change `nz4c`, the restart layout and every existing run.

## 2. Conventions and equations

G = c = 1, G_munu = 8 pi T_munu; ds^2 = -alpha^2 dt^2 + gamma_ij (dx^i + beta^i dt)
(dx^j + beta^j dt); n^mu = (1, -beta^i)/alpha; K = -nabla_mu n^mu as in Z4c (K = -3H in an
expanding universe). T_munu = d_mu phi d_nu phi - g_munu [(1/2) g^rs d_r phi d_s phi + V].

    Pi      = n^mu d_mu phi = (d_t phi - beta^i d_i phi)/alpha      (evolved with phi)
    d_t phi = beta^i d_i phi + alpha Pi
    d_t Pi  = beta^i d_i Pi + alpha (D^i D_i phi + K Pi - V') + gamma^ij d_i alpha d_j phi
    E       = Pi^2/2 + (1/2) gamma^ij d_i phi d_j phi + V
    S_i     = -Pi d_i phi
    S_ij    = d_i phi d_j phi + gamma_ij (Pi^2/2 - (1/2) gamma^kl d_k phi d_l phi - V)

Pi is the momentum measured by the normal observers (alpha = 1, beta = 0: Pi = dot phi);
the ADM canonical momentum is sqrt(gamma) Pi. A wave moving towards +x has S_x > 0. With
alpha = 1 and a homogeneous field: ddot phi + 3 H dot phi + V' = 0.

In the code's variables (gamma_ij = psi^4 gt_ij, psi^-4 = chi^(-4/p), p = `chi_psi_power`,
K = Khat + 2 Theta): D^i D_i phi = psi^-4 [gt^ij d_i d_j phi - Gt^k d_k phi + 2 gt^ij
d_i ln psi d_j phi] with d_i ln psi = d_i chi/(p chi) and Gt^k computed from the
conformal metric (not the evolved Gamma). All metric quantities come from the Z4c state
of the same stage (never from `padm`). Derivatives: the centred differences of
`utils/finite_diff.hpp` at the order of `nghost` (2, 4, 6), upwinded advective
derivatives along the shift, Kreiss-Oliger term as for the spacetime variables.

## 3. Input

`<scalar_field>` (all optional except where noted):

| Option | Default | Meaning |
|---|---|---|
| `couple` | true | the sources enter the spacetime solver and the constraints; false: test field on the evolved spacetime |
| `potential` | quadratic | quadratic, quartic, plateau, inflection, table |
| `mass`, `lambda` | 0 | quadratic, quartic: V = mass^2 phi^2/2 + lambda phi^4/4 |
| `v0`, `mu` | 0, 1 | plateau: V = v0 (1 - exp(-phi/mu))^2 |
| `lambda`, `vev` | 0, 1 | inflection: V = lambda vev^4 phi^2 (3 phi^2 + 2 sqrt2 phi vev + 6 vev^2) / (3 (3 phi^2 + 2 vev^2)^2), the form of SPEC section 6 [TO VERIFY by Track E against arXiv:2512.14649, P1:405-409; core has not read the source] |
| `table_file` | | table: text rows "phi V dV/dphi", equally spaced; cubic Hermite between the rows, tangent beyond the ends |
| `v_offset` | 0 | constant added to V (vacuum energy) |
| `diss` | `<z4c> diss` | Kreiss-Oliger coefficient of phi and Pi |
| `hist_dcycle` | 1 | cycles between records of `<basename>.sf.hst` (0: off) |
| `dump_dcycle`, `dump_dt` | 0, -1 | cycles or time between double-precision dumps |
| `noise` and `noise_*` | none | stochastic sources, section 7 |

The seed of the stochastic sources is `<job> rng_seed` (`rng.md`). A parameter that a
command line overrides must be present in the input file (AthenaK rule).

`<problem> pgen_name = scalar_field`, `id =` `wave` (flat spacetime, phi = phi0 + amp
cos(k.(x - x0)), Pi = pi0 + amp omega sin(k.(x - x0)), integers `n1 n2 n3`), `flrw`
(homogeneous: `phi0`, `pi0`, K from the Hamiltonian constraint, alpha = 1), `plane`
(section 8, test 3). Other problem generators may set `pscalar->u0` themselves (all
cells including ghost cells, or the active cells: the driver exchanges ghost cells before
the run starts).

## 4. Place in the code

Tasks (names in `tasklist/numerical_relativity.hpp`, appended after the Z4c tasks):

| Task | Does | Waits for |
|---|---|---|
| `SF_Recv` (start list), `SF_ClearS`, `SF_ClearR` (end list) | boundary communication | |
| `SF_CopyU` | register u1 (and the lockstep data) | |
| `SF_CalcRHS` | stochastic fields of the stage; right-hand side | `SF_CopyU` |
| `SF_SetTmunu` | sources of all matter into `tmunu_tot` | `SF_CopyU`, `MHD_SetTmunu` if present |
| `Z4c_CalcRHS` | (existing) | now also `SF_SetTmunu` |
| `SF_Kick` | stochastic sources of Khat and At_ij into the Z4c right-hand side | `SF_CalcRHS`, `Z4c_CalcRHS` |
| `Z4c_ExplRK` | (existing) | now also `SF_Kick`: the spacetime is not advanced before the field has read it |
| `SF_ExplRK`, `SF_RestU`, `SF_SendU`, `SF_RecvU`, `SF_Prolong`, `SF_BCS` | update, restriction, exchange, prolongation, physical boundaries | `SF_Kick`, `SF_SetTmunu`, then in sequence |
| `ScalarField::Diagnostics` (list `after_timeintegrator`, behind the particle tasks) | history, dumps | |

Lines of shared files touched (against b28ecca), all small hooks:

| File | Lines | What |
|---|---|---|
| `z4c/tmunu.hpp`, `tmunu.cpp` | 61-71, 56-73 | container `tmunu_tot`, `use_total`, `AllocateTotalSources()` |
| `z4c/z4c_calcrhs.cpp` | 165-171 | read `tmunu_tot` when `use_total` |
| `z4c/z4c_adm.cpp` | 23, 271-275 | constraints: assemble and read `tmunu_tot` when `use_total` |
| `z4c/z4c_tasks.cpp` | 51, 55, 59, 65 | optional dependencies `SF_SetTmunu`, `SF_Kick` |
| `tasklist/numerical_relativity.hpp`, `.cpp` | 25, 92-108, 114-115; 17, 46-47, 61-62, 169-171 | task names, `Phys_SF`, queueing |
| `mesh/meshblock_pack.hpp`, `.cpp` | 40, 81; 35, 61, 233-243, 263-269 | pointer, construction before the NR task list, diagnostics task |
| `driver/driver.cpp` | 30, 472-475, 775-787 | start-up, ghost cells at initialisation |
| `outputs/restart.cpp`, `pgen/pgen.cpp`, `pgen.hpp` | 31, 643-646; 31, 640-643, 984-985; 82 | restart side file, problem generator |
| `outputs/outputs.hpp`, `basetype_output.cpp` | 24, 103-105; 29, 714-731 | output variables `sf_phi`, `sf_Pi`, `sf` (appended: indices 154 to 156) |
| `parameter_input.cpp`, `CMakeLists.txt` | 112; 164, 210-213 | block name, sources |

## 5. Sources of several matter modules

`Tmunu` has a third container, `tmunu_tot`. When a scalar field with `couple = true`
exists, `use_total` is set and the spacetime right-hand side and `ADMConstraints` read
`tmunu_tot` only. The scalar field writes it (active cells) before every right-hand side
and before every evaluation of the constraints:

- before a right-hand side: field sources of the stage + the others, where the others
  are `u_tmunu`, or, with `step_density` (particles with `source_density`), the step
  densities times 1/sqrt(gamma) of the stage plus the vacuum energy, i.e. what the solver
  would have formed itself;
- before the constraints: field sources of the state + `u_tmunu` (the particle deposit at
  that time, including Lambda).

`u_tmunu` stays what the other modules wrote, so particles and the field coexist
(request R2; verified with a vacuum energy supplied either way, section 10). Not yet
covered: the constraint statistics of the particle module (`.cstat.hst`) still normalise
with the particle sources alone (use `<basename>.sf.hst`); a run with particles and a
dynamical field together has not been made.

## 6. Boundaries, refinement, time step, output, restart

- Communication through `MeshBoundaryValuesCC` in its Z4c flavour: same restriction,
  prolongation and exchange as the spacetime variables. Periodic boundaries; outflow
  (extrapolation of order `<z4c> extrap_order`) and reflection through the routine of the
  spacetime variables (`Z4cBCs`), which treats phi and Pi as scalars. No Sommerfeld
  condition for the field.
- Uniform and statically refined meshes. Adaptive refinement stops with an error (it
  needs entries in `mesh/mesh_refinement.cpp`). [Refined mesh: smoke run only, section 10.]
- Time step: that of Z4c (Courant factor times the cell size). A mass term needs
  mass x dt well below 1; not enforced.
- Single MPI rank (diagnostics and stochastic sources); the field update itself uses the
  rank-safe boundary machinery.
- Output variables `sf_phi`, `sf_Pi`, `sf` in the standard outputs (single precision in
  `bin`). Double precision: `<basename>.sf.hst` (box means with coordinate-volume
  weights: phi, Pi, K, chi, alpha, rms of phi and Pi about the mean, E of all matter,
  mean |H|, rms H, max |H|, rms and max |M|, rms Theta, mean [H] = |R| + (2/3) K^2 +
  At_ij At^ij + 16 pi E, lockstep background) and `<basename>.sf.NNNNN.dump` (phi, Pi, chi,
  K, alpha, H, M_i, E and the stochastic fields on the active cells; format at the top of
  `scalar_field_io.cpp`; reader `nrpic.scalar_field.read_dump`). These do not depend on
  the particle module (request R6). [M] of arXiv:2512.14649 is not computed.
- Restart: `<restart file>.sf` next to the mesh restart file holds phi, Pi, the dump
  counters and the lockstep data; amplitudes and tables are rebuilt from their keys.
  Verified bit-identical (section 10).

## 7. Stochastic sources

### 7.1 Noise fields

Periodic cubic box with a cubic root mesh, side L, lower corner x0. A noise field is

    xi(x) = sum_{n in H} 2 Re[ c_n exp(i k_n.(x - x0)) ],   k_n = 2 pi n/L,

over the hemisphere H (n_x > 0, or n_x = 0 and n_y > 0, or n_x = n_y = 0 and n_z > 0;
the half space of `codebase/ref/synth.py`) with 0 < |n|^2 <= `noise_nmax2`
(2 n_max < N). Coefficient: c_n = (complex factor of the shell |n|^2) x alpha_n x (real
factor of the field). No zero mode.

Amplitudes (this fixes the entry of stream 3 in `rng.md`, section 6):

    alpha_n = (z1 + i z2)/sqrt 2,  (z1, z2) = rng::Normal2(key, 0),
    key = {seed, Stream(kStreamStochastic, 2^16 + dof), CellEntity(n_x + 2^20, n_y + 2^20, n_z + 2^20), epoch}

`dof` numbers independent sets of amplitudes; sub-streams below 2^16 stay free for
cell-keyed noise. epoch = 0 for frozen amplitudes; for amplitudes that are new in every
step it is the cycle number reached at the end of the step (`ncycle + 1`; 0 is never
used twice). These are the keys of `tracks/E-stoch-inf/noise/ref/philox_ref.py`.

Synthesis: MeshBlock by MeshBlock, three one-dimensional sums (n_z, then n_y, then n_x)
with tables of cos and sin of 2 pi n (g + 1/2)/N_level from the global cell index g with
the phase reduced in integers. Every cell sums the same terms in the same order for any
division of the mesh; a refined MeshBlock evaluates the same function at its own cell
centres. No Fourier library. Cost: section 9.

### 7.2 Model `noise = power` (generic hook, unit test of the generator)

Increment of a step: shell factor amp q^((tilt-3)/2) L^(-3/2) g(dW_q), q = |n|, dW_q the
change over the step of W = (1 + tanh[s ln(k_sigma/k)])/2 (or the step function,
`noise_window = heaviside`), k_sigma/k_f = `noise_ksigma0` exp(`noise_hubble` (t -
`noise_t0`)); g = dW (`noise_scheme = frozen`: the sum over steps is the windowed frozen
field) or sqrt(dW) (`markov`: Gaussian, white in time, variance of the increment
proportional to dW). Sources: `noise_c_phi` xi_0/dt in d_t phi and `noise_c_pi` xi_1/dt
in d_t Pi, held over the stages, so that a step adds c_phi xi_0 and c_pi xi_1 exactly
(xi_1 has its own amplitudes, dof 1, or those of xi_0 with `noise_pi_dof = 0`).

### 7.3 Model `noise = mukhanov_sasaki` (the sources of SPEC 2.1, 2.2, 3)

Frozen alpha_n (dof 0). Per shell a complex mode function R_q(t) with

    d2R/dtau2 + (3 - eps2) H dR/dtau + (k/a)^2 R = 0,       k = 2 pi q/L,
    S_R = R W'' + [2 R' + (3 - eps2) H R] W',               W = (1 + tanh[s ln(sigma a H/k)])/2,
    W'  = (s/2) sech^2(x) H (1 - eps1),   W'' = (s/2) sech^2(x) [H^2 eps1 (eps2 - 1 + eps1) - 2 s tanh(x) H^2 (1 - eps1)^2],

primes = proper time of the background, eps1 = 4 pi Pi_b^2/H^2, eps2 = -dln eps1/dN =
6 + 2 V'(phi_b)/(H Pi_b) - 2 eps1 (Launay's sign). Fields I_R = L^(-3/2) sum 2 Re[S_R
alpha_n e^(ik.x)] and T_ij = the same with the factor qh_i qh_j/qh^2. Kicks:

    d_t Pi    += alpha_b (Pi_b/H) I_R x noise_pi_sign      (sign-safe form, erratum E4)
    d_t Khat  += -alpha_b eps1 I_R
    d_t At_ij +=  alpha_b eps1 (delta_ij I_R/3 - T_ij),    T_zz = I_R - T_xx - T_yy

and nothing else (chi, gt_ij, Gt^i, Theta, phi, gauge). qh is the wave number of the
centred first difference of the root mesh (`noise_projector = stencil`, request R3) or n
itself (`continuum`). Background: `noise_level = 0` the Friedmann equations for (phi_b,
Pi_b, ln a) integrated with the mode functions, started from the box means; `= 1` the box
means of the mesh at every stage (H = -<K>/3, a = <chi>^(2/p)). Level 2 (local
coefficients) is not implemented. alpha_b is the box mean of the lapse, so the proper
time of the background runs at the rate alpha_b [JUDGEMENT; tested only with alpha = 1].

Stage times (request R5): the lockstep data (time, phi_b, Pi_b, ln a, Re and Im of R_q
and dR_q/dtau per shell) are advanced on the host by the same low-storage update as the
fields (`CopyU`, `ExpRKUpdate`), so every stage evaluates S_R, the window and the kick
coefficients with data of its own stage; no stage time is passed around.

Mode functions at the start: `noise_mode_file`, text rows `|n|^2  Re R  Im R  Re dR/dtau
Im dR/dtau` for every shell (extra rows ignored), in the normalisation in which the
field is L^(-3/2) sum R alpha e^(ik.x) (the QFT amplitude of SPEC 5.4).

### 7.4 What Track E's specification must still supply, and what is not done

| Request | State |
|---|---|
| R1 class, task order, Tmunu from the stage's chi and gt | done (sections 2, 4) |
| R2 additive Tmunu | done in the solver and the constraints, verified to 7.6e-16 (test 5); particle `.cstat.hst` not yet (section 5) |
| R3 kicks at stage times, sign-safe, projector in qh, off by default, bitwise neutral | done; the projector identity verified on the kick fields, the constraint behaviour in an evolved run only as a smoke test (section 10) |
| R4 noise without a Fourier library, keys, synthesis | done; checked against `python/nrpic/scalar_field.py` (numpy FFT), not yet against `codebase/ref/synth.py` or the unit test of `NOISE_SPEC.md` (not on the branch when this was written) |
| R5 stage times | done by lockstep integration |
| R6 double-precision output, constraints without particles, exact restart | done; [M] of P1 not computed |
| R7 no GPU FFT | accepted |
| R8 initial slice | NOT done: no `NRCOSMO2` reader and no in-code synthesis of the perturbed initial slice of SPEC 5.3. Needed from Track E: per shell the complex transfer coefficients of delta phi, delta Pi, delta chi, delta K at t* (they are linear in W R and d(W R)/dt), in a table like the mode file; the code would synthesize them with the same alpha_n |
| SPEC 10.5 diagnostics | box means and constraint norms done; R^NR extraction, shell spectra, per-mode amplitudes: by analysis of the dumps (`read_dump`, `analyse`) |

Also needed from Track E: the mode file of each test case (R_q, dR_q/dtau at N* for every
|n|^2 <= nmax2); a check of the inflection potential against the source; the choice of
level 0 or 1; the discrete or continuum k^2 in the mode equation (the code uses the
continuum k^2 per shell; a stencil k^2 depends on direction and would need one mode
function per wave vector).

## 8. Initial data that satisfy the constraints (test 3)

phi = phi0 + A sin(k.(x - x0)), psi = 1, At_ij = 0, K = K(phi(x)), Pi = K'(phi)/(12 pi).
The momentum constraint holds identically; since |grad phi|^2 = k^2 (A^2 - (phi - phi0)^2)
is a function of phi, the Hamiltonian constraint is K'^2 = 12 pi K^2 - 144 pi^2 G(phi) -
288 pi^2 V(phi), integrated in the problem generator (4096 Runge-Kutta steps, Hermite
table). Valid while the right-hand side is positive (gradient energy below kinetic
energy). General initial data (several modes, tensor part) need the elliptic solve of
decision 0010 item 4; not part of this package.

## 9. Cost

| Configuration | Zone-cycles per second | Relative |
|---|---|---|
| Z4c alone (puncture, 64^3, 32^3 MeshBlocks, nghost 4, RK4), one core of a Xeon 8360Y | 1.494e4 | 1 |
| Z4c with the coupled scalar field, no stochastic sources | 1.337e4 | 1.118 |
| the same with the Mukhanov-Sasaki sources: ball n_max = 16, 8538 modes, 214 shells, six fields synthesized at every stage | 1.239e4 | 1.206 (1.079 over the field alone) |

Run core-20261115-135423-5a6953e (four steps each). So the field costs 12 percent of a
Z4c step and the synthesis 8 percent at 64^3 with n_max = N/4 on one core [VERIFIED]. On
a card: pending (section 10). The synthesis cost per cell grows with the number of
distinct n_x (n_max + 1) and, for small MeshBlocks, with the number of modes per cell
(design review D2).

## 10. What is verified

All on processors (serial build), executable frozen per commit under `.work/exe/`.
Predictions were written before the runs; failed predictions and their follow-up are in
the journal. Figures: `tracks/core/notes/scalar_figs/`.

| Statement | Evidence |
|---|---|
| Existing behaviour unchanged: five existing set-ups (analytic metric; mesh metric with deposit; refined mesh with deposit and excision; Z4c with particle sources; restart files with removal), 36 output files byte-identical between the executable of the unmodified source and the one with the module | run core-20261115-132758-ba37619 (first source: all 36 identical). Final source, run core-20261115-135417-5a6953e: 33 identical, the three mesh restart files differ in 35 bytes each. Those bytes are the nine coarse-mesh indices of `Mesh::mesh_indcs`, which nothing sets and `restart.cpp` writes raw: bytes 8252 to 8287, exactly that range, in all three files (run core-20261115-140328-5a6953e). They are heap content and differ between two executables whose allocation history differs; they are not read back meaningfully. The data of the files are identical |
| Test 1, Klein-Gordon plane wave of a test field on flat spacetime (m = 5, n = (1,1,0), box 1): frequency equals that of the stencils, omega_h, to -1.2e-8 ... -1.34e-8 (the phase error of RK4 at dt = 1/512) in twelve runs; spatial orders 1.99, 3.96, 5.92 for nghost 2, 3, 4; temporal order 3.9993 to 3.9999 with errors equal to the classical RK4 estimate to four digits; dissipation 0.5 damps at 0.9994 of (stencil + integrator); five potentials against the ordinary differential equation converge at orders 3.98 to 4.06 (2.2e-6, 1.5e-5, 7.2e-7, 3.8e-7 at Courant 0.25 over ten time units); the table reproduces the potential it tabulates to 9.1e-10 | runs core-20261115-133809-836ac86, core-20261115-134423-836ac86 (analysis); `fig_wave_convergence.png`, `fig_wave_diss_potentials.png` |
| Test 2, homogeneous slow roll (m = 0.1, phi0 = 3, attractor momentum) with the evolved metric against the Friedmann and Klein-Gordon equations: conformal-time lapse `d_t alpha = -(1/3) alpha^2 K` to a = 3.77, relative differences at Courant 0.25 of 2.9e-7 (a), 2.2e-10 (phi, K), 5.4e-8 (alpha), ratios 15.3 to 15.8 per halving of the step; geodesic slicing to a = 123 (4.81 e-folds), 5.0e-9 (a), field and K on the rounding floor 7e-13; eps1 within 0.994 to 0.997 of 1/(4 pi phi^2); rms H below 5e-12 of [H], momentum constraint below 6.3e-15 | run core-20261115-133955-836ac86; `fig_flrw_conformal.png`, `fig_flrw_geodesic.png` |
| Test 3, plane perturbation (A = 0.003 on phi0 = 3, n = (1,1,0), Pi0 = -0.05) from the data of section 8: at t = 0 rms H = 5.6e-7, 8.9e-9, 1.4e-10 and rms M = 1.3e-5, 2.6e-7, 4.3e-9 for N = 16, 32, 64 (orders 5.97, 5.99 and 5.66, 5.91); during the evolution to t = 0.5 orders 5.15 to 6.00 (H) and 5.22 to 5.99 (M); with a uniform momentum instead (control) rms M = 1.5e-3 and no convergence | run core-20261115-134118-836ac86; `fig_plane_constraints.png`, `fig_plane_convergence.png` |
| Test 4, generic sources (32^3, 2084 modes): coefficients of the synthesized fields equal (shell factor) x (twin alpha) to 2.2e-16 of the rms for frozen, white-in-time and step-window cases, nothing outside the ball (9e-17); shell means of the power within 2.9 sigma (85 shells), mean 1.031 +- 0.022; all dumped fields bit-identical for 1, 8 and 64 MeshBlocks; a restart at cycle 32 gives byte-identical dumps at cycle 64; increments of two steps have phase correlation 1.0 (frozen) and -5e-5 +- 0.06 (white in time); phi and Pi after one step equal the Runge-Kutta response to the sources to 6.6e-16 and 2.6e-15 | run core-20261115-135414-5a6953e (first version core-20261115-134715-1b6bc30, journal entry 4); `fig_noise_power.png` |
| Test 4, Mukhanov-Sasaki sources (16^3, box 10, 435 modes, 31 shells, slow-roll background, geodesic slicing): lockstep mode functions against SciPy 6.4e-3, 3.7e-4, 2.2e-5 for Courant 0.25, 0.125, 0.0625 (orders 4.12, 4.07); the six fields equal (shell factor) x (twin alpha) x (stencil projector) to 7.1e-17 of the rms; 1 and 8 MeshBlocks bit-identical, restart byte-identical; discrete momentum constraint of the kick fields 4.9e-16 of its terms with the stencil projector, 1.4e-2 with the continuum projector; flipped sign of the Pi kick gives rms H = 1.9e-7 after one step against 2.7e-11, doubling with the amplitude | the same run; `fig_noise_ms.png` |
| Test 5, particles and field together (dust universe of `problems/cosmo/flrw.athinput`, 32^3 particles, density-form sources, 16 steps): a vacuum energy Lambda = 0.6 from the particle module against the same from a field at rest with the constant potential Lambda/(8 pi) through `tmunu_tot`: lapse at the probe, proper volume and deposited energy agree to 7.6e-16; a field with V = 0 against no field: 7.1e-16. The vacuum energy changes the final volume by 19 percent | run core-20261115-140626-6699860; `fig_particles_field.png` |
| Statically refined mesh (smoke run): plane wave of test 1 across one refinement level (32^3 root mesh, 120 MeshBlocks, 64 steps) stays stable; rms difference to the exact wave 2.5e-6 (coarse), 6.4e-6 (fine), maximum 1.8e-5, about 100 times the error of a uniform 32^3 mesh | run core-20261115-135434-5a6953e (scouting) |
| Standard outputs `sf` (bin) and `sf_phi` (vtk) are written and read by `athenak/vis/python/bin_convert.py` | unregistered smoke run, `scratch/core/tmp/sf/out_smoke` |
| The module compiles in the card build (CUDA 12.6) | `.work/build_gpu_sf`; card runs pending: Slurm job 4427 (`tracks/core/analysis/scalar/gpu_job.sh`: cost at 128^3, tests 2, 4, 3, 1), queued when this was written; each part registers itself under `tracks/core/runs/` with a `summary.json` |

## 11. Limits and open points

- Card: nothing has run on a card yet (job queued). Layout independence and the twin
  agreement are properties of integer arithmetic and of sums in a fixed order, but on the
  card they are [TO VERIFY] until the job has run.
- First-order residual of the momentum constraint in the evolved Mukhanov-Sasaki run on
  the coarse test mesh (2.7e-12 after one step with either projector; journal entry 4):
  not explained by a test. Track E's test L5 on a resolved mesh decides.
- Not implemented: the perturbed initial slice of SPEC 5.3 (request R8), level 2 of the
  stochastic backreaction, a stencil k^2 in the mode equation, [M] of arXiv:2512.14649,
  the stochastic graviton sources, a Sommerfeld condition for the field, adaptive
  refinement, several MPI ranks, more than one scalar field.
- The inflection potential is transcribed from Track E's SPEC, not from the paper.
- Particles and field in one run: verified for a field at rest (test 5); not run with a
  dynamical field. The constraint statistics of the particle module do not include the
  field.
- Refined meshes: one smoke run; the order of the error across a refinement boundary and
  the constraint behaviour with a coupled field there are not measured. The stencil
  projector uses the cell size of the root mesh.
- The driver's `rk4` drifts a constant by about 1.4e-15 per step (coefficients given to
  15 digits); this bounds the agreement of long geodesic-slicing runs (test 2).
- The restart header holds 36 unset bytes (`Mesh::mesh_indcs`); a regression that compares
  restart files byte by byte across two executables has to mask them, or the mesh
  constructor has to zero them (request to main/core, not done here because it changes
  restart files of existing runs).
- Time step: no limit from the mass term or from the expansion; in conformal time during
  inflation the step covers a growing number of e-folds (use geodesic slicing, as the
  SPEC does).
