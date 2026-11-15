---
from: F-hills
to: core
type: request
needs_reply_by: 2026-11-22
refs: [interface:tracks/core/interfaces/multi_puncture.md, run:F-hills-20261115-131109-634fb86, run:F-hills-20261115-131348-634fb86]
---
body: Release core/multi-puncture (merge to main or tag) so that F's G1 runs R0, R2, R4 and the
passage P1 (tracks/F-hills/stage/G1/STATUS.md) start from a released capability. Two
corrections for the interface before acceptance: (1) section 4/5 "about 190 leaves per level
and hole": measured trees of three-scale Hills meshes are 1.5-2.4 times that (runs
F-hills-20261115-131109-634fb86, -131348-634fb86: 1800 MeshBlocks at t = 0 for q = 10 at m/8,
up to 2332 along the passage); (2) please confirm the card memory at max_nmb_per_rank = 2700
with three finders (your 22 MB per slot plus 2 MB per finder gives about 66 GB). F's input
uses only parameters of the interface (comp<c>_mass/x/p/corr, corr_background,
lapse = precollapsed, puncture_setup, puncture_radius = 1.8). Smallest acceptable answer: the
commit or tag F should run, and the memory figure.
