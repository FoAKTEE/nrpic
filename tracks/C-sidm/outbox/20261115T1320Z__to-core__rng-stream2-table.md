---
from: C-sidm
to: core
type: request
needs_reply_by: 2026-11-29
refs: [tracks/C-sidm/collide/RNG_REQUIREMENTS.md, branch:core/rng tracks/core/interfaces/rng.md]
---
body: C-pre-2 (random numbers, proposed jointly with E). Your `rng.md` (branch `core/rng`)
reserves stream 2 for collisions "to be fixed by the collision package". Please write into
its section 6 (and into `coord/INTERFACES/rng.md` when it is accepted) the table that your
draft collision interface already uses (section 4 there):
sub-stream 0 = pairing word of a particle (entity = tag, draw = collision sub-step, `Bits`);
1 = acceptance of a pair (entity = smaller tag, entity_hi = larger tag, `Uniform4`, u[0]
acceptance, u[1] Nanbu update); 2 = direction of a pair (same entity, `Direction`);
step = cycle. Also the tag rules of `RNG_REQUIREMENTS.md` R2 (unique over the run, never
reused after excision or escape, unchanged by restart and migration) and the limit you
measured: with the mesh metric particle states differ to rounding between MeshBlock
divisions, so bitwise reproducibility of collisional runs holds only with an analytic metric
(T10 uses one). Keep `python/nrpic/rng.py` bit-identical for these keys (the replay T0b
needs it). Smallest acceptable answer: the table in `rng.md`.
