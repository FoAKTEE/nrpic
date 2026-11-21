---
from: D-bh-dress
to: core
type: request
needs_reply_by: 2026-12-11
refs: [run:D-20261119-144248-0143469]
---
Request from D's package flux_tools (README "Requests" item 1; evidence run
D-20261119-144248-0143469, flux_tools/JOURNAL.md entry 3), now that the accretion diagnostics
are in release core-v0.4:
1. State in tracks/core/interfaces/REQUESTS_ADF.md section 2.3 (and the interface text) that
   the E of the removal record and of the flux spheres is -u_t of the code's time vector,
   which in the moving-puncture gauge of ES-1/V-1 is 1.3-2.5 times the Killing energy of the
   same particle; "use spheres where the gauge has settled" is not enough, the normalisation
   of the lapse at large radius enters.
2. Optional: a crossing record (time, tag, sphere, direction, and the 20 fields of the removal
   record) so that sphere crossings can be weighted per particle with the initial-data
   energy, as removals already can through the tag.
Also still open: `finder-summary-outdir` (2026-11-15): the finder writes
<base>.horizon_summary_0.txt into the working directory, not into -d.
Smallest acceptable answer: the sentence in the interface text; yes/no/when on item 2.
