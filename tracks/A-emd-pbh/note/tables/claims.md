# Claims of the lead's documents checked against the run outputs

Written by `note/scripts/ledger.py`; a claim agrees when the file value rounded to the printed
digits equals the printed value (`sig1`: same leading digit; `upper`: at most the bound).

68 claims, 66 agree, 2 disagree.

| Document | Quantity | Claimed | File value | Run | Agrees |
|---|---|---|---|---|---|
| STATUS.md:10 | core turnaround tau | 16.894 | 16.8938 | A-20261115-130948-5a2b58a | yes |
| STATUS.md:10 | first trapped tau | 44.349 | 44.3493 | A-20261115-130948-5a2b58a | yes |
| STATUS.md:11 | first trapped R_i | 2.742 | 2.74183 | A-20261115-130948-5a2b58a | yes |
| STATUS.md:11 | first trapped m | 0.0805 | 0.0805126 | A-20261115-130948-5a2b58a | yes |
| STATUS.md:11 | crunch | 44.454 | 44.4542 | A-20261115-130948-5a2b58a | yes |
| STATUS.md:11 | SR-1 card-hours | 0.15 | 0.146473 | A-20261115-130948-5a2b58a | yes |
| STATUS.md:11 | SR-2 card-hours | 0.16 | 0.156029 | A-20261115-130948-5a2b58a | yes |
| STATUS.md:9 | two generators agree to | 5e-15 | 4.77396e-15 | A-20261115-130257-a7374a4 | yes |
| STATUS.md:9 | two table rules agree to | 7e-18 | 6.93889e-18 | A-20261115-130257-a7374a4 | yes |
| STATUS.md:9 | three exact codes agree to | 1e-14 | 1.06581e-14 | A-20261115-130257-a7374a4 | yes |
| stage/G1/STATUS.md:14 | flat ball M order 2 | 2.00 | 2.00007 | A-emd-pbh-20261115-130402-f5566fb | yes |
| stage/G1/STATUS.md:14 | flat ball M order 4 | 4.00 | 3.99987 | A-emd-pbh-20261115-130402-f5566fb | yes |
| stage/G1/STATUS.md:14 | top hat H order 2 (smooth) | 2.00 | 1.99944 | A-emd-pbh-20261115-130402-f5566fb | yes |
| stage/G1/STATUS.md:14 | top hat H order 4 (smooth) | 4.00 | 4.00133 | A-emd-pbh-20261115-130402-f5566fb | yes |
| stage/G1/STATUS.md:14 | top hat M order 2 (smooth) | 2.00 | 1.99934 | A-emd-pbh-20261115-130402-f5566fb | yes |
| stage/G1/STATUS.md:14 | top hat M order 4 (smooth) | 4.00 | 3.99894 | A-emd-pbh-20261115-130402-f5566fb | yes |
| stage/G1/STATUS.md:14 | taper M order 2 (all cells) | 1.99 | 1.98993 | A-emd-pbh-20261115-130402-f5566fb | yes |
| stage/G1/STATUS.md:14 | taper M order 4 (all cells) | 3.90 | 3.89584 | A-emd-pbh-20261115-130402-f5566fb | yes |
| stage/G1/STATUS.md:14 | smoothed top hat H order 4, N=512 | 3.98 | 3.97784 | A-emd-pbh-20261115-122117-aa1c84d | yes |
| stage/G1/STATUS.md:14 | smoothed top hat M order 4, N=512 | 3.94 | 3.93914 | A-emd-pbh-20261115-122117-aa1c84d | yes |
| stage/G1/STATUS.md:15 | criteria checks passed | 33 | 33 | A-emd-pbh-20261115-130256-a7374a4 | yes |
| stage/G1/STATUS.md:15 | criteria failing ids | T1.2b, T2.2d, T2.4a, T2.4c | T1.2b, T2.2d, T2.4a, T2.4c | A-emd-pbh-20261115-130256-a7374a4 | yes |
| stage/G1/STATUS.md:65 | SR-2 coordinate turnaround | 13.82 | 13.8229 | A-20261115-130948-5a2b58a | yes |
| stage/G1/STATUS.md:68 | SR-2 coordinate crunch | 54.96 | 54.964 | A-20261115-130948-5a2b58a | yes |
| scope/SCOPE.md:47 | h-hat(0.2, 0) | 0.452 | 0.451747 | A-20261115-130252-7877b7a | yes |
| scope/SCOPE.md:60 | slope of read-off times | -1.31 | -1.31227 | A-20261115-130252-7877b7a | yes |
| scope/SCOPE.md:59 | read-off/top-hat range, mu <= 0.15 | 0.80-1.01 | (0.8016716027588598, 1.012282788272597) | A-20261115-130252-7877b7a | yes |
| scope/SCOPE.md:61 | mu_fd(250 t_H) | 0.048 | 0.0481321 | A-20261115-130252-7877b7a | yes |
| scope/SCOPE.md:61 | mu_fd scaled by measured ratio | 0.044 | 0.043683 | A-20261115-130252-7877b7a | yes |
| scope/SCOPE.md:63 | horizon time of mu = 0.045 (t_H) | 239 | 239.105 | A-20261115-130252-7877b7a | yes |
| scope/SCOPE.md:64 | horizon time of mu = 0.04 (t_H) | 285 | 285.311 | A-20261115-130252-7877b7a | yes |
| scope/SCOPE.md:135 | ball capacity q = 3, R_b H_i = 0.9 | 0.031 | 0.0305807 | A-20261115-130252-7877b7a | yes |
| scope/SCOPE.md:135 | ball capacity q = 2, R_b H_i = 0.9 | 0.069 | 0.0688065 | A-20261115-130252-7877b7a | yes |
| scope/SCOPE.md:136 | mean over central capacity | 2.7 | 2.71828 | A-20261115-130252-7877b7a | yes |
| scope/SCOPE.md:86 | mean-contrast formula error | 2e-4 | 0.00019838 | A-20261115-130252-7877b7a | yes |
| scope/SCOPE.md:153 | critical s, virial | 0.55 | 0.547723 | A-20261115-130252-7877b7a | yes |
| scope/SCOPE.md:227 | cost of the v19 run | 5.41 | 5.40985 | A-20261115-130252-7877b7a | yes |
| scope/SCOPE.md:227 | seconds per cycle | 0.761 | 0.76076 | A-20261115-130252-7877b7a | yes |
| scope/SCOPE.md:235 | modelled cost range | 1.1-3.5 | (1.1106044931609134, 3.5403350348592806) | A-20261115-130252-7877b7a | yes |
| scope/SCOPE.md:236 | median cost at 1e6 | 2.4 | 2.38719 | A-20261115-130252-7877b7a | yes |
| scope/SCOPE.md:237 | first scan card-hours | 155 | 155.167 | A-20261115-130252-7877b7a | yes |
| scope/SCOPE.md:230 | s per particle and step | 1.0e-7 | 9.78195e-08 | A-20261115-130252-7877b7a | yes |
| JOURNAL.md:95 | L4 turnaround (three codes) | 9.542048138750 | 9.54205 | A-20261115-130257-a7374a4 | yes |
| JOURNAL.md:95 | L4 trapping | 25.407847821 | 25.4078 | A-20261115-130257-a7374a4 | yes |
| JOURNAL.md:95 | L4 crunch | 26.897059616 | 26.8971 | A-20261115-130257-a7374a4 | yes |
| JOURNAL.md:98 | L5 y | 0.746379 | 0.746379 | A-20261115-130257-a7374a4 | yes |
| JOURNAL.md:98 | L5 R_max/R_i | 1.33980 | 1.3398 | A-20261115-130257-a7374a4 | yes |
| JOURNAL.md:98 | L5 tau_ta | 16.8938 | 16.8938 | A-20261115-130257-a7374a4 | yes |
| JOURNAL.md:98 | L5 tau_c | 44.4542 | 44.4542 | A-20261115-130257-a7374a4 | yes |
| JOURNAL.md:99 | L5 core edge trapped | 44.3815 | 44.3815 | A-20261115-130257-a7374a4 | yes |
| JOURNAL.md:101 | L6 exterior K | 4.3e-15 | 4.32987e-15 | A-20261115-130257-a7374a4 | **no** |
| JOURNAL.md:103 | L7 total mass | 1.00959 | 1.00959 | A-emd-pbh-20261115-153719-91b03d1 | yes |
| JOURNAL.md:104 | L7 rest mass | 1.01590 | 1.0159 | A-emd-pbh-20261115-153719-91b03d1 | yes |
| JOURNAL.md:108 | L8 largest relative deviation (per cent) | 0.17 | 0.166228 | A-20261115-130948-5a2b58a | yes |
| JOURNAL.md:109 | L8 conformal turnaround | 13.823 | 13.8229 | A-20261115-130948-5a2b58a | yes |
| JOURNAL.md:109 | L8 conformal core at tau_AH | 49.506 | 49.506 | A-20261115-130948-5a2b58a | yes |
| JOURNAL.md:109 | L8 conformal crunch | 54.964 | 54.964 | A-20261115-130948-5a2b58a | yes |
| JOURNAL.md:110 | L8 cfl 0.25 limit | 42.30 | 42.3039 | A-20261115-130948-5a2b58a | yes |
| JOURNAL.md:94 | L3 KL deviation at the sharp edge (units of H) | 0.1 | 1.36801 | A-20261115-130257-a7374a4 | **no** |
| runs_ball/JOURNAL.md:116 | runs_ball turnaround | 16.893769 | 16.8938 | A-emd-pbh-20261115-153719-91b03d1 | yes |
| runs_ball/JOURNAL.md:116 | runs_ball R_max/R_i | 1.339803 | 1.3398 | A-emd-pbh-20261115-153719-91b03d1 | yes |
| runs_ball/JOURNAL.md:116 | runs_ball first trapped | 44.349266 | 44.3493 | A-emd-pbh-20261115-153719-91b03d1 | yes |
| runs_ball/JOURNAL.md:117 | runs_ball first trapped R_i | 2.74175 | 2.74175 | A-emd-pbh-20261115-153719-91b03d1 | yes |
| runs_ball/JOURNAL.md:117 | runs_ball first trapped m | 0.080505 | 0.0805053 | A-emd-pbh-20261115-153719-91b03d1 | yes |
| runs_ball/JOURNAL.md:117 | runs_ball core edge | 44.381466 | 44.3815 | A-emd-pbh-20261115-153719-91b03d1 | yes |
| runs_ball/JOURNAL.md:118 | runs_ball crunch | 44.454205 | 44.4542 | A-emd-pbh-20261115-153719-91b03d1 | yes |
| runs_ball/JOURNAL.md:118 | runs_ball m_AH at crunch | 0.0960 | 0.0960184 | A-emd-pbh-20261115-153719-91b03d1 | yes |
| runs_ball/JOURNAL.md:121 | first trapped R_i: lead's run vs runs_ball's run | equal to the printed digits | 2.741829 vs 2.741747 | A-20261115-130948-5a2b58a / A-emd-pbh-20261115-153719-91b03d1 | yes |

Inputs read:

- `A-20261115-130252-7877b7a/scope/scope_numbers.json`: sha256 ok
- `A-emd-pbh-20261115-120425-80492f8/scan_summary.json`: no sha256sums.txt (wave-1 run)
- `A-emd-pbh-20261115-130256-a7374a4/results.json`: no sha256sums.txt (wave-1 run)
- `A-emd-pbh-20261115-130402-f5566fb/convergence.json`: no sha256sums.txt (wave-1 run)
- `A-emd-pbh-20261115-122117-aa1c84d/convergence.json`: no sha256sums.txt (wave-1 run)
- `A-20261115-130257-a7374a4/crosscheck.json`: sha256 ok
- `A-emd-pbh-20261115-153719-91b03d1/exact.json`: sha256 ok
- `A-20261115-130948-5a2b58a/scouting_predictions.json`: sha256 ok
