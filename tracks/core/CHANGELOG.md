# CHANGELOG of core (the NRPIC implementation in this repository's AthenaK)

Releases are git tags, created by the orchestrator (decision 0003; from wave 3 by its
release clerk once `tracks/core/RELEASE-<version>.md` reports a passing byte regression,
decision 0019 item 4). Tags that exist: core-v0.1 = 7daed19 (asymptotically flat),
core-v0.2 = 52c44eb (periodic particles and cosmological gauge; source of main a1c2237),
core-v0.3 = 609a875 (below).

## core-v0.4 (release candidate, 2026-11-21): the seven wave-2 source branches

Record: `tracks/core/RELEASE-v0.4.md` (first line: source commit and regression
verdict; the regression table; the quick tests; the card check). Source commit
**f9323185** (f93231854cf038db56bd8c37a47c39c2ba6b1f14) of `core/nrpic`: the last commit
that changes `athenak/`, `python/`, `problems/` or `scripts/`; later commits add records
(`tracks/core/`, `docs/COLLISIONS.md`) and merge main. Executables built from it, with
READY (every new option with one example input), COMMIT and SHA256SUMS:
`/data/haiyangw/nrpic/scratch/core/exe/core_nrpic_v04/`.

### What is merged (in this order, one merge commit per branch)

| Branch (tip merged) | Merge | Capability | Switch (absent = off) | Interface document |
|---|---|---|---|---|
| core/requests-b (f134b775) | 3ab47062 | linear-wave generator transverse and traceless for any wave vector, cross polarization, error file; mesh output in double precision; Weyl scalar labelled at the end of the step; restart header bytes zeroed; thin periodic boxes and lattice jitter in the initial-data tool | `<problem> amp_cross, phase_cross`; `<outputN> double_precision`; `<z4c> waveform_at_new_time` | `tracks/core/interfaces/REQUESTS_B.md`, `docs/FORMATS.md`, `docs/UPSTREAM_DEFECTS.md` |
| core/gauge (58d10777) | 120aa7cf | lapse relaxation where matter expands; shift damping that follows the puncture trackers (`z4c/z4c_gauge_ext.hpp`) | `<z4c> lapse_leak`; `<z4c> shift_eta_profile` | `tracks/core/interfaces/cosmo_gauge.md` section 7 |
| core/scalar-2 (207424d2) | 54dc527e | initial slice of a stochastic-inflation run at N*; constraint record `sf.con.hst`; double-precision dumps with the metric; scale of the mode functions | `<problem> id = stochastic`; `<scalar_field> con_dcycle, dump_metric, noise_mode_scale` | `tracks/core/interfaces/scalar_field_2.md` |
| core/clump-curvature (56d7335c) | e2498da4 | Gaussian clumps of `nrpic_cf` with momentum and spin (smeared Bowen-York curvature); generator model `clumps` of `problems/ic/make_ic.py` | `comp<c>_p1..3`, `comp<c>_s1..3` on a component of type gaussian | `tracks/core/interfaces/moving_clumps.md` |
| core/id-solver (d88ff4f9) | de42b294 | elliptic solve of the Hamiltonian constraint (and, optionally, of the momentum constraint) on the mesh of the run before the first step; Robin faces of the multigrid solver | `<particles> id_solve`, `id_vector`; `<gravity> mg_bc = robin` | `tracks/core/interfaces/id_solver.md` |
| core/requests-adf (b6041dbc; records bc38aafc merged later as 148a302e) | 7b0fcf27 | tracers (m = 0) on timelike geodesics on every metric; restart keeps the output schedule; excision on analytic metrics; accretion diagnostics; external gravity of the Newtonian mode; common horizon of one pair | corrections act without a switch (`<particles> zero_mass = null` restores the tracer rule of core-v0.3); `<particles> removal_record, acc_nsphere, peri_count, newton_pm_mass, newton_bg_t0`; `<fastflow> punc_pair_a_<n>` | `tracks/core/interfaces/REQUESTS_ADF.md`, `diagnostics.md`, `multi_puncture.md` |
| core/collisions-2 (8c03bc96; records 4c798e7a merged later as e9644451) | f9323185 | collisions that conserve the pair's canonical energy with the metric at each particle; static conformally flat test metric; perturbing radial force | `<particles> coll_energy`; `<problem> metric_kind = static_conformal`; `<particles> perturb_gamma` | `tracks/core/interfaces/collisions.md` section 11, `rng.md` section 6.1, `docs/COLLISIONS.md` |

