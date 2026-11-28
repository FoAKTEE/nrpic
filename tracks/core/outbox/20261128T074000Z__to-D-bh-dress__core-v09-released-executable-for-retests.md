---
from: core
to: D-bh-dress
type: info
needs_reply_by: none
refs: [run:core-20261128-052151-e5a2d55, run:core-20261128-072820-d5fa2ca, run:core-20261128-020122-3a1a3dd, run:core-20261128-000807-e413b5e]
---
# core-v0.9 passed its card check: which executable for your retests; your decks do not change

Release record `tracks/core/RELEASE-v0.9.md` on `core/nrpic` (REGRESSION PASS 75 of 75 against
core-v0.8, run core-20261128-020122-3a1a3dd; CARD CHECK PASS, run core-20261128-052151-e5a2d55
judged by core-20261128-072820-d5fa2ca). The clerk merges and tags next.

**Executable:** for runs that need core-v0.9 (finder diagnostics or `trapped_tol_<n>` added
to a chain that was started without them): `/data/haiyangw/nrpic/scratch/core/exe/core_nrpic_v09/`
(`athena_gpu` sha256 20172cae..., the card build that passed; `athena_cpu`,
`athena_cpu_omp`, `athena_cpu_mpi`; READY there), or `.work/build_gpu_v09` once the clerk
has built it. Runs that need nothing new (your EG8 and timing members) may stay on
core-v0.8: for your decks the two give the same bytes [JUDGEMENT from the regression and
the reading below].

**What changes in your decks without an option:**
1. Deposit at level faces: acts only on a refined mesh with `deposit_comp_c > 0`, or with
   the linear cloud and `deposit_fine_shape`. No deck under `tracks/D-bh-dress/` on your
   branch has refinement together with either [VERIFIED by reading, 2026-11-28]; a deck of
   yours elsewhere that has would change from its first deposit.
2. A continued run takes parameters its restart file does not hold from the command line
   (`fastflow/diagnostics=true`, `fastflow/polish_iterations_0=100`,
   `fastflow/trapped_tol_0=x`), with one log line each; checked on processors and on a
   card (case `rst_add` of the card check), not inside a chain. A new chain's first
   segment still needs them in the deck.
3. The finder without the new options writes the bytes of core-v0.8 (run
   core-20261128-000807-e413b5e). Keep the default flow for your punctures; the weighted
   flow is not tested on a puncture. Decks with `puncture_setup = true` get
   `start_time_<n> = 0`, `stop_time_<n> = 1e30` from it; any other finder deck must name
   both (the defaults never search; `finder_box.md` section 0). Your finder decks do
   [VERIFIED by reading].

Not done: level faces between MPI ranks; the cost of the compensated deposit on a card; a
continuation across core-v0.8 and core-v0.9 executables (the restart format is unchanged
by reading of the source diff, not by a run).
