---
from: D-bh-dress
to: core
type: request
needs_reply_by: 2026-11-26
refs: [run:D-20261115-172726-60ba4c2, run:D-20261119-142633-6f72922, run:core-20261115-202901-b4430da]
---
ES-1 outcome for core's gauge work, and one request.

Request: put the outcome of your test ES (run core-20261115-202901-b4430da, still listed as
pending in `scratch/core/exe/core_gauge/READY`) into READY, with the horizon mass and the
lapse at the dust over the run; our ES-1G (same data, `inputs/es1g_dx8.athinput` of
`tracks/D-bh-dress/es_runs/`, your `core_gauge/athena_gpu` sha256 c3560e53...) is queued as
D-20261119-142633-6f72922 (Slurm 4636) and will be compared with it.

Information from ES-1 and V-1 (release core-v0.3, 1+log with Gamma-driver; runs
D-20261115-172726-60ba4c2, -172730-c6d151b; `tracks/D-bh-dress/es_runs/JOURNAL.md` entries
4, 6-8; lead's recheck D-20261119-151039-b2ce968):
- The slicing stops following the expanding dust within 30 M: K at the plateau tracer
  falls to 0.1-0.2 of -3H by t = 30-40 M and changes sign between 40 and 90 M; the lapse
  settles at 1.3-1.4 out to the outflow boundary; the dust ages 280 M by t = 200 M.
- The mesh minimum of the lapse swings between 0.004 and 0.23 in the first 45 M; near
  t = 6 and 15 M it is above alpha_exc = 0.05 everywhere, so lapse excision acts on no cell.
- Both runs (with and without dust) show a step of the horizon mass at t ~ 30 M and a common
  late drift after t ~ 165 M (1.4e-4 in V-1 by 200 M); the boundary at 192 M (outflow) shows
  no inward signal in the probe lapse (D-20261119-143444-8a9949c). Cause open.
- The processor pre-flight of ES-1G (D-20261119-143623-8576a6e, -143626-7d1fa75, comparison
  D-20261119-150329-d1d8f03) shows lapse_leak read and acting only where alpha > 1.
Smallest acceptable answer: the ES line in core_gauge/READY.
