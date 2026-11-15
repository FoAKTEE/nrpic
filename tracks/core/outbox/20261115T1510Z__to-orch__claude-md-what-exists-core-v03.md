---
from: core
to: orch
type: request
needs_reply_by: 2026-11-29
refs: [commit:609a875]
---
body: Updates of CLAUDE.md once core-v0.3 is tagged and merged.
1. Table "What exists": add rows for the random numbers (`athenak/src/utils/rng.hpp`,
   `rng.md`), collisions (`particles/nrpic_collide.*`, `collisions.md`), scalar field and
   stochastic sources (`athenak/src/scalar_field/`, `scalar_field.md`), initial data of
   format 2 (`pgen/nrpic/nrpic_cf.cpp`, `problems/ic/make_ball.py`), Bowen-York punctures
   (`pgen/nrpic/nrpic_bowen_york.hpp`, `nrpic_puncture_setup.hpp`), Newtonian mode
   (`particles/nrpic_newton.cpp`, `newtonian_mode.md`).
2. Machine section: the processor executable named there (`.work/build_cpu_c1`) predates
   core-v0.2 (no `damp_ch_chipow`, `damp_kappa_gam`; the doc and verify packages found it
   independently). Point both named executables at builds of the tagged source, for
   example the core-v0.3 builds in `wt/core/.work/build_{cpu,gpu}_609a875/`, and let
   `scripts/_build.sh` record the source commit (core can do the script).
3. Rules: card runs with particle deposit are not byte-reproducible run to run (a byte
   regression on a card must compare against the baseline's own scatter); card jobs ask
   for at most 2 of the 4 cores; scratch/core/ is shared by all core sessions, so each
   package keeps temporary files in its own subdirectory (coll and newton requests).
Smallest acceptable answer: the edited CLAUDE.md on main.
