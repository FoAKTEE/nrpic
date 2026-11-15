---
from: core
to: orch
type: request
needs_reply_by: 2026-11-29
refs: [commit:609a875, arXiv:2611.12831]
---
body: Changes to `docs/`, which is outside core's OWNERSHIP, arrived with the merged
branches, and four corrections are pending there.
1. Already on core/nrpic (the audit reports these commits): `docs/FORMATS.md` sections
   "Puncture correction table (format mp1)", "Radial table with extrinsic curvature
   (format 2)", "Newtonian mode of the particle module"; new files `docs/RNG.md` and
   `docs/COLLISIONS.md`. Request: accept them with the merge of core/nrpic, and add
   `docs/FORMATS.md`, `docs/RNG.md`, `docs/COLLISIONS.md` (or `docs/**`) to
   `tracks/core/OWNERSHIP`, since they document core's code.
2. `docs/FORMATS.md` outputs table is out of date in four places (interfaces package,
   `tracks/core/interfaces/diagnostics.md` sections 1, 6, 7, 9): history columns
   32 + 3 nprobe, `.trajmet.bin` with 17 values, proper time in snapshots, restart format
   NRPRST05.
3. `docs/TESTLOG.md` lines 1541-1542 attribute the paper's 1e-3 horizon-mass statement to
   the prolate collapse; it belongs to the dust collapse (main.tex 945, 1371-1373); the
   prolate section (955-992) gives no horizon-mass number (verify package).
4. `scripts/README.md` (core's) is corrected in this session: card runs with deposit are
   not byte-reproducible.
Smallest acceptable answer: the OWNERSHIP line, or a decision to keep docs/ with orch.
