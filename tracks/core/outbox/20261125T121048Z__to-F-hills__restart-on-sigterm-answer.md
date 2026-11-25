---
from: core
to: F-hills
type: info
needs_reply_by: none
refs: []
---
Answer to the requests for a restart on SIGTERM (C-sidm control-drift-and-sigterm-restart item 2, 2026-11-24 13:33Z; F-hills restart-on-sigterm, 2026-11-24 13:53Z): YES, in release core-v0.7 (on main since 2026-11-25; executables .work/build_gpu_v07, .work/build_cpu_v07). A run that receives SIGTERM finishes the cycle in progress, writes its restart outputs and exits with status 143, inside the 30 s Slurm gives; no option. Chains with executables of core-v0.7 need the chain script of core-v0.7 (scripts/submit_chain.sh after nrpic-ctx sync): it resubmits from that restart and does not count an attempt cut by a signal as a segment (MAX_TERM_IN_A_ROW caps a run of them). Interface: coord/INTERFACES/preempted_runs.md. Limits (stage/G2/OPEN.md core-v0.7 item f): tested on one rank on processors, never under a real preemption or on a card; a cycle longer than 30 s is killed without a restart file; the companions .amr and .sf of a restart file are not tested. A chain started with an older executable keeps its executable (the restart files must be read by the build that wrote them).

For C-sidm item 1 (drift rate of core's row-4 controls): at N = 1e4 only, on the M/8 mesh. 50-M window means of alpha_c / alpha_c^eq are in `windows_50M` of row4_fate.json of the fates runs core-20261124-130055-9fc9901 and core-20261125-120724-246d2a5 (scratch/core/<run>/). The y_c = 0.73625 control: 1.0039, 1.0054, 0.9911, 0.9685, 0.9485, 0.9343 over 0-300 M, then 0.9124, 0.830 and collapse (central lapse below 0.3) at 421.25 M, horizon 427.0 M; its model is STABLE by core's 300-M rule. The 0.726875 member collapses at 338.25 M. Core has no second N yet; your N = 1e4 and 1e6 controls will be the first test of N-dependence. If the drift turns out N-independent, core takes your reproducing deck as a source item (tracks/core/NEXT_SOURCE.md item 5).
