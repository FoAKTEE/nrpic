# Numbers of the lead's documents checked against the run outputs

Written by `note/scripts/ledger.py`. Paths relative to `tracks/B-emd-gw/`. Where the document and the file disagree, the file wins.

24 of 28 agree at the precision stated.

| Document:line | Stated | From the files | Agree | Note |
|---|---|---|---|---|
| stage/G0/REPORT.md:46 | [0.81, 3.57] | [0.81, 3.569] | yes |  |
| stage/G0/REPORT.md:50 | [0.0013, 0.21] | [0.001289, 0.2112] | yes | the values are box means (`Hr_mean`, `Mr_mean`); the dumps place most of the violation in the void |
| stage/G0/REPORT.md:50 | [30, 30] | [30.35, 33.47] | yes |  |
| stage/G0/REPORT.md:132 | [0.018, 0.36, 5.8, 0.36] | [0.0175, 0.3617, 5.787, 0.3617] | yes |  |
| stage/G0/REPORT.md:134 | [0.037, 0.76, 12.1, 0.76] | [0.03662, 0.7567, 12.11, 0.7567] | yes |  |
| stage/G0/REPORT.md:134 | [0.48] | [0.481] | yes |  |
| stage/G0/REPORT.md:88 | [1e-07, 1e-07] | [1.914e-07, 7.002e-08] | NO | order of magnitude only: the value at a = 4 is 1.9e-7 |
| stage/G0/REPORT.md:90 | [3e-07, 1.2e-06] | [2.974e-07, 1.248e-06] | yes |  |
| stage/G0/REPORT.md:91 | [1e-12] | [1.254e-12] | yes | largest transverse velocity 1.3e-12 (96 cells, a = 26.3); positions to 4.5e-14 L |
| stage/G0/REPORT.md:119 | [0.018] | [0.01818] | yes |  |
| stage/G1/STATUS.md:16 | [48, 2.6e-12] | [48.0, 2.627e-12] | yes |  |
| stage/G1/STATUS.md:20 | [3e-07, 1.2e-06, 6e-07] | [2.974e-07, 1.248e-06, 5.932e-07] | yes |  |
| stage/G1/STATUS.md:22 | [0.01] | [0.0955] | NO | the production phase error at 64 cells departs by 9.5 % (periodic_z4c/README.md says "10 percent for the production phase at 64"); the other errors to 1 % |
| stage/G1/STATUS.md:38 | [0.034] | [0.03365] | yes |  |
| stage/G1/STATUS.md:39 | [3e-13] | [2.591e-13] | yes |  |
| stage/G1/STATUS.md:40 | [0.01, 0.0009] | [0.01052, 0.0009455] | yes |  |
| stage/G1/STATUS.md:41 | [21.027] | [21.03] | yes |  |
| stage/G1/STATUS.md:43 | [0.001] | [0.001016] | yes |  |
| stage/G1/STATUS.md:45 | [0.00041] | [0.0004077] | yes |  |
| stage/G1/STATUS.md:53 | [1.9e-07, 7e-08] | [1.914e-07, 7.002e-08] | yes |  |
| stage/G1/STATUS.md:80 | [0.48] | [0.481] | yes |  |
| stage/G1/STATUS.md:49 | [144, 392] | [143.7, 391.6] | yes |  |
| STATUS.md:35 | [0.48] | [0.481] | yes |  |
| stage/G0/REVIEW.md:66 | [-1.64e-10, -9.87e-10] | [-1.645e-10, -9.87e-10] | yes |  |
| stage/G0/REVIEW.md:38 | [1.3858e-05] | [1.386e-05] | yes |  |
| tracks/B-emd-gw/verify_cosmo/JOURNAL.md:131 | [16.1] | [16.13] | yes |  |
| stage/G1/STATUS.md:56 | [1.6e-09, 1.1e-10, 3.2e-11] | [1.61e-09, 1.05e-10, 3.19e-11, 3.11e-08, 2.48e-09, 2.98e-09] | NO | values at t = 100 Mpc/h, early in the run (agree there: yes); at the end of the thousandfold expansion (t = 3000 Mpc/h) the relative Hamiltonian constraint is 3.1e-8, 2.5e-9, 3.0e-9 and does not fall from 16 to 32 cells; the fourth-order convergence holds for the error of chi (cosmo/analysis/daverio_a.json, committed file of the cosmology extension) |
| stage/G1/STATUS.md:47 | not on main | on main (release core-v0.3) | NO | written before wave 1 was merged; the mode, its interface document coord/INTERFACES/newtonian_mode.md and the quadrupole history are on main now |
