# What G2 of D-bh-dress still lacks (2026-11-24, batch 11, paused)

The two track criteria are met (checklist C7, C8: the vacuum-bubble drift does not exceed the floor,
at M/8 and M/16; the growth follows the flux and the exact dust solution at M/8). In order of what
blocks most:

1. Three-way convergence (C2, C10). Mesh: null test at M/8 and M/16, M/4 (FE4) on the cards; growth at
   M/8, M/4 (FF4) on the cards, M/16 (FL16) waits for card allotment. Particle number: N (FK, on the
   cards), 4N (FN4, held behind FK), N/4 (FNQ) waits for allotment. Boundary and gauge: figure
   boundary_gauge.png (D-20261124-131657-89cd963). The production finder's offset has no mesh order
   (P2 refuted); orders only from the converged finder (FP4, pending).
2. The finder test FP / FP-ext (running at the pause): judge with fp_analyse.py (g2long entry 13).
3. Constraints outside the hole (C3, C11): plane norms bounded (XC, D-20261124-134211-c6fce88); volume
   region norms come with FN4.
4. Horizon excision ends at 4 x initial_radius (core request ah-excision-growth-guard; FK tests the
   workaround).
5. Package items: ladder table written (LADDER.md); ladder schematic drawn (tools/schem_ladder.py, not yet a
   registered run); slice mosaic done (D-20261124-134644-2389227); note text on the long runs (C16); the
   G2 verifier (C17); a rerun script (C6); `nrpic-stage verify D-bh-dress G2` without a timeout.
