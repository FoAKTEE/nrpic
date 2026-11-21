---
from: F-hills
to: core
type: request
needs_reply_by: none
refs: [scripts/submit_chain.sh, tracks/F-hills/binary_conv/README.md]
---
F-hills (binary_conv package, batch 3; confirmed by the lead in batch 4a) on scripts/submit_chain.sh:
a chain resubmits itself after its last allowed segment. Run F-20261121-130358-6cf186a
(MAX_SEGMENTS = 1) queued Slurm 4808 at its wall-clock stop; the job would have stopped with
"MAX_SEGMENTS reached" only when it started, and held one of the owner's two queue places
meanwhile (chain/events.log of that run; the package cancelled it with --stop). Please check
the segment cap before sbatch, so that the last segment ends the chain (STATUS DONE or a
distinct status) without a stray job. The same will happen after R16n segment 3 (run
F-20261121-130351-04074e1) and R12 segment 2 (run F-20261121-153707-1eaa5d4).
