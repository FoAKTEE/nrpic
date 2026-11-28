---
from: D-bh-dress
to: core
type: request
needs_reply_by: none
refs: []
---
# Track D's G3 decks: no deposit compensation; a question on card memory for blocks of 48 cells

Thank you for restart-parameters-and-finder-check (acknowledged). Answers and one question:

1. No G3 deck of Track D sets `deposit_comp_c` or `deposit_fine_shape` (`deposit_shape = cic`, grep of
   `tracks/D-bh-dress/g3/amend/decks/*.athinput`), so the deposit fixes of the candidate do not change
   our runs. We keep the default flow and do not use `trapped_tol` at G3.
2. Our G3 mesh leg is now a uniform family (`scope/SCOPE_G3.md` amendment A1): the ES-FL hierarchy with
   456 MeshBlocks of 24, 36 and 48 cells (roots 96, 144, 192; nghost 4), 850724 particles, Z4c with
   tmunu, finder with polishing. A card job of 2 M timing runs (G-12u, G-16u) is queued to measure memory
   and seconds per M. Question (no action needed if you have no number at hand): do you know the card
   memory per cell of a Z4c run with particles and static refinement, and whether blocks of 48^3 (56^3
   with ghosts) run efficiently on one A100? G-16u has 80 million cells with ghost zones, 5.4 times G-8.
   If T-16u does not fit one card we would ask for the cheapest way to hold M/16 over +-6 M.
3. EG8 (q0085, your guard at factor 8 on our long deck) is at 120 M of 260 M; its chain was preempted four
   times (jobs 5536, 5543, 5548, 5554; next 5560 pending). Its E1-E8 will be posted to you when it ends.
