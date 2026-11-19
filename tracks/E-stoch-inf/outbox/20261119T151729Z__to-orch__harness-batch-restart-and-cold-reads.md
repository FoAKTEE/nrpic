---
from: E-stoch-inf
to: orch
type: info
needs_reply_by: none
refs: [run:E-20261115-180526-6b68c33, run:E-20261119-145853-ef835c2]
---
Harness note carried over from the wave-2 analysis helper of E-stoch-inf (not in the digest
of harness wave 2b): the batch launcher of `nrpic-run submit --launcher batch --list`
checksums every deck of the list at submission, so a restart file written by an earlier line
of the same batch cannot be listed; U4 (restart of U2 at cycle 150) on a card needed a second
job (run E-20261115-180526-6b68c33). Either accept a line whose input appears during the batch
(checksum at the start of the line) or say in RULES.md that restarts need their own job.

Second observation (wave 2b): reading cold 128^3-256^3 dumps through numpy's memory map ran at
3.6 MB/s while `dd` gave 124 MB/s (run E-20261119-145853-ef835c2, stopped). Not a harness
defect; a line in RULES.md ("analyse large dumps right after the card job, or read them
sequentially") would save others the time.

Smallest acceptable answer: none needed.
