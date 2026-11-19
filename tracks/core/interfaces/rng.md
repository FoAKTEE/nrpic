# Reproducible random numbers: keys, streams, rules

Status: PROPOSAL of core (branch `core/rng`, 2026-11-15) for `coord/INTERFACES/rng.md`.
Clients: Track C (Monte Carlo collisions, C-pre-2), Track E (stochastic sources,
E-pre-4), every tool that samples initial data. Brief lines 544-547 (M11) and the
verification row "Reproducible random numbers". Evidence labels as in the brief; every
number below carries a run id (`tracks/core/runs/<run_id>/manifest.json`, outputs in
`scratch/core/<run_id>/`).

## 1. What the interface guarantees

A draw is a pure function of its key (seed, stream, entity, step, draw). There is no
generator state anywhere, in the code or in a restart file. Therefore a draw does not
depend on the division of the mesh into MeshBlocks, on the number of ranks or threads, on
the order in which a kernel visits its entities, or on where a run was restarted, as long
as the caller builds the key from quantities that have these properties (section 5).

Every function returns the same bits on processors, on a card and in Python. This holds
for the raw words, the uniform deviates and the integers by integer arithmetic, and for
the normal deviates and the directions because they are built from single correctly
rounded operations of IEEE 754 double precision (product, quotient, square root, exact
sums) and call no library logarithm, sine or cosine. [VERIFIED, section 7]

| Where | What |
|---|---|
| `athenak/src/utils/rng.hpp`, namespace `rng` | the generator and the draws, `KOKKOS_INLINE_FUNCTION`, usable in any kernel; no dependence on the rest of AthenaK (`-DNRPIC_STANDALONE`) |
| `athenak/src/utils/rng_mesh.hpp` | entity of a cell: `CellOffsets`, `WrapIndex`; entity of a Fourier mode and the stream word of the stochastic sources keyed by modes: `ModeEntity`, `StochasticModeStream` (twins `rng.mode_entity`, `rng.stochastic_mode_stream`) |
| `python/nrpic/rng.py` | the twin: the same functions on NumPy arrays, broadcasting over all fields of the key |
| `athenak/src/pgen/unit_tests/rng_test.cpp` (`pgen_name = rng_test`), `problems/tests/rng_test.athinput` | unit test inside the code: table of draws, statistical sums, cost, cell check |
| `athenak/src/particles/nrpic_kick.cpp`, `problems/tests/rng_kick_*.athinput` | test kick of the particle momenta: the pattern of a stochastic term in a kernel, and the demonstration of section 7 |
| `tracks/core/analysis/rng/` | drivers of all tests |

## 2. Generator and key layout

Philox-4x64 with ten rounds (the counter-based generators of Salmon, Moraes, Dror and
Shaw, "Parallel random numbers: as easy as 1, 2, 3", 2011 [BACKGROUND: the paper is not
in the knowledge base]): a bijection of a 256-bit counter under a 128-bit key, four
64-bit words per call. It is the function behind `numpy.random.Philox`, which serves as
an independent implementation: `rng.words(...)` equals
`numpy.random.Philox(counter=c - 1, key=k).random_raw(4)` (NumPy adds one to the counter
before it generates). [VERIFIED: 20902 keys, run core-20261115-115626-f0258ce]

| Word | Content | Set by |
|---|---|---|
| key 0 | `seed` | the run: `<job> rng_seed` in the input file (unsigned, up to 64 bits, decimal or `0x...`; default 0); read once with `rng::RunSeed(pin)`; stored with the parameters in restart files |
| key 1 | `stream` = `Stream(id, sub)`: registered identifier in the upper 32 bits, sub-stream in the lower 32 bits | the module: identifier from the registry (section 6), sub-stream chosen by the owner of the stream |
| counter 0 | `entity` | the caller: particle tag, `CellEntity(i, j, k)`, first tag of a pair, wave number |
| counter 1 | `entity_hi` (default 0) | second word of the entity: second tag of a pair, refinement level of a cell |
| counter 2 | `step` | number of the time step that is being taken (`pmesh->ncycle`); 0 for initial data |
| counter 3 | `draw * 256 + kind * 16 + block` | `draw` (below 2^56) numbers the variates of one entity in one step; `kind` (0 raw words, uniform, integer; 1 normal pair; 2 direction) and `block` (retry of the rejection step, 0 to 15) are set by the functions |

