# Release proposal: core-v0.1 and core-v0.2

Proposal of the verify package (owner core) to the orchestrator, who creates the tags
(coord/digests/wave-1-plan.md, line 33). Nothing here is tagged.

| Tag | Commit | Date | Capability | Evidence |
|---|---|---|---|---|
| core-v0.1 | `7daed195af9efb6e93611bf58ebe29b3ce1fc37a` | 2026-11-13 23:02 | asymptotically flat Einstein-Vlasov particle-in-cell in AthenaK | LADDER.md rows 1-4; regressions G and O |
| core-v0.2 | `52c44eb21b54470a5f71fac155c637ec88163a62` | 2026-11-15 02:51 | v0.1 plus periodic particles and a cosmological gauge | cosmo/TESTLOG.md; regressions F and L |

Commands for the orchestrator:

```
git tag -a core-v0.1 7daed195af9efb6e93611bf58ebe29b3ce1fc37a -m "core-v0.1: asymptotically flat NRPIC (tracks/core/verify/RELEASE.md)"
git tag -a core-v0.2 52c44eb21b54470a5f71fac155c637ec88163a62 -m "core-v0.2: periodic particles and cosmological gauge (tracks/core/verify/RELEASE.md)"
```

## Why these commits [VERIFIED with git]

- 7daed19 is the parent of `f36f2b1` (cosmology plan, documents only), which is the
  parent of `0e4613c` (test log entry), the parent of `4467852`, the first commit of the
  cosmology extension that touches `athenak/src`. `athenak/src`, `python`, `problems`
  and `scripts` are identical at 7daed19, f36f2b1 and 0e4613c (`git diff --stat` empty).
- 52c44eb is the commit `core/nrpic` was created from (`git reflog core/nrpic`:
  "branch: Created from main"). The last commit before it that touches `athenak/src` is
  `0c06525` (2026-11-14 08:35). `athenak/src`, `python`, `problems`, `cosmo` and
  `scripts` are identical at 52c44eb and at the head of `main` today (d6eb090), so the
  tag also describes the source every track is using now.

## Executables

No executable is built from either tag commit by name; the release executables named in
CLAUDE.md are:

| Executable | Built | Contents [VERIFIED, option strings in the binary] | Source [JUDGEMENT] |
|---|---|---|---|
| card `.work/build_gpu_c3/src/athena` | 2026-11-14 08:31:30 | every option name of the current source, including `damp_kappa_gam` (0c06525) | the source of 0c06525, i.e. of core-v0.2 |
| processor `.work/build_cpu_c1/src/athena` | 2026-11-14 06:03:37 | `cons_dcycle`, `interp`/`bspline` (f219ade) but not `damp_ch_chipow` (631cfe3) nor `damp_kappa_gam` (0c06525) | a state between f219ade and 631cfe3: older than core-v0.2 |

`git-state.txt` of both build directories records the Kokkos submodule (6739bc623), not
the source. Request (README.md): rebuild the processor executable from core-v0.2 before
it is called the release executable for processors, and let the build script record the
source commit. Until then, a processor run that sets `<z4c> damp_ch_chipow` or
`damp_kappa_gam` gets the parameter-unused warning and the defaults.

Regression with these executables (`regress/`, JOURNAL.md): the card executable
reproduces the core-v0.1 evidence of the dust collapse to round-off (horizon mass
2e-15, central lapse 2.4e-15 from `runs/os/nocap_sc`, made with an executable of
2026-11-13 07:06) and the core-v0.2 evidence of the homogeneous universe and the
linear-growth run to four digits and to 5e-12 of the contrast; the processor executable
reproduces the Kerr passage bitwise. With the defaults of the options added in v0.2,
an asymptotically flat input therefore runs the path of v0.1 [VERIFIED for the collapse
of regression O; the defaults are in `athenak/src/particles/nrpic.cpp` lines 100-188].

## core-v0.1: CHANGELOG against the vendored AthenaK (c5a0d7f, import commit 338bcb1)

28 files of `athenak/src` changed, 3604 lines added (`git diff --stat 338bcb1 7daed19
-- athenak/src`); input options from `options_at.py 338bcb1 7daed19 52c44eb`.

Capabilities.
- Particle type `nrpic` in the particle container (`particles.cpp`, `particles.hpp`,
  `particles_tasks.cpp`): macroparticles with positions, covariant momenta per unit rest
  mass, rest masses, species, tags; ownership across MeshBlocks and refinement.
- Pushers (`nrpic_kernels.hpp`): implicit midpoint in coordinates (`pusher = midpoint`)
  and the spacetime Boris pusher (`pusher = boris`) with the symmetric or the Cholesky
  tetrad (`triad`); fixed-point iteration (`tolerance`, `max_iterations`).
