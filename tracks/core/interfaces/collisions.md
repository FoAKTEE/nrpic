# Monte Carlo collisions in the particle module: design, options, outputs

Status: PROPOSAL of core (branch `core/collisions`, 2026-11-15) for
`coord/INTERFACES/collisions.md`. Client: Track C (S3, brief lines 518-521 and 747-764).
Built on the random numbers of `tracks/core/interfaces/rng.md`. The specification of the
track (`track/C-sidm:tracks/C-sidm/collide/SPEC.md`, read at commit 4c76ca8) is followed
except where section 10 says otherwise. Evidence labels as in the brief; every number in
section 8 carries a run id (`tracks/core/runs/<run_id>/manifest.json`).

Sections 1 to 7 were written before any code (design). Sections 8 and 9 are filled from
the runs; the predictions are in `tracks/core/JOURNAL-coll.md`.

## 1. What the operator does

Once per step, after the push and after the particles have been handed to the MeshBlock
that contains them, the massive particles of every collision cell are paired at random.
A pair collides with the probability

    P = (N - 1) sigma_m M_max v_Mol alpha dt / (sqrt(gamma) dx dy dz)                (1)

(N particles in the cell, sigma_m the cross-section per unit mass, M_max the larger rest
mass of the two macroparticles, v_Mol the Moller speed of the pair, alpha and gamma the
lapse and the determinant of the spatial metric of the cell). A pair that collides is
scattered elastically and isotropically in its centre-of-momentum frame. Everything is
evaluated in the orthonormal frame of the normal observer of the cell. The number of
collisions per proper four-volume is n_a n_b sigma_tot sqrt(gamma_rel^2 - 1), a scalar
[BACKGROUND], so the operator is the Monte Carlo form of the invariant collision integral
of the Boltzmann equation with the Moller flux factor. Without the option `collisions`
nothing of this runs and no array is allocated.

Units: G = c = 1. sigma_m has the dimension length^2/mass, a length in code units. The
mass of the physical particle never enters: a macroparticle of rest mass M stands for
M/m particles of cross-section sigma_m m.

## 2. Options (block `<particles>`; all absent or `collisions = false`: no effect)

| Option | Default | Meaning |
|---|---|---|
| `collisions` | false | switches the operator on |
| `coll_sigma` | 0 | sigma_m, cross-section per unit mass (code units) |
| `coll_sigma_model` | `constant` | `constant`, or `cutoff`: sigma_m / (1 + (v_rel/w)^2)^2 with the relative speed v_rel of the pair (the hook for a velocity dependence, section 3.4) |
| `coll_sigma_w` | 1 | w of the model `cutoff` |
| `coll_pmax` | 0.1 | largest pair probability per sub-step aimed at |
| `coll_subcycle` | `measured` | `measured`: sub-steps from the largest probability of the first pairing of the cell; `conservative`: from the bound v_Mol < 2 |
| `coll_nsub_max` | 1000 | largest number of sub-steps of a cell in one step |
| `coll_cell_factor` | 1 | f = 1, 2 or 4: a collision cell is a block of f^3 mesh cells |
| `coll_weights` | `equal` | `equal`: all colliding macroparticles must have the same rest mass (fatal error otherwise); `nanbu`: unequal masses, section 3.6 |
| `coll_hist_dcycle` | 1 | cycles between records of `<basename>.coll.hst` (0: none) |
| `coll_dump_cycle` | -1 | cycle whose collision step is dumped (before and after) for the replay test |
| `<job> rng_seed` | 0 | seed of the run (`rng.md`) |

## 3. Algorithm

### 3.1 Which particles, which cell

A particle takes part if its rest mass is positive (null particles and light rays never
collide), it has not been flagged for removal, and it lies inside the mesh. Its MeshBlock
is the leaf block that contains its position (wrapped into the mesh in periodic
directions); for the mesh metric this is the block it was assigned to after the push, for
the analytic metrics, which never assign blocks, the operator looks it up and changes
nothing in the particle.

