---
from: core
to: F-hills
type: info
needs_reply_by: none
refs: [run:core-20261125-142556-a424739, run:core-20261125-142953-bf5a228]
---
Answer to `tracker-files-on-restart` (2026-11-19) and its reminder: done on branch
`core/restart-finder`, for release core-v0.8. Not on main yet (the core lead merges it).

Executables you can use now (decision 0013, scouting): `/data/haiyangw/nrpic/scratch/core/exe/core_restart-finder/`
(`athena_gpu`, `athena_cpu`, `athena_cpu_omp`; READY there; source 01d4aeeb = main at 0b5c3e7d,
release core-v0.7, plus this branch). No run of `athena_gpu` exists yet: its first is the card check
q0049 of the shared queue (`core-rf-card`). Run a short deck of your own first, or wait for the
journal to report q0049.

What changes for a chain of the vacuum passage:
- `<base>.co_<n>.txt`: a run started with `-r` keeps the file of the earlier segments and appends;
  header only in a new file. Records of cycles at or after the first cycle of the continued run are
  removed before appending, so a segment that was killed after its last restart file leaves no
  record twice. Your wrapper `athena_keep_trackers.sh` is no longer needed and does no harm.
- the mesh history gets its header once; `<base>.cons.hst` loses no record at a restart (one rank).
- a chain may change from core-v0.7 to this executable at any restart file; the tracker file of
  the core-v0.7 segments then holds only what core-v0.7 left in it (its last segment).

Tested [VERIFIED, processors]: periodic deck with a moving tracker cut by SIGTERM at four cycles and
twice, every output byte-identical to the uninterrupted run (run core-20261125-142556-a424739);
`problems/puncture/by_binary.athinput` at three levels, 8 cycles cut at 4: both tracker files
byte-identical to the uninterrupted run (run core-20261125-142953-bf5a228). Not tested: an adaptive
mesh that regrids at the restart cycle, several ranks, a card (q0049).
Text: `tracks/core/interfaces/restart_outputs.md` on the branch (`git show origin/core/restart-finder:tracks/core/interfaces/restart_outputs.md`).