- Metric at the particles (`metric`): analytic Kerr in spherical Kerr-Schild,
  Boyer-Lindquist or Cartesian Kerr-Schild (`bh_mass`, `bh_spin`), a Hermite lattice of
  the analytic metric (`lattice`, `lattice_dx`), or the evolved Z4c metric on the mesh
  (`mesh`, Catmull-Rom interpolation, `nrpic_mesh.hpp`, `utils/inline_interpolator.hpp`).
- Deposition of the stress-energy into the Z4c matter sources `tmunu` (`deposit`):
  cloud-in-cell at the finest local level (published rule), conservative across
  refinement levels, optional level cap (`deposit_max_level`, `deposit_min_level`,
  `deposit_adaptive` with `deposit_ppc`, `deposit_max_coarsen`); binomial filter passes
  (`nfilter`) with optional compensation (`filter_compensate`, `filter_comp_c`).
- Excision of macroparticles where the lapse falls below `alpha_exc` or inside a found
  apparent horizon (`ah_exc_factor`); counts and masses removed in the history.
- Problem generators (`pgen/nrpic/`): `nrpic_geodesic` (single or inline particles in a
  fixed Kerr metric; `nparticles`, `p<i>_x1..3`, `p<i>_u1..3`, `p<i>_m`) and `nrpic_cf`
  (conformally flat time-symmetric data from components `comp<c>_type` = table,
  puncture, Gaussian, spheroid with `comp<c>_file`, `_mass`, `_sigma`, `_a`, `_b`,
  `_x1..3`; `ncomp`; `lapse`, `lapse_comp`) with particles from `particle_file`.
- Diagnostics (`nrpic_io.cpp`, `nrpic_curvature.cpp`): history `<basename>.nrpic.hst`
  (`hist_dcycle`; sums, mesh integrals before and after the filter, probe lapse and
  density, proper time, excision and escape counts, pusher iterations, MeshBlocks),
  trajectories (`traj_dcycle`, `traj_ntrack`), particle snapshots (`snap_dt`), probe
  (`probe_x1..3`), Kretschmann scalar on slices and its history (`curv_dt`,
  `curv_slice`, `curv_plane_y`); restart of the particle state (exact, `docs/TESTLOG.md`
  lines 64-70); formats in `docs/FORMATS.md`.
- Z4c and mesh (`z4c/`, `mesh/`, `driver/`, `outputs/restart.cpp`): source coupling,
  parabolic relaxation of the Hamiltonian constraint (`<z4c> damp_ch`, `damp_ch_dx`),
  Loehner refinement indicator (`<z4c_amr> lohner_refine`, `lohner_derefine`,
  `lohner_eps`), apparent-horizon finder with search cadence and metric derivatives from
  the interpolant (`<fastflow> find_every`, `metric_drvts`).

Defaults to know.
- `<fastflow> metric_drvts` defaults to `stored`, the original behaviour that reads
  2 to 3 percent low (`docs/TESTLOG.md` lines 310-386); every input of the campaign sets
  `interpolant`. Request: make `interpolant` the default (core decision).
- `deposit` defaults to on only for the mesh metric with Z4c; `nfilter` defaults to 1.

Evidence: LADDER.md (rows 1 and 2 PASS, rows 3 and 4 PARTIAL), `docs/TESTLOG.md`,
`paper/main.pdf`, tables `paper/sections/tables/tab_outcomes.tex`, regression G
(`core-20261115-032625-45e1779`) and O (`core-20261115-032614-45e1779`).

Known limitations (each with its source).
- Prolate collapse at 10^4 particles: horizon mass 3 to 5 percent below M, one
  resolution (LADDER.md row 3).
- Cluster collapse times 1.4 to 1.75 times the paper's at 10^4 particles; growing
  central-lapse oscillation of the stable model, cause not determined (row 4).
- The published lattice mass rule carries 1.2 percent too much mass at 10^4 particles;
  use `make_ic.py --lattice-surface-correction` (`docs/TESTLOG.md` lines 600-633).
- A level-capped cloud disturbs a forming black hole (horizon mass drift 0.65 to 1.1
  percent); collapse runs use the cloud at the finest level (lines 905-937).
- The mesh filter is not conservative across refinement levels (up to 7e-3 of the
  integrals, `docs/TESTLOG.md` lines 650-654).
- A Z4c restart agrees with an uninterrupted run to about 1e-12, not bitwise
  (`scripts/README.md`).
- Provenance: the table `tab:outcomes_overdensities_stated` comes from the chain
  `runs/jeans/n1e4_v20`, whose executable was copied at 2026-11-14 02:44, i.e. built from
  source after 7daed19 (with the v0.2 options at their defaults). The other tables come
  from executables older than 4467852 [JUDGEMENT from the chain and run executable
  dates; not checked run by run].