C++: `rng::Key key{seed, stream, entity, step, entity_hi};` (the last member may be
omitted) and `rng::Uniform(key, draw)`. Python: keyword arguments
`seed, stream, entity, step, draw, entity_hi=0`.

## 3. Draws

| C++ | Python | Result | Definition |
|---|---|---|---|
| `Bits4(key, draw, w)`, `Bits(key, draw)` | `bits4`, `bits` | four raw words; the first | generator call with kind 0, block 0 |
| `Uniform(key, draw)`, `Uniform4(key, draw, u)` | `uniform`, `uniform4` | double in (0,1); four of them | `(floor(w / 2^12) + 1/2) 2^-52` for a word `w`: 52 bits, never 0 or 1, smallest 2^-53, mean exactly 1/2 |
| `Index(key, draw, n)` | `index(..., n=n)` | integer in [0, n) | upper half of the product `w n`; probabilities differ from 1/n by less than 2^-64 |
| `Normal2(key, draw, z)`, `Normal(key, draw)` | `normal2`, `normal` | two independent standard normal deviates; the first | polar form of Box-Muller on a point of the unit disk, below |
| `Direction(key, draw, n)` | `direction` | isotropic unit vector | Marsaglia (1972) construction on a point of the unit disk, below |

`Uniform`, `Index` and `Bits` with the same draw index use the same word and are not
independent of each other; a normal pair, a direction and a uniform deviate with the same
draw index are independent (different kind).

Point of the unit disk: the upper 52 bits of a word give two odd integers `v1`, `v2` in
(-2^26, 2^26); the point `(v1, v2) 2^-26` is accepted if `s = v1^2 + v2^2 < 2^52`
(integer arithmetic; probability pi/4). The four words of a call are tried in order, then
the next block; after 64 rejections (probability 1e-43) a fixed value is returned.

- Normal pair: `z_i = v_i sqrt(2 L / s)` with `L = -ln(s 2^-52)`. `L` comes from the
  arithmetic-geometric mean: `ln(4/y) = pi / (2 agm(1, y)) (1 + O(y^2))` with
  `y = 2^-30 s 2^-52`, ten steps, one quotient, minus the constant `32 ln 2`, clamped at
  zero. Absolute error of `L` below 1e-13, largest found 3.0e-14 [VERIFIED: 202050 values
  against mpmath, run core-20261115-120841-564b404]; the radius `sqrt(2 L)` is then wrong
  by at most 8.4e-8 where `L < 1e-12` (probability 1e-12 per draw) and by 4.7e-10 relative
  for `L > 1e-6`. This is the price of identical bits: against the same deviates computed
  with the library logarithm the 404140 deviates of the test table differ by 11 units in
  the last place in the median and by at most 1.4e-10 relative [VERIFIED: run
  core-20261115-123656-0502788, `fig_rng_agreement.png`]; no statistical test of section 7
  can see it. |z| does not exceed 7.94 (lattice point `v = (5, 1)`); a radius beyond
  7.5 is represented by about 2000 lattice points and one beyond 8 by 45, so the lattice
  is coarse only where the probability per deviate is below 6e-14.
- Direction: `n = (2 v1 h, 2 v2 h, 1 - 2 s)` in units where `v` is in (-1, 1) and `s` in
  (0, 1), `h = sqrt(1 - s)`. For a uniform point of the disk `s` is uniform in (0,1), so
  `n_z` is uniform in (-1,1), and the azimuth is that of `(v1, v2)`. `|n|^2 - 1` is at
  most 4.4e-16 in absolute value [VERIFIED: 1e11 directions, run
  core-20261115-115355-f0258ce].

