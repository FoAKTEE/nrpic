# Monte Carlo collisions in the particle module: design, options, outputs

Status: accepted as the state of release core-v0.3 (decision 0011); sections 2, 4, 5, 7
and 9 amended and section 11 added on branch `core/collisions-2` (wave 2, 2026-11-15) as
a PROPOSAL for the next release: `<particles> coll_energy` (collisions with the metric at
each particle). First written on branch `core/collisions` for
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
| `coll_subcycle` | `measured` | `measured`: sub-steps from the two largest speeds of the cell; `conservative`: from the bound v_Mol < 2 |
| `coll_nsub_max` | 1000 | largest number of sub-steps of a cell in one step |
| `coll_cell_factor` | 1 | f = 1, 2 or 4: a collision cell is a block of f^3 mesh cells |
| `coll_weights` | `equal` | `equal`: all colliding macroparticles must have the same rest mass (fatal error otherwise); `nanbu`: unequal masses, section 3.6 |
| `coll_hist_dcycle` | 1 | cycles between records of `<basename>.coll.hst` (0: none) |
| `coll_dump_cycle` | -1 | cycle whose collision step is dumped (before and after) for the replay test |
| `coll_budget` | false | also evaluate the sum of M W with the metric at each particle before and after the collision step (history columns 30, 31; one metric reconstruction per particle and evaluation) |
| `coll_energy` | absent (= `cell`) | metric with which a pair conserves its energy (section 11). `cell`: the metric of the cell centre, as in core-v0.3 (exact only where the metric does not vary across a collision cell). `particle`: the pair conserves the sum of the covariant momenta u_i and the sum of the canonical energies alpha W - beta^i u_i, each with the metric at the particle; required for runs in a gravitational field that last many collision times. The option is read only if present; its presence (either value) adds history columns 32 to 36, takes the budget of `coll_budget` particle by particle, and writes dumps of version 2 |
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
`coll_nsub_max`, with P_bound = (N - 1) sigma_max M_cell v_bound alpha dt/V (largest
mass of the cell, largest value of the cross-section model). `measured`: v_bound =
min(v_1 + v_2, 2) with the two largest speeds of the particles of the cell in its frame,
which bounds every pair because v_Mol <= |v_a - v_b| <= |v_a| + |v_b|. `conservative`:
v_bound = 2. Every sub-step pairs anew (draw s) and uses P/n_sub.

n_sub is a function of the particles of the cell alone and not of a pairing. This
matters: the first version of the operator took P_bound from the largest probability of
the first pairing, as the track specified, and its collision rate was low by 0.1 percent
(mean Moller speed of the tested pairs, 1e6 particles, 30 per cell, n_sub about 3: run
core-20261115-132842-b33b7f3), because a first pairing with fast pairs was diluted by
more sub-steps than one with slow pairs. With a bound from the cell's particles the
expected number of collisions given the particles is the same for any n_sub, as long as
no probability exceeds one; `coll_pmax` controls the error from a particle colliding at
most once per sub-step. Speeds change during the sub-steps, so a probability can exceed
`coll_pmax` slightly in later sub-steps; `max_P` reports it.

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
| acceptance of a pair | Stream(2, 1) | smaller tag, larger tag | cycle | sub-step | `Uniform4`: u[0] acceptance, u[1] update of the heavier member (`nanbu`), u[2] detailed-balance acceptance (`coll_energy = particle`, section 11.3) |
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
| 28, 29 | sum_MW_species0, sum_M_species0 | sum of M W after the step and rest mass of the colliding particles of species 0 (energy exchange between two species) |
| 30, 31 | sum_MW_particles, dE_particles | with `coll_budget = true`: sum of M W over the colliding particles with the metric reconstructed at each particle (the energy of the history column `sum_mW` and of the deposit) after the collision step, and its change over the collision step; zero otherwise. With `coll_energy` present the change is summed particle by particle inside the cells (rounding of the changes, not of the sums) and both cover the particles of usable cells |
| 32, 33 | sum_MH_particles, dH_particles | only with `coll_energy` present, filled with `coll_budget = true`: sum of M (alpha W - beta^i u_i) with the metric at each particle after the collision step, and its change over the collision step (summed particle by particle) |
| 34 | n_noroot | only with `coll_energy` present: accepted pairs that were left unscattered because the energy equation of the pair had no admissible root (section 11.3) |
| 35 | max_dlam | largest \|lam - 1\| of the collisions of the step (lam = 1: the collision of the cell frame) |
| 36 | n_balance | collisions rejected by the detailed-balance acceptance (section 11.3) |

With `coll_energy = particle`, columns 20 and 24 (dE, abs_dE) refer to the canonical
energies: the change of M_a h_a + M_b h_b of the collided pairs, h = alpha (W - 1) -
beta^i u_i with the metric at each particle.

`<basename>.coll_dump.<cycle>.bin` (`coll_dump_cycle`): 8 bytes "NRPCOLD1", int64 N,
int64 cycle, int64 f, doubles dt, sigma_m, w, pmax, int64 model, weights, subcycle,
nsub_max, uint64 seed, int64 triad gauge; then N records of doubles x^i (3), u_i before
(3), u_i after (3), M, alpha and gamma_xx, xy, xz, yy, yz, zz of the collision cell (7),
proper volume of the cell (1); then N records of int32 tag, level, cell index I/f, J/f,
K/f, n_sub of the cell, number of momentum updates of the particle. Particles without a
collision cell have level -1. Version 2 (`coll_energy` present): magic "NRPCOLD2"; after
the triad gauge the header holds int64 energy mode (0 cell, 1 particle) and int64 flag
(1: the records hold the metric at the particles); each particle record has ten more
doubles: lapse, beta^x, beta^y, beta^z and the inverse spatial metric gamma^xx, ^xy,
^xz, ^yy, ^yz, ^zz at the particle (zero if the flag is 0). Reader of both versions:
`nrpic.collide.read_dump`.

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
| sum of M W with the metric interpolated to each particle (history `sum_mW`, deposited E) | not conserved: the two particles of a pair sit at different depths of the potential inside one cell, and a collision raises this sum on average (measured in the cluster: 1e-8 of the sum per collision for cells of 2 M; sections 8, 9). The design text said "random sign"; the runs showed a steady gain | the same |

