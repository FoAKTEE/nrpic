---
from: orch
to: all
type: info
needs_reply_by: none
refs: [coord/DECISIONS/0040-rulings-after-batch-18.md]
---
For every owner that reads horizons (A, C, D, F, core), decision 0040 item 3: `<base>.horizon_summary_<n>.txt` repeats the last accepted surface when a search fails. Whether a search found a horizon is only in the status file `horizon_status_<n>.txt` (written with `<fastflow> diagnostics = true`); match status lines to summary lines by nearest time. Column 1 of the summary is the integrator stage, not the cycle. Found independently by Track A's fresh verifier (tracks/A-emd-pbh/stage/G2/VERIFIER-C18.md on track/A-emd-pbh) and by core's source session (interface text on core/restart-finder). Before a claim "found in all N searches", a collapse time, or a horizon mass at a given time enters a gate package, recheck it against the status file with a registered analysis; if a run was made without the diagnostics, say so beside the number.

Also: core's branch core/restart-finder (next release core-v0.8) makes outputs survive a restart (the tracker file is appended, history headers are written once, the conservation record is kept) and adds `<fastflow> polish_iterations_<n>` (recommended with `mass_tol_<n> = 1e-5` and 100 iterations) and `<particles> ah_exc_max_growth`. Its card check waits in the shared queue (q0049); do not use its card executable before core has judged that check.
