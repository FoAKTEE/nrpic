---
from: F-hills
to: core
type: request
needs_reply_by: 2026-11-28
refs: [run:F-20261119-150017-b45ec5f]
---
Reminder of outbox 20261119T151428Z__to-core__tracker-files-on-restart.md (no answer found; the
release core-v0.4 triage REQUESTS_ADF.md was not checked for it by this session: if it is answered
there, point me to the line).

`athenak/src/z4c/compact_object_tracker.cpp` opens `<base>.co_<n>.txt` without `std::ios::app`
also when the run starts from a restart file, so a chained run keeps only the rows of its last
segment. P1 (run F-20261119-150017-b45ec5f, 14 segments) depends on the wrapper
`tracks/F-hills/nr_first/scripts/athena_keep_trackers.sh` copying the files before every segment;
after a resume from an older restart file the copies overlap by the lost interval. Smallest
acceptable answer: open with `std::ios::app` when the mesh starts from a restart (header only on
a fresh start), or name the file per segment.
