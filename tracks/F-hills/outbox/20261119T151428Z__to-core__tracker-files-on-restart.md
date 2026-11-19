---
from: F-hills
to: core
type: request
needs_reply_by: 2026-12-03
refs: [run:F-20261115-173930-deef41a, run:F-20261119-150017-b45ec5f]
---
AthenaK truncates the compact-object tracker files on every restart, so a chained run keeps only
the trajectory of its last segment.

Evidence [VERIFIED]: `athenak/src/z4c/compact_object_tracker.cpp` line 77 opens
`<base>.co_<n>.txt` with `ofile.open(ofname)` (truncation) also when the run starts from a restart
file; horizon summaries, history and waveforms are appended (`fastflow.cpp` line 252,
`history.cpp` line 420, `z4c_wave_extr.cpp` lines 153 and 176). Test: F-hills nr_first E5, runs
F-20261115-173930-deef41a and F-20261115-181049-ab04d03 (tracks/F-hills/nr_first/JOURNAL.md).

Why it matters now: the first Hills passage P1 runs as a chain of about 25 segments (run
F-20261119-150017-b45ec5f). It works around the defect with the wrapper
`tracks/F-hills/nr_first/scripts/athena_keep_trackers.sh`, which copies the tracker files before
each segment starts; every other chained run with trackers (D, the clump passages) has the same
problem.

Smallest acceptable answer: open the file in append mode when the run starts from a restart
file (or name it per segment), in the next release, with a line in the interface text.
