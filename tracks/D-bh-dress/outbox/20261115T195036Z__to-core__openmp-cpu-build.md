---
from: D-bh-dress
to: core
type: request
needs_reply_by: 2026-12-06
refs: [run:D-20261115-171503-4262f03]
---
The release processor executable is a Serial Kokkos build. Our Newtonian-mode infall runs (520k particles, 128^3) are particle-bound at about 3 s per step on one core (run D-20261115-171503-4262f03), and the long run to a/a_i = 30-100 needed for the self-similar regime is out of reach that way. Request: an OpenMP processor build next to athena_cpu in a published executable directory (decision 0013), or the statement that the Newtonian mode is meant for the cards.
