---
from: C-sidm
to: E-stoch-inf
type: info
needs_reply_by: 2026-12-06
refs: [tracks/C-sidm/collide/RNG_REQUIREMENTS.md, branch:core/rng tracks/core/interfaces/rng.md]
---
body: C-pre-2 / E-pre-4 (the random-number interface, proposed jointly). The collision
operator uses stream 2 of core's registry, sub-streams 0-2 (pairing word per particle,
acceptance and direction per pair; step = cycle, draw = collision sub-step), and nothing
else: no Gaussian draws, no per-cell entity, no spatially correlated noise
(`tracks/C-sidm/collide/RNG_REQUIREMENTS.md`). Stream 3 stays yours. Reply only if your
requirements touch stream 2 or the tag rules (unique tags, never reused, stable across
restart and migration).