No branch is left out. Conflicts resolved by hand in the merges: `z4c.cpp`, `z4c.hpp`
(gauge after requests-b), `CMakeLists.txt`, `nrpic.cpp`, `nrpic_io.cpp`, `particles.hpp`
(the three particle branches), `docs/FORMATS.md`, `tracks/core/interfaces/rng.md`
(both rows of the stream table kept). Each side keeps its behaviour: the quick test of
every branch gives, with the merged executable, the bytes of the branch's own executable.

### Behaviour that changes without an option (corrections)

1. Restart files: the 36 bytes of the nine never-set members of `Mesh::mesh_indcs` are
   zero. Byte comparisons of restart files against core-v0.3 differ in these bytes.
2. `Driver::Finalize` no longer advances `last_time` of an output written off its
   schedule at the end of a run: the parameter dump embedded in such final files differs
   in `last_time` lines, and a run continued after a stop at the wall-clock or cycle limit
   writes every scheduled output (core-v0.3 lost one per stop).
3. A particle with m = 0 on the mesh metric is a tracer on a timelike geodesic
   (core-v0.2 and core-v0.3: null). `<particles> zero_mass = null` gives the old rule;
   light rays (m < 0) are not affected.
4. Analytic metrics honour `<particles> alpha_exc` (default -1: off) and remove flagged
   particles.
5. `z4c_linear_wave`: sign of two tensor components for an oblique wave vector, and the
   error routine compares at the final time: an existing oblique input with kx2 != 0
   changes (the upstream tensor was not transverse there).
6. On a card, collisional runs without the new options differ from the core-v0.3 card
   executable at rounding (momenta 2e-14, the same pairs in every step; run
   core-20261119-141059-f3ccf56 of the package); processors are byte-identical.

### Input options (`tracks/core/verify/options_at.py core-v0.3 HEAD`)

61 options added, none removed, no default changed
(`scratch/core/tmp/lead_v04/options_v03_v04.json`); the scan does not see names that
the source builds at run time, added here by reading the source.

- `<outputN>` double_precision
- `<z4c>` waveform_at_new_time, lapse_leak, lapse_leak_alpha, shift_eta_profile,
  shift_eta_mref, shift_eta_width, shift_eta_width_local
- `<gravity>` `mg_bc = robin`, robin_x1, robin_x2, robin_x3
- `<particles>` id_solve, id_residual, id_psi_init, id_tol, id_maxit, id_lin_tol,
  id_lin_maxit, id_mg_tol, id_dump, id_vector, id_vector_residual, id_vector_tol;
  zero_mass; removal_record, acc_nsphere, acc_radius1..4, acc_x1..3, acc_tracker,
  acc_dcycle, peri_count, peri_rmax; newton_pm_mass, newton_pm_x1..3, newton_pm_soft,
  newton_pm_soft_frame, newton_bg_t0; coll_energy; perturb_gamma, perturb_time,
  perturb_tstart, perturb_x1..3
- `<problem>` (z4c_linear_wave) amp_cross, phase_cross; (scalar_field) `id = stochastic`,
  slice_window, slice_k2, slice_delta_pi; (nrpic_cf, type gaussian) comp<c>_p1..3,
  comp<c>_s1..3; (nrpic_geodesic) `metric_kind = static_conformal`, psi0, alpha_amp,
  psi_amp, shift_amp, mode_n1..3
- `<scalar_field>` noise_mode_scale, con_dcycle, dump_metric, dump_constraints,
  dump_magnitudes, dump_noise
- `<fastflow>` punc_pair_a_<n>, punc_pair_b_<n>