Entity helpers: `rng::CellEntity(i, j, k)` packs three global cell indices (each below
2^21) into one word; `rng::CellOffsets(pmbp)` (host, once per mesh) returns for every
MeshBlock the global index of its first active cell on its own level, its level relative
to the root mesh and the number of cells of the mesh on that level; `rng::WrapIndex`
maps a ghost-cell index of a periodic direction onto its image.
`rng::ModeEntity(nx, ny, nz)` (`utils/rng_mesh.hpp`; Python `rng.mode_entity`) is the entity of
the Fourier mode of a periodic box with the signed integer wave numbers (nx, ny, nz), each
in [-2^20, 2^20): `CellEntity(nx + 2^20, ny + 2^20, nz + 2^20)`, with `entity_hi` = 0. The
wave numbers are those of the mode on the root mesh, so the entity, and with it the
realisation, does not depend on the resolution or on the division of the mesh.
`rng::StochasticModeStream(dof)` (Python `rng.stochastic_mode_stream`) is the stream word
`Stream(kStreamStochastic, 2^16 + dof)` of section 6. [VERIFIED: the twin equals
`cell_entity(n + 2^20)` for 548958 wave vectors and the corner values, and the amplitudes
built with both helpers equal Track E's independent `noise/ref/philox_ref.py` bit for
bit, run core-20261119-144905-cea3a49; the code draws the same numbers as before the
helpers existed: regression of section 6 of `scalar_field_3.md`.]

## 4. Pattern in a kernel

    #include "utils/rng.hpp"
    const std::uint64_t seed = rng::RunSeed(pin);                       // at start-up
    const std::uint64_t stream = rng::Stream(rng::kStreamCollisions, 0);
    const std::uint64_t step = static_cast<std::uint64_t>(pmesh->ncycle);
    par_for("kick", DevExeSpace(), 0, np-1, KOKKOS_LAMBDA(const int p) {
      const rng::Key key{seed, stream, static_cast<std::uint64_t>(pi(PTAG,p)), step};
      double z[2], n[3];
      rng::Normal2(key, 0, z);                 // draw 0: two normal deviates
      const double u = rng::Uniform(key, 1);   // draw 1: a uniform deviate
      rng::Direction(key, 2, n);               // draw 2: an isotropic direction
      ...
    });

