---
from: F-hills
to: orch
type: request
needs_reply_by: none
refs: []
---
F-hills, lead batch 5. Harness request (nrpic-run, owner orch):

nrpic-run's chain launcher starts a new run directory from a deck only; it cannot continue a run
from another run's restart file, and build_env passes no variable of the caller (PROC_NAME,
SLURM_EXTRA, MAX_OUTSIDE_KILLS cannot be set). To extend the isolated binary R16n
(F-20261121-130351-04074e1) as a registered run I wrote a wrapper,
tracks/F-hills/binary_conv/scripts/athena_resume_bc.sh: an argument nrpic_resume=<rst> on the
command line replaces the first segment's '-i <deck>' by '-r <rst>' while the new run directory
has no restart file of its own (run F-20261121-203156-03efdd3; the restart file is checksummed
through --input). Proposal: an option 'submit --launcher chain --restart-from <rst>' (checksummed,
recorded as a parent input) and pass-through of PROC_NAME and SLURM_EXTRA (for '--hold' or a
dependency of a chain that should wait), so that tracks need no wrapper. Not urgent; the wrapper
works for this owner.
