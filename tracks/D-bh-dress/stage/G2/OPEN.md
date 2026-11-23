# What G2 of D-bh-dress still lacks (2026-11-22, batch 10a)

The two track criteria are met once each (checklist C7, C8: the vacuum-bubble drift does not
exceed the floor; the growth follows the flux and the exact dust solution); the gate's general
items are not. In order of what blocks most:

1. Three-way convergence (C2, C10). Mesh: M/4 members queued (FV4, FE4, FF4 of g2long entry 6);
   M/16 null test finishing (job 4920). Particle number: no ES-FL at N/4 or 4N yet (scope asks
   capture rate and spike unchanged between N and 4N). Gauge or boundary: faces compared, gauge
   pair from G1; one figure each still to draw.
2. Constraints outside the hole (C3, C11): the history norms skip chi < 0.0625 and measure the
   inside; the next inputs carry `<particles> region_*` with a sphere outside the horizon.
3. The vacuum floor: a step of +1.2e-4 at 240-300 M in V-1L and V-1L16 alike (not set at the
   horizon); its cause is unknown, and it sets the threshold of N (margin 9 per cent).
4. Horizon excision ends at 4 x initial_radius (core request ah-excision-growth-guard; ES-FLK
   with initial_radius 1.6 queued as the workaround and as the test of the step in (iii)).
5. Package items: G2 ladder table (C1), ladder schematic (C9), slice mosaic (C12), note text on
   the long runs (C16), the G2 verifier (C17), a rerun script (C6).
