# STATUS of A-emd-pbh

gate:        G0 PASSED 2026-11-19 (coord/GATES.md, tag stage/A-emd-pbh/G0-pass-20261119). G1 package complete for sign-off
             2026-11-21: independent gate review PASS WITH RESERVATIONS (stage/G1/GATE_REVIEW.md), its condition C20 closed by
             the lead of batch 2b; C11, C18 PASS. G2 in progress (horizon formation of the spherical ball).
headline:    The baseline of G1 holds and reproduces bit for bit (verifier, close-out, reviewer and Szekeres reruns); in full
             relativity the expanding ball turns around as the exact solution says, and with the relaxed 1+log lapse and one
             static level of M/16 (BH-1R) a persistent apparent horizon forms at t = 10.875 whose mass follows the exact mass
             of its slice to better than 1e-3 after t ~ 11.7 M (runs_ball A-20261121-081153-b92c08c, re-checked in
             A-20261121-082814-6fadb30; one resolution, not yet independently verified); no run has reached a horizon in the box.
last-result: Lead re-check (runs A-20261121-075605-351d611, repeat -075933-338a6ff; stage/REVIEW-wave3.md): L1-L9 hold.
               G1 verifier rerun identical: ledger 39 confirmed / 2 wrong (corrected) / 1 not confirmed (card-hour model);
               criteria 19/19, Newtonian mode 17/17, ball 12/12. Gate reviewer's checks A-F identical. Wave-1 outputs
               unchanged since their listing (55 files). Szekeres LTB limit, dipole order, error budget identical; 15/15 tests;
               N = 32 geodesic slicing non-finite from tau = 26 (own reader).
             G1 track criteria: T1 constraint orders 2.00/4.00 (flat ball), 3.98/3.94 (smoothed top hat 256->512);
               T2 criteria 41 of 41 checks with 4 diagnostics (after two bands restated to the plotted window, two failures
               turned diagnostics, prediction F5 partly refuted; wave 1 was 33 of 37); T3 met by decision 0013, and the
               Newtonian mode puts the first-collapse time of 9 of the 14 scan points within +2.2e-4 to +6.3e-4 of the
               isolated ellipsoid (spindle +1.5e-3; 64^3 controls +8.8e-4, +1.5e-3; 3.4e4-particle controls -2.4e-4,
               -4.6e-4; run A-20261120-222454-d16dbc6).
             Units: masses, radii, times of the scouting data in M_0 = 1 (total mass 1.0096 M_0).
             SR-1 (geodesic slicing) breakdown at dx = M / M/2: first non-positive metric determinant t = 30.25 / 32.875,
               norm(H) > 1e10 at 30.5 / 33.0, first non-finite line output 31.0 / 33.25. SR-2 turnaround at dx = M/4 with the
               window-free estimators (runs_ball entry 18, A-20261121-081138-ebe70b4): +0.0178 M for the secular turnaround
               (prediction R2 holds), +0.035 M for the local maximum (fails).
             runs_ball (batch 2b, re-checked): BH-1 on uniform meshes M/4-M/8 forms no apparent horizon and breaks down at
               t = 14.3-15.0; SR-1L (relaxed lapse) carries data set 2t to within 1 M of first trapping; at a fixed box the
               core error converges at order 3.7 and 2.6 (entry 19, A-20261121-081605-f95b10c).
             Stranded runs closed: Szekeres files A-20261120-223422-8cc4241 (mass converged to 2e-10), periodic P0L data
               A-20261120-223123-f436c39 (prediction D3 holds: residuals 6e-12, c = 0.088, alpha_min 0.805).
next:        1. Horizon formation in the ball (G2): verify_bh resumes from its journal entry 2 (registered C1-C5, VERIFIER.md:
                the independent check of BH-1R); conv_ball analyses its card job 1 (Slurm 4776) and runs member C, with
                hmean_tol_0 = 1e30 in new decks; report the horizon time and mass errors with their N and dx dependence.
             2. Szekeres card series (64^3-256^3 to tau = 40, files ready in A-20261120-223422-8cc4241, about 1.2 card-hours)
                and the periodic P0L run with the relaxed lapse against its LTB reference (periodic_threshold, files stranded).
             3. Before G2: redraw the architecture schematic against core-v0.5; rerun the wave-1 producers through nrpic-run;
                constraints of data set 2t in dx with core-v0.5 region norms; SR-2 turnaround with the window-free estimator.
blockers:    none from core for the ball (lapse_leak, guard, finder status, dt_lightspeed, AMR in nrpic_cosmo now released in
               core-v0.4/v0.5). Box: a slicing that keeps the Hamiltonian constraint below order one after t = 9 in S1
               (core message 20261120T223017Z item 2); periodic generator for mu >= 0.5 (core/id-solver-2, not released).
             orch: sign-off of G1 (no waiver needed: the four manifests the reviewer found open are closed).
needs:       orch: g1-sign-off-and-waivers (outbox 20261121T08*Z)
             core: open requests of 2026-11-15 served by core-v0.4/v0.5 are to be re-triaged by core (REQUESTS_A2.md); new:
               none this session
             kb: Szekeres slice conformal flatness and apparent horizon versus R = 2M (szekeres/README, unchanged)
offers:      expanding-ball data and exact LTB shells: tracks/A-emd-pbh/expball/ (data sets 2t and 3)
             invariant comparison of AthenaK ball runs: tracks/A-emd-pbh/runs_ball/ (compare.py, turnaround.py)
             quasi-spherical Szekeres reference solution, conformal map, NRCOSMO1 files: tracks/A-emd-pbh/szekeres/ (to B)
             EMD criteria with amplitude conversion and the LTB profile of arXiv:2609.14218: tracks/A-emd-pbh/criteria/
             periodic peak set-up (P0L spherical peak data, tracked axes): tracks/A-emd-pbh/periodic_threshold/
             lead's re-check tool (reruns compared value by value): tracks/A-emd-pbh/analysis/review_wave3.py
budget:      card-hours G2: 1.92 used (0.95 wave 2; jobs 4642 0.45, 4665 0.50, 4748 0.02) of 60; this session 0; no card job of
               A queued at 2026-11-21 00:30 PST. Processors: this session 4 cores for 2 x 3.5 min.
