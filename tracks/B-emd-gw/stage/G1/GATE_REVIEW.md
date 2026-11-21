# GATE_REVIEW.md: independent gate review of G1 of B-emd-gw

Reviewer of batch 6 (decision 0019 item 3), fresh context, 2026-11-21 from 21:14 UTC. I
produced none of the work under review. No tag `stage/B-emd-gw/G1-pass-*` existed when I
started (`git tag -l 'stage/B-emd-gw/*'`: only `stage/B-emd-gw/G0-pass-20261119`). Worktree
after `git merge --no-edit main`: 43834604.

This first version holds only the predictions of my own check, committed before the check
runs (CLAUDE.md rule 5). The verdicts follow in the next version of this file.

## 1. My own check: predictions (written before the run)

Script `scratch/B-emd-gw/gate_review_G1/review_checks.py` (own code; it imports AthenaK's
upstream reader `athenak/vis/python/bin_convert.py` and a copy of
`harness/style/figstyle.py`, nothing of the track). To be registered with `nrpic-run`.

### Check F: criterion 1 on test F (oblique flat wave k = 2 pi (1,1,1), elliptic)

Data: the raw double-precision dumps of runs B-20261119-142016-ee73a03 (N = 16, 32),
B-20261119-142233-70d5043 (N = 48), B-20261119-142124-feb2daf (`flatN64`). Own TT projector
at +k, own helicity basis (m = (e1 + i e2)/sqrt 2, e_R = m m, e_L = conj), forward
combination W = h + i hdot/omega with hdot = -2 alpha K_ij, omega = 2 pi sqrt 3; own Weyl
route W_R = (2/|k|^2)(E_R - i B_R), W_L = (2/|k|^2)(E_L + i B_L) with E = R_ij + K K_ij -
K_ik K^k_j (full nonlinear 3-Ricci) and B = eps_(i^kl D_k K_l j), once with spectral and once
with fourth-order centred derivatives. Time of each dump from the history file (the last
dump is at t = 2.3094 by the history, not at 4/sqrt 3 = 2.30940108; the difference is
1.17e-5 rad of phase, so the track's phase errors test which time it used).

| # | Prediction | Refuted if |
|---|---|---|
| F0 | t = 0: the +k mode of h has the normalization-free ratio abs(H:H)/(H:conj H) = 0.73948 (generator formula with amp 1e-6, amp_cross 5e-7, phase 1 rad) at every N; H:conj H = 6.25e-13 if the generator's e+ has e+:e+ = 2 | ratio off by more than 1e-6 |
| F1 | amplitude error abs(W(t_end))/abs(W(0)) - 1, both helicities equal to 1e-3 of themselves and equal to the track's -1.409e-4, -1.717e-6, -1.574e-7, -3.10e-8 (N = 16, 32, 48, 64; `waves/README.md` item 1) | any N off by more than 2 per cent of the value |
| F2 | phase error arg(W(t_end)/W(0)) + omega t_end = +2.531e-4, +1.218e-5, +2.273e-6, +7.067e-7 (positive: the discrete wave lags) | off by more than 2 per cent, or of the opposite sign |
| F3 | local orders of F1: 6.36, 5.89, 5.65; of F2: 4.38, 4.14, 4.06 | any order off by more than 0.05 |
| F4 | spectral Weyl route equals the TT route, abs(W_E/W_TT - 1) <= 1e-10 at t = 0 and t_end, every N, both helicities (track: 1.1e-11 to 1.2e-11, verifier3 6.0e-11 to 6.4e-11) | above 1e-9 |
| F5 | fourth-order Weyl route: W_E4/W_TT - 1 = (s^2 + s)/2 - 1, s = (8 sin th - sin 2 th)/(6 th), th = 2 pi/N: -1.1671e-3, -7.398e-5, -1.465e-5, -4.639e-6 (N = 16, 32, 48, 64), at t = 0 and t_end; order 4 | off by more than 5 per cent of the deviation at N >= 32 (15 per cent at N = 16) |
| F6 | polarization ratio W_L/W_R constant over the dumps read to <= 1e-8 in modulus and argument (track: W_x/W_+ = 0.5 e^i to <= 1.1e-9) | a drift above 1e-8 |

### Check N: criterion 2 on AthenaK's Newtonian mode (N1, N3)

Data: the raw `newton.newton.hst` of runs B-20261115-163620-5b286c1 (N = 32, alpha = 0.05,
0.1, 0.2), B-20261115-163621-0ae44f1 (N = 64, same alphas), B-20261115-163613-790095f
(`ell32`), -163615-7bc8b30 (`ell64`), -163617-085c093 (N = 128) for alpha = 0.11122237. Own
estimator: Q = traceless part of I_ij, P = (1/5) Q'''_ij Q'''_ij from the d3I columns at
their own times, trapezoid from t_turn to t_x, t_x the first zero of dI_xx (records after a
remainder step below half the median step dropped).

| # | Prediction | Refuted if |
|---|---|---|
| N1 | F_raw = E/(M (2 alpha)^(7/2)) = 0.062059 (N = 32), 0.077205 (N = 64) | off by more than 1 per cent |
| N2 | F_raw and tau_x = t_x/t_turn the same for the four alphas at each N to <= 1e-10 (track: 7e-15, 3e-14; tau_x 2.524849, 2.506970) | spread above 1e-8 |
| N3 | t_x of the benchmark at N = 32, 64, 128: 24.0659, 23.8955, 23.8604; order 2.28 +- 0.05; Richardson 23.851 against the ODE 23.8524 (`newton_tests/README.md` N1) | t_x off by more than 1e-4 relative or order outside the range |
