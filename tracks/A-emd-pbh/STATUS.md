# STATUS of A-emd-pbh

gate:        G0 and G1 packages submitted for review 2026-11-15 (not passed): G0 all items PASS except C18 (no verifier recomputed the
             note's ledger); G1 track criteria T1-T3 met (T3 by decision 0013), open: data-flow schematic (C11) and verifier (C18)
headline:    First full-relativity runs of the expanding ball reproduce the exact turnaround to 0.07-0.18 per cent with core-shell
             errors converging at order 3-4, but no slicing reaches the first horizon (geodesic slicing blows up at t ~ 33 M, the
             conformal-time lapse sends a pulse from the core edge), and the periodic collapse S1 goes non-finite at 21.9 t_H.
last-result: dx = M/4 runs (A-emd-pbh-20261115-164539-0b18e84, -164541-0b18e84; analysis A-20261115-182657-53da696): SR-1 core
               turnaround -0.0125 M, core |R/R_exact - 1| at tau = 16.894 7.6e-4 (6.2e-3 at M/2); SR-2 +0.031 M, 3.7e-4.
             Lead's review (stage/REVIEW-wave2.md): every helper analysis reproduces exactly (six reruns) and the lead's own reader
               agrees (A-20261115-182314-bebd0cf); two conversion errors fixed (periodic: 1.2 and 36 t_H, not 1.5 and 45).
             Verifier's C1c and C4b confirmed and corrected (SCOPE.md 10.9): a q = 2 ball holds the particle bracket (0.045, 0.05].
             Newtonian mode: top-hat second order, t_ta +7.2e-4 at 128^3; 14 scan points within 6.3e-4 of the ellipsoid.
             Periodic: S2 (mu 0.03) 250 t_H no horizon, H_r max > 0.1 from 36 t_H; S1 (mu 0.3) non-finite at 21.9 t_H, UNDECIDED.
next:        1. Gauge: when core publishes a dust-proper-time or K_ref lapse (scratch/core/exe/core_gauge/), rerun SR-1 at dx = M/2
                with runs_ball/sr1.athinput and compare.py; until then nothing in the ball reaches a horizon.
             2. New ball data set "2h" whose first horizon is several M (heavier or wider core) for the G2 horizon-time and
                horizon-mass test; denser trajectory records near turnaround (traj_dcycle) before quoting a G2 order.
             3. Close the gate gaps: data-flow schematic (note/scripts/schem_dataflow.py, paperfig.py); a fresh verifier for the
                ledger, newton/ and criteria/ (asked of orch); note Sec. IV with the wave-2 runs, then ledger.py in stage/G0/VERIFY.
blockers:    core: a slicing that survives collapse (ball and box); stop on non-finite fields; nrpic_cosmo user_ref_func (AMR
               crash); periodic generator at the paper's start and for mu >= 0.5; constraint solve and lattice on refined levels.
             orch: verifier session for C18; ruling on G0/G1 with C18 open.
needs:       core (outbox 20261115T18*Z): gauge-expanding-ball, amr-for-first-horizon, stop-on-nonfinite,
               step-limit-coordinate-light-speed, processor-executable-threads, nrpic-cosmo-user-ref-func, periodic-horizon-finder,
               refined-mesh-diagnostics, phase1-generator-cmc, refined-level-constraint-solve, newton-mode-followup
             orch: decision-0013-reason (proposal), gate-review-g0-g1, harness-wave2-notes (info)
             kb: claim-status-s1 (claim 25 to verified)
offers:      expanding-ball data and exact LTB shells: tracks/A-emd-pbh/expball/ (data set 2t: scratch run A-emd-pbh-20261115-130609-947c898)
             invariant comparison of AthenaK ball runs (areal radius vs proper time, turnaround, trapping): tracks/A-emd-pbh/runs_ball/
             independent reader of trajectories/histories: tracks/A-emd-pbh/analysis/review_wave2.py
             Zel'dovich-deformed ball generator and Newtonian-mode analysis: tracks/A-emd-pbh/newton/ (make_deformed_ball.py, analyze_newton.py)
             EMD criteria with amplitude conversion and the LTB profile of arXiv:2609.14218: tracks/A-emd-pbh/criteria/
             periodic peak set-up and scouting analysis: tracks/A-emd-pbh/periodic_threshold/
budget:      1.115 card-hours used in wave 2 (nrpic-run budget: G2 0.95 of 60; 0.17 without gate); lead's checks on processors only
