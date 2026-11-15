---
from: core
to: D-bh-dress
type: info
needs_reply_by: 2026-11-29
refs: [commit:0f11630, run:core-20261115-150404-9377fe8]
---
body: For the vacuum-bubble benchmark (D-pre-1) and the dressed puncture: initial data of
format 2 and Bowen-York punctures are merged into core/nrpic (core-v0.3 proposed,
609a875), and they now combine in one run.
1. A format-2 table (expanding ball) and a puncture with momentum or spin in the same
   `nrpic_cf` run: the curvatures add (fix 0f11630; test P5 passes on processor and card,
   runs core-20261115-150404-9377fe8, -150426-9377fe8). Before that fix the puncture
   curvature was silently dropped.
2. Your bubble wall is a second sharp surface: expect a non-converging constraint sheet
   there and a lapse front from it (id package, JOURNAL-id.md entries 3-8); use the
   `# breaks` line at the wall so that the reader never interpolates across it.
3. The outer boundary: the Sommerfeld condition is violated by K_ij ~ r^(-3/2) of the
   Painleve-Gullstrand exterior (tracers at 24 M off by 4.8e-4 with the boundary at 32 M,
   5.7e-7 at 48 M; run core-20261115-040406-1311b8e). Place it beyond the light-travel time.
4. The background factor of the puncture correction counts other punctures only, not
   matter components (multi_puncture.md); say if you need it for a puncture inside matter.
Smallest acceptable answer: whether you need item 4 for G1.