This table is the operator of core-v0.3 (`coll_energy` absent or `cell`). What
`coll_energy = particle` conserves: section 11.4.

## 8. What is verified

Processor runs use the serial build, card runs one A100. "Box": periodic Minkowski box,
`problems/tests/coll_box.athinput`, problem generator `nrpic_geodesic` with the analytic
Kerr-Schild functor at `bh_mass = 0` (the fixed-metric path; the functor is exactly
flat). Drivers: `tracks/core/analysis/collisions/` (table at the end of this section).
Predictions and outcomes, including the failed ones: `tracks/core/JOURNAL-coll.md`.

| Statement | Evidence |
|---|---|
| Kernels: for the 208 equal-mass test vectors of the track (outputs from a 60-digit evaluation) the scattered momenta are within 2.6e-16 of max(1, \|u\|) (3.2e-16 with contraction), the pair energy within 1.32 eps and the pair momentum within 0.63 eps of the pair energy, the Moller speed within 1.04e-15; four compilations of the header and the Python twin | run core-20261115-132556-a7dc8ab; `fig_kernel_test.png` |
| One collision step of the code is reproduced by the Python twin written from this text, in seven cases (sub-cycling; cell factor 2; `conservative`; `cutoff`; `nanbu` with masses 1:4; homogeneous curved metric with the symmetric triad, and with the Cholesky triad and the Boris pusher): cell indices, n_sub and number of updates of each of 20000 particles, n_tested, n_coll, n_updated identical; sum_P to 2e-14; momenta to 8.9e-16 (flat) and 9.8e-15 (curved); particles without an update bit-identical | run core-20261115-134644-466dcfd; `fig_replay.png` |
| Option absent: every output file of five existing set-ups is byte-identical to the baseline built from 94dc093 (36 files, processor). On the card the two set-ups whose baseline is reproducible run to run are identical; in the other three exactly the files that differ between two runs of the baseline differ (2, 2, 3 files), the other 21 are identical | runs core-20261115-132618-1a050f3 (first source), core-20261115-140120-7a0efc0 (source of the test runs), core-20261115-140938-0f9d0cf (final source), core-20261115-135757-18d4555 (card) |
| Operator on with sigma = 0: snapshots byte-identical to the run without the option | runs core-20261115-133533-0ca5e3b, core-20261115-135816-18d4555 (card) |
| Pair counting, volume and time factor: sum_W equals sigma M dt/(2 V) sum N (N - 1) of the cell populations counted from the snapshot, to rounding (at most 5.4e-12 on the processor, where the bound of the sum is 1e-10; 4e-16 on the card), for 1.5 to 50000 particles per cell, with sub-cycling, with cell factors 2 and 4, and with lapse 0.7 and sqrt(det gamma) = 1.104 | runs core-20261115-133533-0ca5e3b, core-20261115-135219-42c8489, core-20261115-140259-8742cdf |
| Rate: the mean Moller speed of the tested pairs equals that of random pairs of the actual particles (\|z\| <= 1.7) and of a Maxwell-Juttner gas at the sample temperature to 7.7e-5, at theta = 0.01, 0.1, 1, 10, with and without sub-cycling (1e6 particles, 1.5e6 and 1.5e7 collisions per run); collisions = sum_P within 1.6 sigma; summed weight = (1/2) N rho_0 sigma dt per step within 6e-5 | run core-20261115-133533-0ca5e3b; card: core-20261115-135816-18d4555 (the same numbers of collisions, digit for digit); `fig_rate_history.png`, `fig_rate_summary.png` |
| Conservation, equal masses: the exactly rounded sums of M W over 1e6 particles before and after up to 1.5e7 collisions are equal to the last bit (one run of four in the relaxation test differs by one unit in the last place); every momentum component changes by less than 5e-19 of sum M \|u\|; mean pair defect 0.5 eps of the pair energy | runs core-20261115-133533-0ca5e3b, core-20261115-134036-5684674; `fig_rate_conservation.png` |
| Relaxation: monoenergetic shells (u0 = 0.3, 2) and two-temperature starts (0.03/0.01, 3/1) end as Maxwell-Juttner at the temperature of the conserved energy: KS p 0.26 to 0.90 (4e5 particles), <u^2/W>/3 = theta_eq within 0.06 sigma, both populations within 0.52 sigma | run core-20261115-134036-5684674; card: core-20261115-135932-18d4555; `fig_relax_distributions.png`, `fig_relax_temperatures.png` |
| Entropy: the estimate rises monotonically (largest decrease 2.4 sd/sqrt 2 of the estimator at fixed energy) by 2.63, 2.77, 0.048, 0.123 to s_MJ + bias within 1.4 sd; the gap falls four decades | the same runs; `fig_relax_entropy.png` |
| Time step: the decay rate of theta_1 - theta_2 is nu_inf + s dt_c with s = 0.716(59) (1e6 particles) and 0.744(32) (4e6, card) against the forward-Euler value nu_inf^2/2 = 0.69: first order in the collision sub-step. A step four times too large for a plain collision step (nu_0 dt = 0.4), sub-cycled, lies on the same line at dt/<n_sub> (z = -1.3, -1.5). Initial slope at dt -> 0: 1.000(4) and 0.995(4) of the non-relativistic closed form (track: 0.995 relativistically) | runs core-20261115-134511-0607ce8, core-20261115-140021-18d4555 (card); `fig_conv_dt.png` |
| Cell size, homogeneous gas: the number of collisions does not depend on the cell size (within 1e-3, 2^3 to 64^3 collision cells); blocks of f^3 cells give byte-identical states to the coarser mesh; the relaxation rate is 0.957(12), 0.951(6), 0.948(6) of nu_0 for 50000, 781, 98 particles per cell, 0.926(4) for 12 and 0.879(5) for 1.5 | run core-20261115-135219-42c8489; `fig_cells.png` |
| Reproducibility: with the analytic metric all snapshots are byte-identical for 1, 8, 64 MeshBlocks, for a box whose faces are not binary fractions with 1 and 27, and for a restart from the dump of cycle 37 (1e5 particles, 100 cycles, 5e5 collisions, sub-cycling active); another seed changes every particle. With the metric on the mesh a restart is byte-identical; two divisions are byte-identical in the first box and 5e-15 apart with identical collisions in the second (metric reconstruction of the pusher, `rng.md` section 9). The same on the card. Processor and card: same collisions, momenta 1.8e-15 apart | runs core-20261115-133737-82e2040, core-20261115-133912-f104754, core-20261115-140011-18d4555 (card); `fig_repro.png` |
| Unequal masses 1:4 with `nanbu`: both classes end at one temperature (difference 0.1 to 0.6 sigma) and Maxwell-Juttner (KS p 0.36 to 0.96); updates per collision 1.538 to 1.539 (20/13); light and heavy particles updated equally often; energy defect -0.0020(21) of the thermal energy after 25 collision times, scatter 0.4 percent (2e5 particles); the defects of the history equal the changes of the snapshots to 7e-15. `equal` refuses the same file with an error naming the masses | run core-20261115-140030-7a0efc0; `fig_unequal.png` |
| Curved frame: in the homogeneous metric (lapse 0.7, non-diagonal gamma_ij) on the mesh, with the symmetric triad and the midpoint pusher and with the Cholesky triad and the Boris pusher: pair counting exact with alpha/sqrt(gamma); 1993695 and 1992802 collisions against 1993138 in the flat box at the same rate per coordinate time; sum of M W (with gamma^ij) conserved to 1.0e-14, sum of M u_i to 5e-17 of its scale; energy with the metric at the particles changed by the collision steps by 1.2e-14 in total; relaxation to Maxwell-Juttner in the triad components (KS p 0.78, 0.92) | runs core-20261115-140259-8742cdf (card), core-20261115-140147-15c576d (processor: the same numbers of collisions); `fig_curved_box.png` |
| Relativistic cluster (monoenergetic, y_c = 0.819, 1e4 particles, Z4c with six refinement levels, collision cells of 4^3 mesh cells = 2 M, 150 M = 4.8 dynamical times). Operator on with sigma = 0: byte-identical to operator absent on the processor (2 steps); on the card as close to the baseline as the baseline to its own repeat (lapse 8e-15, positions 3e-13). Knudsen number 30: 470 collisions (sum_P 461.3), central lapse within 0.0024 and mass radii within 2.3 percent of the collisionless run at all times, no particle lost, rest mass identical to the bit, deposit identity 1e-15, pair energies in the cell frame to rounding. The collision steps raise the particle energy (metric at each particle) by 3.9e-6 of its value. Knudsen number 3 with collision cells of 2, 1 and 0.5 M: expected collisions 5037, 5219, 5269; energy gain per collision 1.05e-8, 2.3e-9, 1.1e-9 of the particle energy; final central lapse 0.7914, 0.7885, 0.7891 (collisionless 0.8114) | runs core-20261115-135728-18d4555 (processor), core-20261115-140316-8742cdf and core-20261115-142625-67f8c1d (card); `fig_cluster.png` |

