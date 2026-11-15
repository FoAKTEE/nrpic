# Interface: deposition of the particle sources (proposal for `coord/INTERFACES/deposit.md`)

Status: PROPOSAL (core, 2026-11-15), written from the code at commit b7b431d
(`athenak/src/particles/nrpic.cpp`, `nrpic_mesh.hpp`, `z4c/tmunu.hpp`,
`z4c/z4c_calcrhs.cpp`). Line numbers refer to those files at that commit. Every option is
read in the `<particles>` block. Tests: entries of `docs/TESTLOG.md` (DT) and
`cosmo/TESTLOG.md` (CT) by their titles, and test D1 of this package (`JOURNAL.md`, run
`core-20261115-112600-b7b431d`).

## 1. What is handed to the spacetime solver

Ten fields per cell, the matter seen by the normal observers of the slice, in the
container `Tmunu::u_tmunu` with the index order (`z4c/tmunu.hpp` lines 28-31)

    Sxx Sxy Sxz Syy Syz Szz  E  Sx Sy Sz

    E    = n^a n^b T_ab        = sum_p m_p W_p          w_p(x) / sqrt(gamma)
    S_i  = -gamma_i^a n^b T_ab = sum_p m_p u_(i,p)      w_p(x) / sqrt(gamma)
    S_ij = gamma_i^a gamma_j^b T_ab = sum_p m_p u_(i,p) u_(j,p)/W_p w_p(x) / sqrt(gamma)

with m_p the rest mass, u_i the covariant spatial components of the four-velocity per
unit rest mass, `W = sqrt(1 + gamma^ij u_i u_j)` (`nrpic.cpp` lines 735-745), and w_p the
cloud of the particle per unit coordinate volume (section 2). Same definitions as the
paper (main.tex L619-624, L664-669).

- **Centring.** Cell centres of the active cells of every MeshBlock; ghost cells hold
  no deposit (they are filled by exchange before each filter pass).
- **Time level.** The deposit after the push from t^n to t^n+1 uses the particle state
  at t^n+1 and the metric at t^n+1 (`met1`, filled from the ADM variables at the start
  of the push, lines 372-378). These sources drive the spacetime step from t^n+1 to
  t^n+2 and are held fixed through its Runge-Kutta stages, unless the density form of
  section 5 is on.
- **Lorentz factor.** W is formed with the metric reconstructed at the particle
  (same interpolation as the pusher, `interp`, in the particle's own MeshBlock,
  lines 722-733).
- **Volume element.** `sqrt(gamma)` of the receiving cell centre at t^n+1
  (lines 936-950). Where the determinant is not positive or not finite (a cell next to
  a moving puncture), the ten sources of that cell are set to zero, the cells are
  counted (`n_bad_det_total`) and the first 50 events are reported on standard output
  with their centroid (lines 939-996).
- **Who carries sources.** Particles with `m > 0`. Null particles (`m = 0`) and light
  rays waiting for launch (`m < 0`) deposit nothing (line 720).
- **Constraints.** After every deposit the Hamiltonian and momentum constraints are
  recomputed with the new sources (lines 1350-1357), so constraint outputs at t^n+1 use
  the matter at t^n+1.
- **Ranks.** One MPI rank only (fatal error otherwise, lines 60-64).

## 2. Clouds

Order of operations in `NrpicDepositSources` (lines 654-998):