The mesh cell is identified by its global index on the refinement level of that block,
(l; I, J, K). It is found from the position and from the geometry of the whole mesh
only: I = floor((x - x_min)/(x_max - x_min) N_l), then corrected by at most one so that
face(I) <= x < face(I+1) with the face positions of the mesh on that level, computed with
the formula the mesh uses for the edges of its blocks. The index therefore does not
depend on the division of the mesh into MeshBlocks, and it agrees with block ownership at
block edges.

Collision cell: the mesh cell (f = 1), or the block of f^3 mesh cells with indices
(I/f, J/f, K/f) (f = 2, 4; the cells of a MeshBlock per direction must be a multiple of
f, so a collision cell never straddles two blocks).

Refinement boundaries: each particle collides only with particles of its own collision
cell, which lies inside one leaf MeshBlock on one level. No pair straddles a block or a
level. On the two sides of a refinement boundary the collision cells differ in size; the
probability (1) uses the volume and the occupation of each cell, so the expected rate is
the same function of the local density on both sides, and what changes is the distance
over which partners are found (the cell size, section 3.8). After a change of the mesh
(adaptive refinement) the cells are those of the new mesh; nothing is stored.

### 3.2 Frame

Metric of the collision cell: alpha and gamma_ij at the cell centre at t^{n+1}, the time
level the pushed particles belong to. Mesh metric: the cell-centred values the pusher
reads (`met1`), for f > 1 their mean over the f^3 cells. Analytic metric: the functor at
the centre of the collision cell. The shift does not enter: the frame is that of the
normal observer.

Triad: the same construction as in the spacetime Boris pusher (`nrpic::BuildTriad`,
`nrpic_kernels.hpp`, in the gauge chosen by `<particles> triad`): S with S S^T = gamma,
coframe e^(m)_j = S[j][m], frame vectors e^j_(m) = Si[m][j]. Triad components of the
covariant momentum per unit rest mass: u_(m) = Si[m][j] u_j; back: u_j = S[j][m] u_(m).
The energy per unit rest mass seen by the normal observer is W = sqrt(1 + u_(m) u_(m)).
One triad serves all particles of the cell. A cell whose metric is not usable
(determinant or lapse not positive or not finite) is skipped and counted.

Proper volume of the cell V = sqrt(gamma) dx dy dz (f^3 mesh cells), proper time of the
step d tau = alpha dt.

### 3.3 Pairing

Per cell and per sub-step s: every particle gets the 64-bit word `Bits` of the key
(seed, Stream(collisions, 0), tag, cycle) with draw s. The particles of the cell are
sorted by (word, tag). Positions (0,1), (2,3), ... of the sorted list are the pairs. If
N is odd, the first three particles form the pairs (0,1), (1,2), (2,0), each tested with
half the probability (1), in this order and with the momenta as left by the previous
pair; the rest are paired from position 3. Each particle is thus tested against one
partner drawn uniformly from the other N - 1 (two partners at half weight in the triple),
and the factor N - 1 in (1) restores the rate sum_j M_j sigma_m v_Mol / V summed over all
partners [BACKGROUND: random pairing of Takizuka & Abe 1977 and Nanbu 1997, not
re-read; as specified by the track].

### 3.4 Probability, cross-section, acceptance

For a tested pair: gamma_rel - 1 from the triad components without cancellation
(section 3.5), v_Mol = sqrt((gamma_rel - 1)(gamma_rel + 1))/(W_a W_b), and
P_sub = P/n_sub (halved in the triple). The pair collides if U < P_sub with U the first
uniform deviate of the key (seed, Stream(collisions, 1), smaller tag, cycle, larger tag),
draw s. A probability above one is counted (`n_trunc`) and treated as one.

