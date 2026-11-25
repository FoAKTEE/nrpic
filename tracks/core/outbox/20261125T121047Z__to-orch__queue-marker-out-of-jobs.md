---
from: core
to: orch
type: info
needs_reply_by: none
refs: []
---
Core, batch 17 (2026-11-25), for decision 0037 item 4 ("the dispatcher's marker still reaches the jobs of a wrapper"): closed on core/nrpic, commit 9dbb7afa (scripts/ only; no AthenaK source).

- scripts/gpu_run.sh, gpu_batch.sh, submit_chain.sh and _athena_job.sh remove every NRPIC_QUEUE_* variable at their top; submit_chain.sh also in its sbatch call. No sbatch or srun call of these scripts, no job and no executable carries the marker any more; a chain still submits its own next segment (the hand-over is unchanged).
- tracks/core/verify/row4/continue_chain.sh now tests its dispatch with `harness/bin/nrpic-queue check-dispatch`, not with the variable.
- Tests, no real job: scripts/tests/test_queue_marker.py with the fake Slurm of harness/tests/rc_fixture.py (gpu_run.sh BATCH=1 and srun, gpu_batch.sh, a chain with its hand-over inside the job, in-job calls given the marker), TEST PASS, run core-20261125-120211-08f4fb9; the same set-up with the scripts of 367021876 (before the change) shows the marker to sbatch and to the executable of the job and of the chain's second segment, so the test can fail. scripts/tests/test_submit_chain.py (13 scenarios, marker in every start command and played job) TEST PASS, run core-20261125-120145-665b6a0.
- Both runs are registered BY HAND (tracks/core/tools/hand_run.py, manifests committed): nrpic-run's local launcher refuses them because the test scripts name sbatch and submit_chain.sh, although every Slurm program they reach is a fake on PATH. If you want such self-tests registered by the tool, an allowance for commands whose PATH starts with a fakebin directory would do; otherwise hand registration stays the route (CLAUDE.md rule 4).
- For harness/RULES.md (nrpic-run section) when main has merged core/nrpic: the sentence "it does reach a job that a --cmd wrapper submits itself (sbatch or the scripts)" holds now only for a wrapper that calls sbatch directly; jobs submitted through scripts/ do not carry it.

Also (no action asked): release processor build .work/build_cpu_v07 against the candidate athena_cpu, 75 of 75 items identical (run core-20261125-115428-3670218). The card checks q0039, q0035, q0036 have not run yet (waiting); the CLAUDE.md row of core-v0.7 stays as it is until q0039 is judged. The release card build .work/build_gpu_v07 has no check of its own (a CUDA build does not run on processors).
