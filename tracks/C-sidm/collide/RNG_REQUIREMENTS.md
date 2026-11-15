# RNG_REQUIREMENTS: what the collision operator needs from the shared random numbers

C-pre-2 under decision 0010 (brief M11: the interface is proposed jointly by tracks C and
E; core implements it on branch `core/rng`). Written on 2026-11-15 against core's draft,
which was uncommitted at the time (`wt/core-rng`: `athenak/src/utils/rng.hpp`,
`python/nrpic/rng.py`, `tracks/core/JOURNAL-rng.md`): Philox-4x64-10, key (seed, stream),
counter (entity, entity_hi, step, draw*256 + kind*16 + block), streams registry with
`kStreamCollisions = 2`, draws `Bits`, `Uniform`, `Uniform4`, `Index`, `Normal2`,
`Direction` (Marsaglia), seed `<job> rng_seed`. The draft meets every requirement below
as far as I can read it; items marked CHECK are for core's tests or for the interface text.

## 1. Requirements

R1 Pure function of the key. Every draw of the collision step is a function of (seed,
stream, entity, entity_hi, step, draw) only; nothing depends on the MeshBlock, rank,
thread, array position or execution order. [met by the draft's design]

R2 Entities are physical. Particle entity = the particle's tag (`PTAG`); pair entity =
(min tag, max tag) in (entity, entity_hi). Cell entity is not needed by the collision
operator (pairing is keyed on particles). Requirements on tags (CHECK, particle module):
unique over the whole run, never reused after excision or escape, unchanged by restarts
and by migration between blocks; tags are int32 positions in the particle file today
(`tracks/core/interfaces/particle_id.md` section 2), which bounds a run to 2^31 particles.

R3 Step counter = the cycle number `ncycle`, restored by a restart; sub-step index of the
collision sub-cycling goes into `draw` (below 2^56). Keys used by the operator:

| use | key (seed, stream, entity, entity_hi, step) | draw | call |
|---|---|---|---|
| K1 pairing key of particle | (seed, Stream(2, 0), tag, 0, ncycle) | sub-step | `Bits` (64-bit sort key; ties broken by tag) |
| K2 acceptance of a pair | (seed, Stream(2, 1), min tag, max tag, ncycle) | sub-step | `Uniform4`: u[0] acceptance U < P, u[1] Nanbu-Yonemura update of the heavier member, u[2..3] spare |
| K3 scattering direction | (seed, Stream(2, 2), min tag, max tag, ncycle) | sub-step | `Direction` (isotropic unit vector = nhat of SPEC.md section 3) |

The odd-N triangle tests three different tag pairs, so its keys differ; a pair formed
again in a later sub-step or cycle differs in draw or step. Sub-stream numbers 0, 1, 2 of
stream 2 are reserved here; track E uses stream 3.

R4 Independence of decomposition and restart (test T10): with the same seed the particle
state after any number of cycles is bit-identical for 1, 8 and 64 MeshBlocks, for 1 and 4
MPI ranks, and with a restart at an arbitrary cycle. This needs, besides R1-R3: the set
of particles in a collision cell and their momenta are themselves decomposition-
independent (true for the pusher with an analytic metric; CHECK for the mesh metric);
the order within a cell is canonical (sorted by (K1 key, tag)); n_sub of a cell is a
function of the cell's particles only (no reduction over blocks); no floating-point
reduction whose order depends on the decomposition feeds back into particle data (the
history sums do not).

R5 Platform: the draws are bit-identical on processors and cards (the draft's design and
its tests); the collision outcomes need not be, because the floating-point kinematics may
contract into fused multiply-adds differently; a single differing bit changes later
acceptances. Processor-card comparisons of collisional runs are statistical (TESTS.md T10b).

R6 Quality: uniform deviates in the open interval (0, 1), so U < P never accepts at
P = 0 and always accepts at P >= 1; `Direction` exactly isotropic up to its 2^-25 grid
(sufficient: the collision tests resolve isotropy to ~1e-3); streams for different
(stream, entity, step, draw) statistically independent (Philox; CHECK: core's
statistical tests include pairs of keys that differ only in entity_hi and in the sub-stream).

R7 Python twin: `python/nrpic/rng.py` reproduces K1-K3 bit for bit, so that the replay
test T0b recomputes one collision step of the code from its dump (pairing, acceptance,
direction, scattering) and compares to rounding.

R8 Seeds: `<job> rng_seed` (default 0) is the only seed; independent realizations of a
test use different seeds; the seed is written into the history header and the restart.

R9 Cost: per cell and sub-step one `Bits` per particle, one `Uniform4` and one
`Direction` per pair. Core's predicted costs (prediction P4 of `JOURNAL-rng.md`, lines
110-114, not yet a measurement): one generator call 10-20 ns and a direction 25-30 ns on
one processor core; on an A100 1-2 x 10^9 calls per second and 1-1.5 ns per direction.
So about 60-90 ns per pair on a core and a few ns on a card, small against the sort of
the cell's particles.

## 2. What the collision operator does not need

No spatially correlated noise, no Gaussian draws, no per-cell entity. The coloured noise
of track E (brief M11, Fourier space or local filtering) is E's requirement.

## 3. Proposed addition to `coord/INTERFACES/rng.md`

A table "stream 2 (collisions): sub-stream 0 pairing keys (entity = tag), 1 acceptance
(entity = min tag, entity_hi = max tag), 2 directions (same entity); draw = collision
sub-step; step = ncycle", and the tag rules of R2.
