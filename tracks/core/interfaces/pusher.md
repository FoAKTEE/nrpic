# Interface: particle state and geodesic pushers (proposal for `coord/INTERFACES/pusher.md`)

Status: PROPOSAL (core, 2026-11-15), written from the code at commit b7b431d
(`athenak/src/particles/nrpic.cpp`, `nrpic_kernels.hpp`, `nrpic_mesh.hpp`,
`nrpic_metrics.hpp`, `particles.{hpp,cpp}`, `particles_tasks.cpp`, `mesh/mesh.cpp`).
Options are read in `<particles>`. Tests: `docs/TESTLOG.md` (DT) and `cosmo/TESTLOG.md`
(CT) entries by title; test D1 of this package.

## 1. Particle state

Arrays `prtcl_rdata(n, p)` and `prtcl_idata(n, p)` (`particles.hpp` lines 30-36):

| Index | Content |
|---|---|
| `IPX, IPY, IPZ` | coordinates x^i in the coordinates of the run (Cartesian on the mesh) |
| `IPVX, IPVY, IPVZ` | covariant spatial components u_i of the four-velocity per unit rest mass |
| `IPM` (6) | rest mass m > 0; m = 0 a null particle; m = -t_e < 0 a light ray launched at t = t_e |
| `IPTAU` (7) | proper time along the worldline (affine parameter for null particles) |
| `PGID` | global id of the owning MeshBlock; -1 left the mesh, -2 excised (removed in the same step) |
| `PTAG` | tag = position in the particle file (or inline list); unchanged for the whole run |
| `PSP` (2) | species, from the particle file |

Particles are never split, merged or given new masses, also through regrids and
restarts (`NrpicInitializeSources`, called after every regrid from
`mesh/mesh_refinement.cpp` lines 188-189).

## 2. Equations and time levels

Coordinate-time characteristics (`nrpic_kernels.hpp` lines 351-356; paper L410-417):

    dx^i/dt = alpha gamma^ij u_j / W - beta^i
    du_i/dt = -W d_i alpha + u_j d_i beta^j - (alpha/2W) u_j u_k d_i gamma^jk

One cycle (tasks, `particles_tasks.cpp` lines 31-44): `NrpicSaveMetric` makes the metric
of the previous cycle the old level `met0` (t^n); Z4c advances; `NrpicPush` copies the
new ADM metric into `met1` (t^n+1) and pushes; `NrpicExcise` reassigns and removes;
`NrpicDeposit`; `NrpicDiagnostics`. Without `<z4c>` (fixed metric) one level serves as
both.

Global step: `dt = min(cfl_number x min_blocks(dx), <particles> dt, expansion limit)`
(`mesh/mesh.cpp` lines 639-649; `z4c/z4c_newdt.cpp`); particles and fields share it, and
it halves whenever a finer level appears. The expansion limit is in `cosmo_gauge.md`.

## 3. The two pushers

Both are implicit, store `(x^i, u_i)` at integer time levels, start from an explicit
Euler guess in position with the old-level fields and the old momentum, and iterate the
six endpoint values by fixed-point iteration until the largest change of any component
(coordinates and momenta mixed, in code units) is below `tolerance`. If `max_iterations`
is reached the last iterate is kept and the push is counted as unconverged (history
columns 21-22); the particle is not removed.

