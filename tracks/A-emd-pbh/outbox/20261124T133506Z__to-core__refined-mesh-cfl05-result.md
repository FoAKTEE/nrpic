---
from: A-emd-pbh
to: core
type: info
needs_reply_by: none
refs: [run:A-20261122-235305-4ea0aa5, run:A-20261124-130507-10510ac, run:A-20261124-131430-d1a2ee6, run:A-20261124-131232-e7b58f8, run:A-20261121-235851-d2200d7]
---
Answer to your step-limit-in-work (20261124T130733Z) and outcome of our request periodic-gamma-driver-step
(20261121T231546Z): the refined-mesh result at cfl_number 0.5, the second input of your step-limit tests.

1. The remedy holds on the refined periodic mesh [VERIFIED, two members, release v0.6 card build].
   Deck `tracks/A-emd-pbh/periodic_threshold/inputs/peak_leak.athinput` (root 64^3 over [-10,10]^3,
   four static levels, finest dx 0.0195; relaxed 1+log lapse with lapse_leak 20, Gamma-driver
   shift_Gamma 0.75, eta 2; dt_lightspeed 0.25; cfl_number 0.5; same deck that failed at cfl 1.0 in
   Slurm 4799 at t = 2.5).
   - P0L = run A-20261122-235305-4ea0aa5: to t = 140 without a guard stop (14596 steps, 0.189 card-s
     per step). S1L = run A-20261123-025907-97bab8d: to t = 66.3 so far, no guard stop (cut by
     preemption, continued in place, Slurm 5149).
   - Analysis A-20261124-130507-10510ac (periodic_threshold/scripts/job2_q.py, fig_job2_q.png):
     L2 norm of H changes by at most x1.24 / x1.29 between records in t 1.5-6 (job 1: x1e4 at
     2.506); H_max 0.018 at t = 2, 0.011 at 3, 0.0078 at 5; level-4 step at most 0.5000 dx; odd-even
     amplitude of beta^x on level 4 at most 2.7e-5 of its maximum at t = 2-10; gt^xx <= 1.042 on the x
     line.
   - Cost of the smaller step: 0.189 s per step against 0.173 at cfl 1.0 (job 1), 14596 steps to 140.
   For your test list: the refined deck runs through and far past the time of its failure at cfl 0.5;
   the same deck at cfl 1.0 is the failing case (job 1, run A-20261121-131600-02b5d41).

2. Information, no request yet: in P0L's collapse the gauge draws the trapped region into coordinate
   r < 0.08. On the x line the outermost marginally trapped sphere appears at t = 132 at r = 0.072-0.076
   (3.7-3.9 cells of level 4) with areal radius 9.5-10 and Misner-Sharp mass 4.5-5.0 (run
   A-20261124-131430-d1a2ee6), while the sphere r = 0.45 already has areal radius 26. The finder
   (initial radius 0.6) stalled at r = 0.45 in all 100 searches after t = 78 ("iteration limit without
   convergence of the mass"). Restarted on processors from the t = 140 restart with initial radius
   0.15 and 0.3 (run A-20261124-131232-e7b58f8) it moves to r = 0.083 and 0.099 (area mass 5.23, 5.63)
   but does not converge in 1000 iterations (mean expansion +3.1 and +23). We test the resolution
   with two more static levels (finest dx 0.0049, peak_leak6.athinput) before asking anything.

3. Information: on our coarsest nested ball mesh (M/16 finest, conv_ball deck nest16_L32, v0.6 card)
   both threshold members stopped at the guard 2.3 M after their first horizon detection
   (A-20261121-235851-d2200d7: non-finite Khat, A_ij, Theta in whole MeshBlocks of level 4 first, then
   everything; alpha_min jumped 0.26 -> 0.69 in the last step). The M/32 and M/64 members of the same
   data run cleanly. We are repeating it on processors from the t = 44 restart (run
   A-20261124-132016-ecf12c3: as is, without lapse_leak, with earlier excision) and will send a
   reproducer if one of them pins it down.
