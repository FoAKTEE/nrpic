# CHANGELOG of core (the NRPIC implementation in this repository's AthenaK)

Releases are git tags on branch `core/nrpic`, created by the orchestrator (decision
0003). Earlier tags: proposal in `tracks/core/verify/RELEASE.md` (core-v0.1 = 7daed19,
asymptotically flat; core-v0.2 = 52c44eb, periodic particles and cosmological gauge;
source of core-v0.2 = source of main a1c2237).

## core-v0.3 (proposed, 2026-11-15): wave-1 capabilities of decision 0010

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