Not verified: section 9.

Drivers (each writes `summary.json` with the field `ok` and its figures into the run
directory; run through `tracks/core/analysis/rng/runreg.py`):

| Driver | Test |
|---|---|
| `run_kernel_test.py`, `kernel_test.cpp` | kernels against the track's vectors |
| `run_replay.py` | one step against the Python twin |
| `run_rate.py` | rate, conservation, null runs |
| `run_relax.py` | relaxation, entropy |
| `run_conv_dt.py` | time step |
| `run_cells.py` | cell size, cell factor |
| `run_repro.py` | MeshBlock divisions, restart, seed |
| `run_unequal.py` | unequal masses |
| `run_curved_box.py` | homogeneous curved metric |
| `run_cluster.py` | relativistic cluster |
| `gpu_job.sh` | the card runs, by part |
| `make_box.py`, `common.py` | particle files of the box (draws from the initial-data stream of `rng.md`: entity = tag, step 0, sub-stream 0, draws 0-2 position, 3 speed, 4 direction) |

## 9. Limits, open points, lines touched in shared files

Limits and open points.

- The splitting of streaming and collisions is of first order in the step; the measured
  error of a relaxation rate is nu^2 dt_c/2 (section 8). Nothing of higher order is
  implemented.
- Particles per collision cell: the number of collisions is right at any occupation,
  but with few particles per cell that stay together the relaxation is too slow (2.6
  percent at 12 per cell, 7.5 percent at 1.5 in the test of section 8, in a box where a
  particle crosses a cell in about one collision time). About 100 per cell gave 1
  percent. `coll_cell_factor` trades this against the size of the cell. That repeated
  partners are the cause is [JUDGEMENT]; no control separated it from other effects of a
  small cell.
