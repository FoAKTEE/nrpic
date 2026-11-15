# 0006 Compute budget and machines (D6)

Status: PROVISIONAL · 2026-11-15

Machine: `anta`. Two A100 cards through the Slurm partition `preempt` (one hour per job;
long runs are chained with `scripts/submit_chain.sh`), 144 processor cores shared by all
sessions.

| Owner | GPU-hours to the next gate | Processor cores at a time |
|---|---|---|
| core | 40 | 16 |
| A-emd-pbh | 60 | 16 |
| B-emd-gw | 40 | 16 |
| C-sidm | 20 | 16 |
| D-bh-dress | 30 | 16 |
| E-stoch-inf | 10 | 16 |
| F-hills | 40 | 16 |
| kb | 0 | 8 |

`nrpic-run` records the use and refuses a run beyond the allotment. Raising an allotment
is asked of the user. Priority when the queue is full: brief section 9.11.