## core-v0.2: CHANGELOG against core-v0.1

21 commits touch `athenak/src` between 7daed19 and 52c44eb (`git log 7daed19..52c44eb --
athenak/src`); 14 files, 1918 lines added, 130 removed; a new problem generator
`nrpic_cosmo`. Options: 27 added, none removed, no default changed (`options_at.py`).

Capabilities (cosmo/README.md, the commit messages named).
- Periodic domains: particles and clouds wrap at periodic boundaries; probes and
  clouds in periodic boxes (4467852).
- Proper time per particle; null particles (light rays) in the midpoint pusher, emitted
  at set times; richer trajectory records; extra probes `nprobe`, `probe<n>_x1..3`
  (4467852, 95b5c47).
- Cosmological constant as a source (`<particles> lambda`).
- Density-form sources: the matter sources are handed to Z4c as densities and converted
  with the volume element of every stage (`source_density`), optionally extrapolated to
  the middle of the step (`source_extrap`); the frozen-source coupling of v0.1 is first
  order in an expanding background (`cosmo/TESTLOG.md` lines 41-59).
- Problem generator `nrpic_cosmo` (`<problem> id = flrw | file`, `id_file`, `hubble`;
  white-noise robustness test `noise_amp`, `noise_seed`, `noise_gamma`, `noise_atilde`,
  `noise_theta`); interpolation of file data onto refined blocks (3933309).
- Lapse conditions for cosmology: Bona-Masso with f = 1/3 through the existing
  `lapse_harmonic` (conformal time on the homogeneous solution), `<z4c> lapse_volume`
  (808355c), `lapse_kdriver` (driver towards constant mean curvature, a12783d).
- Constraint damping at a fixed rate per unit coordinate time
  (`damp_kappa1_over_alpha`); exponent of chi in the Hamiltonian-constraint relaxation
  (`damp_ch_chipow`, 631cfe3); damping of the connection constraint alone
  (`damp_kappa_gam`, 0c06525; tested, no gain).
- Cloud shapes `deposit_shape = cic, tsc, pcs` (4681b1a); compensation of the cloud on
  the deposited density `deposit_comp_c` (225e4c6), its limited flux form
  `deposit_comp_limit` (9e24132) and fourth-order term `deposit_comp_c2` (58dad8c).
- Metric at the particles by cubic spline `interp = bspline` (f219ade).
- Step limited by the expansion rate `dt_expansion` (372a62c).
- Diagnostics: mesh statistics in the history (proper volume, mean K, extrema),
  constraint statistics `cstat_dcycle` (55fdcf8, 010aace), conservation of the deposited
  matter on the mesh `cons_dcycle` (f219ade), line records `line_dcycle` (6e40fd3),
  energy-density field dumps at `field_time1..16` with `field_constraints` (581dc4a,
  fe715aa).
- Exact restart of periodic runs (particle restart formats 04 and 05; b670fb1, 372a62c;
  `cosmo/TESTLOG.md` lines 847-862).
- Outside the source tree (reference and initial-data tools, not simulation code):
  constraint solve on the torus `cosmo/ic/cosmo_id.py`, lattices, random fields, light
  rays, Newtonian particle-mesh reference `cosmo/newton/` [this reference predates
  decision 0010; whether it stays outside `athenak/src` is the orchestrator's call].

Production configuration for lattice starts: `cosmo/README.md` ("Options added to the
code for cosmology").

Evidence: `cosmo/TESTLOG.md` (C0 to C6, T1), `cosmo/paper/main.pdf`, regression F
(`core-20261115-032615-45e1779`: lapse 1.9e-7, density 1.1e-6, mean K 3.8e-7 relative
to the exact solution at a = 4; proper time 1.0e-7 at t = 2) and L
(`core-20261115-033408-bac7416`: 0.47 and 0.33 percent from linear theory to a_p = 30 at
amplitude 1e-4; `core-20261115-033410-bac7416` reproduces the earlier run to 5e-12 of
the contrast).

Known limitations.
- Noise after the matter streams cross; black-hole formation in an expanding box (E1);
  the split of the relativistic delay between initial data and evolution (cosmo/PLAN.md
  "State and revisions (2026-11-14 10:31)").
- The default displacement of `cosmo/ic/make_east.py` changed to the Newtonian one
  after the C1 result; with it the 32^3 linear-growth run is 0.6 to 1.0 percent below
  linear theory (regression L pass 1, `core-20261115-032617-45e1779`), against 0.45
  percent with the relativistic displacement of C1. Not a code defect; noted so that
  the C1 number is quoted with its construction.
- Not covered by this package's regression: the B-spline clouds, the compensation
  passes, the spline interpolation and the alternative lapse conditions (the
  production configuration); they rest on the cosmology test log only.