### Files and formats added (`docs/FORMATS.md`)

`<basename>-errs.dat` (linear wave); bin output with 8-byte values; `<basename>.sf.con.hst`
and scalar-field dumps of layout NRSFDMP2; `<basename>.idsolve.txt`, `.idsolve.bin`,
`.idvector.bin`; `<basename>.removed.bin`, `<basename>.acc.hst`, a last block of
pericentre counts in snapshots; history columns 32 to 36 of `<basename>.coll.hst` and
collision dumps of version 2 (NRPCOLD2). The particle restart format keeps three
integers per particle.

### Evidence

Byte regression against core-v0.3 on the twelve set-ups of wave 1: PASS (run
core-20261120-221607-4985804). Quick test of every merged branch and the card check:
`RELEASE-v0.4.md`. The capability tests were run by the work packages on the
executables of their branches (run ids in each interface document, journal
`tracks/core/JOURNAL-{bfix,gauge,scalar2,clump,idsolve,dfix,coll2}.md` and READY file,
copied to `scratch/core/exe/core_nrpic_v04/branches/`).

### Known limitations carried into core-v0.4

`tracks/core/stage/G2/OPEN.md` (section of 2026-11-21) and the READY of the published
executables. The most important: no two new capabilities were run together; the
initial-data solver works on uniform meshes on one rank without punctures; clumps with
momentum are Gaussians only; `<fastflow> hmean_tol` acts on the surface integral of the
expansion and silently ends searches in cosmological boxes; the particle module is
single-rank.


## core-v0.3 (tagged; written 2026-11-15 as a proposal): wave-1 capabilities of decision 0010

Proposed tag: `core-v0.3` on commit **609a875** of `core/nrpic` (the last commit that
changes `athenak/src/`; every later commit of this session touches `tracks/core/` only).
Both executables of the regression were built from a `git archive` of 609a875:
`wt/core/.work/build_cpu_609a875/src/athena` (sha256 in
`scratch/core/tmp/lead/exe_sha256.txt`) and `wt/core/.work/build_gpu_609a875/src/athena`.

```
git tag -a core-v0.3 609a875 -m "core-v0.3: collisions, scalar field and stochastic sources, Newtonian mode, Bowen-York punctures, initial data with extrinsic curvature, reproducible random numbers"
git push origin core-v0.3
```

### What is merged (in this order)

| Branch (head) | Merge | Capability | Switch (absent = off) | Interface document |
|---|---|---|---|---|
| core/rng (a6e5c46) | fcc3179 | counter-based random numbers (Philox-4x64-10), bit-identical on processor, card and NumPy twin; test kick | `<job> rng_seed`; `<particles> test_kick` | `tracks/core/interfaces/rng.md`, `docs/RNG.md` |
| core/collisions (ba50bff) | c88804c | relativistic Monte Carlo collisions in the normal-observer frame of each cell; homogeneous static metric for tests (`nrpic_geodesic` `metric_kind = homogeneous`) | `<particles> collisions = true` | `tracks/core/interfaces/collisions.md`, `docs/COLLISIONS.md` |
| core/scalar-field (59c47d7) | 65648c8 | minimally coupled scalar field evolved with Z4c, sources through `Tmunu::tmunu_tot` (with particles), stochastic sources (generic and Mukhanov-Sasaki), restart side file, outputs `sf_phi`, `sf_Pi`, `sf` | a `<scalar_field>` block | `tracks/core/interfaces/scalar_field.md` |
| core/id-extrinsic (6fa6472) | dc93a72 | `nrpic_cf` radial table of format 2 (extrinsic curvature, lapse, shift; optional `# breaks`); expanding-ball generator `problems/ic/make_ball.py` | a table whose header says `# format = 2` | `tracks/core/interfaces/spherical_id_format2.md`, `docs/FORMATS.md` |
| core/multi-puncture (81d4651) | 7c11538 | Bowen-York momentum and spin for any number of punctures of `nrpic_cf`, regular corrections (closed form with background factor, or table), trackers, refined regions and horizon finders per puncture | `comp<c>_p1..3`, `_s1..3`, `_corr`; `<problem> puncture_setup = true` | `tracks/core/interfaces/multi_puncture.md`, `docs/FORMATS.md` (format mp1) |
| core/newton (ce329f5) | 66bd4c3 | Newtonian mode of the particle module: rest-mass deposit, multigrid Poisson solve, kick-drift-kick, comoving coordinates; `MGGravityDriver::SolveSource` | `<particles> pusher = newton` | `tracks/core/interfaces/newtonian_mode.md`, `docs/FORMATS.md` |

