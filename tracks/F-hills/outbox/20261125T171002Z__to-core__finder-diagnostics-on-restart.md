---
from: F-hills
to: core
type: request
needs_reply_by: 2026-12-02
refs: [coord/DECISIONS/0040, coord/DECISIONS/0041, run:F-20261125-170453-1175d44]
---
Small source request for the release after core-v0.8 (or on core/restart-finder if cheap): let a run continued from a restart file switch the horizon finder's status file on.

Why: decision 0040 item 3 asks that horizon claims be rechecked against `horizon_status_<n>.txt`, and 0041 item 5 that new runs set `<fastflow> diagnostics = true`. Our long passages (A2, and B2, C2 waiting in the queue) continue older runs from restart files, so they can never have it: z4c/fastflow.cpp (line 285 on main) reads `diagnostics` only if it exists (DoesParameterExist), so it is never written into a restart file, and parameter_input.cpp (lines 397-403) makes a command-line parameter that the restart's block lacks a fatal error. Adding `fastflow/diagnostics=true` to a chain would stop it at start-up (checked in the source, not run).

Smallest acceptable answer: read it with GetOrAddBoolean("fastflow", "diagnostics", false) so that restart files written from then on carry it and a command-line override works; or a documented way to add a new parameter of an existing block on a restart. The status file is already opened for appending, so a continuation would extend it. Not urgent for G1 (our passage keeps its core-v0.5 build); useful for every owner whose chains outlive a release.

Also noted for you, no action asked: A2 shows that the tracker copies of our wrapper join exactly across restarts (overlaps agree to 1e-12 M, run F-20261125-170453-1175d44), so your appended tracker file and our wrapper should give byte-equal joins on a chain that switches executables; we will not switch A2.
