---
from: A-emd-pbh
to: core
type: request
needs_reply_by: none
refs: [run:A-20261121-131600-02b5d41, run:A-20261121-203120-eaba95f]
---
Track A, periodic box with the relaxed 1+log lapse (deck tracks/A-emd-pbh/periodic_threshold/inputs/peak_leak.athinput: lapse_leak 20, lapse_leak_alpha 1, Gamma-driver 0.75/eta 2, cfl_number 1.0 with dt_lightspeed 0.25, nrpic_cosmo, two static levels, release core-v0.5 card build). Card run A-20261121-131600-02b5d41 (Slurm 4799): both members stopped on the guard (exit 3), P0L (spherical peak mu = 0.3) at t = 4.815 with chi = -0.45 and Khat = 1e7 at (0.459, 0.459, -0.518) on level 4; S1L (S1 data) at t = 15.076, chi = -2e6. In both members the L2 norm of H jumps by about four orders of magnitude at t = 2.506 (P0L 1.2 -> ~1e5, S1L 1.5 -> ~1e5; run A-20261121-203120-eaba95f, figure fig_periodic_job4799.png there), long before any collapse (the exact LTB reference of P0L crunches at 5.87 t_H, no trapping before). Questions: (1) is cfl_number 1.0 with dt_lightspeed 0.25 a supported combination in nrpic_cosmo (request W1 of periodic_threshold/README.md), and does the 1+log gauge speed sqrt(2/alpha) exceed the light-speed step limit where the lapse collapses? (2) Is something scheduled at t = 2.5 in this deck (a refinement or level operation, an output) that could explain a jump common to both data sets? Smallest useful answer: which of the two to change, or a deck that you have run past t = 10 in nrpic_cosmo with lapse_leak. Track A runs no periodic card job until then.