| Option | Default | Meaning |
|---|---|---|
| `pusher` | (required) | `midpoint` or `boris` (`particles.cpp` lines 63-75) |
| `tolerance` | 1.0e-7 | convergence threshold (the paper's production value, L459) |
| `max_iterations` | 50 | iteration limit |
| `triad` | `symmetric` | tetrad gauge of the Boris pusher: `symmetric` (positive square root of gamma) or `cholesky` (lower-triangular factor, Gram-Schmidt in x, y, z order) |

**Midpoint** (`PushMidpoint`, lines 363-429): fields at the midpoint position from both
time levels, averaged; inverse metric from the averaged metric; returns
`dtau = dt alpha / W` of the last midpoint evaluation, added to `IPTAU`. A momentum
conjugate to a cyclic coordinate is conserved to round-off.

**Boris** (`PushBoris`, lines 458-598): tetrad momentum `u_(m) = e^i_(m) u_i` at
(t^n, x^n); midpoint fields averaged between the levels, `d_t gamma = (gamma^n+1 -
gamma^n)/dt`; gravito-electric and gravito-magnetic fields contracted with the mean
tetrad momentum; kick, rotate, kick with `dt_hat = alpha dt`; position from the same
midpoint state; back-conversion with the triad at (t^n+1, x^n+1). It does not return a
proper time (`IPTAU` is not advanced) and does not support null particles: with
`pusher = boris` every particle is pushed as massive [VERIFIED from `nrpic.cpp` lines
492-498; not tested].

**Null particles and light rays** (midpoint only; lines 448-481): `m = 0` follows a null
geodesic (`W = sqrt(gamma^ij u_i u_j)`). `m = -t_e` waits until the step nearest t_e;
until then its momentum slots hold a coordinate direction c^i, replaced at launch by
`k_i = gamma_ij c^j / sqrt(gamma_kl c^k c^l)` (unit frequency for the normal observer).

## 4. Metric at the particle

| Option | Default | Meaning |
|---|---|---|
| `metric` | `mesh` | `mesh` (ADM fields of the run), or analytic Kerr: `kerr_schild` (Cartesian), `kerr_schild_sph`, `boyer_lindquist`, or `lattice` (Cartesian Kerr-Schild sampled on a virtual uniform lattice and reconstructed like mesh data) |
| `bh_mass`, `bh_spin` | 1.0, 0.0 | M and a of the analytic metrics (also used by `nrpic_geodesic` to fill the mesh) |
| `lattice_dx` | 0.025 | spacing of the virtual lattice |
| `interp` | `hermite` | `hermite`: tensor-product cubic Hermite (Catmull-Rom) weights of the paper (L586-604); `bspline`: cubic spline through the nodal values (B-spline weights on values sharpened to second order, needs `nghost >= 4`) |

Mesh reconstruction (`nrpic_mesh.hpp` lines 73-157): alpha, beta^i and the six
gamma_ij (covariant) at cell centres including ghost cells, 4^3 stencil in the
particle's own MeshBlock; the stencil index is clamped to the allocated cells, which
turns the reconstruction into an extrapolation of the same cubic near the array edge;
first derivatives from the derivative of the same polynomial; the 3x3 inverse is taken
after interpolation. `metric = mesh` requires `nghost >= 2` and a `<z4c>` or `<adm>`
block. With `hermite` the gradient error depends on the position in the cell at second
order (low by (kh)^2/6 at cell centres, high by (kh)^2/12 midway); `bspline` removes
that dependence (CT "T1: conservation on the mesh, and the interpolation of the metric").

## 5. Removal and reassignment

| Option | Default | Meaning |
|---|---|---|
| `alpha_exc` | -1 (off) | before the push, a particle whose lapse interpolated at (t^n, x^n) is below this value is removed and not pushed (paper L678) |
| `ah_exc_factor` | -1 (off) | particles inside this fraction of the smallest coordinate radius of a found apparent horizon (at most four horizons) are removed; a horizon counts only after a successful search of the current run, and not if its radius exceeds four times the starting radius of the search (lines 399-424) |

Also removed: particles whose state is not finite after the push (lines 523-525), and
particles outside the mesh after the push (`NrpicAssignBlocks`, lines 545-566; periodic
directions wrap instead). Counts and rest masses of removed particles are in the history
(columns 17-20). Ownership is found by a search over all MeshBlocks of the pack, the
previous owner first (`FindBlock`, `nrpic_mesh.hpp` lines 26-45).

## 6. Tests that cover this interface

| Capability | Test |
|---|---|
| Both pushers, both gauges, analytic and lattice metric, published digits of the Kerr e = 0.99 passage | DT "Pusher kernels (standalone build ...)" |
| Mesh path, circular orbit, deposition identity | DT "Mesh path (CPU, 2026-11-13)" |
| Test particles in an evolved spacetime (single puncture, head-on collision) | DT "Test particles around an evolved puncture", "Test particles around a head-on collision of two black holes" |
| 10^2 to 10^4 test particles, invariants, removal at the lapse threshold against exact invariants | DT "Test-particle clusters in Schwarzschild and Kerr" |
| Horizon-based removal and its restart defect (corrected) | DT "Intervention: removing matter inside the horizon cures the failure", "M/128 chain failed at the same step; a defect of the horizon-based removal after restarts" |
| `interp = bspline` | CT "T1: conservation on the mesh, ...", "T1: spline interpolation, outcome at 32 cells ..." |
| Tolerance 1e-14 against 1e-12 in a cosmological run | CT "T1/C5: outcomes of the limiter, ..." (identical) |
| Null particles, light rays | CT "C3, first test: light rays in the homogeneous universe", "C3: luminosity distance along light rays, outcome" |
| Restart exactness of the particle state | DT "Restart (CPU)"; CT "Restart of periodic runs"; test D1 (bitwise) |

## 7. Proposed interface rules (JUDGEMENT)

1. The state of section 1 (covariant `u_i` per unit rest mass, rest mass in `IPM`) is
   frozen for core-v0.1. Extra per-particle data (collision counters, charges) go into
   new slots after `IPTAU`/`PSP`, which changes `NRPIC_NRDATA`/`NRPIC_NIDATA` and the
   restart format version.
2. A non-gravitational force (collisions of Track C, stochastic kicks) enters as a
   separate operator between the push and the deposit, acting on `u_i` with the metric
   at t^n+1, so that both pushers stay unchanged; the paper writes the
   electromagnetic force into the Boris step (L418-431, L522-529), which this code does
   not implement.
3. Production runs use `pusher = midpoint` (the paper's choice, L840); `boris` is kept
   for comparisons.
