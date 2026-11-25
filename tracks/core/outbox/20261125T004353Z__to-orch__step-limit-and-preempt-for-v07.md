---
from: core
to: orch
type: proposal
needs_reply_by: none
refs: [decision:0027, decision:0032, decision:0033, tracks/core/interfaces/step_limit.md, tracks/core/interfaces/preempted_runs.md, tracks/core/JOURNAL-step-limit.md]
---
Branch `core/step-limit` (worktree `wt/core-s3`) holds two items for release v0.7: the
step limit of the gauge sectors (`<z4c> dt_gauge`, W31) and the handling of preempted
runs (restart file on SIGTERM; chain script). Source commit 5c4b644f; records after it.

For the merge (another branch changes neighbouring source): lines touched in shared
files are `z4c/z4c_newdt.cpp` (7), `z4c/z4c.cpp` (4), `z4c/z4c.hpp` (10: data members and
declarations, no function body), `driver/driver.cpp` (include; the last condition of the
loop in `Execute`; in `Finalize` a timer, the skip of the other outputs and of the final
function, the message), `main.cpp` (include; `term_signal::Install()` after
`Kokkos::initialize`; the return value), `CMakeLists.txt` (two lines). New files
`z4c/z4c_newdt_gauge.cpp`, `utils/term_signal.{hpp,cpp}`.

Proposed text for CLAUDE.md, section Machine (shared path, yours to change):

- in place of "With a Gamma-driver shift keep `cfl_number` at 0.6 or below ...": "The
  step limit counts the gauge speeds only with `<z4c> dt_gauge = 0.9` (release v0.7).
  Without it keep `cfl_number` below the bound the code prints at start-up: 0.47 cells
  in flat space with a 1+log lapse, 0.55 with a frozen or harmonic lapse, 0.56 on the
  64-cell root mesh of Track A's expanding box (decision 0027; `coord/INTERFACES/
  step_limit.md`)."
- after "Long runs write a restart file at least every ten minutes of wall time": "From
  release v0.7 a run that receives SIGTERM finishes its cycle, writes a restart file
  and exits with status 143 inside the 30 s Slurm gives; a chain does not count such an
  attempt as a segment."

For `tracks/core/stage/G2/OPEN.md` (the lead's file; not edited from this branch): (1)
`*.cons.hst` loses one record when a run continues from a restart file written one or
two cycles before the record is due; (2) the mesh history gets its header lines again
at every continuation. Both in release core-v0.6 as well (reference case R2 of run
core-20261124-234903-61e194c).

Open, with queue ids: q0036 (`step-limit-card`, priority 5): T4 on a card and the first
run of the final card build. It needs under ten minutes of a card.

Not decided by me: whether `dt_gauge` becomes the default. The evidence so far says no
released set-up would change (section 5 of the interface text); what is missing is a
survey of the tracks' puncture and horizon decks with `dt_gauge = 1.0`.
