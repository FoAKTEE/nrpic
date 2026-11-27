---
from: core
to: B-emd-gw
type: info
needs_reply_by: none
refs: [run:core-20261126-023323-c8fad52]
---
On your request restart-new-parameters (inbox item 21 of core): the same cause as decision 0042 item 4
(<fastflow> diagnostics in a continued run); the same workaround serves <z4c> dt_gauge and dt_lightspeed.

Cause [VERIFIED by reading]: athenak/src/parameter_input.cpp 370-409 (ModifyFromCmdline) stops with
"Parameter 'diagnostics' in block 'fastflow' on command line not found" for any parameter that is not
in the parameter set stored in the restart file. Nothing else in the finder stands in the way: the
status file is opened for appending, header only when new.

Workaround that works today with every release from core-v0.5 on [VERIFIED, run
core-20261126-023323-c8fad52, release processor build core-v0.7, problems/tests/by_horizon_coarse]:
give the parameter in a small input file next to -r, not on the command line:
    printf '<fastflow>\ndiagnostics = true\n' > add.athinput
    athena -r <run>/rst/<base>.NNNNN.rst -i add.athinput [other overrides]
The continued run wrote <basename>.horizon_status_0.txt (header and one record per search, exit 0);
the same parameter on the command line exited with status 1. I have NOT checked that
scripts/submit_chain.sh passes an extra "-i" through to its continuation line: test a chain with
DRY=1 first, or continue your chain once by hand-written wrapper.

The source fix (a parameter added on the command line of a restart is accepted with a line in the
log) is item 1 of tracks/core/NEXT_SOURCE.md for core's next source session, with this test.
