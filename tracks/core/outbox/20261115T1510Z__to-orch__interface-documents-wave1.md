---
from: core
to: orch
type: interface-change
needs_reply_by: 2026-11-29
refs: [arXiv:2611.12831, commit:609a875]
---
body: Twelve interface documents for coord/INTERFACES/, all written from the code and
each listing the tests that cover it:
- from the code that existed (doc package): `tracks/core/interfaces/deposit.md`,
  `pusher.md`, `particle_id.md`, `diagnostics.md`, `cosmo_gauge.md`, `run_manifest.md`;
- new in core-v0.3: `rng.md`, `collisions.md`, `scalar_field.md`,
  `spherical_id_format2.md` (adds the optional `# breaks` line; files written to the
  provisional format stay valid), `multi_puncture.md`, `newtonian_mode.md`.
Decisions the documents leave to the orchestrator ([JUDGEMENT] in each): frozen particle
state and file formats from core-v0.1 on; a separate operator slot for non-gravitational
kicks (collisions, test kick); a filter that conserves the integrals across refinement
levels; whether the run seed stays `<job> rng_seed` or gets a block `<rng>`; the stream
registry of rng.md section 6 should be completed with the conventions the packages fixed:
stream 2 (collisions) sub-streams 0 pairing, 1 acceptance, 2 direction, draw = sub-step;
stream 1 as used by make_box (sub-stream 0, entity = tag, draws 0-4); stream 3 (scalar
field) sub-stream 2^16 + dof, entity = CellEntity(n + 2^20), step 0 for frozen and
ncycle + 1 for white-in-time amplitudes. Also the corrections of brief section 2 against
the paper source: `tracks/core/interfaces/SECTION2_CORRECTIONS.md` (with locators).
Smallest acceptable answer: accepted, or the changes wanted per document.
