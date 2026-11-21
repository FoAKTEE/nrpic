# GATE_REVIEW.md: independent gate review of G1 of D-bh-dress

Reviewer of batch 4b (decision 0019 item 3; decision 0023 item 3), fresh context,
2026-11-21 from 16:48 UTC. I produced none of the work under review. No tag
`stage/D-bh-dress/G1-pass-*` existed when I started (`git tag -l`: only
`stage/D-bh-dress/G0-pass-20261120`). Worktree after `git merge --no-edit main`: 3771509c.

This first version holds only the predictions of my own check, committed before it runs.
The verdicts follow in the next version of this file.

## 1. My own check: predictions (written before the run)

Script `scratch/D-bh-dress/tmp/gate_review_G1/review_checks.py` (my code; imports nothing of
the track; figure style from a copy of `harness/style/figstyle.py`), registered with
`nrpic-run`, processors only.

| # | Quantity (source data) | Claim in the package | Prediction; refuted if |
|---|---|---|---|
| P1 | D-pre-1: my own quadrature of `ln(rbar/R) = -int_R^R1 (1/W - 1) dR'/R'`, `W^2 = 1 - 2M(1 - f^2)/R`, `f = S((R - R0)/(R1 - R0))`, `S(x) = 1/(1 + exp(1/x - 1/(1 - x)))`, R0 = 4 M, R1 = 36 M; `a^2 = r_iso(R0)/rbar(R0)`, `m_p = M/a` (DERIVATION.md sections 3-4 only) | a = 0.9765922286441, m_p = 1.023968828206 M, rbar(R0) = 3.055588 M (STATUS.md, DERIVATION.md section 4) | a and m_p equal to 1e-9, rbar(R0) to 1e-6; refuted if either differs by more |
| P2 | D-pre-4: `punc.horizon_summary_0.txt` of D-bh-dress-20261115-121313-284ec4f (M/8) and -121314-284ec4f (M/16), one row per search time; D = Mbar(490) - Mbar(50), Mbar the mean over a 20 M window | +2.9529e-4 (M/8), +3.6743e-5 (M/16) | equal to 1e-3 relative; refuted if not |
| P3 | V-1B floor: `v1b.horizon_summary_0.txt` of D-20261120-222625-63abd72; largest abs(M(t)/M(100) - 1) over 100 <= t <= 200 M | 4.8e-5 | between 4.3e-5 and 5.3e-5; refuted outside |
| P4 | D-pre-3, Q16 (D-20261121-085652-7e189a2): particle number and total mass in the first and the last snapshot (a/a_i = 15.956) | no particle lost; 520048 particles, 15.29505 M | equal in both snapshots; refuted if one particle or 1e-9 of the mass is missing |
| P5 | Q16, last snapshot: M_ta = clump + dust whose initial radius r0 lies below the outermost zero crossing (negative inside, positive outside) of the median radial velocity about the clump's mass centre, in 200 bins of r0 with equal counts, crossing interpolated linearly; second estimator in Eulerian radius bins (mass inside the outermost zero of the mass-weighted mean radial velocity) | 9.3017 M (flags), 9.3030 M (flag-free) | Lagrangian within 1.0 per cent of 9.3017, Eulerian within 1.5 per cent; refuted outside |
