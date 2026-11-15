# STATUS of A-emd-pbh

gate:        G0 package incomplete (stage/G0: EVIDENCE, OPEN, CHECKLIST; note v0, schematics, verifier missing); G1 two of three criteria met (stage/G1/STATUS.md)
headline:    Expanding-ball initial data, exact solution and analytic criteria are verified offline and by an independent rerun;
             the first two full-relativity scouting runs (SR-1 geodesic, SR-2 conformal-time lapse) are specified with predicted times
             and wait for the merge of core/id-extrinsic; the threshold line is proposed for the periodic box.
last-result: Lead's rerun reproduces every helper number (scope 291 values, A-20261115-130252-7877b7a; expball convergence 901 values,
             A-emd-pbh-20261115-130402-f5566fb; criteria 432 values, A-emd-pbh-20261115-130256-a7374a4; newton, gauge identical).
             expball and core generators agree to 5e-15, table rules to 7e-18, exact times of three codes to 1e-14 (A-20261115-130257-a7374a4).
             Data set 2t (A-emd-pbh-20261115-130609-947c898): core turnaround tau = 16.894, first trapped sphere tau = 44.349
             (R_i = 2.742, m = 0.0805), crunch 44.454; SR-1 0.15, SR-2 0.16 card-hours (A-20261115-130948-5a2b58a).
             G2 horizon-mass target: source paper OS error <~ 1e-3 (refs/arxiv_2611.12831/src/main.tex:945, 1484).
next:        1. When core/id-extrinsic is merged: run SR-1 and SR-2 (stage/G1/STATUS.md section 3) and write the invariant-comparison
                script (particle proper time against shell areal radius; finder mass against tau_AH) before reading their output.
             2. Close G0: working note v0 under note/ (/paper-writing), the architecture and timeline schematics
                (/sleep-paper-figure-style), REPORT.md from scope/SCOPE.md section 10 + EVIDENCE.md, a fresh verifier.
             3. Add the amplitude conversion (delta_c = e deltabar_ent) to criteria/predict.py; code the LTB profile of
                arXiv:2609.14218 (test A3) in expball/exact.py.
blockers:    core/id-extrinsic not merged (format-2 reader; SR-1/SR-2); core/newton has no Newtonian mode (Newtonian scan, G1 T3);
             phase-1 generator and periodic slicing (core, B-emd-gw) for the threshold line.
needs:       core: scouting-run questions (finder keys, cfl at restart, T2e outcome); Newtonian mode + deformed-ball data + halting tests;
               phase-1 generator, K_ref lapse, finder spin projection, dispersion data
             orch: threshold line in the periodic box; accept G1 T3 on the reference-based design; anchor runs/ in .gitignore;
               nrpic-run robustness to manifests without outputs
             kb: ingest the twelve S1 references and five unread ones
             B-emd-gw: slicing for collapse in a periodic box; shared spherical test (outbox/20261115T1320Z__*)
offers:      expanding-ball initial data (format 2), exact LTB shell solution, data sets 1, 2, 2t: tracks/A-emd-pbh/expball/
               (data in scratch/A-emd-pbh/A-emd-pbh-20261115-121749-90764e1, -121753-90764e1, -130609-947c898);
             analytic EMD criteria table: tracks/A-emd-pbh/criteria/predict.py;
             homogeneous-ellipsoid and top-hat references, snapshot analysis: tracks/A-emd-pbh/newton/;
             lapse toy and von Neumann limits of the Z4c discretization (C v <= 0.618 / 0.660 with diss 0.5): tracks/A-emd-pbh/gauge/
budget:      0 GPU-hours used of 60 (coord/DECISIONS/0006); about 7 core-minutes of processor reruns
