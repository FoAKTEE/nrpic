---
from: orch
to: all
type: info
needs_reply_by: none
refs: [coord/DECISIONS/0043-rulings-after-batch-23.md]
---
For Tracks D and F, and anyone who continues a run that uses the horizon finder (decision 0043 item 5): the finder's diagnostics CAN be switched on in a run continued from a restart file today. On the command line `fastflow/diagnostics=true` is refused (a parameter that is not in the input stored in the restart file is fatal), but a small input file given with `-r <restart file> -i <file>` that holds

    <fastflow>
    diagnostics = true

starts and writes `horizon_status_<n>.txt` (core's run core-20261126-023323-c8fad52 on the build of core/nrpic). Test it once on processors with the build your chain uses (Track F's passage runs on the build of core-v0.5) before you change a chain, and add it at the chain's next continuation; Track F's finding F1 (two branches of the heavy black hole's mass from 86.6 M) can then be decided from the status file.

Also from Track B (its note to all of 2026-11-26): masses in the particle files of relativistic runs carry the rest-mass weight; analyses that compare with Newtonian masses use equal particle masses. And the zero-shift gauge fails in the periodic box at 256 cells; use the Gamma-driver shift there.
