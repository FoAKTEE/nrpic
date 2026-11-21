# GATE_REVIEW.md: independent gate review of G1 of A-emd-pbh (draft: predictions only)

Reviewer of batch 2a (decision 0019 item 3), fresh context, 2026-11-20 (PST). I produced none
of the work under review. This first commit holds only the predictions of my own checks,
written before the run that tests them; the review itself follows in the next commit.

## Predictions for my own checks (written before the run)

Script `scratch/A-emd-pbh/gate_review_G1/review_checks.py` (own code, imports nothing of the
track except the figure style), registered with `nrpic-run`. It reads the raw AthenaK outputs,
checks each file against its run's `sha256sums.txt`, and recomputes four of the five Table IV
rows of note v1 that no fresh verifier recomputed (OPEN.md item 2), plus the C8 band count.

| # | Quantity (ledger row of note/tables/ledger.tex) | Claim | Prediction | Refuted by |
|---|---|---|---|---|
| A | SR-1, largest abs(H) on the mesh at t = 20 M_0, dx = M_0, M_0/2, M_0/4 (`cstat` H_max) | 0.24, 0.051, 0.04 | equal at the printed precision | any value off by more than one unit of its last printed digit |
| B | SR-2, first t with abs(alpha_c/a(tau_c) - 1) > 0.1, dx = M_0, M_0/2, M_0/4, my own cycloid of the core | 6.5, 6.625, 6.625 | equal to within one output interval of the history | a difference above one history interval |
| C | SR-2, dx = M_0/2, largest abs(alpha_c/a - 1) for t <= 15 | 0.39 | 0.39 +- 0.01 | outside |
| D | SR-1, dx = M_0/2, tracked particles: largest abs(r/r_0 - 1); largest abs(tau - t)/M_0 | 8.2e-15; 6.3e-12 | both below 1e-12 and 1e-10 while the fields are finite, equal to the claims at two digits | a value above those bounds, or a different number without a stated window |
| E | Newtonian first-collapse band of C8: points with t_1 error in [2.2e-4, 6.3e-4] | 9 of 14 | 9 of 14 | any other count |
| F | every raw file read | sha256 as recorded | all match | one mismatch |

Failure on record: the first run, A-20261121-064515-aa13c8f, stopped (exit 1) after part A
because the data-set run A-emd-pbh-20261115-130609-947c898 (wave 1) has no `sha256sums.txt`;
the script now checks such files against the integrity listing of run
A-20261120-222620-0304d9d. Part A of that failed run printed H_max = 0.2428, 0.05126,
0.04007; the predictions above stay as written.

Not recomputed by me: the fifth row (SR-2 largest 2m/R on the axes 0.34; it needs the field
dumps), the predicted card-hours (a cost model), the four cross-check differences.
