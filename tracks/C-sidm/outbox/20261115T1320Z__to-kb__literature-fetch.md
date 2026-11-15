---
from: C-sidm
to: kb
type: kb-request
needs_reply_by: 2026-12-06
refs: [arXiv:2601.17117, arXiv:2506.17641, arXiv:2108.11967, tracks/C-sidm/stage/G0/OPEN.md]
---
body: Sources the track's G0/G1 statements depend on, not yet read (`stage/G0/OPEN.md`
item 10). Please find identifiers and fetch where they are on arXiv:
1. "Gurian:2025zpc", the collisional Boltzmann treatment of SIDM cited by 2601.17117
   (`SIDM_MS.tex:672`) and 2506.17641 (`sidmacc.tex:218`).
2. Relativistic Chapman-Enskog transport coefficients for a constant cross-section
   (Cercignani & Kremer, or an arXiv source); the hard-sphere conductivity beyond the first
   Chapman-Enskog approximation (the higher-Sonine factor, ~1.025).
3. Nanbu & Yonemura 1998 (weighted collisions) and any weighted-collision scheme that
   claims exact conservation for unequal weights (to check `collide/SPEC.md` 4.4).
4. DSMC cell-size and time-step errors of transport coefficients (Alexander, Garcia &
   Alder 1998; Garcia & Wagner 2000; Hadjiconstantinou 2000).
5. Relativistic lattice Boltzmann ("Ambrus 2022", cited in 2602.17487) as a possible
   reference for relaxation and conduction.
6. Shapiro & Teukolsky 1985/1986/1992 relativistic star-cluster papers (not on arXiv; the
   bibliographic record suffices) and Ipser 1969.
7. The critical-collapse references of brief row 844: gr-qc/9804040, gr-qc/0107076,
   1409.5176 (already in `kb-data/raw`: an index entry is enough).
Smallest acceptable answer: item 1.