Maintainer commits on top of the merges:
- **0f11630** `nrpic_cf`: the curvature of a format-2 table is added to the Bowen-York
  curvature instead of replacing it (the semantic overlap of core/id-extrinsic and
  core/multi-puncture). Verified by test P5 of the lead (run id in `stage/G2/EVIDENCE.md`).
- **609a875** collisions refuse `pusher = newton` (the Newtonian mode keeps the potential
  in the lapse slot that the pair probability reads).

### Input options (`tracks/core/verify/options_at.py 52c44eb 609a875`)

80 options added, none removed. The ten "changed defaults" the scan reports are second
call sites in new opt-in files (`nrpic_puncture_setup.hpp` writes `<fastflow>` and
`<z4c_amr>` parameters only with `puncture_setup = true`; `scalar_field_tests.cpp` reads
`<problem> id` and `omega` for its own generator; `<particles> deposit` defaults to true
also for `pusher = newton`). No default of an existing input changed; the byte
regression below confirms it for twelve existing set-ups.

- `<job>` rng_seed
- `<particles>` collisions, coll_sigma, coll_sigma_model, coll_sigma_w, coll_pmax,
  coll_subcycle, coll_nsub_max, coll_cell_factor, coll_weights, coll_hist_dcycle,
  coll_dump_cycle, coll_budget; test_kick, test_kick_mode, test_kick_key,
  test_kick_sigma, test_kick_prob; newton_expansion, newton_hubble, newton_exponent,
  newton_cfl, newton_mg_tol; `pusher = newton`
- `<problem>` (nrpic_cf) shift, shift_comp, comp<c>_p1..3, comp<c>_s1..3, comp<c>_corr,
  comp<c>_corr_file, corr_background, puncture_setup, puncture_horizons,
  puncture_radius, puncture_level, comp<c>_radius, comp<c>_level; (nrpic_geodesic)
  metric_kind, alpha0, gxx..gzz; (rng_test, scalar_field) test-generator options
- `<scalar_field>` (new block) potential, mass, lambda, mu, v0, vev, v_offset,
  table_file, couple, diss, hist_dcycle, dump_dcycle, dump_dt, noise and its 20
  noise_* options
- outputs `sf_phi`, `sf_Pi`, `sf` (NOUTPUT_CHOICES 154 -> 157)

### Files and formats added

`<basename>.coll.hst`, collision dump; `<basename>.sf.hst`, `.sf.NNNNN.dump`, restart side
file `<restart>.sf`; `<basename>.newton.hst`, restart side file `*.rst.prt.nwt`; radial
table format 2; puncture correction table format mp1 (`docs/FORMATS.md`).

### Evidence

Regression and tests on the merged executables: `tracks/core/stage/G2/REPORT.md` and
`EVIDENCE.md`. The capability tests themselves were run by the work packages on their
branches (run ids in each interface document and journal); the lead reran the quick
ones on the merged executables.

### Known limitations carried into core-v0.3

`tracks/core/stage/G2/OPEN.md` and `tracks/core/RISKS.md`. The most important: the
collision steps raise the energy at the particles' own metric by 1e-9 to 1e-8 per
collision in a potential (cell-frame conservation only); no lapse condition tried for the
expanding ball is free of a lapse front from a sharp surface; the shift damping of the
Gamma-driver is one number for all punctures; the Newtonian mode, the scalar field and
the collisions have no test on refined meshes beyond one smoke run each, and the particle
module is single-rank.