Cross-section: `nrpic::CollSigma(model, sigma, w, gamma_rel - 1)` in
`nrpic_collide.hpp` is the only place where sigma_m is evaluated. It receives the
invariant gamma_rel - 1 of the pair, from which the relative speed
v_rel = sqrt((gamma_rel - 1)(gamma_rel + 1))/gamma_rel follows; `constant` returns
sigma, `cutoff` returns sigma/(1 + (v_rel/w)^2)^2. A new velocity dependence is one more
branch there (and one more name in `NrpicCollideInit`); the scattering stays isotropic.

### 3.5 Scattering of one pair

In the triad frame, with unit physical masses: P = u_a + u_b, E = W_a + W_b,
s = E^2 - |P|^2 = 4 + 2 g1 with g1 = gamma_rel - 1, |p*| = sqrt(g1/2), E* = sqrt(s)/2.
g1 is computed as in the track's specification (section 3 there): with D = u_a - u_b,
S = u_a + u_b, e = S/|S|, r = (D.e)^2/(W_a + W_b)^2: g1 = (|D x e|^2 + 4 r)/(2 (1 - r))
for r <= 1/2, otherwise g1 = S_h^2/(sqrt(1 + S_h^2) + 1) + a b (1 - cos psi) with
a = |u_a|, b = |u_b|, S_h = (a - b)(a + b)/(a W_b + b W_a). New direction: the unit
vector nhat of `rng::Direction` for the key (seed, Stream(collisions, 2), smaller tag,
cycle, larger tag), draw s, in the axes of the centre-of-momentum frame reached from the
cell frame by the boost without rotation. Then

    u_a' = |p*| nhat + P [ |p*| (nhat . P) / (sqrt(s) (E + sqrt(s))) + 1/2 ],
    u_b' = P - u_a'.

The particle with the smaller tag is "a". The triad components are transformed back with
the triad of the cell.

### 3.6 Unequal rest masses of macroparticles

