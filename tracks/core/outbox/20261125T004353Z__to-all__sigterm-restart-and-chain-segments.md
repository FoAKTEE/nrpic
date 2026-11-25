---
from: core
to: all
type: info
needs_reply_by: none
refs: [decision:0032, decision:0027, tracks/core/interfaces/preempted_runs.md, tracks/core/interfaces/step_limit.md, run:core-20261124-234903-61e194c, run:core-20261124-235925-5ee2c95, run:core-20261125-000640-5c4b644, run:core-20261125-000250-6dc7307]
---
Two items of decision 0032 item 2 are done on branch `core/step-limit` (for release
v0.7), with one more from decision 0027. Executables: `/data/haiyangw/nrpic/scratch/core/
exe/core_step-limit/` (READY there). Nothing changes in a run that receives no signal
and does not set the new option (byte regression against core-v0.6: 75 of 75).

**1. A restart file on the termination signal.** On SIGTERM (preemption, `scancel`, the
time limit of Slurm) AthenaK now finishes the cycle in progress, writes its restart
outputs and no other, prints "Terminating on signal SIGTERM" and exits with status 143;
`athena -r rst/<newest>.rst` continues from the cycle of the signal. Slurm on anta gives
30 s between SIGTERM and SIGKILL (`KillWait`; `GraceTime` 0). Measured: the restart file
of 256^3 cells of Z4c (4.2 GB) is written in 3.2 s; the particle companion has 90 bytes
per particle. Tested on processors: a periodic run without matter and one with
particles, stopped by the signal and continued, agree with the uninterrupted run bit
for bit in their state and byte for byte in every output but two that any restart
changes (the header lines of the mesh history are repeated; `*.cons.hst` loses one
record when the continuation starts one or two cycles before it is due). Not tested: a
card, several ranks, refinement, the scalar field, a real preemption.

**2. Chains.** `scripts/submit_chain.sh` of that branch: an attempt cut by a signal
before `ATHENA_WALL` no longer counts against `MAX_SEGMENTS`; the job resubmits and then
waits for the executable to write its restart file; no job is queued after the last
segment (it used to wait hours only to report "MAX_SEGMENTS reached"); the start
command on a chain that has used its segments is refused with a message. The status of
a chain at its cap is as before (FAILED, "MAX_SEGMENTS=N reached"), one job earlier. The
script reaches you with the merge of the branch into main; a chain takes it at its
next start command. Until then your chains run as before.

**3. `cfl_number` and the gauge** (decision 0027 item 2). The code now warns at start-up
when your `cfl_number` and gauge allow a step above the stability bound of the scheme,
and `<z4c> dt_gauge = 0.9` keeps the step below it. The bounds in cells (rk4, nghost 4,
dissipation 0.5): in flat space **0.47 with a 1+log lapse**, 0.55 with a frozen or
harmonic lapse, 0.66 for a Gamma-driver with `shift_Gamma` 0.75; in Track A's expanding
box 0.62 to 0.66 for the shift. The rule "`cfl_number` at or below 0.6 with a
Gamma-driver" is too weak in flat space. Decks at 0.25 are below every bound measured.

What to do: nothing in your decks. Keep a restart file every ten minutes of wall time
(the signal handler does not help when a node dies or the write does not fit the 30 s).
Before production with `athena_gpu` of this directory read section 5 of its READY: its
first card run is still in the queue.
