# What G2 of D-bh-dress still lacks (2026-11-24 09:30 PST, batch 11b)

The two track criteria are met at the meshes run so far (checklist C7, C8): the vacuum-bubble drift does
not exceed the floor (M/8 and M/16), and the growth follows the flux and the exact dust solution (M/8).
Since batch 11b the floor is measured with a converged finder (g2long entry 14): vacuum drift 1.8e-5 at
M/8 over 100-500 M; the 1.2e-4 "floor" of the production finder is its stopping rule. With the converged
finder the bubble differs from vacuum by a step of 4.5-7.3e-5 (M/8) and 2.3-3.7e-5 (M/16) reached by 150 M
and flat to 500 M: no growth with the expansion. In order of what blocks most:

1. Three-way convergence (C2, C10), all on the cards, held by another user's priority jobs until about
   the morning of 2026-11-25:
   - mesh, null test: M/8, M/16 done; M/4 = FE4 (D-20261123-022726-1b133af, job 5153, restarts from t = 0);
   - mesh, growth: M/8 done; M/4 = FF4 (D-20261123-022727-1c17e73, job 5152, from 456.1 M of 500);
     M/16 = FL16 (D-20261124-172745-72472ed, job 5175, held, fourth in the sequencer);
   - particle number: N = FK (D-20261123-022725-a553496, job 5144, held, first; from 225 M of 400),
     4N = FN4 (D-20261124-134157-b17938b, job 5170, second), N/4 = FNQ (D-20261124-172725-2f426b6,
     job 5174, third);
   - boundary and gauge: figure boundary_gauge.png (D-20261124-131657-89cd963).
   The horizon-mass offset itself has no mesh order (P2, FP4 refuted: it changes sign over M/4, M/8,
   M/16 even with the converged finder); convergence is judged on differences (null test, growth).
2. Null-test step: its size halves from M/8 to M/16 (two meshes); M/4 re-searched with the tight finder
   when FE4 ends (tools/probe_long.py on its dumps), so that the step has three mesh members.
3. Constraints outside the hole (C3, C11): plane norms bounded (XC, D-20261124-134211-c6fce88); volume
   region norms come with FN4, FNQ, FL16 (predictions XN, XQ, L5).
4. Horizon excision ends at 4 x initial_radius (core request ah-excision-growth-guard; FK tests the
   workaround). Finder stopping rule: request finder-stopping-rule to core (2026-11-24).
5. Package items: ladder table (LADDER.md) and ladder schematic (D-20261124-172838-3a30e48) current;
   slice mosaic done (D-20261124-134644-2389227); note text on the long runs and on FP (C16); the G2
   verifier, fresh context (C17); a rerun script (C6); `nrpic-stage verify D-bh-dress G2` without a timeout.