- Energy in a gravitational field. The collision conserves the pair energy measured
  with the metric of the cell centre. The energy measured with the metric at each
  particle, which is what the deposit hands to the spacetime, rises steadily: in the
  cluster of section 8 by 1.05e-8, 2.3e-9 and 1.1e-9 of its value per collision for
  collision cells of 2, 1 and 0.5 M (5e-5 of a pair's energy at 2 M), 5.2e-5 in total
  over 5000 collisions at Knudsen number 3. It falls with the cell size, by 0.22 from 2
  to 1 M (0.25 for second order) and by 0.10 from 2 to 0.5 M (0.063 for second order;
  my prediction of second order within 40 percent failed there, at 1.3 particles per
  occupied cell and with about 10 percent statistical error). Reading [JUDGEMENT]: the
  partners of a pair sit at different depths of the potential and the collision moves
  kinetic energy between them without the potential difference being paid. A run over
  many relaxation times accumulates this gain in proportion to the number of collisions
  (1e4 particles colliding 1e3 times each at 2 M cells: of order 5 percent of the rest
  mass), so such runs need small collision cells, hence many particles, or a correction
  that is not implemented (for example a rescaling of the pair's momenta to conserve
  the energy at the particles' own positions). This is the first thing to settle
  before science runs of track C. Settled in wave 2: cause and correction
  (`coll_energy = particle`) in section 11.
- Cell size and rate with a density gradient: in the same cluster the expected number
  of collisions rises by 3.6 percent from cells of 2 M to 1 M and by 1.0 percent from 1
  to 0.5 M (the square of the density averaged over a cell is below the average of the
  square).
- Heat conduction (the track's tests T6 to T8) was NOT tested: no run of this package
  measures a transport coefficient. The dependence of transport coefficients on the
  cell size is open.
- `nanbu` conserves energy and momentum only on average: the temperature of a gas of
  2e5 macroparticles with masses 1:4 random-walks by 0.4 percent in 25 collision times.
  Production runs should use equal masses.
- Sub-steps are bounded by the two largest speeds of the cell, which over-estimates the
  largest pair probability (mean n_sub 3.4 to 4.3 where the pairing-based rule had 3.0
  to 3.2). A probability can still exceed `coll_pmax` in later sub-steps (largest seen:
  0.113 for 0.1).
- The cross-section model `cutoff` is exercised by the replay test only (one step
  against the twin); its rate was not compared with a reference average.
- Adaptive refinement during a run, excision of colliding particles (cells with an
  unusable metric, `n_bad_cells`), removal of particles combined with collisions, the
  analytic metrics other than Cartesian Kerr-Schild, and more than one rank (the module
  runs on one) were not exercised. Static refinement was (one refined octant: cell
  assignment, pair counting on both levels, two MeshBlock divisions; run
  core-20261115-140539-54f8bee).
- With the metric on the mesh, two MeshBlock divisions give particle states that differ
  at rounding level unless the faces are binary fractions; this is the pusher's metric
  reconstruction (`rng.md` section 9) and it is unchanged. The collision operator adds
  no dependence on the division: given identical states it makes identical decisions.
- On a card, runs with deposit are not reproducible run to run (atomic sums), so
  "option absent" and "sigma = 0" cannot be shown byte-identical to the baseline there;
  they are on the processor.
- Tags are 32-bit; the pair keys use them as 64-bit words.
- The history sums are plain floating-point sums (relative rounding up to n eps/2 for n
  terms); they do not feed back into the particles.
- Cost (processor, one core, 1e6 particles in 32^3 cells): 0.54 s per step with the
  operator (0.27 s without) at one sub-step, 0.85 s at four sub-steps; card: 1e6
  particles x 200 steps in 2 to 4 s wall including start-up [VERIFIED: wall times of
  runs core-20261115-133533-0ca5e3b and core-20261115-135816-18d4555].

Lines touched in files shared with other work packages (against 94dc093):

| File | Lines of the new file | Change |
|---|---|---|
| `athenak/src/CMakeLists.txt` | 138 | `particles/nrpic_collide.cpp` |
| `athenak/src/particles/nrpic.cpp` | 272 | `NrpicCollideInit(pin);` after `NrpicKickInit(pin);` at the end of `NrpicInit` |
| `athenak/src/particles/particles.hpp` | 121-142 | struct `NrpicCollideOptions`, after `NrpicKickOptions` |
| | 150 | `TaskID collide;` in `ParticlesTaskIDs` |
| | 296-303 | members `coll`, `coll_cell`, `coll_list`, `coll_count`, `coll_begin`, `coll_key`, `coll_face` and the two method declarations, before `private:` |
| `athenak/src/particles/particles_tasks.cpp` | 40-48 | the task `NrpicCollide` between excise and deposit if `coll.on`; the deposit depends on it |
| `athenak/src/pgen/nrpic/nrpic_geodesic.cpp` | 62-96 | `NrpicSetHomogeneous` and its parameters |
| | 119-141 | the branch `<problem> metric_kind = homogeneous` in `NrpicGeodesic` (read only if the parameter is present) |

New files: `athenak/src/particles/nrpic_collide.{hpp,cpp}`, `python/nrpic/collide.py`,
`problems/tests/coll_box.athinput`, `problems/tests/coll_box_curved.athinput`,
`tracks/core/analysis/collisions/*`.

Requests.

- Track C: check the operator independently (TESTS.md T0b can use the dump of section 5
  and `python/nrpic/collide.py` as a second twin); note the changed sub-step rule
  (section 3.7), which SPEC.md 4.5 should adopt, and the cell-occupation effect above for
  the choice of particle numbers; T6 to T8 (conduction) remain the track's.
- Orchestrator: `coord/INTERFACES/rng.md` should carry the sub-streams of stream 2 as in
  section 4 (pairing 0, acceptance 1, direction 2; draw = sub-step) and of stream 1 as
  used by `make_box` (sub-stream 0, entity = tag).

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
- Sub-cycling `measured`: the number of sub-steps comes from the two largest speeds of
  the cell, not from the first pairing (section 3.7): the track's rule biases the rate.

## 11. Collisions with the metric at each particle (`coll_energy = particle`, wave 2)

Work package coll2, branch `core/collisions-2`. Predictions, failed predictions and
outcomes: `tracks/core/JOURNAL-coll2.md`. Evidence for every number: section 11.6.

### 11.1 The defect of core-v0.3 and its cause

The operator of sections 1 to 10 takes both momenta of a pair to the triad of the cell
centre, scatters there, and writes the covariant components back. It conserves the sum
of u_i and the sum of W_c = sqrt(1 + gamma_c^ij u_i u_j) of the pair exactly, with the
metric gamma_c of the cell centre. The energy with the metric at each particle,
W_p = sqrt(1 + gamma^ij(x_p) u_i u_j), is what the deposit hands to the spacetime; it is
not conserved, and in the cluster of section 8 it grew steadily (1e-9 to 1e-8 of the
particle energy per collision).

Cause [VERIFIED by the test of section 11.6, rows G1, in which each of three
consequences could have failed]: for a conformally flat metric, with
eps_p = (psi_c/psi_p)^4 - 1, one collision changes the pair's energy at its own
positions by (eps_a - eps_b) x (energy moved from b to a in the cell frame), to first
order. The mean of this product is not zero when the kinetic energy seen in the cell
frame is correlated with the position inside the cell: for a gas of local temperature
theta ~ psi^-s the mean gain per collision is (1 - s/4) theta <(eps_a - eps_b)^2>,
second order in the cell size and in the gradient, positive for a gas of uniform
temperature or in equilibrium in a potential well (hotter where psi is larger), about
zero at s = 4, negative beyond. The lapse does not enter: with a homogeneous spatial
metric the sum of W_p is conserved to rounding whatever the gradient of the lapse. In
the cluster (s < 4, hotter where deeper) this is a steady gain, as seen.

### 11.2 What a pair must conserve

Neither W at the cell centre nor W_p is the conserved energy. In a stationary metric
the geodesic motion conserves, per particle, the energy conjugate to the time
coordinate,

    H = alpha W - beta^i u_i,        W = sqrt(1 + gamma^ij u_i u_j),

with the metric at the particle (the Hamiltonian that the pushers integrate,
`nrpic_kernels.hpp`), together with u_i where the metric does not depend on x^i: the
canonical four-momentum (-H, u_i) = p_mu / m in the coordinate basis. A collision at
one point conserves the sum of p_mu of the two partners; with the partners at two
points of a cell, the sums of H_p and of u_i, each term with the metric at its own
particle, are what carries over to the system as a whole: for particles that source
the spacetime, the change of the total mass caused by a redistribution of momenta at
fixed positions is, to first order, the sum of M delta H with the fields held fixed
[JUDGEMENT: the velocity-dependent terms of the first post-Newtonian N-body energy,
v^2 (1 + 3U)/2 + 3 v^4/8 per unit mass, are the expansion of alpha W with
alpha = 1 - U, psi^4 = 1 + 2U; own algebra, not checked against a source]. The
operator of core-v0.3 violates the sum of H_p by about 1.5 times the defect of the sum
of W_p in a weak field (section 11.6).

### 11.3 Algorithm (`nrpic_collide.hpp`: `CollEnergy`, `CollCentre`, `CollScatterRel`, `CollEnergyRoot`, `CollBalance`)

Where the pair is evaluated: in the frame of the cell centre, as before (section 3):
one lapse, one volume element and one triad per cell set the probability (rate per
coordinate time alpha_c/sqrt(det gamma_c)) and the axes of the random direction; cells,
pairing, sub-steps and random-number keys are unchanged. How the outgoing momenta are
carried back: as covariant components u_i, unchanged (the canonical momenta, which the
pushers integrate), and the size of the momentum exchanged is then fixed with the
metric at each particle.

Before the cells are processed, lapse, shift and inverse spatial metric are
reconstructed at every colliding particle with the reconstruction of the pusher (mesh
metric at t^{n+1}: `interp` hermite or bspline; analytic metric: the functor) and
expressed in the triad of its cell: b_(m) = e^(m)_i beta^i,
g_(mn) = e^(m)_i e^(n)_j gamma^ij. With triad momenta u_(m) of the cell,
h_p(u) = alpha_p (W_p - 1) - b_p.u is the kinetic part of H_p and
v_p(u) = dh_p/du = alpha_p g_p u/W_p - b_p the coordinate velocity of the particle.

For a tested pair (a, b) with P = u_a + u_b:

1. Transfer. dl = -(W0/(2 alpha_c)) [d + q (q.d)], q = P/2, d = v_a(q) - v_b(q),
   W0 = sqrt(1 + |q|^2): the first Newton step from P/2 towards the split of P at
   which both particles have the same coordinate velocity (the minimum of the pair's
   energy at fixed P). The pair of the cell frame is u~_a = u_a - dl, u~_b = u_b + dl.
   For equal metrics dl = 0.
2. Probability: equation (1) of section 3.4 with the Moller speed (and the
   cross-section) of u~_a, u~_b; acceptance with u[0] as before.
3. Collision of the cell frame: direction nhat (key as before); wv = u~_a' - P/2 of the
   standard collision of u~_a, u~_b.
4. Energy: u_a' = P/2 + dl + lam wv, u_b' = P - u_a', with lam > 0 the root of
   h_a(u_a') + h_b(u_b') = h_a(u_a) + h_b(u_b). The left side is convex in lam and below
   the right side at lam = 0 when the split lies inside the energy surface, so the root
   is unique; Newton iteration from lam = 1 until the residual is below 16 units in the
   last place of the energies. If the split lies outside (a pair whose relative
   velocity is not resolved against the metric difference) or no root is found, the
   pair is left unscattered and counted (`n_noroot`).
5. Detailed balance: the collision takes place with probability min(1, R), decided by
   u[2] of the acceptance key, R the ratio of the rate of the reverse collision to that
   of the forward one, both as densities on the surface of constant P and energy. A
   proposal reaches the point c + r L nhat (c the split of step 4, L the stretch of the
   centre-of-momentum frame, det L = gamma = E/sqrt(s)), and on the surface
   delta(F) d^3q = gamma r^2 dOmega/(dF/dr), so its density is
   (1/4 pi)(dF/dr)/(gamma r^2) and
   R = [P' (dF/dr)_rev/(gamma' r_rev^2)] / [P (dF/dr)_fwd/(gamma r_fwd^2)],
   primes for the state after the collision, P the proposal probability (sigma v_Mol),
   r_fwd = lam p*, r_rev = |L'^-1 (u_a - c)|, (dF/dr)_rev = (v_a - v_b).(u_a - c)/r_rev.
   For equal metrics R = 1 identically (the density is then the invariant two-body
   phase space; checked by hand and to 1.2e-15 by the twin). Rejected collisions are
   counted (`n_balance`).

Why step 1: without the transfer the scheme conserves the same quantities, but in an
equilibrium state it moves energy on average from the partner that is hotter in the
cell frame to the other one (out of a potential well). In the non-relativistic limit a
pair in two conformally flat metrics is a pair of two different inertial masses
psi^4/alpha in the canonical variables; its elastic collision about the common
coordinate velocity has the equilibrium "equal temperature at infinity", Tolman's law.
Why step 5: beyond that limit the rate of the scheme is not symmetric between a state
and its outcome, at first order in the metric difference times the temperature;
without step 5 the reference of section 11.6 shows an energy transfer along the
modulation in equilibrium of 6 percent of that of core-v0.3 at theta = 0.05 and two
thirds of it, of the opposite sign, at theta = 0.3.

### 11.4 What is conserved, and what holds to which order

| Statement | `coll_energy = particle`, equal rest masses |
|---|---|
| rest mass of every macroparticle | unchanged (bit) |
| mass shell | exact: W is computed from u with the metric at the particle |
| sum of M u_i of a pair (covariant components) | rounding (u_b' = P - u_a') |
| sum of M H_p of a pair, H = alpha W - beta^i u_i with the metric at each particle | rounding: at most 16 units in the last place of the kinetic energies (h excludes the rest energy alpha, which does not change) |
| particles that do not collide | unchanged (bit) |
| equilibrium f = F(H) of a stationary metric, F = exp(-H/T) | left unchanged by the collision step, given the cell populations: the transition rate between two states of a pair is symmetric (step 5) [JUDGEMENT: derivation in the journal and in `CollBalance`; tested at theta = 0.05 and 0.3 to the statistical errors of section 11.6] |
| sum of M W_p (deposited energy) | changes at first order in the metric difference per collision, as it must when energy moves between two depths of a potential; no mean drift in equilibrium |
| angular momentum of a pair about a centre, x^i u_j - x^j u_i | not conserved: changes by (x_a - x_b) x Delta u_a per collision (first order in the separation, zero mean in a non-rotating state), as in core-v0.3 and any scheme whose partners sit at different points |
| covariant sum of the four-momenta at one point (parallel transport) | not used: the covariant components of two points are added in the coordinate basis; the difference from a transported sum is first order in the separation times the connection, and it is what the canonical sum above accounts for |
| collision rate | first order in the cell size: lapse, volume element and triad are those of the cell centre, the Moller speed that of the transferred momenta; rejections of step 5 lower it by their share (0.6e-3 to 6e-3 of the proposals in the tests at theta = 0.05, 0.6 to 2.3 percent at 0.2 and 0.3) |
| direction of scattering | isotropic in the triad of the cell centre; for a spatial metric with shear across the cell anisotropic at a particle's own frame at first order in the metric difference |
| transport (heat conduction, viscosity) | the cell-size error of any such scheme; not measured here |

With `coll_weights = nanbu` and unequal masses the pair conserves these quantities in
expectation only, as in section 3.6. A metric that changes in time (Z4c) is taken at
t^{n+1}; H is then the instantaneous Hamiltonian and its sum over a pair is conserved
by the collision step in the same way.

### 11.5 Options, outputs, cost

- `<particles> coll_energy = cell | particle`, read only if present (absent: the
  operator of core-v0.3, every output byte-identical to it). Its presence, with either
  value, adds history columns 32 to 36 (section 5), takes the budget of `coll_budget`
  particle by particle inside the cells, and writes dumps of version 2.
- With `coll_energy = cell` and the option present the particles evolve exactly as with
  the option absent (only the history gains columns).
- Watch `n_noroot` and `n_balance` against `n_coll`: in the tests at most 1.4e-5 and
  2.3e-2 of the proposals.
- Cost: one metric reconstruction per colliding particle and step, and per pair a
  Newton iteration (typically two to four steps). Measured on the processor: the
  collision step of a 1e5-particle Tolman box takes about the same time in both modes
  (wall time of the whole run 387 to 394 s for the four runs of
  core-20261115-164138-cdd7c88, dominated by the implicit push).
- Lines touched in files shared with other work packages (against main b9fbf3e; line
  numbers of the new files):

| File | Lines | Change |
|---|---|---|
| `athenak/src/CMakeLists.txt` | 139 | `particles/nrpic_perturb.cpp` |
| `athenak/src/particles/nrpic.cpp` | 275 | `NrpicPerturbInit(pin);` after `NrpicCollideInit(pin);` |
| | 390-391, 545-546 | `if (pert.on) NrpicPerturbKick(...)` before and after the push in `NrpicPush` |
| `athenak/src/particles/particles.hpp` | 150-153 | members `energy`, `ext` of `NrpicCollideOptions` (the comment of `ext` says columns 32 to 35; they are 32 to 36) |
| | 156-166 | struct `NrpicPerturbOptions` |
| | 326, 330-335 | `coll_pmet`; member `pert` and the two methods of the perturbing force |
| `athenak/src/pgen/nrpic/nrpic_geodesic.cpp` | 14-17, 19 | file comment, `#include <cmath>` |
| | 101-153 | `NrpicSetStaticConformal` and its parameters |
| | 199-227 | the branch `metric_kind = static_conformal` (read only if present) |

  New file: `athenak/src/particles/nrpic_perturb.cpp`. The rest is inside the files of
  the collision package (`nrpic_collide.{hpp,cpp}`, `python/nrpic/collide.py`).

### 11.6 What is verified

Test bed: `<problem> metric_kind = static_conformal` of `nrpic_geodesic` (deck
`problems/tests/coll_box_static.athinput`): alpha = alpha0 (1 + alpha_amp cos phi),
psi = psi0 (1 + psi_amp cos phi), beta^x = shift_amp sin phi on the mesh, periodic box
of 16 x 4 x 4 cells. Reference: `scbox.pair_reference` (`tracks/core/analysis/collisions/`),
a Monte Carlo over pairs of one cell with the metric reconstructed as the pusher does
and the Python twin of the kinematics; it reads no file of the code. Processor runs
with the serial build of 819d588 or f46f159 (identical `athenak/src`), card runs with
the clean card build of f46f159.

| Statement | Evidence |
|---|---|
| G1, cause. Operator of core-v0.3, one step on frozen particles (8e6), 14 cases: the gain of sum W_p per collision equals the pair model in all (largest \|z\| 1.5); with a homogeneous spatial metric and a lapse gradient dW = 7e-21 and -3e-21 per collision (the lapse does not enter); temperature law psi^-8 gives a loss (-1.43e-4, 23 se), psi^-4 about zero (-7e-6 against +8.3e-5 for uniform temperature); ratios for collision cells of 2 and 4 mesh cells 3.98 and 15.8 (model 4.07, 16.7): second order in the cell size; sum H_p gains 1.5 to 1.8 times as much as sum W_p where the lapse varies too | runs core-20261115-160707-6537687 (code), core-20261115-181655-b4b8e33, -181657-426b4a8, -181700-726905c, -181702-c93920b (reference), core-20261115-182037-e24d0d0 (grading); `fig_gradient.png` |
| G2, correction, the same 14 cases: change of sum M H_p per collision 3.5e-17 to 3.5e-16 of the rest mass (rounding); sum M u_i to 2e-20 of sum M \|u\|; the energy handed along the modulation in the ten equilibrium states zero within 1.8 se (core-v0.3: -9e-3 to -1.7e-1 per unit cos phi); rejected share and its dependence on cell size and temperature as in the model (6e-4 to 2.3e-2, \|z\| <= 1.2); pairs without a root only where the model has them (5 of 3.7e5 proposals in the hottest case with cells of two mesh cells, model 3.1e-5) | the same runs |
| A reference that drew the cell uniformly, without the rate factor alpha_c/psi_c^6 of the operator, disagreed with the code by up to 10.8 se in five cases; the corrected reference agrees: the code's rate weighting is the one stated in section 3.4 | runs core-20261115-160136/-160137/-160139-819d588 (old reference), JOURNAL-coll2.md 18:20 UTC |
| Replay: one collision step of the code reproduced by the Python twin from the dump in 13 cases (the seven of section 8 and `coll_energy` = cell, particle, particle with cells of two mesh cells, with the Cholesky triad and the Boris pusher, with `nanbu` and masses 1:4, in the analytic Kerr-Schild metric of a mass with shift): identical tested pairs, collisions and updates; momenta within 1.3e-14 of max(1, \|u\|); untouched particles bit-identical | runs core-20261115-160914-0656925 (819d588), core-20261115-182109-0b69dbe (f46f159, the same counts); `fig_replay.png` |
| T12 of track C and G3: constant lapse 0.8 and conformal factor 1.1: `static_conformal` with `coll_energy = cell` byte-identical to the wave-1 generator `homogeneous`; `particle` the same collisions in every step, momenta within 2.8e-14 after 200 steps, no rejection, lam = 1; 248168 collisions against 248192 in the flat box with the cross-section scaled by alpha0 (z = -0.03), i.e. alpha0 psi0^6 times the flat rate per coordinate volume at equal proper density; pair counting to 1.8e-14 | run core-20261115-182101-3a6e046; `fig_static_homog.png` |
| G4, equilibrium with streaming: Tolman gas in the well (alpha 0.8 to 1.2, psi_amp 0.1), theta_inf = 0.2, 1e5 particles, 57 collisions per particle, two seeds. `particle`: sum M H changes by 6.4e-15 in the collision steps and by -1.4e-7, +6.1e-8 in all (push included); the cos phi mode of ln(theta alpha) stays at -0.24(21) and -0.04(21) percent. `cell`: sum M H grows by 6.5e-3 and 6.2e-3 and the gas ends 3.8 and 3.4 percent colder at the bottom of the well than Tolman's law (a numerical heat flux out of the well) | run core-20261115-164138-cdd7c88 (processor); CARD_G4; `fig_tolman.png` |
| Relativistic cluster (section 8), two steps at Knudsen number 0.03 on the processor: `cell` raises sum M H by 1.48e-5 and sum M W by 9.6e-6 of their values in 773 collisions; `particle` changes sum M H by 4.8e-18 in 772 collisions, none rejected, none without a root | run core-20261115-160913-0656925; card at Knudsen number 3 over 150 M: CARD_C |
| Option absent: every output file of the wave-1 collision tests and of the existing set-ups byte-identical to the release executable core-v0.3 or to the wave-1 runs (processor); card: CARD_R | processor: runs listed in JOURNAL-coll2.md (18:10 and REGRESS_F46 entries) |

## 12. Fluid reference for the short-mean-free-path end (answer to Track C, assessment only)

Request: `track/C-sidm:tracks/C-sidm/outbox/20261115T1320Z__to-core__grhydro-reference.md`
(is the general-relativistic hydrodynamics of the code usable for a static spherical
star with tabulated initial data, and at what effort). Nothing was implemented.

What the tree has [VERIFIED by reading `athenak/src` at f46f159 and by one run]:
- `dyn_grmhd/` (general-relativistic magnetohydrodynamics on a dynamical spacetime,
  conservative finite volume, coupled to Z4c through the same matter-source interface
  as the particles; run without magnetic field by leaving it zero), with the primitive
  solver of `eos/primitive-solver/`: equations of state `ideal` (one adiabatic index,
  `<mhd> gamma`), `piecewise_poly`, `compose` (three-dimensional table), `hybrid`.
- A star generator, `pgen/dyn_grmhd/dyngr_tov.cpp` with `utils/tov/` (`tov_polytrope`,
  `tov_piecewise_poly`, `tov_tabulated`): integrates the Tolman-Oppenheimer-Volkoff
  equations for a polytrope, a piecewise polytrope or a tabulated barotropic relation,
  in Schwarzschild or isotropic coordinates, fills the fluid and the metric, and can add
  a velocity or pressure perturbation (`v_pert`, `p_pert`). It is not a built-in
  generator: build with `PROBLEM=dyn_grmhd/dyngr_tov scripts/build_cpu.sh <dir>`.
- Smoke run in this tree: the stock polytropic star (gamma = 2) on an octant of 32^3
  cells of 0.8 with the spacetime evolved by Z4c, deck `problems/tests/fluid_tov_z4c.athinput`,
  63 steps to t = 20 on one processor core in 173 s: rest mass 0.188313082 -> 0.188313078
  (-1.9e-8); maximum density +13.2 percent and minimum lapse 0.671 -> 0.652, a steady
  contraction under the inward velocity perturbation of the deck (ten cells per stellar
  radius, not a converged star); Hamiltonian-constraint norm 8.4e-4 -> 1.5e-4
  [VERIFIED: run core-20261115-161726-0656925; figure and numbers run
  core-20261115-182216-576283c, `fig_fluid_smoke.png`].

What it can give for the short-mean-free-path end:
1. As it is: stars of one adiabatic index. A collision-dominated gas of the track's
   particles is a relativistic monatomic gas whose index runs from 5/3 to 4/3 with the
   temperature; with one index the module can anchor the method (onset of the radial
   instability of a polytrope against the exact pulsation equation), not the track's
   equilibrium.
2. For the same equilibrium as the particle runs two additions are needed, neither
   small: (a) an equation-of-state policy for the relativistic monatomic gas (Synge:
   h = K3(1/theta)/K2(1/theta); or the Taub-Mathews closed form) next to
   `eos/primitive-solver/idealgas.hpp`, with a temperature inversion in the primitive
   recovery and its instantiation in `dyn_grmhd`; (b) initial data from the track's
   table: the tabulated option of the TOV generator reproduces the star if the track
   supplies the barotropic relation p(rho_0), e(rho_0) along its equilibrium (an
   isotropic distribution function gives a perfect-fluid stress tensor, so the same
   structure equations hold), so no new generator is needed; the generator must become
   selectable by name next to `nrpic_cf` and be tested with our Z4c settings and static
   refinement. Effort [JUDGEMENT]: two to three working sessions of core including the
   tests (a static star stays static to the truncation error of the atmosphere
   treatment; the fundamental radial frequency against the track's
   `gravothermal/tmb.py`; convergence in the mesh), about one card-hour.
3. What it cannot give: anything at finite Knudsen number (no viscosity or heat
   conduction in the module), and it needs an atmosphere floor outside the star, which
   the particle runs do not have; comparisons near the surface are limited by it.

Answer to the smallest acceptable form of the request: yes, usable; with the existing
single-index gas at once (method anchor), with the track's equilibrium after the
equation of state of item 2(a).