Statement [JUDGEMENT; the track's argument, checked here]: an update of the two members
of a pair that conserves the four-momentum of the pair exactly and keeps both on the mass
shell is a rotation of the relative momentum in the centre-of-momentum frame of the two
macroparticles taken as bodies of mass M_a and M_b. Its equilibrium is equipartition per
macroparticle, f ~ exp(-M W/T): heavy macroparticles would be colder per unit mass. All
physical particles have the same mass and must share one distribution, so such a scheme
is biased. The only exact alternative, splitting the heavier macroparticle, changes the
number of particles and is not done here.

Scheme (`coll_weights = nanbu`; Nanbu & Yonemura 1998 [BACKGROUND, not re-read]): the
pair collides with the probability (1) with M_max; the scattering of section 3.5 is that
of two physical particles; the lighter macroparticle always takes its new momentum, the
heavier one takes it with probability M_min/M_max (second uniform deviate of the
acceptance key). Then every macroparticle changes its momentum at the rate
sum_j M_j sigma_m v_Mol / V of its physical particles, whatever its own mass, and each
change is a physical two-body scattering: no bias in the rate or in the equilibrium.

Conservation: the rest mass of every macroparticle is unchanged and the mass shell is
exact. For a pair of equal masses the four-momentum of the pair is conserved to rounding.
For unequal masses it is conserved in expectation only: per event the pair's momentum
changes by (M_max - M_min) Delta u_heavy (heavy member updated) or M_min Delta u_light
(not updated), with mean zero. The code sums these changes and writes them to the history
(columns dE, dP). With `coll_weights = equal` a difference of the masses of the colliding
particles above 1e-12 relative is a fatal error.

### 3.7 Limit on the probability, sub-cycling

The global step is not changed. Per cell: n_sub = ceil(P_bound/`coll_pmax`), at most
`coll_nsub_max`. `measured`: P_bound is the largest P of the tested pairs of the first
pairing (s = 0), evaluated with the momenta at the start of the step. `conservative`:
P_bound = (N - 1) sigma_m M_cell 2 alpha dt/V with the largest mass of the cell and the
bound v_Mol < 2 (and the bound sigma of the model). Every sub-step pairs anew (draw s)
and uses P/n_sub. n_sub is a function of the particles of the cell alone. The expected
number of collisions is the same for any n_sub as long as no probability exceeds one;
`coll_pmax` controls the error from a particle colliding at most once per sub-step.

### 3.8 What the user must resolve

Partners are found within one collision cell: its proper size should be below the mean
free path (the operator reports the largest ratio, column `max_dx_mfp`), and a collision
cell should hold many particles in collisional regions (columns `min_N`, `mean_N`).
Neither is enforced.

### 3.9 Order of evaluation and reproducibility

The state after the collision step is a function of the particle states before it, the
metric of the cells, the cycle number and the seed. Nothing depends on the MeshBlock
division, the storage order of the particles or the order in which a card visits the
cells: cells are identified by global indices; the order inside a cell is the sorted
order of (random word, tag); the keys of all draws hold tags, the cycle and the sub-step;
a cell is processed by one thread from start to end and no data are shared between
cells; sums over cells go only into the history. Restart: the operator has no state. The
cycle counter and the seed are restored by the mesh restart file.

### 3.10 Place in the step

    save metric -> (spacetime) -> push -> excise and assign blocks -> COLLIDE -> deposit
    -> diagnostics

The collision step sees positions, momenta and metric at t^{n+1}; the deposited sources
contain the scattered momenta. The splitting of streaming and collisions is of first
order in the step [JUDGEMENT]. The key uses the number of the step being taken
(`pmesh->ncycle`).

## 4. Random-number keys (stream 2 of the registry in `rng.md`)

| Use | Stream | entity, entity_hi | step | draw | Call |
|---|---|---|---|---|---|
| pairing word of a particle | Stream(2, 0) | tag, 0 | cycle | sub-step | `Bits` |
| acceptance of a pair | Stream(2, 1) | smaller tag, larger tag | cycle | sub-step | `Uniform4`: u[0] acceptance, u[1] update of the heavier member (`nanbu`) |
| direction | Stream(2, 2) | smaller tag, larger tag | cycle | sub-step | `Direction` |

## 5. Outputs

`<basename>.coll.hst`, one record per `coll_hist_dcycle` cycles; a record describes the
collision step of that cycle only (no running sums, so that a restarted run writes the
same records). A new run starts the file, a restart appends. Columns:

| # | Name | Meaning |
|---|---|---|
| 1, 2 | time, cycle | time after the step, number of completed steps |
| 3 | n_part | particles that have a collision cell |
| 4 | n_cells | collision cells with at least two particles |
| 5 | n_tested | pairs tested (all sub-steps) |
| 6 | sum_P | sum of the probabilities of the tested pairs: expected number of collisions given the configuration |
| 7 | n_coll | collisions |
| 8 | n_updated | momentum updates (2 per collision; fewer with `nanbu`) |
| 9 | n_trunc | tested pairs with probability above one |
| 10 | max_P | largest probability of a tested pair in a sub-step |
| 11, 12 | max_nsub, mean_nsub | sub-steps per cell (cells with at least two particles) |
| 13, 14 | min_N, mean_N | particles per collision cell (cells with at least one) |
| 15 | max_dx_mfp | largest V^(1/3) N M sigma_m / V over the cells (cell size over mean free path, constant sigma) |
| 16 | sum_MW | sum of M W over the colliding particles after the step (cell frames) |
| 17-19 | sum_Mu1..3 | sum of M u_i (covariant, coordinate basis) after the step |
| 20 | dE | sum over the collided pairs of the change of M_a W_a + M_b W_b |
| 21-23 | dP1..3 | the same for M_a u_a + M_b u_b (triad components summed as numbers: a measure of the defect, not a vector) |
| 24 | abs_dE | sum over the collided pairs of the absolute change of the pair energy |
| 25 | abs_dP | sum over the collided pairs of the largest absolute change of a triad component of the pair momentum |
| 26 | n_bad_cells | occupied cells skipped because of an unusable metric |
| 27 | sum_W | sum_P without the Moller speed and with the sigma_m of the input: sum over the tested pairs of (N - 1) sigma_m M_max alpha dt/(n_sub V) (half in a triple). sum_P/sum_W is the mean of (sigma/sigma_m) v_Mol over the tested pairs; sum_W = sum over the cells of N (N - 1) sigma_m M alpha dt/(2 V) for equal masses |

`<basename>.coll_dump.<cycle>.bin` (`coll_dump_cycle`): 8 bytes "NRPCOLD1", int64 N,
int64 cycle, int64 f, doubles dt, sigma_m, w, pmax, int64 model, weights, subcycle,
nsub_max, uint64 seed, int64 triad gauge; then N records of doubles x^i (3), u_i before
(3), u_i after (3), M, alpha and gamma_xx, xy, xz, yy, yz, zz of the collision cell (7),
proper volume of the cell (1); then N records of int32 tag, level, cell index I/f, J/f,
K/f, n_sub of the cell, number of momentum updates of the particle. Particles without a
collision cell have level -1.

## 6. Where it is

| File | Content |
|---|---|
| `athenak/src/particles/nrpic_collide.hpp` | kernels without dependence on AthenaK (`-DNRPIC_STANDALONE`): gamma_rel - 1, Moller speed, cross-section, scattering, cell index, in-place sort |
| `athenak/src/particles/nrpic_collide.cpp` | `Particles::NrpicCollideInit`, `NrpicCollide` (task), history and dump |
| `python/nrpic/collide.py` | the Python twin: the same step on NumPy arrays (replay of a dump), Maxwell-Juttner reference functions |
| `problems/tests/coll_box.athinput` | periodic Minkowski box |
| `tracks/core/analysis/collisions/` | drivers and analysis of all tests |

Shared files touched (hooks only): `particles.hpp` (struct `NrpicCollideOptions`, one
task id, members and three method declarations), `particles_tasks.cpp` (the task between
excise and deposit when the option is on), `nrpic.cpp` (one call of `NrpicCollideInit`
at the end of `NrpicInit`), `athenak/src/CMakeLists.txt` (one source file). Line numbers:
section 9.

## 7. Conservation properties (by construction)

| Quantity | `equal` | `nanbu` with unequal masses |
|---|---|---|
| rest mass of every macroparticle | unchanged (bit) | unchanged (bit) |
| mass shell | exact (W is computed from u) | exact |
| pair momentum M (u_a + u_b), triad and covariant components | rounding: u_b' = P - u_a' | in expectation |
| pair energy M (W_a + W_b) in the cell frame | rounding (a few units in the last place of the pair energy) | in expectation |
| momentum and energy of particles that do not collide | unchanged (bit): only accepted pairs are written | the same |
| sum of M W with the metric interpolated to each particle (history `sum_mW`, deposited E) | not exact: a collision changes it by O(Delta u x cell size x gradient of the metric), random sign [JUDGEMENT] | the same |

## 8. What is verified

(filled from the runs; see the end of this file)

## 9. Limits, open points, lines touched in shared files

(filled at the end)

## 10. Differences from the track's specification (SPEC.md at 4c76ca8)

- Cell index from the global geometry with a face correction (3.1) instead of the cell
  of the owning block: needed for an exactly layout-independent result.
- Triad in the gauge of the Boris pusher (`triad` option, default symmetric) instead of
  always Cholesky. With `triad = cholesky` it is the track's frame. The physics is the
  same; the random direction is referred to other axes.
- History records are per step, not accumulated (restart), and the columns are those of
  section 5. `coll_hist_dcycle` instead of `hist_dcycle`.
- `coll_weights = equal` checks all colliding particles of the mesh, not cell by cell.
- Added: `coll_sigma_model`, `coll_sigma_w`.