Cells (`utils/rng_mesh.hpp`):

    auto off = rng::CellOffsets(pmbp);          // rebuild after the mesh has changed
    ... KOKKOS_LAMBDA(const int m, const int k, const int j, const int i) {
      const rng::Key key{seed, stream,
                         rng::CellEntity(off(m,0) + (i - is), off(m,1) + (j - js),
                                         off(m,2) + (k - ks)),
                         step, static_cast<std::uint64_t>(off(m,3))};

Python, the same numbers:

    from nrpic import rng
    key = dict(seed=seed, stream=rng.stream(rng.STREAM_COLLISIONS, 0), entity=tags,
               step=ncycle)
    z1, z2 = rng.normal2(draw=0, **key); u = rng.uniform(draw=1, **key)
    n = rng.direction(draw=2, **key)

## 5. Rules for users

1. The entity is a property of the physical object, never of its storage. Particles: the
   tag (`PTAG`; unique, kept through restarts and removals). Cells: global index on the
   cell's own level and the level (`CellOffsets`). A pair of particles: smaller tag in
   `entity`, larger in `entity_hi`. A Fourier mode: its integer wave numbers on the root mesh (`ModeEntity`). Never the
   array index `p`, the MeshBlock index `m` or its gid, local `(k, j, i)`, a rank or
   thread number, an address, or a floating-point coordinate.
2. The step is the cycle number of the step being taken, which the mesh restart file
   restores. Never a counter that lives only in memory. Stages of one step are told apart
   by the draw index or the sub-stream, not by a fractional step. Initial data: step 0.
   A stream that serves both the initial data and the evolution keys the draws of the
   evolution with `ncycle + 1`, the cycle number reached at the end of the step (the
   first step would otherwise repeat the draws of the initial data, both with step 0),
   unless one draw is meant to serve both: the frozen amplitudes of the stochastic
   sources are drawn once with step 0 and used by the initial slice and by every kick
   (stream 3 below).
3. One draw index per variate of an entity in a step, written as a constant next to the
   kernel that uses it. Reusing an index for a second variate of the same kind makes the
   two identical.
4. Two uses of random numbers for the same entity in the same step differ in the stream
   word. The identifier comes from the registry; the meaning of the sub-stream and of the
   entity in a stream is fixed by its owner and written down next to the registry. Within
   one stream word the entity has one meaning (do not mix cells and tags).
5. One seed per run, `<job> rng_seed`. Members of an ensemble differ in the seed and in
   nothing else. Never derive it from the clock or a process number.
6. The number of draws a kernel uses must not depend on storage either: a selection among
   the particles of a cell must be defined on tags (for example: order the particles of
   the cell by tag, or by a tag-keyed uniform deviate, before pairing them). A rejection
   loop written by the user numbers its attempts with the draw index.
7. New entities created during a run (a decay product, a split particle) need tags that
   are themselves reproducible, for example a function of the parent tag and the step;
   tags are never reused.
8. Refined meshes: draws for the same region on different levels are independent
   (different `entity_hi`). A noise field that must be consistent between levels is drawn
   on one level and transferred with the operators of the mesh; which level, and whether
   the result agrees with noise coloured in Fourier space, is for Track E to settle
   (brief line 546). [JUDGEMENT]
9. Compile without value-changing floating-point options (`-ffast-math`); the functions
   work in double precision whatever `Real` is.
10. Existing generators stay as they are (`utils/random.hpp`, the noise of
    `nrpic_cosmo.cpp`, NumPy generators in the tools). New code that must be reproducible
    uses this interface and neither `Ran2` nor a pool of per-thread generators.

What the interface cannot do for the caller: the draws are identical for identical keys,
but a quantity computed from a draw and from the state of the run is only as reproducible
as that state. Particle states of mesh-coupled runs agree between two divisions into
MeshBlocks to rounding, not to the bit (section 8), so a decision `u < P` can differ
between two divisions when `u` and `P` agree to about 1e-13.

## 6. Registry of streams

| Id | Constant (C++ / Python) | Purpose | Owner | Entity, sub-stream |
|---|---|---|---|---|
| 0 | none | not to be used: a forgotten stream shows up as 0 | | |
| 1 | `kStreamInitialData` / `STREAM_INITIAL_DATA` | sampling of particles and fields at the start of a run (step 0) | core, every track | to be fixed by the first user; suggested: entity = tag or cell, sub-stream = species or field |
| 2 | `kStreamCollisions` / `STREAM_COLLISIONS` | Monte Carlo collisions, decays | core (collisions), Track C | to be fixed by the collision package; suggested: entity = pair of tags, sub-stream = channel |
| 3 | `kStreamStochastic` / `STREAM_STOCHASTIC` | stochastic sources of fields | core (scalar field), Track E | sub-stream bit 16 set (`kStochasticModeBit`): draws keyed by Fourier modes, the 16 bits below it number the degree of freedom, stream word `StochasticModeStream(dof)`; entity = `ModeEntity(nx, ny, nz)`, `entity_hi` = 0; draw 0 = one normal pair per mode, alpha_n = (z1 + i z2)/sqrt 2 (draw 1 is reserved for a second pair of the same mode and step); step = epoch: 0 for amplitudes drawn once (initial slice and all kicks, rule 2), `ncycle + 1` for amplitudes that are new in every step. Sub-streams with bit 16 clear are reserved for draws keyed by cells (entity = cell with level); none exists. Details below the table |
| 4 | `kStreamTests` / `STREAM_TESTS` | tests of this interface | core | sub-streams 1 to 6: unit test (`rng_test.cpp`); 16: test kick, entity = tag, draws 0 and 1 (mode normal), 0 and 1 (mode direction) |
| 5 and above | | unassigned | | a new identifier is added to this table and to both source files in one change |

Stream 3, degrees of freedom of the mode-keyed draws (`athenak/src/scalar_field/
scalar_field_noise.cpp`; requests R-1 to R-3 of `tracks/E-stoch-inf/noise/
RNG_REQUIREMENTS.md`):

| Model (`<scalar_field> noise`) | dof | What it draws | Step word |
|---|---|---|---|
| `mukhanov_sasaki` | 0 | the amplitudes alpha_n of the curvature perturbation: one draw for the initial slice (`<problem> id = stochastic`) and for the sources of Pi, Khat and At_ij | 0 |
| `mukhanov_sasaki` | 1, 2 | reserved for the two tensor polarisations (the graviton sources are not implemented) | |
| `power` (test of the generator) | 0 | noise of phi | 0 with `noise_scheme = frozen`, `ncycle + 1` with `markov` |
| `power` | 1 | noise of Pi (`noise_pi_dof = 1`; with 0 it reuses the amplitudes of dof 0) | as dof 0 |
| any | 3 to 65535 | unassigned: further fields | |

The two models never run together, so the meaning of dof 1 differs between them without a
clash; a model that adds tensor sources to `mukhanov_sasaki` takes dof 1 and 2. The hemisphere
that carries the independent amplitudes (n_x > 0, or n_x = 0 and n_y > 0, or n_x = n_y = 0
and n_z > 0) and the reality condition for the other half are part of the model
(`scalar_field.md` section 7.1), not of the key: the entity of -n is never drawn.

## 7. What is verified

| Statement | Evidence |
|---|---|
| The header, compiled into the processor build and the card build, five standalone compilations (`-O0`; `-O2`; `-O3 -march=native` with fused multiply-add allowed and forbidden; 32-bit products), and the Python twin return identical bits for 202070 keys (edge cases of every field, runs of consecutive values, random keys) in all 15 columns: four words, integer, upper half of a product, four uniform, two normal, three direction components | run core-20261115-115626-f0258ce (tables of runs core-20261115-115134-f0258ce and core-20261115-115230-f0258ce); one sha256 for seven tables; figure `tracks/core/notes/rng_figs/fig_rng_agreement.png`; twin after its last change: run core-20261115-123610-1ee600a |
| The same on a table ten times larger (2002070 keys), final source: processor build, the five standalone compilations and the twin | run core-20261115-125654-a8755fc; one sha256 for six tables, no differing value in the twin |
| The words equal those of `numpy.random.Philox` | runs core-20261115-115626-f0258ce (20902 keys) and core-20261115-125654-a8755fc (21890 keys), none differing |
| Statistics: 253 tests (moments of the uniform, normal and direction draws up to the eighth; chi-square of 1024 bins, of pairs and of bits; covariance with the draw of the key in which one field is larger by one, for each of seed, stream, sub-stream, entity, entity_hi, step, draw; between the registered streams; between the words of a call; between kinds; tails of the normal beyond 3, 4, 5, 6) with the Python twin at 2e7 keys and inside the code at 2e8 keys (processor), 1e10 and 1e11 keys (card): smallest p-value 1.1e-3, none below 1e-3, largest deviation 3.26 standard errors, p-values uniform (Kolmogorov-Smirnov p = 0.61) | runs core-20261115-120536-5bdb22c and core-20261115-122300-b6df7bc (the same numbers; final figures); figures `tracks/core/notes/rng_figs/fig_rng_uniform.png`, `fig_rng_normal.png`, `fig_rng_direction.png`, `fig_rng_pvalues.png` |
| Follow-up of the two largest deviations of that list, both covariances between two words of one call (-3.26 and -3.17 standard errors): 1.008e12 calls with fourteen new seeds give all six covariances within 1.7 standard errors of zero (correlations between -1.6e-6 and +0.5e-6, standard error 1.0e-6); the deviations were chance | run core-20261115-121240-8f4222b |
| Inside the particle module (10000 particles, 800 steps, analytic Kerr-Schild metric): with the key (seed, stream, tag, cycle) the particle states are bit-identical for 1 and 64 MeshBlocks and for a run restarted halfway, in both kick modes; with the MeshBlock in the key (control) all 10000 particles differ between the divisions; with a counter that is not in the restart file (control) all differ after the restart | runs core-20261115-115701-f0258ce and core-20261115-121609-fb0491a (processor, first and final source); figure `tracks/core/notes/rng_figs/fig_kick_demo.png`; card: pending, section 9 |
| The numbers used inside the particle module are those of the Python twin for the stated keys: in flat space the momenta after 800 kicks equal the initial momenta plus the sum of the deviates from the twin | run core-20261115-121609-fb0491a: largest difference 1.7e-16 over 30000 components, 25287 of them with identical bits (the code may fuse the product and the sum of the kick); accumulated kick over sigma sqrt(t): mean 0.0032 +- 0.0058, variance 1.008 +- 0.008 |
| Mesh metric (uniform mesh of 128^3 cells, 10000 particles): the kicks are identical for 8 and 64 MeshBlocks in all 801 cycles (checksums); the particle states differ by at most 1.2e-13 (positions) and 8.0e-15 (momenta) with the kick and 1.1e-13, 7.8e-15 without it, in 9042 and 9048 particles; a run in which 9073 particles are removed at the lapse threshold restarts bit-identically | run core-20261115-115833-f0258ce (processor); card: pending, section 9 |
| Draws keyed by cells: the checksum of a raw word and a normal deviate per cell is the same for 1, 8 and 64 MeshBlocks of a uniform mesh, for two divisions of a mesh with one refined octant (both levels), for the finest level of a mesh with two refinement levels, and equal to the Python twin evaluated on the cells listed from the geometry | run core-20261115-120535-5bdb22c (processor); card: pending, section 9 |
| Existing behaviour unchanged: five existing set-ups (analytic metric; mesh metric with deposit; refined mesh with deposit and excision; Z4c with particle sources; restart files with removal), 36 output files, byte-identical between the executable built from the unmodified source and the new one | run core-20261115-120532-5bdb22c (processor); card: pending, section 9 |

## 8. Cost

| Call | One core, Xeon 8360Y, serial build `-O2` (ns) | One A100 (ns) | Python twin, one core (ns) |
|---|---|---|---|
| generator call, four words (`Bits4`) | 20.5 | 0.026 | 545 |
| `Uniform` | 16.7 | 0.023 | 557 |
| `Uniform4` | 23.0 | 0.028 | 581 |
| `Index` | 15.8 | 0.026 | 584 |
| `Normal2` (two deviates) | 66.8 | 0.133 | 776 |
| `Direction` | 28.4 | 0.043 | 736 |
| loop without a draw | 1.2 | 0.0012 | |

Fastest of three loops over 2e7 keys (processor, run core-20261115-115134-f0258ce), 4e9
keys (card, run core-20261115-115230-f0258ce: 3.9e10 generator calls and 7.5e9 normal
pairs per second) and 2^20 keys (twin, run core-20261115-121342-8f4222b). A normal pair
for each of 512^3 cells costs 0.018 s on the card and 9 s on one core.

## 9. Limits and open points

- Particle states of runs with the metric on the mesh are not bit-identical between two
  divisions into MeshBlocks, with or without random numbers: the reconstruction of the
  metric at a particle forms `(x - xmin) / dx` with the lower edge of the particle's own
  MeshBlock (`athenak/src/particles/nrpic_mesh.hpp`, line 91), which rounds differently
  for different edges. The differences stay at 1e-13 over 800 steps in the test above.
  An experiment on a copy of the source (patch `tracks/core/notes/rng_gather_experiment.diff`,
  not applied) forms the cell coordinate from the position alone; with it the same test
  gives 0 of 10000 differing particles between 8 and 64 MeshBlocks, with and without the
  kick, so the reconstruction is the only source of the difference there; the patched
  executable differs from the present one by up to 1.4e-13 in positions [VERIFIED: run
  core-20261115-124953-8e05112, scouting]. Applying it changes existing results at
  rounding level and needs a decision (request in the report of this work package).
- The particle module runs on a single rank (`nrpic.cpp`, `NrpicInit`); the generator has
  no rank dependence, but the independence of the number of ranks is untested until the
  module runs on several.
- Tags are `int` (31 bits) in the particle arrays; the entity has 64 bits.
- Spatially correlated noise is not part of this interface. Both routes of brief line 546
  can be written with it (Fourier space: entity = mode; local filter: entity = cell).
- Adaptive refinement during a run was not exercised (static refinement only).
- Card: the table of draws, the statistical sums and the cost were run on the card. The
  kick demonstration, the cell check and the regression on the card (one job,
  `tracks/core/analysis/rng/gpu_job.sh`, Slurm job 4414) were still queued behind other
  owners' jobs when this was written; their manifests appear under `tracks/core/runs/`
  when the job has run, and each driver writes a `summary.json` whose field `ok` is the
  verdict.
