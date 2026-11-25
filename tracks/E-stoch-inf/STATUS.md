# STATUS of E-stoch-inf

gate:        G0 PASS (2026-11-20), G1 PASS with reservations (2026-11-21), G2 PASS with
             reservations (2026-11-24; coord/GATES.md, decision 0038, tag G2-pass-20261124).
             U-A4'(a) stays FAILED as written in the gate record. G3: scope fixed (SCOPE 4d),
             pilot queued; no G3 result yet.
reproduction: complete (decision 0028); working note repro/note/manuscript/main.pdf (32 pages).
last-result: Lead batch 17 (2026-11-25 03:46-04:40 PST):
             - Gate review corrections F1-F4 made (note eq. floor with 1/3 and max; STAGE_REPORT
               verdict/figures/decision; fig_ladder box 1; ledger rows name the estimator);
               note rerun R17 E-20261125-115608-b9c1b59 (repro/note/JOURNAL.md 27-28).
             - Floor (R28) at 128 ANSWERED: FL128h E-20261125-041742-71d74fb read by
               E-20261125-115344-a22128b: ratios 1.90 and 2.00, signs kept, control 0.97: second
               order in the amplitude (floor/JOURNAL.md entry 3). The first reading doubled the
               amplitude factor (recipe error, caught by control F3; entry 2; risk R32).
             - G3 scope SCOPE.md section 4d (cbe20398, pushed before any G3 submission): exceedance
               fractions F_pm(nu) of R^NR and zeta, nu = 3, 4 judged; S = 256 seeds of 128^3 from
               the power estimate E-20261125-115822-29795d6 (W2, W3 failed: cells nearly
               independent); one-patch delta-N reference, 128 band pilot E-20261125-115707-b845282
               (L1-L4 hold; lattice variant 0.980, R33); three-amplitude constraint criterion over
               cN 2.0-6.6; Richardson in s^2 (128 vs 160); gauge leg lapse_kdriver = 2; level 2 as
               sensitivity; budget about 14 of 60 card-hours.
             - g3/read_seed.py on existing USR output (E-20261125-120930-980b18e): R^NR Gaussian
               to one-box precision (sigma/sigma_lin 1.002, 1.001; F(3)/Q(3) 1.02-1.05); zeta next.
             - Provenance of the superseded level-2 executable: kept by core at
               core_noise-level2_6ca93cba (hash equal to the seven manifests, checked); asked core
               to confirm, orch for a harness pointer.
card plan:   q0038 FL256h submitted (job 5284, run E-20261125-115534-8414659, priority 2);
             q0045 G3P waiting (priority 5, one batch job, 14 runs, <= 0.95 card-h).
runs pending: q0038 (read by floor/floor_read.py, floor/JOURNAL.md entry 4 to come);
             q0045 (read by the g3 reader still to be written; predictions g3/JOURNAL.md entry 2).
next:        1. Read FL256h with floor_read.py (--pair FL256:<CL256S dir>:<FL256h dir>); F1 at
                256, F4; then replace the note's 'open' sentence on the floor.
             2. Write the g3 reader (R^NR, zeta, exceedances per seed) with its two processor tests;
                read the pilot; replace the cost of 4d.8 by the measured one.
             3. G3 reference: 4e6 direct + importance sampling for the 128 band; the model check
                (TO VERIFY of 4d.3); then queue the baseline 256 seeds.
blockers:    none (the G3 full set waits for the pilot and, if orch wants it, a look at SCOPE 4d).
needs:       core: nothing open (provenance of the level-2 build supplied 2026-11-25, acknowledged).
             orch: ruling or review of SCOPE 4d; harness pointer for moved executables.
offers:      - repro/: the reproduction of both papers (scripts, readers, ledger, verifiers).
             - g2prod/: release ladder and its judges; floor/: the half-amplitude reader.
             - langevin/, repro/langevin/: stochastic delta-N statistics (to A); now with the
               128^3 band (results/ref_inflection_n32.json).
budget:      G2 allotment closed at 19.6 card-hours of 30; G3 allotment 60 card-hours (0038):
             pending FL256h (<= 1.0, a G2-gate run) and G3P (<= 0.95). This session: 0 card-hours
             of finished runs, processors only (at most 4 cores).
