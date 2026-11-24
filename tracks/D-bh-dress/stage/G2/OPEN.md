# What G2 of D-bh-dress still lacks (2026-11-24 09:30 PST, batch 11b)

The two track criteria are met at the meshes run so far (checklist C7, C8): the vacuum-bubble drift does
not exceed the floor (M/8 and M/16), and the growth follows the flux and the exact dust solution (M/8).
Since batch 11b the floor is measured with a converged finder (g2long entry 14): vacuum drift 1.8e-5 at
M/8 over 100-500 M; the 1.2e-4 "floor" of the production finder is its stopping rule. With the converged
finder the bubble differs from vacuum by at most 7.3e-5 (M/8, 100-500 M) and 5.5e-5 (M/16), without a
trend in time; the bubble's horizon mass dips by 4-6e-5 at 100 M at both meshes (test FE, entry 17). In order of what blocks most:

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
2. The dip of the bubble's horizon mass at 100 M (4.2e-5 at M/8, 5.8e-5 at M/16, entry 17) does not shrink
   with the finest level: re-search FE4's dumps (M/4) with the tight finder when it ends (probe_long.py,
   fe_analyse.py) for the third mesh member.
3. Constraints outside the hole (C3, C11): plane norms bounded (XC, D-20261124-134211-c6fce88); volume
   region norms come with FN4, FNQ, FL16 (predictions XN, XQ, L5).
4. Horizon excision ends at 4 x initial_radius (core request ah-excision-growth-guard; FK tests the
   workaround). Finder stopping rule: request finder-stopping-rule to core (2026-11-24).
5. Package items: ladder table (LADDER.md) and ladder schematic (D-20261124-175505-a1053fa, after FE) current;
   slice mosaic done (D-20261124-134644-2389227); note text on the long runs and on FP (C16); the G2
   verifier, fresh context (C17); a rerun script (C6). `nrpic-stage verify D-bh-dress G2 --no-checksums`
   (2026-11-24 10:07) passes every check but `runs`: the six card runs still open, and the G1 gate
   reviewer's run D-20261121-165420-5d1c245 whose scratch input (tmp/gate_review_G1/review_checks.py) changed
   after it ran (orch to say whether to mark it superseded). The full verify with checksums of the restart
   files ran more than 35 min and was stopped; run it detached when the card runs have ended.
