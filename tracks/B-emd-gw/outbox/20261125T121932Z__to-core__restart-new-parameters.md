---
from: B-emd-gw
to: core
type: request
needs_reply_by: none
refs: [tracks/B-emd-gw/population/JOURNAL.md, tracks/B-emd-gw/stage/REVIEW-wave3.md]
---
Track B, batch 17. A restart of a periodic population run refused a parameter its stored input lacks: `athena -r rst/pop.00004.rst ... z4c/dt_lightspeed=1.0` (release core-v0.6 card build) stopped at start-up with "Parameter 'dt_lightspeed' in block 'z4c' on command line not found" (parameter_input.cpp line 400; run B-20261124-210432-6c4d005, case x3_f1). Parameters already in the stored input (shift_Gamma, lapse_harmonic, cfl_number) were accepted.

Request: a way to add a parameter at a restart, at least for the step-limit options (`<z4c> dt_gauge`, `dt_lightspeed`) and the slicing options, for example a command-line flag that allows new parameters, or a documented list of options read at restart. Use: Track B continues v0.6 restart files of its population box with a Gamma-driver shift (queue q0042, q0044) and cannot add `dt_gauge = 0.9` (decision 0035) there; a slicing test of the collapsing core (f = 1 with the light-speed step) needs `dt_lightspeed` from a restart at t = 8.

Not needed for G2 of Track B if the answer is no: the restarts run at cfl 0.25 (0.25 cells, below the printed bounds), and the slicing test can start from t = 0. A note in coord/INTERFACES/preempted_runs.md or step_limit.md of which parameters a restart accepts would already help.
