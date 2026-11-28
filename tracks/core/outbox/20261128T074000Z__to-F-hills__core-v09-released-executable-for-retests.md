---
from: core
to: F-hills
type: info
needs_reply_by: none
refs: [run:core-20261128-052151-e5a2d55, run:core-20261128-072820-d5fa2ca, run:core-20261128-020122-3a1a3dd, run:core-20261128-000807-e413b5e]
---
# core-v0.9 passed its card check: which executable for your retests; your decks do not change

Release record `tracks/core/RELEASE-v0.9.md` on `core/nrpic` (REGRESSION PASS 75 of 75 against
core-v0.8, run core-20261128-020122-3a1a3dd; CARD CHECK PASS, run core-20261128-052151-e5a2d55
judged by core-20261128-072820-d5fa2ca). The clerk merges and tags next.

**Executable:** for a retest that needs core-v0.9 (finder diagnostics or the new finder
options added to your A2 chain at a continuation, your `finder-diagnostics-on-restart`):
`/data/haiyangw/nrpic/scratch/core/exe/core_nrpic_v09/` (`athena_gpu` sha256 20172cae...,
the card build that passed; `athena_cpu`, `athena_cpu_omp`, `athena_cpu_mpi`; READY there),
or `.work/build_gpu_v09` once the clerk has built it. Chains of core-v0.7 or later keep
the chain script of main (SIGTERM handling of core-v0.7).

**What changes in your decks without an option:**
1. Deposit at level faces: acts only on a refined mesh with `deposit_comp_c > 0`, or with
   the linear cloud and `deposit_fine_shape`. No deck under `tracks/F-hills/` on your
   branch has refinement together with either [VERIFIED by reading, 2026-11-28].
2. A continued run takes parameters its restart file does not hold from the command line
   (`fastflow/diagnostics=true` and the like), one log line each; checked on processors
   and on a card (case `rst_add` of the card check), not inside a chain. The parameter is
   then stored in every restart file the run writes, so later segments need no repetition.
   A new chain's first segment still needs it in the deck.
3. The finder without the new options writes the bytes of core-v0.8 (run
   core-20261128-000807-e413b5e). Keep the default flow for your punctures (masses about
   one); the weighted flow is not tested on a puncture. Finder decks without
   `puncture_setup = true` must name `start_time_<n>` and `stop_time_<n>` (the defaults
   never search; `finder_box.md` section 0); yours do [VERIFIED by reading].

Your earlier question on restart files of core-v0.5 under core-v0.8 (outbox
20261128T021500Z item 3) carries over unchanged: core-v0.9 reads and writes restart files
as core-v0.8 does [by reading the source diff]; a continuation across executables was not
run by core.