1. **Level of the cloud.** For particle p in a MeshBlock of level l0, the `nb^3` lattice
   points of its cloud at the spacing of l0 are located; `l_p` is the finest level of the
   MeshBlocks that contain them (the paper's rule, L738), capped by the level cap of
   section 3 (lines 747-809).
2. **Weights.** B-spline of degree 1, 2 or 3 per direction (`deposit_shape`), on the
   uniform lattice of level `l_p` whose cell centres are those of the mesh at that level,
   extended virtually into coarser MeshBlocks; weights sum to one (lines 810-841).
3. **Mapping to leaf cells.** A lattice cell maps to the leaf that contains it if that
   leaf is at level `l_p` or coarser (weight divided by the leaf's coordinate volume), or
   is spread uniformly over the 2^(3k) finer leaves inside it if the leaf is k levels
   finer (weight divided by the lattice cell's volume) (lines 849-891). Both branches
   keep the sum of weights over leaf cells equal to one.
4. **Optional compensation of the cloud** on the coordinate densities (section 4).
5. **Division by sqrt(gamma)** of the cell (section 1).
6. **Filter** (section 4), then the density form and the cosmological constant
   (section 5).

Periodic directions (periodic mesh boundary): the lattice points of a cloud are wrapped
into the domain (`WrapCoord`, lines 797-799, 845-847). Non-periodic outer boundary: the
part of a cloud outside the mesh is dropped (`mb < 0`, line 852), so the identity of
section 6 fails by that weight while a particle is within half a cloud of the boundary.

| Option | Default | Meaning | Tests |
|---|---|---|---|
| `deposit` | true if `metric = mesh` and a `<z4c>` block exists | deposit at all; `true` requires `metric = mesh` | every self-gravitating entry of DT and CT |
| `deposit_shape` | `cic` | `cic`, `tsc`, `pcs`: B-spline of degree 1, 2, 3 (2, 3, 4 cells per direction) | DT "Mesh path (CPU)", "Deposition on refined meshes" (cic); CT "T1a: sampling error of a compressed lattice against the cloud shape", "T1a: cloud-shape study, outcome", "C5/T1: the constraint field, and a wrong inference of mine corrected" (tsc, pcs) |

## 3. Level cap (coarser clouds than the local mesh)

| Option | Default | Meaning | Tests |
|---|---|---|---|
| `deposit_max_level` | 31 (no cap) | finest level (relative to the root) on which a cloud is represented; where the mesh is finer the density of a lattice cell is spread over the finer leaves | DT "Deposition on refined meshes" (caps 1 and 0, identity to 16 digits), "Dust collapse: cloud at the finest level against adaptive cloud level" |
| `deposit_adaptive` | false | per particle cap: the finest level, between `deposit_min_level` and `deposit_max_level`, whose cells hold at least `deposit_ppc` particles at the coordinate density `sqrt(gamma) E` of the previous deposit; the first deposit on a new mesh uses `deposit_min_level`, and a second deposit is made at start-up and after every regrid (lines 1377-1385) | DT "Density-adaptive cloud level on GPU: conservation", "Dust collapse: cloud at the finest level against adaptive cloud level" |
| `deposit_min_level` | 0 | coarsest level of the adaptive cap | as above |
| `deposit_ppc` | 2.0 | target particles per cloud cell of the adaptive cap | as above |
| `deposit_max_coarsen` | 31 (no limit) | a cloud is at most this many levels coarser than its particle's MeshBlock | DT "Dust collapse: cloud coarsening limited to one level" |

Finding that limits their use [VERIFIED, DT entries above]: near a forming black hole any
coarsening raised the constraint violation and made the horizon mass drift (-1.1 % to
+0.65 % after the matter was removed); collapse runs use the published rule (no cap).
The cap is for diffuse matter on a mesh refined for other reasons.

## 4. Smoothing and compensation

Two independent passes exist; both are three-point (or five-point) stencils per
direction applied to all ten components.

**Source filter** (after the division by sqrt(gamma); `NrpicFilterSources`, lines
1144-1197): `nfilter` binomial passes (1/4, 1/2, 1/4)^3, then, if `filter_compensate`,
one pass (-c, 1 + 2c, -c)^3 with `c = filter_comp_c` or `nfilter/4` if negative.
Response per direction `cos^(2n)(k dx/2)`, and `(1 - s)^n (1 + n s)` with the
compensation, `s = sin^2(k dx/2)`. Before every pass the ghost cells are filled: copy
at equal level, restriction and prolongation across levels (lines 1026-1037). The filter
conserves the volume integrals on a single level with uniform `sqrt(gamma)`; across
refinement levels it does not (DT "Test-particle clusters in Schwarzschild and Kerr":
changes of 9e-4 to 7.3e-3 of the integrals once particles cross levels). The history
records the integrals before (columns 9-12) and after (24-27) the filter.

**Compensation of the cloud** (before the division, on the coordinate densities;
lines 897-914, 1059-1137): one pass `u - c d2 u + (c2/16) d4 u` per direction, response
`1 + 4 c s + c2 s^2`. With `c = p/12` and `c2` = 8/45, 37/120, 7/15 for the linear,
quadratic, cubic cloud (p = 2, 3, 4) the deposited density of a long wave is right to
sixth order in dx. It acts before the division because the particles carry
`rho sqrt(gamma)`, and a pass after the division leaves the smoothed part of
`sqrt(gamma)` in the source (CT "T1: the compensation must act on the density, not on
the source"). With `deposit_comp_limit = L > 0` (or `c2 != 0`) the pass is applied in
flux form; each face flux is scaled so that the flux of E is at most L times the smaller
neighbouring E (E stays positive for L <= 1/6); the sums are conserved.

| Option | Default | Meaning | Tests |
|---|---|---|---|
| `nfilter` | 1 | binomial passes after the division | DT "Stable cluster controls" (0, 2, 4 passes) and its addendum in "Compensated filter (source)"; CT "C1" (momentum-constraint residual at the Nyquist number without filter) |
| `filter_compensate` | false | one compensation pass after the binomial passes | DT "Compensated filter (source, 2026-11-13)" (single particle: second moment 2.0000 to 0.0000 cells^2, negative lobes 5 to 10 %), "Compensated filter on the stable cluster: result (06:19)" |
| `filter_comp_c` | -1 (means `nfilter/4`) | c of that pass | as above |
| `deposit_comp_c` | 0 (off) | c of the cloud compensation (1/12, 1/8, 1/6) | CT "T1: the compensation must act on the density, not on the source", "C5, test C: exact box and compensation, first outcomes" |
| `deposit_comp_c2` | 0 | fourth-order term (8/45, 37/120, 7/15) | CT "T1: fourth-order compensation", "T1: spline interpolation, outcome at 32 cells; the fourth-order pass reinstated" |
| `deposit_comp_limit` | 0 (off) | limiter of the flux form | CT "T1: limited compensation", "T1/C5: outcomes of the limiter, ..." (safeguard for positivity, no change of the noise) |

Settings in use: lattice dust collapse one plain pass; test-particle clusters two;
prolate and self-gravitating clusters four with compensation (`paper/sections/method.tex`
line 151); cosmology production `deposit_shape = pcs`, `nfilter = 0`,
`deposit_comp_c = 1/6`, `deposit_comp_c2 = 7/15` (`cosmo/README.md` lines 42-47).

## 5. Density form, extrapolation, cosmological constant

| Option | Default | Meaning | Tests |
|---|---|---|---|
| `source_density` | false | the spacetime solver receives `D = sqrt(gamma) x` (filtered sources) in `u_tmunu_step` and multiplies by `chi^(-6/chi_psi_power)` = 1/sqrt(gamma) of each Runge-Kutta stage (`z4c_calcrhs.cpp` lines 481-491); removes the first-order error of sources held fixed while the volume element changes at the expansion rate. `u_tmunu` keeps the sources of the deposit for constraints and outputs | CT "C0, first test: homogeneous dust universe" (lapse 8 % low at a = 4 without it; 1.9e-7 with it) |
| `source_extrap` | false | D extrapolated to the middle of the coming step from the last two deposits, `D + (dt_next/(2 dt)) (D - D_prev)` (lines 1229-1249); not available on the first step after start or regrid; saved in the restart file | CT "C0" and "Restart of periodic runs" |
| `lambda` | 0 | cosmological constant as vacuum energy: `E += Lambda/(8 pi)`, `S_ij -= Lambda gamma_ij/(8 pi)` in `u_tmunu`; with `source_density` the solver adds it itself (`lambda8pi`); acts only if `deposit = true` | CT "C6 preparation: homogeneous universe with a cosmological constant" |

## 6. Conservation identity and what breaks it

Before the filter, on any mesh,

    sum_C (E, S_i)_C sqrt(gamma_C) dV_C = sum_p m_p (W_p, u_(i,p))

to round-off; the code records both sides every history record (`.nrpic.hst` columns 5,
6-8 and 9-12). Measured: 1e-15 over 3000 cycles on a uniform mesh (DT "Mesh path"), to
the printed 16 digits across three levels on the card and 4e-13 on processors (DT
"Deposition on refined meshes"), 3.6e-15 in test D1. It fails, by design, for: weight
dropped at a non-periodic outer boundary (up to 7e-5 in DT "Test-particle clusters");
the filter across refinement levels (section 4); cells with a non-positive determinant
(section 1). `S_ij` is not recorded.

## 7. Proposed interface rules (JUDGEMENT)

1. Any new matter module (scalar field, collision products) adds to the same ten fields
   in `u_tmunu` before the filter, or supplies densities to `u_tmunu_step` when
   `source_density` is on; it must not write ghost cells.
2. The definitions of section 1 (covariant `u_i`, `sqrt(gamma)` of the receiving cell,
   time level t^n+1) are frozen for core-v0.1; a change is an interface change.
3. A conservative filter across levels (filtering each cloud before the leaf mapping,
   DT "Test-particle clusters") is a candidate for core-v0.2; until then tracks that
   need exact integrals on refined meshes use `nfilter = 0` or read columns 9-12.
